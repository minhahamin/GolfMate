"""LLM 클라이언트 초기화.

OpenRouter는 OpenAI 호환 API라 별도 SDK 없이 langchain_openai.ChatOpenAI에
base_url만 바꿔서 연결한다. API Key는 반드시 환경변수(app.core.config)에서만 읽는다.
"""
from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.core.config import get_settings


@lru_cache
def get_coach_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openrouter_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0.4,
        timeout=30,
        # 재시도를 하면 타임아웃 시 최악의 경우 30초*2가 되어 프론트엔드 타임아웃(35초, coach.ts)
        # 보다 오래 걸릴 수 있다. 실패를 빠르게 확정하고 graph.py의 상세 폴백 메시지로 응답한다.
        max_retries=0,
    )
