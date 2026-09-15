"""AI 골프 일기 LangGraph 정의 (Phase 6).

    START
     -> get_recent_rounds  (round_repository 재사용, Coach와 동일 함수, LLM 없음)
     -> diary_generation   (유일한 LLM 호출 — 감정/사건 정리 + 라운드 매칭 + 일기 생성을
                             한 번에 처리. 무료 LLM의 rate limit을 고려해 Coach와 같은 방식으로
                             여러 단계를 한 노드에 합쳤다)
     -> diary_validator    (규칙 기반 검증/폴백)
     -> END

STT(음성 -> 텍스트)는 이 그래프에 포함하지 않는다. STT 실패(오디오 디코딩 불가 등)는
"AI 판단 실패"가 아니라 "사용자 입력 자체가 유효하지 않음"이라 Coach 스타일의 LLM 폴백과
성격이 다르기 때문이다 — app/services/diary_service.py가 그래프를 부르기 전에 먼저
처리해서 실패 시 422로 명확히 끊는다.
"""
import logging
import time

from langgraph.graph import END, START, StateGraph
from openai import APIConnectionError, APIStatusError, APITimeoutError
from sqlalchemy.orm import Session

from app.ai.diary.parser import parse_diary_response
from app.ai.diary.state import DiaryState
from app.ai.llm.client import get_coach_llm
from app.ai.llm.observability import build_langfuse_config
from app.ai.prompts.diary.system import build_diary_prompt
from app.models.diary import MOOD_MAX_LENGTH
from app.models.round import Round
from app.repositories import round_repository

logger = logging.getLogger(__name__)

FALLBACK_LLM_ERROR: dict[str, str] = {
    "summary": "AI 일기 정리에 실패했습니다. 원문은 그대로 저장했어요.",
    "mood": "",
    "highlights": "",
    "improvement_points": "",
    "next_goal": "",
}

FALLBACK_RATE_LIMITED: dict[str, str] = {
    "summary": "지금 무료 AI 모델 사용량이 많아 정리에 실패했습니다. 원문은 그대로 저장했어요.",
    "mood": "",
    "highlights": "",
    "improvement_points": "",
    "next_goal": "",
}

FALLBACK_QUOTA_EXCEEDED: dict[str, str] = {
    "summary": "AI 일기 정리를 사용할 수 없습니다. 원문은 그대로 저장했어요.",
    "mood": "",
    "highlights": "",
    "improvement_points": "",
    "next_goal": "",
}

FALLBACK_AUTH_ERROR: dict[str, str] = {
    "summary": "AI 설정에 문제가 있어 정리하지 못했습니다. 원문은 그대로 저장했어요.",
    "mood": "",
    "highlights": "",
    "improvement_points": "",
    "next_goal": "",
}

FALLBACK_TIMEOUT: dict[str, str] = {
    "summary": "AI 일기 정리가 시간 초과되었습니다. 원문은 그대로 저장했어요.",
    "mood": "",
    "highlights": "",
    "improvement_points": "",
    "next_goal": "",
}


def _format_rounds(rounds: list[Round]) -> str:
    if not rounds:
        return "없음"
    course_name = lambda r: r.course.name if r.course else "코스 미상"  # noqa: E731
    return "\n".join(f"- id={r.id} {r.round_date} {course_name(r)} {r.score}타" for r in rounds)


def build_diary_graph(db: Session):
    def get_recent_rounds(state: DiaryState) -> dict:
        rounds = round_repository.list_recent_by_user(db, state["user_id"], limit=10)
        return {"recent_rounds": rounds}

    def diary_generation(state: DiaryState) -> dict:
        candidates = state.get("recent_rounds") or []
        prompt = build_diary_prompt(
            raw_text=state["raw_text"],
            recent_rounds_text=_format_rounds(candidates),
        )

        llm = get_coach_llm()
        started = time.monotonic()
        try:
            response = llm.invoke(prompt)
        except APITimeoutError:
            logger.exception("diary_llm_call_timeout user_id=%s", state.get("user_id"))
            return {**FALLBACK_TIMEOUT, "matched_round_id": None, "error": "timeout"}
        except APIConnectionError:
            logger.exception("diary_llm_call_connection_failed user_id=%s", state.get("user_id"))
            return {**FALLBACK_LLM_ERROR, "matched_round_id": None, "error": "connection_error"}
        except APIStatusError as exc:
            logger.exception(
                "diary_llm_call_api_error user_id=%s status=%s", state.get("user_id"), exc.status_code
            )
            if exc.status_code == 429:
                return {**FALLBACK_RATE_LIMITED, "matched_round_id": None, "error": "rate_limited"}
            if exc.status_code == 402:
                return {**FALLBACK_QUOTA_EXCEEDED, "matched_round_id": None, "error": "quota_exceeded"}
            if exc.status_code == 401:
                return {**FALLBACK_AUTH_ERROR, "matched_round_id": None, "error": "auth_error"}
            return {**FALLBACK_LLM_ERROR, "matched_round_id": None, "error": f"api_error_{exc.status_code}"}
        except Exception:
            logger.exception("diary_llm_call_failed user_id=%s", state.get("user_id"))
            return {**FALLBACK_LLM_ERROR, "matched_round_id": None, "error": "llm_call_failed"}

        logger.info(
            "diary_llm_call user_id=%s model=%s latency=%.2fs",
            state.get("user_id"),
            llm.model_name,
            time.monotonic() - started,
        )
        parsed = parse_diary_response(response.content)
        return parsed

    def diary_validator(state: DiaryState) -> dict:
        fields = {
            "summary": state.get("summary") or "",
            "mood": state.get("mood") or "",
            "highlights": state.get("highlights") or "",
            "improvement_points": state.get("improvement_points") or "",
            "next_goal": state.get("next_goal") or "",
        }
        if not any(fields.values()):
            fields = dict(FALLBACK_LLM_ERROR)

        if len(fields["mood"]) > MOOD_MAX_LENGTH:
            fields["mood"] = fields["mood"][: MOOD_MAX_LENGTH - 1].rstrip() + "…"

        round_hint = state.get("round_id_hint")
        if round_hint is not None:
            matched_round_id = round_hint
        else:
            candidate_ids = {r.id for r in (state.get("recent_rounds") or [])}
            llm_matched = state.get("matched_round_id")
            matched_round_id = llm_matched if llm_matched in candidate_ids else None

        return {**fields, "matched_round_id": matched_round_id}

    graph = StateGraph(DiaryState)
    graph.add_node("get_recent_rounds", get_recent_rounds)
    graph.add_node("diary_generation", diary_generation)
    graph.add_node("diary_validator", diary_validator)

    graph.add_edge(START, "get_recent_rounds")
    graph.add_edge("get_recent_rounds", "diary_generation")
    graph.add_edge("diary_generation", "diary_validator")
    graph.add_edge("diary_validator", END)

    return graph.compile()


def run_diary_graph(db: Session, user_id: int, raw_text: str, round_id_hint: int | None) -> dict:
    graph = build_diary_graph(db)
    result: DiaryState = graph.invoke(
        {"user_id": user_id, "raw_text": raw_text, "round_id_hint": round_id_hint},
        config=build_langfuse_config("diary", user_id),
    )
    return {
        "summary": result["summary"],
        "mood": result["mood"],
        "highlights": result["highlights"],
        "improvement_points": result["improvement_points"],
        "next_goal": result["next_goal"],
        "matched_round_id": result.get("matched_round_id"),
    }
