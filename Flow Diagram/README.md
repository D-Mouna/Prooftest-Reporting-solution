# HIMA Prooftest Solution — Flow Diagrams

Architecture flow diagrams for **SPEC-001 v1.59** (G-22 three-layer design; parallel API + OPC device list).

## Images (PNG / SVG)

| Diagram | PNG | SVG |
|---------|-----|-----|
| Architecture overview | [01-architecture-overview.png](./01-architecture-overview.png) | [01-architecture-overview.svg](./01-architecture-overview.svg) |
| Unified mode | [02-case1-vs-case2.png](./02-case1-vs-case2.png) | [02-case1-vs-case2.svg](./02-case1-vs-case2.svg) |
| Service threads | [03-service-threads.png](./03-service-threads.png) | [03-service-threads.svg](./03-service-threads.svg) |
| Device list (API + OPC) | [04-device-list-case1.png](./04-device-list-case1.png) | [04-device-list-case1.svg](./04-device-list-case1.svg) |
| Steps 1–7 summary | [05-steps-summary.png](./05-steps-summary.png) | [05-steps-summary.svg](./05-steps-summary.svg) |

## Markdown sources (Mermaid)

| File | Contents |
|------|----------|
| [01-architecture-overview.md](./01-architecture-overview.md) | Main system: three layers; refresh starts API and OPC together |
| [02-case1-vs-case2.md](./02-case1-vs-case2.md) | Unified mode (engineering or HMI) |
| [03-service-threads.md](./03-service-threads.md) | Background threads: OPC poll, sync loop, plugin monitor |
| [04-device-list-case1.md](./04-device-list-case1.md) | Step 3 device list: simultaneous API + OPC, then merge |
| [05-steps-summary.md](./05-steps-summary.md) | Steps 1–7 reference table |

## Re-render images

```powershell
& "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" "_render_diagrams.py"
```

Requires Playwright + Chromium (`pip install playwright` then `python -m playwright install chromium`).

**Active code:** `Codes\HIMA-Prooftest-Solution-Current`  
**Spec:** `Specifications\SPEC-001-v1.59-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md`
