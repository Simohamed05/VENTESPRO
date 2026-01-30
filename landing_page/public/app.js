const $ = (s, p = document) => p.querySelector(s);
const $$ = (s, p = document) => [...p.querySelectorAll(s)];

/* ----------------------------
   Live time + year
---------------------------- */
(function initTime(){
  const el = $("#liveTime");
  const y = $("#year");
  const update = () => {
    const d = new Date();
    const t = d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
    if (el) el.textContent = t;
  };
  update();
  setInterval(update, 15000);
  if (y) y.textContent = new Date().getFullYear();
})();

/* ----------------------------
   Cursor glow follows mouse
---------------------------- */
(function cursorGlow(){
  const glow = $(".cursor-glow");
  if (!glow) return;

  window.addEventListener("mousemove", (e) => {
    const x = (e.clientX / window.innerWidth) * 100;
    const y = (e.clientY / window.innerHeight) * 100;
    glow.style.setProperty("--x", `${x}%`);
    glow.style.setProperty("--y", `${y}%`);
  });

  window.addEventListener("mouseleave", () => (glow.style.opacity = "0"));
  window.addEventListener("mouseenter", () => (glow.style.opacity = "0.9"));
})();

/* ----------------------------
   i18n (FR/EN) - works on all pages
---------------------------- */
const translations = {
  fr: {
    "nav.home": "Accueil",
    "nav.features": "Fonctionnalités",
    "nav.how": "Fonctionnement",
    "nav.models": "Modèles IA",
    "nav.demo": "Démo",
    "nav.login": "Connexion",
    "nav.tagline": "Forecasting • Analytics • Alerts",
    "nav.ctaDemo": "Demander une démo",
    "footer.tagline": "Prévisions • Analyse • Alertes",
    "live.login": "Connexion",
    "live.secure": "Sécurisé",
    "live.analytics": "Analytics",
    "live.demo": "Démo demandée",
    "live.report": "Rapport exporté",
    "live.alert": "Alerte",
    "login.pill": "Accès sécurisé à VentesPro",
    "login.title": "Connexion",
    "login.desc": "Connectez-vous pour accéder à votre tableau de bord, vos prévisions et vos rapports.",
    "login.emailLabel": "Email",
    "login.passLabel": "Mot de passe",
    "login.submit": "Se connecter",
    "login.noAccount": "Pas de compte ? Demander une démo",
    "login.emailPH": "vous@exemple.com",
    "login.passPH": "••••••••",
    "login.sideTitle": "Accès rapide",
    "login.side1t": "Prévisions",
    "login.side1d": "Auto-Model + intervalles",
    "login.side2t": "Alertes",
    "login.side2d": "Seuils & anomalies",
    "login.side3t": "Rapports",
    "login.side3d": "Export & partage",
    "demo.pill": "Démo gratuite — configuration rapide",
    "demo.title": "Demander une démo",
    "demo.desc": "Décris ton activité et tes données : on te montre comment VentesPro peut prévoir, alerter et générer des rapports.",
    "demo.nameLabel": "Nom",
    "demo.emailLabel": "Email",
    "demo.businessLabel": "Type de business",
    "demo.msgLabel": "Message",
    "demo.submit": "Envoyer",
    "demo.namePH": "Votre nom",
    "demo.emailPH": "vous@exemple.com",
    "demo.msgPH": "Ex: prévoir les ventes par catégorie sur 3 mois…",
    "demo.businessOpt0": "Choisir…",
    "demo.businessOpt1": "Commerce / Retail",
    "demo.businessOpt2": "E-commerce",
    "demo.businessOpt3": "Distribution",
    "demo.businessOpt4": "Services",
    "demo.businessOpt5": "Autre",
    "demo.sideTitle": "Ce que tu obtiens",
    "demo.side1t": "Import",
    "demo.side1d": "CSV/Excel + mapping",
    "demo.side2t": "Analyse",
    "demo.side2d": "KPIs + saisonnalité",
    "demo.side3t": "Prévision IA",
    "demo.side3d": "Auto best model",
    "nav.home": "Accueil",
    "live.signup": "Inscription",
    "signup.pill": "Créez votre compte VentesPro",
    "signup.title": "Inscription",
    "signup.desc": "Créez un compte pour accéder à votre espace et tester les fonctionnalités de VentesPro.",
    "signup.nameLabel": "Nom",
    "signup.emailLabel": "Email",
    "signup.passLabel": "Mot de passe",
    "signup.pass2Label": "Confirmer le mot de passe",
    "signup.submit": "Créer mon compte",
    "signup.haveAccount": "Déjà un compte ? Connexion",
    "signup.namePH": "Votre nom",
    "signup.emailPH": "vous@exemple.com",
    "signup.passPH": "Minimum 6 caractères",
    "signup.pass2PH": "Retapez le mot de passe",
    "signup.sideTitle": "Pourquoi créer un compte ?",
    "signup.side1t": "Dashboard",
    "signup.side1d": "KPIs & tendances",
    "signup.side2t": "Prévisions",
    "signup.side2d": "Meilleur modèle auto",
    "signup.side3t": "Rapports",
    "signup.side3d": "Export PDF/CSV"
  },

  en: {
    "nav.home": "Home",
    "nav.features": "Features",
    "nav.how": "How it works",
    "nav.models": "AI Models",
    "nav.demo": "Demo",
    "nav.login": "Sign in",
    "nav.tagline": "Forecasting • Analytics • Alerts",
    "nav.ctaDemo": "Request a demo",
    "footer.tagline": "Forecast • Analytics • Alerts",
    "live.login": "Sign in",
    "live.secure": "Secured",
    "live.analytics": "Analytics",
    "live.demo": "Demo requested",
    "live.report": "Report exported",
    "live.alert": "Alert",
    "login.pill": "Secure access to VentesPro",
    "login.title": "Sign in",
    "login.desc": "Log in to access your dashboard, forecasts, and reports.",
    "login.emailLabel": "Email",
    "login.passLabel": "Password",
    "login.submit": "Sign in",
    "login.noAccount": "No account? Request a demo",
    "login.emailPH": "you@example.com",
    "login.passPH": "••••••••",
    "login.sideTitle": "Quick access",
    "login.side1t": "Forecasts",
    "login.side1d": "Auto-Model + intervals",
    "login.side2t": "Alerts",
    "login.side2d": "Thresholds & anomalies",
    "login.side3t": "Reports",
    "login.side3d": "Export & share",
    "demo.pill": "Free demo — fast setup",
    "demo.title": "Request a demo",
    "demo.desc": "Describe your business and data: we’ll show how VentesPro forecasts, alerts, and generates reports.",
    "demo.nameLabel": "Name",
    "demo.emailLabel": "Email",
    "demo.businessLabel": "Business type",
    "demo.msgLabel": "Message",
    "demo.submit": "Send",
    "demo.namePH": "Your name",
    "demo.emailPH": "you@example.com",
    "demo.msgPH": "e.g., forecast sales by category for 3 months…",
    "demo.businessOpt0": "Choose…",
    "demo.businessOpt1": "Retail",
    "demo.businessOpt2": "E-commerce",
    "demo.businessOpt3": "Distribution",
    "demo.businessOpt4": "Services",
    "demo.businessOpt5": "Other",
    "demo.sideTitle": "What you get",
    "demo.side1t": "Import",
    "demo.side1d": "CSV/Excel + mapping",
    "demo.side2t": "Analytics",
    "demo.side2d": "KPIs + seasonality",
    "demo.side3t": "AI Forecast",
    "demo.side3d": "Auto best model",
    "nav.home": "Home",
    "live.signup": "Sign up",
    "signup.pill": "Create your VentesPro account",
    "signup.title": "Sign up",
    "signup.desc": "Create an account to access your space and test VentesPro features.",
    "signup.nameLabel": "Name",
    "signup.emailLabel": "Email",
    "signup.passLabel": "Password",
    "signup.pass2Label": "Confirm password",
    "signup.submit": "Create account",
    "signup.haveAccount": "Already have an account? Sign in",
    "signup.namePH": "Your name",
    "signup.emailPH": "you@example.com",
    "signup.passPH": "Minimum 6 characters",
    "signup.pass2PH": "Re-enter password",
    "signup.sideTitle": "Why create an account?",
    "signup.side1t": "Dashboard",
    "signup.side1d": "KPIs & trends",
    "signup.side2t": "Forecasts",
    "signup.side2d": "Auto best model",
    "signup.side3t": "Reports",
    "signup.side3d": "Export PDF/CSV"
  }
};

