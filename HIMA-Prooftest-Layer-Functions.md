# HIMA Automated Prooftest — Functions by layer

| Field | Value |
|-------|--------|
| **Purpose** | Explain every function in Presentation, Application, Domain, and Adapters (ports) |
| **Related** | Layered architecture (not MVC for the whole engine). Web GUI is MVC; engine is use cases + domain + ports |
| **Identity** | Composite **DeviceId** = Project + Configuration + Resource + `Device_TAG` (e.g. same TAG in two projects = two rows). |

**Devices** in diagrams = this program’s catalog (`DeviceProoftestResultList` + in-memory list), not a plant cabinet and not X-OPC.

**SILworX connection** = *this tool’s* API/plugin session. `CloseSilworXconnection()` does **not** quit SILworX or close the engineer’s project.

---

## How to read this document

Each function is described as:

1. **Meaning** — one sentence  
2. **When** — who calls it  
3. **Steps** — exact work  
4. **Calls** — domain / ports  
5. **If skipped** — what breaks  

---

## Layer map

```text
Presentation (MVC)     FastAPI + HTML/JS     thin HTTP only
        ↓
Application            use cases + loops     orchestra
        ↓
Domain                 merge, test edges     no COM, no SQL
        ↓
Adapters (ports)       SILworX, OPC, Store, Reports, Alarms, Files
```

The Web GUI never talks to OPC or SILworX. Controllers only call Application.

---

# 1. Presentation layer (MVC)

**View:** `Graphic Interface/static/` (HTML/JS).  
**Controller:** `Graphic Interface/app.py` (FastAPI).  
**Model:** Application functions below — not SQL rows inside the route.

Controllers must not browse OPC, merge TAGs, or write PDFs.

| HTTP | Application function | Notes |
|------|----------------------|--------|
| `POST /api/start` | `StartEngine()` | In-process restart |
| `POST /api/stop` | `StopEngine()` | Engine only; UI stays |
| `POST /api/silworx/disconnect` | `CloseSilworXconnection()` | Release **this tool’s** SILworX links; SILworX software stays |
| `POST /api/silworx/connect` | `ResumeSilworXconnection()` | Button **Connect to SILworX** |
| `POST /api/refresh` | `RefreshCatalog()` | Manual rebuild |
| `GET /api/health` | `GetEngineStatus()` | Fast; no COM browse |
| `GET /api/devices` | `ListDevices()` | |
| `GET /api/reports` | `ListReports(tag)` | |
| `GET /api/alarms` | `ListAlarms()` | |
| `GET /api/reports/open` | `OpenReport(path)` | Path must stay under report root |

Optional host-only (not Application): process exit for uninstall (`stop_service.ps1`). That is **not** `CloseSilworXconnection()`.

**GUI SILworX badge** (this tool, not “is SILworX.exe alive”):

| Badge | Meaning |
|--------|--------|
| **not connected** | This tool has no API/plugin session. Engine may still be **running** on OPC. |
| **running** | This tool is attached and reading globals. |

---

# 2. Application layer

The orchestra. It does not import OpenOPC or `pyodbc`. It calls Domain and ports.

---

## 2.1 Engine lifecycle

### `StartEngine()`

**Meaning:** Boot the collector on this PC, then fill the device list.

**When:** UI Start, or `main.py` at process start.

**Steps (order matters):**

