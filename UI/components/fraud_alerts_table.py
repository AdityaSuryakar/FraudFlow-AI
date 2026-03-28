"""
fraud_alerts_table.py
=====================
Renders the Fraud Alerts table, displaying filtered account risk data
with colour-coded status badges.
"""

import streamlit as st
from typing import List, Dict


class FraudAlertsTable:
    """
    Renders a styled HTML table of fraud alerts.
    Accepts pre-filtered rows from SidebarComponent.apply_filters().
    """

    BADGE_MAP: Dict[str, str] = {
        "High":   "badge-high",
        "Medium": "badge-medium",
        "Low":    "badge-low",
    }

    @classmethod
    def _build_row_html(cls, row: Dict) -> str:
        """Return the HTML for a single table row."""
        badge_class = cls.BADGE_MAP.get(row["Status"], "badge-low")
        return (
            f'<tr>'
            f'<td><strong>{row["Account"]}</strong></td>'
            f'<td>{row["Pattern"]}</td>'
            f'<td style="font-weight:800;">{row["Risk Score"]}</td>'
            f'<td><span class="{badge_class}">{row["Status"]}</span></td>'
            f'</tr>'
        )

    @classmethod
    def _build_table_html(cls, rows: List[Dict]) -> str:
        """Return the full HTML table string."""
        rows_html = "".join(cls._build_row_html(r) for r in rows)
        return (
            f'<div class="panel">'
            f'<table class="fraud-table">'
            f'<thead>'
            f'<tr><th>Account</th><th>Pattern</th><th>Risk Score</th><th>Status</th></tr>'
            f'</thead>'
            f'<tbody>{rows_html}</tbody>'
            f'</table>'
            f'</div>'
        )

    @classmethod
    def render(cls, filtered_rows: List[Dict]):
        """
        Render the section header and the alerts table.

        Args:
            filtered_rows: List of account dicts returned by SidebarComponent.apply_filters()
        """
        st.markdown('<div class="section-header">🚨 Fraud Alerts</div>', unsafe_allow_html=True)

        if not filtered_rows:
            st.info("No alerts match current filters.")
            return

        st.markdown(cls._build_table_html(filtered_rows), unsafe_allow_html=True)
        st.markdown("")
