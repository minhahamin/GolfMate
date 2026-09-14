"""내기 AI 코멘터리 테스트. 실제 OpenRouter 호출은 하지 않는다 — get_coach_llm을 모킹해서
네트워크/비용 없이 정상/실패 분기를 검증하고, 정산 금액이 LLM 호출 전에 이미 확정되어
프롬프트에 그대로 전달되는지 확인한다.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import auth_headers, register_and_get_token

client = TestClient(app)


def _make_bet(token_owner, owner, token_friend, friend):
    group = client.post(
        "/api/groups", headers=auth_headers(token_owner), json={"name": "내기 모임"}
    ).json()
    client.post(
        f"/api/groups/{group['id']}/members",
        headers=auth_headers(token_owner),
        json={"email": friend["email"]},
    )
    return client.post(
        f"/api/groups/{group['id']}/bets",
        headers=auth_headers(token_owner),
        json={
            "title": "주말 내기",
            "bet_date": "2026-05-01",
            "course_name": "그린힐 컨트리클럽",
            "stake_per_stroke": 1000,
            "scores": {str(owner["id"]): 88, str(friend["id"]): 95},
        },
    ).json()


def test_bet_commentary_requires_authentication():
    response = client.post("/api/ai/bet-commentary", json={"bet_id": 1})

    assert response.status_code == 401


def test_non_member_cannot_get_commentary():
    token_owner, owner = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)
    token_outsider, _ = register_and_get_token(client)
    bet = _make_bet(token_owner, owner, token_friend, friend)

    response = client.post(
        "/api/ai/bet-commentary", headers=auth_headers(token_outsider), json={"bet_id": bet["id"]}
    )

    assert response.status_code == 404


@patch("app.ai.bet.graph.get_coach_llm")
def test_commentary_prompt_uses_precomputed_payouts_not_llm_math(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="흥미진진한 내기였네요! 정산 결과를 확인해보세요.")
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token_owner, owner = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)
    bet = _make_bet(token_owner, owner, token_friend, friend)

    response = client.post(
        "/api/ai/bet-commentary", headers=auth_headers(token_owner), json={"bet_id": bet["id"]}
    )

    assert response.status_code == 200, response.text
    assert response.json()["commentary"]
    mock_llm.invoke.assert_called_once()

    prompt = mock_llm.invoke.call_args[0][0]
    assert "+7,000원" in prompt or "7,000원" in prompt
    assert "-7,000원" in prompt


@patch("app.ai.bet.graph.get_coach_llm")
def test_commentary_llm_failure_returns_fallback(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("upstream timeout")
    mock_get_llm.return_value = mock_llm

    token_owner, owner = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)
    bet = _make_bet(token_owner, owner, token_friend, friend)

    response = client.post(
        "/api/ai/bet-commentary", headers=auth_headers(token_owner), json={"bet_id": bet["id"]}
    )

    assert response.status_code == 200, response.text
    assert "실패" in response.json()["commentary"]
