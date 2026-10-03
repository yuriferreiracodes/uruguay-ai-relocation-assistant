import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.config import get_settings


class RateLimiter:
    """In-memory sliding window per client IP (single-process; fine for the MVP)."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int, window: int) -> bool:
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] >= window:
            hits.popleft()
        if not hits:
            self._hits.pop(key, None)
            hits = self._hits[key]
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


limiter = RateLimiter()


def client_ip(request: Request) -> str:
    if get_settings().trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


async def enforce_rate_limit(request: Request) -> None:
    s = get_settings()
    if not limiter.check(client_ip(request), s.rate_limit_requests, s.rate_limit_window_seconds):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again soon.")
