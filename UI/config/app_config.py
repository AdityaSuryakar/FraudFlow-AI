"""
app_config.py
=============
Handles Streamlit page configuration and global CSS injection.
Updated with dark-mode premium theme for FraudFlow-AI.
"""

import streamlit as st


class AppConfig:
    """Handles Streamlit page configuration and global CSS injection."""

    PAGE_TITLE = "FraudFlow-AI | Fund Flow Intelligence System"
    PAGE_ICON  = "🏦"

    @staticmethod
    def configure():
        """Call once at app startup to set page layout and inject styles."""
        st.set_page_config(
            page_title=AppConfig.PAGE_TITLE,
            page_icon=AppConfig.PAGE_ICON,
            layout="wide",
            initial_sidebar_state="expanded",
        )
        AppConfig._inject_css()

    @staticmethod
    def _inject_css():
        """Inject all global CSS styles for the dark premium theme."""
        st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

  /* ── GLOBAL RESET ─────────────────────────────────────────── */
  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  [data-testid="block-container"] {
      background: linear-gradient(135deg, #0a0e1a 0%, #0f1525 50%, #0a1020 100%) !important;
      color: #e2e8f0 !important;
      font-family: 'Inter', sans-serif !important;
  }

  /* ── SIDEBAR ──────────────────────────────────────────────── */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0d1117 0%, #161b2e 100%) !important;
      border-right: 1px solid rgba(99,102,241,0.2) !important;
  }
  [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
  [data-testid="stSidebar"] .stMarkdown h1,
  [data-testid="stSidebar"] .stMarkdown h2,
  [data-testid="stSidebar"] .stMarkdown h3 { color: #818cf8 !important; }

  .sidebar-brand {
      display: flex; align-items: center; gap: 10px;
      padding: 0.5rem 0 1rem 0;
  }
  .sidebar-brand-icon {
      font-size: 1.8rem;
      filter: drop-shadow(0 0 8px rgba(99,102,241,0.8));
  }
  .sidebar-brand-text {
      font-size: 1.1rem; font-weight: 800; letter-spacing: 0.02em;
      background: linear-gradient(135deg, #818cf8, #c084fc);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .sidebar-brand-sub {
      font-size: 0.65rem; color: #64748b !important; letter-spacing: 0.08em;
      text-transform: uppercase;
  }

  .sidebar-section {
      font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
      color: #475569 !important; text-transform: uppercase; margin: 1rem 0 0.5rem 0;
  }

  .agent-status-item {
      display: flex; align-items: center; gap: 8px;
      padding: 0.4rem 0.6rem; border-radius: 8px;
      background: rgba(99,102,241,0.08); margin-bottom: 0.35rem;
      border: 1px solid rgba(99,102,241,0.15);
  }
  .agent-dot-green { width:8px; height:8px; border-radius:50%; background:#22c55e; box-shadow:0 0 6px #22c55e; flex-shrink:0; }
  .agent-dot-grey  { width:8px; height:8px; border-radius:50%; background:#475569; flex-shrink:0; }
  .agent-name { font-size:0.78rem; font-weight:600; color:#c7d2fe !important; }
  .agent-role { font-size:0.65rem; color:#64748b !important; margin-left:auto; }

  /* ── KPI CARDS ────────────────────────────────────────────── */
  .kpi-row { display:flex; gap:0.8rem; margin-bottom:1.2rem; flex-wrap:wrap; }
  .kpi-card {
      flex:1; min-width:140px; border-radius:14px; padding:1.1rem 1.3rem;
      position:relative; overflow:hidden; cursor:default;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .kpi-card:hover { transform:translateY(-3px); box-shadow:0 8px 32px rgba(0,0,0,0.4); }
  .kpi-card::before {
      content:''; position:absolute; top:-40%; right:-20%;
      width:120px; height:120px; border-radius:50%;
      background:rgba(255,255,255,0.06);
  }
  .kpi-blue   { background:linear-gradient(135deg,#1e3a5f,#1d4ed8); border:1px solid rgba(59,130,246,0.3); }
  .kpi-purple { background:linear-gradient(135deg,#2e1065,#7c3aed); border:1px solid rgba(139,92,246,0.3); }
  .kpi-red    { background:linear-gradient(135deg,#450a0a,#dc2626); border:1px solid rgba(239,68,68,0.3); }
  .kpi-amber  { background:linear-gradient(135deg,#451a03,#d97706); border:1px solid rgba(245,158,11,0.3); }
  .kpi-teal   { background:linear-gradient(135deg,#022c22,#059669); border:1px solid rgba(16,185,129,0.3); }
  .kpi-indigo { background:linear-gradient(135deg,#1e1b4b,#4f46e5); border:1px solid rgba(99,102,241,0.3); }

  .kpi-icon  { font-size:1.6rem; margin-bottom:0.4rem; display:block; }
  .kpi-label { font-size:0.68rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; opacity:0.75; }
  .kpi-value { font-size:2.2rem; font-weight:800; line-height:1.1; margin:0.2rem 0; color:#fff; }
  .kpi-delta-pos { font-size:0.72rem; color:#86efac; font-weight:600; }
  .kpi-delta-neg { font-size:0.72rem; color:#fca5a5; font-weight:600; }
  .kpi-delta-neu { font-size:0.72rem; color:#94a3b8; font-weight:600; }

  /* ── SECTION HEADERS ─────────────────────────────────────── */
  .section-header {
      font-size:0.95rem; font-weight:700; color:#818cf8; margin-bottom:0.2rem;
      display:flex; align-items:center; gap:8px;
  }
  .section-sub { font-size:0.72rem; color:#475569; margin-bottom:0.8rem; }

  /* ── GLASS PANELS ─────────────────────────────────────────── */
  .glass-panel {
      background:rgba(15,21,37,0.8); backdrop-filter:blur(12px);
      border:1px solid rgba(99,102,241,0.18); border-radius:16px;
      padding:1.2rem 1.4rem; margin-bottom:1rem;
      box-shadow:0 4px 24px rgba(0,0,0,0.3);
  }

  /* ── ALERTS TABLE ─────────────────────────────────────────── */
  .alert-table { width:100%; border-collapse:collapse; font-size:0.82rem; }
  .alert-table th {
      color:#64748b; font-weight:600; text-align:left;
      padding:0.55rem 0.8rem; border-bottom:1px solid rgba(99,102,241,0.15);
      font-size:0.68rem; letter-spacing:0.08em; text-transform:uppercase;
  }
  .alert-table td { padding:0.55rem 0.8rem; border-bottom:1px solid rgba(99,102,241,0.06); color:#cbd5e1; }
  .alert-table tr:hover td { background:rgba(99,102,241,0.06); }
  .alert-table .acc-id { color:#818cf8; font-weight:700; font-family:'JetBrains Mono',monospace; font-size:0.8rem; }

  .badge { padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.68rem; }
  .badge-high   { background:rgba(239,68,68,0.18);  color:#f87171; border:1px solid rgba(239,68,68,0.3);   }
  .badge-medium { background:rgba(245,158,11,0.18); color:#fbbf24; border:1px solid rgba(245,158,11,0.3);  }
  .badge-low    { background:rgba(34,197,94,0.18);  color:#4ade80; border:1px solid rgba(34,197,94,0.3);   }

  .pattern-tag { font-size:0.72rem; color:#a5b4fc; background:rgba(99,102,241,0.12); padding:2px 8px; border-radius:6px; }

  /* ── FRAUD CHAIN ─────────────────────────────────────────── */
  .fraud-chain {
      font-family:'JetBrains Mono',monospace; font-size:0.9rem; font-weight:600;
      color:#a5b4fc; background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25);
      border-radius:10px; padding:0.8rem 1rem; margin:0.5rem 0;
      word-break:break-all; line-height:1.6;
  }

  /* ── SCORE BADGE ─────────────────────────────────────────── */
  .score-badge-high   { background:#dc2626; color:#fff; padding:4px 14px; border-radius:8px; font-weight:800; font-size:1rem; }
  .score-badge-medium { background:#d97706; color:#fff; padding:4px 14px; border-radius:8px; font-weight:800; font-size:1rem; }
  .score-badge-low    { background:#16a34a; color:#fff; padding:4px 14px; border-radius:8px; font-weight:800; font-size:1rem; }

  /* ── LIVE HEADER ─────────────────────────────────────────── */
  .main-header {
      display:flex; align-items:center; justify-content:space-between;
      padding:1rem 0 0.5rem 0; margin-bottom:0.5rem;
  }
  .header-logo {
      font-size:1.6rem; font-weight:900; letter-spacing:-0.02em;
      background:linear-gradient(135deg,#818cf8 0%,#c084fc 50%,#38bdf8 100%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  }
  .header-sub { font-size:0.78rem; color:#475569; font-weight:500; margin-top:2px; }
  .live-pill {
      display:inline-flex; align-items:center; gap:6px;
      background:rgba(34,197,94,0.12); border:1px solid rgba(34,197,94,0.3);
      border-radius:20px; padding:4px 12px;
      font-size:0.72rem; font-weight:600; color:#4ade80;
  }
  .live-dot { width:7px; height:7px; border-radius:50%; background:#22c55e; animation:pulse 1.5s infinite; }
  @keyframes pulse {
      0%, 100% { box-shadow:0 0 0 0 rgba(34,197,94,0.6); }
      50%       { box-shadow:0 0 0 5px rgba(34,197,94,0); }
  }

  /* ── BUTTONS ─────────────────────────────────────────────── */
  div.stButton > button {
      background:linear-gradient(135deg,#4f46e5,#7c3aed);
      color:#fff; border:none; border-radius:10px;
      font-family:'Inter',sans-serif; font-weight:700; font-size:0.85rem;
      padding:0.55rem 1.2rem; width:100%;
      box-shadow:0 4px 14px rgba(79,70,229,0.4);
      transition:all 0.2s ease;
  }
  div.stButton > button:hover {
      background:linear-gradient(135deg,#4338ca,#6d28d9);
      box-shadow:0 6px 20px rgba(79,70,229,0.6);
      transform:translateY(-1px);
  }

  /* ── EVIDENCE DOWNLOAD BUTTON ─────────────────────────────── */
  .stDownloadButton > button {
      background:linear-gradient(135deg,#065f46,#059669) !important;
      color:#fff !important; border:none !important; border-radius:10px !important;
      font-weight:700 !important; width:100% !important;
      box-shadow:0 4px 14px rgba(5,150,105,0.4) !important;
  }

  /* ── SELECTBOX / CHECKBOX ─────────────────────────────────── */
  [data-testid="stSelectbox"] > div > div {
      background:rgba(15,21,37,0.9) !important;
      border:1px solid rgba(99,102,241,0.3) !important;
      color:#e2e8f0 !important; border-radius:8px !important;
  }
  [data-testid="stCheckbox"] label { color:#94a3b8 !important; font-size:0.82rem !important; }

  /* ── TABS ─────────────────────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] { gap:4px; background:transparent; }
  .stTabs [data-baseweb="tab"] { background:rgba(99,102,241,0.1); border-radius:8px 8px 0 0; color:#94a3b8; font-weight:600; font-size:0.82rem; border:1px solid rgba(99,102,241,0.15); }
  .stTabs [aria-selected="true"] { background:rgba(99,102,241,0.25) !important; color:#818cf8 !important; border-color:rgba(99,102,241,0.4) !important; }

  /* ── INFO/SUCCESS BOXES ───────────────────────────────────── */
  .stInfo, .stSuccess, .stWarning, .stError {
      border-radius:10px !important; font-size:0.82rem !important;
  }
  .stInfo    { background:rgba(14,165,233,0.1) !important; border:1px solid rgba(14,165,233,0.3) !important; }
  .stSuccess { background:rgba(34,197,94,0.1) !important;  border:1px solid rgba(34,197,94,0.3) !important;  }

  /* ── SCROLLBAR ────────────────────────────────────────────── */
  ::-webkit-scrollbar { width:5px; height:5px; }
  ::-webkit-scrollbar-track { background:transparent; }
  ::-webkit-scrollbar-thumb { background:rgba(99,102,241,0.3); border-radius:3px; }

  hr { border-color:rgba(99,102,241,0.15) !important; }

  /* ── METRIC (native st.metric) ────────────────────────────── */
  [data-testid="metric-container"] {
      background:rgba(15,21,37,0.6); border:1px solid rgba(99,102,241,0.15);
      border-radius:12px; padding:0.8rem 1rem;
  }

  /* ── SPINNER ──────────────────────────────────────────────── */
  .stSpinner > div { border-top-color:#818cf8 !important; }

  /* ── DATAFRAME ────────────────────────────────────────────── */
  [data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)
