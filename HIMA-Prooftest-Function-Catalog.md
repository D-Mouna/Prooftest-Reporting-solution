# HIMA Automated Prooftest — Class & function reference

| Field | Value |
|-------|--------|
| **Generated** | 2026-08-24 |
| **Format** | Grouped by **class**; each method: Does · Needs · Calls · Returns |
| **Use-case guide** | [HIMA-Prooftest-Layer-Functions.md](./HIMA-Prooftest-Layer-Functions.md) |
| **Regenerate** | `python Dev tools/generate_function_catalog.py` |
| **Classes / modules** | 75 classes in 45 files |
| **Functions / methods** | 732 |

Each entry uses:

- **Does** — what the function accomplishes (from docstring or inference)
- **Needs** — parameters and `self.*` dependencies
- **Calls** — other functions/methods invoked (static analysis)
- **Returns** — return type or inferred return value

---

## Entry point

### File `main.py`

**Layer:** Entry point

**Module purpose:** HIMA Automated Prooftest Solution — SPEC-001 v1.18.

#### Module-level functions *(no class)*

##### `parse_args()` · line 30

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `argparse.ArgumentParser`
- `parser.add_argument`
- `Path(__file__).resolve`
- `Path`
- `parser.parse_args`

**Returns:** argparse.Namespace

##### `main()` · line 43

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `log.error`
- `parse_args`
- `AppConfig.load`
- `config.apply_auth_bind_policy`
- `ProoftestService`
- `service.start`
- `create_app`
- `uvicorn.Config`
- `uvicorn.Server`
- `signal.signal`
- `hasattr`
- `log.warning`
- `log.info`
- `server.run`
- `service.stop`

**Returns:** int

---

## Presentation — View wrapper

### File `Graphic Interface/app.py`

**Layer:** Presentation — View wrapper

**Module purpose:** *(no module docstring)*

#### Module-level functions *(no class)*

##### `_is_local_client(request: Request)` · line 16

**Does:** Gate tests patch this symbol to bypass localhost-only checks.

**Needs:**
- Parameters: `request: Request`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `create_app(service: 'ProoftestService', on_shutdown: Optional[Callable[[str], None]] = None)` · line 24

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `service: 'ProoftestService', on_shutdown: Optional[Callable[[str], None]] = None`

**Calls:**
- `_create_app`

**Returns:** `_create_app(service, on_shutdown=on_shutdown, static_dir=STATIC_DIR, version=…` (inferred)

---

## Presentation — View (JavaScript)

### File `Graphic Interface/static/app.js`

**Layer:** Presentation — View (JavaScript)

**Module purpose:** Browser UI module — all functions live in global scope (no ES6 class). Documented as one virtual module.

#### Class `app.js (global functions)` · line 1

**Inherits:** `—`

**Purpose:** Single-page UI: navigation, polling, health tiles, devices, reports, service buttons.

##### `function currentTheme()` · line 20

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function applyTheme(theme)` · line 25

**Does:** *(no comment)*

**Needs:**
- Parameters: `theme`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function setupThemeToggle()` · line 40

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `addEventListener`

**Returns:** `undefined` or `Promise` (async functions)

##### `function showPage(pageId)` · line 49

**Does:** *(no comment)*

**Needs:**
- Parameters: `pageId`

**Calls:**
- `showPage()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function setupNavigation()` · line 63

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `showPage()`
- `showPage()`
- `addEventListener`

**Returns:** `undefined` or `Promise` (async functions)

##### `function silworxProjectNameFromHealth(data)` · line 81

**Does:** *(no comment)*

**Needs:**
- Parameters: `data`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function silworxProjectDeviceCount(data)` · line 109

**Does:** *(no comment)*

**Needs:**
- Parameters: `data`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function updateSummaryChips(data)` · line 115

**Does:** *(no comment)*

**Needs:**
- Parameters: `data`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function shortAlarmTitle(message)` · line 166

**Does:** *(no comment)*

**Needs:**
- Parameters: `message`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function currentDeviceView()` · line 174

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function setupDeviceViewOptions()` · line 180

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `loadDevices()`
- `addEventListener`

**Returns:** `undefined` or `Promise` (async functions)

##### `function vendorLogo(resultsType)` · line 205

**Does:** *(no comment)*

**Needs:**
- Parameters: `resultsType`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function formatResultsTypeLabel(resultsType)` · line 210

**Does:** *(no comment)*

**Needs:**
- Parameters: `resultsType`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function listSearchableItems(list)` · line 226

**Does:** *(no comment)*

**Needs:**
- Parameters: `list`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function deviceColumnFilters()` · line 235

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function rowMatchesColumnFiltersFixed(row, filters)` · line 246

**Does:** *(no comment)*

**Needs:**
- Parameters: `row, filters`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function applyDeviceFilters(advance = false)` · line 261

**Does:** *(no comment)*

**Needs:**
- Parameters: `advance = false`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function applyListSearch(inputId, listId, stateKey, advance = false)` · line 323

**Does:** *(no comment)*

**Needs:**
- Parameters: `inputId, listId, stateKey, advance = false`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function setDeviceFiltersVisible(visible)` · line 363

**Does:** *(no comment)*

**Needs:**
- Parameters: `visible`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function updateDeviceFilterToggleState(filters)` · line 376

**Does:** *(no comment)*

**Needs:**
- Parameters: `filters`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function clearAllDeviceColumnFilters()` · line 384

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function setupDeviceColumnFilters()` · line 392

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `addEventListener`

**Returns:** `undefined` or `Promise` (async functions)

##### `function setupListSearch(inputId, listId, stateKey)` · line 432

**Does:** *(no comment)*

**Needs:**
- Parameters: `inputId, listId, stateKey`

**Calls:**
- `addEventListener`

**Returns:** `undefined` or `Promise` (async functions)

##### `function showListPlaceholder(listId, text)` · line 447

**Does:** *(no comment)*

**Needs:**
- Parameters: `listId, text`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function healthLooksComplete(data)` · line 459

**Does:** *(no comment)*

**Needs:**
- Parameters: `data`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function catalogRefreshBusy(health)` · line 471

**Does:** *(no comment)*

**Needs:**
- Parameters: `health`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function waitForCatalogRefreshIdle(timeoutMs = 180000)` · line 476

**Does:** *(no comment)*

**Needs:**
- Parameters: `timeoutMs = 180000`

**Calls:**
- `/api/health`
- `fetchJson()`
- `renderHealth()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function updateServiceButtons(health)` · line 519

**Does:** *(no comment)*

**Needs:**
- Parameters: `health`

**Calls:**
- `/api/health`
- `fetchJson()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function waitForEngineRunning(timeoutMs = 180000)` · line 556

**Does:** *(no comment)*

**Needs:**
- Parameters: `timeoutMs = 180000`

**Calls:**
- `/api/health`
- `fetchJson()`
- `pollStatus()`
- `loadDevices()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function escapeHtml(text)` · line 596

**Does:** *(no comment)*

**Needs:**
- Parameters: `text`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function showServiceBanner(message)` · line 604

**Does:** *(no comment)*

**Needs:**
- Parameters: `message`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function hideServiceBanner()` · line 610

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function apiAuthToken()` · line 614

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function fetchJson(path, options)` · line 625

**Does:** *(no comment)*

**Needs:**
- Parameters: `path, options`

**Calls:**
- `fetchJson()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function apiErrorText(err)` · line 657

**Does:** *(no comment)*

**Needs:**
- Parameters: `err`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function metricIcon(kind)` · line 668

**Does:** *(no comment)*

**Needs:**
- Parameters: `kind`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function parsePluginSessions(data)` · line 723

**Does:** *(no comment)*

**Needs:**
- Parameters: `data`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function pluginSessionIconsHtml(sessions, registered)` · line 753

**Does:** *(no comment)*

**Needs:**
- Parameters: `sessions, registered`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function healthMetricTile(label, value, hint, tone, state, textValue, wide, iconKind, iconHtml)` · line 764

**Does:** *(no comment)*

**Needs:**
- Parameters: `label, value, hint, tone, state, textValue, wide, iconKind, iconHtml`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function healthCard(label, value, state)` · line 795

**Does:** *(no comment)*

**Needs:**
- Parameters: `label, value, state`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function opcServerTableRow(server)` · line 799

**Does:** *(no comment)*

**Needs:**
- Parameters: `server`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function renderOpcServerTable(servers, emptyMessage)` · line 836

**Does:** *(no comment)*

**Needs:**
- Parameters: `servers, emptyMessage`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function renderHealth(data)` · line 847

**Does:** *(no comment)*

**Needs:**
- Parameters: `data`

**Calls:**
- `renderHealth()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function renderOfflineHealth()` · line 1068

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function renderAlarms(payload)` · line 1082

**Does:** *(no comment)*

**Needs:**
- Parameters: `payload`

**Calls:**
- `fetchJson()`
- `pollStatus()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function showPopup(popup)` · line 1161

**Does:** *(no comment)*

**Needs:**
- Parameters: `popup`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function deviceTestCell(device)` · line 1172

**Does:** *(no comment)*

**Needs:**
- Parameters: `device`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function loadDevices()` · line 1187

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `loadDevices()`
- `fetchJson()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function updateSelectedLabel()` · line 1320

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function formatStartedAt(value)` · line 1330

**Does:** *(no comment)*

**Needs:**
- Parameters: `value`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function renderRunningTests(tests)` · line 1337

**Does:** *(no comment)*

**Needs:**
- Parameters: `tests`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function loadRunningTests()` · line 1356

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `/api/running-tests`
- `fetchJson()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function historyRowHtml(t)` · line 1369

**Does:** *(no comment)*

**Needs:**
- Parameters: `t`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function renderHistoryModal(rows)` · line 1391

**Does:** *(no comment)*

**Needs:**
- Parameters: `rows`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function openHistoryModal()` · line 1402

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `/api/test-history`
- `fetchJson()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function closeHistoryModal()` · line 1422

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function reportBadge(name)` · line 1427

**Does:** *(no comment)*

**Needs:**
- Parameters: `name`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function loadReports()` · line 1434

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `fetchJson()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function refreshAll(manual = false)` · line 1493

**Does:** *(no comment)*

**Needs:**
- Parameters: `manual = false`

**Calls:**
- `/api/refresh`
- `loadDevices()`
- `fetchJson()`
- `pollStatus()`
- `loadDevices()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function pollStatus()` · line 1527

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `/api/health`
- `/api/alarms`
- `pollStatus()`
- `fetchJson()`
- `renderHealth()`
- `loadDevices()`
- `fetchJson()`
- `loadDevices()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function waitForEngineStopped(timeoutMs = 45000)` · line 1681

**Does:** *(no comment)*

**Needs:**
- Parameters: `timeoutMs = 45000`

**Calls:**
- `/api/health`
- `fetchJson()`
- `pollStatus()`

**Returns:** `undefined` or `Promise` (async functions)

##### `function showArchivePath(path)` · line 1744

**Does:** *(no comment)*

**Needs:**
- Parameters: `path`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function closeImportExportMenu()` · line 1756

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function filenameFromDisposition(value, fallbackName)` · line 1761

**Does:** *(no comment)*

**Needs:**
- Parameters: `value, fallbackName`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

##### `function exportArchiveToUserLocation()` · line 1776

**Does:** *(no comment)*

**Needs:**
- Parameters: `none`

**Calls:**
- `*(DOM / local state only)*`

**Returns:** `undefined` or `Promise` (async functions)

---

## Presentation — Controller

### File `Annex codes/layers/presentation/__init__.py`

**Layer:** Presentation — Controller

**Module purpose:** *(no module docstring)*

*(empty module)*

### File `Annex codes/layers/presentation/controllers.py`

**Layer:** Presentation — Controller

**Module purpose:** Presentation layer — FastAPI controllers. Call Application only (no OPC/SQL/PDF/annex).

#### Module-level functions *(no class)*

##### `is_local_client(request: Request)` · line 20

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `request: Request`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `_is_local_client(request: Request)` · line 27

**Does:** Test compatibility:
Gate tests patch `prooftest.web.app._is_local_client`.
Controllers should consult that symbol so localhost-only endpoints
can be bypassed during tests.

**Needs:**
- Parameters: `request: Request`

**Calls:**
- `getattr`
- `callable`
- `bool`
- `fn`
- `is_local_client`

**Returns:** bool

##### `auth_ok(request: Request, service: 'ProoftestService')` · line 45

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `request: Request, service: 'ProoftestService'`

**Calls:**
- `_is_local_client`
- `request.headers.get`
- `request.query_params.get`
- `bool`

**Returns:** bool

##### `application(service: 'ProoftestService')` · line 54

**Does:** Return the Application facade — Presentation's only door.

**Needs:**
- Parameters: `service: 'ProoftestService'`

**Calls:**
- `getattr`
- `RuntimeError`

**Returns:** `app` (inferred)

##### `register_routes(app: FastAPI, ctx: WebApp)` · line 461

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI, ctx: WebApp`

**Calls:**
- `app.mount`
- `StaticFiles`
- `str`
- `StatusController(ctx).register`
- `StatusController`
- `EngineController(ctx).register`
- `EngineController`
- `SilworxController(ctx).register`
- `SilworxController`
- `DeviceController(ctx).register`
- `DeviceController`
- `CatalogController(ctx).register`
- `CatalogController`
- `ReportController(ctx).register`
- `ReportController`
- `AlarmController(ctx).register`
- `AlarmController`

**Returns:** None

#### Class `WebApp` · line 67

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, service: 'ProoftestService', static_dir, version)` · line 68

**Does:** Internal helper.

**Needs:**
- Parameters: `service: 'ProoftestService', static_dir, version`
- Uses instance: `self.alarms_cache`, `self.alarms_cache_lock`, `self.alarms_cache_ttl_sec`, `self.service`, `self.static_dir`, `self.version`

**Calls:**
- `threading.Lock`

**Returns:** None

##### `index_html(self)` · line 82

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.static_dir`

**Calls:**
- `(self.static_dir / 'index.html').read_text`
- `html.replace`

**Returns:** str

#### Class `StatusController` · line 89

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, ctx: WebApp)` · line 90

**Does:** Internal helper.

**Needs:**
- Parameters: `ctx: WebApp`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `register(self, app: FastAPI)` · line 93

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `EngineController` · line 115

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, ctx: WebApp)` · line 116

**Does:** Internal helper.

**Needs:**
- Parameters: `ctx: WebApp`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `register(self, app: FastAPI)` · line 119

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `SilworxController` · line 213

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, ctx: WebApp)` · line 214

**Does:** Internal helper.

**Needs:**
- Parameters: `ctx: WebApp`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `register(self, app: FastAPI)` · line 217

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `DeviceController` · line 254

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, ctx: WebApp)` · line 255

**Does:** Internal helper.

**Needs:**
- Parameters: `ctx: WebApp`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `register(self, app: FastAPI)` · line 258

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `CatalogController` · line 269

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, ctx: WebApp)` · line 270

**Does:** Internal helper.

**Needs:**
- Parameters: `ctx: WebApp`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `register(self, app: FastAPI)` · line 273

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `ReportController` · line 363

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, ctx: WebApp)` · line 364

**Does:** Internal helper.

**Needs:**
- Parameters: `ctx: WebApp`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `register(self, app: FastAPI)` · line 367

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `AlarmController` · line 417

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, ctx: WebApp)` · line 418

**Does:** Internal helper.

**Needs:**
- Parameters: `ctx: WebApp`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `register(self, app: FastAPI)` · line 421

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `app: FastAPI`
- Uses instance: `self.ctx`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

### File `Annex codes/layers/presentation/web_app.py`

**Layer:** Presentation — Controller

**Module purpose:** WebApp factory — Presentation entry. Routes live in controllers.

#### Module-level functions *(no class)*

##### `create_app(service: 'ProoftestService', on_shutdown: Optional[Callable[[str], None]] = None, static_dir, version)` · line 18

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `service: 'ProoftestService', on_shutdown: Optional[Callable[[str], None]] = None, static_dir, version`

**Calls:**
- `service.set_shutdown_callback`
- `FastAPI`
- `WebApp`
- `register_routes`

**Returns:** FastAPI

---

## Application — Service

### File `Annex codes/layers/application/__init__.py`

**Layer:** Application — Service

**Module purpose:** *(no module docstring)*

*(empty module)*

### File `Annex codes/layers/application/catalog_service.py`

**Layer:** Application — Service

**Module purpose:** CatalogService: LoadResultTypes, RefreshCatalog, BindOpcPaths, DiscoverOpcOnly, ReconcileCatalog.

#### Class `CatalogService` · line 19

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, store: StorePort, opc: OpcPort, silworx: SilworxPort, alarms: AlarmPort, types_folder = None, merger = None, archive = None)` · line 20

**Does:** Internal helper.

**Needs:**
- Parameters: `store: StorePort, opc: OpcPort, silworx: SilworxPort, alarms: AlarmPort, types_folder = None, merger = None, archive = None`
- Uses instance: `self.alarms`, `self.archive`, `self.devices`, `self.last_api_identity_count`, `self.last_api_identity_tags`, `self.merger`, `self.opc`, `self.silworx`, `self.store`, `self.types`, `self.types_folder`

**Calls:**
- `CatalogMerger`
- `ResultTypeCatalog`

**Returns:** None

##### `load_result_types(self, folder: Optional[Path] = None)` · line 43

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `folder: Optional[Path] = None`
- Uses instance: `self.alarms`, `self.types`, `self.types_folder`

**Calls:**
- `ResultTypeCatalog`
- `self.alarms.raise_alarm`
- `ResultTypeCatalog.from_csv_folder`

**Returns:** ResultTypeCatalog

##### `sync_types_from_structures(self, structures: dict)` · line 63

**Does:** Mirror production ResultsStructure dict into ResultTypeCatalog (shape gate).

**Needs:**
- Parameters: `structures: dict`
- Uses instance: `self.types`

**Calls:**
- `ResultTypeCatalog`
- `type_members_from_structures(structures).items`
- `type_members_from_structures`
- `ResultType`
- `tuple`
- `sorted`

**Returns:** None

##### `bind_opc_paths(self, identities: list[SilworxIdentity])` · line 70

**Does:** Bind each SILworX TAG to ``…{TAG}.Running`` on any browsed HIMA.* server.

**Needs:**
- Parameters: `identities: list[SilworxIdentity]`
- Uses instance: `self.alarms`, `self.opc`

**Calls:**
- `self.opc.discover_servers`
- `self.alarms.raise_alarm`
- `hasattr`
- `self.opc.list_tags_all_servers`
- `self.opc.find_running_path`
- `path.endswith`
- `len`
- `OpcObservation`
- `observations.append`

**Returns:** list[OpcObservation]

##### `_last_types_by_tag(self)` · line 111

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.devices`, `self.store`

**Calls:**
- `self.store.list_devices`
- `str`
- `row.get`
- `str(row.get('results_type') or '').strip`
- `last.setdefault`

**Returns:** dict[str, str]

##### `discover_opc_only_devices(self)` · line 127

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._last_types_by_tag`, `self.alarms`, `self.opc`, `self.types`

**Calls:**
- `self.opc.discover_servers`
- `self.alarms.raise_alarm`
- `self.opc.discover_opc_only`
- `self.types.names`
- `self._last_types_by_tag`

**Returns:** list[OpcObservation]

##### `refresh_catalog(self)` · line 139

**Does:** Triggers or participates in catalog refresh.

**Needs:**
- Uses instance: `self.alarms`, `self.archive`, `self.bind_opc_paths`, `self.devices`, `self.discover_opc_only_devices`, `self.last_api_identity_count`, `self.last_api_identity_tags`, `self.merger`, `self.reconcile_catalog`, `self.silworx`, `self.store`, `self.types`

**Calls:**
- `self.silworx.has_open_project`
- `self.silworx.is_attached`
- `self.silworx.list_identities`
- `self.types.names`
- `self.alarms.raise_alarm`
- `len`
- `sorted`
- `str`
- `getattr`
- `self.bind_opc_paths`
- `self.discover_opc_only_devices`
- `OpcObservation`
- `next`
- `d.device_id.key`
- `self.store.list_devices`
- `device_from_row`
- `existing.setdefault`
- `device.device_id.key`
- `self.merger.merge`
- `bool`
- `self.archive.keep_opc_only_enabled`
- `host_db.get_service_state`
- `state.get`
- `str(getattr(device, 'project', '') or '').strip`
- `self.store.upsert_device`
- `… +5 more`

**Returns:** list[Device]

##### `reconcile_catalog(self, active_ids: list[str])` · line 285

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `active_ids: list[str]`
- Uses instance: `self.alarms`, `self.store`

**Calls:**
- `self.store.reconcile`
- `self.alarms.raise_alarm`
- `str`

**Returns:** None

##### `run_station_refresh(self, host: object, manual = False)` · line 291

**Does:** Production RefreshCatalog — Domain/ports merge is the brain (Gap B).

**Needs:**
- Parameters: `host: object, manual = False`
- Uses instance: `self.load_result_types`, `self.refresh_catalog`, `self.silworx`, `self.sync_types_from_structures`, `self.types`, `self.types_folder`

**Calls:**
- `getattr`
- `stop.is_set`
- `host.db.set_service_state`
- `callable`
- `sync_fn`
- `host.alarms.clear_shown_on_refresh`
- `host.opc.discover_servers`
- `inval`
- `host.opc.invalidate_cache`
- `host.alarms.raise_alarm`
- `str`
- `self.sync_types_from_structures`
- `self.load_result_types`
- `self.refresh_catalog`
- `any`
- `bool`
- `self.silworx.is_attached`
- `sorted`
- `host.db.sync_schema_case1`
- `list`
- `host.structures.keys`
- `log.warning`
- `sync_device_report_folders`
- `host._case1_sync.commit`
- `host._publish_silworx_state`
- `… +7 more`

**Returns:** dict

### File `Annex codes/layers/application/engine.py`

**Layer:** Application — Service

**Module purpose:** Engine: StartEngine / StopEngine / GetEngineStatus. Workers / host hooks injectable.

#### Class `Engine` · line 14

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, store: StorePort, opc: OpcPort, silworx: SilworxPort, reports: ReportPort, alarms: AlarmPort, catalog: CatalogService, live: LiveTestService, silworx_conn: Optional[SilworxConnectionService] = None, start_workers = None, stop_workers = None, status_fn = None, start_fn = None, stop_fn = None, refresh_fn = None)` · line 15

**Does:** Internal helper.

**Needs:**
- Parameters: `store: StorePort, opc: OpcPort, silworx: SilworxPort, reports: ReportPort, alarms: AlarmPort, catalog: CatalogService, live: LiveTestService, silworx_conn: Optional[SilworxConnectionService] = None, start_workers = None, stop_workers = None, status_fn = None, start_fn = None, stop_fn = None, refresh_fn = None`
- Uses instance: `self._refresh_fn`, `self._start_fn`, `self._start_workers`, `self._status_fn`, `self._stop_fn`, `self._stop_workers`, `self.alarms`, `self.catalog`, `self.engine_state`, `self.live`, `self.opc`, `self.reports`, `self.silworx`, `self.silworx_conn`, `self.store`, `self.workers_started`

**Calls:**
- `SilworxConnectionService`

**Returns:** None

##### `start_engine(self)` · line 50

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._start_fn`, `self._start_workers`, `self.alarms`, `self.catalog`, `self.engine_state`, `self.store`, `self.workers_started`

**Calls:**
- `self._start_fn`
- `self.store.ensure_folders`
- `self.alarms.raise_alarm`
- `str`
- `self.store.connect`
- `self.catalog.load_result_types`
- `self._start_workers`
- `self.catalog.refresh_catalog`

**Returns:** str

##### `stop_engine(self)` · line 89

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._stop_fn`, `self._stop_workers`, `self.engine_state`, `self.silworx`, `self.workers_started`

**Calls:**
- `self._stop_fn`
- `self._stop_workers`
- `self.silworx.detach`

**Returns:** str

##### `refresh_catalog(self)` · line 107

**Does:** Triggers or participates in catalog refresh.

**Needs:**
- Uses instance: `self._refresh_fn`, `self.catalog`

**Calls:**
- `self._refresh_fn`
- `self.catalog.refresh_catalog`

**Returns:** None

##### `get_engine_status(self)` · line 113

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._status_fn`, `self.alarms`, `self.catalog`, `self.engine_state`, `self.live`, `self.opc`, `self.silworx`

**Calls:**
- `dict`
- `self._status_fn`
- `self.opc.discover_servers`
- `self.alarms.raise_alarm`
- `str`
- `self.silworx.is_attached`
- `len`
- `self.alarms.last_error`

**Returns:** dict

### File `Annex codes/layers/application/errors.py`

**Layer:** Application — Service

**Module purpose:** Step codes and last-error mapping at the Application boundary.

#### Class `RecordingAlarmPort` · line 17

**Inherits:** `—`

**Purpose:** In-memory AlarmPort for tests and Engine.last_error.

##### `__init__(self)` · line 20

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._last`, `self.alarms`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `raise_alarm(self, step: str, action: str, message: str, device_tag = None, severity = 'Error')` · line 24

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `step: str, action: str, message: str, device_tag = None, severity = 'Error'`
- Uses instance: `self._last`, `self.alarms`

**Calls:**
- `self.alarms.append`

**Returns:** None

##### `last_error(self)` · line 43

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._last`

**Calls:**
- `dict`

**Returns:** Optional[dict]

### File `Annex codes/layers/application/facade.py`

**Layer:** Application — Service

**Module purpose:** Application facade — the only door Presentation may call.

#### Module-level functions *(no class)*

##### `_mark_catalog_busy(host: Any)` · line 23

**Does:** Internal helper.

**Needs:**
- Parameters: `host: Any`

**Calls:**
- `host.db.set_service_state`
- `getattr`
- `callable`
- `sync_fn`

**Returns:** None

#### Class `ApplicationFacade` · line 33

**Inherits:** `—`

**Purpose:** Named use cases from HIMA-Prooftest-Layer-Functions.md.

##### `__init__(self, host: Any)` · line 36

**Does:** Internal helper.

**Needs:**
- Parameters: `host: Any`
- Uses instance: `self._host`, `self.alarm_port`, `self.archive_port`, `self.catalog`, `self.engine`, `self.live`, `self.opc_port`, `self.query`, `self.report_port`, `self.silworx_conn`, `self.silworx_port`, `self.store_port`

**Calls:**
- `AlarmManagerAdapter`
- `OpcManagerAdapter`
- `getattr`
- `float`
- `int`
- `DatabaseStoreAdapter`
- `AnnexReportAdapter`
- `AnnexListArchiveAdapter`
- `Case1SyncSilworxAdapter`
- `set`
- `(getattr(host, 'structures', {}) or {}).keys`
- `CatalogService`
- `LiveTestService`
- `QueryService`
- `SilworxConnectionService`
- `host.refresh`
- `_mark_catalog_busy`
- `Engine`
- `host.health`
- `host.start`
- `host.request_stop_flags`

**Returns:** None

##### `start_engine(self)` · line 105

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `self._host.start`

**Returns:** None

##### `stop_engine(self, reason: str = 'ui_stop')` · line 108

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `reason: str = 'ui_stop'`
- Uses instance: `self._host`

**Calls:**
- `self._host.stop`

**Returns:** None

##### `request_stop_flags(self, reason: str)` · line 111

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `reason: str`
- Uses instance: `self._host`

**Calls:**
- `self._host.request_stop_flags`

**Returns:** None

##### `request_shutdown(self, reason: str, exit_process = True)` · line 114

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `reason: str, exit_process = True`
- Uses instance: `self._host`

**Calls:**
- `self._host.request_shutdown`

**Returns:** None

##### `get_engine_status(self)` · line 117

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `self._host.health`

**Returns:** dict

##### `refresh_catalog(self)` · line 120

**Does:** RefreshCatalog — Application owns the use case; WorkerHost is the data plane.

**Needs:**
- Uses instance: `self._host`, `self.catalog`

**Calls:**
- `self.catalog.run_station_refresh`

**Returns:** dict

##### `close_silworx_connection(self)` · line 126

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`, `self.silworx_conn`

**Calls:**
- `self.silworx_conn.close_silworx_connection`
- `self._host.db.set_service_state`
- `bool`

**Returns:** dict

##### `resume_silworx_connection(self)` · line 146

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`, `self.silworx_conn`

**Calls:**
- `getattr`
- `bool`
- `self.silworx_conn.resume_silworx_connection`

**Returns:** dict

##### `release_silworx_for_uninstall(self)` · line 158

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `self._host.release_silworx_for_uninstall`

**Returns:** dict

##### `reintegrate_silworx(self)` · line 161

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `self._host.reintegrate_silworx`

**Returns:** dict

##### `list_devices(self, view: str = 'all')` · line 166

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `view: str = 'all'`
- Uses instance: `self._host`, `self.query`

**Calls:**
- `self.query.list_devices`

**Returns:** list

##### `list_reports(self, device: str, results_type: Optional[str] = None, project: Optional[str] = None, device_id: Optional[str] = None)` · line 171

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: str, results_type: Optional[str] = None, project: Optional[str] = None, device_id: Optional[str] = None`
- Uses instance: `self.query`

**Calls:**
- `self.query.list_reports`

**Returns:** list

##### `open_report(self, path: str)` · line 182

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: str`
- Uses instance: `self._host`, `self.query`

**Calls:**
- `Path`
- `self.query.open_report`

**Returns:** tuple[int, Optional[str]]

##### `list_alarms(self)` · line 189

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.query`

**Calls:**
- `self.query.list_alarms_payload`

**Returns:** dict

##### `acknowledge_alarm(self, alarm_id: int)` · line 192

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `alarm_id: int`
- Uses instance: `self.query`

**Calls:**
- `self.query.acknowledge_alarm`

**Returns:** Optional[dict]

##### `reset_alarms(self)` · line 195

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.query`

**Calls:**
- `self.query.reset_alarms`

**Returns:** None

##### `list_running_tests(self)` · line 198

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.query`

**Calls:**
- `self.query.list_running_tests`

**Returns:** list

##### `list_test_history(self)` · line 201

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.query`

**Calls:**
- `self.query.list_test_history`

**Returns:** list

##### `list_archives(self)` · line 206

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.query`

**Calls:**
- `self.query.list_archives`

**Returns:** list

##### `create_archive(self)` · line 209

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.query`

**Calls:**
- `self.query.create_archive`

**Returns:** dict

##### `export_archive(self)` · line 212

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.query`

**Calls:**
- `self.query.export_archive`

**Returns:** tuple[dict, bytes]

##### `restore_archive(self, archive_id: str)` · line 215

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_id: str`
- Uses instance: `self.query`

**Calls:**
- `self.query.restore_archive`

**Returns:** dict

##### `restore_archive_upload(self, path: Path, filename: str)` · line 218

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: Path, filename: str`
- Uses instance: `self.query`

**Calls:**
- `self.query.restore_archive_upload`

**Returns:** dict

##### `clear_keep_opc_only(self, archive_first = True)` · line 221

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_first = True`
- Uses instance: `self.query`

**Calls:**
- `self.query.clear_keep_opc_only`

**Returns:** dict

##### `config(self)` · line 225

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Any

##### `alarms(self)` · line 229

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Any

##### `engine_running(self)` · line 233

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `bool`

**Returns:** bool

##### `_stopped(self)` · line 237

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `bool`

**Returns:** bool

##### `_starting(self)` · line 241

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `bool`

**Returns:** bool

### File `Annex codes/layers/application/live_test.py`

**Layer:** Application — Service

**Module purpose:** LiveTestService: PollOnce, start/end/interrupt, CompleteTest off the poll thread contract.

#### Class `LiveTestService` · line 21

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, opc: OpcPort, store: StorePort, reports: ReportPort, alarms: AlarmPort, detector = None, snapshot_fn = None, defer_complete = False, live_recheck_sec = LIVE_RECHECK_SEC)` · line 22

**Does:** Internal helper.

**Needs:**
- Parameters: `opc: OpcPort, store: StorePort, reports: ReportPort, alarms: AlarmPort, detector = None, snapshot_fn = None, defer_complete = False, live_recheck_sec = LIVE_RECHECK_SEC`
- Uses instance: `self._item_live_ok`, `self._item_recheck_at`, `self._sequence`, `self._skip_logged`, `self.alarms`, `self.completed`, `self.defer_complete`, `self.detector`, `self.interrupted`, `self.live_recheck_sec`, `self.opc`, `self.queue`, `self.reports`, `self.snapshot_fn`, `self.store`

