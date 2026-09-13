# models/ — SQLAlchemy ORM

현재 정의된 모델:

- **User** (`user.py`) — 계정 정보. `id`, `email`(unique), `hashed_password`, `name`,
  `created_at`, `updated_at`. 회원가입/로그인 API는 Phase 2에서 구현하지만, 테이블 구조는
  지금 확정한다.
- **GolferProfile** (`golfer_profile.py`) — User와 1:1. AI Coach/Caddie가 참고하는 실력 지표:
  `handicap`, `average_score`, `driver_distance`, `iron_distance`, `putting_average`,
  `fairway_percentage`, `gir_percentage`, `preferred_tee`, `goal_score`.
- **Course** (`course.py`) — 골프장 기본 정보 (`name`, `region`, `address`, `description`,
  `holes_count`, `par`). Phase 3은 `seed_courses.py`로 넣은 mock 데이터만 쓰고, Phase 7에서
  실제 API/DB로 교체돼도 이 테이블 구조는 유지된다.
- **CourseHole** (`course_hole.py`) — 코스의 홀별 고정 정보(`hole_number`, `par`,
  `distance_meters`). 라운드 실제 기록인 `Hole`과는 다른 테이블이다.
- **Round** (`round.py`) — 사용자가 실제로 플레이한 라운드. `user_id`, `course_id`,
  `round_date`, `score`, `weather`, `temperature`, `wind`, `memo`.
- **Hole** (`hole.py`) — 라운드별 홀 실제 기록. `round_id`, `hole_number`, `par`, `score`,
  `putts`, `fairway_hit`, `gir`, `ob`, `bunker`, `penalty`. Shot(샷 단위) 테이블은 아직 없다 —
  필요해지면 `Hole` 아래에 1:N으로 추가하면 된다.

## 새 모델을 추가할 때

1. 이 폴더에 `xxx.py`를 만들고 `Base`를 상속한다.
2. `__init__.py`에서 import를 추가해 `Base.metadata`에 등록되게 한다 (Alembic autogenerate가
   이걸 보고 변경을 감지한다).
3. `alembic revision --autogenerate -m "..."`로 마이그레이션을 생성한다.

향후 Phase 6+에서 `Diary`, `Group`, `Bet` 등의 모델이 이 패턴으로 추가된다 (전체 데이터 모델은
루트 README의 ERD 참고).
