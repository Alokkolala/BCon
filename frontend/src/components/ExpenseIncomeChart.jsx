import React from 'react';
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

function ExpenseIncomeChart({ data }) {
  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">Expense vs Income</div>
        <div className="muted">Last 90 days</div>
      </div>
      <div className="card-body chart-wrapper">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
            <Legend />
            <Line type="monotone" dataKey="income" stroke="#16a34a" strokeWidth={3} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="expenses" stroke="#ef4444" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ExpenseIncomeChart;
