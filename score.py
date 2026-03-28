"""
score.py — Enhanced Risk Scoring Module (Version 2)

Improvement:
- Dynamic scoring (not fixed weights only)
- Uses pattern details (cycle length, txn count)
- Adds combination bonus
- Produces varied scores (realistic behavior)
"""

import json

# Base weights
WEIGHT_CIRCULAR = 40
WEIGHT_RAPID = 20
WEIGHT_STRUCTURING = 25
WEIGHT_DORMANT = 15

# Thresholds
THRESHOLD_LOW = 30
THRESHOLD_HIGH = 70


def calculate_score(detection_results):
    score = 0

    # 🔴 CIRCULAR (dynamic based on cycle length)
    if detection_results.get("circular", {}).get("flag"):
        details = detection_results["circular"].get("details", {})
        lengths = details.get("cycle_lengths", [])

        if lengths:
            min_len = min(lengths)
            if min_len <= 3:
                score += 50   # 🔥 high risk
            elif min_len <= 5:
                score += 35
            else:
                score += 20
        else:
            score += WEIGHT_CIRCULAR

    # ⚡ RAPID (based on number of transactions)
    if detection_results.get("rapid", {}).get("flag"):
        details = detection_results["rapid"].get("details", {})
        count = details.get("transaction_count", 1)

        score += min(10 + count * 3, 30)  # scaled contribution

    # 💰 STRUCTURING
    if detection_results.get("structuring", {}).get("flag"):
        details = detection_results["structuring"].get("details", {})
        count = details.get("transaction_count", 1)

        score += min(15 + count * 2, 35)

    # 😴 DORMANT
    if detection_results.get("dormant", {}).get("flag"):
        details = detection_results["dormant"].get("details", {})
        days = details.get("days_inactive", 0)

        if days > 180:
            score += 25
        else:
            score += WEIGHT_DORMANT

    # 🔥 COMBINATION BONUS (VERY IMPORTANT)
    active_patterns = sum(
        1 for v in detection_results.values() if v.get("flag")
    )

    if active_patterns >= 2:
        score += 15
    if active_patterns >= 3:
        score += 10

    return min(score, 100)


def get_risk_level(score):
    if score < THRESHOLD_LOW:
        return "allow"
    elif score <= THRESHOLD_HIGH:
        return "flag"
    else:
        return "alert"


def get_risk_level_emoji(level):
    return {"allow": "🟢", "flag": "🟡", "alert": "🔴"}.get(level, "⚪")


def score_account(account_id, detection_results):
    score = calculate_score(detection_results)
    level = get_risk_level(score)

    factors = []
    for k, v in detection_results.items():
        if v.get("flag"):
            factors.append(k)

    return {
        "account_id": account_id,
        "score": score,
        "level": level,
        "emoji": get_risk_level_emoji(level),
        "factors": factors
    }


def score_all_accounts(all_detection_results):
    scored = []

    for account_id, detection_results in all_detection_results.items():
        scored.append(score_account(account_id, detection_results))

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def print_score_summary(scored_accounts, top_n=20):
    print("\n" + "=" * 80)
    print("ENHANCED RISK SCORING SUMMARY")
    print("=" * 80)

    counts = {"allow": 0, "flag": 0, "alert": 0}

    for acc in scored_accounts:
        counts[acc["level"]] += 1

    print(f"\nDistribution:")
    print(f"🟢 Allow:  {counts['allow']}")
    print(f"🟡 Flag:   {counts['flag']}")
    print(f"🔴 Alert:  {counts['alert']}")

    print("\nTop Risk Accounts:")
    print("-" * 60)

    for acc in scored_accounts[:top_n]:
        print(f"{acc['emoji']} {acc['account_id']} → Score: {acc['score']} → {acc['level']} ({', '.join(acc['factors'])})")


def export_scores(scored_accounts, filepath="risk_scores.json"):
    with open(filepath, "w") as f:
        json.dump(scored_accounts, f, indent=2, default=str)

    print(f"\nScores exported to: {filepath}")