**Calls:**
- `RunningEdgeDetector`
- `max`
- `float`
- `set`

**Returns:** None

##### `queue_depth(self)` · line 52

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.queue`

**Calls:**
- `len`

**Returns:** int

##### `seed_device(self, device: Device)` · line 55

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: Device`
- Uses instance: `self.detector`

**Calls:**
- `self.detector.prime`
- `device.device_id.key`

**Returns:** None

##### `poll_once(self, devices: list[Device])` · line 62

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `devices: list[Device]`
- Uses instance: `self._poll_one`, `self.alarms`, `self.seed_device`

**Calls:**
- `self.seed_device`
- `self._poll_one`
- `self.alarms.raise_alarm`
- `str`

**Returns:** None

##### `_server_live_ok(self, server: str)` · line 75

**Does:** Internal helper.

**Needs:**
- Parameters: `server: str`
- Uses instance: `self.opc`

**Calls:**
- `getattr`
- `callable`
- `fn`

**Returns:** Optional[bool]

##### `_mark_item_live(self, running_id: str, ok: bool, quality: str = '')` · line 84

**Does:** Internal helper.

**Needs:**
- Parameters: `running_id: str, ok: bool, quality: str = ''`
- Uses instance: `self._item_live_ok`, `self._skip_logged`

**Calls:**
- `bool`
- `self._skip_logged.discard`

**Returns:** None

##### `_maybe_recheck_item(self, server: str, running_id: str)` · line 89

**Does:** Return True when this item is Good again; False still Bad; None if wait window.

**Needs:**
- Parameters: `server: str, running_id: str`
- Uses instance: `self._item_recheck_at`, `self._mark_item_live`, `self.live_recheck_sec`, `self.opc`

**Calls:**
- `time.monotonic`
- `getattr`
- `callable`
- `fn`
- `self.opc.read_running`
- `str(quality).lower`
- `str`
- `self._mark_item_live`
- `bool`
- `log.info`
- `log.debug`

**Returns:** Optional[bool]

##### `_should_skip_live_poll(self, server: str, running_id: str)` · line 117

**Does:** Skip only when this item (or, if unknown, the server sample) is known Bad.

**Needs:**
- Parameters: `server: str, running_id: str`
- Uses instance: `self._item_live_ok`, `self._server_live_ok`

**Calls:**
- `self._item_live_ok.get`
- `self._server_live_ok`

**Returns:** bool

##### `_poll_one(self, device: Device)` · line 127

**Does:** Internal helper.

**Needs:**
- Parameters: `device: Device`
- Uses instance: `self._mark_item_live`, `self._maybe_recheck_item`, `self._should_skip_live_poll`, `self._skip_logged`, `self.alarms`, `self.detector`, `self.live_recheck_sec`, `self.on_test_ended`, `self.on_test_interrupted`, `self.on_test_started`, `self.opc`

**Calls:**
- `device.device_id.key`
- `self.detector.is_in_progress`
- `self.on_test_interrupted`
- `device.opc_item_prefix.endswith`
- `str`
- `self._should_skip_live_poll`
- `self._skip_logged.add`
- `log.info`
- `self._maybe_recheck_item`
- `self.opc.read_running`
- `self.alarms.raise_alarm`
- `str(quality).lower`
- `self._mark_item_live`
- `getattr`
- `callable`
- `mark`
- `self.detector.observe`
- `self.on_test_started`
- `self.on_test_ended`

**Returns:** None

##### `on_test_started(self, device: Device)` · line 190

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: Device`
- Uses instance: `self.alarms`, `self.store`

**Calls:**
- `self.store.upsert_device`
- `self.alarms.raise_alarm`
- `str`
- `self.store.start_test`

**Returns:** None

##### `on_test_ended(self, device: Device, running_id: str)` · line 206

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: Device, running_id: str`
- Uses instance: `self._next_sequence`, `self._persist_snapshot`, `self.alarms`, `self.defer_complete`, `self.detector`, `self.on_test_interrupted`, `self.opc`, `self.queue`, `self.run_complete`, `self.snapshot_fn`, `self.store`

**Calls:**
- `(device.results_type or '').strip`
- `self.store.upsert_device`
- `self.store.finish_test`
- `self.alarms.raise_alarm`
- `self.detector.confirm_ended`
- `device.device_id.key`
- `self.snapshot_fn`
- `snapshot.get`
- `self.opc.read_running`
- `self.on_test_interrupted`
- `str`
- `bool`
- `str(quality).lower`
- `self._next_sequence`
- `self._persist_snapshot`
- `self.queue.append`
- `self.run_complete`

**Returns:** None

##### `on_test_interrupted(self, device: Device, reason: str)` · line 277

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: Device, reason: str`
- Uses instance: `self.alarms`, `self.interrupted`, `self.store`

**Calls:**
- `self.interrupted.append`
- `self.store.upsert_device`
- `self.store.finish_test`
- `self.alarms.raise_alarm`

**Returns:** None

##### `_next_sequence(self, device_id: str)` · line 297

**Does:** Internal helper.

**Needs:**
- Parameters: `device_id: str`
- Uses instance: `self._sequence`

**Calls:**
- `self._sequence.get`

**Returns:** int

##### `_snapshot_table_name(self, results_type: str)` · line 301

**Does:** Internal helper.

**Needs:**
- Parameters: `results_type: str`
- Uses instance: `self.store`

**Calls:**
- `getattr`
- `callable`
- `str`
- `fn`

**Returns:** str

##### `_persist_snapshot(self, device: Device, snapshot: dict, sequence = None)` · line 310

**Does:** INSERT the frozen OPC copy into ProofTest_* immediately (read-only OPC).

**Needs:**
- Parameters: `device: Device, snapshot: dict, sequence = None`
- Uses instance: `self._snapshot_table_name`, `self.alarms`, `self.store`

**Calls:**
- `device.device_id.key`
- `self._snapshot_table_name`
- `self.store.insert_snapshot`
- `self.alarms.raise_alarm`
- `str`
- `getattr`

**Returns:** tuple[Optional[int], str]

##### `run_complete(self, job: dict)` · line 379

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `job: dict`
- Uses instance: `self.complete_test`

**Calls:**
- `job.get`
- `list`
- `self.complete_test`

**Returns:** None

##### `complete_test(self, device: Device, snapshot: dict, quality_notes: list[str], report_raises = None, sequence = None, record_id = None, snapshot_table = '')` · line 392

**Does:** Write report from the frozen snapshot. SQL insert already done on test end when possible.

**Needs:**
- Parameters: `device: Device, snapshot: dict, quality_notes: list[str], report_raises = None, sequence = None, record_id = None, snapshot_table = ''`
- Uses instance: `self._persist_snapshot`, `self._snapshot_table_name`, `self.alarms`, `self.completed`, `self.reports`, `self.store`

**Calls:**
- `self._snapshot_table_name`
- `self._persist_snapshot`
- `self.alarms.raise_alarm`
- `'; '.join`
- `report_raises`
- `self.reports.write`
- `getattr`
- `callable`
- `updater`
- `int`
- `self.completed.append`
- `self.store.finish_test`

**Returns:** None

### File `Annex codes/layers/application/query.py`

**Layer:** Application — Service

**Module purpose:** QueryService — Presentation calls this, never OPC/SILworX/annex adapters.

#### Class `QueryService` · line 13

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, store: StorePort, reports: ReportPort, alarms: AlarmPort, host = None, archives = None)` · line 14

**Does:** Internal helper.

**Needs:**
- Parameters: `store: StorePort, reports: ReportPort, alarms: AlarmPort, host = None, archives = None`
- Uses instance: `self._host`, `self.alarms`, `self.archives`, `self.reports`, `self.store`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `list_devices(self, view: str = 'all')` · line 29

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `view: str = 'all'`
- Uses instance: `self.alarms`, `self.store`

**Calls:**
- `self.store.list_devices`
- `self.alarms.raise_alarm`
- `str`
- `row.setdefault`
- `row.get`
- `bool`
- `str(row.get('results_type') or '').strip`
- `sort_device_dicts`

**Returns:** list[dict]

##### `list_reports(self, device_tag: str, results_type: Optional[str] = None, project = None, device_id = None)` · line 48

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: Optional[str] = None, project = None, device_id = None`
- Uses instance: `self.reports`

**Calls:**
- `self.reports.list_for_device`

**Returns:** list[dict]

##### `list_alarms(self)` · line 63

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.alarms`

**Calls:**
- `getattr`
- `isinstance`
- `list`

**Returns:** list[dict]

##### `list_alarms_payload(self)` · line 67

**Does:** GUI alarm list + popup queue.

**Needs:**
- Uses instance: `self._host`, `self.store`

**Calls:**
- `set`
- `host.alarms.active_error_keys`
- `isinstance`
- `getattr`
- `host.alarms.recent_alarms`
- `dict`
- `item.get`
- `str`
- `bool`
- `enriched.append`
- `host.alarms.pop_pending_popups`

**Returns:** dict

##### `acknowledge_alarm(self, alarm_id: int)` · line 104

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `alarm_id: int`
- Uses instance: `self._host`, `self.store`

**Calls:**
- `getattr`
- `callable`
- `fn`
- `self._host.alarms.acknowledge_error_key`
- `row.get`

**Returns:** Optional[dict]

##### `reset_alarms(self)` · line 114

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`, `self.store`

**Calls:**
- `getattr`
- `callable`
- `fn`
- `self._host.alarms.reset_all`

**Returns:** None

##### `list_running_tests(self)` · line 124

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.store`

**Calls:**
- `getattr`
- `callable`
- `list`
- `fn`

**Returns:** list[dict]

##### `list_test_history(self)` · line 131

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.store`

**Calls:**
- `getattr`
- `callable`
- `list`
- `fn`

**Returns:** list[dict]

##### `open_report(self, path: str, allowed_roots: list[Path])` · line 138

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: str, allowed_roots: list[Path]`
- Uses instance: `self.alarms`

**Calls:**
- `Path(path).resolve`
- `Path`
- `any`
- `str(file_path).startswith`
- `str`
- `root.resolve`
- `self.alarms.raise_alarm`
- `file_path.exists`

**Returns:** tuple[int, Optional[str]]

##### `list_archives(self)` · line 149

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.archives`

**Calls:**
- `list`
- `self.archives.list_archives`

**Returns:** list

##### `create_archive(self)` · line 157

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.archives`

**Calls:**
- `RuntimeError`
- `self.archives.create_archive`

**Returns:** dict

##### `export_archive(self)` · line 162

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.archives`

**Calls:**
- `RuntimeError`
- `self.archives.export_archive`

**Returns:** tuple[dict, bytes]

##### `restore_archive(self, archive_id: str)` · line 167

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_id: str`
- Uses instance: `self.archives`

**Calls:**
- `RuntimeError`
- `self.archives.restore_archive`

**Returns:** dict

##### `restore_archive_upload(self, path: Path, filename: str)` · line 172

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: Path, filename: str`
- Uses instance: `self.archives`

**Calls:**
- `RuntimeError`
- `self.archives.restore_archive_upload`

**Returns:** dict

##### `clear_keep_opc_only(self, archive_first = True)` · line 177

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_first = True`
- Uses instance: `self.archives`

**Calls:**
- `RuntimeError`
- `self.archives.clear_keep_opc_only`

**Returns:** dict

### File `Annex codes/layers/application/silworx_connection.py`

**Layer:** Application — Service

**Module purpose:** SilworxConnectionService — this tool's API/plugin session only. Never quit SILworX.

#### Class `SilworxConnectionService` · line 16

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, silworx: SilworxPort, catalog: CatalogService, alarms: AlarmPort, refresh_fn = None, mark_refresh_busy = None)` · line 17

**Does:** Internal helper.

**Needs:**
- Parameters: `silworx: SilworxPort, catalog: CatalogService, alarms: AlarmPort, refresh_fn = None, mark_refresh_busy = None`
- Uses instance: `self._mark_refresh_busy`, `self._refresh`, `self.alarms`, `self.catalog`, `self.silworx`

**Calls:**
- `self.catalog.refresh_catalog`

**Returns:** None

##### `close_silworx_connection(self)` · line 32

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._start_refresh_async`, `self.alarms`, `self.silworx`

**Calls:**
- `self.silworx.is_attached`
- `self.silworx.detach`
- `self.alarms.raise_alarm`
- `str`
- `self._start_refresh_async`

**Returns:** dict

##### `resume_silworx_connection(self)` · line 46

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._start_refresh_async`, `self.alarms`, `self.silworx`

**Calls:**
- `self.silworx.attach`
- `self.alarms.raise_alarm`
- `str`
- `self.silworx.has_open_project`
- `self._start_refresh_async`
- `self.silworx.is_attached`

**Returns:** dict

##### `_start_refresh_async(self, action: str)` · line 76

**Does:** Internal helper. Triggers or participates in catalog refresh.

**Needs:**
- Parameters: `action: str`
- Uses instance: `self._mark_refresh_busy`

**Calls:**
- `self._mark_refresh_busy`
- `threading.Thread(target=_run, daemon=True, name=f'silworx-{action.lower()}-refresh').start`
- `threading.Thread`
- `action.lower`

**Returns:** None

---

## Domain — Model logic

### File `Annex codes/layers/domain/__init__.py`

**Layer:** Domain — Model logic

**Module purpose:** *(no module docstring)*

*(empty module)*

### File `Annex codes/layers/domain/device.py`

**Layer:** Domain — Model logic

**Module purpose:** Catalog identity: DeviceId is Project + Configuration + Resource + Device_TAG.

#### Module-level functions *(no class)*

##### `device_from_row(row: dict)` · line 73

**Does:** Build a Device from a Device Prooftest Result List row (SQL or API).

**Needs:**
- Parameters: `row: dict`

**Calls:**
- `str`
- `row.get`
- `DeviceId.from_key`
- `DeviceId`
- `bool`
- `str(row.get('opc_server') or '').strip`
- `str(row.get('opc_item_prefix') or '').strip`
- `Device`

**Returns:** Device

##### `sort_devices(devices: list[Device])` · line 107

**Does:** Device_TAG, then Project, then OPC server.

**Needs:**
- Parameters: `devices: list[Device]`

**Calls:**
- `sorted`
- `d.device_tag.lower`
- `d.project.lower`
- `(d.opc_server or '').lower`

**Returns:** list[Device]

##### `sort_device_dicts(rows: list[dict], tag_key = 'device_tag')` · line 119

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `rows: list[dict], tag_key = 'device_tag'`

**Calls:**
- `sorted`
- `str(r.get(tag_key) or '').lower`
- `str`
- `r.get`
- `str(r.get('project') or r.get('silworx_project') or '').lower`
- `str(r.get('opc_server') or '').lower`

**Returns:** list[dict]

#### Class `DeviceId` · line 12

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__post_init__(self)` · line 18

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.configuration`, `self.device_tag`, `self.project`, `self.resource`

**Calls:**
- `object.__setattr__`
- `(self.project or '').strip`
- `(self.configuration or '').strip`
- `(self.resource or '').strip`
- `(self.device_tag or '').strip`

**Returns:** None

##### `key(self)` · line 24

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.configuration`, `self.device_tag`, `self.project`, `self.resource`

**Calls:**
- `_SEP.join`

**Returns:** str

##### `from_key(cls, key: str)` · line 30

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `key: str`

**Calls:**
- `(key or '').split`
- `len`
- `parts.append`
- `cls`

**Returns:** 'DeviceId'

#### Class `Device` · line 38

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `device_tag(self)` · line 50

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.device_id`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `project(self)` · line 54

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.device_id`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `configuration(self)` · line 58

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.device_id`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `resource(self)` · line 62

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.device_id`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `source_label(self)` · line 65

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.opc_server`, `self.present_on_opc`, `self.project`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

### File `Annex codes/layers/domain/merger.py`

**Layer:** Domain — Model logic

**Module purpose:** Merge SILworX identities with OPC observations. Device_TAG is not globally unique.

#### Class `SilworxIdentity` · line 12

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `OpcObservation` · line 21

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `MergeCollision` · line 30

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `MergeResult` · line 37

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `CatalogMerger` · line 43

**Inherits:** `—`

**Purpose:** Build catalog rows from SILworX + OPC. Never invent type by CSV score when SILworX typed the DeviceId.

##### `_tag_lookup_keys(tag: str)` · line 47

**Does:** SILworX TAG may use '/'; HIMA X-OPC often publishes the same leaf with '_'.

**Needs:**
- Parameters: `tag: str`

**Calls:**
- `str`
- `text.replace`
- `keys.append`

**Returns:** list[str]

##### `_tags_equivalent(a: str, b: str)` · line 57

**Does:** Internal helper.

**Needs:**
- Parameters: `a: str, b: str`

**Calls:**
- `str`
- `left.replace`
- `right.replace`

**Returns:** bool

##### `_opc_matches_for_tag(self, tag: str, opc_by_tag: dict[str, list[OpcObservation]])` · line 61

**Does:** Internal helper.

**Needs:**
- Parameters: `tag: str, opc_by_tag: dict[str, list[OpcObservation]]`
- Uses instance: `self._tag_lookup_keys`

**Calls:**
- `set`
- `self._tag_lookup_keys`
- `opc_by_tag.get`
- `id`
- `seen.add`
- `matches.append`

**Returns:** list[OpcObservation]

##### `merge(self, silworx: list[SilworxIdentity], opc: list[OpcObservation], existing = None)` · line 75

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `silworx: list[SilworxIdentity], opc: list[OpcObservation], existing = None`
- Uses instance: `self._choose_opc_for_device`, `self._opc_matches_for_tag`, `self._tags_equivalent`

**Calls:**
- `set`
- `DeviceId`
- `did.key`
- `skipped.append`
- `seen_silworx.add`
- `Device`
- `opc_by_tag.setdefault(obs.device_tag, []).append`
- `opc_by_tag.setdefault`
- `list`
- `devices.items`
- `self._opc_matches_for_tag`
- `self._choose_opc_for_device`
- `bound_obs.add`
- `id`
- `path_owners.setdefault((chosen.opc_server, chosen.opc_item_prefix), []).append`
- `path_owners.setdefault`
- `path_owners.items`
- `len`
- `collisions.append`
- `MergeCollision`
- `any`
- `self._tags_equivalent`
- `devices.values`
- `existing.get`
- `existing.items`
- `… +6 more`

**Returns:** MergeResult

##### `_choose_opc_for_device(device: Device, matches: list[OpcObservation])` · line 235

**Does:** Internal helper.

**Needs:**
- Parameters: `device: Device, matches: list[OpcObservation]`

**Calls:**
- `len`
- `CatalogMerger._tag_lookup_keys`
- `obs.opc_item_prefix.endswith`

**Returns:** Optional[OpcObservation]

### File `Annex codes/layers/domain/opc_discover.py`

**Layer:** Domain — Model logic

**Module purpose:** Shaped OPC-only discovery — CSV as FILTER / clear-type only, never invent-as-identity.

Rules (unified mode):
- OPC parent folder names are **user-defined** SILworX resource names (not a HIMA
  standard). Discover by ``…{TAG}.Running`` anywhere in the tree.
- Candidate = ``…{TAG}.Running`` or ``…Global Vars.{TAG}.Running`` (TAG has no ``.``)
- Shape gate (per Results type): shared members ≥ max(FLOOR, ceil(RATIO × |type|))
- Type: last known SQL type if set; else unique clear best; else unknown ("")

#### Module-level functions *(no class)*

##### `normalize_member(name: str)` · line 28

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `name: str`

**Calls:**
- `str(name or '').replace(' ', '').lower().split`
- `str(name or '').replace(' ', '').lower`
- `str(name or '').replace`
- `str`

**Returns:** str

##### `member_short_set(members: Iterable[str])` · line 32

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `members: Iterable[str]`

**Calls:**
- `normalize_member`

**Returns:** Set[str]

##### `shape_gate_threshold(type_members: Iterable[str], ratio = SHAPE_GATE_RATIO, floor = SHAPE_GATE_FLOOR)` · line 36

**Does:** Minimum intersection size required for one Results type.

**Needs:**
- Parameters: `type_members: Iterable[str], ratio = SHAPE_GATE_RATIO, floor = SHAPE_GATE_FLOOR`

**Calls:**
- `member_short_set`
- `members.discard`
- `len`
- `int`
- `math.ceil`
- `max`
- `float`

**Returns:** int

##### `score_structure_match(member_names: Set[str], type_members: Set[str])` · line 52

**Does:** Intersection size; require Running in the type definition.

**Needs:**
- Parameters: `member_names: Set[str], type_members: Set[str]`

**Calls:**
- `member_short_set`
- `required.discard`
- `len`
- `required.intersection`

**Returns:** int

##### `parse_shaped_running_item(item: str)` · line 62

**Does:** Accept ``{any.user.parent}.{TAG}.Running`` or ``…Global Vars.{TAG}.Running``.

**Needs:**
- Parameters: `item: str`

**Calls:**
- `str(item or '').strip`
- `str`
- `text.endswith`
- `len`
- `prefix.split`
- `parts[-1].strip`
- `'.'.join(parts[:-1]).strip`
- `'.'.join`

**Returns:** Optional[Tuple[str, str, str]]

##### `members_under_prefix(tags: Sequence[str], prefix: str)` · line 85

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `tags: Sequence[str], prefix: str`

**Calls:**
- `set`
- `tag.startswith`
- `tag[len(prefix_dot):].split`
- `len`
- `members.add`

**Returns:** Set[str]

##### `_gates_for_types(type_sets: Mapping[str, Set[str]], ratio, floor)` · line 96

**Does:** Internal helper.

**Needs:**
- Parameters: `type_sets: Mapping[str, Set[str]], ratio, floor`

**Calls:**
- `shape_gate_threshold`
- `type_sets.items`

**Returns:** Dict[str, int]

##### `resolve_opc_only_type(scores: Mapping[str, int], last_type = '', type_gates = None, gate_n = SHAPE_GATE_FLOOR, clear_margin = CLEAR_MARGIN)` · line 108

**Does:** Prefer last SQL type when present.
Else unique clear winner: best passes its per-type gate and
(best − second) ≥ clear_margin. Else unknown ("").

**Needs:**
- Parameters: `scores: Mapping[str, int], last_type = '', type_gates = None, gate_n = SHAPE_GATE_FLOOR, clear_margin = CLEAR_MARGIN`

**Calls:**
- `(last_type or '').strip`
- `dict`
- `sorted`
- `scores.items`
- `int`
- `gates.get`
- `len`

**Returns:** str

##### `passes_shape_gate(scores: Mapping[str, int], type_gates = None, gate_n = SHAPE_GATE_FLOOR)` · line 142

**Does:** True when at least one Results type reaches its half/floor threshold.

**Needs:**
- Parameters: `scores: Mapping[str, int], type_gates = None, gate_n = SHAPE_GATE_FLOOR`

**Calls:**
- `dict`
- `any`
- `int`
- `gates.get`
- `scores.items`

**Returns:** bool

##### `discover_shaped_from_tag_lists(tags_by_server: Mapping[str, Sequence[str]], type_members: Mapping[str, Iterable[str]], last_types_by_tag = None, gate_n = SHAPE_GATE_FLOOR, gate_ratio = SHAPE_GATE_RATIO, clear_margin = CLEAR_MARGIN)` · line 159

**Does:** Pure shaped discover from browsed OPC tag lists (no invent scorer).

**Needs:**
- Parameters: `tags_by_server: Mapping[str, Sequence[str]], type_members: Mapping[str, Iterable[str]], last_types_by_tag = None, gate_n = SHAPE_GATE_FLOOR, gate_ratio = SHAPE_GATE_RATIO, clear_margin = CLEAR_MARGIN`

**Calls:**
- `dict`
- `member_short_set`
- `type_members.items`
- `_gates_for_types`
- `tags_by_server.items`
- `list`
- `sorted`
- `str(t).endswith`
- `str`
- `parse_shaped_running_item`
- `rejected.append`
- `members_under_prefix`
- `score_structure_match`
- `type_sets.items`
- `passes_shape_gate`
- `resolve_opc_only_type`
- `last_types_by_tag.get`
- `max`
- `scores.values`
- `OpcObservation`
- `best.get`
- `len`
- `best.keys`
- `ShapedDiscoverResult`

**Returns:** ShapedDiscoverResult

##### `type_members_from_structures(structures: Mapping[str, object])` · line 224

**Does:** Build type→member set from ResultsStructure-like objects or ResultType.

**Needs:**
- Parameters: `structures: Mapping[str, object]`

**Calls:**
- `(structures or {}).items`
- `hasattr`
- `list`
- `structure.member_short_names`
- `isinstance`
- `members.append`
- `getattr`
- `str`
- `member_short_set`

**Returns:** Dict[str, Set[str]]

#### Class `ShapedDiscoverResult` · line 154

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

### File `Annex codes/layers/domain/result_types.py`

**Layer:** Domain — Model logic

**Module purpose:** Results Structure type catalogue. Loading types does not create devices.

#### Class `ResultType` · line 11

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `ResultTypeCatalog` · line 18

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `names(self)` · line 22

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.types`

**Calls:**
- `set`
- `self.types.keys`

**Returns:** set[str]

##### `get(self, name: str)` · line 25

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `name: str`
- Uses instance: `self.types`

**Calls:**
- `self.types.get`

**Returns:** Optional[ResultType]

##### `matches_global(self, data_type: str)` · line 28

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `data_type: str`
- Uses instance: `self.types`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `from_csv_folder(cls, folder: Path)` · line 32

**Does:** Minimal CSV loader for unit tests (name from stem; first column = member).

**Needs:**
- Parameters: `folder: Path`

**Calls:**
- `cls`
- `folder.is_dir`
- `sorted`
- `folder.glob`
- `path.read_text`
- `catalog.skipped_files.append`
- `str`
- `ln.strip`
- `text.splitlines`
- `line.split(',')[0].strip`
- `line.split`
- `members.append`
- `stem.replace`
- `ResultType`
- `tuple`

**Returns:** 'ResultTypeCatalog'

### File `Annex codes/layers/domain/running.py`

**Layer:** Domain — Model logic

**Module purpose:** In-memory .Running edge detection. SQL is not updated every poll cycle.

#### Class `EdgeEvent` · line 10

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `RunningEdgeDetector` · line 16

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self)` · line 17

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._in_progress`, `self._last`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `observe(self, device_id: str, running: Optional[bool], quality_good = True, present_on_opc = True)` · line 21

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_id: str, running: Optional[bool], quality_good = True, present_on_opc = True`
- Uses instance: `self._in_progress`, `self._last`

**Calls:**
- `self._in_progress.get`
- `EdgeEvent`
- `self._last.get`
- `bool`

**Returns:** EdgeEvent

##### `confirm_ended(self, device_id: str, still_running: bool)` · line 48

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_id: str, still_running: bool`
- Uses instance: `self._in_progress`, `self._last`

**Calls:**
- `EdgeEvent`

**Returns:** EdgeEvent

##### `is_in_progress(self, device_id: str)` · line 57

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_id: str`
- Uses instance: `self._in_progress`

**Calls:**
- `bool`
- `self._in_progress.get`

**Returns:** bool

##### `prime(self, device_id: str, last_running: Optional[bool], in_progress: bool = False)` · line 60

**Does:** Seed from SQL on restart. Does not overwrite an already-observed DeviceId.

**Needs:**
- Parameters: `device_id: str, last_running: Optional[bool], in_progress: bool = False`
- Uses instance: `self._in_progress`, `self._last`

**Calls:**
- `bool`

**Returns:** None

---

## Ports (interfaces)

### File `Annex codes/layers/ports.py`

**Layer:** Ports (interfaces)

**Module purpose:** Application ports. Adapters live outside Domain.

#### Class `AlarmPort` · line 12

**Inherits:** `Protocol`

**Purpose:** *(no class docstring)*

##### `raise_alarm(self, step: str, action: str, message: str, device_tag = None, severity = 'Error')` · line 13

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `step: str, action: str, message: str, device_tag = None, severity = 'Error'`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `last_error(self)` · line 23

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Optional[dict]

#### Class `SilworxPort` · line 27

**Inherits:** `Protocol`

**Purpose:** *(no class docstring)*

##### `is_attached(self)` · line 28

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `attach(self)` · line 30

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `detach(self)` · line 32

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `list_identities(self, known_types: set[str])` · line 34

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `known_types: set[str]`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[SilworxIdentity]

##### `has_open_project(self)` · line 36

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

#### Class `OpcPort` · line 40

**Inherits:** `Protocol`

**Purpose:** *(no class docstring)*

##### `discover_servers(self)` · line 41

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[str]

##### `list_tags(self, server: str)` · line 43

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[str]

##### `find_running_path(self, server: str, device_tag: str)` · line 45

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str, device_tag: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Optional[str]

##### `read_running(self, server: str, item_id: str)` · line 47

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str, item_id: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** tuple[Optional[bool], str]

##### `server_live_ok(self, server: str)` · line 51

**Does:** True/False when known; None = not sampled yet (poll normally).

**Needs:**
- Parameters: `server: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Optional[bool]

##### `recheck_server_live(self, server: str, running_item: Optional[str] = None)` · line 55

**Does:** Optional: refresh live quality for a ProgID (resume monitoring after Bad).

**Needs:**
- Parameters: `server: str, running_item: Optional[str] = None`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Optional[bool]

##### `mark_live_quality(self, server: str, ok: bool, quality: str = '')` · line 61

**Does:** Optional: record last live quality sample for a ProgID.

**Needs:**
- Parameters: `server: str, ok: bool, quality: str = ''`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `discover_opc_only(self, known_types: set[str], last_types_by_tag = None)` · line 67

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `known_types: set[str], last_types_by_tag = None`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[OpcObservation]

#### Class `StorePort` · line 76

**Inherits:** `Protocol`

**Purpose:** *(no class docstring)*

##### `ensure_folders(self)` · line 77

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `connect(self)` · line 79

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `upsert_device(self, device: Device)` · line 81

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: Device`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `list_devices(self, view: str = 'all')` · line 83

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `view: str = 'all'`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[dict]

##### `reconcile(self, active_ids: list[str])` · line 85

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `active_ids: list[str]`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `mark_inactive(self, device_id: str)` · line 87

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_id: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `insert_snapshot(self, device_tag: str, results_type: str, snapshot: dict, **kwargs)` · line 89

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str, snapshot: dict, **kwargs`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** int

##### `snapshot_table_for(self, results_type: str)` · line 91

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `results_type: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `update_report_path(self, table: str, record_id: int, report_path: str)` · line 93

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `table: str, record_id: int, report_path: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `snapshots_for(self, device_tag: str)` · line 95

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[dict]

##### `start_test(self, device_tag: str, results_type: str)` · line 97

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `finish_test(self, device_tag: str, outcome: str)` · line 99

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, outcome: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `ReportPort` · line 103

**Inherits:** `Protocol`

**Purpose:** *(no class docstring)*

##### `write(self, device_tag: str, results_type: str, snapshot: dict, quality_notes = None, project = '', snapshot_table = None, record_id = None)` · line 104

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str, snapshot: dict, quality_notes = None, project = '', snapshot_table = None, record_id = None`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Optional[str]

##### `list_for_device(self, device_tag: str, results_type: Optional[str] = None, project = None, device_id = None)` · line 116

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: Optional[str] = None, project = None, device_id = None`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[dict]

##### `resolve_open_path(self, path: str)` · line 125

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Optional[str]

#### Class `ArchivePort` · line 129

**Inherits:** `Protocol`

**Purpose:** List archive / keep-OPC use cases — Application must not import annex_list_archive.

##### `list_archives(self)` · line 132

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[dict]

##### `create_archive(self)` · line 134

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** dict

##### `export_archive(self)` · line 136

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** tuple[dict, bytes]

##### `restore_archive(self, archive_id: str)` · line 138

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_id: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** dict

##### `restore_archive_upload(self, path: object, filename: str)` · line 140

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: object, filename: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** dict

##### `clear_keep_opc_only(self, archive_first = True)` · line 142

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_first = True`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** dict

##### `keep_opc_only_enabled(self)` · line 144

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

---

## Adapters

### File `Annex codes/layers/adapters.py`

**Layer:** Adapters

**Module purpose:** Runtime adapters: OpcManager / Database / write_reports / AlarmManager / Case1 → ports.

#### Module-level functions *(no class)*

##### `_structure_to_sql_table(results_type: str)` · line 13

**Does:** Internal helper.

**Needs:**
- Parameters: `results_type: str`

**Calls:**
- `structure_to_sql_table`

**Returns:** str

#### Class `AlarmManagerAdapter` · line 19

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, alarms: Any)` · line 20

