"""AI 캐디 LangGraph 정의 (Phase 8).

    START
     -> get_golfer_profile (golfer_profile_repository 재사용, LLM 없음)
     -> get_weather         (Open-Meteo 실제 API 호출 — app/ai/weather/client.py, LLM 없음)
     -> caddie_generation   (유일한 LLM 호출 — 홀공략/위험요소/클럽전략을 한 번에 생성)
     -> caddie_validator    (규칙 기반 검증/폴백)
     -> END

course/hole은 라우터가 이미 조회해 초기 state로 넘겨준다 (골프장 정보는 공개 데이터라
소유권 확인이 필요 없다 — Coach/Diary가 user_id로 필터링하는 것과 다른 지점).
Tool Calling(공식 LangChain @tool)은 아직 도입하지 않았다 — Coach/Diary/Recommend와 같은
이유로, 지금은 고정된 파이프라인이라 LLM이 동적으로 도구를 선택할 필요가 없다.
"""
import logging
import time

from langgraph.graph import END, START, StateGraph
from openai import APIConnectionError, APIStatusError, APITimeoutError
from sqlalchemy.orm import Session

from app.ai.caddie.parser import parse_caddie_response
from app.ai.caddie.state import CaddieState
from app.ai.llm.client import get_coach_llm
from app.ai.prompts.caddie.system import build_caddie_prompt
from app.ai.weather.client import WeatherFetchError, format_weather_summary, get_current_weather
from app.models.course import Course
from app.models.course_hole import CourseHole
from app.models.golfer_profile import GolferProfile
from app.repositories import golfer_profile_repository

logger = logging.getLogger(__name__)

FALLBACK_LLM_ERROR: dict[str, str] = {
    "hole_analysis": "AI 캐디 분석에 실패했습니다. 잠시 후 다시 시도해주세요.",
    "risk_analysis": "",
    "club_strategy": "",
}

FALLBACK_RATE_LIMITED: dict[str, str] = {
    "hole_analysis": "지금 무료 AI 모델 사용량이 많아 분석에 실패했습니다. 몇 분 후 다시 시도해주세요.",
    "risk_analysis": "",
    "club_strategy": "",
}

FALLBACK_QUOTA_EXCEEDED: dict[str, str] = {
    "hole_analysis": "AI 캐디를 사용할 수 없습니다. OpenRouter 계정의 무료 크레딧을 확인해주세요.",
    "risk_analysis": "",
    "club_strategy": "",
}

FALLBACK_AUTH_ERROR: dict[str, str] = {
    "hole_analysis": "AI 캐디 설정에 문제가 있습니다. OPENROUTER_API_KEY를 확인해주세요.",
    "risk_analysis": "",
    "club_strategy": "",
}

FALLBACK_TIMEOUT: dict[str, str] = {
    "hole_analysis": "AI 캐디 분석이 시간 초과되었습니다. 잠시 후 다시 시도해주세요.",
    "risk_analysis": "",
    "club_strategy": "",
}


def _format_profile(profile: GolferProfile | None) -> str:
    if profile is None:
        return "등록된 프로필 정보 없음"
    parts = []
    if profile.handicap is not None:
        parts.append(f"핸디캡 {profile.handicap}")
    if profile.driver_distance is not None:
        parts.append(f"드라이버 평균 거리 {profile.driver_distance}m")
    if profile.iron_distance is not None:
        parts.append(f"아이언 평균 거리 {profile.iron_distance}m")
    return ", ".join(parts) if parts else "등록된 프로필 정보 없음"


def _format_hole(course: Course, hole: CourseHole) -> str:
    return f"{course.name} {hole.hole_number}번 홀, 파{hole.par}, 거리 {hole.distance_meters}m"


