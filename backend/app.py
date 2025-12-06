"""Flask application entrypoint for BankConnect backend."""
from __future__ import annotations

from flask import Flask, jsonify
from sqlalchemy.exc import OperationalError

from backend.api.budget import init_budget_blueprint
from backend.api.auth import init_auth_blueprint
from backend.api.payments import init_payments_blueprint
from backend.api.plaid import init_plaid_blueprint
from backend.config import load_settings
from backend.database import db
from backend.database.db import Base


def create_app() -> Flask:
    settings = load_settings()
    db.init_engine(settings.database_url)
    Base.metadata.create_all(db.auth_engine)

    app = Flask(__name__)
    auth_bp = init_auth_blueprint(settings)
    plaid_bp = init_plaid_blueprint(settings)
    budget_bp = init_budget_blueprint()
    payments_bp = init_payments_blueprint()
    app.register_blueprint(auth_bp)
    app.register_blueprint(plaid_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(payments_bp)

    @app.get("/health")
    def health():
        try:
            with db.get_session() as session:
                session.execute("SELECT 1")
            return {"status": "ok"}
        except OperationalError:
            return jsonify({"status": "database_error"}), 500

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000, debug=True)
