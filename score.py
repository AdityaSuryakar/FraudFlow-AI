"""
score.py — Risk scoring module
Combines pattern flags into 0-100 risk score using weighted formula.

Formula:
    score = (circular × 40) + (rapid_hops × 20) + (structuring × 25) + (dormant × 15)

Thresholds:
    <30  = allow (low risk)
    30-70 = flag (medium risk)
    >70  = alert (high risk)
"""

import json

# Weight constants
WEIGHT_CIRCULAR = 40
WEIGHT_RAPID = 20
WEIGHT_STRUCTURING = 25
WEIGHT_DORMANT = 15

# Threshold constants
THRESHOLD_LOW = 30
THRESHOLD_HIGH = 70


def calculate_score(detection_results):
    """
    Calculate risk score from detection results.
    
    Args:
        detection_results: dict with keys 'circular', 'rapid', 'structuring', 'dormant'
                          each containing a dict with 'flag' boolean
    
    Returns:
        int: risk score 0-100
    """
    circular = 1 if detection_results.get("circular", {}).get("flag", False) else 0
    rapid = 1 if detection_results.get("rapid", {}).get("flag", False) else 0
    structuring = 1 if detection_results.get("structuring", {}).get("flag", False) else 0
    dormant = 1 if detection_results.get("dormant", {}).get("flag", False) else 0
    
    score = (
        circular * WEIGHT_CIRCULAR +
        rapid * WEIGHT_RAPID +
        structuring * WEIGHT_STRUCTURING +
        dormant * WEIGHT_DORMANT
    )
    
    return min(score, 100)  # Cap at 100


def get_risk_level(score):
    """
    Get risk level category based on score.
    
    Args:
        score: int 0-100
    
    Returns:
        str: 'allow', 'flag', or 'alert'
    """
    if score < THRESHOLD_LOW:
        return "allow"
    elif score <= THRESHOLD_HIGH:
        return "flag"
    else:
        return "alert"


def get_risk_level_emoji(level):
    """Get emoji indicator for risk level."""
    return {"allow": "🟢", "flag": "🟡", "alert": "🔴"}.get(level, "⚪")


def score_account(account_id, detection_results):
    """
    Score a single account and return full details.
    
    Returns:
        dict with score, level, and contributing factors
    """
    score = calculate_score(detection_results)
    level = get_risk_level(score)
    
    # Identify contributing factors
    factors = []
    if detection_results.get("circular", {}).get("flag"):
        factors.append(f"circular(+{WEIGHT_CIRCULAR})")
    if detection_results.get("rapid", {}).get("flag"):
        factors.append(f"rapid(+{WEIGHT_RAPID})")
    if detection_results.get("structuring", {}).get("flag"):
        factors.append(f"structuring(+{WEIGHT_STRUCTURING})")
    if detection_results.get("dormant", {}).get("flag"):
        factors.append(f"dormant(+{WEIGHT_DORMANT})")
    
    return {
        "account_id": account_id,
        "score": score,
        "level": level,
        "emoji": get_risk_level_emoji(level),
        "factors": factors,
        "patterns": {
            "circular": detection_results.get("circular", {}).get("flag", False),
            "rapid": detection_results.get("rapid", {}).get("flag", False),
            "structuring": detection_results.get("structuring", {}).get("flag", False),
            "dormant": detection_results.get("dormant", {}).get("flag", False)
        }
    }


def score_all_accounts(all_detection_results):
    """
    Score all accounts from detection results.
    
    Args:
        all_detection_results: dict mapping account_id -> detection results dict
    
    Returns:
        list of scored account dicts, sorted by score descending
    """
    scored = []
    for account_id, detection_results in all_detection_results.items():
        scored.append(score_account(account_id, detection_results))
    
    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def print_score_summary(scored_accounts, top_n=20):
    """Print a formatted summary of scored accounts."""
    print("\n" + "=" * 80)
    print("RISK SCORING SUMMARY")
    print("=" * 80)
    print(f"\nFormula: circular×{WEIGHT_CIRCULAR} + rapid×{WEIGHT_RAPID} + structuring×{WEIGHT_STRUCTURING} + dormant×{WEIGHT_DORMANT}")
    print(f"Thresholds: <{THRESHOLD_LOW}=allow | {THRESHOLD_LOW}-{THRESHOLD_HIGH}=flag | >{THRESHOLD_HIGH}=alert")
    
    # Count by level
    counts = {"allow": 0, "flag": 0, "alert": 0}
    for acc in scored_accounts:
        counts[acc["level"]] += 1
    
    print(f"\nDistribution:")
    print(f"  🟢 Allow (<{THRESHOLD_LOW}):  {counts['allow']} accounts")
    print(f"  🟡 Flag ({THRESHOLD_LOW}-{THRESHOLD_HIGH}): {counts['flag']} accounts")
    print(f"  🔴 Alert (>{THRESHOLD_HIGH}): {counts['alert']} accounts")
    
    # Show top risk accounts
    print(f"\n{'=' * 80}")
    print(f"TOP {top_n} HIGH-RISK ACCOUNTS")
    print("=" * 80)
    print(f"{'Score':<8}{'Level':<12}{'Account':<15}{'Contributing Factors'}")
    print("-" * 80)
    
    for acc in scored_accounts[:top_n]:
        factors_str = ", ".join(acc["factors"]) if acc["factors"] else "none"
        print(f"{acc['score']:<8}{acc['emoji']} {acc['level']:<10}{acc['account_id']:<15}{factors_str}")


def export_scores(scored_accounts, filepath="risk_scores.json"):
    """Export scores to JSON file."""
    with open(filepath, "w") as f:
        json.dump(scored_accounts, f, indent=2, default=str)
    print(f"\nScores exported to: {filepath}")


if __name__ == "__main__":
    # Test scoring logic with sample data
    print("Testing scoring module...")
    
    # Test single pattern
    test_single = {"circular": {"flag": True}, "rapid": {"flag": False}, 
                   "structuring": {"flag": False}, "dormant": {"flag": False}}
    print(f"Circular only: {calculate_score(test_single)} (expected: {WEIGHT_CIRCULAR})")
    
    # Test multiple patterns
    test_multi = {"circular": {"flag": True}, "rapid": {"flag": True}, 
                  "structuring": {"flag": True}, "dormant": {"flag": True}}
    expected = WEIGHT_CIRCULAR + WEIGHT_RAPID + WEIGHT_STRUCTURING + WEIGHT_DORMANT
    print(f"All patterns: {calculate_score(test_multi)} (expected: {expected})")
    
    # Test thresholds
    print(f"\nThreshold check:")
    print(f"  Score 25: {get_risk_level(25)} (expected: allow)")
    print(f"  Score 50: {get_risk_level(50)} (expected: flag)")
    print(f"  Score 85: {get_risk_level(85)} (expected: alert)")
