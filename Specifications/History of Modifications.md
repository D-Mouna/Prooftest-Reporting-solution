# History of Modifications — SPEC-001

| Field | Value |
|-------|--------|
| **Document** | Cumulative change log for SPEC-001 |
| **Paired spec** | [SPEC-001-v1.62-...](./SPEC-001-v1.62-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) (current) |
| **Location** | `Z:\Project\Report Solution\Specifications` |
| **Filename** | `History of Modifications.md` |
| **Updated** | 2026-08-19 |

> **Policy:** Each SPEC version file documents **only** what changed from its immediate predecessor. This file collects **all** version-to-version modifications for audit. Do not edit superseded SPEC files — append new sections here when publishing a new SPEC version.

---

## How to maintain

1. When creating `SPEC-001-v{X.Y}`, write `## Summary of changes` with **only** the delta from the superseded version.
2. **Copy that same delta block** into this file (newest version at the top).
3. Leave older blocks in this file unchanged.

---

## Collected modifications (newest first)

### Version 1.62 (2026-08-19)

**Supersedes v1.61.** Report folders scoped by Project/DeviceId; presentation controller refactor; production poll/report uses LiveTestService completion path.

#### What changed to v1.62

| Topic | Change |
|-------|--------|
| Report folders | Reports stored under `<Results_Type>/<Project>/<Device_TAG>/` (Project from DeviceId); legacy tag-only folders remain readable. |
| Web report lookup | `GET /api/reports` accepts `project` and/or `device_id` params so identical `Device_TAG` across projects doesn't mix report lists. |
| Production detection/reporting | Production poll uses `LiveTestService` with a `RunningEdgeDetector` keyed by `DeviceId`; snapshot INSERT + report generation happen on the completion path. |
| Presentation controllers | FastAPI routes moved into `Annex codes/layers/presentation/controllers.py` and call services only. |
| Architecture diagrams | Mermaid paired to v1.62; §7 report path includes Project; §10 shows `layers/`; new §12 layered architecture (Presentation/Application/Domain + DeviceId); PNG/SVG `01`–`12` regenerated. |

### Version 1.61 (2026-08-18)

**Supersedes v1.60.** Layered architecture; composite catalog identity; GUI Project/OPC columns; SILworX connect/disconnect without stopping SILworX.

#### What changed to v1.61

| Topic | Change |
|-------|--------|
| **Layers** | Presentation / Application / Domain / ports. Domain in `Annex codes/layers/` does not import FastAPI, OpenOPC, or pyodbc. |
| **Device identity** | DeviceId = Project + Configuration + Resource + Device_TAG. Same TAG, two projects → two rows. SILworX+OPC same DeviceId → one row. |
| **Web table** | Project and OPC server columns; sort Device_TAG, Project, OPC server. |
| **SILworX buttons** | Connect/Disconnect affect this tool’s API/plugin session only (never c3.exe / project/close GUI). |
| **Errors + tests** | Step codes S1–S7; `test_layers.py` with fake ports. |

### Version 1.60 (2026-08-18)

**Supersedes v1.59.** Per-device source on the Device Prooftest Result List and in the web UI.

#### What changed to v1.60

| Topic | Change |
|-------|--------|
| **Device source** | Each Device Prooftest Result List row records its **source**. Devices present on X-OPC are linked to the **OPC server ProgID**. Devices not on OPC are linked to the **SILworX project** where they were detected. |
| **`SilworxProject`** | New column on `DeviceProoftestResultList` stores the API project name at detection. |
| **Web device list** | Each row shows a source line: `OPC: {ProgID}` or `Project: {project name}`. |

### Version 1.59 (2026-08-18)

**Supersedes v1.58.** Device-list update/refresh queries SILworX API and X-OPC simultaneously, then merges.

#### What changed to v1.59

| Topic | Change |
|-------|--------|
| **Device list update** | Every automatic or manual device-list update/refresh queries **SILworX API and X-OPC simultaneously** (two worker threads), then **merges** the results once. |
| **Merge rules** | Union of Device_TAGs. API wins `Results_Type`, `Configuration`, and `Resource`. OPC wins `OPC_Server`, `OPC_ItemPrefix`, and `PresentOnOpc`. API-only devices are kept (not on OPC); OPC-only devices are added with NULL Configuration/Resource. |
| **`device_list_source`** | `api+opc` when both succeed; `api` when only API succeeds; `opc_fallback` when only OPC succeeds. Health card shows **API + OPC**. |
| **G-10 / G-21 / G-22 / §3.1** | Sequential “API then OPC fallback” is replaced by parallel scan. API still attaches **only** when the user has a project open (never `open/local`). If API cannot attach, its contribution is empty while OPC still runs. |
| **Architecture pictures** | Mermaid architecture, functionality catalogue, and Flow Diagram 01/02/04/05 show parallel API+OPC device-list update. |

### Version 1.58 (2026-08-17)

**Supersedes v1.57.** Four-panel order; browse restore; alarm still-active / acknowledge / reset.

#### What changed to v1.58

