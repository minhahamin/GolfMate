"""애플리케이션 전역 설정.

환경변수는 .env 파일 또는 컨테이너 환경변수로 주입되며,
pydantic-settings가 이를 파싱하고 타입을 검증한다.
코드 어디에도 API Key나 접속 정보를 하드코딩하지 않는다.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "local"
    database_url: str = "postgresql+psycopg2://golfmate:golfmate@localhost:5432/golfmate"
    cors_origins: str = "http://localhost:5180"

    jwt_secret_key: str = "dev-only-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # OpenRouter는 OpenAI 호환 API라 langchain_openai.ChatOpenAI에 base_url만 바꿔 붙인다.
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "nvidia/nemotron-3-super-120b-a12b:free"

    # AI 골프 일기(Phase 6)의 STT — 과금/API 키 없이 로컬 faster-whisper로 전사한다.
    # base는 한국어 인식률이 눈에 띄게 낮아 small로 올렸다 (CPU에서 조금 더 느려지는 정도,
    # 과금/API 키는 여전히 없음). 더 키우면(medium 이상) 정확도는 오르지만 응답이 느려진다.
    whisper_model_size: str = "small"

    # Langfuse(Phase 10) — 모든 그래프의 LLM 호출 Trace/토큰/지연시간을 관측.
    # cloud.langfuse.com 무료 플랜 키를 쓴다 (셀프호스팅은 ClickHouse/Redis/MinIO까지
    # 필요해 이 프로젝트의 "과금 없이 가벼운 인프라" 원칙과 맞지 않는다).
    # Public/Secret Key가 비어있으면 langfuse SDK가 자동으로 no-op(전송 없음)로 동작하므로
    # 로컬에서 계정을 안 만들어도 나머지 AI 기능은 그대로 동작한다.
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Settings는 요청마다 새로 파싱할 필요가 없으므로 캐싱한다."""
    return Settings()
