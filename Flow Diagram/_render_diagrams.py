#!/usr/bin/env python3
"""Render Mermaid blocks from Flow Diagram markdown files to PNG and SVG (local Playwright)."""

from __future__ import annotations

import re
import time
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
MERMAID_JS = FOLDER / "mermaid.min.js"


def extract_mermaid(md_path: Path) -> str | None:
    text = md_path.read_text(encoding="utf-8")
    match = re.search(r"```mermaid\s*\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None


def build_html() -> str:
    mermaid_src = MERMAID_JS.read_text(encoding="utf-8")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <script>{mermaid_src}</script>
  <style>
    body {{ margin: 24px; background: #fff; }}
    #out svg {{ max-width: 100%; height: auto; }}
  </style>
</head>
<body>
  <div id="out"></div>
  <script>
    mermaid.initialize({{ startOnLoad: false, theme: "default", securityLevel: "loose" }});
    window.renderDiagram = async function(code) {{
      const id = "mmd-" + Math.random().toString(36).slice(2);
      const result = await mermaid.render(id, code);
      document.getElementById("out").innerHTML = result.svg;
      return result.svg;
    }};
  </script>
</body>
</html>
"""


def main() -> int:
    from playwright.sync_api import sync_playwright

    if not MERMAID_JS.is_file():
        print(f"Missing {MERMAID_JS.name} — run download first.")
        return 1

    md_files = sorted(FOLDER.glob("0*.md"))
    if not md_files:
        print("No diagram markdown files found.")
        return 1

    ok = 0
    html = build_html()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1800, "height": 1400})
        page.set_content(html, wait_until="load", timeout=120000)
        page.wait_for_function("typeof mermaid !== 'undefined'", timeout=30000)

        for md_path in md_files:
            diagram = extract_mermaid(md_path)
            if not diagram:
                print(f"SKIP {md_path.name}: no mermaid block")
                continue
            stem = md_path.stem
            png_path = FOLDER / f"{stem}.png"
            svg_path = FOLDER / f"{stem}.svg"
            try:
                svg = page.evaluate("code => window.renderDiagram(code)", diagram)
                page.wait_for_selector("#out svg", timeout=30000)
                time.sleep(0.3)
                svg_path.write_text(svg, encoding="utf-8")
                page.locator("#out svg").screenshot(path=str(png_path))
                print(f"OK  {stem}.png + {stem}.svg")
                ok += 1
            except Exception as exc:
                print(f"FAIL {stem}: {exc}")

        browser.close()

    print(f"Rendered {ok}/{len(md_files)} diagram(s)")
    return 0 if ok == len(md_files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
