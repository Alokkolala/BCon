import React from 'react';

function ProgressBar({ value, max }) {
  const percent = Math.min((value / (max || 1)) * 100, 100);
  return (
    <div className="progress">
      <div className="progress-bar" style={{ width: `${percent}%` }} />
    </div>
  );
}

function BudgetProgress({ budgets }) {
  if (!budgets?.length) {
    return <div className="muted">No budgets yet. Create a goal to start tracking spending.</div>;
  }

  return (
    <div className="budget-progress-list">
      {budgets.map((budget) => {
        const percent = Math.min((budget.spent / budget.monthly_limit) * 100, 999);
        const statusClass = percent >= 100 ? 'over' : percent >= 80 ? 'near' : 'safe';
        return (
          <div className={`budget-progress-item ${statusClass}`} key={budget.category}>
            <div className="budget-row">
              <div>
                <div className="label">{budget.category}</div>
                <div className="muted small">Budget ${budget.monthly_limit.toFixed(2)} • Remaining ${budget.remaining.toFixed(2)}</div>
              </div>
              <div className="label">
                ${budget.spent.toFixed(2)}
              </div>
            </div>
            <ProgressBar value={budget.spent} max={budget.monthly_limit} />
          </div>
        );
      })}
    </div>
  );
}

export default BudgetProgress;
