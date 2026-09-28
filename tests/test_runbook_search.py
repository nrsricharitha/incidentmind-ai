"""Unit tests for runbook search tool."""

import pytest
from src.tools.runbook_search import search_runbooks, get_runbook_by_id


def test_search_connection_pool_exhausted() -> None:
    """Test searching for 'connection pool exhausted' retrieves DB-POOL-004."""
    results = search_runbooks("connection pool exhausted", service="payment-api")
    assert len(results) > 0
    top = results[0]
    assert top["id"] == "DB-POOL-004"
    assert "Database Connection Pool Exhaustion" in top["title"]
    assert len(top["diagnostic_steps"]) > 0
    assert len(top["recommended_remediation"]) > 0


def test_search_cache_unavailable() -> None:
    """Test searching for cache issues retrieves CACHE-003."""
    results = search_runbooks("cache connection refused redis", service="cache-service")
    assert len(results) > 0
    assert any(rb["id"] == "CACHE-003" for rb in results)


def test_get_runbook_by_id() -> None:
    """Test direct runbook lookup by exact ID."""
    rb = get_runbook_by_id("DB-POOL-004")
    assert rb is not None
    assert rb["id"] == "DB-POOL-004"

    missing = get_runbook_by_id("NONEXISTENT-999")
    assert missing is None
