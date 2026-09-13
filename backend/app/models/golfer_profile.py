"""GolferProfile 테이블.

User와 1:1 관계이며, AI Coach/Caddie가 참고하는 사용자의 실력 지표를 담는다.
필드는 마스터 스펙(핸디캡, 평균타수, 클럽별 거리, 퍼팅/페어웨이/GIR 등)을 따른다.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class GolferProfile(Base):
    __tablename__ = "golfer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    handicap: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    driver_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    iron_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    putting_average: Mapped[float | None] = mapped_column(Float, nullable=True)
    fairway_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    gir_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_tee: Mapped[str | None] = mapped_column(String(50), nullable=True)
    goal_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="golfer_profile")
