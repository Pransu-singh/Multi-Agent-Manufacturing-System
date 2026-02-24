"""
scraper/sources/tavily.py — Tavily search API.
"""
from __future__ import annotations
import threading
import requests


def tavily_search(
    query: str,
    api_key: str,
    max_results: int = 10,
    stop_event: threading.Event = None,
) -> list[dict]:
    """
    Call Tavily Search API. Returns list of {title, url, content, score}.
    """
    if stop_event and stop_event.is_set():
        return []
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "include_raw_content": False,
                "search_depth": "advanced",
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except Exception as e:
        return []
