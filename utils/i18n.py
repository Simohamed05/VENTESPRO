# utils/i18n.py — VentesPRO (aligné 100% avec ton app.py)

import streamlit as st

TRANANG = ("fr", "en")

TRANSLATIONS = {
    "fr": {
        # =========================
        # Language selector
        # =========================
        "lang_label": "🌐 Langue",
        "lang_fr": "FR",
        "lang_en": "EN",
        "theme_label": "🎨 Thème",
        "theme_auto": "Auto",
        "theme_light": "Clair",
        "theme_dark": "Sombre",

        # =========================
        # Sidebar / Upload
        # =========================
        "config_title": "⚙️ Configuration",
        "upload_label": "📥 Chargez votre fichier (CSV/Excel)",
        "upload_help": "Supporte CSV/Excel/TSV/TXT/Parquet (colonnes libres)",
        "download_example": "📄 Télécharger fichier exemple",
        "file_loaded": "✅ Fichier chargé : {name}",
        "file_details_title": "**Détails du fichier :**",
        "file_details_rows": "- Lignes : {n}",
        "file_details_cols": "- Colonnes : {n}",
        "file_details_detected": "- Colonnes détectées : {cols}",
        "file_empty": "❌ Le fichier est vide",
        "err_load_file": "❌ Impossible de charger le fichier.",
        "config_columns": "🔧 Configurer les colonnes",
        "date_col": "📅 Colonne de date",
        "date_col_help": "Sélectionnez la colonne contenant les dates",
        "target_col": "🎯 Colonne cible (à prévoir)",
        "target_col_help": "Sélectionnez la colonne numérique à analyser et prévoir",
        "cat_col": "📦 Colonne catégorique (optionnelle)",
        "cat_col_help": "Sélectionnez une colonne catégorique (ex : Produit, Région)",
        "none": "Aucune",
        "need_cols": "⚠️ Sélectionnez au moins la colonne date et la colonne cible pour continuer.",
        "date_convert_error": "❌ Erreur lors de la conversion de la colonne date : {err}",

        # =========================
        # Quick stats (sidebar)
        # =========================
        "quick_stats": "### 📊 Statistiques Rapides",
        "total_target": "💰 Total Cible",
        "unique_cats": "📦 Catégories Uniques",
        "period_entries": "📅 Période",
        "entries": "{n} entrées",

        # =========================
        # Tabs
        # =========================
        "tab_home": "🏠 Accueil",
        "tab_dashboard": "📊 Tableau de Bord",
        "tab_analysis": "📈 Analyse Avancée",
        "tab_alerts": "⚠️ Alertes",
        "tab_forecast": "🔮 Prévisions",
        "tab_data": "📂 Données",
        "tab_reports": "📑 Rapports",
        "tab_insights": "💡 Insights",
        "tab_support": "📞 Support",

        # =========================
        # HOME
        # =========================
        "home_welcome_title": "### 🎯 Bienvenue sur VentesPRO",
        "home_welcome_text": "Transformez vos données temporelles en insights actionnables avec notre plateforme d'analyse avancée et de prévision par IA.",
        "overview": "### 📊 Vue d'ensemble",

        "kpi_total_target": "Total des valeurs",
        "kpi_unique_categories": "Catégories uniques",
        "kpi_avg_growth": "Croissance moyenne",
        "kpi_avg_target": "Valeur moyenne",
        "kpi_categories": "Catégories",

        "home_features_title": "Fonctionnalités Principales",
        "home_feat_realtime_title": "Analyse en Temps Réel",
        "home_feat_realtime_1": "Dashboard interactif",
        "home_feat_realtime_2": "Visualisations dynamiques",
        "home_feat_realtime_3": "KPIs automatisés",
        "home_feat_realtime_4": "Comparaisons multi-catégories",
        "home_feat_realtime_5": "Analyse saisonnière",

        "home_feat_ai_title": "Prévisions IA",
        "home_feat_ai_1": "5+ modèles de ML",
        "home_feat_ai_2": "Mode Auto-Select",
        "home_feat_ai_3": "Intervalles de confiance",
        "home_feat_ai_4": "Prévisions jusqu'à 1 an",
        "home_feat_ai_5": "Comparaison de modèles",

        "home_feat_alerts_title": "Alertes Intelligentes",
        "home_feat_alerts_1": "Notifications Email/SMS",
        "home_feat_alerts_2": "Seuils personnalisables",
        "home_feat_alerts_3": "Détection d'anomalies",
        "home_feat_alerts_4": "Alertes en temps réel",
        "home_feat_alerts_5": "Historique des alertes",

        "home_global_trend_title": "Tendance Globale",
        "home_trend_chart_title": "Évolution des valeurs avec moyennes mobiles",
        "legend_daily": "Valeurs Quotidiennes",
        "legend_ma7": "Moyenne Mobile 7j",
        "legend_ma30": "Moyenne Mobile 30j",

        "axis_date": "Date",
        "axis_values": "Valeurs",

        "home_quickstart_title": "Guide de Démarrage Rapide",
        "home_howto_title": "📖 Comment utiliser VentesPRO",
        "home_howto_md": """
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
""",

        # =========================
        # DASHBOARD
        # =========================
        "dash_title": "Tableau de Bord Interactif",
        "filters_title": "🔍 Filtres",
        "categories": "Catégories",
        "start_date": "Date de début",
        "end_date": "Date de fin",
        "warn_no_data_filters": "⚠️ Aucune donnée ne correspond aux filtres sélectionnés",

        "dash_tab_trend": "📈 Évolution",
        "dash_tab_geo": "🌍 Géographie",
        "dash_tab_promo": "🏷️ Promotions",
        "dash_tab_stock": "📦 Stocks",
        "dash_tab_season": "📅 Saisonnalité",

        "no_region_col": "📌 Pas de colonne 'Region' dans les données",
        "no_promo_col": "📌 Pas de colonne 'Promo' dans les données",
        "no_stock_col": "📌 Pas de colonne 'Stock' dans les données",

        # Weekdays (utilisés dans Seasonality)
        "day_mon": "Lun",
        "day_tue": "Mar",
        "day_wed": "Mer",
        "day_thu": "Jeu",
        "day_fri": "Ven",
        "day_sat": "Sam",
        "day_sun": "Dim",

        # =========================
        # ANALYSIS
        # =========================
        "analysis_title": "Analyse Avancée et Statistiques",
        "analysis_tab_vars": "📊 Variables",
        "analysis_tab_corr": "🔗 Corrélations",
        "analysis_tab_trends": "📉 Tendances",
        "analysis_tab_pred": "🎯 Analyse Prédictive",
        "use_forecast_section": "Utilisez la section Prévisions pour des modèles avancés",
        "no_numeric_vars": "Aucune variable numérique disponible pour l'analyse",
        "corr_matrix": "Matrice de Corrélation",
        "var_x": "Variable X",
        "var_y": "Variable Y",
        "corr_coef": "Coefficient de corrélation",

        # =========================
        # ALERTS
        # =========================
        "alerts_title": "Système d'Alertes Intelligentes",
        "alerts_intro": "Configurez des alertes pour surveiller les variations importantes de vos valeurs.\nVous recevrez un email lorsque les seuils sont dépassés.",
        "your_name": "👤 Votre nom*",
        "your_email": "📧 Votre email*",
        "your_phone_optional": "📱 Votre téléphone (optionnel)",
        "alert_settings": "### 📊 Paramètres d'Alerte",
        "category_to_watch": "Catégorie à surveiller",
        "rise_threshold": "📈 Seuil de hausse (%)",
        "drop_threshold": "📉 Seuil de baisse (%)",
        "activate_alerts": "✅ Activer les Alertes",
        "invalid_phone": "❌ Format de téléphone invalide (ex: +212766052983 ou 0766052983)",
        "alerts_enabled": "✅ Alertes activées! Vous recevrez un email de confirmation.",
        "save_error": "❌ Erreur lors de l'enregistrement. Essayez à nouveau.",
        "invalid_email": "❌ Format d'email invalide",
        "fill_required": "❌ Veuillez remplir les champs obligatoires",
        "email_alert_confirm_subject": "Confirmation d'Activation des Alertes - VentesPRO",

        # =========================
        # FORECAST
        # =========================
        "forecast_title": "## 🔮 Prévisions par Intelligence Artificielle",
        "forecast_intro": "Générez des prévisions pour votre colonne cible.\n✅ Compatible avec n’importe quelle colonne numérique\n✅ Date optionnelle (si pas de date, une timeline est générée automatiquement)",
        "forecast_tips": "**Modèles conseillés** : Auto (comparaison + ensemble), Extra Trees, Gradient Boosting, Random Forest, XGBoost, SARIMA / Holt-Winters (si saisonnalité) et Prophet pour les séries business.",
        "category_to_forecast": "Catégorie à prévoir",
        "forecast_model": "Modèle de prévision",
        "forecast_horizon": "Horizon de prévision (nombre de points)",
        "show_confidence": "Afficher intervalles de confiance (95%)",
        "generate_forecast": "🔮 Générer les Prévisions",
        "status_prepare": "📦 Préparation des données...",
        "forecast_failed": "❌ Impossible de générer les prévisions.",
        "forecast_success": "✅ Prévisions générées avec succès!",
        "downloads": "### 💾 Téléchargements",
        "download_csv": "📥 Télécharger CSV",
        "download_report": "📄 Télécharger Rapport",

        # =========================
        # EMPTY STATE (no file)
        # =========================
        "welcome_title": "Bienvenue sur VentesPro Analytics",
        "welcome_subtitle": "Votre plateforme d'analyse et de prévision des ventes par IA",
        "welcome_steps_md": """
### 📋 Pour Commencer
**1️⃣ Préparez votre fichier**
- Colonnes: une date + une colonne numérique
- Format date: JJ/MM/AAAA ou AAAA-MM-JJ
- CSV/Excel supportés

**2️⃣ Chargez votre fichier** via la sidebar ⬅️  
**3️⃣ Explorez** les fonctionnalités!
""",
        "tip_example_file": "💡 Astuce: téléchargez le fichier exemple dans la sidebar",

        # =========================
        # FOOTER
        # =========================
        "footer_built_by": "© 2025 VentesPro Analytics | Développé avec ❤️ par {name}",
        "footer_version_powered": "Version 2.0 | Propulsé par Streamlit & IA",
    },

    "en": {
        # =========================
        # Language selector
        # =========================
        "lang_label": "🌐 Language",
        "lang_fr": "FR",
        "lang_en": "EN",
        "theme_label": "🎨 Theme",
        "theme_auto": "Auto",
        "theme_light": "Light",
        "theme_dark": "Dark",

        # =========================
        # Sidebar / Upload
        # =========================
        "config_title": "⚙️ Settings",
        "upload_label": "📥 Upload your file (CSV/Excel)",
        "upload_help": "Supports CSV/Excel/TSV/TXT/Parquet (any columns)",
        "download_example": "📄 Download sample file",
        "file_loaded": "✅ File loaded: {name}",
        "file_details_title": "**File details:**",
        "file_details_rows": "- Rows: {n}",
        "file_details_cols": "- Columns: {n}",
        "file_details_detected": "- Detected columns: {cols}",
        "file_empty": "❌ The file is empty",
        "err_load_file": "❌ Unable to load the file.",
        "config_columns": "🔧 Configure columns",
        "date_col": "📅 Date column",
        "date_col_help": "Select the column containing dates",
        "target_col": "🎯 Target column (to forecast)",
        "target_col_help": "Select the numeric column to analyze and forecast",
        "cat_col": "📦 Category column (optional)",
        "cat_col_help": "Select a categorical column (e.g., Product, Region)",
        "none": "None",
        "need_cols": "⚠️ Please select at least the date column and target column to continue.",
        "date_convert_error": "❌ Error converting date column: {err}",

        # =========================
        # Quick stats (sidebar)
        # =========================
        "quick_stats": "### 📊 Quick Stats",
        "total_target": "💰 Total Target",
        "unique_cats": "📦 Unique Categories",
        "period_entries": "📅 Period",
        "entries": "{n} entries",

        # =========================
        # Tabs
        # =========================
        "tab_home": "🏠 Home",
        "tab_dashboard": "📊 Dashboard",
        "tab_analysis": "📈 Advanced Analysis",
        "tab_alerts": "⚠️ Alerts",
        "tab_forecast": "🔮 Forecasting",
        "tab_data": "📂 Data",
        "tab_reports": "📑 Reports",
        "tab_insights": "💡 Insights",
        "tab_support": "📞 Support",

        # =========================
        # HOME
        # =========================
        "home_welcome_title": "### 🎯 Welcome to VentesPRO",
        "home_welcome_text": "Turn your time-series data into actionable insights with our advanced analytics and AI forecasting platform.",
        "overview": "### 📊 Overview",

        "kpi_total_target": "Total values",
        "kpi_unique_categories": "Unique categories",
        "kpi_avg_growth": "Average growth",
        "kpi_avg_target": "Average value",
        "kpi_categories": "Categories",

        "home_features_title": "Key Features",
        "home_feat_realtime_title": "Real-time Analytics",
        "home_feat_realtime_1": "Interactive dashboard",
        "home_feat_realtime_2": "Dynamic visualizations",
        "home_feat_realtime_3": "Automated KPIs",
        "home_feat_realtime_4": "Multi-category comparisons",
        "home_feat_realtime_5": "Seasonality analysis",

        "home_feat_ai_title": "AI Forecasting",
        "home_feat_ai_1": "5+ ML models",
        "home_feat_ai_2": "Auto-select mode",
        "home_feat_ai_3": "Confidence intervals",
        "home_feat_ai_4": "Forecast up to 1 year",
        "home_feat_ai_5": "Model comparison",

        "home_feat_alerts_title": "Smart Alerts",
        "home_feat_alerts_1": "Email/SMS notifications",
        "home_feat_alerts_2": "Custom thresholds",
        "home_feat_alerts_3": "Anomaly detection",
        "home_feat_alerts_4": "Real-time alerts",
        "home_feat_alerts_5": "Alerts history",

        "home_global_trend_title": "Overall Trend",
        "home_trend_chart_title": "Values evolution with moving averages",
        "legend_daily": "Daily Values",
        "legend_ma7": "7-day Moving Avg",
        "legend_ma30": "30-day Moving Avg",

        "axis_date": "Date",
        "axis_values": "Values",

        "home_quickstart_title": "Quick Start Guide",
        "home_howto_title": "📖 How to use VentesPRO",
        "home_howto_md": """
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
- Category column (optional)

#### 4️⃣ Explore
- Dashboard
- Analysis
- Alerts
- Forecasting
- Reports / Exports
""",

        # =========================
        # DASHBOARD
        # =========================
        "dash_title": "Interactive Dashboard",
        "filters_title": "🔍 Filters",
        "categories": "Categories",
        "start_date": "Start date",
        "end_date": "End date",
        "warn_no_data_filters": "⚠️ No data matches the selected filters",

        "dash_tab_trend": "📈 Trend",
        "dash_tab_geo": "🌍 Geography",
        "dash_tab_promo": "🏷️ Promotions",
        "dash_tab_stock": "📦 Stock",
        "dash_tab_season": "📅 Seasonality",

        "no_region_col": "📌 No 'Region' column found in the data",
        "no_promo_col": "📌 No 'Promo' column found in the data",
        "no_stock_col": "📌 No 'Stock' column found in the data",

        # Weekdays
        "day_mon": "Mon",
        "day_tue": "Tue",
        "day_wed": "Wed",
        "day_thu": "Thu",
        "day_fri": "Fri",
        "day_sat": "Sat",
        "day_sun": "Sun",

        # =========================
        # ANALYSIS
        # =========================
        "analysis_title": "Advanced Analysis & Statistics",
        "analysis_tab_vars": "📊 Variables",
        "analysis_tab_corr": "🔗 Correlations",
        "analysis_tab_trends": "📉 Trends",
        "analysis_tab_pred": "🎯 Predictive Analysis",
        "use_forecast_section": "Use the Forecasting section for advanced models",
        "no_numeric_vars": "No numeric variables available for analysis",
        "corr_matrix": "Correlation Matrix",
        "var_x": "X variable",
        "var_y": "Y variable",
        "corr_coef": "Correlation coefficient",

        # =========================
        # ALERTS
        # =========================
        "alerts_title": "Smart Alerts System",
        "alerts_intro": "Configure alerts to monitor significant changes.\nYou will receive an email when thresholds are exceeded.",
        "your_name": "👤 Your name*",
        "your_email": "📧 Your email*",
        "your_phone_optional": "📱 Your phone (optional)",
        "alert_settings": "### 📊 Alert settings",
        "category_to_watch": "Category to monitor",
        "rise_threshold": "📈 Increase threshold (%)",
        "drop_threshold": "📉 Decrease threshold (%)",
        "activate_alerts": "✅ Enable alerts",
        "invalid_phone": "❌ Invalid phone format (e.g. +212766052983 or 0766052983)",
        "alerts_enabled": "✅ Alerts enabled! You will receive a confirmation email.",
        "save_error": "❌ Error while saving. Please try again.",
        "invalid_email": "❌ Invalid email format",
        "fill_required": "❌ Please fill in required fields",
        "email_alert_confirm_subject": "Alerts enabled confirmation - VentesPRO",

        # =========================
        # FORECAST
        # =========================
        "forecast_title": "## 🔮 AI Forecasting",
        "forecast_intro": "Generate forecasts for your target column.\n✅ Works with any numeric column\n✅ Optional date (if missing, a timeline is generated automatically)",
        "forecast_tips": "**Recommended models**: Auto (comparison + ensemble), Extra Trees, Gradient Boosting, Random Forest, XGBoost, SARIMA / Holt-Winters (seasonality) and Prophet for business series.",
        "category_to_forecast": "Category to forecast",
        "forecast_model": "Forecast model",
        "forecast_horizon": "Forecast horizon (number of points)",
        "show_confidence": "Show confidence interval (95%)",
        "generate_forecast": "🔮 Generate Forecast",
        "status_prepare": "📦 Preparing data...",
        "forecast_failed": "❌ Unable to generate forecasts.",
        "forecast_success": "✅ Forecast generated successfully!",
        "downloads": "### 💾 Downloads",
        "download_csv": "📥 Download CSV",
        "download_report": "📄 Download Report",

        # =========================
        # EMPTY STATE (no file)
        # =========================
        "welcome_title": "Welcome to VentesPro Analytics",
        "welcome_subtitle": "Your AI sales analytics & forecasting platform",
        "welcome_steps_md": """
### 📋 Getting started
**1️⃣ Prepare your file**
- Columns: one date + one numeric column
- Date formats: DD/MM/YYYY or YYYY-MM-DD
- CSV/Excel supported

**2️⃣ Upload your file** from the sidebar ⬅️  
**3️⃣ Explore** the features!
""",
        "tip_example_file": "💡 Tip: download the sample file from the sidebar",

        # =========================
        # FOOTER
        # =========================
        "footer_built_by": "© 2025 VentesPro Analytics | Built with ❤️ by {name}",
        "footer_version_powered": "Version 2.0 | Powered by Streamlit & AI",
    },
}


def set_lang(lang: str):
    """Store 'fr' or 'en' in session_state."""
    if lang not in ("fr", "en"):
        lang = "fr"
    st.session_state["lang"] = lang


def get_lang() -> str:
    return st.session_state.get("lang", "fr")


def t(key: str, **kwargs) -> str:
    """
    Translate a key based on current language.
    Supports .format(**kwargs).
    """
    lang = get_lang()
    text = TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["fr"].get(key, key))
    try:
        return text.format(**kwargs)
    except Exception:
        return text
