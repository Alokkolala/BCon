"""Budgeting and insights endpoints."""
from __future__ import annotations

import calendar
import datetime as dt
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from backend.auth.decorators import login_required
from backend.database.db import get_session
from backend.models.account import Account
from backend.models.budget import Budget
from backend.models.transaction import Transaction

budget_bp = Blueprint("budget", __name__, url_prefix="/budget")


class BudgetService:
    """Service to manage budgets, spending summaries, and recommendations."""

    def __init__(self) -> None:
        self.today = dt.date.today()

    def _month_bounds(self, date: dt.date | None = None) -> tuple[dt.date, dt.date]:
        target = date or self.today
        start = target.replace(day=1)
        end_day = calendar.monthrange(target.year, target.month)[1]
        end = target.replace(day=end_day)
        return start, end

    def upsert_budget(self, user_id: int, category: str, monthly_limit: float, alert_threshold: float | None) -> Budget:
        normalized_category = category.strip()
        with get_session() as session:
            budget = session.scalar(
                select(Budget).where(
                    Budget.user_id == user_id,
                    Budget.category.ilike(normalized_category),
                )
            )
            if budget is None:
                budget = Budget(
                    user_id=user_id,
                    category=normalized_category,
                    monthly_limit=monthly_limit,
                    alert_threshold=alert_threshold,
                )
                session.add(budget)
            else:
                budget.category = normalized_category
                budget.monthly_limit = monthly_limit
                budget.alert_threshold = alert_threshold
            session.commit()
            session.refresh(budget)
            return budget

    def summarize(self, user_id: int) -> Dict[str, Any]:
        start, end = self._month_bounds()
        with get_session() as session:
            budgets = session.scalars(select(Budget).where(Budget.user_id == user_id)).all()
            transactions = session.scalars(
                select(Transaction)
                .join(Account, Transaction.account_id == Account.id)
                .where(
                    Account.user_id == user_id,
                    Transaction.date >= start,
                    Transaction.date <= end,
                )
            ).all()

        spend_by_category: Dict[str, float] = {}
        for tx in transactions:
            if tx.amount >= 0:
                continue
            category = tx.category or "Uncategorized"
            spend_by_category[category] = spend_by_category.get(category, 0.0) + abs(tx.amount)

        budget_status: List[Dict[str, Any]] = []
        alerts: List[str] = []
        chart: List[Dict[str, Any]] = []

        for budget in budgets:
            spent = spend_by_category.get(budget.category, 0.0)
            threshold = budget.alert_threshold or budget.monthly_limit
            if spent >= threshold:
                alerts.append(
                    f"Spending for {budget.category} is ${spent:,.2f}, exceeding your alert threshold of ${threshold:,.2f}."
                )
            remaining = max(budget.monthly_limit - spent, 0.0)
            budget_status.append(
                {
                    "category": budget.category,
                    "monthly_limit": budget.monthly_limit,
                    "alert_threshold": budget.alert_threshold,
                    "spent": spent,
                    "remaining": remaining,
                }
            )
            chart.append(
                {
                    "category": budget.category,
                    "spent": round(spent, 2),
                    "limit": round(budget.monthly_limit, 2),
                }
            )

        recommendations = self._recommendations(budgets, spend_by_category)
        return {
            "budgets": budget_status,
            "alerts": alerts,
            "recommendations": recommendations,
            "chart": chart,
            "period": {"start": start.isoformat(), "end": end.isoformat()},
        }

    def _recommendations(self, budgets: List[Budget], spend_by_category: Dict[str, float]) -> List[str]:
        if not budgets:
            return ["Create your first spending goals to start receiving personalized tips."]

        suggestions: List[str] = []
        overspent = [b for b in budgets if spend_by_category.get(b.category, 0) >= b.monthly_limit]
        nearing = [
            b
            for b in budgets
            if b not in overspent and spend_by_category.get(b.category, 0) >= 0.8 * b.monthly_limit
        ]

        for budget in overspent:
            spent = spend_by_category.get(budget.category, 0.0)
            suggestions.append(
                f"You exceeded your {budget.category} budget by ${spent - budget.monthly_limit:,.2f}. Review recurring charges and set a smaller discretionary cap next month."
            )

        for budget in nearing:
            spent = spend_by_category.get(budget.category, 0.0)
            suggestions.append(
                f"{budget.category} spending is at ${spent:,.2f} ({spent / budget.monthly_limit:.0%} of your goal). Consider moving discretionary purchases to the next billing cycle."
            )

        if not suggestions:
            lowest = min(budgets, key=lambda b: spend_by_category.get(b.category, 0.0) / max(b.monthly_limit, 1))
            suggestions.append(
                f"Great job staying on track. Try reducing your {lowest.category} budget by 5% to accelerate savings."
            )

        top_category = max(spend_by_category.items(), key=lambda item: item[1], default=(None, 0))
        if top_category[0]:
            suggestions.append(
                f"Largest outlay so far is {top_category[0]} at ${top_category[1]:,.2f}. Set automated alerts to stay under your threshold earlier in the month."
            )

        return suggestions[:4]


service = BudgetService()


def init_budget_blueprint() -> Blueprint:
    return budget_bp


@budget_bp.route("/goals", methods=["POST"])
@login_required
def save_goal():
    from flask import g

    payload = request.get_json(force=True)
    category = payload.get("category")
    monthly_limit = payload.get("monthly_limit")
    alert_threshold = payload.get("alert_threshold")

    if not category or monthly_limit is None:
        return jsonify({"error": "category and monthly_limit are required"}), 400

    try:
        monthly_limit_val = float(monthly_limit)
        alert_val = float(alert_threshold) if alert_threshold is not None else None
    except ValueError:
        return jsonify({"error": "monthly_limit and alert_threshold must be numbers"}), 400

    try:
        budget = service.upsert_budget(int(g.current_user.id), category, monthly_limit_val, alert_val)
        return jsonify({
            "budget": {
                "id": budget.id,
                "category": budget.category,
                "monthly_limit": budget.monthly_limit,
                "alert_threshold": budget.alert_threshold,
            }
        })
    except Exception:
        return jsonify({"error": "Unable to save budget"}), 500


@budget_bp.route("/summary", methods=["GET"])
@login_required
def summary():
    from flask import g

    try:
        data = service.summarize(int(g.current_user.id))
        return jsonify(data)
    except Exception:
        return jsonify({"error": "Failed to build budget summary"}), 500
