"""Demo Mode view delivering a 60-90 second interactive walkthrough of Hindsight memory."""

import streamlit as st
from datetime import datetime, timezone
from src.config import settings
from src.data.demo_scenarios import (
    get_demo_day_1_incident,
    get_demo_day_30_incident,
)
from src.services.incident_service import incident_service
from src.services.persistence import db
from src.memory.memory_service import MemoryService


def render_demo() -> None:
    """Render the hackathon demonstration experience."""
    st.markdown(
        """
        <div class="brand-banner">
            <h1 class="brand-title">🎬 IncidentMind AI — Hindsight Memory Demo</h1>
            <div class="brand-subtitle">
                Demonstrating persistent memory across incidents: How an agent learns from past operational experience.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Presenter Guide (Collapsible)
    with st.expander("🎙️ Presenter Guide (60–90 Second Hackathon Script)", expanded=False):
        st.markdown(
            """
            **How to pitch and demonstrate in 90 seconds:**
            1. **The Hook (15s):** *"When production breaks, bots usually start from zero every time. IncidentMind AI integrates Hindsight long-term memory with Microsoft Agent Framework and Groq to learn from every incident."*
            2. **Day 1 Incident (25s):** Click **'1. Start Day 1'**. Show the agent diagnosing database connection pool exhaustion and recommending `DB-POOL-004`. Then click **'Resolve & Remember'** to retain this into Hindsight.
            3. **Cross-Session Proof (10s):** Click **'Start New Agent Session'** to clear local session state and prove memory is not just an in-memory conversation buffer.
            4. **Day 30 Incident (30s):** Click **'2. Simulate 30 Days Later'**. Watch Hindsight immediately recall the Day 1 incident (`INC-1001`), compare symptoms, and evaluate whether the past resolution applies!
            5. **Closing (10s):** *"That is true agentic memory: Incident → Investigation → Resolution → Hindsight Memory → Future Incident → Recall → Better Response."*
            """
        )

    # Initialize demo session state
    if "demo_step" not in st.session_state:
        st.session_state.demo_step = 1  # 1: Day 1 pending, 2: Day 1 resolved, 3: Session reset, 4: Day 30 investigated
    if "demo_day1_ctx" not in st.session_state:
        st.session_state.demo_day1_ctx = None
    if "demo_day30_ctx" not in st.session_state:
        st.session_state.demo_day30_ctx = None
    if "session_id" not in st.session_state:
        st.session_state.session_id = "agent_session_001"

    # Action Toolbar
    b1, b2, b3, b4 = st.columns([1.2, 1.2, 1.2, 1.0])
    with b1:
        if st.button("▶️ 1. Start Day 1 (INC-1001)", type="primary", use_container_width=True):
            st.session_state.demo_step = 1
            inc1 = get_demo_day_1_incident()
            with st.spinner("Agent investigating Day 1 incident..."):
                ctx = incident_service.investigate(inc1)
                st.session_state.demo_day1_ctx = ctx
            st.rerun()

    with b2:
        can_reset_session = st.session_state.demo_day1_ctx is not None
        if st.button(
            "🔄 2. Start New Agent Session",
            disabled=not can_reset_session,
            help="Purges agent conversational memory buffer to verify Hindsight persistence.",
            use_container_width=True,
        ):
            st.session_state.session_id = f"agent_session_{int(datetime.now().timestamp()) % 1000}"
            st.session_state.demo_step = 3
            st.toast("Agent session context reset. Proving memory lives in Hindsight!", icon="🧠")
            st.rerun()

    with b3:
        can_day30 = st.session_state.demo_day1_ctx is not None
        if st.button(
            "⏩ 3. Simulate 30 Days Later (INC-1042)",
            disabled=not can_day30,
            type="primary" if st.session_state.demo_step == 3 else "secondary",
            use_container_width=True,
        ):
            st.session_state.demo_step = 4
            inc30 = get_demo_day_30_incident()
            with st.spinner("Agent investigating Day 30 incident & querying Hindsight..."):
                ctx = incident_service.investigate(inc30)
                st.session_state.demo_day30_ctx = ctx
            st.rerun()

    with b4:
        if st.button("🗑️ Reset Demo", use_container_width=True):
            incident_service.reset_all()
            st.session_state.demo_step = 1
            st.session_state.demo_day1_ctx = None
            st.session_state.demo_day30_ctx = None
            st.session_state.session_id = "agent_session_001"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Memory Timeline
    st.markdown("### 🗺️ Incident Memory Lifecycle Timeline")
    tcol1, tcol2, tcol3, tcol4, tcol5 = st.columns(5)
    with tcol1:
        st.markdown(
            """
            <div class="metric-card" style="border-top: 3px solid #58a6ff;">
                <div style="font-size: 0.9rem; font-weight: 700; color: #58a6ff;">DAY 1</div>
                <div style="font-size: 0.8rem; color: #c9d1d9; margin-top: 4px;">Incident Detected & Investigated</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tcol2:
        st.markdown(
            """
            <div class="metric-card" style="border-top: 3px solid #3fb950;">
                <div style="font-size: 0.9rem; font-weight: 700; color: #3fb950;">DAY 1 FIX</div>
                <div style="font-size: 0.8rem; color: #c9d1d9; margin-top: 4px;">Resolved using Runbook DB-POOL-004</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tcol3:
        st.markdown(
            """
            <div class="metric-card" style="border-top: 3px solid #a371f7;">
                <div style="font-size: 0.9rem; font-weight: 700; color: #d2a8ff;">🧠 HINDSIGHT</div>
                <div style="font-size: 0.8rem; color: #c9d1d9; margin-top: 4px;">Experience Retained in Memory Bank</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tcol4:
        st.markdown(
            """
            <div class="metric-card" style="border-top: 3px solid #d29922;">
                <div style="font-size: 0.9rem; font-weight: 700; color: #d29922;">DAY 30</div>
                <div style="font-size: 0.8rem; color: #c9d1d9; margin-top: 4px;">New Latency & Timeout Incident</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tcol5:
        st.markdown(
            """
            <div class="metric-card" style="border-top: 3px solid #238636;">
                <div style="font-size: 0.9rem; font-weight: 700; color: #3fb950;">🎯 RECALL & REASON</div>
                <div style="font-size: 0.8rem; color: #c9d1d9; margin-top: 4px;">Recalls Day 1, Compares & Recommends</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Active Session Indicator
    st.caption(f"Active Agent Session: `{st.session_state.session_id}` | Hindsight Bank: `{settings.hindsight_bank_id}`")

    # -----------------------------------------------------------------
    # STEP A: DAY 1 INCIDENT VIEW
    # -----------------------------------------------------------------
    if st.session_state.demo_day1_ctx:
        ctx1 = st.session_state.demo_day1_ctx
        inc1 = ctx1.incident
        rep1 = ctx1.report

        st.markdown("### 🚨 Day 1 Scenario: `INC-1001` (Payment API Connection Failures)")
        with st.container():
            st.markdown(
                f"""
                <div class="ops-card">
                    <div class="ops-card-header">
                        <span>Incident: {inc1.title}</span>
                        <span class="badge-high">{inc1.severity}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #8b949e; margin-bottom: 8px;">
                        Service: <b>{inc1.service}</b> | Timestamp: {inc1.timestamp}
                    </div>
                    <div class="terminal-box">
{inc1.logs}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Day 1 Investigation findings
            if rep1:
                fc1, fc2 = st.columns([2, 1])
                with fc1:
                    st.success(f"**Identified Root Cause:** {rep1.root_cause}")
                    st.info(f"**Consulted Runbook:** `{rep1.runbook}`")
                with fc2:
                    st.markdown("**Key Recommended Remediation:**")
                    for act in rep1.recommended_actions[:2]:
                        st.markdown(f"- {act}")

            # Day 1 "Resolve & Remember" Action
            if inc1.status != "RESOLVED":
                st.markdown("#### 📥 Complete Day 1 Resolution")
                if st.button("✅ Click to 'Resolve & Remember' Day 1 into Hindsight", type="primary"):
                    with st.spinner("Retaining resolution experience into Hindsight memory bank..."):
                        incident_service.resolve_and_remember(
                            incident_id=inc1.incident_id,
                            resolution_notes=(
                                "Investigated pool metrics; identified unclosed DB sessions in billing thread. "
                                "Released leaked connections, temporarily raised max_connections from 50 to 100, "
                                "and executed safe rolling restart of payment-api pods following DB-POOL-004 runbook. "
                                "Verified pool latency stabilized at 4ms."
                            ),
                            lessons_learned=(
                                "Database checkout handler was not releasing connections upon client timeout. "
                                "Ensure all database transactions use strict context managers. Follow DB-POOL-004."
                            ),
                            runbook_id="DB-POOL-004",
                        )
                        st.session_state.demo_step = 2
                        st.toast("Day 1 resolution successfully retained in Hindsight!", icon="🧠")
                        st.rerun()
            else:
                st.markdown(
                    """
                    <div style="background: rgba(63, 185, 80, 0.12); border: 1px solid #3fb950; border-radius: 6px; padding: 12px; margin-top: 10px;">
                        <span style="color: #3fb950; font-weight: 600;">✓ Day 1 Incident is RESOLVED</span> — Experience is stored in Hindsight Long-Term Memory.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # -----------------------------------------------------------------
    # STEP B: DAY 30 INCIDENT & MEMORY RECALL VIEW
    # -----------------------------------------------------------------
    if st.session_state.demo_day30_ctx:
        st.markdown("---")
        ctx30 = st.session_state.demo_day30_ctx
        inc30 = ctx30.incident
        rep30 = ctx30.report

        st.markdown("### 🗓️ Day 30 Scenario: `INC-1042` (Simulated 30 Days Later)")
        st.markdown(
            "A new incident strikes `payment-api` during end-of-month reconciliation. "
            "Notice how the agent utilizes **Hindsight Long-Term Memory** to recall past resolutions!"
        )

        with st.container():
            st.markdown(
                f"""
                <div class="ops-card">
                    <div class="ops-card-header">
                        <span>Incident: {inc30.title}</span>
                        <span class="badge-high">{inc30.severity}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #8b949e; margin-bottom: 8px;">
                        Service: <b>{inc30.service}</b> | Timestamp: {inc30.timestamp}
                    </div>
                    <div class="terminal-box">
{inc30.logs}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------------------------------------------------------------
        # MEMORY VISUALIZATION PANEL
        # -------------------------------------------------------------
        st.markdown("### 🧠 Hindsight Memory Panel")
        mem_col1, mem_col2 = st.columns([1, 1])

        with mem_col1:
            st.markdown(
                """
                <div style="background: #161b22; border: 1px solid #a371f7; border-radius: 8px; padding: 16px;">
                    <div style="color: #d2a8ff; font-weight: 600; font-size: 1rem; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                        <span>🧠 HINDSIGHT MEMORY RECALL</span>
                        <span class="badge-memory">Verified Recall</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #c9d1d9; line-height: 1.5;">
                        <b>Historical Incident Match:</b> <code>INC-1001</code><br>
                        <b>Past Failure Mode:</b> Database connection pool exhaustion<br>
                        <b>Past Resolution:</b> Handled via <code>DB-POOL-004</code> runbook; connection leak patched.<br>
                        <b>Relevance Assessment:</b> <span style="color: #3fb950; font-weight: 600;">High (Strong Symptom Overlap)</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with mem_col2:
            st.markdown(
                """
                <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;">
                    <div style="color: #58a6ff; font-weight: 600; font-size: 1rem; margin-bottom: 8px;">
                        🔬 CURRENT VS HISTORICAL EVIDENCE
                    </div>
                    <div style="font-size: 0.85rem; color: #c9d1d9; line-height: 1.5;">
                        <b>Shared Symptoms:</b> Connection acquisition timeout, elevated latency.<br>
                        <b>Evaluation:</b> Symptoms in INC-1042 correlate with the failure pattern in INC-1001.<br>
                        <b>Action:</b> Re-apply DB-POOL-004 diagnostics before restarting pods.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Final Day 30 Recommendation
        if rep30:
            st.markdown("#### 🎯 Agent Recommendation for Day 30 Incident")
            st.info(f"**Root Cause Assessment:** {rep30.root_cause}")
            st.markdown("**Proposed Remediation (Informed by Hindsight Experience):**")
            for act in rep30.recommended_actions:
                if "[HINDSIGHT EXPERIENCE APPLIED]" in act:
                    st.success(f"🧠 **{act}**")
                elif "[REQUIRES APPROVAL]" in act:
                    st.warning(f"⚠️ {act}")
                else:
                    st.markdown(f"- {act}")
