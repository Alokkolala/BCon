import React from 'react';

function formatCurrency(amount, currency = 'USD') {
  if (amount == null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount);
}

function AccountBalanceCard({ account, onSelect, isActive }) {
  return (
    <div
      className={`card account-card ${isActive ? 'active' : ''}`}
      role="button"
      tabIndex={0}
      onClick={() => onSelect(account)}
      onKeyDown={(evt) => evt.key === 'Enter' && onSelect(account)}
    >
      <div className="card-header">
        <div>
          <div className="muted">{account.institution_name}</div>
          <div className="card-title">{account.name}</div>
        </div>
        <span className="pill">{account.subtype || 'Account'}</span>
      </div>
      <div className="card-body balance">
        <div className="label">Current balance</div>
        <div className="value">{formatCurrency(account.balance?.current, account.balance?.currency)}</div>
        {account.mask && <div className="muted">•••• {account.mask}</div>}
      </div>
    </div>
  );
}

export default AccountBalanceCard;
