"""Deterministic log analysis tool for incident investigation."""

import re
from collections import Counter
from typing import Any, Dict, List, Optional
from src.agent.schemas import LogAnalysisResult

# Patterns for log level matching
LOG_LEVEL_PATTERN = re.compile(
    r"\b(FATAL|CRITICAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE)\b", re.IGNORECASE
)

# Common error keywords and patterns
ERROR_SIGNATURES = [
    (re.compile(r"connection\s+pool\s+exhausted", re.IGNORECASE), "Connection Pool Exhaustion"),
    (re.compile(r"failed\s+to\s+acquire\s+(?:database\s+)?connection", re.IGNORECASE), "Database Connection Acquisition Failure"),
    (re.compile(r"failed\s+to\s+obtain\s+(?:db\s+)?connection", re.IGNORECASE), "Database Connection Acquisition Failure"),
    (re.compile(r"database\s+connection\s+timeout", re.IGNORECASE), "Database Connection Timeout"),
    (re.compile(r"request\s+(?:read\s+)?timeout", re.IGNORECASE), "Request Latency Timeout"),
    (re.compile(r"request\s+latency\s+above\s+threshold", re.IGNORECASE), "Elevated Request Latency"),
    (re.compile(r"502\s+bad\s+gateway", re.IGNORECASE), "Upstream Gateway Error (502)"),
    (re.compile(r"504\s+gateway\s+timeout", re.IGNORECASE), "Upstream Gateway Timeout (504)"),
    (re.compile(r"out\s+of\s+memory|oomkilled|java\.lang\.OutOfMemoryError", re.IGNORECASE), "Memory Exhaustion (OOM)"),
    (re.compile(r"connection\s+refused", re.IGNORECASE), "Connection Refused"),
    (re.compile(r"token\s+validation\s+failed|401\s+unauthorized", re.IGNORECASE), "Authentication / Token Failure"),
]

# Service / component regex
SERVICE_MENTION_PATTERN = re.compile(
    r"\b([a-zA-Z0-9_\-]+(?:-service|-api|-db|-gateway|-worker|-daemon))\b", re.IGNORECASE
)


def analyze_logs(
    log_text: str, service_name: str = "", time_window: str = ""
) -> Dict[str, Any]:
    """Analyze incident log text and extract structured diagnostics and evidence.

    Args:
        log_text: Raw log text or stack traces to analyze.
        service_name: Optional service name being investigated.
        time_window: Optional time window string (e.g. 'last 15m').

    Returns:
        Structured dictionary containing error patterns, repeated messages,
        severity indicators, affected components, possible symptoms, and evidence excerpts.
    """
    if not log_text or not log_text.strip():
        return LogAnalysisResult(
            error_patterns=[],
            repeated_messages=[],
            severity_indicators=[],
            affected_components=[service_name] if service_name else [],
            possible_symptoms=[],
            evidence_excerpts=[],
            summary="No log text provided for analysis.",
        ).model_dump()

    lines = [line.strip() for line in log_text.strip().splitlines() if line.strip()]
    severity_counter: Counter[str] = Counter()
    normalized_messages: Counter[str] = Counter()
    detected_patterns: set[str] = set()
    affected_components: set[str] = set()
    evidence_excerpts: List[str] = []
    possible_symptoms: set[str] = set()

    if service_name:
        affected_components.add(service_name)

    for line in lines:
        # 1. Match log level
        level_match = LOG_LEVEL_PATTERN.search(line)
        if level_match:
            lvl = level_match.group(1).upper()
            if lvl == "WARNING":
                lvl = "WARN"
            severity_counter[lvl] += 1
            if lvl in ("ERROR", "CRITICAL", "FATAL") and len(evidence_excerpts) < 8:
                evidence_excerpts.append(line)
        else:
            if ("error" in line.lower() or "fail" in line.lower()) and len(evidence_excerpts) < 8:
                evidence_excerpts.append(line)

        # 2. Match error signatures
        for pattern_regex, label in ERROR_SIGNATURES:
            if pattern_regex.search(line):
                detected_patterns.add(label)
                possible_symptoms.add(pattern_regex.pattern.replace("\\s+", " ").replace("(?:", "").replace(")?", "").replace("\\b", ""))

        # 3. Match service components
        for svc in SERVICE_MENTION_PATTERN.findall(line):
            affected_components.add(svc.lower())

        # 4. Clean message for frequency count
        # Strip ISO timestamps and log level prefixes
        cleaned = re.sub(r"^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?\s*", "", line)
        cleaned = re.sub(r"^(?:ERROR|WARN|INFO|CRITICAL|DEBUG):\s*", "", cleaned, flags=re.IGNORECASE)
        normalized_messages[cleaned.strip()] += 1

    # Extract top repeated messages
    top_repeated = [
        {"message": msg, "count": count}
        for msg, count in normalized_messages.most_common(5)
    ]

    # Formulate summary
    total_errors = severity_counter.get("ERROR", 0) + severity_counter.get("CRITICAL", 0) + severity_counter.get("FATAL", 0)
    total_warns = severity_counter.get("WARN", 0)
    
    summary_parts = []
    if total_errors > 0:
        summary_parts.append(f"{total_errors} error event(s)")
    if total_warns > 0:
        summary_parts.append(f"{total_warns} warning event(s)")
    if detected_patterns:
        summary_parts.append(f"Identified signatures: {', '.join(sorted(detected_patterns))}")
    if not summary_parts:
        summary_parts.append("No prominent error signatures detected in logs.")

    summary_str = " | ".join(summary_parts)

    result = LogAnalysisResult(
        error_patterns=sorted(list(detected_patterns)),
        repeated_messages=top_repeated,
        severity_indicators=list(severity_counter.keys()),
        affected_components=sorted(list(affected_components)),
        possible_symptoms=sorted(list(possible_symptoms)),
        evidence_excerpts=evidence_excerpts if evidence_excerpts else lines[:5],
        summary=summary_str,
    )

    return result.model_dump()
