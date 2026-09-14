"""내기 요청·응답 스키마 (Phase 9).

정산 금액(payout_amount)은 항상 app/services/bet_service.calculate_settlement()가 계산한
값이다 — 클라이언트가 직접 보내지 않는다.
"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BetCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    bet_date: date
    course_name: str = Field(min_length=1, max_length=200)
    stake_per_stroke: int = Field(ge=0)
    scores: dict[int, int] = Field(description="참가자 user_id -> 스코어(총 타수)")

    @model_validator(mode="after")
    def require_at_least_two_participants(self) -> "BetCreate":
        if len(self.scores) < 2:
            raise ValueError("참가자는 2명 이상이어야 합니다.")
        return self


class BetResultRead(BaseModel):
    user_id: int
    name: str
    score: int
    payout_amount: int


class BetListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    bet_date: date
    course_name: str
    created_at: datetime


class BetRead(BetListItem):
    group_id: int
    stake_per_stroke: int
    results: list[BetResultRead] = []


class BetCommentaryRequest(BaseModel):
    bet_id: int


class BetCommentaryResponse(BaseModel):
    commentary: str
