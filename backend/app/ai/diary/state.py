"""AI 골프 일기(Phase 6) LangGraph의 State.

Coach 그래프(app/ai/coach/state.py)와 마찬가지로 이 State는 Diary 그래프 전용이며
다른 그래프와 공유하지 않는다. STT는 그래프 진입 전 서비스 계층에서 처리하므로(이유는
app/ai/diary/graph.py 상단 주석 참고) raw_text는 이미 확보된 상태로 들어온다.
"""
from typing import TypedDict


class DiaryState(TypedDict, total=False):
    user_id: int
    raw_text: str
    round_id_hint: int | None  # 사용자가 폼에서 직접 라운드를 선택했다면 그 id (매칭 생략)

    recent_rounds: list  # 매칭 후보 (Round ORM 인스턴스 목록)
    matched_round_id: int | None

    summary: str
    mood: str
    highlights: str
    improvement_points: str
    next_goal: str
    error: str | None