**Does:** Internal helper.

**Needs:**
- Parameters: `alarms: Any`
- Uses instance: `self._alarms`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `raise_alarm(self, step: str, action: str, message: str, device_tag = None, severity = 'Error')` · line 23

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `step: str, action: str, message: str, device_tag = None, severity = 'Error'`
- Uses instance: `self._alarms`

**Calls:**
- `self._alarms.raise_alarm`

**Returns:** None

##### `last_error(self)` · line 40

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._alarms`

**Calls:**
- `getattr`
- `callable`
- `fn`

**Returns:** Optional[dict]

#### Class `OpcManagerAdapter` · line 45

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, opc: Any, structures_fn = None, shape_gate_ratio = 0.5, shape_gate_floor = 3)` · line 46

**Does:** Internal helper.

**Needs:**
- Parameters: `opc: Any, structures_fn = None, shape_gate_ratio = 0.5, shape_gate_floor = 3`
- Uses instance: `self._opc`, `self._shape_gate_floor`, `self._shape_gate_ratio`, `self._structures_fn`

**Calls:**
- `float`
- `int`

**Returns:** None

##### `discover_servers(self)` · line 59

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._opc`

**Calls:**
- `hasattr`
- `list`
- `self._opc.discover_servers`

**Returns:** list[str]

##### `list_tags(self, server: str)` · line 62

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str`
- Uses instance: `self._opc`

**Calls:**
- `hasattr`
- `list`
- `self._opc.list_all_tags`

**Returns:** list[str]

##### `list_tags_all_servers(self, servers: Optional[list[str]] = None)` · line 67

**Does:** Browse ProofTest tags into cache for every server (used by bind_opc_paths).

**Needs:**
- Parameters: `servers: Optional[list[str]] = None`
- Uses instance: `self._opc`, `self.discover_servers`, `self.list_tags`

**Calls:**
- `hasattr`
- `self._opc.list_tags_all_servers`
- `str`
- `list`
- `(raw or {}).items`
- `self.discover_servers`
- `self.list_tags`

**Returns:** dict[str, list[str]]

##### `invalidate_tag_cache(self)` · line 77

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._opc`

**Calls:**
- `getattr`
- `callable`
- `inval`
- `hasattr`
- `self._opc.invalidate_cache`

**Returns:** None

##### `find_running_path(self, server: str, device_tag: str)` · line 85

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str, device_tag: str`
- Uses instance: `self._opc`

**Calls:**
- `hasattr`
- `self._opc.find_running_path`

**Returns:** Optional[str]

##### `read_running(self, server: str, item_id: str)` · line 90

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str, item_id: str`
- Uses instance: `self._opc`

**Calls:**
- `self._opc.read_values`
- `read_map.get`
- `str`
- `quality_text.lower`
- `getattr`
- `callable`
- `mark`
- `bool`

**Returns:** tuple[Optional[bool], str]

##### `server_live_ok(self, server: str)` · line 107

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str`
- Uses instance: `self._opc`

**Calls:**
- `getattr`
- `callable`
- `fn`

**Returns:** Optional[bool]

##### `recheck_server_live(self, server: str, running_item: Optional[str] = None)` · line 113

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str, running_item: Optional[str] = None`
- Uses instance: `self._opc`, `self.server_live_ok`

**Calls:**
- `getattr`
- `callable`
- `fn`
- `self.server_live_ok`

**Returns:** Optional[bool]

##### `mark_live_quality(self, server: str, ok: bool, quality: str = '')` · line 121

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server: str, ok: bool, quality: str = ''`
- Uses instance: `self._opc`

**Calls:**
- `getattr`
- `callable`
- `fn`

**Returns:** None

##### `discover_opc_only(self, known_types: set[str], last_types_by_tag = None)` · line 126

**Does:** Shaped OPC-only discover (CSV shape gate / clear type). Invent scorer is dead.

**Needs:**
- Parameters: `known_types: set[str], last_types_by_tag = None`
- Uses instance: `self._opc`, `self._shape_gate_floor`, `self._shape_gate_ratio`, `self._structures_fn`, `self.discover_servers`, `self.list_tags`

**Calls:**
- `self._structures_fn`
- `self.discover_servers`
- `hasattr`
- `str`
- `list`
- `(self._opc.list_tags_all_servers(servers) or {}).items`
- `self._opc.list_tags_all_servers`
- `self.list_tags`
- `discover_shaped_from_tag_lists`
- `type_members_from_structures`

**Returns:** list[OpcObservation]

#### Class `DatabaseStoreAdapter` · line 167

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, db: Any, structures: dict)` · line 168

**Does:** Internal helper.

**Needs:**
- Parameters: `db: Any, structures: dict`
- Uses instance: `self._db`, `self._structures`, `self.last_record_id`, `self.last_table`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `ensure_folders(self)` · line 174

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `connect(self)` · line 177

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._db`

**Calls:**
- `getattr`

**Returns:** str

##### `upsert_device(self, device: Device)` · line 180

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: Device`
- Uses instance: `self._db`

**Calls:**
- `self._db.upsert_device`
- `device.device_id.key`
- `getattr`
- `callable`
- `setter`
- `bool`

**Returns:** None

##### `list_devices(self, view: str = 'all')` · line 200

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `view: str = 'all'`
- Uses instance: `self._db`

**Calls:**
- `self._db.list_devices`

**Returns:** list[dict]

##### `list_inactive_devices(self)` · line 203

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._db`

**Calls:**
- `getattr`
- `callable`
- `list`
- `fn`

**Returns:** list[dict]

##### `reconcile(self, active_ids: list[str])` · line 207

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `active_ids: list[str]`
- Uses instance: `self._db`

**Calls:**
- `self._db.reconcile_device_list`

**Returns:** None

##### `mark_inactive(self, device_id: str)` · line 210

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_id: str`
- Uses instance: `self._db`

**Calls:**
- `self._db.reconcile_device_list`

**Returns:** None

##### `insert_snapshot(self, device_tag: str, results_type: str, snapshot: dict, **kwargs)` · line 213

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str, snapshot: dict, **kwargs`
- Uses instance: `self._db`, `self._structures`, `self.last_record_id`, `self.last_table`

**Calls:**
- `_structure_to_sql_table`
- `(self._structures or {}).get`
- `snapshot.items`
- `str(k).startswith`
- `str`
- `member_to_column`
- `structure.member_short_names`
- `allowed.update`
- `filtered.items`
- `self._db.insert_snapshot`
- `kwargs.get`
- `member_cols.update`

**Returns:** int

##### `snapshot_table_for(self, results_type: str)` · line 308

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `results_type: str`

**Calls:**
- `_structure_to_sql_table`

**Returns:** str

##### `update_report_path(self, table: str, record_id: int, report_path: str)` · line 311

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `table: str, record_id: int, report_path: str`
- Uses instance: `self._db`

**Calls:**
- `self._db.update_report_path`

**Returns:** None

##### `snapshots_for(self, device_tag: str)` · line 314

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** list[dict]

##### `start_test(self, device_tag: str, results_type: str)` · line 317

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str`
- Uses instance: `self._db`

**Calls:**
- `self._db.start_test_history`

**Returns:** None

##### `finish_test(self, device_tag: str, outcome: str, result: str = '')` · line 320

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, outcome: str, result: str = ''`
- Uses instance: `self._db`

**Calls:**
- `self._db.finish_open_test_history`

**Returns:** None

##### `list_running_tests(self)` · line 323

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._db`

**Calls:**
- `list`
- `self._db.list_running_tests`

**Returns:** list[dict]

##### `list_test_history(self)` · line 326

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._db`

**Calls:**
- `list`
- `self._db.list_test_history`

**Returns:** list[dict]

##### `list_recent_alarms(self)` · line 329

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._db`

**Calls:**
- `list`
- `self._db.list_recent_alarms`

**Returns:** list[dict]

##### `acknowledge_alarm(self, alarm_id: int)` · line 332

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `alarm_id: int`
- Uses instance: `self._db`

**Calls:**
- `self._db.acknowledge_alarm`

**Returns:** Optional[dict]

##### `reset_alarms(self)` · line 335

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._db`

**Calls:**
- `self._db.reset_alarms`

**Returns:** None

#### Class `AnnexReportAdapter` · line 339

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, config: Any, db: Any, store: DatabaseStoreAdapter)` · line 340

**Does:** Internal helper.

**Needs:**
- Parameters: `config: Any, db: Any, store: DatabaseStoreAdapter`
- Uses instance: `self._config`, `self._db`, `self._store`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `write(self, device_tag: str, results_type: str, snapshot: dict, quality_notes = None, project = '', snapshot_table = None, record_id = None)` · line 345

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str, snapshot: dict, quality_notes = None, project = '', snapshot_table = None, record_id = None`
- Uses instance: `self._config`, `self._db`, `self._store`

**Calls:**
- `write_reports`
- `self._db.update_report_path`
- `int`

**Returns:** Optional[str]

##### `list_for_device(self, device_tag: str, results_type: Optional[str] = None, project = None, device_id = None)` · line 375

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: Optional[str] = None, project = None, device_id = None`
- Uses instance: `self._config`

**Calls:**
- `list_reports_for_device`
- `Path`

**Returns:** list[dict]

##### `resolve_open_path(self, path: str)` · line 393

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Optional[str]

#### Class `AnnexListArchiveAdapter` · line 397

**Inherits:** `—`

**Purpose:** ArchivePort over annex_list_archive — keeps Application free of annex imports.

##### `__init__(self, host: Any)` · line 400

**Does:** Internal helper.

**Needs:**
- Parameters: `host: Any`
- Uses instance: `self._host`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `list_archives(self)` · line 403

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `list`
- `list_list_archives`

**Returns:** list[dict]

##### `create_archive(self)` · line 411

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `create_list_archive`

**Returns:** dict

##### `export_archive(self)` · line 416

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `export_list_archive`

**Returns:** tuple[dict, bytes]

##### `restore_archive(self, archive_id: str)` · line 421

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_id: str`
- Uses instance: `self._host`

**Calls:**
- `restore_list_archive`

**Returns:** dict

##### `restore_archive_upload(self, path: object, filename: str)` · line 426

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `path: object, filename: str`
- Uses instance: `self._host`

**Calls:**
- `restore_from_uploaded_file`
- `Path`

**Returns:** dict

##### `clear_keep_opc_only(self, archive_first = True)` · line 433

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `archive_first = True`
- Uses instance: `self._host`

**Calls:**
- `clear_keep_opc_only`

**Returns:** dict

##### `keep_opc_only_enabled(self)` · line 438

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._host`

**Calls:**
- `bool`
- `keep_opc_only_enabled`

**Returns:** bool

#### Class `Case1SyncSilworxAdapter` · line 447

**Inherits:** `—`

**Purpose:** SilworxPort over SilworxSyncTriggers / Case1SyncTriggers — this tool's session only.

##### `__init__(self, case1: Any, structures_fn = None, project_name_fn = None)` · line 450

**Does:** Internal helper.

**Needs:**
- Parameters: `case1: Any, structures_fn = None, project_name_fn = None`
- Uses instance: `self._case1`, `self._project_name_fn`, `self._structures_fn`

**Calls:**
- `set`

**Returns:** None

##### `is_attached(self)` · line 461

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._case1`

**Calls:**
- `bool`
- `self._case1.is_tool_attached`

**Returns:** bool

##### `attach(self)` · line 464

**Does:** Clear suspend, ensure plugin monitor, and attach every reachable GUI session.

**Needs:**
- Uses instance: `self._case1`

**Calls:**
- `self._case1.resume_tool_clients`
- `bool`
- `self._case1.is_tool_attached`
- `self._case1.discover_api_instances`
- `getattr`
- `self._case1._try_attach_gui_session_on_port`
- `int`
- `__import__('logging').getLogger`
- `__import__`
- `log.warning`

**Returns:** bool

##### `detach(self)` · line 484

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._case1`

**Calls:**
- `self._case1.detach_tool_clients`

**Returns:** None

##### `has_open_project(self)` · line 487

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._case1`

**Calls:**
- `self._case1.is_tool_attached`
- `self._case1.refresh_open_sessions`
- `bool`

**Returns:** bool

##### `list_identities(self, known_types: set[str])` · line 496

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `known_types: set[str]`
- Uses instance: `self._case1`, `self._project_name_fn`, `self._structures_fn`

**Calls:**
- `self._structures_fn`
- `try_discover_devices_via_api`
- `set`
- `_Quiet`
- `self._project_name_fn`
- `rows.append`
- `SilworxIdentity`

**Returns:** list[SilworxIdentity]

---

## Host — Engine runtime

### File `Tool Steps/service.py`

**Layer:** Host — Engine runtime

**Module purpose:** *(no module docstring)*

#### Class `ProoftestService` · line 34

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, config: AppConfig)` · line 35

**Does:** Internal helper.

**Needs:**
- Parameters: `config: AppConfig`
- Uses instance: `self._build_application`, `self._cached_device_counts`, `self._cached_opc_device_counts`, `self._cached_service_state`, `self._case1_sync`, `self._engine_lock`, `self._health_cache`, `self._health_cache_at`, `self._health_cache_ttl_sec`, `self._health_lock`, `self._last_case1_sync_check`, `self._last_device_sync`, `self._last_template_sync`, `self._loop_generation`, `self._on_shutdown`, `self._opc_servers`, `self._schema_sync_done`, `self._silworx_integration_released`, `self._silworx_uninstall_released`, `self._start_token`, `self._starting`, `self._stop`, `self._stop_in_progress`, `self._stopped`, `self._threads`, `self.alarms`, `self.app`, `self.config`, `self.db`, `self.monitor`, `self.opc`, `self.structures`

**Calls:**
- `AlarmManager`
- `Database`
- `OpcManager`
- `threading.Event`
- `Case1SyncTriggers`
- `threading.Lock`
- `self._build_application`

**Returns:** None

##### `_build_application(self)` · line 72

**Does:** Wire Presentation → Application (Engine / Catalog / Query / SILworX).

**Needs:**
- Uses instance: `self.app`

**Calls:**
- `ApplicationFacade`

**Returns:** None

##### `set_shutdown_callback(self, callback: Callable[[str], None])` · line 78

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `callback: Callable[[str], None]`
- Uses instance: `self._on_shutdown`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `engine_running(self)` · line 82

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._starting`, `self._stopped`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `_start_aborted(self, token: int)` · line 85

**Does:** Internal helper.

**Needs:**
- Parameters: `token: int`
- Uses instance: `self._start_token`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `_publish_silworx_state(self)` · line 90

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._case1_sync`, `self.db`

**Calls:**
- `self._case1_sync.refresh_open_sessions`
- `silworx_session_to_state(self._case1_sync.active_session).items`
- `silworx_session_to_state`
- `self.db.set_service_state`
- `silworx_open_projects_state(self._case1_sync.open_sessions).items`
- `silworx_open_projects_state`
- `';'.join`
- `sorted`
- `attached.items`

**Returns:** None

##### `start(self)` · line 107

**Does:** Start or restart the Prooftest engine (OPC/API/poll). Web host stays up.

**Needs:**
- Uses instance: `self._engine_lock`, `self._start_aborted`, `self._start_engine_body`, `self._start_token`, `self._start_watchdog_fire`, `self._starting`, `self._stop`, `self._stop_in_progress`, `self._stopped`, `self._threads`, `self._wait_for_stop_before_start`

**Calls:**
- `log.info`
- `any`
- `t.is_alive`
- `self._wait_for_stop_before_start`
- `self._start_aborted`
- `self._stop.clear`
- `threading.Timer`
- `self._start_watchdog_fire`
- `watchdog.start`
- `self._start_engine_body`
- `log.exception`
- `self._stop.set`
- `watchdog.cancel`

**Returns:** None

##### `_start_watchdog_fire(self, token: int, timeout_sec: float)` · line 169

**Does:** Internal helper.

**Needs:**
- Parameters: `token: int, timeout_sec: float`
- Uses instance: `self._engine_lock`, `self._start_token`, `self._starting`, `self._stop`, `self._stopped`

**Calls:**
- `self._stop.set`
- `log.error`

**Returns:** None

##### `_wait_for_stop_before_start(self, token: int, timeout_sec: float = 45.0)` · line 182

**Does:** Do not run a new engine body until graceful shutdown has released OPC/DB.

**Needs:**
- Parameters: `token: int, timeout_sec: float = 45.0`
- Uses instance: `self._engine_lock`, `self._start_aborted`, `self._start_token`, `self._starting`, `self._stop_in_progress`, `self._stopped`, `self._threads`

**Calls:**
- `log.info`
- `self._start_aborted`
- `time.sleep`
- `log.warning`
- `t.is_alive`
- `', '.join`
- `thread.join`

**Returns:** bool

##### `_start_engine_body(self, token: int)` · line 214

**Does:** Heavy start work. Returns False if Stop cancelled this start.

**Needs:**
- Parameters: `token: int`
- Uses instance: `self._background_sync_loop`, `self._build_application`, `self._case1_sync`, `self._initial_refresh_async`, `self._loop_generation`, `self._persist_alarm`, `self._poll_loop`, `self._schema_sync_done`, `self._start_aborted`, `self._threads`, `self.alarms`, `self.app`, `self.config`, `self.db`, `self.is_silworx_integration_released`, `self.monitor`, `self.opc`, `self.structures`

**Calls:**
- `self._start_aborted`
- `_stage`
- `self.config.ensure_data_dirs`
- `ensure_first_run`
- `self.db.connect`
- `self.alarms.set_persist_callback`
- `load_all_structures`
- `len`
- `self._build_application`
- `sync_results_type_folders_from_catalogue`
- `list`
- `self.structures.keys`
- `ensure_report_templates_for_structures`
- `log.warning`
- `self.db.sync_schema_case2`
- `log.exception`
- `self.alarms.raise_alarm`
- `str`
- `self.monitor.shutdown`
- `ProoftestMonitor`
- `getattr`
- `self.is_silworx_integration_released`
- `log.info`
- `self._case1_sync.prepare_for_engine_start`
- `self._case1_sync.start_monitor`
- `… +8 more`

**Returns:** bool

##### `_initial_refresh_async(self, token: int)` · line 346

**Does:** Internal helper. Triggers or participates in catalog refresh.

**Needs:**
- Parameters: `token: int`
- Uses instance: `self._start_aborted`, `self.refresh`

**Calls:**
- `self._start_aborted`
- `self.refresh`
- `log.info`
- `log.exception`

**Returns:** None

##### `_persist_alarm(self, record: AlarmRecord)` · line 356

**Does:** Internal helper.

**Needs:**
- Parameters: `record: AlarmRecord`
- Uses instance: `self.db`

**Calls:**
- `self.db.log_alarm`

**Returns:** None

##### `_should_exit_process(reason: str, exit_process: Optional[bool])` · line 366

**Does:** Internal helper.

**Needs:**
- Parameters: `reason: str, exit_process: Optional[bool]`

**Calls:**
- `bool`
- `reason.startswith`

**Returns:** bool

##### `is_silworx_integration_released(self)` · line 375

**Does:** True when operator released SILworX for uninstall (until Re-integrate).

**Needs:**
- Uses instance: `self._silworx_integration_released`, `self.db`

**Calls:**
- `getattr`
- `self.db.get_service_state`
- `str(state.get('silworx_integration') or '').strip().lower`
- `str(state.get('silworx_integration') or '').strip`
- `str`
- `state.get`

**Returns:** bool

##### `release_silworx_for_uninstall(self)` · line 394

**Does:** Operator Release SILworX — drop API/plugin/c3 locks so SILworX can be uninstalled.

**Needs:**
- Uses instance: `self._case1_sync`, `self._silworx_integration_released`, `self._silworx_uninstall_released`, `self.alarms`, `self.config`, `self.db`, `self.engine_running`, `self.refresh`

**Calls:**
- `log.warning`
- `self._case1_sync.detach_tool_clients`
- `self._case1_sync.shutdown`
- `list_c3_processes`
- `kill_leftover_c3_after_close`
- `len`
- `getattr`
- `self.db.set_service_state`
- `str`
- `time.strftime`
- `self.alarms.raise_alarm`
- `self.refresh`
- `bool`

**Returns:** Dict[str, object]

##### `reintegrate_silworx(self)` · line 454

**Does:** Operator Re-integrate SILworX after reinstall — allow API/plugin again.

**Needs:**
- Uses instance: `self._case1_sync`, `self._silworx_integration_released`, `self._silworx_uninstall_released`, `self.app`, `self.db`, `self.engine_running`

**Calls:**
- `log.info`
- `self.db.set_service_state`
- `time.strftime`
- `self._case1_sync.prepare_for_engine_start`
- `self._case1_sync.start_monitor`
- `log.warning`
- `str`
- `bool`
- `self.app.resume_silworx_connection`
- `result.update`

**Returns:** Dict[str, object]

##### `release_silworx_engines_keep_running(self)` · line 497

**Does:** G-11 — SILworX removed / uninstall in progress:

**Needs:**
- Uses instance: `self.release_silworx_for_uninstall`

**Calls:**
- `self.release_silworx_for_uninstall`

**Returns:** None

##### `request_shutdown(self, reason: str, exit_process = None)` · line 512

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `reason: str, exit_process = None`
- Uses instance: `self._on_shutdown`, `self._should_exit_process`, `self.stop`

**Calls:**
- `self._should_exit_process`
- `self._on_shutdown`
- `self.stop`

**Returns:** None

##### `request_stop_flags(self, reason: str = '')` · line 518

**Does:** Mark the engine stopped immediately (HTTP-safe).

**Needs:**
- Parameters: `reason: str = ''`
- Uses instance: `self._arm_stop_watchdog`, `self._engine_lock`, `self._loop_generation`, `self._start_token`, `self._starting`, `self._stop`, `self._stop_in_progress`, `self._stopped`

**Calls:**
- `self._stop.set`
- `self._arm_stop_watchdog`
- `log.info`

**Returns:** None

##### `_arm_stop_watchdog(self)` · line 534

**Does:** If graceful Stop hangs, clear the UI 'Stopping' flag so Start stays usable.

**Needs:**
- Uses instance: `self._start_token`, `self._stop_watchdog`

**Calls:**
- `getattr`
- `old.cancel`
- `threading.Timer`
- `timer.start`

**Returns:** None

##### `stop(self, reason: str = '')` · line 561

**Does:** Stop OPC/API/plugin/workers; keep the web host process alive unless exit was requested.

**Needs:**
- Parameters: `reason: str = ''`
- Uses instance: `self._arm_stop_watchdog`, `self._engine_lock`, `self._loop_generation`, `self._start_token`, `self._starting`, `self._stop`, `self._stop_in_progress`, `self._stopped`, `self._threads`

**Calls:**
- `self._stop.is_set`
- `self._stop.set`
- `self._arm_stop_watchdog`
- `any`
- `t.is_alive`
- `log.info`
- `clear_stop_in_progress`
- `perform_graceful_shutdown`

**Returns:** None

##### `refresh(self, manual: bool = False)` · line 580

**Does:** WorkerHost entry — delegates RefreshCatalog to Application CatalogService.

**Needs:**
- Parameters: `manual: bool = False`
- Uses instance: `self.app`

**Calls:**
- `self.app.catalog.run_station_refresh`

**Returns:** Dict[str, object]

##### `_poll_loop(self, generation: int)` · line 586

**Does:** Internal helper.

**Needs:**
- Parameters: `generation: int`
- Uses instance: `self._loop_generation`, `self._starting`, `self._stop`, `self._sync_health_caches_from_db`, `self.config`, `self.db`, `self.monitor`

**Calls:**
- `self._stop.is_set`
- `self._stop.wait`
- `self.monitor.poll_devices`
- `self.db.set_service_state`
- `time.strftime`
- `self._sync_health_caches_from_db`
- `log.exception`

**Returns:** None

##### `_background_sync_loop(self, generation: int)` · line 600

**Does:** Internal helper.

**Needs:**
- Parameters: `generation: int`
- Uses instance: `self._loop_generation`, `self._starting`, `self._stop`

**Calls:**
- `self._stop.is_set`
- `self._stop.wait`
- `time.time`
- `run_background_sync_iteration`
- `log.warning`

**Returns:** None

##### `list_devices(self, view: str = 'all')` · line 612

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `view: str = 'all'`
- Uses instance: `self._starting`, `self._stopped`, `self.app`, `self.db`

**Calls:**
- `self.app.query.list_devices`
- `log.exception`
- `sort_device_dicts`
- `self.db.list_devices`

**Returns:** list

##### `list_reports(self, device: str, results_type: Optional[str] = None, project: Optional[str] = None, device_id: Optional[str] = None)` · line 629

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device: str, results_type: Optional[str] = None, project: Optional[str] = None, device_id: Optional[str] = None`
- Uses instance: `self.app`, `self.config`

**Calls:**
- `self.app.list_reports`
- `list_reports_for_device`

**Returns:** list

##### `close_silworx_connection(self)` · line 650

**Does:** Drop this tool's API/plugin session only. Engine and OPC keep running.

**Needs:**
- Uses instance: `self._cached_service_state`, `self._case1_sync`, `self._health_cache`, `self._health_cache_at`, `self.alarms`, `self.app`, `self.db`, `self.engine_running`, `self.refresh`

**Calls:**
- `self.app.close_silworx_connection`
- `self._case1_sync.is_api_suspended`
- `self._case1_sync.is_tool_attached`
- `self._case1_sync.detach_tool_clients`
- `self.alarms.raise_alarm`
- `str`
- `self.db.set_service_state`
- `self.refresh`

**Returns:** Dict[str, object]

##### `resume_silworx_connection(self)` · line 698

**Does:** Attach to an already-open SILworX project. Never opens or kills SILworX.

**Needs:**
- Uses instance: `self._case1_sync`, `self.alarms`, `self.app`, `self.engine_running`, `self.refresh`

**Calls:**
- `self.app.resume_silworx_connection`
- `self._case1_sync.resume_tool_clients`
- `self.alarms.raise_alarm`
- `str`
- `self.refresh`
- `self._case1_sync.is_tool_attached`

**Returns:** Dict[str, object]

##### `_silworx_badge(self)` · line 734

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._case1_sync`

**Calls:**
- `self._case1_sync.is_tool_attached`

**Returns:** str

##### `_device_counts(self)` · line 737

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.db`

**Calls:**
- `self.db.count_listed_devices`
- `self.db.count_opc_devices`

**Returns:** Tuple[int, int]

##### `_device_counts_for_project(self, project_name: str)` · line 743

**Does:** Active / OPC-present devices belonging to one SILworX project name.

**Needs:**
- Parameters: `project_name: str`
- Uses instance: `self.db`

**Calls:**
- `str(project_name or '').strip`
- `str`
- `self.db.list_active_devices`
- `str((row or {}).get('project') or (row or {}).get('silworx_project') or '').strip`
- `(row or {}).get`

**Returns:** Tuple[int, int]

##### `_api_project_device_count(self)` · line 762

**Does:** Last RefreshCatalog SILworX API identity count (true project size).

**Needs:**
- Uses instance: `self.db`

**Calls:**
- `str((self.db.get_service_state() or {}).get('silworx_project_devices') or '').strip`
- `str`
- `(self.db.get_service_state() or {}).get`
- `self.db.get_service_state`
- `raw.isdigit`
- `int`

**Returns:** Optional[int]

##### `_resolve_silworx_project_name(self, payload: Dict[str, object], project_name: str = '')` · line 772

**Does:** Internal helper.

**Needs:**
- Parameters: `payload: Dict[str, object], project_name: str = ''`
- Uses instance: `self.db`

**Calls:**
- `str(project_name or '').strip`
- `str`
- `isinstance`
- `payload.get`
- `str((api or {}).get('project_name') or (sil or {}).get('silworx_project_name') or (sil or {}).get('project_name') or '').strip`
- `(api or {}).get`
- `(sil or {}).get`
- `self.db.get_service_state`
- `str(st.get('silworx_project_name') or st.get('project_name') or '').strip`
- `st.get`
- `raw.replace(',', ';').split`
- `raw.replace`
- `part.strip`
- `token.split(':', 1)[1].strip`
- `token.split`
- `str(first.get('project_name') or first.get('project_file') or '').strip`
- `first.get`

**Returns:** str

##### `_attach_project_device_counts(self, payload: Dict[str, object], project_name: str = '')` · line 816

**Does:** Expose SILworX project device counts (API size vs OPC-listed subset).

**Needs:**
- Parameters: `payload: Dict[str, object], project_name: str = ''`
- Uses instance: `self._api_project_device_count`, `self._device_counts_for_project`, `self._resolve_silworx_project_name`, `self._silworx_badge`

**Calls:**
- `self._resolve_silworx_project_name`
- `self._api_project_device_count`
- `self._device_counts_for_project`
- `self._silworx_badge`

**Returns:** Dict[str, object]

##### `_opc_device_counts_by_server(self)` · line 846

**Does:** Active catalog devices grouped by OPC ProgID (for health UI).

**Needs:**
- Uses instance: `self.db`

**Calls:**
- `self.db.list_active_devices`
- `str((row or {}).get('opc_server') or '').strip`
- `str`
- `(row or {}).get`
- `counts.get`

**Returns:** Dict[str, int]

##### `_sync_health_caches_from_db(self)` · line 859

**Does:** Keep UI health fresh even when catalog refresh is slow/stuck.

**Needs:**
- Uses instance: `self._cached_device_counts`, `self._cached_opc_device_counts`, `self._cached_service_state`, `self._device_counts`, `self._opc_device_counts_by_server`, `self.db`

**Calls:**
- `self._device_counts`
- `self._opc_device_counts_by_server`
- `self.db.get_service_state`
- `dict`

**Returns:** None

##### `_health_stub_from_caches(self)` · line 876

**Does:** Fast payload when the health lock is busy — never return empty zeros if DB has data.

**Needs:**
- Uses instance: `self._cached_device_counts`, `self._cached_service_state`, `self._decorate_health`, `self._opc_servers`, `self._starting`, `self._stopped`, `self._sync_health_caches_from_db`, `self.config`, `self.db`, `self.engine_running`, `self.monitor`

**Calls:**
- `self._sync_health_caches_from_db`
- `dict`
- `list`
- `str`
- `service_state.get`
- `raw.split`
- `int`
- `(getattr(self, '_cached_opc_device_counts', {}) or {}).get`
- `getattr`
- `bool`
- `self._decorate_health`

**Returns:** Dict[str, object]

##### `_decorate_health(self, payload: Dict[str, object], engine: str)` · line 935

**Does:** Internal helper.

**Needs:**
- Parameters: `payload: Dict[str, object], engine: str`
- Uses instance: `self._attach_project_device_counts`, `self._opc_servers`, `self._silworx_badge`, `self.alarms`, `self.config`, `self.is_silworx_integration_released`

**Calls:**
- `payload.get`
- `isinstance`
- `len`
- `int`
- `self._silworx_badge`
- `self._attach_project_device_counts`
- `payload.setdefault`
- `self.is_silworx_integration_released`
- `bool`
- `getattr`
- `str`
- `self.alarms.last_error`

**Returns:** Dict[str, object]

