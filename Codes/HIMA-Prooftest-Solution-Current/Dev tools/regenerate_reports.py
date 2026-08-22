#!/usr/bin/env python3
"""Re-render existing HIMA HTML reports with corrected template context.

Parses label/value pairs from each report, optionally enriches typed OPC members
(Tag, Serial Number, Parameters, …), and writes the file back in place.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "Annex codes"))
sys.path.insert(0, str(_ROOT / "Tool Steps"))

from prooftest.annex_pdf_generation import (  # noqa: E402
    device_tag_from_report_path,
    merge_snapshots_prefer_existing,
    parse_hima_html_snapshot,
    results_type_from_folder,
    rewrite_report_at_path,
)
from prooftest.config import AppConfig  # noqa: E402
from prooftest.results_csv import (  # noqa: E402
    annexes_directory,
    load_all_structures,
    load_annex_types,
    member_column_dtype_map,
    member_to_column,
)
from prooftest.step01_setup import sanitize_device_tag_for_path  # noqa: E402


def _tag_variants(tag: str) -> List[str]:
    variants = [tag.strip()]
    if "/" in tag:
        variants.append(tag.replace("/", "_"))
    if "_" in tag and "/" not in tag:
        # Common OPC folder form: spaces before underscore may be slash in SILworX.
        parts = tag.rsplit("_", 1)
        if len(parts) == 2 and " " in parts[0]:
            variants.append(f"{parts[0]}/{parts[1]}")
    out: List[str] = []
    for v in variants:
        if v and v not in out:
            out.append(v)
    return out


def _lookup_device_row(db_path: Path, device_tag: str) -> Optional[Dict[str, str]]:
    if not db_path.is_file():
        return None
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        for tag in _tag_variants(device_tag):
            cur.execute(
                "SELECT Device_TAG, Results_Type, OPC_Server, OPC_ItemPrefix "
                "FROM DeviceProoftestResultList WHERE Device_TAG=?",
                (tag,),
            )
            row = cur.fetchone()
            if row:
                return {
                    "device_tag": row[0],
                    "results_type": row[1] or "",
                    "opc_server": row[2] or "",
                    "opc_prefix": row[3] or "",
                }
        safe = sanitize_device_tag_for_path(device_tag)
        cur.execute(
            "SELECT Device_TAG, Results_Type, OPC_Server, OPC_ItemPrefix "
            "FROM DeviceProoftestResultList"
        )
        for row in cur.fetchall():
            if sanitize_device_tag_for_path(row[0]) == safe:
                return {
                    "device_tag": row[0],
                    "results_type": row[1] or "",
                    "opc_server": row[2] or "",
                    "opc_prefix": row[3] or "",
                }
    finally:
        conn.close()
    return None


def iter_report_files(report_root: Path) -> Iterator[Path]:
    for path in sorted(report_root.rglob("*.html")):
        parts = {p.lower() for p in path.parts}
        if "report templates" in parts or "list archives" in parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "Proof test report" in text or "HIMA Automated Prooftest Report" in text:
            yield path


def _identity_from_path(device_tag: str) -> str:
    for v in _tag_variants(device_tag):
        if "/" in v:
            return v
    return device_tag


def _is_hima_system_tag_value(value: Any, device_tag: str) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if not text:
        return False
    safe = sanitize_device_tag_for_path(device_tag)
    return sanitize_device_tag_for_path(text) == safe or text == device_tag


def collect_folder_identity_pool(folder: Path) -> Dict[str, Any]:
    """Use the richest identity/parameter fields from sibling reports in ``folder``."""
    pool: Dict[str, Any] = {}
    identity_keys = {
        "Tag",
        "Serial_Number",
        "Long_Tag",
        "Installation_direction",
        "Assigned_current_output",
        "Current_span",
        "Output_mode",
        "value_4_mA",
        "value_20_mA",
        "Damping",
        "Failure_mode",
        "Medium",
        "Gas_type",
        "Reference_sound_velocity",
        "Temperature_coefficient",
        "Partially_filled_pipe_detection",
        "Low_value_partial_filled_pipe_detection",
        "High_value_partial_filled_pipe_detection",
        "Maximum_damping_partial_filled_pipe_detection",
        "Assigned_low_flow_cutoff",
        "Off_value_low_flow_cutoff",
        "On_value_low_flow_cutoff",
        "Pressure_shock_suppression",
        "Pressure_compensation",
        "Pressure_value",
        "Zero_point",
    }
    for path in sorted(folder.glob("*.html")):
        try:
            parsed = parse_hima_html_snapshot(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        for key in identity_keys:
            val = parsed.get(key)
            if val is None or str(val).strip() == "":
                continue
            if key == "Tag" and _is_hima_system_tag_value(val, device_tag_from_report_path(path)):
                continue
            pool.setdefault(key, val)
    return pool


def merge_regenerate_snapshot(
    parsed: Dict[str, Any],
    opc_snapshot: Dict[str, Any],
    *,
    device_tag: str,
    identity_pool: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Keep historical test scalars; replace empty or mis-bound identity fields."""
    hima_tag = parsed.get("HIMA_system_tag") or _identity_from_path(device_tag)
    merged = merge_snapshots_prefer_existing(parsed, opc_snapshot)
    if identity_pool:
        merged = merge_snapshots_prefer_existing(merged, identity_pool)
    merged["HIMA_system_tag"] = hima_tag
    safe_folder = sanitize_device_tag_for_path(device_tag)
    for key in ("Tag", "Serial_Number", "Long_Tag"):
        parsed_val = parsed.get(key)
        opc_val = opc_snapshot.get(key) or (identity_pool or {}).get(key)
        if opc_val and (
            not parsed_val
            or str(parsed_val).strip() == ""
            or sanitize_device_tag_for_path(str(parsed_val)) == safe_folder
            or str(parsed_val) == str(hima_tag)
        ):
            merged[key] = opc_val
    return merged