let lang = localStorage.getItem("lang") || "fr";

function applyLang() {
  document.documentElement.lang = lang;
  $$("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    const value = translations[lang]?.[key];
    if (value) el.textContent = value;
  });
  $$("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    const value = translations[lang]?.[key];
    if (value) el.setAttribute("placeholder", value);
  });
  const btn = $("#langBtn");
  if (btn) btn.textContent = lang.toUpperCase();
  localStorage.setItem("lang", lang);
}

$("#langBtn")?.addEventListener("click", () => {
  lang = (lang === "fr") ? "en" : "fr";
  applyLang();
});

applyLang();

/* ----------------------------
   Backend calls (Option B)
---------------------------- */
async function postJSON(url, payload) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data?.message || "Request failed");
  return data;
}

/* Login form -> /api/login */
(function login(){
  const form = $("#loginForm");
  if (!form) return;
  const msg = $("#loginMsg");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (msg) msg.textContent = "";
    const payload = {
      email: form.email.value.trim(),
      password: form.password.value
    };
    try {
      const res = await postJSON("/api/login", payload);
      localStorage.setItem("token", res.token);
      if (msg) msg.textContent = (lang === "fr") ? "✅ Connexion réussie !" : "✅ Login success!";
    } catch (err) {
      if (msg) msg.textContent = (lang === "fr") ? `❌ ${err.message}` : `❌ ${err.message}`;
    }
  });
})();

