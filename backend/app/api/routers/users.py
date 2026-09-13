"""로그인한 사용자 본인의 정보/프로필 엔드포인트.

모든 라우트가 get_current_user에 의존하므로, 다른 사용자의 데이터는 절대 조회할 수 없다.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.golfer_profile import GolferProfileRead, GolferProfileUpdate
from app.schemas.user import UserRead
from app.services import profile_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/me/profile", response_model=GolferProfileRead)
def read_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GolferProfileRead:
    return profile_service.get_my_profile(db, current_user.id)


@router.put("/me/profile", response_model=GolferProfileRead)
def update_my_profile(
    payload: GolferProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GolferProfileRead:
    return profile_service.update_my_profile(db, current_user.id, payload)
