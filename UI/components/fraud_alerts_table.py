"""
fraud_alerts_table.py
=====================
Renders the Fraud Alerts table from REAL pipeline data with
colour-coded risk badges and pattern tags.
"""

import streamlit as st
from typing import List, Dict


class FraudAlertsTable:
    """Styled HTML table of fraud alerts from live pipeline results."""

    BADGE_MAP = {
        "alert": "badge-high",
        "flag":  "badge-medium",
        "allow": "badge-low",
    }

    RISK_LABEL = {
        "alert": "HIGH",
        "flag":  "MEDIUM",
        "allow": "LOW",
    }

    PATTERN_ICONS = {
        "circular":    "🔄",
        "rapid":       "⚡",
        "structuring": "💰",
        "dormant":     "😴",
    }

    @classmethod
    def _build_row(cls, row: Dict) -> str:
        level       = row.get("level", "allow")
        badge_class = cls.BADGE_MAP.get(level, "badge-low")
        risk_label  = cls.RISK_LABEL.get(level, "LOW")
        score       = row.get("score", 0)
        factors     = row.get("factors", [])

        pattern_tags = "".join(
            f'<span class="pattern-tag">{cls.PATTERN_ICONS.get(f,"")}{f.capitalize()}</span> '
            for f in factors
        )

        return (
            f"<tr>"
            f"<td><span class='acc-id'>{row['account_id']}</span></td>"
            f"<td>{pattern_tags if pattern_tags else '<span style=\"color:#475569\">—</span>'}</td>"
            f"<td style='font-weight:800;color:#e2e8f0;'>{score}</td>"
            f"<td><span class='badge {badge_class}'>{risk_label}</span></td>"
            f"</tr>"
        )

    @classmethod
    def render(cls, alerts: List[Dict], title: str = "🚨 Fraud Alerts"):
        """Render the alerts section header and table."""
        st.markdown(
            f'<div class="section-header">{title}</div>',
            unsafe_allow_html=True,
        )

        if not alerts:
            st.info("No alerts match current filters.")
            return

        rows_html = "".join(cls._build_row(r) for r in alerts)
        table_html = (
            '<div class="glass-panel" style="padding:0.8rem;">'
            '<table class="alert-table">'
            '<thead><tr>'
            '<th>Account ID</th><th>Pattern(s)</th><th>Risk Score</th><th>Status</th>'
            '</tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            '</table></div>'
        )
        st.markdown(table_html, unsafe_allow_html=True)
        st.markdown("")
