# UI/UX audit — Graphic Interface

| Field | Value |
|-------|--------|
| **Files** | `Graphic Interface/static/index.html`, `app.js`, `style.css` |
| **Code** | **1.77.0** (`APP_VERSION`, `style.css?v=1.77.0`) |
| **Date** | 2026-08-20 |

## Checklist

| # | Requirement | Result | Notes / fix |
|---|-------------|--------|-------------|
| 1 | Project + OPC server columns; sort TAG→Project→OPC | **Pass** | Columns in `index.html`; server `sort_device_dicts`; client sort in `app.js` |
| 2 | Empty states clear | **Pass** | Placeholders “(No device available)” / reports empty |
| 3 | Unknown Results type placeholder | **Pass (1.77)** | Empty/blank type renders as **unknown** (`app.js`; `test_r7_unknown_results_type_placeholder`) |
| 4 | SILworX badge = this tool | **Pass** | Card “SILworX (this tool)”; values “tool attached” / “tool not connected” |
| 5 | Connect / Disconnect titles = this tool only | **Pass (1.77)** | Button `title`s state attach/detach only — no quit SILworX / no project close / no kill c3 (`test_r7_connect_button_titles`) |
| 6 | Connect with no project | **Pass (code path)** | Resume returns status; alarms; OPC catalog remains via unified refresh |
| 7 | Disconnect keeps engine | **Pass** | CloseSilworX does not stop engine; OPC fallback |
| 8 | Stop vs Shutdown distinct | **Pass** | **Stop service** stops engine, page stays open; **Shutdown** is separate `/api/shutdown` (host exit) — not confused with Disconnect |
| 9 | Errors in UI | **Pass** | Alarm list + banners |
| 10 | Localhost-only start/stop/connect | **Pass** | Controllers 403 non-local |
| 11 | escapeHtml on Project / OPC / type | **Pass** | `test_t24` + unknown type path |
| 12 | Layout / wording | **Pass** | No “unified (case N)” Case wording |
| 13 | Gate 11 version | **Pass** | App reports **1.77.0** |

## Findings

| Severity | Finding | Fix |
|----------|---------|-----|
| — | Prior Medium badge “running” like SILworX.exe | Already renamed to tool-attached wording |
| — | Unknown type blank in table | **1.77** shows `unknown` |
| — | Connect/Disconnect ambiguity | **1.77** explicit `title` tooltips |

## Screenshot notes

Skipped this pass (headless). Verify manually: Desktop shortcut **HIMA Prooftest Report** → health row shows “SILworX (this tool)”; device table five columns including Project and OPC server; blank type shows **unknown**; hover Connect/Disconnect for this-tool-only titles.
