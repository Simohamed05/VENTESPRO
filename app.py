# app.py — VentesPRO (Version corrigée & robuste)

import os
import warnings
import traceback
import importlib
import importlib.util
from datetime import datetime, timedelta
from io import BytesIO

# i18n
from utils.i18n import t, set_lang, get_lang

# -----------------------------
# Warnings (AVANT tout import)
# -----------------------------
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# -----------------------------
# Imports principaux
# -----------------------------
import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# FIX CRITIQUE POUR NUMPY 2.0
# -----------------------------
try:
    numpy_version = tuple(map(int, np.__version__.split(".")[:2]))
    if numpy_version >= (2, 0):
        if not hasattr(np, "float_"):
            np.float_ = np.float64
        if not hasattr(np, "int_"):
            np.int_ = np.int64
        if not hasattr(np, "bool_"):
            np.bool_ = bool
except Exception:
    pass

# -----------------------------
# Dépendances optionnelles
# -----------------------------
try:
    from xgboost import XGBRegressor

    _XGBOOST_OK = True
except Exception:
    _XGBOOST_OK = False

_PROPHET_OK = importlib.util.find_spec("prophet") is not None
_SARIMAX_OK = importlib.util.find_spec("statsmodels.tsa.statespace.sarimax") is not None

# -----------------------------
# Visualisation
# -----------------------------
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------
# UI & utils
# -----------------------------
from ui.styles import apply_global_styles
from ui.topbar import render_topbar
from utils.data import load_data
from utils.email import SUPPORT_EMAIL, SUPPORT_PHONE, append_to_excel, send_email_safe
from utils.validation import validate_email, validate_phone

# -----------------------------
# Forecast utils
# -----------------------------
from models.forecasting import (
    basic_confidence_band,
    build_features,
    build_future_features,
    future_dates as build_future_dates,
    prepare_series,
)

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ============================================================
# Helpers
# ============================================================

def _safe_none_label() -> str:
    """Label translated for 'None' option (cat column)."""
    return t("none")

def _is_none_choice(val: str) -> bool:
    return val == _safe_none_label()

def _prophet_df(df_ts: pd.DataFrame) -> pd.DataFrame:
    """Build prophet dataframe robustly from df_ts indexed by date."""
    idx_name = df_ts.index.name if df_ts.index.name else "index"
    tmp = df_ts.reset_index()
    tmp = tmp.rename(columns={idx_name: "ds", "Valeurs": "y"})
    # If the reset index column isn't renamed (edge case):
    if "ds" not in tmp.columns:
        # fallback: first column is usually the index
        tmp = tmp.rename(columns={tmp.columns[0]: "ds", "Valeurs": "y"})
    return tmp[["ds", "y"]]