| Topic | Change |
|-------|--------|
| **Four-panel order** | The equal 2×2 grid is **Service health \| Device list** on the first row and **Report list \| Alarms & errors** on the second row. |
| **Clear / Archive buttons** | **Clear device list** is the visible label; hovering the button shows **Keep OPC devices only**. Archive lists and Clear device list use the same raised action-button style as other primary controls. |
| **Archive path** | After Archive, the saved folder path is shown in a status bar at the **bottom of the page**. |
| **Restore** | Restore uses **Browse restore file…** to upload `devices.csv` or a zip archive (the archive dropdown is removed). |
| **Alarms** | Each row shows **still active** or **no longer exists** (based on whether the same error has been raised again within about 60 seconds). The operator can **Acknowledge** a single alarm or **Reset alarms** for the whole list. Acknowledging does not hide a still-active condition. |

### Version 1.57 (2026-08-17)

**Supersedes v1.56.** Align the four principal panels; archive/clear button labels; browse restore; alarm acknowledge.

#### What changed to v1.57

| Topic | Change |
|-------|--------|
| **Four-panel layout** | Service health, Alarms & errors, Device list, and Report list are aligned in a 2×2 grid. |
| **Health card order** | First: **Service** then **Database**. Middle: **Device list**, **SILworX session**, **Plugin session**, **Queue depth**. Last: **ALL DEVICES** and **OPC ACTIVE DEVICES**. |
| **Device toolbar** | Search and the archive-before-clear checkbox sit bottom-right, immediately above the device list. The checkbox has no white fill; it uses the panel background. **Clear device list** is the button label; hover shows “Keep OPC devices only”. Archive and Clear are full action buttons. After Archive, the archive folder path is shown at the bottom of the page. Restore includes a **Browse** control to upload `devices.csv` or a zip archive. |
| **Alarms** | Each alarm shows whether it is **still active** or **no longer exists**. The operator can **acknowledge** an alarm and **reset** the alarm list. |

### Version 1.56 (2026-08-17)

**Supersedes v1.55.** Archive/restore of device and report lists; keep-OPC-only clear.

#### What changed to v1.56

