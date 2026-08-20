#!/usr/bin/env python3
"""
OPC Classic DA client for HIMA X-OPC DA (in-tree copy for Current).

Canonical path (production):
    HIMA-Prooftest-Solution-Current/Annex codes/OPC/connection_opc.py

Loaded only by annex_opc.py from this same folder — not from Codes/Report-Tool.

Matches the server shown in Softing OPC Toolbox: HIMA X-OPC DA (X_OPC-25138)
with items under branch OTS MIRO_T2_1 (e.g. 200S2503-I11_IN).

Installation (Windows, 32-bit Python recommended for OPC DA):
    pip install OpenOPC-Python3x pywin32

Usage (from this folder, optional probe):
    python connection_opc.py --list-only
    python connection_opc.py --discover-only
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Sequence, Tuple, Union

# ---------------------------------------------------------------------------
# Configuration — HIMA X-OPC DA (X_OPC-25138) per Softing OPC Toolbox
# ---------------------------------------------------------------------------
OPC_SERVER_ID = "X_OPC-25138"
# Registered ProgID (from opc.servers / regedit) — required for OpenOPC connect()
OPC_SERVER_PROG_ID = "HIMA.X_OPC-25138-DA.1"
OPC_SERVER_DISPLAY_NAME = "HIMA X-OPC DA (X_OPC-25138)"
OPC_CONNECT_CANDIDATES = (OPC_SERVER_PROG_ID,)
OPC_HOST = "localhost"
OPC_ITEM_BRANCH = "OTS MIRO_T2_1"
# HIMA exposes leaf items (e.g. .IN1, .PV); parent nodes are not readable
DEFAULT_TAG = "200S2503-I11_IN.IN1"
DEFAULT_LEAF_SUFFIXES = (".IN1", ".IN2", ".PV", ".STA1")
MAX_RETRIES = 3
RETRY_DELAY_SEC = 2.0
RETRY_BACKOFF = 1.5  # multiply delay after each failed attempt

# OPC DA quality strings returned by OpenOPC (server may also return numeric codes)
QUALITY_GOOD = frozenset({"Good", "good"})

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Optional dependency check
# ---------------------------------------------------------------------------
def _import_openopc():
    """Import OpenOPC; raise a clear error if the package is missing."""
    try:
        import OpenOPC  # type: ignore[import-untyped]

        return OpenOPC
    except ImportError as exc:
        raise SystemExit(
            "OpenOPC is not installed. Run:\n"
            "  pip install -r requirements.txt\n"
            "OpenOPC-Python3x only works on Windows with pywin32."
        ) from exc


def _import_pywintypes():
    try:
        import pywintypes  # type: ignore[import-untyped]

        return pywintypes
    except ImportError:
        return None


def _local_hosts() -> frozenset[str]:
    return frozenset({"localhost", "127.0.0.1", "."})


def build_item_id(tag: str, branch: str = OPC_ITEM_BRANCH) -> str:
    """Return a fully qualified item ID (branch.tag...) for X_OPC-25138."""
    tag = tag.strip()
    if not tag:
        raise ValueError("tag must not be empty")
    if tag.startswith(f"{branch}."):
        return tag
    return f"{branch}.{tag}"


def resolve_readable_item_id(item_id: str, tags: Sequence[str]) -> str:
    """
    Map a block name to a readable leaf tag when the server uses nested items.
    E.g. OTS MIRO_T2_1.200S2503-I11_IN -> OTS MIRO_T2_1.200S2503-I11_IN.IN1
    """
    if not tags:
        return item_id
    tag_set = set(tags)
    if item_id in tag_set:
        return item_id
    prefix = item_id if item_id.endswith(".") else f"{item_id}."
    matches = sorted(t for t in tags if t.startswith(prefix))
    if not matches:
        return item_id
    for suffix in DEFAULT_LEAF_SUFFIXES:
        for candidate in matches:
            if candidate.endswith(suffix):
                return candidate
    return matches[0]


def discover_opc_server(
    host: str = OPC_HOST,
    match: str = OPC_SERVER_ID,
) -> Optional[str]:
    """
    Find the registered OPC server name containing X_OPC-25138 (or match).
    Returns the exact string required by OpenOPC connect().
    """
    OpenOPC = _import_openopc()
    opc = OpenOPC.client()
    try:
        browse_host = "localhost" if host.lower() in _local_hosts() else host
        for name in opc.servers(browse_host):
            if match.lower() in name.lower():
                return name
    finally:
        try:
            opc.close()
        except Exception:
            pass
    return None


def connect_server_candidates(
    prog_id: Optional[str] = None,
    discovered: Optional[str] = None,
) -> str:
    """Semicolon-separated list for OpenOPC connect() — tries each until one works."""
    ordered: list[str] = []
    for candidate in (discovered, prog_id, *OPC_CONNECT_CANDIDATES):
        if candidate and candidate not in ordered:
            ordered.append(candidate)
    return ";".join(ordered)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TagReadResult:
    tag: str
    value: Any
    quality: str
    timestamp: Any

    @property
    def is_good(self) -> bool:
        return self.quality in QUALITY_GOOD


# ---------------------------------------------------------------------------
# COM / OPC error helpers
# ---------------------------------------------------------------------------
def _com_error_message(exc: BaseException) -> str:
    """Turn a pywin32 COM error into a short, actionable message."""
    pywintypes = _import_pywintypes()
    if pywintypes is not None and isinstance(exc, pywintypes.com_error):
        # exc.args: (hresult, message, excepinfo, argerror)
        hresult = exc.args[0] if exc.args else None
        text = exc.args[1] if len(exc.args) > 1 else str(exc)
        # Common HRESULTs (signed int may appear as large unsigned)
        hints = {
            -2147024891: "Access denied — check DCOM permissions and run as the correct user.",
            0x80070005: "Access denied — check DCOM permissions and run as the correct user.",
            -2147221005: "Class not registered — OPC server ProgID not installed or wrong bitness (32/64-bit).",
            0x80040154: "Class not registered — OPC server ProgID not installed or wrong bitness (32/64-bit).",
            -2147023174: "RPC server unavailable — OPC server not running or blocked by firewall.",
            0x800706BA: "RPC server unavailable — OPC server not running or blocked by firewall.",
            -2147417846: "Server busy or rejected the call — retry or check server state.",
        }
        hint = hints.get(hresult) or hints.get(hresult & 0xFFFFFFFF if hresult is not None else None, "")
        if hint:
            return f"{text} ({hint})"
        return str(text)
    return str(exc)


def retry(
    operation_name: str,
    func,
    *,
    max_attempts: int = MAX_RETRIES,
    initial_delay: float = RETRY_DELAY_SEC,
    backoff: float = RETRY_BACKOFF,
    retryable_exceptions: Tuple[type, ...] = (Exception,),
):
    """Call func() with exponential backoff; re-raise on final failure."""
    delay = initial_delay
    last_exc: Optional[BaseException] = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except retryable_exceptions as exc:
            last_exc = exc
            if attempt >= max_attempts:
                break
            log.warning(
                "%s failed (attempt %d/%d): %s — retrying in %.1fs",
                operation_name,
                attempt,
                max_attempts,
                _com_error_message(exc),
                delay,
            )
            time.sleep(delay)
            delay *= backoff
    assert last_exc is not None
    raise last_exc


# ---------------------------------------------------------------------------
# OPC client wrapper
# ---------------------------------------------------------------------------
class XOpcDaClient:
    """OpenOPC wrapper for HIMA X-OPC DA (X_OPC-25138)."""

    def __init__(
        self,
        prog_id: str = OPC_SERVER_PROG_ID,
        host: str = OPC_HOST,
        *,
        auto_discover: bool = True,
    ):
        OpenOPC = _import_openopc()
        self._OpenOPC = OpenOPC
        self.prog_id = prog_id
        self.host = host
        self.auto_discover = auto_discover
        self._opc: Any = None
        self.connected_server: Optional[str] = None

    @property
    def connected(self) -> bool:
        return self._opc is not None

    def connect(self) -> None:
        """Connect to HIMA X-OPC DA (X_OPC-25138), with discovery fallback."""
        if self.connected:
            return

        discovered = discover_opc_server(self.host) if self.auto_discover else None
        if discovered:
            log.info("Discovered OPC server: %s", discovered)
        elif self.auto_discover:
            log.warning(
                "No server name containing '%s' in opc.servers(); "
                "trying configured names: %s",
                OPC_SERVER_ID,
                ", ".join(OPC_CONNECT_CANDIDATES),
            )

        if self.auto_discover:
            server_list = connect_server_candidates(self.prog_id, discovered)
        else:
            server_list = self.prog_id

        def _do_connect():
            self._opc = self._OpenOPC.client()
            if self.host.lower() in _local_hosts():
                self._opc.connect(server_list)
            else:
                self._opc.connect(server_list, self.host)
            self.connected_server = getattr(self._opc, "opc_server", None) or (
                discovered or self.prog_id
            )
            log.info("Connected to %s on %s", self.connected_server, self.host)

        retry("OPC connect", _do_connect)

    def disconnect(self) -> None:
        """Close the OPC session; safe to call multiple times."""
        if not self._opc:
            return
        try:
            self._opc.close()
            log.info("Disconnected from OPC server")
        except Exception as exc:
            log.warning("Disconnect raised: %s", _com_error_message(exc))
        finally:
            self._opc = None

    def list_tags(
        self,
        filter_pattern: str = "*",
        *,
        branch: Optional[str] = OPC_ITEM_BRANCH,
    ) -> list[str]:
        """
        Browse item IDs. When filter is '*' and branch is set, lists OTS MIRO_T2_1.
        """
        if not self.connected:
            raise RuntimeError("Not connected")

        browse_path = filter_pattern
        if filter_pattern == "*" and branch:
            # HIMA requires branch.* for flat browse (branch alone returns nothing)
            browse_path = f"{branch}.*"

        def _do_list():
            opc = self._opc
            if opc is None:
                raise RuntimeError("Not connected")
            try:
                tags = opc.list(browse_path, recursive=True, flat=True)
            except TypeError:
                tags = opc.list(browse_path)
            if tags is None:
                return []
            return list(tags)

        tags = retry("OPC browse (list tags)", _do_list)
        return sorted(set(tags))

    def read_tag(self, tag: str) -> TagReadResult:
        """
        Read one tag. OpenOPC returns (value, quality, timestamp) for a single item.
        """
        if not self.connected:
            raise RuntimeError("Not connected")

        def _do_read():
            opc = self._opc
            if opc is None:
                raise RuntimeError("Not connected")
            result = opc.read(tag)
            return _parse_read_result(tag, result)

        return retry("OPC read", _do_read)

    def read_tags(self, tags: Sequence[str]) -> list[TagReadResult]:
        """Read multiple tags in one call (more efficient than repeated single reads)."""
        if not self.connected:
            raise RuntimeError("Not connected")
        if not tags:
            return []

        def _do_read():
            opc = self._opc
            if opc is None:
                raise RuntimeError("Not connected")
            raw = opc.read(list(tags))
            return _parse_multi_read(tags, raw)

        return retry("OPC read (batch)", _do_read)

    def __enter__(self) -> "XOpcDaClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.disconnect()


# Backward-compatible alias
HimaOpcClient = XOpcDaClient


# ---------------------------------------------------------------------------
# Parse OpenOPC read() return values (single vs batch shapes differ)
# ---------------------------------------------------------------------------
def _parse_read_result(tag: str, result: Any) -> TagReadResult:
    if result is None:
        raise ValueError(f"No data returned for tag '{tag}'")
    if isinstance(result, (list, tuple)):
        if len(result) == 3 and not isinstance(result[0], str):
            value, quality, timestamp = result
            return TagReadResult(tag=tag, value=value, quality=str(quality), timestamp=timestamp)
        if len(result) >= 4:
            # (name, value, quality, time)
            name, value, quality, timestamp = result[0], result[1], result[2], result[3]
            return TagReadResult(tag=str(name), value=value, quality=str(quality), timestamp=timestamp)
    raise ValueError(f"Unexpected read() format for '{tag}': {result!r}")


def _parse_multi_read(requested: Sequence[str], raw: Any) -> list[TagReadResult]:
    if not isinstance(raw, list):
        return [_parse_read_result(requested[0], raw)]
    out: list[TagReadResult] = []
    for i, item in enumerate(raw):
        tag = requested[i] if i < len(requested) else f"item_{i}"
        if isinstance(item, (list, tuple)) and len(item) >= 4:
            out.append(
                TagReadResult(
                    tag=str(item[0]),
                    value=item[1],
                    quality=str(item[2]),
                    timestamp=item[3],
                )
            )
        else:
            out.append(_parse_read_result(tag, item))
    return out


def _tag_exists(tags: Iterable[str], tag: str) -> bool:
    """Case-sensitive exact match; some servers use hierarchical names."""
    tag_set = set(tags)
    if tag in tag_set:
        return True
    # Allow user to pass short name if server uses a single segment
    return any(t.endswith("." + tag) or t == tag for t in tag_set)


# ---------------------------------------------------------------------------
# High-level workflow
# ---------------------------------------------------------------------------
def run(
    prog_id: str,
    host: str,
    tag: Optional[str],
    branch: str,
    list_only: bool,
    discover_only: bool,
    max_display: int,
) -> int:
    """
    Main workflow: connect -> list tags -> optionally read one tag -> disconnect.
    Returns process exit code (0 = success).
    """
    if discover_only:
        OpenOPC = _import_openopc()
        opc = OpenOPC.client()
        try:
            browse_host = "localhost" if host.lower() in _local_hosts() else host
            servers = opc.servers(browse_host)
            print(f"OPC servers on {browse_host}:")
            for name in servers:
                marker = " <-- X_OPC-25138" if OPC_SERVER_ID.lower() in name.lower() else ""
                print(f"  {name}{marker}")
            if not any(OPC_SERVER_ID.lower() in s.lower() for s in servers):
                log.warning("No server matching '%s' found.", OPC_SERVER_ID)
                return 1
        finally:
            opc.close()
        return 0

    client = XOpcDaClient(prog_id=prog_id, host=host)
    exit_code = 0

    try:
        client.connect()

        # --- Browse tags under OTS MIRO_T2_1 ---
        log.info("Browsing tags under branch '%s'...", branch)
        tags = client.list_tags("*", branch=branch)
        if not tags:
            log.warning(
                "No tags returned. The server may still be 'Not Configured', "
                "or browsing may require a different filter. Continuing anyway."
            )
        else:
            log.info("Found %d tag(s)", len(tags))
            for name in tags[:max_display]:
                print(f"  {name}")
            if len(tags) > max_display:
                print(f"  ... and {len(tags) - max_display} more")

        if list_only:
            return 0

        if not tag:
            log.info("No --tag specified; skipping read.")
            return 0

        item_id = build_item_id(tag, branch)
        resolved_id = resolve_readable_item_id(item_id, tags)
        if resolved_id != item_id:
            log.info(
                "Resolved '%s' to readable leaf '%s'",
                item_id,
                resolved_id,
            )
            item_id = resolved_id

        # --- Read one tag ---
        if tags and not _tag_exists(tags, item_id) and not _tag_exists(tags, tag):
            log.warning(
                "Tag '%s' not found in browse list. Attempting read anyway "
                "(server may expose items not returned by browse).",
                item_id,
            )

        log.info("Reading tag: %s", item_id)
        try:
            result = client.read_tag(item_id)
        except Exception as exc:
            log.error("Read failed: %s", _com_error_message(exc))
            return 1

        print(f"\nTag:       {result.tag}")
        print(f"Value:     {result.value!r}")
        print(f"Quality:   {result.quality}")
        print(f"Timestamp: {result.timestamp}")

        if not result.is_good:
            log.warning("Quality is not Good — value may be stale or invalid.")
            exit_code = 1

    except KeyboardInterrupt:
        log.info("Interrupted by user")
        return 130
    except Exception as exc:
        log.error("OPC error: %s", _com_error_message(exc))
        return 1
    finally:
        client.disconnect()

    return exit_code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Connect to HIMA X-OPC DA (X_OPC-25138), browse OTS MIRO_T2_1 tags, "
            "and read values."
        )
    )
    parser.add_argument(
        "--prog-id",
        default=OPC_SERVER_PROG_ID,
        help=f"OPC server ProgID (default: {OPC_SERVER_PROG_ID})",
    )
    parser.add_argument(
        "--host",
        default=OPC_HOST,
        help=f"OPC host (default: {OPC_HOST})",
    )
    parser.add_argument(
        "--branch",
        default=OPC_ITEM_BRANCH,
        help=f"Item branch for browse/read (default: {OPC_ITEM_BRANCH})",
    )
    parser.add_argument(
        "--tag",
        default=DEFAULT_TAG,
        help=(
            f"Tag to read — leaf or block name (default: {DEFAULT_TAG}, "
            f"under {OPC_ITEM_BRANCH}; block names auto-resolve to .IN1 etc.)"
        ),
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only browse and print tags; do not read",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="List registered OPC servers and highlight X_OPC-25138",
    )
    parser.add_argument(
        "--max-display",
        type=int,
        default=50,
        help="Max tags to print (default: 50)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("OPC Classic DA via OpenOPC requires Microsoft Windows.")
    args = parse_args()
    raise SystemExit(
        run(
            prog_id=args.prog_id,
            host=args.host,
            tag=args.tag,
            branch=args.branch,
            list_only=args.list_only,
            discover_only=args.discover_only,
            max_display=args.max_display,
        )
    )
