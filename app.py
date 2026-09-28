"""IncidentMind AI - Main Application Entrypoint with Top Navigation & Secondary Sidebar."""

import streamlit as st
from src.ui.styles import CUSTOM_CSS
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
    """Main application lifecycle and responsive two-tier navigation."""
    # Initialize active page state
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Dashboard"

    # =================================================================
    # 1. SECONDARY SIDEBAR NAVIGATION
    # =================================================================
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 6px 0 14px 0;">
                <div style="font-size: 1.35rem; font-weight: 700; color: #58a6ff; display: flex; align-items: center; gap: 8px;">
                    🛡️ IncidentMind AI
                </div>
                <div style="font-size: 0.82rem; color: #8b949e; margin-top: 4px;">
                    A Memory-Powered Incident Response Agent
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Secondary Navigation Items
        if st.button(
            "📖 Runbooks",
            use_container_width=True,
            type="primary" if st.session_state.active_page == "Runbooks" else "secondary",
        ):
            st.session_state.active_page = "Runbooks"
            st.rerun()

        if st.button(
            "🧠 Hindsight Memory",
            use_container_width=True,
            type="primary" if st.session_state.active_page == "Hindsight Memory" else "secondary",
        ):
            st.session_state.active_page = "Hindsight Memory"
            st.rerun()

        if st.button(
            "⚙️ System Information",
            use_container_width=True,
            type="primary" if st.session_state.active_page == "System Information" else "secondary",
        ):
            st.session_state.active_page = "System Information"
            st.rerun()

        st.markdown("---")

        st.markdown(
            """
            <div style="margin-top: 24px; font-size: 0.75rem; color: #484f58; text-align: center;">
                Microsoft AI Hackathon MVP<br>
                IncidentMind AI v1.0.0
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =================================================================
    # 2. MAIN HORIZONTAL TOP NAVIGATION BAR
    # =================================================================
    st.markdown(
        """
        <div class="top-nav-brand">
            <span style="font-size: 1.55rem; font-weight: 700; color: #58a6ff; display: inline-flex; align-items: center; gap: 8px;">
                🛡️ IncidentMind AI
            </span>
            <span style="font-size: 0.88rem; color: #8b949e;">
                A Memory-Powered Incident Response Agent
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Required Main Top Tabs: Dashboard | Demo Mode | Investigate Incident | Incident History
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)

    with t_col1:
        is_active = st.session_state.active_page == "Dashboard"
        if st.button(
            "📊 Dashboard",
            key="top_tab_dashboard",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_page = "Dashboard"
            st.rerun()

    with t_col2:
        is_active = st.session_state.active_page == "Demo Mode"
        if st.button(
            "🎬 Demo Mode",
            key="top_tab_demo",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_page = "Demo Mode"
            st.rerun()

    with t_col3:
        is_active = st.session_state.active_page == "Investigate Incident"
        if st.button(
            "🔍 Investigate Incident",
            key="top_tab_investigate",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_page = "Investigate Incident"
            st.rerun()

    with t_col4:
        is_active = st.session_state.active_page == "Incident History"
        if st.button(
            "📜 Incident History",
            key="top_tab_history",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_page = "Incident History"
            st.rerun()

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # =================================================================
    # 3. PAGE CONTENT ROUTER
    # =================================================================
    active = st.session_state.active_page

    if active == "Dashboard":
        render_dashboard()
    elif active == "Demo Mode":
        render_demo()
    elif active == "Investigate Incident":
        render_investigate()
    elif active == "Incident History":
        render_history()
    elif active == "Runbooks":
        render_runbooks()
    elif active == "Hindsight Memory":
        render_memory()
    elif active == "System Information":
        render_system()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
