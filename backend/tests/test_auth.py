"""회원가입/로그인/보호된 엔드포인트 통합 테스트.

실제 PostgreSQL 연결이 필요하다 (docker compose up db 로 띄운 상태에서 실행).
이메일 중복을 피하기 위해 테스트마다 uuid로 고유한 이메일을 사용한다.
"""
import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:12]}@example.com"


def _register(email: str, password: str = "password123") -> dict:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": "테스트유저"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_register_returns_token_and_user():
    body = _register(_unique_email())

    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["name"] == "테스트유저"
    assert "hashed_password" not in body["user"]


def test_register_duplicate_email_returns_409():
    email = _unique_email()
    _register(email)

    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "password123", "name": "다른유저"},
    )

    assert response.status_code == 409


def test_login_with_correct_password_succeeds():
    email = _unique_email()
    _register(email, password="correct-password")

    response = client.post(
        "/api/auth/login", json={"email": email, "password": "correct-password"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_returns_401():
    email = _unique_email()
    _register(email, password="correct-password")

    response = client.post(
        "/api/auth/login", json={"email": email, "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_me_requires_authentication():
    response = client.get("/api/users/me")

    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token():
    email = _unique_email()
    body = _register(email)
    token = body["access_token"]

    response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == email


def test_profile_is_auto_created_and_updatable():
    body = _register(_unique_email())
    token = body["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    get_response = client.get("/api/users/me/profile", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["handicap"] is None

    update_response = client.put(
        "/api/users/me/profile", headers=headers, json={"handicap": 18.5}
    )
    assert update_response.status_code == 200
    assert update_response.json()["handicap"] == 18.5
