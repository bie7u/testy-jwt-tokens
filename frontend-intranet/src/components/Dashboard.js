import React, { useEffect, useState, useCallback } from 'react';
import { getCustomers, diagnosticLogin, logout } from '../api';

// URL of the customer frontend — configurable via environment variable
const CUSTOMER_FRONTEND_URL = process.env.REACT_APP_CUSTOMER_FRONTEND_URL || 'http://localhost:3002';

const styles = {
  page: { minHeight: '100vh', background: '#f0f2f5' },
  topbar: {
    background: '#1a237e',
    color: '#fff',
    padding: '0 32px',
    height: 60,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  brand: { fontWeight: 700, fontSize: 18, letterSpacing: 1 },
  userInfo: { display: 'flex', alignItems: 'center', gap: 16 },
  username: { fontSize: 14, opacity: 0.9 },
  logoutBtn: {
    background: 'rgba(255,255,255,0.15)',
    border: '1px solid rgba(255,255,255,0.3)',
    color: '#fff',
    padding: '6px 14px',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 13,
  },
  content: { maxWidth: 900, margin: '0 auto', padding: '32px 16px' },
  heading: { color: '#1a237e', marginBottom: 8, fontSize: 22, fontWeight: 700 },
  subheading: { color: '#666', marginBottom: 28, fontSize: 14 },
  table: { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 10, overflow: 'hidden', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' },
  th: { background: '#e8eaf6', color: '#3949ab', fontWeight: 700, padding: '12px 16px', textAlign: 'left', fontSize: 13 },
  td: { padding: '12px 16px', borderBottom: '1px solid #f0f2f5', fontSize: 14, color: '#333' },
  diagBtn: {
    background: '#ff6f00',
    color: '#fff',
    border: 'none',
    padding: '6px 14px',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 13,
    fontWeight: 600,
  },
  badge: {
    display: 'inline-block',
    background: '#e8f5e9',
    color: '#2e7d32',
    borderRadius: 20,
    padding: '2px 10px',
    fontSize: 12,
    fontWeight: 600,
  },
  toast: {
    position: 'fixed',
    bottom: 24,
    right: 24,
    background: '#1b5e20',
    color: '#fff',
    padding: '12px 20px',
    borderRadius: 8,
    fontSize: 14,
    boxShadow: '0 4px 16px rgba(0,0,0,0.18)',
    zIndex: 1000,
  },
  error: { background: '#fdecea', color: '#c62828', borderRadius: 8, padding: '10px 14px', marginBottom: 16 },
};

export default function Dashboard({ user, onLogout }) {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [diagLoading, setDiagLoading] = useState(null);

  const fetchCustomers = useCallback(async () => {
    try {
      const data = await getCustomers();
      setCustomers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCustomers();
  }, [fetchCustomers]);

  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      onLogout();
    }
  };

  const handleDiagnosticLogin = async (customer) => {
    setDiagLoading(customer.id);
    // Open the window synchronously while still inside the user-gesture call
    // stack so that popup blockers (e.g. Firefox) don't block it.  We
    // navigate it to the real URL once the API call returns.
    const win = window.open('', '_blank');
    try {
      const data = await diagnosticLogin(customer.id);
      const url = `${CUSTOMER_FRONTEND_URL}/?code=${data.code}`;
      if (win) {
        win.location.href = url;
      } else {
        window.open(url, '_blank');
      }
      showToast(`Opened diagnostic session for ${customer.username}`);
    } catch (err) {
      if (win) win.close();
      setError(err.message);
    } finally {
      setDiagLoading(null);
    }
  };

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 4000);
  };

  return (
    <div style={styles.page}>
      <div style={styles.topbar}>
        <span style={styles.brand}>🏢 INTRANET</span>
        <div style={styles.userInfo}>
          <span style={styles.username}>
            👤 {user.first_name || user.username} {user.is_staff && '(Staff)'}
          </span>
          <button style={styles.logoutBtn} onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </div>

      <div style={styles.content}>
        <h2 style={styles.heading}>Customer Management</h2>
        <p style={styles.subheading}>
          View all customers and open a diagnostic session in the Customer Portal.
        </p>

        {error && <div style={styles.error}>{error}</div>}

        {loading ? (
          <p>Loading customers…</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>ID</th>
                <th style={styles.th}>Username</th>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Email</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Diagnostic</th>
              </tr>
            </thead>
            <tbody>
              {customers.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ ...styles.td, textAlign: 'center', color: '#aaa' }}>
                    No customers found
                  </td>
                </tr>
              )}
              {customers.map((c) => (
                <tr key={c.id}>
                  <td style={styles.td}>{c.id}</td>
                  <td style={styles.td}>{c.username}</td>
                  <td style={styles.td}>{[c.first_name, c.last_name].filter(Boolean).join(' ') || '—'}</td>
                  <td style={styles.td}>{c.email || '—'}</td>
                  <td style={styles.td}>
                    <span style={styles.badge}>Active</span>
                  </td>
                  <td style={styles.td}>
                    <button
                      style={{
                        ...styles.diagBtn,
                        opacity: diagLoading === c.id ? 0.7 : 1,
                      }}
                      onClick={() => handleDiagnosticLogin(c)}
                      disabled={diagLoading === c.id}
                      title={`Open Customer Portal as ${c.username}`}
                    >
                      {diagLoading === c.id ? '…' : '🔍 Diagnose'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {toast && <div style={styles.toast}>✅ {toast}</div>}
    </div>
  );
}
