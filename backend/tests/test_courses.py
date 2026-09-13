"""골프장 조회 엔드포인트 테스트 (인증 불필요, 공개 API)."""
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import seed_test_course

client = TestClient(app)


def test_list_courses_includes_seeded_course():
    course_id = seed_test_course()

    response = client.get("/api/courses")

    assert response.status_code == 200
    assert any(c["id"] == course_id for c in response.json())


def test_get_course_detail_includes_holes():
    course_id = seed_test_course()

    response = client.get(f"/api/courses/{course_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == course_id
    assert len(body["holes"]) == 3
    assert body["holes"][0]["hole_number"] == 1


def test_get_nonexistent_course_returns_404():
    response = client.get("/api/courses/999999999")

    assert response.status_code == 404
