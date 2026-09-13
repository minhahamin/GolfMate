"""GolferProfile 테이블 접근 전용 계층."""
from sqlalchemy.orm import Session

from app.models.golfer_profile import GolferProfile


def get_by_user_id(db: Session, user_id: int) -> GolferProfile | None:
    return db.query(GolferProfile).filter(GolferProfile.user_id == user_id).first()


def create_empty(db: Session, *, user_id: int) -> GolferProfile:
    profile = GolferProfile(user_id=user_id)
    db.add(profile)
    db.flush()
    return profile


def update(db: Session, profile: GolferProfile, fields: dict) -> GolferProfile:
    for key, value in fields.items():
        setattr(profile, key, value)
    db.flush()
    return profile
