"""Additional behavioral checks; original grading tests remain unchanged."""
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException
from pydantic import ValidationError
import pytest


def test_concurrent_requests_cannot_overrun_rate_limit(fake_redis):
    from app.rate_limiter import RateLimiter
    limiter = RateLimiter(fake_redis, 5)

    def attempt(_):
        try:
            limiter.check("parallel", now=1000)
            return 200
        except HTTPException as error:
            return error.status_code

    with ThreadPoolExecutor(max_workers=12) as pool:
        statuses = list(pool.map(attempt, range(30)))
    assert statuses.count(200) == 5
    assert statuses.count(429) == 25
    assert limiter.hit_count("parallel", now=1000) == 5


def test_blocked_budget_does_not_call_llm(client, fake_redis, auth_headers, monkeypatch):
    from app import main
    from app.cost_guard import CostGuard
    fake_redis.set(CostGuard._key("sv-test"), "100")

    def unexpected_call(*args):
        pytest.fail("LLM must not run after budget rejection")

    monkeypatch.setattr(main, "ask_llm", unexpected_call)
    assert client.post("/ask", headers=auth_headers, json={"question": "Hi"}).status_code == 402


def test_blank_secret_is_rejected(monkeypatch):
    from app.config import Settings
    monkeypatch.setenv("AGENT_API_KEY", "")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_monthly_cost_buckets_are_independent(fake_redis):
    from app.cost_guard import CostGuard, KEY_TTL_SECONDS
    guard = CostGuard(fake_redis, 1)
    guard.record("u", 2, month="2026-08")
    guard.check("u", estimated_cost=0.5, month="2026-09")
    assert 0 < fake_redis.ttl(guard._key("u", "2026-08")) <= KEY_TTL_SECONDS
