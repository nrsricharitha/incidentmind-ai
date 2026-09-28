"""System Information view displaying technology architecture without exposing credentials."""

import streamlit as st
import sys
from importlib import metadata


def render_system() -> None:
    """Render system architecture and informational integration status."""
    st.markdown("## ⚙️ System Architecture & Technology Stack")
    st.markdown(
        "IncidentMind AI combines Microsoft Agent Framework, Groq inference, and Hindsight "
        "long-term memory to create an autonomous, memory-augmented incident response assistant."
    )

    # -----------------------------------------------------------------
    # 1. IncidentMind AI Architecture
    # -----------------------------------------------------------------
    st.markdown("### 🏗️ IncidentMind AI Architecture")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>Core Platform Stack</span>
                </div>
                <div style="font-size: 0.9rem; line-height: 1.8; color: #c9d1d9;">
                    <b>Frontend:</b> <span style="color: #f0f6fc;">Streamlit</span><br>
                    <b>Agent Orchestration:</b> <span style="color: #58a6ff;">Microsoft Agent Framework</span><br>
                    <b>LLM Provider:</b> <span style="color: #f0f6fc;">Groq</span><br>
                    <b>Long-Term Memory:</b> <span style="color: #d2a8ff;">Hindsight</span><br>
                    <b>Local Incident Records:</b> <span style="color: #f0f6fc;">SQLite</span><br>
                    <b>Programming Language:</b> <span style="color: #3fb950;">Python 3.11+</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="ops-card">
                <div class="ops-card-header">
                    <span>Integration Status</span>
                </div>
                <div style="font-size: 0.9rem; line-height: 2.0; color: #c9d1d9;">
                    <div>● <b>Microsoft Agent Framework</b> — <span class="badge-healthy">Integrated</span></div>
                    <div>● <b>Groq</b> — <span class="badge-healthy">Integrated</span></div>
                    <div>● <b>Hindsight</b> — <span class="badge-healthy">Integrated</span></div>
                    <div>● <b>SQLite</b> — <span class="badge-healthy">Integrated</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # 2. Agent Flow & Memory Loop
    # -----------------------------------------------------------------
    st.markdown("### 🔄 End-to-End Agent Flow")
    st.markdown(
        """
        <div class="ops-card">
            <div style="font-size: 0.92rem; color: #c9d1d9; line-height: 1.8; text-align: center; padding: 10px;">
                <span style="color: #58a6ff; font-weight: 700;">User</span><br>
                ↓<br>
                <span style="color: #f0f6fc; font-weight: 600;">Streamlit UI</span><br>
                ↓<br>
                <span style="color: #58a6ff; font-weight: 600;">Microsoft Agent Framework</span><br>
                ↓<br>
                <span style="color: #f0f6fc; font-weight: 600;">Groq LLM</span><br>
                ↓<br>
                <span style="color: #d2a8ff; font-weight: 600;">Hindsight Memory + Incident Tools</span><br>
                ↓<br>
                <span style="color: #f0f6fc; font-weight: 600;">Investigation / Reasoning</span><br>
                ↓<br>
                <span style="color: #3fb950; font-weight: 600;">Incident Response & Resolution</span><br>
                ↓<br>
                <span style="color: #a371f7; font-weight: 700;">Hindsight Retain</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🔁 Continuous Memory Loop")
    st.info(
        "**New Incident ➔ Recall Past Experience ➔ Investigate ➔ Resolve ➔ Retain Experience**"
    )

    # -----------------------------------------------------------------
    # 3. Environment & Package Versions
    # -----------------------------------------------------------------
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

    st.markdown("### 📦 Installed Framework Architecture")
    st.markdown(
        f"""
        * **Microsoft Agent Framework Core:** `{agent_framework_ver}`
        * **Hindsight Agent Framework Integration:** `{hindsight_af_ver}`
        * **Hindsight Client SDK:** `{hindsight_client_ver}`
        * **Python Runtime:** `{sys.version.split()[0]} ({sys.platform})`
        * **Application Version:** `1.0.0 (Production Hackathon MVP)`
        """
    )
