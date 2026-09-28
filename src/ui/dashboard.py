"""Dashboard view for IncidentMind AI."""

import streamlit as st
import pandas as pd
from src.config import settings
from src.services.incident_service import incident_service
from src.services.persistence import db
from src.memory.memory_service import MemoryService


def render_dashboard() -> None:
    """Render the operations dashboard."""
    st.markdown(
        """
        <div class="brand-banner">
            <h1 class="brand-title">🛡️ IncidentMind AI Operations Dashboard</h1>
            <div class="brand-subtitle">
                Autonomous SRE Assistant powered by Microsoft Agent Framework, Groq LLM & Hindsight Long-Term Memory
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch real stats
    stats = incident_service.get_dashboard_stats()
    memory_service = MemoryService()
    hindsight_ok, hindsight_msg = memory_service.check_connection()
    groq_ok = settings.is_groq_configured

    # Top KPI Metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{stats['total']}</div>
                <div class="metric-label">Total Incidents</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #f85149;">{stats['critical']}</div>
                <div class="metric-label">Critical / High</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #d29922;">{stats['active']}</div>
                <div class="metric-label">Active Investigating</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #3fb950;">{stats['resolved']}</div>
                <div class="metric-label">Resolved</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col5:
        hindsight_badge = (
            "<span style='color: #3fb950;'>Active</span>"
            if hindsight_ok
            else "<span style='color: #8b949e;'>Not Set</span>"
        )
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #d2a8ff;">🧠</div>
                <div class="metric-label">Hindsight: {hindsight_badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Subsystems & Connectivity Status
    st.markdown("### 🔌 Core Subsystem Status")
    sc1, sc2, sc3 = st.columns(3)

    with sc1:
        st.markdown(
            """
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>🤖 Microsoft Agent Framework</span>
                    <span class="badge-healthy">Ready</span>
                </div>
                <p style="color: #8b949e; font-size: 0.85rem; margin-bottom: 6px;">
                    Orchestrates autonomous multi-tool invocation, memory context providers, and deterministic inspection pipelines.
                </p>
                <div style="font-size: 0.8rem; color: #58a6ff;">
                    Integration: <code>agent-framework-core v1.19</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with sc2:
        groq_badge = (
            '<span class="badge-healthy">Connected</span>'
            if groq_ok
            else '<span class="badge-high">Key Missing</span>'
        )
        st.markdown(
            f"""
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>⚡ Groq LLM Inference</span>
                    {groq_badge}
                </div>
                <p style="color: #8b949e; font-size: 0.85rem; margin-bottom: 6px;">
                    Ultra-fast inference provider delivering reasoning and incident synthesis.
                </p>
                <div style="font-size: 0.8rem; color: #58a6ff;">
                    Model: <code>{settings.groq_model}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with sc3:
        hs_badge = (
            '<span class="badge-healthy">Connected</span>'
            if hindsight_ok
            else '<span class="badge-high">Setup Required</span>'
        )
        st.markdown(
            f"""
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>🧠 Hindsight Long-Term Memory</span>
                    {hs_badge}
                </div>
                <p style="color: #8b949e; font-size: 0.85rem; margin-bottom: 6px;">
                    Persistent cross-session experience bank retaining root causes and successful remediations.
                </p>
                <div style="font-size: 0.8rem; color: #a371f7;">
                    Memory Bank: <code>{settings.hindsight_bank_id}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Core Value Prop Banner
    st.info(
        "💡 **The IncidentMind Differentiator:** Traditional SRE bots only ask *'What is broken right now?'* "
        "IncidentMind AI uses **Hindsight Long-Term Memory** to ask: *'What happened before, what worked, and how does that experience apply to this incident?'*"
    )

    # Recent Incidents Table
    st.markdown("### 📋 Recent Operational Incidents (Local SQLite Database)")
    incidents = db.list_incidents(limit=10)

    if incidents:
        table_data = []
        for inc in incidents:
            table_data.append(
                {
                    "Incident ID": inc.incident_id,
                    "Timestamp": inc.timestamp,
                    "Service": inc.service,
                    "Severity": inc.severity,
                    "Title": inc.title,
                    "Status": inc.status,
                    "Runbook": inc.runbook_id or "N/A",
                }
            )
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            """
            <div style="background: #161b22; border: 1px dashed #30363d; border-radius: 8px; padding: 30px; text-align: center; color: #8b949e;">
                <p style="margin: 0; font-size: 1rem;">No incidents recorded yet in the local database.</p>
                <p style="margin: 6px 0 0 0; font-size: 0.85rem;">Head over to <b>Demo Mode</b> to run Day 1 / Day 30 scenarios or launch an investigation in <b>Investigate Incident</b>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
