# Device list path — Step 3 (API and OPC together)

```mermaid
flowchart TD
    A["Need device list update / refresh"] --> P["Start SILworX API and X-OPC together"]
    P --> API["SILworX API<br/>attach if user has a project open<br/>never open/local"]
    P --> OPC["X-OPC browse<br/>match Results .Running trees"]
    API --> M["Merge one Device Prooftest Result List"]
    OPC --> M
    M --> H["API wins Results_Type · Configuration · Resource<br/>OPC wins server · prefix · PresentOnOpc"]
    H --> S["device_list_source:<br/>api+opc · api · opc_fallback"]
```

## API session

| Situation | How session token is obtained |
|-----------|------------------------------|
| Engineer has project open | Plugin WebSocket `TRIGGER_SESSION_ID_CHANGED` |
| No GUI project open | API contribution is empty — **never** `POST /project/open/local` |

## What counts as a device

A top-level **global variable** whose **data type** is one of the nine `*_Results` structures, **or** an X-OPC `.Running` tree that matches a Results type.  
Those types are defined by the Results Structures CSV **type catalogue** (members for SQL/OPC).  
**Adding a device** = create that global in SILworX (and/or download so it appears on OPC) — do **not** edit the CSV files.
