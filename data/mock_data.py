"""
Deterministic mock data — Python port of lib/mock-data.ts.
Uses the same seeded PRNG so numbers are stable across reloads.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone, timedelta
from data.churn_model import score_customer

# ── Seeded PRNG (matches JS seeded() from mock-data.ts) ─────────────────────

class _Seeded:
    def __init__(self, seed: int):
        self._s = seed

    def __call__(self) -> float:
        self._s = (self._s * 16807) % 2_147_483_647
        return (self._s - 1) / 2_147_483_646


_rand = _Seeded(42)


def _pick(items):
    return items[int(math.floor(_rand() * len(items)))]


def _between(lo: float, hi: float) -> float:
    return lo + _rand() * (hi - lo)


# ── Name pools ───────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Olivia", "Liam", "Emma", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "Lucas", "Mia", "Aiden", "Amelia", "James", "Harper",
    "Elijah", "Priya", "Arjun", "Chen", "Yuki", "Fatima", "Omar", "Sofia",
    "Mateo", "Grace", "Daniel", "Zara", "Leo", "Nora", "Samuel",
]
LAST_NAMES = [
    "Johnson", "Patel", "Garcia", "Kim", "Nguyen", "Smith", "Muller", "Rossi",
    "Brown", "Singh", "Martinez", "Lee", "Williams", "Okafor", "Silva",
    "Tanaka", "Davis", "Khan", "Anderson", "Lopez",
]

CONTRACTS     = ["Month-to-month", "Month-to-month", "One year", "Two year"]
INTERNET      = ["Fiber optic", "Fiber optic", "DSL", "No"]
PAYMENTS      = [
    "Electronic check", "Electronic check", "Mailed check",
    "Bank transfer (automatic)", "Credit card (automatic)",
]
STATUSES      = ["Completed", "Completed", "Reviewed", "Action taken"]


# ── Customer builder ─────────────────────────────────────────────────────────

def _build_customer(index: int) -> dict:
    first    = _pick(FIRST_NAMES)
    last     = _pick(LAST_NAMES)
    contract = _pick(CONTRACTS)
    tenure   = (
        round(_between(1, 30))  if contract == "Month-to-month" else
        round(_between(12, 55)) if contract == "One year"        else
        round(_between(24, 72))
    )
    internet       = _pick(INTERNET)
    phone_service  = _rand() > 0.1
    base           = 70 if internet == "Fiber optic" else 45 if internet == "DSL" else 20
    monthly_charges = round((base + _between(0, 40)) * 100) / 100
    age            = round(_between(19, 78))
    add_on         = lambda: internet != "No" and _rand() > 0.55

    features = {
        "customer_id":       f"CUST-{(1001 + index * 37):05d}",
        "gender":            "Male" if _rand() > 0.5 else "Female",
        "age":               age,
        "senior_citizen":    age >= 65,
        "partner":           _rand() > 0.5,
        "dependents":        _rand() > 0.7,
        "tenure":            tenure,
        "contract":          contract,
        "internet_service":  internet,
        "payment_method":    _pick(PAYMENTS),
        "paperless_billing": _rand() > 0.4,
        "monthly_charges":   monthly_charges,
        "total_charges":     round(monthly_charges * max(tenure, 1) * _between(0.95, 1.02) * 100) / 100,
        "phone_service":     phone_service,
        "multiple_lines":    ("Yes" if _rand() > 0.5 else "No") if phone_service else "No phone service",
        "online_security":   add_on(),
        "online_backup":     add_on(),
        "device_protection": add_on(),
        "tech_support":      add_on(),
        "streaming_tv":      add_on(),
        "streaming_movies":  add_on(),
    }

    result = score_customer(features)
    return {
        **features,
        "name":              f"{first} {last}",
        "email":             f"{first.lower()}.{last.lower()}@example.com",
        "churn_probability": result.probability,
        "risk_level":        result.risk_level,
    }


# ── Generate mock datasets ───────────────────────────────────────────────────

MOCK_CUSTOMERS: list[dict] = [_build_customer(i) for i in range(64)]

_REFERENCE_DATE = datetime(2026, 10, 2, tzinfo=timezone.utc)

MOCK_HISTORY: list[dict] = sorted(
    [
        {
            "id":              f"PRED-{5200 - i}",
            "customer_id":     c["customer_id"],
            "customer_name":   c["name"],
            "date":            (_REFERENCE_DATE - timedelta(days=round(i * 0.9 + _rand() * 2))).isoformat(),
            "probability":     c["churn_probability"],
            "risk_level":      c["risk_level"],
            "contract":        c["contract"],
            "monthly_charges": c["monthly_charges"],
            "status":          _pick(STATUSES),
        }
        for i, c in enumerate(MOCK_CUSTOMERS[:48])
    ],
    key=lambda r: r["date"],
    reverse=True,
)

MOCK_SUMMARY = {
    "total_customers":    7043,
    "customer_growth":    0.082,
    "churn_rate":         0.265,
    "high_risk_customers":1245,
    "avg_monthly_charges":64.76,
    "retained":           5174,
    "churned":            1869,
    "risk":               {"Low": 4532, "Medium": 1266, "High": 1245},
}


def _build_trend(labels: list[str], scale: int, seed: int) -> list[dict]:
    r = _Seeded(seed)
    result = []
    for i, label in enumerate(labels):
        wave     = math.sin(i / 2) * 0.08
        retained = round(scale * (1 + wave + i * 0.006 + r() * 0.04))
        churned  = round(retained * (0.36 - i * (0.08 / len(labels)) + r() * 0.05))
        result.append({"label": label, "retained": retained, "churned": churned})
    return result


DAYS   = ["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]
MONTHS = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]

MOCK_TREND = {
    "7d":  _build_trend(DAYS, 40, 7),
    "30d": _build_trend([f"Sep {((i + 1) % 30) + 1}" for i in range(30)], 38, 30),
    "3m":  _build_trend([f"W{i+1}" for i in range(13)], 260, 90),
    "1y":  _build_trend(MONTHS, 1100, 365),
}

MOCK_ANALYTICS = {
    "by_contract": [
        {"segment": "Month-to-month", "churn_rate": 0.427, "customers": 3875},
        {"segment": "One year",       "churn_rate": 0.113, "customers": 1473},
        {"segment": "Two year",       "churn_rate": 0.028, "customers": 1695},
    ],
    "by_tenure": [
        {"segment": "0–12 mo",  "churn_rate": 0.474, "customers": 2186},
        {"segment": "13–24 mo", "churn_rate": 0.287, "customers": 1024},
        {"segment": "25–36 mo", "churn_rate": 0.216, "customers":  832},
        {"segment": "37–48 mo", "churn_rate": 0.190, "customers":  762},
        {"segment": "49–60 mo", "churn_rate": 0.144, "customers":  832},
        {"segment": "61–72 mo", "churn_rate": 0.066, "customers": 1407},
    ],
    "by_payment": [
        {"segment": "Electronic check", "churn_rate": 0.453, "customers": 2365},
        {"segment": "Mailed check",     "churn_rate": 0.191, "customers": 1612},
        {"segment": "Bank transfer",    "churn_rate": 0.167, "customers": 1544},
        {"segment": "Credit card",      "churn_rate": 0.152, "customers": 1522},
    ],
    "by_monthly_charges": [
        {"segment": "$18–30",  "churn_rate": 0.098, "customers": 1653},
        {"segment": "$30–50",  "churn_rate": 0.183, "customers":  712},
        {"segment": "$50–70",  "churn_rate": 0.247, "customers": 1167},
        {"segment": "$70–90",  "churn_rate": 0.353, "customers": 1695},
        {"segment": "$90–120", "churn_rate": 0.331, "customers": 1816},
    ],
    "by_internet": [
        {"segment": "Fiber optic", "churn_rate": 0.419, "customers": 3096},
        {"segment": "DSL",         "churn_rate": 0.190, "customers": 2421},
        {"segment": "No internet", "churn_rate": 0.074, "customers": 1526},
    ],
}
