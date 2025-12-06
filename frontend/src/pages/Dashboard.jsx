import React, { useEffect, useMemo, useState } from 'react';
import { fetchAccounts, fetchTransactions } from '../api/financeClient.js';
import AccountBalanceCard from '../components/AccountBalanceCard.jsx';
import TransactionsTable from '../components/TransactionsTable.jsx';
import ExpenseIncomeChart from '../components/ExpenseIncomeChart.jsx';
import TransactionHistory from '../components/TransactionHistory.jsx';
import LoadingSpinner from '../components/LoadingSpinner.jsx';

const USER_ID = 1;

function categorizeTransaction(tx) {
  const isDeposit = Number(tx.amount || 0) >= 0;
  return {
    ...tx,
    category: isDeposit ? 'Deposit' : 'Purchase',
  };
}

function buildTrendSeries(transactions) {
  const buckets = new Map();
  transactions.forEach((tx) => {
    const date = new Date(tx.date);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    const current = buckets.get(key) || { income: 0, expenses: 0 };
    if (tx.amount >= 0) {
      current.income += tx.amount;
    } else {
      current.expenses += Math.abs(tx.amount);
    }
    buckets.set(key, current);
  });

  return Array.from(buckets.entries())
    .sort(([a], [b]) => (a > b ? 1 : -1))
    .map(([period, totals]) => ({ period, ...totals }));
}

function Dashboard() {
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError('');
        const [accountData, transactionData] = await Promise.all([
          fetchAccounts(USER_ID),
          fetchTransactions(USER_ID),
        ]);
        setAccounts(accountData);
        const normalizedTx = transactionData
          .map(categorizeTransaction)
          .sort((a, b) => new Date(b.date) - new Date(a.date));
        setTransactions(normalizedTx);
        if (accountData.length > 0) {
          setSelectedAccount(accountData[0]);
        }
      } catch (err) {
        setError(err?.response?.data?.error || 'Unable to load financial data');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const recentTransactions = useMemo(
    () => transactions.slice(0, 10),
    [transactions]
  );

  const historyForAccount = useMemo(() => {
    if (!selectedAccount) return [];
    return transactions.filter((tx) => tx.account_id === selectedAccount.id);
  }, [selectedAccount, transactions]);

  const chartSeries = useMemo(() => buildTrendSeries(transactions), [transactions]);

  return (
    <div className="dashboard">
      <div className="section-header">
        <div>
          <h1>Financial dashboard</h1>
          <p className="muted">Aggregated balances, spending, and account-level history</p>
        </div>
        <button type="button" className="btn ghost" onClick={() => window.location.reload()}>
          Refresh data
        </button>
      </div>

      {loading && <LoadingSpinner message="Fetching bank data..." />}
      {error && <div className="alert error">{error}</div>}

      {!loading && !error && (
        <>
          <section>
            <h2>Linked accounts</h2>
            <div className="grid accounts">
              {accounts.map((account) => (
                <AccountBalanceCard
                  key={account.id}
                  account={account}
                  onSelect={setSelectedAccount}
                  isActive={selectedAccount?.id === account.id}
                />
              ))}
              {accounts.length === 0 && <div className="muted">No accounts linked yet.</div>}
            </div>
          </section>

          <section className="grid two-col">
            <TransactionsTable title="Recent transactions" transactions={recentTransactions} />
            <ExpenseIncomeChart data={chartSeries} />
          </section>

          <section>
            <TransactionHistory account={selectedAccount} transactions={historyForAccount} />
          </section>
        </>
      )}
    </div>
  );
}

export default Dashboard;
