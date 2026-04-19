# -*- coding: utf-8 -*-
"""
main.py - FraudFlow-AI Command-Line Pipeline Runner
===================================================
Runs the complete 4-agent fraud detection pipeline on
the transaction dataset and prints a full summary report.

Usage:
    python main.py [--demo] [--limit N]

Options:
    --demo      Run with 0.1s delay between transactions for live demo effect
    --limit N   Process only the first N transactions
"""

import argparse
import os
import sys
import time
from datetime import datetime

import pandas as pd

from monitor import MonitoringAgent


def print_banner():
    import sys
    # Ensure UTF-8 output on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sep = "=" * 72
    print()
    print(sep)
    print("  FraudFlow-AI  |  Fund Flow Intelligence System")
    print("  AI-Powered Fraud Detection  |  4-Agent Pipeline")
    print(sep)
    print("  Agent 1: Monitor Agent   - Real-time transaction streaming")
    print("  Agent 2: Analysis Agent  - Graph analytics & pattern detection")
    print("  Agent 3: Decision Agent  - Threshold-based risk classification")
    print("  Agent 4: Action Agent    - Alert generation & FIU evidence")
    print(sep)
    print()


def print_section(title: str):
    print()
    print("-" * 72)
    print(f"  {title}")
    print("-" * 72)


def run_pipeline(demo: bool = False, limit: int = None):
    """Run the full 4-agent pipeline."""
    print_banner()

    start_time = time.time()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Initialising FraudFlow-AI Pipeline...")

    # ── Instantiate Monitoring Agent (bootstraps all sub-agents) ────────────
    agent = MonitoringAgent(
        txn_file=os.path.join(os.path.dirname(__file__), "data", "transactions.csv"),
        acc_file=os.path.join(os.path.dirname(__file__), "data", "accounts.csv"),
    )

    if agent.txn_df.empty:
        print("❌ ERROR: No transaction data found. Run generate_data.py first.")
        sys.exit(1)

    # Optionally limit the number of transactions processed
    if limit and limit > 0:
        agent.txn_df = agent.txn_df.head(limit)
        print(f"ℹ  Processing limited to first {limit} transactions.")

    print_section("RUNNING 4-AGENT PIPELINE")
    delay = 0.05 if demo else 0.0
    agent.stream_transactions(delay=delay)

    # ── Summary ─────────────────────────────────────────────────────────────
    elapsed = time.time() - start_time
    summary = agent.get_summary()

    print_section("PIPELINE COMPLETE — SUMMARY REPORT")
    print(f"  ✅  Total transactions processed : {summary['total_transactions']}")
    print(f"  🚫  Accounts blocked             : {len(summary['blocked_accounts'])}")
    if summary["blocked_accounts"]:
        for acc in summary["blocked_accounts"]:
            print(f"        • {acc}")
    print(f"  ⏱   Pipeline runtime             : {elapsed:.2f}s")
    print(f"  📂  Evidence files               : evidence/")
    print(f"  📋  Audit log                    : logs/fraud_alerts.log")
    print()
    print("  💡 Launch the visual dashboard with:")
    print("     cd UI && streamlit run app.py")
    print()
    print("-" * 72)
    print("  FraudFlow-AI - Evidence ready for submission to FIU-India (goAML)")
    print("-" * 72)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FraudFlow-AI Pipeline Runner")
    parser.add_argument("--demo",  action="store_true", help="Add delays for live demo")
    parser.add_argument("--limit", type=int, default=None, help="Limit transactions to N")
    args = parser.parse_args()

    run_pipeline(demo=args.demo, limit=args.limit)
