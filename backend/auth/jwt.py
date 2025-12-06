"""JWT helpers for issuing and decoding access tokens."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt


class JWTManager:
    def __init__(self, secret: str, algorithm: str = "HS256", exp_minutes: int = 60) -> None:
        self.secret = secret
        self.algorithm = algorithm
        self.exp_minutes = exp_minutes

    def create_access_token(self, user_id: int, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.exp_minutes)).timestamp()),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.InvalidTokenError:
            return None


def get_jwt_manager(secret: str, algorithm: str = "HS256", exp_minutes: int = 60) -> JWTManager:
    return JWTManager(secret=secret, algorithm=algorithm, exp_minutes=exp_minutes)
