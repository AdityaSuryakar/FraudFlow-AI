"""
header.py
=========
Top application header with live scan status and system info.
"""

import streamlit as st
from datetime import datetime


class HeaderComponent:
    """Renders the top title bar with app name and live status indicator."""

    @staticmethod
    def render():
        """Draw the page header with title (left) and status badge (right)."""
        now_str = datetime.now().strftime("%d %b %Y  %H:%M:%S")

        col_title, col_status = st.columns([4, 2])

        with col_title:
            st.markdown(
                '<div class="main-header">'
                '  <div>'
                '    <div class="header-logo">🏦 FraudFlow-AI</div>'
                '    <div class="header-sub">AI-Powered Fund Flow Intelligence &amp; Fraud Detection System</div>'
                '  </div>'
                '</div>',
                unsafe_allow_html=True,
            )

        with col_status:
            st.markdown(
                f'<div style="display:flex;flex-direction:column;align-items:flex-end;padding-top:0.8rem;">'
                f'  <div class="live-pill"><span class="live-dot"></span> Live Monitoring</div>'
                f'  <div style="font-size:0.7rem;color:#475569;margin-top:6px;">{now_str} IST</div>'
                f'  <div style="font-size:0.7rem;color:#4ade80;margin-top:2px;">● 4 Agents Active</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="margin:0.5rem 0 1rem 0;">', unsafe_allow_html=True)
