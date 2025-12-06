"""Encryption helpers for sensitive secrets stored in the database."""
from __future__ import annotations

import base64
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


class CryptoManager:
    """Wrapper around Fernet encryption for symmetric encryption."""

    def __init__(self, key: str) -> None:
        self._key = self._normalize_key(key)
        self._cipher = Fernet(self._key)

    @staticmethod
    def _normalize_key(key: str) -> bytes:
        """Normalize a human-friendly string into a Fernet-compatible key."""
        if not key:
            raise ValueError("Encryption key is required")
        try:
            decoded = base64.urlsafe_b64decode(key)
            if len(decoded) == 32:
                return base64.urlsafe_b64encode(decoded)
        except Exception:
            pass
        padded = key.encode("utf-8")
        padded = (padded * (32 // len(padded) + 1))[:32]
        return base64.urlsafe_b64encode(padded)

    def encrypt(self, value: str) -> str:
        token = self._cipher.encrypt(value.encode("utf-8"))
        return token.decode("utf-8")

    def decrypt(self, token: str) -> Optional[str]:
        try:
            return self._cipher.decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            return None
        except Exception:
            return None


def get_crypto_manager(encryption_key: str) -> CryptoManager:
    return CryptoManager(encryption_key)
