#!/usr/bin/env python3
"""Step 1 environment baseline audit — read-only checks."""
from __future__ import annotations

import json
import socket
import ssl
import struct
import sys
import urllib.request
from pathlib import Path

RESULTS = {}


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS[name] = {"ok": ok, "detail": detail}


def port_open(port: int) -> bool:
    s = socket.socket()
    s.settimeout(2)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def main() -> int:
    py_bits = struct.calcsize("P") * 8
    check("python_32bit", py_bits == 32, f"{sys.version.split()[0]} ({py_bits}-bit) @ {sys.executable}")

    openssl = Path(r"C:\Program Files\FireDaemon OpenSSL 4\bin\openssl.exe")
    check("openssl", openssl.exists(), str(openssl) if openssl.exists() else "not found")

    silworx = Path(r"C:\Program Files\HIMA\SILworX_v16.0.0 R3326")
    check("silworx_install", silworx.exists(), str(silworx))

    from _paths import CONFIG_INI, setup_path

    setup_path()
    from prooftest.config import AppConfig

    config = AppConfig.load(CONFIG_INI)
    api_port = config.silworx_api_port
    api_cert = config.silworx_api_cert or Path(
        r"C:\ProgramData\SILworX_v16.0.0 R3326\settings\api_cert.pem"
    )
    api_client = Path(r"C:\ProgramData\SILworX_v16.0.0 R3326\settings\api_client")
    client_files = list(api_client.glob("*")) if api_client.exists() else []
    check("api_server_cert", api_cert.exists(), str(api_cert))
    check(
        "api_client_cert",
        any(p.suffix == ".pem" for p in client_files),
        ", ".join(p.name for p in client_files) or "missing",
    )

    check("port_silworx_api", port_open(api_port), f"127.0.0.1:{api_port}")
    check("port_web_ui", port_open(8080), "127.0.0.1:8080")

    if api_cert.exists() and port_open(api_port):
        try:
            ctx = ssl.create_default_context(cafile=str(api_cert))
            req = urllib.request.Request(
                f"https://127.0.0.1:{api_port}/api/v1/silworx/info",
                method="POST",
                data=b"{}",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                data = json.loads(resp.read().decode())
            info = data.get("results", data)
            check("silworx_api_info", True, json.dumps(info)[:500])
        except Exception as exc:
            check("silworx_api_info", False, str(exc))
    else:
        check("silworx_api_info", False, "skipped — cert or port unavailable")

    try:
        import pyodbc

        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\\SQLEXPRESS;"
            "DATABASE=HIMA Automated Prooftest;"
            "Trusted_Connection=yes;"
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"
        )
        n = cur.fetchone()[0]
        cur.execute("SELECT name FROM sys.tables ORDER BY name")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        check("sql_server", True, f"{n} tables: {', '.join(tables[:12])}")
    except Exception as exc:
        check("sql_server", False, str(exc))

    try:
        import OpenOPC

        opc = OpenOPC.client()
        servers = opc.servers()
        filtered = [
            s
            for s in servers
            if "X_OPC" in s.upper() or "X-OPC" in s or "HIMA" in s.upper()
        ]
        check("opc_servers", len(filtered) > 0, f"{len(filtered)} HIMA/X-OPC: {filtered}")
    except Exception as exc:
        check("opc_servers", False, str(exc))

    z_sql = Path(r"Z:\Project\Report Solution\2- SQL Tables template")
    c_sql = Path(r"C:\Project\Report Solution\2- SQL Tables template")
    sql_files = sorted(p.name for p in z_sql.glob("*.sql")) if z_sql.exists() else []
    check("sql_templates_z", z_sql.exists(), f"{len(sql_files)} files: {sql_files}")
    check("sql_templates_c", c_sql.exists(), "not present — use Z: path")

    results_csv = Path(r"Z:\Project\Report Solution\3- Results Structures")
    csv_files = sorted(p.name for p in results_csv.glob("*.csv")) if results_csv.exists() else []
    check("results_csv", len(csv_files) == 9, f"{len(csv_files)} files")

    html_root = Path(r"Z:\Project\Report Solution\1- HTML Reports Template")
    html_dirs = sorted(p.name for p in html_root.iterdir() if p.is_dir()) if html_root.exists() else []
    check("html_templates", len(html_dirs) >= 7, f"{len(html_dirs)} families: {html_dirs}")

    api_docs = Path(r"Z:\Project\Report Solution\4- API Documentations\SILworX_v16.0.0 R3326")
    api_example = Path(r"Z:\Project\Report Solution\5- API Application Example\sapi.py")
    plugin_ex = Path(r"Z:\Project\Report Solution\6- Plugin Example")
    check("api_docs_v16", api_docs.exists(), str(api_docs))
    check("api_example", api_example.exists(), str(api_example))
    check("plugin_examples", plugin_ex.exists(), str(plugin_ex))

    e3 = Path(
        r"Z:\Project\SILworX\OTS Demo\ProofTest-Reporting solution\ProofTest-Reporting solution.E3"
    )
    check("project_e3", e3.exists(), str(e3))

    c_reports = Path(r"C:\HIMA Automated Prooftest Reports")
    check("c_reports_folder", c_reports.exists(), str(c_reports))

    print(json.dumps(RESULTS, indent=2))
    failed = [k for k, v in RESULTS.items() if not v["ok"]]
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