/* Demo form -> /api/demo */
(function demo(){
  const form = $("#demoForm");
  if (!form) return;
  const msg = $("#demoMsg");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (msg) msg.textContent = "";
    const payload = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      business: form.business.value,
      message: form.message.value.trim()
    };
    try {
      await postJSON("/api/demo", payload);
      if (msg) msg.textContent = (lang === "fr") ? "✅ Demande envoyée !" : "✅ Request sent!";
    } catch (err) {
      if (msg) msg.textContent = (lang === "fr") ? `❌ ${err.message}` : `❌ ${err.message}`;
    }
  });
})();

/* Signup form -> /api/signup */
(function signup(){
  const form = $("#signupForm");
  if (!form) return;
  const msg = $("#signupMsg");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (msg) msg.textContent = "";
    const payload = {
      name: form.name.value.trim(),
      email: form.email.value.trim(),
      password: form.password.value,
      passwordConfirm: form.password2.value
    };
    try {
      await postJSON("/api/signup", payload);
      if (msg) msg.textContent = (lang === "fr") ? "✅ Compte créé !" : "✅ Account created!";
    } catch (err) {
      if (msg) msg.textContent = (lang === "fr") ? `❌ ${err.message}` : `❌ ${err.message}`;
    }
  });
})();

/* =========================
   REVEAL ANIMATIONS
========================= */
window.addEventListener("scroll", () => {
  document.querySelectorAll(".reveal").forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top <= window.innerHeight * 0.85) {
      el.classList.add("is-in");
    }
  });
});

/* =========================
   CARD TILT / MAGNETIC / TOOLTIPS
========================= */
// Force reveal at load to avoid flicker
window.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".reveal").forEach(el => {
    el.classList.add("is-in");
  });
});
window.addEventListener("DOMContentLoaded", () => {
  // Re-initialise interactions after HTML changes
  initCursorGlow();
  initTilt();
  initMagnetic();
  initTooltip();
  initMobileMenu();
  initParallax();
  initPointerBall();
  initSectionObserver();
  initScrollProgress();
});
function initCursorGlow(){
  const glow = document.querySelector(".cursor-glow");
  if (!glow) return;
  const set = (e) => {
    const x = (e.clientX / window.innerWidth) * 100;
    const y = (e.clientY / window.innerHeight) * 100;
    document.documentElement.style.setProperty("--x", `${x}%`);
    document.documentElement.style.setProperty("--y", `${y}%`);
  };
  window.addEventListener("mousemove", set, { passive: true });
}

