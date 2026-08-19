let selectedDevice = null;
let selectedDeviceId = null;
let selectedProject = null;
let selectedResultsType = null;
let selectedReport = null;
let shownPopupKeys = new Set();

const DEVICE_VIEW_KEY = "prooftest.deviceListView";
const NO_DEVICE_TEXT = "(No device available)";
const NO_REPORT_TEXT = "(No report available)";

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

const listSearchState = {
  device: { index: -1 },
  report: { index: -1 },
};

function listSearchableItems(list) {
  return [...list.children].filter(
    (li) => !li.classList.contains("list-placeholder") && !li.classList.contains("list-empty")
  );
}

function applyListSearch(inputId, listId, stateKey, advance = false) {
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
    list.innerHTML = `<tr class="list-placeholder"><td colspan="5">${escapeHtml(text)}</td></tr>`;
    return;
  }
  list.innerHTML = `<li class="list-placeholder">${escapeHtml(text)}</li>`;
}

let engineWaitGeneration = 0;

async function updateServiceButtons(health) {
  const startBtn = document.getElementById("btn-start-service");
  const stopBtn = document.getElementById("btn-stop-service");
  if (!UI.isLive) {
    startBtn.disabled = true;
    stopBtn.disabled = true;
    const c = document.getElementById("btn-connect-silworx");
    const d = document.getElementById("btn-disconnect-silworx");
    if (c) c.disabled = true;
    if (d) d.disabled = true;
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
  startBtn.disabled = running || starting;
  stopBtn.disabled = !running || starting;
  const connectBtn = document.getElementById("btn-connect-silworx");
  const disconnectBtn = document.getElementById("btn-disconnect-silworx");
  const silRunning = String(health.silworx_status || "").toLowerCase() === "running";
  if (connectBtn) connectBtn.disabled = !running || silRunning;
  if (disconnectBtn) disconnectBtn.disabled = !running || !silRunning;
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
        await refreshAll(false);
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

function healthCard(label, value, state) {
  const cls = state ? ` health-card ${state}` : " health-card";
  return `<div class="${cls.trim()}"><span class="label">${escapeHtml(label)}</span><span class="value">${escapeHtml(value)}</span></div>`;
}

function renderHealth(data) {
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
  const silText = silworxStatus === "running" ? "running" : "not connected";
  const silState = silworxStatus === "running" ? "ok" : "warn";

  const queueState = (data.queue_depth || 0) > 10 ? "warn" : "";
  const pluginInfo = data.plugin_session || {};
  const pluginName = String(pluginInfo.name || "").trim();
  const pluginRegistered = pluginInfo.registered === true || pluginInfo.connected === true;
  const pluginText = pluginName || "not registered";
  const pluginState = pluginRegistered ? "ok" : "";
  const serviceState = data.starting ? "Starting" : data.stopping ? "Stopped" : "Running";
  const serviceCls = data.starting || data.stopping ? "warn" : "ok";
  const sourceRaw = String(data.device_list_source || st.device_list_source || "").toLowerCase();
  const sourceText = sourceRaw === "api+opc"
    ? "API + OPC"
    : sourceRaw === "api"
      ? "API"
      : sourceRaw === "opc_fallback" || sourceRaw === "opc"
        ? "OPC"
        : data.device_list_source
          ? String(data.device_list_source)
          : data.deployment_case != null
            ? `unified (case ${data.deployment_case})`
            : "unified";

  grid.innerHTML = [
    `<div class="health-row health-row-counts">
      ${healthCard("ALL DEVICES", String(data.active_devices ?? 0), "")}
      ${healthCard("OPC ACTIVE DEVICES", String(data.opc_devices ?? 0), "ok")}
    </div>`,
    `<div class="health-row health-row-top">
      ${healthCard("Service", serviceState, serviceCls)}
      ${healthCard("Database", data.database || "unknown", "")}
    </div>`,
    `<div class="health-row health-row-mid">
      ${healthCard("Device list", sourceText, "")}
      ${healthCard("SILworX", silText, silState)}
      ${healthCard("Plugin session", pluginText, pluginState)}
      ${healthCard("Queue depth", String(data.queue_depth ?? 0), queueState)}
    </div>`,
  ].join("");

  const servers = data.opc_servers || [];
  const opcText = document.getElementById("opc-detail-text");
  if (opcText) {
    if (!servers.length) {
      opcText.textContent = "OPC: no X-OPC servers detected on this host.";
    } else {
      opcText.innerHTML =
        "<strong>OPC servers:</strong> " +
        servers
          .map((s) => {
            const status = s.connected ? `${s.tags} tags` : "offline";
            return `${escapeHtml(s.name)} (${status})`;
          })
          .join(" · ");
    }
  }

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
  const hasIssue = servers.some((s) => !s.connected) || data.stopping || Boolean(data.last_error);
  if (badge) {
    badge.textContent = hasIssue ? "attention" : "healthy";
    badge.className = hasIssue ? "panel-badge panel-badge-warn" : "panel-badge panel-badge-ok";
  }
}

function renderOfflineHealth() {
  const grid = document.getElementById("health-grid");
  grid.innerHTML = [
    healthCard("Mode", "Offline preview", "warn"),
    healthCard("Database", "—", ""),
    healthCard("Service", "not connected", "warn"),
  ].join("");
  document.getElementById("opc-detail-text").textContent =
    "Start the Prooftest service and open http://127.0.0.1:8080/ for live data.";
  document.getElementById("health-status-badge").textContent = "offline";
  document.getElementById("health-status-badge").className = "panel-badge panel-badge-warn";
}

function renderAlarms(payload) {
  const alarms = Array.isArray(payload) ? payload : payload.alarms || [];
  const panel = document.getElementById("alarms");
  const list = document.getElementById("alarm-list");
  const badge = document.getElementById("alarm-count-badge");
  const activeCount = alarms.filter((a) => a.active).length;

  badge.textContent = `${activeCount} active`;
  panel.classList.toggle("has-alarms", activeCount > 0);

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
      return `<article class="alarm-item${a.acknowledged ? " acked" : ""}">
        <span class="alarm-step">${escapeHtml(a.step || "?")}</span>
        <div class="alarm-body">
          <p class="alarm-msg">${escapeHtml(a.message)}</p>
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

  const hint = document.getElementById("device-list-hint");
  const view = currentDeviceView();
  const viewLabel = view === "opc" ? "OPC / Running" : "all devices";
  if (hint) hint.textContent = `${devices.length} shown · ${viewLabel}`;

  list.innerHTML = "";
  devices.forEach((d) => {
    const tr = document.createElement("tr");
    const id = d.device_id || `${d.project || ""}|${d.device_tag}`;
    tr.dataset.searchText = `${d.device_tag} ${d.results_type || ""} ${d.project || ""} ${d.opc_server || ""}`.toLowerCase();
    tr.dataset.deviceId = id;
    if (id === selectedDeviceId || (!selectedDeviceId && d.device_tag === selectedDevice)) {
      tr.classList.add("selected");
    }
    const onOpc = Boolean(d.present_on_opc);
    const status = onOpc
      ? '<span class="device-status on-opc">OPC</span>'
      : '<span class="device-status off-opc">not on OPC</span>';
    tr.innerHTML = `
      <td class="device-tag-cell">
        <img class="device-logo" src="${vendorLogo(d.results_type)}" alt=""/>
        <span class="device-tag">${escapeHtml(d.device_tag)}</span>
      </td>
      <td>${escapeHtml(d.results_type || "")}</td>
      <td>${status}</td>
      <td>${escapeHtml(d.project || d.silworx_project || "")}</td>
      <td>${escapeHtml(d.opc_server || "")}</td>`;
    tr.onclick = () => {
      selectedDevice = d.device_tag;
      selectedDeviceId = id;
      selectedProject = d.project || d.silworx_project || "";
      selectedResultsType = d.results_type;
      [...list.children].forEach((c) => c.classList.remove("selected"));
      tr.classList.add("selected");
      updateSelectedLabel();
      loadReports();
    };
    list.appendChild(tr);
  });
  list.scrollTop = previousScroll;
  updateSelectedLabel();
  applyListSearch("device-search", "device-list", "device", false);
}

function updateSelectedLabel() {
  const label = document.getElementById("selected-device-label");
  if (!label) return;
  if (!selectedDevice) {
    label.textContent = "(No report selected)";
    return;
  }
  label.textContent = `Selected: ${selectedDevice}${selectedProject ? ` · ${selectedProject}` : ""}${selectedResultsType ? ` (${selectedResultsType})` : ""}`;
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
    reports = await fetchJson(url);
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
    const data = await fetchJson("/api/refresh", { method: "POST" });
    (data.popups || []).forEach(showPopup);
    await pollStatus();
    await loadDevices();
    await loadRunningTests();
    if (selectedDevice) await loadReports();
  } catch (err) {
    showServiceBanner(`Service error: ${err.message}`);
  }
}

let pollFailStreak = 0;
let pollInFlight = false;

async function pollStatus() {
  if (!UI.isLive || pollInFlight) return;
  pollInFlight = true;
  let health = null;
  try {
    health = await fetchJson("/api/health", { timeoutMs: 4000 });
    renderHealth(health);
    pollFailStreak = 0;
    hideServiceBanner();
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
    showServiceBanner("Engine stopped. Web interface is still active — use Start service to resume.");
    document.getElementById("btn-start-service").disabled = false;
    await updateServiceButtons({ stopping: true, starting: false, engine_running: false });
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

document.getElementById("btn-archive-lists").onclick = async () => {
  if (!UI.isLive) return;
  try {
    const result = await fetchJson("/api/archives", { method: "POST" });
    const path = result.path || result.archive_id || "List Archives";
    showArchivePath(path);
    showServiceBanner(
      `Archived ${result.device_count || 0} devices and ${result.report_count || 0} reports.`
    );
  } catch (err) {
    showServiceBanner(`Archive failed: ${apiErrorText(err)}`);
  }
};

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

document.getElementById("btn-browse-restore").onclick = () => {
  if (!UI.isLive) return;
  document.getElementById("archive-file").click();
};

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
setupListSearch("device-search", "device-list", "device");
setupListSearch("report-search", "report-list", "report");
setupDeviceViewOptions();
if (UI.isLive) {
  setInterval(pollStatus, 8000);
}
