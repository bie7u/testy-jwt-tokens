/**
 * API service for the Intranet frontend.
 * All requests are sent with credentials (cookies) included.
 * The proxy in package.json routes /api/* to http://localhost:8000.
 */

const API_BASE = '/api/auth';

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
  const res = await request('POST', '/login/?require_staff=true', { username, password });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Login failed');
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

export async function getCustomers() {
  const res = await request('GET', '/users/');
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to fetch customers');
  return data;
}

export async function diagnosticLogin(customerId) {
  const res = await request('POST', '/diagnostic-login/', { customer_id: customerId });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Diagnostic login failed');
  return data;
}
