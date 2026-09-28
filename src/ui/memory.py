"""Hindsight Memory view for exploring persistent agent experience and testing recall."""

import streamlit as st
from src.config import settings
from src.memory.memory_service import MemoryService
from src.agent.schemas import MemoryEntry


def render_memory() -> None:
    """Render the enhanced Hindsight Memory Explorer."""
    st.markdown("## 🧠 Hindsight Long-Term Memory")
    st.markdown(
        "Hindsight provides biomimetic, persistent memory that learns from every resolved incident. "
        "Unlike short-term chat buffers or naive vector databases, Hindsight stores structured "
        "**World Facts, Experiences, Observations, and Mental Models** that survive across sessions and agent restarts."
    )

    mem_service = MemoryService()
    connected, msg = mem_service.check_connection()

    # -----------------------------------------------------------------
    # 1. Memory Bank
    # -----------------------------------------------------------------
    st.markdown("### 🏦 Memory Bank")
    mb_col1, mb_col2, mb_col3 = st.columns(3)
    with mb_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.25rem; color: #d2a8ff;">{settings.hindsight_bank_id}</div>
                <div class="metric-label">Bank ID</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mb_col2:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.25rem; color: #58a6ff;">Isolated Namespace</div>
                <div class="metric-label">Memory Boundary</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mb_col3:
        st.markdown(
            """
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.25rem; color: #3fb950;">Cross-Session</div>
                <div class="metric-label">Persistence Mode</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 2. Memory Operations (Retain, Recall, Reflect)
    # -----------------------------------------------------------------
    st.markdown("### ⚙️ Memory Operations")
    op1, op2, op3 = st.columns(3)
    with op1:
        st.markdown(
            """
            <div class="ops-card" style="border-top: 3px solid #3fb950;">
                <div class="ops-card-header">
                    <span style="color: #3fb950;">📥 Retain</span>
                </div>
                <p style="color: #c9d1d9; font-size: 0.88rem; line-height: 1.5;">
                    <b>Stores incident knowledge</b> after an investigation is resolved. Retains symptoms, affected services, root causes, runbooks used, successful remediation steps, and postmortem lessons learned.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with op2:
        st.markdown(
            """
            <div class="ops-card" style="border-top: 3px solid #58a6ff;">
                <div class="ops-card-header">
                    <span style="color: #58a6ff;">🔍 Recall</span>
                </div>
                <p style="color: #c9d1d9; font-size: 0.88rem; line-height: 1.5;">
                    <b>Retrieves relevant historical knowledge</b> when a new incident is investigated. Automatically injected into the agent's instructions before reasoning begins via <code>HindsightProvider</code>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with op3:
        st.markdown(
            """
            <div class="ops-card" style="border-top: 3px solid #a371f7;">
                <div class="ops-card-header">
                    <span style="color: #d2a8ff;">💡 Reflect</span>
                </div>
                <p style="color: #c9d1d9; font-size: 0.88rem; line-height: 1.5;">
                    <b>Synthesizes higher-order reasoning</b> and operational patterns across multiple incidents, refining mental models of service vulnerabilities, flaky dependencies, and runbook efficacy.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------------------
    # 3. Memory Timeline
    # -----------------------------------------------------------------
    st.markdown("### 🗺️ Incident Memory Lifecycle Timeline")
    st.markdown(
        """
        <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; text-align: center;">
                <div style="flex: 1; min-width: 130px; background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid #30363d;">
                    <div style="font-weight: 700; color: #58a6ff;">1. Incident</div>
                    <div style="font-size: 0.78rem; color: #8b949e; margin-top: 4px;">Outage Detected</div>
                </div>
                <div style="color: #58a6ff; font-weight: 700;">➔</div>
                <div style="flex: 1; min-width: 130px; background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid #30363d;">
                    <div style="font-weight: 700; color: #58a6ff;">2. Investigation</div>
                    <div style="font-size: 0.78rem; color: #8b949e; margin-top: 4px;">Logs & Runbooks Analyzed</div>
                </div>
                <div style="color: #58a6ff; font-weight: 700;">➔</div>
                <div style="flex: 1; min-width: 130px; background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid #30363d;">
                    <div style="font-weight: 700; color: #3fb950;">3. Resolution</div>
                    <div style="font-size: 0.78rem; color: #8b949e; margin-top: 4px;">Fix Executed Safely</div>
                </div>
                <div style="color: #a371f7; font-weight: 700;">➔</div>
                <div style="flex: 1; min-width: 130px; background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid #a371f7;">
                    <div style="font-weight: 700; color: #d2a8ff;">4. Memory Retained</div>
                    <div style="font-size: 0.78rem; color: #8b949e; margin-top: 4px;">Stored in Hindsight</div>
                </div>
                <div style="color: #d29922; font-weight: 700;">➔</div>
                <div style="flex: 1; min-width: 130px; background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid #30363d;">
                    <div style="font-weight: 700; color: #d29922;">5. Future Incident</div>
                    <div style="font-size: 0.78rem; color: #8b949e; margin-top: 4px;">Similar Outage Occurs</div>
                </div>
                <div style="color: #3fb950; font-weight: 700;">➔</div>
                <div style="flex: 1; min-width: 130px; background: #0d1117; padding: 12px; border-radius: 6px; border: 1px solid #238636;">
                    <div style="font-weight: 700; color: #3fb950;">6. Memory Recalled</div>
                    <div style="font-size: 0.78rem; color: #8b949e; margin-top: 4px;">Past Fix Re-applied</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------
    # 4. Cross-Session Persistence
    # -----------------------------------------------------------------
    st.markdown("### 🔒 Cross-Session Persistence Architecture")
    st.markdown(
        """
        <div class="ops-card">
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; font-size: 0.88rem;">
                <div style="background: #161b22; padding: 12px; border-radius: 6px; border: 1px solid #30363d;">
                    <div style="font-weight: 600; color: #f0f6fc; margin-bottom: 6px;">1. Current Session State</div>
                    <p style="color: #8b949e; margin: 0;">
                        Ephemeral Streamlit memory holding UI input values and active widgets. Wiped completely when refreshing the browser or clicking <i>"Start New Agent Session"</i>.
                    </p>
                </div>
                <div style="background: #161b22; padding: 12px; border-radius: 6px; border: 1px solid #30363d;">
                    <div style="font-weight: 600; color: #a371f7; margin-bottom: 6px;">2. Historical Memory (Hindsight)</div>
                    <p style="color: #8b949e; margin: 0;">
                        Durable long-term memory residing in Hindsight bank <code>incidentmind-demo</code>. Persists permanently across sessions, days, and container restarts.
                    </p>
                </div>
                <div style="background: #161b22; padding: 12px; border-radius: 6px; border: 1px solid #30363d;">
                    <div style="font-weight: 600; color: #3fb950; margin-bottom: 6px;">3. Recalled Historical Incidents</div>
                    <p style="color: #8b949e; margin: 0;">
                        Semantic match results dynamically queried from Hindsight and injected into the agent instructions to inform active investigation reasoning.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------
    # 5. Stored Incident Knowledge
    # -----------------------------------------------------------------
    st.markdown("### 🗄️ Stored Incident Knowledge")

    # Attempt to query actual memories from Hindsight if connected
    retained_memories = []
    if connected:
        try:
            retained_memories = mem_service.recall_memories(
                query="incident resolution root cause connection pool",
                tags=["incident", "resolution"],
                budget="high",
            )
        except Exception:
            retained_memories = []

    if retained_memories:
        st.success(f"Retrieved {len(retained_memories)} verified memory record(s) from Hindsight bank '{settings.hindsight_bank_id}'.")
        for mem in retained_memories:
            with st.expander(f"🧠 Incident Memory: {mem.id} ({mem.type})", expanded=True):
                st.markdown(f"**Retained Incident Experience:**\n```\n{mem.text}\n```")
                if mem.tags:
                    st.markdown(f"**Tags:** `{'`, `'.join(mem.tags)}`")
                if mem.context:
                    st.caption(f"Context source: {mem.context}")
    else:
        st.markdown(
            f"""
            <div style="background: #161b22; border: 1px dashed #30363d; border-radius: 8px; padding: 24px; text-align: center; color: #8b949e;">
                <p style="margin: 0; font-size: 1rem; color: #c9d1d9;">No memories currently stored or Hindsight memory bank is empty.</p>
                <p style="margin: 6px 0 0 0; font-size: 0.85rem;">
                    To populate memory: Go to <b>Demo Mode</b>, run <b>Day 1</b>, and click <b>'Resolve & Remember'</b> to retain your first incident resolution!
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 6. Live Memory Recall Query Sandbox
    # -----------------------------------------------------------------
    st.markdown("### 🧪 Live Memory Recall Query Sandbox")
    st.markdown("Test live semantic querying against your Hindsight memory bank:")

    with st.form("hindsight_sandbox_form"):
        query = st.text_input(
            "Query Terms or Symptoms",
            value="payment-api database connection pool exhausted timeout",
            placeholder="Enter symptoms or incident query...",
        )
        tag_filter = st.multiselect(
            "Filter by Memory Tags (Optional)",
            ["incident", "resolution", "root_cause", "service:payment-api", "severity:high", "runbook:db-pool-004"],
            default=["incident", "resolution"],
        )
        budget = st.select_slider("Recall Budget", options=["low", "mid", "high"], value="mid")
        run_query = st.form_submit_button("🔍 Query Hindsight Memory", type="primary")

    if run_query:
        if not connected:
            st.warning(
                "Hindsight API is currently not connected. Ensure HINDSIGHT_API_KEY is configured in your environment."
            )
        else:
            with st.spinner(f"Querying Hindsight bank '{settings.hindsight_bank_id}'..."):
                sandbox_results = mem_service.recall_memories(
                    query=query.strip(),
                    tags=tag_filter if tag_filter else None,
                    budget=budget,
                )

            if sandbox_results:
                st.success(f"Retrieved {len(sandbox_results)} matching memory item(s) from Hindsight!")
                for m in sandbox_results:
                    with st.expander(f"🧠 Memory Item: {m.id} ({m.type})", expanded=True):
                        st.markdown(f"**Content:**\n```\n{m.text}\n```")
                        if m.tags:
                            st.markdown(f"**Tags:** `{'`, `'.join(m.tags)}`")
            else:
                st.info(
                    "No memories returned for this query. If you just ran Day 1, make sure to click "
                    "'Resolve & Remember' to store the resolution into Hindsight first!"
                )
