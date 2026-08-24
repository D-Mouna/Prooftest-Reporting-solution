# HIMA Automated Prooftest — Single Process Architecture

One Windows process started by `main.py`. Everything below runs together; MVCS describes **roles**, not separate executables.

---

## 1. Process shell — what `main.py` owns

```mermaid
flowchart TB
  subgraph PROCESS["🖥️ Single Windows process"]
    direction TB

    MAIN["main.py"]
    INI["solution.ini"]
    CFG["AppConfig"]

    MAIN --> CFG
    INI -.-> CFG

    CFG --> HOST["Engine host\nProoftestService"]
    CFG --> HTTP["HTTP stack\nuvicorn + FastAPI"]

    MAIN --> HOST
    MAIN --> HTTP

    HOST -->|"start() on boot"| ENG_ON["Engine ON\nthreads running"]
    HTTP -->|"always listening"| WEB_ON["Web UI ON\n:8080"]
  end

  BROWSER["Browser\n(outside process)"] -->|"HTTP"| WEB_ON
  HOST --> EXT["External systems\nOPC · SILworX · SQL · disk"]
```

| Started by `main.py` | Purpose |
|----------------------|---------|
| `ProoftestService` | Engine lifecycle, background threads, health |
| `create_app()` → uvicorn | Serves UI + REST API |
| `service.start()` | Engine starts immediately (poll + sync) |

---

## 2. MVCS inside the process (clean map)

Four roles **inside the same process**. Infrastructure sits **below** Service/Model — not a fifth MVCS letter.

```mermaid
flowchart TB
  subgraph PROCESS["Single Windows process"]
    direction TB

    subgraph V["V — View"]
      direction LR
      V1["index.html"]
      V2["app.js"]
      V3["style.css"]
    end

    subgraph C["C — Controller"]
      direction LR
      C1["uvicorn"]
      C2["web_app.py"]
      C3["controllers.py"]
    end

    subgraph S["S — Service"]
      direction LR
      S1["ApplicationFacade"]
      S2["CatalogService"]
      S3["LiveTestService"]
      S4["QueryService"]
      S5["SilworxConnectionService"]
    end

    subgraph M["M — Model"]
      direction TB
      M1["Domain\nDevice · Merger · EdgeDetector"]
      M2["Persistence\nStorePort → SQL / SQLite"]
      M3["Live reads\nOpcPort · SilworxPort · ReportPort"]
    end

    subgraph INFRA["Infrastructure (same process, not MVCS)"]
      direction LR
      I1["ProoftestService\nengine host"]
      I2["Threads\npoll · sync · report"]
      I3["Adapters\nadapters.py"]
      I4["Annex\nOPC · API · Plugin · DB · PDF"]
    end

    V -->|"REST only"| C
    C -->|"application(service)"| S
    S --> M
    S --> I3
    I3 --> I4
    I1 --> I2
    I2 -->|"calls same Services"| S
    I1 --> S
  end

  BROWSER["Browser"] --> V
  I4 --> WORLD["OPC · SILworX · SQL · files"]
```

---

## 3. Layer stack (top → bottom)

Easier to read as a **vertical stack**:

```mermaid
flowchart TB
  L1["① View — Graphic Interface/static/\nRendered in browser · polls REST every 2s"]
  L2["② Controller — FastAPI controllers.py\nRoutes · localhost guard · optional auth"]
  L3["③ Service — ApplicationFacade + use-case services\nCatalog · LiveTest · Query · SilworxConn"]
  L4["④ Model — Domain rules + DB + port interfaces\nMerger · EdgeDetector · ProofTest_* tables"]
  L5["⑤ Infrastructure — host · threads · adapters · annex\nProoftestService · OPC/API/Plugin/DB"]

  L1 --> L2 --> L3 --> L4
  L3 --> L5
  L5 --> L4

  style L1 fill:#e3f2fd
  style L2 fill:#bbdefb
  style L3 fill:#90caf9
  style L4 fill:#64b5f6
  style L5 fill:#eceff1
```

**Rule:** arrows go **down** only for MVCS requests. Infrastructure **calls up** into Service (threads), never into Controller.

---

## 4. Two paths through the same process

### A) User / UI path (classic MVCS)

```mermaid
sequenceDiagram
  box Browser
    participant V as View<br/>app.js
  end
  box Single process
    participant C as Controller<br/>controllers.py
    participant S as Service<br/>ApplicationFacade
    participant M as Model<br/>Domain + Store
  end

  V->>C: GET /api/health
  C->>S: get_engine_status()
  S->>M: read health + DB state
  M-->>S: data
  S-->>C: JSON
  C-->>V: response

  V->>C: POST /api/start (localhost)
  C->>S: start_engine()
  Note over S: delegates to engine host
```

### B) Background path (no Controller)

```mermaid
sequenceDiagram
  box Single process
    participant H as Engine host<br/>ProoftestService
    participant T as Thread<br/>poll-loop
    participant S as Service<br/>LiveTestService
    participant M as Model<br/>EdgeDetector + OpcPort + Store
  end
  box External
    participant OPC as X-OPC
  end

  H->>T: start daemon thread
  loop every 1s
    T->>S: poll_once()
    S->>M: read .Running
    M->>OPC: OpcPort read
    OPC-->>M: values
    M-->>S: edge: started / ended
    S->>M: INSERT snapshot on end
  end
```

---

## 5. MVCS quick reference (files)

| MVCS | Folder / file | In process? |
|------|----------------|-------------|
| **V** | `Graphic Interface/static/` | Served by process; runs in browser |
| **C** | `layers/presentation/controllers.py`, `web_app.py` | Yes |
| **S** | `layers/application/facade.py`, `*_service.py` | Yes |
| **M** | `layers/domain/`, `StorePort`, DB via adapters | Yes |
| Host | `Tool Steps/service.py` | Yes — **not** C or S |
| Annex | `Annex codes/OPC`, `API connexion`, … | Yes — **Model I/O** |

---

## 6. What is NOT MVCS (but lives in the process)

```mermaid
mindmap
  root((main.py process))
    MVCS
      View
        static UI
      Controller
        FastAPI routes
      Service
        ApplicationFacade
      Model
        Domain
        SQL store
        Ports
    Not MVCS
      Engine host
        ProoftestService
        start stop health
      Threads
        poll-loop 1s
        sync-loop 2s
        report-worker
      Adapters
        adapters.py
      Annex
        OPC API Plugin DB PDF
```

---

## 7. One-line summary

**`main.py` starts one process containing:** browser-served **View**, FastAPI **Controller**, **ApplicationFacade** Service, **Domain + DB** Model, plus an **engine host + threads + annex adapters** that keep calling the same Service/Model without going through HTTP.
