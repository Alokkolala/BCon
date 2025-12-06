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
