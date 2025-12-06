import React from 'react';
import Dashboard from './pages/Dashboard.jsx';

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">BankConnect</div>
        <div className="header-actions">
          <span className="user-pill">Signed in</span>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;
