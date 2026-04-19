"""
fraud_investigator.py
=====================
Interactive fraud path investigation panel.
Lets users pick any suspicious account,
see its full fund-flow chain, risk score, and generate a FIU-ready evidence report.
"""

import json
import streamlit as st

from data.pipeline_connector import PipelineConnector


class FraudInvestigator:
    """
    Interactive panel: account selector → chain path → risk badge → FIU report.
    """

    PATTERN_ICONS = {
        "circular":    "🔄 Circular Transfer",
        "rapid":       "⚡ Rapid Transactions",
        "structuring": "💰 Structuring (Smurfing)",
        "dormant":     "😴 Dormant Account Activation",
    }

    @classmethod
    def render(cls, connector: PipelineConnector):
        """Draw the full Fraud Path Investigation section."""
        st.markdown(
            '<div class="section-header">👥 Fraud Path Investigator</div>'
            '<div class="section-sub">Select an account to trace its complete fund-flow chain and generate FIU evidence</div>',
            unsafe_allow_html=True,
        )

        suspicious_ids = connector.get_all_suspicious_account_ids()
        if not suspicious_ids:
            st.info("No suspicious accounts detected.")
            return

        selected = st.selectbox(
            "Select Suspicious Account",
            suspicious_ids,
            key="investigator_account",
            help="List shows all HIGH/MEDIUM risk accounts detected by the pipeline",
        )

        chain_info = connector.get_fraud_chain(selected)
        if not chain_info:
            st.warning(f"Could not trace fund chain for {selected}")
            return

        # ── Chain path display ────────────────────────────────────────
        st.markdown(
            f'<div class="fraud-chain">Path: {chain_info["path_str"]}</div>',
            unsafe_allow_html=True,
        )

        # ── Risk badge row ────────────────────────────────────────────
        score   = chain_info["score"]
        risk    = chain_info["risk"]
        factors = chain_info["factors"]
        score_cls = ("score-badge-high" if score > 70
                     else "score-badge-medium" if score > 30
                     else "score-badge-low")

        pattern_labels = " · ".join(
            cls.PATTERN_ICONS.get(f, f.capitalize()) for f in factors
        ) or "No pattern"

        st.markdown(
            f'<div style="margin-bottom:0.8rem;">'
            f'  <span style="color:#64748b;font-size:0.82rem;">Detected patterns: '
            f'    <span style="color:#a5b4fc;">{pattern_labels}</span>'
            f'  </span><br>'
            f'  <span style="color:#64748b;font-size:0.82rem;">Risk Score: </span>'
            f'  <span class="{score_cls}">{score}</span>'
            f'  <span style="color:#{"dc2626" if risk=="Alert" else "d97706" if risk=="Flag" else "16a34a"};'
            f'        font-weight:700;font-size:0.85rem;margin-left:8px;">'
            f'    {risk} Risk'
            f'  </span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Evidence checklist ────────────────────────────────────────
        evidence_items = [
            "✔ Transaction Chain Reconstructed",
            "✔ Accounts Identified",
            f"✔ Suspicious Pattern: {pattern_labels}",
            f"✔ Risk Score Calculated: {score}",
            "✔ FIU-Ready JSON Generated",
        ]
        items_html = "".join(
            f'<div class="check-item">{item}</div>'
            for item in evidence_items
        )
        st.markdown(
            f'<div class="glass-panel" style="padding:0.8rem 1rem;margin-bottom:0.8rem;">'
            f'  <div style="color:#818cf8;font-weight:700;font-size:0.85rem;margin-bottom:0.5rem;">'
            f'    📋 Evidence Report Contents</div>'
            f'  {items_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Generate FIU Report button ────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔍 Analyse Chain", key="btn_analyse"):
                txn_df = connector.get_txn_df()
                acc_txns = txn_df[
                    (txn_df["sender"] == selected) |
                    (txn_df["receiver"] == selected)
                ][["txn_id","sender","receiver","amount","timestamp","tx_type","channel"]].head(10)
                st.dataframe(
                    acc_txns,
                    use_container_width=True,
                    hide_index=True,
                )

        with col2:
            evidence = connector.generate_fiu_evidence(selected)
            evidence_json = json.dumps(evidence, indent=2, default=str)
            st.download_button(
                label="📄 Download FIU Evidence",
                data=evidence_json,
                file_name=f"FIU_Evidence_{selected}.json",
                mime="application/json",
                key="btn_fiu_download",
            )

        # Preview the evidence
        with st.expander("👁 Preview FIU Evidence JSON", expanded=False):
            st.code(evidence_json, language="json")
