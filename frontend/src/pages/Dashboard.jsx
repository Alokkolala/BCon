import React, { useEffect, useMemo, useState } from 'react';
import {
  fetchAccounts,
  fetchTransactions,
  fetchBudgetSummary,
  saveBudgetGoal,
  submitTransfer,
  submitBillPayment,
  fetchPaymentHistory,
} from '../api/financeClient.js';
import AccountBalanceCard from '../components/AccountBalanceCard.jsx';
import TransactionsTable from '../components/TransactionsTable.jsx';
import ExpenseIncomeChart from '../components/ExpenseIncomeChart.jsx';
import TransactionHistory from '../components/TransactionHistory.jsx';
import LoadingSpinner from '../components/LoadingSpinner.jsx';
import BudgetGoalForm from '../components/BudgetGoalForm.jsx';
import BudgetProgress from '../components/BudgetProgress.jsx';
import BudgetAlerts from '../components/BudgetAlerts.jsx';
import BudgetChart from '../components/BudgetChart.jsx';
import InsightsPanel from '../components/InsightsPanel.jsx';
import TransferForm from '../components/TransferForm.jsx';
import BillPayForm from '../components/BillPayForm.jsx';
import PaymentHistory from '../components/PaymentHistory.jsx';

const USER_ID = 1;

function categorizeTransaction(tx) {
  const isDeposit = Number(tx.amount || 0) >= 0;
  return {
    ...tx,
    category: tx.category || (isDeposit ? 'Deposit' : 'Purchase'),
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
  const [budgetSummary, setBudgetSummary] = useState({ budgets: [], alerts: [], recommendations: [], chart: [] });
  const [savingGoal, setSavingGoal] = useState(false);
  const [submittingPayment, setSubmittingPayment] = useState(false);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError('');
        const [accountData, transactionData, budgetData, paymentData] = await Promise.all([
          fetchAccounts(USER_ID),
          fetchTransactions(USER_ID),
          fetchBudgetSummary(USER_ID),
          fetchPaymentHistory(),
        ]);
        setAccounts(accountData);
        const normalizedTx = transactionData
          .map(categorizeTransaction)
          .sort((a, b) => new Date(b.date) - new Date(a.date));
        setTransactions(normalizedTx);
        setBudgetSummary(budgetData);
        setPayments(paymentData);
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

  const handleSaveBudget = async (payload) => {
    setSavingGoal(true);
    try {
      await saveBudgetGoal(payload);
      const refreshed = await fetchBudgetSummary(USER_ID);
      setBudgetSummary(refreshed);
    } finally {
      setSavingGoal(false);
    }
  };

  const refreshPayments = async () => {
    const latest = await fetchPaymentHistory();
    setPayments(latest);
  };

  const handleTransfer = async (payload) => {
    setSubmittingPayment(true);
    setToast('');
    try {
      const result = await submitTransfer(payload);
      await refreshPayments();
      setToast(result?.message || 'Transfer submitted');
    } catch (err) {
      setToast(err?.response?.data?.error || 'Transfer failed');
    } finally {
      setSubmittingPayment(false);
    }
  };

  const handleBillPayment = async (payload) => {
    setSubmittingPayment(true);
    setToast('');
    try {
      const result = await submitBillPayment(payload);
      await refreshPayments();
      setToast(result?.message || 'Bill payment submitted');
    } catch (err) {
      setToast(err?.response?.data?.error || 'Bill payment failed');
    } finally {
      setSubmittingPayment(false);
    }
  };

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
      {toast && <div className="alert success">{toast}</div>}

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

          <section className="grid two-col">
            <div className="card">
              <div className="card-header">
                <div className="card-title">Monthly budgets</div>
                <div className="muted">Track your spending goals and thresholds</div>
              </div>
              <div className="card-body">
                <BudgetAlerts alerts={budgetSummary.alerts} />
                <BudgetProgress budgets={budgetSummary.budgets} />
              </div>
            </div>
            <BudgetChart data={budgetSummary.chart} />
          </section>

          <section className="grid two-col">
            <BudgetGoalForm onSave={handleSaveBudget} saving={savingGoal} />
            <InsightsPanel recommendations={budgetSummary.recommendations} />
          </section>

          <section className="grid two-col">
            <TransferForm accounts={accounts} onSubmit={handleTransfer} submitting={submittingPayment} />
            <BillPayForm accounts={accounts} onSubmit={handleBillPayment} submitting={submittingPayment} />
          </section>

          <section>
            <PaymentHistory payments={payments} />
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
