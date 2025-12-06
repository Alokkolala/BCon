import axios from 'axios';

const apiBaseUrl = import.meta?.env?.VITE_API_BASE_URL || 'http://localhost:5000';

const client = axios.create({
  baseURL: apiBaseUrl,
  timeout: 8000,
});

export async function fetchAccounts(userId) {
  const response = await client.get('/plaid/accounts', { params: { user_id: userId } });
  return response.data.accounts || [];
}

export async function fetchTransactions(userId) {
  const response = await client.get('/plaid/transactions', { params: { user_id: userId } });
  return response.data.transactions || [];
}

export async function fetchBudgetSummary(userId) {
  const response = await client.get('/budget/summary', { params: { user_id: userId } });
  return response.data;
}

export async function saveBudgetGoal({ category, monthly_limit, alert_threshold }) {
  const response = await client.post('/budget/goals', {
    category,
    monthly_limit,
    alert_threshold,
  });
  return response.data.budget;
}

export async function submitTransfer({ from_account_id, to_account_id, amount, note }) {
  const response = await client.post('/payments/transfer', {
    from_account_id,
    to_account_id,
    amount,
    note,
  });
  return response.data.payment;
}

export async function submitBillPayment({ from_account_id, payee_name, payee_account, amount, note }) {
  const response = await client.post('/payments/billpay', {
    from_account_id,
    payee_name,
    payee_account,
    amount,
    note,
  });
  return response.data.payment;
}

export async function fetchPaymentHistory() {
  const response = await client.get('/payments/history');
  return response.data.payments || [];
}
