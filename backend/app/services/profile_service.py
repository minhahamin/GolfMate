"""골퍼 프로필 조회/수정 비즈니스 로직."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.golfer_profile import GolferProfile
from app.repositories import golfer_profile_repository
from app.schemas.golfer_profile import GolferProfileUpdate


def get_my_profile(db: Session, user_id: int) -> GolferProfile:
    profile = golfer_profile_repository.get_by_user_id(db, user_id)
    if profile is None:
        # 회원가입 시 항상 빈 프로필을 함께 만들기 때문에 정상적으로는 발생하지 않는다.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="골퍼 프로필을 찾을 수 없습니다.",
        )
    return profile


def update_my_profile(db: Session, user_id: int, payload: GolferProfileUpdate) -> GolferProfile:
    profile = get_my_profile(db, user_id)
    fields = payload.model_dump(exclude_unset=True)
    golfer_profile_repository.update(db, profile, fields)
    db.commit()
    db.refresh(profile)
    return profile
