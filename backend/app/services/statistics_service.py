"""라운드 통계 계산 — 순수 Python, LLM 호출이 전혀 없다.

여기서 만드는 계산 로직은 Phase 4 AI Coach가 "최근 라운드 통계"를 가져올 때 그대로
재사용한다 (계산은 코드가, 판단/설명은 LLM이 담당한다는 원칙).
"""
from app.models.round import Round
from app.schemas.round import RecentRoundPoint, RoundAnalysis, StatisticsSummary


def compute_round_analysis(round_: Round) -> RoundAnalysis:
    holes = round_.holes

    if not holes:
        score_to_par = round_.score - round_.course.par if round_.course else None
        return RoundAnalysis(score=round_.score, score_to_par=score_to_par, has_hole_detail=False)

    total_par = sum(h.par for h in holes)
    putts_total = sum(h.putts for h in holes)
    # 파3은 티샷이 페어웨이 개념이 아니므로 페어웨이 적중률 계산에서 제외한다.
    fairway_holes = [h for h in holes if h.par != 3]
    par_groups = {3: [], 4: [], 5: []}
    for h in holes:
        if h.par in par_groups:
            par_groups[h.par].append(h.score)

    def avg(values: list[int]) -> float | None:
        return round(sum(values) / len(values), 2) if values else None

    return RoundAnalysis(
        score=round_.score,
        score_to_par=round_.score - total_par,
        has_hole_detail=True,
        putts_total=putts_total,
        putts_average=round(putts_total / len(holes), 2),
        fairway_hit_rate=(
            round(sum(1 for h in fairway_holes if h.fairway_hit) / len(fairway_holes) * 100, 1)
            if fairway_holes
            else None
        ),
        gir_rate=round(sum(1 for h in holes if h.gir) / len(holes) * 100, 1),
        ob_count=sum(h.ob for h in holes),
        bunker_count=sum(h.bunker for h in holes),
        penalty_count=sum(h.penalty for h in holes),
        par3_average=avg(par_groups[3]),
        par4_average=avg(par_groups[4]),
        par5_average=avg(par_groups[5]),
    )


def compute_statistics_summary(rounds: list[Round]) -> StatisticsSummary:
    """rounds는 최신순(내림차순)으로 정렬되어 들어온다고 가정한다."""
    if not rounds:
        return StatisticsSummary(rounds_count=0)

    scores = [r.score for r in rounds]
    rounds_with_holes = [r for r in rounds if r.holes]

    putts_per_round = [sum(h.putts for h in r.holes) for r in rounds_with_holes]
    fairway_rates: list[float] = []
    gir_rates: list[float] = []
    for r in rounds_with_holes:
        fw_holes = [h for h in r.holes if h.par != 3]
        if fw_holes:
            fairway_rates.append(sum(1 for h in fw_holes if h.fairway_hit) / len(fw_holes) * 100)
        gir_rates.append(sum(1 for h in r.holes if h.gir) / len(r.holes) * 100)

    return StatisticsSummary(
        rounds_count=len(rounds),
        average_score=round(sum(scores) / len(scores), 1),
        best_score=min(scores),
        average_putts=round(sum(putts_per_round) / len(putts_per_round), 1) if putts_per_round else None,
        average_fairway_rate=round(sum(fairway_rates) / len(fairway_rates), 1) if fairway_rates else None,
        average_gir_rate=round(sum(gir_rates) / len(gir_rates), 1) if gir_rates else None,
        # 차트는 시간순(오래된 -> 최신)으로 보여줘야 하므로 뒤집는다.
        recent_rounds=[
            RecentRoundPoint(round_date=r.round_date, score=r.score) for r in reversed(rounds)
        ],
    )
