# LEGACY — do not use for the Prooftest tool

**Status:** Frozen / superseded (2026-08-20).

The live OPC Classic DA client used by **HIMA-Prooftest-Solution-Current** now lives at:

```text
HIMA-Prooftest-Solution-Current\Annex codes\OPC\connection_opc.py
```

Loaded only by `Annex codes\OPC\annex_opc.py` from that same folder.

## Why this folder remains

Historical standalone OPC probe (`Connection-opc.py`, `main.py`, `run_opc.ps1`, `setup.ps1`). Kept for reference only.

## Rules

1. **Do not** point Current at this folder.
2. **Do not** edit this tree for production fixes — edit `Current\Annex codes\OPC\` instead.
3. Desktop `C:\Users\Administrator\Desktop\Report-Tool\opc_env\` is only the **32-bit Python interpreter** used by `run_service.ps1`, not this source tree.

See [Codes/README.md](../README.md) and [Legacy-Code-Index.md](../../Legacy-Code-Index.md).
