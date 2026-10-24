"""Analytics page — segment churn rate charts across 5 dimensions."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data.mock_data import MOCK_ANALYTICS

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    margin=dict(l=0, r=0, t=8, b=0),
)

def segment_chart(title: str, description: str, data: list[dict],
                  horizontal: bool = False) -> None:
    df = pd.DataFrame(data)
    df["pct"] = df["churn_rate"] * 100
    df["label_text"] = df["pct"].apply(lambda x: f"{x:.1f}%")

    # Color gradient: low churn → green, high churn → red
    colors = []
    for v in df["pct"]:
        t = (v - df["pct"].min()) / (df["pct"].max() - df["pct"].min() + 1e-9)
        r = int(16 + t * (239 - 16))
        g = int(185 - t * (185 - 68))
        b = int(129 - t * (129 - 68))
        colors.append(f"rgb({r},{g},{b})")

    if horizontal:
        fig = go.Figure(go.Bar(
            x=df["pct"], y=df["segment"],
            orientation="h",
            marker=dict(color=colors, line_width=0),
            text=df["label_text"], textposition="outside",
            textfont=dict(color="#e2e8f0", size=12),
            hovertemplate="%{y}: %{x:.1f}% churn<extra></extra>",
        ))
        fig.update_layout(
            **CHART_LAYOUT, height=220,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                       ticksuffix="%", range=[0, df["pct"].max() * 1.25]),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        )
    else:
        fig = go.Figure(go.Bar(
            x=df["segment"], y=df["pct"],
            marker=dict(color=colors, line_width=0),
            text=df["label_text"], textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
            hovertemplate="%{x}: %{y:.1f}% churn<extra></extra>",
        ))
        fig.update_layout(
            **CHART_LAYOUT, height=220,
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                       ticksuffix="%", range=[0, df["pct"].max() * 1.3]),
        )

    st.markdown(f"""
    <div class="card" style="padding:20px 20px 8px">
      <div class="section-title" style="font-size:1rem">{title}</div>
      <div class="section-sub" style="margin-bottom:0">{description}</div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Customer count sub-row
    cust_html = "<div style='display:flex;gap:12px;flex-wrap:wrap;padding:0 0 8px'>"
    for row in data:
        cust_html += (
            f"<div style='font-size:.75rem;color:#64748b'>"
            f"<span style='color:#94a3b8'>{row['segment']}</span>: "
            f"<strong style='color:#e2e8f0'>{row['customers']:,}</strong> customers</div>"
        )
    cust_html += "</div>"
    st.markdown(cust_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Page ──────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
  <div class="page-title">Churn Analytics</div>
  <div class="page-desc">Understand which customer segments churn the most.</div>
</div>
""", unsafe_allow_html=True)

a = MOCK_ANALYTICS

col1, col2 = st.columns(2, gap="large")

with col1:
    segment_chart("Churn by Contract Type",
                  "Longer contracts strongly reduce churn",
                  a["by_contract"])
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    segment_chart("Churn by Payment Method",
                  "Automatic payments correlate with loyalty",
                  a["by_payment"], horizontal=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    segment_chart("Churn by Internet Service",
                  "Fiber optic customers churn the most",
                  a["by_internet"])

with col2:
    segment_chart("Churn by Tenure",
                  "New customers are the most likely to leave",
                  a["by_tenure"])
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    segment_chart("Churn by Monthly Charges",
                  "Higher bills increase churn likelihood",
                  a["by_monthly_charges"])
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Model insights card
    st.markdown("""
    <div class="card">
      <div class="section-title" style="font-size:1rem">Model Insights</div>
      <div class="section-sub">Gradient Boosting · v1.0.0-demo</div>
      <div style="font-size:.85rem;color:#94a3b8;margin-bottom:16px">
        The model analyzes customer attributes and identifies patterns associated
        with previous customer churn.
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px">
        <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">Accuracy</div>
          <div style="font-size:1.1rem;font-weight:700;color:#a5b4fc">—</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">Precision</div>
          <div style="font-size:1.1rem;font-weight:700;color:#a5b4fc">—</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">Recall</div>
          <div style="font-size:1.1rem;font-weight:700;color:#a5b4fc">—</div>
        </div>
        <div style="background:rgba(255,255,255,0.04);border-radius:10px;padding:12px;text-align:center">
          <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;margin-bottom:4px">ROC AUC</div>
          <div style="font-size:1.1rem;font-weight:700;color:#a5b4fc">—</div>
        </div>
      </div>
      <div style="background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);
                  border-radius:10px;padding:10px;font-size:.8rem;color:#a5b4fc">
        ℹ️ Metrics will populate once the FastAPI backend is connected.
      </div>
    </div>
    """, unsafe_allow_html=True)
