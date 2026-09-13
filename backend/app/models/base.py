"""모든 ORM 모델이 상속하는 Declarative Base.

Alembic의 autogenerate가 테이블을 인식하려면 모든 모델이
이 Base의 metadata에 등록되어 있어야 한다.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
