"""
decide.py — Decision Agent
Applies risk threshold logic and returns allow/flag/alert + reason.
"""

class DecisionAgent:
    """Makes decisions based on risk analysis results."""

    def __init__(self):
        # Threshold constants (matching score.py)
        self.THRESHOLD_LOW = 30
        self.THRESHOLD_HIGH = 70

    def make_decision(self, analysis_result):
        """
        Make a decision based on analysis results.

        Args:
            analysis_result: dict from AnalysisAgent

        Returns:
            dict: decision with action, reason, and risk level
        """
        risk_score = analysis_result["risk_score"]
        patterns = analysis_result.get("patterns", {})
        transaction = analysis_result["transaction"]

        # Determine action based on risk score
        if risk_score < self.THRESHOLD_LOW:
            action = "allow"
            alert_level = "LOW"
            reason = self._get_allow_reason(risk_score, patterns)
        elif risk_score <= self.THRESHOLD_HIGH:
            action = "flag"
            alert_level = "MEDIUM"
            reason = self._get_flag_reason(risk_score, patterns)
        else:
            action = "alert"
            alert_level = "HIGH"
            reason = self._get_alert_reason(risk_score, patterns)

        return {
            "action": action,
            "alert_level": alert_level,
            "risk_score": risk_score,
            "reason": reason,
            "transaction_id": transaction["txn_id"],
            "accounts_involved": [transaction["sender"], transaction["receiver"]]
        }

    def _get_allow_reason(self, risk_score, patterns):
        """Generate reason for allow decision."""
        reasons = []
        if risk_score == 0:
            reasons.append("No suspicious patterns detected")
        else:
            reasons.append(f"Low risk score ({risk_score}) with no critical patterns")

        return "; ".join(reasons)

    def _get_flag_reason(self, risk_score, patterns):
        """Generate reason for flag decision."""
        reasons = [f"Medium risk score ({risk_score})"]

        # Check for specific patterns
        if patterns["circular"]["flag"]:
            reasons.append("Circular transaction pattern detected")
        if patterns["rapid"]["flag"]:
            reasons.append("Rapid transaction pattern detected")

        if not any(p["flag"] for p in patterns.values()):
            reasons.append("Elevated score but no specific patterns identified")

        return "; ".join(reasons)

    def _get_alert_reason(self, risk_score, patterns):
        """Generate reason for alert decision."""
        reasons = [f"High risk score ({risk_score})"]

        # Check for specific patterns
        if patterns["circular"]["flag"]:
            cycle_details = patterns["circular"]["details"]
            if "cycle_lengths" in cycle_details and cycle_details["cycle_lengths"]:
                min_length = min(cycle_details["cycle_lengths"])
                reasons.append(f"Circular transaction pattern (min cycle length: {min_length})")

        if patterns["rapid"]["flag"]:
            rapid_details = patterns["rapid"]["details"]
            if "transaction_count" in rapid_details:
                count = rapid_details["transaction_count"]
                reasons.append(f"Rapid transactions ({count} in 10-minute window)")

        # Add severity indicator
        if risk_score >= 90:
            reasons.append("Critical risk level - immediate attention required")

        return "; ".join(reasons)