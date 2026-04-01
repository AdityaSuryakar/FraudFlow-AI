import pytest
from score import calculate_score, get_risk_level_emoji, score_all_accounts, score_account


def test_score_all_accounts_sorts_descending_by_score():
    results = {
        "A": {"circular": {"flag": True, "details": {"cycle_lengths": [2]}}, "rapid": {"flag": False}, "structuring": {"flag": False}, "dormant": {"flag": False}},
        "B": {"circular": {"flag": False}, "rapid": {"flag": False}, "structuring": {"flag": False}, "dormant": {"flag": False}},
        "C": {"circular": {"flag": True, "details": {"cycle_lengths": [6]}}, "rapid": {"flag": True, "details": {"transaction_count": 1}}, "structuring": {"flag": False}, "dormant": {"flag": False}},
    }
    scored = score_all_accounts(results)
    scores = [acc["score"] for acc in scored]

    assert scores == sorted(scores, reverse=True)
    assert scored[0]["account_id"] == "A"
    assert scored[-1]["account_id"] == "B"


def test_get_risk_level_emoji_varieties():
    assert get_risk_level_emoji("allow") == "🟢"
    assert get_risk_level_emoji("flag") == "🟡"
    assert get_risk_level_emoji("alert") == "🔴"
    assert get_risk_level_emoji("unknown") == "⚪"


def test_calculate_score_caps_at_100_and_alert_from_combo():
    # force extremely high contributions (all patterns active with max values + combo)
    high_risk = {
        "circular": {"flag": True, "details": {"cycle_lengths": [1]}},
        "rapid": {"flag": True, "details": {"transaction_count": 10}},
        "structuring": {"flag": True, "details": {"transaction_count": 20}},
        "dormant": {"flag": True, "details": {"days_inactive": 365}},
    }

    score = calculate_score(high_risk)
    assert score == 100

    scored = score_account("X", high_risk)
    assert scored["level"] == "alert"
    assert scored["emoji"] == "🔴"


def test_score_account_factors_for_multiple_flags():
    detection = {
        "circular": {"flag": False},
        "rapid": {"flag": True, "details": {"transaction_count": 2}},
        "structuring": {"flag": True, "details": {"transaction_count": 1}},
        "dormant": {"flag": False},
    }

    scored = score_account("Z", detection)
    assert set(scored["factors"]) == {"rapid", "structuring"}
    assert scored["level"] in {"flag", "alert"}
