"""Customers page — searchable, filterable customer table with detail drawer."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from data.mock_data import MOCK_CUSTOMERS
from data.churn_model import score_customer

def _badge(risk: str) -> str:
    cls = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}[risk]
    return f'<span class="badge {cls}">{risk}</span>'

st.markdown("""
<div class="page-header">
  <div class="page-title">Customers</div>
  <div class="page-desc">Browse customers and their latest predicted churn risk.</div>
</div>
""", unsafe_allow_html=True)

# ── Filters ───────────────────────────────────────────────────────────────────

f1, f2, f3 = st.columns([3, 1, 1])
query    = f1.text_input("🔍  Search customers", placeholder="Name, ID, or email…")
risk_fil = f2.selectbox("Risk Level", ["All", "High", "Medium", "Low"])
sort_by  = f3.selectbox("Sort by", ["Churn % (↓)", "Churn % (↑)", "Name (A-Z)", "Tenure (↓)"])

# ── Filter & sort ─────────────────────────────────────────────────────────────

df = pd.DataFrame(MOCK_CUSTOMERS)

if query:
    q = query.lower()
    mask = (
        df["name"].str.lower().str.contains(q, na=False)
        | df["customer_id"].str.lower().str.contains(q, na=False)
        | df["email"].str.lower().str.contains(q, na=False)
    )
    df = df[mask]

if risk_fil != "All":
    df = df[df["risk_level"] == risk_fil]

sort_map = {
    "Churn % (↓)": ("churn_probability", False),
    "Churn % (↑)": ("churn_probability", True),
    "Name (A-Z)":  ("name", True),
    "Tenure (↓)":  ("tenure", False),
}
scol, sasc = sort_map[sort_by]
df = df.sort_values(scol, ascending=sasc).reset_index(drop=True)

# ── Summary stats ─────────────────────────────────────────────────────────────

total_shown = len(df)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Shown", total_shown)
c2.metric("High Risk",   int((df["risk_level"] == "High").sum()))
c3.metric("Medium Risk", int((df["risk_level"] == "Medium").sum()))
c4.metric("Low Risk",    int((df["risk_level"] == "Low").sum()))

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Table ─────────────────────────────────────────────────────────────────────

st.markdown('<div class="card" style="padding:0;overflow:hidden">', unsafe_allow_html=True)

# Header
st.markdown("""
<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr;gap:8px;
            padding:12px 20px;background:rgba(99,102,241,0.1);
            border-bottom:1px solid rgba(255,255,255,0.06)">
  <div style="font-size:.72rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Customer</div>
  <div style="font-size:.72rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Risk</div>
  <div style="font-size:.72rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Churn %</div>
  <div style="font-size:.72rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Contract</div>
  <div style="font-size:.72rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Monthly</div>
  <div style="font-size:.72rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.06em">Tenure</div>
</div>
""", unsafe_allow_html=True)

RISK_COLORS = {"High": "#fca5a5", "Medium": "#fcd34d", "Low": "#6ee7b7"}

rows_html = ""
for _, row in df.iterrows():
    risk  = row["risk_level"]
    color = RISK_COLORS[risk]
    rows_html += f"""
    <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr 1fr;gap:8px;
                padding:12px 20px;border-bottom:1px solid rgba(255,255,255,0.04);
                transition:background .15s ease" 
         onmouseover="this.style.background='rgba(99,102,241,0.05)'"
         onmouseout="this.style.background='transparent'">
      <div>
        <div style="font-weight:600;font-size:.88rem;color:#e2e8f0">{row['name']}</div>
        <div style="font-size:.75rem;color:#64748b">{row['customer_id']} &nbsp;·&nbsp; {row['email']}</div>
      </div>
      <div style="align-self:center"><span class="badge badge-{risk.lower()}">{risk}</span></div>
      <div style="align-self:center;font-size:.95rem;font-weight:700;color:{color}">{row['churn_probability']*100:.1f}%</div>
      <div style="align-self:center;font-size:.85rem;color:#94a3b8">{row['contract']}</div>
      <div style="align-self:center;font-size:.85rem;color:#94a3b8">${row['monthly_charges']:.2f}</div>
      <div style="align-self:center;font-size:.85rem;color:#94a3b8">{row['tenure']} mo</div>
    </div>
    """

st.markdown(rows_html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center;padding:12px;font-size:.8rem;color:#64748b'>"
            f"Showing {total_shown} of {len(MOCK_CUSTOMERS)} customers</div>",
            unsafe_allow_html=True)

# ── Customer Detail Expander ───────────────────────────────────────────────────

st.markdown("---")
st.markdown("### 🔍 Inspect a Customer")
cust_ids = ["— pick one —"] + df["customer_id"].tolist()
sel_id   = st.selectbox("Select Customer ID", cust_ids)

if sel_id != "— pick one —":
    cust = next((c for c in MOCK_CUSTOMERS if c["customer_id"] == sel_id), None)
    if cust:
        result = score_customer(cust)
        RISK_COLOR = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}
        rc = RISK_COLOR[result.risk_level]

        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"""
            <div class="card">
              <div style="font-size:1.3rem;font-weight:800;color:#e2e8f0;margin-bottom:4px">{cust['name']}</div>
              <div style="font-size:.82rem;color:#64748b;margin-bottom:16px">{cust['customer_id']} · {cust['email']}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                <div><div style="font-size:.72rem;color:#64748b;text-transform:uppercase">Age</div>
                     <div style="color:#e2e8f0;font-weight:500">{cust['age']}</div></div>
                <div><div style="font-size:.72rem;color:#64748b;text-transform:uppercase">Gender</div>
                     <div style="color:#e2e8f0;font-weight:500">{cust['gender']}</div></div>
                <div><div style="font-size:.72rem;color:#64748b;text-transform:uppercase">Contract</div>
                     <div style="color:#e2e8f0;font-weight:500">{cust['contract']}</div></div>
                <div><div style="font-size:.72rem;color:#64748b;text-transform:uppercase">Tenure</div>
                     <div style="color:#e2e8f0;font-weight:500">{cust['tenure']} months</div></div>
                <div><div style="font-size:.72rem;color:#64748b;text-transform:uppercase">Monthly Charges</div>
                     <div style="color:#e2e8f0;font-weight:500">${cust['monthly_charges']:.2f}</div></div>
                <div><div style="font-size:.72rem;color:#64748b;text-transform:uppercase">Internet</div>
                     <div style="color:#e2e8f0;font-weight:500">{cust['internet_service']}</div></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with d2:
            st.markdown(f"""
            <div class="card result-{result.risk_level.lower()}" style="text-align:center">
              <div style="font-size:.8rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">Churn Probability</div>
              <div style="font-size:3.5rem;font-weight:900;color:{rc}">{result.probability*100:.1f}%</div>
              <div style="margin:10px 0"><span class="badge badge-{result.risk_level.lower()}">{result.risk_level} Risk</span></div>
            </div>
            """, unsafe_allow_html=True)
            if result.recommendations:
                st.markdown("**Top Recommendations**")
                for rec in result.recommendations[:3]:
                    st.markdown(f"""
                    <div style="background:rgba(99,102,241,.07);border:1px solid rgba(99,102,241,.2);
                                border-radius:8px;padding:10px;margin-bottom:6px">
                      <div style="font-size:.85rem;font-weight:600;color:#a5b4fc">{rec.title}</div>
                      <div style="font-size:.77rem;color:#94a3b8;margin-top:3px">{rec.description}</div>
                    </div>
                    """, unsafe_allow_html=True)
