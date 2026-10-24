"""Dashboard page — KPIs, churn trend chart, distribution, risk overview."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data.mock_data import MOCK_CUSTOMERS, MOCK_SUMMARY, MOCK_TREND

# ── Helpers ──────────────────────────────────────────────────────────────────

COLORS = {
    "primary":   "#6366f1",
    "secondary": "#8b5cf6",
    "danger":    "#ef4444",
    "warning":   "#f59e0b",
    "success":   "#10b981",
    "muted":     "#64748b",
    "bg":        "#0a0f1e",
    "surface":   "rgba(255,255,255,0.04)",
    "border":    "rgba(255,255,255,0.08)",
}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8"),
    margin=dict(l=0, r=0, t=8, b=0),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"),
    ),
)

def _badge(risk: str) -> str:
    cls = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}[risk]
    return f'<span class="badge {cls}">{risk}</span>'

def _pct(v: float, digits: int = 1) -> str:
    return f"{v * 100:.{digits}f}%"

# ── Page header ──────────────────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
  <div class="page-title">Customer Churn Analytics</div>
  <div class="page-desc">AI-powered insights to identify customers at risk of leaving.</div>
</div>
""", unsafe_allow_html=True)

s = MOCK_SUMMARY

# ── KPI Cards ────────────────────────────────────────────────────────────────

k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, delta=None, delta_dir="neutral", accent="linear-gradient(90deg,#6366f1,#8b5cf6)"):
    delta_html = ""
    if delta:
        arrow = "▲" if delta_dir == "up" else "▼" if delta_dir == "down" else ""
        delta_html = f'<div class="kpi-delta {delta_dir}">{arrow} {delta}</div>'
    col.markdown(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

with k1: kpi(k1, "Total Customers", f"{s['total_customers']:,}",
             f"+{_pct(s['customer_growth'])} this month", "up")
with k2: kpi(k2, "Churn Rate", _pct(s['churn_rate']),
             "vs 28.4% last month", "up",
             "linear-gradient(90deg,#ef4444,#f87171)")
with k3: kpi(k3, "High Risk", f"{s['high_risk_customers']:,}",
             "requires attention", "neutral",
             "linear-gradient(90deg,#f59e0b,#fbbf24)")
with k4: kpi(k4, "Retained", f"{s['retained']:,}",
             "active customers", "neutral",
             "linear-gradient(90deg,#10b981,#34d399)")
with k5: kpi(k5, "Avg Monthly", f"${s['avg_monthly_charges']:.2f}",
             "per customer", "neutral",
             "linear-gradient(90deg,#06b6d4,#22d3ee)")

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Churn Trend + Distribution ────────────────────────────────────────────────

col_trend, col_dist = st.columns([2, 1])

with col_trend:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Churn Trend</div>', unsafe_allow_html=True)

    range_labels = {"7d": "7 Days", "30d": "30 Days", "3m": "3 Months", "1y": "1 Year"}
    sel = st.radio("Range", list(range_labels.keys()), format_func=lambda x: range_labels[x],
                   horizontal=True, label_visibility="collapsed", key="trend_range")

    trend_data = MOCK_TREND[sel]
    df_trend = pd.DataFrame(trend_data)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_trend["label"], y=df_trend["retained"],
        name="Retained", marker_color="#6366f1",
        marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        x=df_trend["label"], y=df_trend["churned"],
        name="Churned", marker_color="#ef4444",
        marker_line_width=0,
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        barmode="stack",
        height=280,
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with col_dist:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Churn Split</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Overall retention vs churn</div>', unsafe_allow_html=True)

    fig2 = go.Figure(go.Pie(
        labels=["Retained", "Churned"],
        values=[s["retained"], s["churned"]],
        hole=0.65,
        marker=dict(colors=["#6366f1", "#ef4444"],
                    line=dict(color="#0a0f1e", width=3)),
        textinfo="none",
    ))
    fig2.add_annotation(
        text=f"<b>{_pct(s['churn_rate'])}</b><br><span style='font-size:11px;color:#64748b'>churn rate</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="#e2e8f0", family="Inter"),
    )
    fig2.update_layout(**CHART_LAYOUT, height=260, showlegend=True)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Risk Overview + Recent High Risk + Model Info ─────────────────────────────

col_risk, col_recent, col_model = st.columns(3)

with col_risk:
    st.markdown('<div class="card" style="height:320px">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Risk Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Customers by risk level</div>', unsafe_allow_html=True)

    risk_data = s["risk"]
    total_r   = sum(risk_data.values())
    for level, clr in [("High", "#ef4444"), ("Medium", "#f59e0b"), ("Low", "#10b981")]:
        count = risk_data[level]
        pct   = count / total_r
        st.markdown(f"""
        <div style="margin-bottom:14px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px">
            <span style="font-size:.85rem;color:#e2e8f0;font-weight:500">{level} Risk</span>
            <span style="font-size:.85rem;color:{clr};font-weight:600">{count:,} &nbsp;({_pct(pct)})</span>
          </div>
          <div style="height:8px;border-radius:99px;background:rgba(255,255,255,0.06)">
            <div style="height:100%;width:{pct*100:.1f}%;background:{clr};border-radius:99px;
                        transition:width .8s ease"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_recent:
    st.markdown('<div class="card" style="height:320px;overflow:auto">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">High Risk Customers</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Top 5 by churn probability</div>', unsafe_allow_html=True)

    high_risk = sorted(
        [c for c in MOCK_CUSTOMERS if c["risk_level"] == "High"],
        key=lambda c: -c["churn_probability"],
    )[:5]

    for c in high_risk:
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05)">
          <div>
            <div style="font-weight:600;font-size:.9rem;color:#e2e8f0">{c['name']}</div>
            <div style="font-size:.78rem;color:#64748b">{c['customer_id']} · {c['contract']}</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:1.1rem;font-weight:700;color:#ef4444">
              {_pct(c['churn_probability'])}
            </div>
            {_badge(c['risk_level'])}
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_model:
    st.markdown('<div class="card" style="height:320px">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Model Info</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Active prediction model</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom:12px">
      <div style="font-size:.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Model</div>
      <div style="font-size:.95rem;color:#e2e8f0;font-weight:600">Gradient Boosting</div>
    </div>
    <div style="margin-bottom:12px">
      <div style="font-size:.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Version</div>
      <div style="font-size:.95rem;color:#a5b4fc;font-weight:500">v1.0.0-demo</div>
    </div>
    <div style="margin-bottom:16px">
      <div style="font-size:.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">Risk Thresholds</div>
      <div style="font-size:.85rem;color:#e2e8f0;margin-top:4px">
        🟢 Low: &lt;35% &nbsp;|&nbsp; 🟡 Medium: 35–65% &nbsp;|&nbsp; 🔴 High: ≥65%
      </div>
    </div>
    <div style="background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);
                border-radius:10px;padding:10px;font-size:.8rem;color:#a5b4fc">
      ℹ️ Demo mode — connect NEXT_PUBLIC_API_URL to use the real FastAPI backend.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
