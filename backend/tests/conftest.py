"""여러 테스트 파일이 공유하는 헬퍼 (계정 생성, 테스트용 코스 시드 등)."""
import uuid

from app.core.database import SessionLocal
from app.models.course import Course
from app.models.course_hole import CourseHole


def unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


def register_and_get_token(client, email: str | None = None, password: str = "password123") -> tuple[str, dict]:
    email = email or unique_email()
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": "테스트유저"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    return body["access_token"], body["user"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def seed_test_course() -> int:
    """홀 3개짜리 간단한 테스트 전용 코스를 만들고 course_id를 반환한다."""
    db = SessionLocal()
    try:
        course = Course(
            name=f"테스트코스-{uuid.uuid4().hex[:8]}", region="테스트지역", par=11, holes_count=3
        )
        db.add(course)
        db.flush()
        for hole_number, par in enumerate([4, 3, 4], start=1):
            db.add(
                CourseHole(course_id=course.id, hole_number=hole_number, par=par, distance_meters=300)
            )
        db.commit()
        return course.id
    finally:
        db.close()
