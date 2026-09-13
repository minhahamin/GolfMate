"""AI Coach 엔드포인트 테스트.

실제 OpenRouter 호출은 하지 않는다 — get_coach_llm을 모킹해서 네트워크/비용 없이
그래프의 분기(데이터 없음/정상/LLM 실패)를 검증한다.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import auth_headers, register_and_get_token, seed_test_course

client = TestClient(app)

SAMPLE_LLM_RESPONSE = """[현재 상태]
최근 평균 스코어가 꾸준히 유지되고 있습니다.

[가장 큰 문제]
페어웨이 적중률이 낮습니다.

[문제의 원인]
드라이버 방향성이 일정하지 않습니다.

[추천 전략]
스윙 템포를 일정하게 유지하는 연습을 하세요.

[다음 라운드 목표]
페어웨이 적중률 50% 달성.
"""


def _create_round(token: str, course_id: int, score: int = 90) -> None:
    response = client.post(
        "/api/rounds",
        headers=auth_headers(token),
        json={"course_id": course_id, "round_date": "2026-05-01", "score": score},
    )
    assert response.status_code == 201, response.text


def test_coach_requires_authentication():
    response = client.post("/api/ai/coach", json={"question": ""})

    assert response.status_code == 401


def test_coach_without_rounds_returns_no_data_message():
    token, _ = register_and_get_token(client)

    response = client.post("/api/ai/coach", headers=auth_headers(token), json={"question": ""})

    assert response.status_code == 200
    body = response.json()
    assert "라운드가 없어" in body["current_state"]


@patch("app.ai.coach.graph.get_coach_llm")
def test_coach_with_rounds_returns_parsed_sections(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=SAMPLE_LLM_RESPONSE)
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    _create_round(token, course_id)

    response = client.post(
        "/api/ai/coach", headers=auth_headers(token), json={"question": "요즘 스코어가 안 줄어요"}
    )

    assert response.status_code == 200
    body = response.json()
    assert "페어웨이" in body["biggest_problem"]
    assert body["strategy"]
    mock_llm.invoke.assert_called_once()


@patch("app.ai.coach.graph.get_coach_llm")
def test_coach_llm_failure_returns_fallback(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("upstream timeout")
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    _create_round(token, course_id)

    response = client.post("/api/ai/coach", headers=auth_headers(token), json={"question": ""})

    assert response.status_code == 200
    body = response.json()
    assert "실패" in body["current_state"]
