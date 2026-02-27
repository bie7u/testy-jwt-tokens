import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import { getMe, refreshToken, exchangeDiagnosticCode, getDiagnosticInfo } from './api';

// Module-level flag that survives React StrictMode's simulated
// unmount → remount cycle (unlike useRef, which is tied to the component
// instance and may be re-initialised on remount).  The flag is reset to
// false on every real page load because module scope is re-evaluated then.
//
// Purpose: React 18 StrictMode double-fires useEffect in development.
// Without this guard the second invocation would run the normal session
// restore flow with the staff member's still-active cookies, call
// setUser(null) after the is_staff check, and overwrite the customer user
// that the first invocation set — leaving the staff member stuck on the
// login page instead of the customer portal.
let codeExchangeStarted = false;

export default function App() {
  const [user, setUser] = useState(null);
  const [staff, setStaff] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exchangeError, setExchangeError] = useState('');

  useEffect(() => {
    async function init() {
      // Check for a diagnostic exchange code in the URL
      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');

      if (code) {
        // Remove the code from the URL immediately (security hygiene)
        window.history.replaceState({}, document.title, window.location.pathname);
        codeExchangeStarted = true;
        try {
          const data = await exchangeDiagnosticCode(code);
          setUser(data.customer);
          setStaff(data.staff);
          setLoading(false);
          return;
        } catch (err) {
          setExchangeError(err.message);
          setLoading(false);
          return;
        }
      }

      // If a previous effect invocation already started an exchange (e.g.
      // React StrictMode re-running the effect), skip the normal flow so we
      // don't race against the exchange and accidentally clear the user.
      if (codeExchangeStarted) {
        return;
      }

      // Normal session restore flow
      let me = await getMe();
      if (!me) {
        const refreshed = await refreshToken();
        if (refreshed) {
          me = await getMe();
        }
      }
      // Customer portal: reject staff users silently (force re-login)
      if (me && me.is_staff) {
        me = null;
      }
      setUser(me);

      // If a customer session is active, check whether it is a diagnostic
      // session (staff_access_token session cookie present and valid).
      // This restores the diagnostic banner after a page refresh within the
      // same browser session.
      if (me) {
        const diagInfo = await getDiagnosticInfo();
        if (diagInfo) {
          setStaff(diagInfo.staff);
        }
      }

      setLoading(false);
    }
    init();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <span style={{ color: '#888', fontSize: 16 }}>Loading…</span>
      </div>
    );
  }

  if (exchangeError) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', flexDirection: 'column', gap: 12 }}>
        <div style={{ fontSize: 40 }}>⚠️</div>
        <div style={{ color: '#c62828', fontSize: 16 }}>{exchangeError}</div>
        <button
          style={{ marginTop: 8, padding: '8px 20px', cursor: 'pointer' }}
          onClick={() => setExchangeError('')}
        >
          Go to login
        </button>
      </div>
    );
  }

  if (!user) {
    return <Login onLogin={(u) => { setUser(u); setStaff(null); }} />;
  }

  return (
    <Dashboard
      user={user}
      staff={staff}
      onLogout={() => { setUser(null); setStaff(null); }}
    />
  );
}
