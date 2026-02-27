import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import { getMe, refreshToken } from './api';

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Try to restore session on page load
    async function restoreSession() {
      // Tab-scoped session: sessionStorage is cleared when the tab closes, so
      // if there is no marker the user must log in again (even if auth cookies
      // are still present from a previous tab or browser session).
      if (!sessionStorage.getItem('tabSession')) {
        setLoading(false);
        return;
      }
      let me = await getMe();
      if (!me) {
        // Try refresh once
        const refreshed = await refreshToken();
        if (refreshed) {
          me = await getMe();
        }
      }
      setUser(me);
      setLoading(false);
    }
    restoreSession();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <span style={{ color: '#888', fontSize: 16 }}>Loading…</span>
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return <Dashboard user={user} onLogout={() => setUser(null)} />;
}
