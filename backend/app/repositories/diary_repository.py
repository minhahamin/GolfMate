"""Diary 테이블 접근 전용 계층.

모든 조회 함수는 반드시 user_id로 필터링한다 — 다른 사용자의 일기를 절대 반환하지 않는다.
"""
from sqlalchemy.orm import Session, selectinload

from app.models.diary import Diary
from app.models.round import Round


def list_by_user(db: Session, user_id: int) -> list[Diary]:
    return (
        db.query(Diary)
        .filter(Diary.user_id == user_id)
        .order_by(Diary.created_at.desc())
        .all()
    )


def get_by_id_for_user(db: Session, diary_id: int, user_id: int) -> Diary | None:
    return (
        db.query(Diary)
        .options(selectinload(Diary.round).selectinload(Round.course))
        .filter(Diary.id == diary_id, Diary.user_id == user_id)
        .first()
    )


def create(db: Session, **fields) -> Diary:
    diary = Diary(**fields)
    db.add(diary)
    db.flush()
    return diary


def delete(db: Session, diary: Diary) -> None:
    db.delete(diary)
    db.flush()
