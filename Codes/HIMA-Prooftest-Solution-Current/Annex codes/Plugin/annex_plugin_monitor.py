"""
Persistent SILworX plugin WebSocket monitors on all configured port pairs (G-22).

The monitor listens for TRIGGER_SESSION_ID_CHANGED on plugin ports 8400–8409.
It does **not** read device data — that is always done via REST API (step03).

Project modify / code generation / download are detected via session-folder mtime
watchers in step07 (SILworX exposes no plugin triggers for those events).
"""

from __future__ import annotations

import asyncio
import json
import logging
import ssl
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Set

from prooftest.config import AppConfig

log = logging.getLogger(__name__)

TRIGGER_SESSION_ID_CHANGED = "TRIGGER_SESSION_ID_CHANGED"


@dataclass
class PortSessionState:
    api_port: int
    plugin_port: int
    session_id: str = ""
    connected: bool = False
    last_change_at: float = 0.0


@dataclass
class _RegisterPlugin:
    plugin_name: str
    plugin_version: str
    plugin_author: str = "HIMA Prooftest Solution"
    plugin_vendor: str = "Report Solution"
    plugin_license: str = ""
    secret: str = ""
    msg_type: str = "register"
    customized_contextmenu_trigger: list = field(default_factory=list)
    customized_extramenu_trigger: list = field(default_factory=list)
    predefined_trigger: list = field(default_factory=list)

    def __post_init__(self) -> None:
        # timeout>0 asks SILworX to deliver the current open-project session_id on
        # register (and later on change). timeout:0 left the WebSocket "up" with an
        # empty session cache — attach then failed and the UI stayed disconnected.
        self.predefined_trigger = [
            {"trigger_name": TRIGGER_SESSION_ID_CHANGED, "timeout": 10},
        ]


