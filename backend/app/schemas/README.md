# schemas/ — Pydantic 요청/응답 모델

ORM 모델(`app/models`)과 API에 노출되는 형태(`app/schemas`)를 분리한다.
이렇게 하면 `hashed_password` 같은 민감한 필드가 실수로 응답에 섞여 나가는 것을 막을 수 있고,
DB 스키마가 바뀌어도 API 계약을 독립적으로 관리할 수 있다.

- `user.py` — `UserRead` (비밀번호 필드 제외)
- `golfer_profile.py` — `GolferProfileRead`, `GolferProfileUpdate`
- `auth.py` — `UserCreate`(회원가입 입력), `UserLogin`, `AuthResponse`(토큰+`UserRead`)
- `course.py` — `CourseRead`, `CourseHoleRead`, `CourseDetailRead`(홀 목록 포함)
- `round.py` — `HoleInput`/`HoleRead`, `RoundCreate`/`RoundUpdate`/`RoundListItem`/`RoundRead`,
  `RoundAnalysis`(라운드 통계), `StatisticsSummary`(최근 N라운드 집계). `RoundCreate`는
  `score` 또는 `holes` 중 하나는 반드시 있어야 한다는 검증(`model_validator`)을 가진다.
- `coach.py` — `CoachRequest`(질문, 선택), `CoachResponse`(5개 섹션: current_state,
  biggest_problem, cause, strategy, next_goal)
- `diary.py` (Phase 6) — `DiaryListItem`(목록용: id, round_id, summary, mood, created_at),
  `DiaryRead`(상세: round_summary 포함 5개 필드 + raw_text). 생성 요청은 JSON이 아니라
  multipart/form-data(텍스트 또는 오디오 파일)라 `DiaryCreate` 모델은 없다 — 라우터가
  `Form`/`File`을 직접 받는다.

명명 규칙: `XxxCreate` / `XxxUpdate` / `XxxRead`.
