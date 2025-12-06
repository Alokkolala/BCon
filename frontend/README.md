# Frontend

The frontend is a React application that renders the BankConnect dashboard and consumes backend Plaid aggregation APIs.

## Structure
- `src/pages/`: Top-level views (Dashboard, Account Overview, Transactions, Settings). The `Dashboard` page is implemented.
- `src/components/`: Reusable UI elements such as account cards, charts, and tables.
- `src/api/`: API client helpers for talking to the backend securely.
- `src/styles/`: Global styles and theme variables.

## Getting Started
1. Install dependencies: `cd frontend && npm install`.
2. Create a `.env` file in `frontend/` with `VITE_API_BASE_URL=http://localhost:5000` (or your deployed backend URL).
3. Start the dev server: `npm run dev` and open the provided local URL.
4. The dashboard will fetch `/plaid/accounts` and `/plaid/transactions` for the signed-in user (configure user id handling as needed).
