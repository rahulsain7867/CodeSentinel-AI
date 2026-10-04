// api.js - Simple API client for CodeSentinel AI backend

const API_BASE = '/api';

export async function submitReview(code, language) {
  const response = await fetch(`${API_BASE}/review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code, language }),
  });
  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Review failed: ${err}`);
  }
  return response.json(); // Expect JSON with review results
}

export async function fetchDashboard() {
  const response = await fetch(`${API_BASE}/dashboard`);
  if (!response.ok) throw new Error('Failed to load dashboard');
  return response.json();
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE}/history`);
  if (!response.ok) throw new Error('Failed to load history');
  return response.json();
}

export async function fetchTrendData() {
  const response = await fetch(`${API_BASE}/trends`);
  if (!response.ok) throw new Error('Failed to load trends');
  return response.json();
}

export async function fetchRecurringIssues() {
  const response = await fetch(`${API_BASE}/recurring-issues`);
  if (!response.ok) throw new Error('Failed to load recurring issues');
  return response.json();
}
