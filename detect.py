"""
detect.py — Rule-based pattern detection functions
"""

import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
from collections import defaultdict


def load_data(txn_path="data/transactions.csv", acc_path="data/accounts.csv"):
    """Load transactions and accounts data."""
    txn_df = pd.read_csv(txn_path)
    acc_df = pd.read_csv(acc_path)
    txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])
    return txn_df, acc_df


def build_graph(txn_df):
    """Build directed graph from transactions."""
    G = nx.MultiDiGraph()
    for _, row in txn_df.iterrows():
        G.add_edge(
            row["sender"],
            row["receiver"],
            txn_id=row["txn_id"],
            amount=row["amount"],
            timestamp=row["timestamp"],
            tx_type=row["tx_type"],
            channel=row["channel"],
            fraud_label=row["fraud_label"],
            fraud_scenario=row["fraud_scenario"]
        )
    return G


def detect_circular(G, max_hops=4):

    import networkx as nx

    # ✅ Convert MultiGraph → simple Graph
    simple_G = nx.Graph()
    for u, v in G.edges():
        simple_G.add_edge(u, v)

    cycles = nx.cycle_basis(simple_G)

    circular_flags = {}

    for cycle in cycles:
        if len(cycle) <= max_hops:
            for acc in cycle:
                if acc not in circular_flags:
                    circular_flags[acc] = {
                        "flag": True,
                        "cycles": [],
                        "cycle_lengths": []
                    }
                circular_flags[acc]["cycles"].append(cycle)
                circular_flags[acc]["cycle_lengths"].append(len(cycle))

    return circular_flags

def detect_rapid(txn_df, window_minutes=10, min_txns=3):

    import pandas as pd
    from datetime import timedelta

    # ✅ Ensure datetime
    if txn_df["timestamp"].dtype == object:
        txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])

    rapid_flags = {}

    for sender, group in txn_df.groupby("sender"):
        if len(group) < min_txns:
            continue

        group = group.sort_values("timestamp")
        timestamps = group["timestamp"].tolist()

        for i in range(len(timestamps) - min_txns + 1):
            window_start = timestamps[i]
            window_end = window_start + timedelta(minutes=window_minutes)

            txns_in_window = group[
                (group["timestamp"] >= window_start) &
                (group["timestamp"] <= window_end)
            ]

            if len(txns_in_window) >= min_txns:
                rapid_flags[sender] = {
                    "flag": True,
                    "window_start": window_start,
                    "window_end": window_end,
                    "transaction_count": len(txns_in_window),
                    "transaction_ids": txns_in_window["txn_id"].tolist()
                }
                break

    return rapid_flags


def detect_structuring(txn_df, min_amount=45000, max_amount=49900, min_txns=3):
    """
    Detect structuring patterns (3+ txns of ₹45k-₹49.9k same day from same sender).
    Returns dict of {account: structuring_details}.
    """
    structuring_flags = {}
    
    # Filter transactions in amount range
    structuring_txns = txn_df[
        (txn_df["amount"] >= min_amount) & 
        (txn_df["amount"] <= max_amount)
    ].copy()
    
    # Extract date
    structuring_txns["date"] = structuring_txns["timestamp"].dt.date
    
    # Group by sender and date
    for (sender, date), group in structuring_txns.groupby(["sender", "date"]):
        if len(group) >= min_txns:
            structuring_flags[sender] = {
                "flag": True,
                "date": date,
                "transaction_count": len(group),
                "total_amount": group["amount"].sum(),
                "transaction_ids": group["txn_id"].tolist(),
                "amounts": group["amount"].tolist()
            }
    
    return structuring_flags


def detect_dormant(txn_df, acc_df, dormant_days_threshold=90):
    """
    Detect dormant account activity (accounts inactive >90 days suddenly transacting).
    Returns dict of {account: dormant_details}.
    """
    dormant_flags = {}
    
    # Get dormant accounts
    dormant_accs = acc_df[acc_df["status"] == "dormant"]["account_id"].tolist()
    
    # Check transactions from dormant accounts
    for acc in dormant_accs:
        acc_txns = txn_df[
            (txn_df["sender"] == acc) | (txn_df["receiver"] == acc)
        ]
        
        if len(acc_txns) > 0:
            # Get last active date from account data
            acc_data = acc_df[acc_df["account_id"] == acc].iloc[0]
            last_active = pd.to_datetime(acc_data["last_active"])
            
            # Check if first transaction is after dormant threshold
            first_txn = acc_txns["timestamp"].min()
            days_inactive = (first_txn - last_active).days
            
            if days_inactive > dormant_days_threshold:
                dormant_flags[acc] = {
                    "flag": True,
                    "last_active": last_active,
                    "first_transaction": first_txn,
                    "days_inactive": days_inactive,
                    "transaction_count": len(acc_txns),
                    "in_degree": len(acc_txns[acc_txns["receiver"] == acc]),
                    "out_degree": len(acc_txns[acc_txns["sender"] == acc])
                }
    
    return dormant_flags


def get_all_accounts(txn_df, acc_df):
    """Get list of all accounts from both dataframes."""
    tx_accounts = set(txn_df["sender"].unique()) | set(txn_df["receiver"].unique())
    acc_accounts = set(acc_df["account_id"].unique())
    return tx_accounts | acc_accounts


def run_all_detectors(txn_path="data/transactions.csv", acc_path="data/accounts.csv"):
    """
    Run all detection functions and return combined results.
    """
    txn_df, acc_df = load_data(txn_path, acc_path)
    G = build_graph(txn_df)
    
    # Run all detectors
    circular = detect_circular(G)
    rapid = detect_rapid(txn_df)
    structuring = detect_structuring(txn_df)
    dormant = detect_dormant(txn_df, acc_df)
    
    # Get all accounts
    all_accounts = get_all_accounts(txn_df, acc_df)
    
    # Combine results per account
    results = {}
    for acc in all_accounts:
        results[acc] = {
            "circular": circular.get(acc, {"flag": False}),
            "rapid": rapid.get(acc, {"flag": False}),
            "structuring": structuring.get(acc, {"flag": False}),
            "dormant": dormant.get(acc, {"flag": False})
        }
    
    return results, txn_df, acc_df, G


if __name__ == "__main__":
    results, txn_df, acc_df, G = run_all_detectors()
    
    print("\n" + "=" * 60)
    print("DETECTION RESULTS SUMMARY")
    print("=" * 60)
    
    # Count flags
    circular_count = sum(1 for r in results.values() if r["circular"]["flag"])
    rapid_count = sum(1 for r in results.values() if r["rapid"]["flag"])
    structuring_count = sum(1 for r in results.values() if r["structuring"]["flag"])
    dormant_count = sum(1 for r in results.values() if r["dormant"]["flag"])
    
    print(f"\nAccounts flagged:")
    print(f"  - Circular:     {circular_count} accounts")
    print(f"  - Rapid hops:   {rapid_count} accounts")
    print(f"  - Structuring:  {structuring_count} accounts")
    print(f"  - Dormant:      {dormant_count} accounts")
    
    # Show details for flagged accounts
    print("\n" + "-" * 60)
    print("FLAGGED ACCOUNT DETAILS")
    print("-" * 60)
    
    for acc, flags in results.items():
        if any(flags[k]["flag"] for k in flags):
            print(f"\n{acc}:")
            for pattern, data in flags.items():
                if data["flag"]:
                    print(f"  ⚠️  {pattern.upper()}: {data}")
