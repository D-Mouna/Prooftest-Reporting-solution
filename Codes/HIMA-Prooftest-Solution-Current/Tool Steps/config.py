from __future__ import annotations

import configparser
import logging
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

log = logging.getLogger(__name__)


def _default_ini() -> Path:
    return Path(__file__).resolve().parent.parent / "solution.ini"


def _solution_root() -> Path:
    return Path(__file__).resolve().parent.parent


# Station runtime root on C: — three folders created on first run.
STATION_ROOT = Path(r"C:\HIMA Prooftest Reporting Tool")
DEFAULT_REPORTS_FOLDER = STATION_ROOT / "HIMA Automated Prooftest Reports"
DEFAULT_RESULTS_STRUCTURES = STATION_ROOT / "Results Structures"
DEFAULT_DATABASE_FOLDER = STATION_ROOT / "Database"
DEFAULT_SQLITE_PATH = DEFAULT_DATABASE_FOLDER / "prooftest.db"
# PDF/HTML templates live under Reports (not a 4th top-level folder).
DEFAULT_REPORT_TEMPLATES = DEFAULT_REPORTS_FOLDER / "Report Templates"

# Legacy paths (pre-v1.46) — one-time migrate into STATION_ROOT when present.
_LEGACY_REPORTS = Path(r"C:\HIMA Automated Prooftest Reports")
_LEGACY_RESULTS = Path(r"C:\HIMA-Prooftest-Solution-Current\Results Structures")


def bundled_results_structures_seed() -> Path:
    """CSVs shipped next to the solution code (seed source for station catalogue)."""
    return _solution_root() / "Results Structures"


def default_results_structures() -> Path:
    """Runtime Results Structure catalogue under the station root on C:."""
    return DEFAULT_RESULTS_STRUCTURES


def default_reports_folder() -> Path:
    return DEFAULT_REPORTS_FOLDER


def default_sqlite_path() -> Path:
    return DEFAULT_SQLITE_PATH


def default_report_templates() -> Path:
    """HTML/PDF report templates under the station Reports folder."""
    return DEFAULT_REPORT_TEMPLATES


def ensure_station_root(root: Path | None = None) -> Path:
    """
    Create ``C:\\HIMA Prooftest Reporting Tool`` with the three required folders:

    1. ``Database``
    2. ``HIMA Automated Prooftest Reports`` (+ ``Report Templates`` subfolder)
    3. ``Results Structures``
    """
    base = Path(root) if root else STATION_ROOT
    for path in (
        base,
        base / "Database",
        base / "HIMA Automated Prooftest Reports",
        base / "HIMA Automated Prooftest Reports" / "Report Templates",
        base / "Results Structures",
        base / "Results Structures" / "Annexes",
    ):
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            log.warning("Cannot create station path %s: %s", path, exc)
    return base


def _merge_tree(src: Path, dest: Path) -> int:
    """Copy all files from src into dest (newer/different size overwrites). Returns file count."""
    if not src.is_dir():
        return 0
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except OSError:
        return 0
    count = 0
    for path in src.rglob("*"):
        if path.is_dir():
            try:
                (dest / path.relative_to(src)).mkdir(parents=True, exist_ok=True)
            except OSError:
                pass
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        out = dest / rel
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            if (
                not out.exists()
                or path.stat().st_mtime > out.stat().st_mtime
                or path.stat().st_size != out.stat().st_size
            ):
                shutil.copy2(path, out)
                count += 1
                log.info("Migrated %s -> %s", path, out)
        except OSError as exc:
            log.warning("Cannot migrate %s: %s", path, exc)
    return count


