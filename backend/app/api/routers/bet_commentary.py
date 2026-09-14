"""내기 AI 코멘터리 엔드포인트 (Phase 9). 정산 금액은 이미 계산이 끝난 값을 그대로
설명만 한다 — 여기서 다시 계산하지 않는다.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.bet.graph import run_bet_commentary_graph
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.bet import BetCommentaryRequest, BetCommentaryResponse
from app.services import bet_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/bet-commentary", response_model=BetCommentaryResponse)
def get_bet_commentary(
    payload: BetCommentaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BetCommentaryResponse:
    bet = bet_service.get_bet_for_member(db, payload.bet_id, current_user.id)
    commentary = run_bet_commentary_graph(current_user.id, bet)
    return BetCommentaryResponse(commentary=commentary)
