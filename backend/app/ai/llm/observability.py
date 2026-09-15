"""Langfuse observability 초기화 (Phase 10, 마스터 스펙 §18).

이 프로젝트의 모든 그래프(Coach/Diary/Recommend/Caddie/Bet)는 이미 app/ai/llm/client.py의
get_coach_llm() 하나로 LLM 호출이 모여 있다. 그래서 계측도 그래프마다 따로 손대지 않고,
각 그래프의 run_*_graph()가 graph.invoke()에 넘기는 config에 이 모듈의 CallbackHandler
하나만 얹으면 LangChain/LangGraph 실행의 Trace/Span/Generation(모델명, 토큰, 지연시간)이
전부 Langfuse에 잡힌다.

LANGFUSE_PUBLIC_KEY/LANGFUSE_SECRET_KEY가 비어있으면(로컬에서 계정을 안 만든 경우) langfuse
SDK가 자동으로 no-op 클라이언트로 동작해 아무것도 전송하지 않는다(네트워크 호출도 없음) —
Coach 등이 LLM 호출 실패 시 폴백 텍스트로 응답하는 것과 같은 "관측 기능 하나 때문에 핵심
기능이 막히지 않는다" 원칙이다.

셀프호스팅(ClickHouse+Redis+MinIO+Postgres)이 아니라 Langfuse Cloud 무료 플랜을 쓴다 —
OpenRouter/Open-Meteo/로컬 STT·임베딩처럼 이 프로젝트 전체가 따르는 "과금 없이 가벼운
인프라로 실제 서비스 검증" 원칙과 같은 선택이다.
"""
from functools import lru_cache

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from app.core.config import get_settings


@lru_cache
def _get_langfuse_client() -> Langfuse:
    settings = get_settings()
    return Langfuse(
        public_key=settings.langfuse_public_key or None,
        secret_key=settings.langfuse_secret_key or None,
        host=settings.langfuse_host,
    )


@lru_cache
def get_langfuse_handler() -> CallbackHandler:
    _get_langfuse_client()  # 싱글턴을 먼저 등록해야 CallbackHandler가 같은 설정을 재사용한다.
    return CallbackHandler()


def build_langfuse_config(graph_name: str, user_id: int) -> dict:
    """graph.invoke()에 그대로 넘길 config. 그래프 이름/사용자로 Trace를 구분한다."""
    return {
        "callbacks": [get_langfuse_handler()],
        "metadata": {
            "langfuse_trace_name": f"{graph_name}_graph",
            "langfuse_user_id": str(user_id),
            "langfuse_tags": [graph_name],
        },
    }


def flush_langfuse() -> None:
    """앱 종료 시 버퍼에 남은 span을 강제로 전송한다 (FastAPI lifespan에서 호출)."""
    _get_langfuse_client().flush()
