"""
data_store.py
=============
Central repository for all application seed data, dataclass models,
and helper data-generation functions.
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ── Dataclass models ──────────────────────────────────────────────────────────

@dataclass
class AccountRecord:
    """Represents a single financial account with risk metadata."""
    account_id: str
    risk: str        # "High" | "Medium" | "Low"
    pattern: str     # fraud pattern label
    score: int       # risk score 0-100


@dataclass
class FraudChainRecord:
    """Represents a detected fraud transaction chain for an account."""
    account_id: str
    chain: List[str]  # ordered list of account IDs forming the chain
    pattern: str
    score: int
    risk: str


@dataclass
class KPICard:
    """Data model for a single KPI summary card."""
    icon: str
    title: str
    value: str
    delta: str
    delta_class: str  # "delta-green" | "delta-red"
    card_class: str   # CSS gradient class e.g. "metric-card-blue"


# ── DataStore ─────────────────────────────────────────────────────────────────

class DataStore:
    """
    Central repository for all static seed data.
    All attributes are class-level constants — no instantiation needed.
    """

    ACCOUNTS: Dict[str, AccountRecord] = {
        "A101": AccountRecord("A101", "High",   "Circular Transfer",          92),
        "B202": AccountRecord("B202", "High",   "Rapid Transfers",            87),
        "C303": AccountRecord("C303", "Medium", "Structuring",                75),
        "D404": AccountRecord("D404", "Low",    "Dormant Account Activation",  38),
        "E505": AccountRecord("E505", "Medium", "Rapid Transfers",            61),
    }

    FRAUD_CHAINS: Dict[str, FraudChainRecord] = {
        "A101": FraudChainRecord("A101", ["A101","B202","C303","A101"], "Circular Transaction", 92, "High"),
        "B202": FraudChainRecord("B202", ["B202","C303","A101","B202"], "Rapid Transfers",      87, "High"),
        "C303": FraudChainRecord("C303", ["C303","D404","E505"],        "Structuring",          75, "Medium"),
        "D404": FraudChainRecord("D404", ["D404","E505"],               "Dormant Activation",   38, "Low"),
        "E505": FraudChainRecord("E505", ["E505","B202","C303"],        "Rapid Transfers",      61, "Medium"),
    }

    # Graph edges: (source_id, target_id, hex_color, line_width)
    EDGES: List[Tuple] = [
        ("A101","B202","#ef4444",3.5), ("B202","C303","#ef4444",3.5), ("C303","A101","#ef4444",3.5),
        ("D404","B202","#f59e0b",2.0), ("D404","E505","#3b82f6",1.5),
        ("E505","B202","#f59e0b",2.0), ("B202","E505","#3b82f6",1.5), ("C303","E505","#3b82f6",1.5),
    ]

    NODE_COLORS: Dict[str, str] = {
        "A101": "#dc2626", "B202": "#ea580c", "C303": "#dc2626",
        "D404": "#475569", "E505": "#94a3b8",
    }

    NODE_POSITIONS: Dict[str, Tuple[float, float]] = {
        "A101": (0.5,  0.85), "B202": (0.75, 0.55), "C303": (0.55, 0.2),
        "D404": (0.15, 0.55), "E505": (0.88, 0.82),
    }

    KPI_CARDS: List[KPICard] = [
        KPICard("🏛", "Total Accounts",    "100", "+10 Today",  "delta-green", "metric-card-blue"),
        KPICard("⇄",  "Transactions",       "540", "+120 Today", "delta-green", "metric-card-teal"),
        KPICard("🚨", "Fraud Alerts",       "7",   "+4 Today",   "delta-red",   "metric-card-red"),
        KPICard("⚠",  "High Risk",          "4",   "+1 Today",   "delta-red",   "metric-card-orange"),
        KPICard("🔄", "Circular Transfers", "2",   "+1 Today",   "delta-red",   "metric-card-amber"),
    ]

    @staticmethod
    def generate_timeseries() -> Tuple[List[str], List[float]]:
        """Return (hour_labels, transaction_counts) with slight random noise."""
        hours = ["49:00", "6:00", "10:00", "13:00", "15:00", "16:00", "18:30"]
        base  = [65, 68, 72, 78, 82, 88, 95]
        vals  = [max(60, v + random.uniform(-1.5, 1.5)) for v in base]
        return hours, vals
