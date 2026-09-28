"""Predefined demo scenarios for 60-90 second hackathon presentation."""

from typing import Any, Dict
from src.agent.schemas import Incident, Severity

DEMO_DAY_1_DATA: Dict[str, Any] = {
    "incident_id": "INC-1001",
    "timestamp": "2026-09-01T10:05:00Z",
    "service": "payment-api",
    "severity": Severity.HIGH.value,
    "title": "Payment API database connection failures",
    "description": (
        "Multiple customer payment transactions failing with 500 status. "
        "Service reporting inability to acquire database connections under moderate load."
    ),
    "logs": (
        "2026-09-01 10:02:14 ERROR payment-api: failed to acquire database connection\n"
        "2026-09-01 10:02:16 ERROR payment-api: connection pool exhausted\n"
        "2026-09-01 10:02:19 WARN payment-api: request timeout\n"
        "2026-09-01 10:02:21 ERROR payment-api: database connection acquisition timeout"
    ),
    "symptoms": [
        "failed to acquire database connection",
        "connection pool exhausted",
        "request timeout",
        "database connection acquisition timeout",
    ],
    "environment": "production",
    "status": "OPEN",
    "root_cause": (
        "Database connection pool exhaustion caused by leaked connection sessions in "
        "checkout processing worker."
    ),
    "resolution": (
        "Investigated pool metrics; identified unclosed DB sessions in billing thread. "
        "Released leaked connections, temporarily raised max_connections from 50 to 100, "
        "and executed safe rolling restart of payment-api pods following DB-POOL-004 runbook. "
        "Verified pool latency stabilized at 4ms."
    ),
    "runbook_id": "DB-POOL-004",
    "lessons_learned": (
        "Database checkout handler was not releasing connections upon client timeout. "
        "Ensure all database transactions use strict context managers. Follow DB-POOL-004."
    ),
}

DEMO_DAY_30_DATA: Dict[str, Any] = {
    "incident_id": "INC-1042",
    "timestamp": "2026-10-01T14:45:00Z",
    "service": "payment-api",
    "severity": Severity.HIGH.value,
    "title": "Payment API latency spike and connection timeouts",
    "description": (
        "Payment API experiencing latency spike during end-of-month reconciliation. "
        "Application reporting timeouts while acquiring connections."
    ),
    "logs": (
        "2026-10-01 14:41:02 ERROR payment-api: database connection timeout\n"
        "2026-10-01 14:41:04 WARN payment-api: request latency above threshold\n"
        "2026-10-01 14:41:06 ERROR payment-api: failed to obtain DB connection"
    ),
    "symptoms": [
        "database connection timeout",
        "request latency above threshold",
        "failed to obtain DB connection",
    ],
    "environment": "production",
    "status": "OPEN",
    "root_cause": "",
    "resolution": "",
    "runbook_id": "",
    "lessons_learned": "",
}


def get_demo_day_1_incident() -> Incident:
    """Return a fresh copy of the Demo Day 1 Incident object."""
    return Incident(**DEMO_DAY_1_DATA)


def get_demo_day_30_incident() -> Incident:
    """Return a fresh copy of the Demo Day 30 Incident object."""
    return Incident(**DEMO_DAY_30_DATA)