def _to_datetime_index(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Robust conversion to datetime index (Excel serial, strings, etc.)."""
    col = df[date_col]
    try:
        if pd.api.types.is_numeric_dtype(col):
            # Heuristique Excel: jours depuis 1899-12-30
            if col.dropna().shape[0] > 0 and float(col.dropna().median()) > 10000:
                df[date_col] = pd.to_datetime(col, unit="D", origin="1899-12-30", errors="coerce")
            else:
                df[date_col] = pd.to_datetime(col, errors="coerce", dayfirst=True)
        else:
            df[date_col] = pd.to_datetime(col, errors="coerce", dayfirst=True)
    except Exception:
        df[date_col] = pd.to_datetime(col, errors="coerce", dayfirst=True)

    df = df.dropna(subset=[date_col]).sort_values(by=date_col).set_index(date_col)
    return df


# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="📊 VentesPRO",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded",
)

# ============================================================
# Language selector (FIX: set_lang reçoit 'fr'/'en', pas le label)
# ============================================================
with st.sidebar:
    lang_choice = st.radio(
        t("lang_label"),
        [t("lang_fr"), t("lang_en")],
        index=0 if get_lang() == "fr" else 1,
        horizontal=True,
    )
    # Mapping label -> code
    lang_code = "fr" if lang_choice == t("lang_fr") else "en"
    set_lang(lang_code)

# -----------------------------
# Local translation helper (fallback)
# -----------------------------

def tr(fr: str, en: str) -> str:
    """Return fr/en text depending on current language.
    Use this for UI strings that are not yet in utils.i18n."""
    return fr if get_lang() == "fr" else en


TRANSLATIONS = {
    "### \u2728 Fonctionnalit\u00e9s Principales": "### \u2728 Key features",
    "### \u2753 Questions Fr\u00e9quentes": "### \u2753 Frequently asked questions",
    "### \ud83c\udf0d Analyse par R\u00e9gion": "### \ud83c\udf0d Regional analysis",
    "### \ud83c\udfaf Analyse Pr\u00e9dictive": "### \ud83c\udfaf Predictive analysis",
    "### \ud83c\udfc6 Performance par Cat\u00e9gorie": "### \ud83c\udfc6 Performance by category",
    "### \ud83d\udcbe Exporter les Donn\u00e9es": "### \ud83d\udcbe Export data",
    "### \ud83d\udcbe T\u00e9l\u00e9chargements": "### \ud83d\udcbe Downloads",
    "### \ud83d\udcbe T\u00e9l\u00e9charger le Rapport": "### \ud83d\udcbe Download the report",
    "### \ud83d\udcc5 Analyse Saisonni\u00e8re": "### \ud83d\udcc5 Seasonality analysis",
    "### \ud83d\udcc5 Analyse de Saisonnalit\u00e9": "### \ud83d\udcc5 Seasonality analysis",
    "### \ud83d\udcc9 Analyse des Tendances": "### \ud83d\udcc9 Trend analysis",
    "### \ud83d\udcca Analyse D\u00e9taill\u00e9e": "### \ud83d\udcca Detailed analysis",
    "### \ud83d\udcca Analyse par Variable": "### \ud83d\udcca Variable analysis",
    "### \ud83d\udcca Comparaison des mod\u00e8les": "### \ud83d\udcca Model comparison",
    "### \ud83d\udcca Corr\u00e9lation Stock-Valeurs": "### \ud83d\udcca Stock vs values correlation",
    "### \ud83d\udcca Param\u00e8tres d'Alerte": "### \ud83d\udcca Alert settings",
    "### \ud83d\udcca Rapport G\u00e9n\u00e9ral": "### \ud83d\udcca General report",
    "### \ud83d\udcca Statistiques des Donn\u00e9es Filtr\u00e9es": "### \ud83d\udcca Filtered data stats",
    "### \ud83d\udcca Statistiques des Pr\u00e9visions": "### \ud83d\udcca Forecast statistics",
    "### \ud83d\udccb Tableau de Donn\u00e9es": "### \ud83d\udccb Data table",
    "### \ud83d\udce6 Analyse des Cat\u00e9gories": "### \ud83d\udce6 Category analysis",
    "### \ud83d\udd0d Analyse Rapide": "### \ud83d\udd0d Quick analysis",
    "### \ud83d\udd17 Analyse des Corr\u00e9lations": "### \ud83d\udd17 Correlation analysis",
    "### \ud83d\udd25 Carte de Chaleur Saisonni\u00e8re": "### \ud83d\udd25 Seasonality heatmap",
    "### \ud83d\udd2e Pr\u00e9dictions Express": "### \ud83d\udd2e Quick predictions",
    "### \ud83d\uddfa\ufe0f Comparaison entre R\u00e9gions": "### \ud83d\uddfa\ufe0f Region comparison",
    "### \ud83d\ude80 Guide de D\u00e9marrage Rapide": "### \ud83d\ude80 Quick start guide",
    "### \ud83d\udea8 D\u00e9tection en Temps R\u00e9el": "### \ud83d\udea8 Real-time detection",
    "### \ud83e\udded Score de fiabilit\u00e9": "### \ud83e\udded Reliability score",
    "#### \ud83c\udfaf Cat\u00e9gories Strat\u00e9giques": "#### \ud83c\udfaf Strategic categories",
    "#### \ud83c\udfaf Visualisation des Corr\u00e9lations": "#### \ud83c\udfaf Correlation visualization",
    "#### \ud83c\udfc6 Top 5 Cat\u00e9gories": "#### \ud83c\udfc6 Top 5 categories",
    "#### \ud83d\udcc9 5 Cat\u00e9gories les Moins Performantes": "#### \ud83d\udcc9 Bottom 5 categories",
    "#### \ud83d\ude80 Opportunit\u00e9s de Croissance": "#### \ud83d\ude80 Growth opportunities",
    "**Mod\u00e8les conseill\u00e9s** : Auto (comparaison), Random Forest, XGBoost, ": "**Recommended models**: Auto (comparison), Random Forest, XGBoost, ",
    "Aucune donn\u00e9e sur la p\u00e9riode s\u00e9lectionn\u00e9e.": "No data for the selected period.",
    "Aucune donn\u00e9e \u00e0 d\u00e9crire (filtre trop strict).": "No data to describe (filters too strict).",
    "Aucune variable num\u00e9rique disponible pour l'analyse": "No numeric variable available for analysis",
    "Cat\u00e9gorie \u00e0 pr\u00e9voir": "Category to forecast",
    "Cat\u00e9gorie \u00e0 surveiller": "Category to monitor",
    "Choisissez une r\u00e9gion": "Choose a region",
    "Choisissez une variable \u00e0 analyser": "Choose a variable to analyze",
    "Fiabilit\u00e9 estim\u00e9e": "Estimated reliability",
    "G\u00e9n\u00e9rez des pr\u00e9visions pour votre colonne cible en utilisant des mod\u00e8les.\n": "Generate forecasts for your target column using forecasting models.\n",
    "Horizon de pr\u00e9vision (nombre de points)": "Forecast horizon (number of points)",
    "Lien mod\u00e9r\u00e9 entre stock et valeurs": "Moderate link between stock and values",
    "Lignes \u00e0 afficher": "Rows to display",
    "Mod\u00e8le de pr\u00e9vision": "Forecast model",
    "Pas assez de donn\u00e9es pour d\u00e9tecter des variations": "Not enough data to detect changes",
    "Pas assez de variables num\u00e9riques pour l'analyse de corr\u00e9lation": "Not enough numeric variables for correlation analysis",
    "Pas de variable num\u00e9rique (ou pas de donn\u00e9es) pour afficher une distribution.": "No numeric variable (or no data) to display a distribution.",
    "S\u00e9lectionnez une cat\u00e9gorie": "Select a category",
    "Utilisez la section Pr\u00e9visions pour des mod\u00e8les avanc\u00e9s": "Use the Forecasts section for advanced models",
    "\u26a0\ufe0f **Stock Bas** - Envisagez un r\u00e9approvisionnement": "\u26a0\ufe0f **Low stock** - Consider replenishment",
    "\u26a0\ufe0f Impact faible ou n\u00e9gatif : revois la strat\u00e9gie promo.": "\u26a0\ufe0f Low or negative impact: review the promotion strategy.",
    "\u26a0\ufe0f Lift non calculable (pas assez de donn\u00e9es 'Oui/Non' ou moyenne sans promo = 0).": "\u26a0\ufe0f Lift cannot be computed (not enough Yes/No data or no-promo mean = 0).",
    "\u2705 Alertes activ\u00e9es! Vous recevrez un email de confirmation.": "\u2705 Alerts enabled! You will receive a confirmation email.",
    "\u2705 Analyse termin\u00e9e!": "\u2705 Analysis complete!",
    "\u2705 Promotions tr\u00e8s efficaces : continue et optimise le ciblage.": "\u2705 Promotions are very effective: continue and optimize targeting.",
    "\u2705 Pr\u00e9visions g\u00e9n\u00e9r\u00e9es avec succ\u00e8s!": "\u2705 Forecasts generated successfully!",
    "\u2705 Votre message a \u00e9t\u00e9 envoy\u00e9 avec succ\u00e8s! Nous vous r\u00e9pondrons sous 24h.": "\u2705 Your message was sent! We'll reply within 24 hours.",
    "\u274c Erreur lors de l'enregistrement. Essayez \u00e0 nouveau.": "\u274c Error while saving. Please try again.",
    "\u274c Erreur lors de la g\u00e9n\u00e9ration des pr\u00e9visions": "\u274c Error while generating forecasts",
    "\u274c Format de t\u00e9l\u00e9phone invalide (ex: +212766052983 ou 0766052983)": "\u274c Invalid phone format (e.g., +212766052983 or 0766052983)",
    "\u274c Impossible de g\u00e9n\u00e9rer les pr\u00e9visions.": "\u274c Unable to generate forecasts.",
    "\u274c Prophet n'est pas install\u00e9. Installez: pip install prophet": "\u274c Prophet is not installed. Install: pip install prophet",
    "\u274c SARIMAX n'est pas install\u00e9. Installez: pip install statsmodels": "\u274c SARIMAX is not installed. Install: pip install statsmodels",
    "\u274c XGBoost n'est pas install\u00e9. Installez: pip install xgboost": "\u274c XGBoost is not installed. Install: pip install xgboost",
    "\u274c statsmodels n'est pas install\u00e9. Installez: pip install statsmodels": "\u274c statsmodels is not installed. Install: pip install statsmodels",
    "\ud83c\udf0d R\u00e9gions": "\ud83c\udf0d Regions",
    "\ud83d\udca1 Astuce: t\u00e9l\u00e9chargez le fichier exemple dans la sidebar": "\ud83d\udca1 Tip: download the sample file from the sidebar",
    "\ud83d\udca1 V\u00e9rifiez que votre fichier respecte le format requis": "\ud83d\udca1 Check that your file matches the expected format",
    "\ud83d\udcc5 P\u00e9riode": "\ud83d\udcc5 Period",
    "\ud83d\udcca Impact positif mod\u00e9r\u00e9 : teste d\u2019autres m\u00e9caniques promo.": "\ud83d\udcca Moderate positive impact: test other promo mechanics.",
    "\ud83d\udcca Moyenne Cible": "\ud83d\udcca Average target",
    "\ud83d\udccb Tableau d\u00e9taill\u00e9 des pr\u00e9visions": "\ud83d\udccb Detailed forecast table",
    "\ud83d\udccc Ajoute des donn\u00e9es 'Oui' et 'Non' dans la colonne Promo pour mesurer l\u2019impact.": "\ud83d\udccc Add 'Yes' and 'No' values in the Promo column to measure impact.",
    "\ud83d\udccc Pas de colonne 'Promo' dans les donn\u00e9es": "\ud83d\udccc No 'Promo' column in the data",
    "\ud83d\udccc Pas de colonne 'Region' dans les donn\u00e9es": "\ud83d\udccc No 'Region' column in the data",
    "\ud83d\udccc Pas de colonne 'Stock' dans les donn\u00e9es": "\ud83d\udccc No 'Stock' column in the data",
    "\ud83d\udccc S\u00e9lectionne une colonne cat\u00e9gorique pour activer l\u2019analyse par cat\u00e9gorie.": "\ud83d\udccc Select a categorical column to enable category analysis.",
    "\ud83d\udce6 Cat\u00e9gories": "\ud83d\udce6 Categories",
    "\ud83d\udcf1 Votre t\u00e9l\u00e9phone (optionnel)": "\ud83d\udcf1 Your phone (optional)",
    "\ud83d\udd0d Filtres Avanc\u00e9s": "\ud83d\udd0d Advanced filters",
    "\ud83d\udd17 Coefficient de Corr\u00e9lation": "\ud83d\udd17 Correlation coefficient",
    "\ud83d\udd2e G\u00e9n\u00e9rer les Pr\u00e9visions": "\ud83d\udd2e Generate forecasts",
    "\ud83d\ude80 G\u00e9n\u00e9rer les Insights": "\ud83d\ude80 Generate insights",
    "\ud83d\udea8 **Alerte Stock Critique!** Le stock est inf\u00e9rieur \u00e0 30% de la moyenne": "\ud83d\udea8 **Critical stock alert!** Stock is below 30% of average",
    "\ud83e\udd16 Cette section utilise des algorithmes simples pour g\u00e9n\u00e9rer des insights automatiques": "\ud83e\udd16 This section uses simple algorithms to generate automatic insights",
}


def L(fr_text: str) -> str:
    """Translate a fixed French UI string to English when needed."""
    if get_lang() == "en":
        return TRANSLATIONS.get(fr_text, fr_text)
    return fr_text


# Styles
apply_global_styles()

# Topbar
render_topbar("● Online")
st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

# ============================================================
# Sidebar
# ============================================================
st.sidebar.markdown(
    f"""
<div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem;'>
    <h2 style='color: #e2e8f0; font-size: 1.5rem; margin-bottom: 0.5rem;'>{t("config_title")}</h2>
</div>
""",
    unsafe_allow_html=True,
)

uploaded_file = st.sidebar.file_uploader(
    t("upload_label"),
    type=["csv", "xlsx", "xls", "txt", "tsv", "parquet"],
    help=t("upload_help"),
)

# Example file download (FIX: label traduit)
historical_data_file = "ventes_historique.csv"
if os.path.exists(historical_data_file):
    with open(historical_data_file, "rb") as f:
        st.sidebar.download_button(
            label=t("download_example") if "download_example" else "Download example",
            data=f,
            file_name="exemple_historique.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ============================================================
# Main app
# ============================================================
if uploaded_file:
    try:
        df = load_data(uploaded_file)

        if df is None:
            st.error("❌ Impossible de charger le fichier.")
            st.stop()

        if len(df) == 0:
            st.error(t("file_empty"))
            st.stop()

        # Sidebar infos
        source_name = uploaded_file.name
        st.sidebar.success(t("file_loaded", name=source_name))
        st.sidebar.info(
            "\n".join(
                [
                    t("file_details_title"),
                    t("file_details_rows", n=len(df)),
                    t("file_details_cols", n=len(df.columns)),
                    t("file_details_detected", cols=", ".join(df.columns.tolist())),
                ]
            )
        )

        # --------------------------------------------------------
        # Configuration des colonnes
        # --------------------------------------------------------
        with st.expander(t("config_columns"), expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                date_col = st.selectbox(
                    t("date_col"),
                    options=df.columns,
                    index=0 if len(df.columns) > 0 else None,
                    help=t("date_col_help"),
                )

            with col2:
                numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                target_col = st.selectbox(
                    t("target_col"),
                    options=numeric_cols,
                    index=0 if len(numeric_cols) > 0 else None,
                    help=t("target_col_help"),
                )

            with col3:
                none_label = _safe_none_label()
                cat_options = [none_label] + list(df.columns)
                default_cat_index = 0
                if "Produit" in df.columns and "Produit" in cat_options:
                    default_cat_index = cat_options.index("Produit")
                cat_col = st.selectbox(
                    t("cat_col"),
                    options=cat_options,
                    index=default_cat_index,
                    help=t("cat_col_help"),
                )

        if not date_col or not target_col:
            st.warning(t("need_cols"))
            st.stop()

        # --------------------------------------------------------
        # Date conversion (robuste)
        # --------------------------------------------------------
        try:
            df = _to_datetime_index(df, date_col)
        except Exception as e:
            st.error(t("date_convert_error", err=str(e)))
            st.stop()

        # Optional columns
        region_col = "Region" if "Region" in df.columns else None
        promo_col = "Promo" if "Promo" in df.columns else None
        stock_col = "Stock" if "Stock" in df.columns else None

        # Sidebar stats
        st.sidebar.markdown("---")
        st.sidebar.markdown(t("quick_stats"))
        st.sidebar.metric(t("total_target"), f"{df[target_col].sum():,.0f}")
        if not _is_none_choice(cat_col):
            st.sidebar.metric(t("unique_cats"), int(df[cat_col].nunique()))
        st.sidebar.metric(t("period_entries"), t("entries", n=len(df)))

        # --------------------------------------------------------
        # Tabs
        # --------------------------------------------------------
        st.markdown("---")
        tab_home, tab_dashboard, tab_analysis, tab_alerts, tab_forecast, tab_data, tab_reports, tab_insights, tab_support = st.tabs(
            [
                t("tab_home"),
                t("tab_dashboard"),
                t("tab_analysis"),
                t("tab_alerts"),
                t("tab_forecast"),
                t("tab_data"),
                t("tab_reports"),
                t("tab_insights"),
                t("tab_support"),
            ]
        )

        # ============================================================
        # HOME
        # ============================================================
        with tab_home:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.info(f"{t('home_welcome_title')}\n\n{t('home_welcome_text')}")

            st.markdown(t("overview"))

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                total_target = float(df[target_col].sum())
                st.markdown(
                    f"""
<div class='stCard' style='text-align: center;'>
    <h3 style='color: #f59e0b; margin-bottom: 0.5rem;'>💰</h3>
    <h2 style='color: #1e293b; margin: 0;'>{total_target:,.0f}</h2>
    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Total Cible</p>
</div>
""",
                    unsafe_allow_html=True,
                )

            with c2:
                if not _is_none_choice(cat_col):
                    nb_cats = int(df[cat_col].nunique())
                    st.markdown(
                        f"""
<div class='stCard' style='text-align: center;'>
    <h3 style='color: #8b5cf6; margin-bottom: 0.5rem;'>📦</h3>
    <h2 style='color: #1e293b; margin: 0;'>{nb_cats}</h2>
    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Catégories Uniques</p>
</div>
""",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
<div class='stCard' style='text-align: center;'>
    <h3 style='color: #8b5cf6; margin-bottom: 0.5rem;'>📦</h3>
    <h2 style='color: #1e293b; margin: 0;'>—</h2>
    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Catégories</p>
</div>
""",
                        unsafe_allow_html=True,
                    )

            with c3:
                croissance = float(df[target_col].pct_change().mean() * 100) if len(df) > 1 else 0.0
                st.markdown(
                    f"""
<div class='stCard' style='text-align: center;'>
    <h3 style='color: #10b981; margin-bottom: 0.5rem;'>📈</h3>
    <h2 style='color: #1e293b; margin: 0;'>{croissance:+.2f}%</h2>
    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Croissance Moy.</p>
</div>
""",
                    unsafe_allow_html=True,
                )

            with c4:
                avg_target = float(df[target_col].mean()) if len(df) else 0.0
                st.markdown(
                    f"""
<div class='stCard' style='text-align: center;'>
    <h3 style='color: #f59e0b; margin-bottom: 0.5rem;'>💵</h3>
    <h2 style='color: #1e293b; margin: 0;'>{avg_target:,.0f}</h2>
    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Moyenne Cible</p>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            st.markdown(L("### ✨ Fonctionnalités Principales"))
            colA, colB, colC = st.columns(3)

            with colA:
                st.markdown(
                    tr(
                        """
<div class='stCard'>
    <h3 style='color: #6366f1;'>📊 Analyse en Temps Réel</h3>
    <ul style='color: #64748b; line-height: 2;'>
        <li>Dashboard interactif</li>
        <li>Visualisations dynamiques</li>
        <li>KPIs automatisés</li>
        <li>Comparaisons multi-catégories</li>
        <li>Analyse saisonnière</li>
    </ul>
</div>
""",
                        """
<div class='stCard'>
    <h3 style='color: #6366f1;'>📊 Real-time analysis</h3>
    <ul style='color: #64748b; line-height: 2;'>
        <li>Interactive dashboard</li>
        <li>Dynamic visualizations</li>
        <li>Automated KPIs</li>
        <li>Multi-category comparisons</li>
        <li>Seasonality analysis</li>
    </ul>
</div>
""",
                    ),
                    unsafe_allow_html=True,
                )

            with colB:
                st.markdown(
                    tr(
                        """
<div class='stCard'>
    <h3 style='color: #8b5cf6;'>🔮 Prévisions IA</h3>
    <ul style='color: #64748b; line-height: 2;'>
        <li>5+ modèles de ML</li>
        <li>Mode Auto-Select</li>
        <li>Intervalles de confiance</li>
        <li>Prévisions jusqu'à 1 an</li>
        <li>Comparaison de modèles</li>
    </ul>
</div>
""",
                        """
<div class='stCard'>
    <h3 style='color: #8b5cf6;'>🔮 AI forecasting</h3>
    <ul style='color: #64748b; line-height: 2;'>
        <li>5+ ML models</li>
        <li>Auto-select mode</li>
        <li>Confidence intervals</li>
        <li>Forecast up to 1 year</li>
        <li>Model comparison</li>
    </ul>
</div>
""",
                    ),
                    unsafe_allow_html=True,
                )

            with colC:
                st.markdown(
                    tr(
                        """
<div class='stCard'>
    <h3 style='color: #ec4899;'>🚨 Alertes Intelligentes</h3>
    <ul style='color: #64748b; line-height: 2;'>
        <li>Seuils personnalisables</li>
        <li>Détection d'anomalies</li>
        <li>Alertes stock critique</li>
        <li>Notifications email</li>
        <li>Historique complet</li>
    </ul>
</div>
""",
                        """
<div class='stCard'>
    <h3 style='color: #ec4899;'>🚨 Smart alerts</h3>
    <ul style='color: #64748b; line-height: 2;'>
        <li>Custom thresholds</li>
        <li>Anomaly detection</li>
        <li>Critical stock alerts</li>
        <li>Email notifications</li>
        <li>Full history</li>
    </ul>
</div>
""",
                    ),
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown("### 📈 Tendance Globale")

            fig = go.Figure()
            daily_values = df.groupby(df.index)[target_col].sum()
            ma_7 = daily_values.rolling(7).mean()
            ma_30 = daily_values.rolling(30).mean()

            fig.add_trace(
                go.Scatter(
                    x=daily_values.index,
                    y=daily_values.values,
                    name="Valeurs Quotidiennes",
                    mode="lines",
                    line=dict(color="rgba(99, 102, 241, 0.3)", width=1),
                    fill="tozeroy",
                    fillcolor="rgba(99, 102, 241, 0.1)",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=ma_7.index, y=ma_7.values, name="Moyenne Mobile 7j", line=dict(color="#6366f1", width=3)
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=ma_30.index,
                    y=ma_30.values,
                    name="Moyenne Mobile 30j",
                    line=dict(color="#8b5cf6", width=3, dash="dash"),
                )
            )
            fig.update_layout(
                title="Évolution des valeurs avec moyennes mobiles",
                xaxis_title="Date",
                yaxis_title="Valeurs",
                hovermode="x unified",
                height=500,
                template="plotly_white",
                showlegend=True,
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown(L("### 🚀 Guide de Démarrage Rapide"))
            with st.expander(tr("📖 Comment utiliser VentesPRO","📖 How to use VentesPRO"), expanded=False):
                st.markdown(tr("""
#### 1️⃣ Préparer vos données
- Format: CSV ou Excel
- Au moins 1 colonne date + 1 colonne numérique cible
- Dates lisibles (JJ/MM/AAAA, AAAA-MM-JJ, ou Excel serial)

#### 2️⃣ Charger le fichier
- Via la sidebar
- Téléchargez le fichier exemple si besoin

#### 3️⃣ Configurer les colonnes
- Date
- Colonne numérique cible
- Colonne catégorique (optionnelle)

#### 4️⃣ Explorer
- Dashboard
- Analyse
- Alertes
- Prévisions
- Rapports / Exports
""","""
#### 1️⃣ Prepare your data
- Format: CSV or Excel
- At least 1 date column + 1 numeric target column
- Readable dates (DD/MM/YYYY, YYYY-MM-DD, or Excel serial)

#### 2️⃣ Upload the file
- From the sidebar
- Download the sample file if needed

#### 3️⃣ Configure columns
- Date
- Numeric target column
- Categorical column (optional)

#### 4️⃣ Explore
- Dashboard
- Analysis
- Alerts
- Forecasts
- Reports / Exports
"""))

        # ============================================================
        # DASHBOARD
        # ============================================================
        with tab_dashboard:
            st.markdown(tr("## 📊 Tableau de Bord Interactif","## 📊 Interactive dashboard"))

            with st.expander(tr("🔍 Filtres","🔍 Filters"), expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if not _is_none_choice(cat_col):
                        cats_selected = st.multiselect(
                            tr("Catégories","Categories"),
                            df[cat_col].dropna().unique(),
                            default=list(df[cat_col].dropna().unique()[:3]),
                        )
                    else:
                        cats_selected = None

                with col2:
                    date_debut = st.date_input(
                        tr("Date de début","Start date"),
                        value=df.index.min().date(),
                        min_value=df.index.min().date(),
                        max_value=df.index.max().date(),
                    )
                with col3:
                    date_fin = st.date_input(
                        tr("Date de fin","End date"),
                        value=df.index.max().date(),
                        min_value=df.index.min().date(),
                        max_value=df.index.max().date(),
                    )

            df_filtered = df[(df.index >= pd.to_datetime(date_debut)) & (df.index <= pd.to_datetime(date_fin))]
            if cats_selected and (not _is_none_choice(cat_col)):
                df_filtered = df_filtered[df_filtered[cat_col].isin(cats_selected)]

            if len(df_filtered) == 0:
                st.warning(tr("⚠️ Aucune donnée ne correspond aux filtres sélectionnés","⚠️ No data matches the selected filters"))
                st.stop()

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Évolution", "🌍 Géographie", "🏷️ Promotions", "📦 Stocks", "📅 Saisonnalité"])

            with tab1:
                st.markdown("### 📈 Évolution des Valeurs")
                fig = go.Figure()

                if (not _is_none_choice(cat_col)) and cats_selected:
                    for cat in cats_selected:
                        df_cat = df_filtered[df_filtered[cat_col] == cat]
                        fig.add_trace(
                            go.Scatter(x=df_cat.index, y=df_cat[target_col], mode="lines+markers", name=str(cat), line=dict(width=3), marker=dict(size=6))
                        )
                else:
                    fig.add_trace(
                        go.Scatter(x=df_filtered.index, y=df_filtered[target_col], mode="lines+markers", name="Valeurs", line=dict(width=3), marker=dict(size=6))
                    )

                fig.update_layout(
                    title="Comparaison des valeurs",
                    xaxis_title="Date",
                    yaxis_title="Valeurs",
                    hovermode="x unified",
                    height=500,
                    template="plotly_white",
                )
                st.plotly_chart(fig, use_container_width=True)

                if not _is_none_choice(cat_col):
                    st.markdown(L("### 🏆 Performance par Catégorie"))
                    perf_data = []
                    cats_for_perf = cats_selected or list(df_filtered[cat_col].dropna().unique())

                    for cat in cats_for_perf:
                        df_cat = df_filtered[df_filtered[cat_col] == cat]
                        perf_data.append(
                            {
                                "Catégorie": cat,
                                "Total": df_cat[target_col].sum(),
                                "Moyenne": df_cat[target_col].mean(),
                                "Max": df_cat[target_col].max(),
                                "Min": df_cat[target_col].min(),
                                "Croissance": df_cat[target_col].pct_change().mean() * 100 if len(df_cat) > 1 else 0.0,
                            }
                        )

                    perf_df = pd.DataFrame(perf_data).sort_values("Total", ascending=False)
                    st.dataframe(
                        perf_df.style.format({"Total": "{:,.0f}", "Moyenne": "{:,.0f}", "Max": "{:,.0f}", "Min": "{:,.0f}", "Croissance": "{:+.2f}%"}),
                        use_container_width=True,
                        hide_index=True,
                    )

            with tab2:
                if region_col:
                    st.markdown(L("### 🌍 Analyse par Région"))
                    regions = df_filtered[region_col].dropna().unique()
                    region_selected = st.selectbox(L("Choisissez une région"), regions)
                    df_region = df_filtered[df_filtered[region_col] == region_selected]

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("💰 Total Cible", f"{df_region[target_col].sum():,.0f}")
                    with c2:
                        st.metric(L("📊 Moyenne Cible"), f"{df_region[target_col].mean():,.0f}")
                    with c3:
                        part = (df_region[target_col].sum() / df_filtered[target_col].sum()) * 100 if df_filtered[target_col].sum() else 0
                        st.metric("📈 Part du Total", f"{part:.1f}%")

                    if not _is_none_choice(cat_col):
                        values_region = df_region.groupby(cat_col)[target_col].sum().sort_values(ascending=True)
                        fig = go.Figure(
                            go.Bar(
                                x=values_region.values,
                                y=values_region.index.astype(str),
                                orientation="h",
                                text=values_region.values,
                                texttemplate="%{text:,.0f}",
                                textposition="outside",
                            )
                        )
                        fig.update_layout(
                            title=f"Valeurs par Catégorie - {region_selected}",
                            xaxis_title="Valeurs",
                            yaxis_title="Catégorie",
                            height=400,
                            template="plotly_white",
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown(L("### 🗺️ Comparaison entre Régions"))
                    region_comparison = df_filtered.groupby(region_col)[target_col].agg(["sum", "mean", "count"])
                    region_comparison.columns = ["Total", "Moyenne", "Transactions"]
                    region_comparison = region_comparison.sort_values("Total", ascending=False)
                    st.dataframe(
                        region_comparison.style.format({"Total": "{:,.0f}", "Moyenne": "{:,.0f}", "Transactions": "{:,.0f}"}),
                        use_container_width=True,
                    )
                else:
                    st.info(L("📌 Pas de colonne 'Region' dans les données"))

            with tab3:
                if promo_col:
                    st.markdown("### 🏷️ Impact des Promotions")

                    col1, col2 = st.columns(2)

                    with col1:
                        promo_stats = df_filtered.groupby(promo_col)[target_col].agg(["sum", "mean", "count"])
                        oui_sum = promo_stats.loc["Oui", "sum"] if "Oui" in promo_stats.index else 0
                        oui_mean = promo_stats.loc["Oui", "mean"] if "Oui" in promo_stats.index else 0
                        oui_count = promo_stats.loc["Oui", "count"] if "Oui" in promo_stats.index else 0
                        non_sum = promo_stats.loc["Non", "sum"] if "Non" in promo_stats.index else 0
                        non_mean = promo_stats.loc["Non", "mean"] if "Non" in promo_stats.index else 0
                        non_count = promo_stats.loc["Non", "count"] if "Non" in promo_stats.index else 0

                        fig = go.Figure(
                            data=[
                                go.Bar(name="Avec Promo", x=["Total", "Moyenne", "Transactions"], y=[oui_sum, oui_mean, oui_count]),
                                go.Bar(name="Sans Promo", x=["Total", "Moyenne", "Transactions"], y=[non_sum, non_mean, non_count]),
                            ]
                        )
                        fig.update_layout(title="Comparaison Avec/Sans Promotion", barmode="group", height=400, template="plotly_white")
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        values_avec_promo = df_filtered[df_filtered[promo_col] == "Oui"][target_col].mean()
                        values_sans_promo = df_filtered[df_filtered[promo_col] == "Non"][target_col].mean()

                        lift = None
                        if pd.notna(values_sans_promo) and values_sans_promo > 0 and pd.notna(values_avec_promo):
                            lift = ((values_avec_promo - values_sans_promo) / values_sans_promo) * 100

                        if lift is not None:
                            st.markdown(
                                f"""
<div class='stCard' style='text-align: center; padding: 2rem;'>
    <h3 style='color: #6366f1;'>📊 Lift Promotionnel</h3>
    <h1 style='font-size: 3rem; margin: 1rem 0;'>{lift:+.1f}%</h1>
    <p style='color: #64748b;'>Différence moyenne avec/sans promotion</p>
</div>
""",
                                unsafe_allow_html=True,
                            )
                        else:
                            st.warning(L("⚠️ Lift non calculable (pas assez de données 'Oui/Non' ou moyenne sans promo = 0)."))

                        st.markdown("### 💡 Recommandations")
                        if lift is None:
                            st.info(L("📌 Ajoute des données 'Oui' et 'Non' dans la colonne Promo pour mesurer l’impact."))
                        elif lift > 20:
                            st.success(L("✅ Promotions très efficaces : continue et optimise le ciblage."))
                        elif lift > 0:
                            st.info(L("📊 Impact positif modéré : teste d’autres mécaniques promo."))
                        else:
                            st.warning(L("⚠️ Impact faible ou négatif : revois la stratégie promo."))

                    st.markdown("### 📈 Évolution Temporelle")
                    df_promo = df_filtered[df_filtered[promo_col] == "Oui"].resample("W")[target_col].mean()
                    df_no_promo = df_filtered[df_filtered[promo_col] == "Non"].resample("W")[target_col].mean()

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_promo.index, y=df_promo.values, name="Avec Promo", line=dict(width=3)))
                    fig.add_trace(go.Scatter(x=df_no_promo.index, y=df_no_promo.values, name="Sans Promo", line=dict(width=3)))
                    fig.update_layout(title="Comparaison hebdomadaire des valeurs", xaxis_title="Semaine", yaxis_title="Valeurs Moyennes", height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(L("📌 Pas de colonne 'Promo' dans les données"))

            with tab4:
                if stock_col:
                    st.markdown("### 📦 Gestion des Stocks")

                    if not _is_none_choice(cat_col):
                        cat_stock = st.selectbox(L("Sélectionnez une catégorie"), cats_selected or list(df_filtered[cat_col].dropna().unique()), key="stock_cat")
                        df_stock = df_filtered[df_filtered[cat_col] == cat_stock]
                    else:
                        df_stock = df_filtered

                    fig = make_subplots(rows=2, cols=1, subplot_titles=("Niveau de Stock", "Valeurs"), vertical_spacing=0.15)
                    fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock[stock_col], name="Stock", fill="tozeroy", line=dict(width=2)), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df_stock.index, y=df_stock[target_col], name="Valeurs", fill="tozeroy", line=dict(width=2)), row=2, col=1)
                    fig.update_layout(height=600, template="plotly_white", showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("### ⚠️ Alertes de Stock")
                    stock_moyen = float(df_stock[stock_col].mean()) if len(df_stock) else 0.0
                    stock_actuel = float(df_stock[stock_col].iloc[-1]) if len(df_stock) else 0.0

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("📦 Stock Actuel", f"{stock_actuel:.0f}")
                    with c2:
                        st.metric("📊 Stock Moyen", f"{stock_moyen:.0f}")
                    with c3:
                        ratio = ((stock_actuel / stock_moyen) - 1) * 100 if stock_moyen else 0.0
                        st.metric("📈 Variation", f"{ratio:+.1f}%")

                    if stock_moyen and stock_actuel < stock_moyen * 0.3:
                        st.error(L("🚨 **Alerte Stock Critique!** Le stock est inférieur à 30% de la moyenne"))
                    elif stock_moyen and stock_actuel < stock_moyen * 0.5:
                        st.warning(L("⚠️ **Stock Bas** - Envisagez un réapprovisionnement"))
                    else:
                        st.success("✅ Niveau de stock satisfaisant")

                    st.markdown(L("### 📊 Corrélation Stock-Valeurs"))
                    correlation = float(df_stock[stock_col].corr(df_stock[target_col])) if len(df_stock) > 1 else 0.0

                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.metric(L("🔗 Coefficient de Corrélation"), f"{correlation:.3f}")
                        if abs(correlation) > 0.7:
                            st.info("Fort lien entre stock et valeurs")
                        elif abs(correlation) > 0.4:
                            st.info(L("Lien modéré entre stock et valeurs"))
                        else:
                            st.info("Faible lien entre stock et valeurs")

                    with c2:
                        fig = px.scatter(df_stock, x=stock_col, y=target_col, trendline="ols", title="Relation Stock-Valeurs")
                        fig.update_layout(height=300, template="plotly_white")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(L("📌 Pas de colonne 'Stock' dans les données"))

            with tab5:
                st.markdown(L("### 📅 Analyse Saisonnière"))

                df_season = df_filtered.copy()
                df_season["MoisNum"] = df_season.index.month
                monthly_values = df_season.groupby("MoisNum")[target_col].mean().sort_index()

                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        x=monthly_values.index.astype(str),
                        y=monthly_values.values,
                        text=monthly_values.values,
                        texttemplate="%{text:,.0f}",
                        textposition="outside",
                    )
                )
                fig.update_layout(title="Valeurs Moyennes par Mois", xaxis_title="Mois", yaxis_title="Valeurs Moyennes", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 📆 Valeurs par Jour de la Semaine")
                df_season["JourNum"] = df_season.index.dayofweek  # 0=Lundi
                daily_values = df_season.groupby("JourNum")[target_col].mean().sort_index()
                day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

                fig = go.Figure(
                    go.Bar(
                        x=[day_labels[i] for i in daily_values.index],
                        y=daily_values.values,
                        text=daily_values.values,
                        texttemplate="%{text:,.0f}",
                        textposition="outside",
                    )
                )
                fig.update_layout(title="Performance par Jour de la Semaine", xaxis_title="Jour", yaxis_title="Valeurs Moyennes", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(L("### 🔥 Carte de Chaleur Saisonnière"))
                df_heat = df_season.copy()
                df_heat["Mois"] = df_heat.index.month
                df_heat["Jour"] = df_heat.index.day
                pivot = df_heat.pivot_table(values=target_col, index="Jour", columns="Mois", aggfunc="mean")

                fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, hoverongaps=False))
                fig.update_layout(title="Heatmap des Valeurs (Jour x Mois)", xaxis_title="Mois", yaxis_title="Jour du Mois", height=500, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### 💡 Insights Saisonniers")
                best_month = int(monthly_values.idxmax()) if len(monthly_values) else 1
                worst_month = int(monthly_values.idxmin()) if len(monthly_values) else 1
                best_day = int(daily_values.idxmax()) if len(daily_values) else 0
                worst_day = int(daily_values.idxmin()) if len(daily_values) else 0

                c1, c2 = st.columns(2)
                with c1:
                    st.success(f"🏆 **Meilleur Mois**: {best_month} ({monthly_values[best_month]:,.0f})")
                    st.success(f"🏆 **Meilleur Jour**: {day_labels[best_day]} ({daily_values[best_day]:,.0f})")
                with c2:
                    st.warning(f"📉 **Mois le Plus Faible**: {worst_month} ({monthly_values[worst_month]:,.0f})")
                    st.warning(f"📉 **Jour le Plus Faible**: {day_labels[worst_day]} ({daily_values[worst_day]:,.0f})")

        # ============================================================
        # ANALYSIS
        # ============================================================
        with tab_analysis:
            st.markdown(tr("## 📈 Analyse Avancée et Statistiques","## 📈 Advanced analysis & statistics"))
            t1, t2, t3, t4 = st.tabs(["📊 Variables", "🔗 Corrélations", "📉 Tendances", "🎯 Analyse Prédictive"])

            with t1:
                st.markdown(L("### 📊 Analyse par Variable"))
                numeric_cols_all = df.select_dtypes(include=["float64", "int64", "float32", "int32"]).columns.tolist()
                if len(numeric_cols_all) > 0:
                    variable = st.selectbox(L("Choisissez une variable à analyser"), numeric_cols_all)
                    c1, c2 = st.columns([1, 2])

                    with c1:
                        st.markdown("#### 📈 Statistiques Descriptives")
                        stats = df[variable].describe()
                        stats_df = pd.DataFrame(
                            {"Statistique": ["Nombre", "Moyenne", "Écart-type", "Min", "25%", "50%", "75%", "Max"], "Valeur": stats.values}
                        )
                        st.dataframe(stats_df.style.format({"Valeur": "{:,.2f}"}), use_container_width=True, hide_index=True)

                    with c2:
                        fig = go.Figure()
                        fig.add_trace(go.Histogram(x=df[variable], nbinsx=50, name="Distribution"))
                        fig.update_layout(title=f"Distribution de {variable}", xaxis_title=variable, yaxis_title="Fréquence", height=400, template="plotly_white")
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown(f"#### 📈 Évolution de {variable}")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df[variable], mode="lines", name=variable, line=dict(width=2)))
                    ma = df[variable].rolling(30).mean()
                    fig.add_trace(go.Scatter(x=df.index, y=ma, mode="lines", name="Moyenne Mobile 30j", line=dict(width=3, dash="dash")))
                    fig.update_layout(title=f"Évolution temporelle de {variable}", xaxis_title="Date", yaxis_title=variable, hovermode="x unified", height=500, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

                    if not _is_none_choice(cat_col):
                        st.markdown(f"#### 📦 Distribution de {variable} par Catégorie")
                        fig = go.Figure()
                        for cat in df[cat_col].dropna().unique():
                            fig.add_trace(go.Box(y=df[df[cat_col] == cat][variable], name=str(cat), boxmean="sd"))
                        fig.update_layout(title=f"Comparaison de {variable} entre Catégories", yaxis_title=variable, height=400, template="plotly_white")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(L("Aucune variable numérique disponible pour l'analyse"))

            with t2:
                st.markdown(L("### 🔗 Analyse des Corrélations"))
                numeric_df = df.select_dtypes(include=["float64", "int64", "float32", "int32"])
                if numeric_df.shape[1] > 1:
                    corr_matrix = numeric_df.corr()

                    fig = go.Figure(
                        data=go.Heatmap(
                            z=corr_matrix.values,
                            x=corr_matrix.columns,
                            y=corr_matrix.columns,
                            zmid=0,
                            text=corr_matrix.values,
                            texttemplate="%{text:.2f}",
                            colorbar=dict(title="Corrélation"),
                        )
                    )
                    fig.update_layout(title="Matrice de Corrélation", height=600, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown(L("#### 🎯 Visualisation des Corrélations"))
                    c1, c2 = st.columns(2)
                    with c1:
                        var1 = st.selectbox("Variable X", numeric_df.columns, key="corr_x")
                    with c2:
                        var2 = st.selectbox("Variable Y", [c for c in numeric_df.columns if c != var1], key="corr_y")

                    fig = px.scatter(df, x=var1, y=var2, trendline="ols", title=f"Relation entre {var1} et {var2}", color=cat_col if not _is_none_choice(cat_col) else None)
                    fig.update_layout(height=500, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

                    corr_value = float(df[var1].corr(df[var2])) if len(df) > 1 else 0.0
                    st.info(f"**Coefficient de corrélation**: {corr_value:.3f}")
                else:
                    st.warning(L("Pas assez de variables numériques pour l'analyse de corrélation"))

            with t3:
                st.markdown(L("### 📉 Analyse des Tendances"))
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df[target_col], mode="lines", name="Valeurs", line=dict(width=2)))
                ma_7 = df[target_col].rolling(7).mean()
                ma_30 = df[target_col].rolling(30).mean()
                fig.add_trace(go.Scatter(x=ma_7.index, y=ma_7.values, mode="lines", name="MA 7j", line=dict(width=3)))
                fig.add_trace(go.Scatter(x=ma_30.index, y=ma_30.values, mode="lines", name="MA 30j", line=dict(width=3, dash="dash")))
                fig.update_layout(title="Tendances avec Moyennes Mobiles", xaxis_title="Date", yaxis_title="Valeurs", height=500, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with t4:
                st.markdown(L("### 🎯 Analyse Prédictive"))
                st.info(L("Utilisez la section Prévisions pour des modèles avancés"))

                # FIX: ne pas modifier df global
                y_series = df[target_col].values.astype(float)
                X_time = np.arange(len(y_series)).reshape(-1, 1)
                lr = LinearRegression().fit(X_time, y_series)

                future_t = np.arange(len(y_series), len(y_series) + 30).reshape(-1, 1)
                pred = lr.predict(future_t)
                future_dates = pd.date_range(start=df.index.max() + timedelta(days=1), periods=30)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=y_series, mode="lines", name="Historique"))
                fig.add_trace(go.Scatter(x=future_dates, y=pred, mode="lines", name="Prédiction Linéaire", line=dict(dash="dash")))
                fig.update_layout(title="Prédiction Linéaire Simple (30 jours)", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

        # ============================================================
        # ALERTS
        # ============================================================
        with tab_alerts:
            st.markdown(tr("## ⚠️ Système d'Alertes Intelligentes","## ⚠️ Smart alerts system"))
            st.info(
                "Configurez des alertes pour surveiller les variations importantes de vos valeurs.\n"
                "Vous recevrez un email lorsque les seuils sont dépassés."
            )

            with st.form("alert_form"):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("👤 Votre nom*", placeholder="Ex: Mohamed HADI")
                    email = st.text_input("📧 Votre email*", placeholder="Ex: mohamed@exemple.com")
                with col2:
                    phone = st.text_input(L("📱 Votre téléphone (optionnel)"), placeholder="Ex: +212766052983")

                st.markdown(L("### 📊 Paramètres d'Alerte"))
                col1, col2, col3 = st.columns(3)

                with col1:
                    if not _is_none_choice(cat_col):
                        produit_alert = st.selectbox(L("Catégorie à surveiller"), df[cat_col].dropna().unique())
                    else:
                        produit_alert = None

                with col2:
                    seuil_hausse = st.number_input("📈 Seuil de hausse (%)", min_value=0.0, value=10.0, step=5.0)
                with col3:
                    seuil_baisse = st.number_input("📉 Seuil de baisse (%)", min_value=0.0, value=10.0, step=5.0)

                submitted = st.form_submit_button(tr("✅ Activer les Alertes","✅ Enable alerts"), type="primary", use_container_width=True)

                if submitted:
                    if nom and email:
                        if validate_email(email):
                            if phone and not validate_phone(phone):
                                st.error(L("❌ Format de téléphone invalide (ex: +212766052983 ou 0766052983)"))
                            else:
                                user_data = {
                                    "Nom": [nom],
                                    "Email": [email],
                                    "Téléphone": [phone if phone else "N/A"],
                                    "Catégorie": [produit_alert if produit_alert else "Globale"],
                                    "Seuil_Hausse": [seuil_hausse],
                                    "Seuil_Baisse": [seuil_baisse],
                                    "Date_Inscription": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                                }

                                if append_to_excel(user_data):
                                    st.success(L("✅ Alertes activées! Vous recevrez un email de confirmation."))
                                    send_email_safe(
                                        email,
                                        "Confirmation d'Activation des Alertes - VentesPRO",
                                        f"""Bonjour {nom},

Vos alertes ont été activées avec succès.

Détails:
- Catégorie surveillée: {produit_alert if produit_alert else 'Globale'}
- Seuil hausse: +{seuil_hausse}%
- Seuil baisse: -{seuil_baisse}%

Vous recevrez des notifications par email en cas de variation importante.

Cordialement,
L'équipe VentesPRO
""",
                                    )
                                else:
                                    st.error(L("❌ Erreur lors de l'enregistrement. Essayez à nouveau."))
                        else:
                            st.error("❌ Format d'email invalide")
                    else:
                        st.error("❌ Veuillez remplir les champs obligatoires")

            st.markdown("---")
            st.markdown(L("### 🚨 Détection en Temps Réel"))
            if st.button(tr("🔍 Vérifier les Alertes Maintenant","🔍 Check alerts now"), use_container_width=True):
                with st.spinner("Analyse en cours..."):
                    last_two = df[target_col].tail(2)
                    if len(last_two) == 2 and float(last_two.iloc[0]) != 0:
                        variation = (float(last_two.iloc[1]) - float(last_two.iloc[0])) / float(last_two.iloc[0]) * 100
                        if abs(variation) > 10:
                            st.warning(f"⚠️ Variation détectée: {variation:+.2f}%")
                        else:
                            st.success("✅ Aucune variation significative")
                    else:
                        st.info(L("Pas assez de données pour détecter des variations"))

            st.markdown(tr("### 📜 Historique des Alertes","### 📜 Alerts history"))
            alertes_exemple = pd.DataFrame(
                {
                    "Date": [datetime.now() - timedelta(days=i) for i in range(5)],
                    "Catégorie": ["Globale"] * 5,
                    "Variation": [5.2, -8.1, 12.3, -3.4, 7.5],
                    "Message": ["Hausse modérée", "Baisse significative", "Forte hausse", "Légère baisse", "Hausse positive"],
                }
            )
            st.dataframe(alertes_exemple, use_container_width=True)

        # ============================================================
        # FORECAST
        # ============================================================
        with tab_forecast:
            st.markdown(tr("## 🔮 Prévisions par Intelligence Artificielle","## 🔮 AI forecasting"))
            st.info(tr(
                "Générez des prévisions pour votre colonne cible en utilisant des modèles.\n"
                "✅ Compatible avec n’importe quelle colonne numérique\n"
                "✅ Date optionnelle (si pas de date, une timeline est générée automatiquement)",
                "Generate forecasts for your target column using models.\n"
                "✅ Works with any numeric column\n"
                "✅ Date optional (if missing, a timeline is generated automatically)"
            ))
            st.markdown(tr(
                "**Modèles conseillés** : Auto (comparaison), Random Forest, XGBoost, SARIMA / Holt-Winters (si saisonnalité) et Prophet pour les séries business.",
                "**Recommended models**: Auto (comparison), Random Forest, XGBoost, SARIMA / Holt-Winters (seasonality) and Prophet for business time series."
            ))

            col1, col2, col3 = st.columns(3)

            with col1:
                if not _is_none_choice(cat_col):
                    produit = st.selectbox(L("Catégorie à prévoir"), df[cat_col].dropna().unique())
                else:
                    produit = "Globale"

            with col2:
                model_type = st.selectbox(L("Modèle de prévision"),
                    [
                        "Auto (Comparaison)",
                        "Naïf (Dernière valeur)",
                        "Tendance linéaire",
                        "Moyenne Mobile Intelligente",
                        "Holt-Winters",
                        "Random Forest",
                        "XGBoost",
                        "ARIMA",
                        "SARIMA",
                        "Prophet",
                    ],
                )

            with col3:
                horizon = st.number_input(L("Horizon de prévision (nombre de points)"), min_value=1, max_value=365, value=30, step=1)

            show_confidence = st.checkbox("Afficher intervalles de confiance (95%)", value=True)

            if st.button(L("🔮 Générer les Prévisions"), type="primary", use_container_width=True):
                status_text = st.empty()
                progress_bar = st.progress(0)

                forecast_df = None
                confidence_lower = None
                confidence_upper = None
                model_name = model_type
                backtest_mae = None
                backtest_rmse = None

                try:
                    status_text.text("📦 Préparation des données...")
                    progress_bar.progress(10)

                    df_ts, has_date, err = prepare_series(df, target_col, cat_col, date_col, produit)
                    if err:
                        st.error(f"❌ {err}")
                        progress_bar.empty()
                        status_text.empty()
                        st.stop()

                    y = df_ts["Valeurs"].values.astype(float)
                    last_date = df_ts.index[-1]
                    future_dates = build_future_dates(last_date, horizon, freq="D")

                    # -------------------------
                    # Naïf
                    # -------------------------
                    if model_type == "Naïf (Dernière valeur)":
                        status_text.text("📌 Modèle naïf (dernière valeur)...")
                        progress_bar.progress(35)

                        last_val = float(y[-1])
                        forecasts = np.full(horizon, max(last_val, 0.0))

                        if show_confidence:
                            recent = y[-min(len(y), 30) :]
                            std_recent = float(np.std(recent)) if len(recent) > 1 else 0.0
                            confidence_lower, confidence_upper = basic_confidence_band(forecasts, std_recent)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})

                        split_idx = int(len(y) * 0.8)
                        if 0 < split_idx < len(y):
                            y_train, y_test = y[:split_idx], y[split_idx:]
                            pred_test = np.full(len(y_test), y_train[-1])
                            backtest_mae = mean_absolute_error(y_test, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_test, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # Tendance linéaire
                    # -------------------------
                    elif model_type == "Tendance linéaire":
                        status_text.text("📈 Tendance linéaire...")
                        progress_bar.progress(35)

                        X = np.arange(len(y)).reshape(-1, 1)
                        lr = LinearRegression().fit(X, y)

                        future_X = np.arange(len(y), len(y) + horizon).reshape(-1, 1)
                        forecasts = np.maximum(lr.predict(future_X), 0)

                        if show_confidence:
                            residuals = y - lr.predict(X)
                            std = float(np.std(residuals)) if len(residuals) > 1 else 0.0
                            confidence_lower, confidence_upper = basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})

                        split_idx = int(len(y) * 0.8)
                        if 0 < split_idx < len(y):
                            X_tr, y_tr = X[:split_idx], y[:split_idx]
                            X_te, y_te = X[split_idx:], y[split_idx:]
                            lr_bt = LinearRegression().fit(X_tr, y_tr)
                            pred_test = lr_bt.predict(X_te)
                            backtest_mae = mean_absolute_error(y_te, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_te, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # Moyenne mobile intelligente
                    # -------------------------
                    elif model_type == "Moyenne Mobile Intelligente":
                        status_text.text("📈 Moyenne Mobile Intelligente...")
                        progress_bar.progress(35)

                        s = df_ts["Valeurs"]
                        ma_7 = float(s.rolling(7, min_periods=1).mean().iloc[-1])
                        ma_14 = float(s.rolling(14, min_periods=1).mean().iloc[-1])
                        ma_30 = float(s.rolling(30, min_periods=1).mean().iloc[-1])

                        recent = s.tail(14).values.astype(float)
                        x = np.arange(len(recent)).reshape(-1, 1)
                        lr = LinearRegression().fit(x, recent)
                        slope = float(lr.coef_[0])

                        base = ma_7 * 0.5 + ma_14 * 0.3 + ma_30 * 0.2

                        forecasts = []
                        for i in range(horizon):
                            damping = 0.98 ** (i / 7)
                            forecasts.append(max(0.0, base + slope * (i + 1) * damping))
                        forecasts = np.array(forecasts, dtype=float)

                        if show_confidence:
                            std = float(s.tail(30).std()) if len(s) > 1 else 0.0
                            confidence_lower, confidence_upper = basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})

                        split_idx = int(len(y) * 0.8)
                        if 0 < split_idx < len(y):
                            y_train, y_test = y[:split_idx], y[split_idx:]
                            window = min(7, len(y_train))
                            baseline = float(np.mean(y_train[-window:])) if window else 0.0
                            pred_test = np.full(len(y_test), max(baseline, 0.0))
                            backtest_mae = mean_absolute_error(y_test, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_test, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # Holt-Winters
                    # -------------------------
                    elif model_type == "Holt-Winters":
                        status_text.text("❄️ Holt-Winters...")
                        progress_bar.progress(25)

                        try:
                            from statsmodels.tsa.holtwinters import ExponentialSmoothing
                        except Exception:
                            st.error(L("❌ statsmodels n'est pas installé. Installez: pip install statsmodels"))
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        progress_bar.progress(50)

                        seasonal_period = 7 if len(y) >= 14 else max(2, len(y) // 2)

                        try:
                            model = ExponentialSmoothing(
                                y, trend="add", seasonal="add", seasonal_periods=seasonal_period, initialization_method="estimated"
                            ).fit()
                        except Exception:
                            model = ExponentialSmoothing(y, trend="add", seasonal=None, initialization_method="estimated").fit()

                        forecasts = np.maximum(np.array(model.forecast(horizon), dtype=float), 0)

                        if show_confidence:
                            std = float(np.std(y - model.fittedvalues)) if len(y) > 2 else float(np.std(y))
                            confidence_lower, confidence_upper = basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})

                        split_idx = int(len(y) * 0.8)
                        if 0 < split_idx < len(y):
                            y_train, y_test = y[:split_idx], y[split_idx:]
                            seasonal_bt = 7 if len(y_train) >= 14 else max(2, len(y_train) // 2)
                            try:
                                hw_bt = ExponentialSmoothing(
                                    y_train, trend="add", seasonal="add", seasonal_periods=seasonal_bt, initialization_method="estimated"
                                ).fit()
                            except Exception:
                                hw_bt = ExponentialSmoothing(y_train, trend="add", seasonal=None, initialization_method="estimated").fit()
                            pred_test = hw_bt.forecast(len(y_test))
                            backtest_mae = mean_absolute_error(y_test, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_test, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # Random Forest
                    # -------------------------
                    elif model_type == "Random Forest":
                        status_text.text("🌳 Random Forest...")
                        progress_bar.progress(25)

                        df_feat, X, y_rf, feature_cols = build_features(df_ts)

                        split_idx = int(len(df_feat) * 0.8)
                        X_train, y_train = X.iloc[:split_idx], y_rf.iloc[:split_idx]
                        X_test, y_test = X.iloc[split_idx:], y_rf.iloc[split_idx:]

                        model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
                        model.fit(X_train, y_train)

                        progress_bar.progress(60)

                        future_dates2, future_X = build_future_features(df_feat, feature_cols, horizon)
                        forecasts = np.maximum(np.array(model.predict(future_X), dtype=float), 0)

                        if show_confidence:
                            pred_test = model.predict(X_test) if len(X_test) else np.array([])
                            std = float(np.std(y_test.values - pred_test)) if len(pred_test) > 1 else float(df_ts["Valeurs"].std())
                            confidence_lower, confidence_upper = basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates2, "Prévision": forecasts})
                        if len(X_test):
                            pred_test = model.predict(X_test)
                            backtest_mae = mean_absolute_error(y_test.values, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_test.values, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # XGBoost
                    # -------------------------
                    elif model_type == "XGBoost":
                        if not _XGBOOST_OK:
                            st.error(L("❌ XGBoost n'est pas installé. Installez: pip install xgboost"))
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        status_text.text("⚡ XGBoost...")
                        progress_bar.progress(25)

                        df_feat, X, y_xgb, feature_cols = build_features(df_ts)
                        split_idx = int(len(df_feat) * 0.8)
                        X_train, y_train = X.iloc[:split_idx], y_xgb.iloc[:split_idx]

                        model = XGBRegressor(
                            n_estimators=250,
                            max_depth=6,
                            learning_rate=0.05,
                            subsample=0.9,
                            colsample_bytree=0.9,
                            random_state=42,
                            n_jobs=-1,
                        )
                        model.fit(X_train, y_train, verbose=False)

                        progress_bar.progress(60)

                        future_dates2, future_X = build_future_features(df_feat, feature_cols, horizon)
                        forecasts = np.maximum(np.array(model.predict(future_X), dtype=float), 0)

                        if show_confidence:
                            std = float(df_ts["Valeurs"].tail(30).std()) if len(df_ts) > 1 else 0.0
                            confidence_lower, confidence_upper = basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates2, "Prévision": forecasts})

                        X_test = X.iloc[split_idx:]
                        y_test = y_xgb.iloc[split_idx:]
                        if len(X_test):
                            pred_test = model.predict(X_test)
                            backtest_mae = mean_absolute_error(y_test.values, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_test.values, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # ARIMA
                    # -------------------------
                    elif model_type == "ARIMA":
                        status_text.text("📊 ARIMA...")
                        progress_bar.progress(25)

                        try:
                            from statsmodels.tsa.arima.model import ARIMA
                        except Exception:
                            st.error(L("❌ statsmodels n'est pas installé. Installez: pip install statsmodels"))
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        progress_bar.progress(50)

                        model = ARIMA(y, order=(1, 1, 1)).fit()
                        forecasts = np.maximum(np.array(model.forecast(steps=horizon), dtype=float), 0)

                        if show_confidence:
                            try:
                                ci = model.get_forecast(steps=horizon).conf_int()
                                confidence_lower = np.maximum(ci.iloc[:, 0].values.astype(float), 0)
                                confidence_upper = ci.iloc[:, 1].values.astype(float)
                            except Exception:
                                std = float(np.std(y)) if len(y) > 1 else 0.0
                                confidence_lower, confidence_upper = basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})

                        split_idx = int(len(y) * 0.8)
                        if 0 < split_idx < len(y):
                            y_train, y_test = y[:split_idx], y[split_idx:]
                            bt_model = ARIMA(y_train, order=(1, 1, 1)).fit()
                            pred_test = bt_model.forecast(steps=len(y_test))
                            backtest_mae = mean_absolute_error(y_test, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_test, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # SARIMA
                    # -------------------------
                    elif model_type == "SARIMA":
                        status_text.text("🧭 SARIMA...")
                        progress_bar.progress(25)

                        if not _SARIMAX_OK:
                            st.error(L("❌ SARIMAX n'est pas installé. Installez: pip install statsmodels"))
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        from statsmodels.tsa.statespace.sarimax import SARIMAX

                        progress_bar.progress(50)
                        seasonal_order = (1, 1, 1, 7) if len(y) >= 14 else (0, 0, 0, 0)
                        model = SARIMAX(y, order=(1, 1, 1), seasonal_order=seasonal_order).fit(disp=False)

                        forecasts = np.maximum(np.array(model.forecast(steps=horizon), dtype=float), 0)

                        if show_confidence:
                            try:
                                ci = model.get_forecast(steps=horizon).conf_int()
                                confidence_lower = np.maximum(ci.iloc[:, 0].values.astype(float), 0)
                                confidence_upper = ci.iloc[:, 1].values.astype(float)
                            except Exception:
                                std = float(np.std(y)) if len(y) > 1 else 0.0
                                confidence_lower, confidence_upper = basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})

                        split_idx = int(len(y) * 0.8)
                        if 0 < split_idx < len(y):
                            y_train, y_test = y[:split_idx], y[split_idx:]
                            bt_model = SARIMAX(
                                y_train,
                                order=(1, 1, 1),
                                seasonal_order=seasonal_order if len(y_train) >= 14 else (0, 0, 0, 0),
                            ).fit(disp=False)
                            pred_test = bt_model.forecast(steps=len(y_test))
                            backtest_mae = mean_absolute_error(y_test, pred_test)
                            backtest_rmse = np.sqrt(mean_squared_error(y_test, pred_test))

                        progress_bar.progress(100)

                    # -------------------------
                    # Prophet
                    # -------------------------
                    elif model_type == "Prophet":
                        status_text.text("🧠 Prophet...")
                        progress_bar.progress(25)

                        if not _PROPHET_OK:
                            st.error(L("❌ Prophet n'est pas installé. Installez: pip install prophet"))
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        from prophet import Prophet

                        df_prophet = _prophet_df(df_ts)
                        model = Prophet(daily_seasonality=True)
                        model.fit(df_prophet)

                        future = model.make_future_dataframe(periods=horizon, freq="D", include_history=False)
                        forecast = model.predict(future)
                        forecasts = np.maximum(forecast["yhat"].values.astype(float), 0)

                        if show_confidence:
                            confidence_lower = np.maximum(forecast["yhat_lower"].values.astype(float), 0)
                            confidence_upper = forecast["yhat_upper"].values.astype(float)

                        forecast_df = pd.DataFrame({"Date": future["ds"], "Prévision": forecasts})

                        split_idx = int(len(df_prophet) * 0.8)
                        if 0 < split_idx < len(df_prophet):
                            train_df = df_prophet.iloc[:split_idx]
                            test_df = df_prophet.iloc[split_idx:]
                            bt_model = Prophet(daily_seasonality=True)
                            bt_model.fit(train_df)

                            future_bt = bt_model.make_future_dataframe(periods=len(test_df), freq="D", include_history=False)
                            pred_bt = bt_model.predict(future_bt)
                            pred_vals = pred_bt["yhat"].values.astype(float)

                            backtest_mae = mean_absolute_error(test_df["y"].values, pred_vals)
                            backtest_rmse = np.sqrt(mean_squared_error(test_df["y"].values, pred_vals))

                        progress_bar.progress(100)

                    # -------------------------
                    # Auto (Comparaison)
                    # -------------------------
                    elif model_type == "Auto (Comparaison)":
                        status_text.text("🤖 Auto: comparaison des modèles...")
                        progress_bar.progress(10)

                        split_idx = int(len(df_ts) * 0.8)
                        train = df_ts.iloc[:split_idx]
                        test = df_ts.iloc[split_idx:]

                        results = {}
                        forecasts_dict = {}

                        # Naïf
                        try:
                            status_text.text("Auto: test Naïf...")
                            progress_bar.progress(20)

                            last_val = float(train["Valeurs"].iloc[-1])
                            pred_test = np.full(len(test), last_val)
                            mae = mean_absolute_error(test["Valeurs"].values, pred_test) if len(test) else np.inf
                            rmse = np.sqrt(mean_squared_error(test["Valeurs"].values, pred_test)) if len(test) else np.inf
                            results["Naïf"] = {"MAE": mae, "RMSE": rmse}

                            fut_dates = build_future_dates(df_ts.index[-1], horizon, "D")
                            forecasts_dict["Naïf"] = pd.DataFrame({"Date": fut_dates, "Prévision": np.full(horizon, max(last_val, 0.0))})
                        except Exception:
                            results["Naïf"] = {"MAE": np.inf, "RMSE": np.inf}

                        # Tendance linéaire
                        try:
                            status_text.text("Auto: test Tendance linéaire...")
                            progress_bar.progress(35)

                            y_all = df_ts["Valeurs"].values.astype(float)
                            X_all = np.arange(len(y_all)).reshape(-1, 1)

                            X_tr, y_tr = X_all[:split_idx], y_all[:split_idx]
                            X_te, y_te = X_all[split_idx:], y_all[split_idx:]

                            lr = LinearRegression().fit(X_tr, y_tr)
                            pred_test = lr.predict(X_te)
                            mae = mean_absolute_error(y_te, pred_test) if len(y_te) else np.inf
                            rmse = np.sqrt(mean_squared_error(y_te, pred_test)) if len(y_te) else np.inf
                            results["Tendance linéaire"] = {"MAE": mae, "RMSE": rmse}

                            fut_dates = build_future_dates(df_ts.index[-1], horizon, "D")
                            fut_X = np.arange(len(y_all), len(y_all) + horizon).reshape(-1, 1)
                            forecasts = np.maximum(lr.predict(fut_X), 0.0)
                            forecasts_dict["Tendance linéaire"] = pd.DataFrame({"Date": fut_dates, "Prévision": forecasts})
                        except Exception:
                            results["Tendance linéaire"] = {"MAE": np.inf, "RMSE": np.inf}

                        # Random Forest
                        try:
                            status_text.text("Auto: test Random Forest...")
                            progress_bar.progress(55)

                            df_feat, X, y_m, feature_cols = build_features(df_ts)
                            X_train, y_train = X.iloc[:split_idx], y_m.iloc[:split_idx]
                            X_test, y_test = X.iloc[split_idx:], y_m.iloc[split_idx:]

                            rf = RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42, n_jobs=-1)
                            rf.fit(X_train, y_train)

                            pred_test = rf.predict(X_test) if len(X_test) else np.array([])
                            mae = mean_absolute_error(y_test.values, pred_test) if len(pred_test) else np.inf
                            rmse = np.sqrt(mean_squared_error(y_test.values, pred_test)) if len(pred_test) else np.inf
                            results["Random Forest"] = {"MAE": mae, "RMSE": rmse}

                            fut_dates2, future_X = build_future_features(df_feat, feature_cols, horizon)
                            forecasts = np.maximum(rf.predict(future_X), 0.0)
                            forecasts_dict["Random Forest"] = pd.DataFrame({"Date": fut_dates2, "Prévision": forecasts})
                        except Exception:
                            results["Random Forest"] = {"MAE": np.inf, "RMSE": np.inf}

                        # XGBoost (si dispo)
                        if _XGBOOST_OK:
                            try:
                                status_text.text("Auto: test XGBoost...")
                                progress_bar.progress(70)

                                df_feat, X, y_m, feature_cols = build_features(df_ts)
                                X_train, y_train = X.iloc[:split_idx], y_m.iloc[:split_idx]
                                X_test, y_test = X.iloc[split_idx:], y_m.iloc[split_idx:]

                                xgb = XGBRegressor(
                                    n_estimators=200, max_depth=6, learning_rate=0.05, subsample=0.9, random_state=42, n_jobs=-1
                                )
                                xgb.fit(X_train, y_train, verbose=False)

                                pred_test = xgb.predict(X_test) if len(X_test) else np.array([])
                                mae = mean_absolute_error(y_test.values, pred_test) if len(pred_test) else np.inf
                                rmse = np.sqrt(mean_squared_error(y_test.values, pred_test)) if len(pred_test) else np.inf
                                results["XGBoost"] = {"MAE": mae, "RMSE": rmse}

                                fut_dates2, future_X = build_future_features(df_feat, feature_cols, horizon)
                                forecasts = np.maximum(xgb.predict(future_X), 0.0)
                                forecasts_dict["XGBoost"] = pd.DataFrame({"Date": fut_dates2, "Prévision": forecasts})
                            except Exception:
                                results["XGBoost"] = {"MAE": np.inf, "RMSE": np.inf}

                        # SARIMA (si dispo)
                        if _SARIMAX_OK:
                            try:
                                status_text.text("Auto: test SARIMA...")
                                progress_bar.progress(80)
                                from statsmodels.tsa.statespace.sarimax import SARIMAX

                                y_train = train["Valeurs"].values.astype(float)
                                y_test = test["Valeurs"].values.astype(float)

                                seasonal_order = (1, 1, 1, 7) if len(y_train) >= 14 else (0, 0, 0, 0)
                                sarima = SARIMAX(y_train, order=(1, 1, 1), seasonal_order=seasonal_order).fit(disp=False)
                                pred_test = sarima.forecast(steps=len(y_test)) if len(y_test) else np.array([])
                                mae = mean_absolute_error(y_test, pred_test) if len(pred_test) else np.inf
                                rmse = np.sqrt(mean_squared_error(y_test, pred_test)) if len(pred_test) else np.inf
                                results["SARIMA"] = {"MAE": mae, "RMSE": rmse}

                                fut_dates = build_future_dates(df_ts.index[-1], horizon, "D")
                                forecasts = np.maximum(sarima.forecast(steps=horizon), 0.0)
                                forecasts_dict["SARIMA"] = pd.DataFrame({"Date": fut_dates, "Prévision": forecasts})
                            except Exception:
                                results["SARIMA"] = {"MAE": np.inf, "RMSE": np.inf}

                        # Prophet (si dispo)
                        if _PROPHET_OK:
                            try:
                                status_text.text("Auto: test Prophet...")
                                progress_bar.progress(85)

                                from prophet import Prophet

                                df_prophet = _prophet_df(df_ts)
                                train_df = df_prophet.iloc[:split_idx]
                                test_df = df_prophet.iloc[split_idx:]

                                prophet_model = Prophet(daily_seasonality=True)
                                prophet_model.fit(train_df)

                                future_bt = prophet_model.make_future_dataframe(periods=len(test_df), freq="D", include_history=False)
                                pred_bt = prophet_model.predict(future_bt)
                                pred_vals = pred_bt["yhat"].values.astype(float)

                                mae = mean_absolute_error(test_df["y"].values, pred_vals) if len(pred_vals) else np.inf
                                rmse = np.sqrt(mean_squared_error(test_df["y"].values, pred_vals)) if len(pred_vals) else np.inf
                                results["Prophet"] = {"MAE": mae, "RMSE": rmse}

                                future = prophet_model.make_future_dataframe(periods=horizon, freq="D", include_history=False)
                                forecast = prophet_model.predict(future)
                                forecasts = np.maximum(forecast["yhat"].values.astype(float), 0.0)
                                forecasts_dict["Prophet"] = pd.DataFrame({"Date": future["ds"], "Prévision": forecasts})
                            except Exception:
                                results["Prophet"] = {"MAE": np.inf, "RMSE": np.inf}

                        progress_bar.progress(90)

                        comparison_df = pd.DataFrame(results).T.sort_values("MAE")
                        best_model = comparison_df.index[0]

                        backtest_mae = results[best_model].get("MAE")
                        backtest_rmse = results[best_model].get("RMSE")

                        st.success(f"🏆 Meilleur modèle : **{best_model}**")
                        st.markdown(L("### 📊 Comparaison des modèles"))
                        st.dataframe(comparison_df.style.format({"MAE": "{:.2f}", "RMSE": "{:.2f}"}), use_container_width=True)

                        forecast_df = forecasts_dict[best_model]
                        model_name = best_model
                        progress_bar.progress(100)

                    # -------------------------
                    # AFFICHAGE
                    # -------------------------
                    progress_bar.empty()
                    status_text.empty()

                    if forecast_df is None:
                        st.error(L("❌ Impossible de générer les prévisions."))
                        st.stop()

                    st.markdown("---")
                    st.success(L("✅ Prévisions générées avec succès!"))

                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=df_ts.index,
                            y=df_ts["Valeurs"],
                            mode="lines",
                            name="📊 Historique",
                            hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Valeur: %{y:.2f}<extra></extra>",
                        )
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=forecast_df["Date"],
                            y=forecast_df["Prévision"],
                            mode="lines+markers",
                            name=f"🔮 Prévisions ({model_name})",
                            hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Prévision: %{y:.2f}<extra></extra>",
                        )
                    )

                    if show_confidence and confidence_lower is not None and confidence_upper is not None:
                        fig.add_trace(go.Scatter(x=forecast_df["Date"], y=confidence_upper, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
                        fig.add_trace(
                            go.Scatter(
                                x=forecast_df["Date"],
                                y=confidence_lower,
                                mode="lines",
                                line=dict(width=0),
                                fill="tonexty",
                                name="📏 Intervalle de confiance (95%)",
                                hoverinfo="skip",
                            )
                        )

                    fig.update_layout(
                        title=f"📈 Prévisions - {produit}<br><sub>Modèle: {model_name}</sub>",
                        xaxis_title="📅 Date",
                        yaxis_title=f"Valeurs ({target_col})",
                        hovermode="x unified",
                        height=550,
                        template="plotly_white",
                        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown(L("### 📊 Statistiques des Prévisions"))
                    c1, c2, c3, c4 = st.columns(4)

                    avg_forecast = float(forecast_df["Prévision"].mean())
                    max_forecast = float(forecast_df["Prévision"].max())
                    min_forecast = float(forecast_df["Prévision"].min())
                    total_forecast = float(forecast_df["Prévision"].sum())

                    hist_mean = float(df_ts["Valeurs"].mean()) if len(df_ts) else 0.0
                    delta_pct = ((avg_forecast / hist_mean - 1) * 100) if hist_mean else 0.0

                    c1.metric("Prévision moyenne", f"{avg_forecast:.2f}", delta=f"{delta_pct:.1f}%")
                    c2.metric("Prévision max", f"{max_forecast:.2f}")
                    c3.metric("Prévision min", f"{min_forecast:.2f}")
                    c4.metric("Total prévu", f"{total_forecast:.2f}")

                    history_mean = float(df_ts["Valeurs"].mean()) if len(df_ts) else 0.0
                    history_std = float(df_ts["Valeurs"].std()) if len(df_ts) else 0.0
                    volatility_pct = (history_std / history_mean * 100) if history_mean else 100.0
                    data_penalty = 12 if len(df_ts) < 60 else 0
                    model_penalty = 8 if model_name in {"Naïf", "Moyenne Mobile Intelligente"} else 0
                    mae_penalty = 0.0
                    if backtest_mae is not None and history_mean:
                        mae_ratio = min(2.0, backtest_mae / history_mean)
                        mae_penalty = mae_ratio * 40

                    reliability = 100 - min(70, volatility_pct) - data_penalty - model_penalty - mae_penalty
                    reliability = max(0, min(100, round(reliability, 1)))

                    st.markdown(L("### 🧭 Score de fiabilité"))
                    st.metric(L("Fiabilité estimée"), f"{reliability:.1f}%")
                    st.caption("Estimation basée sur un backtest rapide, la stabilité récente et la longueur de l'historique. Ce score n'est pas une garantie.")

                    st.markdown("### 💡 Insights")
                    first = float(forecast_df["Prévision"].iloc[0])
                    last = float(forecast_df["Prévision"].iloc[-1])
                    trend = ((last - first) / first * 100) if first else 0.0
                    volatility = (forecast_df["Prévision"].std() / forecast_df["Prévision"].mean() * 100) if float(forecast_df["Prévision"].mean()) else 0.0

                    a, b = st.columns(2)
                    with a:
                        if trend > 5:
                            st.success(f"📈 Tendance haussière : +{trend:.1f}%")
                        elif trend < -5:
                            st.warning(f"📉 Tendance baissière : {trend:.1f}%")
                        else:
                            st.info(f"➡️ Tendance stable : {trend:.1f}%")
                    with b:
                        if volatility > 20:
                            st.warning(f"⚠️ Forte volatilité : {volatility:.1f}%")
                        else:
                            st.success(f"✅ Faible volatilité : {volatility:.1f}%")

                    with st.expander(L("📋 Tableau détaillé des prévisions")):
                        display_df = forecast_df.copy()
                        display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.strftime("%d/%m/%Y")
                        display_df["Prévision"] = display_df["Prévision"].astype(float).round(2)
                        st.dataframe(display_df, use_container_width=True, hide_index=True)

                    st.markdown('<div id="telechargements"></div>', unsafe_allow_html=True)
                    st.markdown(L("### 💾 Téléchargements"))
                    colA, colB = st.columns(2)

                    with colA:
                        csv = forecast_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="📥 Télécharger CSV",
                            data=csv,
                            file_name=f"previsions_{produit}_{str(model_name).replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            use_container_width=True,
                        )

                    with colB:
                        report = f"""
RAPPORT DE PRÉVISIONS - VentesPRO
{'='*60}

Catégorie: {produit}
Modèle: {model_name}
Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Horizon: {horizon}

STATISTIQUES:
- Prévision moyenne: {avg_forecast:.2f}
- Prévision max: {max_forecast:.2f}
- Prévision min: {min_forecast:.2f}
- Total prévu: {total_forecast:.2f}
- Tendance: {trend:+.2f}%
- Volatilité: {volatility:.2f}%

DONNÉES HISTORIQUES:
- Moyenne historique: {hist_mean:.2f}
- Points: {len(df_ts)}
{'='*60}

PRÉVISIONS:
"""
                        for _, row in forecast_df.iterrows():
                            report += f"{pd.to_datetime(row['Date']).strftime('%d/%m/%Y')}: {float(row['Prévision']):.2f}\n"

                        st.download_button(
                            label="📄 Télécharger Rapport",
                            data=report,
                            file_name=f"rapport_{produit}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                        )

                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(L("❌ Erreur lors de la génération des prévisions"))
                    st.error(str(e))
                    with st.expander("🔍 Traceback"):
                        st.code(traceback.format_exc())

        # ============================================================
        # DATA
        # ============================================================
        with tab_data:
            st.markdown(tr("## 📂 Exploration des Données Brutes","## 📂 Raw data explorer"))

            with st.expander(L("🔍 Filtres Avancés"), expanded=True):
                col1, col2, col3 = st.columns(3)

                with col1:
                    if not _is_none_choice(cat_col):
                        cats_filter = st.multiselect(L("📦 Catégories"), df[cat_col].dropna().unique(), default=list(df[cat_col].dropna().unique()[:5]))
                    else:
                        cats_filter = None

                with col2:
                    if region_col:
                        regions_filter = st.multiselect(L("🌍 Régions"), df[region_col].dropna().unique(), default=list(df[region_col].dropna().unique()[:3]))
                    else:
                        regions_filter = None

                with col3:
                    date_range = st.date_input(L("📅 Période"),
                        [df.index.min().date(), df.index.max().date()],
                        min_value=df.index.min().date(),
                        max_value=df.index.max().date(),
                    )

            df_filtered2 = df.copy()

            if cats_filter and (not _is_none_choice(cat_col)):
                df_filtered2 = df_filtered2[df_filtered2[cat_col].isin(cats_filter)]
            if regions_filter and region_col:
                df_filtered2 = df_filtered2[df_filtered2[region_col].isin(regions_filter)]
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                df_filtered2 = df_filtered2.loc[pd.to_datetime(date_range[0]) : pd.to_datetime(date_range[1])]

            st.markdown(L("### 📊 Statistiques des Données Filtrées"))
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("📦 Lignes", len(df_filtered2))
            with c2:
                days = (df_filtered2.index.max() - df_filtered2.index.min()).days if len(df_filtered2) else 0
                st.metric(L("📅 Période"), f"{days} jours")
            with c3:
                st.metric("💰 Total Cible", f"{df_filtered2[target_col].sum():,.0f}")
            with c4:
                st.metric(L("📊 Moyenne Cible"), f"{df_filtered2[target_col].mean():,.0f}")

            st.markdown(L("### 📋 Tableau de Données"))
            c1, c2, c3 = st.columns(3)
            with c1:
                show_index = st.checkbox("Afficher l'index", value=True)
            with c2:
                n_rows = st.number_input(L("Lignes à afficher"), 10, max(10, len(df_filtered2)), 50)
            with c3:
                sort_col = st.selectbox("Trier par", df_filtered2.columns)

            df_display = df_filtered2.sort_values(sort_col, ascending=False).head(int(n_rows))
            st.dataframe(df_display, use_container_width=True, hide_index=not show_index)

            st.markdown('<div id="telechargements"></div>', unsafe_allow_html=True)
            st.markdown(L("### 💾 Exporter les Données"))

            col1, col2, col3 = st.columns(3)

            with col1:
                csv = df_filtered2.reset_index().to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Télécharger CSV",
                    data=csv,
                    file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with col2:
                try:
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df_filtered2.reset_index().to_excel(writer, sheet_name="Données", index=False)
                    st.download_button(
                        label="📊 Télécharger Excel",
                        data=buffer.getvalue(),
                        file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                except Exception:
                    st.info("Export Excel non disponible")

            with col3:
                json_str = df_filtered2.reset_index().to_json(orient="records", date_format="iso")
                st.download_button(
                    label="📄 Télécharger JSON",
                    data=json_str,
                    file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                )

            st.markdown("---")
            st.markdown(L("### 🔍 Analyse Rapide"))
            tA, tB = st.tabs(["📊 Statistiques Descriptives", "📈 Distribution"])

            with tA:
                if len(df_filtered2):
                    st.dataframe(df_filtered2.describe(), use_container_width=True)
                else:
                    st.info(L("Aucune donnée à décrire (filtre trop strict)."))

            with tB:
                numeric_cols = df_filtered2.select_dtypes(include=["float64", "int64", "float32", "int32"]).columns
                if len(numeric_cols) > 0 and len(df_filtered2):
                    col_to_plot = st.selectbox("Variable", numeric_cols)
                    fig = px.histogram(df_filtered2, x=col_to_plot, title=f"Distribution de {col_to_plot}", marginal="box")
                    fig.update_layout(height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(L("Pas de variable numérique (ou pas de données) pour afficher une distribution."))

        # ============================================================
        # REPORTS
        # ============================================================
        with tab_reports:
            st.markdown(tr("## 📑 Rapports Automatisés","## 📑 Automated reports"))
            st.markdown(L("### 📊 Rapport Général"))

            col1, col2 = st.columns(2)
            with col1:
                date_debut_rapport = st.date_input(tr("Date de début","Start date"), value=df.index.min().date(), key="rapport_debut")
            with col2:
                date_fin_rapport = st.date_input(tr("Date de fin","End date"), value=df.index.max().date(), key="rapport_fin")

            df_rapport = df[(df.index >= pd.to_datetime(date_debut_rapport)) & (df.index <= pd.to_datetime(date_fin_rapport))]
            croissance = float(df_rapport[target_col].pct_change().mean() * 100) if len(df_rapport) > 1 else 0.0

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric(L("📅 Période"), f"{len(df_rapport)} entrées")
            with c2:
                st.metric("💰 Total Cible", f"{df_rapport[target_col].sum():,.0f}")
            with c3:
                st.metric(L("📊 Moyenne Cible"), f"{df_rapport[target_col].mean():,.0f}")
            with c4:
                st.metric("📈 Croissance Moy.", f"{croissance:+.2f}%")

            st.markdown("---")
            st.markdown(L("### 📊 Analyse Détaillée"))

            if (not _is_none_choice(cat_col)) and len(df_rapport):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(L("#### 🏆 Top 5 Catégories"))
                    top_cats = df_rapport.groupby(cat_col)[target_col].sum().sort_values(ascending=False).head(5)
                    fig = go.Figure(go.Bar(x=top_cats.values, y=top_cats.index.astype(str), orientation="h", text=top_cats.values, texttemplate="%{text:,.0f}", textposition="outside"))
                    fig.update_layout(title="Top 5 Catégories", xaxis_title="Valeurs", height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown(L("#### 📉 5 Catégories les Moins Performantes"))
                    bottom_cats = df_rapport.groupby(cat_col)[target_col].sum().sort_values().head(5)
                    fig = go.Figure(go.Bar(x=bottom_cats.values, y=bottom_cats.index.astype(str), orientation="h", text=bottom_cats.values, texttemplate="%{text:,.0f}", textposition="outside"))
                    fig.update_layout(title="5 Catégories à Améliorer", xaxis_title="Valeurs", height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### 📈 Évolution des Valeurs")
            if len(df_rapport):
                daily_values = df_rapport.groupby(df_rapport.index)[target_col].sum()
                ma_7 = daily_values.rolling(7).mean()

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=daily_values.index, y=daily_values.values, name="Valeurs Quotidiennes", line=dict(width=1), fill="tozeroy"))
                fig.add_trace(go.Scatter(x=ma_7.index, y=ma_7.values, name="Moyenne Mobile 7j", line=dict(width=3)))
                fig.update_layout(title="Évolution Quotidienne des Valeurs", xaxis_title="Date", yaxis_title="Valeurs", height=400, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(L("Aucune donnée sur la période sélectionnée."))

            st.markdown("---")
            st.markdown("### 💡 Insights et Recommandations")

            if (not _is_none_choice(cat_col)) and len(df_rapport):
                _cat_sum = df_rapport.groupby(cat_col)[target_col].sum().sort_values(ascending=False)
                top_produits = _cat_sum.head(5)
                bottom_produits = _cat_sum.tail(5)
                best_product = str(top_produits.index[0]) if len(top_produits) else "N/A"
                worst_product = str(bottom_produits.index[0]) if len(bottom_produits) else "N/A"
            else:
                top_produits = pd.Series(dtype=float)
                bottom_produits = pd.Series(dtype=float)
                best_product = "N/A"
                worst_product = "N/A"

            best_month = int(df_rapport.groupby(df_rapport.index.month)[target_col].sum().idxmax()) if len(df_rapport) else 1

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"""
<div class='stCard'>
    <h4 style='color: #10b981;'>✅ Points Forts</h4>
    <ul style='color: #64748b; line-height: 2;'>
        <li>🏆 Catégorie star: <strong>{best_product}</strong></li>
        <li>📈 Croissance moyenne: <strong>{croissance:+.2f}%</strong></li>
        <li>📅 Meilleur mois: <strong>Mois {best_month}</strong></li>
        <li>💰 Total: <strong>{df_rapport[target_col].sum():,.0f}</strong></li>
    </ul>
</div>
""",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""
<div class='stCard'>
    <h4 style='color: #f59e0b;'>⚠️ Points d'Amélioration</h4>
    <ul style='color: #64748b; line-height: 2;'>
        <li>📉 Focus sur: <strong>{worst_product}</strong></li>
        <li>🎯 Réduire la volatilité</li>
        <li>📊 Optimiser les stocks</li>
        <li>🚀 Renforcer les promotions</li>
    </ul>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown('<div id="telechargements"></div>', unsafe_allow_html=True)
            st.markdown(L("### 💾 Télécharger le Rapport"))

            rapport_complet = f"""
╔══════════════════════════════════════════════════════════╗
║     RAPPORT GÉNÉRAL - VentesPRO                          ║
╚══════════════════════════════════════════════════════════╝

Date du rapport: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Période analysée: {date_debut_rapport} au {date_fin_rapport}

{'='*60}
1. RÉSUMÉ EXÉCUTIF
{'='*60}

Durée de la période: {len(df_rapport)} entrées
Total cible: {df_rapport[target_col].sum():,.2f}
Moyenne cible: {df_rapport[target_col].mean():,.2f}
Médiane cible: {df_rapport[target_col].median():,.2f}
Écart-type: {df_rapport[target_col].std():,.2f}
Croissance moyenne: {croissance:+.2f}%

{'='*60}
2. PERFORMANCE PAR PRODUIT
{'='*60}

🏆 TOP 5 PRODUITS:
"""
            for i, (prod, vente) in enumerate(top_produits.items(), 1):
                rapport_complet += f"   {i}. {prod}: {vente:,.2f}\n"

            rapport_complet += "\n📉 5 PRODUITS À AMÉLIORER:\n"
            for i, (prod, vente) in enumerate(bottom_produits.items(), 1):
                rapport_complet += f"   {i}. {prod}: {vente:,.2f}\n"

            rapport_complet += f"""

{'='*60}
3. INSIGHTS ET RECOMMANDATIONS
{'='*60}

POINTS FORTS:
✅ Produit star: {best_product}
✅ Croissance moyenne: {croissance:+.2f}%
✅ Meilleur mois: Mois {best_month}

AXES D'AMÉLIORATION:
⚠️ Focus sur: {worst_product}
⚠️ Optimisation des stocks recommandée
⚠️ Promotions ciblées à renforcer

{'='*60}
Fin du Rapport
{'='*60}
"""

            st.download_button(
                label="📄 Télécharger le Rapport Complet",
                data=rapport_complet,
                file_name=f"rapport_ventes_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary",
            )

        # ============================================================
        # INSIGHTS
        # ============================================================
        with tab_insights:
            st.markdown(tr("## 💡 Insights Générés par Intelligence Artificielle","## 💡 AI-generated insights"))
            st.info(L("🤖 Cette section utilise des algorithmes simples pour générer des insights automatiques"))

            if st.button(L("🚀 Générer les Insights"), type="primary", use_container_width=True):
                import time

                with st.spinner("🔎 Analyse en cours..."):
                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress.progress(i + 1)
                    progress.empty()

                st.success(L("✅ Analyse terminée!"))

                st.markdown("---")
                st.markdown("### 🎯 Insights Principaux")

                croissance_global = float(df[target_col].pct_change().mean() * 100) if len(df) > 1 else 0.0
                if croissance_global > 5:
                    st.success(f"📈 Tendance Positive Forte : croissance moyenne ~ **{croissance_global:.2f}%**")
                elif croissance_global > 0:
                    st.info(f"📊 Croissance Modérée : croissance moyenne ~ **{croissance_global:.2f}%**")
                else:
                    st.warning(f"⚠️ Attention : décroissance moyenne ~ **{croissance_global:.2f}%**")

                st.markdown("---")
                st.markdown(L("### 📅 Analyse de Saisonnalité"))

                monthly_avg = df.groupby(df.index.month)[target_col].mean()
                best_month = int(monthly_avg.idxmax()) if len(monthly_avg) else 1
                worst_month = int(monthly_avg.idxmin()) if len(monthly_avg) else 1

                st.info(
                    f"📊 **Patterns Saisonniers:**\n"
                    f"- 🏆 Meilleur mois: **{best_month}** ({monthly_avg[best_month]:,.0f})\n"
                    f"- 📉 Mois le plus faible: **{worst_month}** ({monthly_avg[worst_month]:,.0f})"
                )

                st.markdown("---")
                st.markdown(L("### 📦 Analyse des Catégories"))

                if (not _is_none_choice(cat_col)) and (cat_col in df.columns):
                    prod_perf = df.groupby(cat_col)[target_col].agg(["sum", "mean", "std"]).round(2)
                    prod_perf.columns = ["Total", "Moyenne", "Volatilité"]
                    prod_perf["CV"] = np.where(prod_perf["Moyenne"] != 0, (prod_perf["Volatilité"] / prod_perf["Moyenne"] * 100).round(2), np.nan)
                    prod_perf = prod_perf.sort_values("Total", ascending=False)

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(L("#### 🎯 Catégories Stratégiques"))
                        top_3 = prod_perf.head(3)
                        for i, (prod, row) in enumerate(top_3.iterrows(), 1):
                            total_sum = float(df[target_col].sum()) if df[target_col].sum() else 0.0
                            part_marche = (row["Total"] / total_sum) * 100 if total_sum else 0.0
                            stability = "Excellent" if (row["CV"] < 20) else ("Bon" if (row["CV"] < 40) else "Volatile")
                            st.success(f"**{i}. {prod}**\n- Part du total: {part_marche:.1f}%\n- Stabilité: {stability}")

                    with col2:
                        st.markdown(L("#### 🚀 Opportunités de Croissance"))
                        bottom_3 = prod_perf.tail(3)
                        avg_mean = float(prod_perf["Moyenne"].mean()) if len(prod_perf) else 0.0
                        for prod, row in bottom_3.iterrows():
                            if row["Moyenne"]:
                                potentiel = ((avg_mean - row["Moyenne"]) / row["Moyenne"]) * 100
                            else:
                                potentiel = 0.0
                            action = "Promouvoir" if potentiel > 50 else ("Optimiser" if potentiel > 20 else "Surveiller")
                            st.warning(f"**{prod}**\n- Potentiel: {potentiel:+.1f}%\n- Action: {action}")
                else:
                    st.info(L("📌 Sélectionne une colonne catégorique pour activer l’analyse par catégorie."))

                st.markdown("---")
                st.markdown(L("### 🔮 Prédictions Express"))

                last_30_days = float(df[target_col].tail(30).mean()) if len(df) else 0.0
                trend_30 = float(df[target_col].tail(30).pct_change().mean()) if len(df) > 1 else 0.0
                prediction_next_month = last_30_days * (1 + trend_30) * 30

                st.info(
                    f"📊 Prévision simple (mois prochain): **{prediction_next_month:,.0f}**\n\n"
                    f"Basé sur la tendance des 30 derniers jours ({trend_30*100:+.2f}% / jour)."
                )

        # ============================================================
        # SUPPORT
        # ============================================================
        with tab_support:
            st.markdown(tr("## 🛠️ Support Technique","## 🛠️ Technical support"))

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    f"""
<div class='stCard'>
    <h3 style='color: #6366f1;'>📧 Email</h3>
    <p style='font-size: 1.2rem; color: #1e293b;'>{SUPPORT_EMAIL}</p>
    <p style='color: #64748b;'>Reply within 24 business hours</p>
</div>
""",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"""
<div class='stCard'>
    <h3 style='color: #6366f1;'>📱 Téléphone</h3>
    <p style='font-size: 1.2rem; color: #1e293b;'>{SUPPORT_PHONE}</p>
    <p style='color: #64748b;'>Mon-Fri: 9am-6pm (GMT+1)</p>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown("### ✉️ Envoyez-nous un Message")

            with st.form("contact_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nom_support = st.text_input("👤 Votre nom*", placeholder="Ex: Mohamed HADI")
                with col2:
                    email_support = st.text_input("📧 Votre email*", placeholder="Ex: mohamed@exemple.com")

                sujet = st.selectbox("📋 Sujet", ["Question générale", "Problème technique", "Demande de fonctionnalité", "Aide à l'utilisation", "Autre"])
                message_support = st.text_area("💬 Votre message*", placeholder="Décrivez votre demande en détail...", height=150)

                submitted = st.form_submit_button(tr("📤 Envoyer le Message","📤 Send message"), type="primary", use_container_width=True)
                if submitted:
                    if nom_support and email_support and message_support:
                        if validate_email(email_support):
                            message_data = {
                                "Nom": [nom_support],
                                "Email": [email_support],
                                "Sujet": [sujet],
                                "Message": [message_support],
                                "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                            }
                            append_to_excel(message_data, "messages_support.xlsx")

                            success, msg = send_email_safe(
                                SUPPORT_EMAIL,
                                f"[Support VentesPro] {sujet} - {nom_support}",
                                f"""Nouveau message de support

De: {nom_support}
Email: {email_support}
Sujet: {sujet}

Message:
{message_support}

---
Envoyé le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}
""",
                            )

                            if success:
                                st.success(L("✅ Votre message a été envoyé avec succès! Nous vous répondrons sous 24h."))
                                st.balloons()
                            else:
                                st.warning(f"Message enregistré mais {msg}")
                        else:
                            st.error("❌ Format d'email invalide")
                    else:
                        st.error("❌ Veuillez remplir tous les champs obligatoires")

            st.markdown("---")
            st.markdown(L("### ❓ Questions Fréquentes"))

            faqs_fr = [
                {
                    "question": "Comment charger mes données?",
                    "reponse": "Utilisez le bouton d’upload dans la sidebar. CSV/Excel acceptés. Assurez-vous d’avoir une colonne date et une colonne numérique (ex: Ventes).",
                },
                {
                    "question": "Quel est le format de date accepté?",
                    "reponse": "JJ/MM/AAAA, AAAA-MM-JJ, et même dates Excel (serial) sont supportés via une conversion robuste.",
                },
                {
                    "question": "Comment fonctionnent les prévisions?",
                    "reponse": "Plusieurs modèles sont disponibles. Le mode Auto backteste plusieurs modèles et choisit le meilleur (MAE).",
                },
                {
                    "question": "Comment configurer les alertes?",
                    "reponse": "Dans l’onglet Alertes: saisissez nom + email, choisissez la catégorie (optionnel), et définissez les seuils.",
                },
                {
                    "question": "Puis-je exporter mes analyses?",
                    "reponse": "Oui: CSV/Excel/JSON dans l’onglet Données, et rapports TXT dans l’onglet Rapports/Prévisions.",
                },
                {
                    "question": "Les données sont-elles sécurisées?",
                    "reponse": "Les données restent dans la session Streamlit. Les emails dépendent de votre configuration d’envoi.",
                },
            ]

            faqs_en = [
                {
                    "question": "How do I upload my data?",
                    "reponse": "Use the upload button in the sidebar. CSV/Excel supported. Make sure you have a date column and a numeric column (e.g., Sales).",
                },
                {
                    "question": "Which date formats are accepted?",
                    "reponse": "DD/MM/YYYY, YYYY-MM-DD, and even Excel serial dates are supported via robust parsing.",
                },
                {
                    "question": "How do forecasts work?",
                    "reponse": "Several models are available. Auto mode backtests multiple models and chooses the best one (MAE).",
                },
                {
                    "question": "How do I configure alerts?",
                    "reponse": "In the Alerts tab: enter name + email, choose a category (optional), and set the thresholds.",
                },
                {
                    "question": "Can I export my analyses?",
                    "reponse": "Yes: CSV/Excel/JSON in the Data tab, and TXT reports in the Reports/Forecasts tab.",
                },
                {
                    "question": "Is my data secure?",
                    "reponse": "Data stays within the Streamlit session. Emails depend on your sending configuration.",
                },
            ]

            faqs = faqs_fr if get_lang() == "fr" else faqs_en
            for i, faq in enumerate(faqs):
                with st.expander(f"❓ {faq['question']}", expanded=(i == 0)):
                    st.markdown(faq["reponse"])

    except Exception as e:
        fname = uploaded_file.name if uploaded_file is not None else "fichier"
        st.error(f"❌ Erreur lors du chargement/traitement ({fname}): {str(e)}")
        st.code(traceback.format_exc())
        st.info(L("💡 Vérifiez que votre fichier respecte le format requis"))

else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(tr("## 🚀 Bienvenue sur VentesPro Analytics","## 🚀 Welcome to VentesPro Analytics"))
        st.markdown(tr("### Votre plateforme d'analyse et de prévision des ventes par IA","### Your AI-powered sales analytics and forecasting platform"))
        st.info(
            """
### 📋 Pour Commencer
**1️⃣ Préparez votre fichier**
- Colonnes: une date + une colonne numérique
- Format date: JJ/MM/AAAA ou AAAA-MM-JJ
- CSV/Excel supportés

**2️⃣ Chargez votre fichier** via la sidebar ⬅️  
**3️⃣ Explorez** les fonctionnalités!
"""
        )
        st.success(L("💡 Astuce: téléchargez le fichier exemple dans la sidebar"))

# Footer
st.markdown("---")
st.markdown(
    tr("""
<div style='text-align: center; padding: 2rem 0; color: #e2e8f0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        © 2025 VentesPro Analytics | Développé avec ❤️ par Mohamed HADI
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;'>
        Version 2.0 | Propulsé par Streamlit & IA
    </p>
</div>
""","""
<div style='text-align: center; padding: 2rem 0; color: #e2e8f0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        © 2025 VentesPro Analytics | Built with ❤️ by Mohamed HADI
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;'>
        Version 2.0 | Powered by Streamlit & AI
    </p>
</div>
"""),
    unsafe_allow_html=True,
)
