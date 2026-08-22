#!/usr/bin/env python3
"""Unit tests for OPC ASCII / Parameters snapshot expansion."""

from __future__ import annotations

import sys
from pathlib import Path

from _paths import SOLUTION_ROOT, setup_path

setup_path()
sys.path.insert(0, str(SOLUTION_ROOT / "Annex codes"))

from OPC.opc_snapshot import (  # type: ignore
    decode_char_codes,
    enrich_snapshot_from_opc,
    expand_parameters_branch,
)


def test_decode_char_codes() -> None:
    assert decode_char_codes([80, 82, 79, 77, 65, 83, 83, 0, 0]) == "PROMASS"
    assert decode_char_codes([ord(c) for c in "LB100202000"] + [0]) == "LB100202000"


def test_expand_parameters_and_ascii() -> None:
    prefix = "HART_FDB_Test._FIT-Promass 300_500"
    tags = [
        f"{prefix}.Tag.Tag[{i}]" for i in range(8)
    ] + [
        f"{prefix}.Serial Number.Serial Number[{i}]" for i in range(12)
    ] + [
        f"{prefix}.Parameters After Test.Installation direction",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[0]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[1]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[2]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[3]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[4]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[5]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[6]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[7]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[8]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[9]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[10]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[11]",
        f"{prefix}.Parameters After Test.20 mA value.20 mA value[12]",
    ]

    store = {
        **{f"{prefix}.Tag.Tag[{i}]": (ord(c), "Good") for i, c in enumerate("PROMASS")},
        f"{prefix}.Tag.Tag[7]": (0, "Good"),
        **{
            f"{prefix}.Serial Number.Serial Number[{i}]": (ord(c), "Good")
            for i, c in enumerate("LB100202000")
        },
        f"{prefix}.Serial Number.Serial Number[11]": (0, "Good"),
        f"{prefix}.Parameters After Test.Installation direction": (1087, "Good"),
        **{
            f"{prefix}.Parameters After Test.20 mA value.20 mA value[{i}]": (ord(c), "Good")
            for i, c in enumerate("400.000 kg/h")
        },
    }

    def read_values(ids):
        return {i: store.get(i, (None, "Bad")) for i in ids}

    expanded = expand_parameters_branch(tags, prefix, "Parameters After Test", read_values)
    assert expanded.get("Installation_direction") == 1087
    assert expanded.get("value_20_mA") == "400.000 kg/h"

    snapshot, notes = enrich_snapshot_from_opc(
        tags=tags,
        prefix=prefix,
        member_types={
            "Tag": "X-HART_ASCII_32",
            "Serial_Number": "X-HART_ASCII_32",
            "Parameters_After_Test": "X-HART_E+H_Promass300/500_Parameters",
        },
        snapshot={
            "Tag": 80,  # wrongly bound to Tag[0] — must still expand
            "Serial_Number": None,
            "Parameters_After_Test": None,
        },
        notes=[
            "Tag: quality Error",
            "Serial_Number: quality Error",
            "Parameters_After_Test: quality Error",
            "Parameters_Before_Test: quality Error",
            "Long_Tag: quality Error",
        ],
        read_values=read_values,
    )
    assert snapshot["Tag"] == "PROMASS"
    assert snapshot["Serial_Number"] == "LB100202000"
    assert snapshot["Installation_direction"] == 1087
    assert snapshot["value_20_mA"] == "400.000 kg/h"
    assert notes == [] or notes == ["Long_Tag: quality Error"]
    assert not any(n.startswith("Tag:") for n in notes)
    assert not any(n.startswith("Serial_Number:") for n in notes)
    assert not any(n.startswith("Parameters_") for n in notes)


def test_annex_catalog_promass_parameters() -> None:
    """Parameters members use annex CSV data types (ASCII_14/20/32, UINT, …)."""
    from prooftest.results_csv import annexes_directory, load_annex_types

    annex_dir = annexes_directory(SOLUTION_ROOT / "Results Structures")
    catalog = load_annex_types(annex_dir)
    assert "X-HART_E+H_Promass300/500_Parameters" in catalog
    assert "X-HART_ASCII_32" in catalog

    prefix = "HART_FDB_Test._FIT-Promass 300_500"
    tags = [
        f"{prefix}.Parameters After Test.Damping.Damping[{i}]"
        for i in range(6)
    ] + [f"{prefix}.Parameters After Test.Installation direction"]

    store = {
        f"{prefix}.Parameters After Test.Installation direction": (1087, "Good"),
        **{
            f"{prefix}.Parameters After Test.Damping.Damping[{i}]": (ord(c), "Good")
            for i, c in enumerate("1.0 s")
        },
    }

    def read_values(ids):
        return {i: store.get(i, (None, "Bad")) for i in ids}

    expanded = expand_parameters_branch(
        tags,
        prefix,
        "Parameters After Test",
        read_values,
        parameters_type="X-HART_E+H_Promass300/500_Parameters",
        type_catalog=catalog,
    )
    assert expanded.get("Installation_direction") == 1087
    assert expanded.get("Damping") == "1.0 s"


def test_template_context_uses_decoded_tag() -> None:
    from prooftest.annex_pdf_generation import build_template_context

    ctx = build_template_context(
        "_FIT-Promass 300_500",
        {
            "Tag": "PROMASS",
            "Serial_Number": "LB100202000",
            "Long_Tag": "Promass",
            "Installation_direction": 1087,
            "Error": True,
            "Actual_Value_1": float("nan"),
        },
    )
    assert ctx["HIMA_system_tag"] == "_FIT-Promass 300_500"
    assert ctx["Device_tag"] == "PROMASS"
    assert ctx["Serial_number"] == "LB100202000"
    assert ctx["Device_tag_long"] == "Promass"
    assert ctx["Installation_direction"] == "1087"
    assert ctx["Actual_Value_1"] == ""


if __name__ == "__main__":
    failed = 0
    for fn in (
        test_decode_char_codes,
        test_expand_parameters_and_ascii,
        test_annex_catalog_promass_parameters,
        test_template_context_uses_decoded_tag,
    ):
        try:
            fn()
            print(f"OK  {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    raise SystemExit(1 if failed else 0)
