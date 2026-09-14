"""AI 캐디 엔드포인트 테스트.

실제 OpenRouter 호출과 실제 Open-Meteo 호출 모두 하지 않는다 — get_coach_llm과
get_current_weather를 모킹해서 네트워크/비용 없이 그래프의 분기(좌표 없음/날씨 실패/
정상/LLM 실패)를 검증한다.
"""
import uuid
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.course import Course
from app.models.course_hole import CourseHole
from tests.conftest import auth_headers, register_and_get_token, seed_test_course

client = TestClient(app)

SAMPLE_LLM_RESPONSE = """[홀공략]
정면 페어웨이 중앙을 겨냥해 안전하게 티샷하세요.

[위험요소]
오른쪽 러프와 그린 앞 벙커를 주의해야 합니다.

[클럽전략]
바람을 고려해 평소보다 한 클럽 길게 잡으세요.
"""


def _seed_course_with_coordinates(**overrides) -> int:
    db = SessionLocal()
    try:
        defaults = {
            "name": f"캐디테스트코스-{uuid.uuid4().hex[:8]}",
            "region": "테스트지역",
            "par": 11,
            "holes_count": 3,
            "difficulty": "중급",
            "latitude": 37.5665,
            "longitude": 126.9780,
        }
        defaults.update(overrides)
        course = Course(**defaults)
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


def test_caddie_requires_authentication():
    response = client.post("/api/ai/caddie", json={"course_id": 1, "hole_number": 1})

    assert response.status_code == 401


def test_caddie_with_nonexistent_course_returns_404():
    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/ai/caddie", headers=auth_headers(token), json={"course_id": 999999, "hole_number": 1}
    )

    assert response.status_code == 404


def test_caddie_with_invalid_hole_number_returns_404():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()  # 3홀짜리 테스트 코스

    response = client.post(
        "/api/ai/caddie", headers=auth_headers(token), json={"course_id": course_id, "hole_number": 10}
    )

    assert response.status_code == 404


@patch("app.ai.caddie.graph.get_coach_llm")
def test_caddie_without_coordinates_skips_weather(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=SAMPLE_LLM_RESPONSE)
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)
    course_id = seed_test_course()  # 좌표 없는 테스트 코스

    response = client.post(
        "/api/ai/caddie", headers=auth_headers(token), json={"course_id": course_id, "hole_number": 1}
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "좌표 미등록" in body["weather_summary"]
    assert "클럽" in body["club_strategy"] or body["club_strategy"]
    mock_llm.invoke.assert_called_once()


@patch("app.ai.caddie.graph.get_current_weather")
@patch("app.ai.caddie.graph.get_coach_llm")
def test_caddie_with_weather_returns_sections(mock_get_llm, mock_get_weather):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=SAMPLE_LLM_RESPONSE)
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm
    mock_get_weather.return_value = {
        "temperature_c": 22.5,
        "wind_speed_kmh": 15.0,
        "precipitation_mm": 0.0,
        "condition": "맑음",
    }

    token, _ = register_and_get_token(client)
    course_id = _seed_course_with_coordinates()

    response = client.post(
        "/api/ai/caddie",
        headers=auth_headers(token),
        json={"course_id": course_id, "hole_number": 2, "question": "이 홀 어떻게 공략해야 해?"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "맑음" in body["weather_summary"]
    assert "페어웨이" in body["hole_analysis"]
    assert "벙커" in body["risk_analysis"]
    assert "클럽" in body["club_strategy"]

    prompt = mock_llm.invoke.call_args[0][0]
    assert "2번 홀" in prompt
    assert "파3" in prompt


@patch("app.ai.caddie.graph.get_current_weather")
@patch("app.ai.caddie.graph.get_coach_llm")
def test_caddie_weather_fetch_failure_still_returns_advice(mock_get_llm, mock_get_weather):
    from app.ai.weather.client import WeatherFetchError

    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=SAMPLE_LLM_RESPONSE)
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm
    mock_get_weather.side_effect = WeatherFetchError("boom")

    token, _ = register_and_get_token(client)
    course_id = _seed_course_with_coordinates()

    response = client.post(
        "/api/ai/caddie", headers=auth_headers(token), json={"course_id": course_id, "hole_number": 1}
    )

    assert response.status_code == 200, response.text
    assert "가져오지 못했습니다" in response.json()["weather_summary"]


@patch("app.ai.caddie.graph.get_coach_llm")
def test_caddie_llm_failure_returns_fallback(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("upstream timeout")
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)
    course_id = seed_test_course()

    response = client.post(
        "/api/ai/caddie", headers=auth_headers(token), json={"course_id": course_id, "hole_number": 1}
    )

    assert response.status_code == 200, response.text
    assert "실패" in response.json()["hole_analysis"]
