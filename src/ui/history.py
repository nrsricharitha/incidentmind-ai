"""Incident History view displaying local SQLite application records."""

import streamlit as st
import pandas as pd
from src.services.persistence import db


def render_history() -> None:
    """Render the incident history and postmortem records."""
    st.markdown("## 📜 Operational Incident History")
    st.markdown(
        "Browse recorded incidents stored in the application's local SQLite database. "
        "Notice: **SQLite stores structured application records**, while **Hindsight stores long-term agent memory and experience**."
    )

    incidents = db.list_incidents(limit=50)

    if not incidents:
        st.info("No incidents found in local database records. Run an investigation or execute Demo Mode.")
        return

    # Filter / Search bar
    col_search, col_filter = st.columns([3, 1])
    with col_search:
        search_term = st.text_input("Search incidents by title, service, or ID:", placeholder="e.g. payment-api, INC-1001...")
    with col_filter:
        status_filter = st.selectbox("Status Filter", ["ALL", "OPEN", "INVESTIGATING", "RESOLVED"])

    filtered = incidents
    if status_filter != "ALL":
        filtered = [i for i in filtered if i.status == status_filter]
    if search_term.strip():
        term = search_term.strip().lower()
        filtered = [
            i for i in filtered
            if term in i.title.lower() or term in i.service.lower() or term in i.incident_id.lower()
        ]

    # Summary table
    table_rows = []
    for inc in filtered:
        table_rows.append(
            {
                "ID": inc.incident_id,
                "Service": inc.service,
                "Severity": inc.severity,
                "Title": inc.title,
                "Status": inc.status,
                "Runbook": inc.runbook_id or "N/A",
                "Timestamp": inc.timestamp,
            }
        )

    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    # Detailed Incident Inspector
    st.markdown("### 🔍 Inspect Incident Record")
    incident_ids = [inc.incident_id for inc in filtered]
    if incident_ids:
        selected_id = st.selectbox("Select Incident ID to view full details:", incident_ids)
        selected_inc = db.get_incident(selected_id)
        selected_rep = db.get_report(selected_id)

        if selected_inc:
            with st.container():
                st.markdown(
                    f"""
                    <div class="ops-card">
                        <div class="ops-card-header">
                            <span>{selected_inc.incident_id} — {selected_inc.title}</span>
                            <span class="badge-high">{selected_inc.severity}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #8b949e; margin-bottom: 10px;">
                            Service: <b>{selected_inc.service}</b> | Status: <b>{selected_inc.status}</b> | Recorded: {selected_inc.timestamp}
                        </div>
                        <div style="margin-bottom: 12px; color: #c9d1d9;">
                            <b>Description:</b> {selected_inc.description}
                        </div>
                        <div style="margin-bottom: 12px;">
                            <b>Raw Logs:</b>
                            <div class="terminal-box" style="margin-top: 6px;">
{selected_inc.logs}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                dc1, dc2 = st.columns(2)
                with dc1:
                    st.markdown("#### 🎯 Identified Root Cause")
                    st.write(selected_inc.root_cause or "Investigation in progress.")
                    st.markdown("#### 🛠️ Resolution Steps")
                    st.write(selected_inc.resolution or "Not yet resolved.")

                with dc2:
                    st.markdown("#### 📖 Runbook Applied")
                    st.write(f"`{selected_inc.runbook_id}`" if selected_inc.runbook_id else "None")
                    st.markdown("#### 💡 Lessons Learned")
                    st.write(selected_inc.lessons_learned or "None recorded.")
