"""헬스체크 엔드포인트.

Phase 1에서는 React <-> FastAPI <-> PostgreSQL 연결이 실제로 동작하는지
증명하는 용도로 사용한다. 인증이 필요 없는 공개 엔드포인트다.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def check_liveness() -> dict[str, str]:
    """서버 프로세스가 살아있는지만 확인한다 (DB 접근 없음)."""
    return {"status": "ok"}


@router.get("/db")
def check_database(db: Session = Depends(get_db)) -> dict[str, str]:
    """DB에 실제 쿼리를 날려 커넥션이 정상인지 확인한다."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
