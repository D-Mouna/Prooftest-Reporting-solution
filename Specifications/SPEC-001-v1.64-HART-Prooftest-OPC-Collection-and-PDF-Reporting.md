# SPEC-001 — HIMA Automated Prooftest Reporting Solution

| Field | Value |
|-------|--------|
| **Document ID** | SPEC-001 |
| **Version** | 1.64 |
| **Date** | 2026-08-20 |
| **Status** | Draft |
| **Location** | `C:\Users\Administrator\Documents\Report Solution` |
| **Filename** | `SPEC-001-v1.64-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md` |
| **Supersedes** | v1.63 |

## Summary of changes (v1.63 → v1.64)

| Topic | Change |
|-------|--------|
| **OPC client location** | Live OPC Classic DA client is `HIMA-Prooftest-Solution-Current\Annex codes\OPC\connection_opc.py`, loaded only by `annex_opc.py` from the same folder. |
| **Trust boundary** | Current no longer loads OPC code from sibling `Codes\Report-Tool` (reduces out-of-tree / path-confusion risk). |
| **Legacy** | `Codes\Report-Tool\` is frozen reference only; not used by production Current. |
| **Code** | Current **1.67**; archive before change **v1.66**. |

Prior behaviour: [SPEC-001-v1.63-...](./SPEC-001-v1.63-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md).
