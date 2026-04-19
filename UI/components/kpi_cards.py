"""
kpi_cards.py
============
Renders the KPI metric cards using REAL pipeline data.
"""

import streamlit as st
from data.pipeline_connector import PipelineConnector


class KPICards:
    """Renders a horizontal row of KPI metric cards from live pipeline results."""

    @staticmethod
    def render(connector: PipelineConnector):
        """Draw all KPI cards from pipeline data."""
        kpi = connector.get_kpi_summary()

        total_accs   = kpi.get("total_accounts", 0)
        total_txns   = kpi.get("total_transactions", 0)
        high_risk    = kpi.get("high_risk_accounts", 0)
        medium_risk  = kpi.get("medium_risk_accounts", 0)
        fraud_txns   = kpi.get("fraud_transactions", 0)
        circular_cnt = kpi.get("circular_transfers", 0)

        cards = [
            {
                "icon": "🏛",
                "label": "Total Accounts",
                "value": str(total_accs),
                "delta": f"{total_accs} monitored",
                "delta_cls": "kpi-delta-neu",
                "cls": "kpi-blue",
            },
            {
                "icon": "⇄",
                "label": "Transactions",
                "value": str(total_txns),
                "delta": f"{fraud_txns} flagged fraud",
                "delta_cls": "kpi-delta-neg",
                "cls": "kpi-purple",
            },
            {
                "icon": "🚨",
                "label": "High Risk Alerts",
                "value": str(high_risk),
                "delta": f"Score > 70",
                "delta_cls": "kpi-delta-neg",
                "cls": "kpi-red",
            },
            {
                "icon": "⚠️",
                "label": "Medium Risk",
                "value": str(medium_risk),
                "delta": "Score 30–70",
                "delta_cls": "kpi-delta-neg",
                "cls": "kpi-amber",
            },
            {
                "icon": "🔄",
                "label": "Circular Transfers",
                "value": str(circular_cnt),
                "delta": "Graph cycles",
                "delta_cls": "kpi-delta-neg" if circular_cnt > 0 else "kpi-delta-pos",
                "cls": "kpi-indigo",
            },
            {
                "icon": "🕵",
                "label": "Fraud TXNs",
                "value": str(fraud_txns),
                "delta": f"{round(fraud_txns/total_txns*100,1) if total_txns else 0}% of total",
                "delta_cls": "kpi-delta-neg",
                "cls": "kpi-teal",
            },
        ]

        html_parts = []
        for c in cards:
            html_parts.append(
                f'<div class="kpi-card {c["cls"]}">'
                f'  <span class="kpi-icon">{c["icon"]}</span>'
                f'  <div class="kpi-label">{c["label"]}</div>'
                f'  <div class="kpi-value">{c["value"]}</div>'
                f'  <div class="{c["delta_cls"]}">{c["delta"]}</div>'
                f'</div>'
            )

        st.markdown(
            f'<div class="kpi-row">{"".join(html_parts)}</div>',
            unsafe_allow_html=True,
        )