##### `health(self)` · line 961

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._cached_device_counts`, `self._cached_opc_device_counts`, `self._cached_service_state`, `self._case1_sync`, `self._decorate_health`, `self._health_cache`, `self._health_cache_at`, `self._health_cache_ttl_sec`, `self._health_lock`, `self._health_stub_from_caches`, `self._opc_device_counts_by_server`, `self._opc_servers`, `self._starting`, `self._stopped`, `self._sync_health_caches_from_db`, `self.config`, `self.db`, `self.engine_running`, `self.is_silworx_integration_released`, `self.monitor`, `self.opc`

**Calls:**
- `dict`
- `service_state.setdefault`
- `getattr`
- `service_state.get`
- `bool`
- `int`
- `self.is_silworx_integration_released`
- `str`
- `time.monotonic`
- `self._health_lock.acquire`
- `self._health_stub_from_caches`
- `self._sync_health_caches_from_db`
- `self._decorate_health`
- `self.opc.health_snapshot`
- `type`
- `silworx_session_to_state`
- `self._case1_sync.refresh_open_sessions`
- `self._case1_sync.api_connected_project_name`
- `self._case1_sync.registered_plugin_session_name`
- `self._case1_sync.plugin_session_states`
- `(self._case1_sync._attached_project_names_by_api or {}).items`
- `self._opc_device_counts_by_server`
- `device_by_server.get`
- `log.exception`
- `self._health_lock.release`

**Returns:** Dict[str, object]

---

## Host — ProoftestMonitor

### File `Tool Steps/step05_detection.py`

**Layer:** Host — ProoftestMonitor

**Module purpose:** Production poll host — thin shell over Application LiveTestService (Gap C).

#### Class `ProoftestMonitor` · line 25

**Inherits:** `—`

**Purpose:** Thin production host for LiveTestService.

Owns OPC snapshot collection + report worker. Edge detection / complete path
is always ``LiveTestService`` (injected from ApplicationFacade when available).

##### `__init__(self, config: AppConfig, db: Database, opc: OpcManager, structures: Dict[str, ResultsStructure], live_service = None)` · line 33

**Does:** Internal helper.

**Needs:**
- Parameters: `config: AppConfig, db: Database, opc: OpcManager, structures: Dict[str, ResultsStructure], live_service = None`
- Uses instance: `self._annex_types`, `self._collect_snapshot`, `self._live`, `self._queue`, `self._report_lock`, `self._report_worker`, `self._reports`, `self._stop`, `self._store`, `self._worker`, `self.config`, `self.db`, `self.opc`, `self.structures`

**Calls:**
- `load_annex_types`
- `annexes_directory`
- `log.info`
- `len`
- `log.warning`
- `queue.Queue`
- `threading.Lock`
- `threading.Event`
- `DatabaseStoreAdapter`
- `AnnexReportAdapter`
- `OpcManagerAdapter`
- `AlarmManagerAdapter`
- `LiveTestService`
- `threading.Thread`
- `self._worker.start`

**Returns:** None

##### `reload_type_catalog(self)` · line 84

**Does:** Reload annex nested types after Results Structures catalogue changes.

**Needs:**
- Uses instance: `self._annex_types`, `self.config`

**Calls:**
- `load_annex_types`
- `annexes_directory`
- `log.info`
- `len`

**Returns:** None

##### `shutdown(self, timeout: float = 30.0)` · line 89

**Does:** Stop the report worker and drain or abandon the completion queue.

**Needs:**
- Parameters: `timeout: float = 30.0`
- Uses instance: `self._queue`, `self._stop`, `self._worker`

**Calls:**
- `self._stop.set`
- `self._queue.put`
- `self._worker.join`
- `self._worker.is_alive`
- `log.warning`

**Returns:** None

##### `poll_devices(self)` · line 97

**Does:** Production poll entry — delegates entirely to LiveTestService.poll_once.

**Needs:**
- Uses instance: `self._live`, `self._queue`, `self.db`

**Calls:**
- `self.db.list_active_devices`
- `devices.append`
- `isinstance`
- `device_from_row`
- `self.db.alarms.raise_alarm`
- `getattr`
- `row.get`
- `str`
- `self._live.poll_once`
- `self._queue.put`
- `self._live.queue.pop`

**Returns:** None

##### `_poll_one(self, device: Union[Dict[str, Any], Device])` · line 117

**Does:** Compatibility for older callers — prefer poll_devices.

**Needs:**
- Parameters: `device: Union[Dict[str, Any], Device]`
- Uses instance: `self._live`, `self._queue`

**Calls:**
- `isinstance`
- `device_from_row`
- `self._live.seed_device`
- `self._live._poll_one`
- `self._queue.put`
- `self._live.queue.pop`

**Returns:** None

##### `_collect_snapshot(self, device: Device)` · line 126

**Does:** Internal helper.

**Needs:**
- Parameters: `device: Device`
- Uses instance: `self._read_snapshot`, `self.db`, `self.opc`, `self.structures`

**Calls:**
- `(device.results_type or '').strip`
- `self.structures.get`
- `self.opc.resolve_device_binding`
- `self.db.upsert_device`
- `device.device_id.key`
- `self._read_snapshot`

**Returns:** tuple[Dict[str, Any], List[str]]

##### `_read_snapshot(self, server: str, tags: List[str], prefix: str, structure: ResultsStructure)` · line 156

**Does:** Internal helper.

**Needs:**
- Parameters: `server: str, tags: List[str], prefix: str, structure: ResultsStructure`
- Uses instance: `self._annex_types`, `self.opc`

**Calls:**
- `structure.member_short_names`
- `n.lower`
- `self.opc.build_member_item_ids`
- `list`
- `item_map.values`
- `self.opc.read_values`
- `member_column_dtype_map`
- `item_map.items`
- `values.get`
- `member_to_column`
- `col_dtypes.get`
- `str(quality).lower`
- `str`
- `notes.append`
- `value_is_empty`
- `is_ascii_type`
- `is_parameters_type`
- `enrich_snapshot_from_opc`
- `t.endswith`
- `self.opc.read_values(server, [running_items[0]]).get`
- `bool`

**Returns:** tuple[Dict[str, Any], List[str]]

##### `_report_worker(self)` · line 208

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._live`, `self._queue`, `self._report_lock`, `self._stop`, `self.db`

**Calls:**
- `self._stop.is_set`
- `self._queue.get`
- `self._live.run_complete`
- `isinstance`
- `event.get`
- `getattr`
- `self.db.alarms.raise_alarm`
- `str`
- `self._queue.task_done`

**Returns:** None

##### `queue_depth(self)` · line 235

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._live`, `self._queue`

**Calls:**
- `self._queue.qsize`

**Returns:** int

##### `live(self)` · line 239

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._live`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** LiveTestService

---

## Host — Sync triggers

### File `Tool Steps/step07_triggers.py`

**Layer:** Host — Sync triggers

**Module purpose:** *(no module docstring)*

#### Module-level functions *(no class)*

##### `_read_marker(marker: Path)` · line 36

**Does:** Internal helper.

**Needs:**
- Parameters: `marker: Path`

**Calls:**
- `marker.exists`
- `float`
- `marker.read_text(encoding='utf-8').strip`
- `marker.read_text`

**Returns:** float

##### `_path_mtime(path: Path)` · line 45

**Does:** Internal helper.

**Needs:**
- Parameters: `path: Path`

**Calls:**
- `path.stat`

**Returns:** float

##### `_parse_lock_ini(lock_path: Path)` · line 52

**Does:** Internal helper.

**Needs:**
- Parameters: `lock_path: Path`

**Calls:**
- `configparser.ConfigParser`
- `parser.read`
- `parser.has_section`
- `section.items`

**Returns:** Dict[str, str]

##### `discover_open_projects(programdata_root: Path)` · line 59

**Does:** Find all SILworX sessions with an active lock.ini (project open in SILworX).

**Needs:**
- Parameters: `programdata_root: Path`

**Calls:**
- `programdata_root.is_dir`
- `sorted`
- `programdata_root.glob`
- `sessions_root.is_dir`
- `sessions_root.iterdir`
- `session_dir.is_dir`
- `lock_ini.exists`
- `_parse_lock_ini`
- `log.debug`
- `lock.get('src', '').strip`
- `lock.get`
- `lock.get('data', '').strip`
- `Path`
- `found.append`
- `SilworxOpenProject`
- `lock.get('temp', '').strip`

**Returns:** List[SilworxOpenProject]

##### `is_silworx_open(programdata_root: Path)` · line 102

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `programdata_root: Path`

**Calls:**
- `bool`
- `discover_open_projects`

**Returns:** bool

##### `pick_configured_session(sessions: List[SilworxOpenProject], configured_projects: List[Path], preferred_version_substr = '')` · line 106

**Does:** Choose which open SILworX session is "active" for UI/state.

**Needs:**
- Parameters: `sessions: List[SilworxOpenProject], configured_projects: List[Path], preferred_version_substr = ''`

**Calls:**
- `_norm`
- `configured_path.stem.lower().replace`
- `configured_path.stem.lower`
- `configured_path.name.lower`
- `session.src_path.name.lower`
- `session.src_path.stem.lower().replace`
- `session.src_path.stem.lower`
- `(session.project_file or '').lower`
- `src_stem.replace`
- `(session.project_name or '').lower().replace`
- `(session.project_name or '').lower`
- `preferred_version_substr.lower().strip`
- `preferred_version_substr.lower`
- `(session.silworx_version or '').lower`

**Returns:** Optional[SilworxOpenProject]

##### `session_working_mtime(session: SilworxOpenProject)` · line 162

**Does:** Fast mtime signal for the live session database (avoid full c3data rglob).

**Needs:**
- Parameters: `session: SilworxOpenProject`

**Calls:**
- `c3data.is_dir`
- `_path_mtime`
- `c3data.iterdir`
- `max`
- `path.is_dir`
- `path.iterdir`
- `child.is_dir`

**Returns:** float

##### `folder_aggregate_mtime(folder: Path, pattern: str = '*.csv')` · line 182

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `folder: Path, pattern: str = '*.csv'`

**Calls:**
- `folder.is_dir`
- `folder.glob`
- `match.is_file`
- `max`
- `_path_mtime`

**Returns:** float

##### `watch_mtime_increased(source_mtime: float, marker: Path)` · line 192

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `source_mtime: float, marker: Path`

**Calls:**
- `_read_marker`

**Returns:** bool

##### `commit_marker(marker: Path, source_mtime: float)` · line 198

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `marker: Path, source_mtime: float`

**Calls:**
- `marker.parent.mkdir`
- `marker.write_text`
- `str`

**Returns:** None

##### `watch_project_changed(project_path: Path, marker: Path)` · line 203

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `project_path: Path, marker: Path`

**Calls:**
- `project_path.exists`
- `project_path.with_suffix`
- `lock.exists`
- `watch_mtime_increased`
- `_path_mtime`

**Returns:** bool

##### `watch_results_structures_changed(folder: Path, marker: Path)` · line 212

**Does:** True when Results Structure CSV folder mtime advanced.

**Needs:**
- Parameters: `folder: Path, marker: Path`

**Calls:**
- `watch_mtime_increased`
- `folder_aggregate_mtime`

**Returns:** bool

##### `watch_session_changed(session: SilworxOpenProject, marker: Path)` · line 223

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `session: SilworxOpenProject, marker: Path`

**Calls:**
- `watch_mtime_increased`
- `session_working_mtime`

**Returns:** bool

##### `silworx_session_to_state(session: Optional[SilworxOpenProject])` · line 227

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `session: Optional[SilworxOpenProject]`

**Calls:**
- `str`

**Returns:** Dict[str, str]

##### `silworx_open_projects_state(sessions: List[SilworxOpenProject])` · line 255

**Does:** Service-state fields listing every open SILworX project (not only the preferred one).

**Needs:**
- Parameters: `sessions: List[SilworxOpenProject]`

**Calls:**
- `(s.project_name or '').strip`
- `(s.project_file or '').strip`
- `(s.session_id or '').strip`
- `str`
- `len`
- `';'.join`

**Returns:** Dict[str, str]

##### `run_background_sync_iteration(service, now: float)` · line 988

**Does:** Run one Step 7 background synchronization iteration (unified path).

**Needs:**
- Parameters: `service, now: float`

**Calls:**
- `getattr`
- `service._stop.is_set`
- `bool`
- `is_silworx_installed`
- `service.release_silworx_engines_keep_running`
- `is_silworx_running`
- `is_silworx_open`
- `service.db.set_service_state`
- `service._case1_sync._plugin_monitor.stop`
- `log.info`
- `service._case1_sync.discover_api_instances`
- `';'.join`
- `iter_port_pairs`
- `service._case1_sync.api_instance_labels`
- `service._case1_sync.plugin_monitor_summary`
- `service._case1_sync.try_close_owned_session`
- `service._case1_sync.release_api_connection`
- `service._case1_sync.is_api_suspended`
- `service._case1_sync.is_tool_attached`
- `service._case1_sync.uncovered_open_projects`
- `', '.join`
- `service.app.refresh_catalog`
- `service.refresh`
- `time.strftime`
- `log.warning`
- `… +21 more`

**Returns:** None

#### Class `SilworxOpenProject` · line 24

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `SilworxSyncTriggers` · line 269

**Inherits:** `—`

**Purpose:** Unified SILworX API/plugin sync (formerly Case1SyncTriggers).

##### `__post_init__(self)` · line 293

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._enabled`, `self.config`

**Calls:**
- `t.strip().lower`
- `t.strip`

**Returns:** None

##### `is_api_suspended(self)` · line 296

**Does:** True when SILworX is down and the service must not open API sessions.

**Needs:**
- Uses instance: `self._silworx_api_suspended`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `is_operator_detached(self)` · line 300

**Does:** True after Disconnect until Connect — do not auto-resume plugin/API.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `bool`
- `getattr`

**Returns:** bool

##### `owns_api_session(self)` · line 304

**Does:** True when this service still tracks an owned API session (legacy; tool no longer opens projects).

**Needs:**
- Uses instance: `self._owned_sessions_by_port`

**Calls:**
- `bool`

**Returns:** bool

##### `discover_api_instances(self, force = False)` · line 308

**Does:** Scan all configured API/plugin port pairs and cache reachable instances.

**Needs:**
- Parameters: `force = False`
- Uses instance: `self._available_instances`, `self._instances_scanned_at`, `self.config`

**Calls:**
- `time.monotonic`
- `discover_available_instances`

**Returns:** List[object]

##### `api_instance_labels(self)` · line 324

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._available_instances`

**Calls:**
- `';'.join`

**Returns:** str

##### `_api_port_order(self)` · line 327

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._available_instances`, `self.config`

**Calls:**
- `sorted`

**Returns:** List[int]

##### `_mark_service_opened_session(self, session_id: str, api_port: int)` · line 334

**Does:** Internal helper.

**Needs:**
- Parameters: `session_id: str, api_port: int`
- Uses instance: `self._active_api_port`, `self._owned_sessions_by_port`, `self._service_owns_api_session`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `_clear_service_opened_session(self, api_port: Optional[int] = None)` · line 339

**Does:** Internal helper.

**Needs:**
- Parameters: `api_port: Optional[int] = None`
- Uses instance: `self._owned_sessions_by_port`, `self._service_owns_api_session`

**Calls:**
- `self._owned_sessions_by_port.clear`
- `self._owned_sessions_by_port.pop`

**Returns:** None

##### `_ensure_silworx_api_available(self)` · line 347

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._silworx_api_suspended`, `self.config`, `self.discover_api_instances`

**Calls:**
- `SilworxApiConnectionError`
- `self.discover_api_instances`

**Returns:** None

##### `get_api_client(self, api_port: Optional[int] = None)` · line 361

**Does:** Lazy SILworX OpenAPI client for one API port.

**Needs:**
- Parameters: `api_port: Optional[int] = None`
- Uses instance: `self._active_api_port`, `self._api_clients`, `self.config`

**Calls:**
- `build_client_for_port`

**Returns:** 'SilworxApiClient'

##### `request_fresh_plugin_session(self, api_port: Optional[int] = None)` · line 371

**Does:** Drop cached plugin tokens and reconnect so SILworX issues a new user_session_id.

**Needs:**
- Parameters: `api_port: Optional[int] = None`
- Uses instance: `self._plugin_monitor`, `self.config`

**Calls:**
- `plugin_port_for_api`
- `self._plugin_monitor.request_fresh_session`

**Returns:** None

##### `_try_attach_gui_session_on_port(self, api_port: int)` · line 380

**Does:** Internal helper.

**Needs:**
- Parameters: `api_port: int`
- Uses instance: `self._attach_with_resolved_session`, `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._plugin_monitor`, `self.config`, `self.get_api_client`, `self.open_sessions`, `self.refresh_open_sessions`, `self.request_fresh_plugin_session`

**Calls:**
- `self.refresh_open_sessions`
- `plugin_port_for_api`
- `(self._attached_session_ids_by_api.get(api_port) or '').strip`
- `self._attached_session_ids_by_api.get`
- `(self._plugin_monitor.get_session_id(plugin_port) or '').strip`
- `self._plugin_monitor.get_session_id`
- `self.get_api_client`
- `client.set_session_id`
- `log.info`
- `self._attached_session_ids_by_api.pop`
- `self._attached_project_names_by_api.pop`
- `self._attach_with_resolved_session`
- `self.request_fresh_plugin_session`

**Returns:** bool

##### `_infer_attached_project_name(self, api_port: int, session_id: str, tree: object)` · line 424

**Does:** Map an attached API session to one open lock.ini project (multi-project safe).

**Needs:**
- Parameters: `api_port: int, session_id: str, tree: object`
- Uses instance: `self._attached_project_names_by_api`, `self.open_sessions`

**Calls:**
- `(session_id or '').strip`
- `sid.lower`
- `(session.session_id or '').strip().lower`
- `(session.session_id or '').strip`
- `(name or '').strip`
- `self._attached_project_names_by_api.items`
- `json.dumps(tree, ensure_ascii=False).lower`
- `json.dumps`
- `(session.project_name or '').strip`
- `(session.project_file or '').strip`
- `name.lower`
- `file_name.lower`
- `candidates.append`
- `len`
- `candidates.sort`

**Returns:** str

##### `_attach_with_resolved_session(self, api_port: int, plugin_port: int, wait_timeout_sec = 0.0)` · line 476

**Does:** Internal helper.

**Needs:**
- Parameters: `api_port: int, plugin_port: int, wait_timeout_sec = 0.0`
- Uses instance: `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._infer_attached_project_name`, `self._last_attached_api_port`, `self._plugin_monitor`, `self.active_session`, `self.config`, `self.get_api_client`, `self.refresh_open_sessions`

**Calls:**
- `resolve_gui_session_id`
- `max`
- `self.get_api_client`
- `client.set_session_id`
- `client.get_structuretree`
- `log.warning`
- `client.clear_session_id`
- `self._attached_session_ids_by_api.pop`
- `self._attached_project_names_by_api.pop`
- `self.refresh_open_sessions`
- `self._infer_attached_project_name`
- `log.info`
- `len`

**Returns:** bool

##### `attached_project_name_for_port(self, api_port: int)` · line 526

**Does:** SILworX project name last attached on this API port.

**Needs:**
- Parameters: `api_port: int`
- Uses instance: `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._infer_attached_project_name`, `self.api_connected_project_name`, `self.open_sessions`

**Calls:**
- `(self._attached_project_names_by_api.get(api_port) or '').strip`
- `self._attached_project_names_by_api.get`
- `(self._attached_session_ids_by_api.get(api_port) or '').strip`
- `self._attached_session_ids_by_api.get`
- `self._infer_attached_project_name`
- `len`
- `self.api_connected_project_name`

**Returns:** str

##### `uncovered_open_projects(self)` · line 541

**Does:** Open lock.ini projects not yet mapped to an attached API port.

**Needs:**
- Uses instance: `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._available_instances`, `self.discover_api_instances`, `self.open_sessions`, `self.refresh_open_sessions`

**Calls:**
- `self.refresh_open_sessions`
- `list`
- `self.discover_api_instances`
- `(self._attached_session_ids_by_api or {}).items`
- `(sid or '').strip`
- `(name or '').strip`
- `(self._attached_project_names_by_api or {}).values`
- `len`
- `(s.project_name or '').strip`

**Returns:** List[str]

##### `api_session_for_port(self, api_port: int, project_path: Optional[Path] = None, alarms: Optional[AlarmManager] = None, allow_open_local = False)` · line 579

**Does:** API session on one SILworX instance — attach only.

**Needs:**
- Parameters: `api_port: int, project_path: Optional[Path] = None, alarms: Optional[AlarmManager] = None, allow_open_local = False`
- Uses instance: `self._attached_session_ids_by_api`, `self._ensure_silworx_api_available`, `self._try_attach_gui_session_on_port`, `self.get_api_client`

**Calls:**
- `self._ensure_silworx_api_available`
- `self.get_api_client`
- `self._try_attach_gui_session_on_port`
- `(self._attached_session_ids_by_api.get(api_port) or '').strip`
- `self._attached_session_ids_by_api.get`
- `client.set_session_id`
- `client.clear_session_id`
- `SilworxProjectConflictError`

**Returns:** Iterator['SilworxApiClient']

##### `api_session(self, project_path: Optional[Path] = None, alarms: Optional[AlarmManager] = None)` · line 619

**Does:** Provide an API client bound to a user-open SILworX project.

**Needs:**
- Parameters: `project_path: Optional[Path] = None, alarms: Optional[AlarmManager] = None`
- Uses instance: `self._api_port_order`, `self._ensure_silworx_api_available`, `self._try_attach_gui_session_on_port`, `self.active_session`, `self.api_session_for_port`, `self.get_api_client`, `self.refresh_active_session`

**Calls:**
- `self._ensure_silworx_api_available`
- `self.refresh_active_session`
- `self._api_port_order`
- `self._try_attach_gui_session_on_port`
- `self.get_api_client`
- `client.clear_session_id`
- `self.api_session_for_port`
- `alarms.raise_alarm`
- `str`
- `SilworxApiError`

**Returns:** Iterator['SilworxApiClient']

##### `try_close_owned_session(self)` · line 677

**Does:** Best-effort close for open/local sessions on all owned API ports.

**Needs:**
- Uses instance: `self._clear_service_opened_session`, `self._owned_sessions_by_port`, `self.get_api_client`, `self.owns_api_session`

**Calls:**
- `self.owns_api_session`
- `list`
- `self._owned_sessions_by_port.items`
- `self.get_api_client`
- `client.close_project`
- `self._clear_service_opened_session`

**Returns:** bool

##### `release_api_connection(self)` · line 693

**Does:** Stop SILworX API sessions when all instances are closed (G-19).

**Needs:**
- Uses instance: `self._active_api_port`, `self._api_clients`, `self._api_opened_by_service`, `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._available_instances`, `self._clear_service_opened_session`, `self._last_attached_api_port`, `self._owned_sessions_by_port`, `self._silworx_api_suspended`, `self.config`

**Calls:**
- `bool`
- `list`
- `self._owned_sessions_by_port.items`
- `self._api_clients.get`
- `build_client_for_port`
- `client.close_project`
- `log.debug`
- `self._clear_service_opened_session`
- `self._api_clients.values`
- `client.clear_session_id`
- `self._api_clients.clear`
- `self._attached_session_ids_by_api.clear`
- `self._attached_project_names_by_api.clear`
- `log.info`

**Returns:** bool

##### `detach_tool_clients(self)` · line 732

**Does:** Drop this tool's API client and plugin monitor. Never project/close GUI, never kill c3.exe.

**Needs:**
- Uses instance: `self._active_api_port`, `self._api_clients`, `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._operator_detached`, `self._plugin_monitor`, `self._silworx_api_suspended`

**Calls:**
- `self._plugin_monitor.stop`
- `log.warning`
- `list`
- `self._api_clients.values`
- `client.clear_session_id`
- `self._api_clients.clear`
- `self._attached_session_ids_by_api.clear`
- `self._attached_project_names_by_api.clear`
- `log.info`

**Returns:** None

##### `resume_tool_clients(self)` · line 753

**Does:** Re-enable API/plugin attach. Does not open a SILworX project.

**Needs:**
- Uses instance: `self._operator_detached`, `self.prepare_for_engine_start`, `self.start_monitor`

**Calls:**
- `self.prepare_for_engine_start`
- `self.start_monitor`

**Returns:** None

##### `is_tool_attached(self)` · line 759

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self.is_api_suspended`, `self.is_operator_detached`

**Calls:**
- `self.is_api_suspended`
- `self.is_operator_detached`
- `bool`

**Returns:** bool

##### `_drop_stale_attachments_vs_plugin(self)` · line 764

**Does:** Drop API attaches whose plugin session token changed (other SILworX window).

**Needs:**
- Uses instance: `self._api_clients`, `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._plugin_monitor`, `self.config`

**Calls:**
- `list`
- `self._attached_session_ids_by_api.items`
- `plugin_port_for_api`
- `(self._plugin_monitor.get_session_id(plugin_port) or '').strip`
- `self._plugin_monitor.get_session_id`
- `log.info`
- `self._attached_session_ids_by_api.pop`
- `self._attached_project_names_by_api.pop`
- `self._api_clients.get`
- `client.clear_session_id`

**Returns:** None

##### `_marker(self, key: str)` · line 791

**Does:** Internal helper.

**Needs:**
- Parameters: `key: str`
- Uses instance: `self.markers_dir`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Path

##### `refresh_open_sessions(self)` · line 794

**Does:** All SILworX sessions with an open project (lock.ini), any instance.

**Needs:**
- Uses instance: `self._available_instances`, `self.active_session`, `self.config`, `self.open_sessions`

**Calls:**
- `discover_open_projects`
- `str`
- `getattr`
- `pick_configured_session`

**Returns:** List[SilworxOpenProject]

##### `refresh_active_session(self)` · line 809

**Does:** Triggers or participates in catalog refresh.

**Needs:**
- Uses instance: `self.active_session`, `self.refresh_open_sessions`

**Calls:**
- `self.refresh_open_sessions`

**Returns:** Optional[SilworxOpenProject]

##### `prepare_for_engine_start(self)` · line 813

**Does:** Clear G-19 suspend flags so a UI Start can use SILworX API again.

**Needs:**
- Uses instance: `self._operator_detached`, `self._silworx_api_suspended`, `self._silworx_down_streak`

**Calls:**
- `log.info`

**Returns:** None

##### `start_monitor(self)` · line 820

**Does:** Start persistent plugin WebSocket listeners on all configured port pairs (G-22).

**Needs:**
- Uses instance: `self._plugin_monitor`, `self.config`

**Calls:**
- `PluginPortMonitor`
- `self._plugin_monitor.start`

**Returns:** None

##### `plugin_monitor_summary(self)` · line 829

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._plugin_monitor`

**Calls:**
- `self._plugin_monitor.port_states_summary`

**Returns:** str

##### `plugin_session_states(self)` · line 834

**Does:** Per-port plugin WebSocket state for Status UI (connected / disconnected).

**Needs:**
- Uses instance: `self._plugin_monitor`

**Calls:**
- `sorted`
- `monitor._ports.values`
- `rows.append`
- `int`
- `bool`
- `str`

**Returns:** list

##### `api_connected_project_name(self, device_list_source: str = '')` · line 852

**Does:** Project name when the device list is served via SILworX API.

**Needs:**
- Parameters: `device_list_source: str = ''`
- Uses instance: `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._last_attached_api_port`, `self.open_sessions`, `self.refresh_open_sessions`

**Calls:**
- `str(device_list_source).lower().strip`
- `str(device_list_source).lower`
- `str`
- `self.refresh_open_sessions`
- `candidate_ports.append`
- `sorted`
- `self._attached_session_ids_by_api.keys`
- `(self._attached_project_names_by_api.get(port) or '').strip`
- `self._attached_project_names_by_api.get`
- `self._attached_session_ids_by_api.get`
- `_project_for_sid`
- `len`

**Returns:** str

##### `registered_plugin_session_name(self)` · line 886

**Does:** Configured plugin name when at least one plugin WebSocket is registered.

**Needs:**
- Uses instance: `self._plugin_monitor`, `self.config`

**Calls:**
- `any`
- `monitor._ports.values`

**Returns:** str

##### `check(self)` · line 896

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._attached_project_names_by_api`, `self._attached_session_ids_by_api`, `self._drop_stale_attachments_vs_plugin`, `self._enabled`, `self._marker`, `self._plugin_monitor`, `self.config`, `self.open_sessions`, `self.refresh_open_sessions`, `self.request_fresh_plugin_session`

**Calls:**
- `str`
- `self.refresh_open_sessions`
- `log.info`
- `self._attached_session_ids_by_api.clear`
- `self._attached_project_names_by_api.clear`
- `self.request_fresh_plugin_session`
- `fired.append`
- `self._plugin_monitor.consume_triggers`
- `self._drop_stale_attachments_vs_plugin`
- `watch_session_changed`
- `self._marker`
- `watch_project_changed`
- `watch_results_structures_changed`

**Returns:** List[str]

##### `commit(self)` · line 954

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._enabled`, `self._marker`, `self.config`, `self.markers_dir`, `self.open_sessions`, `self.refresh_open_sessions`

**Calls:**
- `self.markers_dir.mkdir`
- `self.refresh_open_sessions`
- `commit_marker`
- `self._marker`
- `session_working_mtime`
- `project.exists`
- `_path_mtime`
- `self.config.results_structures.is_dir`
- `folder_aggregate_mtime`

**Returns:** None

##### `shutdown(self)` · line 976

**Does:** Release SILworX API session state and stop plugin monitors.

**Needs:**
- Uses instance: `self._plugin_monitor`, `self.release_api_connection`

**Calls:**
- `self._plugin_monitor.stop`
- `self.release_api_connection`

**Returns:** None

---

## Infrastructure — Tool Steps

### File `Tool Steps/__init__.py`

**Layer:** Infrastructure — Tool Steps

**Module purpose:** Step and service modules — import through the ``prooftest`` package at solution root.

*(empty module)*

### File `Tool Steps/alarms.py`

**Layer:** Infrastructure — Tool Steps

**Module purpose:** *(no module docstring)*

#### Module-level functions *(no class)*

##### `alarm_error_key(step: str, message: Optional[str])` · line 153

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `step: str, message: Optional[str]`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

#### Class `AlarmRecord` · line 142

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `AlarmManager` · line 157

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self)` · line 158

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._alarms`, `self._last_error`, `self._last_seen`, `self._lock`, `self._pending_popups`, `self._persist_callback`, `self._shown_keys`

**Calls:**
- `threading.Lock`
- `set`

**Returns:** None

##### `set_persist_callback(self, callback: Callable[[AlarmRecord], None])` · line 167

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `callback: Callable[[AlarmRecord], None]`
- Uses instance: `self._persist_callback`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `raise_alarm(self, step: str, message: str, severity = 'Error', device_tag = None, cause = None, show_popup = True, action = None)` · line 170

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `step: str, message: str, severity = 'Error', device_tag = None, cause = None, show_popup = True, action = None`
- Uses instance: `self._alarms`, `self._last_error`, `self._last_seen`, `self._lock`, `self._pending_popups`, `self._persist_callback`, `self._shown_keys`

**Calls:**
- `DIAGNOSTICS.get`
- `diag.get`
- `alarm_error_key`
- `AlarmRecord`
- `datetime.now`
- `self._alarms.append`
- `time.monotonic`
- `self._shown_keys.add`
- `self._pending_popups.append`
- `record.timestamp.isoformat`
- `self._persist_callback`

**Returns:** None

##### `last_error(self)` · line 222

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._last_error`, `self._lock`

**Calls:**
- `dict`

**Returns:** Optional[Dict[str, Any]]

##### `clear_shown_on_refresh(self)` · line 226

**Does:** Triggers or participates in catalog refresh.

**Needs:**
- Uses instance: `self._lock`, `self._shown_keys`

**Calls:**
- `self._shown_keys.clear`

**Returns:** None

##### `pop_pending_popups(self)` · line 230

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._lock`, `self._pending_popups`

**Calls:**
- `list`
- `self._pending_popups.clear`

**Returns:** List[Dict[str, Any]]

##### `recent_alarms(self, limit: int = 50)` · line 236

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `limit: int = 50`
- Uses instance: `self._alarms`, `self._lock`, `self.active_error_keys`

**Calls:**
- `self.active_error_keys`
- `a.timestamp.isoformat`
- `reversed`

**Returns:** List[Dict[str, Any]]

##### `active_error_keys(self)` · line 255

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._last_seen`, `self._lock`

**Calls:**
- `time.monotonic`
- `self._last_seen.items`

**Returns:** Set[str]

##### `acknowledge_error_key(self, error_key: str)` · line 264

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `error_key: str`
- Uses instance: `self._alarms`, `self._lock`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `reset_all(self)` · line 270

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._alarms`, `self._last_seen`, `self._lock`, `self._pending_popups`, `self._shown_keys`

**Calls:**
- `self._last_seen.clear`
- `self._shown_keys.clear`
- `self._pending_popups.clear`

**Returns:** None

### File `Tool Steps/config.py`

**Layer:** Infrastructure — Tool Steps

**Module purpose:** *(no module docstring)*

#### Module-level functions *(no class)*

##### `_default_ini()` · line 14

**Does:** Internal helper.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `Path(__file__).resolve`
- `Path`

**Returns:** Path

##### `_solution_root()` · line 18

**Does:** Internal helper.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `Path(__file__).resolve`
- `Path`

**Returns:** Path

##### `bundled_results_structures_seed()` · line 36

**Does:** CSVs shipped next to the solution code (seed source for station catalogue).

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `_solution_root`

**Returns:** Path

##### `default_results_structures()` · line 41

**Does:** Runtime Results Structure catalogue under the station root on C:.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Path

##### `default_reports_folder()` · line 46

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Path

