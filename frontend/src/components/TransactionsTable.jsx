import React from 'react';

function formatCurrency(amount, currency = 'USD') {
  if (amount == null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}

function TransactionsTable({ transactions, title }) {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">{title}</div>
      </div>
      <div className="card-body table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Description</th>
              <th>Merchant</th>
              <th>Category</th>
              <th className="numeric">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 && (
              <tr>
                <td colSpan="5" className="muted center">
                  No transactions yet
                </td>
              </tr>
            )}
            {transactions.map((tx) => (
              <tr key={`${tx.id}-${tx.date}`}>
                <td>{tx.date}</td>
                <td>{tx.description || '—'}</td>
                <td>{tx.merchant_name || '—'}</td>
                <td>
                  <span className={`pill ${tx.category === 'Deposit' ? 'success' : 'warning'}`}>
                    {tx.category}
                  </span>
                </td>
                <td className={`numeric ${tx.amount < 0 ? 'negative' : 'positive'}`}>
                  {formatCurrency(tx.amount, tx.currency)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TransactionsTable;
