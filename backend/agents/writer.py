"""
agents/writer.py — WriterAgent
Consumes structured supplier data and generates a polished procurement report.
"""
from groq import Groq
from .base import BaseAgent, RateLimitSkip, PipelineStopped
from .state import PipelineState, StreamLogger

_WRITER_SYSTEM = """
You are a senior manufacturing procurement consultant writing a report for a client.
Given structured supplier data, write a professional Markdown sourcing report that includes:

1. **Executive Summary** — 2-3 sentences covering what was found
2. **Supplier Profiles** — One section per supplier with name, location, products,
   certifications, MOQ, website, and why they are relevant
3. **Comparison Table** — Markdown table: Supplier | Location | Products | Certifications | MOQ | Website
4. **Recommendations** — Top 3 picks with reasoning
5. **Next Steps** — How to proceed (RFQ, factory visit, sample order)

Be specific, factual, and professional. Use the data provided; do not invent details.
Format everything in clean GitHub-flavored Markdown.
"""


class WriterAgent(BaseAgent):
    """Generates the final procurement report from structured supplier data."""

    def __init__(self, groq_client: Groq):
        super().__init__(groq_client)

    def run(self, state: PipelineState, logger: StreamLogger) -> PipelineState:
        logger.log("── WriterAgent starting ──", "system")

        if not state.raw_results:
            logger.log("No supplier data to write a report from.", "warn")
            state.final_report = "_No suppliers found — try broadening your search._"
            return state

        logger.log(f"Writing report for {len(state.raw_results)} suppliers…", "info")

        import json
        user_prompt = (
            f"Query: {state.user_query}\n"
            f"Product: {state.parsed_product}\n"
            f"Location: {state.parsed_location}\n\n"
            f"Suppliers:\n{json.dumps(state.raw_results, indent=2, ensure_ascii=False)}"
        )

        try:
            report = self.call_llm(
                _WRITER_SYSTEM,
                user_prompt,
                max_tokens=4096,
                temperature=0.4,
                stop_event=state.stop_event,
            )
            state.final_report = report
            logger.log("Report written successfully.", "success")
        except RateLimitSkip as e:
            logger.log(f"Rate limit on report generation: {e}", "warn")
            # Fallback: plain list
            lines = [f"# Supplier Sourcing Report\n\n**Query:** {state.user_query}\n"]
            for s in state.raw_results:
                lines.append(
                    f"## {s.get('name','Unknown')}\n"
                    f"- **Location:** {s.get('location','N/A')}\n"
                    f"- **Products:** {', '.join(s.get('products',[]))}\n"
                    f"- **Website:** {s.get('website','N/A')}\n"
                )
            state.final_report = "\n".join(lines)
            state.errors.append(f"RateLimit: {e}")
        except PipelineStopped:
            state.stopped = True
        except Exception as e:
            logger.log(f"Writer error: {e}", "error")
            state.errors.append(str(e))

        logger.log("── WriterAgent done ──", "system")
        return state
