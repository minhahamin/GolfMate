"""내기 생성/조회, 정산 계산이 API 레벨에서 올바르게 반영되는지, 소유권(그룹 멤버가
아니면 접근 불가)을 검증한다.
"""
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import auth_headers, register_and_get_token

client = TestClient(app)


def _make_group_with_two_members(owner_token, friend_email):
    group = client.post(
        "/api/groups", headers=auth_headers(owner_token), json={"name": "내기 모임"}
    ).json()
    client.post(
        f"/api/groups/{group['id']}/members",
        headers=auth_headers(owner_token),
        json={"email": friend_email},
    )
    return group


def test_create_bet_computes_settlement():
    token_owner, owner = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)
    group = _make_group_with_two_members(token_owner, friend["email"])

    response = client.post(
        f"/api/groups/{group['id']}/bets",
        headers=auth_headers(token_owner),
        json={
            "title": "주말 라운드 내기",
            "bet_date": "2026-05-01",
            "course_name": "그린힐 컨트리클럽",
            "stake_per_stroke": 1000,
            "scores": {str(owner["id"]): 88, str(friend["id"]): 95},
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    results_by_user = {r["user_id"]: r for r in body["results"]}
    assert results_by_user[owner["id"]]["payout_amount"] == 7000
    assert results_by_user[friend["id"]]["payout_amount"] == -7000


def test_create_bet_with_non_member_score_returns_400():
    token_owner, owner = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)
    _, outsider = register_and_get_token(client)
    group = _make_group_with_two_members(token_owner, friend["email"])

    response = client.post(
        f"/api/groups/{group['id']}/bets",
        headers=auth_headers(token_owner),
        json={
            "title": "내기",
            "bet_date": "2026-05-01",
            "course_name": "코스",
            "stake_per_stroke": 1000,
            "scores": {str(owner["id"]): 88, str(outsider["id"]): 95},
        },
    )

    assert response.status_code == 400


def test_create_bet_with_single_participant_returns_422():
    token_owner, owner = register_and_get_token(client)
    group = client.post(
        "/api/groups", headers=auth_headers(token_owner), json={"name": "모임"}
    ).json()

    response = client.post(
        f"/api/groups/{group['id']}/bets",
        headers=auth_headers(token_owner),
        json={
            "title": "내기",
            "bet_date": "2026-05-01",
            "course_name": "코스",
            "stake_per_stroke": 1000,
            "scores": {str(owner["id"]): 88},
        },
    )

    assert response.status_code == 422


def test_non_member_cannot_view_bet():
    token_owner, owner = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)
    token_outsider, _ = register_and_get_token(client)
    group = _make_group_with_two_members(token_owner, friend["email"])

    bet = client.post(
        f"/api/groups/{group['id']}/bets",
        headers=auth_headers(token_owner),
        json={
            "title": "내기",
            "bet_date": "2026-05-01",
            "course_name": "코스",
            "stake_per_stroke": 1000,
            "scores": {str(owner["id"]): 88, str(friend["id"]): 95},
        },
    ).json()

    response = client.get(f"/api/bets/{bet['id']}", headers=auth_headers(token_outsider))

    assert response.status_code == 404


def test_list_bets_for_group():
    token_owner, owner = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)
    group = _make_group_with_two_members(token_owner, friend["email"])

    client.post(
        f"/api/groups/{group['id']}/bets",
        headers=auth_headers(token_owner),
        json={
            "title": "내기1",
            "bet_date": "2026-05-01",
            "course_name": "코스",
            "stake_per_stroke": 1000,
            "scores": {str(owner["id"]): 88, str(friend["id"]): 95},
        },
    )

    response = client.get(f"/api/groups/{group['id']}/bets", headers=auth_headers(token_friend))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "내기1"
