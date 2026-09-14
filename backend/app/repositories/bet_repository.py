"""Bet/BetResult 테이블 접근 전용 계층."""
from sqlalchemy.orm import Session, selectinload

from app.models.bet import Bet
from app.models.bet_result import BetResult


def create(db: Session, **fields) -> Bet:
    bet = Bet(**fields)
    db.add(bet)
    db.flush()
    return bet


def create_results(db: Session, bet_id: int, results: list[dict]) -> None:
    for result in results:
        db.add(BetResult(bet_id=bet_id, **result))
    db.flush()


def get_by_id(db: Session, bet_id: int) -> Bet | None:
    return (
        db.query(Bet)
        .options(selectinload(Bet.results).selectinload(BetResult.user))
        .filter(Bet.id == bet_id)
        .first()
    )


def list_by_group(db: Session, group_id: int) -> list[Bet]:
    return (
        db.query(Bet)
        .filter(Bet.group_id == group_id)
        .order_by(Bet.bet_date.desc())
        .all()
    )
