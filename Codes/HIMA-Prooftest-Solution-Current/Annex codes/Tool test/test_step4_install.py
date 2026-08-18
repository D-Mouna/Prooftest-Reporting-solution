#!/usr/bin/env python3
"""Verification for SPEC Step 4 — first-run folders and case detection."""

from __future__ import annotations

from pathlib import Path

from _paths import CONFIG_INI, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.step01_setup import KNOWN_RESULTS_TYPES, detect_deployment_case, ensure_first_run, results_type_folder_name

def main() -> int:
    config = AppConfig.load(CONFIG_INI)
    alarms = AlarmManager()

    detected = detect_deployment_case(config.silworx_programdata)
    print(f"detect_deployment_case={detected} (ini deployment_case={config.deployment_case})")

    ensure_first_run(config, alarms)

    missing = []
    for results_type in KNOWN_RESULTS_TYPES:
        folder = results_type_folder_name(results_type)
        for root in (config.first_run_folder, config.report_output, config.report_mirror):
            path = root / folder
            if not path.is_dir():
                missing.append(str(path))

    if missing:
        print("FAIL missing folders:")
        for m in missing[:10]:
            print(" ", m)
        return 1

    print(f"OK {len(KNOWN_RESULTS_TYPES)} Results-type folders under:")
    print(f"  {config.first_run_folder}")
    print(f"  {config.report_output}")
    print(f"  {config.report_mirror}")

    marker = config.first_run_folder / "installation.json"
    if marker.is_file():
        print("OK installation.json updated")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
