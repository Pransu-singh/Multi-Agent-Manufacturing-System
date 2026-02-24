/**
 * js/firebase.js
 * Firebase initialisation + auth state + token helpers.
 * Loaded by both index.html and app.html.
 */

// ── CONFIG — replace with your Firebase project values ────────────────────
const FIREBASE_CONFIG = {
  apiKey:            "AIzaSyC0S-GrZN-1nZLDqH-IBVspHZphuWfcyjM",
  authDomain:        "mfg-agent.firebaseapp.com",
  projectId:         "mfg-agent",
  storageBucket:     "mfg-agent.firebasestorage.app",
  messagingSenderId: "104667935709",
  appId:             "1:104667935709:web:62c234838c226ded693c34",
};

// ── Backend base URL ───────────────────────────────────────────────────────
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:5000'
  : '';

// ── Init ───────────────────────────────────────────────────────────────────
firebase.initializeApp(FIREBASE_CONFIG);
const auth = firebase.auth();

let currentUser      = null;
let currentIdToken   = null;

// ── Token helpers ──────────────────────────────────────────────────────────
async function getToken() {
  if (currentUser) {
    currentIdToken = await currentUser.getIdToken();
    return currentIdToken;
  }
  return null;
}

async function apiHeaders() {
  const token = await getToken();
  return {
    'Content-Type':  'application/json',
    'Authorization': `Bearer ${token}`,
  };
}

// ── Auth actions ───────────────────────────────────────────────────────────
function signInWithGoogle() {
  const provider = new firebase.auth.GoogleAuthProvider();
  auth.signInWithPopup(provider).catch(e => {
    console.error('[Auth]', e);
    if (typeof toast === 'function') toast(e.message, 'error');
  });
}

function signOut() {
  auth.signOut().catch(e => {
    if (typeof toast === 'function') toast(e.message, 'error');
  });
}
