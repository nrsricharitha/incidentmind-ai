"""Runbooks view for browsing and searching standardized operational procedures."""

import streamlit as st
from src.tools.runbook_search import load_all_runbooks, search_runbooks


def render_runbooks() -> None:
    """Render the operational runbooks knowledge base."""
    st.markdown("## 📖 Operational Runbooks Knowledge Base")
    st.markdown(
        "Standard operating procedures (SOPs) for known failure modes. "
        "**Key Architectural Distinction:** Runbooks represent *static application knowledge*, "
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

    for rb in results:
        with st.expander(f"📘 {rb['id']}: {rb['title']} (Service: {rb['service']})", expanded=True):
            st.markdown(f"**Target Service:** `{rb['service']}`")
            
            st.markdown("**Associated Symptoms:**")
            st.write(", ".join([f"`{s}`" for s in rb.get("symptoms", [])]))

            rc1, rc2 = st.columns(2)
            with rc1:
                st.markdown("**Diagnostic Steps:**")
                for idx, step in enumerate(rb.get("diagnostic_steps", []), 1):
                    st.markdown(f"{idx}. {step}")

            with rc2:
                st.markdown("**Recommended Remediation:**")
                for idx, rem in enumerate(rb.get("recommended_remediation", []), 1):
                    st.markdown(f"{idx}. {rem}")

            if rb.get("related_runbooks"):
                st.markdown(f"**Related Runbooks:** {', '.join([f'`{r}`' for r in rb['related_runbooks']])}")
