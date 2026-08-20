# SPEC-001 — HIMA Automated Prooftest Reporting Solution

| Field | Value |
|-------|--------|
| **Document ID** | SPEC-001 |
| **Title** | HIMA Automated Prooftest — Background Service, SILworX API, Multi-OPC, SQL, PDF/HTML, Web GUI |
| **Version** | 1.63 |
| **Date** | 2026-08-20 |
| **Status** | Draft |
| **Project** | Report Solution |
| **Location** | `C:\Users\Administrator\Documents\Report Solution` |
| **Filename** | `SPEC-001-v1.63-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md` |
| **Supersedes** | v1.62 |

## Versioning

Specification and code versioning are **project process rules**, not runtime behaviour of the Report Solution.

| Rule | Description |
|------|-------------|
| **SPEC files** | Updates require a **new** file. Do not edit published SPEC versions in place. |
| **Summary of changes** | Each SPEC file documents **only** the delta from its immediate predecessor. |
| **G-12** | Edit only `HIMA-Prooftest-Solution-Current`. Archive before change. |

---

## Summary of changes (v1.62 → v1.63)

Full layered Application facade for production.

| Topic | Change |
|-------|--------|
| **Application facade** | Presentation calls `ApplicationFacade` use cases only (`StartEngine`, `StopEngine`, `GetEngineStatus`, `RefreshCatalog`, SILworX connect/disconnect, `ListDevices` / `ListReports` / `ListAlarms` / `OpenReport`, list archives). Controllers do not import annex PDF/SQL modules on the production path. |
| **Production wiring** | `ProoftestService` remains WorkerHost (threads, G-11, start/stop races) and builds `Engine` + `CatalogService` + `QueryService` + `SilworxConnectionService` + port adapters. |
| **SilworxPort adapter** | `Case1SyncSilworxAdapter` implements attach/detach/list_identities over this tool’s API/plugin session only (never quits SILworX). |
| **OPC-only discovery** | `OpcManagerAdapter.discover_opc_only` uses production OPC browse for CatalogService. |
| **DeviceId** | Unchanged from v1.61+: DeviceId = Project + Configuration + Resource + Device_TAG. |
| **Code** | `HIMA-Prooftest-Solution-Current` **1.66**; archive before this change was **v1.65**. |

---

## Normative references

- Layer functions: [HIMA-Prooftest-Layer-Functions.md](../HIMA-Prooftest-Layer-Functions.md)
- Architecture gaps closed by this version: [Layer-Architecture-Gaps.md](../Layer-Architecture-Gaps.md)
- Prior behaviour: [SPEC-001-v1.62-...](./SPEC-001-v1.62-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md)
