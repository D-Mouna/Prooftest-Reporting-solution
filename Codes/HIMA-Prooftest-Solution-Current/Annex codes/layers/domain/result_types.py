"""Results Structure type catalogue. Loading types does not create devices."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ResultType:
    name: str
    members: tuple[str, ...] = ()
    source_path: str = ""


@dataclass
class ResultTypeCatalog:
    types: Dict[str, ResultType] = field(default_factory=dict)
    skipped_files: List[str] = field(default_factory=list)

    def names(self) -> set[str]:
        return set(self.types.keys())

    def get(self, name: str) -> Optional[ResultType]:
        return self.types.get(name)

    def matches_global(self, data_type: str) -> bool:
        return data_type in self.types

    @classmethod
    def from_csv_folder(cls, folder: Path) -> "ResultTypeCatalog":
        """Minimal CSV loader for unit tests (name from stem; first column = member)."""
        catalog = cls()
        if not folder.is_dir():
            return catalog
        for path in sorted(folder.glob("*.csv")):
            try:
                text = path.read_text(encoding="utf-8-sig")
            except OSError:
                catalog.skipped_files.append(str(path))
                continue
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            if not lines:
                catalog.skipped_files.append(str(path))
                continue
            members: list[str] = []
            for line in lines[1:]:
                cell = line.split(",")[0].strip()
                if cell:
                    members.append(cell)
            stem = path.stem
            name = stem.replace("-", "/") if "FTL" in stem or "Promass" in stem else stem
            catalog.types[stem] = ResultType(name=stem, members=tuple(members), source_path=str(path))
            if name != stem:
                catalog.types[name] = catalog.types[stem]
        return catalog
