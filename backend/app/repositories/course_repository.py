"""Course 테이블 접근 전용 계층."""
from sqlalchemy import func, or_
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
    limit: int | None = None,
) -> list[Course]:
    """Phase 7 골프장 추천용 후보 검색. AI는 이 함수가 돌려준 목록 안에서만 추천한다.

    가상(is_demo) 코스는 제외한다. 실제 골프장 데이터에는 난이도/그린피가 없어(NULL) 해당
    필터는 값이 없는 코스를 탈락시키지 않는다. limit이 있으면 무작위로 그 수만큼만 돌려준다
    (전국 500여 곳을 통째로 LLM에 넘길 수 없다).
    """
    query = db.query(Course).filter(Course.is_demo.is_(False))
    if region:
        query = query.filter(Course.region.ilike(f"%{region}%"))
    if difficulty:
        query = query.filter(or_(Course.difficulty.is_(None), Course.difficulty == difficulty))
    if max_budget is not None:
        query = query.filter(
            (Course.green_fee_avg.is_(None)) | (Course.green_fee_avg <= max_budget)
        )
    if limit is not None:
        return query.order_by(func.random()).limit(limit).all()
    return query.order_by(Course.name).all()
