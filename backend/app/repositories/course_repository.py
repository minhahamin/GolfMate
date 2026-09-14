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


def search(
    db: Session,
    *,
    region: str | None = None,
    difficulty: str | None = None,
    max_budget: int | None = None,
) -> list[Course]:
    """Phase 7 골프장 추천용 후보 검색. AI는 이 함수가 돌려준 목록 안에서만 추천한다."""
    query = db.query(Course)
    if region:
        query = query.filter(Course.region.ilike(f"%{region}%"))
    if difficulty:
        query = query.filter(Course.difficulty == difficulty)
    if max_budget is not None:
        query = query.filter(
            (Course.green_fee_avg.is_(None)) | (Course.green_fee_avg <= max_budget)
        )
    return query.order_by(Course.name).all()
