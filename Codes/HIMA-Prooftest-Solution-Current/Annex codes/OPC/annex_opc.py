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

# OPC Classic DA client lives inside Current (same annex folder) — never load from
# sibling Codes\Report-Tool (path confusion / out-of-tree code risk).
_OPC_CLIENT_PATH = Path(__file__).resolve().parent / "connection_opc.py"

# RPC_E_WRONG_THREAD, RPC_E_DISCONNECTED, CO_E_OBJNOTCONNECTED, E_FAIL (browse)
_COM_REUSE_MARKERS = (
    "addgroup",
    "-2147417842",
    "-2147417848",
    "-2147220995",
    "-2147467259",
    "wrong thread",
    "not connected",
    "opcerror",
)


def _is_com_reuse_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return any(marker in text for marker in _COM_REUSE_MARKERS)


def _is_browse_retryable(exc: BaseException) -> bool:
    """Transient OpenOPC/COM browse failures worth one reconnect + retry."""
    if _is_com_reuse_error(exc):
        return True
    text = str(exc).lower()
    return "list:" in text or "browse" in text


def _load_connection_opc():
    import importlib.util

    path = _OPC_CLIENT_PATH
    if not path.is_file():
        raise ImportError(
            f"OPC client missing: {path}. Expected Annex codes/OPC/connection_opc.py inside Current."
        )
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
    browse_ok: bool = True
    # None = not sampled; True/False = last sample read quality Good / not Good.
    live_ok: Optional[bool] = None
    live_quality: str = ""


@dataclass
class DeviceOpcBinding:
    server: str
    item_prefix: str
    tags: List[str]
    running_item_id: Optional[str] = None


