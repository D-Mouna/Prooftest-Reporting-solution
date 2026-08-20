# Unused code index — cleanup list for `HIMA-Prooftest-Solution-Current`

| Field | Value |
|-------|--------|
| **Scope** | **Only** `Codes\HIMA-Prooftest-Solution-Current\` (not Archives, not `1-`…`7-`, not sibling folders) |
| **Purpose** | Identify old / unused files so the **Current code tree** can be cleaned |
| **Method** | Reachability from `main.py` → `ProoftestService` → Application facade / workers / UI; plus bootstrap map in `prooftest/__init__.py` |
| **Code / SPEC** | **1.73** / **1.64** (`VERSION.json`) |
| **Indexed** | 2026-08-20 |
| **Outside Current** | See [../../Legacy-Code-Index.md](../../Legacy-Code-Index.md) (archives & project folders — separate concern) |

> This file answers: *“What inside Current can I remove without breaking the running tool?”*  
> It does **not** recommend deleting SPEC gate tests unless you explicitly drop that evidence.

---

## How to read this index

| Tier | Meaning | Safe to delete for code cleanup? |
|------|---------|----------------------------------|
| **A — Dead code** | Not imported/called by the running service | **Yes** (after tiny bootstrap edit if noted) |
| **B — Stale artifacts** | Logs / markers / caches left in the tree | **Yes** (regenerated or never needed in repo) |
| **C — Test-only shims** | Only referenced by `Tool test/` | **Yes for production**, but update or keep the matching test first |
| **D — Dev operators** | Manual scripts / standalone plugin runner | **Optional** — not used by `main.py`; keep if you still use them by hand |
| **E — Keep** | Runtime, first-run seed, or SPEC verification | **No** |

---

## Tier A — Dead code (cleanup candidates)

| Path | Status |
|------|--------|
| `Tool Steps/step06_reports.py` | **Removed** in code **1.68** (archive v1.67) |
| `Annex codes/Stop service/annex_start_service.py` | **Removed** in code **1.68**; bootstrap map entry removed |
| `Tool Steps/__init__.py` | Docstring-only; optional (still present) |

Reports and UI start remain on `annex_pdf_generation.py`, `run_service.ps1`, and `/api/start` → `service.start()`.


---

## Tier B — Stale artifacts (not code, but clutter in Current)

| Path | Status |
|------|--------|
| `Annex codes/data/` | **Removed** in code **1.69** (production markers: station `Database\sync_markers`) |
| Repo-root `sync_markers/` | **Removed** in **1.69** |
| Root `auto_start.log`, `crash_*.log`, `service_stderr.log`, `startup_*.log` | **Removed** in **1.69** (recreated by `run_service.ps1` on next start) |
| All `__pycache__/` under Current | **Removed** in **1.69** (Python recreates on run) |
| `Annex codes/Plugin/message_log.json` | **Kept** — HIMA `PluginBase.log_msg` debug dump; empty `[]`; not used by production monitor (see explanation below / ask) |

Gate tests now use `Annex codes/Tool test/data/sync_markers` via `_paths.py`.

---

## Tier C — Test-only shims (old step names)

| Path | Status |
|------|--------|
| `Tool Steps/step02_database.py` | **Removed** in code **1.70**; `test_step5_sql.py` imports from `prooftest.annex_database` |
| `Annex codes/layers/fakes.py` | Still used only by `test_layers.py` — keep while layer gates stay |

---

## Tier D — Dev tools (not the service)

| Path | Status |
|------|--------|
| `Dev tools/open_graphic_interface.ps1` | **Desktop shortcut target** (code **1.73**) — first run creates Desktop “HIMA Prooftest Report” |
| `Dev tools/sync_gui_images.ps1` | Optional branding sync; see `Dev tools/README.md` |
| `install_auto_start.ps1` / `uninstall_auto_start.ps1` | **Keep** — enable/disable reboot auto-start (Task Scheduler). Not loaded at daily runtime. |

**Keep** (operators use these for the real tool): `run_service.ps1`, `stop_service.ps1`, `Annex codes/Stop service/annex_stop_service.ps1`, `annex_windows_auto_start.ps1`, `annex_plugin_monitor.py`.

---

## Tier E — Keep (not “unused”)

### Runtime code (do not delete)

```
main.py
Tool Steps/  → config, service, alarms, results_csv,
               step01_setup, step03_device_list, step04_opc,
               step05_detection, step07_triggers
Annex codes/prooftest/__init__.py
Annex codes/Database/annex_database.py, annex_list_archive.py
Annex codes/API connexion/annex_api_connexion.py
Annex codes/OPC/annex_opc.py, connection_opc.py
Annex codes/PDF generation/annex_pdf_generation.py
Annex codes/Plugin/annex_plugin_monitor.py
Annex codes/Stop service/annex_stop_service.py, annex_silworx_cleanup.py
Annex codes/layers/**  (except fakes.py — Tier C)
Graphic Interface/**
```

### First-run seed (do not delete)

| Path | Role |
|------|------|
| `Results Structures/*.csv` (9 baseline files) | Copied to station catalogue on first run |

### SPEC / gate verification (not runtime, but not “old unused product code”)

| Path | Role |
|------|------|
| `Annex codes/Tool test/` | Gate tests, fixtures, probes — keep unless you abandon automated SPEC checks |

### Config / packaging

`solution.ini`, `requirements.txt`, `VERSION.json`, `README.md`

---

## Recommended cleanup order (when you say “delete”)

1. ~~Tier B artifacts + `__pycache__`~~ — done in code **1.69** (kept `message_log.json`).  
2. ~~Tier A dead modules~~ — done in code **1.68** (`step06_reports.py`, `annex_start_service.py`).  
3. ~~Tier C `step02_database`~~ — done in code **1.70** (`fakes.py` still kept for layer tests).  
4. ~~Tier D~~ — plugin runners removed (**1.71**); branding script in `Dev tools/` (**1.72**); open-UI script is Desktop shortcut target (**1.73**). Keep install/uninstall auto-start at root.

**Do not** put `Tool test/`, `Results Structures/`, or Tier E runtime files on a delete list for “unused old codes.”

---

## Summary counts (Current only)

| Tier | Approx. | For code-file cleanup? |
|------|--------:|------------------------|
| A Dead code | done in 1.68 | Removed (`step06` / `annex_start_service`) |
| B Artifacts | done in 1.69 | Removed (kept `message_log.json`) |
| C Test shims | `fakes.py` left | `step02` removed in 1.70 |
| D Dev tools | partial | Plugin runners removed in 1.71 |
| E Keep | rest of tree | **No** |

Honest bottom line: inside Current, **almost all `.py` files are still live**. The real “old unused **code**” cleanup set is small (Tier A + optional C/D). Most bulk under Current that looks “old” is **Tier B junk** and **Tool test**, not abandoned product modules.

---

*Parent (outside Current): [../../Legacy-Code-Index.md](../../Legacy-Code-Index.md).*
