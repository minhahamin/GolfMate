# schemas/ — Pydantic 요청/응답 모델

ORM 모델(`app/models`)과 API에 노출되는 형태(`app/schemas`)를 분리한다.
이렇게 하면 `hashed_password` 같은 민감한 필드가 실수로 응답에 섞여 나가는 것을 막을 수 있고,
DB 스키마가 바뀌어도 API 계약을 독립적으로 관리할 수 있다.

- `user.py` — `UserRead` (비밀번호 필드 제외)
- `golfer_profile.py` — `GolferProfileRead`, `GolferProfileUpdate`

명명 규칙: `XxxCreate` / `XxxUpdate` / `XxxRead`. Phase 2부터 Auth 관련 스키마
(`UserCreate`, `Token` 등)가 추가된다.
