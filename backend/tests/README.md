# tests/ — Backend 테스트

`pytest` + FastAPI `TestClient`를 사용한다.

## 현재

- `test_health.py` — `/api/health` liveness 스모크 테스트 (DB 없이도 통과).
- `test_auth.py` — 회원가입/로그인/중복이메일/오답비밀번호/보호된 엔드포인트(`/users/me`,
  `/users/me/profile`) 테스트. 실제 PostgreSQL 연결이 필요하며, 이메일 중복을 피하려고
  테스트마다 `uuid`로 고유 이메일을 생성한다 (현재는 트랜잭션 롤백 픽스처 없이 실제 DB에
  데이터가 남는다 — 데이터가 많아지면 격리된 테스트 DB/픽스처 도입을 고려한다).

## Phase별 확장 계획 (마스터 스펙 §28)

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
