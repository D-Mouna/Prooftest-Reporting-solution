# Layer architecture gaps vs specification

| Field | Value |
|-------|--------|
| **Related** | [HIMA-Prooftest-Layer-Functions.md](./HIMA-Prooftest-Layer-Functions.md) |
| **Code** | `Codes\HIMA-Prooftest-Solution-Current\` (**1.74** / SPEC **1.64**) |
| **Written** | 2026-08-20 |
| **Status** | **Production path is layer-pure (1.74)** |

---

## Update (2026-08-20 — code 1.74)

Presentation controllers call **`ApplicationFacade` only**. No `service.db` / annex PDF / list-archive fallbacks remain in controllers. Gate 11 tests attach a facade mock on `service.app`.

**RefreshCatalog** is owned by Application: `CatalogService.run_station_refresh()` (WorkerHost `ProoftestService.refresh` only delegates).

| Rule | Status |
|------|--------|
| UI → Application only | **Yes** |
| Application owns RefreshCatalog | **Yes** (`run_station_refresh`) |
| Engine / Query / SilworxConnection via facade | **Yes** |
| Domain free of COM/SQL | **Yes** |
| WorkerHost = threads / G-11 / start-stop | **Yes** (`Tool Steps/`) |

**Remaining depth (optional later):** `run_station_refresh` still uses `step03` sync helper and host fields; further moving that helper behind ports only would deepen purity without changing the Presentation rule.

---

## Update (2026-08-20 — code 1.66)

Production wired `ApplicationFacade` (first pass). Controllers still had MagicMock fallbacks until 1.74.
