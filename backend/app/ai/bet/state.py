"""내기 AI 코멘터리(Phase 9) LangGraph의 State. 다른 그래프와 마찬가지로 전용이며
공유하지 않는다.
"""
from typing import TypedDict


class BetCommentaryState(TypedDict, total=False):
    user_id: int
    bet: object  # Bet ORM 인스턴스 (results까지 eager load된 상태)
    commentary: str
    error: str | None
