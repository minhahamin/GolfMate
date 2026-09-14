"""AI Coach LangGraph 정의 (마스터 스펙 §11).

무료 LLM의 rate limit을 고려해 "약점 분석"과 "전략 생성"을 한 노드(weakness_and_strategy)로
합쳤지만, 나머지 노드 이름은 스펙의 그래프 다이어그램을 그대로 따라 추적 가능하게 만든다.

    START
     -> intent_analyzer         (지금은 단일 코칭 흐름만 있어 통과만 시킴 — 확장 지점)
     -> get_golfer_profile      (profile 조회, LLM 없음)
     -> get_recent_rounds       (round_repository 재사용, LLM 없음)
     -> retrieve_golf_knowledge (Phase 5 RAG: pgvector에서 질문과 관련된 골프 지식 검색, LLM 없음)
     -> statistics_analyzer     (Phase 3 statistics_service 재사용, LLM 없음)
     -> weakness_and_strategy   (유일한 LLM 호출)
     -> recommendation_validator (규칙 기반 검증/폴백)
     -> END
"""
import logging
import time

from langgraph.graph import END, START, StateGraph
from openai import APIConnectionError, APIStatusError, APITimeoutError
from sqlalchemy.orm import Session

from app.ai.coach.parser import parse_coach_response
from app.ai.coach.state import GolfCoachState
from app.ai.llm.client import get_coach_llm
from app.ai.prompts.coach.system import build_coach_prompt
from app.ai.rag.retriever import retrieve_knowledge
from app.models.golf_knowledge import GolfKnowledge
from app.models.golfer_profile import GolferProfile
from app.models.round import Round
from app.repositories import golfer_profile_repository, round_repository
from app.services import statistics_service

logger = logging.getLogger(__name__)

FALLBACK_NO_DATA: dict[str, str] = {
    "current_state": "아직 등록된 라운드가 없어 분석할 데이터가 없습니다.",
    "biggest_problem": "",
    "cause": "",
    "strategy": "라운드를 1개 이상 등록하면 AI 코치 분석을 받을 수 있습니다.",
    "next_goal": "",
}

FALLBACK_LLM_ERROR: dict[str, str] = {
    "current_state": "AI 코치 응답 생성에 실패했습니다.",
    "biggest_problem": "",
    "cause": "",
    "strategy": "잠시 후 다시 시도해주세요.",
    "next_goal": "",
}

FALLBACK_RATE_LIMITED: dict[str, str] = {
    "current_state": "지금 무료 AI 모델 사용량이 많아 요청이 거절되었습니다.",
    "biggest_problem": "",
    "cause": "",
    "strategy": "OpenRouter 무료 모델의 분당/일일 사용량 한도에 도달했을 가능성이 높습니다. "
    "몇 분 후 다시 시도하거나, 계속되면 OPENROUTER_MODEL을 다른 무료 모델로 바꿔보세요.",
    "next_goal": "",
}

FALLBACK_QUOTA_EXCEEDED: dict[str, str] = {
    "current_state": "AI 코치를 사용할 수 없습니다.",
    "biggest_problem": "",
    "cause": "",
    "strategy": "연결된 OpenRouter 계정의 무료 크레딧/한도가 모두 소진된 것으로 보입니다. "
    "OpenRouter 계정에서 잔여 크레딧을 확인해주세요.",
    "next_goal": "",
}

FALLBACK_AUTH_ERROR: dict[str, str] = {
    "current_state": "AI 코치 설정에 문제가 있어 응답을 생성하지 못했습니다.",
    "biggest_problem": "",
    "cause": "",
    "strategy": "OPENROUTER_API_KEY가 비어있거나 올바르지 않을 수 있습니다. 서버 환경변수를 확인해주세요.",
    "next_goal": "",
}

FALLBACK_TIMEOUT: dict[str, str] = {
    "current_state": "AI 코치 응답 생성이 너무 오래 걸려 시간 초과되었습니다.",
    "biggest_problem": "",
    "cause": "",
    "strategy": "무료 모델 서버가 혼잡한 상태일 수 있습니다. 잠시 후 다시 시도해주세요.",
    "next_goal": "",
}


def _format_profile(profile: GolferProfile | None) -> str:
    if profile is None:
        return "등록된 프로필 정보 없음"

    parts = []
    if profile.handicap is not None:
        parts.append(f"핸디캡 {profile.handicap}")
    if profile.average_score is not None:
        parts.append(f"평균 스코어 {profile.average_score}")
    if profile.driver_distance is not None:
        parts.append(f"드라이버 평균 거리 {profile.driver_distance}m")
    if profile.goal_score is not None:
        parts.append(f"목표 스코어 {profile.goal_score}")
    return ", ".join(parts) if parts else "등록된 프로필 정보 없음"


def _format_statistics(stats: dict) -> str:
    parts = [f"라운드 수 {stats.get('rounds_count', 0)}회"]
    for key, label, suffix in [
        ("average_score", "평균 스코어", ""),
        ("best_score", "베스트 스코어", ""),
        ("average_putts", "평균 퍼팅", "개"),
        ("average_fairway_rate", "페어웨이 적중률", "%"),
        ("average_gir_rate", "GIR", "%"),
    ]:
        value = stats.get(key)
        if value is not None:
            parts.append(f"{label} {value}{suffix}")
    return ", ".join(parts)


def _format_rounds(rounds: list[Round]) -> str:
    if not rounds:
        return "없음"
    course_name = lambda r: r.course.name if r.course else "코스 미상"  # noqa: E731
    return "\n".join(f"- {r.round_date} {course_name(r)} {r.score}타" for r in rounds)


