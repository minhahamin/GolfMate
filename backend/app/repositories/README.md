# repositories/ — DB 접근 계층

Service는 SQLAlchemy Session이나 쿼리문을 직접 다루지 않고, 이 계층의 함수만 호출한다.
이렇게 분리해두면 이후 쿼리 최적화나 캐싱을 추가할 때 Service/Router 코드를 건드리지 않아도 된다.

## 현재

- `user_repository.py` — `get_by_email`, `get_by_id`, `create`
- `golfer_profile_repository.py` — `get_by_user_id`, `create_empty`, `update`

클래스가 아니라 모듈 함수로 작성한다 (상태를 갖지 않으므로 클래스로 감쌀 이유가 없다).
Round, Course 등 Phase 3+ 도메인이 추가되면 같은 패턴으로 `round_repository.py` 등을 둔다.
