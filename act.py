"""
act.py — Action Agent
Logs to file, generates evidence JSON, simulates block.
"""

import os
import json
from datetime import datetime

class ActionAgent:
    """Handles actions for flagged/alerted transactions."""

    def __init__(self, log_file="logs/fraud_alerts.log", evidence_dir="evidence/"):
        # Ensure absolute paths
        if not os.path.isabs(log_file):
            log_file = os.path.join(os.path.dirname(__file__), log_file)
        if not os.path.isabs(evidence_dir):
            evidence_dir = os.path.join(os.path.dirname(__file__), evidence_dir)
            
        self.log_file = log_file
        self.evidence_dir = evidence_dir

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(self.evidence_dir, exist_ok=True)

        # Track blocked accounts
        self.blocked_accounts = set()

    def generate_evidence(self, transaction, analysis_result, decision_result):
        """
        Generate FIU-ready evidence JSON.

        Args:
            transaction: transaction dict
            analysis_result: analysis results from AnalysisAgent
            decision_result: decision results from DecisionAgent

        Returns:
            dict: evidence in FIU-ready JSON format
        """
        # Extract pattern information
        patterns = analysis_result["patterns"]
        journey = analysis_result["journey"]

        # Determine primary pattern
        primary_pattern = "Normal transaction"
        if patterns["circular"]["flag"]:
            primary_pattern = "Circular transaction"
        elif patterns["rapid"]["flag"]:
            primary_pattern = "Rapid transactions"
        elif patterns["structuring"]["flag"]:
            primary_pattern = "Structuring pattern"
        elif patterns["dormant"]["flag"]:
            primary_pattern = "Dormant account activity"

        # Build transaction path (simplified for demo)
        path = f"{transaction['sender']} > {transaction['receiver']}"

        # Calculate time span for patterns
        time_span = self._calculate_time_span(patterns, transaction)

        # Generate reason based on patterns
        reason = self._generate_reason(patterns, analysis_result["risk_score"])

        # Create evidence JSON
        evidence = {
            "alert": decision_result["alert_level"],
            "path": path,
            "pattern": primary_pattern,
            "time_span": time_span,
            "risk_score": analysis_result["risk_score"],
            "reason": reason,
            "fiu_ready": True,
            "transaction_id": transaction["txn_id"],
            "timestamp": transaction["timestamp"].isoformat() if hasattr(transaction["timestamp"], 'isoformat') else str(transaction["timestamp"]),
            "amount": transaction["amount"],
            "accounts_involved": [transaction["sender"], transaction["receiver"]],
            "channel": transaction.get("channel", "unknown"),
            "tx_type": transaction.get("tx_type", "unknown"),
            "generated_at": datetime.now().isoformat(),
            "evidence_version": "1.0"
        }

        return evidence

    def log_action(self, evidence):
        """
        Log the action to file and save evidence JSON.

        Args:
            evidence: evidence dict from generate_evidence
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log to text file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {evidence['alert']} ALERT - {evidence['transaction_id']}: {evidence['reason']}\n")

        # Save evidence JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        evidence_file = os.path.join(
            self.evidence_dir,
            f"{evidence['transaction_id']}_{timestamp}_evidence.json"
        )
        with open(evidence_file, "w", encoding="utf-8") as f:
            json.dump(evidence, f, indent=2, ensure_ascii=False)

        # Simulate account blocking for high-risk alerts
        if evidence["alert"] == "HIGH":
            self._simulate_block(evidence["accounts_involved"])

        print(f"📄 Evidence logged: {evidence_file}")
        print(f"🚫 Action taken: {self._get_action_description(evidence)}")

    def _calculate_time_span(self, patterns, transaction):
        """Calculate time span for the detected pattern."""
        if patterns["rapid"]["flag"]:
            # For rapid transactions, use the window
            details = patterns["rapid"]["details"]
            if "window_start" in details and "window_end" in details:
                duration = details["window_end"] - details["window_start"]
                minutes = duration.total_seconds() / 60
                return f"{int(minutes)} minutes"
        elif patterns["circular"]["flag"]:
            # For circular, estimate based on transaction timing
            return "2 minutes 14 seconds"  # Demo value
        else:
            return "N/A"

    def _generate_reason(self, patterns, risk_score):
        """Generate detailed reason for the alert."""
        reasons = []

        if patterns["circular"]["flag"]:
            reasons.append("Funds returned to origin in <3 min across 3 accounts")
        if patterns["rapid"]["flag"]:
            details = patterns["rapid"]["details"]
            count = details.get("transaction_count", 0)
            reasons.append(f"Multiple rapid transactions ({count} in short window)")
        if risk_score >= 80:
            reasons.append("High risk score indicates potential fraud")

        return "; ".join(reasons) if reasons else f"Risk score: {risk_score}"

    def _simulate_block(self, accounts):
        """Simulate blocking accounts involved in high-risk transactions."""
        for account in accounts:
            if account not in self.blocked_accounts:
                self.blocked_accounts.add(account)
                print(f"🚫 BLOCKED: Account {account} has been temporarily frozen")

    def _get_action_description(self, evidence):
        """Get description of the action taken."""
        if evidence["alert"] == "HIGH":
            return f"Accounts {evidence['accounts_involved']} blocked, FIU evidence generated"
        elif evidence["alert"] == "MEDIUM":
            return f"Transaction {evidence['transaction_id']} flagged for review"
        else:
            return f"Transaction {evidence['transaction_id']} logged for monitoring"

    def get_blocked_accounts(self):
        """Get list of currently blocked accounts."""
        return list(self.blocked_accounts)

    def unblock_account(self, account):
        """Unblock a previously blocked account."""
        if account in self.blocked_accounts:
            self.blocked_accounts.remove(account)
            print(f"✅ UNBLOCKED: Account {account} has been unblocked")
            return True
        return False