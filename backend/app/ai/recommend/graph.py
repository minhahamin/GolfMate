"""골프장 추천 LangGraph 정의 (Phase 7).

    START
     -> get_golfer_profile      (golfer_profile_repository 재사용, LLM 없음)
     -> search_candidate_courses (course_repository.search — region/difficulty/max_budget으로
                                   필터링된 실제 DB 후보만 가져온다, LLM 없음)
     -> recommendation_generation (유일한 LLM 호출 — 후보 중 최대 3곳 순위/이유 생성)
     -> recommendation_validator  (규칙 기반: 후보 목록에 없는 id는 버림 — 환각 방지)
     -> END

Coach/Diary와 같은 원칙: LLM은 실제 DB에서 가져온 후보 중에서만 고르고, 판단/설명만
담당한다. 후보가 비어 있으면 LLM을 호출하지 않고 바로 안내 메시지를 반환한다.
"""
import logging
import time

from langgraph.graph import END, START, StateGraph
from openai import APIConnectionError, APIStatusError, APITimeoutError
from sqlalchemy.orm import Session

from app.ai.llm.client import get_coach_llm
from app.ai.prompts.recommend.system import build_recommend_prompt
from app.ai.recommend.parser import parse_recommend_response
from app.ai.recommend.state import RecommendState
from app.models.course import Course
from app.models.golfer_profile import GolferProfile
from app.repositories import course_repository, golfer_profile_repository

logger = logging.getLogger(__name__)

FALLBACK_NO_CANDIDATES = "조건에 맞는 골프장을 찾지 못했습니다. 지역/난이도/예산 조건을 조금 넓혀서 다시 시도해보세요."
FALLBACK_LLM_ERROR = "AI 추천 생성에 실패했습니다. 잠시 후 다시 시도해주세요."
FALLBACK_RATE_LIMITED = (
    "지금 무료 AI 모델 사용량이 많아 추천을 생성하지 못했습니다. 몇 분 후 다시 시도해주세요."
)
FALLBACK_QUOTA_EXCEEDED = "AI 추천을 사용할 수 없습니다. OpenRouter 계정의 무료 크레딧을 확인해주세요."
FALLBACK_AUTH_ERROR = "AI 추천 설정에 문제가 있습니다. OPENROUTER_API_KEY를 확인해주세요."
FALLBACK_TIMEOUT = "AI 추천 생성이 시간 초과되었습니다. 잠시 후 다시 시도해주세요."


def _format_profile(profile: GolferProfile | None) -> str:
    if profile is None:
        return "등록된 프로필 정보 없음"
    parts = []
    if profile.handicap is not None:
        parts.append(f"핸디캡 {profile.handicap}")
    if profile.average_score is not None:
        parts.append(f"평균 스코어 {profile.average_score}")
    return ", ".join(parts) if parts else "등록된 프로필 정보 없음"


def _format_candidates(candidates: list[Course]) -> str:
    lines = []
    for c in candidates:
        fee = f"{c.green_fee_avg:,}원" if c.green_fee_avg is not None else "가격 정보 없음"
        tags = c.tags or "태그 없음"
        lines.append(f"- id={c.id} {c.name} ({c.region}) 난이도:{c.difficulty} 평균그린피:{fee} 특징:{tags}")
    return "\n".join(lines)


