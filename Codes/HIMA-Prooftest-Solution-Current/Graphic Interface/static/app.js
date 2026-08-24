let selectedDevice = null;
let selectedDeviceId = null;
let selectedProject = null;
let selectedResultsType = null;
let selectedReport = null;
let shownPopupKeys = new Set();
let lastGoodHealth = null;

const DEVICE_VIEW_KEY = "prooftest.deviceListView";
const THEME_KEY = "prooftest.theme";
const NO_DEVICE_TEXT = "(No device available)";
const NO_REPORT_TEXT = "(No report available)";
const PAGE_TITLES = {
  monitor: "Monitor",
  status: "Status",
  alarms: "Alarms",
  service: "Service",
};

function currentTheme() {
  const attr = document.documentElement.getAttribute("data-theme");
  return attr === "dark" ? "dark" : "light";
}

function applyTheme(theme) {
  const next = theme === "dark" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  try {
    localStorage.setItem(THEME_KEY, next);
  } catch (_e) {
    /* ignore */
  }
  const btn = document.getElementById("theme-toggle");
  if (btn) {
    btn.textContent = next === "dark" ? "Theme: Dark" : "Theme: Light";
    btn.setAttribute("aria-pressed", next === "dark" ? "true" : "false");
  }
}

function setupThemeToggle() {
  applyTheme(currentTheme());
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  btn.addEventListener("click", () => {
    applyTheme(currentTheme() === "dark" ? "light" : "dark");
  });
}

function showPage(pageId) {
  const id = PAGE_TITLES[pageId] ? pageId : "monitor";
  document.querySelectorAll(".page").forEach((el) => {
    const match = el.dataset.page === id;
    el.classList.toggle("active", match);
  });
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.page === id);
  });
  const crumb = document.getElementById("crumb-page");
  if (crumb) crumb.textContent = PAGE_TITLES[id] || id;
  document.body.classList.remove("sidebar-open");
}

function setupNavigation() {
  document.querySelectorAll(".nav-item[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => showPage(btn.dataset.page));
  });
  document.querySelectorAll("[data-goto]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      showPage(el.getAttribute("data-goto"));
    });
  });
  const toggle = document.getElementById("sidebar-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      document.body.classList.toggle("sidebar-open");
    });
  }
}

function silworxProjectNameFromHealth(data) {
  const st = data.service_state || {};
  const sil = data.silworx || {};
  const api = data.api_session || {};
  let name = String(
    data.attached_project_name ||
      api.project_name ||
      sil.silworx_project_name ||
      sil.project_name ||
      st.silworx_project_name ||
      st.project_name ||
      ""
  ).trim();
  if (name) return name;
  const raw = String(st.silworx_attached_projects || st.silworx_open_projects || "");
  for (const part of raw.split(";")) {
    const token = part.trim();
    if (!token) continue;
    if (token.includes(":")) return token.split(":").slice(1).join(":").trim();
    return token;
  }
  const open = Array.isArray(data.open_projects) ? data.open_projects : [];
  if (open.length && open[0]) {
    return String(open[0].project_name || open[0].project_file || "").trim();
  }
  return "";
}

function silworxProjectDeviceCount(data) {
  const raw = data.attached_project_devices ?? data.silworx_project_devices;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

function updateSummaryChips(data) {
  if (!data) return;
  const devices = document.getElementById("chip-devices");
  const opc = document.getElementById("chip-opc");
  const service = document.getElementById("chip-service");
  const silworx = document.getElementById("chip-silworx");
  const attachedOpc = data.attached_project_opc_devices;
  const attachedName = silworxProjectNameFromHealth(data);
  const projectDevices = silworxProjectDeviceCount(data);
  const silRunning = String(data.silworx_status || "").toLowerCase() === "running";
  const useProjectCount = Boolean(attachedName) && projectDevices != null;
  if (devices) {
    const n = useProjectCount ? projectDevices : Number(data.active_devices ?? NaN);
    devices.textContent = Number.isFinite(n) ? `Devices ${n}` : "Devices —";
    if (attachedName) {
      devices.title = `SILworX project: ${attachedName}`;
    } else {
      devices.title = "Open Status";
    }
  }
  if (opc) {
    const n = useProjectCount && attachedOpc != null ? Number(attachedOpc) : Number(data.opc_devices ?? 0);
    opc.textContent = `OPC ${Number.isFinite(n) ? n : "—"}`;
    opc.classList.toggle("warn", n === 0);
    opc.classList.remove("ok");
    opc.title = "Open Status";
  }
  if (service) {
    const text = data.starting
      ? "Starting"
      : data.stopping
        ? "Stopping"
        : data.engine_running
          ? "Running"
          : "Stopped";
    service.textContent = `Service ${text}`;
    service.classList.toggle("warn", !data.engine_running || data.stopping || data.starting);
    service.classList.remove("ok");
  }
  if (silworx) {
    silworx.textContent = silRunning ? "SILworX attached" : "SILworX off";
    silworx.classList.toggle("warn", !silRunning);
    silworx.classList.remove("ok");
    if (silRunning && attachedName) {
      silworx.title = `Attached to ${attachedName}`;
    } else {
      silworx.title = "Open Status";
    }
  }
}

function shortAlarmTitle(message) {
  const raw = String(message || "").trim();
  if (raw.length <= 120) return raw;
  const cut = raw.slice(0, 117);
  const sp = cut.lastIndexOf(" ");
  return `${sp > 40 ? cut.slice(0, sp) : cut}…`;
}

function currentDeviceView() {
  const selected = document.querySelector('input[name="device-list-view"]:checked');
  if (selected && selected.value) return selected.value;
  return localStorage.getItem(DEVICE_VIEW_KEY) || "all";
}

function setupDeviceViewOptions() {
  const saved = localStorage.getItem(DEVICE_VIEW_KEY) || "all";
  const radios = document.querySelectorAll('input[name="device-list-view"]');
  radios.forEach((radio) => {
    radio.checked = radio.value === saved;
    radio.addEventListener("change", () => {
      if (!radio.checked) return;
      localStorage.setItem(DEVICE_VIEW_KEY, radio.value);
      loadDevices();
    });
  });
}

const VENDOR_LOGOS = {
  "X-HART_ABB_FCB400_Results": "abb.png",
  "X-HART_Emerson_3051S_Results": "emerson.png",
  "X-HART_E+H_PMx7xB_Results": "eh.png",
  "X-HART_E+H_FTL5xB/6x_Results": "eh.png",
  "X-HART_E+H_FMR6xB_Results": "eh.png",
  "X-HART_E+H_Promass300/500_Results": "eh.png",
  "X-HART_SAMSON_Results": "samson.png",
  "X-HART_WIKA_T32_Results": "wika.png",
  "X-HART_WIKA_T38_Results": "wika.png",
};

function vendorLogo(resultsType) {
  const file = VENDOR_LOGOS[resultsType] || "hart.jpg";
  return UI.asset(`img/${file}`);
}

function formatResultsTypeLabel(resultsType) {
  const raw = String(resultsType || "").trim();
  if (!raw || raw === "unknown") return raw || "—";
  const prefix = "X-HART_";
  const suffix = "_Results";
  if (raw.startsWith(prefix) && raw.endsWith(suffix) && raw.length > prefix.length + suffix.length) {
    return raw.slice(prefix.length, raw.length - suffix.length);
  }
  return raw;
}

const listSearchState = {
  device: { index: -1 },
  report: { index: -1 },
};

function listSearchableItems(list) {
  return [...list.children].filter(
    (li) =>
      !li.classList.contains("list-placeholder") &&
      !li.classList.contains("list-empty") &&
      !li.classList.contains("filter-hidden")
  );
}

function deviceColumnFilters() {
  return {
    device: (document.getElementById("filter-col-device")?.value || "").trim().toLowerCase(),
    type: (document.getElementById("filter-col-type")?.value || "").trim().toLowerCase(),
    opc: (document.getElementById("filter-col-opc")?.value || "").trim().toLowerCase(),
    project: (document.getElementById("filter-col-project")?.value || "").trim().toLowerCase(),
    server: (document.getElementById("filter-col-server")?.value || "").trim().toLowerCase(),
  };
}

/** dataset keys: colDevice, colType, colOpc, colProject, colServer */
function rowMatchesColumnFiltersFixed(row, filters) {
  const map = {
    device: "colDevice",
    type: "colType",
    opc: "colOpc",
    project: "colProject",
    server: "colServer",
  };
  return Object.keys(map).every((key) => {
    const q = filters[key];
    if (!q) return true;
    return String(row.dataset[map[key]] || "").includes(q);
  });
}

function applyDeviceFilters(advance = false) {
  const list = document.getElementById("device-list");
  const input = document.getElementById("device-search");
  if (!list) return;

  const query = (input?.value || "").trim().toLowerCase();
  const filters = deviceColumnFilters();
  const hasColFilter = Object.values(filters).some(Boolean);
  const rows = [...list.children].filter(
    (li) => !li.classList.contains("list-placeholder") && !li.classList.contains("list-empty")
  );

  let visible = 0;
  rows.forEach((row) => {
    row.classList.remove("search-hit", "search-current", "filter-hidden");
    const colOk = rowMatchesColumnFiltersFixed(row, filters);
    const searchOk = !query || (row.dataset.searchText || "").includes(query);
    const show = colOk && searchOk;
    if (!show) {
      row.classList.add("filter-hidden");
    } else {
      visible += 1;
      if (query) row.classList.add("search-hit");
    }
  });

  const hint = document.getElementById("device-list-hint");
  if (hint && rows.length) {
    const view = currentDeviceView();
    const viewLabel = view === "opc" ? "OPC / Running" : "all devices";
    if (query || hasColFilter) {
      hint.textContent = `${visible} of ${rows.length} shown · ${viewLabel}`;
    } else {
      hint.textContent = `${rows.length} shown · ${viewLabel}`;
    }
  }

  updateDeviceFilterToggleState(filters);

  if (!query) {
    listSearchState.device.index = -1;
    return;
  }

  const matches = rows.filter((row) => !row.classList.contains("filter-hidden"));
  if (!matches.length) {
    listSearchState.device.index = -1;
    return;
  }

  let idx = listSearchState.device.index;
  if (!advance || idx < 0) {
    idx = 0;
  } else {
    idx = (idx + 1) % matches.length;
  }
  listSearchState.device.index = idx;
  const current = matches[idx];
  current.classList.add("search-current");
  current.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function applyListSearch(inputId, listId, stateKey, advance = false) {
  if (listId === "device-list") {
    applyDeviceFilters(advance);
    return;
  }
  const input = document.getElementById(inputId);
  const list = document.getElementById(listId);
  if (!input || !list) return;

  const query = input.value.trim().toLowerCase();
  const items = listSearchableItems(list);

  items.forEach((li) => li.classList.remove("search-hit", "search-current"));

  if (!query) {
    listSearchState[stateKey].index = -1;
    return;
  }

  const matches = items.filter((li) => (li.dataset.searchText || "").includes(query));
  matches.forEach((li) => li.classList.add("search-hit"));

  if (!matches.length) {
    listSearchState[stateKey].index = -1;
    return;
  }

  let idx = listSearchState[stateKey].index;
  if (!advance || idx < 0) {
    idx = 0;
  } else {
    idx = (idx + 1) % matches.length;
  }
  listSearchState[stateKey].index = idx;

  const current = matches[idx];
  current.classList.add("search-current");
  current.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function setDeviceFiltersVisible(visible) {
  const row = document.getElementById("device-filter-row");
  const btn = document.getElementById("btn-device-filters");
  if (!row || !btn) return;
  row.classList.toggle("hidden", !visible);
  btn.setAttribute("aria-expanded", visible ? "true" : "false");
  btn.classList.toggle("is-open", visible);
  if (visible) {
    const first = row.querySelector(".col-filter");
    if (first) window.requestAnimationFrame(() => first.focus());
  }
}

function updateDeviceFilterToggleState(filters) {
  const btn = document.getElementById("btn-device-filters");
  if (!btn) return;
  const active = filters || deviceColumnFilters();
  const hasFilter = Object.values(active).some(Boolean);
  btn.classList.toggle("is-active", hasFilter);
}

function clearAllDeviceColumnFilters() {
  document.querySelectorAll(".col-filter").forEach((input) => {
    input.value = "";
  });
  listSearchState.device.index = -1;
  applyDeviceFilters(false);
}

function setupDeviceColumnFilters() {
  const toggle = document.getElementById("btn-device-filters");
  if (toggle) {
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      const row = document.getElementById("device-filter-row");
      const open = row && !row.classList.contains("hidden");
      setDeviceFiltersVisible(!open);
    });
  }

  const clearAll = document.getElementById("btn-clear-device-filters");
  if (clearAll) {
    clearAll.addEventListener("click", (e) => {
      e.stopPropagation();
      clearAllDeviceColumnFilters();
    });
  }

  document.querySelectorAll(".col-filter").forEach((input) => {
    input.addEventListener("input", () => {
      listSearchState.device.index = -1;
      applyDeviceFilters(false);
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        applyDeviceFilters(true);
      }
      if (e.key === "Escape") {
        e.preventDefault();
        setDeviceFiltersVisible(false);
      }
      e.stopPropagation();
    });
  });

  updateDeviceFilterToggleState();
}

