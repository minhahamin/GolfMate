"""모든 모델을 여기서 import해두어야 Base.metadata에 등록되고,
Alembic autogenerate가 테이블 변경을 감지할 수 있다.
"""
from app.models.base import Base
from app.models.golfer_profile import GolferProfile
from app.models.user import User

__all__ = ["Base", "User", "GolferProfile"]
