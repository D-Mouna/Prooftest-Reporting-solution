# Service threads

The background service runs three concurrent activities after `service.start()`.

```mermaid
flowchart TB
    START["service.start()"] --> T1
    START --> T2
    START --> T3

    T1["Thread: OPC poll loop<br/>poll_interval_sec = 1 s"]
    T2["Thread: sync loop<br/>case1_sync_poll_sec = 2 s"]
    T3["Thread: plugin monitor<br/>WebSocket on 8400–8409"]

    T1 --> P1["Read .Running per device"]
    P1 --> P2{"FALSE → TRUE?"}
    P2 -->|start| P3["Wait TRUE → FALSE"]
    P3 --> P4["Snapshot all members → SQL → PDF/HTML"]

    T2 --> C1["check() triggers"]
    C1 --> C2{"Any fired?"}
    C2 -->|yes| REF["refresh() → API + OPC together"]
    C2 -->|no| C3["G-19/G-20: API health · c3 cleanup"]

    T3 --> S1["Session token cache per port"]
    S1 --> S2["Fire silworx_session trigger"]
```

| Thread | Interval | Purpose | Blocks SILworX API? |
|--------|----------|---------|---------------------|
| OPC poll | 1 s | Realtime reads, prooftest edges, reports | No |
| Sync loop | 2 s | Triggers, refresh, API health, c3 cleanup | Can call API on refresh |
| Plugin monitor | Continuous | Session open/close on all 10 plugin ports | No (WebSocket only) |
