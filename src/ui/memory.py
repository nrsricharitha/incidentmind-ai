"""Hindsight Memory view for exploring persistent agent experience and testing recall."""

import streamlit as st
from src.config import settings
from src.memory.memory_service import MemoryService
from src.agent.schemas import MemoryEntry


def render_memory() -> None:
    """Render the Hindsight Memory Explorer and Query Sandbox."""
    st.markdown("## 🧠 Hindsight Long-Term Memory Explorer")
    st.markdown(
        "Hindsight gives AI agents biomimetic, persistent memory that learns over time. "
        "Unlike short-term chat buffers or naive vector search, Hindsight stores structured "
        "**World Facts, Experiences, Observations, and Mental Models** that survive across sessions."
    )

    mem_service = MemoryService()
    connected, msg = mem_service.check_connection()

    # Memory Bank Status Card
    st.markdown("### 🏦 Memory Bank Configuration")
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.3rem; color: #d2a8ff;">{settings.hindsight_bank_id}</div>
                <div class="metric-label">Active Bank ID</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b_col2:
        status_color = "#3fb950" if connected else "#f85149"
        status_text = "ONLINE" if connected else "NOT CONNECTED"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.3rem; color: {status_color};">{status_text}</div>
                <div class="metric-label">Hindsight Cloud Status</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.3rem; color: #58a6ff;">Agent Framework</div>
                <div class="metric-label">Integration Hook</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(f"Status Detail: {msg}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Memory Architecture & Lifecycle
    st.markdown("### 🧬 How Hindsight Powers IncidentMind AI")
    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        st.markdown(
            """
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>1. 📥 RETAIN</span>
                </div>
                <p style="color: #8b949e; font-size: 0.85rem;">
                    When an incident is resolved, its failure mode, root cause, runbook, and lessons learned are retained as durable operational experience.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ac2:
        st.markdown(
            """
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>2. 🔍 RECALL</span>
                </div>
                <p style="color: #8b949e; font-size: 0.85rem;">
                    Before analyzing future incidents, the <code>HindsightProvider</code> hook automatically recalls semantically relevant prior experiences into the agent's context.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with ac3:
        st.markdown(
            """
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>3. 💡 REFLECT</span>
                </div>
                <p style="color: #8b949e; font-size: 0.85rem;">
                    Synthesizes recurring failure patterns across multiple incidents into mental models of system vulnerabilities and runbook efficacy.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Live Memory Recall Sandbox
    st.markdown("### 🧪 Live Hindsight Memory Recall Sandbox")
    st.markdown(
        "Directly test querying your Hindsight memory bank. "
        "Enter any incident symptoms or query below to see what the agent would recall:"
    )

    with st.form("hindsight_sandbox_form"):
        query = st.text_input(
            "Recall Query",
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
            st.error(
                "Cannot query Hindsight: HINDSIGHT_API_KEY is not configured or endpoint is unreachable. "
                "Configure your key in the sidebar or in .env."
            )
        else:
            with st.spinner(f"Querying Hindsight bank '{settings.hindsight_bank_id}'..."):
                memories = mem_service.recall_memories(
                    query=query.strip(),
                    tags=tag_filter if tag_filter else None,
                    budget=budget,
                )

            if memories:
                st.success(f"Retrieved {len(memories)} matching memory item(s) from Hindsight!")
                for m in memories:
                    with st.expander(f"🧠 Memory Item: {m.id} ({m.type})", expanded=True):
                        st.markdown(f"**Content:**\n```\n{m.text}\n```")
                        if m.tags:
                            st.markdown(f"**Tags:** `{'`, `'.join(m.tags)}`")
                        if m.context:
                            st.caption(f"Context source: {m.context}")
            else:
                st.info(
                    "No memories returned for this query. If you just ran Day 1, make sure to click "
                    "'Resolve & Remember' to store the resolution into Hindsight first!"
                )
