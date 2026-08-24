from __future__ import annotations

import configparser
import json
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, TYPE_CHECKING

from prooftest.alarms import AlarmManager
from prooftest.config import AppConfig

if TYPE_CHECKING:
    from prooftest.annex_api_connexion import SilworxApiClient

log = logging.getLogger(__name__)

_SILWORX_DOWN_PROBE_THRESHOLD = 2


@dataclass
class SilworxOpenProject:
    silworx_version: str
    session_id: str
    project_name: str
    project_file: str
    src_path: Path
    data_path: Path
    temp_path: Path
    session_root: Path
    lock_ini: Path


def _read_marker(marker: Path) -> float:
    if not marker.exists():
        return 0.0
    try:
        return float(marker.read_text(encoding="utf-8").strip())
    except ValueError:
        return 0.0


def _path_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _parse_lock_ini(lock_path: Path) -> Dict[str, str]:
    parser = configparser.ConfigParser()
    parser.read(lock_path, encoding="utf-8")
    section = parser["lock"] if parser.has_section("lock") else {}
    return {k: v for k, v in section.items()}


def discover_open_projects(programdata_root: Path) -> List[SilworxOpenProject]:
    """Find all SILworX sessions with an active lock.ini (project open in SILworX)."""
    if not programdata_root.is_dir():
        return []
    found: List[SilworxOpenProject] = []
    for version_dir in sorted(programdata_root.glob("SILworX_v*")):
        sessions_root = version_dir / "sessions"
        if not sessions_root.is_dir():
            continue
        for session_dir in sessions_root.iterdir():
            if not session_dir.is_dir():
                continue
            lock_ini = session_dir / "lock.ini"
            if not lock_ini.exists():
                continue
            try:
                lock = _parse_lock_ini(lock_ini)
            except Exception as exc:
                log.debug("Cannot parse %s: %s", lock_ini, exc)
                continue
            src_raw = lock.get("src", "").strip()
            data_raw = lock.get("data", "").strip()
            if not src_raw or not data_raw:
                continue
            src_path = Path(src_raw)
            project_file = src_path.name
            project_name = src_path.stem
            found.append(
                SilworxOpenProject(
                    silworx_version=version_dir.name,
                    session_id=session_dir.name,
                    project_name=project_name,
                    project_file=project_file,
                    src_path=src_path,
                    data_path=Path(data_raw),
                    temp_path=Path(lock.get("temp", "").strip()) if lock.get("temp") else session_dir / "temp",
                    session_root=session_dir,
                    lock_ini=lock_ini,
                )
            )
    return found


def is_silworx_open(programdata_root: Path) -> bool:
    return bool(discover_open_projects(programdata_root))


def pick_configured_session(
    sessions: List[SilworxOpenProject],
    configured_projects: List[Path],
    *,
    preferred_version_substr: str = "",
) -> Optional[SilworxOpenProject]:
    """
    Choose which open SILworX session is "active" for UI/state.

    Preference order:
      1. Exact configured project path match
      2. Configured project stem / filename fuzzy match (e.g. V16 suffix)
      3. Session whose SILworX version matches a live API instance version
      4. First open session
    """
    if not sessions:
        return None

    def _norm(path: Path) -> str:
        try:
            return str(path.resolve()).lower()
        except OSError:
            return str(path).lower()

    configured = {_norm(p) for p in configured_projects}
    if configured:
        for session in sessions:
            try:
                if _norm(session.src_path) in configured:
                    return session
            except OSError:
                continue
        # Fuzzy: configured "ProofTest-Reporting solution.E3" vs open "... - V16.0.0.E3"
        for configured_path in configured_projects:
            stem = configured_path.stem.lower().replace(" ", "")
            name = configured_path.name.lower()
            for session in sessions:
                src_name = session.src_path.name.lower()
                src_stem = session.src_path.stem.lower().replace(" ", "")
                file_name = (session.project_file or "").lower()
                if name and (name in src_name or name in file_name):
                    return session
                if stem and stem in src_stem.replace("-", ""):
                    return session
                if stem and stem in (session.project_name or "").lower().replace(" ", ""):
                    return session

    if preferred_version_substr:
        token = preferred_version_substr.lower().strip()
        for session in sessions:
            if token and token in (session.silworx_version or "").lower():
                return session

    return sessions[0]


def session_working_mtime(session: SilworxOpenProject) -> float:
    """Fast mtime signal for the live session database (avoid full c3data rglob)."""
    c3data = session.data_path / "c3data"
    if not c3data.is_dir():
        return _path_mtime(session.data_path)
    latest = _path_mtime(c3data)
    try:
        # Top-level files + one directory level is enough to catch SILworX saves.
        for path in c3data.iterdir():
            latest = max(latest, _path_mtime(path))
            if path.is_dir():
                for child in path.iterdir():
                    latest = max(latest, _path_mtime(child))
                    if child.is_dir():
                        latest = max(latest, _path_mtime(child))
    except OSError:
        pass
    return latest


def folder_aggregate_mtime(folder: Path, pattern: str = "*.csv") -> float:
    if not folder.is_dir():
        return 0.0
    latest = 0.0
    for match in folder.glob(pattern):
        if match.is_file():
            latest = max(latest, _path_mtime(match))
    return latest


