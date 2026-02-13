import streamlit as st

TRANSLATIONS = {
    "fr": {
        # NAV / TABS
        "tab_home": "🏠 Accueil",
        "tab_dashboard": "📊 Tableau de Bord",
        "tab_analysis": "📈 Analyse Avancée",
        "tab_alerts": "⚠️ Alertes",
        "tab_forecast": "🔮 Prévisions",
        "tab_data": "📂 Données",
        "tab_reports": "📑 Rapports",
        "tab_insights": "💡 Insights",
        "tab_support": "📞 Support",

        # SIDEBAR
        "config_title": "⚙️ Configuration",
        "upload_label": "📥 Chargez votre fichier (CSV/Excel)",
        "download_example": "📄 Télécharger fichier exemple",
        "stats_quick": "📊 Statistiques Rapides",
        "rows": "Lignes",
        "cols": "Colonnes",

        # COMMON
        "filters": "🔍 Filtres",
        "date_start": "Date de début",
        "date_end": "Date de fin",
        "category": "Catégories",
        "generate": "🔮 Générer les Prévisions",
        "show_conf": "Afficher intervalles de confiance (95%)",
    },

    "en": {
        # NAV / TABS
        "tab_home": "🏠 Home",
        "tab_dashboard": "📊 Dashboard",
        "tab_analysis": "📈 Advanced Analysis",
        "tab_alerts": "⚠️ Alerts",
        "tab_forecast": "🔮 Forecasting",
        "tab_data": "📂 Data",
        "tab_reports": "📑 Reports",
        "tab_insights": "💡 Insights",
        "tab_support": "📞 Support",

        # SIDEBAR
        "config_title": "⚙️ Settings",
        "upload_label": "📥 Upload your file (CSV/Excel)",
        "download_example": "📄 Download sample file",
        "stats_quick": "📊 Quick Stats",
        "rows": "Rows",
        "cols": "Columns",

        # COMMON
        "filters": "🔍 Filters",
        "date_start": "Start date",
        "date_end": "End date",
        "category": "Categories",
        "generate": "🔮 Generate Forecast",
        "show_conf": "Show confidence interval (95%)",
    }
}

def set_lang(lang: str):
    if lang not in ("fr", "en"):
        lang = "fr"
    st.session_state["lang"] = lang

def get_lang() -> str:
    return st.session_state.get("lang", "fr")

def t(key: str) -> str:
    lang = get_lang()
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["fr"].get(key, key))
