"""내기 단건 조회 엔드포인트 (Phase 9). 그룹 생성/멤버 추가는 routers/groups.py에 있다."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.bet import BetRead
from app.services import bet_service

router = APIRouter(prefix="/bets", tags=["bets"])


@router.get("/{bet_id}", response_model=BetRead)
def get_bet(
    bet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BetRead:
    bet = bet_service.get_bet_for_member(db, bet_id, current_user.id)
    return BetRead(**bet_service.to_read_dict(bet))
