# JEV Practice Lab

JEV와 System One 의사결정 모델을 공부하고, **닫힌 질문 → 확률 판단 → 코드 정책 → 감사 로그** 흐름을 실습하는 저장소입니다.

> **검증 범위:** 현재 실제 실행 검증은 로컬 규칙 기반 Mock과 단위 테스트입니다. TypeSafe JEV 및 Ollama 모델의 실제 추론 성능은 아직 검증하지 않았습니다. Mock 수치를 모델의 정확도나 지연 시간으로 해석하면 안 됩니다.

## 왜 생성 모델과 판단 모델을 분리하나?

```text
생성형 LLM: 계획·코드·후보 생성
JEV / System One: Choice·Noul·Score로 제한된 판단
일반 코드: 응답 검증·권한·임계값·사람 확인·실행 결과 검증
```

- **Choice:** 코드가 정한 후보 중 하나를 선택합니다.
- **Noul:** 조건이 참일 확률을 반환합니다.
- **Score:** 순서가 있는 기준에 따른 점수를 반환합니다.
- 높은 확률이나 confidence가 사실·안전·성공을 보증하지는 않습니다.

## 실습 시나리오

| 시나리오 | 판단 | 코드 정책 |
|---|---|---|
| `agent-gate` | allow/confirm/block, 파괴성, 유출, 영향도 | BLOCK / HUMAN_REVIEW / ALLOW |
| `ticket` | 문의 부서, 민감정보 가능성, 긴급도 | 검토 / 우선 큐 / 부서 라우팅 |
| `model-router` | local/fast/strong/human, 고위험 여부 | 모델 또는 사람으로 라우팅 |

이 프로그램은 명령 문자열을 **판단만** 하며 실제 명령 실행·메일 전송·모델 라우팅을 수행하지 않습니다. 완전한 코딩 에이전트나 보안 도구가 아닌 학습용 CLI입니다.

## 빠른 시작 — API 없이

Python 3.11 이상, 별도 Python 패키지 설치 불필요.

```bash
git clone https://github.com/dongkyuhyeon/jev-practice-lab.git
cd jev-practice-lab
python -m unittest -v
python decision_lab.py --backend mock --scenario agent-gate "git status"
python decision_lab.py --backend mock --scenario agent-gate "rm -rf project"
python decision_lab.py --backend mock --scenario ticket "결제가 두 번 됐고 서비스가 500 오류입니다"
python decision_lab.py --backend mock --scenario model-router "의료 진단을 내려줘"
```

Windows에서는 `run-demo.bat`도 사용할 수 있습니다. 출력의 `mock-not-jev`는 **실제 JEV가 아님**을 뜻합니다.

## 실제 TypeSafe JEV

1. `.env.example`을 `.env`로 복사합니다.
2. `TYPESAFE_API_KEY`에 본인의 키를 로컬로 설정합니다.
3. 다음을 실행합니다.

```bash
python decision_lab.py --backend typesafe --scenario ticket "로그인할 수 없습니다"
```

기본 endpoint: `https://api.typesafe.ai/v1/systemone`, 기본 모델: `jev-latest`.
다른 모델을 사용할 때는 `--model`을 명시합니다. 실제 호출에는 요금·데이터 전송이 발생할 수 있습니다.

## 로컬 Ollama System One

Ollama 공식 문서 기준 0.35.0 이상이 필요합니다. Ollama 서버가 실행 중이어야 합니다.

```bash
ollama --version
ollama pull tev1:0.8b
python decision_lab.py --backend ollama --model tev1:0.8b --scenario ticket "결제가 두 번 됐어요"
```

- endpoint: `http://localhost:11434/v1/systemone`
- 로컬 호출에는 API 키가 필요 없습니다.
- Tev1/Nimble은 JEV 자체가 아니라 System One 인터페이스를 사용하는 별도 판단 모델입니다.
- 모델 다운로드 용량 및 실행 가능 여부는 본인 장치에서 확인해야 합니다.

## 문서

- [Threads 5개 분석](docs/threads-analysis.md)
- [실습 절차와 학습 포인트](docs/practice-guide.md)
- [실제 검증 기록 및 한계](docs/verification.md)

## 파일

```text
decision_lab.py        # Mock / Ollama / TypeSafe 백엔드, 정책, 로그
test_decision_lab.py   # 7개 단위 테스트
run-demo.bat          # Windows Mock 데모
run-local.bat         # Windows Ollama 확인 및 호출
.env.example          # 자격 증명 없는 환경변수 템플릿
docs/                 # 출처, 실습, 검증 기록
```

## 안전과 한계

- `.env`, `logs/`, Python 캐시는 Git에서 제외됩니다.
- **감사 로그에는 입력 앞 200자가 포함됩니다.** 실습에는 가상 데이터를 사용하고 로그를 공유하기 전 반드시 민감정보를 제거하세요.
- 원격 JEV 호출은 입력 상태를 외부 서버로 보냅니다. 비밀번호·실제 키·개인정보를 입력하지 마세요.
- 후보 외 응답 및 일부 잘못된 수치는 거부하지만 검증기는 학습용이며 완전한 보안 검증기가 아닙니다.
- 현 정책에는 Choice 확률이 낮을 때의 일괄 abstention이 없습니다. 실제 운영에는 저신뢰 응답 처리와 결정적 권한 검사를 추가해야 합니다.
- API 오류 시 CLI는 실패 종료합니다. 실제 Agent에 연결할 때 위험 행동의 자동 허용으로 대체하지 마세요.
- `pi-quiet-ask`는 참고한 별도 프로젝트이며 이 저장소는 그 extension을 설치하거나 Hermes에 연결하지 않습니다.
- 이 저장소는 대학원 연구 프로젝트와 별개의 JEV 학습 기록입니다.

## 공식 참고자료

- [TypeSafe Skills](https://github.com/typesafe-ai/skills)
- [Ollama Decision Guide](https://docs.ollama.com/capabilities/decision)
- [Ollama System One API](https://docs.ollama.com/api/systemone)
- [pi-quiet-ask](https://github.com/HyunjunJeon/pi-quiet-ask)
