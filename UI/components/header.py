"""
header.py
=========
Top application header — displays the app title and live scan status badge.
"""

import streamlit as st


class HeaderComponent:
    """Renders the top title bar with app name and live status indicator."""

    @staticmethod
    def render():
        """Draw the page header with title (left) and status badge (right)."""
        col_title, col_status = st.columns([3, 1])

        with col_title:
            st.markdown(
                '<span class="title-icon">🏦</span>'
                '<span class="page-title">AI Fund Flow Intelligence System</span>',
                unsafe_allow_html=True,
            )

        with col_status:
            st.markdown("""
            <div class="topbar">
                <span>Last Transaction Scan: 2 sec ago</span>
                <span class="status-dot"></span>
                <span style="color:#16a34a;font-weight:700;">Live</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
