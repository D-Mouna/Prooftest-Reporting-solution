"""
Annex — SILworX API connexion (HTTPS client + plugin WebSocket session bridge).
"""

from __future__ import annotations

import asyncio
import http.client
import json
import logging
import socket
import ssl
import urllib.parse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional

from prooftest.config import AppConfig

log = logging.getLogger(__name__)

TRIGGER_SESSION_ID_CHANGED = "TRIGGER_SESSION_ID_CHANGED"

# SILworX matches this header name exactly. urllib.request.Request.add_header()
# capitalizes names to ``Hima_sapi_user_session_id``, which SILworX rejects.
SESSION_HEADER_NAME = "HIMA_SAPI_user_session_id"

ConnectionFactory = Callable[..., http.client.HTTPSConnection]


class SilworxApiError(Exception):
    """Base class for SILworX API failures."""


class SilworxApiConnectionError(SilworxApiError):
    """Transport or TLS failure reaching the API."""


class SilworxApiHttpError(SilworxApiError):
    """Non-success HTTP status from the API."""

    def __init__(self, status: int, path: str, body: str) -> None:
        self.status = status
        self.path = path
        self.body = body
        super().__init__(f"HTTP {status} for {path}: {body[:500]}")


class SilworxProjectConflictError(SilworxApiHttpError):
    """HTTP 417 — project already open in SILworX GUI (OI-3)."""


class SilworxApiSessionError(SilworxApiError):
    """Operation requires an open API project session."""


class SilworxApiResponseError(SilworxApiError):
    """Unexpected or incomplete JSON payload."""


def is_unusable_gui_session_error(exc: BaseException) -> bool:
    """True when SILworX rejected the plugin ``user_session_id`` (stale or no project)."""
    text = str(exc).lower()
    return any(
        needle in text
        for needle in (
            "session id is not valid",
            "the session id is not valid",
            "no project opened",
            "session is not open",
            "invalid session",
        )
    )


@dataclass(frozen=True)
class GlobalVariablesNode:
    """One Global Variables node in the SILworX structure tree."""

    internal_address: str
    configuration: str
    resource: str
    tree_path: str


@dataclass(frozen=True)
class GlobalVariableRecord:
    """Top-level global variable entry from the API."""

    name: str
    data_type: str


def resolve_api_server_cert(programdata_root: Path, explicit: Optional[Path] = None) -> Path:
    """Locate `settings/api_cert.pem` for server TLS verification."""
    if explicit and explicit.is_file():
        return explicit
    candidates = sorted(programdata_root.glob("SILworX_v*/settings/api_cert.pem"))
    if not candidates:
        raise SilworxApiError(
            f"No SILworX API server certificate under {programdata_root}/SILworX_v*/settings/"
        )
    return candidates[-1]


_SILWORX_API_PORT_START = 51710
_SILWORX_API_PORT_COUNT = 10
_SILWORX_PLUGIN_PORT_START = 8400
_SILWORX_RUNNING_PROBE_TIMEOUT_SEC = 3.0
_SILWORX_PORT_PROBE_TIMEOUT_SEC = 1.5
_SILWORX_CLOSE_PROBE_TIMEOUT_SEC = 5.0


@dataclass(frozen=True)
class SilworxPortPair:
    api_port: int
    plugin_port: int

    @property
    def label(self) -> str:
        return f"{self.api_port}/{self.plugin_port}"


@dataclass(frozen=True)
class SilworxApiInstance:
    """One reachable SILworX API endpoint on this station."""

    api_port: int
    plugin_port: int
    silworx_version: str = ""
    product_name: str = ""

    @property
    def label(self) -> str:
        return f"{self.api_port}/{self.plugin_port}"


def iter_port_pairs(config: AppConfig) -> List[SilworxPortPair]:
    """Yield all configured API/plugin port pairs (default: 51710-51719 / 8400-8409)."""
    start = config.silworx_api_port_start
    count = config.silworx_api_port_count
    plugin_start = config.silworx_plugin_port_start
    return [
        SilworxPortPair(api_port=start + index, plugin_port=plugin_start + index)
        for index in range(count)
    ]


def plugin_port_for_api(api_port: int, config: AppConfig) -> int:
    """Map an API port to its plugin WebSocket port using the configured offset."""
    return config.silworx_plugin_port_start + (api_port - config.silworx_api_port_start)


