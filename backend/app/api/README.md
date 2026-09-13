# api/ — HTTP 라우터

`routers/`에 도메인별 `APIRouter`를 정의하고, `app/main.py`에서 `/api` prefix로 등록한다.

## 현재 라우터

- `routers/health.py`
  - `GET /api/health` — 프로세스 liveness (DB 접근 없음)
  - `GET /api/health/db` — DB에 `SELECT 1`을 날려 연결을 확인
- `routers/auth.py`
  - `POST /api/auth/register` — 회원가입 (이메일 중복 시 409), 토큰+사용자 정보 반환
  - `POST /api/auth/login` — 로그인 (자격 증명 불일치 시 401), 토큰+사용자 정보 반환
- `routers/users.py` (모두 `get_current_user` 의존 — 로그인 필요)
  - `GET /api/users/me` — 내 계정 정보
  - `GET /api/users/me/profile` — 내 골퍼 프로필
  - `PUT /api/users/me/profile` — 내 골퍼 프로필 부분 수정

## 앞으로 추가될 라우터 (마스터 스펙 §20 기준)

`rounds`, `ai` (coach/caddie), `courses`, `diaries`, `groups`, `bets`.
각 라우터는 요청 검증 → service 호출 → 응답 반환만 담당하고, 비즈니스 로직은 갖지 않는다.
