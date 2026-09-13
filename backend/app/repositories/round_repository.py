"""Round/Hole 테이블 접근 전용 계층.

모든 조회 함수는 반드시 user_id로 필터링한다 — 다른 사용자의 라운드를 절대 반환하지 않는다.
"""
from sqlalchemy.orm import Session, selectinload

from app.models.hole import Hole
from app.models.round import Round


def list_by_user(db: Session, user_id: int) -> list[Round]:
    return (
        db.query(Round)
        .options(selectinload(Round.course))
        .filter(Round.user_id == user_id)
        .order_by(Round.round_date.desc())
        .all()
    )


def list_recent_by_user(db: Session, user_id: int, limit: int) -> list[Round]:
    return (
        db.query(Round)
        .options(selectinload(Round.holes))
        .filter(Round.user_id == user_id)
        .order_by(Round.round_date.desc())
        .limit(limit)
        .all()
    )


def get_by_id_for_user(db: Session, round_id: int, user_id: int) -> Round | None:
    return (
        db.query(Round)
        .options(selectinload(Round.course), selectinload(Round.holes))
        .filter(Round.id == round_id, Round.user_id == user_id)
        .first()
    )


def create(db: Session, **fields) -> Round:
    round_ = Round(**fields)
    db.add(round_)
    db.flush()
    return round_


def replace_holes(db: Session, round_id: int, holes: list[dict]) -> None:
    db.query(Hole).filter(Hole.round_id == round_id).delete()
    for hole_fields in holes:
        db.add(Hole(round_id=round_id, **hole_fields))
    db.flush()


def update_fields(db: Session, round_: Round, fields: dict) -> Round:
    for key, value in fields.items():
        setattr(round_, key, value)
    db.flush()
    return round_


def delete(db: Session, round_: Round) -> None:
    db.delete(round_)
    db.flush()
