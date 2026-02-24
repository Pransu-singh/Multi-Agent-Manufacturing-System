/**
 * js/ui.js
 * Pure DOM helpers and render functions.
 * No API calls, no state — only takes data and updates the DOM.
 */

// ── Toast ──────────────────────────────────────────────────────────────────
function toast(msg, type = 'info', duration = 4000) {
  const container = document.getElementById('toasts');
  const el = document.createElement('div');
  el.className  = `toast ${type}`;
  el.textContent = msg;
  container.appendChild(el);
  setTimeout(() => el.remove(), duration);
}

// ── Sidebar ────────────────────────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-overlay').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
}

// ── Screen switching ───────────────────────────────────────────────────────
function showWelcomeScreen() {
  document.getElementById('welcome-screen').style.display = '';
  document.getElementById('results-screen').style.display = 'none';
}

function showResultsScreen() {
  document.getElementById('welcome-screen').style.display  = 'none';
  document.getElementById('results-screen').style.display  = 'flex';
  document.getElementById('results-screen').style.flexDirection = 'column';
}

// ── Result tabs ────────────────────────────────────────────────────────────
function showResultTab(tab) {
  document.querySelectorAll('.res-tab').forEach(b => b.classList.remove('active'));
  const idx = { live: 0, suppliers: 1, report: 2 };
  const btn = document.querySelectorAll('.res-tab')[idx[tab]];
  if (btn) btn.classList.add('active');
  document.getElementById('tab-live').style.display      = tab === 'live'      ? '' : 'none';
  document.getElementById('tab-suppliers').style.display = tab === 'suppliers' ? '' : 'none';
  document.getElementById('tab-report').style.display    = tab === 'report'    ? '' : 'none';
}

// ── Status badge ───────────────────────────────────────────────────────────
function setStatus(s) {
  const el = document.getElementById('results-status');
  const labels = {
    running: '<span class="spinner"></span> Running',
    done:    '✓ Done',
    error:   '✗ Error',
    stopped: '⏹ Stopped',
  };
  el.className = `status-badge ${s}`;
  el.innerHTML = labels[s] || s;
}

// ── Log ────────────────────────────────────────────────────────────────────
function appendLog(msg, level = 'info') {
  const panel = document.getElementById('log-panel');
  const line  = document.createElement('div');
  line.className  = `log-line ${level}`;
  line.textContent = msg;
  panel.appendChild(line);
  panel.scrollTop = panel.scrollHeight;
}

// ── Progress bar ───────────────────────────────────────────────────────────
let _progressVal = 5;
function resetProgress() {
  _progressVal = 5;
  document.getElementById('progress-bar').style.width  = '5%';
  document.getElementById('progress-wrap').style.display = '';
}
function advanceProgress() {
  _progressVal = Math.min(_progressVal + (95 - _progressVal) * 0.06, 92);
  document.getElementById('progress-bar').style.width = `${_progressVal}%`;
}
function completeProgress() {
  document.getElementById('progress-bar').style.width = '100%';
  setTimeout(() => {
    document.getElementById('progress-wrap').style.display = 'none';
  }, 600);
}

// ── Supplier cards ─────────────────────────────────────────────────────────
function renderSuppliers(list) {
  const grid = document.getElementById('suppliers-grid');

  grid.innerHTML = list.map(s => {
    const products = Array.isArray(s.products)
      ? s.products
      : (s.products ? s.products.split(',').map(p => p.trim()) : []);

    const certifications = Array.isArray(s.certifications)
      ? s.certifications
      : (s.certifications ? s.certifications.split(',').map(c => c.trim()) : []);

    return `
      <div class="supplier-card">
        <div class="sc-name">${esc(s.name || 'Unknown')}</div>
        <div class="sc-location">📍 ${esc(s.location || 'Unknown')}</div>
        ${s.description ? `<div class="sc-desc">${esc(s.description)}</div>` : ''}
        <div class="sc-tags">
          ${products.slice(0,4).map(p => `<span class="tag">${esc(p)}</span>`).join('')}
          ${certifications.map(c => `<span class="tag cert">${esc(c)}</span>`).join('')}
          ${s.min_order ? `<span class="tag">MOQ: ${esc(s.min_order)}</span>` : ''}
        </div>
        <div class="sc-footer">
          ${s.website ? `<a class="sc-link" href="${esc(s.website)}" target="_blank" rel="noopener">🌐 Website</a>` : ''}
          ${s.contact  ? `<a class="sc-link" href="mailto:${esc(s.contact)}">✉ Contact</a>` : ''}
        </div>
      </div>
    `;
  }).join('');

  document.getElementById('supp-count').textContent = `(${list.length})`;
}

// ── Markdown report ────────────────────────────────────────────────────────
function renderReport(markdown) {
  const el = document.getElementById('report-content');
  el.innerHTML = (typeof marked !== 'undefined')
    ? marked.parse(markdown)
    : `<pre style="white-space:pre-wrap;font-family:inherit">${esc(markdown)}</pre>`;
}

// ── History sidebar ────────────────────────────────────────────────────────
function renderHistory(items, onLoad, onDelete) {
  const el = document.getElementById('sidebar-history');
  if (!items?.length) {
    el.innerHTML = '<p style="padding:16px;color:var(--muted);font-size:13px">No searches yet.</p>';
    return;
  }
  // Deduplicate by query string — keep most recent
  const seen   = new Set();
  const unique = items.filter(item => {
    const key = (item.query || '').trim().toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  el.innerHTML = unique.map(item => `
    <div class="history-item" data-session="${esc(item.session_id)}">
      <div class="hi-content" data-action="load" data-session="${esc(item.session_id)}">
        <div class="hi-query">${esc(item.query)}</div>
        <div class="hi-date">${item.suppliers_found ?? 0} suppliers · ${formatDate(item.created_at)}</div>
      </div>
      <button class="hi-delete" data-action="delete" data-session="${esc(item.session_id)}" title="Delete">✕</button>
    </div>
  `).join('');

  // Event delegation — one listener on the container
  el.onclick = e => {
    const loadEl  = e.target.closest('[data-action="load"]');
    const delEl   = e.target.closest('[data-action="delete"]');
    if (loadEl)  onLoad(loadEl.dataset.session);
    if (delEl)   onDelete(delEl.dataset.session);
  };
}

function removeHistoryItem(sessionId) {
  const el = document.querySelector(`.history-item[data-session="${sessionId}"]`);
  if (el) el.remove();
  const list = document.getElementById('sidebar-history');
  if (list && !list.querySelector('.history-item')) {
    list.innerHTML = '<p style="padding:16px;color:var(--muted);font-size:13px">No searches yet.</p>';
  }
}

// ── Shared utils ───────────────────────────────────────────────────────────
function esc(s) {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatDate(iso) {
  if (!iso) return '';
  try {
    const d    = new Date(iso);
    const diff = Date.now() - d;
    if (diff < 60_000)      return 'Just now';
    if (diff < 3_600_000)   return `${Math.floor(diff / 60_000)}m ago`;
    if (diff < 86_400_000)  return `${Math.floor(diff / 3_600_000)}h ago`;
    return d.toLocaleDateString();
  } catch { return ''; }
}
