# repositories/ — DB 접근 계층

Service는 SQLAlchemy Session이나 쿼리문을 직접 다루지 않고, 이 계층의 함수만 호출한다.
이렇게 분리해두면 이후 쿼리 최적화나 캐싱을 추가할 때 Service/Router 코드를 건드리지 않아도 된다.

## 현재

- `user_repository.py` — `get_by_email`, `get_by_id`, `create`
- `golfer_profile_repository.py` — `get_by_user_id`, `create_empty`, `update`
- `course_repository.py` — `list_all`, `get_by_id`(홀 목록까지 eager load), `search`(Phase 7 —
  region/difficulty/max_budget으로 필터링, AI 추천은 이 함수가 돌려준 후보 밖으로 나가지 않는다)
- `round_repository.py` — `list_by_user`, `list_recent_by_user`(통계용, 홀 eager load),
  `get_by_id_for_user`(**반드시 user_id로 필터** — 다른 사용자 라운드는 절대 반환하지 않는다),
  `create`, `replace_holes`, `update_fields`, `delete`
- `golf_knowledge_repository.py` — `get_by_title`(시드 멱등성 체크용), `search_similar`(코사인
  거리 기준 상위 N개, RAG 전용이라 user_id 필터 없음)
- `diary_repository.py` (Phase 6) — `list_by_user`, `get_by_id_for_user`(**반드시 user_id로
  필터**, `round`→`course`까지 eager load해 `round_summary` 조립에 쓴다), `create`, `delete`
- `group_repository.py` (Phase 9) — `create`(그룹 생성 + 소유자를 첫 멤버로 추가),
  `list_by_user`, `get_by_id_for_user`(**반드시 멤버십 확인** — 멤버가 아닌 그룹은 절대
  반환하지 않는다), `add_member`, `remove_member`, `is_member`
- `bet_repository.py` (Phase 9) — `create`, `create_results`(정산 결과 일괄 저장),
  `get_by_id`(참가자+유저 eager load), `list_by_group`

클래스가 아니라 모듈 함수로 작성한다 (상태를 갖지 않으므로 클래스로 감쌀 이유가 없다).
