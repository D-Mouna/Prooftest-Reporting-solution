"""
Annex — PDF and HTML report generation.

Uses HIMA HTML templates from ``1- HTML Reports Template`` when a layout exists
for the Results type (and SAMSON FST/PST variant); otherwise falls back to a
simple built-in HTML table.
"""

from __future__ import annotations

import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from prooftest.annex_database import TEMPLATE_MAP
from prooftest.config import AppConfig
from prooftest.results_csv import RESULTS_TYPE_FILES, ResultsStructure, member_to_column
from prooftest.step01_setup import results_type_folder_name, sanitize_device_tag_for_path

_PLACEHOLDER_RE = re.compile(r"\$\(([^)]+)\)")

# Results type / layout key → folder under ``report_html_templates`` (contains report.html + img/).
_SAMSON_HTML_FOLDERS: Dict[str, str] = {
    "X-HART_SAMSON_3793_FST": "SAMSON_3793_FST_V1_5",
    "X-HART_SAMSON_3793_PST": "SAMSON_3793_PST_V1_5",
    "X-HART_SAMSON_3730_FST": "SAMSON_3730_3_FST_V1_5",
    "X-HART_SAMSON_3730_PST": "SAMSON_3730_3_PST_V1_5",
}


def _build_html_template_folder_map() -> Dict[str, str]:
    """Align with ``TEMPLATE_MAP`` table names (same as ``1- HTML Reports Template`` folders)."""
    mapping: Dict[str, str] = {}
    for results_type, (_sql_file, table_name) in TEMPLATE_MAP.items():
        if results_type == "X-HART_SAMSON_Results":
            continue
        mapping[results_type] = table_name
    mapping.update(_SAMSON_HTML_FOLDERS)
    return mapping


HTML_TEMPLATE_FOLDER_MAP: Dict[str, str] = _build_html_template_folder_map()

# Snapshot SQL column → template placeholder aliases (report.html uses mixed casing).
_TEMPLATE_ALIASES: Dict[str, str] = {
    "Long_Tag": "Device_tag_long",
    "Start_Timestamp": "Test_starttime",
    "End_Timestamp": "Test_endtime",
    "CRC_Before_Test": "CRC_before_test",
    "CRC_After_Test": "CRC_after_test",
    "Alarm_Selection": "Alarm_selection",
    "Transfer_Function": "Transfer_function",
    "Lower_Range_Value": "Lower_range_value",
    "Upper_Range_Value": "Upper_range_value",
    "Damping_Value": "Damping_value",
    "Heartbeat_Verification_Result": "Heartbeat_verif_result",
    "High_Error_Current": "High_error_current",
    "Low_Error_Current": "Low_error_current",
    "Error_Code": "Error_code",
    "Device_Type": "Device_type_extended",
    "Serial_Number": "Serial_number",
}

# Template placeholders filled from device tag / static report metadata (not OPC snapshot columns).
_OPTIONAL_PLACEHOLDERS = frozenset(
    {
        "Act_User",
        "User_Level",
        "Manufacturer",
        "Param_device_name",
        "Param_device_serial_number",
        "Param_pressure_install_offset",
        "Write_Protect_Code",
        "Device_tag_long",
        "Device_type_extended",
        "Test_starttime",
        "Test_endtime",
        "Heartbeat_verif_result",
    }
)


def _reverse_template_aliases() -> Dict[str, str]:
    rev: Dict[str, str] = {}
    for sql_col, placeholder in _TEMPLATE_ALIASES.items():
        rev[placeholder.lower()] = sql_col
    return rev


def _apply_numeric_test_point_aliases(context: Dict[str, str], snapshot: Dict[str, Any], decimal_places: int) -> None:
    for key, raw in list(snapshot.items()):
        match = re.match(r"Test_Point_(\d+)$", key, re.IGNORECASE)
        if not match:
            continue
        placeholder = f"Test_value_{match.group(1)}"
        if placeholder not in context:
            context[placeholder] = _format_template_scalar(raw, decimal_places)


