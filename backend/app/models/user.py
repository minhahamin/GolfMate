"""User 테이블.

회원가입/로그인(JWT) 로직 자체는 Phase 2에서 구현한다.
Phase 1에서는 데이터 구조와 마이그레이션만 먼저 확정한다.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.golfer_profile import GolferProfile


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    golfer_profile: Mapped["GolferProfile | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
