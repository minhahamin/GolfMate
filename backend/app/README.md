# app/ — 레이어 구조

이 프로젝트는 아래 흐름을 지키기 위해 계층을 분리한다 (원칙: LLM에게 모든 것을 맡기지 않고,
정확한 계산/조회는 코드가, 판단과 자연어 생성은 LLM이 담당한다).

```text
Router (api/routers)
  ↓ 요청/응답 스키마 검증만
Service (services)
  ↓ 비즈니스 로직, 여러 Repository/Tool 조합
Repository (repositories)
  ↓ SQLAlchemy로 DB read/write
AI Layer (ai)
  ↓ LangGraph / LangChain / Tool Calling / RAG
```

## 각 계층의 책임

- **api/routers**: HTTP 요청을 받아 Pydantic으로 검증하고, service를 호출해 결과를 반환한다.
  DB 세션이나 SQL을 직접 다루지 않는 것이 원칙이지만, `health` 라우터처럼 로직이 없는
  단순 조회는 예외적으로 라우터에서 직접 처리한다.
- **services**: "평균 타수 계산", "내기 정산", "약점 분석 오케스트레이션" 같은 실제
  비즈니스 규칙이 여기 산다. LLM 호출이 필요하면 `ai/` 계층을 호출하되, 계산 가능한 부분은
  절대 LLM에 맡기지 않는다.
- **repositories**: SQLAlchemy 쿼리를 캡슐화한다. Service는 Repository의 메서드만 호출하고
  SQLAlchemy Session을 직접 알 필요가 없다.
- **ai**: LangGraph 그래프, Tool 정의, Prompt 로딩, RAG retriever 등 LLM 관련 코드 전용 공간.
  일반 비즈니스 로직과 섞이지 않도록 강제 분리한다.

## Phase 1 현재 상태

지금은 `health` 라우터 하나만 존재하며, DB 연결 여부를 확인하는 용도로 라우터에서
직접 `SELECT 1`을 실행한다. `services/`, `repositories/`, `ai/`는 Phase 2부터 채워진다.
