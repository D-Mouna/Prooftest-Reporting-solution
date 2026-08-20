# OLD vs NEW (unified cutover)

| Field | Value |
|-------|--------|
| **Code** | HIMA-Prooftest-Solution-Current **1.77** |
| **Date** | 2026-08-20 |

| Topic | OLD | NEW (code 1.77) | Status |
|-------|-----|-----------------|--------|
| Product modes | Case 1 vs Case 2 picker / `detect_deployment_case → 2` | **Unified only** — Case 2 product mode dead | **Keep NEW** |
| OPC-only list | Browse + CSV score ≥3 **invents** Results type | **Shape gate** (`opc_discover.py`): admit + last/clear/unknown | **Keep NEW** |
| RefreshCatalog | `sync_device_list_case1_via_api` as production brain | `CatalogService.run_station_refresh` → **`refresh_catalog`** (ports) | **Keep NEW** |
| Live poll | `ProoftestMonitor` owns edge/complete logic | **`LiveTestService.poll_once`**; monitor is thin shell | **Keep NEW** |
| Identity | TAG-only ambiguity | **DeviceId** = Project+Configuration+Resource+Device_TAG | **Keep NEW** |
| Connect/Disconnect | Confusion with project/close / kill | **This tool’s API/plugin only** | **Keep NEW** |
| GUI columns | TAG/type only | Project + OPC server; sort TAG→Project→OPC | **Keep NEW** |
| Live values | — | Always X-OPC, never SILworX | **Keep NEW** |
| Archives | QueryService imports annex | **`ArchivePort`** / `AnnexListArchiveAdapter` | **Done (1.77)** |
| HTML seed | Hardcoded `Z:\` only | Documents / packaged preferred; Z last | **Done (1.77)** |
| `db_name` | Raw interpolate in CREATE DATABASE | **`validate_sql_database_name`** | **Done (1.77)** |
| Auth / bind | Auth off + any host | **`require_auth_when_non_local`** refuses non-loopback without auth | **Done (1.77)** |

## Unfinished list (accurate)

| Item | Status |
|------|--------|
| Case 1/2 product modes | **Retired** — do not restore |
| OPC invent scorer in production | **Cleared** — legacy invent helper test-only |
| Refresh via step03 brain | **Cleared** — shim for `test_step6` / `test_step12` only |
| LiveTestService-only poll | **Done** |
| QueryService → ArchivePort | **Done (1.77)** |
| Documents-first HTML template seed | **Done (1.77)** |
| `db_name` charset validation | **Done (1.77)** |
| Auth/bind guard | **Done (1.77)** |
| Optional rename every `case1_*` | **Deferred** (hygiene only; aliases already exist) |

Aligns with [CLEANUP-LOG.md](./CLEANUP-LOG.md) and inventory §A7.
