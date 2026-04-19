"""
network_graph.py
================
Renders an interactive Plotly fund-flow network graph using REAL pipeline data.
Nodes are color-coded by risk level. Hovering shows account details.
"""

import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import math

from data.pipeline_connector import PipelineConnector


class NetworkGraph:
    """Interactive Plotly fund-flow graph built from real transaction data."""

    def __init__(self, connector: PipelineConnector):
        self._connector = connector

    def render(self):
        """Render the network graph section."""
        st.markdown(
            '<div class="section-header">◈ Fund Flow Network Graph</div>'
            '<div class="section-sub">Interactive transaction graph — hover nodes for details · Red=High Risk · Amber=Medium · Green=Safe</div>',
            unsafe_allow_html=True,
        )

        nodes, edges = self._connector.get_graph_data()
        if not nodes:
            st.info("No graph data available. Run pipeline first.")
            return

        fig = self._build_plotly_figure(nodes, edges)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    def _build_plotly_figure(self, nodes, edges):
        """Build Plotly figure with spring layout positions."""
        # Build a temporary nx graph for layout
        G = nx.DiGraph()
        node_ids = {n["id"] for n in nodes}
        for n in nodes:
            G.add_node(n["id"])
        for e in edges:
            if e["source"] in node_ids and e["target"] in node_ids:
                G.add_edge(e["source"], e["target"])

        # Spring layout for nice spacing
        pos = nx.spring_layout(G, seed=42, k=2.5 / math.sqrt(max(len(G.nodes()), 1)))

        # ── Edge traces (one per color group) ──────────────────────────
        edge_traces = []
        for e in edges:
            if e["source"] not in pos or e["target"] not in pos:
                continue
            x0, y0 = pos[e["source"]]
            x1, y1 = pos[e["target"]]
            # Draw arrow line
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode="lines",
                line=dict(color=e["color"], width=1.5),
                hoverinfo="none",
                showlegend=False,
            ))

        # ── Node trace ──────────────────────────────────────────────────
        node_x, node_y, node_text, node_hover = [], [], [], []
        node_colors, node_sizes = [], []
        for n in nodes:
            if n["id"] not in pos:
                continue
            x, y = pos[n["id"]]
            node_x.append(x)
            node_y.append(y)
            node_text.append(n["label"])
            node_hover.append(
                f"<b>{n['id']}</b><br>"
                f"Risk Level: <b>{n['risk_level'].upper()}</b><br>"
                f"Risk Score: <b>{n['score']}</b>"
            )
            node_colors.append(n["color"])
            node_sizes.append(n["size"])

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            hoverinfo="text",
            hovertext=node_hover,
            text=node_text,
            textposition="bottom center",
            textfont=dict(color="#c7d2fe", size=9, family="JetBrains Mono"),
            marker=dict(
                color=node_colors,
                size=node_sizes,
                line=dict(color="#0f1525", width=2),
                opacity=0.95,
            ),
            showlegend=False,
        )

        # ── Legend items ────────────────────────────────────────────────
        legend_traces = [
            go.Scatter(x=[None], y=[None], mode="markers",
                       marker=dict(color="#ef4444", size=12),
                       name="High Risk (Alert)"),
            go.Scatter(x=[None], y=[None], mode="markers",
                       marker=dict(color="#f59e0b", size=12),
                       name="Medium Risk (Flag)"),
            go.Scatter(x=[None], y=[None], mode="markers",
                       marker=dict(color="#22c55e", size=12),
                       name="Low Risk (Allow)"),
        ]

        all_traces = edge_traces + [node_trace] + legend_traces

        fig = go.Figure(
            data=all_traces,
            layout=go.Layout(
                paper_bgcolor="rgba(10,14,26,0.0)",
                plot_bgcolor="rgba(15,21,37,0.6)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=390,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                showlegend=True,
                legend=dict(
                    x=0.02, y=0.98,
                    bgcolor="rgba(15,21,37,0.8)",
                    bordercolor="rgba(99,102,241,0.3)",
                    borderwidth=1,
                    font=dict(color="#94a3b8", size=10),
                ),
                hoverlabel=dict(
                    bgcolor="#1e293b", bordercolor="#4f46e5",
                    font=dict(color="#e2e8f0", size=11, family="Inter"),
                ),
            )
        )
        return fig
