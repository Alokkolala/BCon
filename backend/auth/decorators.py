"""Authentication decorators for protecting routes."""
from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import Response, jsonify, g, request

from backend.auth.jwt import JWTManager
from backend.database.db import get_session
from backend.models.user import User

F = TypeVar("F", bound=Callable)

jwt_manager: JWTManager | None = None


def configure_jwt_manager(manager: JWTManager) -> None:
    global jwt_manager
    jwt_manager = manager


def login_required(fn: F) -> F:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if jwt_manager is None:
            return jsonify({"error": "Authentication not configured"}), 500
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        if not token:
            return jsonify({"error": "Unauthorized"}), 401
        payload = jwt_manager.decode_token(token)
        if not payload:
            return jsonify({"error": "Unauthorized"}), 401
        user_id = payload.get("sub")
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
        with get_session() as session:
            user = session.get(User, int(user_id))
            if user is None:
                return jsonify({"error": "Unauthorized"}), 401
            g.current_user = user
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def current_user() -> User | None:
    return getattr(g, "current_user", None)