##### `default_sqlite_path()` · line 50

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Path

##### `default_report_templates()` · line 54

**Does:** HTML/PDF report templates under the station Reports folder.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Path

##### `ensure_station_root(root: Path | None = None)` · line 59

**Does:** Create ``C:\HIMA Prooftest Reporting Tool`` with the three required folders:

**Needs:**
- Parameters: `root: Path | None = None`

**Calls:**
- `Path`
- `path.mkdir`
- `log.warning`

**Returns:** Path

##### `_merge_tree(src: Path, dest: Path)` · line 83

**Does:** Copy all files from src into dest (newer/different size overwrites). Returns file count.

**Needs:**
- Parameters: `src: Path, dest: Path`

**Calls:**
- `src.is_dir`
- `dest.mkdir`
- `src.rglob`
- `path.is_dir`
- `(dest / path.relative_to(src)).mkdir`
- `path.relative_to`
- `path.is_file`
- `out.parent.mkdir`
- `out.exists`
- `path.stat`
- `out.stat`
- `shutil.copy2`
- `log.info`
- `log.warning`

**Returns:** int

##### `_move_or_merge_legacy_dir(legacy: Path, dest: Path, label: str)` · line 118

**Does:** Move the entire legacy folder into ``dest`` under the station root.

**Needs:**
- Parameters: `legacy: Path, dest: Path, label: str`

**Calls:**
- `legacy.is_dir`
- `legacy.resolve`
- `dest.resolve`
- `dest.exists`
- `dest.parent.mkdir`
- `shutil.move`
- `str`
- `log.info`
- `log.warning`
- `_merge_tree`
- `shutil.rmtree`

**Returns:** None

##### `migrate_legacy_station_data(reports: Path, results: Path, sqlite_path: Path)` · line 151

**Does:** Move pre-v1.46 C: locations into ``C:\HIMA Prooftest Reporting Tool``.

**Needs:**
- Parameters: `reports: Path, results: Path, sqlite_path: Path`

**Calls:**
- `_move_or_merge_legacy_dir`
- `_solution_root`
- `legacy_sqlite.is_file`
- `sqlite_path.exists`
- `sqlite_path.parent.mkdir`
- `shutil.copy2`
- `log.info`
- `log.warning`

**Returns:** None

##### `ensure_results_structures_catalogue(target: Path | None = None, seed: Path | None = None)` · line 169

**Does:** Ensure the station ``Results Structures`` folder exists and is seeded.

**Needs:**
- Parameters: `target: Path | None = None, seed: Path | None = None`

**Calls:**
- `Path`
- `default_results_structures`
- `bundled_results_structures_seed`
- `dest.mkdir`
- `log.warning`
- `src.is_dir`
- `src.resolve`
- `dest.resolve`
- `src.glob`
- `csv_path.relative_to`
- `out.exists`
- `out.parent.mkdir`
- `shutil.copy2`
- `log.info`

**Returns:** Path

##### `resolve_sql_templates(configured: Path | None = None)` · line 212

**Does:** Prefer configured path; else C:\ then Z:\ project templates (SPEC Step 1.3).

**Needs:**
- Parameters: `configured: Path | None = None`

**Calls:**
- `Path(configured).exists`
- `Path`
- `candidate.exists`

**Returns:** Path

#### Class `AppConfig` · line 224

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `load(cls, ini_path: Path | None = None)` · line 287

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `ini_path: Path | None = None`

**Calls:**
- `_default_ini`
- `path.resolve`
- `configparser.ConfigParser`
- `parser.read`
- `cls`
- `parser.has_section`
- `parser.getint`
- `parser.getboolean`
- `parser.get('Service', 'auto_start_trigger', fallback='logon').strip().lower`
- `parser.get('Service', 'auto_start_trigger', fallback='logon').strip`
- `parser.get`
- `Path`
- `parser.get('Paths', 'results_structures', fallback='').strip`
- `Path(rs).is_absolute`
- `default_results_structures`
- `parser.get('Paths', 'sql_templates', fallback='').strip`
- `cfg.sql_templates.is_absolute`
- `(_solution_root() / cfg.sql_templates).resolve`
- `_solution_root`
- `parser.get('Database', 'sqlite_path', fallback='').strip`
- `default_sqlite_path`
- `p.strip`
- `projects.split`
- `t.strip`
- `triggers.split`
- `… +20 more`

**Returns:** 'AppConfig'

##### `is_loopback_web_host(self)` · line 438

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.web_host`

**Calls:**
- `(self.web_host or '').strip().lower`
- `(self.web_host or '').strip`

**Returns:** bool

##### `apply_auth_bind_policy(self)` · line 442

**Does:** R4: warn or refuse non-loopback bind without auth.

**Needs:**
- Uses instance: `self.auth_bind_warning`, `self.is_loopback_web_host`, `self.require_auth_when_non_local`, `self.web_auth_enabled`, `self.web_host`

**Calls:**
- `logging.getLogger`
- `self.is_loopback_web_host`
- `log.error`
- `ValueError`
- `log.warning`

**Returns:** None

##### `normalize_report_paths(self)` · line 458

**Does:** Ensure report output defaults to the station reports folder on C:\.

**Needs:**
- Uses instance: `self.first_run_folder`, `self.report_mirror`, `self.report_output`

**Calls:**
- `str(self.report_output).strip`
- `str`
- `str(self.report_mirror).strip`

**Returns:** None

##### `ensure_data_dirs(self)` · line 465

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.first_run_folder`, `self.report_html_templates`, `self.report_output`, `self.results_structures`, `self.sqlite_path`

**Calls:**
- `ensure_station_root`
- `self.sqlite_path.parent.mkdir`
- `self.report_output.mkdir`
- `self.first_run_folder.mkdir`
- `self.report_html_templates.mkdir`
- `ensure_results_structures_catalogue`

**Returns:** None

### File `Tool Steps/results_csv.py`

**Layer:** Infrastructure — Tool Steps

**Module purpose:** *(no module docstring)*

#### Module-level functions *(no class)*

##### `structure_to_sql_table(type_name: str)` · line 81

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `type_name: str`

**Calls:**
- `type_name.replace`
- `name.replace`

**Returns:** str

##### `_parse_int(value: str)` · line 87

**Does:** Internal helper.

**Needs:**
- Parameters: `value: str`

**Calls:**
- `(value or '').strip`
- `int`

**Returns:** Optional[int]

##### `type_name_from_csv_path(csv_path: Path)` · line 97

**Does:** Resolve SILworX Results type name for a CSV file.

**Needs:**
- Parameters: `csv_path: Path`

**Calls:**
- `_FILENAME_TO_TYPE.get`
- `csv_path.name.lower`
- `csv_path.open`
- `csv.DictReader`
- `(row.get('Name') or '').strip`
- `row.get`
- `name.split`
- `log.warning`

**Returns:** str

##### `load_structure(csv_path: Path, type_name: str)` · line 117

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `csv_path: Path, type_name: str`

**Calls:**
- `ResultsStructure`
- `csv_path.open`
- `csv.DictReader`
- `(row.get('Name') or '').strip`
- `row.get`
- `(row.get('Data type') or '').strip`
- `structure.members.append`
- `ResultMember`
- `_parse_int`

**Returns:** ResultsStructure

##### `discover_results_csv_files(directory: Path)` · line 132

**Does:** All Results Structure CSV files in the catalogue folder (sorted).

**Needs:**
- Parameters: `directory: Path`

**Calls:**
- `directory.is_dir`
- `sorted`
- `directory.glob`
- `p.is_file`

**Returns:** List[Path]

##### `load_all_structures(directory: Path)` · line 139

**Does:** Load every ``*.csv`` under ``directory`` as a Results type.

**Needs:**
- Parameters: `directory: Path`

**Calls:**
- `discover_results_csv_files`
- `type_name_from_csv_path`
- `log.warning`
- `load_structure`
- `log.debug`
- `len`
- `directory.is_dir`
- `RESULTS_TYPE_FILES.items`
- `path.exists`

**Returns:** Dict[str, ResultsStructure]

##### `list_results_type_names(directory: Path)` · line 174

**Does:** Type names currently defined by CSVs in ``directory``.

**Needs:**
- Parameters: `directory: Path`

**Calls:**
- `tuple`
- `load_all_structures(directory).keys`
- `load_all_structures`

**Returns:** Tuple[str, ...]

##### `silworx_type_to_sql(dtype: str)` · line 179

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `dtype: str`

**Calls:**
- `dtype.startswith`

**Returns:** str

##### `member_to_column(name: str, type_name: str)` · line 198

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `name: str, type_name: str`

**Calls:**
- `short.startswith`
- `len`
- `re.sub('[^A-Za-z0-9]+', '_', short).strip`
- `re.sub`
- `col[0].isdigit`

**Returns:** str

##### `annexes_directory(results_structures: Path)` · line 211

**Does:** Folder holding nested SILworX type CSVs (ASCII arrays, Parameters structs).

**Needs:**
- Parameters: `results_structures: Path`

**Calls:**
- `Path`

**Returns:** Path

##### `load_annex_types(annexes_dir: Path)` · line 216

**Does:** Load ``X-HART_ASCII_32``, ``X-HART_*_Parameters``, etc. from ``Annexes/``.

**Needs:**
- Parameters: `annexes_dir: Path`

**Calls:**
- `annexes_dir.is_dir`
- `sorted`
- `annexes_dir.glob`
- `type_name_from_csv_path`
- `load_structure`
- `log.warning`

**Returns:** Dict[str, ResultsStructure]

##### `ascii_array_length(dtype: str, catalog: Optional[Dict[str, ResultsStructure]] = None)` · line 235

**Does:** Character count for ``X-HART_ASCII_N`` (and ``BYTE`` arrays in annex CSVs).

**Needs:**
- Parameters: `dtype: str, catalog: Optional[Dict[str, ResultsStructure]] = None`

**Calls:**
- `(dtype or '').strip`
- `_ASCII_LEN_RE.match`
- `int`
- `match.group`
- `member.name.split`
- `short.lower`

**Returns:** Optional[int]

##### `is_ascii_type(dtype: str)` · line 254

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `dtype: str`

**Calls:**
- `bool`
- `_ASCII_LEN_RE.match`
- `(dtype or '').strip`

**Returns:** bool

##### `is_parameters_type(dtype: str, catalog: Optional[Dict[str, ResultsStructure]] = None)` · line 258

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `dtype: str, catalog: Optional[Dict[str, ResultsStructure]] = None`

**Calls:**
- `(dtype or '').strip`
- `dtype.endswith`
- `bool`

**Returns:** bool

##### `member_dtype_map(structure: ResultsStructure)` · line 265

**Does:** Map member short name → SILworX data type.

**Needs:**
- Parameters: `structure: ResultsStructure`

**Calls:**
- `member.name.startswith`
- `len`
- `member.name.split`
- `_MEMBER_SHORT_ALIASES.get`

**Returns:** Dict[str, str]

##### `member_column_dtype_map(structure: ResultsStructure)` · line 278

**Does:** Map SQL snapshot column → SILworX ``Data type`` (includes annex nested types).

**Needs:**
- Parameters: `structure: ResultsStructure`

**Calls:**
- `member.name.startswith`
- `len`
- `member.name.split`
- `_MEMBER_SHORT_ALIASES.get`
- `member_to_column`

**Returns:** Dict[str, str]

#### Class `ResultMember` · line 49

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `ResultsStructure` · line 56

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `sql_table_name(self)` · line 62

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.type_name`

**Calls:**
- `structure_to_sql_table`

**Returns:** str

##### `member_short_names(self)` · line 65

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.members`, `self.type_name`

**Calls:**
- `m.name.startswith`
- `out.append`
- `len`
- `m.name.split`

**Returns:** List[str]

##### `has_running(self)` · line 77

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.members`

**Calls:**
- `any`
- `m.name.endswith`

**Returns:** bool

### File `Tool Steps/step01_setup.py`

**Layer:** Infrastructure — Tool Steps

**Module purpose:** First-run station setup — SPEC-001 Step 1.

On first run, create ``C:\HIMA Prooftest Reporting Tool`` with:
1. ``Database`` — SQL database files / SQLite + tables
2. ``HIMA Automated Prooftest Reports`` — generated PDF/HTML reports (+ Report Templates)
3. ``Results Structures`` — CSV type catalogue (baseline nine; new CSV = new type)

#### Module-level functions *(no class)*

##### `is_silworx_installed(programdata_root: Path)` · line 36

**Does:** True when SILworX appears installed on this station (SPEC Step 1.1).

**Needs:**
- Parameters: `programdata_root: Path`

**Calls:**
- `Path`
- `program_files.is_dir`
- `any`
- `program_files.glob`
- `programdata_root.is_dir`
- `programdata_root.glob`

**Returns:** bool

##### `detect_deployment_case(programdata_root: Path)` · line 46

**Does:** Always returns 1 (unified operating mode).

**Needs:**
- Parameters: `programdata_root: Path`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** int

##### `results_type_folder_name(results_type: str)` · line 57

**Does:** Filesystem-safe folder name for a Results type (`/` → `-` on Windows).

**Needs:**
- Parameters: `results_type: str`

**Calls:**
- `results_type.replace`

**Returns:** str

##### `sanitize_device_tag_for_path(device_tag: str)` · line 62

**Does:** Remove characters invalid in Windows folder names.

**Needs:**
- Parameters: `device_tag: str`

**Calls:**
- `_INVALID_PATH_CHARS.sub`
- `device_tag.strip`
- `cleaned.rstrip`

**Returns:** str

##### `_installation_marker(folder: Path)` · line 69

**Does:** Internal helper.

**Needs:**
- Parameters: `folder: Path`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** Path

##### `_load_installation(marker: Path)` · line 73

**Does:** Internal helper.

**Needs:**
- Parameters: `marker: Path`

**Calls:**
- `marker.is_file`
- `json.loads`
- `marker.read_text`

**Returns:** dict

##### `_write_installation(marker: Path, payload: dict)` · line 82

**Does:** Internal helper.

**Needs:**
- Parameters: `marker: Path, payload: dict`

**Calls:**
- `marker.parent.mkdir`
- `marker.write_text`
- `json.dumps`

**Returns:** None

##### `apply_deployment_case(config: AppConfig, marker: Path)` · line 87

**Does:** Force unified mode (deployment_case = 1).

**Needs:**
- Parameters: `config: AppConfig, marker: Path`

**Calls:**
- `_load_installation`
- `log.info`
- `is_silworx_installed`

**Returns:** bool

##### `create_results_type_folder_hierarchy(roots: Iterable[Path], alarms: AlarmManager, results_types: Optional[Sequence[str]] = None)` · line 106

**Does:** Create one subfolder per Results type under each report root (SPEC Step 1.2).

**Needs:**
- Parameters: `roots: Iterable[Path], alarms: AlarmManager, results_types: Optional[Sequence[str]] = None`

**Calls:**
- `tuple`
- `root.mkdir`
- `results_type_folder_name`
- `(root / folder_name).mkdir`
- `alarms.raise_alarm`
- `str`

**Returns:** None

##### `sync_results_type_folders_from_catalogue(config: AppConfig, alarms: AlarmManager, results_types: Optional[Sequence[str]] = None)` · line 138

**Does:** Ensure report roots have a folder for every Results Structure CSV type.

**Needs:**
- Parameters: `config: AppConfig, alarms: AlarmManager, results_types: Optional[Sequence[str]] = None`

**Calls:**
- `tuple`
- `list_results_type_names`
- `create_results_type_folder_hierarchy`
- `_report_roots`

**Returns:** None

##### `ensure_device_report_folders(config: AppConfig, device_tag: str, results_type: str, alarms: AlarmManager)` · line 154

**Does:** Create per-device subfolders under each report root (SPEC Step 1.2).

**Needs:**
- Parameters: `config: AppConfig, device_tag: str, results_type: str, alarms: AlarmManager`

**Calls:**
- `sanitize_device_tag_for_path`
- `results_type_folder_name`
- `target.mkdir`
- `alarms.raise_alarm`
- `str`

**Returns:** None

##### `sync_device_report_folders(config: AppConfig, devices: Iterable[Tuple[str, str]], alarms: AlarmManager)` · line 179

**Does:** Ensure report subfolders exist for all active devices.

**Needs:**
- Parameters: `config: AppConfig, devices: Iterable[Tuple[str, str]], alarms: AlarmManager`

**Calls:**
- `set`
- `seen.add`
- `ensure_device_report_folders`

**Returns:** None

##### `_report_roots(config: AppConfig)` · line 194

**Does:** Unique report roots (Step 1.2) — avoid duplicate folder trees.

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `path.resolve`
- `roots.append`

**Returns:** List[Path]

##### `persist_deployment_case(config: AppConfig, case = 1, reason = '')` · line 209

**Does:** Persist unified mode (always deployment_case = 1) to installation.json and solution.ini.

**Needs:**
- Parameters: `config: AppConfig, case = 1, reason = ''`

**Calls:**
- `_installation_marker`
- `_load_installation`
- `datetime.now(timezone.utc).isoformat`
- `datetime.now`
- `config.first_run_folder.mkdir`
- `_write_installation`
- `log.warning`
- `ini.is_file`
- `ini.read_text`
- `re.search`
- `re.sub`
- `ini.write_text`
- `log.info`

**Returns:** None

##### `ensure_desktop_ui_shortcut(config: AppConfig)` · line 251

**Does:** Ensure a Desktop shortcut ``HIMA Prooftest Report`` that opens the web UI.

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `Path(__file__).resolve`
- `Path`
- `open_script.is_file`
- `log.warning`
- `Path.home`
- `desktop.is_dir`
- `os.environ.get`
- `str`
- `lnk.is_file`
- `json.dumps`
- `subprocess.run`
- `log.info`
- `(completed.stderr or completed.stdout or '').strip`

**Returns:** None

##### `ensure_first_run(config: AppConfig, alarms: AlarmManager)` · line 322

**Does:** First-use station setup: unified mode, marker file, folder hierarchy.

**Needs:**
- Parameters: `config: AppConfig, alarms: AlarmManager`

**Calls:**
- `_installation_marker`
- `config.first_run_folder.mkdir`
- `apply_deployment_case`
- `list_results_type_names`
- `_report_roots`
- `create_results_type_folder_hierarchy`
- `_load_installation`
- `socket.gethostname`
- `datetime.now(timezone.utc).isoformat`
- `datetime.now`
- `len`
- `_write_installation`
- `ensure_desktop_ui_shortcut`
- `log.info`
- `alarms.raise_alarm`
- `str`

**Returns:** None

### File `Tool Steps/step03_device_list.py`

**Layer:** Infrastructure — Tool Steps

**Module purpose:** SPEC Step 3 — Device Prooftest Result List (G-22 data layer).

Every device-list update/refresh queries **SILworX API and X-OPC at the same
time**. API metadata (Results_Type, Configuration, Resource) is read from
structuretree + globalvariables **only when the user has a project open**
(attach; never ``open/local``). Each device is a **global variable** whose data
type is one of the Results structures defined by CSVs under
``Results Structures\`` (baseline nine + any new types). Operators do not
invent devices by editing CSV rows; they add a CSV only to register a **new
Results structure type**. OPC browse supplies server/prefix/PresentOnOpc and
devices that exist only on X-OPC. Realtime values are never read here — see
step05.

#### Module-level functions *(no class)*

##### `collect_devices_from_global_variables(client, known_types: Set[str])` · line 54

**Does:** Scan every Global Variables node in the open API project session.

**Needs:**
- Parameters: `client, known_types: Set[str]`

**Calls:**
- `client.get_structuretree`
- `client.find_all_globalvariable_nodes`
- `log.warning`
- `set`
- `client.list_top_level_globals`
- `seen_ids.add`
- `found.append`
- `ApiDiscoveredDevice`
- `log.info`

**Returns:** List[ApiDiscoveredDevice]

##### `try_discover_devices_via_api(case1_sync: Case1SyncTriggers, known_types: Set[str], alarms)` · line 110

**Does:** Attempt API-based discovery on every reachable SILworX API instance (G-21).

**Needs:**
- Parameters: `case1_sync: Case1SyncTriggers, known_types: Set[str], alarms`

**Calls:**
- `case1_sync.is_api_suspended`
- `log.info`
- `case1_sync.discover_api_instances`
- `log.warning`
- `case1_sync.api_session_for_port`
- `collect_devices_from_global_variables`
- `case1_sync.attached_project_name_for_port`
- `replace`
- `DeviceId(stamped.silworx_project, stamped.configuration, stamped.resource, stamped.device_tag).key`
- `DeviceId`
- `len`
- `list`
- `merged.values`

**Returns:** Optional[List[ApiDiscoveredDevice]]

##### `_device_list_source_label(api_ok: bool, opc_ok: bool)` · line 184

**Does:** Internal helper.

**Needs:**
- Parameters: `api_ok: bool, opc_ok: bool`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `_discover_opc_or_none(opc: OpcManager | None, structures: Dict[str, ResultsStructure], last_types_by_tag = None)` · line 192

**Does:** OPC browse for the parallel device-list update. None = browse failed / unavailable.

**Needs:**
- Parameters: `opc: OpcManager | None, structures: Dict[str, ResultsStructure], last_types_by_tag = None`

**Calls:**
- `discover_devices_from_opc`
- `log.warning`

**Returns:** Optional[List[OpcDiscoveredDevice]]

##### `apply_merged_device_list(config: AppConfig, db: Database, api_devices: Optional[List[ApiDiscoveredDevice]], opc_discovered: Optional[List[OpcDiscoveredDevice]], structures: Dict[str, ResultsStructure], opc: OpcManager | None = None)` · line 210

**Does:** Persist the union of simultaneous API and OPC discoveries.

**Needs:**
- Parameters: `config: AppConfig, db: Database, api_devices: Optional[List[ApiDiscoveredDevice]], opc_discovered: Optional[List[OpcDiscoveredDevice]], structures: Dict[str, ResultsStructure], opc: OpcManager | None = None`

**Calls:**
- `SilworxIdentity`
- `opc_obs.append`
- `OpcObservation`
- `list`
- `getattr`
- `opc.health_snapshot`
- `str(path).endswith`
- `str`
- `len`
- `r.get`
- `db.list_active_devices`
- `existing_rows.items`
- `Device`
- `DeviceId.from_key`
- `row.get`
- `CatalogMerger().merge`
- `CatalogMerger`
- `db.alarms.raise_alarm`
- `keep_opc_only_enabled`
- `bool`
- `str(getattr(device, 'project', '') or '').strip`
- `device.device_id.key`
- `db.upsert_device`
- `db.set_device_present_on_opc_by_id`
- `active.append`
- `… +7 more`

**Returns:** Tuple[List[str], str]

##### `apply_api_device_list(config: AppConfig, db: Database, devices: List[ApiDiscoveredDevice], opc: OpcManager | None, structures: Dict[str, ResultsStructure])` · line 375

**Does:** Persist API devices, merging a live OPC browse when the manager is available.

**Needs:**
- Parameters: `config: AppConfig, db: Database, devices: List[ApiDiscoveredDevice], opc: OpcManager | None, structures: Dict[str, ResultsStructure]`

**Calls:**
- `_discover_opc_or_none`
- `apply_merged_device_list`

**Returns:** List[str]

##### `sync_device_list_via_api(config: AppConfig, db: Database, structures: Dict[str, ResultsStructure], case1_sync: Case1SyncTriggers, opc: OpcManager | None = None)` · line 388

**Does:** Deprecated thin shim for older gate tests (neutral name).

**Needs:**
- Parameters: `config: AppConfig, db: Database, structures: Dict[str, ResultsStructure], case1_sync: Case1SyncTriggers, opc: OpcManager | None = None`

**Calls:**
- `set`
- `structures.keys`
- `db.list_active_devices`
- `str`
- `row.get`
- `str(row.get('results_type') or '').strip`
- `last_types.setdefault`
- `ThreadPoolExecutor`
- `pool.submit`
- `api_future.result`
- `opc_future.result`
- `apply_merged_device_list`

**Returns:** Tuple[List[str], str]

##### `sync_device_list_from_opc(config: AppConfig, db: Database, opc: OpcManager, structures: Dict[str, ResultsStructure])` · line 431

**Does:** Update device list by scanning X-OPC (when SILworX/API is unavailable).

**Needs:**
- Parameters: `config: AppConfig, db: Database, opc: OpcManager, structures: Dict[str, ResultsStructure]`

**Calls:**
- `_sync_from_opc_discovery`

**Returns:** List[str]

##### `_normalize_member(name: str)` · line 454

**Does:** Deprecated alias — use layers.domain.opc_discover.normalize_member.

**Needs:**
- Parameters: `name: str`

**Calls:**
- `normalize_member`

**Returns:** str

##### `_score_structure_match(member_names: Set[str], structure: ResultsStructure)` · line 461

**Does:** TEST-ONLY / legacy invent scorer.

**Needs:**
- Parameters: `member_names: Set[str], structure: ResultsStructure`

**Calls:**
- `score_structure_match`
- `set`
- `structure.member_short_names`

**Returns:** int

##### `_member_names_under_prefix(tags: List[str], prefix: str)` · line 473

**Does:** Internal helper.

**Needs:**
- Parameters: `tags: List[str], prefix: str`

**Calls:**
- `members_under_prefix`

**Returns:** Set[str]

##### `_discover_on_server_invent_legacy(server: str, tags: List[str], structures: Dict[str, ResultsStructure])` · line 479

**Does:** LEGACY invent-as-identity (test-only). Prefer discover_devices_from_opc shaped path.

**Needs:**
- Parameters: `server: str, tags: List[str], structures: Dict[str, ResultsStructure]`

**Calls:**
- `set`
- `sorted`
- `t.endswith`
- `len`
- `seen_prefixes.add`
- `prefix.split`
- `_member_names_under_prefix`
- `structures.items`
- `_score_structure_match`
- `found.append`

**Returns:** List[Tuple[str, str, str, str]]

##### `discover_devices_from_opc(opc: OpcManager, structures: Dict[str, ResultsStructure], last_types_by_tag = None)` · line 508

**Does:** Shaped OPC discover (production rule).

**Needs:**
- Parameters: `opc: OpcManager, structures: Dict[str, ResultsStructure], last_types_by_tag = None`

**Calls:**
- `opc.discover_servers`
- `opc.list_tags_all_servers`
- `log.info`
- `len`
- `discover_shaped_from_tag_lists`
- `str`
- `list`
- `(all_tags or {}).items`
- `type_members_from_structures`

**Returns:** List[Tuple[str, str, str, str]]

##### `_sync_from_opc_discovery(db: Database, opc: OpcManager | None, structures: Dict[str, ResultsStructure], config = None, alarm_step, empty_message)` · line 542

**Does:** Internal helper.

**Needs:**
- Parameters: `db: Database, opc: OpcManager | None, structures: Dict[str, ResultsStructure], config = None, alarm_step, empty_message`

**Calls:**
- `db.alarms.raise_alarm`
- `db.list_active_devices`
- `str`
- `row.get`
- `str(row.get('results_type') or '').strip`
- `last_types.setdefault`
- `discover_devices_from_opc`
- `active.append`
- `folder_pairs.append`
- `db.upsert_device`
- `db.reconcile_device_list`
- `db.set_present_on_opc`
- `set`
- `sync_device_report_folders`
- `log.info`
- `len`
- `', '.join`

**Returns:** List[str]

#### Class `ApiDiscoveredDevice` · line 43

**Inherits:** `—`

**Purpose:** One Prooftest device row from SILworX global variables.

*(no methods)*

### File `Tool Steps/step04_opc.py`

**Layer:** Infrastructure — Tool Steps

**Module purpose:** SPEC Step 4 — Realtime OPC (uses annex_opc).

*(empty module)*

---

## Adapter — OPC

### File `Annex codes/OPC/__init__.py`

**Layer:** Adapter — OPC

**Module purpose:** *(no module docstring)*

*(empty module)*

### File `Annex codes/OPC/annex_opc.py`

**Layer:** Adapter — OPC

**Module purpose:** Annex — X-OPC DA connexion and device binding.

#### Module-level functions *(no class)*

##### `_is_com_reuse_error(exc: BaseException)` · line 34

**Does:** Internal helper.

**Needs:**
- Parameters: `exc: BaseException`

**Calls:**
- `str(exc).lower`
- `str`
- `any`

**Returns:** bool

##### `_is_browse_retryable(exc: BaseException)` · line 39

**Does:** Transient OpenOPC/COM browse failures worth one reconnect + retry.

**Needs:**
- Parameters: `exc: BaseException`

**Calls:**
- `_is_com_reuse_error`
- `str(exc).lower`
- `str`

**Returns:** bool

##### `_load_connection_opc()` · line 47

**Does:** Internal helper.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `path.is_file`
- `ImportError`
- `importlib.util.spec_from_file_location`
- `importlib.util.module_from_spec`
- `spec.loader.exec_module`

**Returns:** `module` (inferred)

#### Class `OpcServerInfo` · line 68

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `DeviceOpcBinding` · line 79

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `OpcManager` · line 86

**Inherits:** `—`

**Purpose:** Thread-safe OPC access — one client per X-OPC server.

##### `__init__(self, server_filters: Sequence[str])` · line 89

**Does:** Internal helper.

**Needs:**
- Parameters: `server_filters: Sequence[str]`
- Uses instance: `self._browse_failed`, `self._last_servers`, `self._last_tag_counts`, `self._live_ok`, `self._live_quality`, `self._lock`, `self._tags_cache`, `self._thread_clients`, `self.server_filters`

**Calls:**
- `list`
- `threading.Lock`

**Returns:** None

##### `_match_server(self, name: str)` · line 100

**Does:** Keep HIMA X-OPC DA ProgIDs.

**Needs:**
- Parameters: `name: str`
- Uses instance: `self.server_filters`

**Calls:**
- `(name or '').strip`
- `prog_id.upper().startswith`
- `prog_id.upper`
- `fnmatch.fnmatch`
- `prog_id.lower`
- `pattern.lower`

**Returns:** bool

##### `discover_servers(self)` · line 119

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._last_servers`, `self._match_server`

**Calls:**
- `log.info`
- `_load_connection_opc`
- `opc_mod._import_openopc`
- `OpenOPC.client`
- `list`
- `opc.servers`
- `log.exception`
- `opc.close`
- `self._match_server`
- `len`
- `', '.join`
- `opc_mod.discover_opc_server`
- `sorted`

**Returns:** List[str]

##### `device_prefix_candidates(self, device_tag: str, item_prefix: Optional[str] = None)` · line 149

**Does:** Build OPC item prefixes for a device TAG (known bound prefix first).

**Needs:**
- Parameters: `device_tag: str, item_prefix: Optional[str] = None`

**Calls:**
- `prefixes.append`
- `set`
- `seen.add`
- `unique.append`

**Returns:** List[str]

##### `_get_client(self, server_name: str)` · line 163

**Does:** Return an OPC client created on *this* thread (COM STA / OpenOPC).

**Needs:**
- Parameters: `server_name: str`
- Uses instance: `self._lock`, `self._thread_clients`

**Calls:**
- `_load_connection_opc`
- `threading.get_ident`
- `self._thread_clients.get(tid, {}).get`
- `self._thread_clients.get`
- `XOpcDaClient`
- `client.connect`
- `self._thread_clients.setdefault`
- `client.disconnect`

**Returns:** `client` (inferred)

##### `_drop_thread_client(self, server_name: str)` · line 188

**Does:** Internal helper.

**Needs:**
- Parameters: `server_name: str`
- Uses instance: `self._lock`, `self._thread_clients`

**Calls:**
- `threading.get_ident`
- `self._thread_clients.get(tid, {}).pop`
- `self._thread_clients.get`
- `client.disconnect`

**Returns:** None

##### `list_all_tags(self, server_name: str, branch: Optional[str] = None)` · line 199

**Does:** Browse OPC item IDs on one server.

**Needs:**
- Parameters: `server_name: str, branch: Optional[str] = None`
- Uses instance: `self._browse_failed`, `self._drop_thread_client`, `self._get_client`, `self._last_tag_counts`, `self._live_ok`, `self._live_quality`, `self._lock`, `self._sample_live_quality`, `self._tags_cache`

**Calls:**
- `range`
- `set`
- `self._get_client`
- `client.list_tags`
- `merged.update`
- `log.warning`
- `sorted`
- `_is_browse_retryable`
- `self._drop_thread_client`
- `len`
- `self._live_ok.pop`
- `self._live_quality.pop`
- `self._sample_live_quality`

**Returns:** List[str]

##### `_sample_live_quality(self, server_name: str, tags: Sequence[str])` · line 266

**Does:** One cheap Running read — distinguishes address-space browse from live I/O.

**Needs:**
- Parameters: `server_name: str, tags: Sequence[str]`
- Uses instance: `self._get_client`, `self._live_ok`, `self._live_quality`, `self._lock`

**Calls:**
- `next`
- `str(t).endswith`
- `str`
- `self._live_ok.pop`
- `self._get_client`
- `client.read_tag`
- `getattr`
- `quality.lower`
- `log.warning`
- `len`

**Returns:** None

##### `server_live_ok(self, server_name: str)` · line 297

**Does:** True/False when sampled; None if this ProgID was never live-sampled.

**Needs:**
- Parameters: `server_name: str`
- Uses instance: `self._live_ok`, `self._lock`

**Calls:**
- `bool`

**Returns:** Optional[bool]

##### `mark_live_quality(self, server_name: str, ok: bool, quality: str = '')` · line 304

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server_name: str, ok: bool, quality: str = ''`
- Uses instance: `self._live_ok`, `self._live_quality`, `self._lock`

