import React, { useState } from 'react';

function BudgetGoalForm({ onSave, saving }) {
  const [category, setCategory] = useState('Groceries');
  const [monthlyLimit, setMonthlyLimit] = useState('400');
  const [alertThreshold, setAlertThreshold] = useState('350');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!category || !monthlyLimit) {
      setError('Category and monthly limit are required');
      return;
    }
    try {
      await onSave({
        category,
        monthly_limit: Number(monthlyLimit),
        alert_threshold: alertThreshold ? Number(alertThreshold) : null,
      });
      setError('');
    } catch (err) {
      setError(err?.response?.data?.error || 'Unable to save budget');
    }
  };

  return (
    <form className="budget-form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <label className="form-field">
          <span>Category</span>
          <input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Groceries" />
        </label>
        <label className="form-field">
          <span>Monthly limit ($)</span>
          <input type="number" min="0" value={monthlyLimit} onChange={(e) => setMonthlyLimit(e.target.value)} />
        </label>
        <label className="form-field">
          <span>Alert threshold ($)</span>
          <input type="number" min="0" value={alertThreshold} onChange={(e) => setAlertThreshold(e.target.value)} />
          <small className="muted">We will surface alerts once spending crosses this amount.</small>
        </label>
      </div>
      {error && <div className="alert error">{error}</div>}
      <div className="form-actions">
        <button type="submit" className="btn primary" disabled={saving}>
          {saving ? 'Saving...' : 'Save budget'}
        </button>
      </div>
    </form>
  );
}

export default BudgetGoalForm;
