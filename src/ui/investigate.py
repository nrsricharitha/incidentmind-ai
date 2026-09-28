"""Investigate Incident view for interactive incident diagnosis and resolution."""

import streamlit as st
from datetime import datetime, timezone
from src.config import settings
from src.agent.schemas import Incident, Severity, IncidentStatus
from src.services.incident_service import incident_service
from src.services.persistence import db
from src.data.demo_scenarios import DEMO_DAY_1_DATA, DEMO_DAY_30_DATA


def render_investigate() -> None:
    """Render the incident investigation view."""
    st.markdown("## 🔍 Autonomous Incident Investigation")
    st.markdown(
        "Submit an active technical incident or load a pre-configured scenario. "
        "The agent will inspect evidence, query Hindsight memory, consult runbooks, "
        "and generate a structured remediation report."
    )

    # Incident templates
    st.markdown("#### ⚡ Quick Load Incident Templates")
    tc1, tc2, tc3 = st.columns(3)
    
    if "form_title" not in st.session_state:
        st.session_state.form_title = ""
        st.session_state.form_service = "payment-api"
        st.session_state.form_severity = Severity.HIGH.value
        st.session_state.form_desc = ""
        st.session_state.form_logs = ""
        st.session_state.form_id = f"INC-{int(datetime.now().timestamp()) % 10000}"

    with tc1:
        if st.button("📥 Load Day 1 Scenario (DB Pool Exhaustion)", use_container_width=True):
            st.session_state.form_id = DEMO_DAY_1_DATA["incident_id"]
            st.session_state.form_title = DEMO_DAY_1_DATA["title"]
            st.session_state.form_service = DEMO_DAY_1_DATA["service"]
            st.session_state.form_severity = DEMO_DAY_1_DATA["severity"]
            st.session_state.form_desc = DEMO_DAY_1_DATA["description"]
            st.session_state.form_logs = DEMO_DAY_1_DATA["logs"]
            st.rerun()

    with tc2:
        if st.button("📥 Load Day 30 Scenario (Latency & Timeout)", use_container_width=True):
            st.session_state.form_id = DEMO_DAY_30_DATA["incident_id"]
            st.session_state.form_title = DEMO_DAY_30_DATA["title"]
            st.session_state.form_service = DEMO_DAY_30_DATA["service"]
            st.session_state.form_severity = DEMO_DAY_30_DATA["severity"]
            st.session_state.form_desc = DEMO_DAY_30_DATA["description"]
            st.session_state.form_logs = DEMO_DAY_30_DATA["logs"]
            st.rerun()

    with tc3:
        if st.button("🔄 Clear Form", use_container_width=True):
            st.session_state.form_id = f"INC-{int(datetime.now().timestamp()) % 10000}"
            st.session_state.form_title = ""
            st.session_state.form_service = "payment-api"
            st.session_state.form_severity = Severity.HIGH.value
            st.session_state.form_desc = ""
            st.session_state.form_logs = ""
            st.rerun()

    st.markdown("---")

    # Incident Input Form
    with st.form("incident_investigation_form"):
        fc1, fc2, fc3 = st.columns([2, 2, 1])
        with fc1:
            inc_id = st.text_input("Incident Identifier", value=st.session_state.form_id)
        with fc2:
            service = st.selectbox(
                "Impacted Service",
                ["payment-api", "database", "cache-service", "order-service", "user-service", "api-gateway"],
                index=["payment-api", "database", "cache-service", "order-service", "user-service", "api-gateway"].index(
                    st.session_state.form_service
                    if st.session_state.form_service in ["payment-api", "database", "cache-service", "order-service", "user-service", "api-gateway"]
                    else "payment-api"
                ),
            )
        with fc3:
            severity = st.selectbox(
                "Severity",
                [s.value for s in Severity],
                index=[s.value for s in Severity].index(st.session_state.form_severity),
            )

        title = st.text_input("Incident Title / Summary", value=st.session_state.form_title)
        description = st.text_area("Observable Problem Description", value=st.session_state.form_desc, height=80)
        logs = st.text_area(
            "Raw Logs & Error Stack Traces",
            value=st.session_state.form_logs,
            height=140,
            help="Paste relevant operational log lines or stack traces.",
        )

        submitted = st.form_submit_button("🚀 Investigate Incident", use_container_width=True, type="primary")

    if submitted:
        if not title.strip() or not service.strip():
            st.error("Please provide both an incident title and affected service.")
            return

        incident = Incident(
            incident_id=inc_id.strip() or f"INC-{int(datetime.now().timestamp()) % 10000}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            service=service.strip(),
            severity=severity,
            title=title.strip(),
            description=description.strip(),
            logs=logs.strip(),
            symptoms=[],
            status=IncidentStatus.INVESTIGATING.value,
        )

        st.session_state.active_incident = incident
        with st.spinner("Agent running multi-tool investigation workflow..."):
            ctx = incident_service.investigate(incident)
            st.session_state.investigation_context = ctx

    # Display Investigation Results
    if "investigation_context" in st.session_state:
        ctx = st.session_state.investigation_context
        report = ctx.report

        st.markdown("### 🚦 Agent Execution Stages")
        # Render stages truthfully
        stage_cols = st.columns(4)
        stages_list = list(ctx.stages.values())
        for idx, stage in enumerate(stages_list):
            col_target = stage_cols[idx % 4]
            with col_target:
                if stage.status == "completed":
                    st.markdown(
                        f"""
                        <div class="stage-item stage-completed">
                            <b>✓ {stage.label}</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif stage.status == "failed":
                    st.markdown(
                        f"""
                        <div class="stage-item stage-failed">
                            <b>✗ {stage.label}</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif stage.status == "skipped":
                    st.markdown(
                        f"""
                        <div class="stage-item stage-skipped">
                            <b>○ {stage.label}</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="stage-item stage-running">
                            <b>... {stage.label}</b>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)

        # Recalled Memory Alert / Panel (if memories recalled)
        if ctx.recalled_memories:
            st.markdown(
                f"""
                <div style="background: rgba(163, 113, 247, 0.12); border: 1px solid #a371f7; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #d2a8ff; display: flex; align-items: center; gap: 8px;">
                            🧠 Relevant Historical Memory Recalled from Hindsight
                        </h4>
                        <span class="badge-memory">{len(ctx.recalled_memories)} Memory Match(es)</span>
                    </div>
                    <p style="color: #c9d1d9; font-size: 0.9rem; margin: 8px 0 0 0;">
                        The agent retrieved verified experience from prior incidents in bank <code>{settings.hindsight_bank_id}</code>.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            for mem in ctx.recalled_memories:
                with st.expander(f"🧠 Recalled Memory: {mem.id} ({mem.type})", expanded=True):
                    st.markdown(f"**Retained Content:**\n```\n{mem.text}\n```")
                    if mem.tags:
                        st.markdown(f"**Tags:** `{'`, `'.join(mem.tags)}`")

        if report:
            # Main Report Card
            st.markdown("### 📋 Incident Investigation Report")

            r_col1, r_col2 = st.columns([3, 1])
            with r_col1:
                st.markdown(f"#### 🎯 Root Cause Assessment")
                st.info(f"**{report.root_cause}**")
            with r_col2:
                conf_color = "#3fb950" if report.confidence == "HIGH" else "#d29922"
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-value" style="color: {conf_color}; font-size: 1.5rem;">{report.confidence}</div>
                        <div class="metric-label">Confidence Assessment</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Evidence & Runbook Row
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                st.markdown("#### 🔬 Observed Evidence")
                if report.evidence:
                    for ev in report.evidence:
                        st.markdown(f"- <code>{ev}</code>", unsafe_allow_html=True)
                else:
                    st.write("No direct log evidence lines available.")

            with e_col2:
                st.markdown("#### 📖 Matched Runbook")
                if report.runbook and report.runbook != "N/A":
                    st.markdown(
                        f"""
                        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px;">
                            <div style="font-weight: 600; color: #58a6ff;">Runbook: {report.runbook}</div>
                            <div style="font-size: 0.85rem; color: #8b949e; margin-top: 4px;">
                                Consulted for standardized remediation steps.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.write("No matching runbook found.")

                if report.previous_resolution and report.previous_resolution != "None recalled":
                    st.markdown("#### 💡 Historical Resolution Recalled")
                    st.caption(f"{report.previous_resolution}")

            # Recommended Actions
            st.markdown("#### 🛠️ Recommended Actions")
            for act in report.recommended_actions:
                if "[REQUIRES APPROVAL]" in act:
                    st.warning(f"⚠️ {act}")
                elif "[HINDSIGHT EXPERIENCE APPLIED]" in act:
                    st.success(f"🧠 {act}")
                else:
                    st.markdown(f"- {act}")

            # Risks & Follow-up
            k_col1, k_col2 = st.columns(2)
            with k_col1:
                st.markdown("#### ⚠️ Operational Risks")
                for r in report.risks:
                    st.markdown(f"- {r}")
            with k_col2:
                st.markdown("#### 📌 Follow-up Actions")
                for f in report.follow_up:
                    st.markdown(f"- {f}")

            st.markdown("---")

            # -------------------------------------------------------------
            # Resolve & Remember Section
            # -------------------------------------------------------------
            st.markdown("### 💾 Resolve & Remember (Hindsight Memory Retention)")
            st.markdown(
                "When you resolve this incident, IncidentMind AI will record the successful remediation "
                "into **Hindsight Long-Term Memory**, so future similar incidents immediately recall this experience."
            )

            with st.form("resolve_incident_form"):
                res_notes = st.text_area(
                    "Resolution Actions Taken",
                    value="; ".join(report.recommended_actions[:3]),
                    height=80,
                )
                lessons = st.text_area(
                    "Lessons Learned & Postmortem Notes",
                    value="; ".join(report.lessons_learned),
                    height=70,
                )
                resolve_clicked = st.form_submit_button(
                    "✅ Resolve & Remember in Hindsight",
                    type="primary",
                    use_container_width=True,
                )

            if resolve_clicked:
                with st.spinner("Retaining resolution experience into Hindsight memory bank..."):
                    res_out = incident_service.resolve_and_remember(
                        incident_id=report.incident_id,
                        resolution_notes=res_notes.strip(),
                        lessons_learned=lessons.strip(),
                        runbook_id=report.runbook,
                    )

                hs_info = res_out.get("hindsight", {})
                if hs_info.get("retained"):
                    st.balloons()
                    st.success(
                        f"🎉 Incident {report.incident_id} marked as RESOLVED and permanently retained in Hindsight bank '{hs_info.get('bank_id')}'!"
                    )
                else:
                    st.warning(f"Incident marked as RESOLVED locally. Notice: {hs_info.get('message')}")
