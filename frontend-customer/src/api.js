/**
 * API service for the Customer frontend.
 * Supports normal login and diagnostic session via exchange code.
 * In development, the Create React App proxy (package.json "proxy" field)
 * forwards /api/* to the backend. In production, set REACT_APP_API_URL
 * to the backend origin (e.g. http://localhost:8000).
 */

const API_BASE = (process.env.REACT_APP_API_URL || '') + '/api/auth';

async function request(method, path, body = null) {
  const options = {
    method,
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) {
    options.body = JSON.stringify(body);
  }
  const response = await fetch(`${API_BASE}${path}`, options);
  return response;
}

export async function login(username, password) {
  // Customer-only login: reject staff users
  const res = await request('POST', '/login/', { username, password });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Login failed');
  if (data.user && data.user.is_staff) {
    throw new Error('This portal is for customers only.');
  }
  return data;
}

export async function logout() {
  const res = await request('POST', '/logout/');
  if (!res.ok) throw new Error('Logout failed');
}

export async function getMe() {
  const res = await request('GET', '/me/');
  if (res.status === 401) return null;
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to fetch user');
  return data;
}

export async function refreshToken() {
  const res = await request('POST', '/refresh/');
  return res.ok;
}

/**
 * Exchange a one-time diagnostic code for customer JWT cookies.
 * Returns { customer, staff, diagnostic } on success.
 */
export async function exchangeDiagnosticCode(code) {
  const res = await request('POST', '/exchange/', { code });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Exchange failed');
  return data;
}
