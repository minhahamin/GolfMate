# alembic/ — DB 마이그레이션

`env.py`는 `app.core.config.Settings`에서 `DATABASE_URL`을 읽어 alembic.ini의 placeholder URL을
덮어쓰고, `app.models.Base.metadata`를 대상으로 autogenerate를 수행한다.

## 새 마이그레이션 만들기

```bash
cd backend
alembic revision --autogenerate -m "설명"
alembic upgrade head
```

`--autogenerate`가 정확히 동작하려면 `app/models/__init__.py`에 새 모델의 import가
추가되어 있어야 한다.

## 현재 리비전

- `20260913_233226_create_users_and_golfer_profiles.py` — `users`, `golfer_profiles` 테이블 생성.
