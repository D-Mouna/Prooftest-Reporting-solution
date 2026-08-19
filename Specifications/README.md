# Report Solution — Specifications

## Versioning policy

**Every specification update must create a new version file. Do not edit a published version in place.**

### Rules

1. **Immutable prior versions** — When a new version is created, **all previous version files must remain unchanged**. Do not edit headers, status, document history, typos, or any other content in older files. Supersession is recorded only in this README (and in the new file’s `Supersedes` field).
2. **New file per version** — Copy the latest version file, increment the version number, and save under a new filename.
3. **Filename format**:
   ```text
   SPEC-{NNN}-v{major}.{minor}-{Short-Title}.md
   ```
   Example: `SPEC-001-v1.1-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md`
4. **Version numbering**:
   - **Major** (`1.0` → `2.0`): scope, architecture, or acceptance criteria change.
   - **Minor** (`1.0` → `1.1`): clarifications, new sections, corrected mappings, open items closed.
5. **Document header** — Update `Version`, `Date`, and `Status` in the **new** file only.
6. **Document history** — In the **new** SPEC file, §10 Document history lists **only this version’s row**, plus a link to [History of Modifications.md](./History%20of%20Modifications.md). Do not copy the full historical table into each new SPEC.
7. **Summary of changes** — Each new SPEC file must include `## Summary of changes` **immediately after the document header**, documenting **only** what changed from the **immediate predecessor** (`#### What changed from vX.Y−1 to vX.Y`, short description, files touched). **Do not** retain prior-version subsections inside the SPEC file.
8. **History of Modifications** — Append the same delta block to the top of [History of Modifications.md](./History%20of%20Modifications.md) (newest first). That file is the **only** place that accumulates all version-to-version modifications.
9. **Superseded versions** — Record supersession in the **Archived versions** table below and in the new file header (`Supersedes`). **Do not modify** archived spec files.
10. **Code-driven updates** — When a code modification is requested that is **not** already described in the latest specification, **automatically create a new specification version** (increment minor) documenting the change **before or together with** the code update. Implementation must not introduce undocumented behaviour. Agents and developers must follow this rule on every code change request.
11. **Latest pointer** — Update the “Current versions” table below whenever a new version is published.
12. **Paired code versioning** — All solution code changes go in **`HIMA-Prooftest-Solution-Current`** only. **Before** editing, archive a snapshot to `Codes/Archive/HIMA-Prooftest-Solution-v{next}` (run `Codes/archive_current.ps1` or copy manually). Never modify archived code trees. See [Codes/README.md](../Codes/README.md).

| Trigger | Action |
|---------|--------|
| User requests code change | Compare request to latest SPEC file |
| Behaviour not in spec | Create `SPEC-001-v1.{n+1}-...md` with new/clarified requirements |
| Code merged | README “Current versions” points to new spec; append delta to **History of Modifications.md**; [Codes/README.md](../Codes/README.md) — archive then edit **HIMA-Prooftest-Solution-Current** |
| Prior spec files | **Never modified** (immutable archive) |

### When updating

| Step | Action |
|------|--------|
| 1 | Identify latest file for the spec ID (e.g. SPEC-001). |
| 2 | Copy to new filename with incremented version. |
| 3 | Replace **`## Summary of changes`** with **only** the delta from the previous version (do not keep older subsections). |
| 4 | Prepend that same delta to [History of Modifications.md](./History%20of%20Modifications.md). |
| 5 | Apply other edits **only** in the new SPEC file; §10 lists this version only + link to History. |
| 6 | Update this README (“Current versions” and “Archived versions” tables). |
| 7 | **Do not open or save** any older version file. |
| 8 | Do not delete old versions (audit trail). |

---

## Current versions

