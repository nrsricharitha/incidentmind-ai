"""Runbooks view for browsing and searching standardized operational procedures."""

import streamlit as st
from src.tools.runbook_search import load_all_runbooks, search_runbooks


def render_runbooks() -> None:
    """Render the operational runbooks knowledge base."""
    st.markdown("## 📖 Operational Runbook Library")
    st.markdown(
        "Standard operating procedures (SOPs) available to the Incident Response Agent during investigations. "
        "**Key Architectural Distinction:** Runbooks represent *static institutional knowledge*, "
        "whereas **Hindsight** stores *dynamic operational experience* learned from resolved incidents."
    )

    query = st.text_input(
        "Search Runbooks by symptom, service, or title:",
        placeholder="e.g. database connection pool, 500 error, redis timeout...",
    )

    if query.strip():
        results = search_runbooks(query.strip())
        st.caption(f"Found {len(results)} matching runbook(s) for query: '{query}'")
    else:
        results = [rb.model_dump() for rb in load_all_runbooks()]

    if not results:
        st.warning("No runbooks found matching your search criteria.")
        return

    st.markdown("### 📚 Runbook Library")

    for rb in results:
        sev = rb.get("severity", "HIGH")
        badge_class = "badge-critical" if sev == "CRITICAL" else "badge-high"
        inc_type = rb.get("incident_type", "System Degradation")
        root_cause = rb.get("likely_root_cause", "Resource saturation or dependency failure")
        remediation_steps = rb.get("recommended_remediation", [])

        st.markdown(
            f"""
            <div class="ops-card">
                <div class="ops-card-header">
                    <span style="font-size: 1.15rem; font-weight: 700; color: #58a6ff;">
                        📘 {rb['id']} — {rb['title']}
                    </span>
                    <div>
                        <span class="{badge_class}" style="margin-right: 8px;">{sev}</span>
                        <span class="badge-healthy">{rb['service']}</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 10px; font-size: 0.88rem;">
                    <div>
                        <span style="color: #8b949e; font-weight: 600;">Incident Type:</span><br>
                        <span style="color: #f0f6fc;">{inc_type}</span>
                    </div>
                    <div>
                        <span style="color: #8b949e; font-weight: 600;">Related Service:</span><br>
                        <code>{rb['service']}</code>
                    </div>
                </div>
                <div style="margin-top: 12px; font-size: 0.88rem;">
                    <span style="color: #8b949e; font-weight: 600;">Likely Root Cause:</span><br>
                    <span style="color: #c9d1d9;">{root_cause}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"🔍 View Symptoms, Diagnostics & Resolution Steps for {rb['id']}", expanded=False):
            st.markdown("**Known Symptoms:**")
            st.write(", ".join([f"`{s}`" for s in rb.get("symptoms", [])]))

            rc1, rc2 = st.columns(2)
            with rc1:
                st.markdown("**Diagnostic Steps:**")
                for idx, step in enumerate(rb.get("diagnostic_steps", []), 1):
                    st.markdown(f"{idx}. {step}")

            with rc2:
                st.markdown("**Resolution & Remediation Steps:**")
                for idx, rem in enumerate(remediation_steps, 1):
                    st.markdown(f"{idx}. {rem}")

            if rb.get("related_runbooks"):
                st.markdown(f"**Related Runbooks:** {', '.join([f'`{r}`' for r in rb['related_runbooks']])}")
