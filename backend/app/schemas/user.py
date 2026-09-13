"""User 관련 요청/응답 스키마.

비밀번호 해시(hashed_password)는 어떤 응답 스키마에도 절대 포함하지 않는다.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    created_at: datetime
