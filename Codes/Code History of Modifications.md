# Code History of Modifications — HIMA Prooftest Solution

| Field | Value |
|-------|--------|
| **Document** | Cumulative change log for solution **code** archives |
| **Active tree** | [HIMA-Prooftest-Solution-Current](./HIMA-Prooftest-Solution-Current/) |
| **Current `VERSION.json`** | **1.43** |
| **Paired spec** | [SPEC-001-v1.43-...](../Specifications/SPEC-001-v1.43-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) |
| **Location** | `Z:\Project\Report Solution\Codes` |
| **Filename** | `Code History of Modifications.md` |
| **Updated** | 2026-08-12 |

> **Policy:** Edit **only** `HIMA-Prooftest-Solution-Current`. Before each change, archive Current → `Archive/HIMA-Prooftest-Solution-v{next}` (`archive_current.ps1`). Archived folders are immutable. This file collects **all** code version-to-version modifications for audit (same role as [Specifications/History of Modifications.md](../Specifications/History%20of%20Modifications.md) for specs).

---

## How to maintain

1. Run `archive_current.ps1` **before** editing Current.
2. Implement the change in **Current** only; update `VERSION.json` (`spec_version`, `description`).
3. Prepend a new **### Version x.y** block at the top of **Collected modifications** below (newest first) — delta from the previous code/spec version only.
4. Do **not** edit older blocks in this file or anything under `Archive\`.

---

## Compact index (newest first)

| Code / archive | Date | Summary |
|----------------|------|---------|
| **Current → 1.43** | 2026-08-12 | ProofTest_* DDL from Results CSVs; no runtime SQL template folder |
| **Current → 1.42** | 2026-08-12 | First start: folder + SQL DB + nine ProofTest_* tables; schema sync on engine start |
| **Current → 1.40** | 2026-08-12 | Fix Stop vs in-flight Start race; immediate stop flags |
| Archive v1.39 / Current → 1.39 | 2026-08-12 | Fix UI Start after Stop: clear API suspend; `starting` health; unlock during OPC refresh |
| Archive v1.38 | 2026-08-12 | Snapshot before Start-after-Stop fix (held v1.38 engine-stop UI behaviour) |
| Current → 1.38 | 2026-08-06 | UI Stop keeps web host; Start restarts engine; `/api/stop` vs `/api/shutdown` |
| Archive v1.37 | 2026-08-06 | Snapshot before engine-stop / UI-alive change |
| Archive v1.36 | 2026-08-06 | Fix UI stop leaving plugin monitor running (OPC lock hang) |
| Archive v1.35 | 2026-07-01 | Fix `/api/health` blocking under OPC; UI false NetworkError banner |
| Archive v1.34 | 2026-07-01 | Fix `run_service.ps1` line continuations breaking auto-start |
| Archive / Current → 1.33 | 2026-07-01 | Auto-start at **logon**; `health_check_wait_sec` 120 |
| Archive / Current → 1.32 | 2026-06-19 | Windows auto-start Task Scheduler |
| Legacy v1.31 … v1.11 | 2026-06 | Pre-Current policy: one folder per SPEC (frozen under `Codes\` and/or `Archive\`) |

---

## Collected modifications (newest first)

### Version 1.43 (2026-08-12)

**Paired SPEC:** v1.43. Archive before change: v1.41.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **Table DDL** | Prefer applying `.sql` under `sql_templates` | **Generate** from Results Structure CSVs (template-style types); `.sql` optional if present |
| **Deploy** | Needed template directory on station | Ships `Results Structures\`; template path optional/empty |



### Version 1.42 (2026-08-12)

**Supersedes code 1.41 / archive snapshot v1.40.** Paired SPEC: v1.42.

#### What changed

| Topic | Before | After |
|-------|--------|-------|
| **First-start SQL** | DB connect created the database; tables waited for refresh/device sync | After connect + CSV load, **all nine** `ProofTest_*` tables are created from templates immediately |
| **Templates path** | `solution.ini` pointed at `Z:\...` | Prefer `C:\Project\Report Solution\2- SQL Tables template` with C:/Z: fallback resolver |

#### Files touched

| File | Change |
|------|--------|
| `Tool Steps/service.py` | `sync_schema_case2` on engine start (G-05 / Step 1.3) |
| `Tool Steps/config.py` | `resolve_sql_templates()` |
| `solution.ini` | `sql_templates` → C:\ path |
| `VERSION.json` | 1.42 |



### Version 1.40 (2026-08-12) — current

**Supersedes 1.39.** Active: `HIMA-Prooftest-Solution-Current`. Prior archived as `Archive/HIMA-Prooftest-Solution-v1.39`.

#### What changed from v1.39 to v1.40

| Topic | v1.39 | v1.40 (change) |
|-------|-------|----------------|
| **UI Stop vs Start race** | Stop cleaned up, but an in-flight Start could continue and recreate plugin/OPC | Start uses a **token**; Stop increments token and aborts in-flight Start |
| **Stop responsiveness** | Stop work only in background thread | `/api/stop` sets stop flags **in the HTTP request** immediately |

#### Files touched for v1.40

| File | Change |
|------|--------|
| `Tool Steps/service.py` | `_start_token`; `_start_aborted`; `request_stop_flags` |
| `Graphic Interface/app.py` | Immediate stop flags; version 1.40.0 |
| `Graphic Interface/static/app.js` | Abort `waitForEngineRunning` on Stop |
| `VERSION.json` | 1.40 |

---

### Version 1.39 (2026-08-12)

**Supersedes code/spec 1.38.** Active: `HIMA-Prooftest-Solution-Current`. Prior tree archived as `Archive/HIMA-Prooftest-Solution-v1.38`.

#### What changed from v1.38 to v1.39

| Topic | v1.38 | v1.39 (change) |
|-------|-------|----------------|
| **UI Start after Stop** | `/api/health` could block on OPC during start; SILworX API stayed **suspended** after Stop | Clear API suspend on Start; health returns fast `starting`; OPC refresh without holding engine lock |
| **UI feedback** | Start looked dead (health timeout) | UI polls until `engine_running` with “starting” banner |

#### Files touched for v1.39

| File | Change |
|------|--------|
| `Tool Steps/service.py` | `_starting`; unlock during start body; health starting/stopped paths |
| `Tool Steps/step07_triggers.py` | `prepare_for_engine_start()` clears G-19 suspend |
| `Graphic Interface/static/app.js` | `waitForEngineRunning`; starting button state |
| `Graphic Interface/app.py` | `start_in_progress`; version 1.39.0 |
| `VERSION.json` | 1.39 |

---

### Version 1.38 (2026-08-06)

**Supersedes 1.33 line for UI Stop/Start** (interim code archives 1.34–1.37 on the path). Active was Current; prior snapshot `Archive/HIMA-Prooftest-Solution-v1.37`.

#### What changed (engine stop vs process exit)

| Topic | Before | v1.38 (change) |
|-------|--------|----------------|
| **UI Stop** | `POST /api/shutdown` exited the whole process — graphic interface died | **`POST /api/stop`** stops the **engine** only; web host / UI stay on `:8080` |
| **UI Start** | Spawned a second `main.py` when the process was dead | Restarts the engine **in-process** while the UI is already open |
| **G-11 uninstall** | Same as UI Stop | Unchanged: `stop_service.ps1` / `POST /api/shutdown` / signals — **process exit** |
| **Health** | `stopping` only | Adds `engine_running`, `web_host_alive` |

#### Files touched for v1.38

| File | Change |
|------|--------|
| `Tool Steps/service.py` | Restartable engine; `request_shutdown(..., exit_process=)` |
| `Graphic Interface/app.py` | `POST /api/stop`; Start in-process; Shutdown = process exit |
| `Graphic Interface/static/app.js` | Stop/Start messaging; calls `/api/stop` |
| `Annex codes/Stop service/annex_stop_service.py` | Engine-stopped state; web host note |
| `main.py` | Log both `/api/stop` and `/api/shutdown` |
| `VERSION.json` | 1.38 |

---

### Version 1.37 (2026-08-06) — archived snapshot

**Archive reason:** UI Stop keeps web host alive; engine restartable from Start (pre-implementation snapshot / intermediate).

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.37`.

