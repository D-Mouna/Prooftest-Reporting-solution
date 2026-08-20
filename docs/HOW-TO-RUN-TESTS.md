# How to run tests (this machine)

## Environment

- 32-bit Python: `C:\Python 312_32bit\python.exe`
- Working tests dir:

```powershell
cd "C:\Users\Administrator\Documents\Report Solution\Codes\HIMA-Prooftest-Solution-Current\Annex codes\Tool test"
```

## Layer unit tests

```powershell
& "C:\Python 312_32bit\python.exe" test_layers.py
```

**Expected:** `23/23 passed`

## Gate 11 (Web UI)

```powershell
& "C:\Python 312_32bit\python.exe" test_step11_web_ui.py
```

**Expected:** `Gate 11: all checks passed`

## Open-report security probe

```powershell
cd "C:\Users\Administrator\Documents\Report Solution"
& "C:\Python 312_32bit\python.exe" docs\_probe_open_report_security.py
```

**Expected:** `PASS` (outside path → 403)

## Pass/fail summary

| Suite | Result | When |
|-------|--------|------|
| test_layers | **23/23 passed** | 2026-08-20 |
| test_step11_web_ui | **all checks passed** (app 1.75.0) | 2026-08-20 |
| open_report probe | **PASS** (403 outside / 200 inside) | 2026-08-20 |
