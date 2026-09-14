"""골프장 추천(Phase 7) LangGraph의 State. Coach/Diary와 마찬가지로 그래프 전용이며
다른 그래프와 공유하지 않는다.
"""
from typing import TypedDict


class RecommendState(TypedDict, total=False):
    user_id: int
    region: str | None
    difficulty: str | None
    max_budget: int | None
    preference_text: str

    golfer_profile: object | None
    candidates: list  # Course ORM 인스턴스 목록 (검색/필터링된 실제 후보)

    ranked: list[dict]  # [{course_id, reason}, ...] — 후보 밖 id는 validator가 제거
    summary: str
    error: str | None
