"""
monitor.py - Monitoring Agent
Streams transactions one by one, calls Analysis Agent per transaction.
"""
import os
import time
import pandas as pd
from datetime import datetime
from analyse import AnalysisAgent
from decide import DecisionAgent
from act import ActionAgent

class MonitoringAgent:
    """Monitors and processes transactions in real-time."""

    def __init__(self, txn_file="data/transactions.csv", acc_file="data/accounts.csv"):
        # Ensure absolute paths
        if not os.path.isabs(txn_file):
            txn_file = os.path.join(os.path.dirname(__file__), txn_file)
        if not os.path.isabs(acc_file):
            acc_file = os.path.join(os.path.dirname(__file__), acc_file)
            
        self.txn_file = txn_file
        self.acc_file = acc_file
        
        # Load data
        self.txn_df = self._load_data(self.txn_file)
        self.acc_df = self._load_data(self.acc_file)
        
        # Initialize agents
        self.analysis_agent = AnalysisAgent()
        self.decision_agent = DecisionAgent()
        self.action_agent = ActionAgent()

    def _load_data(self, file_path):
        """Load CSV data with error handling."""
        try:
            df = pd.read_csv(file_path)

            # ✅ IMPORTANT FIX
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            print(f"✅ Loaded {len(df)} records from {file_path}")
            return df
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return pd.DataFrame()

    def stream_transactions(self, delay=0.0):
        """
        Stream transactions one by one with optional delay.
        
        Args:
            delay: seconds to wait between transactions (for demo effect)
        """
        if self.txn_df.empty:
            print("❌ No transaction data available")
            return

        # Filter to only high-risk transactions for focused testing
        high_risk_ids = ["TXN_00366", "TXN_00367", "TXN_00368"]
        filtered_df = self.txn_df[self.txn_df["txn_id"].isin(high_risk_ids)]

        if filtered_df.empty:
            print(f"❌ No high-risk transactions found with IDs: {high_risk_ids}")
            return

        print(f"🎯 Processing {len(filtered_df)} high-risk transactions (filtered from {len(self.txn_df)} total)...")
        print("=" * 80)

        for idx, transaction in filtered_df.iterrows():
            print(f"\n🔍 Processing High-Risk Transaction: {transaction['txn_id']}")
            print(f"   Sender: {transaction['sender']} → Receiver: {transaction['receiver']}")
            print(f"   Amount: ${transaction['amount']:.2f} | Time: {transaction['timestamp']}")

            # Step 1: Analyze transaction
            analysis_result = self.analysis_agent.analyze_transaction(
                transaction, self.txn_df, self.acc_df
            )
            print(f"   📈 Risk Score: {analysis_result['risk_score']}")
            print(f"   🔍 Patterns: {', '.join([k for k, v in analysis_result['patterns'].items() if v['flag']])}")

            # Step 2: Make decision
            decision_result = self.decision_agent.make_decision(analysis_result)
            print(f"   ⚖️  Decision: {decision_result['action'].upper()} ({decision_result['alert_level']})")
            print(f"   💬 Reason: {decision_result['reason']}")

            # Step 3: Take action
            if decision_result['action'] in ['flag', 'alert']:
                evidence = self.action_agent.generate_evidence(
                    transaction, analysis_result, decision_result
                )
                self.action_agent.log_action(evidence)
                
                if decision_result['alert_level'] == 'HIGH':
                    print("   🚫 HIGH ALERT: Accounts blocked, FIU evidence generated")
                    print("\n🚨 ALERT GENERATED 🚨")
                    print("This evidence JSON can be directly submitted to the Financial Intelligence Unit.")
                    print("We don't just detect - we document!")
                    print(f"Evidence: {evidence}")
                else:
                    print("   ⚠️  FLAGGED: Transaction logged for review")

            # Demo delay
            if delay > 0:
                time.sleep(delay)

        print("\n" + "=" * 80)
        print("📋 High-Risk Transaction Analysis Complete:")
        print(f"   Total high-risk transactions processed: {len(filtered_df)}")
        print(f"   Blocked accounts: {len(self.action_agent.get_blocked_accounts())}")
        print("   Check 'logs/' and 'evidence/' directories for outputs"
        print("📋 Summary:")
        print(f"   Total transactions processed: {len(self.txn_df)}")
        print(f"   Blocked accounts: {len(self.action_agent.get_blocked_accounts())}")
        print("   Check 'logs/' and 'evidence/' directories for outputs")

    def get_summary(self):
        """Get processing summary."""
        return {
            "total_transactions": len(self.txn_df),
            "blocked_accounts": self.action_agent.get_blocked_accounts(),
            "analysis_agent": "active",
            "decision_agent": "active",
            "action_agent": "active"
        }