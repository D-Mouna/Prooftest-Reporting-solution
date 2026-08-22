"""Expand HIMA X-OPC nested values using SILworX Results Structure data types.

Annex CSVs under ``Results Structures/Annexes/`` define how to interpret OPC
folders:

- ``X-HART_ASCII_32`` (etc.) → BYTE char-array decoded to text
- ``X-HART_*_Parameters`` → nested structure members (UINT, REAL, ASCII, …)
"""

from __future__ import annotations

import math
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from prooftest.results_csv import ResultsStructure

ReadValuesFn = Callable[[Sequence[str]], Dict[str, Tuple[Any, str]]]

_ARRAY_INDEX_RE = re.compile(r"\[(\d+)\]$")

# Promass report.html placeholder names that differ from ``member_to_column`` output.
# Keys are normalized with ``.lower()`` at lookup time.
_PARAM_REPORT_ALIASES: Dict[str, str] = {
    "4 ma value": "value_4_mA",
    "20 ma value": "value_20_mA",
    "installation direction": "Installation_direction",
    "assigned current output": "Assigned_current_output",
    "current span": "Current_span",
    "output mode": "Output_mode",
    "damping": "Damping",
    "failure mode": "Failure_mode",
    "medium": "Medium",
    "gas type": "Gas_type",
    "reference sound velocity": "Reference_sound_velocity",
    "temperature coefficient": "Temperature_coefficient",
    "partially filled pipe detection": "Partially_filled_pipe_detection",
    "low value partial filled pipe detection": "Low_value_partial_filled_pipe_detection",
    "high value partial filled pipe detection": "High_value_partial_filled_pipe_detection",
    "maximum damping partial filled pipe detection": "Maximum_damping_partial_filled_pipe_detection",
    "maximum damping partial filled pipe det": "Maximum_damping_partial_filled_pipe_detection",
    "assigned low flow cutoff": "Assigned_low_flow_cutoff",
    "off value low flow cutoff": "Off_value_low_flow_cutoff",
    "on value low flow cutoff": "On_value_low_flow_cutoff",
    "pressure shock suppression": "Pressure_shock_suppression",
    "pressure compensation": "Pressure_compensation",
    "pressure value": "Pressure_value",
    "zero point": "Zero_point",
}

_SCALAR_TYPES = frozenset(
    {
        "BOOL",
        "BYTE",
        "USINT",
        "WORD",
        "UINT",
        "DWORD",
        "UDINT",
        "REAL",
        "DINT",
        "INT",
    }
)


def quality_is_good(quality: Any) -> bool:
    return str(quality or "").strip().lower() == "good"


def value_is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def decode_char_codes(codes: Sequence[Any], *, max_len: Optional[int] = None) -> str:
    """Decode OPC BYTE/USINT char-array cells into a text string."""
    chars: List[str] = []
    limit = max_len if max_len is not None else len(codes)
    for raw in codes[:limit]:
        if raw is None:
            break
        try:
            if isinstance(raw, str):
                if not raw:
                    break
                code = ord(raw[0])
            else:
                code = int(raw)
        except (TypeError, ValueError):
            break
        if code <= 0:
            break
        if code > 255:
            continue
        chars.append(chr(code))
    return "".join(chars).rstrip("\x00").strip()


def indexed_children(tags: Sequence[str], folder_prefix: str) -> Dict[int, str]:
    """Map array index → full item id for ``…Name[i]`` leaves under a folder."""
    prefix = folder_prefix.rstrip(".") + "."
    out: Dict[int, str] = {}
    for item in tags:
        if not item.startswith(prefix):
            continue
        match = _ARRAY_INDEX_RE.search(item)
        if not match:
            continue
        out[int(match.group(1))] = item
    return out


def _folder_candidates(base_path: str, member: str) -> List[str]:
    base = base_path.rstrip(".")
    return [f"{base}.{member}", f"{base}.{member.replace('_', ' ')}"]