def _apply_structure_column_variants(context: Dict[str, str], snapshot: Dict[str, Any], decimal_places: int) -> None:
    """Duplicate snapshot values under common placeholder spellings (case variants)."""
    for sql_col, raw in snapshot.items():
        if sql_col.startswith("_"):
            continue
        formatted = (
            _format_udint_timestamp(raw)
            if sql_col in ("Start_Timestamp", "End_Timestamp")
            else _format_template_scalar(raw, decimal_places)
        )
        parts = sql_col.split("_")
        variants = {sql_col}
        if parts:
            variants.add("_".join(p[:1].upper() + p[1:] if p else p for p in parts))
            if len(parts) > 1:
                head = parts[0][:1].upper() + parts[0][1:] if parts[0] else ""
                tail = "_".join(p.lower() for p in parts[1:])
                variants.add(f"{head}_{tail}")
        for name in variants:
            if name not in context:
                context[name] = formatted


def placeholder_to_sql_column(placeholder: str, structure: ResultsStructure) -> Optional[str]:
    """Resolve a report.html placeholder to a snapshot SQL column when possible."""
    rev = _reverse_template_aliases()
    if placeholder.lower() in rev:
        return rev[placeholder.lower()]
    match = re.match(r"Test_value_(\d+)$", placeholder, re.IGNORECASE)
    if match:
        return f"Test_Point_{match.group(1)}"
    for member in structure.member_short_names():
        col = member_to_column(f"{structure.type_name}.{member}", structure.type_name)
        if col.lower() == placeholder.lower():
            return col
        if member.replace(" ", "_").lower() == placeholder.lower():
            return col
    return None


def verify_template_placeholder_mapping(
    templates_root: Path,
    structures: Dict[str, ResultsStructure],
) -> List[str]:
    """
    Return ``folder:placeholder`` entries that cannot be resolved from a full mock snapshot.
    Optional static placeholders (Manufacturer, etc.) are allowed to remain empty.
    """
    failures: List[str] = []
    rev_folders: Dict[str, str] = {}
    for results_type, folder in HTML_TEMPLATE_FOLDER_MAP.items():
        rev_folders.setdefault(folder, results_type)

    for folder in list_expected_html_template_folders():
        template_path = templates_root / folder / "report.html"
        if not template_path.is_file():
            failures.append(f"{folder}:missing report.html")
            continue
        results_type = rev_folders.get(folder, "")
        if "SAMSON" in folder:
            structure = structures.get("X-HART_SAMSON_Results")
        else:
            structure = structures.get(results_type)
        if structure is None:
            continue

        snapshot: Dict[str, Any] = {}
        for member in structure.member_short_names():
            col = member_to_column(f"{structure.type_name}.{member}", structure.type_name)
            if "timestamp" in col.lower() or col.endswith("_Timestamp"):
                snapshot[col] = 1_700_000_000
            elif "error" in col.lower() and col != "Error_Code":
                snapshot[col] = False
            else:
                snapshot[col] = 1
        snapshot.setdefault("Error_Code", 0)

        template_html = template_path.read_text(encoding="utf-8")
        context = build_template_context("GATE13-DEVICE", snapshot, decimal_places=3)
        rendered = render_html_template(template_html, context)
        for placeholder in set(_PLACEHOLDER_RE.findall(template_html)):
            if placeholder in context and context.get(placeholder, "") != "":
                continue
            if placeholder in _OPTIONAL_PLACEHOLDERS:
                continue
            if f"$({placeholder})" in rendered:
                failures.append(f"{folder}:{placeholder}")
    return failures


def resolve_report_template_key(device_tag: str, results_type: str) -> str:
    """
    Return the report layout key for Step 6 (§3.4 SAMSON FST/PST).

    SAMSON devices share one Results type and SQL table; FST vs PST (and 3730 vs
    3793 when detectable from the tag) selects the HTML template folder only.
    """
    tag_upper = device_tag.upper()
    if results_type == "X-HART_SAMSON_Results":
        model = "3730" if "3730" in tag_upper else "3793"
        if tag_upper.endswith("_FST"):
            return f"X-HART_SAMSON_{model}_FST"
        if tag_upper.endswith("_PST"):
            return f"X-HART_SAMSON_{model}_PST"
    return results_type


def auto_template_folder_name(results_type: str) -> str:
    """Folder name for a generated report template (new Results types)."""
    return results_type_folder_name(results_type)


def resolve_html_template_folder(device_tag: str, results_type: str) -> Optional[str]:
    """Folder name under ``report_html_templates``, or None when no template exists."""
    layout_key = resolve_report_template_key(device_tag, results_type)
    mapped = HTML_TEMPLATE_FOLDER_MAP.get(layout_key) or HTML_TEMPLATE_FOLDER_MAP.get(results_type)
    if mapped:
        return mapped
    return auto_template_folder_name(results_type)


