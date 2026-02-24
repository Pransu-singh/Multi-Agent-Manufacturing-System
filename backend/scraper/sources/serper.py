"""
scraper/sources/serper.py — Serper.dev Google search API.
"""
from __future__ import annotations
import threading
import requests


def serper_search(
    query: str,
    api_key: str,
    max_results: int = 10,
    stop_event: threading.Event = None,
) -> list[dict]:
    """
    Call Serper.dev. Returns list of {title, link, snippet}.
    """
    if stop_event and stop_event.is_set():
        return []
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": max_results},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        organic = data.get("organic", [])
        return [
            {"title": r.get("title"), "url": r.get("link"), "content": r.get("snippet")}
            for r in organic
        ]
    except Exception:
        return []
