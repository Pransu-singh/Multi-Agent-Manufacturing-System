"""
agents/orchestrator.py — ManufacturingOrchestrator
Wires together Scraper → Researcher → Writer.
Also manages the in-memory report store.
"""
import time
import threading
from groq import Groq
from backend.config import cfg
from backend.scraper import ScraperEngine, ScraperConfig
from .state import PipelineState, StreamLogger, register_stop, cleanup_stop
from .researcher import ResearcherAgent
from .writer import WriterAgent

# ── In-memory report store (max 200 entries, oldest evicted) ─────────────────

_report_store: dict[str, dict] = {}
_REPORT_STORE_MAX = 200


def _store_report(session_id: str, data: dict):
    if len(_report_store) >= _REPORT_STORE_MAX:
        oldest = next(iter(_report_store))
        _report_store.pop(oldest, None)
    _report_store[session_id] = data


def get_report(session_id: str) -> dict | None:
    return _report_store.get(session_id)


# ── Orchestrator ──────────────────────────────────────────────────────────────

class ManufacturingOrchestrator:
    """
    Thread-safe orchestrator. Each call to .run() is independent.
    """

    def __init__(self):
        if not cfg.GROQ_API_KEY:
            raise EnvironmentError(
                "GROQ_API_KEY not set. Add it to your .env file."
            )

        groq_client = Groq(api_key=cfg.GROQ_API_KEY)
        scraper_cfg = ScraperConfig(
            tavily_key=cfg.TAVILY_API_KEY,
            serper_key=cfg.SERPER_API_KEY,
            max_results=cfg.MAX_RESULTS,
            scrape_limit=cfg.SCRAPE_LIMIT,
            timeout=cfg.TIMEOUT,
        )

        scraper = ScraperEngine(scraper_cfg)
        self.groq        = groq_client
        self.scraper_cfg = scraper_cfg
        self.researcher  = ResearcherAgent(groq_client, scraper)
        self.writer      = WriterAgent(groq_client)

    def run(
        self,
        user_query: str,
        logger: StreamLogger = None,
        user_id: str = "",
    ) -> PipelineState:
        logger = logger or StreamLogger()

        # Inject live logger into scraper
        self.researcher.scraper.logger = logger

        state            = PipelineState(user_query=user_query, user_id=user_id)
        state.stop_event = register_stop(state.session_id)
        t0               = time.time()

        logger.log(f"SESSION : {state.session_id}", "system")
        logger.log(f"QUERY   : {user_query}",       "system")
        logger.log(f"MODEL   : {cfg.GROQ_MODEL}",   "system")
        logger._emit({"type": "session", "session_id": state.session_id})

        if self.scraper_cfg.has_tavily:
            logger.log("  Search: Tavily ✓", "success")
        if self.scraper_cfg.has_serper:
            logger.log("  Search: Serper ✓", "success")
        logger.log("  Search: DuckDuckGo ✓ (fallback)", "info")

        try:
            state = self.researcher.run(state, logger)
            if not state.is_stopped():
                state = self.writer.run(state, logger)
        finally:
            cleanup_stop(state.session_id)

        if state.is_stopped():
            logger.log("Pipeline stopped by user.", "warn")
            logger._emit({"type": "stopped"})

        elapsed = round(time.time() - t0, 1)
        logger.log(f"Pipeline complete in {elapsed}s", "success")

        report_data = {
            **state.to_dict(),
            "elapsed_seconds": elapsed,
        }
        _store_report(state.session_id, report_data)

        logger.done(state.final_report, {
            "session_id":      state.session_id,
            "elapsed_seconds": elapsed,
            "suppliers_found": len(state.raw_results),
            "sources_used":    state.sources_used,
        })
        return state
