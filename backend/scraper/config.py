"""
scraper/config.py — ScraperConfig dataclass
Values are seeded from Config (which reads from .env) so MAX_RESULTS,
SCRAPE_LIMIT, and TIMEOUT are all honoured without repeating env lookups.
"""
from dataclasses import dataclass, field


@dataclass
class ScraperConfig:
    tavily_key: str = ""
    serper_key: str = ""

    # Toggle individual directory sources
    use_indiamart:     bool = True
    use_alibaba:       bool = True
    use_made_in_china: bool = True
    use_thomasnet:     bool = True
    use_europages:     bool = True

    # Tunable at runtime (populated from cfg in ScraperEngine)
    max_results:  int = 10   # results per search source
    scrape_limit: int = 5    # max directory pages to deep-scrape per run
    timeout:      int = 12   # HTTP timeout per request (seconds)

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_key and self.tavily_key.startswith("tvly-"))

    @property
    def has_serper(self) -> bool:
        return bool(self.serper_key)
