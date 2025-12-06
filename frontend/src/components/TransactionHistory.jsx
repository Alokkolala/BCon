import React from 'react';

function formatCurrency(amount, currency = 'USD') {
  if (amount == null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}

function TransactionHistory({ account, transactions }) {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <div className="card-title">{account ? `${account.name} history` : 'Select an account'}</div>
          <div className="muted">Detailed line items per account</div>
        </div>
      </div>
      <div className="card-body table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Description</th>
              <th className="numeric">Amount</th>
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 && (
              <tr>
                <td colSpan="3" className="muted center">
                  {account ? 'No transactions for this account' : 'Pick an account to view history'}
                </td>
              </tr>
            )}
            {transactions.map((tx) => (
              <tr key={`${tx.id}-${tx.date}`}>
                <td>{tx.date}</td>
                <td>{tx.description || tx.merchant_name || '—'}</td>
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

export default TransactionHistory;
