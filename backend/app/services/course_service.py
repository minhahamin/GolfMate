"""골프장 조회 비즈니스 로직. Phase 3은 mock 데이터만 있고, Phase 7에서 추천 로직이 붙는다."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.course import Course
from app.repositories import course_repository


def list_courses(db: Session) -> list[Course]:
    return course_repository.list_all(db)


def get_course_detail(db: Session, course_id: int) -> Course:
    course = course_repository.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="골프장을 찾을 수 없습니다.")
    return course
