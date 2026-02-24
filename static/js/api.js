/**
 * js/api.js
 * All communication with the Flask backend.
 * Every function returns a parsed response or throws.
 */

// ── Reports / History ──────────────────────────────────────────────────────
async function apiGetReports(limit = 30) {
  const h = await apiHeaders();
  const r = await fetch(`${API_BASE}/api/reports?limit=${limit}`, { headers: h });
  if (!r.ok) throw new Error(`GET /api/reports → ${r.status}`);
  return r.json(); // { reports: [...] }
}

async function apiGetReport(sessionId) {
  const h = await apiHeaders();
  const r = await fetch(`${API_BASE}/api/report/${sessionId}`, { headers: h });
  if (!r.ok) throw new Error(`GET /api/report → ${r.status}`);
  return r.json();
}

async function apiDeleteReport(sessionId) {
  const h = await apiHeaders();
  await fetch(`${API_BASE}/api/report/${sessionId}`, { method: 'DELETE', headers: h });
}

// ── Query (returns a ReadableStream for SSE) ───────────────────────────────
async function apiStartQuery(query) {
  const token = await getToken();
  const resp  = await fetch(`${API_BASE}/api/query`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body:    JSON.stringify({ query }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ error: resp.statusText }));
    throw new Error(err.error || resp.statusText);
  }
  return resp.body.getReader();
}

// ── Stop pipeline ──────────────────────────────────────────────────────────
async function apiStop(sessionId) {
  const h = await apiHeaders();
  await fetch(`${API_BASE}/api/stop`, {
    method:  'POST',
    headers: h,
    body:    JSON.stringify({ session_id: sessionId }),
  });
}

// ── Suppliers by session ──────────────────────────────────────────────────
async function apiGetSuppliersBySession(sessionId) {
  const h = await apiHeaders();
  const r = await fetch(`${API_BASE}/api/suppliers?session_id=${encodeURIComponent(sessionId)}`, { headers: h });
  if (!r.ok) throw new Error(`GET /api/suppliers → ${r.status}`);
  return r.json(); // { suppliers: [...] }
}

// ── Downloads (opened as window.open since browser can't set headers) ──────
async function apiDownloadTxt(sessionId) {
  const token = await getToken();
  window.open(`${API_BASE}/api/download/${sessionId}?token=${token}`);
}

async function apiDownloadJson(sessionId) {
  const token = await getToken();
  window.open(`${API_BASE}/api/download-json/${sessionId}?token=${token}`);
}

async function apiDownloadPdf(sessionId) {
  const token = await getToken();
  window.open(`${API_BASE}/api/download-pdf/${sessionId}?token=${token}`);
}