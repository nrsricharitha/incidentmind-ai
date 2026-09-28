"""Unit tests for Pydantic incident schemas and validation."""

import pytest
from pydantic import ValidationError
from src.agent.schemas import (
    Incident,
    IncidentReport,
    MemoryEntry,
    Severity,
    IncidentStatus,
)


def test_valid_incident_schema() -> None:
    """Test valid incident instantiation and serialization."""
    incident = Incident(
        incident_id="INC-9999",
        timestamp="2026-09-01T12:00:00Z",
        service="checkout-service",
        severity=Severity.HIGH.value,
        title="Checkout failure under load",
        description="Checkout service failing with 500 error",
        logs="2026-09-01 ERROR checkout-service: connection timed out",
        symptoms=["connection timed out"],
        status=IncidentStatus.OPEN.value,
    )
    assert incident.incident_id == "INC-9999"
    assert incident.severity == "HIGH"
    data = incident.model_dump()
    assert data["service"] == "checkout-service"


def test_invalid_incident_missing_required_fields() -> None:
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError):
        # Missing required fields like incident_id, timestamp, service, title, etc.
        Incident(severity=Severity.HIGH.value)  # type: ignore


def test_valid_incident_report() -> None:
    """Test IncidentReport creation and defaults."""
    report = IncidentReport(
        incident_id="INC-1001",
        title="Payment API DB timeout",
        severity="HIGH",
        affected_service="payment-api",
        summary="DB connection pool failure",
        evidence=["ERROR: connection pool exhausted"],
        root_cause="Pool exhaustion",
        confidence="HIGH",
        recommended_actions=["Restart worker", "Increase pool limit"],
        runbook="DB-POOL-004",
    )
    assert report.incident_id == "INC-1001"
    assert report.confidence == "HIGH"
    assert report.runbook == "DB-POOL-004"
    assert len(report.recommended_actions) == 2


def test_memory_entry_schema() -> None:
    """Test MemoryEntry model validation."""
    entry = MemoryEntry(
        id="mem-42",
        text="Previous incident resolved using DB-POOL-004",
        type="experience",
        tags=["incident", "resolution"],
        context="incidentmind-agent",
    )
    assert entry.id == "mem-42"
    assert "resolution" in entry.tags
