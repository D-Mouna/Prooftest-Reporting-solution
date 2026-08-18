"""
Annex — SQL Server / SQLite database access and SQL table templates.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig
from prooftest.results_csv import (
    RESULTS_TYPE_FILES,
    ResultsStructure,
    load_all_structures,
    load_structure,
    member_to_column,
    silworx_type_to_sql,
    structure_to_sql_table,
)
# TEMPLATE_MAP defined below


class Database:
    def __init__(self, config: AppConfig, alarms: AlarmManager) -> None:
        self.config = config
        self.alarms = alarms
        self.using_sqlite = False
        self._conn: Any = None
        self._lock = threading.Lock()

    def connect(self) -> None:
        if self._conn is not None:
            return
        if not self._try_sql_server() and self.config.fallback_sqlite:
            self._connect_sqlite()
        if self._conn is None:
            raise RuntimeError("Database connection failed")

    def close(self) -> None:
        with self._lock:
            if self._conn is None:
                return
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _try_sql_server(self) -> bool:
        try:
            import pyodbc
        except ImportError:
            return False
        try:
            if self.config.db_trusted:
                conn_str = (
                    f"DRIVER={{{self.config.db_driver}}};"
                    f"SERVER={self.config.db_server};"
                    "DATABASE=master;Trusted_Connection=yes;"
                )
            else:
                return False
            master = pyodbc.connect(conn_str, autocommit=True, timeout=5)
            cur = master.cursor()
            db_name = self.config.db_name.replace("'", "''")
            cur.execute(f"SELECT DB_ID(N'{db_name}')")
            row = cur.fetchone()
            exists = row is not None and row[0] is not None
            if not exists:
                data_dir = Path(self.config.sqlite_path).parent
                data_dir.mkdir(parents=True, exist_ok=True)
                safe = re.sub(r"[^A-Za-z0-9_]+", "_", self.config.db_name).strip("_") or "Prooftest"
                mdf = str((data_dir / f"{safe}.mdf").resolve())
                ldf = str((data_dir / f"{safe}_log.ldf").resolve())
                try:
                    cur.execute(
                        f"CREATE DATABASE [{self.config.db_name}] ON "
                        f"(NAME = N'{safe}', FILENAME = N'{mdf}') "
                        f"LOG ON (NAME = N'{safe}_log', FILENAME = N'{ldf}')"
                    )
                except Exception:
                    # Fallback: default SQL Server data directory
                    cur.execute(f"CREATE DATABASE [{self.config.db_name}]")
            master.close()
            conn_str_db = conn_str.replace("DATABASE=master", f"DATABASE={self.config.db_name}")
            self._conn = pyodbc.connect(conn_str_db, autocommit=False, timeout=5)
            self.using_sqlite = False
            self._ensure_system_tables()
            return True
        except Exception as exc:
            self.alarms.raise_alarm(
                "P1",
                "SQL Server unavailable; using SQLite under station Database folder",
                severity="Warning",
                cause=str(exc),
                show_popup=False,
            )
            return False

    def _connect_sqlite(self) -> None:
        path = self.config.sqlite_path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self.using_sqlite = True
        self._ensure_system_tables()

    @contextmanager
    def cursor(self) -> Iterator[Any]:
        with self._lock:
            self.connect()
            cur = self._conn.cursor()
            try:
                if not self.using_sqlite:
                    cur.execute("SET NOCOUNT ON")
                yield cur
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
            finally:
                cur.close()

    def _ensure_system_tables(self) -> None:
        if self.using_sqlite:
            ddl = [
                """CREATE TABLE IF NOT EXISTS DeviceProoftestResultList (
                    Device_TAG TEXT PRIMARY KEY, Results_Type TEXT NOT NULL, Configuration TEXT,
                    Resource TEXT, OPC_Server TEXT, OPC_ItemPrefix TEXT, IsActive INTEGER DEFAULT 1,
                    LastSeenAt TEXT, LastRunning INTEGER, TestInProgress INTEGER DEFAULT 0,
                    PresentOnOpc INTEGER DEFAULT 0, TestStartedAt TEXT, SilworxProject TEXT)""",
                """CREATE TABLE IF NOT EXISTS AlarmLog (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT, Timestamp TEXT, Severity TEXT, Step TEXT,
                    Device_TAG TEXT, Message TEXT, SolutionHint TEXT, Acknowledged INTEGER DEFAULT 0)""",
                """CREATE TABLE IF NOT EXISTS SchemaVersion (
                    Results_Type TEXT PRIMARY KEY, SourceHash TEXT, SyncedAt TEXT)""",
                """CREATE TABLE IF NOT EXISTS ServiceState (Key TEXT PRIMARY KEY, Value TEXT)""",
                """CREATE TABLE IF NOT EXISTS ProoftestHistory (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Device_TAG TEXT NOT NULL,
                    Results_Type TEXT,
                    StartedAt TEXT,
                    FinishedAt TEXT,
                    Outcome TEXT NOT NULL,
                    Result TEXT)""",
            ]
            with self.cursor() as cur:
                for stmt in ddl:
                    cur.execute(stmt)
            self._ensure_present_on_opc_column()
            self._ensure_test_started_at_column()
            self._ensure_silworx_project_column()
            self._ensure_prooftest_history_table()
            self._ensure_alarm_log_columns()
            return

        tables = {
            "DeviceProoftestResultList": """
                CREATE TABLE [dbo].[DeviceProoftestResultList] (
                    [Device_TAG] NVARCHAR(128) NOT NULL PRIMARY KEY,
                    [Results_Type] NVARCHAR(128) NOT NULL,
                    [Configuration] NVARCHAR(64) NULL,
                    [Resource] NVARCHAR(64) NULL,
                    [OPC_Server] NVARCHAR(128) NULL,
                    [OPC_ItemPrefix] NVARCHAR(256) NULL,
                    [IsActive] BIT NOT NULL DEFAULT 1,
                    [LastSeenAt] DATETIME2 NULL,
                    [LastRunning] BIT NULL,
                    [TestInProgress] BIT NOT NULL DEFAULT 0,
                    [PresentOnOpc] BIT NOT NULL DEFAULT 0,
                    [TestStartedAt] DATETIME2 NULL,
                    [SilworxProject] NVARCHAR(256) NULL
                )
            """,
            "AlarmLog": """
                CREATE TABLE [dbo].[AlarmLog] (
                    [ID] INT IDENTITY(1,1) PRIMARY KEY,
                    [Timestamp] DATETIME2 NULL,
                    [Severity] NVARCHAR(32) NULL,
                    [Step] NVARCHAR(32) NULL,
                    [Device_TAG] NVARCHAR(128) NULL,
                    [Message] NVARCHAR(MAX) NULL,
                    [SolutionHint] NVARCHAR(MAX) NULL,
                    [Acknowledged] BIT NOT NULL DEFAULT 0
                )
            """,
            "SchemaVersion": """
                CREATE TABLE [dbo].[SchemaVersion] (
                    [Results_Type] NVARCHAR(128) NOT NULL PRIMARY KEY,
                    [SourceHash] NVARCHAR(128) NULL,
                    [SyncedAt] DATETIME2 NULL
                )
            """,
            "ServiceState": """
                CREATE TABLE [dbo].[ServiceState] (
                    [Key] NVARCHAR(64) NOT NULL PRIMARY KEY,
                    [Value] NVARCHAR(MAX) NULL
                )
            """,
            "ProoftestHistory": """
                CREATE TABLE [dbo].[ProoftestHistory] (
                    [ID] INT IDENTITY(1,1) PRIMARY KEY,
                    [Device_TAG] NVARCHAR(128) NOT NULL,
                    [Results_Type] NVARCHAR(128) NULL,
                    [StartedAt] DATETIME2 NULL,
                    [FinishedAt] DATETIME2 NULL,
                    [Outcome] NVARCHAR(32) NOT NULL,
                    [Result] NVARCHAR(32) NULL
                )
            """,
        }
        for name, ddl in tables.items():
            if not self._table_exists(name):
                with self.cursor() as cur:
                    cur.execute(ddl)
        self._ensure_present_on_opc_column()
        self._ensure_test_started_at_column()
        self._ensure_silworx_project_column()
        self._ensure_prooftest_history_table()
        self._ensure_alarm_log_columns()

    def log_alarm(self, step: str, severity: str, message: str, solution: str, device_tag: Optional[str] = None) -> None:
        with self.cursor() as cur:
            cur.execute(
                "INSERT INTO AlarmLog (Timestamp, Severity, Step, Device_TAG, Message, SolutionHint) VALUES (?, ?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), severity, step, device_tag, message, solution),
            )

    def list_recent_alarms(self, limit: int = 50) -> List[Dict[str, Any]]:
        from prooftest.alarms import alarm_error_key

        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "SELECT ID, Timestamp, Severity, Step, Device_TAG, Message, SolutionHint, Acknowledged "
                    "FROM AlarmLog ORDER BY Timestamp DESC LIMIT ?",
                    (limit,),
                )
            else:
                cur.execute(
                    "SELECT TOP (?) [ID], [Timestamp], [Severity], [Step], [Device_TAG], [Message], "
                    "[SolutionHint], [Acknowledged] "
                    "FROM [dbo].[AlarmLog] ORDER BY [Timestamp] DESC",
                    (limit,),
                )
            rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "severity": row[2],
                "step": row[3],
                "device_tag": row[4],
                "message": row[5],
                "solution_hint": row[6],
                "acknowledged": bool(row[7]),
                "error_key": alarm_error_key(row[3], row[5]),
            }
            for row in rows
        ]

    def get_alarm(self, alarm_id: int) -> Optional[Dict[str, Any]]:
        from prooftest.alarms import alarm_error_key

        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "SELECT ID, Timestamp, Severity, Step, Device_TAG, Message, SolutionHint, Acknowledged "
                    "FROM AlarmLog WHERE ID = ?",
                    (alarm_id,),
                )
            else:
                cur.execute(
                    "SELECT [ID], [Timestamp], [Severity], [Step], [Device_TAG], [Message], "
                    "[SolutionHint], [Acknowledged] "
                    "FROM [dbo].[AlarmLog] WHERE [ID] = ?",
                    (alarm_id,),
                )
            row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "timestamp": row[1],
            "severity": row[2],
            "step": row[3],
            "device_tag": row[4],
            "message": row[5],
            "solution_hint": row[6],
            "acknowledged": bool(row[7]),
            "error_key": alarm_error_key(row[3], row[5]),
        }

    def acknowledge_alarm(self, alarm_id: int) -> Optional[Dict[str, Any]]:
        row = self.get_alarm(alarm_id)
        if row is None:
            return None
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute("UPDATE AlarmLog SET Acknowledged = 1 WHERE ID = ?", (alarm_id,))
            else:
                cur.execute(
                    "UPDATE [dbo].[AlarmLog] SET [Acknowledged] = 1 WHERE [ID] = ?",
                    (alarm_id,),
                )
        row["acknowledged"] = True
        return row

    def reset_alarms(self) -> None:
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute("UPDATE AlarmLog SET Acknowledged = 1")
            else:
                cur.execute("UPDATE [dbo].[AlarmLog] SET [Acknowledged] = 1")

    def set_service_state(self, key: str, value: str) -> None:
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "INSERT OR REPLACE INTO ServiceState (Key, Value) VALUES (?, ?)",
                    (key, value),
                )
            else:
                cur.execute("SELECT [Value] FROM [dbo].[ServiceState] WHERE [Key]=?", (key,))
                if cur.fetchone():
                    cur.execute("UPDATE [dbo].[ServiceState] SET [Value]=? WHERE [Key]=?", (value, key))
                else:
                    cur.execute("INSERT INTO [dbo].[ServiceState] ([Key], [Value]) VALUES (?, ?)", (key, value))

    def get_service_state(self) -> Dict[str, str]:
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute("SELECT Key, Value FROM ServiceState")
            else:
                cur.execute("SELECT [Key], [Value] FROM [dbo].[ServiceState]")
            return {row[0]: row[1] for row in cur.fetchall()}

    def apply_sql_template(self, template_path: Path, old_table: str, new_table: str) -> None:
        if self._table_exists(new_table):
            return
        text = template_path.read_text(encoding="utf-8", errors="ignore")
        create_match = re.search(
            rf"CREATE TABLE\s+\[dbo\]\.\[({re.escape(old_table)})\]\s*\((.*?)\)\s*ON\s+\[PRIMARY\]",
            text,
            re.S | re.I,
        )
        if not create_match:
            raise ValueError(f"CREATE TABLE not found in template {template_path.name}")
        body = create_match.group(1).strip()
        body = body.replace(f"[{old_table}]", f"[{new_table}]")
        meta_cols = [
            "[Device_TAG] NVARCHAR(128) NULL",
            "[Configuration] NVARCHAR(64) NULL",
            "[Resource] NVARCHAR(64) NULL",
            "[OPC_Server] NVARCHAR(128) NULL",
            "[CollectedAt] DATETIME2 NULL",
            "[ReportPath] NVARCHAR(512) NULL",
            "[SequenceInBatch] INT NULL",
        ]
        if self.using_sqlite:
            self._create_table_from_template_sqlite(text.replace(old_table, new_table), new_table)
            return
        ddl = f"CREATE TABLE [dbo].[{new_table}] ({body}, {', '.join(meta_cols)}) ON [PRIMARY]"
        with self.cursor() as cur:
            cur.execute(ddl)

    def _create_table_from_template_sqlite(self, text: str, table_name: str) -> None:
        cols: List[str] = ["ID INTEGER PRIMARY KEY AUTOINCREMENT"]
        for line in text.splitlines():
            m = re.match(r"\s*\[([^\]]+)\]\s+\[([^\]]+)\]", line)
            if m:
                col, typ = m.group(1), m.group(2).upper()
                if col == "ID":
                    continue
                sqlite_type = "TEXT"
                if typ in ("INT", "BIGINT", "BIT"):
                    sqlite_type = "INTEGER"
                elif typ.startswith("DECIMAL") or typ == "FLOAT" or typ == "REAL":
                    sqlite_type = "REAL"
                elif typ == "IMAGE":
                    sqlite_type = "BLOB"
                cols.append(f"[{col}] {sqlite_type}")
        meta = [
            "Device_TAG TEXT",
            "Configuration TEXT",
            "Resource TEXT",
            "OPC_Server TEXT",
            "CollectedAt TEXT",
            "ReportPath TEXT",
            "SequenceInBatch INTEGER",
        ]
        ddl = f"CREATE TABLE IF NOT EXISTS [{table_name}] ({', '.join(cols + meta)})"
        with self.cursor() as cur:
            cur.execute(ddl)

    def ensure_results_table(self, structure: ResultsStructure, templates_dir: Path | None = None) -> None:
        """
        Create ProofTest_* table if missing.

        Runtime source of truth: Results Structure CSV → generated DDL (template style).
        Optional `.sql` files under templates_dir are design-reference only; used if present,
        never required on a deployed station.
        """
        table = structure.sql_table_name
        if self._table_exists(table):
            return
        tpl_root = Path(templates_dir) if templates_dir else None
        if tpl_root is not None and (not str(templates_dir).strip() or str(tpl_root) in (".", "")):
            tpl_root = None
        if tpl_root is not None and tpl_root.is_dir() and any(tpl_root.glob("*.sql")):
            mapping = TEMPLATE_MAP.get(structure.type_name)
            if mapping:
                tpl_file, old_name = mapping
                tpl_path = tpl_root / tpl_file
                if tpl_path.exists():
                    try:
                        self.apply_sql_template(tpl_path, old_name, table)
                        self._record_schema(structure)
                        return
                    except Exception as exc:
                        self.alarms.raise_alarm(
                            "P1",
                            f"Optional template apply failed for {structure.type_name}; using generator",
                            cause=str(exc),
                            severity="Warning",
                            show_popup=False,
                        )
        self._create_table_from_csv(structure)
        self._record_schema(structure)

    def _table_exists(self, table: str) -> bool:
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            else:
                cur.execute("SELECT 1 FROM sys.tables WHERE name = ?", (table,))
            return cur.fetchone() is not None

    def _column_exists(self, table: str, column: str) -> bool:
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(f"PRAGMA table_info({table})")
                return any(str(row[1]) == column for row in cur.fetchall())
            cur.execute(
                "SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(?) AND name = ?",
                (f"dbo.{table}", column),
            )
            return cur.fetchone() is not None

    def _ensure_present_on_opc_column(self) -> None:
        if self._column_exists("DeviceProoftestResultList", "PresentOnOpc"):
            return
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "ALTER TABLE DeviceProoftestResultList ADD COLUMN PresentOnOpc INTEGER DEFAULT 0"
                )
            else:
                cur.execute(
                    "ALTER TABLE [dbo].[DeviceProoftestResultList] ADD [PresentOnOpc] BIT NOT NULL CONSTRAINT DF_DPRL_PresentOnOpc DEFAULT 0"
                )

    def _ensure_test_started_at_column(self) -> None:
        if self._column_exists("DeviceProoftestResultList", "TestStartedAt"):
            return
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "ALTER TABLE DeviceProoftestResultList ADD COLUMN TestStartedAt TEXT"
                )
            else:
                cur.execute(
                    "ALTER TABLE [dbo].[DeviceProoftestResultList] ADD [TestStartedAt] DATETIME2 NULL"
                )

    def _ensure_silworx_project_column(self) -> None:
        if self._column_exists("DeviceProoftestResultList", "SilworxProject"):
            return
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "ALTER TABLE DeviceProoftestResultList ADD COLUMN SilworxProject TEXT"
                )
            else:
                cur.execute(
                    "ALTER TABLE [dbo].[DeviceProoftestResultList] ADD [SilworxProject] NVARCHAR(256) NULL"
                )

    def _ensure_prooftest_history_table(self) -> None:
        if self._table_exists("ProoftestHistory"):
            return
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    """CREATE TABLE IF NOT EXISTS ProoftestHistory (
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        Device_TAG TEXT NOT NULL,
                        Results_Type TEXT,
                        StartedAt TEXT,
                        FinishedAt TEXT,
                        Outcome TEXT NOT NULL,
                        Result TEXT)"""
                )
            else:
                cur.execute(
                    """CREATE TABLE [dbo].[ProoftestHistory] (
                        [ID] INT IDENTITY(1,1) PRIMARY KEY,
                        [Device_TAG] NVARCHAR(128) NOT NULL,
                        [Results_Type] NVARCHAR(128) NULL,
                        [StartedAt] DATETIME2 NULL,
                        [FinishedAt] DATETIME2 NULL,
                        [Outcome] NVARCHAR(32) NOT NULL,
                        [Result] NVARCHAR(32) NULL
                    )"""
                )

    @staticmethod
    def _iso_ts(value: Any) -> Optional[str]:
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        text = str(value).strip()
        return text or None

    def start_test_history(self, device_tag: str, results_type: str = "") -> None:
        now = datetime.now().isoformat()
        self.finish_open_test_history(device_tag, "interrupted", "unknown")
        with self.cursor() as cur:
            cur.execute(
                "INSERT INTO ProoftestHistory (Device_TAG, Results_Type, StartedAt, Outcome, Result) "
                "VALUES (?, ?, ?, ?, ?)",
                (device_tag, results_type or None, now, "running", None),
            )

    def finish_open_test_history(
        self,
        device_tag: str,
        outcome: str,
        result: Optional[str] = None,
    ) -> bool:
        now = datetime.now().isoformat()
        with self.cursor() as cur:
            cur.execute(
                "SELECT ID FROM ProoftestHistory WHERE Device_TAG=? AND Outcome=? "
                "ORDER BY ID DESC",
                (device_tag, "running"),
            )
            row = cur.fetchone()
            if not row:
                return False
            cur.execute(
                "UPDATE ProoftestHistory SET FinishedAt=?, Outcome=?, Result=? WHERE ID=?",
                (now, outcome, result, row[0]),
            )
        return True

    def interrupt_open_tests(self) -> int:
        now = datetime.now().isoformat()
        with self.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM ProoftestHistory WHERE Outcome=?", ("running",))
            count_row = cur.fetchone()
            count = int(count_row[0] or 0) if count_row else 0
            if count:
                cur.execute(
                    "UPDATE ProoftestHistory SET FinishedAt=?, Outcome=?, Result=? WHERE Outcome=?",
                    (now, "interrupted", "unknown", "running"),
                )
            cur.execute(
                "UPDATE DeviceProoftestResultList SET TestInProgress=0, LastRunning=0, TestStartedAt=NULL "
                "WHERE TestInProgress=1"
            )
        return count

    def list_test_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "SELECT ID, Device_TAG, Results_Type, StartedAt, FinishedAt, Outcome, Result "
                    "FROM ProoftestHistory ORDER BY ID DESC LIMIT ?",
                    (limit,),
                )
            else:
                cur.execute(
                    "SELECT TOP (?) [ID], [Device_TAG], [Results_Type], [StartedAt], [FinishedAt], "
                    "[Outcome], [Result] FROM [dbo].[ProoftestHistory] ORDER BY [ID] DESC",
                    (limit,),
                )
            rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "device_tag": row[1],
                "results_type": row[2],
                "started_at": self._iso_ts(row[3]),
                "finished_at": self._iso_ts(row[4]),
                "outcome": row[5] or "unknown",
                "result": row[6] or "",
            }
            for row in rows
        ]

    def _ensure_alarm_log_columns(self) -> None:
        if not self._table_exists("AlarmLog"):
            return
        if self._column_exists("AlarmLog", "Acknowledged"):
            return
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute("ALTER TABLE AlarmLog ADD COLUMN Acknowledged INTEGER DEFAULT 0")
            else:
                cur.execute(
                    "ALTER TABLE [dbo].[AlarmLog] ADD [Acknowledged] BIT NOT NULL CONSTRAINT DF_AlarmLog_Ack DEFAULT 0"
                )

    def _create_table_from_csv(self, structure: ResultsStructure) -> None:
        """Generate CREATE TABLE matching project SQL template style (no .sql file required)."""
        if self._table_exists(structure.sql_table_name):
            return
        table = structure.sql_table_name
        col_names: List[str] = []
        col_defs: List[str] = []
        if self.using_sqlite:
            col_defs.append("ID INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            col_defs.append("[ID] INT IDENTITY(1,1) NOT NULL")

        for member in structure.members:
            col = _normalize_column_name(member_to_column(member.name, structure.type_name))
            if col in col_names or col == "ID":
                continue
            col_names.append(col)
            if self.using_sqlite:
                sql_type = silworx_type_to_sql(member.data_type)
                if sql_type == "BIT":
                    sqlite_t = "INTEGER"
                elif sql_type == "FLOAT":
                    sqlite_t = "REAL"
                elif sql_type in ("BIGINT", "INT", "TINYINT"):
                    sqlite_t = "INTEGER"
                else:
                    sqlite_t = "TEXT"
                col_defs.append(f"[{col}] {sqlite_t}")
            else:
                sql_type = silworx_dtype_to_sql_template(member.data_type)
                col_defs.append(f"[{col}] {sql_type} NULL")

        if not self.using_sqlite:
            error_col = _find_error_code_column(col_names)
            if error_col:
                for n in (4, 3, 2, 1):
                    shift = {4: 24, 3: 16, 2: 8, 1: 0}[n]
                    if shift:
                        expr = f"CONVERT([int],[{error_col}]/power((2),({shift}))&0xFF)"
                    else:
                        expr = f"CONVERT([int],[{error_col}]&0xFF)"
                    col_defs.append(f"[{error_col}_Byte{n}] AS ({expr}) PERSISTED")

        if self.using_sqlite:
            meta = [
                "[Device_TAG] TEXT", "[Configuration] TEXT", "[Resource] TEXT",
                "[OPC_Server] TEXT", "[CollectedAt] TEXT", "[ReportPath] TEXT",
                "[SequenceInBatch] INTEGER",
            ]
            ddl = f"CREATE TABLE [{table}] ({', '.join(col_defs + meta)})"
        else:
            meta = [
                "[Device_TAG] NVARCHAR(128) NULL", "[Configuration] NVARCHAR(64) NULL",
                "[Resource] NVARCHAR(64) NULL", "[OPC_Server] NVARCHAR(128) NULL",
                "[CollectedAt] DATETIME2 NULL", "[ReportPath] NVARCHAR(512) NULL",
                "[SequenceInBatch] INT NULL",
            ]
            pk = f"CONSTRAINT [PK_{table}] PRIMARY KEY CLUSTERED ([ID] ASC)"
            ddl = f"CREATE TABLE [dbo].[{table}] ({', '.join(col_defs + meta)}, {pk})"
        with self.cursor() as cur:
            cur.execute(ddl)

    def _record_schema(self, structure: ResultsStructure) -> None:
        source = structure.csv_path.read_bytes() if structure.csv_path and structure.csv_path.exists() else b""
        digest = hashlib.sha256(source).hexdigest()
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "INSERT OR REPLACE INTO SchemaVersion (Results_Type, SourceHash, SyncedAt) VALUES (?, ?, ?)",
                    (structure.type_name, digest, datetime.now().isoformat()),
                )
            else:
                synced = datetime.now()
                cur.execute("SELECT 1 FROM [dbo].[SchemaVersion] WHERE [Results_Type]=?", (structure.type_name,))
                if cur.fetchone():
                    cur.execute(
                        "UPDATE [dbo].[SchemaVersion] SET [SourceHash]=?, [SyncedAt]=? WHERE [Results_Type]=?",
                        (digest, synced, structure.type_name),
                    )
                else:
                    cur.execute(
                        "INSERT INTO [dbo].[SchemaVersion] ([Results_Type], [SourceHash], [SyncedAt]) VALUES (?, ?, ?)",
                        (structure.type_name, digest, synced),
                    )

    def sync_schema_case1(self, structures: Dict[str, ResultsStructure], active_types: List[str]) -> None:
        # Ensure tables for every Results type loaded from the C: CSV catalogue.
        for type_name in structures:
            self.ensure_results_table(structures[type_name], self.config.sql_templates)

    def sync_schema_case2(self, templates_dir: Path | None, structures: Dict[str, ResultsStructure]) -> None:
        """Ensure all ProofTest_* tables exist from Results structures (templates optional)."""
        if not structures:
            self.alarms.raise_alarm(
                "P1-C2",
                "Results Structure definitions missing — cannot create ProofTest_* tables",
                cause="Load CSVs from C:\\HIMA-Prooftest-Solution-Current\\Results Structures",
                severity="Error",
                show_popup=True,
            )
            return
        for type_name, structure in structures.items():
            self.ensure_results_table(structure, templates_dir)

    def upsert_device(
        self,
        device_tag: str,
        results_type: str,
        *,
        opc_server: Optional[str] = None,
        opc_prefix: Optional[str] = None,
        configuration: Optional[str] = None,
        resource: Optional[str] = None,
        last_running: Optional[bool] = None,
        test_in_progress: Optional[bool] = None,
        silworx_project: Optional[str] = None,
    ) -> None:
        now = datetime.now().isoformat()
        with self.cursor() as cur:
            cur.execute("SELECT Device_TAG FROM DeviceProoftestResultList WHERE Device_TAG=?", (device_tag,))
            exists = cur.fetchone()
            if exists:
                fields = ["Results_Type=?", "IsActive=1", "LastSeenAt=?"]
                params: List[Any] = [results_type, now]
                if opc_server is not None:
                    fields.append("OPC_Server=?")
                    params.append(opc_server)
                if opc_prefix is not None:
                    fields.append("OPC_ItemPrefix=?")
                    params.append(opc_prefix)
                if configuration is not None:
                    fields.append("Configuration=?")
                    params.append(configuration)
                if resource is not None:
                    fields.append("Resource=?")
                    params.append(resource)
                if silworx_project is not None:
                    fields.append("SilworxProject=?")
                    params.append(silworx_project)
                if last_running is not None:
                    fields.append("LastRunning=?")
                    params.append(int(last_running))
                if test_in_progress is not None:
                    fields.append("TestInProgress=?")
                    params.append(int(test_in_progress))
                    if test_in_progress:
                        cur.execute(
                            "SELECT TestInProgress FROM DeviceProoftestResultList WHERE Device_TAG=?",
                            (device_tag,),
                        )
                        prev_row = cur.fetchone()
                        if not prev_row or not prev_row[0]:
                            fields.append("TestStartedAt=?")
                            params.append(now)
                    else:
                        fields.append("TestStartedAt=?")
                        params.append(None)
                params.append(device_tag)
                cur.execute(f"UPDATE DeviceProoftestResultList SET {', '.join(fields)} WHERE Device_TAG=?", params)
            else:
                started_at = now if test_in_progress else None
                cur.execute(
                    "INSERT INTO DeviceProoftestResultList "
                    "(Device_TAG, Results_Type, Configuration, Resource, OPC_Server, OPC_ItemPrefix, "
                    "IsActive, LastSeenAt, LastRunning, TestInProgress, TestStartedAt, SilworxProject) "
                    "VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?)",
                    (
                        device_tag,
                        results_type,
                        configuration,
                        resource,
                        opc_server,
                        opc_prefix,
                        now,
                        int(last_running) if last_running is not None else None,
                        int(test_in_progress) if test_in_progress is not None else 0,
                        started_at,
                        silworx_project,
                    ),
                )

    @staticmethod
    def _with_device_source(row: Dict[str, Any]) -> Dict[str, Any]:
        """OPC ProgID when present on OPC; otherwise the SILworX project of detection."""
        present = bool(row.get("present_on_opc"))
        opc = str(row.get("opc_server") or "").strip()
        project = str(row.get("silworx_project") or "").strip()
        if present:
            row["source_kind"] = "opc"
            row["source_name"] = opc
            row["source_label"] = f"OPC: {opc}" if opc else "OPC"
        elif project:
            row["source_kind"] = "project"
            row["source_name"] = project
            row["source_label"] = f"Project: {project}"
        else:
            row["source_kind"] = "unknown"
            row["source_name"] = ""
            row["source_label"] = "Source: unknown"
        return row

    def export_device_rows(self) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT Device_TAG, Results_Type, Configuration, Resource, OPC_Server, OPC_ItemPrefix, "
                "IsActive, LastSeenAt, LastRunning, TestInProgress, PresentOnOpc, SilworxProject "
                "FROM DeviceProoftestResultList ORDER BY Device_TAG"
            )
            return [
                {
                    "device_tag": row[0],
                    "results_type": row[1],
                    "configuration": row[2],
                    "resource": row[3],
                    "opc_server": row[4],
                    "opc_item_prefix": row[5],
                    "is_active": int(row[6] or 0),
                    "last_seen_at": row[7],
                    "last_running": bool(row[8]) if row[8] is not None else None,
                    "test_in_progress": bool(row[9]) if row[9] is not None else False,
                    "present_on_opc": bool(row[10]) if row[10] is not None else False,
                    "silworx_project": row[11] or "",
                }
                for row in cur.fetchall()
            ]

    def set_device_present_on_opc(self, device_tag: str, present: bool) -> None:
        with self.cursor() as cur:
            cur.execute(
                "UPDATE DeviceProoftestResultList SET PresentOnOpc=? WHERE Device_TAG=?",
                (1 if present else 0, device_tag),
            )

    def delete_devices_not_on_opc(self) -> List[str]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT Device_TAG FROM DeviceProoftestResultList "
                "WHERE PresentOnOpc=0 OR PresentOnOpc IS NULL"
            )
            removed = [str(row[0]) for row in cur.fetchall() if row and row[0]]
            if removed:
                cur.execute(
                    "DELETE FROM DeviceProoftestResultList WHERE PresentOnOpc=0 OR PresentOnOpc IS NULL"
                )
            return removed

    def list_active_devices(self) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT Device_TAG, Results_Type, Configuration, Resource, OPC_Server, OPC_ItemPrefix, "
                "LastRunning, TestInProgress, PresentOnOpc, SilworxProject "
                "FROM DeviceProoftestResultList WHERE IsActive=1 ORDER BY Device_TAG"
            )
            return [
                self._with_device_source(
                    {
                        "device_tag": row[0],
                        "results_type": row[1],
                        "configuration": row[2],
                        "resource": row[3],
                        "opc_server": row[4],
                        "opc_item_prefix": row[5],
                        "last_running": bool(row[6]) if row[6] is not None else None,
                        "test_in_progress": bool(row[7]) if row[7] is not None else False,
                        "present_on_opc": bool(row[8]) if row[8] is not None else False,
                        "silworx_project": row[9] or "",
                    }
                )
                for row in cur.fetchall()
            ]

    def list_running_tests(self) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT Device_TAG, Results_Type, TestStartedAt "
                "FROM DeviceProoftestResultList "
                "WHERE IsActive=1 AND TestInProgress=1 "
                "ORDER BY TestStartedAt, Device_TAG"
            )
            return [
                {
                    "device_tag": row[0],
                    "results_type": row[1],
                    "started_at": row[2],
                }
                for row in cur.fetchall()
            ]

    def list_devices(self, view: str = "all") -> List[Dict[str, Any]]:
        rows = self.list_active_devices()
        if str(view).lower() == "opc":
            return [row for row in rows if row.get("present_on_opc")]
        return rows

    def count_listed_devices(self) -> int:
        with self.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM DeviceProoftestResultList WHERE IsActive=1")
            row = cur.fetchone()
            return int(row[0] or 0) if row else 0

    def count_opc_devices(self) -> int:
        with self.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM DeviceProoftestResultList WHERE IsActive=1 AND PresentOnOpc=1"
            )
            row = cur.fetchone()
            return int(row[0] or 0) if row else 0

    def set_present_on_opc(self, tags: Set[str]) -> None:
        present = {str(tag) for tag in tags if tag}
        with self.cursor() as cur:
            cur.execute("UPDATE DeviceProoftestResultList SET PresentOnOpc=0")
            for tag in present:
                cur.execute(
                    "UPDATE DeviceProoftestResultList SET PresentOnOpc=1 WHERE Device_TAG=?",
                    (tag,),
                )

    def _prooftest_table_names(self) -> List[str]:
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ProofTest_%'"
                )
            else:
                cur.execute(
                    "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                    "WHERE TABLE_NAME LIKE 'ProofTest_%'"
                )
            return [str(row[0]) for row in cur.fetchall() if row and row[0]]

    def device_has_prooftest_reports(
        self,
        device_tag: str,
        *,
        results_type: Optional[str] = None,
        report_output: Optional[Path] = None,
    ) -> bool:
        """True when the device has a SQL snapshot or an HTML/PDF report file."""
        for table in self._prooftest_table_names():
            target = f"[{table}]" if self.using_sqlite else f"[dbo].[{table}]"
            try:
                with self.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {target} WHERE [Device_TAG]=?", (device_tag,))
                    row = cur.fetchone()
                if row and int(row[0] or 0) > 0:
                    return True
            except Exception:
                continue
        if report_output is not None:
            from prooftest.annex_pdf_generation import list_reports_for_device

            if list_reports_for_device(Path(report_output), device_tag, results_type=results_type):
                return True
            if results_type and list_reports_for_device(Path(report_output), device_tag):
                return True
        return False

    def reconcile_device_list(
        self,
        present_tags: List[str],
        *,
        report_output: Optional[Path] = None,
    ) -> None:
        """
        Keep detected devices. For tags no longer detected: keep the row if the
        device has at least one Prooftest report; otherwise delete it.
        """
        present = set(present_tags)
        with self.cursor() as cur:
            cur.execute("SELECT Device_TAG, Results_Type FROM DeviceProoftestResultList")
            rows = [(str(row[0]), row[1]) for row in cur.fetchall()]
        for tag, results_type in rows:
            if tag in present:
                continue
            if self.device_has_prooftest_reports(
                tag,
                results_type=str(results_type) if results_type else None,
                report_output=report_output,
            ):
                with self.cursor() as cur:
                    cur.execute(
                        "UPDATE DeviceProoftestResultList SET IsActive=1 WHERE Device_TAG=?",
                        (tag,),
                    )
            else:
                with self.cursor() as cur:
                    cur.execute("DELETE FROM DeviceProoftestResultList WHERE Device_TAG=?", (tag,))

    def deactivate_missing_devices(self, active_tags: List[str]) -> None:
        """Backward-compatible name — now applies add/keep/delete retention."""
        self.reconcile_device_list(active_tags)

    def insert_snapshot(
        self,
        table: str,
        device_tag: str,
        values: Dict[str, Any],
        *,
        opc_server: Optional[str],
        sequence: Optional[int] = None,
    ) -> int:
        values = dict(values)
        values.pop("_running_still_true", None)
        values["Device_TAG"] = device_tag
        values["OPC_Server"] = opc_server
        values["CollectedAt"] = datetime.now()
        if sequence is not None:
            values["SequenceInBatch"] = sequence
        cols = list(values.keys())
        placeholders = ", ".join("?" for _ in cols)
        col_sql = ", ".join(f"[{c}]" for c in cols)
        target = f"[{table}]" if self.using_sqlite else f"[dbo].[{table}]"
        with self.cursor() as cur:
            if self.using_sqlite:
                cur.execute(
                    f"INSERT INTO {target} ({col_sql}) VALUES ({placeholders})",
                    [values[c] for c in cols],
                )
                return int(cur.lastrowid)
            cur.execute(
                f"INSERT INTO {target} ({col_sql}) OUTPUT INSERTED.[ID] VALUES ({placeholders})",
                [values[c] for c in cols],
            )
            row = cur.fetchone()
            return int(row[0]) if row and row[0] is not None else 0

    def update_report_path(self, table: str, record_id: int, report_path: str) -> None:
        target = f"[{table}]" if self.using_sqlite else f"[dbo].[{table}]"
        with self.cursor() as cur:
            cur.execute(f"UPDATE {target} SET [ReportPath]=? WHERE [ID]=?", (report_path, record_id))


# --- SQL table templates (SPEC Step 2) ---

"""
SQL table template helpers — SPEC Step 5.