**Calls:**
- `bool`

**Returns:** None

##### `recheck_server_live(self, server_name: str, running_item: Optional[str] = None)` · line 309

**Does:** Re-read one Running item so monitoring can resume after Bad quality.

**Needs:**
- Parameters: `server_name: str, running_item: Optional[str] = None`
- Uses instance: `self._drop_thread_client`, `self._get_client`, `self._lock`, `self._tags_cache`, `self.mark_live_quality`, `self.server_live_ok`

**Calls:**
- `str(running_item or '').strip`
- `str`
- `self._tags_cache.items`
- `key.split`
- `next`
- `str(t).endswith`
- `self.server_live_ok`
- `range`
- `self._drop_thread_client`
- `self._get_client`
- `client.read_tag`
- `getattr`
- `quality.lower`
- `self.mark_live_quality`
- `log.info`
- `_is_browse_retryable`

**Returns:** Optional[bool]

##### `list_tags_all_servers(self, servers: Optional[Sequence[str]] = None)` · line 347

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `servers: Optional[Sequence[str]] = None`
- Uses instance: `self._browse_failed`, `self._last_tag_counts`, `self._lock`, `self.discover_servers`, `self.list_all_tags`

**Calls:**
- `list`
- `self.discover_servers`
- `self._browse_failed.items`
- `dict`
- `sorted`
- `counts.get`
- `self.list_all_tags`
- `log.warning`
- `result.get`

**Returns:** Dict[str, List[str]]

##### `resolve_device_binding(self, device_tag: str, item_prefix: Optional[str], servers: Optional[Sequence[str]] = None)` · line 380

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, item_prefix: Optional[str], servers: Optional[Sequence[str]] = None`
- Uses instance: `self.device_prefix_candidates`, `self.discover_servers`, `self.find_running_tag`, `self.list_all_tags`

**Calls:**
- `list`
- `self.discover_servers`
- `self.list_all_tags`
- `self.device_prefix_candidates`
- `self.find_running_tag`
- `DeviceOpcBinding`

**Returns:** Optional[DeviceOpcBinding]

##### `invalidate_tag_cache(self)` · line 402

**Does:** Drop browsed tag lists so the next refresh re-browses (keep live clients).

**Needs:**
- Uses instance: `self._browse_failed`, `self._live_ok`, `self._live_quality`, `self._lock`, `self._tags_cache`

**Calls:**
- `self._tags_cache.clear`
- `self._browse_failed.clear`
- `self._live_ok.clear`
- `self._live_quality.clear`

**Returns:** None

##### `invalidate_cache(self)` · line 410

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._browse_failed`, `self._live_ok`, `self._live_quality`, `self._lock`, `self._tags_cache`, `self._thread_clients`

**Calls:**
- `self._lock.acquire`
- `log.warning`
- `self._tags_cache.clear`
- `self._browse_failed.clear`
- `self._live_ok.clear`
- `self._live_quality.clear`
- `self._thread_clients.values`
- `bucket.values`
- `client.disconnect`
- `self._thread_clients.clear`
- `self._lock.release`

**Returns:** None

##### `read_values(self, server_name: str, item_ids: Sequence[str])` · line 433

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `server_name: str, item_ids: Sequence[str]`
- Uses instance: `self._drop_thread_client`, `self._get_client`

**Calls:**
- `range`
- `self._get_client`
- `client.read_tags`
- `list`
- `_is_com_reuse_error`
- `log.warning`
- `self._drop_thread_client`

**Returns:** Dict[str, Tuple[Any, str]]

##### `find_running_tag(self, tags: Sequence[str], device_prefix: str)` · line 451

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `tags: Sequence[str], device_prefix: str`

**Calls:**
- `device_prefix.rstrip`
- `t.endswith`

**Returns:** Optional[str]

##### `build_member_item_ids(self, tags: Sequence[str], base_prefix: str, member_names: Sequence[str])` · line 461

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `tags: Sequence[str], base_prefix: str, member_names: Sequence[str]`

**Calls:**
- `base_prefix.rstrip`
- `list`
- `member.replace`
- `any`
- `t.startswith`
- `member.replace(' ', '').lower`
- `len`
- `remainder.split`
- `top.replace(' ', '').lower`
- `top.replace`

**Returns:** Dict[str, str]

##### `_cached_tag_count(self, server_name: str)` · line 493

**Does:** Internal helper.

**Needs:**
- Parameters: `server_name: str`
- Uses instance: `self._lock`, `self._tags_cache`

**Calls:**
- `self._tags_cache.items`
- `key.split`
- `max`
- `len`

**Returns:** int

##### `find_running_path(self, server: str, device_tag: str)` · line 501

**Does:** Return ``…{TAG}.Running`` or ``…Global Vars.{TAG}.Running`` on ``server``.

**Needs:**
- Parameters: `server: str, device_tag: str`
- Uses instance: `self._lock`, `self._tags_cache`, `self.list_all_tags`

**Calls:**
- `str(device_tag or '').strip`
- `str`
- `self._tags_cache.items`
- `key.split`
- `list`
- `self.list_all_tags`
- `log.debug`
- `t.endswith`
- `sorted`

**Returns:** Optional[str]

##### `health_snapshot(self)` · line 537

**Does:** Non-blocking OPC summary from the last discovery/browse cache (Gate 13).

**Needs:**
- Uses instance: `self._browse_failed`, `self._last_servers`, `self._last_tag_counts`, `self._live_ok`, `self._live_quality`, `self._lock`, `self._tags_cache`, `self._thread_clients`

**Calls:**
- `self._lock.acquire`
- `list`
- `getattr`
- `dict`
- `OpcServerInfo`
- `int`
- `counts.get`
- `bool`
- `failed.get`
- `live_ok.get`
- `str`
- `live_q.get`
- `set`
- `self._thread_clients.values`
- `client_names.update`
- `bucket.keys`
- `self._tags_cache.items`
- `key.split`
- `max`
- `tag_counts.get`
- `len`
- `self._lock.release`
- `browse_failed.get`
- `out.append`
- `live_ok_map.get`
- `… +1 more`

**Returns:** List[OpcServerInfo]

##### `server_status(self)` · line 597

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.discover_servers`, `self.list_all_tags`

**Calls:**
- `self.discover_servers`
- `self.list_all_tags`
- `out.append`
- `OpcServerInfo`
- `len`
- `log.warning`

**Returns:** List[OpcServerInfo]

### File `Annex codes/OPC/connection_opc.py`

**Layer:** Adapter — OPC

**Module purpose:** OPC Classic DA client for HIMA X-OPC DA (in-tree copy for Current).

Canonical path (production):
    HIMA-Prooftest-Solution-Current/Annex codes/OPC/connection_opc.py

Loaded only by annex_opc.py from this same folder — not from Codes/Report-Tool.

Matches the server shown in Softing OPC Toolbox: HIMA X-OPC DA (X_OPC-25138)
with items under branch OTS MIRO_T2_1 (e.g. 200S2503-I11_IN).

Installation (Windows, 32-bit Python recommended for OPC DA):
    pip install OpenOPC-Python3x pywin32

Usage (from this folder, optional probe):
    python connection_opc.py --list-only
    python connection_opc.py --discover-only

#### Module-level functions *(no class)*

##### `_import_openopc()` · line 61

**Does:** Import OpenOPC; raise a clear error if the package is missing.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `SystemExit`

**Returns:** `OpenOPC` (inferred)

##### `_import_pywintypes()` · line 75

**Does:** Internal helper.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** `pywintypes` (inferred)

##### `_local_hosts()` · line 84

**Does:** Internal helper.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `frozenset`

**Returns:** frozenset[str]

##### `build_item_id(tag: str, branch: str = OPC_ITEM_BRANCH)` · line 88

**Does:** Return a fully qualified item ID (branch.tag...) for X_OPC-25138.

**Needs:**
- Parameters: `tag: str, branch: str = OPC_ITEM_BRANCH`

**Calls:**
- `tag.strip`
- `ValueError`
- `tag.startswith`

**Returns:** str

##### `resolve_readable_item_id(item_id: str, tags: Sequence[str])` · line 98

**Does:** Map a block name to a readable leaf tag when the server uses nested items.
E.g. OTS MIRO_T2_1.200S2503-I11_IN -> OTS MIRO_T2_1.200S2503-I11_IN.IN1

**Needs:**
- Parameters: `item_id: str, tags: Sequence[str]`

**Calls:**
- `set`
- `item_id.endswith`
- `sorted`
- `t.startswith`
- `candidate.endswith`

**Returns:** str

##### `discover_opc_server(host: str = OPC_HOST, match: str = OPC_SERVER_ID)` · line 119

**Does:** Find a registered HIMA X-OPC DA ProgID for OpenOPC connect().

**Needs:**
- Parameters: `host: str = OPC_HOST, match: str = OPC_SERVER_ID`

**Calls:**
- `_import_openopc`
- `OpenOPC.client`
- `host.lower`
- `_local_hosts`
- `opc.servers`
- `str(name).upper().startswith`
- `str(name).upper`
- `str`
- `match.lower`
- `name.lower`
- `str(name).lower`
- `opc.close`

**Returns:** Optional[str]

##### `connect_server_candidates(prog_id: Optional[str] = None, discovered: Optional[str] = None)` · line 156

**Does:** Semicolon-separated list for OpenOPC connect() — tries each until one works.

**Needs:**
- Parameters: `prog_id: Optional[str] = None, discovered: Optional[str] = None`

**Calls:**
- `ordered.append`
- `';'.join`

**Returns:** str

##### `_com_error_message(exc: BaseException)` · line 186

**Does:** Turn a pywin32 COM error into a short, actionable message.

**Needs:**
- Parameters: `exc: BaseException`

**Calls:**
- `_import_pywintypes`
- `isinstance`
- `len`
- `str`
- `hints.get`

**Returns:** str

##### `retry(operation_name: str, func, max_attempts = MAX_RETRIES, initial_delay = RETRY_DELAY_SEC, backoff = RETRY_BACKOFF, retryable_exceptions = (Exception,))` · line 210

**Does:** Call func() with exponential backoff; re-raise on final failure.

**Needs:**
- Parameters: `operation_name: str, func, max_attempts = MAX_RETRIES, initial_delay = RETRY_DELAY_SEC, backoff = RETRY_BACKOFF, retryable_exceptions = (Exception,)`

**Calls:**
- `range`
- `func`
- `log.warning`
- `_com_error_message`
- `time.sleep`

**Returns:** `func()` (inferred)

##### `_parse_read_result(tag: str, result: Any)` · line 393

**Does:** Internal helper.

**Needs:**
- Parameters: `tag: str, result: Any`

**Calls:**
- `ValueError`
- `isinstance`
- `len`
- `TagReadResult`
- `str`

**Returns:** TagReadResult

##### `_parse_multi_read(requested: Sequence[str], raw: Any)` · line 407

**Does:** Internal helper.

**Needs:**
- Parameters: `requested: Sequence[str], raw: Any`

**Calls:**
- `isinstance`
- `_parse_read_result`
- `enumerate`
- `len`
- `out.append`
- `TagReadResult`
- `str`

**Returns:** list[TagReadResult]

##### `_tag_exists(tags: Iterable[str], tag: str)` · line 427

**Does:** Case-sensitive exact match; some servers use hierarchical names.

**Needs:**
- Parameters: `tags: Iterable[str], tag: str`

**Calls:**
- `set`
- `any`
- `t.endswith`

**Returns:** bool

##### `run(prog_id: str, host: str, tag: Optional[str], branch: str, list_only: bool, discover_only: bool, max_display: int)` · line 439

**Does:** Main workflow: connect -> list tags -> optionally read one tag -> disconnect.
Returns process exit code (0 = success).

**Needs:**
- Parameters: `prog_id: str, host: str, tag: Optional[str], branch: str, list_only: bool, discover_only: bool, max_display: int`

**Calls:**
- `_import_openopc`
- `OpenOPC.client`
- `host.lower`
- `_local_hosts`
- `opc.servers`
- `print`
- `OPC_SERVER_ID.lower`
- `name.lower`
- `any`
- `s.lower`
- `log.warning`
- `opc.close`
- `XOpcDaClient`
- `client.connect`
- `log.info`
- `client.list_tags`
- `len`
- `build_item_id`
- `resolve_readable_item_id`
- `_tag_exists`
- `client.read_tag`
- `log.error`
- `_com_error_message`
- `client.disconnect`

**Returns:** int

##### `parse_args(argv: Optional[Sequence[str]] = None)` · line 543

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `argv: Optional[Sequence[str]] = None`

**Calls:**
- `argparse.ArgumentParser`
- `parser.add_argument`
- `parser.parse_args`

**Returns:** argparse.Namespace

#### Class `TagReadResult` · line 172

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `is_good(self)` · line 179

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.quality`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

#### Class `XOpcDaClient` · line 246

**Inherits:** `—`

**Purpose:** OpenOPC wrapper for HIMA X-OPC DA (X_OPC-25138).

##### `__init__(self, prog_id: str = OPC_SERVER_PROG_ID, host: str = OPC_HOST, auto_discover = True)` · line 249

**Does:** Internal helper.

**Needs:**
- Parameters: `prog_id: str = OPC_SERVER_PROG_ID, host: str = OPC_HOST, auto_discover = True`
- Uses instance: `self._OpenOPC`, `self._opc`, `self.auto_discover`, `self.connected_server`, `self.host`, `self.prog_id`

**Calls:**
- `_import_openopc`

**Returns:** `None` (implicit)

##### `connected(self)` · line 265

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._opc`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** bool

##### `connect(self)` · line 268

**Does:** Connect to HIMA X-OPC DA (X_OPC-25138), with discovery fallback.

**Needs:**
- Uses instance: `self.auto_discover`, `self.connected`, `self.host`, `self.prog_id`

**Calls:**
- `discover_opc_server`
- `log.info`
- `log.warning`
- `', '.join`
- `connect_server_candidates`
- `retry`

**Returns:** None

##### `disconnect(self)` · line 302

**Does:** Close the OPC session; safe to call multiple times.

**Needs:**
- Uses instance: `self._opc`

**Calls:**
- `self._opc.close`
- `log.info`
- `log.warning`
- `_com_error_message`

**Returns:** None

##### `list_tags(self, filter_pattern: str = '*', branch = None)` · line 314

**Does:** Browse item IDs. Full tree when ``branch`` is None; otherwise ``branch.*``.

**Needs:**
- Parameters: `filter_pattern: str = '*', branch = None`
- Uses instance: `self.connected`

**Calls:**
- `RuntimeError`
- `retry`
- `sorted`
- `set`

**Returns:** list[str]

##### `read_tag(self, tag: str)` · line 346

**Does:** Read one tag. OpenOPC returns (value, quality, timestamp) for a single item.

**Needs:**
- Parameters: `tag: str`
- Uses instance: `self.connected`

**Calls:**
- `RuntimeError`
- `retry`

**Returns:** TagReadResult

##### `read_tags(self, tags: Sequence[str])` · line 362

**Does:** Read multiple tags in one call (more efficient than repeated single reads).

**Needs:**
- Parameters: `tags: Sequence[str]`
- Uses instance: `self.connected`

**Calls:**
- `RuntimeError`
- `retry`

**Returns:** list[TagReadResult]

##### `__enter__(self)` · line 378

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.connect`

**Calls:**
- `self.connect`

**Returns:** 'XOpcDaClient'

##### `__exit__(self, exc_type, exc, tb)` · line 382

**Does:** Internal helper.

**Needs:**
- Parameters: `exc_type, exc, tb`
- Uses instance: `self.disconnect`

**Calls:**
- `self.disconnect`

**Returns:** None

### File `Annex codes/OPC/opc_snapshot.py`

**Layer:** Adapter — OPC

**Module purpose:** Expand HIMA X-OPC nested values using SILworX Results Structure data types.

Annex CSVs under ``Results Structures/Annexes/`` define how to interpret OPC
folders:

- ``X-HART_ASCII_32`` (etc.) → BYTE char-array decoded to text
- ``X-HART_*_Parameters`` → nested structure members (UINT, REAL, ASCII, …)

#### Module-level functions *(no class)*

##### `quality_is_good(quality: Any)` · line 68

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `quality: Any`

**Calls:**
- `str(quality or '').strip().lower`
- `str(quality or '').strip`
- `str`

**Returns:** bool

##### `value_is_empty(value: Any)` · line 72

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `value: Any`

**Calls:**
- `isinstance`
- `math.isnan`
- `value.strip`

**Returns:** bool

##### `decode_char_codes(codes: Sequence[Any], max_len = None)` · line 82

**Does:** Decode OPC BYTE/USINT char-array cells into a text string.

**Needs:**
- Parameters: `codes: Sequence[Any], max_len = None`

**Calls:**
- `len`
- `isinstance`
- `ord`
- `int`
- `chars.append`
- `chr`
- `''.join(chars).rstrip('\x00').strip`
- `''.join(chars).rstrip`
- `''.join`

**Returns:** str

##### `indexed_children(tags: Sequence[str], folder_prefix: str)` · line 106

**Does:** Map array index → full item id for ``…Name[i]`` leaves under a folder.

**Needs:**
- Parameters: `tags: Sequence[str], folder_prefix: str`

**Calls:**
- `folder_prefix.rstrip`
- `item.startswith`
- `_ARRAY_INDEX_RE.search`
- `int`
- `match.group`

**Returns:** Dict[int, str]

##### `_folder_candidates(base_path: str, member: str)` · line 120

**Does:** Internal helper.

**Needs:**
- Parameters: `base_path: str, member: str`

**Calls:**
- `base_path.rstrip`
- `member.replace`

**Returns:** List[str]

##### `_read_scalar_leaf(tags: Sequence[str], folder_path: str, read_values: ReadValuesFn)` · line 125

**Does:** Read one scalar OPC item under ``folder_path`` (leaf or first scalar child).

**Needs:**
- Parameters: `tags: Sequence[str], folder_path: str, read_values: ReadValuesFn`

**Calls:**
- `folder_path.rstrip`
- `read_values([folder_path]).get`
- `read_values`
- `quality_is_good`
- `indexed_children`
- `t.startswith`
- `sorted`
- `read_values([leaf]).get`
- `value_is_empty`

**Returns:** Any

##### `decode_ascii_at_path(tags: Sequence[str], folder_path: str, read_values: ReadValuesFn, max_len = None)` · line 151

**Does:** Decode a typed ``X-HART_ASCII_N`` folder at ``folder_path``.

**Needs:**
- Parameters: `tags: Sequence[str], folder_path: str, read_values: ReadValuesFn, max_len = None`

**Calls:**
- `_folder_candidates`
- `folder_path.split`
- `indexed_children`
- `sorted`
- `read_values`
- `values.get`
- `quality_is_good`
- `codes.append`
- `decode_char_codes`

**Returns:** Optional[str]

##### `decode_ascii_under_member(tags: Sequence[str], prefix: str, member: str, read_values: ReadValuesFn, dtype = '', type_catalog = None)` · line 205

**Does:** Decode ``prefix.Member`` when the SILworX type is ``X-HART_ASCII_*``.

**Needs:**
- Parameters: `tags: Sequence[str], prefix: str, member: str, read_values: ReadValuesFn, dtype = '', type_catalog = None`

**Calls:**
- `ascii_array_length`
- `_folder_candidates`
- `decode_ascii_at_path`

**Returns:** Optional[str]

##### `report_key_for_param_member(param_type: str, member_short: str)` · line 225

**Does:** Snapshot / report placeholder key for one Parameters structure member.

**Needs:**
- Parameters: `param_type: str, member_short: str`

**Calls:**
- `_PARAM_REPORT_ALIASES.get`
- `member_short.lower`
- `member_to_column`

**Returns:** str

##### `read_typed_opc_value(dtype: str, folder_path: str, tags: Sequence[str], read_values: ReadValuesFn, type_catalog: Dict[str, 'ResultsStructure'])` · line 235

**Does:** Read one OPC subtree according to the SILworX ``Data type`` from the CSV.

**Needs:**
- Parameters: `dtype: str, folder_path: str, tags: Sequence[str], read_values: ReadValuesFn, type_catalog: Dict[str, 'ResultsStructure']`

**Calls:**
- `(dtype or '').strip`
- `_read_scalar_leaf`
- `is_ascii_type`
- `ascii_array_length`
- `decode_ascii_at_path`
- `is_parameters_type`
- `type_catalog.get`
- `expand_structure_at_path`
- `dtype.upper`
- `dtype_u.startswith`

**Returns:** Any

##### `expand_structure_at_path(tags: Sequence[str], folder_path: str, structure: 'ResultsStructure', read_values: ReadValuesFn, type_catalog: Dict[str, 'ResultsStructure'])` · line 272

**Does:** Flatten a nested SILworX structure (e.g. ``X-HART_*_Parameters``) from OPC.

**Needs:**
- Parameters: `tags: Sequence[str], folder_path: str, structure: 'ResultsStructure', read_values: ReadValuesFn, type_catalog: Dict[str, 'ResultsStructure']`

**Calls:**
- `member_dtype_map`
- `folder_path.rstrip`
- `dtypes.items`
- `member_short.lower`
- `read_typed_opc_value`
- `value_is_empty`
- `member_to_column`
- `report_key_for_param_member`

**Returns:** Dict[str, Any]

##### `expand_parameters_branch(tags: Sequence[str], prefix: str, branch_name: str, read_values: ReadValuesFn, parameters_type = '', type_catalog = None)` · line 307

**Does:** Flatten ``prefix.{branch_name}.*`` using the Parameters SILworX type when known.

**Needs:**
- Parameters: `tags: Sequence[str], prefix: str, branch_name: str, read_values: ReadValuesFn, parameters_type = '', type_catalog = None`

**Calls:**
- `prefix.rstrip`
- `expand_structure_at_path`
- `item.startswith`
- `len`
- `remainder.split('.', 1)[0].strip`
- `remainder.split`
- `groups.setdefault(group, []).append`
- `groups.setdefault`
- `groups.items`
- `report_key_for_param_member`
- `int`
- `m.group`
- `_ARRAY_INDEX_RE.search`
- `sorted`
- `read_values`
- `values.get`
- `quality_is_good`
- `codes.append`
- `decode_char_codes`
- `read_values([leaf]).get`
- `value_is_empty`

**Returns:** Dict[str, Any]

##### `enrich_snapshot_from_opc(tags, prefix, member_types, snapshot, notes, read_values, type_catalog = None)` · line 365

**Does:** Fill typed members that OPC exposes as folders (ASCII arrays, Parameters).

**Needs:**
- Parameters: `tags, prefix, member_types, snapshot, notes, read_values, type_catalog = None`

**Calls:**
- `dict`
- `list`
- `member_types.items`
- `column.replace`
- `prefix.rstrip`
- `is_ascii_type`
- `decode_ascii_under_member`
- `_clear_note`
- `is_parameters_type`
- `expand_parameters_branch`
- `expanded.items`
- `value_is_empty`
- `out.get`
- `'; '.join`
- `member_types.get`
- `_prune_recovered_notes`

**Returns:** Tuple[Dict[str, Any], List[str]]

##### `_prune_recovered_notes(notes: List[str], snapshot: Dict[str, Any])` · line 471

**Does:** Internal helper.

**Needs:**
- Parameters: `notes: List[str], snapshot: Dict[str, Any]`

**Calls:**
- `str(note).split(':', 1)[0].strip`
- `str(note).split`
- `str`
- `head.replace`
- `value_is_empty`
- `snapshot.get`
- `col.lower().startswith`
- `col.lower`
- `any`
- `kept.append`

**Returns:** List[str]

##### `quality_note_for(member_key: str, notes: Sequence[str])` · line 493

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `member_key: str, notes: Sequence[str]`

**Calls:**
- `member_key.lower().replace`
- `member_key.lower`
- `any`
- `str(n).lower().replace(' ', '_').startswith`
- `str(n).lower().replace`
- `str(n).lower`
- `str`

**Returns:** bool

---

## Adapter — SILworX API

### File `Annex codes/API connexion/annex_api_connexion.py`

**Layer:** Adapter — SILworX API

**Module purpose:** Annex — SILworX API connexion (HTTPS client + plugin WebSocket session bridge).

#### Module-level functions *(no class)*

##### `is_unusable_gui_session_error(exc: BaseException)` · line 62

**Does:** True when SILworX rejected the plugin ``user_session_id`` (stale or no project).

**Needs:**
- Parameters: `exc: BaseException`

**Calls:**
- `str(exc).lower`
- `str`
- `any`

**Returns:** bool

##### `resolve_api_server_cert(programdata_root: Path, explicit: Optional[Path] = None)` · line 95

**Does:** Locate `settings/api_cert.pem` for server TLS verification.

**Needs:**
- Parameters: `programdata_root: Path, explicit: Optional[Path] = None`

**Calls:**
- `explicit.is_file`
- `sorted`
- `programdata_root.glob`
- `SilworxApiError`

**Returns:** Path

##### `iter_port_pairs(config: AppConfig)` · line 139

**Does:** Yield all configured API/plugin port pairs (default: 51710-51719 / 8400-8409).

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `SilworxPortPair`
- `range`

**Returns:** List[SilworxPortPair]

##### `plugin_port_for_api(api_port: int, config: AppConfig)` · line 150

**Does:** Map an API port to its plugin WebSocket port using the configured offset.

**Needs:**
- Parameters: `api_port: int, config: AppConfig`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** int

##### `build_client_for_port(config: AppConfig, api_port: int)` · line 155

**Does:** Construct a client for a specific SILworX API port.

**Needs:**
- Parameters: `config: AppConfig, api_port: int`

**Calls:**
- `resolve_api_server_cert`
- `SilworxApiClient`

**Returns:** 'SilworxApiClient'

##### `build_client_from_config(config: AppConfig)` · line 168

**Does:** Construct a client from `solution.ini` preferred API port.

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `build_client_for_port`

**Returns:** 'SilworxApiClient'

##### `probe_api_port(config: AppConfig, api_port: int)` · line 173

**Does:** Return instance metadata when ``POST /silworx/info`` succeeds on ``api_port``.

**Needs:**
- Parameters: `config: AppConfig, api_port: int`

**Calls:**
- `resolve_api_server_cert`
- `SilworxApiClient`
- `client.get_silworx_info`
- `isinstance`
- `str`
- `info.get`
- `SilworxApiInstance`
- `plugin_port_for_api`

**Returns:** Optional[SilworxApiInstance]

##### `discover_available_instances(config: AppConfig)` · line 202

**Does:** Scan all configured port pairs and return those with a responding SILworX API.

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `iter_port_pairs`
- `probe_api_port`
- `found.append`

**Returns:** List[SilworxApiInstance]

##### `is_silworx_running(config: AppConfig)` · line 212

**Does:** True when any configured SILworX API port responds (G-19).

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `bool`
- `discover_available_instances`

**Returns:** bool

##### `is_silworx_running_on_port(config: AppConfig, api_port: int)` · line 221

**Does:** True when a single API port responds.

**Needs:**
- Parameters: `config: AppConfig, api_port: int`

**Calls:**
- `probe_api_port`

**Returns:** bool

##### `pick_api_project_path(config: AppConfig)` · line 520

**Does:** Best project file from solution.ini (diagnostic / Mode-A-removed leftover).

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `versioned.is_file`
- `project.is_file`

**Returns:** Optional[Path]

##### `_plugin_ssl_context(tls_certificate: Optional[Path] = None)` · line 555

**Does:** Internal helper.

**Needs:**
- Parameters: `tls_certificate: Optional[Path] = None`

**Calls:**
- `tls_certificate.is_file`
- `ssl.SSLContext`
- `ctx.load_verify_locations`
- `str`

**Returns:** ssl.SSLContext

##### `_acquire_session_id_async(host = '127.0.0.1', plugin_port = 8400, plugin_name = 'prooftest_session_plugin', timeout_sec = 15.0, tls_certificate = None, api_port = None)` · line 566

**Does:** Internal helper.

**Needs:**
- Parameters: `host = '127.0.0.1', plugin_port = 8400, plugin_name = 'prooftest_session_plugin', timeout_sec = 15.0, tls_certificate = None, api_port = None`

**Calls:**
- `SilworxApiError`
- `_RegisterPlugin`
- `asyncio.get_event_loop().time`
- `asyncio.get_event_loop`
- `websockets.connect`
- `_plugin_ssl_context`
- `ws.send`
- `json.dumps`
- `asdict`
- `log.info`
- `asyncio.wait_for`
- `ws.recv`
- `json.loads`
- `message.get`
- `(message.get('session_id') or '').strip`
- `log.debug`
- `log.warning`

**Returns:** Optional[str]

##### `acquire_open_project_session_id(host = '127.0.0.1', plugin_port = 8400, plugin_name = 'prooftest_session_plugin', timeout_sec = 15.0, tls_certificate = None, api_port = None)` · line 638

**Does:** Return API user_session_id for the currently open SILworX project, if any.

**Needs:**
- Parameters: `host = '127.0.0.1', plugin_port = 8400, plugin_name = 'prooftest_session_plugin', timeout_sec = 15.0, tls_certificate = None, api_port = None`

**Calls:**
- `asyncio.run`
- `_acquire_session_id_async`
- `asyncio.new_event_loop`
- `loop.run_until_complete`
- `loop.close`

**Returns:** Optional[str]

##### `resolve_gui_session_id(config: AppConfig, api_port: int, plugin_monitor = None, timeout_sec = 15.0)` · line 676

**Does:** Return a validated GUI session token for ``api_port``.

**Needs:**
- Parameters: `config: AppConfig, api_port: int, plugin_monitor = None, timeout_sec = 15.0`

**Calls:**
- `plugin_port_for_api`
- `plugin_monitor.get_session_id`
- `log.info`
- `getattr`
- `wait_for_session`
- `request_fresh`
- `max`
- `log.warning`
- `plugin_monitor._ports.get`
- `bool`
- `acquire_open_project_session_id`

**Returns:** Optional[str]

#### Class `SilworxApiError` · line 32

**Inherits:** `Exception`

**Purpose:** Base class for SILworX API failures.

*(no methods)*

#### Class `SilworxApiConnectionError` · line 36

**Inherits:** `SilworxApiError`

**Purpose:** Transport or TLS failure reaching the API.

*(no methods)*

#### Class `SilworxApiHttpError` · line 40

**Inherits:** `SilworxApiError`

**Purpose:** Non-success HTTP status from the API.

##### `__init__(self, status: int, path: str, body: str)` · line 43

**Does:** Internal helper.

**Needs:**
- Parameters: `status: int, path: str, body: str`
- Uses instance: `self.body`, `self.path`, `self.status`

**Calls:**
- `super().__init__`
- `super`

**Returns:** None

#### Class `SilworxProjectConflictError` · line 50

**Inherits:** `SilworxApiHttpError`

**Purpose:** HTTP 417 — project already open in SILworX GUI (OI-3).

*(no methods)*

#### Class `SilworxApiSessionError` · line 54

**Inherits:** `SilworxApiError`

**Purpose:** Operation requires an open API project session.

*(no methods)*

#### Class `SilworxApiResponseError` · line 58

**Inherits:** `SilworxApiError`

**Purpose:** Unexpected or incomplete JSON payload.

*(no methods)*

#### Class `GlobalVariablesNode` · line 78

**Inherits:** `—`

**Purpose:** One Global Variables node in the SILworX structure tree.

*(no methods)*

