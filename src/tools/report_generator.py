"""Incident report generator tool."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from src.agent.schemas import IncidentReport


def generate_incident_report(
    incident_id: str,
    title: str,
    severity: str,
    affected_service: str,
    summary: str,
    evidence: List[str],
    root_cause: str,
    confidence: str = "HIGH",
    historical_matches: Optional[List[str]] = None,
    recommended_actions: Optional[List[str]] = None,
    runbook: str = "N/A",
    previous_resolution: str = "None recalled",
    risks: Optional[List[str]] = None,
    follow_up: Optional[List[str]] = None,
    lessons_learned: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Generate a structured, production-quality incident report.

    Args:
        incident_id: Identifier of the incident (e.g. 'INC-1001').
        title: Short title of the incident.
        severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL).
        affected_service: Name of the impacted service.
        summary: High-level summary of the investigation.
        evidence: Concrete observed log lines, metrics, or diagnostics.
        root_cause: Assessed root cause or explicit insufficient evidence statement.
        confidence: Confidence level in the assessment ('LOW', 'MEDIUM', 'HIGH').
        historical_matches: List of historical incidents or memory references.
        recommended_actions: Proposed safe remediation and diagnostic steps.
        runbook: Identifier of the matched runbook.
        previous_resolution: Resolution details recalled from Hindsight memory.
        risks: Potential risks associated with remediation or inaction.
        follow_up: Action items for post-incident review and prevention.
        lessons_learned: Key operational takeaways for retention.

    Returns:
        Structured IncidentReport dictionary.
    """
    report = IncidentReport(
        incident_id=incident_id,
        title=title,
        severity=severity,
        affected_service=affected_service,
        summary=summary,
        evidence=evidence or [],
        historical_matches=historical_matches or [],
        root_cause=root_cause,
        confidence=confidence,
        recommended_actions=recommended_actions or [],
        runbook=runbook,
        previous_resolution=previous_resolution,
        risks=risks or [],
        follow_up=follow_up or [],
        lessons_learned=lessons_learned or [],
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    return report.model_dump()