def build_caddie_graph(db: Session):
    def get_golfer_profile(state: CaddieState) -> dict:
        profile = golfer_profile_repository.get_by_user_id(db, state["user_id"])
        return {"golfer_profile": profile}

    def get_weather(state: CaddieState) -> dict:
        course: Course = state["course"]
        if course.latitude is None or course.longitude is None:
            return {"weather": None, "weather_summary": "날씨 정보 없음 (좌표 미등록)"}
        try:
            weather = get_current_weather(course.latitude, course.longitude)
        except WeatherFetchError:
            logger.exception("caddie_weather_fetch_failed course_id=%s", course.id)
            return {"weather": None, "weather_summary": "날씨 정보를 가져오지 못했습니다."}
        return {"weather": weather, "weather_summary": format_weather_summary(weather)}

    def caddie_generation(state: CaddieState) -> dict:
        prompt = build_caddie_prompt(
            golfer_profile_text=_format_profile(state.get("golfer_profile")),
            hole_info_text=_format_hole(state["course"], state["hole"]),
            weather_text=state.get("weather_summary") or "날씨 정보 없음",
            question=state.get("question", ""),
        )

        llm = get_coach_llm()
        started = time.monotonic()
        try:
            response = llm.invoke(prompt)
        except APITimeoutError:
            logger.exception("caddie_llm_call_timeout user_id=%s", state.get("user_id"))
            return {**FALLBACK_TIMEOUT, "error": "timeout"}
        except APIConnectionError:
            logger.exception("caddie_llm_call_connection_failed user_id=%s", state.get("user_id"))
            return {**FALLBACK_LLM_ERROR, "error": "connection_error"}
        except APIStatusError as exc:
            logger.exception(
                "caddie_llm_call_api_error user_id=%s status=%s", state.get("user_id"), exc.status_code
            )
            if exc.status_code == 429:
                return {**FALLBACK_RATE_LIMITED, "error": "rate_limited"}
            if exc.status_code == 402:
                return {**FALLBACK_QUOTA_EXCEEDED, "error": "quota_exceeded"}
            if exc.status_code == 401:
                return {**FALLBACK_AUTH_ERROR, "error": "auth_error"}
            return {**FALLBACK_LLM_ERROR, "error": f"api_error_{exc.status_code}"}
        except Exception:
            logger.exception("caddie_llm_call_failed user_id=%s", state.get("user_id"))
            return {**FALLBACK_LLM_ERROR, "error": "llm_call_failed"}

        logger.info(
            "caddie_llm_call user_id=%s model=%s latency=%.2fs",
            state.get("user_id"),
            llm.model_name,
            time.monotonic() - started,
        )
        return parse_caddie_response(response.content)

    def caddie_validator(state: CaddieState) -> dict:
        fields = {
            "hole_analysis": state.get("hole_analysis") or "",
            "risk_analysis": state.get("risk_analysis") or "",
            "club_strategy": state.get("club_strategy") or "",
        }
        if not any(fields.values()):
            fields = dict(FALLBACK_LLM_ERROR)
        return fields

    graph = StateGraph(CaddieState)
    graph.add_node("get_golfer_profile", get_golfer_profile)
    graph.add_node("get_weather", get_weather)
    graph.add_node("caddie_generation", caddie_generation)
    graph.add_node("caddie_validator", caddie_validator)

    graph.add_edge(START, "get_golfer_profile")
    graph.add_edge("get_golfer_profile", "get_weather")
    graph.add_edge("get_weather", "caddie_generation")
    graph.add_edge("caddie_generation", "caddie_validator")
    graph.add_edge("caddie_validator", END)

    return graph.compile()


def run_caddie_graph(
    db: Session, user_id: int, course: Course, hole: CourseHole, question: str
) -> dict:
    graph = build_caddie_graph(db)
    result: CaddieState = graph.invoke(
        {"user_id": user_id, "course": course, "hole": hole, "question": question}
    )
    return {
        "hole_analysis": result["hole_analysis"],
        "risk_analysis": result["risk_analysis"],
        "club_strategy": result["club_strategy"],
        "weather_summary": result.get("weather_summary"),
    }
