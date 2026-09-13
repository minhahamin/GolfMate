"""라운드 CRUD + 통계 엔드포인트. 모두 로그인이 필요하고, 본인 라운드만 다룬다."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.round import (
    RoundAnalysis,
    RoundCreate,
    RoundListItem,
    RoundRead,
    RoundUpdate,
    StatisticsSummary,
)
from app.services import round_service

router = APIRouter(prefix="/rounds", tags=["rounds"])


@router.get("", response_model=list[RoundListItem])
def list_rounds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RoundListItem]:
    return round_service.list_my_rounds(db, current_user.id)


@router.post("", response_model=RoundRead, status_code=201)
def create_round(
    payload: RoundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoundRead:
    return round_service.create_round(db, current_user.id, payload)


@router.get("/statistics/summary", response_model=StatisticsSummary)
def get_statistics_summary(
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StatisticsSummary:
    return round_service.get_statistics_summary(db, current_user.id, limit)


@router.get("/{round_id}", response_model=RoundRead)
def get_round(
    round_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoundRead:
    return round_service.get_my_round(db, current_user.id, round_id)


@router.put("/{round_id}", response_model=RoundRead)
def update_round(
    round_id: int,
    payload: RoundUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoundRead:
    return round_service.update_round(db, current_user.id, round_id, payload)


@router.delete("/{round_id}", status_code=204)
def delete_round(
    round_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    round_service.delete_round(db, current_user.id, round_id)


@router.get("/{round_id}/analysis", response_model=RoundAnalysis)
def get_round_analysis(
    round_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RoundAnalysis:
    return round_service.get_round_analysis(db, current_user.id, round_id)
