# HIMA Automated Prooftest — Functionality & Architecture

| Field | Value |
|-------|--------|
| **Document** | Solution functionality catalogue, runtime pipeline, and system architecture |
| **Runtime** | `HIMA-Prooftest-Solution-Current` |
| **Paired SPEC** | SPEC-001 v1.44 |
| **Location** | `Z:\Project\Report Solution` |
| **Updated** | 2026-08-13 |

> Describes **how the system works today**. Case 1 SILworX uninstall currently auto-exits the process (G-11); it does **not** yet switch to Case 2 OPC-only mode.

---

## 1. Purpose

Background Windows service that must run on the **same station as the X-OPC server**. It:

1. Discovers HART prooftest devices  
2. Reads realtime Results from **X-OPC**  
3. Detects prooftest start/end via `.Running`  
4. Writes SQL snapshots  
5. Generates **HTML/PDF** reports  
6. Exposes a **web graphic interface** on `http://127.0.0.1:8080/`

---

## 2. Deployment cases

| | **Case 1 — Engineering** | **Case 2 — HMI** |
|---|--------------------------|------------------|
| **Where solution runs** | Same PC as SILworX + X-OPC | HMI with X-OPC (SILworX remote / absent) |
| **Device / metadata** | SILworX REST API (`structuretree` + globals); OPC for bindings / fallback | OPC browse only |
| **Triggers** | Plugin WebSocket + file watchers + API lifecycle (G-19 / G-20) | Structure / device-list polls |
| **Config** | `deployment_case = 1` | `deployment_case = 2` |

**First run (Step 1):** if SILworX is installed → Case 1; else → Case 2 (when auto-detect is enabled). Persisted in `installation.json` / `solution.ini`.

---

## 3. Functionality catalogue

| Function | SPEC | Description | How it works |
|----------|------|-------------|--------------|
| **First-run / station setup** | Step 1 | Prepare report folders and deployment case on first start | Creates `C:\HIMA Automated Prooftest Reports` + nine Results-type folders; detects Case 1/2; writes `installation.json` |
| **SQL database & tables** | Step 2 / G-05 | Create DB and nine `ProofTest_*` tables | On engine start: connect (CREATE DATABASE if needed); generate DDL from bundled Results Structure CSVs (template-style types). Template folder is **design reference only** — not required on another PC |
| **Device list** | Step 3 | Maintain `DeviceProoftestResultList` | **Case 1:** SILworX API on every reachable instance (Mode B attach / Mode A `open/local` on preferred port); merge; OPC enrich. Fallback OPC if API suspended/fails. **Case 2:** OPC browse only |
| **OPC realtime reads** | Step 4 | Read live HART Results from X-OPC | Discover X-OPC servers; bind Device_TAG → item path; poll Results members independently of SILworX API (G-22 realtime layer) |
| **Prooftest detection** | Step 5 | Detect test start/end and snapshot results | Watch `.Running` false→true (start) and true→false (end). On end: OPC snapshot → SQL INSERT into matching `ProofTest_*` → queue report |
| **PDF / HTML reports** | Step 6 | Generate reports after each completed test | Fill HTML templates (SAMSON FST/PST by FB type); write under `Reports\{ResultsType}\{DeviceTAG}\`; optional PDF; store `ReportPath` on SQL row |
| **Update triggers** | Step 7 | Refresh device list / schema when projects change | **Case 1:** plugin session events + `c3data` / `.E3` watchers → `refresh()`. **Case 2:** poll on interval. Also hosts G-19 / G-20 / G-11 watches |
| **Web graphic interface** | UI | Operator view and Start/Stop | FastAPI/uvicorn on `:8080` — health, devices, reports, alarms. **Start** restarts engine; **Stop** stops engine only; **Shutdown** exits process (G-11) |
| **Multi-instance SILworX API** | G-21 | Talk to several SILworX windows | Scan 10 port pairs `51710/8400` … `51719/8409`. Attach to each open GUI project (Mode B). `open/local` only on preferred `api_port` (Mode A). Merge device lists |
| **API release when SILworX down** | G-19 | Drop API cleanly when SILworX closes | Two failed `/silworx/info` polls → close owned `open/local` sessions, discard clients, suspend API opens. Do **not** `project/close` GUI sessions. Resume when API returns |
| **Leftover `c3.exe` cleanup** | G-20 | Kill orphan SILworX engine after real close | After prior active session, when `lock.ini` and `OLixClient.exe` both gone → wait 8 s → `taskkill` `c3.exe` only. Never kill during SILworX startup |
| **Full process exit for uninstall** | G-11 | Free locks so SILworX can be uninstalled | `stop_service.ps1` or `POST /api/shutdown` exits process. **Today Case 1 also auto-exits if SILworX install disappears** (does not switch to Case 2 yet) |

---

## 4. Runtime pipeline (detailed)

### 4.1 Process start

1. `main.py` loads `solution.ini`  
2. Creates `ProoftestService` and calls `start()`  
3. Uvicorn serves the UI on `127.0.0.1:8080`

### 4.2 Engine start body

1. `ensure_first_run` — folders / case / `installation.json`  
2. DB connect + create nine `ProofTest_*` tables (CSV generator)  
3. Load Results Structure CSVs  
4. Create `ProoftestMonitor` (+ report worker)  
5. **Case 1:** clear G-19 suspend; start plugin monitor  
6. Start **`poll-loop`** and **`sync-loop`**  
7. `refresh(manual=True)` → `engine=running`

### 4.3 `refresh()`

1. Discover OPC servers  
2. **Case 1:** API device discovery on all instances (or OPC fallback) / **Case 2:** OPC devices  
3. Sync schema  
4. Upsert `DeviceProoftestResultList`  
5. Sync device report folders  
6. Update `ServiceState`

### 4.4 Continuous loops

| Loop | Interval | Role |
|------|----------|------|
| **poll-loop** | ~1 s | OPC `.Running` + Results; detect test edges |
| **sync-loop** | ~0.5 s tick | Triggers, G-19/G-20/G-11, Case 2 polls |
| **plugin-monitor** | event-driven | Session open/close on ports `8400`–`8409` (Case 1) |
| **report-worker** | queue | SQL insert + HTML/PDF off the poll path |

### 4.5 Prooftest event path

```text
OPC .Running ↑  →  mark test in progress
OPC .Running ↓  →  snapshot all Results members
                →  INSERT into ProofTest_*
                →  HTML/PDF under report folders
                →  update ReportPath on SQL row
