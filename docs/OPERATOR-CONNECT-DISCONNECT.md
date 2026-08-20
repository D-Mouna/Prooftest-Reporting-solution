# Operator note — Connect / Disconnect SILworX

**Connect** and **Disconnect** in this tool affect **only this reporting tool’s** SILworX API client and plugin monitor.

They do **not**:

- Quit or stop **SILworX.exe**
- Close the engineer’s open project (`project/close`)
- Kill **c3.exe** as part of Disconnect

After Disconnect, the catalog falls back to **OPC-only** (shape-gated). The Prooftest engine keeps running; live values still come from X-OPC.

## Auth / bind

Default UI bind is **127.0.0.1** (localhost). If you bind the web UI to a non-loopback address (`0.0.0.0` or a LAN IP), enable **`[Web] auth_enabled=true`** and set **`auth_token`**. With `require_auth_when_non_local=true` (default in 1.77), the service **refuses to start** when non-loopback is configured without auth.
