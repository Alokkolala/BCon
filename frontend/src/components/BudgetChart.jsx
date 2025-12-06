import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';

function BudgetChart({ data }) {
  if (!data?.length) {
    return <div className="muted">Add a budget to see spending vs goal.</div>;
  }
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Spending vs. budget</div>
        <div className="muted">Current month</div>
      </div>
      <div className="card-body chart-wrapper">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" interval={0} angle={-15} textAnchor="end" height={70} />
            <YAxis />
            <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
            <Legend />
            <Bar dataKey="limit" fill="#1d4ed8" name="Budget" radius={[4, 4, 0, 0]} />
            <Bar dataKey="spent" fill="#ef4444" name="Spent" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default BudgetChart;
