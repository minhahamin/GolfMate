# models/ — SQLAlchemy ORM

현재 정의된 모델:

- **User** (`user.py`) — 계정 정보. `id`, `email`(unique), `hashed_password`, `name`,
  `created_at`, `updated_at`. 회원가입/로그인 API는 Phase 2에서 구현하지만, 테이블 구조는
  지금 확정한다.
- **GolferProfile** (`golfer_profile.py`) — User와 1:1. AI Coach/Caddie가 참고하는 실력 지표:
  `handicap`, `average_score`, `driver_distance`, `iron_distance`, `putting_average`,
  `fairway_percentage`, `gir_percentage`, `preferred_tee`, `goal_score`.

## 새 모델을 추가할 때

1. 이 폴더에 `xxx.py`를 만들고 `Base`를 상속한다.
2. `__init__.py`에서 import를 추가해 `Base.metadata`에 등록되게 한다 (Alembic autogenerate가
   이걸 보고 변경을 감지한다).
3. `alembic revision --autogenerate -m "..."`로 마이그레이션을 생성한다.

향후 Phase 3+에서 `Round`, `Hole`, `Course`, `Diary`, `Group`, `Bet` 등의 모델이 이 패턴으로
추가된다 (전체 데이터 모델은 루트 README의 ERD 참고).
