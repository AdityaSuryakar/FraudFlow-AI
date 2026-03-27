"""
DAY 1 - FILE 2: build_graph.py
================================
Loads the transactions CSV and constructs a directed weighted graph.

Graph structure:
  - Node  = Account (with metadata: name, status, balance, last_active)
  - Edge  = Transaction (with attributes: amount, timestamp, tx_type, channel, fraud_label)
  - Multi-edges allowed (same two accounts can have multiple transactions)

What this enables:
  - Multi-hop fund tracking        → nx.all_simple_paths()
  - Cycle / circular detection     → nx.simple_cycles()
  - Degree analysis                → who sends/receives the most
  - Subgraph extraction            → isolate fraud clusters

Outputs:
  - graph/fund_flow.graphml        (saved graph for reuse in other modules)
  - Prints verification stats to console
"""

import pandas as pd
import networkx as nx
import os
import json
from datetime import datetime

DATA_DIR  = "data"
GRAPH_DIR = "graph"
os.makedirs(GRAPH_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# STEP 1: Load data
# ─────────────────────────────────────────────
print("\nLoading data...")
txn_df  = pd.read_csv(f"{DATA_DIR}/transactions.csv")
acc_df  = pd.read_csv(f"{DATA_DIR}/accounts.csv")

txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
print(f"  Transactions loaded : {len(txn_df)}")
print(f"  Accounts loaded     : {len(acc_df)}")

# ─────────────────────────────────────────────
# STEP 2: Build directed multigraph
# MultiDiGraph because the same two accounts
# can have multiple transactions between them
# ─────────────────────────────────────────────
print("\nBuilding transaction graph...")
G = nx.MultiDiGraph()

# Add all account nodes with metadata
account_meta = acc_df.set_index("account_id").to_dict("index")
for acc_id, meta in account_meta.items():
    G.add_node(acc_id, **meta)

# Add transaction edges
for _, row in txn_df.iterrows():
    G.add_edge(
        row["sender"],
        row["receiver"],
        txn_id       = row["txn_id"],
        amount       = row["amount"],
        timestamp    = str(row["timestamp"]),
        tx_type      = row["tx_type"],
        channel      = row["channel"],
        fraud_label  = row["fraud_label"],
        fraud_scenario = row["fraud_scenario"]
    )

# ─────────────────────────────────────────────
# STEP 3: Save graph
# ─────────────────────────────────────────────
nx.write_graphml(G, f"{GRAPH_DIR}/fund_flow.graphml")
print(f"  Graph saved → {GRAPH_DIR}/fund_flow.graphml")

# ─────────────────────────────────────────────
# STEP 4: Verification — print graph stats
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  GRAPH VERIFICATION STATS")
print("=" * 55)
print(f"  Total nodes (accounts)      : {G.number_of_nodes()}")
print(f"  Total edges (transactions)  : {G.number_of_edges()}")

# Degree analysis — who is the most active sender/receiver
out_degree = sorted(G.out_degree(), key=lambda x: x[1], reverse=True)
in_degree  = sorted(G.in_degree(),  key=lambda x: x[1], reverse=True)

print(f"\n  Top 5 senders (by tx count):")
for acc, deg in out_degree[:5]:
    name = account_meta.get(acc, {}).get("name", "Unknown")
    print(f"    {acc} ({name:<20}) → {deg} outgoing")

print(f"\n  Top 5 receivers (by tx count):")
for acc, deg in in_degree[:5]:
    name = account_meta.get(acc, {}).get("name", "Unknown")
    print(f"    {acc} ({name:<20}) → {deg} incoming")

# ─────────────────────────────────────────────
# STEP 5: Cycle detection — VERIFY fraud scenario 1
# Convert to simple DiGraph for cycle detection
# (MultiDiGraph cycles work the same way)
# ─────────────────────────────────────────────
print(f"\n  Cycle detection (circular transaction check):")
simple_G = nx.DiGraph()
for u, v, data in G.edges(data=True):
    simple_G.add_edge(u, v)

cycles = list(nx.simple_cycles(simple_G))
short_cycles = [c for c in cycles if len(c) <= 5]   # focus on short fraud loops

if short_cycles:
    print(f"  ✓ {len(short_cycles)} circular chain(s) detected:")
    for cycle in short_cycles[:5]:
        chain = " → ".join(cycle) + f" → {cycle[0]}"
        print(f"      {chain}")
else:
    print("  ✗ No short cycles found — check your planted data")

# ─────────────────────────────────────────────
# STEP 6: Path tracing — verify rapid multi-hop
# Trace fund journey from ACC_010 to ACC_015
# ─────────────────────────────────────────────
print(f"\n  Path tracing (rapid multi-hop check):")
try:
    all_paths = list(nx.all_simple_paths(G, source="ACC_010", target="ACC_015", cutoff=10))
    if all_paths:
        print(f"  ✓ {len(all_paths)} path(s) found from ACC_010 → ACC_015:")
        for path in all_paths[:3]:
            print(f"      {' → '.join(path)}")
    else:
        print("  ✗ No path found — check planted rapid-hop data")
except nx.NodeNotFound as e:
    print(f"  ✗ Node not found: {e}")

# ─────────────────────────────────────────────
# STEP 7: Dormant account check
# ─────────────────────────────────────────────
print(f"\n  Dormant account activity check:")
dormant_accs = acc_df[acc_df["status"] == "dormant"]["account_id"].tolist()
dormant_with_txn = [
    acc for acc in dormant_accs
    if G.in_degree(acc) > 0 or G.out_degree(acc) > 0
]
if dormant_with_txn:
    print(f"  ✓ {len(dormant_with_txn)} dormant account(s) have transactions:")
    for acc in dormant_with_txn:
        name = account_meta.get(acc, {}).get("name", "Unknown")
        print(f"      {acc} ({name}) — in:{G.in_degree(acc)} out:{G.out_degree(acc)}")
else:
    print("  ✗ No dormant account activity found")

# ─────────────────────────────────────────────
# STEP 8: Fraud edge summary
# ─────────────────────────────────────────────
print(f"\n  Fraud transaction breakdown in graph:")
fraud_by_scenario = {}
for u, v, data in G.edges(data=True):
    scenario = data.get("fraud_scenario", "none")
    if scenario != "none":
        fraud_by_scenario[scenario] = fraud_by_scenario.get(scenario, 0) + 1

for scenario, count in fraud_by_scenario.items():
    print(f"    └─ {scenario:<30} : {count} edges")

print("\n" + "=" * 55)
print("  DAY 1 COMPLETE — Graph is ready for Day 2 detection")
print("=" * 55 + "\n")
