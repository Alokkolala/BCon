import React from 'react';

function PaymentHistory({ payments }) {
  if (!payments || payments.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="card-title">Payment & transfer history</div>
          <div className="muted">Track completed and failed money movement</div>
        </div>
        <div className="card-body muted">No payments recorded yet.</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Payment & transfer history</div>
        <div className="muted">Track completed and failed money movement</div>
      </div>
      <div className="card-body">
        <table className="table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Amount</th>
              <th>From</th>
              <th>To / Payee</th>
              <th>Status</th>
              <th>Confirmation</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id}>
                <td className="muted">{payment.type === 'bill' ? 'Bill payment' : 'Transfer'}</td>
                <td className={`numeric ${payment.status === 'failed' ? 'negative' : ''}`}>
                  {payment.currency || '$'} {Number(payment.amount || 0).toFixed(2)}
                </td>
                <td>{payment.from_account_name || '—'}</td>
                <td>{payment.to_account_name || payment.payee_name || '—'}</td>
                <td className={payment.status === 'failed' ? 'text-error' : 'text-success'}>{payment.status}</td>
                <td>{payment.confirmation_code || '—'}</td>
                <td>{payment.created_at ? new Date(payment.created_at).toLocaleString() : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default PaymentHistory;
