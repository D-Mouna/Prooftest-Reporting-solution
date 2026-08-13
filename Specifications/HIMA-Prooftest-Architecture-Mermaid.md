# HIMA Automated Prooftest — Mermaid Architecture

| Field | Value |
|-------|--------|
| **Document** | Architecture diagrams (Mermaid) |
| **Runtime** | `HIMA-Prooftest-Solution-Current` |
| **Paired SPEC** | SPEC-001 v1.44 |
| **Related** | [HIMA-Prooftest-Functionality-and-Architecture.md](./HIMA-Prooftest-Functionality-and-Architecture.md) |
| **Updated** | 2026-08-13 |

> Render in any Mermaid-capable viewer (GitHub, VS Code Markdown preview, Spec docs, etc.).

---

## 1. System context (Case 1 vs Case 2)

```mermaid
flowchart TB
  subgraph CASE1["Case 1 — Engineering station"]
    SW1[SILworX GUI / API<br/>ports 51710–51719]
    OPC1[X-OPC server]
    SOL1[Report Solution<br/>Current]
    DB1[(HIMA Automated Prooftest)]
    RPT1[C:\HIMA Automated Prooftest Reports]
    UI1[Web UI :8080]

    SW1 <-->|API Mode A/B + plugin 8400–8409| SOL1
    OPC1 <-->|Realtime Results / Running| SOL1
    SOL1 --> DB1
    SOL1 --> RPT1
    SOL1 --> UI1
  end

  subgraph CASE2["Case 2 — HMI station"]
    SW2[SILworX remote<br/>not on this PC]
    OPC2[X-OPC server]
    SOL2[Report Solution<br/>Current]
    DB2[(HIMA Automated Prooftest)]
    RPT2[C:\HIMA Automated Prooftest Reports]
    UI2[Web UI :8080]

    SW2 -.->|no local API| SOL2
    OPC2 <-->|Device list + realtime| SOL2
    SOL2 --> DB2
    SOL2 --> RPT2
    SOL2 --> UI2
  end
```

---

## 2. Process and thread architecture

```mermaid
flowchart TB
  MAIN["python main.py"]

  MAIN --> UV["uvicorn / FastAPI<br/>Graphic Interface :8080"]
  MAIN --> SVC["ProoftestService"]

  SVC --> POLL["poll-loop ~1s<br/>OPC Running + Results"]
  SVC --> SYNC["sync-loop ~0.5s<br/>triggers · G-19 · G-20 · G-11"]
  SVC --> PM["plugin-monitor Case 1<br/>WSS 8400–8409"]
  SVC --> RW["report-worker<br/>SQL INSERT + HTML/PDF"]
  SVC --> DB[(SQL Server / SQLite)]
  SVC --> OPC[X-OPC COM]
  SVC --> API[SILworX REST API]

  UV -->|POST /api/stop| SVC
  UV -->|POST /api/start| SVC
  UV -->|POST /api/shutdown G-11| MAIN

  note1["UI Stop: engine threads stop, web stays<br/>G-11: whole process exits"]
```

---

## 3. G-22 three-layer architecture

```mermaid
flowchart LR
  subgraph DATA["1 — Data layer"]
    API[SILworX API<br/>structuretree + globals]
    OPCFB[OPC fallback / Case 2 browse]
    DEV[(DeviceProoftestResultList)]
    API --> DEV
    OPCFB --> DEV
  end

  subgraph TRIG["2 — Trigger layer"]
    PLG[Plugin monitors<br/>session open/close]
    FS[c3data / .E3 / CSV watchers]
    REF[service.refresh]
    PLG --> REF
    FS --> REF
    REF --> DATA
  end

  subgraph RT["3 — Realtime layer"]
    POLL[poll-loop]
    OPC[X-OPC reads]
    DET[Running edge detect]
    POLL --> OPC --> DET
  end

  DET -->|test end| SNAP[Snapshot → SQL → Report]
  TRIG -.->|never blocks| RT
```

---

## 4. End-to-end runtime pipeline

```mermaid
sequenceDiagram
  participant Op as Operator
  participant UI as Web UI :8080
  participant Svc as ProoftestService
  participant SIL as SILworX API
  participant OPC as X-OPC
  participant DB as SQL DB
  participant FS as Report folders

  Op->>UI: Start service / run_service.ps1
  UI->>Svc: start engine
  Svc->>Svc: first-run folders + CREATE DB/tables
  Svc->>SIL: discover instances / Mode A or B
  Svc->>OPC: discover servers
  Svc->>DB: upsert devices + schema
  Svc->>UI: engine_running

  loop Every ~1s poll-loop
    Svc->>OPC: read Running + Results
    alt Running false→true
      Svc->>DB: test_in_progress
    else Running true→false
      Svc->>OPC: full snapshot
      Svc->>DB: INSERT ProofTest_*
      Svc->>FS: HTML/PDF report
      Svc->>DB: update ReportPath
    end
  end

  loop sync-loop
    Svc->>SIL: health / plugin triggers / G-19
    opt Project change
      Svc->>Svc: refresh devices
    end
  end

  Op->>UI: Stop
  UI->>Svc: /api/stop engine only
  Note over UI,Svc: Web host stays alive

  Op->>UI: Shutdown / stop_service.ps1
  UI->>Svc: /api/shutdown process exit
```

