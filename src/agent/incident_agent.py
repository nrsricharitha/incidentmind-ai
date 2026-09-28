"""Incident Response Agent built with Microsoft Agent Framework, Groq, and Hindsight."""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone

from agent_framework.openai import OpenAIChatClient
from hindsight_agent_framework import HindsightProvider

from src.config import settings
from src.agent.schemas import (
    Incident,
    IncidentReport,
    MemoryEntry,
    Severity,
)
from src.agent.prompts import (
    INCIDENT_AGENT_SYSTEM_PROMPT,
    INVESTIGATION_USER_PROMPT_TEMPLATE,
)
from src.tools.log_analyzer import analyze_logs
from src.tools.runbook_search import search_runbooks
from src.tools.service_inspector import inspect_service
from src.tools.incident_patterns import compare_incident_patterns
from src.tools.report_generator import generate_incident_report
from src.memory.hindsight import create_hindsight_provider
from src.memory.memory_service import MemoryService
from src.services.persistence import db

logger = logging.getLogger(__name__)


class InvestigationStage:
    """Represents the real status of an investigation stage."""

    def __init__(self, key: str, label: str) -> None:
        self.key = key
        self.label = label
        self.status = "pending"  # pending, running, completed, failed, skipped
        self.detail = ""

    def complete(self, detail: str = "") -> None:
        self.status = "completed"
        self.detail = detail

    def fail(self, detail: str = "") -> None:
        self.status = "failed"
        self.detail = detail

    def skip(self, detail: str = "") -> None:
        self.status = "skipped"
        self.detail = detail

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "status": self.status,
            "detail": self.detail,
        }


