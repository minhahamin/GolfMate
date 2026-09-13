# repositories/ — DB 접근 계층

현재는 빈 스캐폴드다. Phase 1의 헬스체크는 로직이 없어 라우터에서 직접
`db.execute(text("SELECT 1"))`를 호출하지만, 실제 도메인 데이터(User, GolferProfile, Round...)를
다루기 시작하는 Phase 2부터 이 계층을 채운다.

목표:

```python
class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None: ...
    def create(self, db: Session, user: UserCreate) -> User: ...
```

Service는 SQLAlchemy Session이나 쿼리문을 직접 다루지 않고, 이 Repository의 메서드만 호출한다.
이렇게 분리해두면 이후 쿼리 최적화나 캐싱을 추가할 때 Service/Router 코드를 건드리지 않아도 된다.
