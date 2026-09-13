# tests/ — Backend 테스트

`pytest` + FastAPI `TestClient`를 사용한다.

## 현재

- `test_health.py` — `/api/health` liveness 스모크 테스트 (DB 없이도 통과).
- `test_auth.py` — 회원가입/로그인/중복이메일/오답비밀번호/보호된 엔드포인트(`/users/me`,
  `/users/me/profile`) 테스트.
- `test_courses.py` — 골프장 목록/상세/404 테스트.
- `test_rounds.py` — 라운드 CRUD, 홀 점수 합산으로 score 자동 계산, 통계(`analysis`,
  `statistics/summary`) 계산, 소유권(다른 사용자 라운드 접근 시 404) 테스트.
- `conftest.py` — 위 테스트들이 공유하는 헬퍼: `register_and_get_token`, `auth_headers`,
  `seed_test_course`(홀 3개짜리 테스트 전용 코스 생성).

이 테스트들은 실제 PostgreSQL 연결이 필요하고, 트랜잭션 롤백 픽스처 없이 실제 DB에
데이터를 남긴다 (이메일/코스 이름에 `uuid`를 섞어 충돌은 피한다). 데이터가 많아지면
격리된 테스트 DB/픽스처 도입을 고려한다. 테스트로 쌓인 계정/코스를 정리하려면:

```sql
DELETE FROM users WHERE email LIKE 'test-%@example.com';
DELETE FROM courses WHERE name LIKE '테스트코스-%';
```

## Phase별 확장 계획 (마스터 스펙 §28)

- Phase 4+: AI API의 입출력 검증, Tool calling, RAG retrieval, LangGraph 라우팅
- 특히 **골프 내기 금액/승패 계산은 LLM이 아닌 일반 코드로 테스트**한다 (§29 원칙).

## 실행

```bash
cd backend
pytest
```

DB가 필요한 통합 테스트(`/api/health/db` 등)를 추가할 때는 `docker compose up db`로 실제
PostgreSQL을 띄운 상태에서 실행한다.
