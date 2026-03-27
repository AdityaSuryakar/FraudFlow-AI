"""
analyze.py — Main analysis script
Runs all detectors against the dataset and verifies they fire on planted fraud.
"""

import pandas as pd
import detect
import score
import journey


def load_and_verify_data():
    """Load data and show fraud scenario breakdown."""
    txn_df = pd.read_csv("data/transactions.csv")
    acc_df = pd.read_csv("data/accounts.csv")
    txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
    
    print("=" * 80)
    print("DATA LOADED")
    print("=" * 80)
    print(f"  Transactions: {len(txn_df)}")
    print(f"  Accounts:     {len(acc_df)}")
    
    # Show planted fraud scenarios
    fraud_by_scenario = txn_df[txn_df["fraud_scenario"] != "none"].groupby("fraud_scenario").size()
    print(f"\nPlanted fraud scenarios:")
    for scenario, count in fraud_by_scenario.items():
        print(f"  - {scenario}: {count} transactions")
    
    # Accounts involved in each fraud type
    print(f"\nAccounts involved in planted fraud:")
    for scenario in fraud_by_scenario.index:
        txns = txn_df[txn_df["fraud_scenario"] == scenario]
        accounts = set(txns["sender"].unique()) | set(txns["receiver"].unique())
        print(f"  - {scenario}: {sorted(accounts)}")
    
    return txn_df, acc_df


def verify_detectors(results, txn_df):
    """
    Verify that detectors fire correctly on planted fraud.
    Returns True if all verifications pass.
    """
    print("\n" + "=" * 80)
    print("DETECTOR VERIFICATION")
    print("=" * 80)
    
    # Get accounts flagged by each detector
    circular_flagged = {acc for acc, r in results.items() if r["circular"]["flag"]}
    rapid_flagged = {acc for acc, r in results.items() if r["rapid"]["flag"]}
    structuring_flagged = {acc for acc, r in results.items() if r["structuring"]["flag"]}
    
    # Get planted fraud accounts
    circular_txns = txn_df[txn_df["fraud_scenario"] == "circular"]
    circular_planted = set(circular_txns["sender"].unique()) | set(circular_txns["receiver"].unique())
    
    rapid_txns = txn_df[txn_df["fraud_scenario"] == "rapid_multihop"]
    rapid_planted = set(rapid_txns["sender"].unique()) | set(rapid_txns["receiver"].unique())
    
    structuring_txns = txn_df[txn_df["fraud_scenario"] == "structuring"]
    structuring_planted = set(structuring_txns["sender"].unique()) | set(structuring_txns["receiver"].unique())
    
    all_passed = True
    
    # Verify circular detection
    print("\n🔄 CIRCULAR DETECTION")
    print(f"  Planted accounts: {sorted(circular_planted)}")
    print(f"  Flagged accounts: {sorted(circular_flagged)}")
    missed_circular = circular_planted - circular_flagged
    if missed_circular:
        print(f"  ❌ MISSED: {missed_circular}")
        all_passed = False
    else:
        print(f"  ✅ All circular fraud accounts detected")
    
    # Verify rapid detection
    print("\n⚡ RAPID DETECTION")
    print(f"  Planted accounts: {sorted(rapid_planted)}")
    print(f"  Flagged accounts: {sorted(rapid_flagged)}")
    missed_rapid = rapid_planted - rapid_flagged
    if missed_rapid:
        print(f"  ❌ MISSED: {missed_rapid}")
        all_passed = False
    else:
        print(f"  ✅ All rapid fraud accounts detected")
    
    # Verify structuring detection
    print("\n💰 STRUCTURING DETECTION")
    print(f"  Planted accounts: {sorted(structuring_planted)}")
    print(f"  Flagged accounts: {sorted(structuring_flagged)}")
    missed_structuring = structuring_planted - structuring_flagged
    if missed_structuring:
        print(f"  ❌ MISSED: {missed_structuring}")
        all_passed = False
    else:
        print(f"  ✅ All structuring fraud accounts detected")
    
    # Check false positives on normal accounts
    print("\n🔍 FALSE POSITIVE CHECK")
    normal_txns = txn_df[txn_df["fraud_scenario"] == "none"]
    normal_accounts = set(normal_txns["sender"].unique()) | set(normal_txns["receiver"].unique())
    
    # An account can have both normal and fraud txns, but check for pure-normal flagged
    fraud_accounts = circular_planted | rapid_planted | structuring_planted
    
    false_positives_circular = circular_flagged - fraud_accounts
    false_positives_rapid = rapid_flagged - fraud_accounts
    false_positives_structuring = structuring_flagged - fraud_accounts
    
    if false_positives_circular:
        print(f"  ⚠️  Circular flagged on non-fraud accounts: {false_positives_circular}")
    else:
        print(f"  ✅ No circular false positives on clean accounts")
    
    if false_positives_rapid:
        print(f"  ⚠️  Rapid flagged on non-fraud accounts: {false_positives_rapid}")
    else:
        print(f"  ✅ No rapid false positives on clean accounts")
    
    if false_positives_structuring:
        print(f"  ⚠️  Structuring flagged on non-fraud accounts: {false_positives_structuring}")
    else:
        print(f"  ✅ No structuring false positives on clean accounts")
    
    return all_passed


