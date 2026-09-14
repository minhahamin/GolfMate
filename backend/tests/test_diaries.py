"""AI 골프 일기 CRUD, 소유권, LLM 라운드 매칭 테스트.

실제 OpenRouter 호출은 하지 않는다 — get_coach_llm을 모킹해서 네트워크/비용 없이
그래프의 분기(정상/LLM 실패/환각 방지)를 검증한다. 오디오 업로드(STT) 경로는 Whisper
모델 로딩이 느려 여기서는 다루지 않는다 — 텍스트 입력 경로로 서비스/라우터 로직을 검증한다.
"""
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import auth_headers, register_and_get_token, seed_test_course

client = TestClient(app)


def _sample_response(matched_round_id: str = "없음") -> str:
    return f"""[기분]
아쉽지만 만족스러운 하루였다.

[하이라이트]
전반 드라이버 샷감이 좋았다.

[개선점]
후반 퍼팅 거리감이 아쉬웠다.

[다음목표]
다음 라운드에서는 짧은 퍼팅 연습을 더 하기.

[요약]
전반은 좋았지만 후반 퍼팅에서 타수를 잃은 라운드.

[매칭라운드]
{matched_round_id}
"""


def _create_round(token: str, course_id: int, score: int = 90) -> int:
    response = client.post(
        "/api/rounds",
        headers=auth_headers(token),
        json={"course_id": course_id, "round_date": "2026-05-01", "score": score},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_diary_requires_authentication():
    response = client.post("/api/diaries", data={"text": "오늘 라운드 좋았다"})

    assert response.status_code == 401


def test_create_diary_without_text_or_audio_returns_400():
    token, _ = register_and_get_token(client)

    response = client.post("/api/diaries", headers=auth_headers(token), data={})

    assert response.status_code == 400


@patch("app.ai.diary.graph.get_coach_llm")
def test_create_diary_with_text_only_and_no_rounds(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response())
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/diaries", headers=auth_headers(token), data={"text": "오늘 라운드 좋았다"}
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["round_id"] is None
    assert "퍼팅" in body["improvement_points"]
    assert body["raw_text"] == "오늘 라운드 좋았다"


@patch("app.ai.diary.graph.get_coach_llm")
def test_create_diary_with_round_id_hint_overrides_llm_matching(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response(matched_round_id="없음"))
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    round_id = _create_round(token, course_id)

    response = client.post(
        "/api/diaries",
        headers=auth_headers(token),
        data={"text": "오늘 라운드 좋았다", "round_id": str(round_id)},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["round_id"] == round_id
    assert body["round_summary"] is not None


def test_create_diary_with_foreign_round_id_returns_404():
    token_a, _ = register_and_get_token(client)
    token_b, _ = register_and_get_token(client)
    course_id = seed_test_course()
    round_id = _create_round(token_a, course_id)

    response = client.post(
        "/api/diaries",
        headers=auth_headers(token_b),
        data={"text": "오늘 라운드 좋았다", "round_id": str(round_id)},
    )

    assert response.status_code == 404


@patch("app.ai.diary.graph.get_coach_llm")
def test_llm_hallucinated_round_id_is_discarded(mock_get_llm):
    """후보 목록에 없는 round_id를 LLM이 답하면 무시하고 None으로 저장해야 한다."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response(matched_round_id="999999"))
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)
    course_id = seed_test_course()
    _create_round(token, course_id)

    response = client.post(
        "/api/diaries", headers=auth_headers(token), data={"text": "오늘 라운드 좋았다"}
    )

    assert response.status_code == 201, response.text
    assert response.json()["round_id"] is None


@patch("app.ai.diary.graph.get_coach_llm")
def test_long_mood_from_llm_is_truncated_not_500(mock_get_llm):
    """무료 모델이 [기분]을 프롬프트 지시(5단어 이내)를 어기고 긴 문장으로 답해도,
    mood 컬럼이 String(50)이라 DB DataError로 요청 전체가 실패해서는 안 된다."""
    long_mood_response = """[기분]
오늘은 전반적으로 만족스러웠지만 후반 들어 집중력이 흐트러지면서 퍼팅에서 계속 실수가 나와 다소 아쉬운 감정이 남는 하루였다.

[하이라이트]
전반 드라이버 샷감이 좋았다.

[개선점]
후반 퍼팅 거리감이 아쉬웠다.

[다음목표]
다음 라운드에서는 짧은 퍼팅 연습을 더 하기.

[요약]
전반은 좋았지만 후반 퍼팅에서 타수를 잃은 라운드.

[매칭라운드]
없음
"""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=long_mood_response)
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/diaries", headers=auth_headers(token), data={"text": "오늘 라운드 좋았다"}
    )

    assert response.status_code == 201, response.text
    assert len(response.json()["mood"]) <= 50


@patch("app.ai.diary.graph.get_coach_llm")
def test_diary_llm_failure_still_saves_raw_text(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = RuntimeError("upstream timeout")
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)

    response = client.post(
        "/api/diaries", headers=auth_headers(token), data={"text": "오늘 라운드 좋았다"}
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["raw_text"] == "오늘 라운드 좋았다"
    assert "실패" in body["summary"]


@patch("app.ai.diary.graph.get_coach_llm")
def test_list_diaries_only_shows_own_diaries(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response())
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token_a, _ = register_and_get_token(client)
    token_b, _ = register_and_get_token(client)

    client.post("/api/diaries", headers=auth_headers(token_a), data={"text": "일기 A"})

    response_a = client.get("/api/diaries", headers=auth_headers(token_a))
    response_b = client.get("/api/diaries", headers=auth_headers(token_b))

    assert len(response_a.json()) >= 1
    assert response_b.json() == []


@patch("app.ai.diary.graph.get_coach_llm")
def test_other_user_cannot_access_diary(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response())
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token_a, _ = register_and_get_token(client)
    token_b, _ = register_and_get_token(client)

    created = client.post(
        "/api/diaries", headers=auth_headers(token_a), data={"text": "일기 A"}
    ).json()

    response = client.get(f"/api/diaries/{created['id']}", headers=auth_headers(token_b))

    assert response.status_code == 404


@patch("app.ai.diary.graph.get_coach_llm")
def test_delete_diary(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content=_sample_response())
    mock_llm.model_name = "test-model"
    mock_get_llm.return_value = mock_llm

    token, _ = register_and_get_token(client)
    created = client.post(
        "/api/diaries", headers=auth_headers(token), data={"text": "일기 A"}
    ).json()

    delete_response = client.delete(f"/api/diaries/{created['id']}", headers=auth_headers(token))
    get_response = client.get(f"/api/diaries/{created['id']}", headers=auth_headers(token))

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
