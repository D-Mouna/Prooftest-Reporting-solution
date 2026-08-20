# Code History of Modifications — HIMA Prooftest Solution

| Field | Value |
|-------|--------|
| **Document** | Cumulative change log for solution **code** archives |
| **Active tree** | [HIMA-Prooftest-Solution-Current](./HIMA-Prooftest-Solution-Current/) |
| **Current `VERSION.json`** | **1.77** (SPEC 1.64) |
| **Paired spec** | [SPEC-001-v1.64-...](../Specifications/SPEC-001-v1.64-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) |
| **Location** | `C:\Users\Administrator\Documents\Report Solution\Codes` |
| **Filename** | `Code History of Modifications.md` |
| **Updated** | 2026-08-20 |

> **Policy:** Edit **only** `HIMA-Prooftest-Solution-Current`. Before each change, archive Current → `Archive/HIMA-Prooftest-Solution-v{next}` (`archive_current.ps1`). Archived folders are immutable. This file collects **all** code version-to-version modifications for audit (same role as [Specifications/History of Modifications.md](../Specifications/History%20of%20Modifications.md) for specs).

---

## How to maintain

1. Run `archive_current.ps1` **before** editing Current.
2. Implement the change in **Current** only; update `VERSION.json` (`spec_version`, `description`).
3. Prepend a new **### Version x.y** block at the top of **Collected modifications** below (newest first) — delta from the previous code/spec version only.
4. Do **not** edit older blocks in this file or anything under `Archive\`.

---

## Compact index (newest first)

| Code / archive | Date | Summary |
|----------------|------|---------|
| **Current → 1.77** | 2026-08-20 | R1–R7: ArchivePort, HTML seed order, db_name validation, auth/bind guard, UI unknown type + Connect titles; fastapi/starlette bump; 54/54 |
| **Current → 1.76** | 2026-08-20 | Gaps A/B/C: shaped OPC discover, CatalogService refresh brain, LiveTestService-only poll; T1–T24 |
| Archive v1.75 | 2026-08-20 | Snapshot before A/B/C cutover (optional; audit 1.75 was last archived as 1.74) |
| **Current → 1.75** | 2026-08-20 | Audit cleanup + docs pack; remove dual refresh writer; UI badge/sort |
| Archive v1.74 | 2026-08-20 | Snapshot before audit cleanup |
| **Current → 1.74** | 2026-08-20 | 100% Presentation→Application; RefreshCatalog in CatalogService |
| Archive v1.73 | 2026-08-20 | Snapshot before layer purity |
| **Current → 1.73** | 2026-08-20 | First-run Desktop shortcut “HIMA Prooftest Report”; open-UI script in Dev tools |
| Archive v1.72 | 2026-08-20 | Snapshot before Desktop UI shortcut |
| **Current → 1.72** | 2026-08-20 | Move `sync_gui_images.ps1` into `Dev tools/` with usage README |
| Archive v1.71 | 2026-08-20 | Snapshot before Dev tools relocation |
| **Current → 1.71** | 2026-08-20 | Remove standalone `annex_plugin.py` and `run_plugin*.ps1` |
| Archive v1.70 | 2026-08-20 | Snapshot before standalone plugin removal |
| **Current → 1.70** | 2026-08-20 | Remove `step02_database` shim; Gate 5 uses `annex_database` |
| Archive v1.69 | 2026-08-20 | Snapshot before step02 shim removal |
| **Current → 1.69** | 2026-08-20 | Tier B cleanup: remove stale data/, root logs, sync_markers, `__pycache__` |
| Archive v1.68 | 2026-08-20 | Snapshot before Tier B cleanup |
| **Current → 1.68** | 2026-08-20 | Remove unused `step06_reports.py` and `annex_start_service.py` |
| Archive v1.67 | 2026-08-20 | Snapshot before dead-shim cleanup |
| **Current → 1.67** | 2026-08-20 | OPC client inside Current `Annex codes/OPC/connection_opc.py`; sibling Report-Tool legacy |
| Archive v1.66 | 2026-08-20 | Snapshot before OPC client move into Current |
| **Current → 1.66** | 2026-08-20 | Full Application facade; Presentation → Application only; SilworxPort + OPC-only adapters |
| Archive v1.65 | 2026-08-20 | Snapshot before full layer architecture wiring |
| **Current → 1.65** | 2026-08-19 | Report folders scoped by Project/DeviceId; Presentation controllers + LiveTestService poll integration |
| **Current → 1.64** | 2026-08-18 | Layers; composite DeviceId; GUI Project/OPC columns; SILworX attach/detach without killing SILworX |
| Archive v1.63 | 2026-08-18 | Snapshot before layered architecture |
| **Current → 1.63** | 2026-08-18 | Per-device source: OPC ProgID or SILworX project, shown in the device list |
| Archive v1.62 | 2026-08-18 | Snapshot before per-device OPC/project source |
| **Current → 1.62** | 2026-08-18 | Device list: SILworX API and X-OPC simultaneously, then merge |
| Archive v1.61 | 2026-08-18 | Snapshot before parallel API+OPC device-list update |
| **Current → 1.61** | 2026-08-17 | Health\|devices / reports\|alarms; browse restore; alarm still-active, ack, reset |
| Archive v1.60 | 2026-08-17 | Snapshot before four-panel order, browse restore, and alarm ack/reset |
| **Current → 1.60** | 2026-08-17 | Equal 2×2 panel grid (health/alarms then devices/reports) |
| Archive v1.59 | 2026-08-17 | Snapshot before UI layout / browse restore / alarm acknowledge |
| **Current → 1.59** | 2026-08-17 | Archive/restore device+report lists; keep-OPC-only clear |
| Archive v1.58 | 2026-08-17 | Snapshot before list archive / keep-OPC-only |
| **Current → 1.58** | 2026-08-17 | ALL ACTIVE vs OPC counts; all/OPC Running device-list views |
| Archive v1.57 | 2026-08-17 | Snapshot before device-list view filters |
| **Current → 1.57** | 2026-08-17 | Device list: add new; delete only if no reports; UI shows DB list |
| Archive v1.56 | 2026-08-17 | Snapshot before device-list retention |
| **Current → 1.56** | 2026-08-17 | Send `HIMA_SAPI_user_session_id` with exact casing (`http.client`, not urllib) |
| Archive v1.55 | 2026-08-17 | Snapshot before session-header casing fix |
| **Current → 1.55** | 2026-08-17 | Refresh plugin session after SILworX project open; retry API attach |
| Archive v1.54 | 2026-08-17 | Snapshot before plugin session refresh |
| **Current → 1.54** | 2026-08-17 | Serialize Stop vs Start; plugin discovery off start thread |
| Archive v1.53 | 2026-08-17 | Snapshot before Stop/Start overlap hang fix |
| **Current → 1.53** | 2026-08-17 | Fix Stop→Start hang (`health.stopping` + start blocked on OPC refresh) |
| Archive v1.52 | 2026-08-17 | Snapshot before Stop/Start hang fix |
| **Current → 1.52** | 2026-08-17 | Never open SILworX project; API only if user has project open, else OPC |
| Archive v1.51 | 2026-08-17 | Snapshot before attach-only / no Mode A |
| **Current → 1.51** | 2026-08-14 | Remove separate Case 2; unified API→OPC mode |
| Archive v1.50 | 2026-08-14 | Snapshot before Case 2 removal |
| **Current → 1.50** | 2026-08-14 | API down → periodic OPC device-list scan (`opc_fallback`) |
| Archive v1.49 | 2026-08-14 | Snapshot before OPC fallback poll |
| **Current → 1.49** | 2026-08-14 | G-11: SILworX uninstall → keep running; release blockers; Case 2 OPC |
| Archive v1.48 | 2026-08-14 | Snapshot before G-11 OPC switch |
| **Current → 1.48** | 2026-08-14 | First-run 3 folders; DB in Database; new CSV → type + auto report template |
| Archive v1.47 | 2026-08-14 | Snapshot before first-run/template clarification |
| **Current → 1.47** | 2026-08-14 | Actually **move** legacy Reports into station root; remove old `C:\HIMA Automated Prooftest Reports` |
| Archive v1.46 | 2026-08-14 | Snapshot before migrate-move fix |
| **Current → 1.46** | 2026-08-14 | Station root `C:\HIMA Prooftest Reporting Tool` (Results Structures, Reports, Database) |
| Archive v1.45 | 2026-08-14 | Snapshot before station-root relocation |
| **Current → 1.45** | 2026-08-14 | Clarify globals vs Results Structure CSVs (docstrings); paired SPEC v1.45 |
| Archive v1.43 | 2026-08-14 | Snapshot before v1.45 clarification |
| **Current → 1.43** | 2026-08-12 | ProofTest_* DDL from Results CSVs; no runtime SQL template folder |
| **Current → 1.42** | 2026-08-12 | First start: folder + SQL DB + nine ProofTest_* tables; schema sync on engine start |
| **Current → 1.40** | 2026-08-12 | Fix Stop vs in-flight Start race; immediate stop flags |
| Archive v1.39 / Current → 1.39 | 2026-08-12 | Fix UI Start after Stop: clear API suspend; `starting` health; unlock during OPC refresh |
| Archive v1.38 | 2026-08-12 | Snapshot before Start-after-Stop fix (held v1.38 engine-stop UI behaviour) |
| Current → 1.38 | 2026-08-06 | UI Stop keeps web host; Start restarts engine; `/api/stop` vs `/api/shutdown` |
| Archive v1.37 | 2026-08-06 | Snapshot before engine-stop / UI-alive change |
| Archive v1.36 | 2026-08-06 | Fix UI stop leaving plugin monitor running (OPC lock hang) |
| Archive v1.35 | 2026-07-01 | Fix `/api/health` blocking under OPC; UI false NetworkError banner |
| Archive v1.34 | 2026-07-01 | Fix `run_service.ps1` line continuations breaking auto-start |
| Archive / Current → 1.33 | 2026-07-01 | Auto-start at **logon**; `health_check_wait_sec` 120 |
| Archive / Current → 1.32 | 2026-06-19 | Windows auto-start Task Scheduler |
| Legacy v1.31 … v1.11 | 2026-06 | Pre-Current policy: one folder per SPEC (frozen under `Codes\` and/or `Archive\`) |

---

## Collected modifications (newest first)

### Version 1.77 (2026-08-20)

**Paired SPEC:** v1.64.

R1–R7 hygiene after Gaps A/B/C: `ArchivePort` + `AnnexListArchiveAdapter` (QueryService no annex import); `resolve_html_templates_seed` prefers Documents over Z; `validate_sql_database_name`; `require_auth_when_non_local` / `auth_bind_warning`; UI unknown-type placeholder and Connect/Disconnect this-tool-only titles; `SilworxSyncTriggers` / `sync_device_list_via_api` aliases; pin `fastapi==0.141.1` + `starlette==1.3.1` (pip-audit clean); layer tests **54/54**.

### Version 1.76 (2026-08-20)

**Paired SPEC:** v1.64.

Finish unified cutover Gaps A/B/C: shaped OPC-only discover (`opc_discover.py`, no invent-as-identity); `CatalogService.run_station_refresh` uses domain refresh (step03 sync is test shim); production poll = `LiveTestService` via thin `ProoftestMonitor`; edge tests T1–T24; docs + security refresh; `python-multipart` → 0.0.31.

### Version 1.75 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.74.

Post-architecture audit: stop dual catalog write (no domain `refresh_catalog` after step03 sync); UI sort + SILworX “this tool” badge wording; add `docs/` inventory, OLD-vs-NEW, cleanup, audits, security, as-built architecture.

### Version 1.74 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.73.

Enforce layer purity: Presentation controllers call `ApplicationFacade` only (no `service.db` / annex fallbacks). Move production `RefreshCatalog` body into `CatalogService.run_station_refresh`; WorkerHost `refresh` delegates. Gate 11 attaches a facade mock on `service.app`.

### Version 1.73 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.72.

Move `open_graphic_interface.ps1` into `Dev tools/`. On station setup (`ensure_first_run`), create Desktop shortcut **HIMA Prooftest Report.lnk** that runs that script (opens the web UI; service must already be running).

### Version 1.72 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.71.

Move optional branding helper `sync_gui_images.ps1` from solution root into `Dev tools/` with `Dev tools/README.md` clarifying it is not runtime. Prefer Documents (then Z:) asset path for `7- Images for the graphical interface`.

### Version 1.71 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.70.

Remove unused standalone SILworX plugin helpers: `Annex codes/Plugin/annex_plugin.py`, `run_plugin.ps1`, `run_plugins_all.ps1`. Production session handling remains `annex_plugin_monitor.py` inside the service.

### Version 1.70 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.69.

Remove unused `Tool Steps/step02_database.py` re-export shim. Retarget `test_step5_sql.py` to import `TEMPLATE_MAP` / `generate_missing_templates` from `prooftest.annex_database`.

### Version 1.69 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.68.

Remove stale Tier B clutter from Current: `Annex codes/data/`, root `sync_markers/`, root start/crash logs, and all `__pycache__`. Keep `Plugin/message_log.json` for review. Point Tool test `SYNC_MARKERS` at `Tool test/data/sync_markers`.

### Version 1.68 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.67.

Remove unused dead modules: `Tool Steps/step06_reports.py` (Step 6 re-export shim) and `Annex codes/Stop service/annex_start_service.py` (unused cold-start spawn). Drop `annex_start_service` from `prooftest/__init__.py` bootstrap map. Reports stay on `annex_pdf_generation`; auto-start stays on Task Scheduler → `run_service.ps1`.

### Version 1.67 (2026-08-20)

**Paired SPEC:** v1.64. Archive before change: v1.66.

Move OPC Classic DA client into Current (`Annex codes/OPC/connection_opc.py`). `annex_opc.py` loads only from that path. Sibling `Codes/Report-Tool` marked legacy (no out-of-tree OPC load).

### Version 1.66 (2026-08-20)

**Paired SPEC:** v1.63. Archive before change: v1.65.

Wire full Application facade for production: Presentation controllers call `ApplicationFacade` only (with MagicMock fallbacks for Gate 11). `ProoftestService` builds Engine/Catalog/Query/SilworxConnection + SilworxPort and OPC-only adapters. Live poll path unchanged via LiveTestService.

### Version 1.65 (2026-08-19)

**Paired SPEC:** v1.62. Archive before change: v1.64.

Presentation controllers use DB/annex adapters for test compatibility; production polling/reporting routes realtime detection through `LiveTestService` with DeviceId-keyed `RunningEdgeDetector`; report output directories are scoped by `Project/DeviceId` to prevent report mixing for identical `Device_TAG`.

### Version 1.64 (2026-08-18)

**Paired SPEC:** v1.61. Archive before change: v1.63.

Split catalog/merge/poll contracts into Domain + Application (`Annex codes/layers/`) with fake-port unit tests. Device list identity is DeviceId (Project+Configuration+Resource+TAG). GUI table adds Project and OPC server columns. Connect/Disconnect SILworX drop this tool’s API/plugin session only (engine stays up; no c3.exe kill). Alarms use S1–S7; PDF failure keeps the SQL snapshot.

### Version 1.63 (2026-08-18)

**Paired SPEC:** v1.60. Archive before change: v1.62.

Each device row stores a source: OPC server ProgID when the device is on X-OPC, otherwise the SILworX project where it was detected (`SilworxProject`). The web device list shows `OPC: …` or `Project: …` on every row.

### Version 1.62 (2026-08-18)

**Paired SPEC:** v1.59. Archive before change: v1.61.

Device-list `refresh()` and background poll start SILworX API discovery and X-OPC browse on two threads at the same time, then merge once (`api+opc` / `api` / `opc_fallback`). Health shows **API + OPC**. API still never opens a SILworX project.

### Version 1.61 (2026-08-17)

**Paired SPEC:** v1.58. Archive before change: v1.60.

Four-panel order is Health | Device list / Report list | Alarms. Archive and Clear are raised buttons; Clear hover text is “Keep OPC devices only”. After Archive the folder path is shown at the bottom of the page. Restore is Browse-upload of csv/zip. Alarms show still active vs no longer exists (60 s re-raise window), with Acknowledge and Reset.

### Version 1.60 (2026-08-17)

**Paired SPEC:** v1.57. Archive before change: v1.59.

Equal 2×2 panel grid (implementation snapshot; panel order completed in 1.61).

### Version 1.59 (2026-08-17)

**Paired SPEC:** v1.56. Archive before change: v1.58.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Keep OPC only** | Non-OPC devices with reports stayed in the list until they disappeared with no reports | Operator can clear the list to **OPC devices only**. Report files stay on disk. Later API syncs do not re-add non-OPC devices until Restore |
| **List archive** | No snapshot of the lists | Timestamped `devices.csv` + `reports.csv` (and copied report files) under `List Archives` on the station root |
| **Restore** | Not available | Operator can restore a selected archive into the device list and copy missing report files back |

### Version 1.58 (2026-08-17)

**Paired SPEC:** v1.55. Archive before change: v1.57.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Health counts** | One **Active devices** number | **ALL ACTIVE DEVICES** (listed devices) and **ACTIVE DEVICES ON OPC** (devices with a `.Running` OPC item) |
| **Device list filter** | One list of all `IsActive=1` rows | Two exclusive views: all devices (including deleted with reports) vs OPC/Running only |
| **`PresentOnOpc`** | Not stored | Set from the current OPC `.Running` browse on each device-list sync |

### Version 1.57 (2026-08-17)

**Paired SPEC:** v1.54. Archive before change: v1.56.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **New device** | Could be upserted then hidden (`IsActive=0`) or never painted in the UI | Always added and shown in the Device list |
| **Removed device** | Marked `IsActive=0` (hidden) whether or not it had reports | **Deleted** if no SQL snapshot and no HTML/PDF; **kept** if at least one report exists |
| **Web Device list** | Loaded only after Refresh; `/api/devices` returned empty while the engine was stopped; health poll did not refresh the list | Loads on page open and with the 5 s health poll; list comes from the database even if the engine is stopped |

### Version 1.56 (2026-08-17)

**Paired SPEC:** v1.53. Archive before change: v1.55.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **REST session header** | `urllib.request.Request` capitalized `HIMA_SAPI_user_session_id` to `Hima_sapi_user_session_id` | `http.client.HTTPSConnection` sends the exact HIMA name (same as `sapi.py`) |
| **SILworX attach** | Plugin token was valid, but `structuretree/info` always returned “The session ID is not valid.” | Header is recognized; API attach can succeed when a project is open |
| **Regression test** | None for header casing | `test_sapi_session_header.py` |

### Version 1.55 (2026-08-17)

**Paired SPEC:** v1.53. Archive before change: v1.54.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Plugin token after project open** | Cached `user_session_id` from before the project was opened was reused | Token is dropped; plugin WebSocket re-registers |
| **Attach retry** | `structuretree/info` “session ID is not valid” / “No project opened” → OPC immediately | Re-register, wait for a new token, retry API attach |
| **lock.ini project appears** | Device list stayed on OPC until a plugin trigger arrived (often never) | Fresh plugin session requested as soon as an open project is detected |

### Version 1.54 (2026-08-17)

**Paired SPEC:** v1.52. Archive before change: v1.53.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Stop then Start** | Start could run while Stop still joined threads / closed the DB | Start waits for Stop to finish (up to 45 s) |
| **Old poll/sync loops** | Clearing `_stop` could revive a loop that missed shutdown | Loop generation so old threads exit even if `_stop` is cleared |
| **Plugin monitor start** | Probed all SILworX API ports on the engine-start thread (~15 s) | Discovery runs in the monitor thread |
| **First device refresh** | `refresh()` blocked `start()` so health stayed `starting` | Refresh runs in a background thread after the engine is running |

### Version 1.53 (2026-08-17)

**Paired SPEC:** v1.52. Archive before change: v1.52.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Health after Stop** | `stopping: true` forever while engine is stopped | `stopping` only while stop is in progress |
| **Start after Stop** | UI aborted wait immediately; Start/Stop buttons stayed disabled | Wait continues; buttons re-enable if start does not finish |
| **Engine “running”** | Set only after first OPC/API `refresh()` (can block minutes) | Set after poll/sync loops start; refresh follows |
| **Plugin register fail** | Retry every 1 s (flooded SILworX / OPC) | Backoff up to 30 s when registration is rejected |

### Version 1.52 (2026-08-17)

**Paired SPEC:** v1.52. Archive before change: v1.51.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Mode A / `open/local`** | Service could open the `.E3` itself when no GUI project | **Forbidden** — tool never opens a SILworX project |
| **API device list** | API whenever SILworX answered | API **only** when the user has a project open (plugin attach) |
| **No project open** | Mode A open then close | **OPC scan** (`opc_fallback`) |

### Version 1.51 (2026-08-14)

**Paired SPEC:** v1.51. Archive before change: v1.50.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Case 2** | Separate `deployment_case=2` HMI / OPC-only product mode | Removed — folded into unified mode (`deployment_case` always 1) |
| **Device list** | Case 1 API path vs Case 2 OPC path | Always API when available, else OPC (`opc_fallback`) |
| **G-11** | Switch/persist Case 2 | Release SILworX engines; keep running; OPC continue; no case switch |
| **Gate 12** | Asserted Case 2 selection / Case 2 refresh | Asserts unified case=1 + OPC fallback behaviour |

### Version 1.46 (2026-08-14)

**Paired SPEC:** v1.46. Archive before change: v1.45.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Station root** | Reports / CSVs / SQLite in separate places | `C:\HIMA Prooftest Reporting Tool\` with `Results Structures\`, `HIMA Automated Prooftest Reports\`, `Database\` |
| **Results CSVs** | Package-relative or ad-hoc C: path | Runtime catalogue under station root; new `*.csv` = new Results type |

### Version 1.45 (2026-08-14)

**Paired SPEC:** v1.45. Archive before change: v1.43.

#### What changed from prior Current (1.43/1.44 docs) to 1.45

| Topic | Before | After |
|-------|--------|-------|
| **Device identity** | Easy to confuse with editing Results Structure CSVs | Docstrings state: devices = SILworX **globals** typed as one of nine Results structures |
| **CSV folder watch** | Looked like a normal device-add trigger | Documented as **type-catalogue maintenance only** |

Behaviour unchanged — documentation/comments only (`results_csv.py`, `step07_triggers.py`, `step03_device_list.py`, `config.py`, `VERSION.json`).

### Version 1.43 (2026-08-12)

**Paired SPEC:** v1.43. Archive before change: v1.41.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Table DDL** | Prefer applying `.sql` under `sql_templates` | **Generate** from Results Structure CSVs (template-style types); `.sql` optional if present |
| **Deploy** | Needed template directory on station | Ships `Results Structures\`; template path optional/empty |



### Version 1.42 (2026-08-12)

**Supersedes code 1.41 / archive snapshot v1.40.** Paired SPEC: v1.42.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **First-start SQL** | DB connect created the database; tables waited for refresh/device sync | After connect + CSV load, **all nine** `ProofTest_*` tables are created from templates immediately |
| **Templates path** | `solution.ini` pointed at `Z:\...` | Prefer `C:\Project\Report Solution\2- SQL Tables template` with C:/Z: fallback resolver |

#### Files touched

| File | Change |
|------|--------|
| `Tool Steps/service.py` | `sync_schema_case2` on engine start (G-05 / Step 1.3) |
| `Tool Steps/config.py` | `resolve_sql_templates()` |
| `solution.ini` | `sql_templates` → C:\ path |
| `VERSION.json` | 1.42 |



### Version 1.40 (2026-08-12) — current

**Supersedes 1.39.** Active: `HIMA-Prooftest-Solution-Current`. Prior archived as `Archive/HIMA-Prooftest-Solution-v1.39`.

#### What changed from v1.39 to v1.40

| Topic | v1.39 | v1.40 (change) |
|-------|-------|----------------|
| **UI Stop vs Start race** | Stop cleaned up, but an in-flight Start could continue and recreate plugin/OPC | Start uses a **token**; Stop increments token and aborts in-flight Start |
| **Stop responsiveness** | Stop work only in background thread | `/api/stop` sets stop flags **in the HTTP request** immediately |

#### Files touched for v1.40

| File | Change |
|------|--------|
| `Tool Steps/service.py` | `_start_token`; `_start_aborted`; `request_stop_flags` |
| `Graphic Interface/app.py` | Immediate stop flags; version 1.40.0 |
| `Graphic Interface/static/app.js` | Abort `waitForEngineRunning` on Stop |
| `VERSION.json` | 1.40 |

---

### Version 1.39 (2026-08-12)

**Supersedes code/spec 1.38.** Active: `HIMA-Prooftest-Solution-Current`. Prior tree archived as `Archive/HIMA-Prooftest-Solution-v1.38`.

#### What changed from v1.38 to v1.39

| Topic | v1.38 | v1.39 (change) |
|-------|-------|----------------|
| **UI Start after Stop** | `/api/health` could block on OPC during start; SILworX API stayed **suspended** after Stop | Clear API suspend on Start; health returns fast `starting`; OPC refresh without holding engine lock |
| **UI feedback** | Start looked dead (health timeout) | UI polls until `engine_running` with “starting” banner |

#### Files touched for v1.39

| File | Change |
|------|--------|
| `Tool Steps/service.py` | `_starting`; unlock during start body; health starting/stopped paths |
| `Tool Steps/step07_triggers.py` | `prepare_for_engine_start()` clears G-19 suspend |
| `Graphic Interface/static/app.js` | `waitForEngineRunning`; starting button state |
| `Graphic Interface/app.py` | `start_in_progress`; version 1.39.0 |
| `VERSION.json` | 1.39 |

---

### Version 1.38 (2026-08-06)

**Supersedes 1.33 line for UI Stop/Start** (interim code archives 1.34–1.37 on the path). Active was Current; prior snapshot `Archive/HIMA-Prooftest-Solution-v1.37`.

#### What changed (engine stop vs process exit)

| Topic | Before | v1.38 (change) |
|-------|--------|----------------|
| **UI Stop** | `POST /api/shutdown` exited the whole process — graphic interface died | **`POST /api/stop`** stops the **engine** only; web host / UI stay on `:8080` |
| **UI Start** | Spawned a second `main.py` when the process was dead | Restarts the engine **in-process** while the UI is already open |
| **G-11 uninstall** | Same as UI Stop | Unchanged: `stop_service.ps1` / `POST /api/shutdown` / signals — **process exit** |
| **Health** | `stopping` only | Adds `engine_running`, `web_host_alive` |

#### Files touched for v1.38

| File | Change |
|------|--------|
| `Tool Steps/service.py` | Restartable engine; `request_shutdown(..., exit_process=)` |
| `Graphic Interface/app.py` | `POST /api/stop`; Start in-process; Shutdown = process exit |
| `Graphic Interface/static/app.js` | Stop/Start messaging; calls `/api/stop` |
| `Annex codes/Stop service/annex_stop_service.py` | Engine-stopped state; web host note |
| `main.py` | Log both `/api/stop` and `/api/shutdown` |
| `VERSION.json` | 1.38 |

---

### Version 1.37 (2026-08-06) — archived snapshot

**Archive reason:** UI Stop keeps web host alive; engine restartable from Start (pre-implementation snapshot / intermediate).

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.37`.

