"""Payments/transfer integration stub for BankConnect."""
from __future__ import annotations

import datetime as dt
import uuid
from typing import Any, Dict


class PaymentIntegrationError(Exception):
    """Raised when a payment provider returns an error."""


class PaymentGateway:
    """Facade for interacting with external money-movement providers."""

    def __init__(self, provider: str = "plaid") -> None:
        self.provider = provider

    def initiate_transfer(
        self,
        *,
        amount: float,
        currency: str | None,
        source_account_name: str,
        destination_account_name: str,
        note: str | None = None,
    ) -> Dict[str, Any]:
        self._validate_amount(amount)
        reference = f"TRX-{uuid.uuid4().hex[:10].upper()}"
        return {
            "status": "completed",
            "reference": reference,
            "provider": self.provider,
            "message": f"Transfer from {source_account_name} to {destination_account_name} executed",
            "completed_at": dt.datetime.utcnow(),
            "note": note,
        }

    def pay_bill(
        self,
        *,
        amount: float,
        currency: str | None,
        source_account_name: str,
        payee_name: str,
        payee_account: str | None = None,
        note: str | None = None,
    ) -> Dict[str, Any]:
        self._validate_amount(amount)
        reference = f"BILL-{uuid.uuid4().hex[:10].upper()}"
        return {
            "status": "completed",
            "reference": reference,
            "provider": self.provider,
            "message": f"Payment to {payee_name} scheduled",
            "completed_at": dt.datetime.utcnow(),
            "note": note,
            "payee_account": payee_account,
        }

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if amount <= 0:
            raise PaymentIntegrationError("Amount must be positive")
