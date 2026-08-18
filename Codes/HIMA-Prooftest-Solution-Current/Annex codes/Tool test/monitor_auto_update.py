#!/usr/bin/env python3
"""Snapshot service/DB state and detect changes over a watch window."""

from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import pyodbc

from pathlib import Path

from _paths import CONFIG_INI

INI = CONFIG_INI


WATCH_SEC = 120
INTERVAL_SEC = 15
API = "http://127.0.0.1:8080/api/health"


def sql_snapshot() -> dict:
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=HIMA Automated Prooftest;"
        "Trusted_Connection=yes;"
    )
    cur = conn.cursor()
    cur.execute("SELECT name FROM sys.tables WHERE name LIKE 'ProofTest%' OR name IN "
                  "('DeviceProoftestResultList','SchemaVersion','ServiceState') ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    cur.execute(
        "SELECT Device_TAG, Results_Type, IsActive, OPC_Server, LastSeenAt "
        "FROM DeviceProoftestResultList ORDER BY Device_TAG"
    )
    devices = [
        {
            "tag": r[0],
            "type": r[1],
            "active": bool(r[2]),
            "server": r[3],
            "last_seen": str(r[4]) if r[4] else None,
        }
        for r in cur.fetchall()
    ]
    cur.execute("SELECT Results_Type, SyncedAt FROM SchemaVersion ORDER BY Results_Type")
    schema = {r[0]: str(r[1]) if r[1] else None for r in cur.fetchall()}
    cur.execute("SELECT [Key], [Value] FROM ServiceState ORDER BY [Key]")
    service_state = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()
    return {
        "tables": tables,
        "devices": devices,
        "active_count": sum(1 for d in devices if d["active"]),
        "schema_version": schema,
        "service_state": service_state,
    }


def api_health() -> dict:
    try:
        with urllib.request.urlopen(API, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        return {"error": str(exc)}


def snapshot(label: str) -> dict:
    e3 = Path(r"Z:\Project\SILworX\OTS Demo\ProofTest-Reporting solution\ProofTest-Reporting solution.E3")
    marker = e3.parent / ".last_sync_mtime"
    health = api_health()
    silworx = health.get("silworx", {}) if isinstance(health, dict) else {}
    session_data = silworx.get("silworx_session_data", "")
    objects_dat = Path(session_data) / "c3data" / "objects.dat" if session_data else None
    return {
        "label": label,
        "time": datetime.now().isoformat(timespec="seconds"),
        "e3_mtime": datetime.fromtimestamp(e3.stat().st_mtime).isoformat(timespec="seconds") if e3.exists() else None,
        "e3_locked": e3.with_suffix(e3.suffix + ".lock").exists(),
        "sync_marker": marker.read_text(encoding="utf-8").strip() if marker.exists() else None,
        "silworx_open": silworx.get("silworx_open"),
        "silworx_project": silworx.get("silworx_project_name"),
        "session_objects_dat_mtime": datetime.fromtimestamp(objects_dat.stat().st_mtime).isoformat(timespec="seconds")
        if objects_dat and objects_dat.exists()
        else None,
        "health": health,
        "sql": sql_snapshot(),
    }


def diff(before: dict, after: dict) -> dict:
    changes = []
    if before["sql"]["active_count"] != after["sql"]["active_count"]:
        changes.append(f"active devices: {before['sql']['active_count']} -> {after['sql']['active_count']}")
    before_tags = {d["tag"]: d for d in before["sql"]["devices"]}
    after_tags = {d["tag"]: d for d in after["sql"]["devices"]}
    for tag in sorted(set(before_tags) | set(after_tags)):
        if tag not in before_tags:
            changes.append(f"device added: {tag}")
        elif tag not in after_tags:
            changes.append(f"device removed: {tag}")
        elif before_tags[tag] != after_tags[tag]:
            changes.append(f"device changed: {tag}")
    if before["sql"]["tables"] != after["sql"]["tables"]:
        added = set(after["sql"]["tables"]) - set(before["sql"]["tables"])
        removed = set(before["sql"]["tables"]) - set(after["sql"]["tables"])
        if added:
            changes.append(f"tables added: {sorted(added)}")
        if removed:
            changes.append(f"tables removed: {sorted(removed)}")
    if before["sql"]["schema_version"] != after["sql"]["schema_version"]:
        changes.append("SchemaVersion rows changed")
    if before["sql"]["service_state"] != after["sql"]["service_state"]:
        for k in sorted(set(before["sql"]["service_state"]) | set(after["sql"]["service_state"])):
            if before["sql"]["service_state"].get(k) != after["sql"]["service_state"].get(k):
                changes.append(
                    f"ServiceState[{k}]: {before['sql']['service_state'].get(k)} -> {after['sql']['service_state'].get(k)}"
                )
    if before.get("e3_mtime") != after.get("e3_mtime"):
        changes.append(f".E3 mtime: {before.get('e3_mtime')} -> {after.get('e3_mtime')}")
    return {"automatic_updates_detected": len(changes) > 0, "changes": changes}


def main() -> None:
    before = snapshot("T0_start")
    print("=== SNAPSHOT T0 ===")
    print(json.dumps(before, indent=2))
    snapshots = [before]
    elapsed = 0
    while elapsed < WATCH_SEC:
        time.sleep(INTERVAL_SEC)
        elapsed += INTERVAL_SEC
        snap = snapshot(f"T+{elapsed}s")
        snapshots.append(snap)
        print(f"--- poll T+{elapsed}s active={snap['sql']['active_count']} last_poll={snap['sql']['service_state'].get('last_poll')}")
    after = snapshots[-1]
    result = diff(before, after)
    print("\n=== SNAPSHOT T+120s ===")
    print(json.dumps(after, indent=2))
    print("\n=== DIFF (T0 vs T+120s) ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
