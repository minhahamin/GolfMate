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
- `routers/courses.py` (공개, 인증 불필요)
  - `GET /api/courses` — 골프장 목록
  - `GET /api/courses/{course_id}` — 골프장 상세(홀별 파/거리 포함)
- `routers/rounds.py` (모두 `get_current_user` 의존, 본인 라운드만 접근 가능)
  - `GET /api/rounds` — 내 라운드 목록
  - `POST /api/rounds` — 라운드 생성 (홀 상세를 보내면 score를 서버가 합산 계산)
  - `GET /api/rounds/{round_id}` / `PUT` / `DELETE` — 상세/수정/삭제 (다른 사용자 것은 404)
  - `GET /api/rounds/{round_id}/analysis` — 해당 라운드 통계 (순수 계산, LLM 없음)
  - `GET /api/rounds/statistics/summary` — 최근 N라운드 집계 통계
    (라우트 순서 주의: `{round_id}`보다 먼저 등록해야 "statistics"가 id로 오인되지 않는다)

- `routers/coach.py` (`get_current_user` 의존)
  - `POST /api/ai/coach` — 최근 라운드 기반 AI 코칭 분석 (LangGraph, `app/ai/coach/graph.py`).
    응답은 항상 200이며, 데이터 없음/LLM 실패도 폴백 메시지로 200 응답에 담긴다 (§29).
- `routers/diaries.py` (모두 `get_current_user` 의존, 본인 일기만 접근 가능, Phase 6)
  - `GET /api/diaries` — 내 일기 목록
  - `POST /api/diaries` — 일기 생성. JSON이 아니라 multipart/form-data(텍스트 또는 오디오
    파일, 선택적 `round_id`)를 받는다. 오디오는 로컬 faster-whisper로 전사한 뒤 폐기한다
    (`app/ai/stt/transcriber.py`). 텍스트/오디오 둘 다 없으면 400, 오디오 전사에 실패하면
    422, 그 외에는 LLM 실패도 폴백 텍스트로 201 응답에 담긴다(원문은 항상 저장됨).
  - `GET /api/diaries/{diary_id}` / `DELETE` — 상세/삭제 (다른 사용자 것은 404)
- `routers/recommend.py` (`get_current_user` 의존, Phase 7)
  - `POST /api/ai/recommend-courses` — 지역/난이도/예산/자유 선호 조건으로 필터링된 실제
    `courses` DB 후보 중에서 AI가 최대 3곳을 순위/이유와 함께 추천 (LangGraph,
    `app/ai/recommend/graph.py`). 후보가 없으면 LLM 호출 없이 바로 안내 응답.
- `routers/caddie.py` (`get_current_user` 의존, Phase 8)
  - `POST /api/ai/caddie` — 골프장/홀/선택적 질문을 받아 Open-Meteo 실시간 날씨를 반영한
    홀공략/위험요소/클럽전략을 생성 (LangGraph, `app/ai/caddie/graph.py`). 존재하지 않는
    골프장/홀은 404, 날씨 조회 실패나 LLM 실패는 폴백으로 200 응답.
- `routers/groups.py` (모두 `get_current_user` 의존, 본인이 속한 그룹만 접근 가능, Phase 9)
  - `POST /api/groups` — 그룹 생성 (생성자가 그룹장 + 첫 멤버가 됨)
  - `GET /api/groups` — 내가 속한 그룹 목록
  - `GET /api/groups/{group_id}` — 그룹 상세(멤버 목록 포함, 멤버가 아니면 404)
  - `POST /api/groups/{group_id}/members` — 이메일로 멤버 추가 (그룹장만, 403/404)
  - `DELETE /api/groups/{group_id}/members/{user_id}` — 멤버 제거/탈퇴 (본인 탈퇴 또는
    그룹장만, 그룹장 본인은 탈퇴 불가)
  - `POST /api/groups/{group_id}/bets` — 내기 생성 + 정산 (`bet_service.calculate_settlement`,
    참가자는 반드시 그룹 멤버여야 하고 2명 이상이어야 함)
  - `GET /api/groups/{group_id}/bets` — 그룹의 내기 목록
- `routers/bets.py` (`get_current_user` 의존, Phase 9)
  - `GET /api/bets/{bet_id}` — 내기 상세(참가자별 스코어+정산 금액, 그룹 멤버가 아니면 404)
- `routers/bet_commentary.py` (`get_current_user` 의존, Phase 9)
  - `POST /api/ai/bet-commentary` — 이미 계산된 정산 결과를 설명하는 AI 코멘터리 생성
    (LangGraph, `app/ai/bet/graph.py`). LLM은 금액을 다시 계산하지 않는다.

## 앞으로 추가될 라우터 (마스터 스펙 §20 기준)

Phase 10(Langfuse)은 새 라우터가 아니라 기존 그래프에 트레이싱을 추가하는 방식이다.
각 라우터는 요청 검증 → service 호출 → 응답 반환만 담당하고, 비즈니스 로직은 갖지 않는다.
