"""
fraud_investigator.py
=====================
Renders the Fraud Path Investigation panel — account selector, chain path
display, risk badge, evidence checklist, and report generation button.
"""

import streamlit as st

from data.data_store import DataStore, FraudChainRecord


class FraudInvestigator:
    """
    Interactive panel that lets users select an account and view
    its detected fraud chain, risk score, and generate an evidence report.
    """

    EVIDENCE_ITEMS = [
        "Transaction Chain",
        "Accounts",
        "Suspicious Pattern",
        "Risk Score",
    ]

    # ── private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _chain_html(chain_str: str) -> str:
        return f'<div class="fraud-chain">{chain_str}</div>'

    @staticmethod
    def _risk_badge_html(ci: FraudChainRecord) -> str:
        score_cls = "risk-score-high"  if ci.risk == "High" else "risk-score-medium"
        label_cls = "risk-label-high"  if ci.risk == "High" else "risk-label-medium"
        return (
            f'<div style="margin-bottom:0.8rem;">'
            f'<span style="color:#6b7280;font-size:0.85rem;">'
            f'Fraud Chain: {ci.pattern} &nbsp; Risk Score:</span>'
            f'<span class="{score_cls}">{ci.score}</span>'
            f'<span class="{label_cls}">{ci.risk} Risk</span>'
            f'</div>'
        )

    @classmethod
    def _evidence_panel_html(cls) -> str:
        items_html = "".join(
            f'<div class="check-item">✔ {item}</div>'
            for item in cls.EVIDENCE_ITEMS
        )
        return (
            f'<div class="panel" style="margin-bottom:0.8rem;">'
            f'<div style="color:#1565c0;font-weight:800;font-size:0.9rem;margin-bottom:0.5rem;">'
            f'📋 Generate Evidence Report</div>'
            f'{items_html}'
            f'</div>'
        )

    # ── public render ─────────────────────────────────────────────────────────

    @classmethod
    def render(cls):
        """Draw the full Fraud Path Investigation section."""
        st.markdown(
            '<div class="section-header">👥 Fraud Path Investigation</div>',
            unsafe_allow_html=True,
        )

        # Account selector
        selected  = st.selectbox("Select Account", list(DataStore.FRAUD_CHAINS.keys()), key="acct")
        ci        = DataStore.FRAUD_CHAINS[selected]
        chain_str = " → ".join(ci.chain)

        # Chain path display
        st.markdown(cls._chain_html(chain_str), unsafe_allow_html=True)

        # Risk badge
        st.markdown(cls._risk_badge_html(ci), unsafe_allow_html=True)

        # Evidence checklist panel
        st.markdown(cls._evidence_panel_html(), unsafe_allow_html=True)

        # Generate Report button
        if st.button("Generate Report"):
            st.success(
                f"✅ Report generated for **{selected}** — "
                f"`{chain_str}` | Score: **{ci.score}** ({ci.risk})"
            )
