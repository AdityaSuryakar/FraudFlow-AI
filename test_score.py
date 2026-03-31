import pytest
from score import calculate_score, get_risk_level, score_account


def test_calculate_score_no_flags_returns_zero():
    result = calculate_score({
        "circular": {"flag": False},
        "rapid": {"flag": False},
        "structuring": {"flag": False},
        "dormant": {"flag": False}
    })
    assert result == 0


def test_calculate_score_circular_short_cycle_high_risk():
    result = calculate_score({
        "circular": {"flag": True, "details": {"cycle_lengths": [3]}},
        "rapid": {"flag": False},
        "structuring": {"flag": False},
        "dormant": {"flag": False}
    })
    assert result == 50


def test_calculate_score_combination_bonus_applied():
    result = calculate_score({
        "circular": {"flag": True, "details": {"cycle_lengths": [6]}},
        "rapid": {"flag": True, "details": {"transaction_count": 4}},
        "structuring": {"flag": True, "details": {"transaction_count": 3}},
        "dormant": {"flag": False}
    })
    # circular(20) + rapid(percentage) + structuring + combo
    assert result >= 60
    assert result <= 100


def test_get_risk_level_boundaries():
    assert get_risk_level(10) == "allow"
    assert get_risk_level(30) == "flag"
    assert get_risk_level(70) == "flag"
    assert get_risk_level(71) == "alert"


def test_score_account_includes_expected_fields():
    scored = score_account("A123", {
        "circular": {"flag": False},
        "rapid": {"flag": False},
        "structuring": {"flag": False},
        "dormant": {"flag": False}
    })

    assert scored["account_id"] == "A123"
    assert scored["level"] == "allow"
    assert scored["emoji"] == "🟢"
    assert scored["factors"] == []
