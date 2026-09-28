"""Unit tests for demo scenarios data integrity."""

import pytest
from src.data.demo_scenarios import (
    get_demo_day_1_incident,
    get_demo_day_30_incident,
    DEMO_DAY_1_DATA,
    DEMO_DAY_30_DATA,
)


def test_demo_day_1_scenario() -> None:
    """Verify Day 1 scenario loads with correct incident parameters."""
    inc = get_demo_day_1_incident()
    assert inc.incident_id == "INC-1001"
    assert inc.service == "payment-api"
    assert inc.severity == "HIGH"
    assert "connection pool exhausted" in inc.logs
    assert inc.runbook_id == "DB-POOL-004"
    assert len(inc.symptoms) > 0


def test_demo_day_30_scenario() -> None:
    """Verify Day 30 scenario loads with separate incident parameters."""
    inc = get_demo_day_30_incident()
    assert inc.incident_id == "INC-1042"
    assert inc.service == "payment-api"
    assert inc.severity == "HIGH"
    assert "failed to obtain DB connection" in inc.logs
    assert inc.incident_id != DEMO_DAY_1_DATA["incident_id"]
    assert inc.timestamp != DEMO_DAY_1_DATA["timestamp"]