def _format_knowledge(entries: list[GolfKnowledge]) -> str:
    if not entries:
        return "관련 지식 없음"
    return "\n".join(f"- {entry.title}: {entry.content}" for entry in entries)


def build_coach_graph(db: Session):
    """요청마다 이 DB 세션에 바인딩된 그래프를 새로 컴파일한다 (컴파일 비용은 가볍다)."""

    def intent_analyzer(state: GolfCoachState) -> dict:
        # 지금은 단일 코칭 흐름만 있어, 빈 질문에 기본 질문을 채워주는 정도만 한다.
        # (LangGraph 노드는 최소 1개 키를 갱신해야 하므로 순수 통과 노드로 두지 않는다.)
        question = (state.get("question") or "").strip() or "전반적인 경기력을 분석해줘"
        return {"question": question}

    def get_golfer_profile(state: GolfCoachState) -> dict:
        profile = golfer_profile_repository.get_by_user_id(db, state["user_id"])
        return {"golfer_profile": profile}

    def get_recent_rounds(state: GolfCoachState) -> dict:
        rounds = round_repository.list_recent_by_user(db, state["user_id"], limit=10)
        return {"recent_rounds": rounds, "has_data": bool(rounds)}

    def retrieve_golf_knowledge(state: GolfCoachState) -> dict:
        knowledge = retrieve_knowledge(db, state["question"])
        return {"retrieved_knowledge": knowledge}

    def statistics_analyzer(state: GolfCoachState) -> dict:
        if not state.get("has_data"):
            return {"statistics": {}}
        stats = statistics_service.compute_statistics_summary(state["recent_rounds"])
        return {"statistics": stats.model_dump()}

    def weakness_and_strategy(state: GolfCoachState) -> dict:
        if not state.get("has_data"):
            return {"final_answer": FALLBACK_NO_DATA}

        prompt = build_coach_prompt(
            golfer_profile_text=_format_profile(state.get("golfer_profile")),
            statistics_text=_format_statistics(state.get("statistics") or {}),
            recent_rounds_text=_format_rounds(state["recent_rounds"]),
            rounds_count=len(state["recent_rounds"]),
            knowledge_text=_format_knowledge(state.get("retrieved_knowledge") or []),
            question=state["question"],
        )

        llm = get_coach_llm()
        started = time.monotonic()
        try:
            response = llm.invoke(prompt)
        except APITimeoutError:
            logger.exception("coach_llm_call_timeout user_id=%s", state.get("user_id"))
            return {"final_answer": FALLBACK_TIMEOUT, "error": "timeout"}
        except APIConnectionError:
            logger.exception("coach_llm_call_connection_failed user_id=%s", state.get("user_id"))
            return {"final_answer": FALLBACK_LLM_ERROR, "error": "connection_error"}
        except APIStatusError as exc:
            logger.exception(
                "coach_llm_call_api_error user_id=%s status=%s", state.get("user_id"), exc.status_code
            )
            if exc.status_code == 429:
                return {"final_answer": FALLBACK_RATE_LIMITED, "error": "rate_limited"}
            if exc.status_code == 402:
                return {"final_answer": FALLBACK_QUOTA_EXCEEDED, "error": "quota_exceeded"}
            if exc.status_code == 401:
                return {"final_answer": FALLBACK_AUTH_ERROR, "error": "auth_error"}
            return {"final_answer": FALLBACK_LLM_ERROR, "error": f"api_error_{exc.status_code}"}
        except Exception:
            logger.exception("coach_llm_call_failed user_id=%s", state.get("user_id"))
            return {"final_answer": FALLBACK_LLM_ERROR, "error": "llm_call_failed"}

        logger.info(
            "coach_llm_call user_id=%s model=%s latency=%.2fs",
            state.get("user_id"),
            llm.model_name,
            time.monotonic() - started,
        )
        return {"final_answer": parse_coach_response(response.content)}

    def recommendation_validator(state: GolfCoachState) -> dict:
        answer = state.get("final_answer") or {}
        if not any(answer.values()):
            return {"final_answer": FALLBACK_LLM_ERROR}
        return {"final_answer": answer}

    graph = StateGraph(GolfCoachState)
    graph.add_node("intent_analyzer", intent_analyzer)
    graph.add_node("get_golfer_profile", get_golfer_profile)
    graph.add_node("get_recent_rounds", get_recent_rounds)
    graph.add_node("retrieve_golf_knowledge", retrieve_golf_knowledge)
    graph.add_node("statistics_analyzer", statistics_analyzer)
    graph.add_node("weakness_and_strategy", weakness_and_strategy)
    graph.add_node("recommendation_validator", recommendation_validator)

    graph.add_edge(START, "intent_analyzer")
    graph.add_edge("intent_analyzer", "get_golfer_profile")
    graph.add_edge("get_golfer_profile", "get_recent_rounds")
    graph.add_edge("get_recent_rounds", "retrieve_golf_knowledge")
    graph.add_edge("retrieve_golf_knowledge", "statistics_analyzer")
    graph.add_edge("statistics_analyzer", "weakness_and_strategy")
    graph.add_edge("weakness_and_strategy", "recommendation_validator")
    graph.add_edge("recommendation_validator", END)

    return graph.compile()


def run_coach_graph(db: Session, user_id: int, question: str) -> dict[str, str]:
    graph = build_coach_graph(db)
    result: GolfCoachState = graph.invoke({"user_id": user_id, "question": question})
    return result["final_answer"]