def _read_scalar_leaf(
    tags: Sequence[str],
    folder_path: str,
    read_values: ReadValuesFn,
) -> Any:
    """Read one scalar OPC item under ``folder_path`` (leaf or first scalar child)."""
    folder_path = folder_path.rstrip(".")
    if folder_path in tags:
        val, quality = read_values([folder_path]).get(folder_path, (None, "Bad"))
        if quality_is_good(quality):
            return val
        return None
    indexed = indexed_children(tags, folder_path)
    if indexed:
        return None
    folder_dot = folder_path + "."
    children = [t for t in tags if t.startswith(folder_dot) and "[" not in t]
    if not children:
        return None
    leaf = sorted(children, key=len)[0]
    val, quality = read_values([leaf]).get(leaf, (None, "Bad"))
    if quality_is_good(quality) and not value_is_empty(val):
        return val
    return None


def decode_ascii_at_path(
    tags: Sequence[str],
    folder_path: str,
    read_values: ReadValuesFn,
    *,
    max_len: Optional[int] = None,
) -> Optional[str]:
    """Decode a typed ``X-HART_ASCII_N`` folder at ``folder_path``."""
    for folder in _folder_candidates(folder_path, folder_path.split(".")[-1]):
        indexed = indexed_children(tags, folder)
        if not indexed and folder != folder_path:
            indexed = indexed_children(tags, folder_path)
        if not indexed:
            # ``folder.Member[i]`` pattern (Tag.Tag[0..])
            for candidate in _folder_candidates(folder_path, folder_path.split(".")[-1]):
                sub = indexed_children(tags, candidate)
                if sub:
                    indexed = sub
                    break
        if not indexed:
            continue
        indices = sorted(indexed)
        if max_len is not None:
            indices = [i for i in indices if i < max_len]
        item_ids = [indexed[i] for i in indices]
        values = read_values(item_ids)
        codes: List[Any] = []
        for item_id in item_ids:
            val, quality = values.get(item_id, (None, "Bad"))
            if not quality_is_good(quality):
                break
            codes.append(val)
        text = decode_char_codes(codes, max_len=max_len)
        if text:
            return text
    # Direct indexed children under folder_path
    indexed = indexed_children(tags, folder_path)
    if indexed:
        item_ids = [indexed[i] for i in sorted(indexed)]
        if max_len is not None:
            item_ids = item_ids[:max_len]
        values = read_values(item_ids)
        codes = []
        for item_id in item_ids:
            val, quality = values.get(item_id, (None, "Bad"))
            if not quality_is_good(quality):
                break
            codes.append(val)
        text = decode_char_codes(codes, max_len=max_len)
        if text:
            return text
    return None


def decode_ascii_under_member(
    tags: Sequence[str],
    prefix: str,
    member: str,
    read_values: ReadValuesFn,
    *,
    dtype: str = "",
    type_catalog: Optional[Dict[str, "ResultsStructure"]] = None,
) -> Optional[str]:
    """Decode ``prefix.Member`` when the SILworX type is ``X-HART_ASCII_*``."""
    from prooftest.results_csv import ascii_array_length

    max_len = ascii_array_length(dtype, type_catalog) if dtype else None
    for folder in _folder_candidates(prefix, member):
        text = decode_ascii_at_path(tags, folder, read_values, max_len=max_len)
        if text:
            return text
    return None


def report_key_for_param_member(param_type: str, member_short: str) -> str:
    """Snapshot / report placeholder key for one Parameters structure member."""
    alias = _PARAM_REPORT_ALIASES.get(member_short.lower())
    if alias:
        return alias
    from prooftest.results_csv import member_to_column

    return member_to_column(f"{param_type}.{member_short}", param_type)