---

### Version 1.36 (2026-08-06) — archived snapshot

**Archive reason:** Fix UI stop leaving plugin monitor running (OPC lock hang).

| Topic | Before | After |
|-------|--------|-------|
| **UI Stop hang** | Shutdown called OPC `invalidate_cache` before stopping plugin monitor; lock hang left plugin retries against SILworX | Stop plugin monitor **first**; timed OPC lock; signal uvicorn exit early on process exit |

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.36`.

---

### Version 1.35 (2026-07-01) — archived snapshot

**Archive reason:** Fix health API blocking and UI false NetworkError banner.

| Topic | Before | After |
|-------|--------|-------|
| **`/api/health`** | Could block under OPC load | Non-blocking `health_snapshot()` path |
| **UI banner** | NetworkError stayed after recovery | Clear banner on success; require repeated failures |

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.35`.

---

### Version 1.34 (2026-07-01) — archived snapshot

**Archive reason:** Fix `run_service.ps1` broken line continuations breaking auto-start.

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.34`.

---

### Version 1.33 (2026-07-01)

**Supersedes 1.32.** Active: `HIMA-Prooftest-Solution-Current`. Archive: `Archive/HIMA-Prooftest-Solution-v1.33` (and related).

#### What changed from v1.32 to v1.33

| Topic | v1.32 | v1.33 (change) |
|-------|-------|----------------|
| **Auto-start trigger** | System **startup** as **SYSTEM** only | **`auto_start_trigger`** — default **`logon`** (mapped **Z:** works); optional **`startup`** |
| **Health check wait** | Fixed ~25 s sleep | **`health_check_wait_sec`** (default **120 s**), poll until `/api/health` responds |
| **Task action** | Script on **Z:** without WorkingDirectory/UNC | **WorkingDirectory** set; UNC for SYSTEM tasks |

#### Files touched for v1.33

| File | Change |
|------|--------|
| `solution.ini` | `auto_start_trigger = logon`, `health_check_wait_sec = 120` |
| `Tool Steps/config.py` | Config keys |
| `Annex codes/Stop service/annex_windows_auto_start.ps1` | Logon vs startup; UNC; WorkingDirectory |
| `run_service.ps1` | Health poll; stderr / auto_start log |

---

### Version 1.32 (2026-06-19)

**Supersedes 1.31 (legacy folder policy → Current).**

#### What changed from v1.31 to v1.32

| Topic | v1.31 | v1.32 (change) |
|-------|-------|----------------|
| **Windows auto-start** | Manual `run_service.ps1` only | Task Scheduler **`HIMA-Prooftest-Service`**; `auto_start = true` |
| **Install / remove** | — | `install_auto_start.ps1`, `uninstall_auto_start.ps1`; sync from `run_service.ps1` |

Snapshot path: `Archive/HIMA-Prooftest-Solution-v1.32`.

---

### Versions 1.31 – 1.11 (legacy / frozen)

Under the **old** policy, each SPEC bump created a new `HIMA-Prooftest-Solution-v{x.y}` folder (some also copied into `Archive\`). Those trees are **frozen**. Highlights (see also Spec History of Modifications):

| Version | Theme |
|---------|--------|
| **1.31** | Device/report list search UI |
| **1.29–1.30** | Report storage under `C:\HIMA Automated Prooftest Reports`; Gates 12–13; experimental hero (1.30) |
| **1.28** | Web GUI Start/Stop buttons; scroll list placeholders |
| **1.27** | Gate 9 SQL insert; `OUTPUT INSERTED.ID`; cumulative SPEC summary introduced |
| **1.26** | G-22 three-layer architecture; plugin monitor / one-shot session fix |
| **1.25–1.24** | Gate 8 triggers; Gate 7 approved |
| **1.23** | G-21 multi-instance API/plugin ports 51710–51719 / 8400–8409 |
| **1.22–1.19** | G-20 SILworX process cleanup; G-19 API release when SILworX closed |
| **1.17–1.11** | G-17 annex layout; G-16 annex_* files; G-15 Tool test; G-14 steps; G-13 no globals CSV; G-12 code versioning; G-11 graceful shutdown |

---

### Versions before 1.11

Initial OPC-centric Prooftest service, multi-OPC, SQL/PDF/HTML, Case 1/2, web GUI foundations — see [Specifications/History of Modifications.md](../Specifications/History%20of%20Modifications.md) compact index and archived SPEC files.

---

## Related files

| Path | Role |
|------|------|
| [README.md](./README.md) | Code versioning policy |
| [Archive/ARCHIVE_INDEX.json](./Archive/ARCHIVE_INDEX.json) | Next archive version + archive reasons |
| [archive_current.ps1](./archive_current.ps1) | Snapshot Current before edits |
| [../Specifications/History of Modifications.md](../Specifications/History%20of%20Modifications.md) | Spec-side cumulative log |
