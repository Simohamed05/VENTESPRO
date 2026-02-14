import streamlit as st
import base64
from pathlib import Path


def _logo_data_uri(logo_path: str) -> str | None:
    p = Path(logo_path)
    if not p.exists() or not p.is_file():
        return None
    ext = p.suffix.lower().lstrip(".")
    if ext not in {"png", "jpg", "jpeg", "webp", "svg"}:
        return None
    mime = "image/svg+xml" if ext == "svg" else f"image/{'jpeg' if ext == 'jpg' else ext}"
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def render_topbar(app_status: str = "● Online", logo_path: str = "VentesPRO.png") -> None:
    """Topbar SaaS sticky (logo, statut, lien export)."""
    logo_uri = _logo_data_uri(logo_path)
    logo_html = f"<img src='{logo_uri}' alt='VentesPRO logo' />" if logo_uri else "📊"

    st.markdown(
        f"""
        <div class="vp-topbar">
          <div class="vp-topbar-left">
            <div class="vp-logo">{logo_html}</div>
            <div class="vp-brand">
              <div class="vp-title">VentesPRO</div>
              <div class="vp-subtitle">Analytics • Forecast • Alerts</div>
            </div>
          </div>

          <div class="vp-topbar-right">
            <span class="vp-status">{app_status}</span>
            <a class="vp-btn" href="#telechargements">Export</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
