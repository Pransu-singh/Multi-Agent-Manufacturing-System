"""
agents/base.py — Base agent class and shared LLM utilities.
"""
import re
import json
import threading
from groq import Groq
from backend.config import cfg


class RateLimitSkip(Exception):
    """Raised when Groq 429 rate-limit is hit — caller should degrade gracefully."""


class PipelineStopped(Exception):
    """Raised when user presses Stop."""


def call_groq(
    client: Groq,
    system: str,
    user: str,
    max_tokens: int = 2048,
    temperature: float = 0.3,
    stop_event: threading.Event = None,
) -> str:
    """
    Call Groq LLM.
    • Raises RateLimitSkip on 429 so callers can continue with fallback.
    • Raises PipelineStopped when stop_event is set.
    """
    if stop_event and stop_event.is_set():
        raise PipelineStopped()
    try:
        resp = client.chat.completions.create(
            model=cfg.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        msg = str(e)
        if "429" in msg or "rate_limit" in msg.lower() or "rate limit" in msg.lower():
            raise RateLimitSkip(msg)
        raise


def parse_json_llm(raw: str) -> list | dict | None:
    """Strip markdown fences and parse the first JSON object/array from LLM output."""
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        return json.loads(clean)
    except Exception:
        m = re.search(r"(\[.*\]|\{.*\})", clean, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None


class BaseAgent:
    """Minimal base class: holds a Groq client, exposes call_llm / parse_json."""

    def __init__(self, groq_client: Groq):
        self.groq = groq_client

    def call_llm(self, system: str, user: str, **kwargs) -> str:
        return call_groq(self.groq, system, user, **kwargs)

    def parse_json(self, raw: str):
        return parse_json_llm(raw)
