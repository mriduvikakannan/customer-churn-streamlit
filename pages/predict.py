"""Predict Churn page — customer feature form + result panel."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
from data.churn_model import score_customer

COLORS = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}
BG     = {"High": "rgba(239,68,68,.08)", "Medium": "rgba(245,158,11,.08)", "Low": "rgba(16,185,129,.08)"}
BORDER = {"High": "rgba(239,68,68,.35)", "Medium": "rgba(245,158,11,.35)", "Low": "rgba(16,185,129,.35)"}

# ── Page header ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="page-header">
  <div class="page-title">Predict Customer Churn</div>
  <div class="page-desc">Run the churn model on a single customer profile and get actionable retention guidance.</div>
</div>
""", unsafe_allow_html=True)

col_form, col_result = st.columns([1, 1], gap="large")

with col_form:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧾 Customer Profile")

    with st.form("predict_form"):
        # ── Identity ──────────────────────────────────────────────────────────
        st.markdown("**Identity**")
        fc1, fc2 = st.columns(2)
        customer_id = fc1.text_input("Customer ID", value="CUST-99001")
        gender      = fc2.selectbox("Gender", ["Male", "Female"])

        fc3, fc4, fc5 = st.columns(3)
        age            = fc3.number_input("Age", 18, 100, 42)
        partner        = fc4.toggle("Has partner", value=True)
        dependents     = fc5.toggle("Has dependents", value=False)
        senior_citizen = age >= 65

        st.divider()

        # ── Plan ──────────────────────────────────────────────────────────────
        st.markdown("**Plan & Billing**")
        fp1, fp2 = st.columns(2)
        contract    = fp1.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        payment_method = fp2.selectbox("Payment Method", [
            "Electronic check", "Mailed check",
            "Bank transfer (automatic)", "Credit card (automatic)",
        ])

        fp3, fp4, fp5 = st.columns(3)
        tenure          = fp3.number_input("Tenure (months)", 0, 120, 14)
        monthly_charges = fp4.number_input("Monthly Charges ($)", 0.0, 200.0, 79.50, step=0.5)
        total_charges   = fp5.number_input("Total Charges ($)", 0.0, 10000.0,
                                           round(monthly_charges * max(tenure, 1), 2), step=1.0)
        paperless_billing = st.toggle("Paperless billing", value=True)

        st.divider()

        # ── Services ──────────────────────────────────────────────────────────
        st.markdown("**Services**")
        phone_service = st.toggle("Phone service", value=True)
        if phone_service:
            multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes"])
        else:
            multiple_lines = "No phone service"

        internet_service = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])

        if internet_service != "No":
            s1, s2, s3 = st.columns(3)
            online_security  = s1.toggle("Online Security")
            online_backup    = s2.toggle("Online Backup")
            device_protection= s3.toggle("Device Protection")
            t1, t2, t3 = st.columns(3)
            tech_support      = t1.toggle("Tech Support")
            streaming_tv      = t2.toggle("Streaming TV")
            streaming_movies  = t3.toggle("Streaming Movies")
        else:
            online_security = online_backup = device_protection = False
            tech_support = streaming_tv = streaming_movies = False

        submitted = st.form_submit_button("🔮  Run Prediction", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── Result Panel ──────────────────────────────────────────────────────────────

with col_result:
    if not submitted:
        st.markdown("""
        <div class="card" style="height:100%;display:flex;flex-direction:column;
             align-items:center;justify-content:center;text-align:center;min-height:400px">
          <div style="font-size:4rem;margin-bottom:16px">🔮</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;margin-bottom:8px">
            Ready to predict
          </div>
          <div style="font-size:.9rem;color:#64748b;max-width:280px">
            Fill in the customer profile and click <strong>Run Prediction</strong> to see
            the churn probability and retention recommendations.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        customer = {
            "customer_id":       customer_id,
            "gender":            gender,
            "age":               age,
            "senior_citizen":    senior_citizen,
            "partner":           partner,
            "dependents":        dependents,
            "tenure":            tenure,
            "contract":          contract,
            "internet_service":  internet_service,
            "payment_method":    payment_method,
            "paperless_billing": paperless_billing,
            "monthly_charges":   monthly_charges,
            "total_charges":     total_charges,
            "phone_service":     phone_service,
            "multiple_lines":    multiple_lines,
            "online_security":   online_security,
            "online_backup":     online_backup,
            "device_protection": device_protection,
            "tech_support":      tech_support,
            "streaming_tv":      streaming_tv,
            "streaming_movies":  streaming_movies,
        }

        with st.spinner("Scoring customer…"):
            result = score_customer(customer)

        risk  = result.risk_level
        prob  = result.probability
        color = COLORS[risk]

        # ── Gauge ─────────────────────────────────────────────────────────────
        st.markdown(f"""
        <div class="card result-{risk.lower()}" style="text-align:center;margin-bottom:16px">
          <div style="font-size:.8rem;color:#64748b;text-transform:uppercase;letter-spacing:.08em;
                      margin-bottom:8px">Churn Probability</div>
          <div style="font-size:4rem;font-weight:900;color:{color};line-height:1">
            {prob*100:.1f}%
          </div>
          <div style="margin-top:10px">
            <span class="badge badge-{risk.lower()}">{risk} Risk</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge",
            value=prob * 100,
            gauge=dict(
                axis=dict(range=[0, 100], tickfont=dict(color="#64748b"), tickwidth=1),
                bar=dict(color=color, thickness=0.3),
                bgcolor="rgba(255,255,255,0.04)",
                borderwidth=0,
                steps=[
                    dict(range=[0, 35],  color="rgba(16,185,129,.12)"),
                    dict(range=[35, 65], color="rgba(245,158,11,.12)"),
                    dict(range=[65, 100],color="rgba(239,68,68,.12)"),
                ],
                threshold=dict(line=dict(color=color, width=3), thickness=0.8, value=prob*100),
            ),
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=180, margin=dict(l=20, r=20, t=20, b=0),
            font=dict(family="Inter, sans-serif", color="#94a3b8"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        # ── Risk Factors ───────────────────────────────────────────────────────
        if result.factors:
            st.markdown("**🔴 Risk Factors**")
            for f in result.factors:
                bar_width = min(100, f.impact / 1.5 * 100)
                st.markdown(f"""
                <div style="margin-bottom:10px">
                  <div style="display:flex;justify-content:space-between;font-size:.85rem;margin-bottom:3px">
                    <span style="color:#e2e8f0;font-weight:500">{f.label}</span>
                    <span style="color:#f87171">+{f.impact:.2f}</span>
                  </div>
                  <div style="height:5px;background:rgba(255,255,255,0.06);border-radius:99px">
                    <div style="height:100%;width:{bar_width:.0f}%;background:linear-gradient(90deg,#ef4444,#f87171);
                                border-radius:99px"></div>
                  </div>
                  <div style="font-size:.75rem;color:#64748b;margin-top:2px">{f.description}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Protective Factors ─────────────────────────────────────────────────
        if result.protective_factors:
            st.markdown("**🟢 Protective Factors**")
            for f in result.protective_factors:
                bar_width = min(100, abs(f.impact) / 1.8 * 100)
                st.markdown(f"""
                <div style="margin-bottom:8px">
                  <div style="display:flex;justify-content:space-between;font-size:.85rem;margin-bottom:3px">
                    <span style="color:#e2e8f0;font-weight:500">{f.label}</span>
                    <span style="color:#34d399">{f.impact:.2f}</span>
                  </div>
                  <div style="height:5px;background:rgba(255,255,255,0.06);border-radius:99px">
                    <div style="height:100%;width:{bar_width:.0f}%;background:linear-gradient(90deg,#10b981,#34d399);
                                border-radius:99px"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Recommendations ────────────────────────────────────────────────────
        if result.recommendations:
            st.markdown("**💡 Retention Recommendations**")
            icons = ["📞", "📄", "💰", "🔧", "🛡️"]
            for i, rec in enumerate(result.recommendations):
                st.markdown(f"""
                <div style="background:rgba(99,102,241,.07);border:1px solid rgba(99,102,241,.2);
                            border-radius:10px;padding:12px;margin-bottom:8px">
                  <div style="font-size:.9rem;font-weight:600;color:#a5b4fc;margin-bottom:4px">
                    {icons[i % len(icons)]} {rec.title}
                  </div>
                  <div style="font-size:.8rem;color:#94a3b8">{rec.description}</div>
                </div>
                """, unsafe_allow_html=True)
