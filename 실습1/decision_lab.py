#!/usr/bin/env python
"""Jev/System One 실습: 닫힌 질문 -> 확률 판단 -> 일반 코드 정책 -> 감사 로그."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OLLAMA_URL = "http://localhost:11434/v1/systemone"
TYPESAFE_URL = "https://api.typesafe.ai/v1/systemone"

SCENARIOS: dict[str, dict[str, Any]] = {
    "ticket": {
        "description": "고객 문의를 분류하고 긴급도와 개인정보 포함 가능성을 판단",
        "questions": {
            "route": {
                "type": "choice",
                "instructions": "문의의 주된 처리 부서 하나를 고르세요.",
                "criteria": {
                    "billing": "결제, 환불, 청구 문제",
                    "technical": "오류, 장애, 사용법 문제",
                    "account": "로그인, 계정, 권한 문제",
                    "general": "그 밖의 일반 문의",
                },
            },
            "sensitive": {
                "type": "noul",
                "instructions": "문의에 비밀번호, API 키, 카드번호 등 민감정보가 포함되었을 가능성이 높습니까?",
                "criteria": {"false": "민감정보 징후 없음", "true": "민감정보 징후 있음"},
            },
            "urgency": {
                "type": "score",
                "instructions": "응답 긴급도를 평가하세요.",
                "criteria": ["일반: 시간 압박 없음", "빠른 대응: 사용자가 불편함", "즉시: 서비스 중단 또는 명확한 손해"],
            },
        },
    },
    "agent-gate": {
        "description": "AI 에이전트가 실행하려는 명령을 허용·확인·차단으로 라우팅",
        "questions": {
            "action": {
                "type": "choice",
                "instructions": "이 도구 호출에 적용할 가장 안전한 처리 하나를 고르세요.",
                "criteria": {
                    "allow": "읽기 전용이거나 쉽게 되돌릴 수 있고 요청 범위 안임",
                    "confirm": "변경·삭제·외부 전송이 있어 사람 확인이 필요함",
                    "block": "자격 증명 유출, 광범위 삭제, 요청 범위 밖의 위험 행동",
                },
            },
            "destructive": {
                "type": "noul",
                "instructions": "이 도구 호출이 파일, 데이터, 히스토리를 되돌리기 어렵게 삭제하거나 덮어쓸 가능성이 높습니까?",
                "criteria": {"false": "파괴적이지 않음", "true": "파괴적일 가능성이 높음"},
            },
            "exfiltration": {
                "type": "noul",
                "instructions": "이 호출이 비밀값이나 사용자 데이터를 외부로 전송할 가능성이 높습니까?",
                "criteria": {"false": "외부 유출 징후 없음", "true": "외부 유출 가능성 있음"},
            },
            "impact": {
                "type": "score",
                "instructions": "실패했을 때 예상되는 영향을 평가하세요.",
                "criteria": ["없음", "작음: 쉽게 복구", "큼: 데이터·서비스 영향", "심각: 광범위 손실 또는 보안 사고"],
            },
        },
    },
    "model-router": {
        "description": "요청 특성에 따라 로컬·빠른·강한 모델·사람 검토로 라우팅",
        "questions": {
            "route": {
                "type": "choice",
                "instructions": "이 요청을 처리할 경로 하나를 고르세요.",
                "criteria": {
                    "local": "민감하거나 단순하여 로컬 모델에 적합",
                    "fast": "저위험 반복 분류로 빠른 모델에 적합",
                    "strong": "복잡한 생성·분석으로 강한 생성 모델이 필요",
                    "human": "법률, 의료, 금융, 권한 변경 등 사람 검토가 필요",
                },
            },
            "high_risk": {
                "type": "noul",
                "instructions": "잘못 처리하면 사용자에게 중대한 법적·의료적·금전적·보안상 피해가 생길 수 있습니까?",
                "criteria": {"false": "중대한 피해 가능성이 낮음", "true": "중대한 피해 가능성이 높음"},
            },
        },
    },
}


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"연결 실패: {exc.reason}") from exc


def build_request(scenario: str, state: str, backend: str, model: str | None) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"알 수 없는 scenario: {scenario}")
    default_model = "jev-latest" if backend == "typesafe" else "tev1:0.8b"
    return {"model": model or default_model, "state": state, "questions": SCENARIOS[scenario]["questions"]}


def mock_response(scenario: str, state: str) -> dict[str, Any]:
    """구조 실습용 규칙 기반 가짜 응답. Jev/의사결정 모델이 아니다."""
    text = state.lower()
    if scenario == "ticket":
        keys = {"billing": ["환불", "결제", "청구", "카드"], "technical": ["오류", "500", "장애", "안 돼"], "account": ["로그인", "계정", "비밀번호", "권한"]}
        route = max(keys, key=lambda k: sum(w in text for w in keys[k]))
        if not any(w in text for words in keys.values() for w in words): route = "general"
        sensitive = 0.95 if any(w in text for w in ["api key", "apikey", "비밀번호", "카드번호", "token"]) else 0.05
        urgency = 1.85 if any(w in text for w in ["장애", "500", "중단", "당장"]) else 0.65
        answers = {"route": choice_answer(route, list(SCENARIOS[scenario]["questions"]["route"]["criteria"])), "sensitive": {"type": "noul", "noul": sensitive}, "urgency": {"type": "score", "score": urgency, "confidence": 0.72}}
    elif scenario == "agent-gate":
        destructive = 0.98 if any(w in text for w in ["rm -rf", "delete", "drop table", "reset --hard", "force push"]) else 0.08
        exfil = 0.97 if any(w in text for w in ["api_key", "secret", "token", ".env", "curl http"]) and any(w in text for w in ["curl", "upload", "post", "send"]) else 0.04
        action = "block" if max(destructive, exfil) >= 0.9 else ("confirm" if any(w in text for w in ["write", "edit", "install", "commit"]) else "allow")
        impact = 3.0 if action == "block" else (1.5 if action == "confirm" else 0.25)
        answers = {"action": choice_answer(action, ["allow", "confirm", "block"]), "destructive": {"type": "noul", "noul": destructive}, "exfiltration": {"type": "noul", "noul": exfil}, "impact": {"type": "score", "score": impact, "confidence": 0.82}}
    else:
        high = 0.94 if any(w in text for w in ["의료", "진단", "투자", "송금", "법률", "비밀번호", "권한"]) else 0.08
        route = "human" if high >= 0.8 else ("local" if any(w in text for w in ["개인", "민감", "로컬"]) else ("strong" if any(w in text for w in ["논문", "분석", "설계", "코드"]) else "fast"))
        answers = {"route": choice_answer(route, ["local", "fast", "strong", "human"]), "high_risk": {"type": "noul", "noul": high}}
    return {"model": "rule-mock-not-jev", "answers": answers, "usage": {"input_tokens": 0, "output_tokens": 0}}


def choice_answer(selected: str, options: list[str]) -> dict[str, Any]:
    rest = 0.1 / (len(options) - 1)
    probabilities = {k: (0.9 if k == selected else rest) for k in options}
    return {"type": "choice", "choice": selected, "probabilities": probabilities, "confidence": 0.8}


def answer_probability(answer: dict[str, Any]) -> float:
    value = answer.get("noul", answer.get("probability"))
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)) or not 0 <= float(value) <= 1:
        raise ValueError("유효하지 않은 Noul 응답")
    return float(value)


def validate_response(scenario: str, raw: dict[str, Any]) -> dict[str, Any]:
    questions = SCENARIOS[scenario]["questions"]
    answers = raw.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("응답에 answers 객체가 없습니다.")
    normalized: dict[str, Any] = {}
    for qid, q in questions.items():
        answer = answers.get(qid)
        if not isinstance(answer, dict): raise ValueError(f"{qid} 응답이 없습니다.")
        if q["type"] == "choice":
            allowed = set(q["criteria"])
            selected, probs = answer.get("choice"), answer.get("probabilities")
            if selected not in allowed or not isinstance(probs, dict) or set(probs) != allowed:
                raise ValueError(f"{qid}: 허용되지 않은 choice/probabilities")
            values = {k: float(v) for k, v in probs.items()}
            if any(not math.isfinite(v) or v < 0 or v > 1 for v in values.values()): raise ValueError(f"{qid}: 잘못된 확률")
            if values[selected] + 1e-8 < max(values.values()): raise ValueError(f"{qid}: choice가 최대 확률 항목이 아님")
            normalized[qid] = {"type": "choice", "choice": selected, "probabilities": values, "confidence": float(answer.get("confidence", 0))}
        elif q["type"] == "noul":
            normalized[qid] = {"type": "noul", "probability": answer_probability(answer)}
        else:
            score = float(answer.get("score"))
            if not math.isfinite(score) or not 0 <= score <= len(q["criteria"]) - 1: raise ValueError(f"{qid}: score 범위 오류")
            normalized[qid] = {"type": "score", "score": score, "confidence": float(answer.get("confidence", 0))}
    return {"model": raw.get("model"), "answers": normalized, "usage": raw.get("usage", {}), "raw": raw}


def apply_policy(scenario: str, result: dict[str, Any]) -> dict[str, str]:
    a = result["answers"]
    if scenario == "agent-gate":
        selected = a["action"]["choice"]
        risk = max(a["destructive"]["probability"], a["exfiltration"]["probability"])
        # 모델의 allow보다 코드 정책이 우선한다. 위험 시 자동 실행하지 않는다.
        if selected == "block" or risk >= 0.90: return {"decision": "BLOCK", "reason": "파괴·유출 위험이 높아 차단"}
        if selected == "confirm" or risk >= 0.50 or a["impact"]["score"] >= 1.5: return {"decision": "HUMAN_REVIEW", "reason": "사람 확인 후에만 실행"}
        return {"decision": "ALLOW", "reason": "낮은 위험. 단, 실제 실행기는 별도 권한 검사를 해야 함"}
    if scenario == "ticket":
        if a["sensitive"]["probability"] >= 0.70: return {"decision": "REDACT_AND_REVIEW", "reason": "민감정보 가능성"}
        if a["urgency"]["score"] >= 1.5: return {"decision": "PRIORITY_QUEUE", "reason": "긴급도 높음"}
        return {"decision": f"ROUTE_{a['route']['choice'].upper()}", "reason": "분류 결과에 따라 라우팅"}
    if a["high_risk"]["probability"] >= 0.70 or a["route"]["choice"] == "human": return {"decision": "HUMAN_REVIEW", "reason": "고위험 요청"}
    return {"decision": f"ROUTE_{a['route']['choice'].upper()}", "reason": "요청 특성에 따른 모델 라우팅"}


def write_audit(scenario: str, backend: str, state: str, result: dict[str, Any], policy: dict[str, str]) -> Path:
    out = Path(__file__).with_name("logs"); out.mkdir(exist_ok=True)
    record = {"time": datetime.now(timezone.utc).isoformat(), "scenario": scenario, "backend": backend, "state_sha256": hashlib.sha256(state.encode()).hexdigest(), "state_preview": state[:200], "model": result["model"], "answers": result["answers"], "policy": policy}
    path = out / "decisions.jsonl"
    with path.open("a", encoding="utf-8") as f: f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def run(args: argparse.Namespace) -> int:
    load_dotenv(Path(__file__).with_name(".env"))
    state = " ".join(args.state).strip() or input("판단할 상태를 입력하세요: ").strip()
    if not state: raise ValueError("state가 비었습니다.")
    payload = build_request(args.scenario, state, args.backend, args.model)
    start = time.perf_counter()
    if args.backend == "mock": raw = mock_response(args.scenario, state); source = "mock-not-jev"
    elif args.backend == "ollama": raw = post_json(os.getenv("OLLAMA_SYSTEMONE_URL", OLLAMA_URL), payload); source = "local-systemone"
    else:
        key = os.getenv("TYPESAFE_API_KEY", "").strip()
        if not key: raise RuntimeError("TYPESAFE_API_KEY가 없습니다. .env를 설정하세요.")
        raw = post_json(os.getenv("TYPESAFE_BASE_URL", TYPESAFE_URL), payload, {"Authorization": f"Bearer {key}"}); source = "typesafe-jev"
    result = validate_response(args.scenario, raw)
    policy = apply_policy(args.scenario, result)
    elapsed = (time.perf_counter() - start) * 1000
    path = write_audit(args.scenario, source, state, result, policy)
    print(f"\n시나리오 : {args.scenario} — {SCENARIOS[args.scenario]['description']}")
    print(f"판단 출처 : {source} / {result['model']}")
    for key, value in result["answers"].items(): print(f"{key:12}: {json.dumps(value, ensure_ascii=False)}")
    print(f"정책 결정 : {policy['decision']} — {policy['reason']}")
    print(f"지연 시간 : {elapsed:.1f} ms")
    print(f"감사 로그 : {path}")
    if source == "mock-not-jev": print("주의      : 이 결과는 구조 검증용 mock이며 실제 Jev/decision model 결과가 아닙니다.")
    if args.raw: print(json.dumps(raw, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Jev/System One Decision Lab")
    p.add_argument("state", nargs="*")
    p.add_argument("--scenario", choices=SCENARIOS, default="agent-gate")
    p.add_argument("--backend", choices=["mock", "ollama", "typesafe"], default="mock")
    p.add_argument("--model")
    p.add_argument("--raw", action="store_true")
    args = p.parse_args(argv)
    try: return run(args)
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"오류: {exc}", file=sys.stderr); return 1

if __name__ == "__main__": raise SystemExit(main())