1. **First-run folders** — Create station directories if missing, e.g. `C:\HIMA Prooftest Reporting Tool\` with Reports (one folder per Results type), Results Structures CSVs, Database folder. Write `installation.json`.  
2. **Connect store** — Open SQL Server `HIMA Automated Prooftest` or SQLite fallback. Create catalog + `ProofTest_*` tables if needed.  
3. **Load Result types** — `LoadResultTypes()`: CSVs are **types** (ABB, E+H, …), not transmitters.  
4. **Start workers** — poll, sync, report worker (empty list until step 5).  
5. **`RefreshCatalog()`** — first real TAG list + OPC paths.

**Calls:** files, `StorePort.connect`, `LoadResultTypes`, host threads, `RefreshCatalog`.

**If skipped:** no folders, no SQL, poll has nothing to read.

**Status:** `starting` until step 5 finishes, then `running`.

---

### `StopEngine()`

**Meaning:** Stop collecting. Keep the **process and Web GUI**.

**When:** `POST /api/stop`.

**Steps:** Stop poll/sync/report/plugin workers; release **this tool’s** OPC COM and SILworX API/plugin clients; do not exit uvicorn.

**Calls:** OpcPort.disconnect, SilworxPort.disconnect (same idea as close-connection, plus stop OPC poll).

**If skipped:** Stop button leaves COM held; SILworX uninstall can fail.

**Status:** `stopped`.

---

### `CloseSilworXconnection()`

**Meaning:** This tool **hangs up** SILworX (API + plugin). It does **not** quit SILworX, does **not** `project/close` the engineer’s project, does **not** kill `c3.exe`.

**When:** Disconnect button, or operator wants OPC-only tags while SILworX stays open.

**Steps:**

1. Drop this process’s API client and cached session id.  
2. Stop plugin-monitor (8400–8409).  
3. Never `project/close` a GUI-attached session.  
4. Badge **not connected**.  
5. Engine stays **running**.  
6. `RefreshCatalog()` in **OPC-only** mode (`DiscoverOpcOnlyDevices` / bind from OPC tags).  
7. Poll `.Running` continues.

**Calls:** `SilworxPort.disconnect_client_only`, `RefreshCatalog` (OPC-only).

**If skipped:** tool keeps API sessions forever; cannot run “tags from OPC only” while leaving SILworX up.

---

### `ResumeSilworXconnection()`

**Meaning:** This tool **attaches again** to SILworX if a project is already open.

**When:** Button **Connect to SILworX**.

**Steps:** Probe API; if project open, Get TAG + type; `BindOpcPaths`; Domain.merge; badge **running**. If no project / API down: stay **not connected**, keep OPC catalog, alarm.

**Calls:** `SilworxPort`, `RefreshCatalog`.

**If skipped:** no way back to SILworX identity after disconnect.

---

### `GetEngineStatus()`

**Meaning:** Read-only snapshot for the GUI. Does not start/stop anything. Does not browse OPC (use cache) so the page does not freeze.

**When:** `GET /api/health` on a timer.

| Field | Meaning |
|--------|--------|
| **engine `starting`** | Boot in progress (folders / DB / CSVs / first catalog). Poll not useful yet. UI up. |
| **engine `running`** | Workers up. OPC usable. SILworX may be **not connected** or **running** (separate badge). |
| **engine `stopped`** | After `StopEngine()`. No poll. UI still up. |
| **opc_count** | How many **X-OPC servers** matched (`*X_OPC*` / `*HIMA*`). Not how many transmitters. `1` server can hold `12` devices. `0` = cannot Get tags. |
| **device_count** | How many **Device_TAG** rows in the catalog. After Close SILworX, still the OPC-only list size. |
| **queue_depth** | How many **finished tests** wait in the report worker (SQL/PDF not done). `0` = idle. Growing = reports lag; poll can still be healthy. |

Optional extra (not engine): `silworx: not connected | running` = **our** attachment, not “SILworX.exe is alive.”

**Calls:** in-memory engine flags, cached OPC server list, `StorePort` counts, report queue size.

**If skipped:** UI cannot show health; operators guess whether poll is on.

---

## 2.2 Catalog (device list)

### `LoadResultTypes()`

**Meaning:** Load the **structure catalogue** from Results CSVs (what members `X-HART_E+H_FTL5xB/6x_Results` has). This does **not** create devices.

**When:** Inside `StartEngine()`, and if sync sees CSV folder change.

**Steps:** Read each `*.csv` under the station Results Structures folder; build type → member names; used later to (1) recognise SILworX globals of that type, (2) know which OPC fields to snapshot, (3) know SQL table `ProofTest_*`.

**Calls:** files / config.

**If skipped:** `RefreshCatalog` cannot tell a proof-test global from any other variable.

---

### `RefreshCatalog()`

**Meaning:** Rebuild **who the devices are** (DeviceId + Results_Type) and **where they live on OPC**. Persist catalog. This is the main catalog use case.

**Production path (1.76):** `ApplicationFacade.refresh_catalog` → `CatalogService.run_station_refresh` → domain `refresh_catalog` (ports). Host still does schema / markers / service_state. Does **not** use step03 as the brain.

**When:** StartEngine, manual Refresh, Close/Resume SILworX, background sync.

**When:** End of `StartEngine()`, `POST /api/refresh`, sync loop (project/CSV change), after Close/Resume SILworX.

**Steps:**

1. Discover X-OPC servers on this PC (`OpcPort.discover_servers`) — cache for `opc_count`.  
2. If **this tool** is attached and a project is open: `SilworxPort.list_identities()` → TAG, type, Configuration, Resource.  
3. `BindOpcPaths(tags)` for those TAGs.  
4. If SILworX identity list is empty (not attached, or no project): `DiscoverOpcOnlyDevices()`.  
5. `Domain.merge` — same TAG in SILworX and OPC = **one** device (type from SILworX, path from OPC).  
6. `StorePort.upsert` catalog rows; set `present_on_opc`.  
7. `ReconcileCatalog(seen_tags)`.

**Calls:** `SilworxPort`, `OpcPort`, `Domain.merge`, `StorePort`.

**If skipped:** poll has no list; GUI devices empty.

**Same TAG in SILworX and OPC:** one row; SILworX wins type; OPC wins path and live values. Never two rows.

---

### `BindOpcPaths(tags)`

**Meaning:** For TAGs we **already know** (usually from SILworX), **construct** the OPC item — do not scan the whole tree to invent devices.

**When:** Inside `RefreshCatalog()` when identities exist.

**Steps:** For each TAG, in order, on each known X-OPC server:

1. `OTS ProofTest.{TAG}.Running`  
2. `OPC ProofTest.{TAG}.Running`  

If the item exists → `opc_item_prefix` = `{branch}.{TAG}`, `present_on_opc = yes`.  
If not → keep the SILworX device, `present_on_opc = no` (do not poll).

**Calls:** `OpcPort.find_path`.

**If skipped:** catalog has TAGs but poll cannot read `.Running`.

---

### `DiscoverOpcOnlyDevices()`

**Meaning:** Build the list **only from OPC** when this tool has **no** SILworX identities (not attached, or no open project). Still does not quit SILworX.

**When:** `RefreshCatalog()` when SILworX is not attached, and for TAGs not in the SILworX identity list.

**Steps:** Browse only branches `OTS ProofTest` and `OPC ProofTest`. Candidate = `{branch}.{TAG}.Running` where TAG has **no** `.` (rejects `SomeFlag.Running` and dotted mid-segments). **Shape gate:** ≥3 members shared with ≥1 known Results type (includes Running) or ignore. **Type:** last SQL type if known; else unique clear best (best≥3 and best−second≥2); else **unknown** — no `ProofTest_*` snapshot until type known.

**Calls:** `OpcPort` browse + `layers.domain.opc_discover` (not invent scorer).

**If skipped:** disconnecting this tool from SILworX leaves an empty catalog even though OPC still has tags.

---

### `ReconcileCatalog(seen_tags)`

**Meaning:** TAGs that disappeared from SILworX/OPC this refresh must not destroy history.

**When:** End of `RefreshCatalog()`.

**Steps:** Mark missing TAGs inactive / not on OPC. **Do not** delete `ProofTest_*` snapshot rows or report files.

**Calls:** `StorePort`.

**If skipped:** a gone transmitter wipes audit reports, or the list fills with ghosts forever (pick a policy: inactive flag, not delete).

---

## 2.3 Live proof test

### `PollOnce()`

**Meaning:** One pass over devices that have an OPC path: read `.Running`, detect start/end edges.

**When:** poll loop, about every 1 s, only if engine is **running**.

**Steps:** `ListDevices` with `present_on_opc`; skip others. `OpcPort.read_running(prefix)`. Compare with last value in Domain (memory, not SQL every second). Rising → `OnTestStarted`. Falling → `OnTestEnded`. No edge → nothing.

**Calls:** `OpcPort.read_running`, Domain edge detector.

**If skipped:** tests finish and nothing is stored.

---

### `OnTestStarted(tag)`

**Meaning:** `.Running` went **false → true**. Test began. **Do not** snapshot Results yet (values change during the test).

**When:** Domain, from `PollOnce()`.

**Steps:** State `idle → running`. Optional `StorePort` flag `test_in_progress = true`. Log TAG.

**Calls:** Domain, optional Store.

**If skipped:** cannot tell “in progress” on the GUI; end edge still works if last_running is tracked in memory.

---

### `OnTestEnded(tag)`

**Meaning:** `.Running` went **true → false**. Test may be finished. Confirm before snapshot (flicker).

**When:** Domain, from `PollOnce()`.

**Steps:** Read `.Running` once more. If true again → ignore (flicker). If still false → `CompleteTest(tag)` (queue to report worker; do not block poll).

**Calls:** `OpcPort.read_running`, then `CompleteTest`.

**If skipped:** falling edge never produces a report.

---

### `CompleteTest(tag)`

**Meaning:** After a confirmed end: copy Results from OPC, save SQL, write report.

**When:** Report worker, queued by `OnTestEnded`.

**Steps:**

1. `OpcPort.read_results(prefix, member names from Result type)`.  
2. `StorePort.insert_snapshot` into the matching `ProofTest_*` table.  
3. `ReportPort.write` HTML/PDF under `Reports\{type}\{TAG}\`.  
4. Set `ReportPath` on the SQL row.  
5. Clear `test_in_progress`. Note bad OPC quality; still save row + alarm.

**Calls:** `OpcPort.read_results`, `StorePort`, `ReportPort`.

**If skipped:** test ended in the field but no audit file.

**Same TAG case:** snapshot uses **that** device’s OPC path only — one PDF.

---

### `OnTestInterrupted(tag, reason)`

**Meaning:** Test was in progress but we **must not** pretend we have a complete snapshot (OPC gone, tag disappeared).

**When:** `PollOnce` / refresh sees `test_in_progress` and `present_on_opc = no`, or COM failure.

**Steps:** No `insert_snapshot`. Alarm with reason. Clear `test_in_progress`. Keep old reports.

**Calls:** Store, alarms.

**If skipped:** missing OPC looks like a successful test with empty/wrong values.

---

## 2.4 Reports and queries (GUI)

### `ListDevices()`

**Meaning:** Catalog rows for the UI table.

**When:** `GET /api/devices`.

**Steps:** Read store (TAG, type, OPC path, present_on_opc, test_in_progress). Engine **stopped** → empty list (or last snapshot — pick one; prefer empty so UI matches `stopped`).

**Calls:** `StorePort`.

---

### `ListReports(tag)`

**Meaning:** Past reports for one TAG.

**When:** `GET /api/reports?device=`.

**Steps:** `ReportPath` on snapshot rows and/or files under that device folder.

**Calls:** Store + report folder.

---

### `ListAlarms()`

**Meaning:** Recent errors + popup queue (which Step/action failed).

**When:** `GET /api/alarms`.

**Calls:** Store / alarm port.

---

### `OpenReport(path)`

**Meaning:** Return the file only if it is under the configured report root (no path traversal).

**When:** `GET /api/reports/open`.

**Calls:** files.

---

## 2.5 Background loops

These are **not** extra business rules. They only call the functions above.

| Loop | Period | Calls |
|------|--------|--------|
| **poll** | ~1 s | `PollOnce()` |
| **sync** | ~0.5–2 s | If this tool is attached: SILworX reachable? Project/CSV changed? → `RefreshCatalog()`. Does not close SILworX. |
| **report worker** | queue | `CompleteTest` SQL + files off the poll thread |

Plugin session events (if attached) only mean “catalog may be stale” → `RefreshCatalog()`.

---

# 3. Domain layer

No FastAPI, no OpenOPC, no SQL. Pure rules.

### `Device` (entity)

Fields: `Device_TAG`, `Results_Type`, `configuration`, `resource`, `opc_server`, `opc_item_prefix`, `present_on_opc`, test state `idle | running | completing`.

### `merge(silworx_identities, opc_bindings) → catalog`

- Key = **DeviceId** (Project + Configuration + Resource + Device_TAG), not TAG alone.
- API wins Results_Type / project fields; OPC wins server / prefix / PresentOnOpc.
- Same TAG in two projects → two rows.
- OPC path collision → alarm; one bind kept. 
- **In both:** one device; type/config from SILworX; path from OPC; `present_on_opc = yes`.  
- **SILworX only:** keep TAG; `present_on_opc = no`.  
- **OPC only:** TAG = folder name; type = last stored or unknown until SILworX attach.

### `on_running_sample(tag, previous, current) → none | started | ended`

- false→true → started  
- true→false → ended  
- else → none  

### `should_snapshot_after_fall(running_reread) → bool`

Snapshot only if still false (anti-flicker).

---

# 4. Adapter layer (ports)

Application calls **ports**. Implementations live in adapters.

## 4.1 `SilworxPort`

| Function | Does |
|----------|------|
| `is_reachable()` | Probe API ports (e.g. 51710–51719) |
| `list_identities()` | If project open: globals whose type is a loaded `*_Results` type → TAG, type, config, resource. Never live Results. |
| `disconnect_client_only()` | Drop **this tool’s** client/plugin. Do not quit SILworX, do not `project/close` GUI sessions. |
| `attach()` | Resume: attach to existing open project (Mode B). |

**Must not:** publish OPC server list as devices; read `.Running`.

---

## 4.2 `OpcPort`

| Function | Does |
|----------|------|
| `discover_servers()` | `opc.servers("localhost")`, filter `*X_OPC*` / `*HIMA*`. Cached for `opc_count`. |
| `find_path(tag)` | Test `OTS ProofTest.{tag}.Running` then `OPC ProofTest.{tag}.Running`. |
| `list_running_folders()` | OPC-only catalog: child folders under those branches that have `.Running`. |
| `read_running(prefix)` | One item `{prefix}.Running`. |
| `read_results(prefix, members)` | All Result fields except Running (or including as needed). |
| `disconnect()` | Release COM on this thread. |

One OPC client **per thread** (COM STA). Poll and refresh must not share one COM object.

---

## 4.3 `StorePort`

| Function | Does |
|----------|------|
| `connect()` / `close()` | SQL Server or SQLite |
| `upsert_device(...)` | Catalog row by TAG |
| `set_present_on_opc(tags)` | Flags |
| `insert_snapshot(table, tag, values)` | `ProofTest_*` |
| `update_report_path(...)` | After PDF |
| `list_devices()` / `list_alarms()` | GUI |
| `mark_inactive(tags)` | Reconcile; never delete snapshots |

---

## 4.4 `ReportPort`

| Function | Does |
|----------|------|
| `write(tag, type, snapshot)` | HTML/PDF; return path |
| `list_for_device(tag)` | Files for UI |

---

## 4.5 `AlarmPort`

`raise(step, message, tag?)` — persist + optional GUI popup. Application maps failures to Step names (catalog, OPC, snapshot, report).

---

# 5. One proof test through all layers

```text
Presentation     POST /api/start
Application      StartEngine()
                   folders → store → LoadResultTypes → workers → RefreshCatalog()
Presentation     GET /api/health → GetEngineStatus()  (starting then running)

RefreshCatalog   SilworxPort.list_identities  (if attached)
                 BindOpcPaths / DiscoverOpcOnlyDevices
                 Domain.merge
                 StorePort.upsert

poll ~1s         PollOnce → OpcPort.read_running → Domain edge
                 false→true  OnTestStarted
                 true→false  OnTestEnded → queue CompleteTest
report worker    CompleteTest → read_results → insert_snapshot → ReportPort.write

Presentation     GET /api/devices, /api/reports
```

**Same TAG in SILworX and OPC:** `Domain.merge` in `RefreshCatalog` produces one catalog row; `CompleteTest` uses that row’s OPC path once.

---

# 6. What each layer must not do

| Layer | Must not |
|--------|----------|
| Presentation | COM, merge, PDF, SQL |
| Application | Guess type by CSV score when SILworX already gave TAG; SQL every 1 s poll; kill `c3.exe` |
| Domain | Import FastAPI / OpenOPC / pyodbc |
| SilworxPort | Live `.Running` / Results; quitting SILworX |
| OpcPort | Decide Configuration/Resource |
| StorePort | Business merge rules |

---

*End of document*
