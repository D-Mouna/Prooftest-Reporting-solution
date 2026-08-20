# Implementation inventory — HIMA-Prooftest-Solution-Current

| Field | Value |
|-------|--------|
| **Machine path** | `C:\Users\Administrator\Documents\Report Solution` |
| **Active code** | `Codes\HIMA-Prooftest-Solution-Current` |
| **VERSION.json** | code **1.77** · SPEC **1.64** |
| **Git** | `main` @ Documents git root → `D-Mouna/Prooftest-Reporting-solution` |
| **Evidence date** | 2026-08-20 |

> Claims below are from files on **this** tree only.

---

## A1. Architecture / folder map

### Current tree (as built)

```text
HIMA-Prooftest-Solution-Current/
├── main.py, run_service.ps1, stop_service.ps1
├── install_auto_start.ps1, uninstall_auto_start.ps1
├── solution.ini, VERSION.json, requirements.txt
├── Tool Steps/          ← Host / WorkerHost (threads, G-11, wire facade)
├── Annex codes/
│   ├── layers/
│   │   ├── presentation/  controllers.py, web_app.py
│   │   ├── application/   facade, engine, catalog, query, live_test, silworx_connection
│   │   ├── domain/        device, merger, result_types, running, opc_discover
│   │   ├── ports.py, adapters.py, fakes.py
│   ├── OPC/, Database/, API connexion/, PDF generation/, Plugin/, Stop service/
│   ├── prooftest/__init__.py   import bootstrap
│   └── Tool test/              gates
├── Graphic Interface/   static UI
├── Results Structures/  first-run seed CSVs
└── Dev tools/           open_graphic_interface.ps1, sync_gui_images.ps1
```

### Intended layers vs placement

| Layer | Intended | Actual folder | Status |
|-------|----------|---------------|--------|
| Presentation | thin HTTP | `layers/presentation/` + `Graphic Interface/` | **NEW** / wired |
| Application | use cases | `layers/application/` | **NEW** / wired via `ApplicationFacade` |
| Domain | merge, edges | `layers/domain/` | **NEW** |
| Adapters | ports impl | `layers/adapters.py` + annex OPC/DB/API/PDF/archive | **NEW** + **KEPT** annex |
| Host | threads | `Tool Steps/service.py` | **MODIFIED** WorkerHost |
| Test | gates | `Annex codes/Tool test/` | **KEPT** + `test_layers.py` **NEW** |

