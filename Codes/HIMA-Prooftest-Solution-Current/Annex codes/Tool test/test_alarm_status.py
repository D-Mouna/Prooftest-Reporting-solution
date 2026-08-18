#!/usr/bin/env python3
"""Alarm still-active window, acknowledge, and reset."""

from __future__ import annotations

from _paths import setup_path

setup_path()

from prooftest.alarms import AlarmManager, alarm_error_key


def main() -> int:
    manager = AlarmManager()
    manager.raise_alarm("P3", "OPC read failed", device_tag="100-XV-001_FST", show_popup=False)
    key = alarm_error_key("P3", "OPC read failed")
    if key not in manager.active_error_keys():
        print("FAIL newly raised alarm is not active")
        return 1
    rows = manager.recent_alarms()
    if not rows or not rows[0]["active"] or rows[0]["acknowledged"]:
        print(f"FAIL recent alarm flags {rows[:1]}")
        return 1

    manager.acknowledge_error_key(key)
    rows = manager.recent_alarms()
    if not rows[0]["acknowledged"]:
        print("FAIL acknowledge did not set acknowledged")
        return 1
    if key not in manager.active_error_keys():
        print("FAIL acknowledged alarm that is still occurring must remain active")
        return 1

    manager.reset_all()
    if manager.active_error_keys():
        print(f"FAIL reset left active keys {manager.active_error_keys()}")
        return 1
    if any(not row["acknowledged"] for row in manager.recent_alarms()):
        print("FAIL reset did not acknowledge in-memory alarms")
        return 1

    print("OK  alarm still-active / acknowledge / reset")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
