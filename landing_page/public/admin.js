const $ = (s, p=document) => p.querySelector(s);

function key() {
  return sessionStorage.getItem("adminKey") || "";
}

async function getJSON(url) {
  const r = await fetch(url, { headers: { "x-admin-key": key() } });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data?.message || "Request failed");
  return data;
}

function fmtDate(s) {
  try { return new Date(s).toLocaleString(); } catch { return s; }
}

function renderStats(stats) {
  const wrap = $("#stats");
  if (!wrap) return;
  wrap.innerHTML = `
    <div class="kpi"><div class="kpi-num">${stats.users}</div><div class="kpi-label">Users</div></div>
    <div class="kpi"><div class="kpi-num">${stats.demos}</div><div class="kpi-label">Démos</div></div>
    <div class="kpi"><div class="kpi-num">${stats.logins}</div><div class="kpi-label">Logins (total)</div></div>
    <div class="kpi"><div class="kpi-num">${stats.login_success}</div><div class="kpi-label">Logins OK</div></div>
  `;
}

function renderTable(type, rows) {
  const wrap = $("#tableWrap");
  if (!wrap) return;

  if (!rows.length) {
    wrap.innerHTML = `<p class="fine">Aucune donnée.</p>`;
    return;
  }

  if (type === "demos") {
    wrap.innerHTML = `
      <table class="table">
        <thead><tr>
          <th>ID</th><th>Nom</th><th>Email</th><th>Business</th><th>Message</th><th>Date</th>
        </tr></thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td>${r.id}</td>
              <td>${r.name}</td>
              <td>${r.email}</td>
              <td>${r.business}</td>
              <td>${(r.message || "").slice(0,120)}</td>
              <td>${fmtDate(r.created_at)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  if (type === "users") {
    wrap.innerHTML = `
      <table class="table">
        <thead><tr>
          <th>ID</th><th>Nom</th><th>Email</th><th>Role</th><th>Date</th>
        </tr></thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td>${r.id}</td>
              <td>${r.name || "-"}</td>
              <td>${r.email}</td>
              <td><span class="pill-mini">${r.role}</span></td>
              <td>${fmtDate(r.created_at)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  if (type === "logins") {
    wrap.innerHTML = `
      <table class="table">
        <thead><tr>
          <th>ID</th><th>User ID</th><th>Email</th><th>Status</th><th>IP</th><th>User-Agent</th><th>Date</th>
        </tr></thead>
        <tbody>
          ${rows.map(r => `
            <tr>
              <td>${r.id}</td>
              <td>${r.user_id ?? "-"}</td>
              <td>${r.email}</td>
              <td>
                <span class="pill-mini ${r.success ? "ok":"bad"}">
                  ${r.success ? "SUCCESS" : "FAILED"}
                </span>
              </td>
              <td>${r.ip || "-"}</td>
              <td>${(r.user_agent || "").slice(0,60)}</td>
              <td>${fmtDate(r.created_at)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }
}

async function loadAll() {
  const msg = $("#adminMsg");
  if (msg) msg.textContent = "";

  const stats = await getJSON("/api/admin/stats");
  renderStats(stats);

  // default tab
  const demos = await getJSON("/api/admin/demos");
  renderTable("demos", demos);
}

document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-tab]");
  if (!btn) return;

  try {
    const tab = btn.getAttribute("data-tab");
    const rows = await getJSON(`/api/admin/${tab}`);
    renderTable(tab, rows);
  } catch (err) {
    const msg = $("#adminMsg");
    if (msg) msg.textContent = `❌ ${err.message}`;
  }
});

document.getElementById("saveKey")?.addEventListener("click", async () => {
  const k = document.getElementById("adminKey")?.value?.trim();
  const msg = document.getElementById("adminMsg");
  if (!k) { if (msg) msg.textContent = "❌ Admin key requise."; return; }

  sessionStorage.setItem("adminKey", k);

  try {
    await loadAll();
    if (msg) msg.textContent = "✅ Données chargées.";
    // reveal show
    document.querySelectorAll(".reveal").forEach(el => el.classList.add("is-in"));
  } catch (err) {
    if (msg) msg.textContent = `❌ ${err.message}`;
  }
});
