"""
evidence_report.py
==================
Renders the static Evidence Report checklist panel in the right column.
"""

import streamlit as st


class EvidenceReport:
    """
    Displays a static checklist panel listing the contents
    of any generated evidence report.
    """

    ITEMS = [
        "Transaction Chain",
        "Accounts",
        "Suspicious Pattern",
        "Risk Score",
    ]

    @classmethod
    def render(cls):
        """Draw the Evidence Report section header and checklist panel."""
        st.markdown(
            '<div class="section-header">📁 Evidence Report</div>',
            unsafe_allow_html=True,
        )

        items_html = "".join(
            f'<div class="check-item">✔ {item}</div>'
            for item in cls.ITEMS
        )

        st.markdown(
            f'<div class="panel">{items_html}</div>',
            unsafe_allow_html=True,
        )
