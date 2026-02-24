/**
 * js/app.js
 * Main application logic for app.html.
 * Depends on: firebase.js, api.js, ui.js
 */

// ── App state ──────────────────────────────────────────────────────────────
let activeSessionId = null;
let activeReader    = null;

// ── Auth gate ──────────────────────────────────────────────────────────────
auth.onAuthStateChanged(async user => {
  if (!user) {
    // Not logged in — send back to login page
    window.location.href = '/';
    return;
  }
  currentUser    = user;
  currentIdToken = await user.getIdToken();

  // Refresh token every 55 min
  setInterval(async () => {
    currentIdToken = await user.getIdToken(true);
  }, 55 * 60 * 1000);

  // Populate header
  document.getElementById('user-name').textContent = user.displayName || user.email;
  document.getElementById('user-photo').src        = user.photoURL || '';

  loadHistory();
});

// ── Sign out ───────────────────────────────────────────────────────────────
document.getElementById('signout-btn').addEventListener('click', () => {
  signOut();
  // onAuthStateChanged will redirect to / after signOut resolves
});

// ── Sidebar ────────────────────────────────────────────────────────────────
document.getElementById('menu-btn').addEventListener('click', toggleSidebar);
document.getElementById('sidebar-overlay').addEventListener('click', closeSidebar);
document.getElementById('new-search-btn').addEventListener('click', showWelcome);

// ── Welcome / search ───────────────────────────────────────────────────────
document.getElementById('main-query').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitQuery(); }
});
document.getElementById('main-send-btn').addEventListener('click', submitQuery);

function fillInput(text) {
  const input = document.getElementById('main-query');
  input.value = text;
  input.focus();
}

document.querySelectorAll('.example-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const query = chip.dataset.query;
    fillInput(query);
  });
});

// ── Results header buttons ─────────────────────────────────────────────────
document.getElementById('stop-btn').addEventListener('click',     stopPipeline);
document.getElementById('dl-txt-btn').addEventListener('click',   () => apiDownloadTxt(activeSessionId));
document.getElementById('dl-json-btn').addEventListener('click',  () => apiDownloadJson(activeSessionId));
document.getElementById('dl-pdf-btn').addEventListener('click', () => apiDownloadPdf(activeSessionId));

// ── Results tabs ───────────────────────────────────────────────────────────
document.querySelectorAll('.res-tab').forEach((btn, i) => {
  const tabs = ['live', 'suppliers', 'report'];
  btn.addEventListener('click', () => showResultTab(tabs[i]));
});

// ── Core functions ─────────────────────────────────────────────────────────
function showWelcome() {
  closeSidebar();
  if (activeReader) { activeReader.cancel(); activeReader = null; }
  showWelcomeScreen();
}

async function loadHistory() {
  try {
    const { reports } = await apiGetReports(30);
    renderHistory(
      reports || [],
      sessionId => loadReport(sessionId),
      sessionId => deleteReport(sessionId),
    );
  } catch (e) {
    console.error('[History]', e);
  }
}

async function loadReport(sessionId) {
  try {
    const data = await apiGetReport(sessionId);
    activeSessionId = sessionId;

    showResultsScreen();
    document.getElementById('results-query-label').textContent = data.query || '';
    document.getElementById('log-panel').innerHTML             = '';
    document.getElementById('suppliers-grid').innerHTML        = '';
    document.getElementById('supp-count').textContent          = '';
    document.getElementById('progress-wrap').style.display     = 'none';
    document.getElementById('stop-btn').style.display          = 'none';
    document.getElementById('dl-txt-btn').style.display        = '';
    document.getElementById('dl-json-btn').style.display       = '';
    document.getElementById('dl-pdf-btn').style.display        = '';


    setStatus('done');

    // Load report text
    const reportText = data.report_text || data.document || '';
    if (reportText) {
      renderReport(reportText);
      showResultTab('report');
    }

    // Load suppliers for this session in the background
    apiGetSuppliersBySession(sessionId).then(({ suppliers }) => {
      if (suppliers?.length) renderSuppliers(suppliers);
    }).catch(() => {});

    closeSidebar();
  } catch (e) {
    toast('Could not load report', 'error');
    console.error('[loadReport]', e);
  }
}

async function deleteReport(sessionId) {
  removeHistoryItem(sessionId);
  if (activeSessionId === sessionId) showWelcome();
  try {
    await apiDeleteReport(sessionId);
  } catch (e) {
    console.error('[deleteReport]', e);
  }
}

async function submitQuery() {
  const query = document.getElementById('main-query').value.trim();
  if (!query) return;

  activeSessionId = null;

  showResultsScreen();
  document.getElementById('results-query-label').textContent = query;
  document.getElementById('log-panel').innerHTML             = '';
  document.getElementById('suppliers-grid').innerHTML        = '';
  document.getElementById('report-content').innerHTML        = '<p style="color:var(--muted)">Report generating…</p>';
  document.getElementById('supp-count').textContent          = '';
  document.getElementById('stop-btn').style.display          = '';
  document.getElementById('dl-txt-btn').style.display        = 'none';
  document.getElementById('dl-json-btn').style.display       = 'none';
  document.getElementById('dl-pdf-btn').style.display        = 'none';


  setStatus('running');
  resetProgress();
  showResultTab('live');

  try {
    const reader  = await apiStartQuery(query);
    activeReader  = reader;
    const decoder = new TextDecoder();
    let   buffer  = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (line.startsWith('data: ')) handleSSE(line.slice(6));
      }
    }
  } catch (e) {
    setStatus('error');
    appendLog(`Error: ${e.message}`, 'error');
  }

  loadHistory();
}

function handleSSE(raw) {
  let msg;
  try { msg = JSON.parse(raw); } catch { return; }

  switch (msg.type) {
    case 'session':
      activeSessionId = msg.session_id;
      break;
    case 'log':
      appendLog(msg.message, msg.level);
      advanceProgress();
      break;
    case 'suppliers':
      renderSuppliers(msg.data);
      break;
    case 'done':
      setStatus('done');
      completeProgress();
      document.getElementById('stop-btn').style.display   = 'none';
      document.getElementById('dl-txt-btn').style.display = '';
      document.getElementById('dl-json-btn').style.display = '';
      document.getElementById('dl-json-btn').style.display = '';

      if (msg.report) renderReport(msg.report);
      toast(`Done! ${msg.meta?.suppliers_found ?? 0} suppliers found in ${msg.meta?.elapsed_seconds}s`, 'success');
      break;
    case 'stopped':
      setStatus('stopped');
      document.getElementById('stop-btn').style.display = 'none';
      appendLog('⏹ Pipeline stopped by user.', 'warn');
      break;
    case 'error':
      appendLog(`Error: ${msg.message}`, 'error');
      break;
  }
}

async function stopPipeline() {
  if (!activeSessionId) return;
  try { await apiStop(activeSessionId); } catch {}
  setStatus('stopped');
  document.getElementById('stop-btn').style.display = 'none';
}
