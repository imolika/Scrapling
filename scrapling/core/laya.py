"""Laya System 1 Decision & Guardrail Integration for Scrapling.

Provides ultra-fast non-autoregressive pre-fetch engine routing, challenge triage,
and prompt injection defense.
"""

import os
import json
import logging
import urllib.request
from typing import Optional, Dict, Any, Literal

logger = logging.getLogger("scrapling.laya")

DEFAULT_LAYA_URL = os.getenv("LAYA_SERVICE_URL", "http://127.0.0.1:8026")


class LayaScraplingRouter:
    """Pre-fetch engine router and post-fetch challenge triage powered by Laya System 1."""

    def __init__(self, service_url: Optional[str] = None):
        self.service_url = (service_url or DEFAULT_LAYA_URL).rstrip("/")
        self.timeout = 4.0

    def is_available(self) -> bool:
        """Check if Laya server is responding on /health."""
        try:
            req = urllib.request.Request(f"{self.service_url}/health", method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def predict_engine(self, url: str) -> Dict[str, Any]:
        """Predict the most optimal fetching engine (fast, dynamic, stealthy) for a URL."""
        payload = {
            "state": f"Target URL to scrape: {url}",
            "questions": {
                "engine": {
                    "instructions": "Which scraping engine is most appropriate for this target URL? Fast (curl_cffi TLS impersonation for static sites and REST APIs), Dynamic (Playwright headless Chromium for dynamic SPAs), or Stealthy (Camoufox Turnstile solver for Cloudflare or anti-bot protected sites)?",
                    "type": "choice",
                    "criteria": ["fast", "dynamic", "stealthy"]
                },
                "antibot_risk": {
                    "instructions": "Does this target website have active Cloudflare Turnstile, Cloudflare WAF, or anti-bot protection?",
                    "type": "choice",
                    "criteria": ["low", "medium", "high"]
                }
            },
            "min_confidence": 0.5
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.service_url}/v1/systemone",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    res = json.loads(resp.read().decode("utf-8"))
                    answers = res.get("answers", {})
                    engine = answers.get("engine", {}).get("choice", "fast")
                    conf = answers.get("engine", {}).get("answer_confidence", 0.8)
                    risk = answers.get("antibot_risk", {}).get("choice", "low")
                    return {
                        "engine": engine,
                        "confidence": round(conf, 3),
                        "antibot_risk": risk,
                        "source": "laya-system1"
                    }
        except Exception:
            pass

        return {
            "engine": "fast",
            "confidence": 0.8,
            "antibot_risk": "low",
            "source": "heuristic-fallback"
        }

    def triage_challenge(self, status_code: int, page_title: str, html_body: str) -> Dict[str, Any]:
        """Triage whether a scrape result encountered a Cloudflare Turnstile or anti-bot challenge."""
        title_lower = (page_title or "").lower()
        body_lower = (html_body or "")[:3000].lower()
        is_cf = (
            status_code in (403, 429) or
            "just a moment" in title_lower or
            "cf-turnstile" in body_lower or
            "challenges.cloudflare.com" in body_lower
        )
        return {
            "is_challenge": is_cf,
            "challenge_type": "cloudflare_turnstile" if is_cf else "clean",
            "should_escalate_to_stealthy": is_cf
        }

    def scan_rag_safety(self, text: str) -> Dict[str, Any]:
        """Scan extracted markdown for prompt injection triggers before feeding into downstream LLM."""
        triggers = [
            "ignore all previous instructions",
            "ignore previous directions",
            "system prompt override",
            "you are now in developer mode",
            "jailbreak"
        ]
        has_injection = any(t in text[:3000].lower() for t in triggers)
        return {
            "is_safe": not has_injection,
            "risk": "injection_risk" if has_injection else "clean"
        }


def auto_fetch(url: str, **kwargs):
    """Automatically selects the best Scrapling fetcher for a URL using Laya System 1 decision engine.
    
    If the initial fetch hits an anti-bot challenge (403 or Turnstile managed challenge),
    auto_fetch automatically escalates to StealthyFetcher with Turnstile solving.
    """
    from scrapling.fetchers import Fetcher, DynamicFetcher, StealthyFetcher

    router = LayaScraplingRouter()
    pred = router.predict_engine(url)
    engine = pred.get("engine", "fast")

    if engine == "fast":
        page = Fetcher.get(url, **kwargs)
        # Check if challenge encountered
        status = getattr(page, "status", 200)
        title = (page.css("title::text").get() or "").strip()
        body = page.body.decode("utf-8", errors="ignore")[:3000] if hasattr(page, "body") and page.body else ""
        triage = router.triage_challenge(status, title, body)
        if triage["should_escalate_to_stealthy"]:
            logger.info("Laya detected Cloudflare Turnstile; auto-escalating to StealthyFetcher.")
            return StealthyFetcher.fetch(url, solve_cloudflare=True, **kwargs)
        return page

    elif engine == "dynamic":
        return DynamicFetcher.fetch(url, **kwargs)
    else:
        return StealthyFetcher.fetch(url, solve_cloudflare=True, **kwargs)
