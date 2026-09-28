"""Deterministic unit tests for all IncidentMind AI agent tools."""

import pytest
from src.tools.log_analyzer import analyze_logs
from src.tools.runbook_search import search_runbooks, get_runbook_by_id
from src.tools.service_inspector import inspect_service
from src.tools.incident_patterns import compare_incident_patterns
from src.tools.report_generator import generate_incident_report


def test_tool_analyze_logs() -> None:
    """Verify analyze_logs extracts expected signatures."""
    logs = "2026-09-01 10:00:00 ERROR database: connection pool exhausted"
    res = analyze_logs(logs, service_name="database")
    assert "Connection Pool Exhaustion" in res["error_patterns"]
    assert "database" in res["affected_components"]
    assert len(res["evidence_excerpts"]) == 1


def test_tool_search_runbooks() -> None:
    """Verify search_runbooks returns matching runbook."""
    res = search_runbooks("HikariPool connection timeout", service="database")
    assert len(res) > 0
    assert res[0]["id"] == "DB-POOL-004"


def test_tool_inspect_service_safe_simulation() -> None:
    """Verify inspect_service returns simulated data and sets simulated flag."""
    res = inspect_service("payment-api")
    assert res["service_name"] == "payment-api"
    assert res["simulated"] is True
    assert "latency_ms" in res
    assert "connection_state" in res

    # Unknown service fallback
    unknown = inspect_service("unknown-service-xyz")
    assert unknown["simulated"] is True
    assert unknown["status"] == "HEALTHY"


def test_tool_compare_incident_patterns_high_similarity() -> None:
    """Verify compare_incident_patterns detects overlap and computes similarity."""
    current_symptoms = [
        "database connection timeout",
        "failed to obtain DB connection",
    ]
    historical_context = (
        "Previous incident INC-1001 for payment-api involved database connection timeout "
        "and failed to acquire database connection."
    )
    res = compare_incident_patterns(
        current_symptoms=current_symptoms,
        current_service="payment-api",
        historical_context=historical_context,
    )
    assert res["similarity_score"] > 0.5
    assert "INC-1001" in res["historical_incident_ids"]
    assert len(res["shared_symptoms"]) > 0
    assert "High similarity" in res["relevance_assessment"] or "Moderate similarity" in res["relevance_assessment"]


def test_tool_compare_incident_patterns_empty_history() -> None:
    """Verify compare_incident_patterns handles absent historical context."""
    res = compare_incident_patterns(
        current_symptoms=["symptom-a"],
        current_service="svc",
        historical_context="",
    )
    assert res["similarity_score"] == 0.0
    assert "No historical context" in res["key_differences"][0]


def test_tool_generate_incident_report() -> None:
    """Verify generate_incident_report produces valid report payload."""
    report = generate_incident_report(
        incident_id="INC-1001",
        title="DB Failure",
        severity="HIGH",
        affected_service="payment-api",
        summary="DB pool saturated",
        evidence=["Log excerpt 1"],
        root_cause="Pool exhaustion",
        confidence="HIGH",
        recommended_actions=["Restart", "Patch leak"],
        runbook="DB-POOL-004",
    )
    assert report["incident_id"] == "INC-1001"
    assert report["confidence"] == "HIGH"
    assert report["runbook"] == "DB-POOL-004"
    assert "generated_at" in report
