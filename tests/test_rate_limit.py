import pytest

from app import rate_limit
from app.rate_limit import RateLimiter


@pytest.fixture
def clock(monkeypatch):
    """A fake monotonic clock the test can move forward."""
    now = [1000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: now[0])
    return now


def test_limit_resets_after_the_window(clock):
    limiter = RateLimiter(max_requests=1, window_seconds=60)

    assert limiter.allow("a") is True
    assert limiter.allow("a") is False

    clock[0] += 61

    assert limiter.allow("a") is True


def test_clients_have_independent_limits(clock):
    limiter = RateLimiter(max_requests=1, window_seconds=60)

    assert limiter.allow("a") is True
    assert limiter.allow("b") is True
    assert limiter.allow("a") is False


def test_stale_clients_are_forgotten(clock):
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    limiter.allow("a")
    limiter.allow("b")
    assert set(limiter._hits) == {"a", "b"}

    clock[0] += 61
    limiter.allow("c")

    assert set(limiter._hits) == {"c"}


def test_active_clients_are_not_forgotten(clock):
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    limiter.allow("a")
    clock[0] += 50
    limiter.allow("a")
    clock[0] += 20  # 70s since the first hit, 20s since the last one
    limiter.allow("b")

    assert "a" in limiter._hits