def watch_mtime_increased(source_mtime: float, marker: Path) -> bool:
    if source_mtime <= 0:
        return False
    return source_mtime > _read_marker(marker)


def commit_marker(marker: Path, source_mtime: float) -> None:
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(source_mtime), encoding="utf-8")


def watch_project_changed(project_path: Path, marker: Path) -> bool:
    if not project_path.exists():
        return False
    lock = project_path.with_suffix(project_path.suffix + ".lock")
    if lock.exists():
        return False
    return watch_mtime_increased(_path_mtime(project_path), marker)


def watch_results_structures_changed(folder: Path, marker: Path) -> bool:
    """True when Results Structure CSV folder mtime advanced.

    A new ``*.csv`` in ``Results Structures\\`` is a **new Results type** (device
    type). Reload catalogue → create ``ProofTest_*`` table + report folder, then
    refresh so globals of that type are discovered. Editing an existing CSV
    updates the type definition; devices remain SILworX globals of that type.
    """
    return watch_mtime_increased(folder_aggregate_mtime(folder), marker)


def watch_session_changed(session: SilworxOpenProject, marker: Path) -> bool:
    return watch_mtime_increased(session_working_mtime(session), marker)


def silworx_session_to_state(session: Optional[SilworxOpenProject]) -> Dict[str, str]:
    if session is None:
        return {
            "silworx_open": "0",
            "silworx_project_name": "",
            "silworx_project_file": "",
            "silworx_project_src": "",
            "silworx_session_data": "",
            "silworx_version": "",
            "silworx_session_id": "",
            "session_id": "",
            "project_state": "",
            "project_name": "",
        }
    return {
        "silworx_open": "1",
        "silworx_project_name": session.project_name,
        "silworx_project_file": session.project_file,
        "silworx_project_src": str(session.src_path),
        "silworx_session_data": str(session.data_path),
        "silworx_version": session.silworx_version,
        "silworx_session_id": session.session_id,
        "session_id": session.session_id,
        "project_state": "open",
        "project_name": session.project_name,
    }


def silworx_open_projects_state(sessions: List[SilworxOpenProject]) -> Dict[str, str]:
    """Service-state fields listing every open SILworX project (not only the preferred one)."""
    names = [s.project_name for s in sessions if (s.project_name or "").strip()]
    files = [s.project_file for s in sessions if (s.project_file or "").strip()]
    ids = [s.session_id for s in sessions if (s.session_id or "").strip()]
    return {
        "silworx_open_count": str(len(sessions)),
        "silworx_open_projects": ";".join(names),
        "silworx_open_project_files": ";".join(files),
        "silworx_open_session_ids": ";".join(ids),
    }


