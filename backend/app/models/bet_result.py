"""BetResult 테이블 — 내기 한 건에서 참가자 1명의 스코어와 정산 금액.

payout_amount은 bet_service.calculate_settlement()가 계산한 값을 그대로 저장한다 —
LLM은 이 숫자를 절대 다시 계산하지 않고 설명(코멘터리)만 담당한다(설계 원칙 5번).
"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.bet import Bet
    from app.models.user import User


class BetResult(Base):
    __tablename__ = "bet_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    bet_id: Mapped[int] = mapped_column(ForeignKey("bets.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    score: Mapped[int] = mapped_column(Integer, nullable=False)
    payout_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    bet: Mapped["Bet"] = relationship(back_populates="results")
    user: Mapped["User"] = relationship()
