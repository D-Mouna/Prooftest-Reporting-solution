# Architecture as built (not the ideal prompt)

| Field | Value |
|-------|--------|
| **Code** | HIMA-Prooftest-Solution-Current **1.74+** |
| **Date** | 2026-08-20 |

## Hub diagram (what exists now)

```mermaid
flowchart LR
  UI[Web GUI<br/>Graphic Interface]
  Pres[Presentation<br/>controllers.py]
  App[ApplicationFacade]
  Cat[CatalogService]
  Live[LiveTestService]
  Q[QueryService]
  SilC[SilworxConnectionService]
  Dom[Domain<br/>DeviceId Merger Edges]
  Ports[Ports / Adapters]
  Host[WorkerHost<br/>ProoftestService]
  OPC[OPC Classic DA]
  API[SILworX REST/Plugin]
  DB[(SQL / SQLite)]
  PDF[PDF/HTML reports]

  UI --> Pres --> App
  App --> Cat
  App --> Live
  App --> Q
  App --> SilC
  Cat --> Dom
  Live --> Dom
  Cat --> Ports
  Live --> Ports
  Q --> Ports
  SilC --> Ports
  Ports --> OPC
  Ports --> API
  Ports --> DB
  Ports --> PDF
  Host --> App
  Host --> OPC
  Host --> API
  Cat -.->|run_station_refresh still calls| Step03[step03 sync_device_list_case1_via_api]
  Step03 --> Dom
  Step03 --> OPC
  Step03 --> API
  Step03 --> DB
```

## Implemented vs missing

| Piece | Status |
|-------|--------|
| Presentation → Application only | **Implemented** (1.74) |
| DeviceId composite | **Implemented** |
| Close/Resume SILworX (tool only) | **Implemented** |
| GUI Project / OPC columns | **Implemented** |
| Domain merger + edge detector | **Implemented** |
| Single production refresh without step03 | **Missing** (delegates to step03) |
| OPC-only without CSV score | **Missing** |
| LiveTestService-only poll | **Missing** (step05 monitor still production) |

## Station vs code

- **Code:** Documents `...\HIMA-Prooftest-Solution-Current`
- **Data:** `C:\HIMA Prooftest Reporting Tool\` (Reports, Results Structures, Database)
