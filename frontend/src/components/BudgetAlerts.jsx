import React from 'react';

function BudgetAlerts({ alerts }) {
  if (!alerts?.length) {
    return <div className="muted">No alerts yet. Stay on budget to keep it this way!</div>;
  }
  return (
    <div className="alert info">
      <ul>
        {alerts.map((alert, idx) => (
          <li key={idx}>{alert}</li>
        ))}
      </ul>
    </div>
  );
}

export default BudgetAlerts;