def build_recommend_graph(db: Session):
    def get_golfer_profile(state: RecommendState) -> dict:
        profile = golfer_profile_repository.get_by_user_id(db, state["user_id"])
        return {"golfer_profile": profile}

    def search_candidate_courses(state: RecommendState) -> dict:
        candidates = course_repository.search(
            db,
            region=state.get("region"),
            difficulty=state.get("difficulty"),
            max_budget=state.get("max_budget"),
        )
        return {"candidates": candidates}

    def recommendation_generation(state: RecommendState) -> dict:
        candidates = state.get("candidates") or []
        if not candidates:
            return {"summary": FALLBACK_NO_CANDIDATES, "ranked": []}

        prompt = build_recommend_prompt(
            golfer_profile_text=_format_profile(state.get("golfer_profile")),
            preference_text=state.get("preference_text") or "",
            candidates_text=_format_candidates(candidates),
        )

        llm = get_coach_llm()
        started = time.monotonic()
        try:
            response = llm.invoke(prompt)
        except APITimeoutError:
            logger.exception("recommend_llm_call_timeout user_id=%s", state.get("user_id"))
            return {"summary": FALLBACK_TIMEOUT, "ranked": [], "error": "timeout"}
        except APIConnectionError:
            logger.exception("recommend_llm_call_connection_failed user_id=%s", state.get("user_id"))
            return {"summary": FALLBACK_LLM_ERROR, "ranked": [], "error": "connection_error"}
        except APIStatusError as exc:
            logger.exception(
                "recommend_llm_call_api_error user_id=%s status=%s", state.get("user_id"), exc.status_code
            )
            if exc.status_code == 429:
                return {"summary": FALLBACK_RATE_LIMITED, "ranked": [], "error": "rate_limited"}
            if exc.status_code == 402:
                return {"summary": FALLBACK_QUOTA_EXCEEDED, "ranked": [], "error": "quota_exceeded"}
            if exc.status_code == 401:
                return {"summary": FALLBACK_AUTH_ERROR, "ranked": [], "error": "auth_error"}
            return {"summary": FALLBACK_LLM_ERROR, "ranked": [], "error": f"api_error_{exc.status_code}"}
        except Exception:
            logger.exception("recommend_llm_call_failed user_id=%s", state.get("user_id"))
            return {"summary": FALLBACK_LLM_ERROR, "ranked": [], "error": "llm_call_failed"}

        logger.info(
            "recommend_llm_call user_id=%s model=%s latency=%.2fs",
            state.get("user_id"),
            llm.model_name,
            time.monotonic() - started,
        )
        parsed = parse_recommend_response(response.content)
        return {"summary": parsed["summary"], "ranked": parsed["ranked"]}

    def recommendation_validator(state: RecommendState) -> dict:
        candidate_ids = {c.id for c in (state.get("candidates") or [])}
        ranked = [item for item in (state.get("ranked") or []) if item["course_id"] in candidate_ids]

        summary = state.get("summary") or ""
        if (state.get("candidates")) and not ranked and not state.get("error"):
            # 후보는 있었는데 LLM이 유효한 id를 하나도 못 골랐을 때 — 빈 목록으로 조용히
            # 응답하는 대신 실패했음을 명확히 알린다.
            summary = summary or FALLBACK_LLM_ERROR

        return {"summary": summary, "ranked": ranked}

    graph = StateGraph(RecommendState)
    graph.add_node("get_golfer_profile", get_golfer_profile)
    graph.add_node("search_candidate_courses", search_candidate_courses)
    graph.add_node("recommendation_generation", recommendation_generation)
    graph.add_node("recommendation_validator", recommendation_validator)

    graph.add_edge(START, "get_golfer_profile")
    graph.add_edge("get_golfer_profile", "search_candidate_courses")
    graph.add_edge("search_candidate_courses", "recommendation_generation")
    graph.add_edge("recommendation_generation", "recommendation_validator")
    graph.add_edge("recommendation_validator", END)

    return graph.compile()


def run_recommend_graph(
    db: Session,
    user_id: int,
    *,
    region: str | None,
    difficulty: str | None,
    max_budget: int | None,
    preference_text: str,
) -> dict:
    graph = build_recommend_graph(db)
    result: RecommendState = graph.invoke(
        {
            "user_id": user_id,
            "region": region,
            "difficulty": difficulty,
            "max_budget": max_budget,
            "preference_text": preference_text,
        }
    )
    candidates_by_id = {c.id: c for c in (result.get("candidates") or [])}
    return {
        "summary": result["summary"],
        "recommendations": [
            {"course": candidates_by_id[item["course_id"]], "reason": item["reason"]}
            for item in result["ranked"]
        ],
    }
