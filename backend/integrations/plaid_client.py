"""Plaid integration client for BankConnect."""
from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

import requests

from backend.config import PlaidSettings


class PlaidIntegrationError(Exception):
    """Base exception for Plaid integration errors."""


class PlaidClient:
    def __init__(self, settings: PlaidSettings) -> None:
        self.settings = settings
        self.base_url = self._get_base_url(settings.environment)

    @staticmethod
    def _get_base_url(environment: str) -> str:
        env_map = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com",
        }
        if environment not in env_map:
            raise PlaidIntegrationError(f"Unsupported Plaid environment: {environment}")
        return env_map[environment]

    def create_link_token(self, user_id: str) -> str:
        payload = {
            "client_id": self.settings.client_id,
            "secret": self.settings.secret,
            "user": {"client_user_id": user_id},
            "client_name": "BankConnect",
            "products": ["transactions"],
            "language": "en",
            "country_codes": ["US"],
        }
        if self.settings.redirect_uri:
            payload["redirect_uri"] = self.settings.redirect_uri
        response = self._post("/link/token/create", payload)
        link_token = response.get("link_token")
        if not link_token:
            raise PlaidIntegrationError("Failed to receive link token from Plaid")
        return link_token

    def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        payload = {
            "client_id": self.settings.client_id,
            "secret": self.settings.secret,
            "public_token": public_token,
        }
        response = self._post("/item/public_token/exchange", payload)
        access_token = response.get("access_token")
        item_id = response.get("item_id")
        if not access_token:
            raise PlaidIntegrationError("Failed to exchange public token for access token")
        return {"access_token": access_token, "item_id": item_id}

    def remove_item(self, access_token: str) -> bool:
        payload = {
            "client_id": self.settings.client_id,
            "secret": self.settings.secret,
            "access_token": access_token,
        }
        response = self._post("/item/remove", payload)
        return bool(response.get("removed"))

    def fetch_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        payload = {
            "client_id": self.settings.client_id,
            "secret": self.settings.secret,
            "access_token": access_token,
            "options": {"include_identity": False},
        }
        response = self._post("/accounts/balance/get", payload)
        accounts = response.get("accounts", [])
        if not isinstance(accounts, list):
            raise PlaidIntegrationError("Unexpected response shape for accounts")
        return accounts

    def fetch_transactions(
        self, access_token: str, start_date: dt.date, end_date: Optional[dt.date] = None
    ) -> List[Dict[str, Any]]:
        if end_date is None:
            end_date = dt.date.today()
        payload = {
            "client_id": self.settings.client_id,
            "secret": self.settings.secret,
            "access_token": access_token,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "options": {"count": 100, "offset": 0},
        }
        response = self._post("/transactions/get", payload)
        transactions = response.get("transactions", [])
        if not isinstance(transactions, list):
            raise PlaidIntegrationError("Unexpected response shape for transactions")
        return transactions

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            result = requests.post(url, json=payload, timeout=10)
            result.raise_for_status()
        except requests.RequestException as exc:
            raise PlaidIntegrationError(f"Plaid request failed: {exc}") from exc
        try:
            return result.json()
        except ValueError as exc:
            raise PlaidIntegrationError("Plaid returned a non-JSON response") from exc
