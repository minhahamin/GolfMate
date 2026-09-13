"""Course 테이블 접근 전용 계층."""
from sqlalchemy.orm import Session, selectinload

from app.models.course import Course


def list_all(db: Session) -> list[Course]:
    return db.query(Course).order_by(Course.name).all()


def get_by_id(db: Session, course_id: int) -> Course | None:
    return (
        db.query(Course)
        .options(selectinload(Course.holes))
        .filter(Course.id == course_id)
        .first()
    )
