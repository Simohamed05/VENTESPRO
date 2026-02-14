import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


VP_PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Plus Jakarta Sans, Segoe UI, sans-serif", size=13, color="#0f172a"),
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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700&display=swap');

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
        --vp-sidebar-bg: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        --vp-sidebar-text: #e2e8f0;
        --vp-hero-grad-1: rgba(37, 99, 235, 0.1);
        --vp-hero-grad-2: rgba(14, 165, 233, 0.09);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --vp-bg: #0b1120;
            --vp-surface: #111827;
            --vp-surface-strong: #0f172a;
            --vp-text: #e2e8f0;
            --vp-text-muted: #f1f5f9;
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
            --vp-sidebar-bg: linear-gradient(180deg, #030712 0%, #0f172a 100%);
            --vp-sidebar-text: #e2e8f0;
            --vp-hero-grad-1: rgba(96, 165, 250, 0.13);
            --vp-hero-grad-2: rgba(56, 189, 248, 0.12);
        }
    }

    /* Global Styles */
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container - Adaptatif */
    .main {
        background: radial-gradient(circle at top, var(--vp-hero-grad-1), transparent 42%),
                    radial-gradient(circle at 8% 22%, var(--vp-hero-grad-2), transparent 48%),
                    linear-gradient(120deg, rgba(2, 132, 199, 0.03), transparent 35%),
                    var(--vp-bg);
        padding: 2rem;
    }

    .stApp {
        background: var(--vp-bg);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--vp-sidebar-bg) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }

    [data-testid="stSidebar"] * {
        color: var(--vp-sidebar-text) !important;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: var(--vp-sidebar-text) !important;
    }

    /* File uploader sidebar: lisibilité élevée */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
        color: #0f172a !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
        color: #475569 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        background: #e2e8f0 !important;
        color: #0f172a !important;
        border: 1px solid #94a3b8 !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
        background: #cbd5e1 !important;
    }

    /* Download button sidebar: lisibilité élevée */
    [data-testid="stSidebar"] .stDownloadButton > button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #1d4ed8 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.28) !important;
    }
    [data-testid="stSidebar"] .stDownloadButton > button:hover {
        background: #1d4ed8 !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }

    /* Titres - Adaptatifs */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Sora', 'Plus Jakarta Sans', sans-serif !important;
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

    [data-testid="stMetric"] {
        background: linear-gradient(180deg, color-mix(in oklab, var(--vp-surface) 88%, transparent), var(--vp-surface));
        border: 1px solid var(--vp-border);
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: var(--vp-shadow-soft);
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
      background: linear-gradient(120deg, rgba(15, 23, 42, 0.82), rgba(30, 41, 59, 0.64));
      backdrop-filter: blur(16px);
      border: 1px solid rgba(148,163,184,0.18);
      box-shadow: 0 16px 30px rgba(0,0,0,0.2);
    }
    .vp-topbar-left{display:flex;gap:12px;align-items:center;}
    .vp-logo{
      width:48px;height:48px;display:flex;align-items:center;justify-content:center;
      border-radius: 14px;
      background: linear-gradient(135deg, var(--vp-primary) 0%, var(--vp-accent) 100%);
      color:white;font-weight:700;
      overflow:hidden;
      box-shadow: 0 8px 18px rgba(14, 165, 233, 0.25);
    }
    .vp-logo img{
      width:100%;
      height:100%;
      object-fit:cover;
      border-radius: inherit;
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
    /* ===================== TABS (st.tabs) - BIG + CENTER + ATTRACTIVE ===================== */
    div[data-testid="stTabs"]{
      position: static;
      top: auto;
      z-index: 1;
      background: transparent;
      padding-top: 6px;
    }
    
    /* Conteneur des tabs */
    div[data-testid="stTabs"] [role="tablist"]{
  display: flex !important;
  justify-content: center !important;
  gap: 14px !important;
  flex-wrap: nowrap !important;
  overflow-x: auto !important;
  white-space: nowrap !important;

  background: color-mix(in oklab, var(--vp-surface-strong) 68%, transparent) !important;
  border: none !important;
  box-shadow: var(--vp-shadow-soft) !important;
  border-radius: 999px !important;
  padding: 12px 0 !important;
  margin: 10px auto 20px auto !important;
}
    @media (prefers-color-scheme: dark){
      div[data-testid="stTabs"] [role="tablist"]{
        background: rgba(17,24,39,0.55);
        border: 1px solid rgba(148,163,184,0.22);
      }
    }
    
    /* Boutons tabs */
    div[data-testid="stTabs"] button[role="tab"]{
      padding: 10px 16px !important;
      border-radius: 999px !important;
      font-weight: 700 !important;
      font-size: 15px !important;
      border: 1px solid var(--vp-border) !important;
      background: var(--vp-surface) !important;
      color: var(--vp-text) !important;
      transition: all .2s ease-in-out;
      box-shadow: 0 8px 16px rgba(15,23,42,0.08);
    }
    
    div[data-testid="stTabs"] button[role="tab"]:hover{
      transform: translateY(-2px);
      border-color: var(--vp-border-strong) !important;
      box-shadow: var(--vp-shadow-soft);
    }
    
    /* Tab active */
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"]{
      background: linear-gradient(135deg, var(--vp-primary) 0%, var(--vp-accent) 100%) !important;
      color: white !important;
      border: none !important;
      box-shadow: 0 14px 26px rgba(37, 99, 235, 0.22);
    }
    
    /* Cache la barre rouge/bleue fine par défaut */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"]{
      display:none !important;
    }
    
    /* Réduit l’espace inutile au-dessus du contenu */
    div[data-testid="stTabs"] [data-testid="stVerticalBlock"]{
      gap: 0.3rem;
    }

    [data-testid="stForm"] {
      background: color-mix(in oklab, var(--vp-surface) 93%, transparent);
      border: 1px solid var(--vp-border);
      border-radius: 16px;
      padding: 14px;
      box-shadow: var(--vp-shadow-soft);
    }

    @keyframes vpFadeUp {
      from { opacity: .0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    [data-testid="block-container"] > div {
      animation: vpFadeUp .34s ease both;
    }

    @media (max-width: 900px) {
      .main {
        padding: 1rem;
      }
      .vp-topbar{
        position: static;
        padding: 12px;
        border-radius: 14px;
      }
      .vp-brand .vp-title{
        font-size: 14px;
      }
      .vp-brand .vp-subtitle{
        display:none;
      }
      div[data-testid="stTabs"] [role="tablist"]{
        justify-content: flex-start !important;
        padding: 8px !important;
        margin: 8px 0 14px 0 !important;
      }
      div[data-testid="stTabs"] button[role="tab"]{
        font-size: 13px !important;
        padding: 8px 12px !important;
      }
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


def apply_theme_overrides(theme_mode: str = "auto") -> None:
    """Apply runtime theme overrides: auto | light | dark."""
    if theme_mode not in {"auto", "light", "dark"}:
        theme_mode = "auto"

    if theme_mode == "auto":
        st.markdown(
            """
<style>
    :root{
        color-scheme: light dark;
    }
    .stApp{
        transition: background-color .25s ease, color .25s ease;
    }
</style>
""",
            unsafe_allow_html=True,
        )
        return

    if theme_mode == "light":
        vars_block = """
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
        --vp-sidebar-bg: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        --vp-sidebar-text: #e2e8f0;
        --vp-hero-grad-1: rgba(37, 99, 235, 0.1);
        --vp-hero-grad-2: rgba(14, 165, 233, 0.09);
        """
        color_scheme = "light"
    else:
        vars_block = """
        --vp-bg: #0b1120;
        --vp-surface: #111827;
        --vp-surface-strong: #0f172a;
        --vp-text: #e2e8f0;
        --vp-text-muted: #f1f5f9;
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
        --vp-sidebar-bg: linear-gradient(180deg, #030712 0%, #0f172a 100%);
        --vp-sidebar-text: #e2e8f0;
        --vp-hero-grad-1: rgba(96, 165, 250, 0.13);
        --vp-hero-grad-2: rgba(56, 189, 248, 0.12);
        """
        color_scheme = "dark"

    st.markdown(
        f"""
<style>
    :root {{
        color-scheme: {color_scheme};
        {vars_block}
    }}

    .stApp {{
        transition: background-color .25s ease, color .25s ease;
    }}

    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div:focus-within,
    .stNumberInput > div > div:focus-within,
    .stTextArea > div > div:focus-within {{
        border-color: var(--vp-primary) !important;
        box-shadow: 0 0 0 2px var(--vp-primary-soft) !important;
    }}

    .stButton > button,
    .stDownloadButton > button {{
        letter-spacing: .2px;
    }}

    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--vp-border-strong);
        border-radius: 999px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--vp-surface-strong);
    }}
</style>
""",
        unsafe_allow_html=True,
    )
