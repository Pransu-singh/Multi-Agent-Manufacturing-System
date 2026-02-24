# backend/db/store.py

from supabase import create_client
from backend.config import cfg
from datetime import datetime

_client = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_SERVICE_ROLE_KEY)

class SupabaseStore:

    # ── Suppliers ─────────────────────

    def save_suppliers(self, session_id, user_id, query, suppliers):
        rows = []
        for s in suppliers:
            rows.append({
                "id": f"{session_id}_{hash(s.get('name',''))}",
                "session_id": session_id,
                "user_id": user_id,
                "query": query,
                "name": s.get("name"),
                "location": s.get("location"),
                "products": s.get("products"),
                "website": s.get("website"),
                "contact": s.get("contact"),
                "description": s.get("description"),
                "certifications": s.get("certifications"),
                "min_order": s.get("min_order"),
                "source": s.get("source"),
            })
        _client.table("suppliers").upsert(rows).execute()

    def get_user_suppliers(self, user_id, limit=100, session_id=None):
        q = _client.table("suppliers").select("*").eq("user_id", user_id)
        if session_id:
            q = q.eq("session_id", session_id)
        return q.limit(limit).execute().data or []

    # ── Reports ─────────────────────

    def save_report(self, state_dict, elapsed=0):
        _client.table("reports").upsert({
            "session_id": state_dict["session_id"],
            "user_id": state_dict.get("user_id"),
            "query": state_dict.get("query"),
            "product": state_dict.get("product"),
            "location": state_dict.get("location"),
            "report_text": state_dict.get("report"),
            "suppliers_found": state_dict.get("suppliers_found"),
            "sources_used": ",".join(state_dict.get("sources_used", [])),
            "elapsed_seconds": elapsed,
        }).execute()

    def get_report(self, session_id):
        r = _client.table("reports").select("*").eq("session_id", session_id).execute()
        return r.data[0] if r.data else None

    def get_user_reports(self, user_id, limit=50):
        r = _client.table("reports").select("*").eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit).execute()
        return r.data or []

    def delete_report(self, session_id):
        _client.table("reports").delete().eq("session_id", session_id).execute()
        _client.table("suppliers").delete().eq("session_id", session_id).execute()
        _client.table("history").delete().eq("session_id", session_id).execute()

    # ── History ─────────────────────

    def log_query(self, user_id, query, session_id):
        _client.table("history").upsert({
            "id": f"{user_id}_{session_id}",
            "user_id": user_id,
            "query": query,
            "session_id": session_id,
        }).execute()

    def get_user_history(self, user_id, limit=20):
        r = _client.table("history").select("*").eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit).execute()
        return r.data or []

    def get_stats(self):
        return {
            "total_suppliers": len(_client.table("suppliers").select("id").execute().data),
            "total_reports": len(_client.table("reports").select("session_id").execute().data),
            "total_queries": len(_client.table("history").select("id").execute().data),
        }

_store = SupabaseStore()

def get_store():
    return _store