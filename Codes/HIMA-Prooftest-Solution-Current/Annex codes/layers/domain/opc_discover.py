"""Shaped OPC-only discovery — CSV as FILTER / clear-type only, never invent-as-identity.

Rules (unified mode):
- OPC parent folder names are **user-defined** SILworX resource names (not a HIMA
  standard). Discover by ``…{TAG}.Running`` anywhere in the tree.
- Candidate = ``…{TAG}.Running`` or ``…Global Vars.{TAG}.Running`` (TAG has no ``.``)
- Shape gate (per Results type): shared members ≥ max(FLOOR, ceil(RATIO × |type|))
- Type: last known SQL type if set; else unique clear best; else unknown ("")
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from layers.domain.merger import OpcObservation

# Fraction of each Results CSV member set that must overlap on OPC (per type).
SHAPE_GATE_RATIO = 0.5
# Never accept fewer than this many shared members (tiny/test CSVs).
SHAPE_GATE_FLOOR = 3
# Legacy alias — minimum absolute overlap (same as floor).
SHAPE_GATE_N = SHAPE_GATE_FLOOR
CLEAR_MARGIN = 2


def normalize_member(name: str) -> str:
    return str(name or "").replace(" ", "").lower().split(".")[-1]


def member_short_set(members: Iterable[str]) -> Set[str]:
    return {normalize_member(m) for m in members if normalize_member(m)}


def shape_gate_threshold(
    type_members: Iterable[str],
    *,
    ratio: float = SHAPE_GATE_RATIO,
    floor: int = SHAPE_GATE_FLOOR,
) -> int:
    """Minimum intersection size required for one Results type."""
    members = member_short_set(type_members)
    members.discard("")
    if "running" not in members:
        return 10**9
    count = len(members)
    needed = int(math.ceil(max(0.0, float(ratio)) * count))
    return max(int(floor), needed)


def score_structure_match(member_names: Set[str], type_members: Set[str]) -> int:
    """Intersection size; require Running in the type definition."""
    required = member_short_set(type_members)
    required.discard("")
    if "running" not in required:
        return 0
    observed = member_short_set(member_names)
    return len(required.intersection(observed))


def parse_shaped_running_item(item: str) -> Optional[Tuple[str, str, str]]:
    """
    Accept ``{any.user.parent}.{TAG}.Running`` or ``…Global Vars.{TAG}.Running``.

    Parent folder names are project-specific. Returns ``(parent_path, device_tag, prefix)``.
    Rejects bare ``TAG.Running`` (no parent).
    """
    text = str(item or "").strip()
    if not text.endswith(".Running"):
        return None
    prefix = text[: -len(".Running")]
    if not prefix or "." not in prefix:
        return None
    parts = prefix.split(".")
    tag = parts[-1].strip()
    if not tag:
        return None
    parent = ".".join(parts[:-1]).strip()
    if not parent:
        return None
    return parent, tag, prefix


def members_under_prefix(tags: Sequence[str], prefix: str) -> Set[str]:
    prefix_dot = prefix + "."
    members: Set[str] = set()
    for tag in tags:
        if tag.startswith(prefix_dot):
            top = tag[len(prefix_dot) :].split(".")[0]
            if top:
                members.add(top)
    return members


def _gates_for_types(
    type_sets: Mapping[str, Set[str]],
    *,
    ratio: float,
    floor: int,
) -> Dict[str, int]:
    return {
        name: shape_gate_threshold(members, ratio=ratio, floor=floor)
        for name, members in type_sets.items()
    }


def resolve_opc_only_type(
    scores: Mapping[str, int],
    *,
    last_type: str = "",
    type_gates: Optional[Mapping[str, int]] = None,
    gate_n: int = SHAPE_GATE_FLOOR,
    clear_margin: int = CLEAR_MARGIN,
) -> str:
    """
    Prefer last SQL type when present.
    Else unique clear winner: best passes its per-type gate and
    (best − second) ≥ clear_margin. Else unknown ("").
    """
    last = (last_type or "").strip()
    if last:
        return last
    gates = dict(type_gates or {})
    ranked = sorted(
        (
            (score, name)
            for name, score in scores.items()
            if score >= int(gates.get(name, gate_n))
        ),
        key=lambda item: (-item[0], item[1]),
    )
    if not ranked:
        return ""
    best_score, best_name = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0
    if best_score - second >= clear_margin:
        return best_name
    return ""


def passes_shape_gate(
    scores: Mapping[str, int],
    *,
    type_gates: Optional[Mapping[str, int]] = None,
    gate_n: int = SHAPE_GATE_FLOOR,
) -> bool:
    """True when at least one Results type reaches its half/floor threshold."""
    gates = dict(type_gates or {})
    return any(score >= int(gates.get(name, gate_n)) for name, score in scores.items())


@dataclass(frozen=True)
class ShapedDiscoverResult:
    observations: List[OpcObservation]
    rejected_running_items: List[str]


def discover_shaped_from_tag_lists(
    tags_by_server: Mapping[str, Sequence[str]],
    type_members: Mapping[str, Iterable[str]],
    *,
    last_types_by_tag: Optional[Mapping[str, str]] = None,
    gate_n: int = SHAPE_GATE_FLOOR,
    gate_ratio: float = SHAPE_GATE_RATIO,
    clear_margin: int = CLEAR_MARGIN,
) -> ShapedDiscoverResult:
    """Pure shaped discover from browsed OPC tag lists (no invent scorer)."""
    last_types_by_tag = dict(last_types_by_tag or {})
    type_sets: Dict[str, Set[str]] = {
        name: member_short_set(members) for name, members in type_members.items()
    }
    type_gates = _gates_for_types(type_sets, ratio=gate_ratio, floor=gate_n)
    # Prefer one observation per TAG (best shape score, then shorter path).
    best: Dict[str, Tuple[int, OpcObservation]] = {}
    rejected: List[str] = []

    for server, tags in tags_by_server.items():
        tag_list = list(tags or [])
        for item in sorted(t for t in tag_list if str(t).endswith(".Running")):
            parsed = parse_shaped_running_item(item)
            if parsed is None:
                rejected.append(item)
                continue
            _branch, device_tag, prefix = parsed
            members = members_under_prefix(tag_list, prefix)
            scores = {
                type_name: score_structure_match(members, members_set)
                for type_name, members_set in type_sets.items()
            }
            if not passes_shape_gate(scores, type_gates=type_gates, gate_n=gate_n):
                rejected.append(item)
                continue
            results_type = resolve_opc_only_type(
                scores,
                last_type=last_types_by_tag.get(device_tag, ""),
                type_gates=type_gates,
                gate_n=gate_n,
                clear_margin=clear_margin,
            )
            shape_score = max(scores.values()) if scores else 0
            obs = OpcObservation(
                device_tag=device_tag,
                opc_server=server,
                opc_item_prefix=prefix,
                results_type=results_type,
                running_item=f"{prefix}.Running",
            )
            current = best.get(device_tag)
            if current is None:
                best[device_tag] = (shape_score, obs)
            else:
                cur_score, cur_obs = current
                if shape_score > cur_score or (
                    shape_score == cur_score
                    and len(prefix) < len(cur_obs.opc_item_prefix)
                ):
                    best[device_tag] = (shape_score, obs)

    observations = [best[tag][1] for tag in sorted(best.keys())]
    return ShapedDiscoverResult(observations=observations, rejected_running_items=rejected)


def type_members_from_structures(structures: Mapping[str, object]) -> Dict[str, Set[str]]:
    """Build type→member set from ResultsStructure-like objects or ResultType."""
    out: Dict[str, Set[str]] = {}
    for name, structure in (structures or {}).items():
        if structure is None:
            continue
        if hasattr(structure, "member_short_names"):
            members = list(structure.member_short_names())
        elif hasattr(structure, "members"):
            raw = structure.members
            members = []
            for m in raw:
                if isinstance(m, str):
                    members.append(m)
                else:
                    members.append(getattr(m, "name", str(m)))
        else:
            continue
        out[str(name)] = member_short_set(members)
    return out
