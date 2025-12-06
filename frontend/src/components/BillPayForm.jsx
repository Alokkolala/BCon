import React, { useMemo, useState } from 'react';

function BillPayForm({ accounts, onSubmit, submitting }) {
  const [fromAccountId, setFromAccountId] = useState('');
  const [payeeName, setPayeeName] = useState('');
  const [payeeAccount, setPayeeAccount] = useState('');
  const [amount, setAmount] = useState('');
  const [note, setNote] = useState('');

  const selectableAccounts = useMemo(() => accounts || [], [accounts]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!fromAccountId || !payeeName || !amount) return;
    onSubmit({
      from_account_id: Number(fromAccountId),
      payee_name: payeeName,
      payee_account: payeeAccount,
      amount: Number(amount),
      note,
    });
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Pay a bill</div>
        <div className="muted">Send payments to utilities, subscriptions, or other payees</div>
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
            Payee name
            <input value={payeeName} onChange={(e) => setPayeeName(e.target.value)} placeholder="Utility company" />
          </label>

          <label className="form-field">
            Payee account/reference
            <input
              value={payeeAccount}
              onChange={(e) => setPayeeAccount(e.target.value)}
              placeholder="Account # or email"
            />
          </label>

          <label className="form-field">
            Amount
            <input
              type="number"
              min="0"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="120.00"
            />
          </label>

          <label className="form-field">
            Note (optional)
            <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Invoice 123" />
          </label>

          <div className="form-actions">
            <button className="btn" type="submit" disabled={submitting}>
              {submitting ? 'Processing...' : 'Pay bill'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default BillPayForm;