Builds `.sql` files in `2- SQL Tables template` from Results Structure CSV definitions,
following the column style of existing HIMA templates (Cerabar / Promass).
"""

# Maps SILworX Results type → (template filename, CREATE TABLE name inside file).
TEMPLATE_MAP: dict[str, tuple[str, str]] = {
    "X-HART_ABB_FCB400_Results": ("Prooftest_ABB_FCB400_V1_5.sql", "ABB_FCB400_V1_5"),
    "X-HART_Emerson_3051S_Results": ("Prooftest_Emerson_3051S_V1_5.sql", "Emerson_3051S_V1_5"),
    "X-HART_E+H_PMx7xB_Results": ("Prooftest_Cerabar_V1_5.sql", "Cerabar_PMx7xB_V1_5"),
    "X-HART_E+H_FTL5xB/6x_Results": ("Prooftest_Liquiphant_V1_5.sql", "Liquiphant_FTLxxB_V1_5"),
    "X-HART_E+H_FMR6xB_Results": ("Prooftest_FMR6xB_V1_5.sql", "FMR6xB_V1_5"),
    "X-HART_E+H_Promass300/500_Results": ("Prooftest_Promass_V1_5.sql", "Promass_300_500_V1_5"),
    "X-HART_SAMSON_Results": ("Prooftest_SAMSON_3793_V1_5.sql", "Samson_3793_V1_5"),
    "X-HART_WIKA_T32_Results": ("Prooftest_WIKA_T32_V1_5.sql", "WIKA_T32_V1_5"),
    "X-HART_WIKA_T38_Results": ("Prooftest_WIKA_T38_V1_5.sql", "WIKA_T38_V1_5"),
}

_ERROR_BYTE_TEMPLATE = """
\t[{col}_Byte4]  AS (CONVERT([int],[{col}]/power((2),(24))&0xFF)) PERSISTED,
\t[{col}_Byte3]  AS (CONVERT([int],[{col}]/power((2),(16))&0xFF)) PERSISTED,
\t[{col}_Byte2]  AS (CONVERT([int],[{col}]/power((2),(8))&0xFF)) PERSISTED,
\t[{col}_Byte1]  AS (CONVERT([int],[{col}]&0xFF)) PERSISTED,"""


def _normalize_column_name(col: str) -> str:
    if col == "Error_Code":
        return "Error_code"
    return col


def _find_error_code_column(columns: List[str]) -> Optional[str]:
    for col in columns:
        if col.lower() == "error_code":
            return col
    return None


def silworx_dtype_to_sql_template(dtype: str) -> str:
    """Map SILworX member type to SQL column type used in HIMA templates."""
    dtype = (dtype or "").strip()
    if dtype == "REAL":
        return "[decimal](10, 3)"
    if dtype == "BOOL":
        return "[bit]"
    if dtype in ("BYTE", "USINT"):
        return "[int]"
    if dtype in ("WORD", "UINT"):
        return "[int]"
    if dtype == "DWORD":
        return "[bigint]"
    if dtype in ("UDINT", "DINT"):
        return "[bigint]"
    if dtype.startswith("X-HART"):
        return "[nvarchar](50)"
    if dtype.startswith("X-"):
        return "[nvarchar](max)"
    return "[nvarchar](128)"


def build_create_table_sql(table_name: str, structure: ResultsStructure) -> str:
    """Generate a single CREATE TABLE block for one Results structure."""
    lines = [
        "USE [ProofTest]",
        "GO",
        f"/****** Object:  Table [dbo].[{table_name}]    Script Date: auto-generated ******/",
        "SET ANSI_NULLS ON",
        "GO",
        "SET QUOTED_IDENTIFIER ON",
        "GO",
        f"CREATE TABLE [dbo].[{table_name}](",
        "\t[ID] [int] IDENTITY(1,1) NOT NULL,",
    ]
    col_names: List[str] = []
    for member in structure.members:
        col = _normalize_column_name(member_to_column(member.name, structure.type_name))
        if col in col_names or col == "ID":
            continue
        col_names.append(col)
        sql_type = silworx_dtype_to_sql_template(member.data_type)
        lines.append(f"\t[{col}] {sql_type} NULL,")

    error_col = _find_error_code_column(col_names)
    if error_col:
        lines.append(_ERROR_BYTE_TEMPLATE.format(col=error_col).rstrip(","))

    lines.extend(
        [
            f" CONSTRAINT [PK_{table_name}] PRIMARY KEY CLUSTERED ",
            "(",
            "\t[ID] ASC",
            ")WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]",
            ") ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]",
            "GO",
            "",
        ]
    )
    return "\n".join(lines)


def write_template_file(templates_dir: Path, structure: ResultsStructure) -> Path:
    """Write the SQL template for one Results type."""
    mapping = TEMPLATE_MAP.get(structure.type_name)
    if not mapping:
        raise KeyError(f"No template mapping for {structure.type_name}")
    filename, table_name = mapping
    path = templates_dir / filename
    path.write_text(build_create_table_sql(table_name, structure), encoding="utf-8")
    return path


def generate_missing_templates(structures_dir: Path, templates_dir: Path) -> List[Path]:
    """Generate SQL templates for types that have no template file yet."""
    written: List[Path] = []
    for type_name, csv_name in RESULTS_TYPE_FILES.items():
        mapping = TEMPLATE_MAP.get(type_name)
        if not mapping:
            continue
        tpl_path = templates_dir / mapping[0]
        if tpl_path.exists():
            continue
        csv_path = structures_dir / csv_name
        if not csv_path.exists():
            continue
        structure = load_structure(csv_path, type_name)
        written.append(write_template_file(templates_dir, structure))
    return written


def template_for_type(type_name: str) -> Optional[tuple[str, str]]:
    return TEMPLATE_MAP.get(type_name)
