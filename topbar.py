import streamlit as st


def render_topbar(app_status: str = "● Online") -> None:
    """Topbar SaaS sticky (logo, statut, lien export)."""
    st.markdown(
        f"""
        <div class="vp-topbar">
          <div class="vp-topbar-left">
            <div class="vp-logo">📊</div>
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
