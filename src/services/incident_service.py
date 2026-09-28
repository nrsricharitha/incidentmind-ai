"""Service layer coordinating incidents, investigations, persistence, and memory retention."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from src.config import settings
from src.agent.schemas import Incident, IncidentReport, IncidentStatus
from src.agent.incident_agent import InvestigationContext, agent_coordinator
from src.memory.memory_service import MemoryService
from src.services.persistence import db

logger = logging.getLogger(__name__)


class IncidentService:
    """Manages business operations for incidents, agent investigations, and memory retention."""

    def __init__(self) -> None:
        self.coordinator = agent_coordinator
        self.memory_service = MemoryService()

    def investigate(
        self, incident: Incident, stage_callback: Optional[Any] = None
    ) -> InvestigationContext:
        """Run agent investigation on an incident."""
        # Ensure incident is saved to local DB
        db.save_incident(incident)
        # Execute investigation
        ctx = self.coordinator.investigate_sync(incident, stage_callback=stage_callback)
        return ctx

    def resolve_and_remember(
        self,
        incident_id: str,
        resolution_notes: str = "",
        lessons_learned: str = "",
        runbook_id: str = "",
    ) -> Dict[str, Any]:
        """Mark an incident as resolved and retain its experience in Hindsight long-term memory.

        This is the critical step in the memory loop:
        Incident -> Investigation -> Resolution -> Hindsight Retention -> Future Incident Recall
        """
        incident = db.get_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident with ID '{incident_id}' not found.")

        # Update incident record
        incident.status = IncidentStatus.RESOLVED.value
        if resolution_notes:
            incident.resolution = resolution_notes
        if lessons_learned:
            incident.lessons_learned = lessons_learned
        if runbook_id:
            incident.runbook_id = runbook_id
        incident.updated_at = datetime.now(timezone.utc).isoformat()

        # Save to SQLite
        db.save_incident(incident)
        report = db.get_report(incident_id)

        # Retain into Hindsight long-term memory
        hindsight_result: Dict[str, Any] = {
            "retained": False,
            "message": "Hindsight retention not performed",
        }

        if settings.is_hindsight_configured:
            try:
                retention_resp = self.memory_service.retain_resolution(
                    incident=incident, report=report
                )
                hindsight_result = {
                    "retained": True,
                    "bank_id": settings.hindsight_bank_id,
                    "message": "Successfully retained incident resolution into Hindsight long-term memory bank.",
                    "details": retention_resp,
                }
                logger.info(
                    "Retained incident %s into Hindsight bank %s",
                    incident_id,
                    settings.hindsight_bank_id,
                )
            except Exception as e:
                logger.error("Failed to retain incident into Hindsight: %s", e)
                hindsight_result = {
                    "retained": False,
                    "error": str(e),
                    "message": f"Hindsight retention failed: {str(e)}",
                }
        else:
            hindsight_result = {
                "retained": False,
                "message": (
                    "Hindsight retention skipped: HINDSIGHT_API_KEY is not configured. "
                    "Incident was resolved in local records only."
                ),
            }

        return {
            "incident": incident,
            "report": report,
            "hindsight": hindsight_result,
        }

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Fetch dashboard statistics including local counts and memory connectivity."""
        stats = db.get_stats()
        hindsight_ok, hindsight_msg = self.memory_service.check_connection()
        groq_ok = settings.is_groq_configured

        return {
            **stats,
            "hindsight_connected": hindsight_ok,
            "hindsight_status": hindsight_msg,
            "groq_configured": groq_ok,
            "groq_model": settings.groq_model,
            "hindsight_bank": settings.hindsight_bank_id,
        }

    def reset_all(self) -> None:
        """Reset demo environment and clear local records."""
        db.clear_all()


# Default singleton instance
incident_service = IncidentService()
