"""Shaped OPC-only discovery — CSV as FILTER / clear-type only, never invent-as-identity.

Rules (unified mode):
- Branches only: ``OTS ProofTest``, ``OPC ProofTest``
- Candidate = ``{branch}.{TAG}.Running`` where TAG has no ``.``
- Shape gate: ≥ N members shared with ≥1 known Results type (N includes Running)
- Type: last known SQL type if set; else unique clear best
  (best ≥ N AND best − second ≥ CLEAR_MARGIN); else unknown (empty string)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from layers.domain.merger import OpcObservation

OTS_BRANCH = "OTS ProofTest"
OPC_BRANCH = "OPC ProofTest"
PROOFTEST_BRANCHES: tuple[str, ...] = (OTS_BRANCH, OPC_BRANCH)

SHAPE_GATE_N = 3
CLEAR_MARGIN = 2


def normalize_member(name: str) -> str:
    return str(name or "").replace(" ", "").lower().split(".")[-1]


def member_short_set(members: Iterable[str]) -> Set[str]:
    return {normalize_member(m) for m in members if normalize_member(m)}


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
    Accept only ``{branch}.{TAG}.Running`` with TAG a single segment (no dots).

    Returns ``(branch, device_tag, prefix)`` or None.
    Rejects ``SomeFlag.Running``, ``branch.a.b.Running``, etc.
    """
    text = str(item or "").strip()
    if not text.endswith(".Running"):
        return None
    prefix = text[: -len(".Running")]
    for branch in PROOFTEST_BRANCHES:
        head = branch + "."
        if not prefix.startswith(head):
            continue
        remainder = prefix[len(head) :]
        if not remainder or "." in remainder:
            return None
        return branch, remainder, prefix
    return None


def members_under_prefix(tags: Sequence[str], prefix: str) -> Set[str]:
    prefix_dot = prefix + "."
    members: Set[str] = set()
    for tag in tags:
        if tag.startswith(prefix_dot):
            top = tag[len(prefix_dot) :].split(".")[0]
            if top:
                members.add(top)
    return members


def resolve_opc_only_type(
    scores: Mapping[str, int],
    *,
    last_type: str = "",
    gate_n: int = SHAPE_GATE_N,
    clear_margin: int = CLEAR_MARGIN,
) -> str:
    """
    Prefer last SQL type when present.
    Else unique clear winner: best ≥ gate_n and (best − second) ≥ clear_margin.
    Else unknown ("").
    """
    last = (last_type or "").strip()
    if last:
        return last
    ranked = sorted(
        ((score, name) for name, score in scores.items() if score >= gate_n),
        key=lambda item: (-item[0], item[1]),
    )
    if not ranked:
        return ""
    best_score, best_name = ranked[0]
    second = ranked[1][0] if len(ranked) > 1 else 0
    if best_score - second >= clear_margin:
        return best_name
    return ""


def passes_shape_gate(scores: Mapping[str, int], *, gate_n: int = SHAPE_GATE_N) -> bool:
    return any(score >= gate_n for score in scores.values())


@dataclass(frozen=True)
class ShapedDiscoverResult:
    observations: List[OpcObservation]
    rejected_running_items: List[str]


def discover_shaped_from_tag_lists(
    tags_by_server: Mapping[str, Sequence[str]],
    type_members: Mapping[str, Iterable[str]],
    *,
    last_types_by_tag: Optional[Mapping[str, str]] = None,
    gate_n: int = SHAPE_GATE_N,
    clear_margin: int = CLEAR_MARGIN,
) -> ShapedDiscoverResult:
    """Pure shaped discover from browsed OPC tag lists (no invent scorer)."""
    last_types_by_tag = dict(last_types_by_tag or {})
    type_sets: Dict[str, Set[str]] = {
        name: member_short_set(members) for name, members in type_members.items()
    }
    # Prefer one observation per TAG (best shape score, OTS before OPC).
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
            if not passes_shape_gate(scores, gate_n=gate_n):
                rejected.append(item)
                continue
            results_type = resolve_opc_only_type(
                scores,
                last_type=last_types_by_tag.get(device_tag, ""),
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
            prefer_ots = prefix.startswith(OTS_BRANCH)
            if current is None:
                best[device_tag] = (shape_score, obs)
            else:
                cur_score, cur_obs = current
                cur_ots = cur_obs.opc_item_prefix.startswith(OTS_BRANCH)
                if shape_score > cur_score or (shape_score == cur_score and prefer_ots and not cur_ots):
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
