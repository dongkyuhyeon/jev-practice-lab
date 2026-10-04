# JEV Practice Lab

**JEV를 이해하고 직접 실습하기 위한 저장소입니다.**

## What is JEV?

JEV는 긴 답변을 작성하는 대신 **정해진 선택지 중 하나를 고르거나, 참일 가능성과 점수를 반환하는 판단 모델**입니다.

ChatGPT 같은 생성형 LLM에게 “답변을 작성해 줘”라고 한다면, JEV에게는 “이 문의는 어느 부서로 보내야 해?”처럼 범위가 정해진 질문을 합니다.

## Why JEV?

AI 에이전트에는 글을 쓰는 일뿐 아니라 분류·라우팅·검수처럼 반복되는 판단도 많습니다. **생성은 LLM, 판단은 JEV**로 나누는 접근이 관심을 끄는 이유입니다. Skill 연동과 Ollama의 로컬 판단 모델도 이 흐름을 보여줍니다.

JEV가 모든 LLM을 대체하는 것은 아닙니다. 실행과 안전 확인은 일반 코드와 사람이 맡습니다.

## Contents

1. [What is JEV? — 개념과 LLM과의 차이](01-what-is-jev/README.md)
2. [How does JEV work? — Choice · Noul · Score](02-how-jev-works/README.md)
3. [JEV in the wild — Threads에서 본 활용 사례](03-jev-in-the-wild/README.md)
4. [실습 1 — 판단과 코드 정책 연결하기](실습1/README.md)

새 실습은 `실습2`, `실습3`처럼 독립 폴더로 추가합니다.

> 현재 실행 검증은 Mock과 테스트입니다. 실제 JEV·Ollama 모델 추론은 아직 검증하지 않았습니다.
