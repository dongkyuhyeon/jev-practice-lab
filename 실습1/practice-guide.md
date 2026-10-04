# 실습 가이드

## 목표

JEV를 자유 생성 모델로 쓰는 것이 아니라 코드가 만든 후보에 대한 판단 도구로 사용하는 구조를 익힙니다.
아래 명령은 저장소 루트에서 실행합니다.

## 1. Mock으로 구조 이해

```bash
python 실습1/decision_lab.py --backend mock --scenario agent-gate "git status" --raw
python 실습1/decision_lab.py --backend mock --scenario agent-gate "rm -rf project" --raw
```

`state`가 어떻게 `questions`와 묶이는지 `build_request`를 읽어 보세요. `mock_response`는 단순 키워드 규칙이므로 이해할 수 있는 예제만 처리합니다. 실제 의미 판단 성능을 보여주지 않습니다.

## 2. Choice·Noul·Score 동시 사용

```bash
python 실습1/decision_lab.py --backend mock --scenario ticket "비밀번호와 API key를 보냅니다"
```

서로 다른 질문의 응답을 `apply_policy`에서 합칩니다. 모델 확률과 정책 임계값은 다른 것입니다. 임계값은 실제 데이터에서 오탐·미탐을 측정하여 정해야 합니다.

## 3. 실제 모델로 백엔드 교체

실제 호출 실패 시 Mock으로 조용히 대체하지 않습니다.

**TypeSafe JEV:** `실습1/.env.example`을 같은 폴더의 `.env`로 복사하고 본인의 `TYPESAFE_API_KEY`를 넣습니다. 키를 Git이나 채팅에 공유하지 마세요. 원격 호출은 입력을 외부 서버로 보내며 요금이 발생할 수 있습니다.

**로컬 Ollama:** Ollama 0.35.0 이상을 설치하고 서버를 실행한 뒤 `ollama pull tev1:0.8b`로 모델을 내려받습니다. API 키는 필요 없습니다. Tev1은 JEV 자체가 아닌 별도 판단 모델입니다.

```bash
python 실습1/decision_lab.py --backend ollama --model tev1:0.8b --scenario ticket "결제가 두 번 됐어요" --raw
python 실습1/decision_lab.py --backend typesafe --scenario ticket "결제가 두 번 됐어요" --raw
```

## 4. 평가하기

가상 입력 20~50개를 직접 작성하고 사람이 먼저 정답 라벨을 정하세요.

- 문의 분류 정확도 및 혼동행렬
- 고위험 요청 미탐률
- 저신뢰 응답 비율
- 사람 확인으로 넘긴 비율
- 실제 모델 end-to-end latency의 median/p95
- 모델·언어별 차이

현재 저장소에는 이 성능평가 데이터셋이나 평가 결과가 없습니다. Mock의 지연·정확도는 모델 성능이 아닙니다.

## 5. 다음 확장

- 생성형 LLM이 만드는 질문을 JSON schema로 검증
- 관찰된 후보에 `other`/`ask_user`를 넣고 abstention 적용
- 로그 입력 preview 제거 또는 로컬 redaction
- 권한 allowlist와 deterministic safety gate
- 실제 실행 결과와 모델의 완료 판단을 분리

JEV를 확률적 판단 도구로 쓰되 권한·검증·사람 승인을 대체하지 않는 것이 핵심입니다.