def _move_or_merge_legacy_dir(legacy: Path, dest: Path, label: str) -> None:
    """
    Move the entire legacy folder into ``dest`` under the station root.

    If ``dest`` does not exist yet → ``shutil.move``.
    If ``dest`` already exists → merge contents, then remove ``legacy``.
    """
    if not legacy.is_dir():
        return
    try:
        if legacy.resolve() == dest.resolve():
            return
    except OSError:
        return

    if not dest.exists():
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(legacy), str(dest))
            log.info("Moved %s folder %s -> %s", label, legacy, dest)
            return
        except OSError as exc:
            log.warning("Cannot move %s %s -> %s (%s); trying merge", label, legacy, dest, exc)

    merged = _merge_tree(legacy, dest)
    log.info("Merged %s from %s into %s (%s file(s))", label, legacy, dest, merged)
    try:
        shutil.rmtree(legacy)
        log.info("Removed legacy %s folder %s", label, legacy)
    except OSError as exc:
        log.warning("Could not remove legacy %s folder %s: %s", label, legacy, exc)


def migrate_legacy_station_data(
    reports: Path,
    results: Path,
    sqlite_path: Path,
) -> None:
    """Move pre-v1.46 C: locations into ``C:\\HIMA Prooftest Reporting Tool``."""
    _move_or_merge_legacy_dir(_LEGACY_REPORTS, reports, "Reports")
    _move_or_merge_legacy_dir(_LEGACY_RESULTS, results, "Results Structures")
    legacy_sqlite = _solution_root() / "Annex codes" / "data" / "prooftest.db"
    if legacy_sqlite.is_file() and not sqlite_path.exists():
        try:
            sqlite_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(legacy_sqlite, sqlite_path)
            log.info("Migrated SQLite DB -> %s", sqlite_path)
        except OSError as exc:
            log.warning("Cannot migrate SQLite DB: %s", exc)


def ensure_results_structures_catalogue(
    target: Path | None = None,
    seed: Path | None = None,
) -> Path:
    """
    Ensure the station ``Results Structures`` folder exists and is seeded.

    Copies any missing ``*.csv`` from the package seed folder. New Results types
    are added by placing CSVs in this C: catalogue folder.
    """
    dest = Path(target) if target else default_results_structures()
    src = Path(seed) if seed else bundled_results_structures_seed()
    try:
        dest.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        log.warning("Cannot create Results Structures catalogue %s: %s", dest, exc)
        return dest
    if src.is_dir() and src.resolve() != dest.resolve():
        for pattern in ("*.csv", "Annexes/*.csv"):
            for csv_path in src.glob(pattern):
                rel = csv_path.relative_to(src)
                out = dest / rel
                if out.exists():
                    continue
                try:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(csv_path, out)
                    log.info("Seeded Results Structure CSV -> %s", out)
                except OSError as exc:
                    log.warning("Cannot seed %s: %s", out, exc)
    return dest






_SQL_TEMPLATE_CANDIDATES = (
    Path(r"C:\Project\Report Solution\2- SQL Tables template"),
    Path(r"Z:\Project\Report Solution\2- SQL Tables template"),
)


def resolve_sql_templates(configured: Path | None = None) -> Path:
    """Prefer configured path; else C:\\ then Z:\\ project templates (SPEC Step 1.3)."""
    if configured and Path(configured).exists():
        return Path(configured)
    for candidate in _SQL_TEMPLATE_CANDIDATES:
        if candidate.exists():
            return candidate
    if configured:
        return Path(configured)
    return _SQL_TEMPLATE_CANDIDATES[0]

