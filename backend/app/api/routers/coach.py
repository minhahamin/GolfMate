"""AI Coach 엔드포인트."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.coach.graph import run_coach_graph
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.coach import CoachRequest, CoachResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/coach", response_model=CoachResponse)
def get_coach_analysis(
    payload: CoachRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CoachResponse:
    answer = run_coach_graph(db, current_user.id, payload.question)
    return CoachResponse(**answer)