def main():
    """Run full analysis pipeline."""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  FRAUD DETECTION SYSTEM - FULL ANALYSIS".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # Step 1: Load and verify data
    txn_df, acc_df = load_and_verify_data()
    
    # Step 2: Run all detectors
    print("\n" + "=" * 80)
    print("RUNNING DETECTORS")
    print("=" * 80)
    
    results, txn_df, acc_df, G = detect.run_all_detectors()
    
    # Count flags
    circular_count = sum(1 for r in results.values() if r["circular"]["flag"])
    rapid_count = sum(1 for r in results.values() if r["rapid"]["flag"])
    structuring_count = sum(1 for r in results.values() if r["structuring"]["flag"])
    dormant_count = sum(1 for r in results.values() if r["dormant"]["flag"])
    
    print(f"\nDetection summary:")
    print(f"  🔄 Circular:    {circular_count} accounts flagged")
    print(f"  ⚡ Rapid:        {rapid_count} accounts flagged")
    print(f"  💰 Structuring: {structuring_count} accounts flagged")
    print(f"  😴 Dormant:     {dormant_count} accounts flagged")
    
    # Step 3: Verify detectors
    all_passed = verify_detectors(results, txn_df)
    
    # Step 4: Score all accounts
    print("\n" + "=" * 80)
    print("RISK SCORING")
    print("=" * 80)
    
    scored = score.score_all_accounts(results)
    score.print_score_summary(scored, top_n=20)
    
    # Step 5: Journey analysis for high-risk accounts
    print("\n" + "=" * 80)
    print("JOURNEY ANALYSIS")
    print("=" * 80)
    
    # Get alert-level accounts
    alert_accounts = [s["account_id"] for s in scored if s["level"] == "alert"]
    print(f"\nAnalyzing journeys for {len(alert_accounts)} alert-level accounts...")
    
    if alert_accounts:
        journey_results = journey.analyze_suspicious_journeys(G, alert_accounts[:10])
        journey.print_journey_summary(journey_results, top_n=5)
    
    # Step 6: Final summary
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  ANALYSIS COMPLETE".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    if all_passed:
        print("\n✅ ALL VERIFICATIONS PASSED")
        print("   Detectors correctly identified planted fraud patterns")
    else:
        print("\n⚠️  SOME VERIFICATIONS FAILED")
        print("   Review detector logic for missed patterns")
    
    print(f"\n📊 Results:")
    print(f"   - Total accounts analyzed: {len(scored)}")
    print(f"   - Alert-level (>70): {len([s for s in scored if s['level'] == 'alert'])}")
    print(f"   - Flag-level (30-70): {len([s for s in scored if s['level'] == 'flag'])}")
    print(f"   - Allow-level (<30): {len([s for s in scored if s['level'] == 'allow'])}")
    
    # Export scores
    score.export_scores(scored, "risk_scores.json")
    
    return results, scored, journey_results if alert_accounts else {}


if __name__ == "__main__":
    results, scored, journeys = main()
