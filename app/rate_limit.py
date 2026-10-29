import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.config import settings


class RateLimiter:
    """Sliding window limiter kept in memory (one process only)."""

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._last_purge = time.monotonic()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        self._purge_stale(now)
        hits = self._hits[key]
        while hits and now - hits[0] >= self.window_seconds:
            hits.popleft()
        if len(hits) >= self.max_requests:
            return False
        hits.append(now)
        return True

    def _purge_stale(self, now: float) -> None:
        """Forget clients that haven't made a request in a full window.

        Without this, every IP ever seen would stay in memory forever.
        Runs at most once per window, so it adds no cost to most requests.
        """
        if now - self._last_purge < self.window_seconds:
            return
        self._last_purge = now
        stale = [
            key
            for key, hits in self._hits.items()
            if not hits or now - hits[-1] >= self.window_seconds
        ]
        for key in stale:
            del self._hits[key]


rate_limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)


# async so it runs on the event loop and the limiter needs no lock.
async def check_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
