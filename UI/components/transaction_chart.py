"""
transaction_chart.py
====================
Renders Plotly area chart of transactions over time,
split by normal vs fraud — using REAL pipeline data.
"""

import streamlit as st
import plotly.graph_objects as go

from data.pipeline_connector import PipelineConnector


class TransactionChart:
    """Interactive Plotly area chart showing transaction volume over time."""

    @staticmethod
    def render(connector: PipelineConnector):
        """Draw the transactions-over-time section."""
        st.markdown(
            '<div class="section-header">📈 Transaction Volume Over Time</div>'
            '<div class="section-sub">Normal vs Fraud transaction distribution across the monitoring window</div>',
            unsafe_allow_html=True,
        )

        hours, normal, fraud = connector.get_transaction_timeseries()

        if not hours:
            st.info("No timeseries data available.")
            return

        fig = go.Figure()

        # Normal transactions area
        fig.add_trace(go.Scatter(
            x=hours, y=normal,
            mode="lines+markers",
            name="Normal",
            line=dict(color="#22c55e", width=2.5),
            marker=dict(size=5, color="#22c55e", line=dict(color="#0f1525", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.08)",
            hovertemplate="<b>%{x}</b><br>Normal TXNs: <b>%{y}</b><extra></extra>",
        ))

        # Fraud transactions area
        fig.add_trace(go.Scatter(
            x=hours, y=fraud,
            mode="lines+markers",
            name="Fraud",
            line=dict(color="#ef4444", width=2.5),
            marker=dict(size=6, color="#ef4444", line=dict(color="#0f1525", width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(239,68,68,0.12)",
            hovertemplate="<b>%{x}</b><br>Fraud TXNs: <b>%{y}</b><extra></extra>",
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,21,37,0.5)",
            margin=dict(l=10, r=10, t=10, b=40),
            height=240,
            xaxis=dict(
                tickfont=dict(color="#475569", size=9, family="Inter"),
                gridcolor="rgba(99,102,241,0.08)",
                tickangle=-30,
            ),
            yaxis=dict(
                tickfont=dict(color="#475569", size=9),
                gridcolor="rgba(99,102,241,0.08)",
                zeroline=False,
            ),
            legend=dict(
                x=0.02, y=0.98, orientation="h",
                bgcolor="rgba(15,21,37,0.8)",
                bordercolor="rgba(99,102,241,0.25)",
                borderwidth=1,
                font=dict(color="#94a3b8", size=10),
            ),
            hoverlabel=dict(
                bgcolor="#1e293b", bordercolor="#4f46e5",
                font=dict(color="#e2e8f0", size=11),
            ),
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
