# Legacy Code Index — HIMA Automated Prooftest Reporting Tool

| Field | Value |
|-------|--------|
| **Active runtime** | `Codes\HIMA-Prooftest-Solution-Current` (code **1.65**, SPEC **1.62**) |
| **Project root** | `C:\Users\Administrator\Documents\Report Solution` |
| **Indexed** | 2026-08-19 |
| **Scope** | Folders **outside** `HIMA-Prooftest-Solution-Current` (archives, templates, predecessor trees) |
| **Current-only index** | [Codes/HIMA-Prooftest-Solution-Current/Legacy-Code-Index.md](./Codes/HIMA-Prooftest-Solution-Current/Legacy-Code-Index.md) — unused code **inside** Current |

> **Rule:** Edit **only** `HIMA-Prooftest-Solution-Current`. Everything below is legacy, reference, template, or archive — do not develop there unless explicitly restoring history.

---

## Summary

| Category | Count | Runtime use |
|----------|------:|-------------|
| Archive snapshots (`Archive\HIMA-Prooftest-Solution-v*`) | **54** | None — read-only audit trail |
| Unversioned predecessor tree | **1** (`HIMA-Prooftest-Solution`) | None |
| Pre-HIMA consulting-era code | **2** branches under `0- Previous solution` | None |
| Numbered asset folders (`1-` … `7-`) | **7** | **Partial** — templates/seeds only (`1-`, `2-`; `7-` via sync script) |
| API/plugin reference examples | **3** folders (`4-`, `5-`, `6-`) | Audit/tests only |
| Shared OPC sibling | **1** (`Codes\Report-Tool`) | **Legacy** — production OPC is inside Current |
| Empty placeholders | **2** (`MVC Architecture`, `Report Solution 2`) | None |
| Docs / diagrams (no Current Python) | **2** (`Specifications`, `Flow Diagram`) | None |

---

## 1. Active tool (NOT legacy — for reference)

