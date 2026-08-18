# Architecture overview (G-22)

Three parallel layers on the host station. Device-list refresh queries SILworX API and X-OPC **at the same time**.

```mermaid
flowchart TB
    subgraph HOST["Host station — Report Solution"]
        SVC["Background service<br/>(ProoftestService)"]
        WEB["Web GUI :8080"]
        DB[("HIMA Automated Prooftest<br/>SQL Server / SQLite")]
        RPT["Report folders<br/>C:\\HIMA Automated Prooftest Reports"]
    end

    subgraph L1["Layer 1 — Metadata (API + OPC together)"]
        API["HTTPS API :51710–51719<br/>structuretree + globals read"]
        OPCB["X-OPC device-list browse"]
    end

    subgraph L2["Layer 2 — Change triggers"]
        PM["Plugin monitor :8400–8409<br/>TRIGGER_SESSION_ID_CHANGED"]
        FS["File watchers<br/>c3data · .E3 · CSV defs (rare)"]
    end

    subgraph L3["Layer 3 — Realtime (X-OPC, independent)"]
        OPC["OPC poll loop 1 s<br/>discover servers · read tags"]
    end

    SILworX["SILworX<br/>(engineering station)"]
    XOPC["X-OPC servers<br/>(HIMA / X_OPC*)"]

    SILworX --> API
    SILworX --> PM
    XOPC --> OPC
    XOPC --> OPCB

    PM -->|session open/close| REFRESH
    FS -->|modify · codegen · download · type CSV| REFRESH
    WEB -->|manual refresh| REFRESH
    REFRESH["service.refresh()"] --> API
    REFRESH --> OPCB
    API -->|Results_Type · Config/Resource| DB
    OPCB -->|union of tags · prefix · PresentOnOpc| DB

    OPC -->|Running edge · snapshot on complete| MON["ProoftestMonitor<br/>(Step 5)"]
    MON -->|SQL insert| DB
    MON -->|PDF/HTML| RPT

    SVC --> WEB
    SVC --> DB
```

## One-line summary

**REST API** and **X-OPC** both feed the device list on every refresh, then merge. **Plugin + file watchers** detect when metadata may have changed. **X-OPC poll** runs independently for live values, prooftest detection, snapshots, and reports.
