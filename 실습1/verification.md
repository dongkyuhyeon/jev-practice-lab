# 검증 기록

## 기존 실습에서 실제 수행한 검증

- Python 문법 컴파일 통과
- `python -m unittest -v`: 7개 테스트 통과
- Mock `git status`: ALLOW
- Mock 파괴적 명령 문자열: BLOCK
- Mock 민감정보 문의: REDACT_AND_REVIEW
- Mock 의료 요청: HUMAN_REVIEW
- JSONL 감사 로그 생성 및 필수 필드 확인
- Ollama가 없는 환경에서 실패 종료 확인
- `.env` 및 로그의 Git 제외 설정 확인

별도의 임시 검증 스크립트는 `AD_HOC_VERIFY_OK`를 반환했고 이후 삭제했습니다.

## 이 저장소의 자동 테스트

`test_decision_lab.py`는 요청 구조, Mock 출처, 정책 분기, 후보 밖 응답 거부, Noul 응답 호환을 검사합니다. 저장소 루트에서 다음을 실행합니다.

```bash
python -m unittest discover -s 실습1 -v
python -m py_compile 실습1/decision_lab.py 실습1/test_decision_lab.py
```

Mock 출력은 코드 동작 검증이며 실제 JEV의 정확도·calibration·속도 검증이 아닙니다. 원격 API를 호출하는 테스트는 포함하지 않습니다.

## 아직 검증하지 않은 것

- TypeSafe 실제 JEV 성공 응답
- Ollama 실제 판단 모델 추론
- pi-quiet-ask extension E2E
- benchmark 정확도 또는 model latency
- 운영 환경의 보안성·calibration

## 검증 수준

집중 단위 테스트와 ad-hoc 검증입니다. 실제 모델 통합 테스트나 운영 적합성 검증을 완료했다고 주장하지 않습니다.
