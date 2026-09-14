"""Course 테이블 — 골프장 기본 정보.

Phase 3에서는 seed_courses.py로 넣은 mock 데이터만 존재한다. Phase 7에서 실제 골프장
API/DB로 교체될 때도 이 테이블 구조(및 CourseHole)는 그대로 유지된다.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.course_hole import CourseHole


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    holes_count: Mapped[int] = mapped_column(Integer, default=18)
    par: Mapped[int] = mapped_column(Integer, default=72)

    # Phase 7 골프장 추천용 필드 — search_service가 이 값들로 후보를 필터링하고,
    # LLM에게는 필터링된 후보만 넘겨 실존하지 않는 골프장을 추천하지 않게 한다.
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="중급")
    green_fee_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 콤마 구분, 예: "바다전망,링크스"

    # Phase 8 AI 캐디용 — 실제 지역 좌표(Open-Meteo 등 외부 날씨 API 호출에 쓴다, 키 불필요).
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    holes: Mapped[list["CourseHole"]] = relationship(
        back_populates="course", order_by="CourseHole.hole_number", cascade="all, delete-orphan"
    )
