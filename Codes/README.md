# Report Solution — Code versioning

**All development happens in one folder: `HIMA-Prooftest-Solution-Current`.**  
Before any code change, archive a snapshot under `Archive/` with an incremented version number.

Specifications still use versioned files (`SPEC-001-v{x.y}-...md`) — see [Specifications/README.md](../Specifications/README.md).

---

## Rules

1. **Single active tree** — Edit **only** `HIMA-Prooftest-Solution-Current\`. Never modify archived copies or legacy `HIMA-Prooftest-Solution-v*` folders.
2. **Archive before change** — **Before** applying any code modification, copy `HIMA-Prooftest-Solution-Current` to:
   ```text
   Archive\HIMA-Prooftest-Solution-v{next}\
   ```
   Use the next version from `Archive/ARCHIVE_INDEX.json`, then increment the index.
3. **Immutable archives** — Archived folders are read-only snapshots. Do not fix bugs or refactor inside `Archive\`.
4. **Spec pairing** — `VERSION.json` in **Current** must declare the `spec_version` that the code implements. When behaviour changes, create a new SPEC file first (or together with the code change).
5. **Do not delete** archives or legacy version folders (audit trail).

| Trigger | Action |
|---------|--------|
| Any code change | Run `archive_current.ps1` (or manual copy) **first**, then edit **Current** |
| Behaviour not in spec | New `SPEC-001-v{next}` **and** archive + edit **Current** |
| Spec-only clarification | New spec file; archive + code update only if implementation must change |

### Workflow (every code change)

| Step | Action |
|------|--------|
| 1 | Read latest SPEC-001; create new spec version if behaviour is not yet specified. |
| 2 | Run `.\archive_current.ps1` from `Codes\` (or copy Current → `Archive\HIMA-Prooftest-Solution-v{next}`). |
| 3 | Implement changes **only** in `HIMA-Prooftest-Solution-Current\`. |
| 4 | Update `VERSION.json` in Current (`spec_version`, `description`). |
| 5 | Prepend the code delta to [Code History of Modifications.md](./Code%20History%20of%20Modifications.md). |
| 6 | Update `Specifications/README.md` / History of Modifications if a new spec was published. |
| 7 | Update the new spec file references → `HIMA-Prooftest-Solution-Current\`. |

---

## Active code

| Folder | Role | Specification |
|--------|------|---------------|
| **[HIMA-Prooftest-Solution-Current](./HIMA-Prooftest-Solution-Current/)** | **Active — all edits here** | See `VERSION.json` → latest SPEC-001 |

**Quick start:**

```powershell
cd "Z:\Project\Report Solution\Codes\HIMA-Prooftest-Solution-Current"
powershell -ExecutionPolicy Bypass -File .\run_service.ps1
```

**Archive before next change:**

```powershell
cd "Z:\Project\Report Solution\Codes"
powershell -ExecutionPolicy Bypass -File .\archive_current.ps1
```

---

## Archives

New snapshots (from the Current policy) live under **[Archive/](./Archive/)**.  
See [Archive/README.md](./Archive/README.md) and [Archive/ARCHIVE_INDEX.json](./Archive/ARCHIVE_INDEX.json).

**Code change log (all versions):** [Code History of Modifications.md](./Code%20History%20of%20Modifications.md) — same role as the Specifications history file; prepend a delta block after each archive + Current edit.

---

## Legacy versioned folders (frozen)

`HIMA-Prooftest-Solution-v1.11` … `v1.31` at the `Codes\` root were created under the **old policy** (new folder per spec version). They remain frozen and are **not** updated. New work uses **Current** + **Archive** only.

| Spec version | Legacy folder | Status |
|--------------|---------------|--------|
| 1.31 | [HIMA-Prooftest-Solution-v1.31](./HIMA-Prooftest-Solution-v1.31/) | Frozen (superseded by Current) |
| 1.29 | [HIMA-Prooftest-Solution-v1.29](./HIMA-Prooftest-Solution-v1.29/) | Frozen |
| … | `HIMA-Prooftest-Solution-v*` | Frozen |

`HIMA-Prooftest-Solution\` (unversioned) predates versioning — do not use.

**Tool test:** gate tests live in `HIMA-Prooftest-Solution-Current\Annex codes\Tool test\`.

**Code layout (G-17):** `Tool Steps\` holds Steps + main service code. Annex modules in purpose-named folders (`Database`, `API connexion`, `OPC`, `PDF generation`, `Stop service`, `Plugin`); web GUI in `Graphic Interface\`.

---

## Other code

| Folder | Role |
|--------|------|
| [Report-Tool](./Report-Tool/) | Shared OPC client (`Connection-opc.py`); referenced by Prooftest solution via relative path |