| Path | Role |
|------|------|
| `Codes\HIMA-Prooftest-Solution-Current\` | **Only folder to edit.** `main.py`, `Tool Steps\`, `Annex codes\`, `Graphic Interface\`, bundled `Results Structures\`. |
| Station runtime (deploy target) | `C:\HIMA Prooftest Reporting Tool\` — live DB, reports, CSV catalogue on the PC (not source code). |

---

## 2. Pure legacy — not imported by Current at runtime

### 2.1 Code archives (54 snapshots)

**Path:** `Codes\Archive\HIMA-Prooftest-Solution-v1.11` … `v1.64`  
**Index:** `Codes\Archive\ARCHIVE_INDEX.json` (next archive: **v1.65**)  
**Policy:** Immutable snapshots taken **before** each code change. Never edit after creation.

| Version range | Count | Notes |
|---------------|------:|-------|
| v1.11 – v1.31 | 21 | Migrated from old “new folder per spec” policy |
| v1.32 – v1.64 | 33 | Current archive-before-change policy; reasons in `ARCHIVE_INDEX.json` |

**Latest archive:** `v1.64` (2026-08-18) — *Before presentation controllers, LiveTestService wiring, DeviceId reports, architecture diagrams.*

<details>
<summary>All 54 archive folder names</summary>

```
HIMA-Prooftest-Solution-v1.11   HIMA-Prooftest-Solution-v1.12   HIMA-Prooftest-Solution-v1.13
HIMA-Prooftest-Solution-v1.14   HIMA-Prooftest-Solution-v1.15   HIMA-Prooftest-Solution-v1.16
HIMA-Prooftest-Solution-v1.17   HIMA-Prooftest-Solution-v1.18   HIMA-Prooftest-Solution-v1.19
HIMA-Prooftest-Solution-v1.20   HIMA-Prooftest-Solution-v1.21   HIMA-Prooftest-Solution-v1.24
HIMA-Prooftest-Solution-v1.25   HIMA-Prooftest-Solution-v1.26   HIMA-Prooftest-Solution-v1.27
HIMA-Prooftest-Solution-v1.28   HIMA-Prooftest-Solution-v1.29   HIMA-Prooftest-Solution-v1.30
HIMA-Prooftest-Solution-v1.31   HIMA-Prooftest-Solution-v1.32   HIMA-Prooftest-Solution-v1.33
HIMA-Prooftest-Solution-v1.34   HIMA-Prooftest-Solution-v1.35   HIMA-Prooftest-Solution-v1.36
HIMA-Prooftest-Solution-v1.37   HIMA-Prooftest-Solution-v1.38   HIMA-Prooftest-Solution-v1.39
HIMA-Prooftest-Solution-v1.40   HIMA-Prooftest-Solution-v1.41   HIMA-Prooftest-Solution-v1.42
HIMA-Prooftest-Solution-v1.43   HIMA-Prooftest-Solution-v1.44   HIMA-Prooftest-Solution-v1.45
HIMA-Prooftest-Solution-v1.46   HIMA-Prooftest-Solution-v1.47   HIMA-Prooftest-Solution-v1.48
HIMA-Prooftest-Solution-v1.49   HIMA-Prooftest-Solution-v1.50   HIMA-Prooftest-Solution-v1.51
HIMA-Prooftest-Solution-v1.52   HIMA-Prooftest-Solution-v1.53   HIMA-Prooftest-Solution-v1.54
HIMA-Prooftest-Solution-v1.55   HIMA-Prooftest-Solution-v1.56   HIMA-Prooftest-Solution-v1.57
HIMA-Prooftest-Solution-v1.58   HIMA-Prooftest-Solution-v1.59   HIMA-Prooftest-Solution-v1.60
HIMA-Prooftest-Solution-v1.61   HIMA-Prooftest-Solution-v1.62   HIMA-Prooftest-Solution-v1.63
HIMA-Prooftest-Solution-v1.64
```

</details>

---

### 2.2 Unversioned predecessor (pre–G-12)

| Path | Description | Status |
|------|-------------|--------|
| `Codes\HIMA-Prooftest-Solution\` | Early monolith: `prooftest\` package, web UI, tests, `solution.ini`. Predates versioning policy. | **Do not use** — README says use Current |

~59 Python-related files. Ancestor of all versioned trees; logic was copied forward into Current over time.

---

### 2.3 Pre–Report Solution consulting work

**Path:** `0- Previous solution\` (~1,070 files)

| Subfolder | Contents | Python? |
|-----------|----------|---------|
| `Alternative Reporting\` | Standalone tray/report app (WeasyPrint PDF, pyodbc, pystray). Latest dev: `2025-07-28\11-10\`. Shipped: `Last Release\Report.exe`. | **Yes** (~126 `.py` files incl. history) |
| `Alternative Reporting\000 History\` | Dated snapshots 2025-06-30 → 2025-07-25 | Yes |
| `Automated Prooftest\01 last Release\` | Vendor device packages (E&H, SAMSON, WIKA, Micropilot, …) — HTML templates, GraphworX, workbench imports | Templates/assets only |
| `Automated Prooftest\02 Versionen Archiv\` | Superseded vendor release copies | Assets |
| `Automated Prooftest\03 ReportingV2\` | Early reporting v2 templates | Templates only |
| `Automated Prooftest\05 Demos Rechner\` | Demo PC configs (ACHEMA, Fieldworker, Samson, Himatrix+CMS-V, …) | Demo assets |
| `Automated Prooftest\Fieldworker App\` | Fieldworker app install/docs; `Code\` has legacy `signature_pad.js` only | Minimal JS |
| Other (`Endress und Hauser`, `Protokolle`, `Vorlagen`, …) | PDFs, PPTs, CSVs, videos, consulting docs | No code |

**Current references:** none.

---

### 2.4 Empty placeholders

| Path | Status |
|------|--------|
| `MVC Architecture\` | Empty — unused |
| `Report Solution 2\` | Empty — unused |

---

## 3. External to Current tree — but used at runtime

These are **not** inside `HIMA-Prooftest-Solution-Current` but Current **imports or seeds from** them.

| Path | Role | Current reference |
|------|------|-------------------|
| `Codes\Report-Tool\Connection-opc.py` | **Legacy copy** of OPC Classic DA client | **No** — Current uses `Annex codes\OPC\connection_opc.py` |
| `Codes\Report-Tool\` (rest) | `main.py`, `setup.ps1`, `run_opc.ps1`, `requirements.txt` | Standalone OPC probe (legacy); not part of prooftest service |
| `HIMA-Prooftest-Solution-Current\Annex codes\OPC\connection_opc.py` | Live OPC Classic DA client | `annex_opc.py` loads from same folder only |
| `1- HTML Reports Template\` | 12 HIMA device HTML report layouts | `annex_pdf_generation.py` — template seed; gate test `test_step10_reports.py` |
| `2- SQL Tables template\` | 10 `Prooftest_*.sql` schema files | `Tool Steps\config.py` — fallback path; runtime schema mostly from CSV now |
| `7- Images for the graphical interface\` | Branding images (folder may be empty; synced copy lives in Current) | `sync_gui_images.ps1` → `Graphic Interface\static\img\` |

**Hardcoded 32-bit Python (Desktop, not Documents):**

| Path | Role |
|------|------|
| `C:\Users\Administrator\Desktop\Report-Tool\opc_env\Scripts\python.exe` | Used by `run_service.ps1` and `annex_start_service.py` for 32-bit OpenOPC |

---

## 4. Reference / audit only — not runtime imports

| Path | Contents | Current reference |
|------|----------|-------------------|
| `3- Results Structures\` | 9 baseline `X-HART_*_Results.csv` type definitions | Duplicate of bundled seed; `_step1_audit.py` only |
| `4- API Documentations\` | SILworX v16 API docs + generated clients (~2,500+ files) | `_step1_audit.py` |
| `5- API Application Example\` | HIMA reference: `sapi.py`, `silworx_info.py`, `silworx_registry.py` | Audit; patterns copied into `annex_api_connexion.py` |
| `6- Plugin Example\` | SILworX plugin samples (Asset_Inventory, O_Scope, Diagnose) | `_step1_audit.py` |

---

## 5. Documentation and tooling (no Current runtime Python)

| Path | Role |
|------|------|
| `Specifications\` | Versioned SPEC-001 markdown + `architecture-diagrams\` SVG/PNG |
| `Flow Diagram\` | Mermaid/PNG flow docs + `_render_diagrams.py`, `mermaid.min.js` |
| `HIMA-Prooftest-Layer-Functions.md` | Layer/function reference doc |
| `Codes\Code History of Modifications.md` | Code change log |
| `Codes\archive_current.ps1` | Archive workflow script (dev tooling) |
| `Codes\README.md` | Versioning policy |

---

## 6. Quick lookup — “Is this folder used by Current?”

| If you are in… | Used at runtime? | Action |
|----------------|------------------|--------|
| `HIMA-Prooftest-Solution-Current\` | **Yes** | Edit here |
| `Codes\Archive\` | No | Read-only history |
| `Codes\HIMA-Prooftest-Solution\` | No | Legacy — do not edit |
| `0- Previous solution\` | No | Historical reference |
| `Codes\Report-Tool\` | **No** (legacy) | Do not edit for production |
| `1- HTML Reports Template\` | **Seed only** | Update when adding report layouts |
| `2- SQL Tables template\` | **Fallback only** | Legacy SQL reference |
| `3-` … `6-` numbered folders | Audit/tests | Reference material |
| `Specifications\`, `Flow Diagram\` | No | Documentation |
| `MVC Architecture\`, `Report Solution 2\` | No | Can ignore or remove |

---

## 7. Related paths outside this project tree

| Path | Relationship |
|------|--------------|
| `C:\Users\Administrator\Desktop\Report-Tool\_prooftest_docs_push\` | Git mirror for GitHub push (not runtime) |
| `C:\HIMA Prooftest Reporting Tool\` | Station runtime data (DB, reports, CSV catalogue) |
| `Z:\Project\Report Solution\` | **Deprecated path** — project moved to `Documents\Report Solution`; some Current code still hardcodes `Z:\` fallbacks |

---

*See also: [Codes/README.md](./Codes/README.md), [Codes/Archive/ARCHIVE_INDEX.json](./Codes/Archive/ARCHIVE_INDEX.json), [Codes/Archive/README.md](./Codes/Archive/README.md).*
