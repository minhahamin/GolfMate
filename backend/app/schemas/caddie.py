"""AI 캐디 요청/응답 스키마 (Phase 8)."""
from pydantic import BaseModel, Field


class CaddieRequest(BaseModel):
    course_id: int
    hole_number: int = Field(ge=1, le=18)
    question: str = Field(default="", max_length=300)


class CaddieResponse(BaseModel):
    weather_summary: str | None = None
    hole_analysis: str
    risk_analysis: str
    club_strategy: str