def _plugin_ssl_context(tls_certificate) -> ssl.SSLContext:
    from pathlib import Path

    cert_path = Path(tls_certificate) if tls_certificate else None
    if cert_path and cert_path.is_file():
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cafile=str(cert_path))
        return ctx
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class PluginPortMonitor:
    """Background listener on every configured SILworX plugin port."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._ports: Dict[int, PortSessionState] = {}
        self._pending: Set[str] = set()
        self._unavailable_warned: Set[int] = set()
        self._reregister: Set[int] = set()

    def _ensure_port_state(self, api_port: int, plugin_port: int) -> None:
        with self._lock:
            if plugin_port not in self._ports:
                self._ports[plugin_port] = PortSessionState(
                    api_port=api_port,
                    plugin_port=plugin_port,
                )

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        # Do not probe SILworX ports on the engine-start thread — that scan can
        # take many seconds and overlapped Stop/Start hangs the UI on "starting".
        self._stop.clear()
        self._thread = threading.Thread(target=self._thread_main, name="plugin-monitor", daemon=True)
        self._thread.start()
        log.info(
            "Plugin port monitor starting (instance discovery in background) name=%s",
            self.config.silworx_plugin_name,
        )

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            with self._lock:
                active = [
                    self._port_tag(s.api_port, s.plugin_port)
                    for s in self._ports.values()
                    if s.connected
                ]
            if active:
                log.info(
                    "Plugin port monitor stopping (connected: %s)",
                    ", ".join(active),
                )
            else:
                log.info("Plugin port monitor stopping")
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._thread = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def get_session_id(self, plugin_port: int) -> Optional[str]:
        with self._lock:
            state = self._ports.get(plugin_port)
            if state and state.session_id:
                return state.session_id
        return None

    def wait_for_session_id(
        self,
        plugin_port: int,
        *,
        timeout_sec: float = 15.0,
        poll_sec: float = 0.25,
        not_equal: str = "",
    ) -> Optional[str]:
        """Poll the monitor cache until a session id appears or timeout elapses."""
        stale = (not_equal or "").strip()
        deadline = time.monotonic() + max(0.0, float(timeout_sec))
        while time.monotonic() < deadline:
            session_id = self.get_session_id(plugin_port)
            if session_id and session_id != stale:
                return session_id
            if not self.is_running():
                break
            time.sleep(min(poll_sec, max(0.0, deadline - time.monotonic())))
        session_id = self.get_session_id(plugin_port)
        if session_id and session_id != stale:
            return session_id
        return None

    def request_fresh_session(self, plugin_port: Optional[int] = None) -> None:
        """Drop cached tokens and reconnect the plugin WebSocket to get a new session id."""
        with self._lock:
            targets = [plugin_port] if plugin_port is not None else list(self._ports.keys())
            if plugin_port is not None and plugin_port not in self._ports:
                targets = [plugin_port]
            for port in targets:
                state = self._ports.get(port)
                if state:
                    state.session_id = ""
                self._reregister.add(port)
        if plugin_port is None:
            log.info("plugin monitor fresh-session requested on all cached ports")
        else:
            log.info("plugin monitor fresh-session requested plugin=%s", plugin_port)

    def _should_reregister(self, plugin_port: int) -> bool:
        with self._lock:
            if plugin_port in self._reregister:
                self._reregister.discard(plugin_port)
                return True
            return False

    def port_states_summary(self) -> str:
        with self._lock:
            parts = []
            for state in sorted(self._ports.values(), key=lambda s: s.plugin_port):
                sid = state.session_id[:8] + "…" if len(state.session_id) > 8 else state.session_id
                flag = "up" if state.connected else "down"
                parts.append(f"{state.api_port}/{state.plugin_port}:{flag}:{sid or '-'}")
            return ";".join(parts)

    def consume_triggers(self) -> List[str]:
        with self._lock:
            fired = sorted(self._pending)
            self._pending.clear()
        return fired

    @staticmethod
    def _port_tag(api_port: int, plugin_port: int) -> str:
        return f"api={api_port} plugin={plugin_port}"

    def _thread_main(self) -> None:
        try:
            asyncio.run(self._async_main())
        except Exception as exc:
            if not self._stop.is_set():
                log.warning("Plugin port monitor stopped: %s", exc)

    async def _async_main(self) -> None:
        from prooftest.annex_api_connexion import (
            SilworxApiInstance,
            discover_available_instances,
            plugin_port_for_api,
        )

        rescan_sec = max(30.0, float(self.config.case1_sync_poll_sec) * 15)
        tasks: Dict[int, asyncio.Task] = {}

        async def _maintain_listeners() -> None:
            while not self._stop.is_set():
                instances = discover_available_instances(self.config)
                if not instances:
                    preferred = self.config.silworx_api_port
                    instances = [
                        SilworxApiInstance(
                            api_port=preferred,
                            plugin_port=plugin_port_for_api(preferred, self.config),
                            silworx_version="",
                            product_name="",
                        )
                    ]
                active_plugin_ports: Set[int] = set()
                for inst in instances:
                    active_plugin_ports.add(inst.plugin_port)
                    self._ensure_port_state(inst.api_port, inst.plugin_port)
                    if inst.plugin_port not in tasks or tasks[inst.plugin_port].done():
                        tasks[inst.plugin_port] = asyncio.create_task(
                            self._listen_port(inst.api_port, inst.plugin_port)
                        )
                for plugin_port, task in list(tasks.items()):
                    if plugin_port not in active_plugin_ports:
                        task.cancel()
                        tasks.pop(plugin_port, None)
                # Interruptible sleep so Stop can unwind without waiting a full rescan.
                deadline = time.monotonic() + rescan_sec
                while time.monotonic() < deadline and not self._stop.is_set():
                    await asyncio.sleep(0.25)
            for task in tasks.values():
                task.cancel()

        await _maintain_listeners()

    async def _listen_port(self, api_port: int, plugin_port: int) -> None:
        try:
            import websockets
        except ImportError:
            log.error("websockets package required for plugin monitor")
            return

        register = _RegisterPlugin(
            plugin_name=self.config.silworx_plugin_name,
            plugin_version="1.0.0",
        )
        url = f"wss://{self.config.silworx_api_host}:{plugin_port}"
        tag = self._port_tag(api_port, plugin_port)
        backoff = 1.0

        while not self._stop.is_set():
            disconnect_reason = "connection closed"
            reregistering = False
            try:
                async with websockets.connect(
                    url,
                    ssl=_plugin_ssl_context(self.config.silworx_api_cert),
                    ping_interval=20,
                    ping_timeout=20,
                ) as ws:
                    await ws.send(json.dumps(asdict(register)))
                    self._set_connected(plugin_port, True)
                    self._unavailable_warned.discard(plugin_port)
                    log.info(
                        "plugin monitor connected %s name=%s (persistent WebSocket)",
                        tag,
                        self.config.silworx_plugin_name,
                    )
                    # SILworX may deliver the open-project session shortly after register.
                    session_deadline = time.monotonic() + 12.0
                    while (
                        not self._stop.is_set()
                        and time.monotonic() < session_deadline
                        and not self.get_session_id(plugin_port)
                    ):
                        if self._should_reregister(plugin_port):
                            reregistering = True
                            disconnect_reason = "re-register for fresh session"
                            break
                        try:
                            raw = await asyncio.wait_for(ws.recv(), timeout=0.5)
                        except asyncio.TimeoutError:
                            continue
                        message = json.loads(raw)
                        trigger_id = message.get("trigger_id")
                        if message.get("msg_type") == "trigger" and trigger_id:
                            await ws.send(
                                json.dumps({"msg_type": "resume", "trigger_id": trigger_id})
                            )
                        self._handle_message(plugin_port, api_port, message)
                    if reregistering:
                        backoff = 1.0
                        continue
                    if not self.get_session_id(plugin_port):
                        log.warning(
                            "plugin monitor %s connected but no session_id after register — will retry",
                            tag,
                        )
                        disconnect_reason = "no session after register"
                    else:
                        while not self._stop.is_set():
                            if self._should_reregister(plugin_port):
                                reregistering = True
                                disconnect_reason = "re-register for fresh session"
                                log.info(
                                    "plugin monitor re-registering %s (fresh session after project open)",
                                    tag,
                                )
                                break
                            try:
                                raw = await asyncio.wait_for(ws.recv(), timeout=0.5)
                            except asyncio.TimeoutError:
                                continue
                            message = json.loads(raw)
                            trigger_id = message.get("trigger_id")
                            if message.get("msg_type") == "trigger" and trigger_id:
                                await ws.send(
                                    json.dumps({"msg_type": "resume", "trigger_id": trigger_id})
                                )
                            self._handle_message(plugin_port, api_port, message)
                    backoff = 1.0
            except OSError as exc:
                disconnect_reason = f"connect failed: {exc}"
                self._set_connected(plugin_port, False)
                if not self._stop.is_set():
                    if plugin_port not in self._unavailable_warned:
                        self._unavailable_warned.add(plugin_port)
                        log.info(
                            "plugin monitor %s no plugin server (%s) — further retries at DEBUG",
                            tag,
                            exc,
                        )
                    else:
                        log.debug(
                            "plugin monitor %s retry (%s)",
                            tag,
                            exc,
                        )
            except Exception as exc:
                disconnect_reason = str(exc)
                self._set_connected(plugin_port, False)
                if not self._stop.is_set():
                    log.warning(
                        "plugin monitor %s error (%s); retry in %.0fs",
                        tag,
                        exc,
                        min(backoff, 30.0),
                    )
            else:
                if not self._stop.is_set():
                    log.info(
                        "plugin monitor disconnected %s (%s)",
                        tag,
                        disconnect_reason,
                    )

            if self._stop.is_set():
                log.info("plugin monitor disconnected %s (service shutdown)", tag)
                break
            if reregistering:
                backoff = 1.0
                continue
            sleep_for = min(backoff, 30.0)
            deadline = time.monotonic() + sleep_for
            while time.monotonic() < deadline and not self._stop.is_set():
                await asyncio.sleep(0.25)
            backoff = min(backoff * 2, 30.0)

        self._set_connected(plugin_port, False)

    def _set_connected(self, plugin_port: int, connected: bool) -> None:
        with self._lock:
            state = self._ports.get(plugin_port)
            if state:
                state.connected = connected

    def _handle_message(self, plugin_port: int, api_port: int, message: dict) -> None:
        session_id_present = "session_id" in message
        is_session_trigger = (
            message.get("msg_type") == "trigger"
            and message.get("trigger_name") == TRIGGER_SESSION_ID_CHANGED
        )
        if not session_id_present and not is_session_trigger:
            return

        session_id = (message.get("session_id") or "").strip()

        with self._lock:
            state = self._ports.get(plugin_port)
            if state is None:
                return
            previous = state.session_id
            state.session_id = session_id
            state.last_change_at = time.monotonic()
            changed = session_id != previous

        if changed:
            log.info(
                "plugin monitor session change %s session=%s",
                self._port_tag(api_port, plugin_port),
                session_id[:12] + "…" if len(session_id) > 12 else session_id or "<closed>",
            )
            with self._lock:
                self._pending.add("silworx_session")
