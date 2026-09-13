"""라운드 CRUD + 통계 조회 비즈니스 로직.

모든 조회/수정/삭제는 반드시 user_id로 소유권을 확인한다 — 다른 사용자의 라운드는
존재 자체를 알 수 없도록 404로만 응답한다 (403이 아니다).
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.round import Round
from app.repositories import course_repository, round_repository
from app.schemas.round import RoundAnalysis, RoundCreate, RoundUpdate, StatisticsSummary
from app.services import statistics_service

NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="라운드를 찾을 수 없습니다.")


def _holes_to_dicts(holes) -> list[dict]:
    return [h.model_dump() for h in holes]


def create_round(db: Session, user_id: int, payload: RoundCreate) -> Round:
    if course_repository.get_by_id(db, payload.course_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="골프장을 찾을 수 없습니다.")

    score = sum(h.score for h in payload.holes) if payload.holes else payload.score

    round_ = round_repository.create(
        db,
        user_id=user_id,
        course_id=payload.course_id,
        round_date=payload.round_date,
        score=score,
        weather=payload.weather,
        temperature=payload.temperature,
        wind=payload.wind,
        memo=payload.memo,
    )

    if payload.holes:
        round_repository.replace_holes(db, round_.id, _holes_to_dicts(payload.holes))

    db.commit()
    return round_repository.get_by_id_for_user(db, round_.id, user_id)


def list_my_rounds(db: Session, user_id: int) -> list[Round]:
    return round_repository.list_by_user(db, user_id)


def get_my_round(db: Session, user_id: int, round_id: int) -> Round:
    round_ = round_repository.get_by_id_for_user(db, round_id, user_id)
    if round_ is None:
        raise NOT_FOUND
    return round_


def update_round(db: Session, user_id: int, round_id: int, payload: RoundUpdate) -> Round:
    get_my_round(db, user_id, round_id)  # 존재/소유권 확인

    fields = payload.model_dump(exclude_unset=True, exclude={"holes"})

    if payload.holes is not None:
        round_repository.replace_holes(db, round_id, _holes_to_dicts(payload.holes))
        fields["score"] = sum(h.score for h in payload.holes)

    round_ = round_repository.get_by_id_for_user(db, round_id, user_id)
    round_repository.update_fields(db, round_, fields)
    db.commit()
    return round_repository.get_by_id_for_user(db, round_id, user_id)


def delete_round(db: Session, user_id: int, round_id: int) -> None:
    round_ = get_my_round(db, user_id, round_id)
    round_repository.delete(db, round_)
    db.commit()


def get_round_analysis(db: Session, user_id: int, round_id: int) -> RoundAnalysis:
    round_ = get_my_round(db, user_id, round_id)
    return statistics_service.compute_round_analysis(round_)


def get_statistics_summary(db: Session, user_id: int, limit: int = 10) -> StatisticsSummary:
    rounds = round_repository.list_recent_by_user(db, user_id, limit)
    return statistics_service.compute_statistics_summary(rounds)
