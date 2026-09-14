"""골프 내기 정산 — **LLM이 아닌 순수 Python이 금액을 계산한다** (설계 원칙 5번).

타당 내기(가장 흔한 방식): 참가자 모든 쌍에 대해 스코어가 낮은 쪽이 스코어가 높은 쪽에게서
(타수 차 × stake_per_stroke)를 받는다. 한 사람의 최종 정산액은 모든 쌍별 승패를 합산한
값이다 — 제로섬(전체 합은 항상 0)이 되도록 설계했다.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bet import Bet
from app.repositories import bet_repository, group_repository

NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="내기를 찾을 수 없습니다.")


def to_read_dict(bet: Bet) -> dict:
    return {
        "id": bet.id,
        "group_id": bet.group_id,
        "title": bet.title,
        "bet_date": bet.bet_date,
        "course_name": bet.course_name,
        "stake_per_stroke": bet.stake_per_stroke,
        "created_at": bet.created_at,
        "results": [
            {
                "user_id": r.user_id,
                "name": r.user.name,
                "score": r.score,
                "payout_amount": r.payout_amount,
            }
            for r in bet.results
        ],
    }


def calculate_settlement(scores: dict[int, int], stake_per_stroke: int) -> dict[int, int]:
    """user_id -> score 맵을 받아 user_id -> 정산 금액(양수=받음, 음수=지불) 맵을 반환한다.

    참가자가 2명 미만이면 정산할 대상이 없다.
    """
    payouts = {user_id: 0 for user_id in scores}
    user_ids = list(scores.keys())

    for i in range(len(user_ids)):
        for j in range(i + 1, len(user_ids)):
            a, b = user_ids[i], user_ids[j]
            # b가 a보다 타수가 많으면(스코어가 나쁘면) 양수 — a가 b에게서 받는다.
            diff = scores[b] - scores[a]
            amount = diff * stake_per_stroke
            payouts[a] += amount
            payouts[b] -= amount

    return payouts


def create_bet(
    db: Session,
    group_id: int,
    creator_id: int,
    *,
    title: str,
    bet_date,
    course_name: str,
    stake_per_stroke: int,
    scores: dict[int, int],
) -> Bet:
    group = group_repository.get_by_id_for_member(db, group_id, creator_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="그룹을 찾을 수 없습니다.")

    member_ids = {m.user_id for m in group.members}
    non_member_ids = set(scores.keys()) - member_ids
    if non_member_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="그룹 멤버가 아닌 참가자가 포함되어 있습니다.",
        )
    if len(scores) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="참가자는 2명 이상이어야 합니다."
        )

    payouts = calculate_settlement(scores, stake_per_stroke)

    bet = bet_repository.create(
        db,
        group_id=group_id,
        created_by=creator_id,
        title=title,
        bet_date=bet_date,
        course_name=course_name,
        stake_per_stroke=stake_per_stroke,
    )
    bet_repository.create_results(
        db,
        bet.id,
        [
            {"user_id": user_id, "score": scores[user_id], "payout_amount": payouts[user_id]}
            for user_id in scores
        ],
    )
    db.commit()
    return bet_repository.get_by_id(db, bet.id)


def get_bet_for_member(db: Session, bet_id: int, user_id: int) -> Bet:
    bet = bet_repository.get_by_id(db, bet_id)
    if bet is None or group_repository.get_by_id_for_member(db, bet.group_id, user_id) is None:
        raise NOT_FOUND
    return bet


def list_bets_for_group(db: Session, group_id: int, user_id: int) -> list[Bet]:
    if group_repository.get_by_id_for_member(db, group_id, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="그룹을 찾을 수 없습니다.")
    return bet_repository.list_by_group(db, group_id)
