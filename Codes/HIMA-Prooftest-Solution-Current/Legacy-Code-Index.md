# Legacy / Unused Code Index — `HIMA-Prooftest-Solution-Current`

| Field | Value |
|-------|--------|
| **Scope** | Only files inside `Codes\HIMA-Prooftest-Solution-Current\` |
| **Active runtime** | `main.py` → `ProoftestService` → `ApplicationFacade` + workers + uvicorn/FastAPI |
| **Code version** | **1.67** / SPEC **1.64** (see `VERSION.json`) |
| **Indexed** | 2026-08-20 (re-scan after Application facade + in-tree OPC) |
| **Parent index** | [Legacy-Code-Index.md](../../Legacy-Code-Index.md) — archives and folders **outside** Current |

> Production path is now Presentation → Application facade → WorkerHost. OPC client is in-tree at `Annex codes/OPC/connection_opc.py`.

---

## Summary

| Status | ~Files | Meaning |
|--------|-------:|---------|
| **RUNTIME** | 55+ | Loaded/constructed when the service runs |
| **LEGACY_UNUSED** | 40+ | Dead shims, uncalled helpers, barrel `__init__`s, stale `data/` / logs |
| **TEST_ONLY** | 43+ | Entire `Annex codes/Tool test/` + `layers/fakes.py` |
| **DEV_TOOL** | 10+ | Operator PS1s, standalone plugin runners, probes |
| **FUTURE / DUPLICATE packages** | 0 | Application modules are now constructed for production |

---

## 1. What **is** the current tool (RUNTIME)

```
main.py
  ├─ ProoftestService (WorkerHost: threads, G-11, start/stop races)
  │    └─ ApplicationFacade
  │         ├─ QueryService, SilworxConnectionService  → actively called
  │         ├─ Engine, CatalogService, LiveTestService → constructed on facade
  │         └─ adapters / ports
  └─ Graphic Interface → layers/presentation/controllers
       └─ application(service) → facade (MagicMock fallback for Gate 11)
```

| Path | Role |
|------|------|
| `main.py`, `run_service.ps1`, `stop_service.ps1` | Process start/stop |
| `solution.ini`, `requirements.txt`, `VERSION.json` | Config / deps / version |
| `Tool Steps/config.py`, `service.py`, `alarms.py`, `results_csv.py` | Host + config |
| `Tool Steps/step01_setup.py`, `step03_device_list.py`, `step04_opc.py`, `step05_detection.py`, `step07_triggers.py` | Engine body / poll / sync |
| `Annex codes/prooftest/__init__.py` | Import bootstrap |
| `Annex codes/Database/*`, `API connexion/*`, `PDF generation/*` | Store / SILworX / reports |
| `Annex codes/OPC/annex_opc.py` | OPC manager |
| `Annex codes/OPC/connection_opc.py` | **OPC Classic DA client (in-tree)** |
| `Annex codes/Plugin/annex_plugin_monitor.py` | Plugin session monitor |
| `Annex codes/Stop service/annex_stop_service.py`, `annex_silworx_cleanup.py`, `*.ps1` (stop/auto-start) | Shutdown / G-11 / tasks |
| `layers/application/facade.py` | Presentation door |
| `layers/application/{engine,catalog_service,query,silworx_connection,live_test,errors}.py` | Application (wired) |
| `layers/domain/*`, `layers/ports.py`, `layers/adapters.py` | Domain + ports |
| `layers/presentation/web_app.py`, `controllers.py` | HTTP API |
| `Graphic Interface/*` | Web UI |
| `Results Structures/*.csv` | First-run seed catalogue |

**Nuance:** Catalog refresh and engine start **bodies** still run in WorkerHost (`service.refresh` / `service.start`); facade exposes them as Application use cases. Facade’s `LiveTestService` is constructed; **poll uses step05’s LiveTestService instance**.

---

## 2. Old / unused inside Current

### 2.1 LEGACY_UNUSED — shims and dead modules

| Path | Why unused |
|------|------------|
| `Tool Steps/step02_database.py` | Re-export shim → `annex_database`; only `test_step5_sql.py` |
| `Tool Steps/step06_reports.py` | Re-export shim → `annex_pdf_generation`; **zero** production refs |
| `Tool Steps/__init__.py` | Docstring only |
| `Annex codes/Stop service/annex_start_service.py` | In bootstrap map; **no callers** (`run_service.ps1` + `/api/start` supersede) |
| `layers/__init__.py`, `layers/*/ __init__.py` (barrels) | Not imported on runtime path |
| `Annex codes/Plugin/message_log.json` | Debug artifact |

### 2.2 LEGACY_UNUSED — stale data / logs

| Path | Why unused |
|------|------------|
| `Annex codes/data/sync_markers/*.marker` (~33) | Dev copy; runtime writes station `Database/sync_markers` on `C:` |
| `Annex codes/data/service.log` | Old log; not written by production |
| Repo-root `sync_markers/`, `*_stderr.log`, `*_stdout.log`, `auto_start.log`, `service_stderr.log` (if present) | Captured run artifacts; not imported |

### 2.3 TEST_ONLY

| Path | Notes |
|------|-------|
| `Annex codes/Tool test/` (entire folder, ~43 files) | Gates, probes, fixtures — not runtime |
| `Annex codes/layers/fakes.py` | Test doubles for `test_layers.py` |

### 2.4 DEV_TOOL (not imported by service)

| Path | Purpose |
|------|---------|
| `install_auto_start.ps1`, `uninstall_auto_start.ps1` | Task Scheduler setup |
| `open_graphic_interface.ps1` | Open browser to UI |
| `sync_gui_images.ps1` | Branding copy into `static/img/` |
| `Annex codes/Plugin/annex_plugin.py`, `run_plugin.ps1`, `run_plugins_all.ps1` | Standalone SILworX **dev** plugin (not the monitor) |
| `README.md`, `Legacy-Code-Index.md` | Docs |

---

## 3. Quick lookup

| If you see… | Used by running tool? |
|-------------|------------------------|
| `step01`, `step03`–`step05`, `step07` | **Yes** |
| `step02`, `step06` | **No** (shims) |
| `connection_opc.py` / `annex_opc.py` | **Yes** |
| `ApplicationFacade` / Query / SilworxConnection | **Yes** |
| `Engine` / `CatalogService` | **Constructed**; lifecycle still via WorkerHost |
| `Tool test/` | **No** |
| `Annex codes/data/` | **No** (stale) |
| `annex_plugin.py` (standalone) | **No** (dev) |
| `annex_plugin_monitor.py` | **Yes** |
| `annex_start_service.py` | **No** |
| Sibling `Codes\Report-Tool\` | **No** — legacy; client is in-tree |

---

## 4. Cleanup candidates (optional)

Safe after updating tests/bootstrap:

1. `Tool Steps/step06_reports.py`
2. `Annex codes/data/` stale markers + `service.log`
3. Root log files / `sync_markers/` copies
4. `Plugin/message_log.json`
5. `annex_start_service.py` (+ remove from `prooftest/__init__.py` map)

**Do not remove without a plan:** Application layer, `connection_opc.py`, `Tool test/`, `step02_database.py` (gate 5), `prooftest/__init__.py`.

---

*See also: [Codes/README.md](../README.md), [Layer-Architecture-Gaps.md](../../Layer-Architecture-Gaps.md).*
