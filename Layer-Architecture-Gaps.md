# Layer architecture gaps vs specification

| Field | Value |
|-------|--------|
| **Related** | [HIMA-Prooftest-Layer-Functions.md](./HIMA-Prooftest-Layer-Functions.md) |
| **Code** | `Codes\HIMA-Prooftest-Solution-Current\` (**1.66** / SPEC **1.63**) |
| **Written** | 2026-08-20 |
| **Status** | **Addressed in code 1.66** — see below |

---

## Update (2026-08-20 — code 1.66)

Production now wires an **`ApplicationFacade`**: Presentation controllers call Application use cases first. `ProoftestService` is the WorkerHost that builds Engine / Catalog / Query / SilworxConnection + port adapters (`Case1SyncSilworxAdapter`, OPC-only discovery).

| Former gap | Status after 1.66 |
|------------|-------------------|
| UI → `service.db` / annex PDF | **Closed on production path** — controllers use `ApplicationFacade` |
| Engine / Catalog / Query unused | **Wired** on the host; SILworX connect/disconnect via `SilworxConnectionService` |
| No SilworxPort adapter | **Added** `Case1SyncSilworxAdapter` |
| Dual orchestration forever | **Reduced** — Presentation → Application; WorkerHost keeps threads/G-11/start races |

**Still intentional:** Catalog refresh for Case1 markers/schema still runs through `ProoftestService.refresh()`, which ApplicationFacade exposes as `RefreshCatalog()`. Replacing that entirely with `CatalogService.refresh_catalog()` alone can be a later step.

---

## Historical gap list (pre-1.66)

### 1. Web UI did not talk to Application only
Controllers called `ProoftestService` / `service.db` / annex PDF directly.

### 2. Application classes existed but were not the boss
`Engine`, `CatalogService`, `QueryService`, `SilworxConnectionService` were mostly test-only.

### 3. Presentation skipped Application for tools
Device list, reports, archives imported DB/PDF/annex in controllers.

### 4. Only live-test path was layered
Poll/report used `LiveTestService`; start/stop/catalog/SILworX used Tool Steps.

### 5. Two parallel implementations
Same jobs in layers and in Tool Steps; production used the old copy.

### 6. Device identity doc vs code
Layer doc (older) said TAG-only; code uses DeviceId (project+config+resource+TAG).

### 7. Domain purity
`layers/domain/` was clean, but many decisions still lived in Tool Steps/annex.

### 8. Extra UI features not in Application map
Archives / alarm ack were controller→annex, not named Application use cases.
