"""Bet 테이블 — 그룹이 특정 라운드에서 한 내기 한 건.

Round은 사용자 1명 소유라 그룹원 여러 명의 같은 날 스코어를 한 라운드로 묶을 방법이 없다 —
그래서 Bet은 Round를 참조하지 않고 스코어를 BetResult에 직접 기록한다(bet_service.py 참고).
"""
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.bet_result import BetResult


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    bet_date: Mapped[date] = mapped_column(Date, nullable=False)
    course_name: Mapped[str] = mapped_column(String(200), nullable=False)
    stake_per_stroke: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    results: Mapped[list["BetResult"]] = relationship(
        back_populates="bet", cascade="all, delete-orphan"
    )
