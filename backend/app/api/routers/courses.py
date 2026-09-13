"""골프장 조회 엔드포인트. 로그인 여부와 무관하게 공개된다."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.course import CourseDetailRead, CourseRead
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db)) -> list[CourseRead]:
    return course_service.list_courses(db)


@router.get("/{course_id}", response_model=CourseDetailRead)
def get_course(course_id: int, db: Session = Depends(get_db)) -> CourseDetailRead:
    return course_service.get_course_detail(db, course_id)
