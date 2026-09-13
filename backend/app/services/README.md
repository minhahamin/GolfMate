# services/ — 비즈니스 로직

## 현재

- `auth_service.py` — 회원가입(중복 이메일 검사, 비밀번호 해싱, 빈 GolferProfile 동시 생성),
  로그인(자격 증명 검증), 두 경우 모두 JWT를 발급해 `AuthResponse`로 반환한다.
- `profile_service.py` — 로그인한 사용자 본인의 골퍼 프로필 조회/부분 수정
  (`GolferProfileUpdate.model_dump(exclude_unset=True)`로 보낸 필드만 갱신).

## 앞으로 (Phase 3+)

`round_service.py` (통계 계산), `bet_service.py` (내기 정산 — **LLM이 아닌 Python이 금액을
계산**한다), `recommendation_service.py` 등.

원칙: 계산 가능한 것은 여기(Python)에서 처리하고, 자연어 판단/설명이 필요한 부분만
`app/ai/`를 호출한다.
