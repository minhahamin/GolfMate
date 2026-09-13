"""Hole 테이블 — 라운드에서 실제로 플레이한 홀별 기록 (Shot-level 데이터는 향후 확장)."""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.round import Round


class Hole(Base):
    __tablename__ = "holes"
    __table_args__ = (UniqueConstraint("round_id", "hole_number", name="uq_round_hole_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False)
    hole_number: Mapped[int] = mapped_column(Integer, nullable=False)
    par: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    putts: Mapped[int] = mapped_column(Integer, nullable=False)
    fairway_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    gir: Mapped[bool] = mapped_column(Boolean, default=False)
    ob: Mapped[int] = mapped_column(Integer, default=0)
    bunker: Mapped[int] = mapped_column(Integer, default=0)
    penalty: Mapped[int] = mapped_column(Integer, default=0)

    round: Mapped["Round"] = relationship(back_populates="holes")
