# Backend

This backend is a Flask-based API server with authentication and Plaid integration for aggregating user bank accounts.

## Key modules
- `app.py`: Flask application entrypoint that configures the database, authentication, Plaid blueprint, and a basic health endpoint.
- `config.py`: Loads environment-driven configuration, including Plaid credentials, database URL, encryption key, and JWT settings.
- `api/auth.py`: Blueprint for local and OAuth login, registration, password reset, and profile management endpoints.
- `integrations/plaid_client.py`: Lightweight Plaid client wrapper with error handling for link token creation, public token exchange, account retrieval, transaction retrieval, and item removal.
- `api/plaid.py`: Blueprint exposing endpoints to create link tokens, exchange public tokens, unlink accounts, and fetch accounts/transactions while persisting data securely.
- `integrations/payments_client.py`: Stub payments gateway for initiating transfers and bill payments via providers like Plaid/Yodlee.
- `api/payments.py`: Blueprint for secure transfers, bill payments, and retrieving payment history.
- `database/`: SQLAlchemy engine/session initialization.
- `models/`: SQLAlchemy models for `User`, `Account`, `Transaction`, `Budget` (monthly spending goals), and `Payment` (transfers/bill-pay ledger).
- `utils/crypto.py`: Symmetric encryption helper for protecting Plaid access tokens at rest.

## Environment variables
Set the following before running the server:
- `PLAID_CLIENT_ID` and `PLAID_SECRET`: Plaid API credentials.
- `PLAID_ENV`: `sandbox` (default), `development`, or `production`.
- `PLAID_REDIRECT_URI`: Redirect URI for OAuth flows (optional).
- `DATABASE_URL`: SQLAlchemy-compatible connection string (defaults to `sqlite:///bankconnect.db`).
- `ENCRYPTION_KEY`: Secret used to encrypt Plaid access tokens at rest.
- `JWT_SECRET`: Secret used to sign JWT access tokens.
- `JWT_ALGORITHM`: JWT signing algorithm (default: `HS256`).
- `JWT_EXP_MINUTES`: Access token lifetime in minutes (default: `60`).
- `PASSWORD_RESET_EXP_MINUTES`: Password reset token lifetime in minutes (default: `30`).
- `OAUTH_GOOGLE_CLIENT_ID` / `OAUTH_GOOGLE_CLIENT_SECRET`: Optional provider credentials for Google sign-in flows.

## Running locally
1. `cd backend`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. Set environment variables above (a 32+ character string works for `ENCRYPTION_KEY`).
5. `python app.py`

### Auth endpoints
- `POST /auth/register` with `{ "email": "user@example.com", "password": "...", "full_name": "User" }` -> returns `{ user, access_token }`.
- `POST /auth/login` with `{ "email": "user@example.com", "password": "..." }` -> returns `{ user, access_token }`.
- `POST /auth/oauth/callback` with `{ provider, external_id, email, provider_token }` to support third-party identity flows.
- `POST /auth/password-reset/request` with `{ email }` returns a reset token (simulates sending via email).
- `POST /auth/password-reset/confirm` with `{ token, new_password }` to update the password.
- `GET /auth/profile` / `PUT /auth/profile` to view and update profile data (requires `Authorization: Bearer <token>`).

### Plaid endpoints (protected with JWT)
Pass `Authorization: Bearer <token>` from the auth endpoints above.
- `POST /plaid/link-token` -> `{ "link_token": "..." }`.
- `POST /plaid/exchange` with `{ "public_token": "public-sandbox-..." }` -> stores accounts and transactions.
- `POST /plaid/unlink` with `{ "plaid_account_id": "..." }` -> unlinks and removes stored data.
- `GET /plaid/accounts` -> `{ "accounts": [...] }` for the authenticated user.
- `GET /plaid/transactions` -> `{ "transactions": [...] }` for the authenticated user.

### Budgeting + insights endpoints (protected with JWT)
- `POST /budget/goals` with `{ category, monthly_limit, alert_threshold? }` to create or update a monthly spending goal.
- `GET /budget/summary` -> aggregates monthly spend by category, budget utilization, alert messages when thresholds are crossed, and AI-like recommendations for savings.

### Payments, transfers, and bill pay (protected with JWT)
- `POST /payments/transfer` with `{ from_account_id, to_account_id, amount, note? }` to move money between linked accounts.
- `POST /payments/billpay` with `{ from_account_id, payee_name, amount, payee_account?, note? }` to initiate a bill payment.
- `GET /payments/history` -> returns a ledger of past transfers and bill payments with confirmation details and statuses.

Errors from Plaid or persistence are returned as JSON `{ "error": "..." }` with appropriate status codes.