@dataclass
class AppConfig:
    deployment_case: int = 1  # always 1 — unified mode (former Case 2 folded into API→OPC path)
    auto_detect_case: bool = False  # obsolete; ignored (always unified)
    auto_start: bool = True
    auto_start_trigger: str = "logon"
    auto_start_delay_sec: int = 90
    health_check_wait_sec: int = 120
    first_run_folder: Path = field(default_factory=default_reports_folder)
    results_structures: Path = field(default_factory=default_results_structures)
    sql_templates: Path = Path()
    db_name: str = "HIMA Automated Prooftest"
    db_server: str = r"localhost\SQLEXPRESS"
    db_driver: str = "ODBC Driver 17 for SQL Server"
    db_trusted: bool = True
    fallback_sqlite: bool = True
    sqlite_path: Path = field(default_factory=default_sqlite_path)
    silworx_projects: List[Path] = field(default_factory=list)
    silworx_programdata: Path = Path(r"C:\ProgramData")
    silworx_api_host: str = "127.0.0.1"
    silworx_api_port: int = 51710
    silworx_api_port_start: int = 51710
    silworx_api_port_count: int = 10
    silworx_plugin_port_start: int = 8400
    silworx_plugin_port: int | None = None
    silworx_api_cert: Path | None = None
    silworx_api_client_cert_dir: Path | None = None
    silworx_api_timeout_sec: float = 120.0
    silworx_api_open_timeout_sec: float = 600.0
    silworx_plugin_name: str = "prooftest_session_plugin"
    plugin_monitor_enabled: bool = True
    sync_triggers: List[str] = field(
        default_factory=lambda: [
            "silworx_session",
            "code_generation",
            "download",
            "results_structures",
        ]
    )
    case1_sync_poll_sec: float = 2.0
    opc_discover_all: bool = True
    opc_server_filter: List[str] = field(default_factory=lambda: ["HIMA.*"])
    poll_interval_sec: float = 1.0
    device_list_poll_sec: float = 2.0
    template_poll_sec: float = 1.0
    opc_shape_gate_ratio: float = 0.5
    opc_shape_gate_floor: int = 3
    report_format: str = "html"
    report_output: Path = Path()
    report_mirror: Path = Path()
    report_filename_pattern: str = "{Device_TAG}_{DateTime:yyyy-MM-dd_HH-mm-ss}"
    report_decimal_places: int = 3
    report_html_templates: Path = field(default_factory=default_report_templates)
    report_html_seed: Path | None = None
    web_host: str = "127.0.0.1"
    web_port: int = 8080
    web_auth_enabled: bool = False
    web_auth_token: str = ""
    web_localhost_bypass: bool = True
    require_auth_when_non_local: bool = True
    auth_bind_warning: bool = False
    ini_path: Path = field(default_factory=_default_ini)

    @classmethod
    def load(cls, ini_path: Path | None = None) -> "AppConfig":
        path = ini_path or _default_ini()
        path = path.resolve()
        parser = configparser.ConfigParser()
        parser.read(path, encoding="utf-8")
        cfg = cls()
        cfg.ini_path = path

        if parser.has_section("Service"):
            # Always unified mode (legacy deployment_case=2 in old ini is ignored).
            _ = parser.getint("Service", "deployment_case", fallback=1)
            cfg.deployment_case = 1
            cfg.auto_detect_case = parser.getboolean("Service", "auto_detect_case", fallback=False)
            cfg.auto_start = parser.getboolean("Service", "auto_start", fallback=True)
            cfg.auto_start_trigger = parser.get("Service", "auto_start_trigger", fallback="logon").strip().lower()
            cfg.auto_start_delay_sec = parser.getint("Service", "auto_start_delay_sec", fallback=90)
            cfg.health_check_wait_sec = parser.getint("Service", "health_check_wait_sec", fallback=120)

        if parser.has_section("Paths"):
            cfg.first_run_folder = Path(parser.get("Paths", "first_run_folder"))
            rs = parser.get("Paths", "results_structures", fallback="").strip()
            # Runtime catalogue must live on C: unless an absolute override is set.
            if rs and Path(rs).is_absolute():
                cfg.results_structures = Path(rs)
            else:
                cfg.results_structures = default_results_structures()
            st = parser.get("Paths", "sql_templates", fallback="").strip()
            if st:
                cfg.sql_templates = Path(st)
                if not cfg.sql_templates.is_absolute():
                    cfg.sql_templates = (_solution_root() / cfg.sql_templates).resolve()
            else:
                cfg.sql_templates = Path()  # empty = unused (design-ref optional)

        if parser.has_section("Database"):
            cfg.db_name = parser.get("Database", "name", fallback=cfg.db_name)
            cfg.db_server = parser.get("Database", "server", fallback=cfg.db_server)
            cfg.db_driver = parser.get("Database", "driver", fallback=cfg.db_driver)
            cfg.db_trusted = parser.getboolean("Database", "trusted_connection", fallback=True)
            cfg.fallback_sqlite = parser.getboolean("Database", "fallback_sqlite", fallback=True)
            raw_sqlite = parser.get("Database", "sqlite_path", fallback="").strip()
            if raw_sqlite:
                cfg.sqlite_path = Path(raw_sqlite)
            else:
                cfg.sqlite_path = default_sqlite_path()

        if parser.has_section("SILworX"):
            projects = parser.get("SILworX", "projects", fallback="")
            cfg.silworx_projects = [Path(p.strip()) for p in projects.split(",") if p.strip()]
            programdata = parser.get("SILworX", "programdata_root", fallback=r"C:\ProgramData")
            cfg.silworx_programdata = Path(programdata)
            triggers = parser.get(
                "SILworX",
                "sync_triggers",
                fallback="silworx_session, code_generation, download, results_structures",
            )
            cfg.sync_triggers = [t.strip() for t in triggers.split(",") if t.strip()]
            cfg.silworx_api_host = parser.get("SILworX", "api_host", fallback=cfg.silworx_api_host)
            cfg.silworx_api_port = parser.getint("SILworX", "api_port", fallback=cfg.silworx_api_port)
            cfg.silworx_api_port_start = parser.getint(
                "SILworX", "api_port_start", fallback=cfg.silworx_api_port_start
            )
            cfg.silworx_api_port_count = parser.getint(
                "SILworX", "api_port_count", fallback=cfg.silworx_api_port_count
            )
            cfg.silworx_plugin_port_start = parser.getint(
                "SILworX", "api_plugin_port_start", fallback=cfg.silworx_plugin_port_start
            )
            if parser.has_option("SILworX", "api_plugin_port"):
                cfg.silworx_plugin_port = parser.getint("SILworX", "api_plugin_port")
            else:
                cfg.silworx_plugin_port = cfg.silworx_plugin_port_start + (
                    cfg.silworx_api_port - cfg.silworx_api_port_start
                )
            cert = parser.get("SILworX", "api_cert", fallback="").strip()
            if cert:
                cfg.silworx_api_cert = Path(cert)
            client_dir = parser.get("SILworX", "api_client_cert_dir", fallback="").strip()
            if client_dir:
                cfg.silworx_api_client_cert_dir = Path(client_dir)
            cfg.silworx_api_timeout_sec = parser.getfloat(
                "SILworX", "api_timeout_sec", fallback=cfg.silworx_api_timeout_sec
            )
            cfg.silworx_api_open_timeout_sec = parser.getfloat(
                "SILworX", "api_open_timeout_sec", fallback=cfg.silworx_api_open_timeout_sec
            )
            cfg.silworx_plugin_name = parser.get(
                "SILworX", "api_plugin_name", fallback=cfg.silworx_plugin_name
            )
            cfg.plugin_monitor_enabled = parser.getboolean(
                "SILworX", "plugin_monitor_enabled", fallback=cfg.plugin_monitor_enabled
            )

        if parser.has_section("OPC"):
            cfg.opc_discover_all = parser.getboolean("OPC", "discover_all_servers", fallback=True)
            # HIMA X-OPC registers as ProgID "HIMA.*" regardless of the product display name.
            filt = parser.get("OPC", "server_filter", fallback="HIMA.*")
            cfg.opc_server_filter = [f.strip() for f in filt.split(";") if f.strip()]
            cfg.poll_interval_sec = parser.getfloat("OPC", "poll_interval_sec", fallback=1.0)
            cfg.device_list_poll_sec = parser.getfloat("OPC", "device_list_poll_sec", fallback=2.0)
            cfg.case1_sync_poll_sec = parser.getfloat("OPC", "case1_sync_poll_sec", fallback=2.0)
            cfg.template_poll_sec = parser.getfloat("OPC", "template_poll_sec", fallback=1.0)
            cfg.opc_shape_gate_ratio = parser.getfloat(
                "OPC", "shape_gate_ratio", fallback=cfg.opc_shape_gate_ratio
            )
            cfg.opc_shape_gate_floor = parser.getint(
                "OPC", "shape_gate_floor", fallback=cfg.opc_shape_gate_floor
            )

        if parser.has_section("Reports"):
            cfg.report_format = parser.get("Reports", "format", fallback="html").lower()
            cfg.report_output = Path(parser.get("Reports", "output_directory"))
            cfg.report_mirror = Path(parser.get("Reports", "local_mirror"))
            cfg.report_filename_pattern = parser.get("Reports", "filename_pattern", fallback=cfg.report_filename_pattern)
            cfg.report_decimal_places = parser.getint("Reports", "decimal_places", fallback=3)
            templates = parser.get("Reports", "html_templates", fallback="").strip()
            if templates:
                cfg.report_html_templates = Path(templates)
            else:
                cfg.report_html_templates = default_report_templates()
            seed = parser.get("Reports", "html_templates_seed", fallback="").strip()
            if seed:
                cfg.report_html_seed = Path(seed)

        if parser.has_section("Web"):
            cfg.web_host = parser.get("Web", "host", fallback=cfg.web_host)
            cfg.web_port = parser.getint("Web", "port", fallback=8080)
            cfg.web_auth_enabled = parser.getboolean("Web", "auth_enabled", fallback=False)
            cfg.web_auth_token = parser.get("Web", "auth_token", fallback="").strip()
            cfg.web_localhost_bypass = parser.getboolean("Web", "auth_localhost_bypass", fallback=True)
            cfg.require_auth_when_non_local = parser.getboolean(
                "Web", "require_auth_when_non_local", fallback=True
            )
            if cfg.web_auth_enabled and not cfg.web_auth_token:
                log = logging.getLogger(__name__)
                log.warning("Web auth_enabled=true but auth_token empty — authentication disabled")
                cfg.web_auth_enabled = False

        cfg.apply_auth_bind_policy()
        cfg.normalize_report_paths()
        if not cfg.sqlite_path.is_absolute():
            cfg.sqlite_path = (_solution_root() / cfg.sqlite_path).resolve()
        ensure_station_root(STATION_ROOT)
        migrate_legacy_station_data(
            cfg.first_run_folder,
            cfg.results_structures,
            cfg.sqlite_path,
        )
        ensure_results_structures_catalogue(cfg.results_structures)
        return cfg

    def is_loopback_web_host(self) -> bool:
        host = (self.web_host or "").strip().lower()
        return host in ("127.0.0.1", "::1", "localhost")

    def apply_auth_bind_policy(self) -> None:
        """R4: warn or refuse non-loopback bind without auth."""
        log = logging.getLogger(__name__)
        self.auth_bind_warning = False
        if self.is_loopback_web_host() or self.web_auth_enabled:
            return
        msg = (
            f"web_host={self.web_host!r} is not loopback and web_auth_enabled=false — "
            "enable [Web] auth_enabled=true + auth_token, or bind 127.0.0.1"
        )
        self.auth_bind_warning = True
        if self.require_auth_when_non_local:
            log.error("SECURITY: %s (require_auth_when_non_local=true)", msg)
            raise ValueError(msg)
        log.warning("SECURITY: %s", msg)

    def normalize_report_paths(self) -> None:
        """Ensure report output defaults to the station reports folder on C:\\."""
        if not self.report_output or str(self.report_output).strip() in ("", "."):
            self.report_output = self.first_run_folder
        if not self.report_mirror or str(self.report_mirror).strip() in ("", "."):
            self.report_mirror = self.first_run_folder

    def ensure_data_dirs(self) -> None:
        ensure_station_root(STATION_ROOT)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.report_output.mkdir(parents=True, exist_ok=True)
        self.first_run_folder.mkdir(parents=True, exist_ok=True)
        self.report_html_templates.mkdir(parents=True, exist_ok=True)
        ensure_results_structures_catalogue(self.results_structures)