| Topic | Change |
|-------|--------|
| **Keep OPC only** | The operator can **clear** the Device Prooftest Result List so that **only devices present on X-OPC** (`.Running`) remain. Devices not on OPC are removed from the list even if they still have reports. Report files on disk are not deleted. |
| **List archive** | Before clearing (or at any time), the operator can **archive** the current device list and report list to CSV under the station root (`List Archives\<timestamp>\`: `devices.csv`, `reports.csv`, `manifest.json`, plus a copy of report files). |
| **Restore** | The operator can **restore** a selected archive: device rows are put back in the list, and missing report files are copied back from the archive. |
| **Health counts** | Show **ALL DEVICES** and **OPC ACTIVE DEVICES** as a pair (side by side or stacked). Only **OPC ACTIVE DEVICES** uses the green healthy colour. |

### Version 1.55 (2026-08-17)

**Supersedes v1.54.** Health counts and device-list view options.

#### What changed to v1.55

| Topic | Change |
|-------|--------|
| **Health counts** | The graphic interface must show **ALL ACTIVE DEVICES** (every listed device: currently detected plus deleted devices kept because they have reports) and **ACTIVE DEVICES ON OPC** (how many of those currently exist on X-OPC with a `.Running` item). |
| **Device list views** | Two exclusive options: (1) show **all** listed devices, including deleted ones that still have reports; (2) show **only** devices that exist on OPC and are monitored via the Running bit. |

### Version 1.54 (2026-08-17)

**Supersedes v1.53.** Device list add / keep / delete rules, and the web list must show them.

#### What changed to v1.54

| Topic | Change |
|-------|--------|
| **New device** | When a Prooftest device is detected (API globals or OPC scan), it **must appear** in the Device Prooftest Result List and in the web **Device list**. |
| **Removed device, no reports** | If a previously listed device is no longer detected and it has **no** Prooftest report (no SQL snapshot and no HTML/PDF file), **delete** it from the list. |
| **Removed device, has reports** | If it has **at least one** Prooftest report, **keep** it in the list so past reports remain reachable. |
| **Web Device list** | The UI must show the current database list on load and on the health poll — not only after a successful Refresh, and not only while the engine is running. |

### Version 1.53 (2026-08-17)

**Supersedes v1.52.** Refresh the plugin `user_session_id` after the user opens a SILworX project so the API device-list path can attach.

#### What changed to v1.53

| Topic | Change |
|-------|--------|
| **Plugin session after project open** | A `user_session_id` received while SILworX has no project (or before the user opens one) is **invalid** after the project is opened. SILworX does **not** always emit `TRIGGER_SESSION_ID_CHANGED` on project open. |
| **Required recovery** | When `lock.ini` shows a newly opened project, or when `structuretree/info` returns “session ID is not valid” / “No project opened” while a project is open, the service **must drop** the cached token, **re-register** the plugin WebSocket on that port, wait for a new `user_session_id`, and retry attach. |
| **Still never open a project** | The tool still must **not** call `open/local`. If there is still no user-open project after the retry, use **OPC scan**. |

### Version 1.52 (2026-08-17)

**Supersedes v1.51.** The report tool never opens a SILworX project. API device list only when the user has a project open; otherwise OPC scan.

#### What changed to v1.52

| Topic | Change |
|-------|--------|
| **Never open a SILworX project** | The report tool **must not** call `POST /project/open/local`. Mode A is **removed**. |
| **API device list** | Use SILworX API **only when the user has a project open** (attach to that session; never `project/close` on it). |
| **No project open** | Update the device list by **scanning X-OPC** (`opc_fallback`). |
| **G-10 / G-21 / §3.5** | Align: attach-only; OPC when no user-open project |


### Version 1.51 (2026-08-14)

**Supersedes v1.50.** Remove separate Case 2 product mode. One unified operating mode (`deployment_case = 1`): API device list when available, otherwise OPC scan. G-11 keeps running on OPC without switching/persisting Case 2.

#### What changed to v1.51

| Topic | Change |
|-------|--------|
| **Remove separate Case 2** | Former HMI / OPC-only Case 2 is **part of the single unified operating mode** (always `deployment_case = 1`). No product switch to Case 2. |
| **Device list** | Prefer SILworX API when available; otherwise **OPC scan** (`opc_fallback`) — same path for engineering, HMI, API down, and after G-11 uninstall |
| **G-11** | On SILworX uninstall: release API/plugin/`c3.exe`, **keep running**, continue OPC device list — **do not** persist Case 2 |
| **Step 1 / config** | Auto-detect Case 2 removed; `deployment_case` always 1; `auto_detect_case` obsolete |
| **Gate 12** | Retargeted to OPC-fallback checks within unified mode (`test_step12_case2.py`) |


### Version 1.50 (2026-08-14)

**Supersedes v1.49.** If SILworX/API is not available, update the device list by periodic X-OPC scanning (Case 1 `opc_fallback`).


### Version 1.49 (2026-08-14)

**Supersedes v1.48.** G-11: SILworX uninstall → keep Report Solution running; release API/plugin/`c3.exe`; switch device list to Case 2 OPC scanning.


### Version 1.48 (2026-08-14)

**Supersedes v1.47.** First-run creates `C:\HIMA Prooftest Reporting Tool` with Database / Reports / Results Structures; new CSV → new type + auto Proof-test report template.


### Version 1.46 (2026-08-14)

**Supersedes v1.45.** Station runtime root: `C:\HIMA Prooftest Reporting Tool` (Results Structures, Reports, Database).


### Version 1.45 (2026-08-14)

**Supersedes v1.44.** Clarification only (behaviour unchanged).

#### What changed from v1.44 to v1.45

| Topic | v1.44 | v1.45 (change) |
|-------|-------|----------------|
| **Device add** | Easy to confuse with editing Results Structure CSVs | Engineer creates **SILworX globals** typed as one of the nine Results structures |
| **CSV files** | Runtime DDL source | Same + explicitly **fixed type catalogue**; CSV folder watch = definition maintenance only |


### Version 1.44 (2026-08-12)

**Supersedes v1.43.** Spec-only. Active code: `HIMA-Prooftest-Solution-Current`.

#### What changed from v1.43 to v1.44

| Topic | v1.43 | v1.44 (change) |
|-------|-------|----------------|
| **G-14 … G-17** | Under §2 general requirements | Under **Solution structure** (not runtime requirements) |
| **Manual edits** | Present in v1.43 | Preserved |


### Version 1.43 (2026-08-12)

**Supersedes v1.42.** Active code: `HIMA-Prooftest-Solution-Current`.

#### What changed from v1.42 to v1.43

| Topic | v1.42 | v1.43 (change) |
|-------|-------|----------------|
| **SQL DDL source** | Runtime oriented to `.sql` template files | **Generator** from Results Structure CSVs; template folder = design reference only |
| **Deployed PC** | Implied need for `2- SQL Tables template` | **No** template folder required |
| **Bundled data** | CSVs often only on engineering share | `Results Structures\` shipped inside Current |


### Version 1.42 (2026-08-12)

**Supersedes v1.41.** Active code folder: `HIMA-Prooftest-Solution-Current`.

#### What changed from v1.41 to v1.42

| Topic | v1.41 | v1.42 (change) |
|-------|-------|----------------|
| **G-05 / first start** | Folder only on first start | Folder + SQL DB **`HIMA Automated Prooftest`** + nine `ProofTest_*` tables from templates |
| **Template path** | Primarily `Z:\...\2- SQL Tables template` | Primary **`C:\Project\Report Solution\2- SQL Tables template`** |
| **Engine start** | Schema sync during refresh | Schema sync immediately after DB connect / structure load |

#### Files touched for v1.42

| File | Change |
|------|--------|
| `SPEC-001-v1.42-...` | G-05, Step 1.3 |
| `Tool Steps/service.py` | Initial schema on start |
| `Tool Steps/config.py` | Template path fallback |
| `solution.ini` / `VERSION.json` | Paths / 1.42 |


### Version 1.41 (2026-08-12)

**Supersedes v1.39.** Active code folder: `HIMA-Prooftest-Solution-Current`. Spec-only: relocate G-12 (no runtime behaviour change). Code tree may already carry v1.40 Stop/Start race fixes in `VERSION.json` history.

#### What changed from v1.39 to v1.41

| Topic | v1.39 | v1.41 (change) |
|-------|-------|----------------|
| **G-12 placement** | Listed under §2 **General specifications** (with runtime G-xx requirements) | Moved under **Versioning** — G-12 is a **versioning / process** rule, not a runtime solution requirement |
| **G-12 wording** | Referred to copying `HIMA-Prooftest-Solution-v{x.y}` per SPEC (legacy folder policy) | Aligned with **Current + Archive** policy ([Codes/README.md](../Codes/README.md)) |

#### Description of v1.41 modifications

1. Removed **G-12** from the §2 general requirements table.
2. Expanded the document **Versioning** section and placed **G-12** there with Current/Archive wording.

#### Files touched for v1.41

| File | Change |
|------|--------|
| `SPEC-001-v1.41-...` | Versioning section; G-12 relocated out of §2 |
| `History of Modifications.md` | Delta prepended |
| `Specifications/README.md` | Current pointer → 1.41 |
| `VERSION.json` | 1.41 (spec pairing) |


### Version 1.39 (2026-08-12)

**Supersedes v1.38.** Active code folder: `HIMA-Prooftest-Solution-Current` (archived prior tree as `HIMA-Prooftest-Solution-v1.38`).

#### What changed from v1.38 to v1.39

| Topic | v1.38 | v1.39 (change) |
|-------|-------|----------------|
| **UI Start after Stop** | Health blocked on OPC during start; API stayed suspended after Stop | Clear API suspend; fast `starting` health; OPC refresh without engine lock |
| **UI feedback** | Looked dead after Start | Poll until `engine_running` with starting banner |

#### Files touched for v1.39

| File | Change |
|------|--------|
| `Tool Steps/service.py` | `_starting`; unlock during start; health starting path |
| `Tool Steps/step07_triggers.py` | `prepare_for_engine_start()` |
| `Graphic Interface/static/app.js` | `waitForEngineRunning` |
| `Graphic Interface/app.py` | `start_in_progress` |
| `VERSION.json` | 1.39 |


### Version 1.38 (2026-08-06)

**Supersedes v1.33.** Active code folder: `HIMA-Prooftest-Solution-Current` (archived prior tree as `HIMA-Prooftest-Solution-v1.37`).

#### What changed from v1.33 to v1.38

| Topic | v1.33 | v1.38 (change) |
|-------|-------|----------------|
| **UI Stop** | `POST /api/shutdown` exited the whole process — graphic interface died | **`POST /api/stop`** stops the **engine** only; web host / UI stay on `:8080` |
| **UI Start** | Spawned a second `main.py` when the process was dead | Restarts the engine **in-process** while the UI is already open |
| **G-11 uninstall** | Same as UI Stop | Unchanged path: `stop_service.ps1` / `POST /api/shutdown` / signals — **process exit** |
| **Health** | `stopping` only | Adds `engine_running`, `web_host_alive`; health still answers when engine is stopped |

#### Files touched for v1.38

| File | Change |
|------|--------|
| `Tool Steps/service.py` | Restartable engine; `request_shutdown(..., exit_process=)`; health when stopped |
| `Graphic Interface/app.py` | `POST /api/stop`; Start in-process; Shutdown = process exit |
| `Graphic Interface/static/app.js` | Stop/Start messaging; calls `/api/stop` |
| `Annex codes/Stop service/annex_stop_service.py` | Engine-stopped state; web host note |
| `main.py` | Log both `/api/stop` and `/api/shutdown` |
| `VERSION.json`, `README.md` | Spec 1.38 |
| `SPEC-001-v1.39-...md` | §5.1 #7, §5.4, §5.5 |
| `History of Modifications.md` | Cumulative log started / updated |

### Version 1.33 (2026-07-01)

**Supersedes v1.32.** Active code folder: `HIMA-Prooftest-Solution-Current`.

#### What changed from v1.32 to v1.33

| Topic | v1.32 | v1.33 (change) |
|-------|-------|----------------|
| **Auto-start trigger** | At **system startup** as **SYSTEM** only | **`auto_start_trigger`** — default **`logon`** (current user; mapped **Z:** works); optional **`startup`** (SYSTEM + UNC path resolution) |
| **Health check wait** | `run_service.ps1` fixed **25 s** sleep | **`health_check_wait_sec`** (default **120 s**), poll every 10 s until `/api/health` responds |
| **Task action** | Script path on **Z:** | **WorkingDirectory** set; mapped drives resolved to **UNC** for SYSTEM tasks |

#### Files touched for v1.33

| File | Change |
|------|--------|
| `solution.ini` | `auto_start_trigger = logon`, `health_check_wait_sec = 120` |
| `Tool Steps/config.py` | `auto_start_trigger`, `health_check_wait_sec` |
| `Annex codes/Stop service/annex_windows_auto_start.ps1` | Logon vs startup trigger; UNC path; WorkingDirectory |
| `run_service.ps1` | Poll health up to `health_check_wait_sec`; stderr log; relative `solution.ini` |
| `SPEC-001-v1.33-...md` | §5.6 auto-start trigger; health wait |

### Version 1.32 (2026-06-19)

**Supersedes v1.31.** Active code folder: `HIMA-Prooftest-Solution-Current` (archived as `HIMA-Prooftest-Solution-v1.33` before v1.33 edits).

#### What changed from v1.31 to v1.32

| Topic | v1.31 | v1.32 (change) |
|-------|-------|----------------|
| **Windows auto-start** | Manual `run_service.ps1` only | **`auto_start = true`** — Task Scheduler task **`HIMA-Prooftest-Service`** runs `run_service.ps1` **at Windows startup** (delay `auto_start_delay_sec`, default 90 s) |
| **Install / remove** | — | `install_auto_start.ps1`, `uninstall_auto_start.ps1`; `run_service.ps1` **syncs** task when `auto_start=true` |

#### Files touched for v1.32

| File | Change |
|------|--------|
| `solution.ini` | `auto_start = true`, `auto_start_delay_sec = 90` |
| `Tool Steps/config.py` | `auto_start`, `auto_start_delay_sec` |
| `Annex codes/Stop service/annex_windows_auto_start.ps1` | Task Scheduler register / sync |
| `install_auto_start.ps1`, `uninstall_auto_start.ps1` | Operator scripts |
| `run_service.ps1` | Sync auto-start task after start |
| `SPEC-001-v1.32-...md` | §5.6 Windows auto-start |

### Version 1.31 (2026-06-19)

#### What changed from v1.29 to v1.31

| Topic | v1.29 | v1.31 (change) |
|-------|-------|----------------|
| **Device list search** | Scroll list only | **Search field** above device list — type to highlight matches and scroll to the first; **Enter** cycles matches; **all devices remain visible** |
| **Report list search** | Scroll list only | **Search field** above report list — same behaviour for report file names |

#### Files touched for v1.31

| File | Change |
|------|--------|
| `Graphic Interface/static/index.html` | `#device-search`, `#report-search` inputs |
| `Graphic Interface/static/app.js` | `applyListSearch`, `setupListSearch` |
| `Graphic Interface/static/style.css` | `.list-search-input`, `.search-hit`, `.search-current` |
| `Annex codes/Tool test/test_step11_web_ui.py` | Search field markers |
| `SPEC-001-v1.31-...md` | §5.1 list search behaviour |

### Version 1.29 (2026-06-19)

**Supersedes v1.28.** Active code folder was `HIMA-Prooftest-Solution-v1.29` (now **frozen**).

#### What changed from v1.28 to v1.29

| Topic | v1.28 | v1.29 (change) |
|-------|-------|----------------|
| **Report storage location** | Step 1.2 names `C:\HIMA Automated Prooftest Reports`, but `solution.ini` used `Z:\Project\Report Solution\Reports` as `output_directory` | **All PDF/HTML reports** are written under **`C:\HIMA Automated Prooftest Reports`** (same as `first_run_folder` / Step 1.2). `[Reports] output_directory` must match that path |
| **Mirror copy** | Optional `local_mirror` could differ from output | Mirror copy is **skipped** when `local_mirror` equals `output_directory`; default is the same `C:\` root |
| **Code folder** | Misplaced `X-HART_*_Results` could appear under solution root if paths were wrong | Config normalizes empty/relative output to `first_run_folder`; report roots deduplicated in Step 1 |

#### Files touched for v1.29

| File | Change |
|------|--------|
| `solution.ini` | `output_directory` → `C:\HIMA Automated Prooftest Reports` |
| `Tool Steps/config.py` | Default `report_output` to `first_run_folder` |
| `Tool Steps/step01_setup.py` | Deduplicate report roots before creating hierarchy |
| `Annex codes/PDF generation/annex_pdf_generation.py` | Skip mirror write when mirror equals output |
| `SPEC-001-v1.29-...md` | Step 1.2 / §6 clarified |

#### Gate 12 update (same v1.29 — no new spec/code version)

| Topic | Before Gate 12 | After Gate 12 (v1.29) |
|-------|----------------|------------------------|
| **Gate 11** | In progress | **Approved** 2026-06-18 |
| **Gate 12** | Code done; validation pending | **`test_step12_case2.py`** — **Approved** 2026-06-19; Case 2 OPC device list, schema sync, background poll |

#### Files touched for Gate 12 (v1.29)

| File | Change |
|------|--------|
| `Annex codes/Tool test/test_step12_case2.py` | **New** gate test |
| `SPEC-001-v1.29-...md` | §5 gate table + Gate 12 criteria |

#### Gate 12 approval (v1.29)

Gate 12 (**Case 2 deployment**, `test_step12_case2.py`) is **formally approved**. Gate 13 may proceed.

#### Gate 13 update (same v1.29 — no new spec/code version)

| Topic | Before Gate 13 | After Gate 13 (v1.29) |
|-------|----------------|------------------------|
| **`/api/health` blocking** | Could call blocking OPC browse | **`OpcManager.health_snapshot()`** — cached server list only |
| **Web auth** | Not specified | Optional `[Web] auth_enabled` + `auth_token`; `X-Prooftest-Token` or `?token=`; localhost bypass |
| **Column mapping** | Partial | **`verify_template_placeholder_mapping()`** — all twelve HIMA templates |

#### Files touched for Gate 13 (v1.29)

| File | Change |
|------|--------|
| `Annex codes/OPC/annex_opc.py` | `health_snapshot()` (non-blocking) |
| `Tool Steps/service.py` | `health()` uses snapshot |
| `Graphic Interface/app.py` | Auth middleware |
| `Graphic Interface/static/app.js` | Token header + `?token=` persistence |
| `Tool Steps/config.py` | `auth_*` settings; disable auth if token empty |
| `Annex codes/PDF generation/annex_pdf_generation.py` | `verify_template_placeholder_mapping()` |
| `Annex codes/Tool test/test_step13_hardening.py` | **New** gate test |
| `solution.ini` | `[Web] auth_*` documented |

#### Gate 13 approval (v1.29)

Gate 13 (**Hardening**, `test_step13_hardening.py`) is **formally approved**. Roadmap gates **0–13** are complete on v1.29.

### Version 1.28 (2026-06-19)

**Supersedes v1.27.** Active code folder was `HIMA-Prooftest-Solution-v1.28` (now **frozen**).

#### What changed from v1.27 to v1.28

| Topic | v1.27 | v1.28 (change) |
|-------|-------|----------------|
| **Web UI — service control** | Stop via `POST /api/shutdown` / `stop_service.ps1` only | **Start service** and **Stop service** buttons in the Web GUI; `POST /api/start` (localhost) spawns background `main.py` (same as `run_service.ps1`) |
| **Web UI — scroll lists** | Placeholders varied; lists could appear empty without visible panel | Device and report **scrolling lists always visible**; show **`(No device selected)`** and **`(No report selected)`** when empty |
| **Specification file** | `SPEC-001-v1.27-...md` (active) | **`SPEC-001-v1.28-...md`** (active); v1.27 file **immutable** |
| **Code folder** | `HIMA-Prooftest-Solution-v1.27` (active) | **`HIMA-Prooftest-Solution-v1.28`** (active); v1.27 frozen in `VERSION.json` |

#### Description of v1.28 modifications

1. **Start / Stop service buttons (§5.1 #7).** Operators can start the background Prooftest process from the Web GUI (`POST /api/start`, localhost only) or stop it completely (`POST /api/shutdown`). Start is disabled while the service is already running; Stop triggers graceful shutdown (G-11).

2. **Persistent scroll list placeholders (§5.1 #1–2).** The device list and report list panels remain visible with fixed minimum height. When no devices are detected or none is selected, the device list shows **`(No device selected)`**. When no report is available or selected, the report list shows **`(No report selected)`**.

#### Files touched for v1.28

| File | Change |
|------|--------|
| `Graphic Interface/static/index.html` | Start / Stop service buttons; default list placeholders |
| `Graphic Interface/static/app.js` | Service control handlers; placeholder text |
| `Graphic Interface/app.py` | `POST /api/start` |
| `Annex codes/Stop service/annex_start_service.py` | **New** — spawn background `main.py` |
| `Tool Steps/config.py` | `ini_path` on `AppConfig` |
| `SPEC-001-v1.28-...md` | This document |
| `VERSION.json` | `spec_version` 1.28, `status: active` |

### Version 1.27 (2026-06-18)

**Supersedes v1.26.** Active code folder was `HIMA-Prooftest-Solution-v1.27` (now **frozen**).

#### What changed from v1.26 to v1.27

| Topic | v1.26 | v1.27 (change) |
|-------|-------|----------------|
| **Gate 8 status** | Done — *await your approval before Gate 9* | **Approved** 2026-06-18; Gate 9 may proceed |
| **Gate 9** | Code for Step 5 insert existed; gate test **pending** | Gate test **`test_step9_prooftest_sql.py`** — **Approved** 2026-06-18 |
| **Step 5 SQL insert (`insert_snapshot`)** | Used `SCOPE_IDENTITY()` after INSERT — often returned **`0`** on SQL Server (with `SET NOCOUNT ON`), so `ReportPath` update and row verification failed | Uses **`OUTPUT INSERTED.[ID]`** so every insert returns the real row ID |
| **§3.5 Mode B / plugin session** | One-shot plugin conflict fix was **implemented in v1.26 code** but **not fully written in the v1.26 spec** | **Documented in spec:** when `plugin_monitor_enabled = true` and monitor is running, API refresh uses monitor cache or waits — **no second** `prooftest_session_plugin` register; service log line table added |
| **Summary of changes** | Not present as a cumulative section | **New section** at top of spec (this section) with descriptions and retained prior-version summaries |
| **Specification file** | `SPEC-001-v1.26-...md` (active) | **`SPEC-001-v1.27-...md`** (active); v1.26 file **immutable** |
| **Code folder** | `HIMA-Prooftest-Solution-v1.26` (active) | **`HIMA-Prooftest-Solution-v1.27`** (active); v1.26 frozen in `VERSION.json` |
| **Gates 10–13** | Scope defined; not started | **Gates 10–13 approved** (roadmap complete) |
| **G-22 architecture, plugin monitor, OPC poll** | Introduced in v1.26 | **No behavioural change** — copied into v1.27 codebase as-is |

#### Description of v1.27 modifications

1. **Gate 8 approved.** The G-22 trigger layer from v1.26 (persistent plugin monitor on `8400`–`8409`, multi-session `c3data`/`.E3` watchers, `test_step8_triggers.py`) is formally approved for use on engineering stations. No new trigger code in v1.27 — only spec status update.

2. **Gate 9 — Prooftest SQL insert verification.** New script `Annex codes/Tool test/test_step9_prooftest_sql.py` proves Step 5 end-to-end on a test database:
   - `insert_snapshot` writes to the correct `ProofTest_*` table with `Device_TAG`, `OPC_Server`, `CollectedAt`, `SequenceInBatch`.
   - `ProoftestMonitor` detects `Running` FALSE→TRUE→FALSE (mock OPC) and the background worker inserts the SQL row.
   - Uses isolated SQLite (`Tool test/data/gate9_prooftest.db`) so production `HIMA Automated Prooftest` data is not modified.

3. **SQL Server insert ID fix.** `annex_database.py` → `insert_snapshot()`: SQL Server path changed from `SCOPE_IDENTITY()` to `OUTPUT INSERTED.[ID]` because the former returned `0` when `SET NOCOUNT ON` was set on the cursor, breaking `update_report_path()` and gate checks.

4. **Spec clarification for plugin session (v1.26 code, v1.27 spec).** §3.5 now states explicitly that with `plugin_monitor_enabled = true` the service must not run the short-lived one-shot WebSocket (`acquire_open_project_session_id`) while the monitor is up — that behaviour was added in **v1.26 code** (`resolve_gui_session_id`, `wait_for_session_id`, monitor before `refresh()`); **v1.27 only documents it** in the specification.

5. **Versioning policy applied.** New spec file and new code folder per [Codes/README.md](../Codes/README.md); v1.26 spec and code tree left unchanged for audit.

#### Gate 10 update (same v1.27 — no new spec/code version)

| Topic | Before Gate 10 | After Gate 10 (v1.27) |
|-------|----------------|------------------------|
| **Gate 9** | Done — await approval | **Approved** 2026-06-18 |
| **Gate 10** | Code existed; template hardening pending | **`test_step10_reports.py`**; HIMA HTML templates from `1- HTML Reports Template`; SAMSON FST/PST folders; `html_templates` in `solution.ini` |
| **Report paths** | Flat under `report_output` | **`device_report_dir()`** — matches Step 1.2 folder hierarchy |
| **Spec/code version** | 1.27 | **Still 1.27** — gates advance within one version until a release bump is needed |

#### Files touched for Gate 10 (v1.27)

| File | Change |
|------|--------|
| `Annex codes/PDF generation/annex_pdf_generation.py` | FST/PST template key, subfolder paths, `decimal_places`, mirror copy fix |
| `Annex codes/Tool test/test_step10_reports.py` | **New** gate test |
| `SPEC-001-v1.27-...md` | Gate 9 approved; Gate 10 criteria in §6; gate table updated |

#### Gate 11 update (same v1.27 — no new spec/code version)

| Topic | Before Gate 11 | After Gate 11 prep (v1.27) |
|-------|----------------|----------------------------|
| **Gate 10** | Done — await approval | **Approved** 2026-06-18 |
| **Gate 11** | Code existed; polish pending | **`test_step11_web_ui.py`**; `AlarmLog` persistence on `raise_alarm`; health panel shows SILworX; `/api/reports?results_type=` |
| **sqlite_path** | Pointed at v1.25 folder | **v1.27** `Annex codes/data/prooftest.db` |
| **Spec/code version** | 1.27 | **Still 1.27** |

#### Files touched for Gate 11 prep (v1.27)

| File | Change |
|------|--------|
| `Tool Steps/alarms.py` | `set_persist_callback` — write to `AlarmLog` on raise |
| `Tool Steps/service.py` | Wire alarm persistence after DB connect |
| `Annex codes/Database/annex_database.py` | `list_recent_alarms()` for API alarm zone |
| `Graphic Interface/app.py` | `results_type` on reports; alarms from DB; version `1.27.0` |
| `Graphic Interface/static/app.js` | SILworX in health; pass `results_type` to reports API |
| `Annex codes/Tool test/test_step11_web_ui.py` | **New** gate test |
| `solution.ini` | `sqlite_path` → v1.27 data folder |
| `requirements.txt` | `httpx` for gate-test `TestClient` |
| `Graphic Interface/static/` | HIMA-branded UI redesign; `img/` logos from `7- Images for the graphical interface` |

| File | Change |
|------|--------|
| `Annex codes/Tool test/test_step9_prooftest_sql.py` | **New** gate test |
| `Annex codes/Database/annex_database.py` | `insert_snapshot` → `OUTPUT INSERTED.[ID]` on SQL Server |
| `VERSION.json` | `spec_version` 1.27, `status: active` |
| `SPEC-001-v1.27-...md` | **New** spec (this file) |
| `HIMA-Prooftest-Solution-v1.26/VERSION.json` | `status: frozen` (only edit allowed on frozen tree) |

---

### Version 1.26 (2026-06-17) — frozen

**G-22 three-layer architecture.** Separated concerns into: **(1) Data layer** — device list and metadata read only via SILworX REST API; **(2) Trigger layer** — persistent plugin WebSocket monitor on ports `8400`–`8409` plus `c3data`/`.E3` mtime on all open sessions; **(3) Realtime layer** — independent OPC poll loop (1 s), never blocked by API or plugin work.

**Plugin monitor (`annex_plugin_monitor.py`).** Background listener on every reachable API/plugin port pair; caches `user_session_id` from `TRIGGER_SESSION_ID_CHANGED`; rescan when SILworX instances appear.

**One-shot plugin conflict fix (code).** `resolve_gui_session_id()` waits on monitor cache when monitor is active; `service.py` starts monitor before first `refresh()`; `PluginPortMonitor.is_running()` and `wait_for_session_id()` added.

**Multi-session triggers.** `step07_triggers.py` watches all open SILworX sessions for project modify and code generation, not only the preferred session.

---

### Version 1.25 (2026-06-16) — frozen

**Gate 8 complete.** Wired `code_generation` and `download` triggers to `service.refresh()`; added `run_plugins_all.ps1`, `Plugin/README.md`, `test_step8_triggers.py`; service state `silworx_plugin_ports_configured`.

---

### Version 1.24 (2026-06-16) — frozen

**Gate 7 approved; Gate 8 started.** Separate `code_generation` / `download` trigger names; roadmap gates 0–13 table; `test_step8_triggers.py` introduced.

---

### Version 1.23 (2026-06-16) — frozen

**G-21 multi-instance API.** Scan and connect to all SILworX API/plugin port pairs `51710`–`51719` / `8400`–`8409`; `discover_available_instances()`, `api_session_for_port()`; merged device list across instances.

---

### Version 1.22 (2026-06-16) — frozen

**G-20 rewrite.** Removed API-based kill logic; kill `c3.exe` only after confirmed SILworX close (`lock.ini` gone, `OLixClient.exe` gone, 8 s grace); never on startup.

---

### Version 1.21 (2026-06-16) — frozen

**G-20 fix v2.** Reset `_silworx_seen_running` after cleanup so kill gate cannot fire during the next SILworX startup; `down_streak` reset after clean shutdown.

---

### Version 1.20 (2026-06-16) — frozen

**G-20 fix.** Never kill `c3.exe` while SILworX is opening, running, or a project is open; process kill only after four consecutive “closed” polls with `_silworx_seen_running`.

---

### Version 1.19 (2026-06-16) — frozen

**G-19 API session release.** Release SILworX API connection when SILworX closes (`is_silworx_running` via `POST /silworx/info`); `release_api_connection` in `step07_triggers.py`. **G-19 fix:** `_service_owns_api_session`, consecutive-probe release, `is_api_suspended`. **G-20 addition:** `annex_silworx_cleanup.py` for stale `c3.exe` / `hima.*` after confirmed close.

---

### Versions 1.17–1.18 — frozen

**G-17 layout.** Annex modules in purpose-named root folders (`Database`, `API connexion`, `OPC`, `PDF generation`, `Plugin`, `Stop service`); web GUI in `Graphic Interface\`; `prooftest/__init__.py` import bootstrap.

**G-16.** Flat step modules + `annex_*` files. **G-15.** `Tool test\` folder for gate scripts. **G-14.** Step files under `prooftest/steps`.

---

### Versions 1.11–1.16 — frozen

**G-11** graceful shutdown (`POST /api/shutdown`, `stop_service.ps1`). **G-12** code folder versioning policy. **G-13** no globals CSV export; `prooftest_session_plugin` session bridge only.

---

### Versions 1.9–1.10 — frozen

**1.9** user requirements rewrite: Steps 1–7, Case 1 API device list, Case 2 OPC+CSV, Step 7 codegen triggers, error catalog. **1.10** gates 0–6 record: nine `ProofTest_*` tables, `TEMPLATE_MAP`, OI-3 OPC fallback, §3.5 API session modes, `solution.ini` alignment.

---

### Versions 1.0–1.8 — frozen

Initial OPC-centric spec through Case 1 OPC-only device list, background service, multi-OPC, web GUI, SILworX `lock.ini` session detection. See the compact index below for row-per-version notes.

---

## Compact document-history index

| Version | Date | Notes |
|---------|------|-------|
| 1.39 | 2026-08-12 | Fix UI Start after Stop (API suspend + health while starting)
| 1.38 | 2026-08-06 | Engine stop vs process exit (`/api/stop`); Start in-process; G-11 still `/api/shutdown` |
| 1.33 | 2026-07-01 | Auto-start at logon; `health_check_wait_sec` 120 |
| 1.32 | 2026-06-19 | Windows auto-start Task Scheduler |
| 1.31 | 2026-06-19 | Device/report list search |
| 1.29 | 2026-06-19 | Reports under `C:\HIMA Automated Prooftest Reports`; Gates 12–13 |
| 1.28 | 2026-06-19 | Start/Stop UI buttons; list placeholders |
| 1.27 | 2026-06-18 | Gate 9; SQL `OUTPUT INSERTED.ID`; cumulative Summary introduced (later moved here) |
| 1.26 | 2026-06-17 | G-22 three-layer architecture; plugin monitor one-shot fix |
| 1.25 | 2026-06-16 | Gate 8 complete |
| 1.24 | 2026-06-16 | Gate 7 approved; Gate 8 started |
| 1.23 | 2026-06-16 | G-21 multi-instance API ports |
| 1.22–1.19 | 2026-06-16 | G-20 / G-19 SILworX close and cleanup |
| 1.17–1.11 | 2026-06 | G-11…G-17 layout and versioning |
| 1.10–1.9 | 2026-06 | Requirements rewrite; gates 0–6 |
| 1.8–1.0 | 2026-05…06 | Initial OPC / web GUI / Case 1–2 foundation |
