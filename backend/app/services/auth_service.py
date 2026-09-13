"""회원가입/로그인 비즈니스 로직.

라우터는 이 서비스만 호출하고, 비밀번호 해싱이나 SQL은 직접 다루지 않는다.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import golfer_profile_repository, user_repository
from app.schemas.auth import AuthResponse, UserCreate, UserLogin


def register(db: Session, payload: UserCreate) -> AuthResponse:
    if user_repository.get_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다.",
        )

    user = user_repository.create(
        db,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
    )
    golfer_profile_repository.create_empty(db, user_id=user.id)
    db.commit()
    db.refresh(user)

    return _build_auth_response(user)


def login(db: Session, payload: UserLogin) -> AuthResponse:
    user = user_repository.get_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    return _build_auth_response(user)


def _build_auth_response(user: User) -> AuthResponse:
    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user=user)
