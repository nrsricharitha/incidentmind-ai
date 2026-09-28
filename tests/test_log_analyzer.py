"""Unit tests for deterministic log analyzer tool."""

import pytest
from src.tools.log_analyzer import analyze_logs


def test_analyze_database_connection_pool_logs() -> None:
    """Test log analysis against database connection pool logs."""
    logs = """
    2026-09-01 10:02:14 ERROR payment-api: failed to acquire database connection
    2026-09-01 10:02:16 ERROR payment-api: connection pool exhausted
    2026-09-01 10:02:19 WARN payment-api: request timeout
    2026-09-01 10:02:21 ERROR payment-api: database connection acquisition timeout
    """
    result = analyze_logs(logs, service_name="payment-api")

    assert "Connection Pool Exhaustion" in result["error_patterns"]
    assert "Database Connection Acquisition Failure" in result["error_patterns"]
    assert "payment-api" in result["affected_components"]
    assert "ERROR" in result["severity_indicators"]
    assert "WARN" in result["severity_indicators"]
    assert len(result["evidence_excerpts"]) > 0


def test_analyze_empty_logs() -> None:
    """Test log analysis with empty or whitespace-only input."""
    result = analyze_logs("", service_name="auth-service")
    assert result["error_patterns"] == []
    assert result["evidence_excerpts"] == []
    assert result["affected_components"] == ["auth-service"]


def test_analyze_repeated_messages() -> None:
    """Test message frequency deduplication."""
    logs = """
    ERROR svc: connection timed out
    ERROR svc: connection timed out
    ERROR svc: connection timed out
    ERROR svc: other error
    """
    result = analyze_logs(logs)
    repeated = result["repeated_messages"]
    assert len(repeated) > 0
    top = repeated[0]
    assert "connection timed out" in top["message"]
    assert top["count"] == 3
