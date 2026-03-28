"""
app_config.py
=============
Handles Streamlit page configuration and global CSS injection.
"""

import streamlit as st


class AppConfig:
    """Handles Streamlit page configuration and global CSS injection."""

    PAGE_TITLE = "AI Fund Flow Intelligence System"
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
        """Inject all global CSS styles for the white/light theme."""
        st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"],
  [data-testid="block-container"] {
      background-color: #f4f6fa !important;
      color: #1a1d23 !important;
      font-family: 'Syne', sans-serif !important;
  }

  [data-testid="stSidebar"] {
      background-color: #ffffff !important;
      border-right: 1px solid #e0e4ef !important;
  }
  [data-testid="stSidebar"] * { color: #1a1d23 !important; }

  .sidebar-header {
      font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 800;
      color: #1a1d23; margin-bottom: 1rem; letter-spacing: 0.04em;
  }

  /* KPI cards */
  .metric-card {
      border-radius: 12px; padding: 1rem 1.2rem; color: white;
      min-height: 110px; display: flex; flex-direction: column;
      justify-content: space-between; box-shadow: 0 2px 10px rgba(0,0,0,0.12);
  }
  .metric-card-blue   { background: linear-gradient(135deg,#1565c0,#1e88e5); }
  .metric-card-teal   { background: linear-gradient(135deg,#00695c,#00897b); }
  .metric-card-red    { background: linear-gradient(135deg,#b71c1c,#e53935); }
  .metric-card-orange { background: linear-gradient(135deg,#e65100,#fb8c00); }
  .metric-card-amber  { background: linear-gradient(135deg,#f57f17,#fbc02d); }

  .metric-title { font-size:0.72rem; font-weight:700; opacity:0.92; text-transform:uppercase; letter-spacing:0.08em; }
  .metric-value { font-size:2.5rem; font-weight:800; line-height:1; margin:0.3rem 0; }
  .metric-delta { font-size:0.8rem; font-weight:600; }
  .delta-green  { color:#c8f7d0; }
  .delta-red    { color:#ffd6d4; }

  /* Section headers */
  .section-header { font-family:'Syne',sans-serif; font-size:1rem; font-weight:800; color:#1565c0; margin-bottom:0.25rem; }
  .section-sub    { font-size:0.75rem; color:#6b7280; margin-bottom:0.7rem; }

  /* Panel */
  .panel { background:#ffffff; border:1px solid #e0e4ef; border-radius:12px; padding:1rem 1.2rem; box-shadow:0 1px 4px rgba(0,0,0,0.06); }

  /* Fraud Alerts table */
  .fraud-table { width:100%; border-collapse:collapse; font-size:0.83rem; }
  .fraud-table th { color:#6b7280; font-weight:700; text-align:left; padding:0.5rem 0.6rem; border-bottom:2px solid #e0e4ef; text-transform:uppercase; font-size:0.72rem; letter-spacing:0.06em; }
  .fraud-table td { padding:0.55rem 0.6rem; border-bottom:1px solid #f0f2f8; color:#1a1d23; }
  .badge-high   { background:#fde8e8; color:#b91c1c; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.72rem; border:1px solid #fca5a5; }
  .badge-medium { background:#fef3c7; color:#92400e; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.72rem; border:1px solid #fcd34d; }
  .badge-low    { background:#dbeafe; color:#1e40af; padding:2px 10px; border-radius:20px; font-weight:700; font-size:0.72rem; border:1px solid #93c5fd; }

  /* Fraud chain */
  .fraud-chain { background:#f0f4ff; border:1px solid #c7d2fe; border-radius:8px; padding:0.8rem 1rem;
      font-family:'JetBrains Mono',monospace; font-size:1rem; font-weight:600; color:#1e40af; letter-spacing:0.02em; margin-bottom:0.8rem; }

  /* Risk score badges */
  .risk-score-high   { background:#ef4444; color:white; padding:3px 12px; border-radius:6px; font-weight:800; font-size:0.9rem; margin-right:6px; }
  .risk-score-medium { background:#f59e0b; color:white; padding:3px 12px; border-radius:6px; font-weight:800; font-size:0.9rem; margin-right:6px; }
  .risk-label-high   { color:#dc2626; font-weight:700; font-size:0.9rem; }
  .risk-label-medium { color:#d97706; font-weight:700; font-size:0.9rem; }

  /* Checklist */
  .check-item { color:#16a34a; font-size:0.85rem; margin:0.28rem 0; font-weight:600; }

  /* Button */
  div.stButton > button {
      background: linear-gradient(135deg,#16a34a,#22c55e); color:white;
      font-family:'Syne',sans-serif; font-weight:700; font-size:0.9rem;
      border:none; border-radius:8px; padding:0.55rem 1.5rem; width:100%;
      box-shadow:0 2px 6px rgba(22,163,74,0.3);
  }
  div.stButton > button:hover {
      background:linear-gradient(135deg,#15803d,#16a34a);
      box-shadow:0 4px 12px rgba(22,163,74,0.4);
  }

  /* Top-bar */
  .topbar { display:flex; align-items:center; justify-content:flex-end; gap:0.6rem; font-size:0.78rem; color:#6b7280; padding-bottom:0.5rem; }
  .status-dot { width:9px; height:9px; border-radius:50%; background:#22c55e; display:inline-block; box-shadow:0 0 6px #22c55e; }

  /* Page title */
  .page-title { font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; color:#1a1d23; }
  .title-icon { font-size:1.5rem; margin-right:0.4rem; }

  /* Form overrides */
  label { color:#374151 !important; font-size:0.82rem !important; }
  [data-testid="stSelectbox"] > div > div { background:#f9fafb !important; border-color:#d1d5db !important; color:#1a1d23 !important; }
  [data-testid="stCheckbox"] label { color:#374151 !important; font-size:0.85rem !important; }

  /* Scrollbar */
  ::-webkit-scrollbar { width:6px; }
  ::-webkit-scrollbar-track { background:#f4f6fa; }
  ::-webkit-scrollbar-thumb { background:#d1d5db; border-radius:3px; }

  hr { border-color:#e0e4ef !important; }
</style>
""", unsafe_allow_html=True)
