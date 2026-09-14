"""골프장 추천 요청/응답 스키마 (Phase 7)."""
from pydantic import BaseModel, Field

from app.schemas.course import CourseRead


class CourseRecommendationRequest(BaseModel):
    region: str | None = Field(default=None, max_length=100)
    difficulty: str | None = Field(default=None, max_length=20)
    max_budget: int | None = Field(default=None, ge=0)
    preference_text: str = Field(default="", max_length=500)


class CourseRecommendation(BaseModel):
    course: CourseRead
    reason: str


class CourseRecommendationResponse(BaseModel):
    summary: str
    recommendations: list[CourseRecommendation]
