"""AI Coach LangGraph의 State. 마스터 스펙 §12 GolfCoachState를 따른다.

모든 것을 하나의 거대한 State에 넣지 않는다는 원칙에 따라, 이 State는 Coach 그래프
전용이며 다른 그래프(향후 Caddie 등)와 공유하지 않는다.
"""
from typing import TypedDict


class GolfCoachState(TypedDict, total=False):
    user_id: int
    question: str

    golfer_profile: object | None  # GolferProfile ORM 인스턴스 (또는 None)
    recent_rounds: list  # Round ORM 인스턴스 목록 (statistics_service가 그대로 소비)
    statistics: dict
    has_data: bool
    retrieved_knowledge: list  # GolfKnowledge ORM 인스턴스 목록 (RAG 검색 결과)

    final_answer: dict[str, str]
    error: str | None
