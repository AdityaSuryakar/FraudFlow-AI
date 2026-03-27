"""
DAY 1 - FILE 3: preview_graph.py
==================================
Quick visual sanity check — draws the graph and saves as PNG.

Two plots:
  1. Full graph overview (all 80 accounts)
  2. Fraud subgraph only (zoom in on fraud clusters)

Run after build_graph.py to visually confirm your data looks right.
Not needed for the final demo — just for Day 1 verification.
"""

import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")   # non-interactive backend (saves to file)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

GRAPH_DIR = "graph"
DATA_DIR  = "data"

# ─────────────────────────────────────────────
# Load graph and data
# ─────────────────────────────────────────────
G      = nx.read_graphml(f"{GRAPH_DIR}/fund_flow.graphml")
txn_df = pd.read_csv(f"{DATA_DIR}/transactions.csv")
acc_df = pd.read_csv(f"{DATA_DIR}/accounts.csv")

# ─────────────────────────────────────────────
# COLOR SCHEME
# ─────────────────────────────────────────────
FRAUD_SCENARIOS = {
    "circular":          "#E24B4A",   # red
    "rapid_multihop":    "#E8593C",   # coral
    "structuring":       "#EF9F27",   # amber
    "dormant_activation":"#7F77DD",   # purple
}
NORMAL_NODE_COLOR  = "#B5D4F4"   # light blue
DORMANT_NODE_COLOR = "#CECBF6"   # light purple
NORMAL_EDGE_COLOR  = "#D3D1C7"   # light gray

# Build node color map
dormant_set = set(acc_df[acc_df["status"] == "dormant"]["account_id"].tolist())

# Build fraud node set (nodes involved in any fraud transaction)
fraud_nodes = set(
    txn_df[txn_df["fraud_label"] == "fraud"]["sender"].tolist() +
    txn_df[txn_df["fraud_label"] == "fraud"]["receiver"].tolist()
)

def get_node_color(node):
    if node in dormant_set:
        return DORMANT_NODE_COLOR
    if node in fraud_nodes:
        return "#F0997B"   # coral — involved in fraud
    return NORMAL_NODE_COLOR

# Build edge color map
def get_edge_color(u, v, data):
    scenario = data.get("fraud_scenario", "none")
    return FRAUD_SCENARIOS.get(scenario, NORMAL_EDGE_COLOR)

# ─────────────────────────────────────────────
# PLOT 1: Full graph overview
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 14))
ax.set_facecolor("#F8F8F6")
fig.patch.set_facecolor("#F8F8F6")

# Use spring layout — good for showing clusters
pos = nx.spring_layout(G, seed=42, k=1.8)

node_colors = [get_node_color(n) for n in G.nodes()]
node_sizes  = []
for n in G.nodes():
    deg = G.in_degree(n) + G.out_degree(n)
    node_sizes.append(100 + deg * 30)

edge_colors = []
edge_widths = []
for u, v, data in G.edges(data=True):
    col = get_edge_color(u, v, data)
    edge_colors.append(col)
    edge_widths.append(2.5 if col != NORMAL_EDGE_COLOR else 0.6)

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                       alpha=0.85, ax=ax)
nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths,
                       alpha=0.7, arrows=True, arrowsize=10,
                       connectionstyle="arc3,rad=0.1", ax=ax)

# Only label fraud-involved nodes to keep it readable
fraud_labels = {n: n for n in fraud_nodes if n in G.nodes()}
nx.draw_networkx_labels(G, pos, labels=fraud_labels, font_size=7,
                        font_color="#2C2C2A", ax=ax)

# Legend
legend_elements = [
    mpatches.Patch(facecolor=NORMAL_NODE_COLOR,   label="Normal account"),
    mpatches.Patch(facecolor=DORMANT_NODE_COLOR,  label="Dormant account"),
    mpatches.Patch(facecolor="#F0997B",            label="Account in fraud path"),
    mpatches.Patch(facecolor=FRAUD_SCENARIOS["circular"],          label="Circular transaction"),
    mpatches.Patch(facecolor=FRAUD_SCENARIOS["rapid_multihop"],    label="Rapid multi-hop"),
    mpatches.Patch(facecolor=FRAUD_SCENARIOS["structuring"],       label="Structuring"),
    mpatches.Patch(facecolor=FRAUD_SCENARIOS["dormant_activation"],label="Dormant activation"),
    mpatches.Patch(facecolor=NORMAL_EDGE_COLOR,    label="Normal transaction"),
]
ax.legend(handles=legend_elements, loc="upper left", fontsize=9,
          framealpha=0.9, facecolor="white")
ax.set_title("Fund Flow Graph — Full Overview\n(colored edges = fraud transactions)",
             fontsize=14, pad=16, color="#2C2C2A")
ax.axis("off")

plt.tight_layout()
plt.savefig(f"{GRAPH_DIR}/full_graph.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved → {GRAPH_DIR}/full_graph.png")

# ─────────────────────────────────────────────
# PLOT 2: Fraud subgraph only
# ─────────────────────────────────────────────
fraud_edges = [
    (u, v, k) for u, v, k, data in G.edges(data=True, keys=True)
    if data.get("fraud_label") == "fraud"
]
fraud_subgraph = G.edge_subgraph(fraud_edges).copy()

fig2, ax2 = plt.subplots(figsize=(14, 10))
ax2.set_facecolor("#F8F8F6")
fig2.patch.set_facecolor("#F8F8F6")

pos2 = nx.spring_layout(fraud_subgraph, seed=10, k=3.0)

node_cols2 = [get_node_color(n) for n in fraud_subgraph.nodes()]
edge_cols2 = [get_edge_color(u, v, d) for u, v, d in fraud_subgraph.edges(data=True)]
edge_widths2 = [2.5 for _ in fraud_subgraph.edges()]

nx.draw_networkx_nodes(fraud_subgraph, pos2, node_color=node_cols2,
                       node_size=400, alpha=0.9, ax=ax2)
nx.draw_networkx_edges(fraud_subgraph, pos2, edge_color=edge_cols2,
                       width=edge_widths2, alpha=0.85, arrows=True, arrowsize=15,
                       connectionstyle="arc3,rad=0.15", ax=ax2)
nx.draw_networkx_labels(fraud_subgraph, pos2, font_size=8,
                        font_color="#2C2C2A", ax=ax2)

ax2.set_title("Fraud Subgraph — Planted Fraud Patterns Only",
              fontsize=14, pad=16, color="#2C2C2A")
ax2.legend(handles=legend_elements, loc="upper left", fontsize=9,
           framealpha=0.9, facecolor="white")
ax2.axis("off")

plt.tight_layout()
plt.savefig(f"{GRAPH_DIR}/fraud_subgraph.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved → {GRAPH_DIR}/fraud_subgraph.png")

print("\n  ✓ Preview complete — open graph/full_graph.png and graph/fraud_subgraph.png to verify")
