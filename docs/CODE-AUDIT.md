# Code audit — HIMA-Prooftest-Solution-Current

| Field | Value |
|-------|--------|
| **Scope** | This machine’s Current tree **1.77** |
| **Date** | 2026-08-20 |

## Findings

| ID | Severity | Finding | File / symbol | Impact | Status |
|----|----------|---------|---------------|--------|--------|
| C1 | **High** | Dual catalog writers (trailing domain refresh after step03) | `CatalogService.run_station_refresh` | Double upsert | **Fixed** (1.75) — trailing call removed |
| C2 | **High** | OPC-only invent via CSV score ≥3 | was `OpcManagerAdapter` → invent scorer | Wrong type / false devices | **Fixed (1.76)** — `layers/domain/opc_discover.py` shape gate; invent = test-only |
| C3 | **Medium** | Production poll not solely LiveTestService | was step05 own logic | Two mental models | **Fixed (1.76)** — `ProoftestMonitor.poll_devices` → `LiveTestService.poll_once` (`live_service=app.live`) |
| C4 | **Medium** | `web_auth_enabled` defaults **False** | `config.py` | LAN exposure if host ≠ 127.0.0.1 | **Mitigated (1.77)** — `require_auth_when_non_local` default **true** refuses non-loopback bind without auth; `auth_bind_warning` on health / startup |
| C5 | **Medium** | Hardcoded `Z:\` HTML seed path | `annex_pdf_generation` | First-run templates fail if Z: missing | **Fixed (1.77)** — `resolve_html_templates_seed` order: config → Documents → packaged → Z fallback |
| C6 | **Medium** | `QueryService` imports `annex_list_archive` | was `query.py` | No dedicated port | **Fixed (1.77)** — `ArchivePort` + `AnnexListArchiveAdapter`; QueryService no annex import |
| C7 | **Low** | Layer Functions TAG-only header | `HIMA-Prooftest-Layer-Functions.md` | Doc drift | **Fixed** — DeviceId header + DiscoverOpcOnly wording |
| C8 | **Low** | `CREATE DATABASE` uses interpolated name | `annex_database.py` | Config-controlled string build | **Fixed (1.77)** — `validate_sql_database_name` before CREATE |
| C9 | **Info** | Presentation pure after 1.74 | `controllers.py` | — | Done |
| C10 | **Info** | Start vs Stop races on Host | `service.py` | — | Keep |

## Critical

None open after C1–C8. Auth remains off by default on **loopback** only; non-loopback without auth is refused when `require_auth_when_non_local=true` (default).

## Layering — remaining only

- Host still owns threads, schema sync markers, c3 cleanup after confirmed SILworX close (not Disconnect).
- **Optional hygiene:** mass rename leftover `case1_*` symbols / aliases (`Case1SyncTriggers` → `SilworxSyncTriggers`, `sync_device_list_case1_via_api` → `sync_device_list_via_api`).
- **Not remaining:** QueryService → `annex_list_archive` (cleared via ArchivePort). Application → `step03.sync_device_list_case1_via_api` inside `run_station_refresh` (removed in 1.76). Domain under `layers/domain/` stays free of OpenOPC/pyodbc/FastAPI.

## Grep evidence (callers after 1.76/1.77)

See [ARCHITECTURE-AS-BUILT.md](./ARCHITECTURE-AS-BUILT.md) § Caller evidence.
