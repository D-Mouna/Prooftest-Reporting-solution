# OLD vs NEW — functionality and code (this machine)

| Field | Value |
|-------|--------|
| **OLD** | Pre–layered-architecture behaviour (Case 1/2, TAG-only, CSV invent, ShutdownProcess confusion) |
| **NEW** | Code in `HIMA-Prooftest-Solution-Current` as of audit 2026-08-20 (≈1.74+) |
| **Evidence root** | `C:\Users\Administrator\Documents\Report Solution\Codes\HIMA-Prooftest-Solution-Current` |

## Comparison table

| Topic | OLD behaviour | NEW behaviour | OLD code location | NEW code location | Keep / Replace / Delete |
|-------|---------------|---------------|-------------------|-------------------|-------------------------|
| 1. Case 1 vs 2 | Separate Case 1 API / Case 2 OPC product modes | **Unified** `deployment_case=1` always; API+OPC merge | `detect_deployment_case` returning 1/2; `sync_device_list_case2` | `step01_setup.apply_deployment_case`; `sync_device_list_case1_via_api` | **Replace** modes; alias `case2` **deprecated** |
| 2. Device identity | TAG-only merge | **DeviceId** = Project+Configuration+Resource+TAG | TAG keys in DB/list | `layers/domain/device.py` `DeviceId` | **Replace** |
| 3. Same TAG two projects | One row / overwrite | **Two rows** (test_02) | TAG merge | `CatalogMerger` | **Keep NEW** |
| 4. SILworX+OPC same TAG | Ambiguous / last writer | Merge by DeviceId + OPC bind; collisions alarmed | step03 ad-hoc | `CatalogMerger` + `apply_merged_device_list` | **Keep NEW** (production still via step03+merger) |
| 5. OPC list build | Browse + **CSV score ≥3 invents type** | Intended: construct `OTS/OPC ProofTest.{TAG}.Running` | `_score_structure_match`, `discover_devices_from_opc` | `bind_opc_paths` (construct); **adapter still calls CSV discover** | **Partial** — CSV path **still live** for OPC-only |
| 6. LoadResultTypes vs RefreshCatalog | Mixed | Types = CSVs; Refresh = device catalog | mixed annex | `load_result_types` vs `run_station_refresh` / `refresh_catalog` | **Keep NEW** |
| 7. Shutdown vs Close SILworX | Process exit confused with disconnect | **CloseSilworXconnection** = tool detach only; process exit = `/api/shutdown` + `stop_service.ps1` | old stop mixing | `silworx_connection.py`; Host `request_shutdown`; `c3.exe` only on uninstall path in step07/service | **Keep both**, separated |
| 8. Resume / Connect button | Missing or Mode A open project | **Connect** → `resume_silworx_connection`; never `project/open` for tool | Mode A | `facade.resume_*`; UI `#btn-connect-silworx` | **Keep NEW** |
| 9. GetEngineStatus | Sparse | health: deployment, opc_servers, devices, queue, silworx_status, plugin, starting/stopping | service.health | `service.health` via facade | **Keep NEW** |
| 10. GUI columns | TAG/type only | **Project** + **OPC server** columns; sort TAG→Project→OPC | old HTML | `index.html` + `app.js` + `sort_device_dicts` | **Keep NEW** |
| 11. Errors | Often silent | Alarms S-steps + AlarmLog + UI list | partial | `AlarmManager` + `QueryService.list_alarms_payload` | **Keep NEW** |
| 12. Poll SQL | Upsert every second common | Intended memory edges via `RunningEdgeDetector`; Host still uses `ProoftestMonitor` | step05 poll | `live_test.py` + step05 **hybrid** | **Unfinished** full cutover |
| 13. project/close, silworx/close, c3 kill | Callable / risky | `project/close` in API client = **legacy diagnostic**; Close SILworX **never** project/close GUI; **c3.exe** only after confirmed SILworX uninstall close (step07/service) | `annex_api_connexion.py` | same + comments in step07 | **Keep** host uninstall kill; **not** UI Close |
| 14. Dead shims | step02/step06 re-exports | **Removed** 1.70/1.68 | Tool Steps shims | gone | **Deleted** |
| Z:\ / Copy folders | Hardcoded Z: | Still some Z: seeds; **no** Current-Copy | various | `annex_pdf_generation._package_html_templates_seed` | **Fix later** |

## Behaviour the operator sees that changed

- Device list shows **Project** and **OPC server**; same TAG can appear twice for two projects.
- **Connect / Disconnect SILworX** buttons control *this tool’s* attachment (badge “tool attached / tool not connected”).
- Engine **Stop** keeps the web UI up; full process exit is separate (shutdown / stop_service).
- Alarms appear in the UI with acknowledge/reset.

## Behaviour that must stay the same

- OPC Classic DA on the **same PC** (32-bit Python).
- `.Running` falling edge → snapshot → SQL → PDF/HTML reports.
- Web **Stop** ≠ process kill; uninstall may still need process exit + careful c3 cleanup.
- Auto-start via Task Scheduler → `run_service.ps1`.