#### Class `GlobalVariableRecord` · line 88

**Inherits:** `—`

**Purpose:** Top-level global variable entry from the API.

*(no methods)*

#### Class `SilworxPortPair` · line 116

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `label(self)` · line 121

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.api_port`, `self.plugin_port`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

#### Class `SilworxApiInstance` · line 126

**Inherits:** `—`

**Purpose:** One reachable SILworX API endpoint on this station.

##### `label(self)` · line 135

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.api_port`, `self.plugin_port`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

#### Class `SilworxApiClient` · line 226

**Inherits:** `—`

**Purpose:** Session-aware HTTPS client for SILworX `/api/v1`.

Endpoints used (SPEC Step 3):
  POST /silworx/info
  POST /project/structuretree/info
  POST /node/globalvariables/content/read
  POST /project/close  (legacy / diagnostic only — service never opens a project)

##### `__init__(self, host: str = '127.0.0.1', port: int = 51710, server_ca_cert, client_cert_dir = None, timeout_sec = 120.0, open_project_timeout_sec = 600.0, connection_factory = None)` · line 237

**Does:** Internal helper.

**Needs:**
- Parameters: `host: str = '127.0.0.1', port: int = 51710, server_ca_cert, client_cert_dir = None, timeout_sec = 120.0, open_project_timeout_sec = 600.0, connection_factory = None`
- Uses instance: `self._connection_factory`, `self._ssl_context`, `self.client_cert_dir`, `self.host`, `self.open_project_timeout_sec`, `self.port`, `self.server_ca_cert`, `self.timeout_sec`, `self.user_session_id`

**Calls:**
- `int`
- `Path`
- `float`
- `ssl.create_default_context`
- `str`

**Returns:** None

##### `base_url(self)` · line 263

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.host`, `self.port`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `_request(self, path: str, session_id = None, query = None, json_body = None, require_session = False, timeout_sec = None)` · line 266

**Does:** Internal helper.

**Needs:**
- Parameters: `path: str, session_id = None, query = None, json_body = None, require_session = False, timeout_sec = None`
- Uses instance: `self._connection_factory`, `self._ssl_context`, `self.host`, `self.port`, `self.timeout_sec`, `self.user_session_id`

**Calls:**
- `SilworxApiSessionError`
- `urllib.parse.urlencode`
- `json.dumps(json_body).encode`
- `json.dumps`
- `self._connection_factory`
- `conn.request`
- `conn.getresponse`
- `response.read`
- `SilworxApiConnectionError`
- `str`
- `conn.close`
- `body_bytes.decode`
- `body.lower`
- `SilworxProjectConflictError`
- `SilworxApiHttpError`

**Returns:** bytes

##### `_request_json(self, path: str, timeout_sec: Optional[float] = None, **kwargs)` · line 321

**Does:** Internal helper.

**Needs:**
- Parameters: `path: str, timeout_sec: Optional[float] = None, **kwargs`
- Uses instance: `self._request`

**Calls:**
- `self._request`
- `json.loads`
- `raw.decode`
- `SilworxApiResponseError`

**Returns:** Dict[str, Any]

##### `get_silworx_info(self)` · line 328

**Does:** POST /silworx/info — version and license (no session, no JSON body).

**Needs:**
- Uses instance: `self._request_json`

**Calls:**
- `self._request_json`
- `payload.get`

**Returns:** Dict[str, Any]

##### `open_project_local(self, project_file: Path)` · line 333

**Does:** POST /project/open/local — diagnostic helper only.

**Needs:**
- Parameters: `project_file: Path`
- Uses instance: `self._request_json`, `self.open_project_timeout_sec`, `self.user_session_id`

**Calls:**
- `Path`
- `project_file.is_file`
- `SilworxApiError`
- `str`
- `self._request_json`
- `(payload.get('results') or {}).get`
- `payload.get`
- `SilworxApiResponseError`
- `json.dumps`
- `log.info`

**Returns:** str

##### `set_session_id(self, session_id: Optional[str])` · line 362

**Does:** Attach to an existing open-project API session (GUI / plugin workflow).

**Needs:**
- Parameters: `session_id: Optional[str]`
- Uses instance: `self.user_session_id`

**Calls:**
- `(session_id or '').strip`

**Returns:** None

##### `clear_session_id(self)` · line 366

**Does:** Drop cached session id without closing the project in SILworX.

**Needs:**
- Uses instance: `self.user_session_id`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

##### `close_project(self, session_id: Optional[str] = None, timeout_sec = None)` · line 370

**Does:** POST /project/close — release an API session opened by this client.

**Needs:**
- Parameters: `session_id: Optional[str] = None, timeout_sec = None`
- Uses instance: `self._request_json`, `self.timeout_sec`, `self.user_session_id`

**Calls:**
- `(session_id or self.user_session_id or '').strip`
- `self._request_json`
- `log.warning`

**Returns:** bool

##### `get_structuretree(self)` · line 399

**Does:** POST /project/structuretree/info — full configuration/resource tree.

**Needs:**
- Uses instance: `self._request_json`

**Calls:**
- `self._request_json`
- `payload.get`

**Returns:** Dict[str, Any]

##### `read_global_variables(self, internal_address: str)` · line 404

**Does:** POST /node/globalvariables/content/read for one Global Variables node.

**Needs:**
- Parameters: `internal_address: str`
- Uses instance: `self._request_json`

**Calls:**
- `self._request_json`
- `payload.get`
- `results.get`
- `nested.get`
- `SilworxApiResponseError`
- `json.dumps`

**Returns:** List[Dict[str, Any]]

##### `_is_global_variables_node(node: Dict[str, Any])` · line 424

**Does:** Internal helper.

**Needs:**
- Parameters: `node: Dict[str, Any]`

**Calls:**
- `(node.get('display_name') or node.get('name') or '').strip`
- `node.get`
- `((node.get('type_info') or {}).get('display_name') or '').lower`
- `(node.get('type_info') or {}).get`
- `((node.get('type_info') or {}).get('symbol') or '').lower`
- `type_symbol.replace`

**Returns:** bool

##### `_node_label(node: Dict[str, Any])` · line 437

**Does:** Internal helper.

**Needs:**
- Parameters: `node: Dict[str, Any]`

**Calls:**
- `(node.get('display_name') or node.get('name') or '').strip`
- `node.get`

**Returns:** str

##### `_node_symbol(node: Dict[str, Any])` · line 441

**Does:** Internal helper.

**Needs:**
- Parameters: `node: Dict[str, Any]`

**Calls:**
- `((node.get('type_info') or {}).get('symbol') or '').lower`
- `(node.get('type_info') or {}).get`
- `node.get`

**Returns:** str

##### `find_all_globalvariable_nodes(self, tree: Optional[Dict[str, Any]] = None)` · line 444

**Does:** Walk structuretree and return every Global Variables node.

**Needs:**
- Parameters: `tree: Optional[Dict[str, Any]] = None`
- Uses instance: `self.get_structuretree`

**Calls:**
- `self.get_structuretree`
- `tree.get`
- `isinstance`
- `walk`
- `log.info`
- `len`

**Returns:** List[GlobalVariablesNode]

##### `list_top_level_globals(self, internal_address: str)` · line 500

**Does:** Read globals at one node; return only top-level variables (no nested items).

**Needs:**
- Parameters: `internal_address: str`
- Uses instance: `self.read_global_variables`

**Calls:**
- `self.read_global_variables`
- `(var.get('name') or '').strip`
- `var.get`
- `(var.get('data_type') or '').strip`
- `records.append`
- `GlobalVariableRecord`

**Returns:** List[GlobalVariableRecord]

##### `project_session(self, project_file: Path)` · line 511

**Does:** Open project via API and always close the session in `finally`.

**Needs:**
- Parameters: `project_file: Path`
- Uses instance: `self.close_project`, `self.open_project_local`

**Calls:**
- `self.open_project_local`
- `self.close_project`

**Returns:** Iterator[str]

#### Class `_RegisterPlugin` · line 532

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__post_init__(self)` · line 544

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.customized_contextmenu_trigger`, `self.customized_extramenu_trigger`, `self.predefined_trigger`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

---

## Adapter — Plugin WebSocket

### File `Annex codes/Plugin/annex_plugin_monitor.py`

**Layer:** Adapter — Plugin WebSocket

**Module purpose:** Persistent SILworX plugin WebSocket monitors on all configured port pairs (G-22).

The monitor listens for TRIGGER_SESSION_ID_CHANGED on plugin ports 8400–8409.
It does **not** read device data — that is always done via REST API (step03).

Project modify / code generation / download are detected via session-folder mtime
watchers in step07 (SILworX exposes no plugin triggers for those events).

#### Module-level functions *(no class)*

##### `_plugin_ssl_context(tls_certificate)` · line 60

**Does:** Internal helper.

**Needs:**
- Parameters: `tls_certificate`

**Calls:**
- `Path`
- `cert_path.is_file`
- `ssl.SSLContext`
- `ctx.load_verify_locations`
- `str`

**Returns:** ssl.SSLContext

#### Class `PortSessionState` · line 30

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `_RegisterPlugin` · line 39

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__post_init__(self)` · line 51

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.predefined_trigger`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** None

#### Class `PluginPortMonitor` · line 74

**Inherits:** `—`

**Purpose:** Background listener on every configured SILworX plugin port.

##### `__init__(self, config: AppConfig)` · line 77

**Does:** Internal helper.

**Needs:**
- Parameters: `config: AppConfig`
- Uses instance: `self._lock`, `self._pending`, `self._ports`, `self._reregister`, `self._stop`, `self._thread`, `self._unavailable_warned`, `self.config`

**Calls:**
- `threading.Event`
- `threading.Lock`
- `set`

**Returns:** None

##### `_ensure_port_state(self, api_port: int, plugin_port: int)` · line 87

**Does:** Internal helper.

**Needs:**
- Parameters: `api_port: int, plugin_port: int`
- Uses instance: `self._lock`, `self._ports`

**Calls:**
- `PortSessionState`

**Returns:** None

##### `start(self)` · line 95

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._stop`, `self._thread`, `self._thread_main`, `self.config`

**Calls:**
- `self._thread.is_alive`
- `self._stop.clear`
- `threading.Thread`
- `self._thread.start`
- `log.info`

**Returns:** None

##### `stop(self)` · line 108

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._lock`, `self._port_tag`, `self._ports`, `self._stop`, `self._thread`

**Calls:**
- `self._thread.is_alive`
- `self._port_tag`
- `self._ports.values`
- `log.info`
- `', '.join`
- `self._stop.set`
- `self._thread.join`

**Returns:** None

##### `is_running(self)` · line 128

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._thread`

**Calls:**
- `self._thread.is_alive`

**Returns:** bool

##### `get_session_id(self, plugin_port: int)` · line 131

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `plugin_port: int`
- Uses instance: `self._lock`, `self._ports`

**Calls:**
- `self._ports.get`

**Returns:** Optional[str]

##### `wait_for_session_id(self, plugin_port: int, timeout_sec = 15.0, poll_sec = 0.25, not_equal = '')` · line 138

**Does:** Poll the monitor cache until a session id appears or timeout elapses.

**Needs:**
- Parameters: `plugin_port: int, timeout_sec = 15.0, poll_sec = 0.25, not_equal = ''`
- Uses instance: `self.get_session_id`, `self.is_running`

**Calls:**
- `(not_equal or '').strip`
- `time.monotonic`
- `max`
- `float`
- `self.get_session_id`
- `self.is_running`
- `time.sleep`
- `min`

**Returns:** Optional[str]

##### `request_fresh_session(self, plugin_port: Optional[int] = None)` · line 161

**Does:** Drop cached tokens and reconnect the plugin WebSocket to get a new session id.

**Needs:**
- Parameters: `plugin_port: Optional[int] = None`
- Uses instance: `self._lock`, `self._ports`, `self._reregister`

**Calls:**
- `list`
- `self._ports.keys`
- `self._ports.get`
- `self._reregister.add`
- `log.info`

**Returns:** None

##### `_should_reregister(self, plugin_port: int)` · line 177

**Does:** Internal helper.

**Needs:**
- Parameters: `plugin_port: int`
- Uses instance: `self._lock`, `self._reregister`

**Calls:**
- `self._reregister.discard`

**Returns:** bool

##### `port_states_summary(self)` · line 184

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._lock`, `self._ports`

**Calls:**
- `sorted`
- `self._ports.values`
- `len`
- `parts.append`
- `';'.join`

**Returns:** str

##### `consume_triggers(self)` · line 193

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._lock`, `self._pending`

**Calls:**
- `sorted`
- `self._pending.clear`

**Returns:** List[str]

##### `_port_tag(api_port: int, plugin_port: int)` · line 200

**Does:** Internal helper.

**Needs:**
- Parameters: `api_port: int, plugin_port: int`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `_thread_main(self)` · line 203

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._async_main`, `self._stop`

**Calls:**
- `asyncio.run`
- `self._async_main`
- `self._stop.is_set`
- `log.warning`

**Returns:** None

##### `_async_main(self)` · line 210

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.config`

**Calls:**
- `max`
- `float`
- `_maintain_listeners`

**Returns:** None

##### `_listen_port(self, api_port: int, plugin_port: int)` · line 254

**Does:** Internal helper.

**Needs:**
- Parameters: `api_port: int, plugin_port: int`
- Uses instance: `self._handle_message`, `self._port_tag`, `self._set_connected`, `self._should_reregister`, `self._stop`, `self._unavailable_warned`, `self.config`, `self.get_session_id`

**Calls:**
- `log.error`
- `_RegisterPlugin`
- `self._port_tag`
- `self._stop.is_set`
- `websockets.connect`
- `_plugin_ssl_context`
- `ws.send`
- `json.dumps`
- `asdict`
- `self._set_connected`
- `self._unavailable_warned.discard`
- `log.info`
- `time.monotonic`
- `self.get_session_id`
- `self._should_reregister`
- `asyncio.wait_for`
- `ws.recv`
- `json.loads`
- `message.get`
- `self._handle_message`
- `log.warning`
- `self._unavailable_warned.add`
- `log.debug`
- `str`
- `min`
- `… +1 more`

**Returns:** None

##### `_set_connected(self, plugin_port: int, connected: bool)` · line 389

**Does:** Internal helper.

**Needs:**
- Parameters: `plugin_port: int, connected: bool`
- Uses instance: `self._lock`, `self._ports`

**Calls:**
- `self._ports.get`

**Returns:** None

##### `_handle_message(self, plugin_port: int, api_port: int, message: dict)` · line 395

**Does:** Internal helper.

**Needs:**
- Parameters: `plugin_port: int, api_port: int, message: dict`
- Uses instance: `self._lock`, `self._pending`, `self._port_tag`, `self._ports`

**Calls:**
- `message.get`
- `(message.get('session_id') or '').strip`
- `self._ports.get`
- `time.monotonic`
- `log.info`
- `self._port_tag`
- `len`
- `self._pending.add`

**Returns:** None

---

## Adapter — Database

### File `Annex codes/Database/annex_database.py`

**Layer:** Adapter — Database

**Module purpose:** Annex — SQL Server / SQLite database access and SQL table templates.

#### Module-level functions *(no class)*

##### `validate_sql_database_name(name: str)` · line 32

**Does:** Allow safe SQL identifiers for CREATE DATABASE / USE (R3).

**Needs:**
- Parameters: `name: str`

**Calls:**
- `(name or '').strip`
- `_SQL_DB_NAME_RE.fullmatch`
- `ValueError`
- `len`

**Returns:** str

##### `_normalize_column_name(col: str)` · line 1306

**Does:** Internal helper.

**Needs:**
- Parameters: `col: str`

**Calls:**
- `*(no direct calls detected)*`

**Returns:** str

##### `_find_error_code_column(columns: List[str])` · line 1312

**Does:** Internal helper.

**Needs:**
- Parameters: `columns: List[str]`

**Calls:**
- `col.lower`

**Returns:** Optional[str]

##### `silworx_dtype_to_sql_template(dtype: str)` · line 1319

**Does:** Map SILworX member type to SQL column type used in HIMA templates.

**Needs:**
- Parameters: `dtype: str`

**Calls:**
- `(dtype or '').strip`
- `dtype.startswith`

**Returns:** str

##### `build_create_table_sql(table_name: str, structure: ResultsStructure)` · line 1341

**Does:** Generate a single CREATE TABLE block for one Results structure.

**Needs:**
- Parameters: `table_name: str, structure: ResultsStructure`

**Calls:**
- `_normalize_column_name`
- `member_to_column`
- `col_names.append`
- `silworx_dtype_to_sql_template`
- `lines.append`
- `_find_error_code_column`
- `_ERROR_BYTE_TEMPLATE.format(col=error_col).rstrip`
- `_ERROR_BYTE_TEMPLATE.format`
- `lines.extend`
- `'\n'.join`

**Returns:** str

##### `write_template_file(templates_dir: Path, structure: ResultsStructure)` · line 1381

**Does:** Write the SQL template for one Results type.

**Needs:**
- Parameters: `templates_dir: Path, structure: ResultsStructure`

**Calls:**
- `TEMPLATE_MAP.get`
- `KeyError`
- `path.write_text`
- `build_create_table_sql`

**Returns:** Path

##### `generate_missing_templates(structures_dir: Path, templates_dir: Path)` · line 1392

**Does:** Generate SQL templates for types that have no template file yet.

**Needs:**
- Parameters: `structures_dir: Path, templates_dir: Path`

**Calls:**
- `RESULTS_TYPE_FILES.items`
- `TEMPLATE_MAP.get`
- `tpl_path.exists`
- `csv_path.exists`
- `load_structure`
- `written.append`
- `write_template_file`

**Returns:** List[Path]

##### `template_for_type(type_name: str)` · line 1410

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `type_name: str`

**Calls:**
- `TEMPLATE_MAP.get`

**Returns:** Optional[tuple[str, str]]

#### Class `Database` · line 50

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `__init__(self, config: AppConfig, alarms: AlarmManager)` · line 51

**Does:** Internal helper.

**Needs:**
- Parameters: `config: AppConfig, alarms: AlarmManager`
- Uses instance: `self._conn`, `self._lock`, `self.alarms`, `self.config`, `self.using_sqlite`

**Calls:**
- `threading.Lock`

**Returns:** None

##### `connect(self)` · line 58

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._conn`, `self._connect_sqlite`, `self._try_sql_server`, `self.config`

**Calls:**
- `self._try_sql_server`
- `self._connect_sqlite`
- `RuntimeError`

**Returns:** None

##### `close(self)` · line 66

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._conn`, `self._lock`

**Calls:**
- `self._conn.close`

**Returns:** None

##### `_try_sql_server(self)` · line 76

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._conn`, `self._ensure_system_tables`, `self.alarms`, `self.config`, `self.using_sqlite`

**Calls:**
- `pyodbc.connect`
- `master.cursor`
- `validate_sql_database_name`
- `cur.execute`
- `cur.fetchone`
- `Path`
- `data_dir.mkdir`
- `str`
- `(data_dir / f'{safe}.mdf').resolve`
- `(data_dir / f'{safe}_log.ldf').resolve`
- `master.close`
- `conn_str.replace`
- `self._ensure_system_tables`
- `self.alarms.raise_alarm`

**Returns:** bool

##### `_connect_sqlite(self)` · line 127

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._conn`, `self._ensure_system_tables`, `self.config`, `self.using_sqlite`

**Calls:**
- `path.parent.mkdir`
- `sqlite3.connect`
- `str`
- `self._ensure_system_tables`

**Returns:** None

##### `cursor(self)` · line 136

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._conn`, `self._lock`, `self.connect`, `self.using_sqlite`

**Calls:**
- `self.connect`
- `self._conn.cursor`
- `cur.execute`
- `self._conn.commit`
- `self._conn.rollback`
- `cur.close`

**Returns:** Iterator[Any]

##### `_ensure_system_tables(self)` · line 151

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._ensure_alarm_log_columns`, `self._ensure_device_id_identity`, `self._ensure_present_on_opc_column`, `self._ensure_prooftest_history_table`, `self._ensure_silworx_project_column`, `self._ensure_test_started_at_column`, `self._table_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `self._ensure_present_on_opc_column`
- `self._ensure_test_started_at_column`
- `self._ensure_silworx_project_column`
- `self._ensure_device_id_identity`
- `self._ensure_prooftest_history_table`
- `self._ensure_alarm_log_columns`
- `tables.items`
- `self._table_exists`

**Returns:** None

##### `log_alarm(self, step: str, severity: str, message: str, solution: str, device_tag: Optional[str] = None)` · line 251

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `step: str, severity: str, message: str, solution: str, device_tag: Optional[str] = None`
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `datetime.now().isoformat`
- `datetime.now`

**Returns:** None

##### `list_recent_alarms(self, limit: int = 50)` · line 258

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `limit: int = 50`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchall`
- `bool`
- `alarm_error_key`

**Returns:** List[Dict[str, Any]]

##### `get_alarm(self, alarm_id: int)` · line 291

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `alarm_id: int`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchone`
- `bool`
- `alarm_error_key`

**Returns:** Optional[Dict[str, Any]]

##### `acknowledge_alarm(self, alarm_id: int)` · line 323

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `alarm_id: int`
- Uses instance: `self.cursor`, `self.get_alarm`, `self.using_sqlite`

**Calls:**
- `self.get_alarm`
- `self.cursor`
- `cur.execute`

**Returns:** Optional[Dict[str, Any]]

##### `reset_alarms(self)` · line 338

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `set_service_state(self, key: str, value: str)` · line 345

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `key: str, value: str`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchone`

**Returns:** None

##### `get_service_state(self)` · line 359

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchall`

**Returns:** Dict[str, str]

##### `apply_sql_template(self, template_path: Path, old_table: str, new_table: str)` · line 367

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `template_path: Path, old_table: str, new_table: str`
- Uses instance: `self._create_table_from_template_sqlite`, `self._table_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._table_exists`
- `template_path.read_text`
- `re.search`
- `re.escape`
- `ValueError`
- `create_match.group(1).strip`
- `create_match.group`
- `body.replace`
- `self._create_table_from_template_sqlite`
- `text.replace`
- `', '.join`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_create_table_from_template_sqlite(self, text: str, table_name: str)` · line 396

**Does:** Internal helper.

**Needs:**
- Parameters: `text: str, table_name: str`
- Uses instance: `self.cursor`

**Calls:**
- `text.splitlines`
- `re.match`
- `m.group`
- `m.group(2).upper`
- `typ.startswith`
- `cols.append`
- `', '.join`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `ensure_results_table(self, structure: ResultsStructure, templates_dir: Path | None = None)` · line 425

**Does:** Create ProofTest_* table if missing.

**Needs:**
- Parameters: `structure: ResultsStructure, templates_dir: Path | None = None`
- Uses instance: `self._create_table_from_csv`, `self._record_schema`, `self._table_exists`, `self.alarms`, `self.apply_sql_template`

**Calls:**
- `self._table_exists`
- `Path`
- `str(templates_dir).strip`
- `str`
- `tpl_root.is_dir`
- `any`
- `tpl_root.glob`
- `TEMPLATE_MAP.get`
- `tpl_path.exists`
- `self.apply_sql_template`
- `self._record_schema`
- `self.alarms.raise_alarm`
- `self._create_table_from_csv`

**Returns:** None

##### `_table_exists(self, table: str)` · line 460

**Does:** Internal helper.

**Needs:**
- Parameters: `table: str`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchone`

**Returns:** bool

##### `_column_exists(self, table: str, column: str)` · line 468

**Does:** Internal helper.

**Needs:**
- Parameters: `table: str, column: str`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `any`
- `str`
- `cur.fetchall`
- `cur.fetchone`

**Returns:** bool

##### `_ensure_present_on_opc_column(self)` · line 479

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._column_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._column_exists`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_ensure_test_started_at_column(self)` · line 492

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._column_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._column_exists`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_ensure_silworx_project_column(self)` · line 505

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._column_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._column_exists`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_ensure_device_id_identity(self)` · line 518

**Does:** Composite DeviceId (Project+Configuration+Resource+Device_TAG), unique, not TAG alone.

**Needs:**
- Uses instance: `self._backfill_device_ids`, `self._column_exists`, `self._ensure_sqlserver_device_id_unique`, `self._rebuild_sqlite_device_list_pk`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._column_exists`
- `self.cursor`
- `cur.execute`
- `self._backfill_device_ids`
- `self._rebuild_sqlite_device_list_pk`
- `self._ensure_sqlserver_device_id_unique`

**Returns:** None

##### `_backfill_device_ids(self)` · line 534

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchall`
- `DeviceId(project or '', cfg or '', res or '', tag or '').key`
- `DeviceId`

**Returns:** None

##### `_rebuild_sqlite_device_list_pk(self)` · line 553

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchall`
- `str`
- `int`

**Returns:** None

##### `_ensure_sqlserver_device_id_unique(self)` · line 582

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchone`
- `str`

**Returns:** None

##### `_ensure_prooftest_history_table(self)` · line 603

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._table_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._table_exists`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_iso_ts(value: Any)` · line 632

**Does:** Internal helper.

**Needs:**
- Parameters: `value: Any`

**Calls:**
- `hasattr`
- `value.isoformat`
- `str(value).strip`
- `str`

**Returns:** Optional[str]

##### `start_test_history(self, device_tag: str, results_type: str = '')` · line 640

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str = ''`
- Uses instance: `self.cursor`, `self.finish_open_test_history`

**Calls:**
- `datetime.now().isoformat`
- `datetime.now`
- `self.finish_open_test_history`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `finish_open_test_history(self, device_tag: str, outcome: str, result: Optional[str] = None)` · line 650

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, outcome: str, result: Optional[str] = None`
- Uses instance: `self.cursor`

**Calls:**
- `datetime.now().isoformat`
- `datetime.now`
- `self.cursor`
- `cur.execute`
- `cur.fetchone`

**Returns:** bool

##### `interrupt_open_tests(self)` · line 672

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `datetime.now().isoformat`
- `datetime.now`
- `self.cursor`
- `cur.execute`
- `cur.fetchone`
- `int`

**Returns:** int

##### `list_test_history(self, limit: int = 50)` · line 689

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `limit: int = 50`
- Uses instance: `self._iso_ts`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchall`
- `self._iso_ts`

**Returns:** List[Dict[str, Any]]

##### `_ensure_alarm_log_columns(self)` · line 717

**Does:** Internal helper.

**Needs:**
- Uses instance: `self._column_exists`, `self._table_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._table_exists`
- `self._column_exists`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_create_table_from_csv(self, structure: ResultsStructure)` · line 730

**Does:** Generate CREATE TABLE matching project SQL template style (no .sql file required).

**Needs:**
- Parameters: `structure: ResultsStructure`
- Uses instance: `self._table_exists`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._table_exists`
- `col_defs.append`
- `_normalize_column_name`
- `member_to_column`
- `col_names.append`
- `silworx_type_to_sql`
- `silworx_dtype_to_sql_template`
- `_find_error_code_column`
- `', '.join`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_record_schema(self, structure: ResultsStructure)` · line 792

**Does:** Internal helper.

**Needs:**
- Parameters: `structure: ResultsStructure`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `structure.csv_path.exists`
- `structure.csv_path.read_bytes`
- `hashlib.sha256(source).hexdigest`
- `hashlib.sha256`
- `self.cursor`
- `cur.execute`
- `datetime.now().isoformat`
- `datetime.now`
- `cur.fetchone`

**Returns:** None

##### `sync_schema_case1(self, structures: Dict[str, ResultsStructure], active_types: List[str])` · line 815

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `structures: Dict[str, ResultsStructure], active_types: List[str]`
- Uses instance: `self.config`, `self.ensure_results_table`

**Calls:**
- `self.ensure_results_table`

**Returns:** None

##### `sync_schema_case2(self, templates_dir: Path | None, structures: Dict[str, ResultsStructure])` · line 820

**Does:** Ensure all ProofTest_* tables exist from Results structures (templates optional).

**Needs:**
- Parameters: `templates_dir: Path | None, structures: Dict[str, ResultsStructure]`
- Uses instance: `self.alarms`, `self.ensure_results_table`

**Calls:**
- `self.alarms.raise_alarm`
- `structures.items`
- `self.ensure_results_table`

**Returns:** None

##### `upsert_device(self, device_tag: str, results_type: str, opc_server = None, opc_prefix = None, configuration = None, resource = None, last_running = None, test_in_progress = None, silworx_project = None, device_id = None)` · line 834

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str, opc_server = None, opc_prefix = None, configuration = None, resource = None, last_running = None, test_in_progress = None, silworx_project = None, device_id = None`
- Uses instance: `self.cursor`

**Calls:**
- `datetime.now().isoformat`
- `datetime.now`
- `DeviceId(silworx_project or '', configuration or '', resource or '', device_tag or '').key`
- `DeviceId`
- `self.cursor`
- `cur.execute`
- `cur.fetchone`
- `cur.fetchall`
- `str`
- `str(donor_project or '').strip`
- `fields.append`
- `params.append`
- `int`
- `', '.join`

**Returns:** None

##### `_with_device_source(row: Dict[str, Any])` · line 946

**Does:** OPC ProgID when present on OPC; otherwise the SILworX project of detection.

**Needs:**
- Parameters: `row: Dict[str, Any]`

**Calls:**
- `bool`
- `row.get`
- `str(row.get('opc_server') or '').strip`
- `str`
- `str(row.get('silworx_project') or '').strip`

**Returns:** Dict[str, Any]

##### `export_device_rows(self)` · line 966

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `int`
- `bool`
- `cur.fetchall`

**Returns:** List[Dict[str, Any]]

##### `set_device_present_on_opc_by_id(self, device_id: str, present: bool)` · line 993

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_id: str, present: bool`
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `set_device_present_on_opc(self, device_tag: str, present: bool)` · line 1000

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, present: bool`
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `delete_devices_not_on_opc(self)` · line 1007

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `str`
- `cur.fetchall`

**Returns:** List[str]

##### `list_active_devices(self)` · line 1020

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self._with_device_source`, `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `self._with_device_source`
- `bool`
- `cur.fetchall`

**Returns:** List[Dict[str, Any]]

##### `list_inactive_devices(self)` · line 1048

**Does:** Inactive catalog rows (e.g. API-only GVs dropped on OPC-only refresh).

**Needs:**
- Uses instance: `self._with_device_source`, `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `self._with_device_source`
- `bool`
- `cur.fetchall`

**Returns:** List[Dict[str, Any]]

##### `list_running_tests(self)` · line 1077

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchall`

**Returns:** List[Dict[str, Any]]

##### `list_devices(self, view: str = 'all')` · line 1094

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `view: str = 'all'`
- Uses instance: `self.list_active_devices`

**Calls:**
- `self.list_active_devices`
- `str(view).lower`
- `str`
- `row.get`

**Returns:** List[Dict[str, Any]]

##### `count_listed_devices(self)` · line 1100

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchone`
- `int`

**Returns:** int

##### `count_opc_devices(self)` · line 1106

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.cursor`

**Calls:**
- `self.cursor`
- `cur.execute`
- `cur.fetchone`
- `int`

**Returns:** int

##### `set_present_on_opc(self, tags: Set[str])` · line 1114

**Does:** Mark OPC presence. Keys may be DeviceId, Device_TAG, or OPC_ItemPrefix.

**Needs:**
- Parameters: `tags: Set[str]`
- Uses instance: `self.cursor`

**Calls:**
- `str`
- `self.cursor`
- `cur.execute`

**Returns:** None

##### `_prooftest_table_names(self)` · line 1140

**Does:** Internal helper.

