#!/usr/bin/env python3
import sys
from pathlib import Path

from _paths import setup_path

setup_path()

import pyodbc
from prooftest.results_csv import RESULTS_TYPE_FILES, structure_to_sql_table

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=HIMA Automated Prooftest;"
    "Trusted_Connection=yes;"
)
cur = conn.cursor()
cur.execute("SELECT DB_NAME()")
print("database:", cur.fetchone()[0])
cur.execute("SELECT name FROM sys.tables ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print("table_count:", len(tables))
for t in tables:
    print(" ", t)
expected = [structure_to_sql_table(x) for x in RESULTS_TYPE_FILES]
missing = [t for t in expected if t not in tables]
print("missing_proof_test_tables:", missing or "none")
for t in ["DeviceProoftestResultList", "ProofTest_SAMSON_Results", "ProofTest_ABB_FCB400_Results"]:
    if t in tables:
        cur.execute(f"SELECT COUNT(*) FROM [{t}]")
        print(f"rows_{t}:", cur.fetchone()[0])
conn.close()
