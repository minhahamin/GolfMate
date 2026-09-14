"""모든 모델을 여기서 import해두어야 Base.metadata에 등록되고,
Alembic autogenerate가 테이블 변경을 감지할 수 있다.
"""
from app.models.base import Base
from app.models.bet import Bet
from app.models.bet_result import BetResult
from app.models.course import Course
from app.models.course_hole import CourseHole
from app.models.diary import Diary
from app.models.golf_knowledge import GolfKnowledge
from app.models.golfer_profile import GolferProfile
from app.models.group import Group
from app.models.group_member import GroupMember
from app.models.hole import Hole
from app.models.round import Round
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "GolferProfile",
    "Course",
    "CourseHole",
    "Round",
    "Hole",
    "GolfKnowledge",
    "Diary",
    "Group",
    "GroupMember",
    "Bet",
    "BetResult",
]
