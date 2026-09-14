"""그룹/멤버/내기 CRUD 엔드포인트 (Phase 9). 모두 로그인이 필요하고, 본인이 속한 그룹만
접근할 수 있다 (다른 그룹은 404).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.bet import BetCreate, BetListItem, BetRead
from app.schemas.group import AddMemberRequest, GroupCreate, GroupDetailRead, GroupRead
from app.services import bet_service, group_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupDetailRead, status_code=201)
def create_group(
    payload: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GroupDetailRead:
    group = group_service.create_group(db, current_user.id, payload.name)
    return GroupDetailRead(**group_service.to_detail_dict(group))


@router.get("", response_model=list[GroupRead])
def list_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[GroupRead]:
    return group_service.list_my_groups(db, current_user.id)


@router.get("/{group_id}", response_model=GroupDetailRead)
def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GroupDetailRead:
    group = group_service.get_group_detail(db, group_id, current_user.id)
    return GroupDetailRead(**group_service.to_detail_dict(group))


@router.post("/{group_id}/members", response_model=GroupDetailRead, status_code=201)
def add_member(
    group_id: int,
    payload: AddMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GroupDetailRead:
    group = group_service.add_member_by_email(db, group_id, current_user.id, payload.email)
    return GroupDetailRead(**group_service.to_detail_dict(group))


@router.delete("/{group_id}/members/{user_id}", status_code=204)
def remove_member(
    group_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    group_service.remove_member(db, group_id, current_user.id, user_id)


@router.post("/{group_id}/bets", response_model=BetRead, status_code=201)
def create_bet(
    group_id: int,
    payload: BetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BetRead:
    bet = bet_service.create_bet(
        db,
        group_id,
        current_user.id,
        title=payload.title,
        bet_date=payload.bet_date,
        course_name=payload.course_name,
        stake_per_stroke=payload.stake_per_stroke,
        scores=payload.scores,
    )
    return BetRead(**bet_service.to_read_dict(bet))


@router.get("/{group_id}/bets", response_model=list[BetListItem])
def list_bets(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BetListItem]:
    return bet_service.list_bets_for_group(db, group_id, current_user.id)