```

### 4.6 Operator controls

| Action | Effect |
|--------|--------|
| **UI Stop** (`POST /api/stop`) | Release OPC / API / plugin / workers; **web UI stays up** |
| **UI Start** (`POST /api/start`) | Restart engine in-process |
| **Shutdown** (`POST /api/shutdown` / `stop_service.ps1`) | Same cleanup + **process exit** (G-11) |

### 4.7 SILworX lifecycle (Case 1 — current behaviour)

| Event | Solution reaction |
|-------|-------------------|
| SILworX window opens + project open | Plugin session trigger → `refresh()`; Mode B attach; merge devices from that instance |
| SILworX up, no project open | Mode B unavailable; Mode A may `open/local` configured `.E3` on preferred port then `project/close`; else OPC fallback |
| SILworX closed (still installed) | **G-19:** release API / suspend opens; UI + OPC keep running; **G-20** may kill leftover `c3.exe` |
| SILworX uninstalled | **G-11 auto process exit** (current). Desired future: stay up as Case 2 / OPC-only |

---

## 5. System architecture

### 5.1 Process and threads

```text
python main.py
├─ uvicorn (Graphic Interface)     ← survives UI Stop; dies on G-11 exit
├─ poll-loop                       ← OPC realtime (G-22 realtime layer)
├─ sync-loop                       ← triggers + G-19/G-20/G-11
├─ plugin-monitor (Case 1)         ← WebSocket on 8400–8409
└─ report-worker                   ← SQL + reports

Data stores:
  SQL Server  «HIMA Automated Prooftest»
  Reports     C:\HIMA Automated Prooftest Reports
