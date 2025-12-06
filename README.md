# BankConnect

BankConnect aggregates bank accounts and financial data into one interface. This repository provides a modular structure for building the backend API, frontend web application, shared utilities, and documentation.

## Repository Structure
- **backend/**: API server, integrations with banking providers, authentication, database configuration, models, and utility helpers.
- **frontend/**: React/Vue application with pages, components, forms, and styles for the user interface.
- **shared/**: Cross-cutting utilities such as configuration and logging usable by both frontend and backend.
- **docs/**: Project documentation, installation guides, and setup instructions.

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn **or** Python 3.11+ with pip
- PostgreSQL or MongoDB instance
- Plaid or Yodlee sandbox credentials for testing banking integrations
- Secrets for JWT signing and optional OAuth providers (Google, Facebook, etc.)

### Initial Setup
1. Clone the repository and install dependencies for your stack:
   - **Backend (Node.js example)**:
     - `cd backend`
     - `npm install`
   - **Backend (Python Flask example)**:
     - `cd backend`
     - `python -m venv .venv && source .venv/bin/activate`
     - `pip install -r requirements.txt`
   - **Frontend**:
     - `cd frontend`
     - `npm install`
2. Configure environment variables for database access, OAuth providers, and banking API credentials (see `shared/config`).
3. Run backend and frontend dev servers from their respective directories.

### Next Steps
- Implement API routes under `backend/api` and integration services under `backend/integrations`.
- Build UI pages under `frontend/pages` and reusable components under `frontend/components`.
- Add shared logging/configuration utilities to `shared`.
- Document setup and architecture details in `docs`.

## Contributing
1. Fork the repository and create feature branches.
2. Add tests and documentation for your changes when applicable.
3. Submit pull requests for review.
