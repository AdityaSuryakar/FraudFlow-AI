"""
analyse.py — Optimized Analysis Agent
"""

from datetime import datetime
import pandas as pd   # ✅ FIXED (was turtle 🤦)
import detect
import score
import journey


class AnalysisAgent:

    def __init__(self):
        self.graph_cache = None
        self.last_update = None
        self.precomputed_flags = None

    def analyze_transaction(self, transaction, txn_df, acc_df):

        sender = transaction["sender"]
        receiver = transaction["receiver"]
        timestamp = transaction["timestamp"]

        # ✅ Ensure datetime
        if txn_df["timestamp"].dtype == object:
            txn_df["timestamp"] = pd.to_datetime(txn_df["timestamp"])

        # ✅ Build graph (cached)
        if self.graph_cache is None or self._should_rebuild_graph():
            print("⚡ Building transaction graph...")
            self.graph_cache = detect.build_graph(txn_df)
            self.last_update = datetime.now()
            self.precomputed_flags = None

        G = self.graph_cache

        # ✅ Precompute detectors once
        if self.precomputed_flags is None:
            print("⚡ Precomputing detection results (one-time)...")

            self.precomputed_flags = {
                "circular": detect.detect_circular(G),
                "rapid": detect.detect_rapid(txn_df),
                "structuring": detect.detect_structuring(txn_df),
                "dormant": detect.detect_dormant(txn_df, acc_df)
            }

        circular_flags = self.precomputed_flags["circular"]
        rapid_flags = self.precomputed_flags["rapid"]
        structuring_flags = self.precomputed_flags["structuring"]
        dormant_flags = self.precomputed_flags["dormant"]

        results = {
            "circular": {
                "flag": sender in circular_flags or receiver in circular_flags,
                "details": circular_flags.get(sender, circular_flags.get(receiver, {}))
            },
            "rapid": {
                "flag": sender in rapid_flags,
                "details": rapid_flags.get(sender, {})
            },
            "structuring": {
                "flag": sender in structuring_flags,
                "details": structuring_flags.get(sender, {})
            },
            "dormant": {
                "flag": sender in dormant_flags or receiver in dormant_flags,
                "details": dormant_flags.get(sender, dormant_flags.get(receiver, {}))
            }
        }

        risk_score = score.calculate_score(results)

        graph_stats = self._get_graph_stats(G, sender, receiver)

        journey_info = self._get_journey_info(G, sender, timestamp)

        return {
            "transaction": dict(transaction),
            "patterns": results,
            "risk_score": risk_score,
            "graph_stats": graph_stats,
            "journey": journey_info
        }

    def _should_rebuild_graph(self):
        return self.last_update is None or (datetime.now() - self.last_update).seconds > 300

    def _get_graph_stats(self, G, sender, receiver):
        try:
            return {
                "total_nodes": len(G.nodes()),
                "total_edges": len(G.edges()),
                "sender_degree": G.degree(sender) if sender in G else 0,
                "receiver_degree": G.degree(receiver) if receiver in G else 0,
                "direct_connection": G.has_edge(sender, receiver)
            }
        except Exception:
            return {}

    def _get_journey_info(self, G, account, timestamp):
        try:
            paths = journey.get_outgoing_journey(G, account, cutoff=3)
            return {
                "account": account,
                "outgoing_paths": len(paths),
                "max_path_length": max(len(p) for p in paths) if paths else 0,
                "timestamp": str(timestamp)
            }
        except Exception:
            return {}