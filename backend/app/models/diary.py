"""Diary 테이블 — 사용자가 라운드 소감을 적거나 녹음하면 AI가 정리한 골프 일기.

round_id는 Round/Hole처럼 소유(cascade) 관계가 아니라 느슨한 참조라 CASCADE가 아닌
SET NULL을 쓴다 — 연결된 라운드가 삭제돼도 일기 자체는 남아야 한다.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.round import Round

# app/ai/diary/graph.py가 LLM 응답을 이 길이로 강제 자른다 — 무료 모델이 프롬프트의
# "5단어 이내" 지시를 어겨도 DB DataError(StringDataRightTruncation)로 요청 전체가
# 실패하지 않도록 하는 안전장치.
MOOD_MAX_LENGTH = 50


class Diary(Base):
    __tablename__ = "diaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    round_id: Mapped[int | None] = mapped_column(
        ForeignKey("rounds.id", ondelete="SET NULL"), nullable=True
    )

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    mood: Mapped[str] = mapped_column(String(MOOD_MAX_LENGTH), nullable=False)
    highlights: Mapped[str] = mapped_column(Text, nullable=False)
    improvement_points: Mapped[str] = mapped_column(Text, nullable=False)
    next_goal: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    round: Mapped["Round | None"] = relationship()