| Spec ID | Latest file | Version | Date | Status |
|---------|-------------|---------|------|--------|
| SPEC-001 | [SPEC-001-v1.62-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md](./SPEC-001-v1.62-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | 1.62 | 2026-08-19 | Draft |

---

## Specification index

| ID | Title |
|----|--------|
| SPEC-001 | HIMA Automated Prooftest — Background service, multi-OPC, SQL, PDF/HTML, web GUI (unified API→OPC mode) |

**Change log (all versions):** [History of Modifications.md](./History%20of%20Modifications.md)

### Archived versions

| Version | File | Status |
|---------|------|--------|
| 1.61 | [SPEC-001-v1.61-...](./SPEC-001-v1.61-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.62 |
| 1.60 | [SPEC-001-v1.60-...](./SPEC-001-v1.60-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.61 |
| 1.59 | [SPEC-001-v1.59-...](./SPEC-001-v1.59-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.60 |
| 1.58 | [SPEC-001-v1.58-...](./SPEC-001-v1.58-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.59 |
| 1.57 | [SPEC-001-v1.57-...](./SPEC-001-v1.57-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.58 |
| 1.56 | [SPEC-001-v1.56-...](./SPEC-001-v1.56-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.57 |
| 1.55 | [SPEC-001-v1.55-...](./SPEC-001-v1.55-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.56 |
| 1.54 | [SPEC-001-v1.54-...](./SPEC-001-v1.54-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.55 |
| 1.53 | [SPEC-001-v1.53-...](./SPEC-001-v1.53-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.54 |
| 1.52 | [SPEC-001-v1.52-...](./SPEC-001-v1.52-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.53 |
| 1.51 | [SPEC-001-v1.51-...](./SPEC-001-v1.51-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.52 |
| 1.50 | [SPEC-001-v1.50-...](./SPEC-001-v1.50-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.51 |
| 1.49 | [SPEC-001-v1.49-...](./SPEC-001-v1.49-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.50 |
| 1.48 | [SPEC-001-v1.48-...](./SPEC-001-v1.48-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.49 |
| 1.46 | [SPEC-001-v1.46-...](./SPEC-001-v1.46-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.48 |
| 1.45 | [SPEC-001-v1.45-...](./SPEC-001-v1.45-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.46 |
| 1.44 | [SPEC-001-v1.44-...](./SPEC-001-v1.44-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.45 |
| 1.43 | [SPEC-001-v1.43-...](./SPEC-001-v1.43-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.44 |
| 1.42 | [SPEC-001-v1.42-...](./SPEC-001-v1.42-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.43 |
| 1.41 | [SPEC-001-v1.41-...](./SPEC-001-v1.41-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.42 |
| 1.39 | [SPEC-001-v1.39-...](./SPEC-001-v1.39-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.41 |
| 1.0 | [SPEC-001-v1.0-...](./SPEC-001-v1.0-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.1 | [SPEC-001-v1.1-...](./SPEC-001-v1.1-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.2 | [SPEC-001-v1.2-...](./SPEC-001-v1.2-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.3 | [SPEC-001-v1.3-...](./SPEC-001-v1.3-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.4 | [SPEC-001-v1.4-...](./SPEC-001-v1.4-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.5 | [SPEC-001-v1.5-...](./SPEC-001-v1.5-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.6 | [SPEC-001-v1.6-...](./SPEC-001-v1.6-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.7 | [SPEC-001-v1.7-...](./SPEC-001-v1.7-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded |
| 1.8 | [SPEC-001-v1.8-...](./SPEC-001-v1.8-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.9 |
| 1.9 | [SPEC-001-v1.9-...](./SPEC-001-v1.9-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.10 |
| 1.10 | [SPEC-001-v1.10-...](./SPEC-001-v1.10-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.11 |
| 1.11 | [SPEC-001-v1.11-...](./SPEC-001-v1.11-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.12 |
| 1.12 | [SPEC-001-v1.12-...](./SPEC-001-v1.12-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.13 |
| 1.13 | [SPEC-001-v1.13-...](./SPEC-001-v1.13-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.14 |
| 1.14 | [SPEC-001-v1.14-...](./SPEC-001-v1.14-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.15 |
| 1.16 | [SPEC-001-v1.16-...](./SPEC-001-v1.16-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.17 |
| 1.26 | [SPEC-001-v1.26-...](./SPEC-001-v1.26-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.27 |
| 1.27 | [SPEC-001-v1.27-...](./SPEC-001-v1.27-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.28 |
| 1.30 | [SPEC-001-v1.30-...](./SPEC-001-v1.30-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Archived (experimental hero video; superseded by v1.31 active line via v1.29) |
| 1.38 | [SPEC-001-v1.38-...](./SPEC-001-v1.38-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.39 |
| 1.33 | [SPEC-001-v1.33-...](./SPEC-001-v1.33-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.38 |
| 1.32 | [SPEC-001-v1.32-...](./SPEC-001-v1.32-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.33 |
| 1.31 | [SPEC-001-v1.31-...](./SPEC-001-v1.31-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.32 |
| 1.28 | [SPEC-001-v1.28-...](./SPEC-001-v1.28-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.29 |
| 1.25 | [SPEC-001-v1.25-...](./SPEC-001-v1.25-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.26 |
| 1.24 | [SPEC-001-v1.24-...](./SPEC-001-v1.24-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.25 |
| 1.20 | [SPEC-001-v1.20-...](./SPEC-001-v1.20-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.21 |
| 1.19 | [SPEC-001-v1.19-...](./SPEC-001-v1.19-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.20 |
| 1.17 | [SPEC-001-v1.17-...](./SPEC-001-v1.17-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.19 |
| 1.15 | [SPEC-001-v1.15-...](./SPEC-001-v1.15-HART-Prooftest-OPC-Collection-and-PDF-Reporting.md) | Superseded by v1.16 |