@dataclass
class SilworxSyncTriggers:
    """Unified SILworX API/plugin sync (formerly Case1SyncTriggers)."""
    config: AppConfig
    markers_dir: Path
    active_session: Optional[SilworxOpenProject] = None
    open_sessions: List[SilworxOpenProject] = field(default_factory=list)
    _plugin_monitor: Optional[object] = field(default=None, repr=False)
    _api_clients: Dict[int, "SilworxApiClient"] = field(default_factory=dict, repr=False)
    _available_instances: List[object] = field(default_factory=list, repr=False)
    _instances_scanned_at: float = field(default=0.0, repr=False)
    _active_api_port: Optional[int] = field(default=None, repr=False)
    _api_opened_by_service: bool = field(default=False, repr=False)
    _service_owns_api_session: bool = field(default=False, repr=False)
    _owned_sessions_by_port: Dict[int, str] = field(default_factory=dict, repr=False)
    _attached_session_ids_by_api: Dict[int, str] = field(default_factory=dict, repr=False)
    _attached_project_names_by_api: Dict[int, str] = field(default_factory=dict, repr=False)
    _last_attached_api_port: Optional[int] = field(default=None, repr=False)
    _silworx_api_suspended: bool = field(default=False, repr=False)
    _operator_detached: bool = field(default=False, repr=False)
    _silworx_down_streak: int = field(default=0, repr=False)
    _silworx_session_was_active: bool = field(default=False, repr=False)
    _silworx_close_detected_at: Optional[float] = field(default=None, repr=False)
    _silworx_c3_cleanup_done: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        self._enabled = {t.strip().lower() for t in self.config.sync_triggers if t.strip()}

    def is_api_suspended(self) -> bool:
        """True when SILworX is down and the service must not open API sessions."""
        return self._silworx_api_suspended

    def is_operator_detached(self) -> bool:
        """True after Disconnect until Connect — do not auto-resume plugin/API."""
        return bool(getattr(self, "_operator_detached", False))

    def owns_api_session(self) -> bool:
        """True when this service still tracks an owned API session (legacy; tool no longer opens projects)."""
        return bool(self._owned_sessions_by_port)

    def discover_api_instances(self, *, force: bool = False) -> List[object]:
        """Scan all configured API/plugin port pairs and cache reachable instances."""
        import time

        from prooftest.annex_api_connexion import discover_available_instances

        if (
            not force
            and self._available_instances
            and time.monotonic() - self._instances_scanned_at < self.config.case1_sync_poll_sec
        ):
            return self._available_instances
        self._available_instances = discover_available_instances(self.config)
        self._instances_scanned_at = time.monotonic()
        return self._available_instances

    def api_instance_labels(self) -> str:
        return ";".join(inst.label for inst in self._available_instances)

    def _api_port_order(self) -> List[int]:
        ports = [inst.api_port for inst in self._available_instances]
        preferred = self.config.silworx_api_port
        if preferred in ports:
            return [preferred] + [port for port in sorted(ports) if port != preferred]
        return sorted(ports)

    def _mark_service_opened_session(self, session_id: str, api_port: int) -> None:
        self._service_owns_api_session = True
        self._owned_sessions_by_port[api_port] = session_id
        self._active_api_port = api_port

    def _clear_service_opened_session(self, api_port: Optional[int] = None) -> None:
        if api_port is None:
            self._owned_sessions_by_port.clear()
        else:
            self._owned_sessions_by_port.pop(api_port, None)
        if not self._owned_sessions_by_port:
            self._service_owns_api_session = False

    def _ensure_silworx_api_available(self) -> None:
        from prooftest.annex_api_connexion import SilworxApiConnectionError

        if self._silworx_api_suspended:
            raise SilworxApiConnectionError("SILworX API suspended — no instances available")
        instances = self.discover_api_instances()
        if not instances:
            self._silworx_api_suspended = True
            raise SilworxApiConnectionError(
                f"SILworX API unavailable on {self.config.silworx_api_host} "
                f"ports {self.config.silworx_api_port_start}-"
                f"{self.config.silworx_api_port_start + self.config.silworx_api_port_count - 1}"
            )

    def get_api_client(self, api_port: Optional[int] = None) -> "SilworxApiClient":
        """Lazy SILworX OpenAPI client for one API port."""
        from prooftest.annex_api_connexion import build_client_for_port

        port = api_port or self._active_api_port or self.config.silworx_api_port
        if port not in self._api_clients:
            self._api_clients[port] = build_client_for_port(self.config, port)
        self._active_api_port = port
        return self._api_clients[port]

    def request_fresh_plugin_session(self, api_port: Optional[int] = None) -> None:
        """Drop cached plugin tokens and reconnect so SILworX issues a new user_session_id."""
        if self._plugin_monitor is None:
            return
        from prooftest.annex_api_connexion import plugin_port_for_api

        plugin_port = None if api_port is None else plugin_port_for_api(api_port, self.config)
        self._plugin_monitor.request_fresh_session(plugin_port)

    def _try_attach_gui_session_on_port(self, api_port: int) -> bool:
        from prooftest.annex_api_connexion import (
            plugin_port_for_api,
        )

        self.refresh_open_sessions()
        if not self.open_sessions:
            return False
        plugin_port = plugin_port_for_api(api_port, self.config)

        # Reuse a cached attach only when the plugin still reports the same session.
        cached_sid = (self._attached_session_ids_by_api.get(api_port) or "").strip()
        live_sid = ""
        if self._plugin_monitor is not None:
            try:
                live_sid = (self._plugin_monitor.get_session_id(plugin_port) or "").strip()
            except Exception:
                live_sid = ""
        if cached_sid and (not live_sid or live_sid == cached_sid):
            client = self.get_api_client(api_port)
            client.set_session_id(cached_sid)
            return True
        if cached_sid and live_sid and live_sid != cached_sid:
            log.info(
                "SILworX plugin session changed on %s/%s — re-attaching",
                api_port,
                plugin_port,
            )
            self._attached_session_ids_by_api.pop(api_port, None)
            self._attached_project_names_by_api.pop(api_port, None)

        if self._attach_with_resolved_session(api_port, plugin_port, wait_timeout_sec=8.0):
            return True

        log.info(
            "SILworX plugin session unusable on %s/%s — re-registering for a fresh token",
            api_port,
            plugin_port,
        )
        self.request_fresh_plugin_session(api_port)
        if self._attach_with_resolved_session(api_port, plugin_port, wait_timeout_sec=12.0):
            return True
        return False

    def _infer_attached_project_name(
        self,
        api_port: int,
        session_id: str,
        tree: object,
    ) -> str:
        """Map an attached API session to one open lock.ini project (multi-project safe)."""
        sid = (session_id or "").strip()
        sid_l = sid.lower()
        for session in self.open_sessions:
            if (session.session_id or "").strip().lower() == sid_l:
                return session.project_name
            # Plugin tokens sometimes embed / prefix the ProgramData session id.
            sess = (session.session_id or "").strip().lower()
            if sess and (sess in sid_l or sid_l in sess):
                return session.project_name

        claimed = {
            (name or "").strip()
            for port, name in self._attached_project_names_by_api.items()
            if port != api_port and (name or "").strip()
        }
        try:
            blob = json.dumps(tree, ensure_ascii=False).lower()
        except Exception:
            blob = ""
        candidates: List[tuple[int, str]] = []
        if blob:
            for session in self.open_sessions:
                name = (session.project_name or "").strip()
                file_name = (session.project_file or "").strip()
                if not name:
                    continue
                if name in claimed:
                    continue
                name_l = name.lower()
                file_l = file_name.lower()
                if name_l and name_l in blob:
                    candidates.append((len(name_l), name))
                elif file_l and file_l in blob:
                    candidates.append((len(file_l), name))
            if not candidates:
                # Last resort: allow already-claimed names (same project on two ports).
                for session in self.open_sessions:
                    name = (session.project_name or "").strip()
                    if name and name.lower() in blob:
                        candidates.append((len(name), name))
        if candidates:
            candidates.sort(key=lambda item: (-item[0], item[1]))
            return candidates[0][1]
        return ""

    def _attach_with_resolved_session(
        self,
        api_port: int,
        plugin_port: int,
        *,
        wait_timeout_sec: float = 0.0,
    ) -> bool:
        from prooftest.annex_api_connexion import (
            SilworxApiError,
            resolve_gui_session_id,
        )

        session_id = resolve_gui_session_id(
            self.config,
            api_port,
            plugin_monitor=self._plugin_monitor,
            timeout_sec=max(wait_timeout_sec, 15.0) if wait_timeout_sec else 15.0,
        )
        if not session_id:
            return False
        client = self.get_api_client(api_port)
        client.set_session_id(session_id)
        try:
            tree = client.get_structuretree()
        except SilworxApiError as exc:
            log.warning(
                "SILworX GUI session rejected on %s/%s (%s)",
                api_port,
                plugin_port,
                exc,
            )
            client.clear_session_id()
            self._attached_session_ids_by_api.pop(api_port, None)
            self._attached_project_names_by_api.pop(api_port, None)
            return False
        self.refresh_open_sessions()
        matched_project = self._infer_attached_project_name(api_port, session_id, tree)
        self._attached_session_ids_by_api[api_port] = session_id
        self._attached_project_names_by_api[api_port] = matched_project
        self._last_attached_api_port = api_port
        log.info(
            "Attached SILworX API %s / plugin %s → project=%s session=%s (preferred UI=%s)",
            api_port,
            plugin_port,
            matched_project or "?",
            session_id[:16] + ("…" if len(session_id) > 16 else ""),
            self.active_session.project_name if self.active_session else "?",
        )
        return True

    def attached_project_name_for_port(self, api_port: int) -> str:
        """SILworX project name last attached on this API port."""
        name = (self._attached_project_names_by_api.get(api_port) or "").strip()
        if name:
            return name
        session_id = (self._attached_session_ids_by_api.get(api_port) or "").strip()
        if session_id:
            inferred = self._infer_attached_project_name(api_port, session_id, {})
            if inferred:
                return inferred
        # Only fall back to the preferred UI session when a single project is open.
        if len(self.open_sessions) <= 1:
            return self.api_connected_project_name("api")
        return ""

    def uncovered_open_projects(self) -> List[str]:
        """
        Open lock.ini projects not yet mapped to an attached API port.

        When more projects are open than SILworX API instances, only the
        instance count can be scanned (one project per API port). Remaining
        lock.ini entries are not treated as uncovered forever.
        """
        self.refresh_open_sessions()
        if not self.open_sessions:
            return []
        instances = list(self._available_instances or [])
        if not instances:
            try:
                instances = list(self.discover_api_instances() or [])
            except Exception:
                instances = []
        scanned_ports = {
            port
            for port, sid in (self._attached_session_ids_by_api or {}).items()
            if (sid or "").strip()
        }
        attached_names = {
            (name or "").strip()
            for name in (self._attached_project_names_by_api or {}).values()
            if (name or "").strip()
        }
        capacity = len(instances) if instances else 0
        if capacity and len(scanned_ports) >= capacity:
            # Every reachable SILworX instance was scanned at least once.
            return []
        return [
            s.project_name
            for s in self.open_sessions
            if (s.project_name or "").strip() and s.project_name not in attached_names
        ]

    @contextmanager
    def api_session_for_port(
        self,
        api_port: int,
        project_path: Optional[Path] = None,
        alarms: Optional[AlarmManager] = None,
        *,
        allow_open_local: bool = False,
    ) -> Iterator["SilworxApiClient"]:
        """
        API session on one SILworX instance — attach only.

        The report tool never opens a SILworX project (no ``open/local``).
        If the user has no project open on this port, raise conflict so the
        caller falls back to OPC device-list scan.
        """
        from prooftest.annex_api_connexion import SilworxProjectConflictError

        _ = project_path, allow_open_local  # never open a project; kept for call-site compatibility
        self._ensure_silworx_api_available()
        client = self.get_api_client(api_port)

        if self._try_attach_gui_session_on_port(api_port):
            sid = (self._attached_session_ids_by_api.get(api_port) or "").strip()
            if sid:
                client.set_session_id(sid)
            try:
                yield client
            finally:
                # Keep the attach map for multi-instance discovery; only clear the
                # client handle so the next port/session bind starts clean.
                client.clear_session_id()
            return

        raise SilworxProjectConflictError(
            417,
            "attach-only",
            f"No user-open project on API port {api_port} — report tool does not open SILworX projects",
        )

    @contextmanager
    def api_session(
        self,
        project_path: Optional[Path] = None,
        alarms: Optional[AlarmManager] = None,
    ) -> Iterator["SilworxApiClient"]:
        """
        Provide an API client bound to a user-open SILworX project.

        Scans reachable API/plugin port pairs (G-21). Never opens a project.
        If no GUI project is open, raises so the device list can use OPC.
        """
        from prooftest.annex_api_connexion import (
            SilworxApiError,
            SilworxProjectConflictError,
        )

        self._ensure_silworx_api_available()
        _ = project_path  # unused — tool never opens a project file
        self.refresh_active_session()

        if self.active_session is not None:
            for api_port in self._api_port_order():
                if self._try_attach_gui_session_on_port(api_port):
                    client = self.get_api_client(api_port)
                    try:
                        yield client
                    finally:
                        client.clear_session_id()
                    return

        last_conflict: Optional[SilworxProjectConflictError] = None
        last_error: Optional[Exception] = None
        for api_port in self._api_port_order():
            try:
                with self.api_session_for_port(api_port, alarms=alarms) as client:
                    yield client
                return
            except SilworxProjectConflictError as exc:
                last_conflict = exc
                continue
            except SilworxApiError as exc:
                last_error = exc
                continue

        if last_conflict is not None:
            if alarms is not None:
                alarms.raise_alarm(
                    "S2-C1",
                    "SILworX API: no user-open project (or session id unavailable) — OPC device list",
                    cause=str(last_conflict),
                    severity="Warning",
                    show_popup=False,
                )
            raise last_conflict
        if last_error is not None:
            raise last_error
        raise SilworxApiError("No SILworX API port could provide a project session")

    def try_close_owned_session(self) -> bool:
        """Best-effort close for open/local sessions on all owned API ports."""
        if not self.owns_api_session():
            return True
        from prooftest.annex_api_connexion import _SILWORX_CLOSE_PROBE_TIMEOUT_SEC

        all_closed = True
        for api_port, session_id in list(self._owned_sessions_by_port.items()):
            client = self.get_api_client(api_port)
            closed = client.close_project(session_id, timeout_sec=_SILWORX_CLOSE_PROBE_TIMEOUT_SEC)
            if closed:
                self._clear_service_opened_session(api_port)
            else:
                all_closed = False
        return all_closed

    def release_api_connection(self) -> bool:
        """
        Stop SILworX API sessions when all instances are closed (G-19).

        Clears cached API clients. Never calls project/close on the engineer's
        GUI project. Legacy owned open/local sessions (if any) are closed.
        """
        had_session = bool(self._owned_sessions_by_port) or bool(self._api_clients)
        if not had_session:
            return False

        from prooftest.annex_api_connexion import (
            _SILWORX_CLOSE_PROBE_TIMEOUT_SEC,
            build_client_for_port,
        )

        for api_port, session_id in list(self._owned_sessions_by_port.items()):
            client = self._api_clients.get(api_port)
            if client is None:
                client = build_client_for_port(self.config, api_port)
            try:
                client.close_project(session_id, timeout_sec=_SILWORX_CLOSE_PROBE_TIMEOUT_SEC)
            except Exception as exc:
                log.debug("API close_project on port %s: %s", api_port, exc)
        self._clear_service_opened_session()

        for client in self._api_clients.values():
            client.clear_session_id()
        self._api_clients.clear()
        self._active_api_port = None
        self._api_opened_by_service = False
        self._attached_session_ids_by_api.clear()
        self._attached_project_names_by_api.clear()
        self._last_attached_api_port = None
        self._available_instances = []
        self._silworx_api_suspended = True
        log.info("SILworX API connection released (all instances down)")
        return had_session

    def detach_tool_clients(self) -> None:
        """Drop this tool's API client and plugin monitor. Never project/close GUI, never kill c3.exe."""
        if self._plugin_monitor is not None:
            try:
                self._plugin_monitor.stop()
            except Exception as exc:
                log.warning("Plugin monitor stop failed during SILworX disconnect: %s", exc)
            self._plugin_monitor = None
        for client in list(self._api_clients.values()):
            try:
                client.clear_session_id()
            except Exception:
                pass
        self._api_clients.clear()
        self._attached_session_ids_by_api.clear()
        self._attached_project_names_by_api.clear()
        self._active_api_port = None
        self._silworx_api_suspended = True
        self._operator_detached = True
        log.info("SILworX tool session detached (SILworX software left running)")

    def resume_tool_clients(self) -> None:
        """Re-enable API/plugin attach. Does not open a SILworX project."""
        self._operator_detached = False
        self.prepare_for_engine_start()
        self.start_monitor()

    def is_tool_attached(self) -> bool:
        if self.is_api_suspended() or self.is_operator_detached():
            return False
        return bool(self._attached_session_ids_by_api) or bool(self._attached_project_names_by_api)

    def _drop_stale_attachments_vs_plugin(self) -> None:
        """Drop API attaches whose plugin session token changed (other SILworX window)."""
        if self._plugin_monitor is None:
            return
        from prooftest.annex_api_connexion import plugin_port_for_api

        for api_port, sid in list(self._attached_session_ids_by_api.items()):
            plugin_port = plugin_port_for_api(api_port, self.config)
            live = ""
            try:
                live = (self._plugin_monitor.get_session_id(plugin_port) or "").strip()
            except Exception:
                live = ""
            if live and sid and live != sid:
                log.info(
                    "Dropping stale SILworX attach on API %s (plugin session changed)",
                    api_port,
                )
                self._attached_session_ids_by_api.pop(api_port, None)
                self._attached_project_names_by_api.pop(api_port, None)
                client = self._api_clients.get(api_port)
                if client is not None:
                    try:
                        client.clear_session_id()
                    except Exception:
                        pass

    def _marker(self, key: str) -> Path:
        return self.markers_dir / f"{key}.marker"

    def refresh_open_sessions(self) -> List[SilworxOpenProject]:
        """All SILworX sessions with an open project (lock.ini), any instance."""
        self.open_sessions = discover_open_projects(self.config.silworx_programdata)
        preferred_version = ""
        for inst in self._available_instances or []:
            preferred_version = str(getattr(inst, "silworx_version", "") or "")
            if preferred_version:
                break
        self.active_session = pick_configured_session(
            self.open_sessions,
            self.config.silworx_projects,
            preferred_version_substr=preferred_version,
        )
        return self.open_sessions

    def refresh_active_session(self) -> Optional[SilworxOpenProject]:
        self.refresh_open_sessions()
        return self.active_session

    def prepare_for_engine_start(self) -> None:
        """Clear G-19 suspend flags so a UI Start can use SILworX API again."""
        self._silworx_api_suspended = False
        self._operator_detached = False
        self._silworx_down_streak = 0
        log.info("SILworX API suspend cleared for engine start")

    def start_monitor(self) -> None:
        """Start persistent plugin WebSocket listeners on all configured port pairs (G-22)."""
        if not self.config.plugin_monitor_enabled or self._plugin_monitor is not None:
            return
        from prooftest.annex_plugin_monitor import PluginPortMonitor

        self._plugin_monitor = PluginPortMonitor(self.config)
        self._plugin_monitor.start()

    def plugin_monitor_summary(self) -> str:
        if self._plugin_monitor is None:
            return ""
        return self._plugin_monitor.port_states_summary()

    def plugin_session_states(self) -> list:
        """Per-port plugin WebSocket state for Status UI (connected / disconnected)."""
        monitor = self._plugin_monitor
        if monitor is None:
            return []
        with monitor._lock:
            rows = []
            for state in sorted(monitor._ports.values(), key=lambda s: s.plugin_port):
                rows.append(
                    {
                        "api_port": int(state.api_port),
                        "plugin_port": int(state.plugin_port),
                        "connected": bool(state.connected),
                        "session_id": str(state.session_id or ""),
                    }
                )
            return rows

    def api_connected_project_name(self, device_list_source: str = "") -> str:
        """Project name when the device list is served via SILworX API."""
        source = str(device_list_source).lower().strip()
        if source in {"opc", "opc_fallback"}:
            return ""
        self.refresh_open_sessions()

        def _project_for_sid(session_id: str) -> str:
            for session in self.open_sessions:
                if session.session_id == session_id:
                    return session.project_name
            return ""

        candidate_ports: List[int] = []
        if self._last_attached_api_port is not None:
            candidate_ports.append(self._last_attached_api_port)
        for port in sorted(self._attached_session_ids_by_api.keys()):
            if port not in candidate_ports:
                candidate_ports.append(port)

        for port in candidate_ports:
            project_name = (self._attached_project_names_by_api.get(port) or "").strip()
            if project_name:
                return project_name
            session_id = self._attached_session_ids_by_api.get(port, "")
            if not session_id:
                continue
            project_from_sid = _project_for_sid(session_id)
            if project_from_sid:
                return project_from_sid
        if len(self.open_sessions) == 1:
            return self.open_sessions[0].project_name
        return ""

    def registered_plugin_session_name(self) -> str:
        """Configured plugin name when at least one plugin WebSocket is registered."""
        monitor = self._plugin_monitor
        if monitor is None:
            return ""
        with monitor._lock:
            if any(state.connected for state in monitor._ports.values()):
                return self.config.silworx_plugin_name
        return ""

    def check(self) -> List[str]:
        fired: List[str] = []
        previous_open = {
            (s.silworx_version, s.session_id, str(s.src_path))
            for s in self.open_sessions
        }
        self.refresh_open_sessions()
        current_open = {
            (s.silworx_version, s.session_id, str(s.src_path))
            for s in self.open_sessions
        }
        newly_open = current_open - previous_open
        if newly_open:
            log.info(
                "SILworX project open/change detected — requesting fresh plugin session"
            )
            # Force remapping of API ports → projects after a new window/project opens.
            self._attached_session_ids_by_api.clear()
            self._attached_project_names_by_api.clear()
            self.request_fresh_plugin_session()
            if "silworx_session" in self._enabled:
                fired.append("silworx_session")

        if self._plugin_monitor is not None:
            for trigger in self._plugin_monitor.consume_triggers():
                if trigger == "silworx_session":
                    self._drop_stale_attachments_vs_plugin()
                if trigger in self._enabled and trigger not in fired:
                    fired.append(trigger)

        for session in self.open_sessions:
            key = f"session_{session.session_id}_{session.project_name}"
            if watch_session_changed(session, self._marker(key)):
                if "silworx_session" in self._enabled and "silworx_session" not in fired:
                    fired.append("silworx_session")
                if "code_generation" in self._enabled and "code_generation" not in fired:
                    fired.append("code_generation")

        if not self.open_sessions:
            for project in self.config.silworx_projects:
                if "download" in self._enabled and watch_project_changed(
                    project, self._marker(f"e3_{project.name}")
                ):
                    fired.append("download")
                if "code_generation" in self._enabled and watch_project_changed(
                    project, self._marker(f"e3_codegen_{project.name}")
                ):
                    fired.append("code_generation")

        if "results_structures" in self._enabled and self.config.results_structures:
            if watch_results_structures_changed(
                self.config.results_structures,
                self._marker("results_structures"),
            ):
                fired.append("results_structures")

        return fired

    def commit(self) -> None:
        self.markers_dir.mkdir(parents=True, exist_ok=True)
        self.refresh_open_sessions()
        for session in self.open_sessions:
            key = f"session_{session.session_id}_{session.project_name}"
            commit_marker(self._marker(key), session_working_mtime(session))
        if not self.open_sessions:
            for project in self.config.silworx_projects:
                if project.exists():
                    if "download" in self._enabled:
                        commit_marker(self._marker(f"e3_{project.name}"), _path_mtime(project))
                    if "code_generation" in self._enabled:
                        commit_marker(
                            self._marker(f"e3_codegen_{project.name}"),
                            _path_mtime(project),
                        )
        if self.config.results_structures.is_dir():
            commit_marker(
                self._marker("results_structures"),
                folder_aggregate_mtime(self.config.results_structures),
            )

    def shutdown(self) -> None:
        """Release SILworX API session state and stop plugin monitors."""
        if self._plugin_monitor is not None:
            self._plugin_monitor.stop()
            self._plugin_monitor = None
        self.release_api_connection()


