# MFG Agent — AI Supplier Finder

A multi-agent system for manufacturing procurement research. Given a plain-English query like *"Find aluminum suppliers in India"*, it searches the web and B2B directories, extracts structured supplier data with an LLM, and produces a professional sourcing report — all streamed live to a chat UI.

---

## Architecture

```
User Query
    │
    ▼
ManufacturingOrchestrator
    │
    ├── ResearcherAgent
    │     ├── Step 1 · Parse query → product + location  (LLM, ~100 tokens)
    │     ├── Step 2 · Scrape web + B2B directories       (pure HTTP, 0 tokens)
    │     └── Step 3 · Extract structured supplier list   (LLM, ~3 000 tokens)
    │                   └── hand-off → PipelineState.mark_handoff()
    │
    └── WriterAgent
          └── Synthesise executive report               (LLM, ~3 000 tokens)
                └── SSE stream → browser chat UI
```

**Key design decisions:**
- `backend/scraper/` is a pure HTTP module with zero LLM dependency — can be used standalone
- `backend/agents/` owns all LLM + orchestration logic

---

## Features

- **Live streaming** — log lines, step indicators, and supplier cards appear in real time via Server-Sent Events (SSE)
- **Multi-source scraping** — IndiaMART, Alibaba, ThomasNet, Europages, Kompass, TradeIndia, ExportersIndia, Made-in-China, GlobalSources + web search
- **Graceful rate-limit handling** — if Groq's token quota is hit mid-pipeline, each step falls back silently instead of crashing:
  - Parse → keyword extraction from query text
  - Extract → raw directory data passed through directly
  - Write → compact report generated in Python without LLM
- **Stop button** — cancels an in-progress run cleanly at any pipeline stage
- **Download reports** — TXT, JSON, or PDF (via browser print) with no files saved to the server
- **CLI mode** — run headless from the terminal

---


## Quick Start

### 1. Clone and install

```bash
git clone [https://github.com/pransu-singhMulti-Agent-Manufacturing-System](https://github.com/Pransu-singh/Multi-Agent-Manufacturing-System).git
cd Multi-Agent-Manufacturing-System
pip install -r requirements.txt
```

### 2. Configure environment

Copy the example and fill in your keys:

```bash
cp .env.example .env
```


> DuckDuckGo search is always enabled as a free fallback — the system works with just `GROQ_API_KEY`.

### 3. Run

**Web UI (recommended):**
```bash
python -m backend
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query` | Start a pipeline. Body: `{"query": "..."}`. Returns SSE stream. |
| `POST` | `/api/stop` | Cancel a running pipeline. Body: `{"session_id": "MFG-..."}`. |
| `GET` | `/api/download/<session_id>` | Download report as `.txt` |
| `GET` | `/api/download-json/<session_id>` | Download full structured data as `.json` |
| `GET` | `/api/health` | Server status, model info, active sources |

### SSE Event Types

The `/api/query` stream emits newline-delimited JSON frames:

```jsonc
{"type": "session",   "session_id": "MFG-1234567890"}
{"type": "log",       "level": "info|success|warn|error|agent|system", "message": "..."}
{"type": "suppliers", "data": [{...}, ...]}
{"type": "done",      "report": "...", "meta": {"elapsed_seconds": 42, ...}}
{"type": "stopped"}
```

---

## Data Sources

| Source | Region | Type |
|--------|--------|------|
| DuckDuckGo | Global | Web search (free, always on) |
| Tavily | Global | AI web search (optional) |
| Serper | Global | Google search (optional) |
| IndiaMART | India | B2B directory |
| TradeIndia | India | B2B directory |
| ExportersIndia | India | B2B directory |
| Alibaba | China / Global | B2B marketplace |
| Made-in-China | China | B2B directory |
| GlobalSources | Asia | B2B directory |
| ThomasNet | USA / Canada | Industrial directory |
| Europages | Europe | B2B directory |
| Kompass | Global | Business directory |

Sources are selected automatically based on the detected location in the query.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | **Required.** Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `TAVILY_API_KEY` | — | Optional Tavily search key |
| `SERPER_API_KEY` | — | Optional Serper search key |
| `PORT` | `5000` | Flask server port |
| `HOST` | `0.0.0.0` | Flask bind address |
| `DEBUG` | `false` | Flask debug mode |
| `TIMEOUT` | `12` | HTTP request timeout (seconds) |
| `MAX_RESULTS` | `10` | Max search results per query |
| `SCRAPE_LIMIT` | `5` | Max pages to deep-scrape |

---

## Groq Rate Limits (Free Tier)

Groq's free tier has token-per-minute (TPM) and token-per-day (TPD) limits. The pipeline makes 3 LLM calls per run — parse (~100 tokens), extract (~3 000 tokens), write (~3 000 tokens). If a limit is hit:

- The affected step skips silently with a fallback (no error shown in the UI)
- A yellow warning appears in the log stream
- The pipeline continues and completes with whatever data it has

Upgrade to Groq's Dev Tier at [console.groq.com/settings/billing](https://console.groq.com/settings/billing) to remove daily limits.

---

## Downloading Reports

After a run completes, three download options appear in the report header:

| Button | Format | Contents |
|--------|--------|----------|
| ⬇ TXT | Plain text | Metadata header + full narrative report |
| ⬇ JSON | JSON | Full structured data including all supplier fields |
| 🖨 PDF | PDF (via browser) | Click → browser print dialog → "Save as PDF" |

Reports are kept in server memory for the duration of the process (max 50 reports, oldest evicted). They are **not** written to disk.

---

## License

MIT
