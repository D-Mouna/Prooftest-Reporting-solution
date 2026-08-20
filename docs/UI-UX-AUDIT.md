# UI/UX audit — Graphic Interface

| Field | Value |
|-------|--------|
| **Files** | `Graphic Interface/static/index.html`, `app.js`, `style.css` |
| **Date** | 2026-08-20 |

## Checklist

| # | Requirement | Result | Notes / fix |
|---|-------------|--------|-------------|
| 1 | Project + OPC server columns; sort TAG→Project→OPC | **Pass** | Columns in `index.html`; server `sort_device_dicts`; **client sort added** in `app.js` |
| 2 | Empty states clear | **Pass** | Placeholders “(No device available)” / reports empty |
| 3 | SILworX badge = this tool | **Pass after fix** | Card “SILworX (this tool)”; values “tool attached” / “tool not connected” |
| 4 | Connect with no project | **Pass (code path)** | Resume returns status; alarms; OPC catalog remains via unified refresh |
| 5 | Disconnect keeps engine | **Pass** | CloseSilworX does not stop engine; OPC fallback |
| 6 | Errors in UI | **Pass** | Alarm list + banners |
| 7 | Localhost-only start/stop/connect | **Pass** | Controllers 403 non-local |
| 8 | Layout / wording | **Medium** | Removed “unified (case N)” Case wording |
| 9 | Misleading Case 1/2 / Shutdown labels | **Mostly clear** | Stop vs Shutdown remain distinct in API |

## Findings

| Severity | Finding | Fix |
|----------|---------|-----|
| Medium | Badge said “running” like SILworX.exe | Renamed to tool-attached wording |
| Low | Sort only server-side | Added client sort |
| Low | “unified (case N)” | Now “unified” |

## Screenshot notes

Not captured in this pass (headless). Verify manually: Desktop shortcut **HIMA Prooftest Report** → health row shows “SILworX (this tool)”; device table five columns including Project and OPC server.
