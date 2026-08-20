# Implementation inventory — HIMA-Prooftest-Solution-Current

| Field | Value |
|-------|--------|
| **Machine path** | `C:\Users\Administrator\Documents\Report Solution` |
| **Active code** | `Codes\HIMA-Prooftest-Solution-Current` |
| **VERSION.json** | code **1.75** · SPEC **1.64** |
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
│   │   ├── domain/        device, merger, result_types, running
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
| Adapters | ports impl | `layers/adapters.py` + annex OPC/DB/API/PDF | **NEW** + **KEPT** annex |
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
| RefreshCatalog | `facade.refresh_catalog` → `CatalogService.run_station_refresh` | `facade.py`, `catalog_service.py` | **NEW** (body still calls `step03.sync_device_list_case1_via_api`) |
| BindOpcPaths | `CatalogService.bind_opc_paths` | `catalog_service.py` | **NEW** |
| DiscoverOpcOnlyDevices | `CatalogService.discover_opc_only_devices` | `catalog_service.py` | **NEW** (adapter still uses CSV-score helper) |
| ReconcileCatalog | `CatalogService.reconcile_catalog` | `catalog_service.py` | **NEW** |
| LoadResultTypes | `CatalogService.load_result_types` | `catalog_service.py` | **NEW** |
| PollOnce | `LiveTestService.poll_once` | `live_test.py` | **NEW** |
| OnTestStarted | `LiveTestService.on_test_started` | `live_test.py` | **NEW** |
| OnTestEnded | `LiveTestService.on_test_ended` | `live_test.py` | **NEW** |
| CompleteTest | `LiveTestService.complete_test` | `live_test.py` | **NEW** |
| OnTestInterrupted | `LiveTestService.on_test_interrupted` | `live_test.py` | **NEW** |
| ListDevices | `QueryService.list_devices` / `facade.list_devices` | `query.py` | **NEW** |
| ListReports | `QueryService.list_reports` | `query.py` | **NEW** |
| ListAlarms | `QueryService.list_alarms_payload` | `query.py` | **NEW** |
| OpenReport | `QueryService.open_report` | `query.py` | **NEW** (403 outside roots) |
| GetEngineStatus | `facade.get_engine_status` → `host.health()` | `facade.py`, `service.py` | **MODIFIED** host health |
| loops | Host `_poll_loop`, `_background_sync_loop` | `service.py` | **KEPT** / Host |

Production poll: `ProoftestMonitor.poll_devices` (step05) still drives live collection; `LiveTestService` used from monitor path / tests — **hybrid** (see A7).

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

---

## A4. Ports / adapters

| Port (`ports.py`) | Adapter (`adapters.py`) | Status |
|-------------------|-------------------------|--------|
| `AlarmPort` | `AlarmManagerAdapter` | **NEW** |
| `SilworxPort` | `Case1SyncSilworxAdapter` | **NEW** |
| `OpcPort` | `OpcManagerAdapter` | **NEW** |
| `StorePort` | `DatabaseStoreAdapter` | **NEW** |
| `ReportPort` | `AnnexReportAdapter` | **NEW** |

Test doubles: `layers/fakes.py` — `FakeSilworx`, `FakeOpc`, `FakeStore`, `FakeReports` (**TEST**).

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
| GET/POST | `/api/archives*` | archive use cases |
| POST | `/api/devices/keep-opc` | `clear_keep_opc_only` |

Controllers **do not** import annex/OPC/SQL after 1.74 (`application(service)` required).

### UI (`Graphic Interface/static/`)

| Control | ID / evidence |
|---------|----------------|
| Connect to SILworX | `#btn-connect-silworx` → POST `/api/silworx/connect` |
| Disconnect | `#btn-disconnect-silworx` → POST `/api/silworx/disconnect` |
| Devices columns | Device, Type, OPC, **Project**, **OPC server** (`index.html` th) |
| Sort | Server `sort_device_dicts` + client sort in `app.js` (audit fix) |
| Badge | Health card “SILworX (this tool)” = tool attachment |

---

## A6. Unit tests added (layers)

File: `Annex codes/Tool test/test_layers.py`

| Test | Asserts |
|------|---------|
| `test_01_same_deviceid_one_row` | Same DeviceId → one row |
| `test_02_same_tag_two_projects` | Same TAG two projects → two rows |
| `test_03_same_tag_same_opc_path_collision` | Collision alarm |
| `test_04`–`05` | SILworX-only / OPC-only |
| `test_06`–`10` | Running edges / complete / interrupt / poll continues |
| `test_11`–`13` | LoadResultTypes, BindOpcPaths, Reconcile |
| `test_14`–`16` | Engine status, Close/Resume SILworX |
| `test_17`–`18` | List order/fields; OpenReport outside root 403 |
| `test_19`–`23` | No OPC alarm; report fail; store fail; project-scoped reports; seed detector |

**Run:**

```powershell
cd "C:\Users\Administrator\Documents\Report Solution\Codes\HIMA-Prooftest-Solution-Current\Annex codes\Tool test"
& "C:\Python 312_32bit\python.exe" test_layers.py
```

Also Gate 11: `test_step11_web_ui.py` (facade required on `service.app`).

---

## A7. Promised but NOT finished

1. **Single RefreshCatalog implementation** — production still uses `step03.sync_device_list_case1_via_api` inside `CatalogService.run_station_refresh`; domain `refresh_catalog()` is used mainly by unit tests / Engine helper, not the sole production writer.
2. **OPC-only discovery without CSV score** — `OpcManagerAdapter.discover_opc_only` → `discover_devices_from_opc` still **CSV member-scores** (`step03_device_list._score_structure_match`).
3. **LiveTestService as sole poll path** — production poll still `ProoftestMonitor` (step05); LiveTestService is layered but not the only runtime poller.
4. **Layer doc identity** — `HIMA-Prooftest-Layer-Functions.md` still says TAG-only in the header; code uses **DeviceId**.
5. **QueryService archive methods** still import `annex_list_archive` (Application → annex), not a dedicated FilesPort.
6. **Hardcoded paths** — HTML template seed still `Z:\Project\Report Solution\1- HTML Reports Template` in `annex_pdf_generation.py`; SQL candidates C:/Z: in `config.py`.

---

*See also: [OLD-vs-NEW.md](./OLD-vs-NEW.md), [ARCHITECTURE-AS-BUILT.md](./ARCHITECTURE-AS-BUILT.md).*
