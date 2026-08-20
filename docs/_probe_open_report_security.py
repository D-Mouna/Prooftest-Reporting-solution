"""Minimal security probes for QueryService path traversal (no live HTTP)."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Codes" / "HIMA-Prooftest-Solution-Current" / "Annex codes"))

from layers.application.query import QueryService  # noqa: E402
from layers.fakes import FakeOpc, FakeReports, FakeSilworx, FakeStore  # noqa: E402


class _Alarm:
    def __init__(self) -> None:
        self.raised = []

    def raise_alarm(self, *a, **k):
        self.raised.append((a, k))

    def last_error(self):
        return None


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="sec_open_report_"))
    root = tmp / "reports"
    root.mkdir()
    outside = tmp / "secret.txt"
    outside.write_text("x", encoding="utf-8")
    inside = root / "ok.html"
    inside.write_text("ok", encoding="utf-8")

    q = QueryService(FakeStore(), FakeReports(), _Alarm())
    code, _ = q.open_report(str(outside), [root])
    print(f"path_traversal_outside -> {code} (expect 403)")
    code2, path2 = q.open_report(str(inside), [root])
    print(f"path_inside_root -> {code2} path={path2 is not None} (expect 200)")
    # traversal-style relative
    evil = root / ".." / "secret.txt"
    code3, _ = q.open_report(str(evil), [root])
    print(f"path_dotdot_resolved -> {code3} (expect 403)")
    failed = 0
    if code != 403:
        failed += 1
    if code2 != 200:
        failed += 1
    if code3 != 403:
        failed += 1
    print("PASS" if failed == 0 else f"FAIL ({failed})")
    return failed


if __name__ == "__main__":
    raise SystemExit(main())