def build_client_for_port(config: AppConfig, api_port: int) -> "SilworxApiClient":
    """Construct a client for a specific SILworX API port."""
    cert = resolve_api_server_cert(config.silworx_programdata, config.silworx_api_cert)
    return SilworxApiClient(
        host=config.silworx_api_host,
        port=api_port,
        server_ca_cert=cert,
        client_cert_dir=config.silworx_api_client_cert_dir,
        timeout_sec=config.silworx_api_timeout_sec,
        open_project_timeout_sec=config.silworx_api_open_timeout_sec,
    )


def build_client_from_config(config: AppConfig) -> "SilworxApiClient":
    """Construct a client from `solution.ini` preferred API port."""
    return build_client_for_port(config, config.silworx_api_port)


def probe_api_port(config: AppConfig, api_port: int) -> Optional[SilworxApiInstance]:
    """Return instance metadata when ``POST /silworx/info`` succeeds on ``api_port``."""
    try:
        cert = resolve_api_server_cert(config.silworx_programdata, config.silworx_api_cert)
    except SilworxApiError:
        return None
    client = SilworxApiClient(
        host=config.silworx_api_host,
        port=api_port,
        server_ca_cert=cert,
        timeout_sec=_SILWORX_PORT_PROBE_TIMEOUT_SEC,
    )
    try:
        info = client.get_silworx_info()
    except SilworxApiError:
        return None
    version = ""
    product = ""
    if isinstance(info, dict):
        version = str(info.get("silworx_version") or info.get("version") or "")
        product = str(info.get("product_name") or info.get("product") or "")
    return SilworxApiInstance(
        api_port=api_port,
        plugin_port=plugin_port_for_api(api_port, config),
        silworx_version=version,
        product_name=product,
    )


def discover_available_instances(config: AppConfig) -> List[SilworxApiInstance]:
    """Scan all configured port pairs and return those with a responding SILworX API."""
    found: List[SilworxApiInstance] = []
    for pair in iter_port_pairs(config):
        instance = probe_api_port(config, pair.api_port)
        if instance is not None:
            found.append(instance)
    return found


def is_silworx_running(config: AppConfig) -> bool:
    """
    True when any configured SILworX API port responds (G-19).

    Scans ``api_port_start`` .. ``api_port_start + api_port_count - 1``.
    """
    return bool(discover_available_instances(config))


def is_silworx_running_on_port(config: AppConfig, api_port: int) -> bool:
    """True when a single API port responds."""
    return probe_api_port(config, api_port) is not None


