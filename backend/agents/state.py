"""
agents/state.py — Shared state objects used throughout the pipeline.
"""
import json
import sys
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime


# ─── Stop-signal registry ─────────────────────────────────────────────────────

_stop_events: dict[str, threading.Event] = {}
_stop_lock = threading.Lock()


def register_stop(session_id: str) -> threading.Event:
    ev = threading.Event()
    with _stop_lock:
        _stop_events[session_id] = ev
    return ev


def request_stop(session_id: str) -> bool:
    with _stop_lock:
        ev = _stop_events.get(session_id)
    if ev:
        ev.set()
        return True
    return False


def cleanup_stop(session_id: str):
    with _stop_lock:
        _stop_events.pop(session_id, None)


# ─── StreamLogger ──────────────────────────────────────────────────────────────

class StreamLogger:
    """Dual-output: terminal + SSE queue for the chatbot frontend."""

    def __init__(self, queue=None):
        self.queue = queue
        self.lines: list[dict] = []

    def _emit(self, entry: dict):
        self.lines.append(entry)
        msg = entry.get("message", str(entry))
        print(msg)
        if self.queue:
            self.queue.put(json.dumps(entry))

    def log(self, msg: str, level: str = "info"):
        self._emit({
            "type": "log", "level": level, "message": msg,
            "ts": datetime.utcnow().isoformat(),
        })

    def suppliers(self, data: list):
        self._emit({"type": "suppliers", "data": data})

    def done(self, report: str, meta: dict):
        self._emit({"type": "done", "report": report, "meta": meta})

    def error(self, msg: str):
        self._emit({"type": "error", "message": msg})
        print(f"[ERROR] {msg}", file=sys.stderr)

    def suppliers_raw(self, data):
        """scraper.py compatibility shim."""
        pass


# ─── PipelineState ─────────────────────────────────────────────────────────────

@dataclass
class PipelineState:
    session_id:        str    = field(default_factory=lambda: f"MFG-{int(time.time())}")
    user_id:           str    = ""   # Firebase UID of requesting user
    user_query:        str    = ""
    parsed_product:    str    = ""
    parsed_location:   str    = ""
    scrape_summary:    str    = ""
    raw_results:       list   = field(default_factory=list)
    sources_used:      list   = field(default_factory=list)
    handoff_done:      bool   = False
    handoff_timestamp: str    = ""
    final_report:      str    = ""
    errors:            list   = field(default_factory=list)
    stopped:           bool   = False
    stop_event:        object = field(default=None, repr=False)

    def mark_handoff(self):
        self.handoff_done      = True
        self.handoff_timestamp = datetime.utcnow().isoformat()

    def is_stopped(self) -> bool:
        return self.stopped or (
            self.stop_event is not None and self.stop_event.is_set()
        )

    def to_dict(self) -> dict:
        return {
            "session_id":      self.session_id,
            "user_id":         self.user_id,
            "query":           self.user_query,
            "product":         self.parsed_product,
            "location":        self.parsed_location,
            "sources_used":    self.sources_used,
            "suppliers_found": len(self.raw_results),
            "suppliers":       self.raw_results,
            "report":          self.final_report,
            "errors":          self.errors,
        }
