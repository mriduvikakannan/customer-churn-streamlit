"""
Rule-weighted logistic scorer — exact Python port of lib/churn-model.ts.
Stands in for a real Gradient Boosting backend until FastAPI is connected.
"""
import math
from dataclasses import dataclass, field
from typing import Optional

RISK_THRESHOLDS = {"medium": 0.35, "high": 0.65}


def get_risk_level(probability: float) -> str:
    if probability >= RISK_THRESHOLDS["high"]:
        return "High"
    if probability >= RISK_THRESHOLDS["medium"]:
        return "Medium"
    return "Low"


@dataclass
class RiskFactor:
    label: str
    description: str
    impact: float


@dataclass
class RetentionAction:
    title: str
    description: str


@dataclass
class PredictionResult:
    customer_id: str
    probability: float
    risk_level: str
    will_churn: bool
    factors: list[RiskFactor]
    protective_factors: list[RiskFactor]
    recommendations: list[RetentionAction]
    model_version: str
    generated_at: str


# ── Risk rules (increase churn probability) ──────────────────────────────────

RULES = [
    {
        "when": lambda c: c["tenure"] < 12,
        "weight": 1.1,
        "label": "Short tenure",
        "description": "Customers in their first year churn far more often.",
        "action": RetentionAction(
            "Strengthen onboarding",
            "Schedule a check-in call and share a personalized getting-started guide.",
        ),
    },
    {
        "when": lambda c: c["contract"] == "Month-to-month",
        "weight": 1.3,
        "label": "Month-to-month contract",
        "description": "No long-term commitment makes it easy to leave at any time.",
        "action": RetentionAction(
            "Offer a long-term contract",
            "Present a discounted one- or two-year plan to encourage commitment.",
        ),
    },
    {
        "when": lambda c: c["monthly_charges"] > 75,
        "weight": 0.7,
        "label": "High monthly charges",
        "description": "Monthly bill is above the typical range for similar customers.",
        "action": RetentionAction(
            "Provide a personalized discount",
            "Consider a loyalty discount or bundle to lower the monthly bill.",
        ),
    },
    {
        "when": lambda c: c["payment_method"] == "Electronic check",
        "weight": 0.6,
        "label": "Electronic check payment",
        "description": "Manual payment methods correlate with higher churn.",
        "action": RetentionAction(
            "Encourage automatic payments",
            "Offer a small credit for switching to automatic card or bank payments.",
        ),
    },
    {
        "when": lambda c: c["internet_service"] == "Fiber optic",
        "weight": 0.5,
        "label": "Fiber optic service",
        "description": "Fiber customers show higher churn, often price- or quality-related.",
        "action": RetentionAction(
            "Review service quality",
            "Proactively check connection quality and resolve any open issues.",
        ),
    },
    {
        "when": lambda c: c["internet_service"] != "No" and not c["tech_support"],
        "weight": 0.45,
        "label": "No tech support",
        "description": "Customers without support access are less likely to resolve problems.",
        "action": RetentionAction(
            "Offer additional support",
            "Provide a complimentary tech support trial for the next 3 months.",
        ),
    },
    {
        "when": lambda c: c["internet_service"] != "No" and not c["online_security"],
        "weight": 0.35,
        "label": "No online security",
        "description": "Fewer add-on services means weaker product attachment.",
        "action": RetentionAction(
            "Provide a suitable service upgrade",
            "Bundle online security or backup at a reduced introductory price.",
        ),
    },
    {
        "when": lambda c: c["senior_citizen"],
        "weight": 0.3,
        "label": "Senior citizen",
        "description": "This segment shows a moderately higher historical churn rate.",
        "action": None,
    },
    {
        "when": lambda c: c["paperless_billing"],
        "weight": 0.2,
        "label": "Paperless billing",
        "description": "Slightly associated with higher churn in historical data.",
        "action": None,
    },
    {
        "when": lambda c: not c["partner"] and not c["dependents"],
        "weight": 0.25,
        "label": "No partner or dependents",
        "description": "Single-person accounts tend to switch providers more easily.",
        "action": None,
    },
]

PROTECTIVE_RULES = [
    {
        "when": lambda c: c["contract"] == "Two year",
        "weight": -1.6,
        "label": "Two-year contract",
        "description": "Long-term commitment strongly reduces churn.",
        "action": None,
    },
    {
        "when": lambda c: c["contract"] == "One year",
        "weight": -0.8,
        "label": "One-year contract",
        "description": "An annual commitment reduces churn risk.",
        "action": None,
    },
    {
        "when": lambda c: c["tenure"] >= 48,
        "weight": -1.0,
        "label": "Long tenure",
        "description": "Loyal customers with 4+ years are unlikely to leave.",
        "action": None,
    },
    {
        "when": lambda c: "automatic" in c["payment_method"].lower(),
        "weight": -0.3,
        "label": "Automatic payments",
        "description": "Automated billing reduces friction and churn.",
        "action": None,
    },
    {
        "when": lambda c: c["tech_support"] and c["online_security"],
        "weight": -0.35,
        "label": "Support & security add-ons",
        "description": "Multiple add-on services increase product attachment.",
        "action": None,
    },
]

INTERCEPT = -2.1


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def score_customer(customer: dict) -> PredictionResult:
    from datetime import datetime, timezone

    risk_rules = [r for r in RULES if r["when"](customer)]
    protective = [r for r in PROTECTIVE_RULES if r["when"](customer)]

    logit = sum(r["weight"] for r in risk_rules + protective) + INTERCEPT
    probability = min(0.98, max(0.02, sigmoid(logit)))
    risk_level = get_risk_level(probability)

    factors = sorted(
        [RiskFactor(r["label"], r["description"], r["weight"]) for r in risk_rules],
        key=lambda f: -f.impact,
    )
    protective_factors = [
        RiskFactor(r["label"], r["description"], r["weight"]) for r in protective
    ]

    recommendations: list[RetentionAction] = [
        r["action"] for r in risk_rules if r["action"] is not None
    ][:5]

    if risk_level != "Low" and not any(
        r.title == "Contact the customer" for r in recommendations
    ):
        recommendations.insert(
            0,
            RetentionAction(
                "Contact the customer",
                "Reach out personally to understand concerns before they decide to leave.",
            ),
        )

    recs = recommendations[:2] if risk_level == "Low" else recommendations[:5]

    return PredictionResult(
        customer_id=customer["customer_id"],
        probability=probability,
        risk_level=risk_level,
        will_churn=probability >= 0.5,
        factors=factors,
        protective_factors=protective_factors,
        recommendations=recs,
        model_version="v1.0.0-demo",
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
