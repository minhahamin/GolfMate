"""SQLAlchemy 엔진/세션 설정.

DB 관련 로직은 이 모듈에만 두고, 다른 레이어(router/service/repository)는
여기서 만든 engine/SessionLocal/get_db만 가져다 쓴다.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용 DB 세션 제공자."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