---

## 5. Multi-instance SILworX (Mode A / Mode B)

```mermaid
flowchart TB
  SCAN["Scan ports 51710/8400 … 51719/8409"]

  SCAN --> I0["Instance n"]
  SCAN --> I1["Instance n+1"]
  SCAN --> IN["…"]

  I0 --> Q{"GUI project open<br/>on this port?"}
  Q -->|Yes Mode B| ATT["Attach plugin session<br/>read globals — no project/close"]
  Q -->|No| P{"Preferred api_port?"}
  P -->|Yes Mode A| OL["open/local configured .E3<br/>read globals → project/close"]
  P -->|No| SKIP["Skip open/local"]

  ATT --> MERGE["Merge device lists"]
  OL --> MERGE
  SKIP --> MERGE
  MERGE --> DB[(DeviceProoftestResultList)]
  MERGE --> OPC["Enrich OPC server / prefix"]
```

---

## 6. Prooftest data flow

```mermaid
flowchart LR
  DEV[Device in list] --> OPC[OPC item path]
  OPC --> RUN{Running?}
  RUN -->|rising edge| START[Mark test started]
  RUN -->|falling edge| SNAP[Read all Results members]
  SNAP --> TBL["ProofTest_* table row"]
  TBL --> RPT["HTML/PDF<br/>Reports\\Type\\TAG\\"]
  RPT --> PATH[ReportPath column]
```

---

## 7. SILworX lifecycle vs solution (Case 1 today)

```mermaid
stateDiagram-v2
  [*] --> EngineRunning

  EngineRunning --> ApiActive: SILworX API up
  ApiActive --> ModeB: GUI project open
  ApiActive --> ModeA: no GUI project / preferred port
  ModeB --> ApiActive: refresh / merge devices
  ModeA --> ApiActive: open/local then close

  ApiActive --> ApiSuspended: G-19 SILworX closed\n(2 failed probes)
  ApiSuspended --> ApiActive: API back

  ApiActive --> C3Cleanup: G-20 lock.ini + GUI gone\nwait 8s → kill c3.exe
  ApiSuspended --> C3Cleanup: same

  EngineRunning --> ProcessExit: G-11 uninstall detected\nor /api/shutdown
  ProcessExit --> [*]

  note right of ProcessExit
    UI Stop does not exit process
    Current: SILworX uninstall → auto exit
  end note
```

---

## 8. Code / folder architecture

```mermaid
flowchart TB
  ROOT["HIMA-Prooftest-Solution-Current"]

  ROOT --> MAIN["main.py · solution.ini · run/stop_service.ps1"]
  ROOT --> TS["Tool Steps"]
  ROOT --> AX["Annex codes"]
  ROOT --> GI["Graphic Interface"]
  ROOT --> RS["Results Structures CSVs"]

  TS --> S01[step01_setup]
  TS --> S02[step02_database]
  TS --> S03[step03_device_list]
  TS --> S04[step04_opc]
  TS --> S05[step05_detection]
  TS --> S06[step06_reports]
  TS --> S07[step07_triggers]
  TS --> SVC[service · config · alarms]

  AX --> DB[Database / annex_database]
  AX --> API[API connexion]
  AX --> OPC[OPC]
  AX --> PDF[PDF generation]
  AX --> PLG[Plugin + monitor]
  AX --> STP[Stop service + c3 cleanup]
  AX --> TT[Tool test]

  GI --> WEB[app.py + static UI]

  SVC --> AX
  S01 --> S07
  WEB --> SVC
```

---

## 9. Component deployment view

```mermaid
flowchart TB
  subgraph HOST["Windows station with X-OPC"]
    subgraph SOL["Report Solution process"]
      UI[Web UI]
      ENG[Engine threads]
    end
    SQL[(SQL Server<br/>HIMA Automated Prooftest)]
    DISK[C:\HIMA Automated Prooftest Reports]
    OPC[X-OPC]
    SIL[SILworX optional Case 1]
  end

  UI --- ENG
  ENG <--> OPC
  ENG <--> SIL
  ENG --> SQL
  ENG --> DISK
```

---

*End of document*
