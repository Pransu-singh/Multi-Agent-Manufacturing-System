"""
scraper/engine.py — ScraperEngine
Orchestrates all search sources and aggregates text for LLM ingestion.
"""
from __future__ import annotations
import threading
from .config import ScraperConfig
from .sources.duckduckgo import ddg_search
from .sources.tavily import tavily_search
from .sources.serper import serper_search
from .sources.directories import scrape_directories


class ScraperEngine:
    """
    Runs multiple search sources in parallel and returns a combined summary
    string ready to be fed to the LLM researcher.
    """

    def __init__(self, config: ScraperConfig, logger=None):
        self.cfg    = config
        self.logger = logger   # StreamLogger — injected per-run by orchestrator

    def _log(self, msg: str, level: str = "info"):
        if self.logger:
            self.logger.log(msg, level)
        else:
            print(f"[{level.upper()}] {msg}")

    def run(
        self,
        query: str,
        logger=None,
        stop_event: threading.Event = None,
    ) -> dict:
        """
        Run all enabled sources. Returns:
          {"summary": str, "sources_used": list[str]}
        """
        if logger:
            self.logger = logger

        chunks: list[str] = []
        sources_used: list[str] = []

        # ── 1. Premium search APIs ────────────────────────────────────────────
        if self.cfg.has_tavily:
            self._log("Searching Tavily…", "info")
            results = tavily_search(query, self.cfg.tavily_key, max_results=self.cfg.max_results, stop_event=stop_event)
            if results:
                text = self._format_search_results(results, key_url="url", key_body="content")
                chunks.append(f"=== TAVILY RESULTS ===\n{text}")
                sources_used.append("Tavily")
                self._log(f"  Tavily: {len(results)} results", "success")

        if self.cfg.has_serper:
            self._log("Searching Serper…", "info")
            results = serper_search(query, self.cfg.serper_key, max_results=self.cfg.max_results, stop_event=stop_event)
            if results:
                text = self._format_search_results(results, key_url="url", key_body="content")
                chunks.append(f"=== SERPER RESULTS ===\n{text}")
                sources_used.append("Serper")
                self._log(f"  Serper: {len(results)} results", "success")

        # ── 2. DuckDuckGo fallback ────────────────────────────────────────────
        if not sources_used or True:   # always run DDG for coverage
            self._log("Searching DuckDuckGo…", "info")
            results = ddg_search(query, max_results=self.cfg.max_results, stop_event=stop_event)
            if results:
                text = self._format_search_results(results, key_url="href", key_body="body")
                chunks.append(f"=== DUCKDUCKGO RESULTS ===\n{text}")
                sources_used.append("DuckDuckGo")
                self._log(f"  DuckDuckGo: {len(results)} results", "success")

        # ── 3. B2B Directories ────────────────────────────────────────────────
        enabled_dirs = {
            "IndiaMART":     self.cfg.use_indiamart,
            "Alibaba":       self.cfg.use_alibaba,
            "Made-in-China": self.cfg.use_made_in_china,
            "ThomasNet":     self.cfg.use_thomasnet,
            "Europages":     self.cfg.use_europages,
        }
        self._log("Scraping B2B directories…", "info")
        dir_results = scrape_directories(query, enabled=enabled_dirs, scrape_limit=self.cfg.scrape_limit, timeout=self.cfg.timeout, stop_event=stop_event)
        for name, text in dir_results.items():
            if text.strip():
                chunks.append(f"=== {name.upper()} ===\n{text}")
                sources_used.append(name)
                self._log(f"  {name}: scraped {len(text)} chars", "success")

        if not chunks:
            self._log("No results from any source.", "warn")
            return {"summary": "", "sources_used": []}

        summary = "\n\n".join(chunks)
        self._log(
            f"Scraping complete — {len(summary):,} chars from {len(sources_used)} sources",
            "success",
        )
        return {"summary": summary, "sources_used": sources_used}

    @staticmethod
    def _format_search_results(
        results: list[dict],
        key_url: str = "url",
        key_body: str = "content",
    ) -> str:
        lines = []
        for r in results:
            title = r.get("title", "")
            url   = r.get(key_url, "")
            body  = r.get(key_body, "")
            lines.append(f"• {title}\n  URL: {url}\n  {body}\n")
        return "\n".join(lines)
