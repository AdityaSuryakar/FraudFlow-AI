"""
sidebar.py
==========
Sidebar UI component — renders all filters and returns a FilterState.
Also provides apply_filters() to filter account data based on selections.
"""

import streamlit as st
from dataclasses import dataclass
from typing import List, Dict

from data.data_store import DataStore


# ── FilterState dataclass ─────────────────────────────────────────────────────

@dataclass
class FilterState:
    """Holds the current state of all sidebar filter controls."""
    date_range: str   = "Last 24 Hours"
    high: bool        = True
    medium: bool      = True
    low: bool         = False
    circular: bool    = True
    rapid: bool       = True
    structuring: bool = False
    dormant: bool     = False


# ── SidebarComponent ──────────────────────────────────────────────────────────

class SidebarComponent:
    """
    Renders the sidebar controls and returns a populated FilterState.
    Also provides static helper to apply filters against DataStore accounts.
    """

    @staticmethod
    def render() -> FilterState:
        """Draw sidebar widgets and return the resulting FilterState."""
        state = FilterState()

        with st.sidebar:
            st.markdown('<div class="sidebar-header">⚙ Controls & Filters</div>', unsafe_allow_html=True)
            st.markdown("---")

            # Date Range
            st.markdown("**Date Range**")
            state.date_range = st.selectbox(
                "",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom"],
                label_visibility="collapsed",
            )

            st.markdown("---")

            # Risk Level
            st.markdown("**Risk Level**")
            state.high   = st.checkbox("High",   value=True)
            state.medium = st.checkbox("Medium", value=True)
            state.low    = st.checkbox("Low",    value=False)

            st.markdown("---")

            # Pattern
            st.markdown("**Pattern**")
            state.circular    = st.checkbox("Circular Transfer",          value=True)
            state.rapid       = st.checkbox("Rapid Transfers",            value=True)
            state.structuring = st.checkbox("Structuring",                value=False)
            state.dormant     = st.checkbox("Dormant Account Activation", value=False)

            st.markdown("---")
            st.button("Apply Filters", use_container_width=True)

        return state

    @staticmethod
    def apply_filters(state: FilterState) -> List[Dict]:
        """
        Filter DataStore.ACCOUNTS using the given FilterState.
        Returns a list of dicts ready for table rendering.
        """
        risk_map = {
            "High":   state.high,
            "Medium": state.medium,
            "Low":    state.low,
        }
        pattern_map = {
            "Circular Transfer":          state.circular,
            "Rapid Transfers":            state.rapid,
            "Structuring":                state.structuring,
            "Dormant Account Activation": state.dormant,
        }

        results = []
        for rec in DataStore.ACCOUNTS.values():
            if not risk_map.get(rec.risk, True):        continue
            if not pattern_map.get(rec.pattern, True):  continue
            results.append({
                "Account":    rec.account_id,
                "Pattern":    rec.pattern,
                "Risk Score": rec.score,
                "Status":     rec.risk,
            })
        return results
