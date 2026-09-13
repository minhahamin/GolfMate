# tests/ — Backend 테스트

`pytest` + FastAPI `TestClient`를 사용한다.

## 현재

- `test_health.py` — `/api/health` liveness 스모크 테스트 (DB 없이도 통과).

## Phase별 확장 계획 (마스터 스펙 §28)

- Phase 2: Auth (회원가입/로그인/JWT), 사용자별 데이터 접근 제한 테스트
- Phase 3: Round CRUD, Statistics 계산 테스트
- Phase 4+: AI API의 입출력 검증, Tool calling, RAG retrieval, LangGraph 라우팅
- 특히 **골프 내기 금액/승패 계산은 LLM이 아닌 일반 코드로 테스트**한다 (§29 원칙).

## 실행

```bash
cd backend
pytest
```

DB가 필요한 통합 테스트(`/api/health/db` 등)를 추가할 때는 `docker compose up db`로 실제
PostgreSQL을 띄운 상태에서 실행한다.
