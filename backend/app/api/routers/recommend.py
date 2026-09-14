"""골프장 추천 엔드포인트 (Phase 7). Coach와 마찬가지로 별도 서비스 계층 없이
그래프를 직접 호출한다 — DB 쓰기가 없는 상태 없는(stateless) 요청/응답이기 때문이다.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.recommend.graph import run_recommend_graph
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.recommend import CourseRecommendationRequest, CourseRecommendationResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/recommend-courses", response_model=CourseRecommendationResponse)
def recommend_courses(
    payload: CourseRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseRecommendationResponse:
    result = run_recommend_graph(
        db,
        current_user.id,
        region=payload.region,
        difficulty=payload.difficulty,
        max_budget=payload.max_budget,
        preference_text=payload.preference_text,
    )
    return CourseRecommendationResponse(**result)
