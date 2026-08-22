from __future__ import annotations

"""Results Structure CSV type catalogue (dynamic).

Every ``*.csv`` under the runtime catalogue
``C:\\HIMA Prooftest Reporting Tool\\Results Structures\\`` defines one
Prooftest Results **type**. The nine shipped files are the baseline; adding a
new CSV registers a new device type (SQL ``ProofTest_*`` table, API/OPC
matching, report folders). The package may keep a seed copy next to the code;
the watched folder is always the station path from ``solution.ini``.

Devices themselves remain SILworX **global variables** whose data type matches
one of these structures — add a CSV only when introducing a **new Results
structure type**.
"""

import csv
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

log = logging.getLogger(__name__)

# Baseline nine: filename → SILworX type name (``/`` where the library uses it).
# New CSVs are discovered from the folder; this map only fixes known aliases.
RESULTS_TYPE_FILES: Dict[str, str] = {
    "X-HART_ABB_FCB400_Results": "X-HART_ABB_FCB400_Results.csv",
    "X-HART_Emerson_3051S_Results": "X-HART_Emerson_3051S_Results.csv",
    "X-HART_E+H_PMx7xB_Results": "X-HART_E+H_PMx7xB_Results.csv",
    "X-HART_E+H_FTL5xB/6x_Results": "X-HART_E+H_FTL5xB-6x_Results.csv",
    "X-HART_E+H_FMR6xB_Results": "X-HART_E+H_FMR6xB_Results.csv",
    "X-HART_E+H_Promass300/500_Results": "X-HART_E+H_Promass300-500_Results.csv",
    "X-HART_SAMSON_Results": "X-HART_SAMSON_Results.csv",
    "X-HART_WIKA_T32_Results": "X-HART_WIKA_T32_Results.csv",
    "X-HART_WIKA_T38_Results": "X-HART_WIKA_T38_Results.csv",
}

_FILENAME_TO_TYPE: Dict[str, str] = {v.lower(): k for k, v in RESULTS_TYPE_FILES.items()}

# Known SILworX CSV typos → canonical member short name (OPC folder spelling).
_MEMBER_SHORT_ALIASES: Dict[str, str] = {
    "Patameters Before Test": "Parameters Before Test",
}


@dataclass
class ResultMember:
    name: str
    data_type: str
    sequence: Optional[int] = None


@dataclass
class ResultsStructure:
    type_name: str
    members: List[ResultMember] = field(default_factory=list)
    csv_path: Optional[Path] = None

    @property
    def sql_table_name(self) -> str:
        return structure_to_sql_table(self.type_name)

    def member_short_names(self) -> List[str]:
        prefix = self.type_name + "."
        out: List[str] = []
        for m in self.members:
            if m.name.startswith(prefix):
                out.append(m.name[len(prefix) :])
            elif "." in m.name:
                out.append(m.name.split(".", 1)[1])
            else:
                out.append(m.name)
        return out

    def has_running(self) -> bool:
        return any(m.name.endswith(".Running") or m.name.endswith(" Running") for m in self.members)


def structure_to_sql_table(type_name: str) -> str:
    name = type_name.replace("X-HART_", "ProofTest_")
    name = name.replace("/", "_")
    return name


def _parse_int(value: str) -> Optional[int]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def type_name_from_csv_path(csv_path: Path) -> str:
    """Resolve SILworX Results type name for a CSV file."""
    known = _FILENAME_TO_TYPE.get(csv_path.name.lower())
    if known:
        return known
    try:
        with csv_path.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                name = (row.get("Name") or "").strip()
                if not name:
                    continue
                if "." not in name:
                    return name
                return name.split(".", 1)[0]
    except OSError as exc:
        log.warning("Cannot read Results Structure CSV %s: %s", csv_path, exc)
    return csv_path.stem


def load_structure(csv_path: Path, type_name: str) -> ResultsStructure:
    structure = ResultsStructure(type_name=type_name, csv_path=csv_path)
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = (row.get("Name") or "").strip()
            if not name or name == type_name:
                continue
            dtype = (row.get("Data type") or "").strip()
            structure.members.append(
                ResultMember(name=name, data_type=dtype, sequence=_parse_int(row.get("Sequence Number", "")))
            )
    return structure


def discover_results_csv_files(directory: Path) -> List[Path]:
    """All Results Structure CSV files in the catalogue folder (sorted)."""
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.csv") if p.is_file())


def load_all_structures(directory: Path) -> Dict[str, ResultsStructure]:
    """
    Load every ``*.csv`` under ``directory`` as a Results type.

    New files (beyond the baseline nine) become new device types automatically.
    """
    structures: Dict[str, ResultsStructure] = {}
    for path in discover_results_csv_files(directory):
        try:
            type_name = type_name_from_csv_path(path)
            if type_name in structures:
                log.warning(
                    "Duplicate Results type %s from %s (keeping first: %s)",
                    type_name,
                    path.name,
                    structures[type_name].csv_path,
                )
                continue
            structures[type_name] = load_structure(path, type_name)
            log.debug(
                "Loaded Results structure %s from %s (%s members)",
                type_name,
                path.name,
                len(structures[type_name].members),
            )
        except Exception as exc:
            log.warning("Skipping Results Structure CSV %s: %s", path, exc)
    if not structures and directory.is_dir():
        for type_name, filename in RESULTS_TYPE_FILES.items():
            path = directory / filename
            if path.exists():
                structures[type_name] = load_structure(path, type_name)
    return structures


