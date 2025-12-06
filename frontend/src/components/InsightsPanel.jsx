import React from 'react';

function InsightsPanel({ recommendations }) {
  if (!recommendations?.length) return null;
  return (
    <div className="card insights">
      <div className="card-header">
        <div className="card-title">Smart tips</div>
        <div className="muted">AI-driven budgeting guidance</div>
      </div>
      <ul>
        {recommendations.map((rec, idx) => (
          <li key={idx}>{rec}</li>
        ))}
      </ul>
    </div>
  );
}

export default InsightsPanel;
