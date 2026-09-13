"""Round/Hole 요청·응답 스키마 및 통계 응답 스키마."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.course import CourseRead


class HoleInput(BaseModel):
    hole_number: int = Field(ge=1, le=18)
    par: int = Field(ge=3, le=5)
    score: int = Field(ge=1)
    putts: int = Field(ge=0)
    fairway_hit: bool = False
    gir: bool = False
    ob: int = Field(default=0, ge=0)
    bunker: int = Field(default=0, ge=0)
    penalty: int = Field(default=0, ge=0)


class HoleRead(HoleInput):
    model_config = ConfigDict(from_attributes=True)


class RoundBase(BaseModel):
    course_id: int
    round_date: date
    weather: str | None = None
    temperature: float | None = None
    wind: str | None = None
    memo: str | None = None


class RoundCreate(RoundBase):
    # 홀 상세를 입력하면 score는 서버가 홀 점수 합으로 계산하므로, 이 경우 score는 선택이다.
    score: int | None = None
    holes: list[HoleInput] | None = None

    @model_validator(mode="after")
    def require_score_or_holes(self) -> "RoundCreate":
        if self.score is None and not self.holes:
            raise ValueError("score 또는 holes 중 하나는 반드시 입력해야 합니다.")
        return self


class RoundUpdate(BaseModel):
    round_date: date | None = None
    score: int | None = None
    weather: str | None = None
    temperature: float | None = None
    wind: str | None = None
    memo: str | None = None
    holes: list[HoleInput] | None = None


class RoundListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course: CourseRead
    round_date: date
    score: int


class RoundRead(RoundListItem):
    weather: str | None = None
    temperature: float | None = None
    wind: str | None = None
    memo: str | None = None
    holes: list[HoleRead] = []
    created_at: datetime


class RoundAnalysis(BaseModel):
    score: int
    score_to_par: int | None = None
    has_hole_detail: bool

    putts_total: int | None = None
    putts_average: float | None = None
    fairway_hit_rate: float | None = None
    gir_rate: float | None = None
    ob_count: int | None = None
    bunker_count: int | None = None
    penalty_count: int | None = None

    par3_average: float | None = None
    par4_average: float | None = None
    par5_average: float | None = None


class RecentRoundPoint(BaseModel):
    round_date: date
    score: int


class StatisticsSummary(BaseModel):
    rounds_count: int
    average_score: float | None = None
    best_score: int | None = None
    average_putts: float | None = None
    average_fairway_rate: float | None = None
    average_gir_rate: float | None = None
    recent_rounds: list[RecentRoundPoint] = []
