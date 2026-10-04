# 실습 1. JEV Decision Lab

**문장을 입력하면 분류와 점수를 받고, 코드가 그 결과를 어떻게 처리하는지 확인하는 첫 실습입니다.**

예를 들어 “결제가 두 번 됐어요”라는 문의를 넣으면 결제 담당으로 분류하는 흐름을 살펴봅니다. 명령 실행·문의 전송은 하지 않고 판단 결과만 출력합니다.

## 세 가지 시나리오

- `agent-gate`: 명령 문자열을 허용·확인·차단 후보로 판단합니다.
- `ticket`: 문의 부서, 민감정보 가능성, 긴급도를 판단합니다.
- `model-router`: 요청을 로컬·빠른·강한 모델 또는 사람 검토 후보로 분류합니다.

## Mock과 실제 백엔드

기본 `mock`은 키워드 규칙으로 만든 구조 검증용 가짜 응답이며 JEV가 아닙니다. 현재 검증된 것은 Mock과 단위 테스트 7개뿐이고, 실제 TypeSafe JEV 및 Ollama 추론은 검증하지 않았습니다. 로컬 기본 모델 `tev1:0.8b`도 JEV 자체가 아니라 같은 System One 인터페이스를 사용하는 별도 판단 모델입니다.

## 실행 예시

저장소 루트에서 Python 3.11 이상으로 실행하며 별도 패키지는 필요 없습니다.

```bash
python 실습1/decision_lab.py --backend mock --scenario agent-gate "git status"
python 실습1/decision_lab.py --backend mock --scenario ticket "비밀번호와 API key를 보냅니다"
python 실습1/decision_lab.py --backend mock --scenario model-router "의료 진단을 내려줘"
```

Windows에서는 `run-demo.bat`를 실행할 수 있습니다. 실제 백엔드 설정은 `.env.example`, `run-local.bat`, [상세 실습 가이드](practice-guide.md)를 참고하세요. 실행 결과와 미검증 범위는 [검증 기록](verification.md)에 정리했습니다.

감사 로그에는 입력 앞 200자가 기록되므로 실제 비밀값이나 개인정보를 입력하지 마세요.

이전: [3장. 공개 사례에서 본 JEV](../03-jev-in-the-wild/README.md)