**Needs:**
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`
- `str`
- `cur.fetchall`

**Returns:** List[str]

##### `device_has_prooftest_reports(self, device_tag: str, results_type = None, report_output = None)` · line 1153

**Does:** True when the device has a SQL snapshot or an HTML/PDF report file.

**Needs:**
- Parameters: `device_tag: str, results_type = None, report_output = None`
- Uses instance: `self._prooftest_table_names`, `self.cursor`, `self.using_sqlite`

**Calls:**
- `self._prooftest_table_names`
- `self.cursor`
- `cur.execute`
- `cur.fetchone`
- `int`
- `list_reports_for_device`
- `Path`

**Returns:** bool

##### `reconcile_device_list(self, present_tags: List[str], report_output = None)` · line 1180

**Does:** Keep detected devices. Missing DeviceIds are marked inactive; snapshot history is never deleted.

**Needs:**
- Parameters: `present_tags: List[str], report_output = None`
- Uses instance: `self.cursor`

**Calls:**
- `str`
- `self.cursor`
- `cur.execute`
- `cur.fetchall`

**Returns:** None

##### `deactivate_missing_devices(self, active_tags: List[str])` · line 1233

**Does:** Backward-compatible name — now applies add/keep/delete retention.

**Needs:**
- Parameters: `active_tags: List[str]`
- Uses instance: `self.reconcile_device_list`

**Calls:**
- `self.reconcile_device_list`

**Returns:** None

##### `insert_snapshot(self, table: str, device_tag: str, values: Dict[str, Any], opc_server, sequence = None)` · line 1237

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `table: str, device_tag: str, values: Dict[str, Any], opc_server, sequence = None`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `dict`
- `values.pop`
- `datetime.now`
- `list`
- `values.keys`
- `', '.join`
- `self.cursor`
- `cur.execute`
- `int`
- `cur.fetchone`

**Returns:** int

##### `update_report_path(self, table: str, record_id: int, report_path: str)` · line 1271

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `table: str, record_id: int, report_path: str`
- Uses instance: `self.cursor`, `self.using_sqlite`

**Calls:**
- `self.cursor`
- `cur.execute`

**Returns:** None

### File `Annex codes/Database/annex_list_archive.py`

**Layer:** Adapter — Database

**Module purpose:** Archive and restore the Device Prooftest Result List and report list (CSV).

#### Module-level functions *(no class)*

##### `archive_root(config: AppConfig)` · line 52

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `Path`

**Returns:** Path

##### `keep_opc_only_enabled(db: Any)` · line 56

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `db: Any`

**Calls:**
- `str`
- `db.get_service_state().get`
- `db.get_service_state`

**Returns:** bool

##### `set_keep_opc_only(db: Any, enabled: bool)` · line 63

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `db: Any, enabled: bool`

**Calls:**
- `db.set_service_state`

**Returns:** None

##### `_csv_cell(value: Any)` · line 67

**Does:** Internal helper.

**Needs:**
- Parameters: `value: Any`

**Calls:**
- `isinstance`
- `str`

**Returns:** str

##### `_collect_reports(config: AppConfig, devices: List[Dict[str, Any]])` · line 75

**Does:** Internal helper.

**Needs:**
- Parameters: `config: AppConfig, devices: List[Dict[str, Any]]`

**Calls:**
- `Path`
- `set`
- `str`
- `device.get`
- `list_reports_for_device`
- `seen.add`
- `path.resolve().relative_to`
- `path.resolve`
- `output.resolve`
- `rows.append`
- `report.get`
- `relative.replace`
- `rows.sort`

**Returns:** List[Dict[str, str]]

##### `create_list_archive(db: Any, config: AppConfig)` · line 113

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `db: Any, config: AppConfig`

**Calls:**
- `datetime.now().strftime`
- `datetime.now`
- `archive_root`
- `folder.mkdir`
- `reports_dir.mkdir`
- `db.export_device_rows`
- `_collect_reports`
- `devices_csv.open`
- `csv.DictWriter`
- `writer.writeheader`
- `writer.writerow`
- `_csv_cell`
- `device.get`
- `reports_csv.open`
- `Path`
- `source.is_file`
- `dest.parent.mkdir`
- `shutil.copy2`
- `datetime.now().isoformat`
- `len`
- `str`
- `(folder / 'manifest.json').write_text`
- `json.dumps`

**Returns:** Dict[str, Any]

##### `zip_archive_folder(folder: Path)` · line 176

**Does:** Pack an on-disk list archive folder into a restore-compatible zip.

**Needs:**
- Parameters: `folder: Path`

**Calls:**
- `io.BytesIO`
- `zipfile.ZipFile`
- `sorted`
- `folder.rglob`
- `path.is_file`
- `archive.write`
- `path.relative_to(folder).as_posix`
- `path.relative_to`
- `buf.getvalue`

**Returns:** bytes

##### `export_list_archive(db: Any, config: AppConfig)` · line 187

**Does:** Create a list archive and return manifest plus zip bytes for export.

**Needs:**
- Parameters: `db: Any, config: AppConfig`

**Calls:**
- `create_list_archive`
- `Path`
- `zip_archive_folder`

**Returns:** tuple[Dict[str, Any], bytes]

##### `list_list_archives(config: AppConfig)` · line 196

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `config: AppConfig`

**Calls:**
- `archive_root`
- `root.is_dir`
- `sorted`
- `root.iterdir`
- `folder.is_dir`
- `ARCHIVE_ID_RE.match`
- `str`
- `manifest_path.is_file`
- `json.loads`
- `manifest_path.read_text`
- `isinstance`
- `item.update`
- `payload.get`
- `int`
- `datetime.fromtimestamp(folder.stat().st_mtime).isoformat`
- `datetime.fromtimestamp`
- `folder.stat`
- `archives.append`

**Returns:** List[Dict[str, Any]]

##### `_archive_folder(config: AppConfig, archive_id: str)` · line 234

**Does:** Internal helper.

**Needs:**
- Parameters: `config: AppConfig, archive_id: str`

**Calls:**
- `ARCHIVE_ID_RE.match`
- `ListArchiveError`
- `archive_root`
- `folder.is_dir`

**Returns:** Path

##### `_safe_extract_zip(archive: zipfile.ZipFile, dest: Path)` · line 243

**Does:** Internal helper.

**Needs:**
- Parameters: `archive: zipfile.ZipFile, dest: Path`

**Calls:**
- `dest.resolve`
- `archive.infolist`
- `(dest / info.filename).resolve`
- `ListArchiveError`
- `info.is_dir`
- `target.mkdir`
- `target.parent.mkdir`
- `archive.open`
- `target.open`
- `shutil.copyfileobj`

**Returns:** None

##### `restore_from_folder(db: Any, config: AppConfig, folder: Path, archive_id = '')` · line 257

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `db: Any, config: AppConfig, folder: Path, archive_id = ''`

**Calls:**
- `devices_csv.is_file`
- `folder.rglob`
- `path.is_file`
- `ListArchiveError`
- `devices_csv.open`
- `csv.DictReader`
- `(row.get('Device_TAG') or '').strip`
- `row.get`
- `(row.get('Results_Type') or '').strip`
- `db.upsert_device`
- `(row.get('OPC_Server') or '').strip`
- `(row.get('OPC_ItemPrefix') or '').strip`
- `(row.get('Configuration') or '').strip`
- `(row.get('Resource') or '').strip`
- `(row.get('SilworxProject') or '').strip`
- `(row.get('DeviceId') or '').strip`
- `(row.get('PresentOnOpc') or '').strip`
- `db.set_device_present_on_opc`
- `Path`
- `reports_csv.is_file`
- `reports_csv.open`
- `(row.get('RelativePath') or '').replace('\\', '/').lstrip`
- `(row.get('RelativePath') or '').replace`
- `source.is_file`
- `dest.parent.mkdir`
- `… +4 more`

**Returns:** Dict[str, Any]

##### `restore_list_archive(db: Any, config: AppConfig, archive_id: str)` · line 327

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `db: Any, config: AppConfig, archive_id: str`

**Calls:**
- `_archive_folder`
- `restore_from_folder`

**Returns:** Dict[str, Any]

##### `restore_from_uploaded_file(db: Any, config: AppConfig, uploaded_path: Path, original_name: str = '')` · line 332

**Does:** Restore devices (and reports if present) from an uploaded csv or zip.

**Needs:**
- Parameters: `db: Any, config: AppConfig, uploaded_path: Path, original_name: str = ''`

**Calls:**
- `(original_name or uploaded_path.name).lower`
- `Path`
- `tempfile.mkdtemp`
- `name.endswith`
- `shutil.copy2`
- `restore_from_folder`
- `zipfile.ZipFile`
- `_safe_extract_zip`
- `ListArchiveError`
- `shutil.rmtree`

**Returns:** Dict[str, Any]

##### `clear_keep_opc_only(db: Any, config: AppConfig, archive_first = True)` · line 358

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `db: Any, config: AppConfig, archive_first = True`

**Calls:**
- `db.count_opc_devices`
- `ListArchiveError`
- `create_list_archive`
- `db.delete_devices_not_on_opc`
- `set_keep_opc_only`
- `len`
- `db.count_listed_devices`

**Returns:** Dict[str, Any]

#### Class `ListArchiveError` · line 48

**Inherits:** `ValueError`

**Purpose:** Operator-facing archive/restore/clear error.

*(no methods)*

---

## Adapter — Reports

### File `Annex codes/PDF generation/annex_pdf_generation.py`

**Layer:** Adapter — Reports

**Module purpose:** Annex — PDF and HTML report generation.

Uses HIMA HTML templates from ``1- HTML Reports Template`` when a layout exists
for the Results type (and SAMSON FST/PST variant); otherwise falls back to a
simple built-in HTML table.

#### Module-level functions *(no class)*

##### `_build_html_template_folder_map()` · line 36

**Does:** Align with ``TEMPLATE_MAP`` table names (same as ``1- HTML Reports Template`` folders).

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `TEMPLATE_MAP.items`
- `mapping.update`

**Returns:** Dict[str, str]

##### `_reverse_template_aliases()` · line 94

**Does:** Internal helper.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `_TEMPLATE_ALIASES.items`
- `placeholder.lower`

**Returns:** Dict[str, str]

##### `_apply_numeric_test_point_aliases(context: Dict[str, str], snapshot: Dict[str, Any], decimal_places: int)` · line 101

**Does:** Internal helper.

**Needs:**
- Parameters: `context: Dict[str, str], snapshot: Dict[str, Any], decimal_places: int`

**Calls:**
- `list`
- `snapshot.items`
- `re.match`
- `match.group`
- `_format_template_scalar`

**Returns:** None

##### `_apply_structure_column_variants(context: Dict[str, str], snapshot: Dict[str, Any], decimal_places: int)` · line 111

**Does:** Duplicate snapshot values under common placeholder spellings (case variants).

**Needs:**
- Parameters: `context: Dict[str, str], snapshot: Dict[str, Any], decimal_places: int`

**Calls:**
- `snapshot.items`
- `sql_col.startswith`
- `_format_udint_timestamp`
- `_format_template_scalar`
- `sql_col.split`
- `variants.add`
- `'_'.join`
- `p[:1].upper`
- `len`
- `parts[0][:1].upper`
- `p.lower`

**Returns:** None

##### `placeholder_to_sql_column(placeholder: str, structure: ResultsStructure)` · line 134

**Does:** Resolve a report.html placeholder to a snapshot SQL column when possible.

**Needs:**
- Parameters: `placeholder: str, structure: ResultsStructure`

**Calls:**
- `_reverse_template_aliases`
- `placeholder.lower`
- `re.match`
- `match.group`
- `structure.member_short_names`
- `member_to_column`
- `col.lower`
- `member.replace(' ', '_').lower`
- `member.replace`

**Returns:** Optional[str]

##### `verify_template_placeholder_mapping(templates_root: Path, structures: Dict[str, ResultsStructure])` · line 151

**Does:** Return ``folder:placeholder`` entries that cannot be resolved from a full mock snapshot.
Optional static placeholders (Manufacturer, etc.) are allowed to remain empty.

**Needs:**
- Parameters: `templates_root: Path, structures: Dict[str, ResultsStructure]`

**Calls:**
- `HTML_TEMPLATE_FOLDER_MAP.items`
- `rev_folders.setdefault`
- `list_expected_html_template_folders`
- `template_path.is_file`
- `failures.append`
- `rev_folders.get`
- `structures.get`
- `structure.member_short_names`
- `member_to_column`
- `col.lower`
- `col.endswith`
- `snapshot.setdefault`
- `template_path.read_text`
- `build_template_context`
- `render_html_template`
- `set`
- `_PLACEHOLDER_RE.findall`
- `context.get`

**Returns:** List[str]

##### `resolve_report_template_key(device_tag: str, results_type: str)` · line 201

**Does:** Return the report layout key for Step 6 (§3.4 SAMSON FST/PST).

**Needs:**
- Parameters: `device_tag: str, results_type: str`

**Calls:**
- `device_tag.upper`
- `tag_upper.endswith`

**Returns:** str

##### `auto_template_folder_name(results_type: str)` · line 218

**Does:** Folder name for a generated report template (new Results types).

**Needs:**
- Parameters: `results_type: str`

**Calls:**
- `results_type_folder_name`

**Returns:** str

##### `resolve_html_template_folder(device_tag: str, results_type: str)` · line 223

**Does:** Folder name under ``report_html_templates``, or None when no template exists.

**Needs:**
- Parameters: `device_tag: str, results_type: str`

**Calls:**
- `resolve_report_template_key`
- `HTML_TEMPLATE_FOLDER_MAP.get`
- `auto_template_folder_name`

**Returns:** Optional[str]

##### `list_expected_html_template_folders()` · line 232

**Does:** All HIMA HTML template folders required for the nine Results types.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `folders.extend`
- `_SAMSON_HTML_FOLDERS.values`
- `folders.append`
- `sorted`
- `set`

**Returns:** List[str]

##### `verify_html_templates(templates_root: Path)` · line 243

**Does:** Return folder names missing ``report.html`` under ``templates_root``.

**Needs:**
- Parameters: `templates_root: Path`

**Calls:**
- `list_expected_html_template_folders`
- `(templates_root / folder / 'report.html').is_file`
- `missing.append`

**Returns:** List[str]

##### `resolve_html_template_path(templates_root: Path, device_tag: str, results_type: str)` · line 252

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `templates_root: Path, device_tag: str, results_type: str`

**Calls:**
- `resolve_html_template_folder`
- `path.is_file`
- `auto_template_folder_name`
- `alt.is_file`

**Returns:** Optional[Path]

##### `resolve_html_templates_seed(seed_root: Path | None = None, config = None)` · line 268

**Does:** Resolve HTML template seed directory (R2).

**Needs:**
- Parameters: `seed_root: Path | None = None, config = None`

**Calls:**
- `candidates.append`
- `Path`
- `getattr`
- `Path(__file__).resolve`
- `path.is_dir`

**Returns:** tuple[Optional[Path], str]

##### `_package_html_templates_seed()` · line 303

**Does:** Best-effort seed path; prefer resolve_html_templates_seed for callers.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `resolve_html_templates_seed`
- `Path`

**Returns:** Path

##### `seed_known_report_templates(templates_root: Path, seed_root: Path | None = None, config = None)` · line 309

**Does:** Copy baseline HIMA report template folders into the station templates dir.

**Needs:**
- Parameters: `templates_root: Path, seed_root: Path | None = None, config = None`

**Calls:**
- `logging.getLogger`
- `resolve_html_templates_seed`
- `src.is_dir`
- `log.warning`
- `log.info`
- `templates_root.mkdir`
- `list_expected_html_template_folders`
- `src_dir.is_dir`
- `(dest_dir / 'report.html').is_file`
- `shutil.copytree`

**Returns:** int

##### `build_auto_report_template_html(structure: ResultsStructure)` · line 344

**Does:** Generate a Proof-test report.html from a Results Structure CSV definition.

**Needs:**
- Parameters: `structure: ResultsStructure`

**Calls:**
- `html.escape`
- `structure.type_name.replace('X-HART_', '').replace('_Results', '').replace`
- `structure.type_name.replace('X-HART_', '').replace`
- `structure.type_name.replace`
- `member_to_column`
- `col.replace`
- `rows.append`
- `''.join`

**Returns:** str

##### `ensure_report_template_for_structure(templates_root: Path, structure: ResultsStructure, seed_root = None)` · line 399

**Does:** Ensure a report.html exists for this Results type.

**Needs:**
- Parameters: `templates_root: Path, structure: ResultsStructure, seed_root = None`

**Calls:**
- `templates_root.mkdir`
- `HTML_TEMPLATE_FOLDER_MAP.get`
- `seed_known_report_templates`
- `_SAMSON_HTML_FOLDERS.values`
- `path.is_file`
- `auto_template_folder_name`
- `dest.is_file`
- `dest_dir.mkdir`
- `dest.write_text`
- `build_auto_report_template_html`
- `Path`
- `_package_html_templates_seed`
- `img.is_dir`
- `(seed / candidate / 'img').is_dir`
- `shutil.copytree`
- `(dest_dir / 'img').exists`

**Returns:** Path

##### `ensure_report_templates_for_structures(templates_root: Path, structures: Dict[str, ResultsStructure], seed_root = None)` · line 457

**Does:** Ensure every loaded Results type has a Proof-test report template.

**Needs:**
- Parameters: `templates_root: Path, structures: Dict[str, ResultsStructure], seed_root = None`

**Calls:**
- `seed_known_report_templates`
- `structures.values`
- `written.append`
- `ensure_report_template_for_structure`

**Returns:** List[Path]

##### `device_report_dir(output_root: Path, device_tag: str, results_type: str, project: str = '')` · line 473

**Does:** ``<root>/<Results_Type>/<Project>/<Device_TAG>/`` when project is set; else tag-only (legacy).

**Needs:**
- Parameters: `output_root: Path, device_tag: str, results_type: str, project: str = ''`

**Calls:**
- `results_type_folder_name`
- `sanitize_device_tag_for_path`

**Returns:** Path

##### `result_line_text(snapshot: Dict[str, Any])` · line 486

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `snapshot: Dict[str, Any]`

**Calls:**
- `snapshot.get`

**Returns:** str

##### `format_value(value: Any, decimal_places: int = 3)` · line 500

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `value: Any, decimal_places: int = 3`

**Calls:**
- `isinstance`
- `str`

**Returns:** str

##### `_format_template_scalar(value: Any, decimal_places: int)` · line 510

**Does:** Internal helper.

**Needs:**
- Parameters: `value: Any, decimal_places: int`

**Calls:**
- `isinstance`
- `math.isnan`
- `str`

**Returns:** str

##### `_format_udint_timestamp(value: Any)` · line 524

**Does:** Internal helper.

**Needs:**
- Parameters: `value: Any`

**Calls:**
- `int`
- `datetime.fromtimestamp(seconds, tz=timezone.utc).strftime`
- `datetime.fromtimestamp`
- `str`

**Returns:** str

##### `_error_code_byte_fields(error_code: Any)` · line 532

**Does:** Internal helper.

**Needs:**
- Parameters: `error_code: Any`

**Calls:**
- `int`

**Returns:** Dict[str, int]

##### `build_template_context(device_tag: str, snapshot: Dict[str, Any], decimal_places = 3)` · line 545

**Does:** Map SQL snapshot columns to ``$(placeholder)`` values for report.html.

**Needs:**
- Parameters: `device_tag: str, snapshot: Dict[str, Any], decimal_places = 3`

**Calls:**
- `str`
- `snapshot.items`
- `key.startswith`
- `_format_udint_timestamp`
- `_format_template_scalar`
- `_TEMPLATE_ALIASES.items`
- `snapshot.get`
- `_apply_numeric_test_point_aliases`
- `_apply_structure_column_variants`
- `_error_code_byte_fields(error_code).items`
- `_error_code_byte_fields`

**Returns:** Dict[str, str]

##### `render_html_template(template_html: str, context: Dict[str, str])` · line 607

**Does:** Replace ``$(Name)`` placeholders; lookup is case-insensitive on ``Name``.

**Needs:**
- Parameters: `template_html: str, context: Dict[str, str]`

**Calls:**
- `key.lower`
- `context.items`
- `_PLACEHOLDER_RE.sub`

**Returns:** str

##### `copy_template_assets(template_dir: Path, output_dir: Path)` · line 620

**Does:** Copy ``img/`` (CSS, logos) beside the generated report.html.

**Needs:**
- Parameters: `template_dir: Path, output_dir: Path`

**Calls:**
- `src_img.is_dir`
- `dest_img.mkdir`
- `src_img.iterdir`
- `item.name.lower`
- `item.is_dir`
- `shutil.copytree`
- `shutil.copy2`

**Returns:** None

##### `build_html_report_from_template(templates_root: Path, device_tag: str, results_type: str, snapshot: Dict[str, Any], decimal_places = 3)` · line 641

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `templates_root: Path, device_tag: str, results_type: str, snapshot: Dict[str, Any], decimal_places = 3`

**Calls:**
- `resolve_html_template_path`
- `template_path.read_text`
- `build_template_context`
- `render_html_template`

**Returns:** Optional[str]

##### `build_html_report(device_tag: str, results_type: str, snapshot: Dict[str, Any], quality_notes = None, decimal_places = 3, template_key = None, templates_root = None)` · line 657

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `device_tag: str, results_type: str, snapshot: Dict[str, Any], quality_notes = None, decimal_places = 3, template_key = None, templates_root = None`

**Calls:**
- `build_html_report_from_template`
- `resolve_report_template_key`
- `result_line_text`
- `sorted`
- `snapshot.items`
- `key.startswith`
- `rows.append`
- `html.escape`
- `str`
- `format_value`
- `'; '.join`
- `datetime.now().strftime`
- `datetime.now`
- `''.join`

**Returns:** str

##### `write_reports(config: AppConfig, device_tag: str, results_type: str, snapshot: Dict[str, Any], quality_notes = None, project = '')` · line 725

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `config: AppConfig, device_tag: str, results_type: str, snapshot: Dict[str, Any], quality_notes = None, project = ''`

**Calls:**
- `device_report_dir`
- `output_dir.mkdir`
- `mirror_dir.resolve`
- `output_dir.resolve`
- `str`
- `mirror_dir.mkdir`
- `datetime.now().strftime`
- `datetime.now`
- `sanitize_device_tag_for_path`
- `resolve_html_template_path`
- `build_html_report`
- `html_path.write_text`
- `copy_template_assets`
- `shutil.copy2`
- `written.append`
- `(output_dir / f'{base_name}.html').is_file`
- `HTML(filename=str(output_dir / f'{base_name}.html'), base_url=str(output_dir)).write_pdf`
- `HTML`
- `HTML(string=html_body).write_pdf`
- `fallback.write_text`

**Returns:** List[str]

##### `parse_hima_html_snapshot(html_text: str)` · line 848

**Does:** Best-effort extract field values from a rendered HIMA ``report.html``.

**Needs:**
- Parameters: `html_text: str`

**Calls:**
- `_LABEL_VALUE_RE.finditer`
- `re.sub('\\s+', ' ', match.group(1)).strip().lower`
- `re.sub('\\s+', ' ', match.group(1)).strip`
- `re.sub`
- `match.group`
- `html.unescape`
- `match.group(2).strip`
- `_HIMA_LABEL_KEYS.get`
- `value.lower`
- `re.search`
- `summary.group(1).lower`
- `summary.group`
- `range`
- `re.compile`
- `row_re.finditer`
- `m.group`
- `m.group(2).strip`
- `m.group(3).strip`
- `test_val.lower`
- `test_val.replace(' mA', '').strip`
- `test_val.replace`
- `actual_val.lower`
- `actual_val.replace(' mA', '').strip`
- `actual_val.replace`

**Returns:** Dict[str, Any]

##### `merge_snapshots_prefer_existing(base: Dict[str, Any], overlay: Dict[str, Any])` · line 892

**Does:** Merge snapshots; keep non-empty ``base`` values, fill gaps from ``overlay``.

**Needs:**
- Parameters: `base: Dict[str, Any], overlay: Dict[str, Any]`

**Calls:**
- `dict`
- `base.items`
- `isinstance`
- `math.isnan`
- `val.strip`

**Returns:** Dict[str, Any]

##### `results_type_from_folder(folder_name: str)` · line 906

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `folder_name: str`

**Calls:**
- `results_type_folder_name`

**Returns:** Optional[str]

##### `device_tag_from_report_path(html_path: Path)` · line 913

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `html_path: Path`

**Calls:**
- `re.match`
- `m.group`

**Returns:** str

##### `rewrite_report_at_path(html_path: Path, config: AppConfig, results_type: str, device_tag: str, snapshot: Dict[str, Any], quality_notes = None)` · line 921

**Does:** Re-render a HIMA template report in place at ``html_path``.

**Needs:**
- Parameters: `html_path: Path, config: AppConfig, results_type: str, device_tag: str, snapshot: Dict[str, Any], quality_notes = None`

**Calls:**
- `html_path.read_text`
- `build_html_report`
- `html_path.write_text`
- `resolve_html_template_path`
- `copy_template_assets`

**Returns:** bool

##### `list_reports_for_device(output_dir: Path, device_tag: str, results_type = None, project = None, device_id = None)` · line 950

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `output_dir: Path, device_tag: str, results_type = None, project = None, device_id = None`

**Calls:**
- `DeviceId.from_key`
- `sanitize_device_tag_for_path`
- `_dirs_for_type`
- `results_type_folder_name`
- `output_dir.is_dir`
- `output_dir.iterdir`
- `type_dir.is_dir`
- `folder.is_dir`
- `folder.glob`
- `path.suffix.lower`
- `files.append`
- `str`
- `datetime.fromtimestamp(path.stat().st_mtime).isoformat`
- `datetime.fromtimestamp`
- `path.stat`
- `files.sort`

**Returns:** List[Dict[str, str]]

##### `encode_report_dir_token(report_dir: Path)` · line 1004

**Does:** URL-safe token for a report folder (used by ``/api/reports/asset/``).

**Needs:**
- Parameters: `report_dir: Path`

**Calls:**
- `base64.urlsafe_b64encode(str(report_dir.resolve()).encode('utf-8')).decode('ascii').rstrip`
- `base64.urlsafe_b64encode(str(report_dir.resolve()).encode('utf-8')).decode`
- `base64.urlsafe_b64encode`
- `str(report_dir.resolve()).encode`
- `str`
- `report_dir.resolve`

**Returns:** str

##### `decode_report_dir_token(token: str, allowed_roots: Sequence[Path])` · line 1009

**Does:** Decode ``encode_report_dir_token``; return None when outside allowed report roots.

**Needs:**
- Parameters: `token: str, allowed_roots: Sequence[Path]`

**Calls:**
- `len`
- `Path(base64.urlsafe_b64decode(padded.encode('ascii')).decode('utf-8')).resolve`
- `Path`
- `base64.urlsafe_b64decode(padded.encode('ascii')).decode`
- `base64.urlsafe_b64decode`
- `padded.encode`
- `report_dir.relative_to`
- `root.resolve`

**Returns:** Optional[Path]

##### `inject_report_base_href(html_text: str, base_href: str)` · line 1027

**Does:** Insert ``<base href=...>`` so relative ``img/`` assets load over HTTP.

**Needs:**
- Parameters: `html_text: str, base_href: str`

**Calls:**
- `re.search`
- `html.escape`
- `match.end`

**Returns:** str

##### `prepare_report_html_for_http(html_text: str, report_file: Path)` · line 1039

**Does:** Rewrite HIMA template HTML so CSS/logos resolve when opened from the web UI.

**Needs:**
- Parameters: `html_text: str, report_file: Path`

**Calls:**
- `encode_report_dir_token`
- `inject_report_base_href`

**Returns:** str

---

## Infrastructure — Shutdown

### File `Annex codes/Stop service/annex_silworx_cleanup.py`

**Layer:** Infrastructure — Shutdown

**Module purpose:** *(no module docstring)*

#### Module-level functions *(no class)*

##### `close_grace_sec()` · line 34

**Does:** *(no docstring — read source)*

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `*(no direct calls detected)*`

**Returns:** float

##### `_query_processes(name_pattern: str)` · line 38

**Does:** Internal helper.

**Needs:**
- Parameters: `name_pattern: str`

**Calls:**
- `subprocess.run`
- `result.stdout.strip`
- `json.loads`
- `log.debug`
- `isinstance`

**Returns:** List[dict]

##### `list_c3_processes()` · line 66

**Does:** Return running c3.exe processes only.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `_query_processes`
- `str`
- `row.get`
- `name.lower`
- `int`
- `procs.append`
- `C3Process`

**Returns:** List[C3Process]

##### `has_olixclient()` · line 87

**Does:** True when the SILworX GUI helper (OLixClient.exe) is running.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `bool`
- `_query_processes`

**Returns:** bool

##### `is_silworx_session_active(silworx_open)` · line 92

**Does:** True when SILworX is open or its GUI is running.

**Needs:**
- Parameters: `silworx_open`

**Calls:**
- `has_olixclient`

**Returns:** bool

##### `should_kill_c3_after_close(session_was_active, session_active, close_detected_at, now, grace_sec = _SILWORX_CLOSE_GRACE_SEC)` · line 103

**Does:** True only after a confirmed SILworX close (session was active, now inactive)
and the grace period has elapsed.

**Needs:**
- Parameters: `session_was_active, session_active, close_detected_at, now, grace_sec = _SILWORX_CLOSE_GRACE_SEC`

**Calls:**
- `bool`
- `list_c3_processes`

**Returns:** bool

##### `kill_leftover_c3_after_close(config: AppConfig, force = True)` · line 124

**Does:** Terminate leftover c3.exe processes after confirmed SILworX close (G-20).

**Needs:**
- Parameters: `config: AppConfig, force = True`

**Calls:**
- `list_c3_processes`
- `CleanupResult`
- `log.warning`
- `len`
- `', '.join`
- `str`
- `cmd.append`
- `subprocess.run`
- `killed.append`
- `skipped.append`

**Returns:** CleanupResult

#### Class `C3Process` · line 18

**Inherits:** `—`

**Purpose:** *(no class docstring)*

*(no methods)*

#### Class `CleanupResult` · line 25

**Inherits:** `—`

**Purpose:** *(no class docstring)*

##### `changed(self)` · line 30

**Does:** *(no docstring — read source)*

**Needs:**
- Uses instance: `self.killed`

**Calls:**
- `bool`

**Returns:** bool

### File `Annex codes/Stop service/annex_stop_service.py`

**Layer:** Infrastructure — Shutdown

**Module purpose:** Annex — graceful service shutdown (G-11).

#### Module-level functions *(no class)*

##### `clear_stop_in_progress(service, reason = '')` · line 18

**Does:** Always clear the UI 'Stopping' flag and drop stale health cache.

**Needs:**
- Parameters: `service, reason = ''`

**Calls:**
- `log.info`

**Returns:** None

##### `perform_graceful_shutdown(service, reason: str = '')` · line 33

**Does:** Release OPC, SILworX API, monitor, DB — used by ProoftestService.stop().

**Needs:**
- Parameters: `service, reason: str = ''`

**Calls:**
- `log.info`
- `service._stop.set`
- `service._case1_sync.shutdown`
- `log.warning`
- `service.monitor.shutdown`
- `service.db.interrupt_open_tests`
- `service.opc.invalidate_cache`
- `threading.current_thread`
- `list`
- `getattr`
- `thread.join`
- `thread.is_alive`
- `service.db.set_service_state`
- `time.strftime`
- `service.db.close`
- `clear_stop_in_progress`

**Returns:** None

---

## Runtime

### File `Annex codes/layers/__init__.py`

**Layer:** Runtime

**Module purpose:** Presentation / Application / Domain / ports — no FastAPI, OpenOPC, or pyodbc here.

*(empty module)*

### File `Annex codes/prooftest/__init__.py`

**Layer:** Runtime

**Module purpose:** Bootstrap package for the HIMA Prooftest solution (SPEC-001 v1.23).

Maps ``prooftest.*`` imports to ``Tool Steps/``, annex modules to ``Annex codes/``,
and the web app to ``Graphic Interface/``.

#### Module-level functions *(no class)*

##### `_load_module(qualified_name: str, file_path: Path)` · line 35

**Does:** Internal helper.

**Needs:**
- Parameters: `qualified_name: str, file_path: Path`

**Calls:**
- `importlib.util.spec_from_file_location`
- `ImportError`
- `importlib.util.module_from_spec`
- `spec.loader.exec_module`

**Returns:** ModuleType

##### `_bootstrap()` · line 62

**Does:** Internal helper.

**Needs:**
- No parameters beyond `self`/`cls`.

**Calls:**
- `str`
- `sys.path.insert`
- `any`
- `isinstance`
- `sys.meta_path.insert`
- `_ProoftestFinder`
- `_ANNEX_MODULES.items`
- `_load_module`
- `ModuleType`
- `setattr`

**Returns:** None

#### Class `_ProoftestFinder` · line 47

**Inherits:** `importlib.abc.MetaPathFinder`

**Purpose:** *(no class docstring)*

##### `find_spec(self, fullname: str, path, target = None)` · line 48

**Does:** *(no docstring — read source)*

**Needs:**
- Parameters: `fullname: str, path, target = None`

**Calls:**
- `fullname.startswith`
- `fullname.split`
- `len`
- `py.is_file`
- `importlib.util.spec_from_file_location`

**Returns:** `None` (inferred)

---