No `Current - Copy` folder under `Codes\` (glob 2026-08-20: zero matches).

---

## A2. Application functions actually present

| Prompt name | Actual symbol | File | Status |
|-------------|---------------|------|--------|
| StartEngine | `ApplicationFacade.start_engine` → `host.start()`; also `Engine.start_engine` | `facade.py`, `engine.py` | **NEW** (facade delegates host) |
| StopEngine | `ApplicationFacade.stop_engine` → flags + `perform_graceful_shutdown` | `facade.py` | **NEW** |
| CloseSilworXconnection | `ApplicationFacade.close_silworx_connection` → `SilworxConnectionService.close_silworx_connection` | `facade.py`, `silworx_connection.py` | **NEW** |
| ResumeSilworXconnection | `resume_silworx_connection` | same | **NEW** |
| RefreshCatalog | `facade.refresh_catalog` → `CatalogService.run_station_refresh` → **`refresh_catalog` (ports)** | `facade.py`, `catalog_service.py` | **NEW (1.76)** — does **not** call `sync_device_list_case1_via_api` |
| BindOpcPaths | `CatalogService.bind_opc_paths` | `catalog_service.py` | **NEW** — construct OTS/OPC `.Running`; no CSV invent |
| DiscoverOpcOnlyDevices | `CatalogService.discover_opc_only_devices` → `OpcPort.discover_opc_only` → **`opc_discover` shape gate** | `catalog_service.py`, `adapters.py`, `domain/opc_discover.py` | **NEW (1.76)** |
| ReconcileCatalog | `CatalogService.reconcile_catalog` | `catalog_service.py` | **NEW** |
| LoadResultTypes | `CatalogService.load_result_types` / `sync_types_from_structures` | `catalog_service.py` | **NEW** |
| PollOnce | `LiveTestService.poll_once` | `live_test.py` | **NEW** — **sole** production poll brain |
| OnTestStarted | `LiveTestService.on_test_started` | `live_test.py` | **NEW** |
| OnTestEnded | `LiveTestService.on_test_ended` | `live_test.py` | **NEW** (skips ProofTest_* if type unknown) |
| CompleteTest | `LiveTestService.complete_test` | `live_test.py` | **NEW** |
| OnTestInterrupted | `LiveTestService.on_test_interrupted` | `live_test.py` | **NEW** |
| ListDevices | `QueryService.list_devices` / `facade.list_devices` | `query.py` | **NEW** |
| ListReports | `QueryService.list_reports` | `query.py` | **NEW** |
| ListAlarms | `QueryService.list_alarms_payload` | `query.py` | **NEW** |
| OpenReport | `QueryService.open_report` | `query.py` | **NEW** (403 outside roots) |
| ListArchives / KeepOpc | `QueryService` → **`ArchivePort`** | `query.py`, `adapters.AnnexListArchiveAdapter` | **NEW (1.77)** |
| GetEngineStatus | `facade.get_engine_status` → `host.health()` | `facade.py`, `service.py` | **MODIFIED** host health |

**Production poll (1.76+):** `service._poll_loop` → `ProoftestMonitor.poll_devices` (thin shell) → **`LiveTestService.poll_once`**. Monitor constructed with `live_service=app.live`.

**Deprecated shims (tests only):** `sync_device_list_via_api` / alias `sync_device_list_case1_via_api` — called from `test_step6_devices.py` / `test_step12_case2.py`, not from `run_station_refresh`.

---

## A3. Domain classes actually present

| Class | File | One sentence | Status |
|-------|------|--------------|--------|
| `DeviceId` | `layers/domain/device.py` | Frozen composite key: project+configuration+resource+device_tag | **NEW** |
| `Device` | same | Catalog row with OPC fields + `present_on_opc` | **NEW** |
| `sort_devices` / `sort_device_dicts` | same | Sort TAG → Project → OPC server | **NEW** |
| `CatalogMerger`, `SilworxIdentity`, `OpcObservation`, `MergeResult` | `layers/domain/merger.py` | Merge SILworX + OPC; collision/duplicate rules | **NEW** |
| `ResultType`, `ResultTypeCatalog` | `layers/domain/result_types.py` | CSV folder → type catalogue | **NEW** |
| `RunningEdgeDetector` | `layers/domain/running.py` | Rising/falling Running edges in memory | **NEW** |
| Shaped OPC discover helpers | `layers/domain/opc_discover.py` | Shape gate + clear/unknown type (no invent) | **NEW (1.76)** |

---

## A4. Ports / adapters

| Port (`ports.py`) | Adapter (`adapters.py`) | Status |
|-------------------|-------------------------|--------|
| `AlarmPort` | `AlarmManagerAdapter` | **NEW** |
| `SilworxPort` | `Case1SyncSilworxAdapter` | **NEW** |
| `OpcPort` | `OpcManagerAdapter` | **NEW** |
| `StorePort` | `DatabaseStoreAdapter` | **NEW** |
| `ReportPort` | `AnnexReportAdapter` | **NEW** |
| `ArchivePort` | `AnnexListArchiveAdapter` | **NEW (1.77)** |

Test doubles: `layers/fakes.py` — `FakeSilworx`, `FakeOpc`, `FakeStore`, `FakeReports`, `FakeArchive` (**TEST**).

---

## A5. Web GUI routes and controls

### Routes (`layers/presentation/controllers.py`)

| Method | Path | Application call |
|--------|------|------------------|
| GET | `/api/health` | `get_engine_status` |
| GET | `/api/devices` | `list_devices` |
| GET | `/api/reports` | `list_reports` |
| GET | `/api/reports/open` | `open_report` |
| GET | `/api/alarms` | `list_alarms` |
| POST | `/api/alarms/{id}/ack` | `acknowledge_alarm` |
| POST | `/api/alarms/reset` | `reset_alarms` |
| POST | `/api/start` | `start_engine` (localhost) |
| POST | `/api/stop` | `stop_engine` (localhost) |
| POST | `/api/shutdown` | `request_shutdown` (localhost) |
| POST | `/api/refresh` | `refresh_catalog` |
| POST | `/api/silworx/connect` | `resume_silworx_connection` (localhost) |
| POST | `/api/silworx/disconnect` | `close_silworx_connection` (localhost) |
| GET/POST | `/api/archives*` | archive use cases via ArchivePort |
| POST | `/api/devices/keep-opc` | `clear_keep_opc_only` |

Controllers **do not** import annex/OPC/SQL after 1.74 (`application(service)` required).

### UI (`Graphic Interface/static/`)

| Control | ID / evidence |
|---------|----------------|
| Connect to SILworX | `#btn-connect-silworx` → POST `/api/silworx/connect` (title: this-tool attach only) |
| Disconnect | `#btn-disconnect-silworx` → POST `/api/silworx/disconnect` (title: detach only) |
| Stop service | `#btn-stop-service` — stops engine; page stays open (distinct from `/api/shutdown`) |
| Devices columns | Device, Type, OPC, **Project**, **OPC server**; empty type → **unknown** |
| Sort | Server `sort_device_dicts` + client sort in `app.js` |
| Badge | Health card “SILworX (this tool)” = tool attachment |

