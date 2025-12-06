# Frontend

The frontend is a React or Vue.js application that presents account aggregation, transaction insights, and settings management.

## Structure
- `pages/`: Top-level views for Dashboard, Account Overview, Transactions, and Settings.
- `components/`: Reusable UI pieces such as Header, Sidebar, and FinancialCharts.
- `forms/`: Authentication and bank-linking forms (login, signup, OAuth flows).
- `styles/`: Global styles, component-level SCSS/CSS, and theme variables.

## Getting Started
1. Initialize your framework (e.g., `npm create vite@latest frontend -- --template react`).
2. Install dependencies with `npm install` or `yarn`.
3. Configure environment variables for API base URLs and OAuth redirect URIs.
4. Add shared UI/state utilities as needed under `shared/` in the repo root.
