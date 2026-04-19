"""
sidebar.py
==========
Sidebar UI component — agent status, pipeline controls, and live filters.
"""

import streamlit as st
from dataclasses import dataclass
from typing import List, Dict

from data.pipeline_connector import PipelineConnector


# ── FilterState ────────────────────────────────────────────────────────────────

@dataclass
class FilterState:
    """Holds the current state of all sidebar filter controls."""
    risk_high:       bool = True
    risk_medium:     bool = True
    risk_low:        bool = False
    circular:        bool = True
    rapid:           bool = True
    structuring:     bool = True
    dormant:         bool = True
    min_score:       int  = 0


# ── SidebarComponent ────────────────────────────────────────────────────────────

class SidebarComponent:

    AGENTS = [
        ("🔍", "Monitor Agent",    "Real-time ingestion"),
        ("🧠", "Analysis Agent",   "Pattern detection"),
        ("⚖️",  "Decision Agent",   "Risk thresholds"),
        ("🚨", "Action Agent",     "Alert & evidence"),
    ]

    @staticmethod
    def render(connector: PipelineConnector) -> FilterState:
        """Draw sidebar widgets and return the resulting FilterState."""
        state = FilterState()

        with st.sidebar:
            # ── Brand ──────────────────────────────────────────────────
            st.markdown(
                '<div class="sidebar-brand">'
                '  <span class="sidebar-brand-icon">🏦</span>'
                '  <div>'
                '    <div class="sidebar-brand-text">FraudFlow-AI</div>'
                '    <div class="sidebar-brand-sub">Fund Flow Intelligence</div>'
                '  </div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<hr>', unsafe_allow_html=True)

            # ── Agent Status ───────────────────────────────────────────
            st.markdown('<div class="sidebar-section">● Agent Status</div>', unsafe_allow_html=True)

            agent_html = ""
            for icon, name, role in SidebarComponent.AGENTS:
                dot_cls = "agent-dot-green" if connector.loaded else "agent-dot-grey"
                status_str = "Active" if connector.loaded else "Idle"
                agent_html += (
                    f'<div class="agent-status-item">'
                    f'  <span class="{dot_cls}"></span>'
                    f'  <span class="agent-name">{icon} {name}</span>'
                    f'  <span class="agent-role">{status_str}</span>'
                    f'</div>'
                )
            st.markdown(agent_html, unsafe_allow_html=True)

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── Pipeline control ───────────────────────────────────────
            st.markdown('<div class="sidebar-section">⚙ Pipeline Control</div>', unsafe_allow_html=True)
            if st.button("▶ Run Full Pipeline", key="btn_run_pipeline"):
                with st.spinner("Running 4-agent pipeline..."):
                    connector.load_and_run()
                st.success("✅ Pipeline complete!")
                st.rerun()

            if connector.loaded:
                kpi = connector.get_kpi_summary()
                st.markdown(
                    f'<div style="font-size:0.72rem;color:#4ade80;text-align:center;margin-top:4px;">'
                    f'✔ Processed {kpi.get("total_transactions",0)} transactions'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── Risk Level Filter ──────────────────────────────────────
            st.markdown('<div class="sidebar-section">⚠ Risk Level</div>', unsafe_allow_html=True)
            state.risk_high   = st.checkbox("🔴 High Risk (Alert)",   value=True)
            state.risk_medium = st.checkbox("🟡 Medium Risk (Flag)",  value=True)
            state.risk_low    = st.checkbox("🟢 Low Risk (Allow)",    value=False)

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── Pattern Filter ─────────────────────────────────────────
            st.markdown('<div class="sidebar-section">🔍 Fraud Pattern</div>', unsafe_allow_html=True)
            state.circular    = st.checkbox("🔄 Circular Transfer",          value=True)
            state.rapid       = st.checkbox("⚡ Rapid Transactions",          value=True)
            state.structuring = st.checkbox("💰 Structuring (Smurfing)",      value=True)
            state.dormant     = st.checkbox("😴 Dormant Account Activation",  value=True)

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── Min Score slider ───────────────────────────────────────
            st.markdown('<div class="sidebar-section">📊 Min Risk Score</div>', unsafe_allow_html=True)
            state.min_score = st.slider("", 0, 100, 0, 5, label_visibility="collapsed")

            st.markdown('<hr>', unsafe_allow_html=True)

            # ── Dataset info ───────────────────────────────────────────
            st.markdown('<div class="sidebar-section">ℹ Dataset Info</div>', unsafe_allow_html=True)
            if connector.loaded:
                kpi = connector.get_kpi_summary()
                info_lines = [
                    ("Accounts",      kpi.get("total_accounts",     0)),
                    ("Transactions",  kpi.get("total_transactions",  0)),
                    ("Fraud TXNs",    kpi.get("fraud_transactions",  0)),
                    ("High Risk",     kpi.get("high_risk_accounts",  0)),
                ]
                for label, val in info_lines:
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;'
                        f'font-size:0.75rem;color:#64748b;padding:2px 0;">'
                        f'  <span>{label}</span><span style="color:#94a3b8;font-weight:600;">{val}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<div style="font-size:0.75rem;color:#475569;">Run pipeline to load data</div>',
                            unsafe_allow_html=True)

        return state

    @staticmethod
    def apply_filters(state: FilterState, alerts: List[Dict]) -> List[Dict]:
        """
        Filter alerts list using the sidebar filter state.

        Args:
            state:  FilterState from render()
            alerts: list of account dicts from connector.get_fraud_alerts()
        """
        level_map = {
            "alert": state.risk_high,
            "flag":  state.risk_medium,
            "allow": state.risk_low,
        }

        results = []
        for rec in alerts:
            if not level_map.get(rec.get("level", "allow"), True):
                continue
            if rec.get("score", 0) < state.min_score:
                continue
            factors = rec.get("factors", [])
            # Pattern filter — include if ANY selected pattern matches
            pattern_ok = (
                (state.circular    and "circular"    in factors) or
                (state.rapid       and "rapid"       in factors) or
                (state.structuring and "structuring" in factors) or
                (state.dormant     and "dormant"     in factors) or
                not factors  # no pattern = show by default if not filtered
            )
            if not pattern_ok:
                continue
            results.append(rec)
        return results
