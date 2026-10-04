import asyncio
import html
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx

from app.config import Settings
from app.knowledge.sources import ALLOWED_DOMAINS, OFFICIAL_CATEGORIES, sources_for
from app.schemas.chat import Source

logger = logging.getLogger(__name__)

MAX_CHARS_PER_SOURCE = 1500


@dataclass
class RetrievedContext:
    text: str | None = None
    sources: list[Source] = field(default_factory=lambda: list[Source]())


def _is_allowed(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == d or host.endswith(f".{d}") for d in ALLOWED_DOMAINS)


def _html_to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|noscript|svg|nav|header|footer)\b.*?</\1>", " ", raw)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", text).strip()


class Retriever:
    """Fetches curated official pages. Only URLs from sources.py are ever requested."""

    def __init__(self, settings: Settings, http: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._http = http
        self._cache: dict[str, tuple[float, str, str]] = {}

    async def retrieve(self, category: str) -> RetrievedContext:
        selected = sources_for(category)
        if not selected:
            return RetrievedContext()
        if category not in OFFICIAL_CATEGORIES:
            # Reference links only: these answers are not grounded in fetched pages, so
            # there is nothing to retrieve and no retrieval date to report.
            return RetrievedContext(sources=[Source(title=s.title, url=s.url) for s in selected])

        results = await asyncio.gather(
            *(self._fetch(s.url) for s in selected), return_exceptions=True
        )
        sources: list[Source] = []
        parts: list[str] = []
        for src, res in zip(selected, results, strict=True):
            if isinstance(res, BaseException) or res is None:
                sources.append(Source(title=src.title, url=src.url))
                continue
            text, retrieved_at = res
            sources.append(Source(title=src.title, url=src.url, retrieved_at=retrieved_at))
            parts.append(f"[{src.title} — {src.url} — retrieved {retrieved_at}]\n{text}")
        return RetrievedContext(text="\n\n".join(parts) or None, sources=sources)

    async def _fetch(self, url: str) -> tuple[str, str] | None:
        if not _is_allowed(url):
            return None
        cached = self._cache.get(url)
        now = time.monotonic()
        if cached and now - cached[0] < self._settings.retrieval_cache_ttl_seconds:
            return cached[1], cached[2]
        try:
            if self._http is not None:
                resp = await self._http.get(url)
            else:
                async with httpx.AsyncClient(
                    timeout=self._settings.retrieval_timeout_seconds, follow_redirects=True
                ) as http:
                    resp = await http.get(url)
            resp.raise_for_status()
            if not _is_allowed(str(resp.url)):
                return None
            text = _html_to_text(resp.text)[:MAX_CHARS_PER_SOURCE]
        except httpx.HTTPError:
            logger.warning("retrieval failed for %s", url)
            return None
        if not text:
            return None
        retrieved_at = datetime.now(UTC).strftime("%Y-%m-%d")
        self._cache[url] = (now, text, retrieved_at)
        return text, retrieved_at
