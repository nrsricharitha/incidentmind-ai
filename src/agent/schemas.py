"""Data models and schemas for IncidentMind AI using Pydantic."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Incident severity classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    """Incident lifecycle state."""
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    MITIGATED = "MITIGATED"
    RESOLVED = "RESOLVED"


class ServiceStatus(str, Enum):
    """Service health state."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNAVAILABLE = "UNAVAILABLE"


class LogAnalysisResult(BaseModel):
    """Structured findings extracted from raw incident logs."""
    error_patterns: List[str] = Field(
        default_factory=list, description="Unique regex/keyword-matched error signatures"
    )
    repeated_messages: List[Dict[str, Any]] = Field(
        default_factory=list, description="Messages with their occurrence count"
    )
    severity_indicators: List[str] = Field(
        default_factory=list, description="Log levels identified (ERROR, WARN, etc.)"
    )
    affected_components: List[str] = Field(
        default_factory=list, description="Services, modules, or threads referenced"
    )
    possible_symptoms: List[str] = Field(
        default_factory=list, description="Derived observable symptoms"
    )
    evidence_excerpts: List[str] = Field(
        default_factory=list, description="Key log lines acting as concrete evidence"
    )
    summary: str = Field(default="", description="High-level summary of log analysis")


class Runbook(BaseModel):
    """Operational runbook definition."""
    id: str = Field(description="Runbook identifier e.g. DB-POOL-004")
    title: str = Field(description="Runbook title")
    service: str = Field(description="Associated service or system component")
    symptoms: List[str] = Field(
        default_factory=list, description="Known symptoms addressed by this runbook"
    )
    diagnostic_steps: List[str] = Field(
        default_factory=list, description="Step-by-step diagnostic actions"
    )
    recommended_remediation: List[str] = Field(
        default_factory=list, description="Safe resolution and remediation actions"
    )
    related_runbooks: List[str] = Field(
        default_factory=list, description="Related runbook references"
    )


class ServiceHealth(BaseModel):
    """Simulated service health diagnostics."""
    service_name: str
    status: ServiceStatus
    health_state: str
    latency_ms: float
    error_rate_pct: float
    connection_state: str
    active_connections: int
    max_connections: int
    recent_deployment: str
    simulated: bool = Field(
        default=True,
        description="Explicit flag verifying this is simulated demo infrastructure",
    )


class PatternComparisonResult(BaseModel):
    """Comparison between current incident evidence and historical patterns."""
    similarity_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Normalized similarity metric"
    )
    matched_patterns: List[str] = Field(
        default_factory=list, description="Identified symptom and error overlaps"
    )
    historical_incident_ids: List[str] = Field(
        default_factory=list, description="Referenced historical incident identifiers"
    )
    shared_symptoms: List[str] = Field(
        default_factory=list, description="Symptoms present in both current and past"
    )
    key_differences: List[str] = Field(
        default_factory=list, description="Divergences between incidents"
    )
    relevance_assessment: str = Field(
        default="", description="Analysis of whether previous resolution applies"
    )


class IncidentReport(BaseModel):
    """Structured incident investigation report produced by the agent."""
    incident_id: str
    title: str
    severity: str
    affected_service: str
    summary: str
    evidence: List[str] = Field(
        default_factory=list, description="Observed facts and log evidence"
    )
    historical_matches: List[str] = Field(
        default_factory=list, description="Recalled historical incident references"
    )
    root_cause: str = Field(
        description="Assessed root cause or explicit insufficient evidence statement"
    )
    confidence: str = Field(
        default="MEDIUM", description="Confidence level: LOW, MEDIUM, or HIGH"
    )
    recommended_actions: List[str] = Field(
        default_factory=list, description="Proposed resolution and diagnostic steps"
    )
    runbook: str = Field(default="N/A", description="Referenced runbook ID")
    previous_resolution: str = Field(
        default="None recalled", description="Resolution recalled from Hindsight memory"
    )
    risks: List[str] = Field(
        default_factory=list, description="Potential risks and mitigation precautions"
    )
    follow_up: List[str] = Field(
        default_factory=list, description="Post-incident preventative items"
    )
    lessons_learned: List[str] = Field(
        default_factory=list, description="Key operational insights for retention"
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Incident(BaseModel):
    """Operational incident record stored in local persistence."""
    incident_id: str
    timestamp: str
    service: str
    severity: str
    title: str
    description: str
    logs: str
    symptoms: List[str] = Field(default_factory=list)
    environment: str = "production"
    status: str = "OPEN"
    root_cause: str = ""
    resolution: str = ""
    runbook_id: str = ""
    lessons_learned: str = ""
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class MemoryEntry(BaseModel):
    """Memory representation retrieved from Hindsight."""
    id: str
    text: str
    type: str = "experience"
    tags: List[str] = Field(default_factory=list)
    context: str = ""
    created_at: Optional[str] = None
    relevance: str = "High"
