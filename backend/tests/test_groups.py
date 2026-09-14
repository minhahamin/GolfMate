"""그룹 CRUD, 멤버 관리, 소유권(다른 사용자 접근 차단) 테스트."""
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import auth_headers, register_and_get_token

client = TestClient(app)


def test_create_group_adds_owner_as_member():
    token, user = register_and_get_token(client)

    response = client.post("/api/groups", headers=auth_headers(token), json={"name": "주말 골프 모임"})

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["owner_id"] == user["id"]
    assert len(body["members"]) == 1
    assert body["members"][0]["user_id"] == user["id"]


def test_non_member_cannot_access_group():
    token_a, _ = register_and_get_token(client)
    token_b, _ = register_and_get_token(client)

    created = client.post(
        "/api/groups", headers=auth_headers(token_a), json={"name": "비공개 모임"}
    ).json()

    response = client.get(f"/api/groups/{created['id']}", headers=auth_headers(token_b))

    assert response.status_code == 404


def test_list_groups_only_shows_my_groups():
    token_a, _ = register_and_get_token(client)
    token_b, _ = register_and_get_token(client)

    client.post("/api/groups", headers=auth_headers(token_a), json={"name": "A의 모임"})

    response_a = client.get("/api/groups", headers=auth_headers(token_a))
    response_b = client.get("/api/groups", headers=auth_headers(token_b))

    assert len(response_a.json()) >= 1
    names_b = [g["name"] for g in response_b.json()]
    assert "A의 모임" not in names_b


def test_owner_can_add_member_by_email():
    token_owner, _ = register_and_get_token(client)
    token_friend, friend = register_and_get_token(client)

    group = client.post(
        "/api/groups", headers=auth_headers(token_owner), json={"name": "모임"}
    ).json()

    response = client.post(
        f"/api/groups/{group['id']}/members",
        headers=auth_headers(token_owner),
        json={"email": friend["email"]},
    )

    assert response.status_code == 201, response.text
    member_ids = [m["user_id"] for m in response.json()["members"]]
    assert friend["id"] in member_ids

    # 친구도 이제 그룹에 접근할 수 있어야 한다
    friend_view = client.get(f"/api/groups/{group['id']}", headers=auth_headers(token_friend))
    assert friend_view.status_code == 200


def test_non_owner_cannot_add_member():
    token_owner, _ = register_and_get_token(client)
    token_member, member = register_and_get_token(client)
    token_outsider, outsider = register_and_get_token(client)

    group = client.post(
        "/api/groups", headers=auth_headers(token_owner), json={"name": "모임"}
    ).json()
    client.post(
        f"/api/groups/{group['id']}/members",
        headers=auth_headers(token_owner),
        json={"email": member["email"]},
    )

    response = client.post(
        f"/api/groups/{group['id']}/members",
        headers=auth_headers(token_member),
        json={"email": outsider["email"]},
    )

    assert response.status_code == 403


def test_adding_nonexistent_email_returns_404():
    token_owner, _ = register_and_get_token(client)
    group = client.post(
        "/api/groups", headers=auth_headers(token_owner), json={"name": "모임"}
    ).json()

    response = client.post(
        f"/api/groups/{group['id']}/members",
        headers=auth_headers(token_owner),
        json={"email": "no-such-user@example.com"},
    )

    assert response.status_code == 404


def test_member_can_leave_but_owner_cannot():
    token_owner, owner = register_and_get_token(client)
    token_member, member = register_and_get_token(client)

    group = client.post(
        "/api/groups", headers=auth_headers(token_owner), json={"name": "모임"}
    ).json()
    client.post(
        f"/api/groups/{group['id']}/members",
        headers=auth_headers(token_owner),
        json={"email": member["email"]},
    )

    leave_response = client.delete(
        f"/api/groups/{group['id']}/members/{member['id']}", headers=auth_headers(token_member)
    )
    assert leave_response.status_code == 204

    owner_leave_response = client.delete(
        f"/api/groups/{group['id']}/members/{owner['id']}", headers=auth_headers(token_owner)
    )
    assert owner_leave_response.status_code == 400
