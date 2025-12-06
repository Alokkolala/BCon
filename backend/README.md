# Backend

This backend is a Flask-based API server with Plaid integration for aggregating user bank accounts.

## Key modules
- `app.py`: Flask application entrypoint that configures the database, Plaid blueprint, and a basic health endpoint.
- `config.py`: Loads environment-driven configuration, including Plaid credentials, database URL, and encryption key.
- `integrations/plaid_client.py`: Lightweight Plaid client wrapper with error handling for link token creation, public token exchange, account retrieval, transaction retrieval, and item removal.
- `api/plaid.py`: Blueprint exposing endpoints to create link tokens, exchange public tokens, unlink accounts, and fetch accounts/transactions while persisting data securely.
- `database/`: SQLAlchemy engine/session initialization.
- `models/`: SQLAlchemy models for `User`, `Account`, and `Transaction`.
- `utils/crypto.py`: Symmetric encryption helper for protecting Plaid access tokens at rest.

## Environment variables
Set the following before running the server:
- `PLAID_CLIENT_ID` and `PLAID_SECRET`: Plaid API credentials.
- `PLAID_ENV`: `sandbox` (default), `development`, or `production`.
- `PLAID_REDIRECT_URI`: Redirect URI for OAuth flows (optional).
- `DATABASE_URL`: SQLAlchemy-compatible connection string (defaults to `sqlite:///bankconnect.db`).
- `ENCRYPTION_KEY`: Secret used to encrypt Plaid access tokens at rest.

## Running locally
1. `cd backend`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Set environment variables above (a 32+ character string works for `ENCRYPTION_KEY`).
5. `python app.py`

The Plaid endpoints are served under `/plaid`. Example payloads:
- `POST /plaid/link-token` with `{ "user_id": 1 }`.
- `POST /plaid/exchange` with `{ "user_id": 1, "public_token": "public-sandbox-..." }`.
- `POST /plaid/unlink` with `{ "user_id": 1, "plaid_account_id": "..." }`.
- `GET /plaid/accounts?user_id=1`
- `GET /plaid/transactions?user_id=1`

Errors from Plaid or persistence are returned as JSON `{ "error": "..." }` with appropriate status codes.
