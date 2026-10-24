# ChurnGuard AI — Streamlit Edition

A full-featured customer churn prediction dashboard rebuilt in Python/Streamlit,
faithfully ported from the original Next.js app.

## Pages

| Page | Description |
|------|-------------|
| 🏠 Dashboard | KPI cards, churn trend chart, donut chart, risk overview |
| 🔮 Predict Churn | Customer form → gauge + risk factors + recommendations |
| 👥 Customers | Searchable/filterable customer table with inline detail |
| 📋 Prediction History | Full history log with status badges |
| 📈 Analytics | 5 segment churn-rate bar charts |

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a GitHub repo
2. Go to https://share.streamlit.io → **New app**
3. Point to `app.py` and deploy — done!

## Connect a FastAPI backend

Set `NEXT_PUBLIC_API_URL` (or add a `BACKEND_URL` env var and wire it into
`data/churn_model.py`) to switch from mock data to live predictions.