def read_typed_opc_value(
    dtype: str,
    folder_path: str,
    tags: Sequence[str],
    read_values: ReadValuesFn,
    type_catalog: Dict[str, "ResultsStructure"],
) -> Any:
    """Read one OPC subtree according to the SILworX ``Data type`` from the CSV."""
    from prooftest.results_csv import (
        ResultsStructure,
        ascii_array_length,
        is_ascii_type,
        is_parameters_type,
        member_dtype_map,
    )

    dtype = (dtype or "").strip()
    if not dtype:
        return _read_scalar_leaf(tags, folder_path, read_values)

    if is_ascii_type(dtype):
        length = ascii_array_length(dtype, type_catalog)
        return decode_ascii_at_path(tags, folder_path, read_values, max_len=length)

    if is_parameters_type(dtype, type_catalog):
        struct = type_catalog.get(dtype)
        if struct is not None:
            return expand_structure_at_path(tags, folder_path, struct, read_values, type_catalog)
        return None

    dtype_u = dtype.upper()
    if dtype_u in _SCALAR_TYPES or dtype_u.startswith("X-HART"):
        return _read_scalar_leaf(tags, folder_path, read_values)

    return _read_scalar_leaf(tags, folder_path, read_values)


def expand_structure_at_path(
    tags: Sequence[str],
    folder_path: str,
    structure: "ResultsStructure",
    read_values: ReadValuesFn,
    type_catalog: Dict[str, "ResultsStructure"],
) -> Dict[str, Any]:
    """
    Flatten a nested SILworX structure (e.g. ``X-HART_*_Parameters``) from OPC.

    Keys are report/SQL column names derived from member names and types.
    """
    from prooftest.results_csv import member_dtype_map, member_to_column

    dtypes = member_dtype_map(structure)
    out: Dict[str, Any] = {}
    base = folder_path.rstrip(".")

    for member_short, member_dtype in dtypes.items():
        if not member_short or member_short.lower() == "array dimension":
            continue
        member_path = f"{base}.{member_short}"
        value = read_typed_opc_value(
            member_dtype, member_path, tags, read_values, type_catalog
        )
        if value_is_empty(value):
            continue
        col = member_to_column(f"{structure.type_name}.{member_short}", structure.type_name)
        out[col] = value
        report_key = report_key_for_param_member(structure.type_name, member_short)
        if report_key != col:
            out[report_key] = value
    return out


def expand_parameters_branch(
    tags: Sequence[str],
    prefix: str,
    branch_name: str,
    read_values: ReadValuesFn,
    *,
    parameters_type: str = "",
    type_catalog: Optional[Dict[str, "ResultsStructure"]] = None,
) -> Dict[str, Any]:
    """
    Flatten ``prefix.{branch_name}.*`` using the Parameters SILworX type when known.
    """
    base = prefix.rstrip(".")
    folder = f"{base}.{branch_name}"

    if parameters_type and type_catalog and parameters_type in type_catalog:
        expanded = expand_structure_at_path(
            tags, folder, type_catalog[parameters_type], read_values, type_catalog
        )
        if expanded:
            return expanded

    # Fallback: discover OPC groups under the branch (no annex CSV).
    folder_dot = folder + "."
    groups: Dict[str, List[str]] = {}
    for item in tags:
        if not item.startswith(folder_dot):
            continue
        remainder = item[len(folder_dot) :]
        group = remainder.split(".", 1)[0].strip()
        if group:
            groups.setdefault(group, []).append(item)

    out: Dict[str, Any] = {}
    for group, items in groups.items():
        report_key = report_key_for_param_member(parameters_type or "Parameters", group)
        indexed = {int(m.group(1)): t for t in items if (m := _ARRAY_INDEX_RE.search(t))}
        if indexed:
            item_ids = [indexed[i] for i in sorted(indexed)]
            values = read_values(item_ids)
            codes: List[Any] = []
            for item_id in item_ids:
                val, quality = values.get(item_id, (None, "Bad"))
                if not quality_is_good(quality):
                    break
                codes.append(val)
            text = decode_char_codes(codes)
            if text:
                out[report_key] = text
            continue
        exact = f"{folder}.{group}"
        leaf = exact if exact in items else sorted(items, key=len)[0]
        val, quality = read_values([leaf]).get(leaf, (None, "Bad"))
        if quality_is_good(quality) and not value_is_empty(val):
            out[report_key] = val
    return out


