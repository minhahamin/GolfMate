"""AI 캐디 엔드포인트 (Phase 8).코스/홀은 공개 데이터라 소유권 확인이 필요 없고,
Coach와 마찬가지로 별도 서비스 계층 없이 라우터가 직접 조회 + 그래프 호출을 담당한다.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.caddie.graph import run_caddie_graph
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.repositories import course_repository
from app.schemas.caddie import CaddieRequest, CaddieResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/caddie", response_model=CaddieResponse)
def get_caddie_advice(
    payload: CaddieRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CaddieResponse:
    course = course_repository.get_by_id(db, payload.course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="골프장을 찾을 수 없습니다.")

    hole = next((h for h in course.holes if h.hole_number == payload.hole_number), None)
    if hole is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="해당 홀을 찾을 수 없습니다.")

    result = run_caddie_graph(db, current_user.id, course, hole, payload.question)
    return CaddieResponse(**result)
