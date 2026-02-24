"""
auth/firebase.py — Firebase Admin SDK integration.
Loads credentials from backend/firebase_key.json (gitignored).

Usage in Flask routes:
    @app.route("/api/query", methods=["POST"])
    @require_auth
    def query_endpoint(user: dict):
        user_id = user["uid"]
        ...
"""
from __future__ import annotations
import os
from functools import wraps

from flask import request, jsonify


# ── Firebase Admin init ───────────────────────────────────────────────────────

_firebase_initialized = False

# Absolute path to the key file sitting next to this file's parent (backend/)
_KEY_PATH = os.path.join(os.path.dirname(__file__), "..", "firebase_key.json")
_KEY_PATH = os.path.normpath(_KEY_PATH)


def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return

    import firebase_admin
    from firebase_admin import credentials
    import json
    import base64

    if firebase_admin._apps:
        _firebase_initialized = True
        return

    firebase_b64 = os.getenv("FIREBASE_CREDENTIALS_B64")

    if not firebase_b64:
        raise RuntimeError(
            "FIREBASE_CREDENTIALS_B64 environment variable is not set."
        )

    try:
        firebase_dict = json.loads(
            base64.b64decode(firebase_b64).decode("utf-8")
        )
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        print("[Auth] Firebase initialized from base64 env")
    except Exception as e:
        raise RuntimeError(f"Invalid FIREBASE_CREDENTIALS_B64: {e}")

def verify_token(id_token: str) -> dict | None:
    """
    Verify a Firebase ID token.
    Returns decoded token dict (uid, email, name, …) or None on failure.
    """
    try:
        _init_firebase()
        from firebase_admin import auth
        return auth.verify_id_token(id_token)
    except Exception as e:
        print(f"[Auth] Token verification failed: {e}")
        return None


# ── Flask decorators ──────────────────────────────────────────────────────────

def require_auth(f):
    """
    Enforces authentication. Injects `user` dict as first arg to the route.
    Expects header:  Authorization: Bearer <firebase-id-token>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        id_token = auth_header[len("Bearer "):]
        user = verify_token(id_token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(user, *args, **kwargs)
    return decorated


def optional_auth(f):
    """Passes user=None if not authenticated instead of rejecting."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            user = verify_token(auth_header[len("Bearer "):])
        return f(user, *args, **kwargs)
    return decorated
