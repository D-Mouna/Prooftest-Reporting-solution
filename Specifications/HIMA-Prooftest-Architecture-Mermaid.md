# HIMA Automated Prooftest — Mermaid Architecture

| Field | Value |
|-------|--------|
| **Document** | Architecture diagrams (Mermaid) |
| **Runtime** | `HIMA-Prooftest-Solution-Current` |
| **Paired SPEC** | SPEC-001 v1.59 |
| **Related** | [HIMA-Prooftest-Functionality-and-Architecture.md](./HIMA-Prooftest-Functionality-and-Architecture.md) |
| **Pictures** | [architecture-diagrams/](./architecture-diagrams/) |
| **Updated** | 2026-08-18 |

> Render in any Mermaid-capable viewer. PNGs/SVGs under `architecture-diagrams\` match these diagrams (`01`–`11`).

---

## 1. System context (unified mode)

```mermaid
flowchart TB
  subgraph MODE["Unified operating mode — engineering or HMI"]
    SW[SILworX GUI / API<br/>optional · 51710–51719 · plugin 8400–8409]
    OPC[X-OPC server<br/>required]
    SOL[Report Solution]
    ROOT["C:\\HIMA Prooftest Reporting Tool<br/>Database · Reports · Results Structures"]
    UI[Web UI :8080]

    SW <-->|API when a project is open| SOL
    OPC <-->|"Realtime always · device list always (parallel with API)"| SOL
    SOL --> ROOT
    SOL --> UI
  end
```

---

## 2. Process and thread architecture

```mermaid
flowchart TB
  MAIN["python main.py"]

  MAIN --> UV["uvicorn / FastAPI :8080"]
  MAIN --> SVC["ProoftestService"]

  SVC --> POLL["poll-loop ~1s<br/>OPC Running + Results"]
  SVC --> SYNC["sync-loop ~0.5s<br/>triggers · G-19 · G-20 · G-11<br/>device list API+OPC if API down"]
  SVC --> PM["plugin-monitor<br/>WSS 8400–8409 Development plugin"]
  SVC --> RW["report-worker<br/>SQL + HTML/PDF"]
  SVC --> DISK["Station root on C:"]
  SVC --> OPC[X-OPC]
  SVC --> API[SILworX REST API]

  UV -->|/api/stop| SVC
  UV -->|/api/start| SVC
  UV -->|/api/shutdown optional exit| MAIN
```

---

## 3. G-22 three-layer architecture

```mermaid
flowchart LR
  subgraph DATA["1 — Data layer"]
    API[SILworX API globals]
    OPCSCAN[X-OPC browse<br/>always with API]
    DEV[(DeviceProoftestResultList)]
    API --> DEV
    OPCSCAN --> DEV
  end

  subgraph TRIG["2 — Trigger layer"]
    PLG[Plugin session open/close]
    FS[c3data / .E3 watchers]
    CSV[New Results CSV<br/>→ type + SQL + template]
    OPCPOLL[OPC device poll<br/>while API down]
    REF[service.refresh / sync]
    PLG --> REF
    FS --> REF
    CSV --> REF
    OPCPOLL --> OPCSCAN
    REF --> DATA
  end

  subgraph RT["3 — Realtime layer"]
    POLL[poll-loop]
    OPC[X-OPC reads]
    DET[Running edge]
    POLL --> OPC --> DET
  end

  DET -->|test end| SNAP[Snapshot → SQL → Report]
  TRIG -.->|never blocks| RT
```

---

## 4. Device list (API and OPC together)

```mermaid
flowchart TD
  NEED[Need device list update / refresh] --> P[Start SILworX API and X-OPC together]
  P --> API["Attach REST if user has a project open<br/>never open/local · structuretree + globals"]
  P --> OPC[Scan X-OPC servers<br/>match Results types]
  API --> MERGE[Merge one DeviceProoftestResultList]
  OPC --> MERGE
  MERGE --> SRC["ServiceState.device_list_source<br/>api+opc · api · opc_fallback"]
```

---

## 5. End-to-end runtime pipeline

```mermaid
sequenceDiagram
  participant Op as Operator
  participant UI as Web UI
  participant Svc as ProoftestService
  participant SIL as SILworX API
  participant OPC as X-OPC
  participant Disk as Station root C:
  participant DB as SQL DB

  Op->>UI: run_service / Start
  UI->>Svc: start engine
  Svc->>Disk: create Database · Reports · Results Structures
  Svc->>DB: CREATE tables from CSVs
  par Device list together
    opt User has SILworX project open
      Svc->>SIL: plugin user_session_id + REST header HIMA_SAPI_user_session_id
      Svc->>SIL: attach structuretree + globals
    end
    Svc->>OPC: device list scan
  end
  Svc->>OPC: discover servers

  loop poll-loop ~1s
    Svc->>OPC: Running + Results
    alt test end
      Svc->>DB: INSERT ProofTest_*
      Svc->>Disk: HTML/PDF under Reports
    end
  end

  loop sync-loop
    alt API up
      Svc->>SIL: triggers / G-19 health
    else API down
      Svc->>SIL: API attach attempt (no-op if suspended)
      Svc->>OPC: periodic device-list scan
    end
  end

  Note over Svc,Disk: G-11 uninstall: release API/plugin/c3 — keep running on OPC (unified)
  Op->>UI: Stop = engine only · Shutdown = process exit optional
