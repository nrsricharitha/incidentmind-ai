"""Incident pattern comparison tool to evaluate similarity against historical context."""

import re
from typing import Any, Dict, List
from src.agent.schemas import PatternComparisonResult


def compare_incident_patterns(
    current_symptoms: List[str],
    current_service: str,
    historical_context: str = "",
) -> Dict[str, Any]:
    """Compare current incident symptoms with historical incident context.

    This tool normalizes incident evidence and assesses whether previously
    recorded incidents and resolutions share underlying failure modes with the
    current active event.

    Args:
        current_symptoms: List of observable symptoms identified in current incident.
        current_service: The service currently undergoing investigation.
        historical_context: Text or summary of historical memories recalled from Hindsight.

    Returns:
        Structured pattern comparison with similarity score, shared symptoms,
        key differences, and relevance assessment.
    """
    if not historical_context or not historical_context.strip():
        return PatternComparisonResult(
            similarity_score=0.0,
            matched_patterns=[],
            historical_incident_ids=[],
            shared_symptoms=[],
            key_differences=["No historical context was provided or recalled for comparison."],
            relevance_assessment="No historical matches found in Hindsight memory. Proceeding with first-principles runbook diagnosis.",
        ).model_dump()

    # Extract historical incident IDs (e.g. INC-1001, INC-1042)
    incident_id_matches = re.findall(r"\bINC-\d+\b", historical_context, re.IGNORECASE)
    historical_ids = list(set([m.upper() for m in incident_id_matches]))

    hist_lower = historical_context.lower()
    matched_patterns: List[str] = []
    shared_symptoms: List[str] = []
    key_differences: List[str] = []

    # Check symptom overlap
    for symptom in current_symptoms:
        s_clean = symptom.lower().strip()
        if not s_clean:
            continue
        words = set(s_clean.split())
        if s_clean in hist_lower:
            shared_symptoms.append(symptom)
            matched_patterns.append(f"Direct symptom match: '{symptom}'")
        elif len(words) > 1 and any(w in hist_lower for w in words if len(w) > 4):
            shared_symptoms.append(symptom)
            matched_patterns.append(f"Partial symptom match: '{symptom}'")
        else:
            key_differences.append(f"Symptom '{symptom}' was not documented in historical memory")

    # Check service match
    service_match = current_service.lower() in hist_lower if current_service else False
    if service_match:
        matched_patterns.append(f"Identical service scope: '{current_service}'")
    else:
        key_differences.append("Service scope differs or not explicitly stated in historical record")

    # Compute similarity score
    total_checks = max(len(current_symptoms) + 1, 1)
    matches_count = len(shared_symptoms) + (1 if service_match else 0)
    similarity_score = min(round(matches_count / total_checks, 2), 1.0)

    # Relevance assessment
    if similarity_score >= 0.7:
        relevance = (
            f"High similarity ({int(similarity_score * 100)}%). Current incident closely matches "
            f"historical incident(s) {', '.join(historical_ids) if historical_ids else 'in memory'}. "
            "Previous remediation actions (e.g., connection pool sizing and connection leak mitigation) "
            "have strong relevance and should be verified against current evidence."
        )
    elif similarity_score >= 0.4:
        relevance = (
            f"Moderate similarity ({int(similarity_score * 100)}%). Several symptoms overlap with "
            f"historical records {', '.join(historical_ids) if historical_ids else ''}, "
            "but divergences exist. Evaluate historical remediation as a reference while inspecting current metrics."
        )
    else:
        relevance = (
            f"Low similarity ({int(similarity_score * 100)}%). Weak correlation with historical records. "
            "Rely primarily on fresh log analysis and standard runbooks."
        )

    return PatternComparisonResult(
        similarity_score=similarity_score,
        matched_patterns=matched_patterns,
        historical_incident_ids=historical_ids,
        shared_symptoms=shared_symptoms,
        key_differences=key_differences,
        relevance_assessment=relevance,
    ).model_dump()