function initTilt(){
  // Apply tilt to more elements (features, models, steps, KPIs, mini cards) for richer interactions
  const cards = document.querySelectorAll(
    ".card-tilt, .feature, .model, .step, .kpi, .mini-card"
  );
  if (!cards.length) return;
  const max = 10; // degrees
  cards.forEach(card => {
    card.addEventListener("mousemove", (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width;
      const py = (e.clientY - r.top) / r.height;
      const rx = (py - 0.5) * -max;
      const ry = (px - 0.5) * max;
      card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });
  });
}

function initMagnetic(){
  // Apply magnetic translation to more elements (features, models, steps, KPIs, mini cards)
  const items = document.querySelectorAll(
    ".magnetic, .feature, .model, .step, .kpi, .mini-card"
  );
  if (!items.length) return;
  items.forEach(el => {
    el.addEventListener("mousemove", (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - (r.left + r.width/2)) / (r.width/2);
      const y = (e.clientY - (r.top + r.height/2)) / (r.height/2);
      el.style.transform = `translate(${x * 6}px, ${y * 6}px)`;
    });
    el.addEventListener("mouseleave", () => {
      el.style.transform = "";
    });
  });
}

function initTooltip(){
  const tip = document.querySelector(".tooltip");
  if (!tip) return;
  const els = document.querySelectorAll("[data-tip]");
  if (!els.length) return;
  const move = (e) => {
    tip.style.left = (e.clientX + 14) + "px";
    tip.style.top  = (e.clientY + 14) + "px";
  };
  els.forEach(el => {
    el.addEventListener("mouseenter", () => {
      tip.textContent = el.getAttribute("data-tip") || "";
      tip.style.opacity = "1";
      tip.style.transform = "translate3d(0,0,0)";
      window.addEventListener("mousemove", move, { passive: true });
    });
    el.addEventListener("mouseleave", () => {
      tip.style.opacity = "0";
      tip.style.transform = "translate3d(0,10px,0)";
      window.removeEventListener("mousemove", move);
    });
  });
}

function initParallax(){
  const heroBg = document.querySelector(".hero-bg");
  if (!heroBg) return;
  const update = (e) => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    const cx = w / 2;
    const cy = h / 2;
    const dx = (e.clientX - cx) / cx;
    const dy = (e.clientY - cy) / cy;
    const rangeX = 40;
    const rangeY = 30;
    const offX = dx * rangeX;
    const offY = dy * rangeY;
    document.documentElement.style.setProperty("--parallaxX", offX + "px");
    document.documentElement.style.setProperty("--parallaxY", offY + "px");
  };
  window.addEventListener("mousemove", update, { passive: true });
}

function initPointerBall(){
  const existing = document.querySelector(".pointer-ball");
  if (existing) existing.remove();
  const ball = document.createElement("div");
  ball.className = "pointer-ball";
  document.body.appendChild(ball);
  let x = 0, y = 0;
  let rafId = null;
  const move = (e) => {
    x = e.clientX;
    y = e.clientY;
    if (!rafId) {
      rafId = requestAnimationFrame(() => {
      ball.style.transform = `translate(${x}px, ${y}px)`;
      rafId = null;
    });
    }
  };
  window.addEventListener("mousemove", move, { passive: true });
  window.addEventListener("mouseleave", () => {
    ball.style.opacity = "0";
  });
  window.addEventListener("mouseenter", () => {
    ball.style.opacity = "0.8";
  });
}

function initSectionObserver(){
  const sections = document.querySelectorAll("section[id]");
  const links = document.querySelectorAll(".menu a[href^='#']");
  if (!sections.length || !links.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute("id");
        links.forEach(l => l.classList.remove("active"));
        const active = document.querySelector(`.menu a[href='#${id}']`);
        if (active) active.classList.add("active");
      }
    });
  }, { threshold: 0.4 });
  sections.forEach(sec => observer.observe(sec));
}

