"""
scraper/sources/duckduckgo.py — DuckDuckGo free search (always available).
"""
from __future__ import annotations
import threading


def ddg_search(query: str, max_results: int = 10, stop_event: threading.Event = None) -> list[dict]:
    """
    Run a DuckDuckGo text search and return a list of result dicts.
    Each dict: {title, href, body}
    """
    if stop_event and stop_event.is_set():
        return []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddg:
            results = list(ddg.text(query, max_results=max_results))
        return results or []
    except Exception as e:
        return []