class SilworxApiClient:
    """
    Session-aware HTTPS client for SILworX `/api/v1`.

    Endpoints used (SPEC Step 3):
      POST /silworx/info
      POST /project/structuretree/info
      POST /node/globalvariables/content/read
      POST /project/close  (legacy / diagnostic only — service never opens a project)
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 51710,
        *,
        server_ca_cert: Path,
        client_cert_dir: Optional[Path] = None,
        timeout_sec: float = 120.0,
        open_project_timeout_sec: float = 600.0,
        connection_factory: Optional[ConnectionFactory] = None,
    ) -> None:
        self.host = host
        self.port = int(port)
        self.server_ca_cert = Path(server_ca_cert)
        self.client_cert_dir = Path(client_cert_dir) if client_cert_dir else None
        self.timeout_sec = float(timeout_sec)
        self.open_project_timeout_sec = float(open_project_timeout_sec)
        self.user_session_id: Optional[str] = None
        self._connection_factory = connection_factory or http.client.HTTPSConnection
        self._ssl_context = (
            None
            if connection_factory is not None
            else ssl.create_default_context(cafile=str(self.server_ca_cert))
        )

    @property
    def base_url(self) -> str:
        return f"https://{self.host}:{self.port}/api/v1"

    def _request(
        self,
        path: str,
        *,
        session_id: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        json_body: Any = None,
        require_session: bool = False,
        timeout_sec: Optional[float] = None,
    ) -> bytes:
        if require_session and not (session_id or self.user_session_id):
            raise SilworxApiSessionError("SILworX API session is not open")

        full_path = "/api/v1" + path
        if query:
            full_path += "?" + urllib.parse.urlencode(query)

        # Use http.client (same as HIMA sapi.py). urllib.request.Request capitalizes
        # header names, so SILworX never sees HIMA_SAPI_user_session_id.
        headers: Dict[str, str] = {}
        sid = session_id or self.user_session_id
        if sid:
            headers[SESSION_HEADER_NAME] = sid
        data: Optional[bytes] = None
        if json_body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(json_body).encode("utf-8")

        timeout = self.timeout_sec if timeout_sec is None else timeout_sec
        conn_kwargs: Dict[str, Any] = {"timeout": timeout}
        if self._ssl_context is not None:
            conn_kwargs["context"] = self._ssl_context
        conn = self._connection_factory(self.host, self.port, **conn_kwargs)
        try:
            conn.request("POST", full_path, body=data, headers=headers)
            response = conn.getresponse()
            status = response.status
            body_bytes = response.read()
        except (TimeoutError, socket.timeout, http.client.HTTPException) as exc:
            raise SilworxApiConnectionError(str(exc)) from exc
        except OSError as exc:
            raise SilworxApiConnectionError(str(exc)) from exc
        finally:
            conn.close()

        if status < 200 or status >= 300:
            body = body_bytes.decode("utf-8", errors="replace")
            if status == 417 or (
                status == 400
                and ("project is still open" in body.lower() or "a project is still open" in body.lower())
            ):
                raise SilworxProjectConflictError(status, path, body)
            raise SilworxApiHttpError(status, path, body)
        return body_bytes

    def _request_json(self, path: str, timeout_sec: Optional[float] = None, **kwargs: Any) -> Dict[str, Any]:
        raw = self._request(path, timeout_sec=timeout_sec, **kwargs)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise SilworxApiResponseError(f"Invalid JSON from {path}") from exc

    def get_silworx_info(self) -> Dict[str, Any]:
        """POST /silworx/info — version and license (no session, no JSON body)."""
        payload = self._request_json("/silworx/info")
        return payload.get("results", payload)

    def open_project_local(self, project_file: Path) -> str:
        """
        POST /project/open/local — diagnostic helper only.

        The Report Solution service **never** calls this. Device list uses API
        only when the user already has a project open; otherwise OPC scan.
        """
        project_file = Path(project_file)
        if not project_file.is_file():
            raise SilworxApiError(f"Project file not found: {project_file}")

        query = {
            "projectfile": str(project_file),
            "suppress_ldap_login": "true",
        }
        payload = self._request_json(
            "/project/open/local",
            query=query,
            timeout_sec=self.open_project_timeout_sec,
        )
        sid = (payload.get("results") or {}).get("user_session_id")
        if not sid:
            raise SilworxApiResponseError(
                f"No user_session_id in open/local response: {json.dumps(payload)[:500]}"
            )
        self.user_session_id = sid
        log.info("SILworX API session opened for %s", project_file.name)
        return sid

    def set_session_id(self, session_id: Optional[str]) -> None:
        """Attach to an existing open-project API session (GUI / plugin workflow)."""
        self.user_session_id = (session_id or "").strip() or None

    def clear_session_id(self) -> None:
        """Drop cached session id without closing the project in SILworX."""
        self.user_session_id = None

    def close_project(
        self,
        session_id: Optional[str] = None,
        *,
        timeout_sec: Optional[float] = None,
    ) -> bool:
        """
        POST /project/close — release an API session opened by this client.

        Returns True when close succeeded or no session was active.
        """
        sid = (session_id or self.user_session_id or "").strip() or None
        if not sid:
            self.user_session_id = None
            return True
        self.user_session_id = sid
        try:
            self._request_json(
                "/project/close",
                require_session=True,
                timeout_sec=timeout_sec if timeout_sec is not None else self.timeout_sec,
            )
            return True
        except SilworxApiError as exc:
            log.warning("SILworX API close_project failed: %s", exc)
            return False
        finally:
            self.user_session_id = None

    def get_structuretree(self) -> Dict[str, Any]:
        """POST /project/structuretree/info — full configuration/resource tree."""
        payload = self._request_json("/project/structuretree/info", require_session=True)
        return payload.get("results", payload)

    def read_global_variables(self, internal_address: str) -> List[Dict[str, Any]]:
        """POST /node/globalvariables/content/read for one Global Variables node."""
        query = {"internal_address": internal_address}
        payload = self._request_json(
            "/node/globalvariables/content/read",
            query=query,
            require_session=True,
        )
        results = payload.get("results") or {}
        variables = results.get("variables")
        if variables is None:
            nested = results.get("content_globalvariables") or {}
            variables = nested.get("variables")
        if variables is None:
            raise SilworxApiResponseError(
                f"Unexpected globalvariables response: {json.dumps(payload)[:800]}"
            )
        return variables

    @staticmethod
    def _is_global_variables_node(node: Dict[str, Any]) -> bool:
        display = (node.get("display_name") or node.get("name") or "").strip()
        type_text = ((node.get("type_info") or {}).get("display_name") or "").lower()
        type_symbol = ((node.get("type_info") or {}).get("symbol") or "").lower()
        if display == "Global Variables":
            return True
        if "global variable" in type_text:
            return True
        if "globalvariable" in type_symbol.replace("_", ""):
            return True
        return False

    @staticmethod
    def _node_label(node: Dict[str, Any]) -> str:
        return (node.get("display_name") or node.get("name") or "").strip()

    @staticmethod
    def _node_symbol(node: Dict[str, Any]) -> str:
        return ((node.get("type_info") or {}).get("symbol") or "").lower()

    def find_all_globalvariable_nodes(self, tree: Optional[Dict[str, Any]] = None) -> List[GlobalVariablesNode]:
        """
        Walk structuretree and return every Global Variables node.

        Annotates each node with Configuration and Resource context (SPEC §3.2).
        """
        if tree is None:
            tree = self.get_structuretree()

        roots = tree.get("structure_tree") or tree.get("structuretree") or []
        if isinstance(roots, dict):
            roots = [roots]

        found: List[GlobalVariablesNode] = []

        def walk(
            node: Dict[str, Any],
            configuration: str,
            resource: str,
            path_parts: List[str],
        ) -> None:
            label = self._node_label(node)
            symbol = self._node_symbol(node)
            path_parts = path_parts + ([label] if label else [])

            cfg = configuration
            res = resource
            if symbol == "configuration" or label.lower() == "configuration":
                cfg = label or cfg
                res = ""
            elif "resource" in symbol and label:
                res = label

            if self._is_global_variables_node(node):
                addr = (node.get("internal_address") or "").strip()
                if addr:
                    found.append(
                        GlobalVariablesNode(
                            internal_address=addr,
                            configuration=cfg,
                            resource=res,
                            tree_path=" / ".join(path_parts),
                        )
                    )

            for child in node.get("children") or []:
                if isinstance(child, dict):
                    walk(child, cfg, res, path_parts)

        for root in roots:
            if isinstance(root, dict):
                walk(root, "", "", [])

        log.info("SILworX API: found %d Global Variables node(s)", len(found))
        return found

    def list_top_level_globals(self, internal_address: str) -> List[GlobalVariableRecord]:
        """Read globals at one node; return only top-level variables (no nested items)."""
        records: List[GlobalVariableRecord] = []
        for var in self.read_global_variables(internal_address):
            name = (var.get("name") or "").strip()
            dtype = (var.get("data_type") or "").strip()
            if name and dtype:
                records.append(GlobalVariableRecord(name=name, data_type=dtype))
        return records

    @contextmanager
    def project_session(self, project_file: Path) -> Iterator[str]:
        """Open project via API and always close the session in `finally`."""
        sid = self.open_project_local(project_file)
        try:
            yield sid
        finally:
            self.close_project()


def pick_api_project_path(config: AppConfig) -> Optional[Path]:
    """Best project file from solution.ini (diagnostic / Mode-A-removed leftover)."""
    for project in config.silworx_projects:
        versioned = project.parent / f"{project.stem} - V16.0.0.E3"
        if versioned.is_file():
            return versioned
        if project.is_file():
            return project
    return None


@dataclass
class _RegisterPlugin:
    plugin_name: str
    plugin_version: str
    plugin_author: str = "HIMA Prooftest Solution"
    plugin_vendor: str = "Report Solution"
    plugin_license: str = ""
    secret: str = ""
    msg_type: str = "register"
    customized_contextmenu_trigger: list = None
    customized_extramenu_trigger: list = None
    predefined_trigger: list = None

    def __post_init__(self) -> None:
        if self.customized_contextmenu_trigger is None:
            self.customized_contextmenu_trigger = []
        if self.customized_extramenu_trigger is None:
            self.customized_extramenu_trigger = []
        if self.predefined_trigger is None:
            self.predefined_trigger = [
                {"trigger_name": TRIGGER_SESSION_ID_CHANGED, "timeout": 10},
            ]


def _plugin_ssl_context(tls_certificate: Optional[Path] = None) -> ssl.SSLContext:
    if tls_certificate and tls_certificate.is_file():
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cafile=str(tls_certificate))
        return ctx
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


async def _acquire_session_id_async(
    *,
    host: str = "127.0.0.1",
    plugin_port: int = 8400,
    plugin_name: str = "prooftest_session_plugin",
    timeout_sec: float = 15.0,
    tls_certificate: Optional[Path] = None,
    api_port: Optional[int] = None,
) -> Optional[str]:
    try:
        import websockets
    except ImportError as exc:
        raise SilworxApiError(
            "websockets package is required to read globals from an open SILworX project"
        ) from exc

    register = _RegisterPlugin(
        plugin_name=plugin_name,
        plugin_version="1.0.0",
    )
    url = f"wss://{host}:{plugin_port}"
    if api_port is not None:
        tag = f"api={api_port} plugin={plugin_port}"
    else:
        tag = f"plugin={plugin_port}"
    deadline = asyncio.get_event_loop().time() + timeout_sec
    connected = False

    try:
        async with websockets.connect(url, ssl=_plugin_ssl_context(tls_certificate)) as ws:
            await ws.send(json.dumps(asdict(register)))
            connected = True
            log.info("plugin one-shot connected %s name=%s", tag, plugin_name)
            while asyncio.get_event_loop().time() < deadline:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    break
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
                except asyncio.TimeoutError:
                    break
                message = json.loads(raw)
                if message.get("msg_type") != "trigger":
                    continue
                if message.get("trigger_name") != TRIGGER_SESSION_ID_CHANGED:
                    continue
                session_id = (message.get("session_id") or "").strip()
                trigger_id = message.get("trigger_id")
                if trigger_id:
                    await ws.send(
                        json.dumps({"msg_type": "resume", "trigger_id": trigger_id})
                    )
                if not session_id:
                    log.debug("SILworX session bridge: project closed (empty session id)")
                    continue
                log.info("plugin one-shot session acquired %s", tag)
                return session_id
    except OSError as exc:
        log.warning("plugin one-shot unavailable %s: %s", tag, exc)
        return None
    except Exception as exc:
        log.warning("plugin one-shot failed %s: %s", tag, exc)
        return None
    finally:
        if connected:
            log.info(
                "plugin one-shot disconnected %s (expected — closes after use)",
                tag,
            )
    return None


def acquire_open_project_session_id(
    *,
    host: str = "127.0.0.1",
    plugin_port: int = 8400,
    plugin_name: str = "prooftest_session_plugin",
    timeout_sec: float = 15.0,
    tls_certificate: Optional[Path] = None,
    api_port: Optional[int] = None,
) -> Optional[str]:
    """Return API user_session_id for the currently open SILworX project, if any."""
    try:
        return asyncio.run(
            _acquire_session_id_async(
                host=host,
                plugin_port=plugin_port,
                plugin_name=plugin_name,
                timeout_sec=timeout_sec,
                tls_certificate=tls_certificate,
                api_port=api_port,
            )
        )
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                _acquire_session_id_async(
                    host=host,
                    plugin_port=plugin_port,
                    plugin_name=plugin_name,
                    timeout_sec=timeout_sec,
                    tls_certificate=tls_certificate,
                    api_port=api_port,
                )
            )
        finally:
            loop.close()


def resolve_gui_session_id(
    config: AppConfig,
    api_port: int,
    *,
    plugin_monitor: Optional[object] = None,
    timeout_sec: float = 15.0,
) -> Optional[str]:
    """
    Return a validated GUI session token for ``api_port``.

    Prefers the cached token from the background plugin monitor (G-22). When the
    monitor is enabled and running, waits briefly for the cache instead of opening
    a second one-shot WebSocket registration on the same plugin port.
    """
    plugin_port = plugin_port_for_api(api_port, config)
    tag = f"api={api_port} plugin={plugin_port}"
    if plugin_monitor is not None:
        cached = plugin_monitor.get_session_id(plugin_port)
        if cached:
            log.info("plugin session from monitor cache %s", tag)
            return cached

        monitor_active = (
            config.plugin_monitor_enabled
            and getattr(plugin_monitor, "is_running", lambda: False)()
        )
        if monitor_active:
            wait_for_session = getattr(plugin_monitor, "wait_for_session_id", None)
            if wait_for_session is not None:
                log.info(
                    "plugin monitor active — waiting for session cache %s (one-shot disabled)",
                    tag,
                )
                session_id = wait_for_session(plugin_port, timeout_sec=timeout_sec)
                if session_id:
                    log.info("plugin session from monitor cache %s", tag)
                    return session_id
                log.warning(
                    "plugin monitor has no session yet %s — one-shot skipped",
                    tag,
                )
                return None

    log.info(
        "plugin one-shot register %s name=%s (closes after session acquired)",
        tag,
        config.silworx_plugin_name,
    )
    return acquire_open_project_session_id(
        host=config.silworx_api_host,
        plugin_port=plugin_port,
        plugin_name=config.silworx_plugin_name,
        timeout_sec=timeout_sec,
        tls_certificate=config.silworx_api_cert,
        api_port=api_port,
    )
