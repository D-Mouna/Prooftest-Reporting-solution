# Tool test

Scripts to **verify and audit** the HIMA Prooftest solution. They are **not** part of the runtime service.

Solution code lives two levels up (solution root):

```text
..\..\main.py
..\..\Annex codes\prooftest\  ← import bootstrap
..\..\Tool Steps\         ← Steps + service
..\..\Graphic Interface\
..\..\Annex codes\Database\, ..\OPC\, …
..\..\solution.ini
..\..\run_service.ps1
```

## Prerequisites

- 32-bit Python (OPC DA)
- Service running for HTTP smoke tests: `..\run_service.ps1`
- SQL Server / SILworX / OPC as required per script

## Run all gate tests

```powershell
cd "Z:\Project\Report Solution\Codes\HIMA-Prooftest-Solution-v1.21\Annex codes\Tool test"
.\run_tests.ps1
```

## Scripts

| Script | Purpose |
|--------|---------|
| `_step1_audit.py` | Gate 1 — environment baseline (read-only) |
| `test_smoke.py` | Gate 2 — HTTP smoke test against running service |
| `test_silworx_api.py` | Gate 3 — SILworX OpenAPI client |
| `test_step4_install.py` | Gate 4 / SPEC Step 1 — folders + case detection |
| `test_step5_sql.py` | Gate 5 / SPEC Step 2 — nine SQL tables |
| `test_step6_devices.py` | Gate 6 / SPEC Step 3 — device list API + OPC fallback |
| `_check_sql.py` | List SQL tables and row counts |
| `_probe_sql_instances.py` | Find working SQL Server instance names |
| `_probe_cert_dialog.py` | UI automation probe for API certificate dialog |
| `monitor_auto_update.py` | Watch service/SQL state over 120 s |

Test artefacts (JSON snapshots, logs) are stored under `Tool test\data\`.
