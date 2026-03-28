# FraudFlow-AI
Intelligent Fund Flow Tracking and Fraud Detection System

## 🚀 4-Agent Fraud Detection Pipeline

This system implements a sophisticated 4-agent pipeline for real-time fraud detection with FIU-ready evidence generation.

### Agent Architecture

#### 1. **Monitor Agent** (`monitor.py`)
- **Role**: Real-time transaction streaming and pipeline orchestration
- **Function**: Processes transactions one-by-one, coordinates analysis workflow
- **Key Feature**: Simulates live transaction monitoring

#### 2. **Analysis Agent** (`analyse.py`)
- **Role**: Multi-pattern fraud detection engine
- **Function**: Runs all detectors (circular, rapid, structuring, dormant patterns)
- **Output**: Pattern flags, risk scores, and graph statistics

#### 3. **Decision Agent** (`decide.py`)
- **Role**: Risk threshold evaluation and action determination
- **Function**: Applies business logic to determine allow/flag/alert actions
- **Thresholds**:
  - <30: Allow (Low risk)
  - 30-70: Flag (Medium risk)
  - >70: Alert (High risk)

#### 4. **Action Agent** (`act.py`)
- **Role**: Evidence generation and enforcement actions
- **Function**: Logs alerts, generates FIU-ready JSON evidence, simulates account blocking
- **Innovation**: **FIU-Ready Evidence Generation**

## 💡 Innovation Moment

**"This evidence JSON can be directly submitted to the Financial Intelligence Unit. We don't just detect - we document!"**

### Evidence Output Format

```json
{
  "alert": "HIGH",
  "path": "ACC_012 > ACC_034 > ACC_007 > ACC_012",
  "pattern": "Circular transaction",
  "time_span": "2 minutes 14 seconds",
  "risk_score": 85,
  "reason": "Funds returned to origin in <3 min across 3 accounts",
  "fiu_ready": true,
  "transaction_id": "TXN_001",
  "timestamp": "2024-01-15T10:30:00",
  "amount": 5000.00,
  "accounts_involved": ["ACC_012", "ACC_034"],
  "generated_at": "2024-01-15T10:30:05"
}
```

## 🏃 Quick Start

### Run the Complete Pipeline Demo
```bash
python demo_pipeline.py
```

### Run Individual Components
```bash
# Monitor transactions
python monitor.py

# Test analysis agent
python -c "from analyse import AnalysisAgent; print('Analysis Agent Ready')"
```

## 📊 Detection Patterns

- **Circular Transactions**: Funds returning to origin through multiple accounts
- **Rapid Transactions**: Multiple transactions within short time windows
- **Structuring**: Breaking large transactions into smaller amounts
- **Dormant Accounts**: Unusual activity in long-dormant accounts

## 🛠 Technical Stack

- **Python 3.8+**
- **NetworkX**: Graph analysis and pattern detection
- **Pandas**: Data processing and manipulation
- **Real-time Processing**: Streaming transaction analysis
- **JSON Evidence**: FIU-compliant documentation

## 📁 Project Structure

```
FraudFlow-AI/
├── monitor.py          # Monitoring Agent
├── analyse.py          # Analysis Agent
├── decide.py           # Decision Agent
├── act.py             # Action Agent
├── demo_pipeline.py    # Complete pipeline demo
├── detect.py          # Pattern detection functions
├── score.py           # Risk scoring logic
├── journey.py         # Transaction journey reconstruction
├── data/
│   ├── transactions.csv
│   └── accounts.csv
├── evidence/           # Generated evidence files
├── logs/              # Action logs
└── graph/             # Graph visualizations
```