---

### Version 1.36 (2026-08-06) — archived snapshot

**Archive reason:** Fix UI stop leaving plugin monitor running (OPC lock hang).

| Topic | Before | After |
|-------|--------|-------|
| **UI Stop hang** | Shutdown called OPC `invalidate_cache` before stopping plugin monitor; lock hang left plugin retries against SILworX | Stop plugin monitor **first**; timed OPC lock; signal uvicorn exit early on process exit |

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.36`.

---

### Version 1.35 (2026-07-01) — archived snapshot

**Archive reason:** Fix health API blocking and UI false NetworkError banner.

| Topic | Before | After |
|-------|--------|-------|
| **`/api/health`** | Could block under OPC load | Non-blocking `health_snapshot()` path |
| **UI banner** | NetworkError stayed after recovery | Clear banner on success; require repeated failures |

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.35`.

---

### Version 1.34 (2026-07-01) — archived snapshot

**Archive reason:** Fix `run_service.ps1` broken line continuations breaking auto-start.

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.34`.

---

### Version 1.33 (2026-07-01)

**Supersedes 1.32.** Active: `HIMA-Prooftest-Solution-Current`. Archive: `Archive/HIMA-Prooftest-Solution-v1.33` (and related).

#### What changed from v1.32 to v1.33

| Topic | v1.32 | v1.33 (change) |
|-------|-------|----------------|
| **Auto-start trigger** | System **startup** as **SYSTEM** only | **`auto_start_trigger`** — default **`logon`** (mapped **Z:** works); optional **`startup`** |
| **Health check wait** | Fixed ~25 s sleep | **`health_check_wait_sec`** (default **120 s**), poll until `/api/health` responds |
| **Task action** | Script on **Z:** without WorkingDirectory/UNC | **WorkingDirectory** set; UNC for SYSTEM tasks |

#### Files touched for v1.33

| File | Change |
|------|--------|
| `solution.ini` | `auto_start_trigger = logon`, `health_check_wait_sec = 120` |
| `Tool Steps/config.py` | Config keys |
| `Annex codes/Stop service/annex_windows_auto_start.ps1` | Logon vs startup; UNC; WorkingDirectory |
| `run_service.ps1` | Health poll; stderr / auto_start log |

---

### Version 1.32 (2026-06-19)

**Supersedes 1.31 (legacy folder policy → Current).**

#### What changed from v1.31 to v1.32

| Topic | v1.31 | v1.32 (change) |
|-------|-------|----------------|
| **Windows auto-start** | Manual `run_service.ps1` only | Task Scheduler **`HIMA-Prooftest-Service`**; `auto_start = true` |
| **Install / remove** | — | `install_auto_start.ps1`, `uninstall_auto_start.ps1`; sync from `run_service.ps1` |

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.32`.