# Deprecated alias — leftover UNIFIED naming (not a Case 1 product mode).
Case1SyncTriggers = SilworxSyncTriggers


def run_background_sync_iteration(service, now: float) -> None:
    """Run one Step 7 background synchronization iteration (unified path)."""
    if getattr(service, "_stop", None) is not None and service._stop.is_set():
        return
    if getattr(service, "_stopped", False) and not getattr(service, "_starting", False):
        return

    from prooftest.results_csv import load_all_structures
    from prooftest.step01_setup import is_silworx_installed

    # Operator Release SILworX / G-11: stay OPC-only until Re-integrate.
    integration_released = bool(
        getattr(service, "is_silworx_integration_released", lambda: False)()
    )

    # G-11: SILworX gone — release blockers once; keep running; OPC device list below.
    if not is_silworx_installed(service.config.silworx_programdata):
        if not getattr(service, "_silworx_uninstall_released", False):
            service.release_silworx_engines_keep_running()
            service._silworx_uninstall_released = True
            integration_released = True

    if now - service._last_case1_sync_check >= service.config.case1_sync_poll_sec:
        service._last_case1_sync_check = now
        from prooftest.annex_api_connexion import is_silworx_running
        silworx_running = is_silworx_running(service.config)

        silworx_open = is_silworx_open(service.config.silworx_programdata)

        if integration_released:
            # Do not auto-resume API/plugin while released for uninstall.
            service._case1_sync._silworx_api_suspended = True
            service.db.set_service_state("silworx_api_connected", "0")
            service.db.set_service_state("device_list_source", "opc_fallback")
            service.db.set_service_state("silworx_plugin_monitor_state", "")
        elif getattr(service._case1_sync, "is_operator_detached", lambda: False)():
            # Disconnect SILworX: stay detached until Connect — do not auto-resume.
            service._case1_sync._silworx_api_suspended = True
            service.db.set_service_state("silworx_api_connected", "0")
            service.db.set_service_state("silworx_plugin_monitor_state", "")
            if service._case1_sync._plugin_monitor is not None:
                try:
                    service._case1_sync._plugin_monitor.stop()
                except Exception:
                    pass
                service._case1_sync._plugin_monitor = None
        # G-19: release API session when SILworX software is down.
        elif silworx_running:
            service._silworx_uninstall_released = False
            service._case1_sync._silworx_down_streak = 0
            if service._case1_sync._silworx_api_suspended:
                log.info("SILworX API available again — resuming API device discovery")
            service._case1_sync._silworx_api_suspended = False
            instances = service._case1_sync.discover_api_instances()
            from prooftest.annex_api_connexion import iter_port_pairs

            plugin_ports = ";".join(
                f"{p.api_port}/{p.plugin_port}" for p in iter_port_pairs(service.config)
            )
            service.db.set_service_state(
                "silworx_api_ports_active",
                service._case1_sync.api_instance_labels(),
            )
            service.db.set_service_state("silworx_plugin_ports_configured", plugin_ports)
            monitor_summary = service._case1_sync.plugin_monitor_summary()
            if monitor_summary:
                service.db.set_service_state("silworx_plugin_monitor_state", monitor_summary)
            else:
                service.db.set_service_state("silworx_plugin_monitor_state", "")
            service.db.set_service_state("silworx_api_connected", "1" if instances else "0")
        else:
            service._case1_sync._silworx_down_streak += 1
            if service._case1_sync._silworx_down_streak == 1:
                service._case1_sync.try_close_owned_session()
            if service._case1_sync._silworx_down_streak >= _SILWORX_DOWN_PROBE_THRESHOLD:
                if service._case1_sync.release_api_connection():
                    service.db.set_service_state("silworx_api_connected", "0")
                service._case1_sync._silworx_api_suspended = True

        # Keep updating the device list via Application RefreshCatalog (not step03 brain).
        # Also retry when API/plugin is up but this tool is not yet attached (initial
        # refresh often races the plugin WebSocket and would otherwise stay on OPC forever).
        # When several SILworX projects are open, refresh again until each has been
        # scanned on at least one API port (or device_list_poll elapses).
        api_unavailable = (
            integration_released
            or service._case1_sync.is_api_suspended()
            or getattr(service._case1_sync, "is_operator_detached", lambda: False)()
            or not silworx_running
        )
        need_api_attach = (
            (not integration_released)
            and silworx_running
            and not api_unavailable
            and silworx_open
            and not service._case1_sync.is_tool_attached()
        )
        uncovered = []
        try:
            if (not integration_released) and silworx_running and silworx_open and not api_unavailable:
                uncovered = service._case1_sync.uncovered_open_projects()
        except Exception:
            uncovered = []
        need_multi_project_scan = bool(uncovered)
        if (
            api_unavailable or need_api_attach or need_multi_project_scan
        ) and not service._stop.is_set():
            if now - service._last_device_sync >= service.config.device_list_poll_sec:
                try:
                    if need_multi_project_scan:
                        log.info(
                            "Open SILworX projects not yet API-scanned: %s — refreshing",
                            ", ".join(uncovered),
                        )
                    if getattr(service, "app", None) is not None:
                        service.app.refresh_catalog()
                    else:
                        service.refresh(manual=False)
                    service.db.set_service_state(
                        "last_opc_device_scan",
                        time.strftime("%Y-%m-%d %H:%M:%S"),
                    )
                except Exception as exc:
                    log.warning("Device-list refresh failed: %s", exc)
                service._last_device_sync = now

        # G-20: kill leftover c3.exe only after confirmed SILworX close (lock.ini / GUI gone).
        # Never uses API probes or c3.exe presence alone — opening SILworX is always safe.
        from prooftest.annex_silworx_cleanup import (
            close_grace_sec,
            is_silworx_session_active,
            kill_leftover_c3_after_close,
            list_c3_processes,
            should_kill_c3_after_close,
        )

        session_active = is_silworx_session_active(silworx_open=silworx_open)
        sync = service._case1_sync

        if session_active:
            sync._silworx_session_was_active = True
            sync._silworx_close_detected_at = None
            sync._silworx_c3_cleanup_done = False
        elif sync._silworx_session_was_active:
            if sync._silworx_close_detected_at is None:
                sync._silworx_close_detected_at = now
                log.info(
                    "SILworX close detected — waiting %.0fs before c3.exe cleanup",
                    close_grace_sec(),
                )
            elif should_kill_c3_after_close(
                session_was_active=sync._silworx_session_was_active,
                session_active=session_active,
                close_detected_at=sync._silworx_close_detected_at,
                now=now,
                grace_sec=close_grace_sec(),
            ):
                if not sync._silworx_c3_cleanup_done and list_c3_processes():
                    cleanup = kill_leftover_c3_after_close(service.config)
                    service.db.set_service_state(
                        "silworx_cleanup_killed",
                        str(len(cleanup.killed)),
                    )
                if not list_c3_processes():
                    sync._silworx_c3_cleanup_done = True
                    sync._silworx_session_was_active = False
                    sync._silworx_close_detected_at = None
        triggers = service._case1_sync.check()
        service._publish_silworx_state()
        if triggers and not service._stop.is_set():
            log.info("Auto-sync triggered: %s", ", ".join(triggers))
            if (
                "results_structures" in triggers
                or "silworx_session" in triggers
                or "code_generation" in triggers
                or "download" in triggers
            ):
                service.structures = load_all_structures(service.config.results_structures)
                if service.monitor is not None:
                    service.monitor.structures = service.structures
                    if "results_structures" in triggers:
                        service.monitor.reload_type_catalog()
                if "results_structures" in triggers:
                    from prooftest.step01_setup import sync_results_type_folders_from_catalogue
                    from prooftest.annex_pdf_generation import ensure_report_templates_for_structures

                    sync_results_type_folders_from_catalogue(
                        service.config,
                        service.alarms,
                        list(service.structures.keys()),
                    )
                    try:
                        ensure_report_templates_for_structures(
                            service.config.report_html_templates,
                            service.structures,
                        )
                    except Exception as exc:
                        log.warning("Report template ensure failed: %s", exc)
                    log.info(
                        "Results Structures catalogue reloaded: %s type(s)",
                        len(service.structures),
                    )
            if "silworx_session" in triggers or "code_generation" in triggers:
                try:
                    service.opc.invalidate_tag_cache()
                except Exception:
                    service.opc.invalidate_cache()
            # Do not block the sync loop on a long OPC browse — UI stays responsive
            # and catalog_refresh is visible immediately.
            def _refresh() -> None:
                try:
                    if getattr(service, "app", None) is not None:
                        service.app.refresh_catalog()
                    else:
                        service.refresh(manual=False)
                    try:
                        service.db.set_service_state(
                            "last_opc_device_scan",
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                        )
                    except Exception:
                        pass
                except Exception as exc:
                    log.warning("Triggered catalog refresh failed: %s", exc)

            import threading

            try:
                service.db.set_service_state("catalog_refresh", "1")
                sync_fn = getattr(service, "_sync_health_caches_from_db", None)
                if callable(sync_fn):
                    sync_fn()
            except Exception:
                pass
            threading.Thread(
                target=_refresh, daemon=True, name="triggered-catalog-refresh"
            ).start()
