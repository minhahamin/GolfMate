"""골프장 추천 엔드포인트 테스트.

실제 OpenRouter 호출은 하지 않는다 — get_coach_llm을 모킹해서 네트워크/비용 없이
그래프의 분기(후보 없음/정상/환각 방지/LLM 실패)를 검증한다.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.course import Course
from app.models.course_hole import CourseHole
from tests.conftest import auth_headers, register_and_get_token

client = TestClient(app)


def _seed_recommend_course(**overrides) -> int:
    db = SessionLocal()
    try:
        import uuid

        defaults = {
            "name": f"추천테스트코스-{uuid.uuid4().hex[:8]}",
            "region": "경기도 용인",
            "address": "테스트 주소",
            "description": "테스트용 코스",
            "holes_count": 3,
            "par": 11,
            "difficulty": "초급",
            "green_fee_avg": 100000,
            "tags": "테스트",
        }
        defaults.update(overrides)
        course = Course(**defaults)
        db.add(course)
        db.flush()
        for hole_number, par in enumerate([4, 3, 4], start=1):
            db.add(CourseHole(course_id=course.id, hole_number=hole_number, par=par, distance_meters=300))
        db.commit()
        return course.id
    finally:
        db.close()


def _sample_response(course_id: int) -> str:
    return f"""[총평]
조건에 맞는 곳으로 이 코스를 추천합니다.

[1위]
id: {course_id}
이유: 난이도와 예산이 사용자에게 잘 맞습니다.
"""


def test_recommend_requires_authentication():
    response = client.post("/api/ai/recommend-courses", json={})

    assert response.status_code == 401


def test_recommend_with_no_matching_candidates_skips_llm():
    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/ai/recommend-courses",
        headers=auth_headers(token),
        json={"region": "존재하지않는지역이름12345"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["recommendations"] == []
    assert "찾지 못했습니다" in body["summary"]


@patch("app.ai.recommend.graph.get_coach_llm")
def test_recommend_returns_ranked_course_from_candidates(mock_get_llm):
    course_id = _seed_recommend_course(region="경기도 용인특이지역", difficulty="초급")
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response(course_id))
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/ai/recommend-courses",
        headers=auth_headers(token),
        json={"region": "용인특이지역"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["course"]["id"] == course_id
    assert "난이도" in body["recommendations"][0]["reason"]


@patch("app.ai.recommend.graph.get_coach_llm")
def test_llm_hallucinated_course_id_is_discarded(mock_get_llm):
    _seed_recommend_course(region="환각테스트지역")
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response(999999))
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/ai/recommend-courses",
        headers=auth_headers(token),
        json={"region": "환각테스트지역"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["recommendations"] == []


@patch("app.ai.recommend.graph.get_coach_llm")
def test_recommend_llm_failure_returns_fallback(mock_get_llm):
    _seed_recommend_course(region="실패테스트지역")
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("upstream timeout")
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/ai/recommend-courses",
        headers=auth_headers(token),
        json={"region": "실패테스트지역"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["recommendations"] == []
    assert "실패" in response.json()["summary"]


def test_max_budget_filters_out_expensive_courses():
    _seed_recommend_course(region="예산테스트지역", green_fee_avg=300000)

    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/ai/recommend-courses",
        headers=auth_headers(token),
        json={"region": "예산테스트지역", "max_budget": 50000},
    )

    assert response.status_code == 200
    assert response.json()["recommendations"] == []
