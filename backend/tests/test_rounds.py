"""라운드 CRUD, 통계 계산, 소유권(다른 사용자 접근 차단) 테스트."""
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import auth_headers, register_and_get_token, seed_test_course

client = TestClient(app)


def _round_payload(course_id: int, **overrides) -> dict:
    payload = {
        "course_id": course_id,
        "round_date": "2026-05-01",
        "weather": "맑음",
        "temperature": 22.5,
        "wind": "약함",
        "memo": "테스트 라운드",
    }
    payload.update(overrides)
    return payload


def _hole(hole_number: int, par: int, score: int, putts: int = 2, **overrides) -> dict:
    hole = {
        "hole_number": hole_number,
        "par": par,
        "score": score,
        "putts": putts,
        "fairway_hit": True,
        "gir": False,
        "ob": 0,
        "bunker": 0,
        "penalty": 0,
    }
    hole.update(overrides)
    return hole


def test_create_round_with_score_only():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()

    response = client.post(
        "/api/rounds",
        headers=auth_headers(token),
        json=_round_payload(course_id, score=95),
    )

    assert response.status_code == 201, response.text
    assert response.json()["score"] == 95
    assert response.json()["holes"] == []


def test_create_round_without_score_or_holes_returns_422():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()

    response = client.post("/api/rounds", headers=auth_headers(token), json=_round_payload(course_id))

    assert response.status_code == 422


def test_create_round_with_holes_computes_score():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    holes = [_hole(1, 4, 5), _hole(2, 3, 4), _hole(3, 4, 4)]

    response = client.post(
        "/api/rounds", headers=auth_headers(token), json=_round_payload(course_id, holes=holes)
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["score"] == 13  # 5+4+4
    assert len(body["holes"]) == 3


def test_list_rounds_only_shows_own_rounds():
    token_a, _ = register_and_get_token(client)
    token_b, _ = register_and_get_token(client)
    course_id = seed_test_course()

    client.post("/api/rounds", headers=auth_headers(token_a), json=_round_payload(course_id, score=90))

    response_a = client.get("/api/rounds", headers=auth_headers(token_a))
    response_b = client.get("/api/rounds", headers=auth_headers(token_b))

    assert len(response_a.json()) >= 1
    assert response_b.json() == []


def test_other_user_cannot_access_round():
    token_a, _ = register_and_get_token(client)
    token_b, _ = register_and_get_token(client)
    course_id = seed_test_course()

    created = client.post(
        "/api/rounds", headers=auth_headers(token_a), json=_round_payload(course_id, score=88)
    ).json()

    response = client.get(f"/api/rounds/{created['id']}", headers=auth_headers(token_b))

    assert response.status_code == 404


def test_update_round_replaces_holes_and_recomputes_score():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    created = client.post(
        "/api/rounds", headers=auth_headers(token), json=_round_payload(course_id, score=90)
    ).json()

    new_holes = [_hole(1, 4, 4), _hole(2, 3, 3), _hole(3, 4, 5)]
    response = client.put(
        f"/api/rounds/{created['id']}", headers=auth_headers(token), json={"holes": new_holes}
    )

    assert response.status_code == 200
    assert response.json()["score"] == 12  # 4+3+5
    assert len(response.json()["holes"]) == 3


def test_delete_round():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    created = client.post(
        "/api/rounds", headers=auth_headers(token), json=_round_payload(course_id, score=90)
    ).json()

    delete_response = client.delete(f"/api/rounds/{created['id']}", headers=auth_headers(token))
    get_response = client.get(f"/api/rounds/{created['id']}", headers=auth_headers(token))

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_round_analysis_with_hole_detail():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    # 파4=5(보기), 파3=3(파), 파4=4(파) -> 총파11, 총스코어12, score_to_par=+1
    holes = [
        _hole(1, 4, 5, putts=2, fairway_hit=True, gir=False),
        _hole(2, 3, 3, putts=1, fairway_hit=True, gir=True),
        _hole(3, 4, 4, putts=2, fairway_hit=False, gir=True),
    ]
    created = client.post(
        "/api/rounds", headers=auth_headers(token), json=_round_payload(course_id, holes=holes)
    ).json()

    response = client.get(f"/api/rounds/{created['id']}/analysis", headers=auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["has_hole_detail"] is True
    assert body["score_to_par"] == 1
    assert body["putts_total"] == 5
    assert body["gir_rate"] == round(2 / 3 * 100, 1)


def test_analysis_without_hole_detail_returns_score_to_par_only():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()  # 테스트 코스 파 총합 11
    created = client.post(
        "/api/rounds", headers=auth_headers(token), json=_round_payload(course_id, score=15)
    ).json()

    response = client.get(f"/api/rounds/{created['id']}/analysis", headers=auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["has_hole_detail"] is False
    assert body["score_to_par"] == 4  # 15 - 11
    assert body["putts_total"] is None


def test_statistics_summary_aggregates_recent_rounds():
    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    client.post(
        "/api/rounds",
        headers=auth_headers(token),
        json=_round_payload(course_id, round_date="2026-04-01", score=100),
    )
    client.post(
        "/api/rounds",
        headers=auth_headers(token),
        json=_round_payload(course_id, round_date="2026-04-08", score=90),
    )

    response = client.get("/api/rounds/statistics/summary", headers=auth_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["rounds_count"] == 2
    assert body["best_score"] == 90
    assert body["average_score"] == 95.0
