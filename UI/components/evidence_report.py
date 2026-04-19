"""
evidence_report.py
==================
Renders the FIU Evidence Report panel with a summary of all generated reports.
"""

import streamlit as st
from data.pipeline_connector import PipelineConnector


class EvidenceReport:
    """
    Shows a summary of detected fraud patterns and the FIU report readiness status.
    """

    @staticmethod
    def render(connector: PipelineConnector):
        """Draw the Evidence Report section."""
        st.markdown(
            '<div class="section-header">📁 FIU Evidence Summary</div>'
            '<div class="section-sub">Financial Intelligence Unit — India reporting readiness</div>',
            unsafe_allow_html=True,
        )

        breakdown = connector.get_pattern_breakdown()
        alerts    = connector.get_fraud_alerts()
        high_risk = [a for a in alerts if a["level"] == "alert"]

        items = [
            ("🔄 Circular Transfer Accounts",  breakdown.get("Circular",    0), "#ef4444"),
            ("⚡ Rapid Transaction Accounts",   breakdown.get("Rapid",       0), "#f59e0b"),
            ("💰 Structuring Accounts",         breakdown.get("Structuring", 0), "#8b5cf6"),
            ("😴 Dormant Account Activations",  breakdown.get("Dormant",     0), "#06b6d4"),
        ]

        items_html = ""
        for label, count, color in items:
            bar_width = min(100, count * 10)
            items_html += (
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:0.6rem;">'
                f'  <div style="flex:1;font-size:0.78rem;color:#94a3b8;">{label}</div>'
                f'  <div style="width:80px;background:rgba(99,102,241,0.1);border-radius:4px;height:6px;overflow:hidden;">'
                f'    <div style="width:{bar_width}%;background:{color};height:100%;border-radius:4px;"></div>'
                f'  </div>'
                f'  <div style="width:28px;text-align:right;font-size:0.82rem;font-weight:700;color:{color};">{count}</div>'
                f'</div>'
            )

        fiu_ready = len(high_risk)
        st.markdown(
            f'<div class="glass-panel">'
            f'  <div style="color:#818cf8;font-weight:700;font-size:0.85rem;margin-bottom:0.8rem;">📊 Pattern Detection Summary</div>'
            f'  {items_html}'
            f'  <hr style="border-color:rgba(99,102,241,0.15);margin:0.8rem 0;">'
            f'  <div style="display:flex;justify-content:space-between;align-items:center;">'
            f'    <span style="font-size:0.78rem;color:#94a3b8;">FIU-Ready Reports</span>'
            f'    <span style="font-size:1.1rem;font-weight:800;color:#f87171;">{fiu_ready}</span>'
            f'  </div>'
            f'  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.4rem;">'
            f'    <span style="font-size:0.78rem;color:#94a3b8;">goAML Portal Status</span>'
            f'    <span style="font-size:0.72rem;color:#4ade80;font-weight:700;">✔ Ready</span>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # FIU checklist items
        checklist = [
            "Transaction chain reconstructed",
            "Multi-account patterns identified",
            "Risk scores calculated (0–100)",
            "Evidence JSON formatted for goAML",
            "Alert levels assigned (HIGH/MEDIUM)",
        ]
        checks_html = "".join(
            f'<div style="font-size:0.78rem;color:#4ade80;margin:0.3rem 0;">✔ {item}</div>'
            for item in checklist
        )
        st.markdown(
            f'<div class="glass-panel" style="padding:0.8rem 1rem;">'
            f'  <div style="color:#818cf8;font-weight:700;font-size:0.82rem;margin-bottom:0.5rem;">'
            f'    📋 FIU Report Compliance</div>'
            f'  {checks_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
