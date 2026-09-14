"""내기 정산 계산 단위 테스트 — DB/HTTP 없이 순수 함수만 검증한다.

설계 원칙 5번("내기 금액 계산은 LLM이 아닌 Python 코드가 담당하고 별도로 테스트한다")을
지키기 위한 핵심 테스트. 타당 내기 규칙: 모든 쌍에 대해 스코어가 낮은 쪽이 스코어가 높은
쪽에게서 (타수 차 × stake_per_stroke)를 받는다.
"""
from app.services.bet_service import calculate_settlement


def test_two_players_lower_score_wins():
    payouts = calculate_settlement({1: 90, 2: 95}, stake_per_stroke=1000)

    assert payouts[1] == 5000  # 5타 적게 쳐서 5000원 받음
    assert payouts[2] == -5000


def test_tied_scores_result_in_zero_payout():
    payouts = calculate_settlement({1: 90, 2: 90}, stake_per_stroke=1000)

    assert payouts[1] == 0
    assert payouts[2] == 0


def test_three_players_pairwise_settlement():
    # A=88, B=92, C=95 / stake=1000
    # A vs B: A가 4타 적음 -> A +4000, B -4000
    # A vs C: A가 7타 적음 -> A +7000, C -7000
    # B vs C: B가 3타 적음 -> B +3000, C -3000
    payouts = calculate_settlement({"A": 88, "B": 92, "C": 95}, stake_per_stroke=1000)

    assert payouts["A"] == 11000  # 4000 + 7000
    assert payouts["B"] == -1000  # -4000 + 3000
    assert payouts["C"] == -10000  # -7000 + -3000


def test_settlement_is_always_zero_sum():
    for scores in [
        {1: 80, 2: 85, 3: 90, 4: 95},
        {1: 100, 2: 100, 3: 70},
        {1: 72, 2: 150},
    ]:
        payouts = calculate_settlement(scores, stake_per_stroke=500)
        assert sum(payouts.values()) == 0


def test_zero_stake_produces_zero_payouts():
    payouts = calculate_settlement({1: 80, 2: 100}, stake_per_stroke=0)

    assert payouts[1] == 0
    assert payouts[2] == 0


def test_single_participant_has_no_settlement():
    payouts = calculate_settlement({1: 90}, stake_per_stroke=1000)

    assert payouts == {1: 0}
