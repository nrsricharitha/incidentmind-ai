"""IncidentMind AI - Streamlit Application Entrypoint."""

import streamlit as st
from src.ui.styles import CUSTOM_CSS
from src.config import settings
from src.memory.memory_service import MemoryService
from src.ui.dashboard import render_dashboard
from src.ui.investigate import render_investigate
from src.ui.history import render_history
from src.ui.runbooks import render_runbooks
from src.ui.memory import render_memory
from src.ui.demo import render_demo
from src.ui.system import render_system

# Page configuration
st.set_page_config(
    page_title="IncidentMind AI — Memory-Powered Incident Response",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply dark SRE / operations styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main() -> None:
    """Main application navigation and lifecycle."""
    # Sidebar Navigation & Branding
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #30363d; margin-bottom: 16px;">
            <div style="font-size: 1.4rem; font-weight: 700; color: #58a6ff; display: flex; align-items: center; gap: 8px;">
                🛡️ IncidentMind AI
            </div>
            <div style="font-size: 0.82rem; color: #8b949e; margin-top: 4px;">
                A Memory-Powered Incident Response Agent
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation menu
    nav_options = [
        "🛡️ Dashboard",
        "🎬 Demo Mode",
        "🔍 Investigate Incident",
        "📜 Incident History",
        "📖 Runbooks",
        "🧠 Hindsight Memory",
        "⚙️ System Information",
    ]

    selected_nav = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=1,  # Default to Demo Mode for fast presentation
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")

    # Connectivity Badges in Sidebar
    mem_service = MemoryService()
    hindsight_ok, _ = mem_service.check_connection()
    groq_ok = settings.is_groq_configured

    st.sidebar.markdown("#### ⚡ Platform Status")
    st.sidebar.markdown(
        f"""
        <div style="font-size: 0.85rem; line-height: 1.8;">
            <b>Groq LLM:</b> {'<span class="badge-healthy">Connected</span>' if groq_ok else '<span class="badge-high">Key Missing</span>'}<br>
            <b>Hindsight:</b> {'<span class="badge-healthy">Connected</span>' if hindsight_ok else '<span class="badge-high">Key Missing</span>'}<br>
            <b>Bank:</b> <code>{settings.hindsight_bank_id}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Sidebar Settings / Key Configuration Expander
    with st.sidebar.expander("🔑 Configure API Keys", expanded=not (groq_ok and hindsight_ok)):
        st.markdown(
            "<p style='font-size: 0.8rem; color: #8b949e;'>Enter API keys here or define them in your <code>.env</code> file.</p>",
            unsafe_allow_html=True,
        )
        groq_input = st.text_input(
            "Groq API Key",
            value=settings.groq_api_key or "",
            type="password",
            placeholder="gsk_...",
        )
        hindsight_input = st.text_input(
            "Hindsight API Key",
            value=settings.hindsight_api_key or "",
            type="password",
            placeholder="hnd_...",
        )
        bank_input = st.text_input(
            "Hindsight Bank ID",
            value=settings.hindsight_bank_id,
            placeholder="incidentmind-demo",
        )

        if st.button("💾 Apply Key Configuration", use_container_width=True):
            settings.set_groq_api_key(groq_input)
            settings.set_hindsight_api_key(hindsight_input)
            settings.set_hindsight_bank_id(bank_input)
            st.toast("Settings applied successfully!", icon="✅")
            st.rerun()

    st.sidebar.markdown(
        """
        <div style="margin-top: 30px; font-size: 0.75rem; color: #484f58; text-align: center;">
            Microsoft AI Hackathon MVP<br>
            IncidentMind AI v1.0.0
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Route navigation
    if selected_nav == "🛡️ Dashboard":
        render_dashboard()
    elif selected_nav == "🎬 Demo Mode":
        render_demo()
    elif selected_nav == "🔍 Investigate Incident":
        render_investigate()
    elif selected_nav == "📜 Incident History":
        render_history()
    elif selected_nav == "📖 Runbooks":
        render_runbooks()
    elif selected_nav == "🧠 Hindsight Memory":
        render_memory()
    elif selected_nav == "⚙️ System Information":
        render_system()


if __name__ == "__main__":
    main()
