"""
Annex — X-OPC DA connexion and device binding.
"""

from __future__ import annotations

import fnmatch
import logging
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

log = logging.getLogger(__name__)

REPORT_TOOL = Path(__file__).resolve().parents[3] / "Report-Tool"

# RPC_E_WRONG_THREAD, RPC_E_DISCONNECTED, CO_E_OBJNOTCONNECTED
_COM_REUSE_MARKERS = (
    "addgroup",
    "-2147417842",
    "-2147417848",
    "-2147220995",
    "wrong thread",
    "not connected",
)


def _is_com_reuse_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return any(marker in text for marker in _COM_REUSE_MARKERS)


def _load_connection_opc():
    import importlib.util

    path = REPORT_TOOL / "Connection-opc.py"
    module_name = "hima_connection_opc"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load OPC client from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@dataclass
class OpcServerInfo:
    prog_id: str
    connected: bool = False
    tag_count: int = 0


@dataclass
class DeviceOpcBinding:
    server: str
    item_prefix: str
    tags: List[str]
    running_item_id: Optional[str] = None


class OpcManager:
    """Thread-safe OPC access — one client per X-OPC server."""

    def __init__(
        self,
        server_filters: Sequence[str],
        default_branch: str,
        prooftest_branches: Optional[Sequence[str]] = None,
    ) -> None:
        self.server_filters = list(server_filters)
        self.default_branch = default_branch
        self.prooftest_branches = list(prooftest_branches or ["OTS ProofTest", "OPC ProofTest"])
        self._lock = threading.Lock()
        self._thread_clients: Dict[int, Dict[str, Any]] = {}
        self._tags_cache: Dict[str, List[str]] = {}
        self._last_servers: List[str] = []

    def _match_server(self, name: str) -> bool:
        for pattern in self.server_filters:
            if fnmatch.fnmatch(name.lower(), pattern.lower()):
                return True
        return False

    def discover_servers(self) -> List[str]:
        opc_mod = _load_connection_opc()
        OpenOPC = opc_mod._import_openopc()
        opc = OpenOPC.client()
        try:
            names = opc.servers("localhost")
        finally:
            opc.close()
        matched = [n for n in names if self._match_server(n)]
        if not matched:
            discovered = opc_mod.discover_opc_server()
            if discovered:
                matched = [discovered]
        self._last_servers = sorted(matched)
        return self._last_servers

    def device_prefix_candidates(self, device_tag: str, item_prefix: Optional[str] = None) -> List[str]:
        """Build OPC item prefixes for a device TAG (e.g. 100-FZT-001)."""
        prefixes: List[str] = []
        if item_prefix:
            prefixes.append(item_prefix)
        for branch in self.prooftest_branches:
            prefixes.append(f"{branch}.{device_tag}")
        if self.default_branch:
            prefixes.append(f"{self.default_branch}.{device_tag}")
        prefixes.append(device_tag)
        seen: set[str] = set()
        unique: List[str] = []
        for p in prefixes:
            if p and p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def _get_client(self, server_name: str):
        """Return an OPC client created on *this* thread (COM STA / OpenOPC)."""
        opc_mod = _load_connection_opc()
        XOpcDaClient = opc_mod.XOpcDaClient
        tid = threading.get_ident()

        with self._lock:
            existing = self._thread_clients.get(tid, {}).get(server_name)
        if existing is not None:
            return existing

        client = XOpcDaClient(prog_id=server_name, auto_discover=False)
        client.connect()
        with self._lock:
            bucket = self._thread_clients.setdefault(tid, {})
            if server_name not in bucket:
                bucket[server_name] = client
            else:
                try:
                    client.disconnect()
                except Exception:
                    pass
                client = bucket[server_name]
        return client

    def _drop_thread_client(self, server_name: str) -> None:
        tid = threading.get_ident()
        with self._lock:
            client = self._thread_clients.get(tid, {}).pop(server_name, None)
        if client is None:
            return
        try:
            client.disconnect()
        except Exception:
            pass

    def _browse_branches(self) -> List[Optional[str]]:
        order: List[Optional[str]] = list(self.prooftest_branches)
        if self.default_branch and self.default_branch not in order:
            order.append(self.default_branch)
        return order

    def list_all_tags(self, server_name: str, branch: Optional[str] = None) -> List[str]:
        """Browse Prooftest branches on one server (e.g. OTS ProofTest.*)."""
        cache_key = f"{server_name}|{branch or '|'.join(self.prooftest_branches)}"
        with self._lock:
            if cache_key in self._tags_cache:
                return self._tags_cache[cache_key]
        client = self._get_client(server_name)
        merged: set[str] = set()
        branches = [branch] if branch else self._browse_branches()
        for browse_branch in branches:
            try:
                tags = client.list_tags("*", branch=browse_branch)
                if tags:
                    merged.update(tags)
                    log.debug("Server %s branch %r: %d tags", server_name, browse_branch, len(tags))
            except Exception as exc:
                log.debug("Browse %r on %s failed: %s", browse_branch, server_name, exc)
        result = sorted(merged)
        with self._lock:
            self._tags_cache[cache_key] = result
        return result

    def list_tags_all_servers(self, servers: Optional[Sequence[str]] = None) -> Dict[str, List[str]]:
        server_list = list(servers) if servers else self.discover_servers()
        result: Dict[str, List[str]] = {}
        for server in server_list:
            try:
                result[server] = self.list_all_tags(server)
            except Exception as exc:
                log.warning("Browse failed on %s: %s", server, exc)
                result[server] = []
        return result

    def resolve_device_binding(
        self,
        device_tag: str,
        item_prefix: Optional[str],
        servers: Optional[Sequence[str]] = None,
    ) -> Optional[DeviceOpcBinding]:
        server_list = list(servers) if servers else self.discover_servers()
        for server in server_list:
            tags = self.list_all_tags(server)
            if not tags:
                continue
            for prefix in self.device_prefix_candidates(device_tag, item_prefix):
                running_id = self.find_running_tag(tags, prefix)
                if running_id:
                    return DeviceOpcBinding(
                        server=server,
                        item_prefix=prefix,
                        tags=tags,
                        running_item_id=running_id,
                    )
        return None

    def invalidate_cache(self) -> None:
        # Timed acquire so service Stop cannot hang forever while OPC poll holds the lock.
        acquired = self._lock.acquire(timeout=3.0)
        if not acquired:
            log.warning("OPC invalidate_cache skipped — lock busy (shutdown continues)")
            return
        try:
            self._tags_cache.clear()
            for bucket in self._thread_clients.values():
                for client in bucket.values():
                    try:
                        client.disconnect()
                    except Exception:
                        pass
            self._thread_clients.clear()
        finally:
            self._lock.release()

    def read_values(self, server_name: str, item_ids: Sequence[str]) -> Dict[str, Tuple[Any, str]]:
        if not item_ids:
            return {}
        last_exc: Optional[BaseException] = None
        for attempt in range(2):
            try:
                client = self._get_client(server_name)
                results = client.read_tags(list(item_ids))
                return {r.tag: (r.value, r.quality) for r in results}
            except Exception as exc:
                last_exc = exc
                if attempt == 0 and _is_com_reuse_error(exc):
                    log.warning("OPC client stale on this thread (%s); reconnecting", exc)
                    self._drop_thread_client(server_name)
                    continue
                raise
        raise last_exc  # pragma: no cover

    def find_running_tag(self, tags: Sequence[str], device_prefix: str) -> Optional[str]:
        prefix = device_prefix.rstrip(".")
        exact = f"{prefix}.Running"
        if exact in tags:
            return exact
        for t in tags:
            if t.endswith(f".{prefix}.Running") or (t.endswith(".Running") and prefix in t):
                return t
        return None

    def build_member_item_ids(self, tags: Sequence[str], base_prefix: str, member_names: Sequence[str]) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        base = base_prefix.rstrip(".")
        prefix_dot = base + "."
        tag_list = list(tags)
        for member in member_names:
            member_key = member.replace(" ", "_")
            exact = f"{base}.{member}"
            if exact in tags:
                mapping[member_key] = exact
                continue
            member_norm = member.replace(" ", "").lower()
            for t in tag_list:
                if not t.startswith(prefix_dot):
                    continue
                remainder = t[len(prefix_dot) :]
                top = remainder.split(".")[0]
                if top.replace(" ", "").lower() != member_norm:
                    continue
                mapping[member_key] = exact if top == member else t
                break
        return mapping

    def _cached_tag_count(self, server_name: str) -> int:
        with self._lock:
            best = 0
            for key, tags in self._tags_cache.items():
                if key.split("|", 1)[0] == server_name:
                    best = max(best, len(tags))
            return best

    def health_snapshot(self) -> List[OpcServerInfo]:
        """Non-blocking OPC summary from the last discovery/browse cache (Gate 13)."""
        with self._lock:
            servers = list(self._last_servers)
            client_names: set[str] = set()
            for bucket in self._thread_clients.values():
                client_names.update(bucket.keys())
            tag_counts: Dict[str, int] = {}
            for key, tags in self._tags_cache.items():
                srv = key.split("|", 1)[0]
                tag_counts[srv] = max(tag_counts.get(srv, 0), len(tags))
        if not servers:
            return []
        out: List[OpcServerInfo] = []
        for name in servers:
            tag_count = tag_counts.get(name, 0)
            connected = tag_count > 0 or name in client_names
            out.append(OpcServerInfo(prog_id=name, connected=connected, tag_count=tag_count))
        return out

    def server_status(self) -> List[OpcServerInfo]:
        out: List[OpcServerInfo] = []
        for name in self.discover_servers():
            try:
                tags = self.list_all_tags(name)
                out.append(OpcServerInfo(prog_id=name, connected=True, tag_count=len(tags)))
            except Exception as exc:
                log.warning("OPC server %s unavailable: %s", name, exc)
                out.append(OpcServerInfo(prog_id=name, connected=False))
        return out
