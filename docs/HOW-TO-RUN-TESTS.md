# How to run tests (this machine)

## Environment

- 32-bit Python: `C:\Python 312_32bit\python.exe`
- Working tests dir:

```powershell
cd "C:\Users\Administrator\Documents\Report Solution\Codes\HIMA-Prooftest-Solution-Current\Annex codes\Tool test"
```

## Layer unit tests (baseline + T1–T24 + R1–R7)

```powershell
& "C:\Python 312_32bit\python.exe" test_layers.py
```

**Expected:** `54/54 passed` (23 baseline + 24 edge `test_t01`…`test_t24` + 7 `test_r*`)

## Gate 11 (Web UI)

```powershell
& "C:\Python 312_32bit\python.exe" test_step11_web_ui.py
```

**Expected:** `Gate 11: all checks passed` (app **1.77.0**)

## Open-report security probe

```powershell
cd "C:\Users\Administrator\Documents\Report Solution"
& "C:\Python 312_32bit\python.exe" docs\_probe_open_report_security.py
```

**Expected:** `PASS` (outside path → 403)

## Dependency scan

```powershell
& "C:\Python 312_32bit\python.exe" -m pip install pip-audit -q
& "C:\Python 312_32bit\python.exe" -m pip_audit -r "C:\Users\Administrator\Documents\Report Solution\Codes\HIMA-Prooftest-Solution-Current\requirements.txt"
```

**Expected (2026-08-20 after fastapi/starlette bump):** No known vulnerabilities found.

## Pass/fail summary

| Suite | Result | When |
|-------|--------|------|
| test_layers | **54/54 passed** | 2026-08-20 |
| test_step11_web_ui | **all checks passed** (app 1.77.0) | 2026-08-20 |
| open_report probe | **PASS** (403 outside / 200 inside) | 2026-08-20 |
| pip-audit | **No known vulnerabilities found** | 2026-08-20 |
