"""
scraper/parser.py — HTML parsing utilities
"""
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch_html(url: str, timeout: int = 12) -> str | None:
    """Fetch a URL and return raw HTML text, or None on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception:
        return None


def extract_text(html: str, max_chars: int = 8000) -> str:
    """Strip tags and return clean text (truncated)."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:max_chars]


def extract_emails(text: str) -> list[str]:
    return list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)))


def extract_phones(text: str) -> list[str]:
    return list(set(re.findall(r"[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]", text)))
