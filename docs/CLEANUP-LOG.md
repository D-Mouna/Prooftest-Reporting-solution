# Cleanup log — dead / dual OLD paths

| Field | Value |
|-------|--------|
| **Tree** | `Codes\HIMA-Prooftest-Solution-Current` |
| **Archive before cleanup** | `Codes\Archive\HIMA-Prooftest-Solution-v1.74` |
| **Date** | 2026-08-20 |

## Candidates before delete (evidence)

| Candidate | Evidence | Action taken |
|-----------|----------|--------------|
| Dual `refresh_catalog()` after `run_station_refresh` | `catalog_service.py` called domain `refresh_catalog()` after `sync_device_list_case1_via_api` → **two writers** | **Removed** trailing call |
| `sync_device_list_case2` alias | `step03_device_list.py` | **Deprecated** comment; alias kept for old tests |
| `step02_database.py` / `step06_reports.py` | Already removed in 1.68–1.70 | Already gone |
| `annex_start_service.py` / standalone plugin runners | Removed 1.68–1.71 | Already gone |
| `Current - Copy` | Glob under Codes: **0** | N/A |
| `Annex codes/data/` stale markers | Removed Tier B 1.69 | Already gone |
| CSV-score `discover_devices_from_opc` | Still called from `OpcManagerAdapter.discover_opc_only` | **Not deleted** — still production OPC-only typer; marked **UNFINISHED** replace |
| `project/close` in API client | Diagnostic only; service never opens projects | **Kept** — not UI-exposed as Close SILworX |
| Process exit / c3 cleanup | Required for SILworX uninstall (G-11) | **Kept** on Host; not CloseSilworX |

## Cleanup log

| Removed or disabled | Why | Replaced by | Risk |
|---------------------|-----|-------------|------|
| Trailing `CatalogService.refresh_catalog()` inside `run_station_refresh` | Dual merge/upsert after step03 | Single production writer: `sync_device_list_case1_via_api` via Application entry | Low — tests use `refresh_catalog` directly |
| Misleading UI “unified (case N)” | Case 2 product mode gone | Label `"unified"` | None |
| SILworX badge wording “running/not connected” alone | Confused with SILworX.exe | “tool attached” / “tool not connected”; card “SILworX (this tool)” | None |
| Unsorted device table trust | Spec requires TAG→Project→OPC | Client-side sort in `app.js` (server already sorts) | None |

## Re-test

```powershell
cd "...\Annex codes\Tool test"
& "C:\Python 312_32bit\python.exe" test_layers.py
& "C:\Python 312_32bit\python.exe" test_step11_web_ui.py
```

(Results recorded in HOW-TO-RUN-TESTS.md after run.)
