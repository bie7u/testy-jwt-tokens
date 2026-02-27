import React from 'react';
import { logout } from '../api';

const styles = {
  page: { minHeight: '100vh', background: '#f0f2f5' },
  diagnostic: {
    background: 'linear-gradient(90deg, #e65100, #ff6f00)',
    color: '#fff',
    padding: '12px 32px',
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    fontSize: 14,
    fontWeight: 500,
  },
  diagIcon: { fontSize: 20 },
  diagText: { flex: 1 },
  diagBadge: {
    background: 'rgba(255,255,255,0.2)',
    border: '1px solid rgba(255,255,255,0.4)',
    borderRadius: 20,
    padding: '2px 12px',
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: 0.5,
  },
  topbar: {
    background: '#00695c',
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
  content: { maxWidth: 800, margin: '0 auto', padding: '32px 16px' },
  card: {
    background: '#fff',
    borderRadius: 12,
    padding: 32,
    boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
    marginBottom: 24,
  },
  greeting: { color: '#00695c', fontSize: 22, fontWeight: 700, marginBottom: 8 },
  infoLabel: { color: '#888', fontSize: 12, fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 },
  infoValue: { color: '#333', fontSize: 15, marginBottom: 16 },
  tokenSection: {
    background: '#f9fbe7',
    border: '1px solid #dce775',
    borderRadius: 10,
    padding: '16px 20px',
    marginTop: 16,
  },
  tokenTitle: { color: '#827717', fontWeight: 700, fontSize: 13, marginBottom: 8 },
  tokenHint: { color: '#9e9d24', fontSize: 12 },
};

export default function Dashboard({ user, staff, onLogout }) {
  const isDiagnostic = Boolean(staff);

  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      onLogout();
    }
  };

  return (
    <div style={styles.page}>
      {isDiagnostic && (
        <div style={styles.diagnostic}>
          <span style={styles.diagIcon}>🔍</span>
          <span style={styles.diagText}>
            <strong>Sesja diagnostyczna</strong> — Przeglądasz portal jako klient{' '}
            <strong>{user.username}</strong>. Sesję zainicjował pracownik{' '}
            <strong>{staff.username}</strong> ({staff.first_name} {staff.last_name}).{' '}
            Sesja wygaśnie po zamknięciu karty.
          </span>
          <span style={styles.diagBadge}>DIAGNOSTYKA</span>
        </div>
      )}

      <div style={styles.topbar}>
        <span style={styles.brand}>🛍️ PORTAL KLIENTA</span>
        <div style={styles.userInfo}>
          <span style={styles.username}>👤 {user.first_name || user.username}</span>
          <button style={styles.logoutBtn} onClick={handleLogout}>
            Wyloguj
          </button>
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.card}>
          <h2 style={styles.greeting}>
            Witaj, {user.first_name || user.username}! 👋
          </h2>

          <div style={styles.infoLabel}>Nazwa użytkownika</div>
          <div style={styles.infoValue}>{user.username}</div>

          <div style={styles.infoLabel}>Email</div>
          <div style={styles.infoValue}>{user.email || '—'}</div>

          <div style={styles.infoLabel}>Imię i nazwisko</div>
          <div style={styles.infoValue}>
            {[user.first_name, user.last_name].filter(Boolean).join(' ') || '—'}
          </div>

          {isDiagnostic && (
            <div style={styles.tokenSection}>
              <div style={styles.tokenTitle}>🔑 Tokeny sesji diagnostycznej</div>
              <div style={styles.tokenHint}>
                W tej sesji aktywne są dwa tokeny JWT w ciasteczkach sesji (wygasają po zamknięciu karty):
              </div>
              <ul style={{ margin: '8px 0 0', paddingLeft: 18, color: '#827717', fontSize: 12 }}>
                <li>
                  <strong>Token klienta</strong> (<code>access_token</code>) — identyfikuje użytkownika{' '}
                  <em>{user.username}</em> (ID: {user.id}); używany przez backend do autoryzacji żądań
                </li>
                <li>
                  <strong>Token pracownika</strong> (<code>staff_access_token</code>) — identyfikuje{' '}
                  <em>{staff.username}</em> (ID: {staff.id}); backend może go odczytać z każdego żądania
                  w celu logowania akcji audytowych
                </li>
              </ul>
              <div style={{ marginTop: 8, color: '#9e9d24', fontSize: 12 }}>
                Oba ciasteczka są sesyjne — nie mają daty wygaśnięcia i znikną po zamknięciu karty przeglądarki.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
