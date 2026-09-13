# services/ — 비즈니스 로직

현재는 빈 스캐폴드다. Phase 1에는 로직다운 로직이 없는 헬스체크 하나뿐이라 아직 채우지 않았다.

Phase 2(Auth)부터 여기에 다음과 같은 서비스가 들어온다:

- `auth_service.py` — 회원가입/로그인, JWT 발급
- `profile_service.py` — 골퍼 프로필 생성/수정
- Phase 3+: `round_service.py` (통계 계산), `bet_service.py` (내기 정산 — **LLM이 아닌
  Python이 금액을 계산**한다), `recommendation_service.py` 등

원칙: 계산 가능한 것은 여기(Python)에서 처리하고, 자연어 판단/설명이 필요한 부분만
`app/ai/`를 호출한다.
