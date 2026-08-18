#!/usr/bin/env python3
"""Smoke tests for HIMA Prooftest solution on local host."""

from __future__ import annotations

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8080"


def get(path: str):
    with urllib.request.urlopen(f"{BASE}{path}", timeout=120) as resp:
        return json.loads(resp.read().decode())


def post(path: str):
    req = urllib.request.Request(f"{BASE}{path}", method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    health = get("/api/health")
    assert health["database"] in ("sqlserver", "sqlite"), health
    assert health["deployment_case"] == 1, health
    print("OK health:", health["database"], "OPC servers:", len(health["opc_servers"]))

    devices = get("/api/devices")
    print("OK devices:", len(devices))

    refresh = post("/api/refresh")
    print("OK refresh:", refresh.get("status", refresh))

    from pathlib import Path

    marker = Path(r"C:\HIMA Automated Prooftest Reports\installation.json")
    assert marker.exists(), "First-run marker missing"
    print("OK first-run marker:", marker)

    alarms = get("/api/alarms")
    print("OK alarms:", len(alarms.get("alarms", [])))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("FAIL:", exc)
        raise SystemExit(1)