def list_expected_html_template_folders() -> List[str]:
    """All HIMA HTML template folders required for the nine Results types."""
    folders: List[str] = []
    for results_type in RESULTS_TYPE_FILES:
        if results_type == "X-HART_SAMSON_Results":
            folders.extend(_SAMSON_HTML_FOLDERS.values())
        elif results_type in HTML_TEMPLATE_FOLDER_MAP:
            folders.append(HTML_TEMPLATE_FOLDER_MAP[results_type])
    return sorted(set(folders))


def verify_html_templates(templates_root: Path) -> List[str]:
    """Return folder names missing ``report.html`` under ``templates_root``."""
    missing: List[str] = []
    for folder in list_expected_html_template_folders():
        if not (templates_root / folder / "report.html").is_file():
            missing.append(folder)
    return missing


def resolve_html_template_path(
    templates_root: Path,
    device_tag: str,
    results_type: str,
) -> Optional[Path]:
    folder = resolve_html_template_folder(device_tag, results_type)
    if not folder:
        return None
    path = templates_root / folder / "report.html"
    if path.is_file():
        return path
    # Fallback: Results-type folder name (auto-generated templates)
    alt = templates_root / auto_template_folder_name(results_type) / "report.html"
    return alt if alt.is_file() else None


def _package_html_templates_seed() -> Path:
    return Path(r"Z:\Project\Report Solution\1- HTML Reports Template")


def seed_known_report_templates(templates_root: Path, seed_root: Path | None = None) -> int:
    """Copy baseline HIMA report template folders into the station templates dir."""
    src = Path(seed_root) if seed_root else _package_html_templates_seed()
    if not src.is_dir():
        return 0
    templates_root.mkdir(parents=True, exist_ok=True)
    copied = 0
    for folder in list_expected_html_template_folders():
        src_dir = src / folder
        dest_dir = templates_root / folder
        if not src_dir.is_dir():
            continue
        if (dest_dir / "report.html").is_file():
            continue
        try:
            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
            copied += 1
        except OSError:
            pass
    return copied


