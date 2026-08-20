# SILworX plugin layer (G-22)

## Roles (v1.27)

| Layer | Responsibility | Module |
|-------|----------------|--------|
| **REST API** | Device list, Results_Type, Configuration, Resource | `step03_device_list.py`, `annex_api_connexion.py` |
| **Plugin monitor** | Persistent WebSocket on ports `8400`–`8409`; session open/close signals | `annex_plugin_monitor.py` |
| **Session folders** | Project modify + code generation (`c3data` mtime), download (`.E3` mtime) | `step07_triggers.py` |
| **OPC** | Realtime values only — independent 1 s poll loop | `step05_detection.py`, `annex_opc.py` |

SILworX exposes only `TRIGGER_SESSION_ID_CHANGED` and `TRIGGER_VALIDATE` on the plugin WebSocket.
There are **no** native plugin events for code generation or download — those remain file-based watchers on **all** open sessions.

## Manual SILworX setup (required)

`C:\ProgramData\SILworX_v*\settings\settings.ini`:

```ini
[Plugin_Server]
Development=prooftest_session_plugin
```

## Plugin runtime

The **background service** runs the plugin monitor (`annex_plugin_monitor.py`) when
`plugin_monitor_enabled = true` in `solution.ini`. Standalone `annex_plugin.py` /
`run_plugin*.ps1` helpers were removed; use the service monitor only.

## Triggers → API re-read

On any trigger, `service.refresh()` re-reads open projects via REST API on all reachable instances (G-21).
When a project is opened, the monitor **re-registers** so REST attach uses a new `user_session_id` (SPEC v1.53).

```ini
sync_triggers = silworx_session, code_generation, download, results_structures
```

## Verify

Service logs (match against SILworX Plug-In Server log):

| Log line | Meaning |
|----------|---------|
| `plugin monitor connected api=51710 plugin=8400 ...` | Persistent listener — should stay registered in SILworX |
| `plugin monitor disconnected api=... plugin=...` | WebSocket lost or service stopped |
| `plugin monitor active — waiting for session cache ...` | API refresh waits on monitor cache (no second register) |
| `plugin one-shot connected ...` | One-shot bridge only when monitor is off or not running |
| `plugin session from monitor cache api=...` | API read reused monitor token (no extra register) |
| `plugin monitor fresh-session requested ...` | Cached token dropped after project open / rejected session |
| `plugin monitor re-registering ...` | WebSocket reconnect to obtain a new `user_session_id` |

```powershell
cd "Annex codes\Tool test"
& "C:\Python 312_32bit\python.exe" test_step8_triggers.py
```
