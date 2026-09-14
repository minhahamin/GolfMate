"""Course/CourseHole 응답 스키마."""
from pydantic import BaseModel, ConfigDict


class CourseHoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hole_number: int
    par: int
    distance_meters: int


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    region: str
    address: str | None = None
    description: str | None = None
    holes_count: int
    par: int
    difficulty: str
    green_fee_avg: int | None = None
    tags: str | None = None


class CourseDetailRead(CourseRead):
    holes: list[CourseHoleRead] = []