def build_auto_report_template_html(structure: ResultsStructure) -> str:
    """Generate a Proof-test report.html from a Results Structure CSV definition."""
    title = html.escape(structure.type_name.replace("X-HART_", "").replace("_Results", "").replace("_", " "))
    type_esc = html.escape(structure.type_name)
    rows: List[str] = []
    for member in structure.members:
        col = member_to_column(member.name, structure.type_name)
        label = html.escape(col.replace("_", " "))
        rows.append(
            f'  <div class="value">\n'
            f'    <div class="value-left">{label}</div>\n'
            f'    <div class="value-center">$({html.escape(col)})</div>\n'
            f"  </div>\n"
        )
    body_rows = "".join(rows) if rows else "  <p>No members defined in Results Structure CSV.</p>\n"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Proof test report — {type_esc}</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; margin: 1.5rem; color: #222; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }}
  .report {{ font-size: 1.4rem; font-weight: 700; color: #003366; }}
  .device {{ font-size: 1.1rem; color: #444; }}
  .caption {{ margin-top: 1.2rem; margin-bottom: 0.4rem; font-weight: 700; color: #003366; }}
  .value {{ display: grid; grid-template-columns: 16rem 1fr; gap: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid #e5e5e5; }}
  .value-left {{ color: #555; }}
  .value-center {{ font-weight: 600; }}
  hr {{ border: none; border-top: 1px solid #ccc; margin: 1rem 0; }}
</style>
</head>
<body>
<div class="header">
  <div>
    <div class="report">Proof test report</div>
    <div class="device">{title}</div>
  </div>
</div>
<div class="value">
  <div class="value-left">Date/Time (UTC)</div>
  <div class="value-center">$(Start_Timestamp)</div>
</div>
<div class="value">
  <div class="value-left">Device tag</div>
  <div class="value-center">$(Tag)</div>
</div>
<hr/>
<div class="caption">Results — {type_esc}</div>
{body_rows}
</body>
</html>
"""


def ensure_report_template_for_structure(
    templates_root: Path,
    structure: ResultsStructure,
    *,
    seed_root: Path | None = None,
) -> Path:
    """
    Ensure a report.html exists for this Results type.

    Known baseline types: seed from HIMA HTML template pack when missing.
    New types (extra CSVs): auto-generate a Proof-test report template.
    """
    templates_root.mkdir(parents=True, exist_ok=True)
    mapped = HTML_TEMPLATE_FOLDER_MAP.get(structure.type_name)
    if structure.type_name == "X-HART_SAMSON_Results":
        seed_known_report_templates(templates_root, seed_root)
        # Prefer any existing SAMSON template folder
        for folder in _SAMSON_HTML_FOLDERS.values():
            path = templates_root / folder / "report.html"
            if path.is_file():
                return path
        folder = auto_template_folder_name(structure.type_name)
    elif mapped:
        folder = mapped
        dest = templates_root / folder / "report.html"
        if not dest.is_file():
            seed_known_report_templates(templates_root, seed_root)
        if dest.is_file():
            return dest
        folder = auto_template_folder_name(structure.type_name)
    else:
        folder = auto_template_folder_name(structure.type_name)

    dest_dir = templates_root / folder
    dest = dest_dir / "report.html"
    if dest.is_file():
        return dest
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest.write_text(build_auto_report_template_html(structure), encoding="utf-8")
    # Best-effort copy of img assets from a seeded template for CSS/logo
    seed = Path(seed_root) if seed_root else _package_html_templates_seed()
    for candidate in ("WIKA_T32_V1_5", "Cerabar_PMx7xB_V1_5"):
        img = templates_root / candidate / "img"
        if not img.is_dir() and (seed / candidate / "img").is_dir():
            try:
                shutil.copytree(seed / candidate / "img", templates_root / candidate / "img", dirs_exist_ok=True)
            except OSError:
                pass
        img = templates_root / candidate / "img"
        if img.is_dir() and not (dest_dir / "img").exists():
            try:
                shutil.copytree(img, dest_dir / "img")
            except OSError:
                pass
            break
    return dest


def ensure_report_templates_for_structures(
    templates_root: Path,
    structures: Dict[str, ResultsStructure],
    *,
    seed_root: Path | None = None,
) -> List[Path]:
    """Ensure every loaded Results type has a Proof-test report template."""
    seed_known_report_templates(templates_root, seed_root)
    written: List[Path] = []
    for structure in structures.values():
        written.append(
            ensure_report_template_for_structure(templates_root, structure, seed_root=seed_root)
        )
    return written


def device_report_dir(
    output_root: Path,
    device_tag: str,
    results_type: str,
    project: str = "",
) -> Path:
    """``<root>/<Results_Type>/<Project>/<Device_TAG>/`` when project is set; else tag-only (legacy)."""
    folder = output_root / results_type_folder_name(results_type)
    if project:
        folder = folder / sanitize_device_tag_for_path(project)
    return folder / sanitize_device_tag_for_path(device_tag)


def result_line_text(snapshot: Dict[str, Any]) -> str:
    error = snapshot.get("Error") or snapshot.get("error")
    if error in (True, 1, "1", "True", "true"):
        return "Prooftest Unsuccessful"
    hb = snapshot.get("Heartbeat_verif_result") or snapshot.get("Heartbeat Verification Result")
    if hb in (809, "809"):
        return "Successful"
    if hb in (33161, "33161"):
        return "Not done"
    if error in (False, 0, "0", "False", "false", None):
        return "Prooftest Successful"
    return "Prooftest Successful"


def format_value(value: Any, decimal_places: int = 3) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        return f"{value:.{decimal_places}f}"
    return str(value)


def _format_template_scalar(value: Any, decimal_places: int) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        return f"{value:.{decimal_places}f}"
    return str(value)


def _format_udint_timestamp(value: Any) -> str:
    try:
        seconds = int(value)
        return datetime.fromtimestamp(seconds, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, ValueError, OSError, OverflowError):
        return "" if value is None else str(value)


def _error_code_byte_fields(error_code: Any) -> Dict[str, int]:
    try:
        value = int(error_code)
    except (TypeError, ValueError):
        return {}
    return {
        "Error_code_Byte1": (value >> 0) & 0xFF,
        "Error_code_Byte2": (value >> 8) & 0xFF,
        "Error_code_Byte3": (value >> 16) & 0xFF,
        "Error_code_Byte4": (value >> 24) & 0xFF,
    }


def build_template_context(
    device_tag: str,
    snapshot: Dict[str, Any],
    *,
    decimal_places: int = 3,
) -> Dict[str, str]:
    """Map SQL snapshot columns to ``$(placeholder)`` values for report.html."""
    context: Dict[str, str] = {
        "Device_tag": device_tag,
        "Tag": device_tag,
        "HIMA_system_tag": device_tag,
        "Param_device_tag": device_tag,
        "Device_tag_long": device_tag,
    }

    for key, raw in snapshot.items():
        if key.startswith("_"):
            continue
        if key in ("Start_Timestamp", "End_Timestamp"):
            context[key] = _format_udint_timestamp(raw)
        else:
            context[key] = _format_template_scalar(raw, decimal_places)

    for sql_col, placeholder in _TEMPLATE_ALIASES.items():
        if sql_col in context and placeholder not in context:
            if sql_col in ("Start_Timestamp", "End_Timestamp"):
                context[placeholder] = _format_udint_timestamp(snapshot.get(sql_col))
            else:
                context[placeholder] = context[sql_col]

    _apply_numeric_test_point_aliases(context, snapshot, decimal_places)
    _apply_structure_column_variants(context, snapshot, decimal_places)

    error_code = snapshot.get("Error_Code") if "Error_Code" in snapshot else snapshot.get("Error_code")
    if error_code is not None:
        for byte_key, byte_val in _error_code_byte_fields(error_code).items():
            context[byte_key] = str(byte_val)

    if "Error" in snapshot:
        context["Error"] = _format_template_scalar(snapshot["Error"], decimal_places)

    return context


def render_html_template(template_html: str, context: Dict[str, str]) -> str:
    """Replace ``$(Name)`` placeholders; lookup is case-insensitive on ``Name``."""
    lower_map = {key.lower(): value for key, value in context.items()}

    def replacer(match: re.Match[str]) -> str:
        name = match.group(1)
        if name in context:
            return context[name]
        return lower_map.get(name.lower(), "")

    return _PLACEHOLDER_RE.sub(replacer, template_html)


def copy_template_assets(template_dir: Path, output_dir: Path) -> None:
    """Copy ``img/`` (CSS, logos) beside the generated report.html."""
    src_img = template_dir / "img"
    if not src_img.is_dir():
        return
    dest_img = output_dir / "img"
    dest_img.mkdir(parents=True, exist_ok=True)
    for item in src_img.iterdir():
        target = dest_img / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def build_html_report_from_template(
    templates_root: Path,
    device_tag: str,
    results_type: str,
    snapshot: Dict[str, Any],
    *,
    decimal_places: int = 3,
) -> Optional[str]:
    template_path = resolve_html_template_path(templates_root, device_tag, results_type)
    if template_path is None:
        return None
    template_html = template_path.read_text(encoding="utf-8")
    context = build_template_context(device_tag, snapshot, decimal_places=decimal_places)
    return render_html_template(template_html, context)


def build_html_report(
    device_tag: str,
    results_type: str,
    snapshot: Dict[str, Any],
    *,
    quality_notes: Optional[List[str]] = None,
    decimal_places: int = 3,
    template_key: Optional[str] = None,
    templates_root: Optional[Path] = None,
) -> str:
    if templates_root is not None:
        from_template = build_html_report_from_template(
            templates_root,
            device_tag,
            results_type,
            snapshot,
            decimal_places=decimal_places,
        )
        if from_template is not None:
            return from_template

    layout_key = template_key or resolve_report_template_key(device_tag, results_type)
    outcome = result_line_text(snapshot)
    rows = []
    for key, value in sorted(snapshot.items()):
        if key.startswith("_"):
            continue
        rows.append(
            f"<tr><td>{html.escape(str(key))}</td>"
            f"<td>{html.escape(format_value(value, decimal_places))}</td></tr>"
        )
    quality_html = ""
    if quality_notes:
        quality_html = "<p class='warn'>" + html.escape("; ".join(quality_notes)) + "</p>"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Prooftest Report — {html.escape(device_tag)}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 2rem; }}
    h1 {{ color: #003366; }}
    .result {{ font-size: 1.2rem; font-weight: bold; margin: 1rem 0; }}
    .warn {{ color: #a66; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
    th {{ background: #eef3f8; }}
  </style>
</head>
<body>
  <h1>HIMA Automated Prooftest Report</h1>
  <p><strong>Device TAG:</strong> {html.escape(device_tag)}</p>
  <p><strong>Results type:</strong> {html.escape(results_type)}</p>
  <p><strong>Report template:</strong> {html.escape(layout_key)}</p>
  <p><strong>Generated:</strong> {html.escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</p>
  <p class="result">Result: {html.escape(outcome)}</p>
  {quality_html}
  <table>
    <thead><tr><th>Field</th><th>Value</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""


def write_reports(
    config: AppConfig,
    device_tag: str,
    results_type: str,
    snapshot: Dict[str, Any],
    *,
    quality_notes: Optional[List[str]] = None,
    project: str = "",
) -> List[str]:
    output_dir = device_report_dir(config.report_output, device_tag, results_type, project=project)
    mirror_dir = device_report_dir(config.report_mirror, device_tag, results_type, project=project)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        mirror_same = mirror_dir.resolve() == output_dir.resolve()
    except OSError:
        mirror_same = str(mirror_dir) == str(output_dir)
    if not mirror_same:
        mirror_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_tag = sanitize_device_tag_for_path(device_tag)
    base_name = f"{safe_tag}_{stamp}"
    decimal_places = config.report_decimal_places
    templates_root = config.report_html_templates
    template_path = resolve_html_template_path(templates_root, device_tag, results_type)
    written: List[str] = []

    html_body = build_html_report(
        device_tag,
        results_type,
        snapshot,
        quality_notes=quality_notes,
        decimal_places=decimal_places,
        templates_root=templates_root,
    )

    if config.report_format in ("html", "both"):
        html_path = output_dir / f"{base_name}.html"
        html_path.write_text(html_body, encoding="utf-8")
        if template_path is not None:
            copy_template_assets(template_path.parent, output_dir)
            if not mirror_same:
                copy_template_assets(template_path.parent, mirror_dir)
        if not mirror_same:
            shutil.copy2(html_path, mirror_dir / html_path.name)
        written.append(str(html_path))

    if config.report_format in ("pdf", "both"):
        pdf_path = output_dir / f"{base_name}.pdf"
        try:
            from weasyprint import HTML  # type: ignore

            if template_path is not None and (output_dir / f"{base_name}.html").is_file():
                HTML(filename=str(output_dir / f"{base_name}.html"), base_url=str(output_dir)).write_pdf(
                    str(pdf_path)
                )
            else:
                HTML(string=html_body).write_pdf(str(pdf_path))
            if not mirror_same:
                shutil.copy2(pdf_path, mirror_dir / pdf_path.name)
            written.append(str(pdf_path))
        except Exception:
            fallback = output_dir / f"{base_name}.pdf.html"
            fallback.write_text(html_body, encoding="utf-8")
            if not mirror_same:
                shutil.copy2(fallback, mirror_dir / fallback.name)
            written.append(str(fallback))

    return written


def list_reports_for_device(
    output_dir: Path,
    device_tag: str,
    *,
    results_type: Optional[str] = None,
    project: Optional[str] = None,
    device_id: Optional[str] = None,
) -> List[Dict[str, str]]:
    if device_id and not project:
        try:
            from layers.domain.device import DeviceId

            project = DeviceId.from_key(device_id).project or None
        except Exception:
            project = project
    safe = sanitize_device_tag_for_path(device_tag)
    safe_project = sanitize_device_tag_for_path(project) if project else ""
    search_dirs: List[Path] = []

    def _dirs_for_type(type_dir: Path) -> None:
        legacy = type_dir / safe
        if safe_project:
            scoped = type_dir / safe_project / safe
            if scoped.is_dir():
                search_dirs.append(scoped)
                return
        if legacy.is_dir():
            search_dirs.append(legacy)

    if results_type:
        _dirs_for_type(output_dir / results_type_folder_name(results_type))
    elif output_dir.is_dir():
        for type_dir in output_dir.iterdir():
            if type_dir.is_dir():
                _dirs_for_type(type_dir)
    else:
        return []

    files: List[Dict[str, str]] = []
    for folder in search_dirs:
        if not folder.is_dir():
            continue
        for path in folder.glob(f"{safe}*"):
            if path.suffix.lower() in (".html", ".pdf", ".pdf.html"):
                files.append(
                    {
                        "name": path.name,
                        "path": str(path),
                        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                    }
                )
    files.sort(key=lambda x: x["modified"], reverse=True)
    return files
