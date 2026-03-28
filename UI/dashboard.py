"""
dashboard.py
============
Top-level orchestrator that wires every UI component together
and drives the full Streamlit layout.
"""

import streamlit as st

from config.app_config import AppConfig
from data.data_store import DataStore
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

    Rendering order:
        1. AppConfig     — page setup & CSS
        2. Sidebar       — filters → FilterState
        3. Header        — title + live badge
        4. KPICards      — five summary tiles
        5. Left column:
             a. NetworkGraph        — fund-flow graph
             b. FraudInvestigator   — chain path + report
        6. Right column:
             a. FraudAlertsTable    — filtered alerts
             b. TransactionChart    — time-series chart
             c. EvidenceReport      — checklist panel
    """

    def __init__(self):
        self.filter_state: FilterState = FilterState()

    def run(self):
        """Launch the full dashboard — call this once from app.py."""

        # 1. Page config + CSS
        AppConfig.configure()

        # 2. Sidebar → capture filter selections
        self.filter_state = SidebarComponent.render()

        # 3. Header
        HeaderComponent.render()

        # 4. KPI cards
        KPICards.render()

        # 5. Two-column main layout
        left_col, right_col = st.columns([3, 2], gap="medium")

        with left_col:
            # 5a. Fund-flow network graph
            NetworkGraph().render()

            # 5b. Fraud path investigation panel
            FraudInvestigator.render()

        with right_col:
            # 5c. Filtered fraud-alerts table
            filtered_rows = SidebarComponent.apply_filters(self.filter_state)
            FraudAlertsTable.render(filtered_rows)

            # 5d. Transactions over time chart
            TransactionChart.render()

            # 5e. Evidence report checklist
            EvidenceReport.render()
