import streamlit as st

st.set_page_config(
    page_title="ChurnGuard AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ─────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    background: #0a0f1e !important;
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] {
    background: #0d1426 !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
}
[data-testid="stMain"] {
    background: #0a0f1e !important;
}
[data-testid="stHeader"] { display: none; }

/* ── Sidebar nav ─────────────────────────────────────── */
[data-testid="stSidebarNavLink"] {
    border-radius: 10px !important;
    margin-bottom: 4px !important;
    transition: all .2s ease !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
}
[data-testid="stSidebarNavLink"]:hover {
    background: rgba(99,102,241,0.12) !important;
    color: #a5b4fc !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(168,85,247,0.15)) !important;
    color: #a5b4fc !important;
    border-left: 3px solid #6366f1 !important;
}

/* ── Cards ───────────────────────────────────────────── */
.card {
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(20px);
    transition: all .3s ease;
}
.card:hover {
    border-color: rgba(99,102,241,0.3);
    box-shadow: 0 8px 32px rgba(99,102,241,0.08);
}

/* ── KPI Cards ───────────────────────────────────────── */
.kpi-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: all .3s ease;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, linear-gradient(90deg, #6366f1, #8b5cf6));
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(99,102,241,0.12);
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(135deg, #e2e8f0, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.kpi-label { font-size: 0.8rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 6px; }
.kpi-delta { font-size: 0.8rem; margin-top: 8px; }
.kpi-delta.up { color: #34d399; }
.kpi-delta.down { color: #f87171; }
.kpi-delta.neutral { color: #94a3b8; }

/* ── Risk badges ─────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: .04em;
}
.badge-high   { background: rgba(239,68,68,.18);  color: #fca5a5; border: 1px solid rgba(239,68,68,.3);  }
.badge-medium { background: rgba(245,158,11,.15); color: #fcd34d; border: 1px solid rgba(245,158,11,.25); }
.badge-low    { background: rgba(52,211,153,.15); color: #6ee7b7; border: 1px solid rgba(52,211,153,.25); }

/* ── Section headers ─────────────────────────────────── */
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.section-sub { font-size: 0.9rem; color: #64748b; margin-bottom: 20px; }

/* ── Page header ─────────────────────────────────────── */
.page-header {
    padding: 32px 0 24px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 28px;
}
.page-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}
.page-desc { font-size: 0.95rem; color: #64748b; margin-top: 6px; }

/* ── Result panel ────────────────────────────────────── */
.result-high   { border-color: rgba(239,68,68,.4) !important; background: linear-gradient(135deg, rgba(239,68,68,.07), rgba(255,255,255,.02)) !important; }
.result-medium { border-color: rgba(245,158,11,.4) !important; background: linear-gradient(135deg, rgba(245,158,11,.07), rgba(255,255,255,.02)) !important; }
.result-low    { border-color: rgba(52,211,153,.4) !important; background: linear-gradient(135deg, rgba(52,211,153,.07), rgba(255,255,255,.02)) !important; }

/* ── Tables ──────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrame"] thead th {
    background: rgba(99,102,241,0.12) !important;
    color: #94a3b8 !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: .06em;
}

/* ── Inputs ──────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] > div > div > input,
[data-testid="stSlider"] {
    border-radius: 10px !important;
}
.stSlider .thumb { background: #6366f1 !important; }

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all .2s ease !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.45) !important;
}

/* ── Divider ─────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Sidebar logo ────────────────────────────────────── */
.sidebar-logo {
    padding: 16px 4px 24px;
    display: flex; align-items: center; gap: 10px;
}
.sidebar-logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.sidebar-logo-text { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.sidebar-logo-sub  { font-size: 0.7rem; color: #64748b; }

/* ── Progress bar override ───────────────────────────── */
.stProgress > div > div { background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; border-radius: 99px !important; }
</style>
""", unsafe_allow_html=True)

# Sidebar branding
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">📊</div>
        <div>
            <div class="sidebar-logo-text">ChurnGuard</div>
            <div class="sidebar-logo-sub">AI · v1.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/dashboard.py",  title="Dashboard",          icon="🏠"),
    st.Page("pages/predict.py",    title="Predict Churn",      icon="🔮"),
    st.Page("pages/customers.py",  title="Customers",          icon="👥"),
    st.Page("pages/history.py",    title="Prediction History", icon="📋"),
    st.Page("pages/analytics.py",  title="Analytics",          icon="📈"),
])
pg.run()
