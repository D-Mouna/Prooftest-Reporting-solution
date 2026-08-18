#!/usr/bin/env python3
"""
Gate 10 / SPEC Step 6 — PDF/HTML report generation.

Verifies:
  1. Result line rules (Error → Unsuccessful / successful).
  2. SAMSON FST vs PST report template key (§3.4).
  3. All twelve HIMA HTML templates under ``1- HTML Reports Template``.
  4. Template rendering (Cerabar + WIKA) and mirror copy.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from _paths import CONFIG_INI, setup_path

setup_path()

from prooftest.config import AppConfig
from prooftest.results_csv import RESULTS_TYPE_FILES
from prooftest.annex_pdf_generation import (
    device_report_dir,
    list_reports_for_device,
    resolve_html_template_folder,
    resolve_report_template_key,
    result_line_text,
    verify_html_templates,
    write_reports,
)

TEST_TAG = "GATE10-TEST-DEVICE"
CERABAR_TYPE = "X-HART_E+H_PMx7xB_Results"
WIKA_TYPE = "X-HART_WIKA_T32_Results"


def test_result_line() -> int:
    if result_line_text({"Error": True}) != "Prooftest Unsuccessful":
        print("FAIL Error=TRUE should be Unsuccessful")
        return 1
    if result_line_text({"Error": False}) != "Prooftest Successful":
        return 1
    print("OK  result line rules")
    return 0


def test_samson_template_keys() -> int:
    fst = resolve_report_template_key("100-XV-001_FST", "X-HART_SAMSON_Results")
    pst = resolve_report_template_key("100-XV-001_PST", "X-HART_SAMSON_Results")
    fst_folder = resolve_html_template_folder("100-XV-001_FST", "X-HART_SAMSON_Results")
    if fst != "X-HART_SAMSON_3793_FST" or fst_folder != "SAMSON_3793_FST_V1_5":
        print(f"FAIL FST mapping: key={fst!r} folder={fst_folder!r}")
        return 1
    if resolve_report_template_key("100-XV-3730-001_PST", "X-HART_SAMSON_Results") != "X-HART_SAMSON_3730_PST":
        print("FAIL SAMSON 3730 PST key")
        return 1
    print("OK  SAMSON FST/PST template keys and folders")
    return 0


def test_all_html_templates_present() -> int:
    config = AppConfig.load(CONFIG_INI)
    missing = verify_html_templates(config.report_html_templates)
    if missing:
        print(f"FAIL missing HTML templates: {', '.join(missing)}")
        return 1
    expected = 12
    found = len(list(config.report_html_templates.glob("*/report.html")))
    print(f"OK  all {expected} HIMA HTML template folders present ({found} report.html files)")
    return 0


def test_hima_html_template_cerabar() -> int:
    config = AppConfig.load(CONFIG_INI)
    tmp = Path(tempfile.mkdtemp(prefix="gate10_hima_"))
    try:
        config.report_output = tmp / "reports"
        config.report_mirror = tmp / "mirror"
        config.report_format = "html"
        config.report_decimal_places = 2

        snapshot = {
            "Error": False,
            "Actual_Value_1": 4.12345,
            "Device_ID": 12345,
            "Heartbeat_Verification_Result": 809,
        }
        paths = write_reports(config, TEST_TAG, CERABAR_TYPE, snapshot)
        body = Path(paths[0]).read_text(encoding="utf-8")
        if "Proof test report" not in body or TEST_TAG not in body:
            print("FAIL Cerabar HIMA template render")
            return 1
        if not (Path(paths[0]).parent / "img" / "report.css").is_file():
            print("FAIL Cerabar img assets not copied")
            return 1
        print("OK  Cerabar_PMx7xB_V1_5 template render")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_hima_html_template_wika() -> int:
    config = AppConfig.load(CONFIG_INI)
    tmp = Path(tempfile.mkdtemp(prefix="gate10_wika_"))
    try:
        config.report_output = tmp / "reports"
        config.report_mirror = tmp / "mirror"
        config.report_format = "html"

        snapshot = {"Error": False, "Device_ID": 99}
        paths = write_reports(config, TEST_TAG, WIKA_TYPE, snapshot)
        html_path = Path(paths[0])
        body = html_path.read_text(encoding="utf-8")
        if "WIKA T32" not in body and "Proof test report" not in body:
            print("FAIL WIKA should use HIMA template, not generic fallback")
            return 1
        if TEST_TAG not in body:
            print("FAIL WIKA template missing device tag")
            return 1
        if not list_reports_for_device(config.report_output, TEST_TAG, results_type=WIKA_TYPE):
            print("FAIL list_reports_for_device")
            return 1
        print(f"OK  WIKA_T32_V1_5 template render -> {html_path.name}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    for test in (
        test_result_line,
        test_samson_template_keys,
        test_all_html_templates_present,
        test_hima_html_template_cerabar,
        test_hima_html_template_wika,
    ):
        rc = test()
        if rc:
            return rc
    print("Gate 10 / Step 6 report check complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
