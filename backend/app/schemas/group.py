"""그룹/멤버 요청·응답 스키마 (Phase 9)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class AddMemberRequest(BaseModel):
    email: EmailStr


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    owner_id: int
    created_at: datetime


class GroupMemberRead(BaseModel):
    user_id: int
    name: str
    email: str
    joined_at: datetime


class GroupDetailRead(GroupRead):
    members: list[GroupMemberRead] = []
