"""Payments and transfers endpoints."""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from backend.auth.decorators import login_required
from backend.database.db import get_session
from backend.integrations.payments_client import PaymentGateway, PaymentIntegrationError
from backend.models.account import Account
from backend.models.payment import Payment

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


def _serialize_payment(payment: Payment, accounts: Dict[int, Account] | None = None) -> Dict[str, Any]:
    account_lookup = accounts or {}
    source = account_lookup.get(payment.from_account_id) or payment.from_account
    destination = account_lookup.get(payment.to_account_id) if payment.to_account_id else None
    return {
        "id": payment.id,
        "type": payment.type,
        "status": payment.status,
        "amount": payment.amount,
        "currency": payment.currency,
        "from_account_id": payment.from_account_id,
        "from_account_name": source.name if source else None,
        "to_account_id": payment.to_account_id,
        "to_account_name": destination.name if destination else payment.payee_name,
        "payee_name": payment.payee_name,
        "confirmation_code": payment.confirmation_code,
        "note": payment.note,
        "provider": payment.provider,
        "message": payment.error_message,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
    }


class PaymentsService:
    """Handle transfers, bill payments, and history lookups."""

    def __init__(self, gateway: PaymentGateway) -> None:
        self.gateway = gateway

    def _load_account(self, session, user_id: int, account_id: int) -> Account:
        account = session.scalar(select(Account).where(Account.user_id == user_id, Account.id == account_id))
        if account is None:
            raise ValueError("Account not found")
        return account

    def transfer(self, user_id: int, from_account_id: int, to_account_id: int, amount: float, note: str | None) -> Payment:
        if from_account_id == to_account_id:
            raise ValueError("Source and destination accounts must differ")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        with get_session() as session:
            source = self._load_account(session, user_id, from_account_id)
            destination = self._load_account(session, user_id, to_account_id)
            try:
                receipt = self.gateway.initiate_transfer(
                    amount=amount,
                    currency=source.currency,
                    source_account_name=source.name or source.institution_name or "Source",
                    destination_account_name=destination.name or destination.institution_name or "Destination",
                    note=note,
                )
            except PaymentIntegrationError as exc:
                payment = Payment(
                    user_id=user_id,
                    from_account_id=source.id,
                    to_account_id=destination.id,
                    amount=amount,
                    currency=source.currency,
                    type="transfer",
                    status="failed",
                    error_message=str(exc),
                    note=note,
                )
                session.add(payment)
                session.commit()
                session.refresh(payment)
                return payment

            payment = Payment(
                user_id=user_id,
                from_account_id=source.id,
                to_account_id=destination.id,
                amount=amount,
                currency=source.currency,
                type="transfer",
                status=receipt.get("status", "completed"),
                confirmation_code=receipt.get("reference"),
                provider=receipt.get("provider"),
                note=receipt.get("note") or note,
                completed_at=receipt.get("completed_at"),
            )
            session.add(payment)
            session.commit()
            session.refresh(payment)
            return payment

    def pay_bill(
        self,
        user_id: int,
        from_account_id: int,
        payee_name: str,
        amount: float,
        note: str | None,
        payee_account: str | None = None,
    ) -> Payment:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        normalized_payee = payee_name.strip()
        if not normalized_payee:
            raise ValueError("Payee name is required")

        with get_session() as session:
            source = self._load_account(session, user_id, from_account_id)
            try:
                receipt = self.gateway.pay_bill(
                    amount=amount,
                    currency=source.currency,
                    source_account_name=source.name or source.institution_name or "Source",
                    payee_name=normalized_payee,
                    payee_account=payee_account,
                    note=note,
                )
            except PaymentIntegrationError as exc:
                payment = Payment(
                    user_id=user_id,
                    from_account_id=source.id,
                    amount=amount,
                    currency=source.currency,
                    type="bill",
                    status="failed",
                    error_message=str(exc),
                    note=note,
                    payee_name=normalized_payee,
                    payee_account=payee_account,
                )
                session.add(payment)
                session.commit()
                session.refresh(payment)
                return payment

            payment = Payment(
                user_id=user_id,
                from_account_id=source.id,
                amount=amount,
                currency=source.currency,
                type="bill",
                status=receipt.get("status", "completed"),
                confirmation_code=receipt.get("reference"),
                provider=receipt.get("provider"),
                note=receipt.get("note") or note,
                completed_at=receipt.get("completed_at"),
                payee_name=normalized_payee,
                payee_account=payee_account or receipt.get("payee_account"),
            )
            session.add(payment)
            session.commit()
            session.refresh(payment)
            return payment

    def history(self, user_id: int) -> List[Payment]:
        with get_session() as session:
            payments = session.scalars(
                select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
            ).all()
            account_ids = {
                p.from_account_id
                for p in payments
                if p.from_account_id is not None
            } | {p.to_account_id for p in payments if p.to_account_id is not None}
            accounts = {acct.id: acct for acct in session.scalars(select(Account).where(Account.id.in_(account_ids))).all()}
            return [_serialize_payment(payment, accounts) for payment in payments]


service: PaymentsService | None = None


def init_payments_blueprint() -> Blueprint:
    global service
    service = PaymentsService(PaymentGateway())
    return payments_bp


@payments_bp.route("/transfer", methods=["POST"])
@login_required
def create_transfer():
    from flask import g

    payload = request.get_json(force=True)
    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")
    amount = payload.get("amount")
    note = payload.get("note")

    if from_account_id is None or to_account_id is None or amount is None:
        return jsonify({"error": "from_account_id, to_account_id, and amount are required"}), 400

    try:
        amt_value = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be numeric"}), 400

    try:
        payment = service.transfer(int(g.current_user.id), int(from_account_id), int(to_account_id), amt_value, note)
        response = _serialize_payment(payment)
        status_code = 200 if payment.status != "failed" else 502
        response["message"] = response.get("message") or "Transfer processed"
        return jsonify({"payment": response}), status_code
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "Unable to process transfer"}), 500


@payments_bp.route("/billpay", methods=["POST"])
@login_required
def create_bill_payment():
    from flask import g

    payload = request.get_json(force=True)
    from_account_id = payload.get("from_account_id")
    payee_name = payload.get("payee_name")
    amount = payload.get("amount")
    payee_account = payload.get("payee_account")
    note = payload.get("note")

    if from_account_id is None or payee_name is None or amount is None:
        return jsonify({"error": "from_account_id, payee_name, and amount are required"}), 400

    try:
        amt_value = float(amount)
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be numeric"}), 400

    try:
        payment = service.pay_bill(
            int(g.current_user.id), int(from_account_id), payee_name, amt_value, note, payee_account=payee_account
        )
        response = _serialize_payment(payment)
        status_code = 200 if payment.status != "failed" else 502
        response["message"] = response.get("message") or "Bill payment processed"
        return jsonify({"payment": response}), status_code
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "Unable to process bill payment"}), 500


@payments_bp.route("/history", methods=["GET"])
@login_required
def payment_history():
    from flask import g

    try:
        payments = service.history(int(g.current_user.id))
        return jsonify({"payments": payments})
    except Exception:
        return jsonify({"error": "Failed to load payment history"}), 500