class InvestigationContext:
    """Full execution context and state for an incident investigation."""

    def __init__(self, incident: Incident) -> None:
        self.incident = incident
        self.stages: Dict[str, InvestigationStage] = {
            "understood": InvestigationStage("understood", "Incident understood"),
            "evidence_analyzed": InvestigationStage("evidence_analyzed", "Evidence analyzed"),
            "service_inspected": InvestigationStage("service_inspected", "Service inspected"),
            "runbooks_searched": InvestigationStage("runbooks_searched", "Runbooks searched"),
            "memory_recalled": InvestigationStage("memory_recalled", "Hindsight memory recalled"),
            "patterns_compared": InvestigationStage("patterns_compared", "Historical incidents compared"),
            "root_cause_assessed": InvestigationStage("root_cause_assessed", "Root cause assessed"),
            "resolution_generated": InvestigationStage("resolution_generated", "Resolution generated"),
        }
        self.log_analysis: Optional[Dict[str, Any]] = None
        self.service_health: Optional[Dict[str, Any]] = None
        self.runbooks: List[Dict[str, Any]] = []
        self.recalled_memories: List[MemoryEntry] = []
        self.pattern_comparison: Optional[Dict[str, Any]] = None
        self.report: Optional[IncidentReport] = None
        self.llm_used: bool = False
        self.hindsight_used: bool = False
        self.error_message: Optional[str] = None
        self.llm_response_text: str = ""
        self.execution_logs: List[str] = []

    def log(self, message: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        entry = f"[{ts}] {message}"
        self.execution_logs.append(entry)
        logger.info(entry)


class IncidentAgentCoordinator:
    """Coordinates Microsoft Agent Framework, Groq LLM, and Hindsight Memory."""

    def __init__(self) -> None:
        self.memory_service = MemoryService()

    def _build_agent_framework_agent(self) -> Any:
        """Construct the Microsoft Agent Framework agent instance."""
        if not settings.is_groq_configured:
            return None

        # Build Groq-compatible OpenAIChatClient
        chat_client = OpenAIChatClient(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )

        # Context providers: Hindsight if configured
        context_providers = []
        if settings.is_hindsight_configured:
            hindsight_prov = create_hindsight_provider(
                bank_id=settings.hindsight_bank_id,
                api_key=settings.hindsight_api_key,
                api_url=settings.hindsight_api_url,
            )
            if hindsight_prov:
                context_providers.append(hindsight_prov)

        # Available function tools
        tools = [
            analyze_logs,
            search_runbooks,
            inspect_service,
            compare_incident_patterns,
            generate_incident_report,
        ]

        agent = chat_client.as_agent(
            name="IncidentResponseAgent",
            instructions=INCIDENT_AGENT_SYSTEM_PROMPT,
            tools=tools,
            context_providers=context_providers,
        )
        return agent

    async def investigate_async(
        self,
        incident: Incident,
        stage_callback: Optional[Callable[[str, str, str], None]] = None,
    ) -> InvestigationContext:
        """Execute full incident investigation asynchronously."""
        ctx = InvestigationContext(incident)
        ctx.log(f"Starting investigation for incident: {incident.incident_id} ({incident.title})")

        def update_stage(key: str, status: str, detail: str = "") -> None:
            if key in ctx.stages:
                stage = ctx.stages[key]
                if status == "completed":
                    stage.complete(detail)
                elif status == "failed":
                    stage.fail(detail)
                elif status == "skipped":
                    stage.skip(detail)
                if stage_callback:
                    stage_callback(key, status, detail)

        # -------------------------------------------------------------
        # STAGE 1: Incident Understood
        # -------------------------------------------------------------
        try:
            if not incident.title or not incident.service:
                raise ValueError("Incident must include title and affected service.")
            ctx.log(f"Incident parsed. Service: {incident.service}, Severity: {incident.severity}")
            update_stage("understood", "completed", f"Parsed incident scope: {incident.service} ({incident.severity})")
        except Exception as e:
            update_stage("understood", "failed", str(e))
            ctx.error_message = str(e)
            return ctx

        # -------------------------------------------------------------
        # STAGE 2: Evidence Analyzed (Deterministic Log Analysis)
        # -------------------------------------------------------------
        try:
            ctx.log("Analyzing incident logs and error patterns...")
            analysis_dict = analyze_logs(
                log_text=incident.logs,
                service_name=incident.service,
            )
            ctx.log_analysis = analysis_dict
            patterns_found = analysis_dict.get("error_patterns", [])
            symptoms = analysis_dict.get("possible_symptoms", [])

            # Update incident symptoms if empty
            if not incident.symptoms and symptoms:
                incident.symptoms = symptoms

            detail_str = (
                f"Identified {len(patterns_found)} error pattern(s): {', '.join(patterns_found)}"
                if patterns_found
                else "Log parsing completed; no critical signatures found."
            )
            ctx.log(f"Log analysis: {detail_str}")
            update_stage("evidence_analyzed", "completed", detail_str)
        except Exception as e:
            ctx.log(f"Log analysis failed: {e}")
            update_stage("evidence_analyzed", "failed", str(e))

        # -------------------------------------------------------------
        # STAGE 3: Service Inspected (Safe Simulated Diagnostics)
        # -------------------------------------------------------------
        try:
            ctx.log(f"Inspecting simulated diagnostic health for: {incident.service}")
            health_dict = inspect_service(incident.service)
            ctx.service_health = health_dict
            detail_str = f"Status: {health_dict.get('status')} | Latency: {health_dict.get('latency_ms')}ms | {health_dict.get('connection_state')}"
            ctx.log(f"Service health: {detail_str}")
            update_stage("service_inspected", "completed", detail_str)
        except Exception as e:
            ctx.log(f"Service inspection failed: {e}")
            update_stage("service_inspected", "failed", str(e))

        # -------------------------------------------------------------
        # STAGE 4: Runbooks Searched
        # -------------------------------------------------------------
        try:
            search_query = f"{incident.title} {' '.join(incident.symptoms)} {incident.service}"
            ctx.log(f"Searching operational runbooks with query: '{search_query[:50]}...'")
            runbooks = search_runbooks(search_query, service=incident.service)
            ctx.runbooks = runbooks
            if runbooks:
                top_rb = runbooks[0]
                incident.runbook_id = top_rb.get("id", "")
                detail_str = f"Found runbook {top_rb.get('id')} ({top_rb.get('title')})"
            else:
                detail_str = "No matching runbooks found in knowledge base."
            ctx.log(detail_str)
            update_stage("runbooks_searched", "completed", detail_str)
        except Exception as e:
            ctx.log(f"Runbook search error: {e}")
            update_stage("runbooks_searched", "failed", str(e))

        # -------------------------------------------------------------
        # STAGE 5: Hindsight Memory Recalled
        # -------------------------------------------------------------
        recalled_text_block = ""
        try:
            if settings.is_hindsight_configured:
                ctx.log(f"Querying Hindsight long-term memory bank: '{settings.hindsight_bank_id}'")
                recall_query = f"{incident.title} {incident.service} {' '.join(incident.symptoms)}"
                memories = self.memory_service.recall_memories(
                    query=recall_query,
                    tags=["incident", "resolution", "root_cause"],
                    budget="mid",
                )
                ctx.recalled_memories = memories
                if memories:
                    ctx.hindsight_used = True
                    detail_str = f"Recalled {len(memories)} relevant incident memory record(s) from Hindsight bank."
                    recalled_text_block = "\n".join([f"- {m.text}" for m in memories])
                    ctx.log(detail_str)
                    update_stage("memory_recalled", "completed", detail_str)
                else:
                    detail_str = "Hindsight queried: No matching prior incident memories found."
                    ctx.log(detail_str)
                    update_stage("memory_recalled", "completed", detail_str)
            else:
                detail_str = "Hindsight not configured: HINDSIGHT_API_KEY is missing."
                ctx.log(detail_str)
                update_stage("memory_recalled", "skipped", detail_str)
        except Exception as e:
            ctx.log(f"Hindsight recall error: {e}")
            update_stage("memory_recalled", "failed", f"Hindsight error: {str(e)}")

        # -------------------------------------------------------------
        # STAGE 6: Historical Incidents Compared
        # -------------------------------------------------------------
        try:
            if ctx.recalled_memories and recalled_text_block:
                ctx.log("Comparing current incident pattern against historical Hindsight memory...")
                comparison_dict = compare_incident_patterns(
                    current_symptoms=incident.symptoms,
                    current_service=incident.service,
                    historical_context=recalled_text_block,
                )
                ctx.pattern_comparison = comparison_dict
                score = comparison_dict.get("similarity_score", 0.0)
                relevance = comparison_dict.get("relevance_assessment", "")
                detail_str = f"Pattern similarity: {int(score * 100)}% | {relevance[:90]}..."
                ctx.log(detail_str)
                update_stage("patterns_compared", "completed", detail_str)
            else:
                detail_str = "Skipped: No historical memory available to compare."
                ctx.log(detail_str)
                update_stage("patterns_compared", "skipped", detail_str)
        except Exception as e:
            ctx.log(f"Pattern comparison error: {e}")
            update_stage("patterns_compared", "failed", str(e))

        # -------------------------------------------------------------
        # STAGE 7: Root Cause Assessed & Resolution Generated
        # -------------------------------------------------------------
        # Attempt LLM run via Microsoft Agent Framework if Groq configured
        llm_success = False
        if settings.is_groq_configured:
            try:
                ctx.log(f"Invoking Microsoft Agent Framework with Groq model '{settings.groq_model}'...")
                agent = self._build_agent_framework_agent()
                if agent:
                    user_prompt = INVESTIGATION_USER_PROMPT_TEMPLATE.format(
                        incident_id=incident.incident_id,
                        title=incident.title,
                        service=incident.service,
                        severity=incident.severity,
                        timestamp=incident.timestamp,
                        description=incident.description,
                        logs=incident.logs,
                    )
                    if recalled_text_block:
                        user_prompt += f"\n\nRECALLED HINDSIGHT HISTORICAL MEMORIES:\n{recalled_text_block}"

                    # Run Microsoft Agent Framework Agent
                    response = await agent.run(messages=user_prompt)
                    ctx.llm_used = True
                    llm_success = True
                    response_text = getattr(response, "text", str(response))
                    ctx.llm_response_text = response_text
                    ctx.log("Microsoft Agent Framework run completed successfully.")
            except Exception as e:
                ctx.log(f"Groq / Agent Framework execution error: {e}")
                ctx.error_message = f"LLM execution failed: {str(e)}"

        # Synthesize final IncidentReport
        try:
            report = self._assemble_report(ctx, llm_success=llm_success)
            ctx.report = report

            # Update incident with findings
            incident.root_cause = report.root_cause
            incident.resolution = "; ".join(report.recommended_actions)
            if report.runbook and report.runbook != "N/A":
                incident.runbook_id = report.runbook
            if report.lessons_learned:
                incident.lessons_learned = "; ".join(report.lessons_learned)
            incident.status = "INVESTIGATING"

            # Persist to SQLite
            db.save_incident(incident)
            db.save_report(incident.incident_id, report)

            update_stage("root_cause_assessed", "completed", f"Root Cause: {report.root_cause[:70]}...")
            update_stage("resolution_generated", "completed", f"Actions: {len(report.recommended_actions)} proposed steps. Runbook: {report.runbook}")
            ctx.log("Investigation completed and report persisted.")
        except Exception as e:
            ctx.log(f"Report assembly failed: {e}")
            update_stage("root_cause_assessed", "failed", str(e))
            update_stage("resolution_generated", "failed", str(e))

        return ctx

    def _assemble_report(
        self, ctx: InvestigationContext, llm_success: bool = False
    ) -> IncidentReport:
        """Deterministically assemble or enrich the structured IncidentReport."""
        incident = ctx.incident
        evidence_lines: List[str] = []
        if ctx.log_analysis:
            evidence_lines.extend(ctx.log_analysis.get("evidence_excerpts", []))
        if ctx.service_health:
            sh = ctx.service_health
            evidence_lines.append(
                f"Diagnostic Telemetry: {sh.get('health_state')} (Latency: {sh.get('latency_ms')}ms, Saturated: {sh.get('active_connections')}/{sh.get('max_connections')} connections)"
            )

        top_rb = ctx.runbooks[0] if ctx.runbooks else None
        rb_id = top_rb.get("id", "N/A") if top_rb else "N/A"

        # Determine historical match IDs
        historical_matches: List[str] = []
        previous_resolution = "None recalled"
        if ctx.recalled_memories:
            for mem in ctx.recalled_memories:
                historical_matches.append(mem.id)
                if "resolution:" in mem.text.lower() or "runbook applied:" in mem.text.lower():
                    previous_resolution = mem.text[:200]
            if ctx.pattern_comparison:
                for hid in ctx.pattern_comparison.get("historical_incident_ids", []):
                    if hid not in historical_matches:
                        historical_matches.append(hid)

        # Root cause deduction
        patterns = (ctx.log_analysis.get("error_patterns", []) if ctx.log_analysis else [])
        if "Connection Pool Exhaustion" in patterns or "Database Connection Timeout" in patterns:
            root_cause = (
                "Database connection pool exhaustion. Upstream worker threads saturated the connection pool "
                "due to unclosed database transactions or connection leaks under load."
            )
            confidence = "HIGH"
        elif "Upstream Gateway Timeout (504)" in patterns:
            root_cause = "Gateway ingress timeout caused by downstream service latency exhaustion."
            confidence = "MEDIUM"
        elif not evidence_lines:
            root_cause = "Insufficient evidence to determine the root cause."
            confidence = "LOW"
        else:
            root_cause = f"Service degradation in {incident.service} evidenced by error signatures: {', '.join(patterns)}."
            confidence = "MEDIUM"

        # Safe recommended actions
        recommended_actions: List[str] = []
        if top_rb and top_rb.get("recommended_remediation"):
            for act in top_rb.get("recommended_remediation")[:4]:
                if any(kw in act.lower() for kw in ["restart", "increase", "delete", "flush"]):
                    recommended_actions.append(f"[REQUIRES APPROVAL] {act}")
                else:
                    recommended_actions.append(act)
        else:
            recommended_actions = [
                "Inspect live error rates and active connection pools.",
                "[REQUIRES APPROVAL] Restart affected worker pods if connection leak persists.",
                "Review recent application deployments.",
            ]

        # Prior resolution context from Hindsight
        if ctx.recalled_memories and ctx.pattern_comparison and ctx.pattern_comparison.get("similarity_score", 0) > 0.5:
            relevance = ctx.pattern_comparison.get("relevance_assessment", "")
            recommended_actions.append(
                f"[HINDSIGHT EXPERIENCE APPLIED] High similarity with past incident. Prior resolution confirmed: '{previous_resolution[:120]}...'"
            )

        risks = [
            "Restarting service pods without connection drain may terminate inflight requests.",
            "Increasing pool size without database capacity review may overwhelm DB server memory.",
        ]
        follow_up = [
            "Audit application code for unhandled exceptions leaving DB sessions open.",
            "Configure Prometheus alerting for connection pool utilization > 80%.",
        ]
        lessons_learned = [
            f"Apply runbook {rb_id} immediately upon connection acquisition timeout.",
            "Ensure connection timeouts are configured with strict bounded deadlines.",
        ]

        summary = (
            f"Investigation of {incident.incident_id} ({incident.service}) identified: {root_cause} "
            f"Confidence: {confidence}. Runbook {rb_id} selected."
        )

        return IncidentReport(
            incident_id=incident.incident_id,
            title=incident.title,
            severity=incident.severity,
            affected_service=incident.service,
            summary=summary,
            evidence=evidence_lines,
            historical_matches=historical_matches,
            root_cause=root_cause,
            confidence=confidence,
            recommended_actions=recommended_actions,
            runbook=rb_id,
            previous_resolution=previous_resolution,
            risks=risks,
            follow_up=follow_up,
            lessons_learned=lessons_learned,
        )

    def investigate_sync(
        self,
        incident: Incident,
        stage_callback: Optional[Callable[[str, str, str], None]] = None,
    ) -> InvestigationContext:
        """Synchronous wrapper for investigate_async."""
        import concurrent.futures

        def _run_in_new_loop():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(
                    self.investigate_async(incident, stage_callback)
                )
            finally:
                new_loop.close()

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None and loop.is_running():
            # If an event loop is already running (e.g. inside Streamlit),
            # try nest_asyncio if installed, else execute in a dedicated thread.
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(
                    self.investigate_async(incident, stage_callback)
                )
            except Exception:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_run_in_new_loop)
                    return future.result()
        else:
            return _run_in_new_loop()


# Default coordinator instance
agent_coordinator = IncidentAgentCoordinator()
