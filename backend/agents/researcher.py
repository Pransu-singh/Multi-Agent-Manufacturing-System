"""
agents/researcher.py — ResearcherAgent
Parses the user query, scrapes supplier data, and structures results.
"""
import json
from groq import Groq
from .base import BaseAgent, RateLimitSkip, PipelineStopped
from .state import PipelineState, StreamLogger
from backend.scraper import ScraperEngine


_PARSE_SYSTEM = """
You are a manufacturing procurement analyst.
Extract the product/material and geographic location from the user's query.
Respond ONLY with valid JSON: {"product": "...", "location": "..."}
If location is not specified, use "Global".
"""

_EXTRACT_SYSTEM = """
You are a manufacturing procurement data extractor.
Given raw search results about suppliers, extract a structured list.
Respond ONLY with a valid JSON array of objects, each with:
{
  "name": "Company Name",
  "location": "City, Country",
  "products": ["product1", "product2"],
  "website": "https://...",
  "contact": "email or phone if found",
  "description": "1-2 sentence description",
  "certifications": ["ISO 9001", ...],
  "min_order": "MOQ if mentioned",
  "source": "where this was found"
}
Include only real companies. If a field is unknown use null.
Return 5-15 of the best, most specific results.
"""


class ResearcherAgent(BaseAgent):
    """
    1. Parse user query → product + location (LLM)
    2. Delegate scraping to ScraperEngine
    3. Extract structured suppliers via LLM
    4. Mark handoff on PipelineState
    """

    def __init__(self, groq_client: Groq, scraper: ScraperEngine):
        super().__init__(groq_client)
        self.scraper = scraper

    # ── public entry point ────────────────────────────────────────────────────

    def run(self, state: PipelineState, logger: StreamLogger) -> PipelineState:
        logger.log("── ResearcherAgent starting ──", "system")

        # 1. Parse query
        state = self._parse_query(state, logger)
        if state.is_stopped():
            return state

        # 2. Scrape
        state = self._scrape(state, logger)
        if state.is_stopped():
            return state

        # 3. Extract suppliers
        state = self._extract_suppliers(state, logger)

        state.mark_handoff()
        logger.log(
            f"ResearcherAgent done — {len(state.raw_results)} suppliers found",
            "success",
        )
        return state

    # ── private helpers ───────────────────────────────────────────────────────

    def _parse_query(self, state: PipelineState, logger: StreamLogger) -> PipelineState:
        logger.log("Parsing query with LLM…", "info")
        try:
            raw = self.call_llm(
                _PARSE_SYSTEM,
                state.user_query,
                max_tokens=256,
                stop_event=state.stop_event,
            )
            parsed = self.parse_json(raw) or {}
            state.parsed_product  = parsed.get("product",  state.user_query)
            state.parsed_location = parsed.get("location", "Global")
            logger.log(f"  Product : {state.parsed_product}",  "info")
            logger.log(f"  Location: {state.parsed_location}", "info")
        except RateLimitSkip as e:
            logger.log(f"Rate limit on query parse — using raw query: {e}", "warn")
            state.parsed_product  = state.user_query
            state.parsed_location = "Global"
        except PipelineStopped:
            state.stopped = True
        return state

    def _scrape(self, state: PipelineState, logger: StreamLogger) -> PipelineState:
        search_query = f"{state.parsed_product} suppliers manufacturers {state.parsed_location}"
        logger.log(f"Scraping: {search_query}", "info")
        try:
            result = self.scraper.run(search_query, logger, stop_event=state.stop_event)
            state.scrape_summary = result.get("summary", "")
            state.sources_used   = result.get("sources_used", [])
        except PipelineStopped:
            state.stopped = True
        except Exception as e:
            logger.log(f"Scrape error: {e}", "error")
            state.errors.append(str(e))
        return state

    def _extract_suppliers(
        self, state: PipelineState, logger: StreamLogger
    ) -> PipelineState:
        if not state.scrape_summary:
            logger.log("No scrape data to extract from.", "warn")
            return state

        logger.log("Extracting structured suppliers from scraped data…", "info")
        prompt = (
            f"User query: {state.user_query}\n"
            f"Product: {state.parsed_product}\n"
            f"Location: {state.parsed_location}\n\n"
            f"Raw data:\n{state.scrape_summary[:12000]}"
        )
        try:
            raw = self.call_llm(
                _EXTRACT_SYSTEM,
                prompt,
                max_tokens=3000,
                stop_event=state.stop_event,
            )
            suppliers = self.parse_json(raw)
            if isinstance(suppliers, list):
                state.raw_results = suppliers
                logger.suppliers(suppliers)
            else:
                logger.log("LLM returned non-list for suppliers — skipping.", "warn")
        except RateLimitSkip as e:
            logger.log(f"Rate limit on supplier extraction: {e}", "warn")
            state.errors.append(f"RateLimit: {e}")
        except PipelineStopped:
            state.stopped = True
        except Exception as e:
            logger.log(f"Extraction error: {e}", "error")
            state.errors.append(str(e))
        return state
