"""
test_full_pipeline.py — End-to-End Pipeline Test
"""

import os
import pandas as pd
from analyse import AnalysisAgent
from decide import DecisionAgent
from act import ActionAgent


def run_full_test(limit=10):
    print("🚀 Running FULL Pipeline Test")
    print("=" * 60)

    base_path = os.path.dirname(__file__)
    txn_file = os.path.join(base_path, "data", "transactions.csv")
    acc_file = os.path.join(base_path, "data", "accounts.csv")

    txn_df = pd.read_csv(txn_file)
    txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
    acc_df = pd.read_csv(acc_file)

    analysis_agent = AnalysisAgent()
    decision_agent = DecisionAgent()
    action_agent = ActionAgent()

    flagged = 0
    alerts = 0

    for i in range(min(limit, len(txn_df))):
        txn = txn_df.iloc[i]

        print(f"\n🔍 TXN {txn['txn_id']}")

        analysis = analysis_agent.analyze_transaction(txn, txn_df, acc_df)
        decision = decision_agent.make_decision(analysis)
        evidence = action_agent.generate_evidence(txn, analysis, decision)

        print(f"   Score: {analysis['risk_score']}")
        print(f"   Decision: {decision['action']} ({decision['alert_level']})")

        if decision["action"] in ["flag", "alert"]:
            action_agent.log_action(evidence)

            if decision["action"] == "flag":
                flagged += 1
            else:
                alerts += 1

    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print(f"Processed: {limit}")
    print(f"Flagged: {flagged}")
    print(f"Alerts: {alerts}")
    print("=" * 60)


if __name__ == "__main__":
    run_full_test(limit=10)