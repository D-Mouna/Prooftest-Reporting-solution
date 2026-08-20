# HIMA Automated Prooftest Solution — **Current**

**Active working tree** for all code changes. Paired with **SPEC-001 v1.61** (see `VERSION.json`).

Before any modification, archive this folder — run `..\archive_current.ps1`.

**Unused code inside Current (cleanup list):** [Legacy-Code-Index.md](./Legacy-Code-Index.md)

**Dev-only helpers (not runtime):** [Dev tools/README.md](./Dev%20tools/README.md)

## Quick start

```powershell
cd "Z:\Project\Report Solution\Codes\HIMA-Prooftest-Solution-Current"
powershell -ExecutionPolicy Bypass -File .\run_service.ps1
```

Web UI: **http://127.0.0.1:8080/** — or double-click the Desktop shortcut **HIMA Prooftest Report** (created on first service start).

**Start / Stop in the UI:** Stop ends the Prooftest engine (OPC, SILworX API, plugin monitors) but **keeps the web page up** so you can Start again. Full process exit (for SILworX uninstall) uses `.\stop_service.ps1` or `POST /api/shutdown`.

## Windows auto-start (after logon)

`solution.ini` has `auto_start = true` and `auto_start_trigger = logon` (recommended when code lives on mapped drive **Z:**). Register the scheduled task **once as Administrator**:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_auto_start.ps1
```

After reboot and logon, the service starts automatically (90 s delay, then ~90-120 s until the web UI is ready). Use `auto_start_trigger = startup` only if the solution path is on a local or UNC path visible to **SYSTEM** at boot.

To disable:

```powershell
# set auto_start = false in solution.ini, then:
powershell -ExecutionPolicy Bypass -File .\uninstall_auto_start.ps1
```

## Gate tests

```powershell
cd "Annex codes\Tool test"
python test_step13_hardening.py
```
