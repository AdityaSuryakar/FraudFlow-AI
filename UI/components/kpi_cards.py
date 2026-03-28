"""
kpi_cards.py
============
Renders the row of five KPI summary metric cards at the top of the dashboard.
"""

import streamlit as st

from data.data_store import DataStore, KPICard


class KPICards:
    """
    Renders a horizontal row of gradient KPI metric cards.
    Card definitions are sourced from DataStore.KPI_CARDS.
    """

    @staticmethod
    def _build_card_html(card: KPICard) -> str:
        """Return the HTML string for a single metric card."""
        return (
            f'<div class="metric-card {card.card_class}">'
            f'  <div class="metric-title">{card.icon} {card.title}</div>'
            f'  <div class="metric-value">{card.value}</div>'
            f'  <div class="metric-delta {card.delta_class}">{card.delta}</div>'
            f'</div>'
        )

    @classmethod
    def render(cls):
        """Draw all KPI cards in equal-width columns."""
        cards = DataStore.KPI_CARDS
        cols  = st.columns(len(cards))

        for col, card in zip(cols, cards):
            with col:
                st.markdown(cls._build_card_html(card), unsafe_allow_html=True)

        st.markdown("")
