#!/usr/bin/env python3
"""Generate missing SQL templates and verify all nine ProofTest tables — Step 5."""

from __future__ import annotations

import sys
from pathlib import Path

from _paths import CONFIG_INI, setup_path

setup_path()

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.annex_database import (
    TEMPLATE_MAP,
    Database,
    generate_missing_templates,
)
from prooftest.results_csv import RESULTS_TYPE_FILES, load_all_structures, structure_to_sql_table

META_COLS = {
    "Device_TAG",
    "Configuration",
    "Resource",
    "OPC_Server",
    "CollectedAt",
    "ReportPath",
    "SequenceInBatch",
}


def main() -> int:
    config = AppConfig.load(CONFIG_INI)
    structures = load_all_structures(config.results_structures)

    written = generate_missing_templates(config.results_structures, config.sql_templates)
    print(f"Generated {len(written)} template(s):")
    for path in written:
        print(" ", path.name)

    alarms = AlarmManager()
    db = Database(config, alarms)
    db.connect()
    db.sync_schema_case1(structures, [])

    missing_tables = []
    missing_meta = []
    for type_name in RESULTS_TYPE_FILES:
        table = structure_to_sql_table(type_name)
        if not db._table_exists(table):
            missing_tables.append(table)
            continue
        with db.cursor() as cur:
            cur.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=?",
                (table,),
            )
            cols = {row[0] for row in cur.fetchall()}
        if not META_COLS.issubset(cols):
            missing_meta.append(table)

    print(f"TEMPLATE_MAP entries: {len(TEMPLATE_MAP)}")
    print(f"SQL template files: {len(list(config.sql_templates.glob('*.sql')))}")

    if missing_tables:
        print("FAIL missing tables:", missing_tables)
        return 1
    if missing_meta:
        print("FAIL missing metadata columns:", missing_meta)
        return 1

    print("OK all 9 ProofTest_* tables exist with metadata columns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
