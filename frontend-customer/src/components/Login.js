import React, { useState } from 'react';
import { login } from '../api';

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #00695c 0%, #00897b 100%)',
  },
  card: {
    background: '#fff',
    borderRadius: 12,
    padding: '40px 48px',
    width: 380,
    boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
  },
  logo: { textAlign: 'center', marginBottom: 8, fontSize: 40 },
  title: { textAlign: 'center', color: '#00695c', marginBottom: 4, fontSize: 24, fontWeight: 700 },
  subtitle: { textAlign: 'center', color: '#888', marginBottom: 32, fontSize: 14 },
  label: { display: 'block', marginBottom: 4, fontWeight: 600, color: '#444', fontSize: 13 },
  input: {
    width: '100%',
    padding: '10px 12px',
    border: '1.5px solid #ddd',
    borderRadius: 8,
    fontSize: 15,
    marginBottom: 16,
    boxSizing: 'border-box',
  },
  button: {
    width: '100%',
    padding: '12px',
    background: '#00695c',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    marginTop: 4,
  },
  error: {
    background: '#fdecea',
    color: '#c62828',
    borderRadius: 8,
    padding: '10px 14px',
    marginBottom: 16,
    fontSize: 13,
  },
};

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(username, password);
      sessionStorage.setItem('tabSession', '1');
      onLogin(data.user, null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.logo}>🛍️</div>
        <h1 style={styles.title}>Customer Portal</h1>
        <p style={styles.subtitle}>Sign in to your account</p>
        {error && <div style={styles.error}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <label style={styles.label}>Username</label>
          <input
            style={styles.input}
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
            placeholder="your username"
          />
          <label style={styles.label}>Password</label>
          <input
            style={styles.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="password"
          />
          <button style={styles.button} type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}
