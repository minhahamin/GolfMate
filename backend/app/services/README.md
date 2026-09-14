# services/ — 비즈니스 로직

## 현재

- `auth_service.py` — 회원가입(중복 이메일 검사, 비밀번호 해싱, 빈 GolferProfile 동시 생성),
  로그인(자격 증명 검증), 두 경우 모두 JWT를 발급해 `AuthResponse`로 반환한다.
- `profile_service.py` — 로그인한 사용자 본인의 골퍼 프로필 조회/부분 수정
  (`GolferProfileUpdate.model_dump(exclude_unset=True)`로 보낸 필드만 갱신).

- `course_service.py` — 골프장 목록/상세 조회 (없으면 404).
- `round_service.py` — 라운드 CRUD 오케스트레이션. 홀 상세가 오면 `score`를 홀 점수 합으로
  다시 계산하고, 모든 조회/수정/삭제는 소유권 확인(`get_my_round`)을 거친다.
- `statistics_service.py` — **순수 Python 계산, LLM 호출 없음**. `compute_round_analysis`
  (한 라운드 통계: score_to_par, 퍼팅/페어웨이/GIR, 파3·4·5별 평균)와
  `compute_statistics_summary`(최근 N라운드 집계: 평균/베스트 스코어, 추이). Phase 4 AI Coach가
  이 함수들을 그대로 재사용한다.
- `diary_service.py` (Phase 6) — 일기 생성 오케스트레이션: 오디오가 있으면 먼저 STT(실패
  시 422), `round_id`를 직접 지정했으면 소유권 확인(다른 사용자 라운드면 404) 후
  `app/ai/diary/graph.py`를 호출해 구조화 필드를 생성하고 저장한다. 조회/삭제는 Round와
  동일하게 소유권 확인(`get_my_diary`)을 거쳐 404-not-403 원칙을 따른다.

## 앞으로 (Phase 7+)

`bet_service.py` (내기 정산 — **LLM이 아닌 Python이 금액을 계산**한다), `recommendation_service.py` 등.

원칙: 계산 가능한 것은 여기(Python)에서 처리하고, 자연어 판단/설명이 필요한 부분만
`app/ai/`를 호출한다.
