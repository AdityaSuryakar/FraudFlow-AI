"""
DAY 1 - FILE 1: generate_data.py
=================================
Generates a synthetic banking transaction dataset with:
  - 80 accounts (normal + fraudulent)
  - ~400 normal transactions
  - 4 fraud scenarios planted intentionally:
      1. Circular chain (A→B→C→A)
      2. Rapid multi-hop (A→B→C→D→E in minutes)
      3. Structuring / smurfing (many just-below-threshold transfers)
      4. Dormant account sudden activation

Output: data/transactions.csv, data/accounts.csv
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
NUM_ACCOUNTS        = 80
NUM_NORMAL_TXN      = 350
BASE_DATE           = datetime(2024, 1, 1, 9, 0, 0)   # Jan 1, 2024, 9am
STRUCTURING_LIMIT   = 50000   # ₹50,000 — transactions just below this are suspicious
OUTPUT_DIR          = "data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

CHANNELS  = ["mobile", "web", "branch", "atm", "upi"]
TX_TYPES  = ["IMPS", "NEFT", "RTGS", "UPI", "CASH_DEP", "CASH_WD"]
NAMES     = [
    "Amit Shah", "Priya Nair", "Rahul Verma", "Sneha Patel", "Vikas Sharma",
    "Deepa Reddy", "Karan Mehta", "Ananya Iyer", "Sanjay Gupta", "Pooja Singh",
    "Nikhil Joshi", "Meera Pillai", "Arjun Rao", "Kavya Menon", "Rohan Das",
    "Swati Tiwari", "Manish Kumar", "Neha Bose", "Suresh Nair", "Divya Agarwal",
    "Aakash Yadav", "Lakshmi Murugan", "Vijay Patil", "Ritu Malhotra", "Shiv Pandey",
    "Aarti Desai", "Ramesh Chandra", "Usha Rani", "Neeraj Saxena", "Preeti Ghosh",
    "Ajay Bhatt", "Pallavi Hegde", "Vinod Mishra", "Shreya Kulkarni", "Manoj Tiwari",
    "Bhavna Shah", "Ankur Srivastava", "Chitra Nambiar", "Pankaj Mathur", "Sunita Roy",
    "Anil Kapoor", "Rekha Sharma", "Sunil Verma", "Geeta Patel", "Harish Gupta",
    "Nandita Basu", "Rajiv Menon", "Lata Krishnan", "Girish Jain", "Mamta Chauhan",
    "Tarun Bajaj", "Fiona D'souza", "Akash Pandey", "Ridhi Oberoi", "Dev Malhotra",
    "Sarika Tiwari", "Mukesh Lal", "Anjali Rajan", "Venkat Iyer", "Premlata Sen",
    "Siddharth Nair", "Kavitha Rao", "Brij Mohan", "Yasmin Khan", "Ravi Deshpande",
    "Sudha Hegde", "Amar Singh", "Jaya Pillai", "Pramod Dubey", "Nalini Das",
    "Vivek Chatterjee", "Sangeeta Bose", "Hitesh Agarwal", "Tanya Mehta",
    "Umesh Chandra", "Chandrika Nair", "Dinesh Patil", "Sharmila Sharma",
    "Gopal Yadav", "Leela Menon"
]

# ─────────────────────────────────────────────
# STEP 1: Create accounts
# ─────────────────────────────────────────────
account_ids = [f"ACC_{str(i).zfill(3)}" for i in range(1, NUM_ACCOUNTS + 1)]

accounts = []
for i, acc_id in enumerate(account_ids):
    # Most accounts active; a few dormant (used in fraud scenario 4)
    is_dormant = (i >= 70)
    last_active = (BASE_DATE - timedelta(days=random.randint(180, 400))).strftime("%Y-%m-%d") \
                  if is_dormant else \
                  (BASE_DATE - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")

    accounts.append({
        "account_id":   acc_id,
        "name":         NAMES[i],
        "balance":      round(random.uniform(10000, 500000), 2),
        "account_type": random.choice(["savings", "current", "salary"]),
        "status":       "dormant" if is_dormant else "active",
        "last_active":  last_active,
        "risk_label":   "dormant" if is_dormant else "normal"   # ground truth
    })

accounts_df = pd.DataFrame(accounts)

# ─────────────────────────────────────────────
# STEP 2: Normal transactions
# ─────────────────────────────────────────────
transactions = []
txn_id_counter = 1

def make_txn(sender, receiver, amount, ts, channel=None, tx_type=None, fraud_label="normal", fraud_scenario="none"):
    global txn_id_counter
    t = {
        "txn_id":         f"TXN_{str(txn_id_counter).zfill(5)}",
        "sender":         sender,
        "receiver":       receiver,
        "amount":         round(amount, 2),
        "timestamp":      ts.strftime("%Y-%m-%d %H:%M:%S"),
        "channel":        channel or random.choice(CHANNELS),
        "tx_type":        tx_type or random.choice(TX_TYPES),
        "fraud_label":    fraud_label,       # ground truth: normal / fraud
        "fraud_scenario": fraud_scenario,    # none / circular / rapid / structuring / dormant
    }
    txn_id_counter += 1
    return t

active_accounts = account_ids[:70]   # normal pool
current_time = BASE_DATE

for _ in range(NUM_NORMAL_TXN):
    sender, receiver = random.sample(active_accounts, 2)
    amount = round(random.uniform(500, 75000), 2)
    current_time += timedelta(minutes=random.randint(1, 60))
    transactions.append(make_txn(sender, receiver, amount, current_time))

# ─────────────────────────────────────────────
# STEP 3: FRAUD SCENARIO 1 — Circular transaction
#
# ACC_001 → ACC_002 → ACC_003 → ACC_001
# Same amount, within 2-3 minutes each hop
# Purpose: money laundering loop — hard to detect without graph cycles
# ─────────────────────────────────────────────
circ_start = BASE_DATE + timedelta(hours=3)
circ_amount = 95000.00
circ_chain  = ["ACC_001", "ACC_002", "ACC_003", "ACC_001"]

for i in range(len(circ_chain) - 1):
    ts = circ_start + timedelta(minutes=i * 2 + random.randint(0, 1))
    transactions.append(make_txn(
        circ_chain[i], circ_chain[i+1],
        circ_amount - (i * 50),   # tiny variation to avoid exact match detection
        ts,
        channel="mobile",
        tx_type="IMPS",
        fraud_label="fraud",
        fraud_scenario="circular"
    ))

# ─────────────────────────────────────────────
# STEP 4: FRAUD SCENARIO 2 — Rapid multi-hop (layering)
#
# ACC_010 → ACC_011 → ACC_012 → ACC_013 → ACC_014 → ACC_015
# All within 8 minutes — classic layering to obscure origin
# ─────────────────────────────────────────────
rapid_start  = BASE_DATE + timedelta(hours=5)
rapid_amount = 200000.00
rapid_chain  = ["ACC_010", "ACC_011", "ACC_012", "ACC_013", "ACC_014", "ACC_015"]

for i in range(len(rapid_chain) - 1):
    ts = rapid_start + timedelta(minutes=i * 1 + random.randint(0, 1))
    # Amount decays slightly each hop (fees simulation)
    transactions.append(make_txn(
        rapid_chain[i], rapid_chain[i+1],
        rapid_amount * (0.995 ** i),
        ts,
        channel="web",
        tx_type="NEFT",
        fraud_label="fraud",
        fraud_scenario="rapid_multihop"
    ))

# ─────────────────────────────────────────────
# STEP 5: FRAUD SCENARIO 3 — Structuring / Smurfing
#
# ACC_020 sends ₹48k–₹49.9k to multiple accounts in one day
# Staying just below ₹50k to avoid reporting thresholds
# ─────────────────────────────────────────────
struct_start    = BASE_DATE + timedelta(hours=7)
struct_sender   = "ACC_020"
struct_receivers = ["ACC_021", "ACC_022", "ACC_023", "ACC_024", "ACC_025", "ACC_026"]

for i, receiver in enumerate(struct_receivers):
    ts = struct_start + timedelta(minutes=i * 15 + random.randint(0, 5))
    amount = random.uniform(47000, 49900)   # deliberately below 50k
    transactions.append(make_txn(
        struct_sender, receiver,
        amount,
        ts,
        channel=random.choice(["mobile", "web", "upi"]),
        tx_type="IMPS",
        fraud_label="fraud",
        fraud_scenario="structuring"
    ))

# ─────────────────────────────────────────────
# STEP 6: FRAUD SCENARIO 4 — Dormant account activation
#
# ACC_071 (dormant 200+ days) suddenly receives ₹5L then immediately
# distributes to multiple accounts — classic shell/mule pattern
# ─────────────────────────────────────────────
dormant_start    = BASE_DATE + timedelta(hours=10)
dormant_account  = "ACC_071"
dormant_feeder   = "ACC_030"    # sends the large sum
dormant_receivers = ["ACC_040", "ACC_041", "ACC_042"]

# Big inflow to dormant account
transactions.append(make_txn(
    dormant_feeder, dormant_account,
    500000.00,
    dormant_start,
    channel="branch",
    tx_type="RTGS",
    fraud_label="fraud",
    fraud_scenario="dormant_activation"
))

# Rapid outflow from dormant account within minutes
for i, recv in enumerate(dormant_receivers):
    ts = dormant_start + timedelta(minutes=i * 3 + 1)
    transactions.append(make_txn(
        dormant_account, recv,
        160000.00 - (i * 1000),
        ts,
        channel="mobile",
        tx_type="IMPS",
        fraud_label="fraud",
        fraud_scenario="dormant_activation"
    ))

# ─────────────────────────────────────────────
# STEP 7: Sort by timestamp and save
# ─────────────────────────────────────────────
txn_df = pd.DataFrame(transactions)
txn_df = txn_df.sort_values("timestamp").reset_index(drop=True)

accounts_df.to_csv(f"{OUTPUT_DIR}/accounts.csv", index=False)
txn_df.to_csv(f"{OUTPUT_DIR}/transactions.csv", index=False)

# ─────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────
print("=" * 55)
print("  DATASET GENERATED SUCCESSFULLY")
print("=" * 55)
print(f"  Accounts created      : {len(accounts_df)}")
print(f"    └─ Active accounts  : {len(accounts_df[accounts_df['status']=='active'])}")
print(f"    └─ Dormant accounts : {len(accounts_df[accounts_df['status']=='dormant'])}")
print()
print(f"  Transactions created  : {len(txn_df)}")
print(f"    └─ Normal           : {len(txn_df[txn_df['fraud_label']=='normal'])}")
print(f"    └─ Fraud total      : {len(txn_df[txn_df['fraud_label']=='fraud'])}")
print()
print("  Fraud breakdown:")
for scenario in txn_df[txn_df["fraud_label"]=="fraud"]["fraud_scenario"].unique():
    count = len(txn_df[txn_df["fraud_scenario"]==scenario])
    print(f"    └─ {scenario:<25}: {count} transactions")
print()
print(f"  Files saved:")
print(f"    └─ {OUTPUT_DIR}/accounts.csv")
print(f"    └─ {OUTPUT_DIR}/transactions.csv")
print("=" * 55)
