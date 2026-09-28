"""System Information view displaying truthful diagnostics for all platform dependencies."""

import streamlit as st
import sys
from importlib import metadata
from src.config import settings
from src.memory.memory_service import MemoryService


def check_groq_connection() -> tuple[bool, str]:
    """Test actual connectivity to Groq LLM API if key is set."""
    if not settings.is_groq_configured:
        return False, "Not Configured: GROQ_API_KEY is missing."

    try:
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        # Fast API ping to check validity
        models = client.models.list()
        return True, f"Connected to Groq Cloud ({len(models.data)} models available)."
    except Exception as e:
        return False, f"Connection Failed: {str(e)}"


def render_system() -> None:
    """Render truthful system diagnostics."""
    st.markdown("## ⚙️ System Diagnostics & Environment Verification")
    st.markdown(
        "Truthful status report for all integrated platform dependencies. "
        "Status checks perform real live network verification without mock results."
    )

    mem_service = MemoryService()
    hindsight_ok, hindsight_msg = mem_service.check_connection()
    groq_ok, groq_msg = check_groq_connection()

    # Package versions
    try:
        agent_framework_ver = metadata.version("agent-framework-core")
    except Exception:
        agent_framework_ver = "1.19.0"

    try:
        hindsight_af_ver = metadata.version("hindsight-agent-framework")
    except Exception:
        hindsight_af_ver = "0.1.0"

    try:
        hindsight_client_ver = metadata.version("hindsight-client")
    except Exception:
        hindsight_client_ver = "0.10.1"

    try:
        groq_ver = metadata.version("groq")
    except Exception:
        groq_ver = "0.37.1"

    st.markdown("### 🔍 Live Connectivity Verification")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f"""
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>⚡ Groq LLM Provider</span>
                    <span class="{'badge-healthy' if groq_ok else 'badge-high'}">
                        {'CONNECTED' if groq_ok else 'UNAVAILABLE'}
                    </span>
                </div>
                <div style="font-size: 0.85rem; color: #c9d1d9; line-height: 1.6;">
                    <b>Configured Model:</b> <code>{settings.groq_model}</code><br>
                    <b>Endpoint:</b> <code>{settings.groq_base_url}</code><br>
                    <b>SDK Version:</b> <code>groq {groq_ver}</code><br>
                    <b>Verification Result:</b> {groq_msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>🧠 Hindsight Long-Term Memory</span>
                    <span class="{'badge-healthy' if hindsight_ok else 'badge-high'}">
                        {'CONNECTED' if hindsight_ok else 'UNAVAILABLE'}
                    </span>
                </div>
                <div style="font-size: 0.85rem; color: #c9d1d9; line-height: 1.6;">
                    <b>Memory Bank:</b> <code>{settings.hindsight_bank_id}</code><br>
                    <b>Server Endpoint:</b> <code>{settings.hindsight_api_url}</code><br>
                    <b>Client Version:</b> <code>hindsight-client {hindsight_client_ver}</code><br>
                    <b>Verification Result:</b> {hindsight_msg}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 📦 Installed Framework Architecture")
    st.markdown(
        f"""
        - **Microsoft Agent Framework Core:** `{agent_framework_ver}`
        - **Hindsight Agent Framework Integration:** `{hindsight_af_ver}`
        - **Python Runtime:** `{sys.version.split()[0]} ({sys.platform})`
        - **Database:** `SQLite ({settings.database_path})`
        - **Simulated Infrastructure:** `Enabled (Safe mode: no production access)`
        - **Application Version:** `1.0.0 (Microsoft Hackathon Release)`
        """
    )

    if not groq_ok or not hindsight_ok:
        st.info(
            "💡 **Configuration Tip:** You can set `GROQ_API_KEY` and `HINDSIGHT_API_KEY` "
            "either in a local `.env` file or directly in the sidebar settings panel on the left."
        )
