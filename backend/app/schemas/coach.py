"""AI Coach 요청/응답 스키마."""
from pydantic import BaseModel, Field


class CoachRequest(BaseModel):
    question: str = Field(default="", max_length=500)


class CoachResponse(BaseModel):
    current_state: str
    biggest_problem: str
    cause: str
    strategy: str
    next_goal: str
