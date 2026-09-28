"""Runbook search tool for retrieving relevant operational remediation procedures."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.config import RUNBOOKS_DIR
from src.agent.schemas import Runbook


def load_all_runbooks(runbooks_dir: Optional[Path] = None) -> List[Runbook]:
    """Load all JSON runbooks from the specified directory."""
    target_dir = runbooks_dir or RUNBOOKS_DIR
    runbooks: List[Runbook] = []

    if not target_dir.exists():
        return runbooks

    for file_path in target_dir.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                runbooks.append(Runbook(**data))
        except Exception:
            continue

    return runbooks


def search_runbooks(query: str, service: str = "") -> List[Dict[str, Any]]:
    """Search the operational runbook knowledge base for matching procedures.

    Args:
        query: Query string containing symptoms, error messages, or topics
               (e.g., 'connection pool exhausted', 'database timeout', '500 error').
        service: Optional service name to bias or filter runbook relevance.

    Returns:
        A list of matching runbooks ranked by relevance, including diagnostic
        steps and recommended remediation actions.
    """
    runbooks = load_all_runbooks()
    if not runbooks:
        return []

    query_tokens = set(query.lower().split()) if query else set()
    service_clean = service.lower().strip()

    scored_results: List[tuple[float, Runbook]] = []

    for rb in runbooks:
        score = 0.0

        # Exact runbook ID match in query
        if rb.id.lower() in query.lower():
            score += 10.0

        # Service match
        if service_clean and service_clean in rb.service.lower():
            score += 3.0
        elif service_clean and rb.service.lower() in service_clean:
            score += 2.0

        # Symptom matching
        for symptom in rb.symptoms:
            s_lower = symptom.lower()
            if s_lower in query.lower():
                score += 5.0
            else:
                s_tokens = set(s_lower.split())
                overlap = query_tokens.intersection(s_tokens)
                if overlap:
                    score += len(overlap) * 1.5

        # Title matching
        title_tokens = set(rb.title.lower().split())
        title_overlap = query_tokens.intersection(title_tokens)
        score += len(title_overlap) * 2.0

        if score > 0:
            scored_results.append((score, rb))

    # Sort descending by score
    scored_results.sort(key=lambda x: x[0], reverse=True)

    # Return top 3 matches as dicts
    return [rb.model_dump() for _, rb in scored_results[:3]]


def get_runbook_by_id(runbook_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a specific runbook by its ID e.g. DB-POOL-004."""
    runbooks = load_all_runbooks()
    for rb in runbooks:
        if rb.id.upper() == runbook_id.strip().upper():
            return rb.model_dump()
    return None
