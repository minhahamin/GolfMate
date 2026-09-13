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
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Settings는 요청마다 새로 파싱할 필요가 없으므로 캐싱한다."""
    return Settings()