```

---

## 6. Multi-instance SILworX (attach only)

```mermaid
flowchart TB
  SCAN["Scan 51710/8400 … 51719/8409"]
  OPC[X-OPC device-list scan<br/>always started with API]
  SCAN --> Q{"User has a project open?"}
  Q -->|Yes| FRESH["Drop cached plugin session<br/>re-register WebSocket"]
  FRESH --> ATT["REST header HIMA_SAPI_user_session_id<br/>exact case via http.client<br/>read globals — never project/close"]
  Q -->|No| MERGE
  ATT --> MERGE[Merge API + OPC devices]
  SCAN -->|no instance reachable| MERGE
  OPC --> MERGE
  MERGE --> DB[(Device list)]
```

---

## 7. Prooftest data flow

```mermaid
flowchart LR
  DEV[Device in list] --> OPC[OPC item path]
  OPC --> RUN{Running?}
  RUN -->|rising| START[Test started]
  RUN -->|falling| SNAP[Snapshot Results]
  SNAP --> TBL[ProofTest_* row]
  TBL --> RPT["Reports\\Type\\TAG\\ HTML/PDF"]
  RPT --> PATH[ReportPath]
```

---

## 8. SILworX lifecycle vs solution

```mermaid
stateDiagram-v2
  [*] --> EngineRunning

  EngineRunning --> UserProjectOpen: user opens SILworX project
  EngineRunning --> OpcDevicePoll: no project open
  UserProjectOpen --> FreshPlugin: re-register plugin session
  FreshPlugin --> AttachSession: plugin attach + read globals
  AttachSession --> UserProjectOpen: refresh

  UserProjectOpen --> OpcDevicePoll: user closed project / G-19
  OpcDevicePoll --> UserProjectOpen: user opens project again

  UserProjectOpen --> C3Cleanup: G-20 after close grace
  OpcDevicePoll --> C3Cleanup: same

  UserProjectOpen --> OpcAfterUninstall: G-11 SILworX uninstalled
  OpcDevicePoll --> OpcAfterUninstall: G-11 SILworX uninstalled
  OpcAfterUninstall --> EngineRunning: keep process · OPC device list

  EngineRunning --> ProcessExit: /api/shutdown optional
  ProcessExit --> [*]
```

---

## 9. Station folder architecture

```mermaid
flowchart TB
  ROOT["C:\\HIMA Prooftest Reporting Tool"]
  ROOT --> DB["Database\\<br/>SQL files / SQLite + ProofTest_* tables"]
  ROOT --> RPT["HIMA Automated Prooftest Reports\\<br/>generated PDF/HTML"]
  RPT --> TPL["Report Templates\\<br/>seeded + auto for new CSV types"]
  ROOT --> RS["Results Structures\\<br/>*.csv type catalogue<br/>new CSV = new device type"]
```

---

## 10. Code / folder architecture

```mermaid
flowchart TB
  PKG["HIMA-Prooftest-Solution-Current"]
  PKG --> MAIN[main.py · solution.ini]
  PKG --> TS[Tool Steps]
  PKG --> AX[Annex codes]
  PKG --> GI[Graphic Interface]
  PKG --> SEED[Results Structures seed CSVs]

  TS --> S03[step03 device list API+OPC together]
  TS --> S07[step07 triggers G-11/G-19]
  AX --> PDF[PDF generation · auto templates]
  AX --> STP[Stop service · c3 cleanup]
  SEED -->|first start copy| STATION["C:\\HIMA Prooftest Reporting Tool\\Results Structures"]
```

---

## 11. Component deployment view

```mermaid
flowchart TB
  subgraph HOST["Windows station with X-OPC"]
    subgraph SOL["Report Solution process"]
      UI[Web UI]
      ENG[Engine threads]
    end
    DISK["C:\\HIMA Prooftest Reporting Tool<br/>Database · Reports · Results Structures"]
    OPC[X-OPC]
    SIL[SILworX optional]
  end

  UI --- ENG
  ENG <--> OPC
  ENG <-->|when available| SIL
  ENG --> DISK
  SIL -.->|G-11 uninstall| ENG
```

---

*End of document*
