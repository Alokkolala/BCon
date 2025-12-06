"""Authentication blueprint for signup, login, OAuth, and profile management."""
from __future__ import annotations

import datetime as dt
import secrets
from typing import Dict, Optional

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from backend.auth.decorators import configure_jwt_manager, login_required
from backend.auth.jwt import JWTManager, get_jwt_manager
from backend.auth.passwords import hash_password, verify_password
from backend.config import Settings
from backend.database.db import get_session
from backend.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

jwt_exp_minutes: int = 60
password_reset_exp_minutes: int = 30
jwt_factory: JWTManager | None = None


def init_auth_blueprint(settings: Settings) -> Blueprint:
    """Initialize the auth blueprint with runtime settings."""
    global jwt_exp_minutes, password_reset_exp_minutes, jwt_factory
    jwt_exp_minutes = settings.jwt_exp_minutes
    password_reset_exp_minutes = settings.password_reset_exp_minutes
    jwt_factory = get_jwt_manager(settings.jwt_secret, settings.jwt_algorithm, settings.jwt_exp_minutes)
    configure_jwt_manager(jwt_factory)
    return auth_bp


def _serialize_user(user: User) -> Dict[str, Optional[str]]:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "provider": user.provider,
    }


def _ensure_jwt_factory() -> JWTManager:
    if jwt_factory is None:
        raise RuntimeError("JWT factory not configured")
    return jwt_factory


@auth_bp.route("/register", methods=["POST"])
def register():
    payload = request.get_json(force=True)
    email = payload.get("email")
    password = payload.get("password")
    full_name = payload.get("full_name")
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    with get_session() as session:
        existing = session.scalar(select(User).where(User.email == email))
        if existing:
            return jsonify({"error": "User already exists"}), 409
        user = User(email=email, full_name=full_name, hashed_password=hash_password(password), provider="local")
        session.add(user)
        session.commit()
        access_token = _ensure_jwt_factory().create_access_token(user.id, user.email)
        return jsonify({"user": _serialize_user(user), "access_token": access_token})


@auth_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json(force=True)
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    with get_session() as session:
        user = session.scalar(select(User).where(User.email == email))
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            return jsonify({"error": "Invalid credentials"}), 401
        access_token = _ensure_jwt_factory().create_access_token(user.id, user.email)
        return jsonify({"user": _serialize_user(user), "access_token": access_token})


@auth_bp.route("/oauth/callback", methods=["POST"])
def oauth_callback():
    payload = request.get_json(force=True)
    provider = payload.get("provider")
    external_id = payload.get("external_id") or payload.get("provider_user_id")
    email = payload.get("email")
    full_name = payload.get("full_name")
    provider_token = payload.get("provider_token")
    if not provider or not external_id or not email:
        return jsonify({"error": "provider, external_id, and email are required"}), 400
    if not provider_token:
        return jsonify({"error": "provider_token is required to validate the OAuth response"}), 400
    with get_session() as session:
        user = session.scalar(select(User).where(User.external_id == external_id, User.provider == provider))
        if not user:
            user = session.scalar(select(User).where(User.email == email))
        if not user:
            user = User(email=email, full_name=full_name, provider=provider, external_id=external_id)
            session.add(user)
            session.commit()
        else:
            user.external_id = external_id
            user.provider = provider
            if full_name:
                user.full_name = full_name
            session.commit()
        access_token = _ensure_jwt_factory().create_access_token(user.id, user.email)
        return jsonify({"user": _serialize_user(user), "access_token": access_token})


@auth_bp.route("/password-reset/request", methods=["POST"])
def request_password_reset():
    payload = request.get_json(force=True)
    email = payload.get("email")
    if not email:
        return jsonify({"error": "email is required"}), 400
    with get_session() as session:
        user = session.scalar(select(User).where(User.email == email))
        if not user:
            return jsonify({"error": "User not found"}), 404
        token = secrets.token_urlsafe(32)
        expires_at = dt.datetime.utcnow() + dt.timedelta(minutes=password_reset_exp_minutes)
        user.password_reset_token = token
        user.password_reset_expires = expires_at
        session.commit()
        # In production, send token via email provider. Here we return it for demonstration/testing.
        return jsonify({"reset_token": token, "expires_at": expires_at.isoformat()})


@auth_bp.route("/password-reset/confirm", methods=["POST"])
def confirm_password_reset():
    payload = request.get_json(force=True)
    token = payload.get("token")
    new_password = payload.get("new_password")
    if not token or not new_password:
        return jsonify({"error": "token and new_password are required"}), 400
    now = dt.datetime.utcnow()
    with get_session() as session:
        user = session.scalar(
            select(User).where(User.password_reset_token == token, User.password_reset_expires >= now)
        )
        if not user:
            return jsonify({"error": "Invalid or expired reset token"}), 400
        user.hashed_password = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        session.commit()
        return jsonify({"message": "Password updated"})


@auth_bp.route("/profile", methods=["GET"])
@login_required
def profile():
    from flask import g

    return jsonify({"user": _serialize_user(g.current_user)})


@auth_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    payload = request.get_json(force=True)
    full_name = payload.get("full_name")
    email = payload.get("email")
    new_password = payload.get("new_password")
    with get_session() as session:
        from flask import g

        current = session.get(User, g.current_user.id)
        if email and email != current.email:
            existing = session.scalar(select(User).where(User.email == email))
            if existing:
                return jsonify({"error": "Email already in use"}), 409
            current.email = email
        if full_name:
            current.full_name = full_name
        if new_password:
            current.hashed_password = hash_password(new_password)
        session.commit()
        return jsonify({"user": _serialize_user(current)})
