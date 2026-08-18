# HIMA Automated Prooftest — Functionality & Architecture

| Field | Value |
|-------|--------|
| **Document** | Solution functionality catalogue, runtime pipeline, and system architecture |
| **Runtime** | `HIMA-Prooftest-Solution-Current` |
| **Paired SPEC** | SPEC-001 v1.59 |
| **Location** | `Z:\Project\Report Solution` |
| **Updated** | 2026-08-18 |

> Describes **how the system works today**. Station data lives under `C:\HIMA Prooftest Reporting Tool`. **One unified mode:** every device-list update/refresh queries **SILworX API and X-OPC at the same time**, then merges. API contributes only when the user has a project open (the tool never opens a project). On SILworX uninstall (G-11) the solution **keeps running** on OPC after releasing SILworX locks.

**Pictures:** `Specifications\architecture-diagrams\` (`01`–`11`) and `Flow Diagram\`.

---

## 1. Purpose

Background Windows service that must run on the **same station as the X-OPC server**. It:

1. Discovers HART prooftest devices (API and OPC together)  
2. Reads realtime Results from **X-OPC**  
3. Detects prooftest start/end via `.Running`  
4. Writes SQL snapshots under the station **Database** folder  
5. Generates **HTML/PDF** reports  
6. Exposes a **web graphic interface** on `http://127.0.0.1:8080/`

---

## 2. Station root (first run)

On first start the solution creates:

```text
C:\HIMA Prooftest Reporting Tool\
├─ Database\                          ← SQL .mdf/.ldf or SQLite prooftest.db + tables
├─ HIMA Automated Prooftest Reports\  ← generated PDF/HTML reports
│  └─ Report Templates\               ← HTML templates (seeded + auto for new CSV types)
└─ Results Structures\                ← CSV type catalogue (seed 9; new CSV = new type)
```

| # | Folder | Role |
|---|--------|------|
| 1 | **Database** | Create DB + `ProofTest_*` tables here |
| 2 | **HIMA Automated Prooftest Reports** | Future prooftest PDF/HTML reports |
| 3 | **Results Structures** | Nine baseline CSVs; copy a new CSV → new Results / device type + SQL table + report template |

Package seed CSVs remain under `HIMA-Prooftest-Solution-Current\Results Structures\` and are copied into the station catalogue on first start.

---

## 3. Operating mode (unified)

| Aspect | Behaviour |
|--------|-----------|
| **Where solution runs** | Same station as X-OPC (engineering or HMI) |
| **Device list** | On every update/refresh: **SILworX REST API and X-OPC simultaneously**, then merge (`api+opc` / `api` / `opc_fallback`). API only if the user has a project open. The tool **never** opens a SILworX project. After a project is opened, the plugin session is **refreshed** (re-register) so the API path can attach. |
| **Triggers / change detect** | Plugin WebSocket + `c3data` / `.E3` + Results CSV watch when SILworX present; parallel device-list poll while API unavailable |
| **Config** | Always `deployment_case = 1` (legacy Case 2 removed) |

**G-11 uninstall:** release SILworX engines → **stay up** → continue OPC device list (still unified mode).

---

## 4. Functionality catalogue

| Function | SPEC | Description | How it works |
|----------|------|-------------|--------------|
| **First-run / station setup** | Step 1 | Create station root + three folders | See §2; unified mode; `installation.json` |
| **SQL database & tables** | Step 2 / G-05 | Create DB and `ProofTest_*` tables | Files under `Database\`; DDL from each Results Structure CSV (baseline nine + any added) |
| **Device list** | Step 3 / G-10 | Maintain `DeviceProoftestResultList` | **API and OPC together** on every refresh. API attaches **only when the user has a project open**. If no project / SILworX down → API empty, OPC fills the list. Tool never `open/local`. Opening a project **re-registers** the plugin for a new `user_session_id`. |
| **OPC realtime reads** | Step 4 | Live HART Results | Independent poll-loop (~1 s); never blocked by API (G-22) |
| **Prooftest detection** | Step 5 | Start/end + snapshot | `.Running` edges → SQL INSERT → queue report |
| **PDF / HTML reports** | Step 6 | Reports after each test | Templates under `Report Templates\`; **auto-create** for new CSV types; output under Reports\{Type}\{TAG}\ |
| **Update triggers** | Step 7 | Refresh metadata | Session/`c3data`/`.E3` → `refresh()` (API + OPC together). New Results CSV → reload type + SQL + template. API down → same parallel scan (API no-ops) |
| **Web graphic interface** | UI | Operator view | FastAPI `:8080`. Start / Stop engine; Shutdown = process exit |
| **Multi-instance SILworX** | G-21 | Several SILworX windows | Ports `51710/8400` … `51719/8409`; attach to user-open project only (never Mode A `open/local`) |
| **API release when SILworX closed** | G-19 | Drop API cleanly | Two failed probes → release/suspend; UI + OPC continue; **parallel device-list poll** while suspended |
| **Leftover `c3.exe` cleanup** | G-20 | Kill orphan engine | After real close (`lock.ini` + GUI gone) → wait 8 s → `taskkill` `c3.exe` |
| **SILworX uninstall** | G-11 | Free locks; keep solution | Release API/plugin/`c3.exe`; **keep running**; continue OPC device list (unified) |
| **Full process exit** | optional | Operator exit | `stop_service.ps1` / `POST /api/shutdown` — **not** required for uninstall |

---

## 5. Runtime pipeline

### 5.1 Process start

1. `main.py` loads `solution.ini`  
2. `ProoftestService.start()`  
3. Uvicorn serves UI on `127.0.0.1:8080`

### 5.2 Engine start body

1. Create station root + three folders; seed Results CSVs  
2. Connect DB under `Database\`; create `ProofTest_*` for every CSV type  
3. Load Results Structures; ensure report templates  
4. Start plugin monitor when possible; start **poll-loop** + **sync-loop**  
5. `refresh(manual=True)` → `engine=running`

### 5.3 `refresh()` / device list rule

```text
start API attach + X-OPC browse  ──together──► merge DeviceProoftestResultList
       │                              │
       │ API: project open?           │ OPC: always scan Results .Running
       │   yes → globals              │
       │   no  → empty contribution   │
       ▼                              ▼
  api+opc (both ok)  ·  api (OPC failed)  ·  opc_fallback (API empty)
