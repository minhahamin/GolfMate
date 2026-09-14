"""내기 AI 코멘터리 LangGraph 정의 (Phase 9).

    START
     -> commentary_generation (유일한 LLM 호출 — 이미 계산된 정산 결과를 설명만 한다)
     -> commentary_validator  (규칙 기반: 응답이 비어있으면 폴백)
     -> END

정산 금액(payout_amount)은 이 그래프에 들어오기 전에 app/services/bet_service.py가 이미
계산을 끝낸 값이다 — LLM은 절대 금액을 다시 계산하지 않는다 (설계 원칙 5번).
bet은 라우터가 멤버십 확인 후 이미 조회해 초기 state로 넘긴다 (Caddie의 course/hole과 동일).
"""
import logging
import time

from langgraph.graph import END, START, StateGraph
from openai import APIConnectionError, APIStatusError, APITimeoutError

from app.ai.bet.state import BetCommentaryState
from app.ai.llm.client import get_coach_llm
from app.ai.prompts.bet.system import build_bet_commentary_prompt
from app.models.bet import Bet

logger = logging.getLogger(__name__)

FALLBACK_LLM_ERROR = "AI 코멘터리 생성에 실패했습니다. 잠시 후 다시 시도해주세요."
FALLBACK_RATE_LIMITED = "지금 무료 AI 모델 사용량이 많아 코멘터리를 생성하지 못했습니다. 몇 분 후 다시 시도해주세요."
FALLBACK_QUOTA_EXCEEDED = "AI 코멘터리를 사용할 수 없습니다. OpenRouter 계정의 무료 크레딧을 확인해주세요."
FALLBACK_AUTH_ERROR = "AI 설정에 문제가 있습니다. OPENROUTER_API_KEY를 확인해주세요."
FALLBACK_TIMEOUT = "AI 코멘터리 생성이 시간 초과되었습니다. 잠시 후 다시 시도해주세요."


def _format_results(bet: Bet) -> str:
    lines = []
    for r in sorted(bet.results, key=lambda r: -r.payout_amount):
        sign = "+" if r.payout_amount >= 0 else ""
        lines.append(f"- {r.user.name}: {r.score}타, {sign}{r.payout_amount:,}원")
    return "\n".join(lines)


def build_bet_commentary_graph():
    def commentary_generation(state: BetCommentaryState) -> dict:
        bet: Bet = state["bet"]
        prompt = build_bet_commentary_prompt(
            title=bet.title,
            bet_date=str(bet.bet_date),
            course_name=bet.course_name,
            stake_per_stroke=bet.stake_per_stroke,
            results_text=_format_results(bet),
        )

        llm = get_coach_llm()
        started = time.monotonic()
        try:
            response = llm.invoke(prompt)
        except APITimeoutError:
            logger.exception("bet_commentary_llm_call_timeout user_id=%s", state.get("user_id"))
            return {"commentary": FALLBACK_TIMEOUT, "error": "timeout"}
        except APIConnectionError:
            logger.exception("bet_commentary_llm_call_connection_failed user_id=%s", state.get("user_id"))
            return {"commentary": FALLBACK_LLM_ERROR, "error": "connection_error"}
        except APIStatusError as exc:
            logger.exception(
                "bet_commentary_llm_call_api_error user_id=%s status=%s",
                state.get("user_id"),
                exc.status_code,
            )
            if exc.status_code == 429:
                return {"commentary": FALLBACK_RATE_LIMITED, "error": "rate_limited"}
            if exc.status_code == 402:
                return {"commentary": FALLBACK_QUOTA_EXCEEDED, "error": "quota_exceeded"}
            if exc.status_code == 401:
                return {"commentary": FALLBACK_AUTH_ERROR, "error": "auth_error"}
            return {"commentary": FALLBACK_LLM_ERROR, "error": f"api_error_{exc.status_code}"}
        except Exception:
            logger.exception("bet_commentary_llm_call_failed user_id=%s", state.get("user_id"))
            return {"commentary": FALLBACK_LLM_ERROR, "error": "llm_call_failed"}

        logger.info(
            "bet_commentary_llm_call user_id=%s model=%s latency=%.2fs",
            state.get("user_id"),
            llm.model_name,
            time.monotonic() - started,
        )
        return {"commentary": response.content.strip()}

    def commentary_validator(state: BetCommentaryState) -> dict:
        commentary = state.get("commentary") or ""
        if not commentary:
            commentary = FALLBACK_LLM_ERROR
        return {"commentary": commentary}

    graph = StateGraph(BetCommentaryState)
    graph.add_node("commentary_generation", commentary_generation)
    graph.add_node("commentary_validator", commentary_validator)

    graph.add_edge(START, "commentary_generation")
    graph.add_edge("commentary_generation", "commentary_validator")
    graph.add_edge("commentary_validator", END)

    return graph.compile()


def run_bet_commentary_graph(user_id: int, bet: Bet) -> str:
    graph = build_bet_commentary_graph()
    result: BetCommentaryState = graph.invoke({"user_id": user_id, "bet": bet})
    return result["commentary"]
