"""
pipeline_connector.py
=====================
Bridges the UI layer with the real backend pipeline.
Loads transactions.csv + accounts.csv, runs the 4-agent pipeline,
and returns structured results for dashboard rendering.
"""

import os
import sys
import json
import pandas as pd
import networkx as nx
from datetime import datetime
from typing import Dict, List, Tuple

# ── Make sure the root backend modules are importable ───────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import detect
import score as score_module
import journey as journey_module
from decide import DecisionAgent
from act import ActionAgent


# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(ROOT, "data")
TXN_FILE = os.path.join(DATA_DIR, "transactions.csv")
ACC_FILE  = os.path.join(DATA_DIR, "accounts.csv")


class PipelineConnector:
    """
    Runs the full 4-agent analysis on the dataset and exposes
    aggregated results for dashboard widgets.
    """

    def __init__(self):
        self._txn_df   = None
        self._acc_df   = None
        self._graph    = None
        self._results  = None   # per-account detection results
        self._scored   = None   # list[dict] sorted by score desc
        self._decisions = {}    # account_id → decision dict
        self._loaded   = False

    # ── Public load/run ──────────────────────────────────────────────────────

    def load_and_run(self) -> bool:
        """Load data and run all detectors + scoring + decisions. Returns True on success."""
        try:
            self._txn_df = pd.read_csv(TXN_FILE)
            self._acc_df = pd.read_csv(ACC_FILE)
            self._txn_df["timestamp"] = pd.to_datetime(self._txn_df["timestamp"])

            # Build transaction graph
            self._graph = detect.build_graph(self._txn_df)

            # Run all detectors
            circular   = detect.detect_circular(self._graph)
            rapid      = detect.detect_rapid(self._txn_df)
            structuring = detect.detect_structuring(self._txn_df)
            dormant    = detect.detect_dormant(self._txn_df, self._acc_df)

            all_accounts = detect.get_all_accounts(self._txn_df, self._acc_df)

            self._results = {}
            for acc in all_accounts:
                self._results[acc] = {
                    "circular":    circular.get(acc, {"flag": False}),
                    "rapid":       rapid.get(acc, {"flag": False}),
                    "structuring": structuring.get(acc, {"flag": False}),
                    "dormant":     dormant.get(acc, {"flag": False}),
                }

            # Score all accounts
            self._scored = score_module.score_all_accounts(self._results)

            # Run decisions for top-50 accounts
            da = DecisionAgent()
            for acc_data in self._scored[:50]:
                acc_id = acc_data["account_id"]
                analysis = {
                    "patterns":   self._results[acc_id],
                    "risk_score": acc_data["score"],
                    "transaction": {"txn_id": "N/A", "sender": acc_id, "receiver": "N/A"},
                }
                self._decisions[acc_id] = da.make_decision(analysis)

            self._loaded = True
            return True
        except Exception as e:
            print(f"[PipelineConnector] ERROR: {e}")
            return False

    # ── Accessors ────────────────────────────────────────────────────────────

    @property
    def loaded(self) -> bool:
        return self._loaded

    def get_kpi_summary(self) -> Dict:
        if not self._loaded:
            return {}
        total_accs   = len(self._results)
        total_txns   = len(self._txn_df)
        high_risk    = sum(1 for a in self._scored if a["level"] == "alert")
        medium_risk  = sum(1 for a in self._scored if a["level"] == "flag")
        fraud_txns   = len(self._txn_df[self._txn_df["fraud_label"] == "fraud"])
        circular_cnt = sum(1 for v in self._results.values() if v["circular"]["flag"])
        return {
            "total_accounts":   total_accs,
            "total_transactions": total_txns,
            "high_risk_accounts": high_risk,
            "medium_risk_accounts": medium_risk,
            "fraud_transactions": fraud_txns,
            "circular_transfers": circular_cnt,
        }

    def get_scored_accounts(self, limit: int = 30) -> List[Dict]:
        """Return top scored accounts as list of dicts."""
        if not self._loaded:
            return []
        out = []
        for a in self._scored[:limit]:
            decision = self._decisions.get(a["account_id"], {})
            out.append({
                "account_id": a["account_id"],
                "score":      a["score"],
                "level":      a["level"],
                "factors":    a["factors"],
                "action":     decision.get("action", "allow"),
                "alert_level": decision.get("alert_level", "LOW"),
            })
        return out

    def get_fraud_alerts(self) -> List[Dict]:
        """Return only alerted + flagged accounts."""
        return [a for a in self.get_scored_accounts(50) if a["level"] in ("alert", "flag")]

    def get_graph_data(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Return (nodes, edges) for Plotly graph rendering.
        nodes: [{id, label, color, size, risk_level}]
        edges: [{source, target, weight, color}]
        """
        if not self._loaded:
            return [], []

        # Only show top 40 accounts by degree or score
        scored_ids = {a["account_id"] for a in self._scored[:40]}
        G = self._graph

        # Build score lookup
        score_map  = {a["account_id"]: a["score"] for a in self._scored}
        level_map  = {a["account_id"]: a["level"] for a in self._scored}

        COLOR_MAP = {"alert": "#ef4444", "flag": "#f59e0b", "allow": "#22c55e"}
        DEFAULT_COLOR = "#94a3b8"

        nodes = []
        for n in G.nodes():
            if n not in scored_ids:
                continue
            lvl   = level_map.get(n, "allow")
            sc    = score_map.get(n, 0)
            color = COLOR_MAP.get(lvl, DEFAULT_COLOR)
            nodes.append({
                "id":         n,
                "label":      n,
                "color":      color,
                "size":       max(15, min(45, sc // 2)),
                "risk_level": lvl,
                "score":      sc,
            })

        visible_ids = {nd["id"] for nd in nodes}
        edges = []
        seen = set()
        for u, v, data in G.edges(data=True):
            if u not in visible_ids or v not in visible_ids:
                continue
            key = (u, v)
            if key in seen:
                continue
            seen.add(key)
            # Edge color based on source risk
            src_lvl = level_map.get(u, "allow")
            ec = COLOR_MAP.get(src_lvl, DEFAULT_COLOR)
            edges.append({
                "source": u,
                "target": v,
                "color":  ec,
                "amount": data.get("amount", 0),
            })

        return nodes, edges

    def get_transaction_timeseries(self) -> Tuple[List[str], List[int], List[int]]:
        """
        Returns (labels, normal_counts, fraud_counts) grouped by hour.
        """
        if not self._loaded:
            return [], [], []

        df = self._txn_df.copy()
        df["hour"] = df["timestamp"].dt.floor("h")
        grouped = df.groupby(["hour", "fraud_label"]).size().unstack(fill_value=0)

        hours  = grouped.index.strftime("%H:%M").tolist()
        normal = grouped.get("normal", pd.Series(dtype=int)).tolist()
        fraud  = grouped.get("fraud",  pd.Series(dtype=int)).tolist()
        return hours, normal, fraud

    def get_fraud_chain(self, account_id: str) -> Dict:
        """
        Return full journey info for an account.
        """
        if not self._loaded or account_id not in self._graph:
            return {}
        paths = journey_module.get_outgoing_journey(self._graph, account_id, cutoff=5)
        best_path = max(paths, key=len) if paths else [account_id]

        acc_data = self._results.get(account_id, {})
        factors  = [k for k, v in acc_data.items() if v.get("flag")]
        sc       = next((a["score"] for a in self._scored if a["account_id"] == account_id), 0)
        level    = next((a["level"] for a in self._scored if a["account_id"] == account_id), "allow")
        pattern  = factors[0].capitalize() if factors else "Normal"

        return {
            "account_id": account_id,
            "chain":      best_path,
            "path_str":   " → ".join(best_path),
            "pattern":    pattern,
            "score":      sc,
            "risk":       level.capitalize(),
            "factors":    factors,
        }

    def get_all_suspicious_account_ids(self) -> List[str]:
        """Return IDs of all accounts with level == alert or flag."""
        return [a["account_id"] for a in self._scored if a["level"] in ("alert", "flag")]

    def generate_fiu_evidence(self, account_id: str) -> Dict:
        """
        Build a FIU-ready evidence report dict for an account.
        """
        chain_info = self.get_fraud_chain(account_id)
        score      = chain_info.get("score", 0)
        level      = chain_info.get("risk", "Low")
        factors    = chain_info.get("factors", [])

        # Collect key transactions involving this account
        txns = self._txn_df[
            (self._txn_df["sender"] == account_id) |
            (self._txn_df["receiver"] == account_id)
        ].head(10)

        txn_list = []
        for _, row in txns.iterrows():
            txn_list.append({
                "txn_id":    row["txn_id"],
                "from":      row["sender"],
                "to":        row["receiver"],
                "amount":    float(row["amount"]),
                "timestamp": str(row["timestamp"]),
                "type":      row.get("tx_type", "N/A"),
                "channel":   row.get("channel", "N/A"),
            })

        evidence = {
            "fiu_report_version":   "2.0",
            "generated_at":         datetime.now().isoformat(),
            "fiu_ready":            True,
            "account_under_review": account_id,
            "risk_score":           score,
            "risk_level":           level,
            "alert_level":          "HIGH" if score > 70 else "MEDIUM",
            "fraud_patterns":       factors,
            "fund_flow_chain":      chain_info.get("path_str", ""),
            "chain_accounts":       chain_info.get("chain", []),
            "key_transactions":     txn_list,
            "detection_summary": {
                k: bool(v.get("flag")) for k, v in self._results.get(account_id, {}).items()
            },
            "recommendation":       "Submit to FIU-India via goAML portal" if score > 70
                                    else "Monitor and flag for review",
        }
        return evidence

    def get_pattern_breakdown(self) -> Dict[str, int]:
        """Return count of each detected pattern across all accounts."""
        if not self._loaded:
            return {}
        return {
            "Circular":    sum(1 for v in self._results.values() if v["circular"]["flag"]),
            "Rapid":       sum(1 for v in self._results.values() if v["rapid"]["flag"]),
            "Structuring": sum(1 for v in self._results.values() if v["structuring"]["flag"]),
            "Dormant":     sum(1 for v in self._results.values() if v["dormant"]["flag"]),
        }

    def get_txn_df(self):
        return self._txn_df

    def get_acc_df(self):
        return self._acc_df
