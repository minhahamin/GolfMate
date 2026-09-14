"""AI 골프 일기 응답 스키마.

생성 요청은 JSON이 아니라 multipart/form-data(텍스트 또는 오디오 파일)라 별도의
DiaryCreate 모델 없이 라우터에서 Form/File을 직접 받는다.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DiaryListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    round_id: int | None
    summary: str
    mood: str
    created_at: datetime


class DiaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    round_id: int | None
    round_summary: str | None = None
    raw_text: str
    summary: str
    mood: str
    highlights: str
    improvement_points: str
    next_goal: str
    created_at: datetime
