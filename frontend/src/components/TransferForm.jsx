import React, { useMemo, useState } from 'react';

function TransferForm({ accounts, onSubmit, submitting }) {
  const [fromAccountId, setFromAccountId] = useState('');
  const [toAccountId, setToAccountId] = useState('');
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');

  const selectableAccounts = useMemo(() => accounts || [], [accounts]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!fromAccountId || !toAccountId || !amount) return;
    onSubmit({
      from_account_id: Number(fromAccountId),
      to_account_id: Number(toAccountId),
      amount: Number(amount),
      note,
    });
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Transfer between accounts</div>
        <div className="muted">Move funds instantly across your linked accounts</div>
      </div>
      <div className="card-body">
        <form className="form-grid" onSubmit={handleSubmit}>
          <label className="form-field">
            From account
            <select value={fromAccountId} onChange={(e) => setFromAccountId(e.target.value)}>
              <option value="">Select account</option>
              {selectableAccounts.map((acct) => (
                <option key={acct.id} value={acct.id}>
                  {acct.name} • {acct.mask}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            To account
            <select value={toAccountId} onChange={(e) => setToAccountId(e.target.value)}>
              <option value="">Select account</option>
              {selectableAccounts.map((acct) => (
                <option key={acct.id} value={acct.id}>
                  {acct.name} • {acct.mask}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            Amount
            <input
              type="number"
              min="0"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="250.00"
            />
          </label>

          <label className="form-field">
            Note (optional)
            <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Savings transfer" />
          </label>

          <div className="form-actions">
            <button className="btn" type="submit" disabled={submitting}>
              {submitting ? 'Processing...' : 'Transfer now'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TransferForm;
