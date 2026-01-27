import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


VP_PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#0f172a"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="rgba(15,23,42,0.98)", font=dict(color="white")),
        legend=dict(bgcolor="rgba(255,255,255,0)", borderwidth=0, orientation="h"),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(
            gridcolor="rgba(148,163,184,0.18)",
            zerolinecolor="rgba(148,163,184,0.18)",
            showline=False,
            tickfont=dict(color="#334155"),
            title=dict(font=dict(color="#0f172a")),
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.18)",
            zerolinecolor="rgba(148,163,184,0.18)",
            showline=False,
            tickfont=dict(color="#334155"),
            title=dict(font=dict(color="#0f172a")),
        ),
    )
)


CSS_STYLES = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --vp-bg: #f8fafc;
        --vp-surface: #ffffff;
        --vp-surface-strong: #f1f5f9;
        --vp-text: #0f172a;
        --vp-text-muted: #64748b;
        --vp-border: rgba(148, 163, 184, 0.35);
        --vp-border-strong: rgba(148, 163, 184, 0.6);
        --vp-primary: #2563eb;
        --vp-primary-strong: #1d4ed8;
        --vp-primary-soft: rgba(37, 99, 235, 0.1);
        --vp-accent: #0ea5e9;
        --vp-success: #16a34a;
        --vp-warning: #f59e0b;
        --vp-danger: #ef4444;
        --vp-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        --vp-shadow-soft: 0 6px 16px rgba(15, 23, 42, 0.08);
        --vp-radius: 16px;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --vp-bg: #0b1120;
            --vp-surface: #111827;
            --vp-surface-strong: #0f172a;
            --vp-text: #e2e8f0;
            --vp-text-muted: #94a3b8;
            --vp-border: rgba(148, 163, 184, 0.24);
            --vp-border-strong: rgba(148, 163, 184, 0.4);
            --vp-primary: #60a5fa;
            --vp-primary-strong: #3b82f6;
            --vp-primary-soft: rgba(96, 165, 250, 0.15);
            --vp-accent: #38bdf8;
            --vp-success: #22c55e;
            --vp-warning: #fbbf24;
            --vp-danger: #f87171;
            --vp-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
            --vp-shadow-soft: 0 10px 20px rgba(0, 0, 0, 0.25);
        }
    }

    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container - Adaptatif */
    .main {
        background: radial-gradient(circle at top, rgba(37, 99, 235, 0.08), transparent 40%),
                    radial-gradient(circle at 10% 20%, rgba(14, 165, 233, 0.08), transparent 45%),
                    var(--vp-bg);
        padding: 2rem;
    }

    /* Sidebar - Toujours sombre */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }

    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }

    /* Titres - Adaptatifs */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: var(--vp-text) !important;
    }

    h1 {
        background: linear-gradient(135deg, var(--vp-primary) 0%, var(--vp-accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }

    h2 {
        color: var(--vp-text) !important;
        border-bottom: 2px solid var(--vp-border);
        padding-bottom: 0.6rem;
        margin-top: 2rem !important;
    }

    h3 {
        color: var(--vp-primary) !important;
    }

    /* Cards - Adaptatifs selon le thème */
    .stCard {
        background: var(--vp-surface);
        border-radius: var(--vp-radius);
        padding: 1.5rem;
        box-shadow: var(--vp-shadow-soft);
        border: 1px solid var(--vp-border);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: var(--vp-text);
    }

    .stCard:hover {
        transform: translateY(-4px);
        box-shadow: var(--vp-shadow);
    }

    /* Metric Cards - Adaptatifs */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--vp-text) !important;
        background: none;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: var(--vp-text-muted) !important;
        opacity: 0.9;
    }

    /* Buttons - Toujours visibles */
    .stButton>button {
        background: linear-gradient(135deg, var(--vp-primary) 0%, var(--vp-primary-strong) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px;
        transition: all 0.3s ease !important;
        width: 100%;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 26px rgba(37, 99, 235, 0.25) !important;
    }

    /* Selectbox/Inputs - Toujours visibles */
    .stSelectbox>div>div {
        background-color: var(--vp-surface) !important;
        border-radius: 12px !important;
        border: 1px solid var(--vp-border) !important;
    }

    .stTextInput>div>div {
        background-color: var(--vp-surface) !important;
        border-radius: 12px !important;
        border: 1px solid var(--vp-border) !important;
    }

    .stNumberInput>div>div {
        background-color: var(--vp-surface) !important;
        border-radius: 12px !important;
        border: 1px solid var(--vp-border) !important;
    }

    .stTextArea>div>div {
        background-color: var(--vp-surface) !important;
        border-radius: 12px !important;
        border: 1px solid var(--vp-border) !important;
    }

    /* Tables - Adaptatifs */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--vp-shadow-soft);
        border: 1px solid var(--vp-border);
    }

    /* Alerts - Adaptatifs avec contraste */
    .stAlert {
        border-radius: 12px;
        border: none;
        padding: 1rem;
        color: var(--vp-text);
    }

    /* Success Alert */
    .stAlert[data-baseweb="notification"] {
        background: rgba(34, 197, 94, 0.12) !important;
        border: 1px solid rgba(34, 197, 94, 0.35) !important;
    }

    /* Info Alert */
    .stAlert[data-baseweb="notification"][kind="info"] {
        background: rgba(37, 99, 235, 0.12) !important;
        border: 1px solid rgba(37, 99, 235, 0.35) !important;
    }

    /* Warning Alert */
    .stAlert[data-baseweb="notification"][kind="warning"] {
        background: rgba(245, 158, 11, 0.12) !important;
        border: 1px solid rgba(245, 158, 11, 0.35) !important;
    }

    /* Error Alert */
    .stAlert[data-baseweb="notification"][kind="error"] {
        background: rgba(239, 68, 68, 0.12) !important;
        border: 1px solid rgba(239, 68, 68, 0.35) !important;
    }

    /* Download link */
    .download-link {
        display: inline-block;
        background: linear-gradient(135deg, var(--vp-primary) 0%, var(--vp-accent) 100%);
        color: white !important;
        padding: 10px 20px;
        border-radius: 12px;
        text-decoration: none !important;
        font-weight: 600;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .download-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 22px rgba(37, 99, 235, 0.24);
    }

    /* Topbar SaaS */
    .vp-topbar{
      position: sticky;
      top: 0;
      z-index: 999;
      display:flex;
      justify-content:space-between;
      align-items:center;
      padding: 14px 18px;
      border-radius: 18px;
      background: rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(148,163,184,0.18);
      box-shadow: 0 16px 30px rgba(0,0,0,0.2);
    }
    .vp-topbar-left{display:flex;gap:12px;align-items:center;}
    .vp-logo{
      width:42px;height:42px;display:flex;align-items:center;justify-content:center;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--vp-primary) 0%, var(--vp-accent) 100%);
      color:white;font-weight:700;
    }
    .vp-brand .vp-title{color:white;font-size:16px;font-weight:700;line-height:1;}
    .vp-brand .vp-subtitle{color:rgba(226,232,240,0.8);font-size:12px;margin-top:3px;}
    .vp-topbar-right{display:flex;gap:10px;align-items:center;}
    .vp-status{
      padding:6px 10px;border-radius:999px;
      background: rgba(34, 197, 94, 0.12);
      border:1px solid rgba(34, 197, 94, 0.3);
      color: rgba(226,232,240,0.95);
      font-size:12px;font-weight:600;
    }
    .vp-btn{
      display:inline-flex;align-items:center;justify-content:center;
      padding: 8px 14px;border-radius: 12px;
      background: linear-gradient(135deg, var(--vp-primary) 0%, var(--vp-accent) 100%);
      color:white !important;
      font-weight:700;
      text-decoration:none !important;
      box-shadow: 0 10px 20px rgba(14, 165, 233, 0.2);
    }

    /* Glass Card upgrade */
    .stCard{
      background: var(--vp-surface) !important;
      backdrop-filter: blur(12px);
    }

</style>
"""


def apply_global_styles() -> None:
    """Apply Plotly template and global CSS styles."""
    try:
        pio.templates["ventespro"] = VP_PLOTLY_TEMPLATE
        pio.templates.default = "ventespro"
    except Exception:
        pass

    st.markdown(CSS_STYLES, unsafe_allow_html=True)
