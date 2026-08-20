# Cleanup log — dead / dual OLD paths

| Field | Value |
|-------|--------|
| **Tree** | `Codes\HIMA-Prooftest-Solution-Current` |
| **Archive before 1.77** | Prior Current at 1.76 (Gaps A/B/C) |
| **Date** | 2026-08-20 |

## This pass (1.77 R1–R7)

| Candidate | Evidence | Action taken |
|-----------|----------|--------------|
| QueryService → `annex_list_archive` | `query.py` | **Replaced** by `ArchivePort` + `AnnexListArchiveAdapter` (annex import only in adapter) |
| Hardcoded `Z:\` HTML seed | `annex_pdf_generation` | **`resolve_html_templates_seed`**: explicit → config → Documents → packaged → Z last |
| Raw `db_name` in CREATE DATABASE | `annex_database.py` | **`validate_sql_database_name`** |
| Auth off on any bind | `config.py` | **`require_auth_when_non_local`** default true; **`auth_bind_warning`** |
| `Case1SyncTriggers` name | `step07_triggers.py` | **`SilworxSyncTriggers`** primary; `Case1SyncTriggers` alias |
| `sync_device_list_case1_via_api` name | `step03_device_list.py` | **`sync_device_list_via_api`** primary; case1 name alias (test shim) |
| fastapi / starlette advisories | `requirements.txt` | **Pinned** `fastapi==0.141.1`, `starlette==1.3.1` (pip-audit clean) |

## Earlier (1.76 cutover A/B/C)

| Candidate | Evidence | Action taken |
|-----------|----------|--------------|
| CSV invent scorer as production OPC-only | `discover_devices_from_opc` + `_score_structure_match` | **Replaced** by `layers/domain/opc_discover.py` shape gate; invent path renamed `_discover_on_server_invent_legacy` (test-only) |
| `OpcManagerAdapter.discover_opc_only` → invent | adapters.py | **Now** calls shaped discover |
| `run_station_refresh` → `sync_device_list_case1_via_api` | catalog_service.py | **Removed** — Domain `refresh_catalog` is production brain |
| Background sync → step03 | step07_triggers.py | **Redirected** to `service.app.refresh_catalog()` |
| `ProoftestMonitor` as real poll engine | step05 | **Thinned** — `poll_devices` → `LiveTestService.poll_once`; shares `app.live` |
| `sync_device_list_case2` | alias | Still deprecated; not restored as product mode |
| `python-multipart==0.0.20` | pip-audit CVEs | **Pinned** to `0.0.31` |

## Earlier (1.75 audit)

| Removed or disabled | Why |
|---------------------|-----|
| Trailing dual `refresh_catalog()` after step03 | Dual writers |
| Misleading UI “unified (case N)” | Case 2 product mode gone |
| SILworX badge wording | “tool attached / not connected” |

## Re-test

```powershell
cd "...\Annex codes\Tool test"
& "C:\Python 312_32bit\python.exe" test_layers.py
& "C:\Python 312_32bit\python.exe" test_step11_web_ui.py
```