---

### Versions 1.31 – 1.11 (legacy / frozen)

Under the **old** policy, each SPEC bump created a new `HIMA-Prooftest-Solution-v{x.y}` folder (some also copied into `Archive\`). Those trees are **frozen**. Highlights (see also Spec History of Modifications):

| Version | Theme |
|---------|--------|
| **1.31** | Device/report list search UI |
| **1.29–1.30** | Report storage under `C:\HIMA Automated Prooftest Reports`; Gates 12–13; experimental hero (1.30) |
| **1.28** | Web GUI Start/Stop buttons; scroll list placeholders |
| **1.27** | Gate 9 SQL insert; `OUTPUT INSERTED.ID`; cumulative SPEC summary introduced |
| **1.26** | G-22 three-layer architecture; plugin monitor / one-shot session fix |
| **1.25–1.24** | Gate 8 triggers; Gate 7 approved |
| **1.23** | G-21 multi-instance API/plugin ports 51710–51719 / 8400–8409 |
| **1.22–1.19** | G-20 SILworX process cleanup; G-19 API release when SILworX closed |
| **1.17–1.11** | G-17 annex layout; G-16 annex_* files; G-15 Tool test; G-14 steps; G-13 no globals CSV; G-12 code versioning; G-11 graceful shutdown |

---

### Versions before 1.11

Initial OPC-centric Prooftest service, multi-OPC, SQL/PDF/HTML, Case 1/2, web GUI foundations — see [Specifications/History of Modifications.md](../Specifications/History%20of%20Modifications.md) compact index and archived SPEC files.

---

## Related files

| Path | Role |
|------|------|
| [README.md](./README.md) | Code versioning policy |
| [Archive/ARCHIVE_INDEX.json](./Archive/ARCHIVE_INDEX.json) | Next archive version + archive reasons |
| [archive_current.ps1](./archive_current.ps1) | Snapshot Current before edits |
| [../Specifications/History of Modifications.md](../Specifications/History%20of%20Modifications.md) | Spec-side cumulative log |