function initScrollProgress(){
  const bar = document.getElementById("scrollProgress");
  if (!bar) return;
  const update = () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = progress + "%";
  };
  window.addEventListener("scroll", update, { passive: true });
  update();
}

function initMobileMenu(){
  const burger = document.getElementById("hamburger");
  const menu = document.getElementById("mobileMenu");
  if (!burger || !menu) return;
  burger.addEventListener("click", () => {
    const open = menu.style.display === "flex";
    menu.style.display = open ? "none" : "flex";
    burger.setAttribute("aria-expanded", String(!open));
    menu.setAttribute("aria-hidden", String(open));
  });
}

/* =========================
   I18N FR/EN for main index page
========================= */
document.addEventListener("DOMContentLoaded", () => {
  const dict = {
    fr: {
      // NAV
      nav_features: "Fonctionnalités",
      nav_how: "Fonctionnement",
      nav_models: "Modèles IA",
      nav_reports: "Rapports",
      nav_contact: "Contact",
      btn_login: "Connexion",
      btn_signup: "Créer un compte",
      btn_demo: "Demander une démo",
      // HERO
      hero_pill: "Plateforme intelligente de prévision & analyse des ventes",
      hero_h1_a: "Transforme ton historique de ventes en",
      hero_h1_b: "prévisions fiables",
      hero_h1_c: "alertes intelligentes",
      hero_h1_d: "et décisions data-driven.",
      hero_lead:
        "VentesPro est une application web avancée basée sur l’IA & le Machine Learning. Import CSV/Excel → analyse → prévision → alertes → rapports exportables, via une interface claire et interactive.",
      hero_cta_try: "Essayer VentesPro",
      hero_cta_how: "Voir comment ça marche",
      kpi_1: "Comparaison automatique des modèles",
      kpi_2: "Import & configuration dynamique",
      kpi_3: "Seuils & anomalies détectées",
      // MOCK
      mock_title: "VentesPro Dashboard",
      mock_data_title: "Données",
      mock_data_sub: "Import & nettoyage",
      mock_dash_title: "Dashboard",
      mock_dash_sub: "Vue globale",
      mock_ai_title: "Prévisions IA",
      mock_ai_sub: "Auto-Model",
      mock_alert_title: "Alertes",
      mock_alert_sub: "Seuils & risques",
      mock_graph_title: "Prévision (intervalle de confiance)",
      tag_mae: "MAE",
      tag_rmse: "RMSE",
      tag_season: "Saisonnalité",
      tag_anom: "Anomalies",
      // FEATURES
      feat_head_h2: "Tout le workflow ventes, dans une seule plateforme",
      feat_head_p: "Import → préparation → analyse → prévision → alertes → rapports. Simple, rapide, data-driven.",
      feat_1_h3: "Gestion & préparation des données",
      feat_1_p: "Import CSV/Excel, mapping colonnes (dates, quantités, catégories), nettoyage, agrégation & structuration temporelle.",
      feat_2_h3: "Tableau de bord interactif",
      feat_2_p: "Évolution des ventes, moyennes, saisonnalité (jours/mois forts), KPI, tendances — comprendre le passé avant de prévoir.",
      feat_3_h3: "Alertes intelligentes",
      feat_3_p: "Définis des seuils de variation (hausse/baisse). Détection d’anomalies et alertes visuelles pour réagir vite.",
      // HOW
      how_h2: "Comment ça marche",
      how_p: "Un parcours fluide, pensé pour la prise de décision stratégique.",
      step1_h3: "Importer & configurer",
      step1_p: "Charge tes données (CSV/Excel) et mappe les colonnes (date, quantité, catégorie…).",
      step2_h3: "Analyser & comprendre",
      step2_p: "Stats, distributions, corrélations, moyennes mobiles, saisonnalité — révèle les patterns cachés.",
      step3_h3: "Prévoir avec l’IA",
      step3_p: "Mode Auto compare MAE/RMSE et sélectionne le modèle le plus fiable, avec intervalle de confiance.",
      step4_h3: "Déclencher des alertes",
      step4_p: "Seuils (hausse/baisse), anomalies, notifications visuelles — anticipe risques et opportunités.",
      step5_h3: "Exporter des rapports",
      step5_p: "Rapports synthétiques et partageables pour stock, planification commerciale et objectifs.",
      // MODELS
      models_h2: "Prévisions IA : plusieurs familles de modèles",
      models_p: "Statistiques, Machine Learning, modèles avancés — avec sélection automatique du meilleur.",
      stat_h3: "Statistiques",
      ml_h3: "Machine Learning",
      adv_h3: "Avancés",
      chip_robust: "Robustes",
      chip_flex: "Flexible",
      chip_smart: "Smart",
      // REPORTS
      reports_h2: "Rapports & aide à la décision",
      reports_p:
        "Génère des rapports synthétiques exportables pour suivre la performance, partager les résultats, optimiser le stock, la planification commerciale et les objectifs de vente.",
      badge_insights: "📌 Insights",
      badge_export: "📤 Export",
      badge_trends: "📈 Trends",
      goal_title: "Objectif",
      goal_sub: "Démocratiser la data science appliquée aux ventes",
      meter_rel: "Fiabilité",
      meter_cla: "Clarté",
      meter_pro: "Proactivité",
      // CONTACT
      contact_h2: "Demander une démo",
      contact_p: "Dis-moi ton secteur et ton type de données — je t’aide à configurer VentesPro rapidement.",
      form_name_label: "Nom",
      form_email_label: "Email",
      form_business_label: "Type de business",
      form_msg_label: "Message",
      form_send: "Envoyer",
      form_note: "* Démo gratuite — réponse rapide.",
      form_business_choose: "Choisir…",
      form_business_ecom: "E-commerce",
      form_business_retail: "Retail",
      form_business_wholesale: "Grossiste",
      form_business_other: "Autre",
      // Placeholders
      form_name_ph: "Votre nom",
      form_email_ph: "vous@exemple.com",
      form_msg_ph: "Ex : je veux prévoir mes ventes par catégorie sur 3 mois…",
      // FOOTER
      foot_small: "Prévisions • Analyse • Alertes",
      foot_link_features: "Fonctionnalités",
      foot_link_models: "Modèles",
      foot_link_contact: "Contact",
      rights: "Tous droits réservés."
    },

    en: {
      // NAV
      nav_features: "Features",
      nav_how: "How it works",
      nav_models: "AI Models",
      nav_reports: "Reports",
      nav_contact: "Contact",
      btn_login: "Sign in",
      btn_signup: "Create account",
      btn_demo: "Request a demo",
      // HERO
      hero_pill: "Smart platform for sales forecasting & analytics",
      hero_h1_a: "Turn your sales history into",
      hero_h1_b: "reliable forecasts",
      hero_h1_c: "smart alerts",
      hero_h1_d: "and data-driven decisions.",
      hero_lead:
        "VentesPro is an advanced web app powered by AI & Machine Learning. Import CSV/Excel → analyze → forecast → alerts → exportable reports, with a clear and interactive interface.",
      hero_cta_try: "Try VentesPro",
      hero_cta_how: "See how it works",
      kpi_1: "Automatic model comparison",
      kpi_2: "Import & dynamic setup",
      kpi_3: "Thresholds & anomalies detected",
      // MOCK
      mock_title: "VentesPro Dashboard",
      mock_data_title: "Data",
      mock_data_sub: "Import & cleaning",
      mock_dash_title: "Dashboard",
      mock_dash_sub: "Overview",
      mock_ai_title: "AI Forecasts",
      mock_ai_sub: "Auto-Model",
      mock_alert_title: "Alerts",
      mock_alert_sub: "Thresholds & risks",
      mock_graph_title: "Forecast (confidence interval)",
      tag_mae: "MAE",
      tag_rmse: "RMSE",
      tag_season: "Seasonality",
      tag_anom: "Anomalies",
      // FEATURES
      feat_head_h2: "Your entire sales workflow in one platform",
      feat_head_p: "Import → prep → analysis → forecasting → alerts → reports. Simple, fast, data-driven.",
      feat_1_h3: "Data preparation & management",
      feat_1_p: "Import CSV/Excel, column mapping (dates, quantities, categories), cleaning, aggregation & time structuring.",
      feat_2_h3: "Interactive dashboard",
      feat_2_p: "Sales over time, averages, seasonality (best days/months), KPIs, trends — understand the past before forecasting.",
      feat_3_h3: "Smart alerts",
      feat_3_p: "Set change thresholds (up/down). Detect anomalies and show visual alerts to react fast.",
      // HOW
      how_h2: "How it works",
      how_p: "A smooth journey designed for better decision-making.",
      step1_h3: "Import & configure",
      step1_p: "Upload your data (CSV/Excel) and map columns (date, quantity, category…).",
      step2_h3: "Analyze & understand",
      step2_p: "Stats, distributions, correlations, moving averages, seasonality — uncover hidden patterns.",
      step3_h3: "Forecast with AI",
      step3_p: "Auto mode compares MAE/RMSE and selects the most reliable model, with confidence intervals.",
      step4_h3: "Trigger alerts",
      step4_p: "Thresholds (up/down), anomalies, visual notifications — anticipate risks and opportunities.",
      step5_h3: "Export reports",
      step5_p: "Shareable summary reports for inventory, planning, and targets.",
      // MODELS
      models_h2: "AI forecasting: multiple model families",
      models_p: "Statistics, Machine Learning, advanced models — with automatic best-model selection.",
      stat_h3: "Statistical",
      ml_h3: "Machine Learning",
      adv_h3: "Advanced",
      chip_robust: "Robust",
      chip_flex: "Flexible",
      chip_smart: "Smart",
      // REPORTS
      reports_h2: "Reports & decision support",
      reports_p:
        "Generate exportable summary reports to track performance, share results, and optimize inventory, planning, and sales targets.",
      badge_insights: "📌 Insights",
      badge_export: "📤 Export",
      badge_trends: "📈 Trends",
      goal_title: "Goal",
      goal_sub: "Make sales data science accessible",
      meter_rel: "Reliability",
      meter_cla: "Clarity",
      meter_pro: "Proactivity",
      // CONTACT
      contact_h2: "Request a demo",
      contact_p: "Tell us your industry and data type — we’ll help you set up VentesPro quickly.",
      form_name_label: "Name",
      form_email_label: "Email",
      form_business_label: "Business type",
      form_msg_label: "Message",
      form_send: "Send",
      form_note: "* Free demo — quick reply.",
      form_business_choose: "Choose…",
      form_business_ecom: "E-commerce",
      form_business_retail: "Retail",
      form_business_wholesale: "Wholesale",
      form_business_other: "Other",
      // Placeholders
      form_name_ph: "Your name",
      form_email_ph: "you@example.com",
      form_msg_ph: "Example: I want category-level forecasts for the next 3 months…",
      // FOOTER
      foot_small: "Forecasting • Analytics • Alerts",
      foot_link_features: "Features",
      foot_link_models: "Models",
      foot_link_contact: "Contact",
      rights: "All rights reserved."
    }
  };

  function applyLang(lang) {
    const pack = dict[lang] || dict.fr;
    localStorage.setItem("lang", lang);
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (pack[key]) el.textContent = pack[key];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder");
      if (pack[key]) el.setAttribute("placeholder", pack[key]);
    });
    document.querySelectorAll(".langToggle").forEach((btn) => {
      btn.textContent = lang === "fr" ? "EN" : "FR";
    });
    if (lang === "en") {
      document.title = "VentesPro — Smart Sales Forecasting & Analytics";
    } else {
      document.title = "VentesPro — Prévision & Analyse Intelligente des Ventes";
    }
  }

  document.querySelectorAll(".langToggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const current = localStorage.getItem("lang") || "fr";
      applyLang(current === "fr" ? "en" : "fr");
    });
  });

  applyLang(localStorage.getItem("lang") || "fr");
});
