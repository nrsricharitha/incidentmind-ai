"""Service for managing long-term memory operations with Hindsight."""

import logging
from typing import Any, Dict, List, Optional, Tuple
from hindsight_client import Hindsight
from src.config import settings
from src.agent.schemas import Incident, IncidentReport, MemoryEntry

logger = logging.getLogger(__name__)


class MemoryService:
    """Manages Hindsight memory operations, direct recall, and retention."""

    def __init__(
        self,
        bank_id: Optional[str] = None,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
    ) -> None:
        self.bank_id = bank_id or settings.hindsight_bank_id
        self.api_key = api_key or settings.hindsight_api_key
        self.api_url = api_url or settings.hindsight_api_url
        self._client: Optional[Hindsight] = None
        self._cached_key: Optional[str] = None
        self._cached_url: Optional[str] = None
        self._ensured_banks: set[str] = set()

    def _get_client(self) -> Hindsight:
        """Resolve and cache a Hindsight client instance."""
        # Always check latest settings if key was not explicitly provided
        key = self.api_key or settings.hindsight_api_key
        url = self.api_url or settings.hindsight_api_url

        if not key:
            raise ValueError(
                "Hindsight API key is missing. Set HINDSIGHT_API_KEY in .env or environment variables."
            )

        if self._client is None or self._cached_key != key or self._cached_url != url:
            self._client = Hindsight(
                base_url=url,
                api_key=key,
                timeout=25.0,
            )
            self._cached_key = key
            self._cached_url = url
        return self._client

    def _ensure_bank(self, client: Hindsight, bank_id: str) -> None:
        """Ensure bank exists on first use (best effort)."""
        if bank_id in self._ensured_banks:
            return
        try:
            client.create_bank(
                bank_id=bank_id,
                name=bank_id,
                mission=(
                    "IncidentMind AI operational memory bank. Retains and recalls technical incidents, "
                    "failure modes, observable symptoms, affected services, root causes, executed runbooks, "
                    "and successful resolution steps to assist incident responders."
                ),
            )
        except Exception as e:
            logger.debug("Bank ensure for %s: %s", bank_id, e)
        self._ensured_banks.add(bank_id)

    def check_connection(self) -> Tuple[bool, str]:
        """Verify truthful connectivity to Hindsight API.

        Returns:
            Tuple of (connected: bool, status_message: str).
        """
        key = self.api_key or settings.hindsight_api_key
        url = self.api_url or settings.hindsight_api_url

        if not key:
            return False, "Not Connected: HINDSIGHT_API_KEY is not configured."

        try:
            client = self._get_client()
            version_info = client.get_version()
            version_str = getattr(version_info, "version", "connected")
            return True, f"Connected to Hindsight Cloud (v{version_str}) at {url}"
        except Exception as e:
            logger.warning("Hindsight connectivity check failed: %s", e)
            return False, f"Connection Failed: {str(e)}"

    def recall_memories(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        budget: str = "mid",
        max_tokens: int = 4096,
    ) -> List[MemoryEntry]:
        """Recall relevant historical memories from Hindsight.

        Args:
            query: Natural language search query or incident symptoms.
            tags: Optional tags to filter recall (e.g. ['incident', 'resolution']).
            budget: Recall budget ('low', 'mid', 'high').
            max_tokens: Maximum tokens of memory to retrieve.

        Returns:
            List of MemoryEntry objects containing real recalled facts/experiences.
        """
        key = self.api_key or settings.hindsight_api_key
        if not key:
            logger.info("Cannot recall memories: HINDSIGHT_API_KEY is not configured.")
            return []

        try:
            client = self._get_client()
            bank = self.bank_id or settings.hindsight_bank_id
            self._ensure_bank(client, bank)

            logger.info("Recalling Hindsight memories for bank '%s' query: '%s'", bank, query[:60])
            response = client.recall(
                bank_id=bank,
                query=query,
                budget=budget,
                max_tokens=max_tokens,
                tags=tags,
                tags_match="any" if tags else None,
            )

            entries: List[MemoryEntry] = []
            for item in (response.results or []):
                text = getattr(item, "text", "")
                if not text:
                    continue

                item_id = str(getattr(item, "id", f"mem_{len(entries)+1}"))
                item_type = str(getattr(item, "type", "experience"))
                item_tags = list(getattr(item, "tags", []) or [])
                item_context = str(getattr(item, "context", ""))

                entries.append(
                    MemoryEntry(
                        id=item_id,
                        text=text,
                        type=item_type,
                        tags=item_tags,
                        context=item_context,
                        relevance="High",
                    )
                )

            logger.info("Hindsight recall returned %d memory items.", len(entries))
            return entries

        except Exception as e:
            logger.error("Hindsight recall error: %s", e)
            return []

    def retain_resolution(
        self,
        incident: Incident,
        report: Optional[IncidentReport] = None,
    ) -> Dict[str, Any]:
        """Retain a resolved incident into Hindsight long-term memory.

        Args:
            incident: The incident record containing root cause and resolution.
            report: Optional detailed incident report.

        Returns:
            Dict containing retention status and metadata.
        """
        key = self.api_key or settings.hindsight_api_key
        if not key:
            raise ValueError(
                "Cannot retain memory: HINDSIGHT_API_KEY is not configured."
            )

        client = self._get_client()
        bank = self.bank_id or settings.hindsight_bank_id
        self._ensure_bank(client, bank)

        # Construct high-density semantic content for Hindsight retention
        content_lines = [
            f"Incident Record: {incident.incident_id}",
            f"Title: {incident.title}",
            f"Service: {incident.service}",
            f"Severity: {incident.severity}",
            f"Symptoms: {', '.join(incident.symptoms) if incident.symptoms else 'None recorded'}",
            f"Root Cause: {incident.root_cause or (report.root_cause if report else 'Identified failure')}",
            f"Runbook Applied: {incident.runbook_id or (report.runbook if report else 'N/A')}",
            f"Resolution: {incident.resolution or (report.previous_resolution if report else 'Remediated')}",
        ]

        if incident.lessons_learned:
            content_lines.append(f"Lessons Learned: {incident.lessons_learned}")
        elif report and report.lessons_learned:
            content_lines.append(f"Lessons Learned: {'; '.join(report.lessons_learned)}")

        if incident.logs:
            content_lines.append(f"Key Evidence Logs:\n{incident.logs.strip()}")

        content_body = "\n".join(content_lines)

        tags = [
            "incident",
            "resolution",
            "root_cause",
            f"service:{incident.service}",
            f"severity:{incident.severity.lower()}",
        ]
        if incident.runbook_id:
            tags.append(f"runbook:{incident.runbook_id.lower()}")

        logger.info(
            "Retaining incident %s in Hindsight bank '%s' with %d tags",
            incident.incident_id,
            bank,
            len(tags),
        )

        response = client.retain(
            bank_id=bank,
            content=content_body,
            context="incidentmind-resolution",
            metadata={
                "incident_id": incident.incident_id,
                "service": incident.service,
                "severity": incident.severity,
                "runbook_id": incident.runbook_id or "",
            },
            tags=tags,
        )

        return {
            "success": True,
            "bank_id": bank,
            "incident_id": incident.incident_id,
            "response": str(response),
            "retained_content": content_body,
            "tags": tags,
        }