---

## A6. Unit tests added (layers)

File: `Annex codes/Tool test/test_layers.py`  
**Expected run:** `54/54 passed` (23 baseline + 24 edge + 7 R1–R7).

### Baseline `test_01` … `test_23`

| Test | Asserts |
|------|---------|
| `test_01_same_deviceid_one_row` | Same DeviceId → one row |
| `test_02_same_tag_two_projects` | Same TAG two projects → two rows |
| `test_03_same_tag_same_opc_path_collision` | Collision alarm |
| `test_04_silworx_only_not_on_opc` | SILworX-only listed, not on OPC |
| `test_05_opc_only_folder` | OPC-only folder |
| `test_06_false_true_started_no_snapshot` | false→true start, no snapshot |
| `test_07_true_false_complete_once` | true→false complete |
| `test_08_flicker_no_complete` | Flicker no complete |
| `test_09_interrupt_no_snapshot` | Interrupt |
| `test_10_poll_continues_after_device_a_error` | Poll isolation |
| `test_11_load_result_types` | LoadResultTypes |
| `test_12_bind_opc_paths_ots_then_opc` | BindOpcPaths OTS then OPC |
| `test_13_reconcile_marks_inactive_keeps_snapshots` | Reconcile |
| `test_14_engine_status_after_start` | Engine status |
| `test_15_close_silworx_keeps_opc_refresh` | Close SILworX |
| `test_16_resume_silworx` | Resume SILworX |
| `test_17_list_devices_order_and_fields` | Project + OPC fields / sort |
| `test_18_open_report_outside_root` | OpenReport 403 |
| `test_19_no_opc_servers_alarm_no_crash` | No OPC servers |
| `test_20_report_fail_keeps_snapshot` | Report fail keeps snapshot |
| `test_21_start_engine_store_fail` | Store fail on start |
| `test_22_reports_scoped_by_project` | Reports scoped by project |
| `test_23_seed_detector_does_not_retrigger_start` | Seed detector |

### Edge cases `test_t01` … `test_t24` (1.76)

| Test | Asserts |
|------|---------|
| `test_t01` … `test_t24` | Shape gate, unknown type, Connect/Disconnect attach-only, escapeHtml, localhost mutating checks (see prior inventory) |

### R1–R7 `test_r*` (1.77)

| Test | Asserts |
|------|---------|
| `test_r1_query_uses_archive_port_not_annex` | QueryService has no `annex_list_archive`; FakeArchive works |
| `test_r2_html_seed_prefers_documents_over_z` | `resolve_html_templates_seed` prefers config/Documents |
| `test_r3_db_name_validation` | `validate_sql_database_name` rejects injection-like names |
| `test_r4_auth_bind_policy_loopback_ok` | Loopback + auth off → no warning |
| `test_r4_auth_bind_policy_non_local_refuses` | `0.0.0.0` without auth → ValueError when require=true |
| `test_r7_unknown_results_type_placeholder` | Empty type surfaces as `unknown` |
| `test_r7_connect_button_titles` | Connect/Disconnect titles + Stop service wording |

**Run:**

```powershell
cd "C:\Users\Administrator\Documents\Report Solution\Codes\HIMA-Prooftest-Solution-Current\Annex codes\Tool test"
& "C:\Python 312_32bit\python.exe" test_layers.py
```

Also Gate 11: `test_step11_web_ui.py` (facade required on `service.app`; app **1.77.0**).

---

## A7. Promised but NOT finished

Gaps A/B/C and R1–R7 archive/seed/`db_name`/auth work are **done**. Remaining is optional hygiene only:

1. **Optional** mass rename of leftover `case1_*` symbols (aliases already: `SilworxSyncTriggers`, `sync_device_list_via_api`).

---

*See also: [OLD-vs-NEW.md](./OLD-vs-NEW.md), [ARCHITECTURE-AS-BUILT.md](./ARCHITECTURE-AS-BUILT.md).*
