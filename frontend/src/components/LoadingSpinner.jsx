import React from 'react';

function LoadingSpinner({ message = 'Loading data...' }) {
  return (
    <div className="loading">
      <div className="spinner" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}

export default LoadingSpinner;