class OpcManager:
    """Thread-safe OPC access — one client per X-OPC server."""

    def __init__(self, server_filters: Sequence[str]) -> None:
        self.server_filters = list(server_filters)
        self._lock = threading.Lock()
        self._thread_clients: Dict[int, Dict[str, Any]] = {}
        self._tags_cache: Dict[str, List[str]] = {}
        self._last_servers: List[str] = []
        self._last_tag_counts: Dict[str, int] = {}
        self._browse_failed: Dict[str, bool] = {}
        self._live_ok: Dict[str, bool] = {}
        self._live_quality: Dict[str, str] = {}

    def _match_server(self, name: str) -> bool:
        """
        Keep HIMA X-OPC DA ProgIDs.

        After install, Windows always registers these as ``HIMA.…`` (e.g.
        ``HIMA.X_OTS-25100-DA.1``). The SILworX/project display name is unrelated.
        Configured ``server_filter`` patterns may add extra matches; ``HIMA.*`` is
        always accepted.
        """
        prog_id = (name or "").strip()
        if not prog_id:
            return False
        if prog_id.upper().startswith("HIMA."):
            return True
        for pattern in self.server_filters:
            if fnmatch.fnmatch(prog_id.lower(), pattern.lower()):
                return True
        return False

    def discover_servers(self) -> List[str]:
        log.info("OPC discover_servers: enumerating localhost")
        opc_mod = _load_connection_opc()
        OpenOPC = opc_mod._import_openopc()
        opc = OpenOPC.client()
        try:
            names = list(opc.servers("localhost") or [])
        except Exception as exc:
            log.exception("OPC discover_servers failed: %s", exc)
            names = []
        finally:
            try:
                opc.close()
            except Exception:
                pass
        matched = [n for n in names if self._match_server(n)]
        log.info(
            "OPC discover_servers: raw=%d matched=%d (%s)",
            len(names),
            len(matched),
            ", ".join(matched[:8]) + ("..." if len(matched) > 8 else ""),
        )
        if not matched:
            discovered = opc_mod.discover_opc_server()
            if discovered:
                matched = [discovered]
                log.info("OPC discover_servers: fallback ProgID %s", discovered)
        self._last_servers = sorted(matched)
        return self._last_servers

    def device_prefix_candidates(self, device_tag: str, item_prefix: Optional[str] = None) -> List[str]:
        """Build OPC item prefixes for a device TAG (known bound prefix first)."""
        prefixes: List[str] = []
        if item_prefix:
            prefixes.append(item_prefix)
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

    def list_all_tags(self, server_name: str, branch: Optional[str] = None) -> List[str]:
        """
        Browse OPC item IDs on one server.

        Parent folder names are user-defined SILworX resources. Browse the full
        tree (optional ``branch`` limits to one folder when a caller already
        knows a path).
        """
        cache_key = f"{server_name}|{branch or 'ALL'}"
        with self._lock:
            if cache_key in self._tags_cache:
                return self._tags_cache[cache_key]

        result: List[str] = []
        last_exc: Optional[BaseException] = None
        for attempt in range(2):
            merged: set[str] = set()
            browse_errors = 0
            try:
                client = self._get_client(server_name)
                tags = client.list_tags("*", branch=branch)
                if tags:
                    merged.update(tags)
            except Exception as exc:
                last_exc = exc
                log.warning(
                    "Browse %r on %s failed (attempt %d/2): %s",
                    branch,
                    server_name,
                    attempt + 1,
                    exc,
                )
                browse_errors += 1
                if branch is not None:
                    try:
                        client = self._get_client(server_name)
                        flat = client.list_tags("*", branch=None)
                        if flat:
                            merged.update(flat)
                            browse_errors = 0
                            last_exc = None
                    except Exception as flat_exc:
                        last_exc = flat_exc
                        log.warning("Full browse on %s failed: %s", server_name, flat_exc)
                        browse_errors += 1
            result = sorted(merged)
            if result:
                break
            if attempt == 0 and last_exc is not None and _is_browse_retryable(last_exc):
                self._drop_thread_client(server_name)
                continue
            break

        with self._lock:
            if result:
                self._tags_cache[cache_key] = result
                self._last_tag_counts[server_name] = len(result)
                self._browse_failed[server_name] = False
            else:
                self._browse_failed[server_name] = True
                self._last_tag_counts[server_name] = 0
                self._live_ok.pop(server_name, None)
                self._live_quality.pop(server_name, None)
        if result:
            self._sample_live_quality(server_name, result)
        return result

    def _sample_live_quality(self, server_name: str, tags: Sequence[str]) -> None:
        """One cheap Running read — distinguishes address-space browse from live I/O."""
        running = next((t for t in tags if str(t).endswith(".Running")), None)
        if not running:
            with self._lock:
                self._live_ok.pop(server_name, None)
                self._live_quality[server_name] = ""
            return
        try:
            client = self._get_client(server_name)
            sample = client.read_tag(running)
            quality = str(getattr(sample, "quality", "") or "")
            ok = quality.lower() == "good"
            with self._lock:
                self._live_ok[server_name] = ok
                self._live_quality[server_name] = quality or ("Good" if ok else "Bad")
            if not ok:
                log.warning(
                    "OPC %s browsed OK (%d tags) but live quality=%s on %s "
                    "(address space present; controller/X-OPC runtime link down)",
                    server_name,
                    len(tags),
                    quality or "Bad",
                    running,
                )
        except Exception as exc:
            with self._lock:
                self._live_ok[server_name] = False
                self._live_quality[server_name] = f"read-error:{exc}"
            log.warning("OPC %s live sample read failed: %s", server_name, exc)

    def server_live_ok(self, server_name: str) -> Optional[bool]:
        """True/False when sampled; None if this ProgID was never live-sampled."""
        with self._lock:
            if server_name not in self._live_ok:
                return None
            return bool(self._live_ok[server_name])

    def mark_live_quality(self, server_name: str, ok: bool, quality: str = "") -> None:
        with self._lock:
            self._live_ok[server_name] = bool(ok)
            self._live_quality[server_name] = quality or ("Good" if ok else "Bad")

    def recheck_server_live(
        self, server_name: str, running_item: Optional[str] = None
    ) -> Optional[bool]:
        """Re-read one Running item so monitoring can resume after Bad quality."""
        item = str(running_item or "").strip()
        if not item:
            with self._lock:
                for key, tags in self._tags_cache.items():
                    if key.split("|", 1)[0] != server_name:
                        continue
                    item = next((t for t in tags if str(t).endswith(".Running")), "")
                    if item:
                        break
        if not item:
            return self.server_live_ok(server_name)
        last_exc: Optional[BaseException] = None
        for attempt in range(2):
            try:
                if attempt:
                    self._drop_thread_client(server_name)
                client = self._get_client(server_name)
                sample = client.read_tag(item)
                quality = str(getattr(sample, "quality", "") or "")
                ok = quality.lower() == "good"
                self.mark_live_quality(server_name, ok, quality)
                if ok:
                    log.info("OPC %s live quality restored (Good) on %s", server_name, item)
                return ok
            except Exception as exc:
                last_exc = exc
                if attempt == 0 and _is_browse_retryable(exc):
                    continue
                break
        self.mark_live_quality(
            server_name, False, f"read-error:{last_exc}" if last_exc else "Bad"
        )
        return False

    def list_tags_all_servers(self, servers: Optional[Sequence[str]] = None) -> Dict[str, List[str]]:
        server_list = list(servers) if servers else self.discover_servers()
        # Browse productive servers first; defer ProgIDs that previously failed
        # so RefreshCatalog is not blocked for minutes on dead X-OPC instances.
        with self._lock:
            failed = {name for name, bad in self._browse_failed.items() if bad}
            counts = dict(self._last_tag_counts)

        def _rank(name: str) -> tuple:
            if counts.get(name, 0) > 0:
                return (0, -counts.get(name, 0), name)
            if name in failed:
                return (2, 0, name)
            return (1, 0, name)

        ordered = sorted(server_list, key=_rank)
        result: Dict[str, List[str]] = {}
        for server in ordered:
            known_bad = server in failed and counts.get(server, 0) <= 0
            try:
                tags = self.list_all_tags(server)
                result[server] = tags
            except Exception as exc:
                log.warning("Browse failed on %s: %s", server, exc)
                result[server] = []
                with self._lock:
                    self._browse_failed[server] = True
                    self._last_tag_counts[server] = 0
            if known_bad and not result.get(server):
                # Still tried once this cycle; do not loop further retries here.
                continue
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

    def invalidate_tag_cache(self) -> None:
        """Drop browsed tag lists so the next refresh re-browses (keep live clients)."""
        with self._lock:
            self._tags_cache.clear()
            self._browse_failed.clear()
            self._live_ok.clear()
            self._live_quality.clear()

    def invalidate_cache(self) -> None:
        # Timed acquire so service Stop cannot hang forever while OPC poll holds the lock.
        # Full disconnect is for Stop/shutdown only — Refresh must use invalidate_tag_cache()
        # or poll threads race COM (RemoveGroup / NoneType.read / UI deadlock).
        acquired = self._lock.acquire(timeout=3.0)
        if not acquired:
            log.warning("OPC invalidate_cache skipped — lock busy (shutdown continues)")
            return
        try:
            self._tags_cache.clear()
            self._browse_failed.clear()
            self._live_ok.clear()
            self._live_quality.clear()
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
            has_children = any(t.startswith(exact + ".") for t in tag_list)
            # Folders (ASCII char-arrays / Parameters structures): keep the folder
            # path so callers can detect Bad/Error and expand via opc_snapshot.
            if has_children:
                mapping[member_key] = exact
                continue
            if exact in tags:
                mapping[member_key] = exact
                continue
            member_norm = member.replace(" ", "").lower()
            for t in tag_list:
                if not t.startswith(prefix_dot):
                    continue
                remainder = t[len(prefix_dot) :]
                # Never bind a Results member to a char-array cell (…[i]).
                if "[" in remainder:
                    continue
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

    def find_running_path(self, server: str, device_tag: str) -> Optional[str]:
        """Return ``…{TAG}.Running`` or ``…Global Vars.{TAG}.Running`` on ``server``.

        Parent folder names are user-defined SILworX resource names.
        """
        tag = str(device_tag or "").strip()
        if not tag or "." in tag:
            return None
        tags: List[str] = []
        with self._lock:
            for key, cached in self._tags_cache.items():
                if key.split("|", 1)[0] == server:
                    tags = list(cached)
                    break
        if not tags:
            try:
                tags = list(self.list_all_tags(server) or [])
            except Exception as exc:
                log.debug("find_running_path browse %s failed: %s", server, exc)
                tags = []
        suffix_plain = f".{tag}.Running"
        suffix_gv = f".Global Vars.{tag}.Running"
        candidates = [
            t
            for t in tags
            if t.endswith(suffix_gv) or t.endswith(suffix_plain) or t == f"{tag}.Running"
        ]
        if not candidates:
            return None

        def _rank(path: str) -> tuple:
            gv = 0 if ".Global Vars." in path else 1
            return (gv, len(path), path)

        return sorted(candidates, key=_rank)[0]

    def health_snapshot(self) -> List[OpcServerInfo]:
        """Non-blocking OPC summary from the last discovery/browse cache (Gate 13).

        Must never wait on ``self._lock`` — health holds its own lock and a wait
        here deadlocks the UI (empty stub while browse/poll owns the OPC lock).
        """
        acquired = self._lock.acquire(blocking=False)
        if not acquired:
            # Best-effort: last known servers + last successful tag counts (never fake 0).
            servers = list(getattr(self, "_last_servers", []) or [])
            counts = dict(getattr(self, "_last_tag_counts", {}) or {})
            failed = dict(getattr(self, "_browse_failed", {}) or {})
            live_ok = dict(getattr(self, "_live_ok", {}) or {})
            live_q = dict(getattr(self, "_live_quality", {}) or {})
            return [
                OpcServerInfo(
                    prog_id=name,
                    connected=True,
                    tag_count=int(counts.get(name, 0)),
                    browse_ok=not bool(failed.get(name)) or int(counts.get(name, 0)) > 0,
                    live_ok=live_ok.get(name),
                    live_quality=str(live_q.get(name, "") or ""),
                )
                for name in servers
            ]
        try:
            servers = list(self._last_servers)
            client_names: set[str] = set()
            for bucket in self._thread_clients.values():
                client_names.update(bucket.keys())
            tag_counts: Dict[str, int] = dict(self._last_tag_counts)
            for key, tags in self._tags_cache.items():
                srv = key.split("|", 1)[0]
                tag_counts[srv] = max(tag_counts.get(srv, 0), len(tags))
                if tags:
                    self._last_tag_counts[srv] = tag_counts[srv]
            browse_failed = dict(self._browse_failed)
            live_ok_map = dict(self._live_ok)
            live_q_map = dict(self._live_quality)
        finally:
            self._lock.release()
        if not servers:
            return []
        out: List[OpcServerInfo] = []
        for name in servers:
            tag_count = int(tag_counts.get(name, 0))
            failed = bool(browse_failed.get(name)) and tag_count == 0
            connected = tag_count > 0 or name in client_names
            out.append(
                OpcServerInfo(
                    prog_id=name,
                    connected=connected,
                    tag_count=tag_count,
                    browse_ok=not failed,
                    live_ok=live_ok_map.get(name),
                    live_quality=str(live_q_map.get(name, "") or ""),
                )
            )
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
