# Threads 5개 분석

사용자가 제공한 공유 링크를 직접 요청하고 HTML의 `og:url`, `og:title`, `og:description`에서 원문 주소와 공개 설명을 확인했습니다. 댓글·후속 게시물·이미지의 모든 내용을 수집한 것은 아닙니다.

| 번호 | 공유 링크 | 원문 | 확인한 내용 |
|---|---|---|---|
| 1 | https://www.threads.com/share/BAaeHBGzOS/ | https://www.threads.com/@choi.openai/post/Dd6EemdgK7S | JEV 이후 OpenAI Decisions API·Liquid AI d1 등 판단 모델 생태계 확장 소개 |
| 2 | https://www.threads.com/share/_6wXDcQ2X/ | https://www.threads.com/@choi.openai/post/Dd56KYlCVj9 | Ollama `/v1/systemone`, Nimble·Tev1을 통한 로컬 판단 |
| 3 | https://www.threads.com/share/BAX6iqEjuR/ | https://www.threads.com/@unclejobs.ai/post/DdbgeoFCfSb | Claude Code 등에 Skill을 설치해 JEV를 판단 worker로 활용하자는 소개 |
| 4 | https://www.threads.com/@rascal_geekersai/post/DdawY5roARP | 동일 | LLM이 closed question을 만들고 JEV가 판단하는 `pi-quiet-ask` 코드 사례 |
| 5 | https://www.threads.com/share/_67lvvryI/ | https://www.threads.com/@jaykimuniverse/post/DdbzjgnErJo | 공식 TypeSafe Skills 분석을 소개하는 짧은 게시물 |

## 관찰된 흐름

```text
판단 모델이라는 범주 확장
→ 로컬 System One 실행
→ 생성형 Agent에 판단 도구/Skill 추가
→ closed question을 확률로 판단
→ 일반 코드가 정책 적용 및 결과 기록
```

다섯 게시물 모두 실제 운영 사례는 아닙니다. 1번은 동향 소개, 2번은 공식 문서로 확인 가능한 실행 인터페이스, 3·5번은 활용 방향 소개, 4번은 공개 구현 링크가 있는 사례입니다.

## pi-quiet-ask에서 확인한 구현

참고 저장소: https://github.com/HyunjunJeon/pi-quiet-ask
확인 당시 commit: `47b286e`.

- tool_call: destructive / exfiltration / scope / impact 판단
- tool_result: 비밀값 노출 및 failure class 판단
- before_agent_start: intent / ambiguity 판단
- agent_end: 완료 주장과 실제 검증 여부 점검
- turn_end: 반복 실패와 진행 phase 판단
- ask_user: 대화에 이미 답이 있는지 판단
- evidence ledger: 실제 도구 결과로 작업·검증 상태 기록

README와 소스를 읽은 결과이지 본 저장소에서 해당 pi extension의 실제 E2E 동작을 재현한 결과는 아닙니다. 참고 저장소는 sidecar 실패 시 fail-open 동작을 문서화합니다. 이를 위험 행동의 안전 보증으로 해석하면 안 됩니다.

## 외부 주장과 검증 범위

- d1이 Decision Index에서 JEV보다 높다는 글의 주장은 특정 benchmark·버전의 비교로 봐야 합니다. 이 저장소에서 benchmark를 재실행하지 않았습니다.
- Ollama의 `/v1/systemone`, Choice/Noul/Score 요청 구조는 공식 문서를 확인하여 구현했습니다.
- '출력 토큰 0'은 모델·제공자의 구현 및 usage 표기에 따라 다릅니다. Ollama 공식 Choice 예시에는 `output_tokens: 1`도 있으므로 모든 판단 모델에 일괄 적용하지 않습니다.
- API 제공 여부나 모델 버전은 바뀔 수 있으므로 실행 전 공식 문서를 확인하세요.

## 원문 외 참고

- https://docs.ollama.com/capabilities/decision
- https://docs.ollama.com/api/systemone
- https://github.com/typesafe-ai/skills
- https://docs.liquid.ai/guides/decision-model-guide