```

### 5.4 Continuous loops

| Loop | Interval | Role |
|------|----------|------|
| **poll-loop** | ~1 s | OPC `.Running` + Results |
| **sync-loop** | ~0.5 s tick | Triggers, G-19/G-20/G-11; **API+OPC device poll when API down** |
| **plugin-monitor** | event-driven | Session open/close `8400`–`8409` when SILworX present |
| **report-worker** | queue | SQL insert + HTML/PDF |

### 5.5 Prooftest event path

```text
OPC .Running ↑  →  mark test in progress
OPC .Running ↓  →  snapshot Results → INSERT ProofTest_* → HTML/PDF → ReportPath
```

### 5.6 Operator controls

| Action | Effect |
|--------|--------|
| **UI Stop** | Release OPC/API/plugin/workers; **web UI stays up** |
| **UI Start** | Restart engine in-process |
| **Shutdown** | Cleanup + **process exit** (optional; not auto on uninstall) |

### 5.7 SILworX lifecycle

| Event | Solution reaction |
|-------|-------------------|
| Project open | Plugin trigger → `refresh()`; attach session; merge API + OPC devices |
| No project open | **OPC still scanned in parallel** (tool never opens the project) |
| SILworX closed (still installed) | **G-19** suspend API; **OPC device-list poll**; **G-20** may kill leftover `c3.exe` |
| SILworX uninstalled | **G-11** release engines; **keep running**; OPC device list |

---

## 6. System architecture

### 6.1 Process and threads

```text
python main.py
├─ uvicorn (Graphic Interface)     ← survives UI Stop
├─ poll-loop                       ← OPC realtime
├─ sync-loop                       ← triggers · G-19 · G-20 · G-11 · API+OPC poll
├─ plugin-monitor                  ← WSS 8400–8409 (when SILworX present)
└─ report-worker                   ← SQL + reports

Station data (C:\HIMA Prooftest Reporting Tool):
  Database\ · HIMA Automated Prooftest Reports\ · Results Structures\
```

### 6.2 G-22 three layers

| Layer | Role |
|-------|------|
| **Data** | Device metadata via **API globals and OPC browse together**. CSVs = Results **types** (add CSV → new type) |
| **Trigger** | Plugin + `c3data`/`.E3` → `refresh()`. New CSV → schema + template. API down → same parallel device poll. Never block OPC realtime |
| **Realtime** | Independent OPC poll (~1 s) for `.Running` + values |

### 6.3 Device list via API and OPC together

| Situation | Behaviour |
|-----------|-----------|
| **User has a SILworX project open** | Attach to that session (plugin); read globals **and** scan OPC; **do not** `project/close` |
| **No project open** | API empty; OPC fills the list (`opc_fallback`). The tool **never** opens a SILworX project |

### 6.4 Code layout

```text
HIMA-Prooftest-Solution-Current/
  main.py, solution.ini, VERSION.json
  Tool Steps/          service, steps 01–07, results_csv, config
  Annex codes/         Database, API, OPC, PDF, Plugin, Stop service, Tool test
  Graphic Interface/
  Results Structures/  package seed → copied to C:\…\Results Structures
```

---

## 7. Data stores

| Store | Path / name |
|-------|-------------|
| **Station root** | `C:\HIMA Prooftest Reporting Tool` |
| **SQL name** | `HIMA Automated Prooftest` (`localhost\SQLEXPRESS` or SQLite under `Database\`) |
| **Reports** | `...\HIMA Automated Prooftest Reports\{Results_Type}\{Device_TAG}\` |
| **Templates** | `...\HIMA Automated Prooftest Reports\Report Templates\` |
| **Results CSVs** | `...\Results Structures\*.csv` |

System tables: `DeviceProoftestResultList`, `AlarmLog`, `SchemaVersion`, `ServiceState`.  
Results tables: one `ProofTest_*` per Results Structure CSV.

---

## 8. Key web endpoints

| Endpoint | Role |
|----------|------|
| `GET /api/health` | Engine / web / SILworX / OPC status |
| `POST /api/start` | Restart engine |
| `POST /api/stop` | Stop engine only |
| `POST /api/shutdown` | Full process exit |
| `POST /api/refresh` | Manual device / OPC refresh |
| `GET /api/devices`, `/api/reports`, `/api/alarms` | Operator data |

Localhost-only for start/stop/shutdown.

---

## 9. Related documents

| Document | Path |
|----------|------|
| Specification | `SPEC-001-v1.53-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md` |
| Mermaid source | [HIMA-Prooftest-Architecture-Mermaid.md](./HIMA-Prooftest-Architecture-Mermaid.md) |
| Architecture PNGs | `architecture-diagrams\` (`01-system-context` … `09-deployment`) |
| Spec / code history | `History of Modifications.md` / `Codes\Code History of Modifications.md` |

---

*End of document*
