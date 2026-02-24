"""
scraper/sources/directories.py — B2B manufacturer directory scrapers.
Covers: IndiaMART, Alibaba, Made-in-China, ThomasNet, Europages.
"""
from __future__ import annotations
import re
import threading
import urllib.parse
from backend.scraper.parser import fetch_html, extract_text


def _search_url(base: str, query: str) -> str:
    return f"{base}{urllib.parse.quote_plus(query)}"


def scrape_indiamart(query: str, timeout: int = 12, stop_event: threading.Event = None) -> str:
    if stop_event and stop_event.is_set():
        return ""
    url = _search_url(
        "https://dir.indiamart.com/search.mp?ss=", query
    )
    html = fetch_html(url, timeout=timeout)
    return extract_text(html) if html else ""


def scrape_alibaba(query: str, timeout: int = 12, stop_event: threading.Event = None) -> str:
    if stop_event and stop_event.is_set():
        return ""
    url = _search_url(
        "https://www.alibaba.com/trade/search?SearchText=", query
    )
    html = fetch_html(url, timeout=timeout)
    return extract_text(html) if html else ""


def scrape_made_in_china(query: str, timeout: int = 12, stop_event: threading.Event = None) -> str:
    if stop_event and stop_event.is_set():
        return ""
    url = _search_url(
        "https://www.made-in-china.com/multi-search/", query
    ) + "/F0/1.html"
    html = fetch_html(url, timeout=timeout)
    return extract_text(html) if html else ""


def scrape_thomasnet(query: str, timeout: int = 12, stop_event: threading.Event = None) -> str:
    if stop_event and stop_event.is_set():
        return ""
    url = _search_url(
        "https://www.thomasnet.com/search/?searchTerm=", query
    )
    html = fetch_html(url, timeout=timeout)
    return extract_text(html) if html else ""


def scrape_europages(query: str, timeout: int = 12, stop_event: threading.Event = None) -> str:
    if stop_event and stop_event.is_set():
        return ""
    url = _search_url(
        "https://www.europages.co.uk/en/search?q=", query
    )
    html = fetch_html(url, timeout=timeout)
    return extract_text(html) if html else ""


_DIRECTORY_SCRAPERS = {
    "IndiaMART":     scrape_indiamart,
    "Alibaba":       scrape_alibaba,
    "Made-in-China": scrape_made_in_china,
    "ThomasNet":     scrape_thomasnet,
    "Europages":     scrape_europages,
}


def scrape_directories(
    query: str,
    enabled: dict[str, bool] = None,
    scrape_limit: int = 5,
    timeout: int = 12,
    stop_event: threading.Event = None,
) -> dict[str, str]:
    """
    Scrape enabled B2B directories in parallel (threads).
    Returns {directory_name: text_content}.
    """
    if enabled is None:
        enabled = {k: True for k in _DIRECTORY_SCRAPERS}

    results: dict[str, str] = {}
    lock = threading.Lock()

    def _run(name, fn):
        if stop_event and stop_event.is_set():
            return
        if not enabled.get(name, False):
            return
        try:
            text = fn(query, timeout=timeout, stop_event=stop_event)
            if text:
                with lock:
                    results[name] = text
        except Exception:
            pass

    threads = [
        threading.Thread(target=_run, args=(name, fn), daemon=True)
        for name, fn in _DIRECTORY_SCRAPERS.items()
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    return results
