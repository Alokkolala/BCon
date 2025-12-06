"""Flask blueprint providing Plaid account aggregation endpoints."""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request
from sqlalchemy import delete, select

from backend.auth.decorators import login_required
from backend.config import Settings
from backend.database.db import get_session
from backend.integrations.plaid_client import PlaidClient, PlaidIntegrationError
from backend.models.account import Account
from backend.models.transaction import Transaction
from backend.models.user import User
from backend.utils.crypto import CryptoManager

plaid_bp = Blueprint("plaid", __name__, url_prefix="/plaid")


def _serialize_account(account: Account) -> Dict[str, Any]:
    return {
        "id": account.id,
        "plaid_account_id": account.plaid_account_id,
        "institution_name": account.institution_name,
        "name": account.name,
        "mask": account.mask,
        "subtype": account.subtype,
        "balance": {
            "available": account.balance_available,
            "current": account.balance_current,
            "currency": account.currency,
        },
    }


def _serialize_transaction(tx: Transaction) -> Dict[str, Any]:
    return {
        "id": tx.id,
        "account_id": tx.account_id,
        "amount": tx.amount,
        "currency": tx.currency,
        "date": tx.date.isoformat(),
        "category": tx.category,
        "merchant_name": tx.merchant_name,
        "description": tx.description,
    }


class PlaidService:
    """Service wrapper combining Plaid client calls with persistence."""

    def __init__(self, plaid_client: PlaidClient, crypto: CryptoManager) -> None:
        self.plaid_client = plaid_client
        self.crypto = crypto

    def create_link_token(self, user_id: int) -> str:
        return self.plaid_client.create_link_token(str(user_id))

    def exchange_and_store(self, user_id: int, public_token: str) -> List[Account]:
        token_data = self.plaid_client.exchange_public_token(public_token)
        access_token = token_data["access_token"]
        encrypted_token = self.crypto.encrypt(access_token)

        accounts_data = self.plaid_client.fetch_accounts(access_token)
        transactions_data = self.plaid_client.fetch_transactions(
            access_token, start_date=dt.date.today() - dt.timedelta(days=30)
        )

        with get_session() as session:
            user = session.get(User, user_id)
            if not user:
                raise RuntimeError("User not found")
            accounts = []
            for account_payload in accounts_data:
                plaid_account_id = account_payload.get("account_id")
                account = session.scalar(
                    select(Account).where(
                        Account.user_id == user.id, Account.plaid_account_id == plaid_account_id
                    )
                )
                if account is None:
                    account = Account(user_id=user.id, plaid_account_id=plaid_account_id, encrypted_access_token="")
                    session.add(account)
                account.institution_name = (account_payload.get("official_name")
                                             or account_payload.get("name"))
                account.name = account_payload.get("name")
                account.mask = account_payload.get("mask")
                account.subtype = account_payload.get("subtype")
                balances = account_payload.get("balances", {})
                account.balance_available = balances.get("available")
                account.balance_current = balances.get("current")
                account.currency = balances.get("iso_currency_code") or balances.get("unofficial_currency_code")
                account.encrypted_access_token = encrypted_token
                accounts.append(account)
                session.flush()

            # Refresh transactions
            session.execute(delete(Transaction).where(Transaction.account_id.in_([acct.id for acct in accounts])))
            for tx_payload in transactions_data:
                plaid_account_id = tx_payload.get("account_id")
                account_for_tx = next((acct for acct in accounts if acct.plaid_account_id == plaid_account_id), None)
                if not account_for_tx:
                    continue
                pf_category = tx_payload.get("personal_finance_category", {}) or {}
                category = pf_category.get("primary") or pf_category.get("detailed")
                if not category:
                    categories = tx_payload.get("category") or []
                    category = categories[0] if categories else None
                transaction = Transaction(
                    account_id=account_for_tx.id,
                    amount=tx_payload.get("amount", 0.0),
                    currency=tx_payload.get("iso_currency_code") or tx_payload.get("unofficial_currency_code"),
                    date=dt.date.fromisoformat(tx_payload.get("date")),
                    category=category,
                    merchant_name=tx_payload.get("merchant_name"),
                    description=tx_payload.get("name"),
                )
                session.add(transaction)
            session.commit()
            return accounts

    def unlink_account(self, user_id: int, plaid_account_id: str) -> bool:
        with get_session() as session:
            account = session.scalar(
                select(Account).where(Account.user_id == user_id, Account.plaid_account_id == plaid_account_id)
            )
            if account is None:
                return False
            access_token = self.crypto.decrypt(account.encrypted_access_token)
            if access_token:
                try:
                    self.plaid_client.remove_item(access_token)
                except PlaidIntegrationError:
                    pass
            session.execute(delete(Transaction).where(Transaction.account_id == account.id))
            session.delete(account)
            session.commit()
            return True

    def list_accounts(self, user_id: int) -> List[Dict[str, Any]]:
        with get_session() as session:
            accounts = session.scalars(select(Account).where(Account.user_id == user_id)).all()
            return [_serialize_account(account) for account in accounts]

    def list_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        with get_session() as session:
            transactions = (
                session.scalars(
                    select(Transaction)
                    .join(Account, Transaction.account_id == Account.id)
                    .where(Account.user_id == user_id)
                ).all()
            )
            return [_serialize_transaction(tx) for tx in transactions]


service: PlaidService | None = None


def init_plaid_blueprint(settings: Settings) -> Blueprint:
    global service
    plaid_client = PlaidClient(settings.plaid)
    crypto = CryptoManager(settings.encryption_key)
    service = PlaidService(plaid_client, crypto)
    return plaid_bp


@plaid_bp.route("/link-token", methods=["POST"])
@login_required
def link_token():
    from flask import g

    try:
        token = service.create_link_token(int(g.current_user.id))
        return jsonify({"link_token": token})
    except PlaidIntegrationError as exc:
        return jsonify({"error": str(exc)}), 502


@plaid_bp.route("/exchange", methods=["POST"])
@login_required
def exchange_public_token():
    from flask import g

    payload = request.get_json(force=True)
    public_token = payload.get("public_token")
    if not public_token:
        return jsonify({"error": "public_token is required"}), 400
    try:
        accounts = service.exchange_and_store(int(g.current_user.id), public_token)
        return jsonify({"accounts": [_serialize_account(account) for account in accounts]})
    except PlaidIntegrationError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception:
        return jsonify({"error": "Failed to store account data"}), 500


@plaid_bp.route("/unlink", methods=["POST"])
@login_required
def unlink_account():
    from flask import g

    payload = request.get_json(force=True)
    plaid_account_id = payload.get("plaid_account_id")
    if not plaid_account_id:
        return jsonify({"error": "plaid_account_id is required"}), 400
    removed = service.unlink_account(int(g.current_user.id), plaid_account_id)
    if not removed:
        return jsonify({"error": "Account not found"}), 404
    return jsonify({"removed": True})


@plaid_bp.route("/accounts", methods=["GET"])
@login_required
def list_accounts():
    from flask import g

    try:
        accounts = service.list_accounts(int(g.current_user.id))
        return jsonify({"accounts": accounts})
    except Exception:
        return jsonify({"error": "Failed to retrieve accounts"}), 500


@plaid_bp.route("/transactions", methods=["GET"])
@login_required
def list_transactions():
    from flask import g

    try:
        transactions = service.list_transactions(int(g.current_user.id))
        return jsonify({"transactions": transactions})
    except Exception:
        return jsonify({"error": "Failed to retrieve transactions"}), 500
