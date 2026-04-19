"""
dashboard.py
============
Central orchestrator for the FraudFlow-AI dashboard.
Wires all UI components together with REAL pipeline data.
"""

import streamlit as st

from config.app_config import AppConfig
from data.pipeline_connector import PipelineConnector
from components.sidebar import SidebarComponent, FilterState
from components.header import HeaderComponent
from components.kpi_cards import KPICards
from components.network_graph import NetworkGraph
from components.fraud_investigator import FraudInvestigator
from components.fraud_alerts_table import FraudAlertsTable
from components.transaction_chart import TransactionChart
from components.evidence_report import EvidenceReport


class Dashboard:
    """
    Central orchestrator for the AI Fund Flow Intelligence System dashboard.

    Layout:
        1. AppConfig     — page setup & dark CSS
        2. Sidebar       — agent status, pipeline control, filters → FilterState
        3. Header        — logo + live badge
        4. KPICards      — six metric tiles from real data
        5. Tabs:
             Tab 1 – Overview:
               Left  col: NetworkGraph (Plotly), FraudInvestigator
               Right col: TransactionChart (Plotly), FraudAlertsTable
             Tab 2 – Evidence & FIU:
               EvidenceReport + full scored accounts table
             Tab 3 – Raw Data Explorer:
               Interactive transactions dataframe
    """

    def __init__(self):
        self.filter_state: FilterState = FilterState()

    def _get_connector(self) -> PipelineConnector:
        """Get or create a cached PipelineConnector in session state."""
        if "connector" not in st.session_state:
            st.session_state["connector"] = PipelineConnector()
            # Auto-run on first load
            with st.spinner("🚀 Initialising FraudFlow-AI Pipeline..."):
                st.session_state["connector"].load_and_run()
        return st.session_state["connector"]

    def run(self):
        """Launch the full dashboard."""

        # 1. Page config + CSS
        AppConfig.configure()

        # 2. Get / run pipeline connector
        connector = self._get_connector()

        # 3. Sidebar
        self.filter_state = SidebarComponent.render(connector)

        # 4. Header
        HeaderComponent.render()

        # 5. KPI cards
        KPICards.render(connector)

        # 6. Main tab layout
        tab_overview, tab_evidence, tab_rawdata = st.tabs([
            "📊 Overview Dashboard",
            "📁 FIU Evidence Centre",
            "🗄 Raw Data Explorer",
        ])

        # ── TAB 1: Overview ───────────────────────────────────────────
        with tab_overview:
            left_col, right_col = st.columns([3, 2], gap="medium")

            with left_col:
                # Fund-flow network graph
                NetworkGraph(connector).render()
                st.markdown("")

                # Fraud path investigator
                FraudInvestigator.render(connector)

            with right_col:
                # Transactions over time chart
                TransactionChart.render(connector)
                st.markdown("")

                # Fraud alerts table (filtered)
                all_alerts  = connector.get_fraud_alerts()
                filtered    = SidebarComponent.apply_filters(self.filter_state, all_alerts)
                FraudAlertsTable.render(filtered, title="🚨 Fraud Alerts")

        # ── TAB 2: Evidence Centre ────────────────────────────────────
        with tab_evidence:
            ev_col, score_col = st.columns([1, 2], gap="medium")

            with ev_col:
                EvidenceReport.render(connector)

            with score_col:
                st.markdown(
                    '<div class="section-header">📋 Full Risk Score Board</div>'
                    '<div class="section-sub">All accounts ranked by risk score — from the Detection & Scoring Engine</div>',
                    unsafe_allow_html=True,
                )

                scored = connector.get_scored_accounts(limit=80)
                if scored:
                    import pandas as pd
                    df = pd.DataFrame(scored)
                    df.columns = ["Account ID", "Score", "Level", "Patterns", "Action", "Alert"]
                    df["Patterns"] = df["Patterns"].apply(lambda x: ", ".join(x) if x else "—")

                    def color_level(val):
                        if val == "alert":
                            return "color: #f87171; font-weight:700"
                        elif val == "flag":
                            return "color: #fbbf24; font-weight:700"
                        return "color: #4ade80"

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        height=450,
                    )
                else:
                    st.info("Run pipeline to see risk scores.")

        # ── TAB 3: Raw Data Explorer ──────────────────────────────────
        with tab_rawdata:
            data_col1, data_col2 = st.columns([3, 2], gap="medium")

            with data_col1:
                st.markdown(
                    '<div class="section-header">🗄 Transactions Dataset</div>'
                    '<div class="section-sub">Full transaction log with fraud labels and scenario tags</div>',
                    unsafe_allow_html=True,
                )
                txn_df = connector.get_txn_df()
                if txn_df is not None:
                    # Quick filter
                    show_fraud_only = st.checkbox("Show fraud transactions only", value=False)
                    df_show = txn_df[txn_df["fraud_label"] == "fraud"] if show_fraud_only else txn_df
                    st.dataframe(
                        df_show[[
                            "txn_id","sender","receiver","amount",
                            "timestamp","tx_type","channel",
                            "fraud_label","fraud_scenario"
                        ]],
                        use_container_width=True,
                        hide_index=True,
                        height=440,
                    )
                    st.markdown(
                        f'<div style="font-size:0.72rem;color:#475569;margin-top:4px;">'
                        f'Showing {len(df_show)} of {len(txn_df)} transactions</div>',
                        unsafe_allow_html=True,
                    )

            with data_col2:
                st.markdown(
                    '<div class="section-header">🏛 Accounts Dataset</div>'
                    '<div class="section-sub">Account metadata including status and risk labels</div>',
                    unsafe_allow_html=True,
                )
                acc_df = connector.get_acc_df()
                if acc_df is not None:
                    show_dormant = st.checkbox("Show dormant accounts only", value=False)
                    df_acc = acc_df[acc_df["status"] == "dormant"] if show_dormant else acc_df
                    st.dataframe(
                        df_acc[[
                            "account_id", "name", "account_type",
                            "status", "balance", "last_active"
                        ]],
                        use_container_width=True,
                        hide_index=True,
                        height=440,
                    )
