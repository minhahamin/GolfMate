"""AI 캐디(Phase 8) LangGraph의 State. Coach/Diary/Recommend와 마찬가지로 그래프 전용이며
다른 그래프와 공유하지 않는다.

course/hole은 라우터가 이미 소유권/존재 여부와 무관하게(코스는 공개 데이터) 조회해 넘겨준
ORM 인스턴스를 그대로 받는다 — Recommend의 candidates와 달리 매칭이 필요 없는 단일 대상이라
그래프 안에서 다시 조회하지 않는다.
"""
from typing import TypedDict


class CaddieState(TypedDict, total=False):
    user_id: int
    course: object  # Course ORM 인스턴스
    hole: object  # CourseHole ORM 인스턴스
    question: str

    golfer_profile: object | None
    weather: dict | None
    weather_summary: str

    hole_analysis: str
    risk_analysis: str
    club_strategy: str
    error: str | None
