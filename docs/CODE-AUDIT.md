# Code audit — HIMA-Prooftest-Solution-Current

| Field | Value |
|-------|--------|
| **Scope** | This machine’s Current tree |
| **Date** | 2026-08-20 |

## Findings

| ID | Severity | Finding | File / symbol | Impact | Fix |
|----|----------|---------|---------------|--------|-----|
| C1 | **High** | Dual catalog writers historically; trailing domain refresh after step03 | `CatalogService.run_station_refresh` | Inconsistent DeviceId / double upsert | **Fixed** — removed trailing `refresh_catalog()` |
| C2 | **High** | OPC-only discovery still CSV-scores members to invent Results type | `step03._score_structure_match` ← `OpcManagerAdapter.discover_opc_only` | Can invent wrong type / extra devices vs construct-path rule | Replace discover with branch+`.Running` without CSV invent; track as unfinished |
| C3 | **Medium** | Production poll not solely `LiveTestService` | `step05.ProoftestMonitor` vs `live_test.LiveTestService` | Two mental models | Migrate poll to LiveTestService only |
| C4 | **Medium** | `web_auth_enabled` defaults **False** | `config.py` | LAN exposure if host ≠ 127.0.0.1 | Keep host `127.0.0.1`; enable auth on shared PCs |
| C5 | **Medium** | Hardcoded `Z:\` HTML seed path | `annex_pdf_generation._package_html_templates_seed` | First-run templates fail if Z: missing | Prefer Documents path |
| C6 | **Medium** | Application `QueryService` imports annex_list_archive | `query.py` | Layer leak | Add FilesPort later |
| C7 | **Low** | Layer Functions doc header still TAG-only | `HIMA-Prooftest-Layer-Functions.md` | Doc drift | Update identity section to DeviceId |
| C8 | **Low** | `CREATE DATABASE` uses interpolated name | `annex_database.py` | Config-controlled only; still string build | Validate db_name charset |
| C9 | **Info** | Presentation pure after 1.74 | `controllers.py` `application()` | — | Done |
| C10 | **Info** | Start vs Stop races handled on Host | `service.py` locks / generation | — | Keep |

## Critical

None open after C1 fix (no RCE / auth bypass beyond default auth-off on localhost).

## Layering violations remaining

- Application → `prooftest.step03_device_list` inside `run_station_refresh`.
- Application → `annex_list_archive` inside QueryService.
- Domain: clean (no OpenOPC/pyodbc/FastAPI imports observed under `layers/domain/`).
