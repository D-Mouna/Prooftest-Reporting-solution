import pyodbc

servers = [
    r"localhost\SQLEXPRESS",
    r".\SQLEXPRESS",
    r"(local)\SQLEXPRESS",
    r"localhost\SQLEXPRESS2017",
    r".\SQLEXPRESS2017",
    r"localhost",
    r".",
    r"(local)",
]
for s in servers:
    try:
        c = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={s};DATABASE=master;Trusted_Connection=yes;Timeout=4"
        )
        cur = c.cursor()
        cur.execute("SELECT @@SERVERNAME, @@SERVICENAME")
        inst = cur.fetchone()
        cur.execute("SELECT name FROM sys.databases ORDER BY name")
        dbs = [r[0] for r in cur.fetchall()]
        hima = [d for d in dbs if "HIMA" in d or "Proof" in d]
        print(f"OK  SERVER={s!r}")
        print(f"    instance={inst}")
        print(f"    HIMA/Proof DBs={hima}")
        if hima:
            c2 = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={s};DATABASE={hima[0]};Trusted_Connection=yes;Timeout=4"
            )
            cur2 = c2.cursor()
            cur2.execute("SELECT COUNT(*) FROM sys.tables")
            print(f"    tables_in_{hima[0]}={cur2.fetchone()[0]}")
            c2.close()
        c.close()
    except Exception as exc:
        print(f"FAIL SERVER={s!r} -> {exc}")