function setupListSearch(inputId, listId, stateKey) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.addEventListener("input", () => {
    listSearchState[stateKey].index = -1;
    applyListSearch(inputId, listId, stateKey, false);
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      applyListSearch(inputId, listId, stateKey, true);
    }
  });
}

function showListPlaceholder(listId, text) {
  const list = document.getElementById(listId);
  if (!list) return;
  if (list.tagName === "TBODY") {
    list.innerHTML = `<tr class="list-placeholder"><td colspan="7">${escapeHtml(text)}</td></tr>`;
    return;
  }
  list.innerHTML = `<li class="list-placeholder">${escapeHtml(text)}</li>`;
}

let engineWaitGeneration = 0;

function healthLooksComplete(data) {
  if (!data || typeof data !== "object") return false;
  // Incomplete lock-stub payloads omit decorated fields and wipe the panel to zeros.
  if (data.engine == null && data.opc_count == null && data.silworx_status == null) {
    const st = data.service_state || {};
    if (!Object.keys(st).length && Number(data.active_devices || 0) === 0) {
      return false;
    }
  }
  return true;
}

function catalogRefreshBusy(health) {
  const st = (health && health.service_state) || {};
  return String(st.catalog_refresh || "") === "1";
}

async function waitForCatalogRefreshIdle(timeoutMs = 180000) {
  const started = Date.now();
  const baselineDone = String(
    ((lastGoodHealth && lastGoodHealth.service_state) || {}).last_catalog_refresh || ""
  );
  let sawBusy = false;
  let idleStreak = 0;
  while (Date.now() - started < timeoutMs) {
    try {
      const health = await fetchJson("/api/health", { timeoutMs: 4000 });
      if (!healthLooksComplete(health)) {
        await new Promise((r) => setTimeout(r, 1000));
        continue;
      }
      lastGoodHealth = health;
      renderHealth(health);
      if (catalogRefreshBusy(health)) {
        sawBusy = true;
        idleStreak = 0;
        showServiceBanner("Refreshing device list — waiting for catalog…");
      } else {
        idleStreak += 1;
        const done = String((health.service_state || {}).last_catalog_refresh || "");
        const doneAdvanced = Boolean(done && done !== baselineDone);
        if ((sawBusy && idleStreak >= 1) || doneAdvanced || (idleStreak >= 2 && Date.now() - started > 1200)) {
          hideServiceBanner();
          return health;
        }
        // Catalog never went busy (or already finished) — do not leave the banner stuck.
        if (!sawBusy && idleStreak >= 3) {
          hideServiceBanner();
          return health;
        }
      }
    } catch (_err) {
      /* keep waiting */
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  showServiceBanner("Catalog refresh timed out — showing last known device list.");
  return lastGoodHealth;
}

async function updateServiceButtons(health) {
  const startBtn = document.getElementById("btn-start-service");
  const stopBtn = document.getElementById("btn-stop-service");
  const connectBtn = document.getElementById("btn-connect-silworx");
  const disconnectBtn = document.getElementById("btn-disconnect-silworx");
  const releaseBtn = document.getElementById("btn-release-silworx");
  const reintegrateBtn = document.getElementById("btn-reintegrate-silworx");
  if (!UI.isLive) {
    startBtn.disabled = true;
    stopBtn.disabled = true;
    if (connectBtn) connectBtn.disabled = true;
    if (disconnectBtn) disconnectBtn.disabled = true;
    if (releaseBtn) releaseBtn.disabled = true;
    if (reintegrateBtn) reintegrateBtn.disabled = true;
    return;
  }
  if (!health) {
    try {
      health = await fetchJson("/api/health", { timeoutMs: 4000 });
    } catch {
      startBtn.disabled = false;
      stopBtn.disabled = true;
      return;
    }
  }
  const starting = !!health.starting;
  const running = !!health.engine_running && !health.stopping && !starting;
  const released = String(health.silworx_integration || "").toLowerCase() === "released";
  startBtn.disabled = running || starting;
  stopBtn.disabled = !running || starting;
  const silRunning = String(health.silworx_status || "").toLowerCase() === "running";
  if (connectBtn) connectBtn.disabled = !running || silRunning || released;
  if (disconnectBtn) disconnectBtn.disabled = !running || !silRunning || released;
  if (releaseBtn) releaseBtn.disabled = !running || released;
  if (reintegrateBtn) reintegrateBtn.disabled = !running || !released;
}

async function waitForEngineRunning(timeoutMs = 180000) {
  const myGen = engineWaitGeneration;
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (myGen !== engineWaitGeneration) {
      return false;
    }
    try {
      const health = await fetchJson("/api/health", { timeoutMs: 4000 });
      await updateServiceButtons(health);
      if (health.engine_running && !health.starting) {
        hideServiceBanner();
        showServiceBanner("Engine running — syncing device list…");
        await waitForCatalogRefreshIdle(180000);
        await pollStatus();
        await loadDevices();
        await loadRunningTests();
        if (selectedDevice) await loadReports();
        hideServiceBanner();
        return true;
      }
      if (health.stopping) {
        showServiceBanner("Engine stopping — Start will continue when Stop finishes…");
      } else if (health.starting) {
        showServiceBanner("Engine starting — OPC/SILworX sync in progress…");
      }
    } catch (err) {
      if (myGen !== engineWaitGeneration) {
        return false;
      }
      showServiceBanner(`Waiting for engine: ${err.message}`);
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  if (myGen === engineWaitGeneration) {
    showServiceBanner("Engine start timed out. Check service_stderr.log or try Start again.");
  }
  return false;
}

function escapeHtml(text) {
  return String(text ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function showServiceBanner(message) {
  const el = document.getElementById("service-banner");
  el.textContent = message;
  el.classList.remove("hidden");
}

function hideServiceBanner() {
  document.getElementById("service-banner").classList.add("hidden");
}

function apiAuthToken() {
  if (!UI.isLive) return null;
  const params = new URLSearchParams(window.location.search);
  const fromUrl = params.get("token");
  if (fromUrl) {
    sessionStorage.setItem("prooftest_token", fromUrl);
    return fromUrl;
  }
  return sessionStorage.getItem("prooftest_token");
}

async function fetchJson(path, options) {
  const url = UI.api(path);
  if (!url) {
    throw new Error("offline");
  }
  const opts = options ? { ...options } : {};
  const timeoutMs = Number(opts.timeoutMs || 0);
  delete opts.timeoutMs;
  const token = apiAuthToken();
  if (token) {
    const headers = new Headers(opts.headers || {});
    headers.set("X-Prooftest-Token", token);
    opts.headers = headers;
  }
  let timer = null;
  if (timeoutMs > 0) {
    const ctrl = new AbortController();
    opts.signal = ctrl.signal;
    timer = setTimeout(() => ctrl.abort(), timeoutMs);
  }
  try {
    const res = await fetch(url, opts);
    if (res.status === 401) {
      throw new Error("Authentication required — open with ?token=... or set X-Prooftest-Token");
    }
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  } finally {
    if (timer) clearTimeout(timer);
  }
}

function apiErrorText(err) {
  const raw = String((err && err.message) || err || "");
  try {
    const parsed = JSON.parse(raw);
    if (parsed && parsed.detail) return String(parsed.detail);
  } catch (_ignore) {
    /* not JSON */
  }
  return raw;
}

function metricIcon(kind) {
  const stroke = "currentColor";
  const common = `fill="none" stroke="${stroke}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"`;
  if (kind === "list") {
    return `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><rect x="4" y="5" width="16" height="14" rx="2" ${common}/><path ${common} d="M8 10h8M8 14h5"/></svg>`;
  }
  if (kind === "shield-check") {
    return `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><path ${common} d="M12 3l7 3v6c0 4.5-3.2 7.4-7 9-3.8-1.6-7-4.5-7-9V6l7-3z"/><path ${common} d="M9 12l2 2 4-4"/></svg>`;
  }
  if (kind === "circle-check") {
    return `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><circle cx="12" cy="12" r="9" ${common}/><path ${common} d="M8 12l2.5 2.5L16 9"/></svg>`;
  }
  if (kind === "circle-warn") {
    return `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><circle cx="12" cy="12" r="9" ${common}/><path ${common} d="M12 8v5"/><circle cx="12" cy="16.5" r="0.9" fill="${stroke}"/></svg>`;
  }
  if (kind === "circle-x") {
    return `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><circle cx="12" cy="12" r="9" ${common}/><path ${common} d="M9 9l6 6M15 9l-6 6"/></svg>`;
  }
  if (kind === "plug") {
    // Connected: two barrel connectors joined
    return (
      `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">` +
      `<g transform="rotate(-35 12 12)">` +
      `<rect x="2.5" y="9.5" width="6.5" height="5" rx="1.2" ${common}/>` +
      `<rect x="8.5" y="10.2" width="3" height="3.6" rx="0.5" ${common}/>` +
      `<rect x="12.5" y="10.2" width="3" height="3.6" rx="0.5" ${common}/>` +
      `<rect x="15" y="9.5" width="6.5" height="5" rx="1.2" ${common}/>` +
      `</g>` +
      `</svg>`
    );
  }
  if (kind === "plug-off") {
    // Disconnected: plugs pulled apart with gap + arrows (clearly not joined)
    return (
      `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">` +
      `<g transform="rotate(-35 12 12)">` +
      `<rect x="1" y="9.5" width="6" height="5" rx="1.2" ${common}/>` +
      `<rect x="6.5" y="10.2" width="2.2" height="3.6" rx="0.5" ${common}/>` +
      `<rect x="15.3" y="10.2" width="2.2" height="3.6" rx="0.5" ${common}/>` +
      `<rect x="17" y="9.5" width="6" height="5" rx="1.2" ${common}/>` +
      `<path ${common} d="M10.2 12H8.8"/>` +
      `<path ${common} d="M13.8 12h1.4"/>` +
      `<path ${common} d="M9.4 10.8L8.2 12l1.2 1.2"/>` +
      `<path ${common} d="M14.6 10.8L15.8 12l-1.2 1.2"/>` +
      `</g>` +
      `</svg>`
    );
  }
  if (kind === "project-tree") {
    // Simple folder-tree: root + two child nodes
    return `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><path ${common} d="M6 6h6"/><path ${common} d="M9 6v12"/><path ${common} d="M9 12h7"/><path ${common} d="M9 18h7"/><rect x="4" y="4" width="5" height="4" rx="1" ${common}/><rect x="16" y="10" width="5" height="4" rx="1" ${common}/><rect x="16" y="16" width="5" height="4" rx="1" ${common}/></svg>`;
  }
  return `<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true"><circle cx="12" cy="12" r="8" ${common}/><path ${common} d="M12 8v5"/><circle cx="12" cy="16.5" r="0.9" fill="${stroke}"/></svg>`;
}

function parsePluginSessions(data) {
  // Empty array is authoritative (e.g. after Disconnect) — do not fall back to
  // stale silworx_plugin_monitor_state which can still say "up".
  if (Array.isArray(data.plugin_sessions)) {
    return data.plugin_sessions.map((s) => ({
      api_port: Number(s.api_port) || 0,
      plugin_port: Number(s.plugin_port) || 0,
      connected: s.connected === true,
      session_id: String(s.session_id || ""),
    }));
  }
  const toolAttached = String(data.silworx_status || "").toLowerCase() === "running";
  const registered = (data.plugin_session || {}).registered === true;
  if (!toolAttached && !registered) {
    return [];
  }
  const raw = String((data.service_state || {}).silworx_plugin_monitor_state || "");
  if (!raw.trim()) return [];
  return raw.split(";").map((part) => {
    const [ports, flag, sid] = String(part).trim().split(":");
    const [api, plugin] = String(ports || "").split("/");
    return {
      api_port: Number(api) || 0,
      plugin_port: Number(plugin) || 0,
      connected: String(flag || "").toLowerCase() === "up",
      session_id: sid && sid !== "-" ? sid : "",
    };
  }).filter((s) => s.plugin_port || s.api_port);
}

function pluginSessionIconsHtml(sessions, registered) {
  const on = registered === true;
  const title = on ? "Plugin session registered" : "Plugin session not registered";
  const cls = on ? "plugin-session-icon is-connected" : "plugin-session-icon is-disconnected";
  return (
    `<span class="health-metric-icon ${cls}" title="${escapeHtml(title)}" aria-hidden="true">` +
    metricIcon(on ? "plug" : "plug-off") +
    `</span>`
  );
}

function healthMetricTile(label, value, hint, tone, state, textValue, wide, iconKind, iconHtml) {
  const stateClass = state ? ` ${state}` : "";
  const toneClass = tone ? ` metric-${tone}` : " metric-neutral";
  const wideClass = wide ? " health-metric-span-2" : "";
  const multiline = Array.isArray(value);
  const valueClass =
    (textValue || multiline ? " health-metric-value is-text" : " health-metric-value") +
    (multiline ? " is-multiline" : "");
  const icon = iconHtml || `<span class="health-metric-icon">${metricIcon(iconKind || "info")}</span>`;
  let valueHtml;
  if (multiline) {
    const lines = value.length ? value : ["—"];
    valueHtml = lines
      .map((line) => `<span class="health-metric-line">${escapeHtml(line)}</span>`)
      .join("");
  } else {
    valueHtml = escapeHtml(value);
  }
  return (
    `<article class="health-metric${stateClass}${toneClass}${wideClass}">` +
    `<header class="health-metric-head">` +
    `<span class="health-metric-label">${escapeHtml(label)}</span>` +
    icon +
    `</header>` +
    `<p class="${valueClass.trim()}">${valueHtml}</p>` +
    (hint ? `<p class="health-metric-hint">${escapeHtml(hint)}</p>` : "") +
    `</article>`
  );
}

/** @deprecated use healthMetricTile */
function healthCard(label, value, state) {
  return healthMetricTile(label, value, "", state === "warn" ? "amber" : "neutral", state, !/^\d+$/.test(String(value)));
}

function opcServerTableRow(server) {
  const devices = Number.isFinite(Number(server.devices)) ? Number(server.devices) : 0;
  const tags = Number.isFinite(Number(server.tags)) ? Number(server.tags) : 0;
  let status = "Offline";
  let statusClass = "status-neutral";
  let live = "—";
  let liveClass = "status-neutral";

  if (server.connected) {
    status = "Connected";
    statusClass = "status-ok";
    if (server.browse_ok === false && !tags && !devices) {
      status = "Browse failed";
      statusClass = "status-bad";
    }
    if (server.live_ok === true) {
      live = "Good";
      liveClass = "status-ok";
    } else if (server.live_ok === false) {
      live = "Bad";
      liveClass = "status-bad";
    } else if (server.live_quality) {
      live = String(server.live_quality);
      liveClass = "status-neutral";
    }
  }

  return (
    `<tr>` +
    `<td class="opc-col-name">${escapeHtml(server.name || "—")}</td>` +
    `<td class="opc-col-status"><span class="status-pill ${statusClass}">${escapeHtml(status)}</span></td>` +
    `<td class="opc-col-num">${devices}</td>` +
    `<td class="opc-col-status"><span class="status-pill ${liveClass}">${escapeHtml(live)}</span></td>` +
    `</tr>`
  );
}

function renderOpcServerTable(servers, emptyMessage) {
  const opcList = document.getElementById("opc-detail-list");
  if (!opcList) return;
  if (!servers.length) {
    const msg = emptyMessage || "No X-OPC servers detected on this host.";
    opcList.innerHTML = `<tr><td colspan="4" class="opc-server-empty">${escapeHtml(msg)}</td></tr>`;
    return;
  }
  opcList.innerHTML = servers.map((s) => opcServerTableRow(s)).join("");
}

function renderHealth(data) {
  if (!healthLooksComplete(data)) {
    if (lastGoodHealth) {
      data = lastGoodHealth;
    } else {
      return;
    }
  } else {
    lastGoodHealth = data;
  }
  const grid = document.getElementById("health-grid");
  const badge = document.getElementById("health-status-badge");

  const sil = data.silworx || {};
  const st = data.service_state || {};
  const deviceSource = String(data.device_list_source || st.device_list_source || "").toLowerCase();
  const apiSession = data.api_session || {};
  const apiConnected = deviceSource === "api" || deviceSource === "api+opc";
  const apiProject =
    apiSession.project_name ||
    (apiConnected ? sil.silworx_project_name || sil.project_name || "" : "");
  const silworxStatus = String(data.silworx_status || "").toLowerCase();
  const silworxReleased =
    String(data.silworx_integration || "").toLowerCase() === "released";
  const attachedProjectDevices = silworxProjectDeviceCount(data);
  const attachedProjectOpc = data.attached_project_opc_devices;
  const attachedProjectName = silworxProjectNameFromHealth(data);
  const hasProjectCounts =
    attachedProjectName &&
    attachedProjectDevices != null &&
    Number.isFinite(Number(attachedProjectDevices));
  const openProjects = Array.isArray(data.open_projects) ? data.open_projects : [];
  const silworxVersions = [];
  const seenVersions = new Set();
  for (const p of openProjects) {
    const ver = String((p && p.silworx_version) || "").trim();
    if (ver && !seenVersions.has(ver)) {
      seenVersions.add(ver);
      silworxVersions.push(ver);
    }
  }
  const fallbackVersion = String(
    sil.silworx_version || st.silworx_version || ""
  ).trim();
  if (!silworxVersions.length && fallbackVersion) {
    silworxVersions.push(fallbackVersion);
  }
  const silLines = [];
  if (silworxReleased) {
    silLines.push("Released for uninstall");
  } else if (silworxVersions.length) {
    silLines.push(...silworxVersions);
  } else {
    silLines.push("—");
  }
  const silState = silworxReleased || !silworxVersions.length ? "warn" : "";
  const openFromState = String(st.silworx_open_projects || "")
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean);
  const openNames = openProjects.length
    ? openProjects.map((p) => p.project_name || p.project_file || p.session_id).filter(Boolean)
    : openFromState;
  const openLines = openNames.length
    ? openNames
    : [sil.project_name || sil.silworx_project_name || "—"].filter(Boolean);
  const attachedMap = data.attached_projects || {};
  const attachedLines = Object.keys(attachedMap)
    .map((port) => `${attachedMap[port]} (${port})`)
    .filter(Boolean);

  const queueState = (data.queue_depth || 0) > 10 ? "warn" : "";
  const pluginSessions = parsePluginSessions(data);
  const pluginConnectedCount = pluginSessions.filter((s) => s.connected).length;
  const pluginInfo = data.plugin_session || {};
  const pluginName = String(
    pluginInfo.name || st.silworx_plugin_name || "prooftest_session_plugin"
  ).trim();
  const pluginRegistered =
    pluginConnectedCount > 0 ||
    pluginInfo.registered === true ||
    pluginInfo.connected === true;
  const pluginLines = [];
  if (pluginRegistered || pluginSessions.length) {
    pluginLines.push(`${pluginName}:`);
    const rows = pluginSessions.length
      ? pluginSessions
      : [{ api_port: 0, plugin_port: 0, connected: false, session_id: "" }];
    for (const s of rows) {
      const ports = s.plugin_port ? `${s.api_port}/${s.plugin_port}` : "—";
      pluginLines.push(`– ${ports}`);
    }
  } else {
    pluginLines.push("not registered");
  }
  const pluginState = pluginRegistered && pluginConnectedCount > 0 ? "" : "warn";
  const serviceState = data.starting
    ? "Starting"
    : data.stopping
      ? "Stopping"
      : data.engine_running
        ? "Running"
        : "Stopped";
  const serviceCls =
    data.starting || data.stopping || !data.engine_running ? "warn" : "";
  const sourceRaw = String(data.device_list_source || st.device_list_source || "").toLowerCase();
  const sourceText = sourceRaw === "api+opc"
    ? "API + OPC"
    : sourceRaw === "api"
      ? "API"
      : sourceRaw === "opc_fallback" || sourceRaw === "opc"
        ? "OPC"
        : data.device_list_source
          ? String(data.device_list_source)
          : "unified";

  const opcActive = Number(data.opc_devices ?? 0);
  const allDevicesValue = hasProjectCounts
    ? String(Number(attachedProjectDevices))
    : String(data.active_devices ?? 0);
  const opcDevicesValue = hasProjectCounts && attachedProjectOpc != null
    ? String(Number(attachedProjectOpc))
    : String(opcActive);
  const opcCountState =
    (hasProjectCounts ? Number(attachedProjectOpc) : opcActive) > 0 ? "" : "warn";
  const opcTone = opcCountState ? "amber" : "green";
  const serviceTone = serviceCls ? "amber" : "green";
  const silTone = silworxReleased ? "red" : silState ? "amber" : "blue";
  const pluginTone =
    pluginConnectedCount >= 2 ? "green" : pluginConnectedCount === 1 ? "amber" : "red";
  const queueTone = queueState ? "amber" : "neutral";
  const attachedTone = attachedLines.length ? "blue" : "amber";

  const serviceIcon = serviceCls ? "circle-warn" : "circle-check";
  const pluginIcons = pluginSessionIconsHtml(pluginSessions, pluginRegistered);
  const silIcon = silworxReleased ? "circle-x" : silworxVersions.length ? "circle-check" : "circle-warn";
  const silHint = silworxReleased
    ? "Operator released SILworX for uninstall — use Re-integrate after reinstall"
    : "SILworX version(s) the tool detects";

  grid.innerHTML = [
    healthMetricTile(
      "ALL DEVICES",
      allDevicesValue,
      attachedProjectName ? `Project: ${attachedProjectName}` : "SILworX project devices in catalog",
      "blue",
      "",
      false,
      false,
      "list"
    ),
    healthMetricTile(
      "OPC ACTIVE DEVICES",
      opcDevicesValue,
      "Devices with live OPC path",
      opcTone,
      opcCountState,
      false,
      false,
      "list"
    ),
    healthMetricTile("Service", serviceState, "Prooftest engine process", serviceTone, serviceCls, true, false, serviceIcon),
    healthMetricTile("Database", data.database || "unknown", "Annex catalog store", "neutral", "", true, false, "info"),
    healthMetricTile("Device list", sourceText, "Discovery source for device table", "neutral", "", true, false, "info"),
    healthMetricTile("SILworX", silLines, silHint, silTone, silState, true, false, silIcon),
    healthMetricTile(
      "Plugin sessions",
      pluginLines,
      "SILworX API plugin WebSocket per instance",
      pluginTone,
      pluginState,
      true,
      false,
      "plug",
      pluginIcons
    ),
    healthMetricTile("Queue depth", String(data.queue_depth ?? 0), "Pending report jobs", queueTone, queueState, false, false, "info"),
    healthMetricTile("Open SILworX projects", openLines, "Projects open in SILworX", "neutral", "", true, true, "info"),
    healthMetricTile(
      "API-scanned projects",
      attachedLines.length ? attachedLines : ["—"],
      "Attached API scan targets",
      attachedTone,
      attachedLines.length ? "" : "warn",
      true,
      true,
      "project-tree"
    ),
  ].join("");

  renderOpcServerTable(data.opc_servers || []);

  const err = data.last_error;
  const errBox = document.getElementById("last-error-banner");
  if (errBox) {
    if (err && (err.step || err.message)) {
      errBox.classList.remove("hidden");
      errBox.textContent = `${err.step || "?"} · ${err.action || ""} · ${err.message || ""}`.replace(/\s+·\s+$/, "");
    } else {
      errBox.classList.add("hidden");
      errBox.textContent = "";
    }
  }
  // Only flag attention when a connected/known ProofTest server is unhealthy or service is stopping.
  const proofServers = (data.opc_servers || []).filter(
    (s) => /prooftest|proof.?tes|x-opc|x_ots|x-ots/i.test(String(s.name || ""))
  );
  const watch = proofServers.length ? proofServers : data.opc_servers || [];
  const hasIssue =
    (watch.length > 0 && watch.every((s) => !s.connected)) ||
    data.stopping ||
    Boolean(data.last_error);
  if (badge) {
    badge.textContent = hasIssue ? "attention" : "healthy";
    badge.className = hasIssue
      ? "panel-badge panel-badge-warn status-summary-badge"
      : "panel-badge panel-badge-ok status-summary-badge";
  }
  updateSummaryChips(data);
}

function renderOfflineHealth() {
  const grid = document.getElementById("health-grid");
  grid.innerHTML = [
    healthMetricTile("Mode", "Offline preview", "UI loaded without live service", "amber", "warn", true, false, "circle-warn"),
    healthMetricTile("Database", "—", "Annex catalog store", "neutral", "", true, false, "info"),
    healthMetricTile("Service", "not connected", "Start the Prooftest engine", "red", "warn", true, false, "circle-x"),
  ].join("");
  renderOpcServerTable(
    [],
    "Start the Prooftest service and open http://127.0.0.1:8080/ for live data."
  );
  document.getElementById("health-status-badge").className = "panel-badge panel-badge-warn status-summary-badge";
}

function renderAlarms(payload) {
  const alarms = Array.isArray(payload) ? payload : payload.alarms || [];
  const panel = document.getElementById("alarms");
  const list = document.getElementById("alarm-list");
  const badge = document.getElementById("alarm-count-badge");
  const navBadge = document.getElementById("nav-alarm-badge");
  const activeCount = alarms.filter((a) => a.active).length;

  badge.textContent = `${activeCount} active`;
  panel.classList.toggle("has-alarms", activeCount > 0);
  if (navBadge) {
    if (activeCount > 0) {
      navBadge.hidden = false;
      navBadge.textContent = String(activeCount);
    } else {
      navBadge.hidden = true;
      navBadge.textContent = "0";
    }
  }

  if (!alarms.length) {
    list.innerHTML = '<p class="alarm-empty">No alarms — service operating normally.</p>';
    return;
  }

  list.innerHTML = alarms
    .slice(0, 12)
    .map((a) => {
      const device = a.device_tag ? ` · Device: ${escapeHtml(a.device_tag)}` : "";
      const time = a.timestamp ? escapeHtml(String(a.timestamp)) : "";
      const hint = a.solution_hint
        ? `<p class="alarm-hint">${escapeHtml(a.solution_hint)}</p>`
        : "";
      const life = a.active
        ? { cls: "active", text: "still active" }
        : { cls: "cleared", text: "no longer exists" };
      const ackBadge = a.acknowledged
        ? '<span class="alarm-status acked">acknowledged</span>'
        : "";
      const ackBtn =
        a.id && !a.acknowledged
          ? `<button type="button" class="btn-ack" data-alarm-id="${escapeHtml(String(a.id))}">Acknowledge</button>`
          : "";
      const fullMsg = String(a.message || "");
      const shortMsg = shortAlarmTitle(fullMsg);
      const needsExpand = fullMsg.length > 120;
      const msgHtml = needsExpand
        ? `<p class="alarm-msg-short">${escapeHtml(shortMsg)}</p>
           <details class="alarm-details">
             <summary>Show full details</summary>
             <pre>${escapeHtml(fullMsg)}</pre>
           </details>`
        : `<p class="alarm-msg">${escapeHtml(fullMsg)}</p>`;
      return `<article class="alarm-item${a.acknowledged ? " acked" : ""}">
        <span class="alarm-step">${escapeHtml(a.step || "?")}</span>
        <div class="alarm-body">
          ${msgHtml}
          <p class="alarm-meta"><span class="alarm-status ${life.cls}">${life.text}</span>${ackBadge}${escapeHtml(a.severity || "Error")}${device} · ${time}</p>
          ${hint}
          ${ackBtn}
        </div>
      </article>`;
    })
    .join("");

  list.querySelectorAll(".btn-ack").forEach((btn) => {
    btn.onclick = async () => {
      const id = btn.getAttribute("data-alarm-id");
      if (!id || !UI.isLive) return;
      try {
        await fetchJson(`/api/alarms/${encodeURIComponent(id)}/ack`, { method: "POST" });
        await pollStatus();
      } catch (err) {
        showServiceBanner(`Acknowledge failed: ${apiErrorText(err)}`);
      }
    };
  });
}

function showPopup(popup) {
  const key = popup.step + "|" + popup.message;
  if (shownPopupKeys.has(key)) return;
  shownPopupKeys.add(key);
  document.getElementById("modal-step").textContent = `Step ${popup.step || "?"}`;
  document.getElementById("modal-title").textContent = popup.title || popup.step || "Error";
  document.getElementById("modal-message").textContent = popup.message || "";
  document.getElementById("modal-solution").textContent = popup.solution || "See specification troubleshooting catalog.";
  document.getElementById("modal").classList.remove("hidden");
}

function deviceTestCell(device) {
  if (!device || !device.test_in_progress) {
    return '<td class="device-test-cell" aria-label="No prooftest running"></td>';
  }
  const started = device.test_started_at || device.started_at;
  const title = started
    ? `Prooftest running · started ${formatStartedAt(started)}`
    : "Prooftest running";
  return (
    `<td class="device-test-cell">` +
    `<span class="device-test-running" title="${escapeHtml(title)}">` +
    `<span class="device-test-dot" aria-hidden="true"></span>Running</span></td>`
  );
}

async function loadDevices() {
  const list = document.getElementById("device-list");
  const previousScroll = list.scrollTop;

  let devices;
  try {
    const view = currentDeviceView();
    devices = await fetchJson(`/api/devices?view=${encodeURIComponent(view)}`, { timeoutMs: 4000 });
  } catch (err) {
    if (err.message === "offline") {
      showListPlaceholder("device-list", NO_DEVICE_TEXT);
      return;
    }
    list.innerHTML = `<li class="list-empty">Failed to load devices: ${escapeHtml(err.message)}</li>`;
    return;
  }

  if (!devices.length) {
    showListPlaceholder("device-list", NO_DEVICE_TEXT);
    const hintEmpty = document.getElementById("device-list-hint");
    if (hintEmpty) hintEmpty.textContent = "Device Prooftest Result List · 0 devices";
    selectedDevice = null;
    selectedDeviceId = null;
    selectedProject = null;
    selectedResultsType = null;
    updateSelectedLabel();
    showListPlaceholder("report-list", NO_REPORT_TEXT);
    return;
  }

  // Sort: Device_TAG, then Project, then OPC server (matches domain sort_device_dicts).
  devices.sort((a, b) => {
    const tag = String(a.device_tag || "").localeCompare(String(b.device_tag || ""), undefined, { sensitivity: "base" });
    if (tag !== 0) return tag;
    const proj = String(a.project || a.silworx_project || "").localeCompare(
      String(b.project || b.silworx_project || ""),
      undefined,
      { sensitivity: "base" }
    );
    if (proj !== 0) return proj;
    return String(a.opc_server || "").localeCompare(String(b.opc_server || ""), undefined, { sensitivity: "base" });
  });

  const hint = document.getElementById("device-list-hint");
  const view = currentDeviceView();
  const viewLabel = view === "opc" ? "OPC / Running" : "all devices";
  if (hint) hint.textContent = `${devices.length} shown · ${viewLabel}`;

  list.innerHTML = "";
  let selectionStillPresent = false;
  devices.forEach((d, idx) => {
    const tr = document.createElement("tr");
    const id = d.device_id || `${d.project || ""}|${d.device_tag}`;
    const resultsType = d.results_type && String(d.results_type).trim() ? d.results_type : "unknown";
    const typeLabel = formatResultsTypeLabel(resultsType);
    const project = d.project || d.silworx_project || "";
    const opcServer = d.opc_server || "";
    const onOpc = Boolean(d.present_on_opc);
    const opcLabel = onOpc ? "opc" : "not on opc";
    tr.dataset.searchText = `${d.device_tag} ${typeLabel} ${resultsType} ${project} ${opcServer} ${opcLabel}`.toLowerCase();
    tr.dataset.colDevice = String(d.device_tag || "").toLowerCase();
    tr.dataset.colType = `${typeLabel} ${resultsType}`.toLowerCase();
    tr.dataset.colOpc = opcLabel;
    tr.dataset.colProject = String(project).toLowerCase();
    tr.dataset.colServer = String(opcServer).toLowerCase();
    tr.dataset.deviceId = id;
    if (id === selectedDeviceId || (!selectedDeviceId && d.device_tag === selectedDevice)) {
      tr.classList.add("selected");
      selectionStillPresent = true;
      selectedDevice = d.device_tag;
      selectedDeviceId = id;
      selectedProject = project;
      selectedResultsType = d.results_type;
    }
    if (d.test_in_progress) {
      tr.classList.add("device-row-running");
    }
    const status = onOpc
      ? '<span class="device-status on-opc">OPC</span>'
      : '<span class="device-status off-opc">not on OPC</span>';
    tr.innerHTML = `
      <td class="device-row-corner"><span class="row-index" title="Row ${idx + 1}">${idx + 1}</span></td>
      <td class="device-tag-cell">
        <span class="device-logo-wrap" aria-hidden="true">
          <img class="device-logo" src="${vendorLogo(d.results_type)}" alt=""/>
        </span>
        <span class="device-tag">${escapeHtml(d.device_tag)}</span>
      </td>
      <td title="${escapeHtml(resultsType)}">${escapeHtml(typeLabel)}</td>
      <td>${status}</td>
      <td>${escapeHtml(project)}</td>
      <td>${escapeHtml(opcServer)}</td>
      ${deviceTestCell(d)}`;
    tr.onclick = () => {
      selectedDevice = d.device_tag;
      selectedDeviceId = id;
      selectedProject = project;
      selectedResultsType = d.results_type;
      [...list.children].forEach((c) => c.classList.remove("selected"));
      tr.classList.add("selected");
      updateSelectedLabel();
      loadReports();
    };
    list.appendChild(tr);
  });
  if (selectedDeviceId || selectedDevice) {
    if (!selectionStillPresent) {
      selectedDevice = null;
      selectedDeviceId = null;
      selectedProject = null;
      selectedResultsType = null;
      selectedReport = null;
      showListPlaceholder("report-list", NO_REPORT_TEXT);
      const openBtn = document.getElementById("btn-open");
      if (openBtn) openBtn.disabled = true;
    }
  }
  if (!selectedDeviceId && !selectedDevice && devices.length) {
    const first = devices[0];
    const firstId = first.device_id || `${first.project || ""}|${first.device_tag}`;
    selectedDevice = first.device_tag;
    selectedDeviceId = firstId;
    selectedProject = first.project || first.silworx_project || "";
    selectedResultsType = first.results_type;
    const firstRow = [...list.querySelectorAll("tr")].find((r) => r.dataset.deviceId === firstId);
    if (firstRow) firstRow.classList.add("selected");
    loadReports();
  }
  list.scrollTop = previousScroll;
  updateSelectedLabel();
  applyDeviceFilters(false);
}

function updateSelectedLabel() {
  const label = document.getElementById("selected-device-label");
  if (!label) return;
  if (!selectedDevice) {
    label.textContent = "(No report selected)";
    return;
  }
  label.textContent = `Selected: ${selectedDevice}${selectedProject ? ` · ${selectedProject}` : ""}${selectedResultsType ? ` (${formatResultsTypeLabel(selectedResultsType)})` : ""}`;
}

function formatStartedAt(value) {
  if (!value) return "start time unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

function renderRunningTests(tests) {
  const list = document.getElementById("running-tests-list");
  const badge = document.getElementById("running-tests-count");
  const rows = Array.isArray(tests) ? tests : [];
  if (badge) badge.textContent = `${rows.length} active`;
  if (!list) return;
  if (!rows.length) {
    list.innerHTML = '<li class="list-placeholder">(No test in progress)</li>';
    return;
  }
  list.innerHTML = rows
    .map(
      (t) =>
        `<li><span class="running-device">${escapeHtml(t.device_tag || "?")}</span>` +
        `<span class="running-started">Started ${escapeHtml(formatStartedAt(t.started_at))}</span></li>`
    )
    .join("");
}

async function loadRunningTests() {
  if (!UI.isLive) {
    renderRunningTests([]);
    return;
  }
  try {
    const tests = await fetchJson("/api/running-tests", { timeoutMs: 4000 });
    renderRunningTests(tests);
  } catch (_err) {
    renderRunningTests([]);
  }
}

function historyRowHtml(t) {
  const outcome = String(t.outcome || "unknown").toLowerCase();
  const result = String(t.result || "").toLowerCase();
  const resultFlag = result
    ? `<span class="history-flag ${escapeHtml(result)}">${escapeHtml(result)}</span>`
    : "";
  const finished =
    outcome === "running"
      ? "in progress"
      : t.finished_at
        ? formatStartedAt(t.finished_at)
        : "finish time unknown";
  return `<li>
    <span class="history-device">${escapeHtml(t.device_tag || "?")}</span>
    <span class="history-flags">
      <span class="history-flag ${escapeHtml(outcome)}">${escapeHtml(outcome)}</span>
      ${resultFlag}
    </span>
    <span class="history-times">Started ${escapeHtml(formatStartedAt(t.started_at))} · Finished ${escapeHtml(finished)}</span>
  </li>`;
}

function renderHistoryModal(rows) {
  const list = document.getElementById("history-modal-list");
  if (!list) return;
  const tests = Array.isArray(rows) ? rows : [];
  if (!tests.length) {
    list.innerHTML = '<li class="list-placeholder">(No prooftest history)</li>';
    return;
  }
  list.innerHTML = tests.map(historyRowHtml).join("");
}

async function openHistoryModal() {
  const modal = document.getElementById("history-modal");
  if (!modal) return;
  renderHistoryModal([]);
  modal.classList.remove("hidden");
  if (!UI.isLive) {
    renderHistoryModal([]);
    return;
  }
  try {
    const rows = await fetchJson("/api/test-history", { timeoutMs: 4000 });
    renderHistoryModal(rows);
  } catch (err) {
    const list = document.getElementById("history-modal-list");
    if (list) {
      list.innerHTML = `<li class="list-placeholder">Failed to load history: ${escapeHtml(err.message)}</li>`;
    }
  }
}

function closeHistoryModal() {
  const modal = document.getElementById("history-modal");
  if (modal) modal.classList.add("hidden");
}

function reportBadge(name) {
  const lower = (name || "").toLowerCase();
  if (lower.endsWith(".pdf") || lower.endsWith(".pdf.html")) return { text: "PDF", cls: "pdf" };
  if (lower.endsWith(".html")) return { text: "HTML", cls: "html" };
  return { text: "FILE", cls: "html" };
}

async function loadReports() {
  selectedReport = null;
  document.getElementById("btn-open").disabled = true;
  const list = document.getElementById("report-list");

  if (!selectedDevice) {
    showListPlaceholder("report-list", NO_REPORT_TEXT);
    return;
  }

  list.innerHTML = `<li class="list-placeholder">${escapeHtml(NO_REPORT_TEXT)}</li>`;

  let url = `/api/reports?device=${encodeURIComponent(selectedDevice)}`;
  if (selectedResultsType) {
    url += `&results_type=${encodeURIComponent(selectedResultsType)}`;
  }
  if (selectedProject) {
    url += `&project=${encodeURIComponent(selectedProject)}`;
  }
  if (selectedDeviceId) {
    url += `&device_id=${encodeURIComponent(selectedDeviceId)}`;
  }

  let reports;
  try {
    reports = await fetchJson(url, { timeoutMs: 8000 });
  } catch (err) {
    list.innerHTML = `<li class="list-empty">Failed to load reports: ${escapeHtml(err.message)}</li>`;
    return;
  }

  if (!reports.length) {
    showListPlaceholder("report-list", NO_REPORT_TEXT);
    return;
  }

  list.innerHTML = "";
  reports.forEach((r) => {
    const li = document.createElement("li");
    li.setAttribute("role", "option");
    li.dataset.searchText = `${r.name} ${r.modified || ""}`.toLowerCase();
    const badge = reportBadge(r.name);
    li.innerHTML = `
      <span class="report-badge ${badge.cls}">${badge.text}</span>
      <div class="report-info">
        <span class="report-name">${escapeHtml(r.name)}</span>
        <span class="report-date">${escapeHtml(r.modified || "")}</span>
      </div>`;
    li.onclick = () => {
      selectedReport = r.path;
      [...list.children].forEach((c) => c.classList.remove("selected"));
      li.classList.add("selected");
      document.getElementById("btn-open").disabled = false;
    };
    list.appendChild(li);
  });
  applyListSearch("report-search", "report-list", "report", false);
}

async function refreshAll(manual = false) {
  if (!UI.isLive) {
    showServiceBanner(
      "Offline preview — images and layout only. Start the service and open http://127.0.0.1:8080/ for live devices, reports, and alarms."
    );
    renderOfflineHealth();
    renderAlarms([]);
    renderRunningTests([]);
    await loadDevices();
    return;
  }

  if (manual) shownPopupKeys.clear();
  try {
    const data = await fetchJson("/api/refresh", { method: "POST", timeoutMs: 8000 });
    (data.popups || []).forEach(showPopup);
    if (data.status === "refresh_started") {
      showServiceBanner("Refreshing device list…");
      await waitForCatalogRefreshIdle(180000);
    }
    await pollStatus();
    await loadDevices();
    await loadRunningTests();
    if (selectedDevice) await loadReports();
    hideServiceBanner();
  } catch (err) {
    showServiceBanner(`Service error: ${err.message}`);
  }
}

let pollFailStreak = 0;
let pollInFlight = false;
let lastCatalogBusy = false;

async function pollStatus() {
  if (!UI.isLive || pollInFlight) return;
  pollInFlight = true;
  let health = null;
  try {
    health = await fetchJson("/api/health", { timeoutMs: 4000 });
    renderHealth(health);
    pollFailStreak = 0;
    const busy = catalogRefreshBusy(health);
    if (!busy) {
      hideServiceBanner();
    } else {
      showServiceBanner("Refreshing device list — waiting for catalog…");
    }
    // Reload devices as soon as a catalog refresh finishes (don't wait another 8s).
    if (lastCatalogBusy && !busy) {
      try {
        await loadDevices();
      } catch (_ignore) {
        /* keep UI alive */
      }
    }
    lastCatalogBusy = busy;
  } catch (err) {
    pollFailStreak += 1;
    if (pollFailStreak >= 2) {
      showServiceBanner(`Cannot reach service API: ${err.message}`);
    }
    try {
      await updateServiceButtons();
    } catch (_ignore) {
      /* keep UI alive */
    }
    pollInFlight = false;
    return;
  }
  try {
    const alarmData = await fetchJson("/api/alarms", { timeoutMs: 4000 });
    renderAlarms(alarmData);
    (alarmData.popups || []).forEach(showPopup);
  } catch (err) {
    renderAlarms([]);
    if (pollFailStreak >= 2) {
      showServiceBanner(`Alarms API unavailable: ${err.message}`);
    }
  }
  try {
    await loadRunningTests();
  } catch (_ignore) {
    /* keep UI alive */
  }
  try {
    await loadDevices();
  } catch (_ignore) {
    /* keep UI alive */
  }
  try {
    await updateServiceButtons(health);
  } catch (_ignore) {
    /* keep UI alive */
  }
  pollInFlight = false;
}

document.getElementById("btn-refresh").onclick = () => refreshAll(true);
const connectSil = document.getElementById("btn-connect-silworx");
if (connectSil) {
  connectSil.onclick = async () => {
    try {
      const result = await fetchJson("/api/silworx/connect", { method: "POST", timeoutMs: 60000 });
      showServiceBanner(`SILworX: ${result.silworx || result.status || "updated"}`);
      await refreshAll(false);
    } catch (err) {
      showServiceBanner(`Connect to SILworX failed: ${err.message}`);
    }
  };
}
const disconnectSil = document.getElementById("btn-disconnect-silworx");
if (disconnectSil) {
  disconnectSil.onclick = async () => {
    try {
      const result = await fetchJson("/api/silworx/disconnect", { method: "POST", timeoutMs: 60000 });
      showServiceBanner(`SILworX: ${result.silworx || result.status || "not connected"}`);
      await refreshAll(false);
    } catch (err) {
      showServiceBanner(`Disconnect SILworX failed: ${err.message}`);
    }
  };
}
const releaseSil = document.getElementById("btn-release-silworx");
if (releaseSil) {
  releaseSil.onclick = async () => {
    if (
      !confirm(
        "Release SILworX from this tool?\n\n" +
          "This detaches the API/plugin and may stop leftover c3.exe processes so SILworX can be uninstalled.\n" +
          "The report tool keeps running on OPC only.\n\n" +
          "Use Re-integrate SILworX after SILworX is reinstalled."
      )
    ) {
      return;
    }
    try {
      const result = await fetchJson("/api/silworx/release", { method: "POST", timeoutMs: 120000 });
      showServiceBanner(
        `SILworX released for uninstall (${result.status || "released"}). Tool continues on OPC.`
      );
      await refreshAll(false);
    } catch (err) {
      showServiceBanner(`Release SILworX failed: ${err.message}`);
    }
  };
}
const reintegrateSil = document.getElementById("btn-reintegrate-silworx");
if (reintegrateSil) {
  reintegrateSil.onclick = async () => {
    try {
      const result = await fetchJson("/api/silworx/reintegrate", {
        method: "POST",
        timeoutMs: 120000,
      });
      showServiceBanner(
        `SILworX re-integrated (${result.silworx || result.status || "integrated"}).`
      );
      await refreshAll(false);
    } catch (err) {
      showServiceBanner(`Re-integrate SILworX failed: ${err.message}`);
    }
  };
}
document.getElementById("btn-start-service").onclick = async () => {
  if (!UI.isLive) return;
  const startBtn = document.getElementById("btn-start-service");
  const stopBtn = document.getElementById("btn-stop-service");
  engineWaitGeneration += 1;
  startBtn.disabled = true;
  stopBtn.disabled = true;
  try {
    const result = await fetchJson("/api/start", { method: "POST" });
    if (result.status === "already_running") {
      hideServiceBanner();
      await updateServiceButtons();
      return;
    }
    showServiceBanner("Engine starting — OPC/SILworX sync may take up to ~2 minutes.");
    const ok = await waitForEngineRunning();
    if (!ok) {
      await updateServiceButtons();
    }
  } catch (err) {
    showServiceBanner(`Start failed: ${err.message}`);
    await updateServiceButtons();
  }
};
async function waitForEngineStopped(timeoutMs = 45000) {
  const myGen = engineWaitGeneration;
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (myGen !== engineWaitGeneration) {
      return false;
    }
    try {
      const health = await fetchJson("/api/health", { timeoutMs: 4000 });
      await updateServiceButtons(health);
      await pollStatus();
      if (!health.stopping && !health.engine_running && !health.starting) {
        return true;
      }
      if (health.stopping) {
        showServiceBanner("Engine stopping — waiting for OPC/SILworX cleanup…");
      }
    } catch (err) {
      if (myGen !== engineWaitGeneration) {
        return false;
      }
      showServiceBanner(`Waiting for Stop: ${err.message}`);
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  if (myGen === engineWaitGeneration) {
    showServiceBanner("Stop is taking longer than expected — try Start again, or check service_stderr.log.");
  }
  return false;
}

document.getElementById("btn-stop-service").onclick = async () => {
  if (!UI.isLive) return;
  if (
    !confirm(
      "Stop the Prooftest engine?\n\nOPC, SILworX API, and plugin monitors will stop. This web page stays open so you can Start again."
    )
  ) {
    return;
  }
  engineWaitGeneration += 1;
  document.getElementById("btn-stop-service").disabled = true;
  try {
    await fetchJson("/api/stop?reason=ui_stop", { method: "POST" });
    showServiceBanner("Engine stopping — waiting for cleanup…");
    await updateServiceButtons({ stopping: true, starting: false, engine_running: false });
    const stopped = await waitForEngineStopped(45000);
    if (stopped) {
      showServiceBanner("Engine stopped. Web interface is still active — use Start service to resume.");
      document.getElementById("btn-start-service").disabled = false;
      await updateServiceButtons();
      await pollStatus();
    }
  } catch (err) {
    showServiceBanner(`Stop failed: ${err.message}`);
    await updateServiceButtons();
  }
};
document.getElementById("btn-open").onclick = () => {
  if (!selectedReport || !UI.isLive) return;
  window.open(UI.api(`/api/reports/open?path=${encodeURIComponent(selectedReport)}`), "_blank");
};

function showArchivePath(path) {
  const el = document.getElementById("archive-status");
  if (!el) return;
  if (!path) {
    el.classList.add("hidden");
    el.textContent = "";
    return;
  }
  el.textContent = `Archive saved to: ${path}`;
  el.classList.remove("hidden");
}

function closeImportExportMenu() {
  const menu = document.querySelector(".import-export-menu");
  if (menu) menu.removeAttribute("open");
}

function filenameFromDisposition(value, fallbackName) {
  const fallback = fallbackName || "list-archive.zip";
  const raw = String(value || "");
  const utf8Match = raw.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match && utf8Match[1]) {
    try {
      return decodeURIComponent(utf8Match[1]);
    } catch (_ignore) {
      return utf8Match[1];
    }
  }
  const plainMatch = raw.match(/filename="?([^\";]+)"?/i);
  return plainMatch && plainMatch[1] ? plainMatch[1] : fallback;
}

async function exportArchiveToUserLocation() {
  if (!UI.isLive) return;
  const url = UI.api("/api/archives/export");
  if (!url) return;
  try {
    const token = apiAuthToken();
    const headers = token ? { "X-Prooftest-Token": token } : undefined;
    const res = await fetch(url, { method: "POST", headers });
    if (!res.ok) throw new Error(await res.text());
    const blob = await res.blob();
    const filename = filenameFromDisposition(
      res.headers.get("Content-Disposition"),
      "list-archive.zip"
    );
    const archivePath = res.headers.get("X-Archive-Path") || "";
    const deviceCount = Number(res.headers.get("X-Device-Count") || 0);
    const reportCount = Number(res.headers.get("X-Report-Count") || 0);

    if (window.showSaveFilePicker) {
      const handle = await window.showSaveFilePicker({
        suggestedName: filename,
        types: [{ description: "Zip archive", accept: { "application/zip": [".zip"] } }],
      });
      const writable = await handle.createWritable();
      await writable.write(blob);
      await writable.close();
    } else {
      const href = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = href;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(href);
    }

    showArchivePath(archivePath);
    showServiceBanner(`Exported ${deviceCount} devices and ${reportCount} reports.`);
  } catch (err) {
    const message = apiErrorText(err);
    if (
      /404|not found|method not allowed|405/i.test(message) &&
      /archives\/export|detail/i.test(String((err && err.message) || ""))
    ) {
      showServiceBanner("Export is not available in the running service yet. Restart the Prooftest service, then try Export again.");
    } else {
      showServiceBanner(`Export failed: ${message}`);
    }
  } finally {
    closeImportExportMenu();
  }
}

document.getElementById("btn-keep-opc").onclick = async () => {
  if (!UI.isLive) return;
  const archiveFirst = document.getElementById("archive-before-clear").checked;
  const message = archiveFirst
    ? "Clear the device list and keep only OPC / Running devices?\n\nThe current device list and report list will be archived first so they can be restored later.\n\nReport files on disk are not deleted."
    : "Clear the device list and keep only OPC / Running devices?\n\nLists will not be archived. Report files on disk are not deleted.";
  if (!confirm(message)) return;
  try {
    const result = await fetchJson(`/api/devices/keep-opc?archive=${archiveFirst ? "true" : "false"}`, {
      method: "POST",
    });
    if (result.archive && result.archive.path) {
      showArchivePath(result.archive.path);
    }
    showServiceBanner(
      `Cleared ${result.removed_count || 0} non-OPC device(s). ${result.opc_devices || 0} OPC device(s) remain.`
    );
    selectedDevice = null;
    selectedDeviceId = null;
    selectedProject = null;
    selectedResultsType = null;
    await loadDevices();
  } catch (err) {
    showServiceBanner(`Clear device list failed: ${apiErrorText(err)}`);
  }
};

const importBtn = document.getElementById("btn-import-list");
if (importBtn) {
  importBtn.onclick = () => {
    if (!UI.isLive) return;
    const fileInput = document.getElementById("archive-file");
    if (fileInput) fileInput.click();
    closeImportExportMenu();
  };
}

const exportBtn = document.getElementById("btn-export-list");
if (exportBtn) {
  exportBtn.onclick = () => exportArchiveToUserLocation();
}

document.getElementById("archive-file").onchange = async (event) => {
  const file = event.target.files && event.target.files[0];
  event.target.value = "";
  if (!file || !UI.isLive) return;
  if (
    !confirm(
      `Restore device list from ${file.name}?\n\nExisting report files are left unchanged.`
    )
  ) {
    return;
  }
  try {
    const url = UI.api("/api/archives/upload-restore");
    const body = new FormData();
    body.append("file", file);
    const opts = { method: "POST", body };
    const token = apiAuthToken();
    if (token) opts.headers = { "X-Prooftest-Token": token };
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(await res.text());
    const result = await res.json();
    showServiceBanner(
      `Restored ${result.restored_devices || 0} device(s) and ${result.restored_reports || 0} missing report file(s).`
    );
    await loadDevices();
  } catch (err) {
    showServiceBanner(`Restore failed: ${apiErrorText(err)}`);
  }
};

document.getElementById("btn-reset-alarms").onclick = async () => {
  if (!UI.isLive) return;
  if (!confirm("Acknowledge and reset all alarms?")) return;
  try {
    await fetchJson("/api/alarms/reset", { method: "POST" });
    await pollStatus();
  } catch (err) {
    showServiceBanner(`Reset alarms failed: ${apiErrorText(err)}`);
  }
};

document.getElementById("modal-close").onclick = () => {
  document.getElementById("modal").classList.add("hidden");
};

document.getElementById("btn-prooftest-history").onclick = () => openHistoryModal();
document.getElementById("history-modal-close").onclick = () => closeHistoryModal();
document.getElementById("history-modal").addEventListener("click", (event) => {
  if (event.target.id === "history-modal") closeHistoryModal();
});

refreshAll(false);
setupThemeToggle();
setupNavigation();
setupListSearch("device-search", "device-list", "device");
setupListSearch("report-search", "report-list", "report");
setupDeviceColumnFilters();
setupDeviceViewOptions();
if (UI.isLive) {
  setInterval(pollStatus, 2000);
}
