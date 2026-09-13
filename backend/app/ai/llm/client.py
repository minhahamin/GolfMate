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
        max_retries=1,
    )
