"""
network_graph.py
================
Renders the directed fund-flow network graph using networkx + matplotlib.
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

from data.data_store import DataStore


class NetworkGraph:
    """
    Builds a directed graph from DataStore edge/node data
    and renders it as a styled matplotlib figure inside Streamlit.
    """

    def __init__(self):
        self._graph = self._build_graph()

    def _build_graph(self) -> nx.DiGraph:
        """Construct the directed graph from DataStore ACCOUNTS and EDGES."""
        G = nx.DiGraph()

        for node_id in DataStore.ACCOUNTS:
            G.add_node(node_id)

        for src, dst, color, width in DataStore.EDGES:
            G.add_edge(src, dst, color=color, width=width)

        return G

    def _draw_edges(self, ax, pos: dict):
        """Draw all directed edges with their stored colour and width."""
        G = self._graph
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edge_color=[G[u][v]["color"] for u, v in G.edges()],
            width=[G[u][v]["width"] for u, v in G.edges()],
            arrows=True,
            arrowsize=22,
            arrowstyle="-|>",
            connectionstyle="arc3,rad=0.08",
            min_source_margin=25,
            min_target_margin=25,
        )

    def _draw_nodes(self, ax, pos: dict):
        """Draw nodes with their colour coding and white borders."""
        G = self._graph
        nx.draw_networkx_nodes(
            G, pos, ax=ax,
            node_color=[DataStore.NODE_COLORS[n] for n in G.nodes()],
            node_size=1500,
            linewidths=2.5,
            edgecolors="#ffffff",
        )

    def _draw_labels(self, ax, pos: dict):
        """Draw white bold account-ID labels on each node."""
        nx.draw_networkx_labels(
            self._graph, pos, ax=ax,
            font_color="white",
            font_size=9,
            font_weight="bold",
        )

    def render(self):
        """Render the section header and the matplotlib graph figure."""
        st.markdown(
            '<div class="section-header">◈ Fund Flow Network</div>'
            '<div class="section-sub">Visualizing financial transactions as graph</div>',
            unsafe_allow_html=True,
        )

        pos = DataStore.NODE_POSITIONS

        fig, ax = plt.subplots(figsize=(7, 4.5))
        fig.patch.set_facecolor("#f8faff")
        ax.set_facecolor("#f8faff")

        self._draw_edges(ax, pos)
        self._draw_nodes(ax, pos)
        self._draw_labels(ax, pos)

        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.axis("off")
        plt.tight_layout(pad=0.3)

        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.markdown("")