def _collect_opc_snapshot(
    opc: Any,
    server: str,
    prefix: str,
    structure: Any,
    annex_types: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    from prooftest.opc_snapshot import enrich_snapshot_from_opc, value_is_empty
    from prooftest.results_csv import is_ascii_type, is_parameters_type

    tags = opc.list_all_tags(server)
    short_names = [n for n in structure.member_short_names() if n.lower() != "running"]
    item_map = opc.build_member_item_ids(tags, prefix, short_names)
    item_ids = list(item_map.values())
    if not item_ids:
        return {}, ["No OPC members resolved"]
    values = opc.read_values(server, item_ids)
    snapshot: Dict[str, Any] = {}
    notes: List[str] = []
    col_dtypes = member_column_dtype_map(structure)
    member_types: Dict[str, str] = {}
    for member, item_id in item_map.items():
        val, quality = values.get(item_id, (None, "Bad"))
        col = member_to_column(f"{structure.type_name}.{member}", structure.type_name)
        snapshot[col] = val
        dtype = col_dtypes.get(col, "")
        member_types[col] = dtype
        if str(quality).lower() != "good":
            notes.append(f"{member}: quality {quality}")
        elif value_is_empty(val) and dtype and (
            is_ascii_type(dtype) or is_parameters_type(dtype, annex_types)
        ):
            notes.append(f"{member}: quality Empty")

    def _read(ids: List[str]) -> Dict[str, tuple]:
        return opc.read_values(server, ids)

    return enrich_snapshot_from_opc(
        tags=tags,
        prefix=prefix,
        member_types=member_types,
        snapshot=snapshot,
        notes=notes,
        read_values=_read,
        type_catalog=annex_types,
    )


def _fallback_opc_binding(
    opc: Any,
    device_tag: str,
    *,
    preferred_server: str = "",
) -> Optional[Any]:
    """Resolve HART_FDB_Test.* prefix when DB row is missing."""
    from prooftest.annex_opc import DeviceOpcBinding

    servers = [preferred_server] if preferred_server else opc.discover_servers()
    safe = sanitize_device_tag_for_path(device_tag)
    prefixes = [
        f"HART_FDB_Test.{safe}",
        f"HART_FDB_Test.{device_tag.replace('/', '_')}",
        safe,
        device_tag,
    ]
    seen: set[str] = set()
    for server in servers:
        tags = opc.list_all_tags(server)
        if not tags:
            continue
        for prefix in prefixes:
            if not prefix or prefix in seen:
                continue
            seen.add(prefix)
            running = opc.find_running_tag(tags, prefix)
            has_members = any(t.startswith(f"{prefix.rstrip('.')}.") for t in tags)
            if running or has_members:
                return DeviceOpcBinding(
                    server=server,
                    item_prefix=prefix,
                    tags=tags,
                    running_item_id=running,
                )
    return None


def regenerate_one(
    html_path: Path,
    config: AppConfig,
    structures: Dict[str, Any],
    annex_types: Dict[str, Any],
    opc: Any,
    *,
    use_opc: bool,
    dry_run: bool,
) -> Tuple[bool, str]:
    report_root = config.report_output
    html = html_path.read_text(encoding="utf-8", errors="replace")
    parsed = parse_hima_html_snapshot(html)
    path_tag = device_tag_from_report_path(html_path)
    row = _lookup_device_row(Path(config.sqlite_path), path_tag)
    device_tag = (row or {}).get("device_tag") or _identity_from_path(path_tag)
    results_type = (row or {}).get("results_type") or ""
    if not results_type:
        try:
            folder = html_path.relative_to(report_root).parts[0]
            results_type = results_type_from_folder(folder) or ""
        except ValueError:
            results_type = ""
    if not results_type:
        return False, "could not infer results type"
    structure = structures.get(results_type)
    if structure is None:
        return False, f"no structure for {results_type}"

    opc_snapshot: Dict[str, Any] = {}
    notes: List[str] = []
    if use_opc and opc is not None:
        server = (row or {}).get("opc_server") or "HIMA.X-OPC_10406_ProofTes-DA.1"
        prefix = (row or {}).get("opc_prefix") or ""
        binding = opc.resolve_device_binding(
            device_tag,
            prefix or None,
            servers=[server],
        )
        if binding is None:
            binding = _fallback_opc_binding(
                opc,
                device_tag,
                preferred_server=server,
            )
        if binding:
            opc_snapshot, notes = _collect_opc_snapshot(
                opc,
                binding.server,
                binding.item_prefix,
                structure,
                annex_types,
            )
        else:
            notes.append("OPC binding not found")

    snapshot = merge_regenerate_snapshot(
        parsed,
        opc_snapshot,
        device_tag=device_tag,
        identity_pool=collect_folder_identity_pool(html_path.parent),
    )
    if dry_run:
        return True, (
            f"dry-run {html_path.name}: Tag={snapshot.get('Tag')!r} "
            f"Serial={snapshot.get('Serial_Number')!r} notes={len(notes)}"
        )
    ok = rewrite_report_at_path(
        html_path,
        config,
        results_type,
        device_tag,
        snapshot,
        quality_notes=notes,
    )
    if not ok:
        return False, "rewrite skipped (not a HIMA template report)"
    return True, f"updated {html_path}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reports-root",
        type=Path,
        default=None,
        help="Override report output folder (default: from solution.ini)",
    )
    parser.add_argument("--no-opc", action="store_true", help="Parse HTML only; no live OPC enrich")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path, help="Specific HTML files (default: scan all)")
    args = parser.parse_args()

    cfg = AppConfig.load(_ROOT / "solution.ini")
    if args.reports_root:
        cfg.report_output = args.reports_root
    structures = load_all_structures(cfg.results_structures)
    annex_types = load_annex_types(annexes_directory(cfg.results_structures))

    opc = None
    if not args.no_opc:
        from prooftest.annex_opc import OpcManager

        opc = OpcManager(server_filters=cfg.opc_server_filter)

    targets = list(args.paths) if args.paths else list(iter_report_files(cfg.report_output))
    if not targets:
        print("No report HTML files found.")
        return 1

    ok_count = 0
    for path in targets:
        path = path.resolve()
        try:
            ok, msg = regenerate_one(
                path,
                cfg,
                structures,
                annex_types,
                opc,
                use_opc=not args.no_opc,
                dry_run=args.dry_run,
            )
        except Exception as exc:
            ok, msg = False, f"{path}: {exc}"
        print(("OK " if ok else "FAIL ") + msg)
        if ok:
            ok_count += 1
    print(f"Done: {ok_count}/{len(targets)}")
    return 0 if ok_count == len(targets) else 2


if __name__ == "__main__":
    raise SystemExit(main())
