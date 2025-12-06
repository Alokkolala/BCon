# Backend

The backend hosts the BankConnect API server, authentication system, integrations with banking providers, and database access layer.

## Structure
- `api/`: REST/GraphQL endpoints for account aggregation and user actions.
- `integrations/`: Clients for banking APIs (e.g., Plaid, Yodlee).
- `auth/`: OAuth2/JWT authentication flows and token management.
- `database/`: Database configuration, migrations, and query helpers for PostgreSQL/MongoDB.
- `models/`: Data models representing users, bank accounts, and transactions.
- `utils/`: Shared backend utilities such as security helpers and encryption.

## Getting Started
- Choose a server stack (Node.js with Express/Fastify or Python Flask) and initialize dependencies here.
- Add environment variables for database credentials, OAuth secrets, and integration keys.
- Implement routes under `api/` that leverage `integrations/` and `database/` layers.
