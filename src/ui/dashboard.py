"""Dashboard view for IncidentMind AI."""

import streamlit as st
import pandas as pd
from src.config import settings
from src.services.incident_service import incident_service
from src.services.persistence import db
from src.memory.memory_service import MemoryService


def render_dashboard() -> None:
    """Render the concise operations dashboard."""
    # Prominent Differentiator Callout Banner
    st.markdown(
        """
        <div class="brand-banner" style="padding: 18px 24px; margin-bottom: 20px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #58a6ff; margin-bottom: 6px;">
                💡 The IncidentMind AI Differentiator
            </div>
            <div style="font-size: 0.95rem; color: #c9d1d9; line-height: 1.5;">
                Traditional incident bots ask: <i>"What is broken right now?"</i><br>
                <b>IncidentMind asks:</b> <i>"What happened before, what worked, and how does that experience apply to this incident?"</i>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch real stats from SQLite and Hindsight
    incidents = db.list_incidents(limit=100)
    stats = incident_service.get_dashboard_stats()
    
    # Compute metrics
    total_count = len(incidents)
    active_investigations = len([i for i in incidents if i.status == "INVESTIGATING"])
    recent_resolutions = len([i for i in incidents if i.status == "RESOLVED"])
    
    # Severity distribution
    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for inc in incidents:
        s = inc.severity.upper()
        if s in sev_counts:
            sev_counts[s] += 1
        else:
            sev_counts["MEDIUM"] += 1

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
                <div class="metric-value" style="color: #f85149;">{sev_counts['CRITICAL'] + sev_counts['HIGH']}</div>
                <div class="metric-label">Critical / High</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #d29922;">{active_investigations}</div>
                <div class="metric-label">Active Investigating</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #3fb950;">{recent_resolutions}</div>
                <div class="metric-label">Recent Resolutions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: #d2a8ff;">🧠 {settings.hindsight_bank_id}</div>
                <div class="metric-label">Hindsight Memory Bank</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Operational Breakdown: Severity & Memory Activity
    oc1, oc2 = st.columns([1, 1])

    with oc1:
        st.markdown("### 📊 Severity Distribution")
        st.markdown(
            f"""
            <div class="ops-card">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.88rem;">
                    <div>
                        <span class="badge-critical">CRITICAL</span>: <b>{sev_counts['CRITICAL']}</b> incident(s)
                    </div>
                    <div>
                        <span class="badge-high">HIGH</span>: <b>{sev_counts['HIGH']}</b> incident(s)
                    </div>
                    <div>
                        <span class="badge-healthy">MEDIUM</span>: <b>{sev_counts['MEDIUM']}</b> incident(s)
                    </div>
                    <div>
                        <span class="badge-memory">LOW</span>: <b>{sev_counts['LOW']}</b> incident(s)
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with oc2:
        st.markdown("### 🧠 Memory & Learning Activity")
        st.markdown(
            f"""
            <div class="ops-card">
                <div style="font-size: 0.88rem; color: #c9d1d9; line-height: 1.6;">
                    <b>Memory Bank:</b> <code>{settings.hindsight_bank_id}</code><br>
                    <b>Retention Mode:</b> Automatic on incident resolution<br>
                    <b>Learning Loop:</b> Retains failure patterns, symptoms & resolutions for cross-session recall.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Recent Incidents Table
    st.markdown("### 📋 Recent Operational Incidents (Local SQLite Database)")
    recent_incidents = db.list_incidents(limit=10)

    if recent_incidents:
        table_data = []
        for inc in recent_incidents:
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
            <div style="background: #161b22; border: 1px dashed #30363d; border-radius: 8px; padding: 24px; text-align: center; color: #8b949e;">
                <p style="margin: 0; font-size: 1rem; color: #c9d1d9;">No incidents recorded yet in the local database.</p>
                <p style="margin: 6px 0 0 0; font-size: 0.85rem;">
                    Switch to <b>Demo Mode</b> in the top navigation to run the Day 1 / Day 30 scenarios, or submit an incident in <b>Investigate Incident</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
