"""GolferProfile 관련 요청/응답 스키마."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GolferProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    handicap: float | None = None
    average_score: float | None = None
    driver_distance: float | None = None
    iron_distance: float | None = None
    putting_average: float | None = None
    fairway_percentage: float | None = None
    gir_percentage: float | None = None
    preferred_tee: str | None = None
    goal_score: int | None = None
    created_at: datetime


class GolferProfileUpdate(BaseModel):
    """Phase 2에서 프로필 수정 API가 붙을 때 사용할 입력 스키마."""

    handicap: float | None = None
    average_score: float | None = None
    driver_distance: float | None = None
    iron_distance: float | None = None
    putting_average: float | None = None
    fairway_percentage: float | None = None
    gir_percentage: float | None = None
    preferred_tee: str | None = None
    goal_score: int | None = None