def list_results_type_names(directory: Path) -> Tuple[str, ...]:
    """Type names currently defined by CSVs in ``directory``."""
    return tuple(load_all_structures(directory).keys())


def silworx_type_to_sql(dtype: str) -> str:
    mapping = {
        "BOOL": "BIT",
        "BYTE": "TINYINT",
        "USINT": "TINYINT",
        "WORD": "INT",
        "UINT": "INT",
        "DWORD": "BIGINT",
        "UDINT": "BIGINT",
        "REAL": "FLOAT",
        "DINT": "INT",
    }
    if dtype in mapping:
        return mapping[dtype]
    if dtype.startswith("X-HART"):
        return "NVARCHAR(MAX)"
    return "NVARCHAR(128)"


def member_to_column(name: str, type_name: str) -> str:
    short = name
    prefix = type_name + "."
    if short.startswith(prefix):
        short = short[len(prefix) :]
    col = re.sub(r"[^A-Za-z0-9]+", "_", short).strip("_")
    if not col:
        col = "Member"
    if col[0].isdigit():
        col = f"M_{col}"
    return col


def annexes_directory(results_structures: Path) -> Path:
    """Folder holding nested SILworX type CSVs (ASCII arrays, Parameters structs)."""
    return Path(results_structures) / "Annexes"


def load_annex_types(annexes_dir: Path) -> Dict[str, ResultsStructure]:
    """Load ``X-HART_ASCII_32``, ``X-HART_*_Parameters``, etc. from ``Annexes/``."""
    structures: Dict[str, ResultsStructure] = {}
    if not annexes_dir.is_dir():
        return structures
    for path in sorted(annexes_dir.glob("*.csv")):
        try:
            type_name = type_name_from_csv_path(path)
            if type_name in structures:
                continue
            structures[type_name] = load_structure(path, type_name)
        except Exception as exc:
            log.warning("Skipping annex type CSV %s: %s", path, exc)
    return structures


_ASCII_LEN_RE = re.compile(r"^X-HART_ASCII_(\d+)$", re.IGNORECASE)


def ascii_array_length(dtype: str, catalog: Optional[Dict[str, ResultsStructure]] = None) -> Optional[int]:
    """
    Character count for ``X-HART_ASCII_N`` (and ``BYTE`` arrays in annex CSVs).

    Prefer the numeric suffix in the type name (``X-HART_ASCII_32`` → 32 cells).
    """
    dtype = (dtype or "").strip()
    match = _ASCII_LEN_RE.match(dtype)
    if match:
        return int(match.group(1))
    if catalog and dtype in catalog:
        for member in catalog[dtype].members:
            short = member.name.split(".")[-1]
            if short.lower() == "array dimension":
                # Annex CSV uses upper range 31 for a 32-byte string (indices 0..31).
                return 32
    return None


def is_ascii_type(dtype: str) -> bool:
    return bool(_ASCII_LEN_RE.match((dtype or "").strip()))


def is_parameters_type(dtype: str, catalog: Optional[Dict[str, ResultsStructure]] = None) -> bool:
    dtype = (dtype or "").strip()
    if dtype.endswith("_Parameters"):
        return True
    return bool(catalog and dtype in catalog and "Parameters" in dtype)


def member_dtype_map(structure: ResultsStructure) -> Dict[str, str]:
    """Map member short name → SILworX data type."""
    prefix = structure.type_name + "."
    out: Dict[str, str] = {}
    for member in structure.members:
        short = member.name[len(prefix) :] if member.name.startswith(prefix) else member.name.split(".")[-1]
        canonical = _MEMBER_SHORT_ALIASES.get(short, short)
        out[short] = member.data_type
        if canonical != short:
            out[canonical] = member.data_type
    return out


def member_column_dtype_map(structure: ResultsStructure) -> Dict[str, str]:
    """Map SQL snapshot column → SILworX ``Data type`` (includes annex nested types)."""
    prefix = structure.type_name + "."
    out: Dict[str, str] = {}
    for member in structure.members:
        short = member.name[len(prefix) :] if member.name.startswith(prefix) else member.name.split(".")[-1]
        canonical = _MEMBER_SHORT_ALIASES.get(short, short)
        col = member_to_column(f"{structure.type_name}.{canonical}", structure.type_name)
        out[col] = member.data_type
        # Legacy typo column from CSV member name (e.g. Patameters_Before_Test).
        if canonical != short:
            out[member_to_column(f"{structure.type_name}.{short}", structure.type_name)] = member.data_type
    return out