```

| Layer | Responsibility |
|-------|----------------|
| **Host process** | `python main.py` — owns service + uvicorn |
| **Web host** | FastAPI UI — survives UI Stop; dies on G-11 exit |
| **poll-loop** | OPC Running detection + snapshot trigger |
| **sync-loop** | Triggers, G-19/G-20/G-11, Case 2 polls |
| **plugin-monitor** | WebSocket listeners on plugin ports (Case 1) |
| **report-worker** | Async SQL insert + HTML/PDF generation |
| **Data layer** | SQL DB + report folders |

### 5.2 G-22 three layers

| Layer | Role |
|-------|------|
| **Data** | Device list / `Results_Type` / Configuration / Resource via SILworX API (Case 1) or OPC (Case 2 / fallback) |
| **Trigger** | Plugin monitors + `c3data` / `.E3` watchers call `refresh()` — never block OPC poll |
| **Realtime** | Independent OPC poll-loop (~1 s) for `.Running` + Results values |

### 5.3 Mode A vs Mode B (SILworX API)

| Mode | When | Behaviour |
|------|------|-----------|
| **Mode B** | GUI has a project open | Attach to existing GUI session via plugin (`user_session_id`). Do **not** call `project/close` |
| **Mode A** | No GUI project; preferred `api_port` only | `POST /project/open/local` with path from `solution.ini` → read devices → `POST /project/close` |

Multiple SILworX windows → scan all port pairs; attach to each reachable GUI session; merge device lists. `open/local` only on the **preferred** `api_port`.

### 5.4 Code layout (G-14 / G-16 / G-17)

```text
HIMA-Prooftest-Solution-Current/
  main.py, solution.ini, VERSION.json
  run_service.ps1, stop_service.ps1
  Tool Steps/                 ← Steps + core service
    service.py, config.py, alarms.py, results_csv.py
    step01_setup.py … step07_triggers.py
  Annex codes/
    Database/                 annex_database.py
    API connexion/            annex_api_connexion.py
    OPC/                      annex_opc.py
    PDF generation/           annex_pdf_generation.py
    Plugin/                   annex_plugin.py, annex_plugin_monitor.py
    Stop service/             annex_stop_service.py, annex_silworx_cleanup.py
    Tool test/                gate / audit scripts
    prooftest/__init__.py     import bootstrap
  Graphic Interface/          app.py, static/
  Results Structures/         bundled CSVs (runtime DDL + members)
```

---

## 6. Data stores

### SQL

| Item | Value |
|------|--------|
| **Database name** | `HIMA Automated Prooftest` |
| **Server (default)** | `localhost\SQLEXPRESS` (trusted); SQLite fallback if unavailable |
| **System tables** | `DeviceProoftestResultList`, `AlarmLog`, `SchemaVersion`, `ServiceState` |
| **Results tables** | `ProofTest_ABB_FCB400_Results`, `ProofTest_Emerson_3051S_Results`, `ProofTest_E+H_PMx7xB_Results`, `ProofTest_E+H_FTL5xB_6x_Results`, `ProofTest_E+H_FMR6xB_Results`, `ProofTest_E+H_Promass300_500_Results`, `ProofTest_SAMSON_Results`, `ProofTest_WIKA_T32_Results`, `ProofTest_WIKA_T38_Results` |

### Reports

| Item | Value |
|------|--------|
| **Root** | `C:\HIMA Automated Prooftest Reports` |
| **Layout** | `\{X-HART_*_Results}\{Device_TAG}\` → HTML/PDF files |

---

## 7. Key API endpoints (web)

| Endpoint | Role |
|----------|------|
| `GET /api/health` | Engine / web / SILworX / OPC status |
| `POST /api/start` | Restart engine (UI stays up) |
| `POST /api/stop` | Stop engine only (UI stays up) |
| `POST /api/shutdown` | Full process exit (G-11) |
| `POST /api/refresh` | Manual device / OPC refresh |
| `GET /api/devices`, `/api/reports`, `/api/alarms` | Operator data |

Localhost-only for start/stop/shutdown.

---

## 8. Related documents

| Document | Path |
|----------|------|
| Specification | `Specifications\SPEC-001-v1.44-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md` |
| Mermaid diagrams | [HIMA-Prooftest-Architecture-Mermaid.md](./HIMA-Prooftest-Architecture-Mermaid.md) |
| Spec history | `Specifications\History of Modifications.md` |
| Code history | `Codes\Code History of Modifications.md` |
| Code versioning | `Codes\README.md` |

---

*End of document*
