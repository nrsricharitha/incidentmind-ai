"""Custom CSS styling for IncidentMind AI dark SRE / Operations Console."""

CUSTOM_CSS = """
<style>
/* Global theme refinements */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre, .stCode, [data-testid="stMarkdownContainer"] code {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Header branding banner */
.brand-banner {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #090d13 100%);
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.brand-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: #58a6ff;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-subtitle {
    font-size: 1.05rem;
    color: #8b949e;
    margin-top: 6px;
    font-weight: 400;
}

/* Metric / Stat cards */
.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #f0f6fc;
}

.metric-label {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #8b949e;
    margin-top: 4px;
}

/* Status badges */
.badge-critical {
    background-color: rgba(248, 81, 73, 0.15);
    color: #f85149;
    border: 1px solid #f85149;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 0.75rem;
}

.badge-high {
    background-color: rgba(210, 153, 34, 0.15);
    color: #d29922;
    border: 1px solid #d29922;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 0.75rem;
}

.badge-healthy {
    background-color: rgba(63, 185, 80, 0.15);
    color: #3fb950;
    border: 1px solid #3fb950;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 0.75rem;
}

.badge-memory {
    background-color: rgba(163, 113, 247, 0.15);
    color: #d2a8ff;
    border: 1px solid #a371f7;
    border-radius: 4px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 0.75rem;
}

/* Ops Console Cards */
.ops-card {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
}

.ops-card-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f0f6fc;
    margin-bottom: 12px;
    border-bottom: 1px solid #21262d;
    padding-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Stage step indicators */
.stage-item {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: 6px;
    border-radius: 6px;
    font-size: 0.9rem;
}

.stage-completed {
    background-color: rgba(63, 185, 80, 0.1);
    color: #3fb950;
    border-left: 4px solid #3fb950;
}

.stage-failed {
    background-color: rgba(248, 81, 73, 0.1);
    color: #f85149;
    border-left: 4px solid #f85149;
}

.stage-skipped {
    background-color: rgba(139, 148, 158, 0.1);
    color: #8b949e;
    border-left: 4px solid #8b949e;
}

.stage-running {
    background-color: rgba(88, 166, 255, 0.1);
    color: #58a6ff;
    border-left: 4px solid #58a6ff;
}

/* Timeline component */
.timeline-step {
    padding: 12px 16px;
    border-left: 2px solid #58a6ff;
    margin-left: 12px;
    position: relative;
    margin-bottom: 12px;
}

.timeline-step::before {
    content: "●";
    color: #58a6ff;
    position: absolute;
    left: -7px;
    top: 10px;
    font-size: 14px;
}

/* Terminal log look */
.terminal-box {
    background: #05080c;
    border: 1px solid #21262d;
    border-radius: 6px;
    padding: 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #c9d1d9;
    overflow-x: auto;
    max-height: 280px;
    overflow-y: auto;
}

/* Top Horizontal Navigation Styling */
.top-nav-container {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 24px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
}

.top-nav-brand {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #21262d;
}

/* Top Navigation Buttons */
div[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background: linear-gradient(135deg, #1f6feb 0%, #238636 100%) !important;
    border: 1px solid #388bfd !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    box-shadow: 0 0 10px rgba(31, 111, 235, 0.35) !important;
}

div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #58a6ff !important;
    color: #58a6ff !important;
    background: #161b22 !important;
}

/* Secondary Sidebar Navigation Buttons */
section[data-testid="stSidebar"] button[kind="primary"] {
    background: rgba(88, 166, 255, 0.15) !important;
    border: 1px solid #58a6ff !important;
    color: #58a6ff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}

section[data-testid="stSidebar"] button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #21262d !important;
    color: #8b949e !important;
    text-align: left !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    border-color: #30363d !important;
    color: #f0f6fc !important;
    background: #161b22 !important;
}
</style>
"""