def enrich_snapshot_from_opc(
    *,
    tags: Sequence[str],
    prefix: str,
    member_types: Dict[str, str],
    snapshot: Dict[str, Any],
    notes: List[str],
    read_values: ReadValuesFn,
    type_catalog: Optional[Dict[str, "ResultsStructure"]] = None,
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Fill typed members that OPC exposes as folders (ASCII arrays, Parameters).

    ``member_types`` maps snapshot column → SILworX ``Data type`` from Results CSV.
    """
    catalog = type_catalog or {}
    out = dict(snapshot)
    remaining_notes = list(notes)

    def _clear_note(*keys: str) -> None:
        needles = {str(k).lower().replace(" ", "_") for k in keys if k}
        needles |= {n.replace("_", " ") for n in needles}
        remaining_notes[:] = [
            n
            for n in remaining_notes
            if not any(
                str(n).lower().replace(" ", "_").startswith(needle.replace(" ", "_") + ":")
                or str(n).lower().startswith(needle + ":")
                for needle in needles
            )
        ]

    from prooftest.results_csv import is_ascii_type, is_parameters_type

    for column, dtype in member_types.items():
        if not dtype:
            continue
        member_label = column.replace("_", " ")
        folder = f"{prefix.rstrip('.')}.{member_label}"

        if is_ascii_type(dtype):
            decoded = decode_ascii_under_member(
                tags,
                prefix,
                member_label,
                read_values,
                dtype=dtype,
                type_catalog=catalog,
            )
            if not decoded:
                decoded = decode_ascii_under_member(
                    tags, prefix, column, read_values, dtype=dtype, type_catalog=catalog
                )
            if decoded:
                out[column] = decoded
                _clear_note(column, member_label)
            continue

        if is_parameters_type(dtype, catalog) or column in (
            "Parameters_Before_Test",
            "Parameters_After_Test",
        ):
            branch = (
                "Parameters Before Test"
                if "Before" in column
                else "Parameters After Test"
            )
            param_dtype = dtype if is_parameters_type(dtype, catalog) else ""
            expanded = expand_parameters_branch(
                tags,
                prefix,
                branch,
                read_values,
                parameters_type=param_dtype,
                type_catalog=catalog,
            )
            if expanded:
                for key, val in expanded.items():
                    if key not in out or value_is_empty(out.get(key)):
                        out[key] = val
                summary = "; ".join(f"{k}={v}" for k, v in list(expanded.items())[:8])
                out[column] = summary[:500]
                _clear_note(column, member_label)

    # Device-parameter page: After Test wins, then Before (use annex type when known).
    for branch, col in (
        ("Parameters After Test", "Parameters_After_Test"),
        ("Parameters Before Test", "Parameters_Before_Test"),
    ):
        param_dtype = member_types.get(col, "")
        expanded = expand_parameters_branch(
            tags,
            prefix,
            branch,
            read_values,
            parameters_type=param_dtype,
            type_catalog=catalog,
        )
        for key, val in expanded.items():
            if key not in out or value_is_empty(out.get(key)):
                out[key] = val

    remaining_notes[:] = _prune_recovered_notes(remaining_notes, out)
    return out, remaining_notes


def _prune_recovered_notes(notes: List[str], snapshot: Dict[str, Any]) -> List[str]:
    kept: List[str] = []
    for note in notes:
        head = str(note).split(":", 1)[0].strip()
        col = head.replace(" ", "_")
        if col in snapshot and not value_is_empty(snapshot.get(col)):
            continue
        if col.lower().startswith("parameters_") and any(
            k in snapshot and not value_is_empty(snapshot.get(k))
            for k in (
                "Installation_direction",
                "value_4_mA",
                "value_20_mA",
                "Parameters_Before_Test",
                "Parameters_After_Test",
            )
        ):
            continue
        kept.append(note)
    return kept


def quality_note_for(member_key: str, notes: Sequence[str]) -> bool:
    needle = member_key.lower().replace(" ", "_") + ":"
    return any(str(n).lower().replace(" ", "_").startswith(needle) for n in notes)
