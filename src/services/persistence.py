"""SQLite local persistence for application incident records and reports."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import settings
from src.agent.schemas import Incident, IncidentReport


class IncidentDatabase:
    """Manages local SQLite database operations for operational incident records."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or settings.database_path
        self._ensure_dir()
        self.init_db()

    def _ensure_dir(self) -> None:
        """Ensure the parent directory for the SQLite file exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Create a connection with row factory enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initialize database tables if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    service TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    logs TEXT NOT NULL,
                    symptoms TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    status TEXT NOT NULL,
                    root_cause TEXT,
                    resolution TEXT,
                    runbook_id TEXT,
                    lessons_learned TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS incident_reports (
                    incident_id TEXT PRIMARY KEY,
                    report_json TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
                )
                """
            )
            conn.commit()

    def save_incident(self, incident: Incident) -> Incident:
        """Insert or replace an incident record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO incidents (
                    incident_id, timestamp, service, severity, title,
                    description, logs, symptoms, environment, status,
                    root_cause, resolution, runbook_id, lessons_learned,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident.incident_id,
                    incident.timestamp,
                    incident.service,
                    incident.severity,
                    incident.title,
                    incident.description,
                    incident.logs,
                    json.dumps(incident.symptoms),
                    incident.environment,
                    incident.status,
                    incident.root_cause,
                    incident.resolution,
                    incident.runbook_id,
                    incident.lessons_learned,
                    incident.created_at,
                    incident.updated_at,
                ),
            )
            conn.commit()
        return incident

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Fetch an incident by its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM incidents WHERE incident_id = ?", (incident_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["symptoms"] = json.loads(data.get("symptoms") or "[]")
            return Incident(**data)

    def list_incidents(self, limit: int = 50) -> List[Incident]:
        """List all incidents ordered by creation time descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM incidents ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = cursor.fetchall()
            incidents: List[Incident] = []
            for row in rows:
                data = dict(row)
                data["symptoms"] = json.loads(data.get("symptoms") or "[]")
                incidents.append(Incident(**data))
            return incidents

    def save_report(self, incident_id: str, report: IncidentReport) -> None:
        """Store an incident report as JSON."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO incident_reports (incident_id, report_json, generated_at)
                VALUES (?, ?, ?)
                """,
                (incident_id, json.dumps(report.model_dump()), report.generated_at),
            )
            conn.commit()

    def get_report(self, incident_id: str) -> Optional[IncidentReport]:
        """Fetch stored report for an incident."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT report_json FROM incident_reports WHERE incident_id = ?",
                (incident_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return IncidentReport(**json.loads(row["report_json"]))

    def get_stats(self) -> Dict[str, int]:
        """Get aggregate counts for dashboard."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM incidents")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM incidents WHERE status IN ('OPEN', 'INVESTIGATING')"
            )
            active = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM incidents WHERE severity IN ('CRITICAL', 'HIGH') AND status != 'RESOLVED'"
            )
            critical = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM incidents WHERE status = 'RESOLVED'")
            resolved = cursor.fetchone()[0]

            return {
                "total": total,
                "active": active,
                "critical": critical,
                "resolved": resolved,
            }

    def clear_all(self) -> None:
        """Delete all stored incidents and reports (used for demo reset)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM incident_reports")
            cursor.execute("DELETE FROM incidents")
            conn.commit()


# Default singleton instance
db = IncidentDatabase()
