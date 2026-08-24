#!/usr/bin/env python3
"""Generate HIMA-Prooftest-Function-Catalog.md — per-class method reference."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT.parent.parent / "HIMA-Prooftest-Function-Catalog.md"

PYTHON_GLOBS = [
    "main.py",
    "Tool Steps/*.py",
    "Graphic Interface/app.py",
    "Annex codes/layers/**/*.py",
    "Annex codes/prooftest/__init__.py",
    "Annex codes/Database/*.py",
    "Annex codes/API connexion/*.py",
    "Annex codes/OPC/*.py",
    "Annex codes/PDF generation/*.py",
    "Annex codes/Plugin/*.py",
    "Annex codes/Stop service/*.py",
]

SKIP_PYTHON = {"Annex codes/layers/fakes.py"}

JS_FILES = ["Graphic Interface/static/app.js"]

LAYER_HINTS: list[tuple[str, str]] = [
    ("Graphic Interface/static/", "Presentation — View (JavaScript)"),
    ("Graphic Interface/", "Presentation — View wrapper"),
    ("layers/presentation/", "Presentation — Controller"),
    ("layers/application/", "Application — Service"),
    ("layers/domain/", "Domain — Model logic"),
    ("layers/adapters.py", "Adapters"),
    ("layers/ports.py", "Ports (interfaces)"),
    ("Tool Steps/service.py", "Host — Engine runtime"),
    ("Tool Steps/step05", "Host — ProoftestMonitor"),
    ("Tool Steps/step07", "Host — Sync triggers"),
    ("Tool Steps/", "Infrastructure — Tool Steps"),
    ("Annex codes/OPC/", "Adapter — OPC"),
    ("Annex codes/API connexion/", "Adapter — SILworX API"),
    ("Annex codes/Plugin/", "Adapter — Plugin WebSocket"),
    ("Annex codes/Database/", "Adapter — Database"),
    ("Annex codes/PDF generation/", "Adapter — Reports"),
    ("Annex codes/Stop service/", "Infrastructure — Shutdown"),
    ("main.py", "Entry point"),
]

SKIP_SELF = frozenset({"self", "cls"})


@dataclass
class MethodDoc:
    name: str
    signature: str
    lineno: int
    does: str
    needs: list[str]
    calls: list[str]
    returns: str


@dataclass
class ClassDoc:
    name: str
    summary: str
    lineno: int
    bases: str
    methods: list[MethodDoc] = field(default_factory=list)


@dataclass
class ModuleDoc:
    rel_path: str
    layer: str
    summary: str
    module_functions: list[MethodDoc] = field(default_factory=list)
    classes: list[ClassDoc] = field(default_factory=list)


def layer_for(rel: str) -> str:
    rel = rel.replace("\\", "/")
    for prefix, label in LAYER_HINTS:
        if prefix in rel:
            return label
    return "Runtime"


def docstring_text(node: ast.AST) -> str:
    raw = ast.get_docstring(node)
    if not raw:
        return ""
    return raw.strip()


def format_args(args: ast.arguments, *, include_self: bool = False) -> str:
    parts: list[str] = []
    all_args = list(args.posonlyargs) + list(args.args)
    defaults_offset = len(all_args) - len(args.defaults)
    for i, arg in enumerate(all_args):
        if arg.arg in SKIP_SELF and not include_self:
            continue
        name = arg.arg
        if arg.annotation:
            try:
                name += f": {ast.unparse(arg.annotation)}"
            except Exception:
                pass
        default_idx = i - defaults_offset
        if default_idx >= 0:
            try:
                name += f" = {ast.unparse(args.defaults[default_idx])}"
            except Exception:
                name += " = …"
        parts.append(name)
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    for i, arg in enumerate(args.kwonlyargs):
        name = arg.arg
        if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
            try:
                name += f" = {ast.unparse(args.kw_defaults[i])}"
            except Exception:
                name += " = …"
        parts.append(name)
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return ", ".join(parts)


def format_call(func: ast.expr) -> str | None:
    try:
        if isinstance(func, ast.Attribute):
            return ast.unparse(func)
        if isinstance(func, ast.Name):
            return func.id
    except Exception:
        pass
    return None


class MethodAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.self_attrs: set[str] = set()
        self._seen: set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        label = format_call(node.func)
        if label and label not in self._seen:
            self._seen.add(label)
            self.calls.append(label)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == "self":
            self.self_attrs.add(node.attr)
        self.generic_visit(node)


def return_description(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    if node.returns:
        try:
            return ast.unparse(node.returns)
        except Exception:
            return "*(annotated)*"
    for sub in ast.walk(node):
        if isinstance(sub, ast.Return):
            if sub.value is None:
                return "`None`"
            try:
                val = ast.unparse(sub.value)
                if len(val) > 80:
                    val = val[:77] + "…"
                return f"`{val}` (inferred)"
            except Exception:
                return "*(value)*"
    return "`None` (implicit)"


def infer_does(name: str, calls: list[str], self_attrs: set[str]) -> str:
    if name == "__init__":
        return "Construct instance and wire dependencies."
    hints: list[str] = []
    if name.startswith("_") and not name.startswith("__"):
        hints.append("Internal helper.")
    if "raise_alarm" in " ".join(calls):
        hints.append("May raise an alarm on failure.")
    if "refresh" in name.lower() or any("refresh" in c for c in calls):
        hints.append("Triggers or participates in catalog refresh.")
    if not hints:
        return "*(no docstring — read source)*"
    return " ".join(hints)


def analyze_method(node: ast.FunctionDef | ast.AsyncFunctionDef, class_name: str | None) -> MethodDoc:
    doc = docstring_text(node)
    does = doc if doc else infer_does(node.name, [], set())
    # first paragraph only for Does if long
    if doc and "\n\n" in doc:
        does = doc.split("\n\n")[0].replace("\n", " ")

    analyzer = MethodAnalyzer()
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        analyzer.visit(child)

    needs: list[str] = []
    params = format_args(node.args)
    if params:
        needs.append(f"Parameters: `{params}`")
    if class_name and analyzer.self_attrs:
        attrs = ", ".join(f"`self.{a}`" for a in sorted(analyzer.self_attrs))
        needs.append(f"Uses instance: {attrs}")
    if not needs:
        needs.append("No parameters beyond `self`/`cls`.")

    calls = analyzer.calls[:25]
    if len(analyzer.calls) > 25:
        calls.append(f"… +{len(analyzer.calls) - 25} more")

    sig_name = node.name
    sig = f"{sig_name}({format_args(node.args, include_self=True)})"
    ret = return_description(node)

    return MethodDoc(
        name=node.name,
        signature=sig,
        lineno=node.lineno,
        does=does,
        needs=needs,
        calls=calls if calls else ["*(no direct calls detected)*"],
        returns=ret,
    )


def parse_python(path: Path) -> ModuleDoc:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    text = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text, filename=str(path))
    mod = ModuleDoc(rel_path=rel, layer=layer_for(rel), summary=docstring_text(tree) or "*(no module docstring)*")

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            mod.module_functions.append(analyze_method(node, None))
        elif isinstance(node, ast.ClassDef):
            bases = ", ".join(ast.unparse(b) for b in node.bases) if node.bases else "—"
            cls = ClassDoc(
                name=node.name,
                summary=docstring_text(node) or "*(no class docstring)*",
                lineno=node.lineno,
                bases=bases,
            )
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cls.methods.append(analyze_method(item, node.name))
            cls.methods.sort(key=lambda m: m.lineno)
            mod.classes.append(cls)

    mod.module_functions.sort(key=lambda m: m.lineno)
    mod.classes.sort(key=lambda c: c.lineno)
    return mod


JS_FUNC_START = re.compile(r"^(?:async\s+)?function\s+(\w+)\s*(\([^)]*\))")


def extract_js_function_body(lines: list[str], start_idx: int) -> tuple[str, int]:
    """Return body text from function start line; end_idx is last line of function."""
    depth = 0
    started = False
    body_lines: list[str] = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        for ch in line:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}":
                depth -= 1
        if started:
            body_lines.append(line)
        if started and depth == 0:
            return "\n".join(body_lines), i
    return "\n".join(body_lines), len(lines) - 1


def parse_js(path: Path) -> ModuleDoc:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    mod = ModuleDoc(
        rel_path=rel,
        layer=layer_for(rel),
        summary="Browser UI module — all functions live in global scope (no ES6 class). Documented as one virtual module.",
    )

    pseudo_methods: list[MethodDoc] = []
    i = 0
    while i < len(lines):
        m = JS_FUNC_START.match(lines[i].strip())
        if m:
            name, params = m.group(1), m.group(2)
            comment = "*(no comment)*"
            for j in range(i - 1, max(-1, i - 8), -1):
                prev = lines[j].strip()
                if prev.startswith("//"):
                    comment = prev.lstrip("/ ").strip()
                    break
                if prev and not prev.endswith("{") and not prev.endswith(","):
                    break
            body, end_i = extract_js_function_body(lines, i)
            calls: list[str] = []
            for pat in [
                r"fetchJson\s*\(\s*['\"]([^'\"]+)['\"]",
                r"fetch\s*\(\s*['\"]([^'\"]+)['\"]",
                r"\b(showPage|renderHealth|loadDevices|pollStatus|fetchJson)\s*\(",
            ]:
                for hit in re.findall(pat, body):
                    label = hit if isinstance(hit, str) else hit
                    if label not in calls:
                        calls.append(label if label.startswith("/") else f"{label}()")
            if "addEventListener" in body:
                calls.append("addEventListener")
            pseudo_methods.append(
                MethodDoc(
                    name=name,
                    signature=f"function {name}{params}",
                    lineno=i + 1,
                    does=comment,
                    needs=[f"Parameters: `{params.strip('()') or 'none'}`"] ,
                    calls=calls if calls else ["*(DOM / local state only)*"],
                    returns="`undefined` or `Promise` (async functions)",
                )
            )
            i = end_i + 1
            continue
        i += 1

    mod.classes.append(
        ClassDoc(
            name="app.js (global functions)",
            summary="Single-page UI: navigation, polling, health tiles, devices, reports, service buttons.",
            lineno=1,
            bases="—",
            methods=pseudo_methods,
        )
    )
    return mod


def collect_python_modules() -> list[Path]:
    paths: set[Path] = set()
    for pattern in PYTHON_GLOBS:
        for p in ROOT.glob(pattern):
            if p.is_file() and p.suffix == ".py":
                rel = str(p.relative_to(ROOT)).replace("\\", "/")
                if rel not in SKIP_PYTHON:
                    paths.add(p)
    return sorted(paths, key=lambda p: str(p).lower())


def render_method(m: MethodDoc) -> list[str]:
    lines = [
        f"##### `{m.signature}` · line {m.lineno}",
        "",
        f"**Does:** {m.does}",
        "",
        "**Needs:**",
    ]
    for n in m.needs:
        lines.append(f"- {n}")
    lines.extend(["", "**Calls:**"])
    for c in m.calls:
        lines.append(f"- `{c}`")
    lines.extend(["", f"**Returns:** {m.returns}", ""])
    return lines


def render_class(cls: ClassDoc) -> list[str]:
    lines = [
        f"#### Class `{cls.name}` · line {cls.lineno}",
        "",
        f"**Inherits:** `{cls.bases}`",
        "",
        f"**Purpose:** {cls.summary}",
        "",
    ]
    if not cls.methods:
        lines.extend(["*(no methods)*", ""])
        return lines
    for m in cls.methods:
        lines.extend(render_method(m))
    return lines


def render_module(mod: ModuleDoc) -> list[str]:
    lines = [
        f"### File `{mod.rel_path}`",
        "",
        f"**Layer:** {mod.layer}",
        "",
        f"**Module purpose:** {mod.summary}",
        "",
    ]
    if mod.module_functions:
        lines.extend(["#### Module-level functions *(no class)*", ""])
        for m in mod.module_functions:
            lines.extend(render_method(m))
    for cls in mod.classes:
        lines.extend(render_class(cls))
    if not mod.module_functions and not mod.classes:
        lines.append("*(empty module)*")
        lines.append("")
    return lines


def main() -> None:
    modules: list[ModuleDoc] = []
    for path in collect_python_modules():
        try:
            modules.append(parse_python(path))
        except SyntaxError as exc:
            modules.append(
                ModuleDoc(
                    rel_path=str(path.relative_to(ROOT)).replace("\\", "/"),
                    layer=layer_for(str(path.relative_to(ROOT))),
                    summary=f"Parse error: {exc}",
                )
            )
    for rel in JS_FILES:
        p = ROOT / rel
        if p.is_file():
            modules.append(parse_js(p))

    by_layer: dict[str, list[ModuleDoc]] = {}
    for mod in modules:
        by_layer.setdefault(mod.layer, []).append(mod)

    layer_order = [
        "Entry point",
        "Presentation — View wrapper",
        "Presentation — View (JavaScript)",
        "Presentation — Controller",
        "Application — Service",
        "Domain — Model logic",
        "Ports (interfaces)",
        "Adapters",
        "Host — Engine runtime",
        "Host — ProoftestMonitor",
        "Host — Sync triggers",
        "Infrastructure — Tool Steps",
        "Adapter — OPC",
        "Adapter — SILworX API",
        "Adapter — Plugin WebSocket",
        "Adapter — Database",
        "Adapter — Reports",
        "Infrastructure — Shutdown",
        "Runtime",
    ]

    n_methods = sum(
        len(m.module_functions) + sum(len(c.methods) for c in m.classes) for m in modules
    )

    out: list[str] = [
        "# HIMA Automated Prooftest — Class & function reference",
        "",
        "| Field | Value |",
        "|-------|--------|",
        f"| **Generated** | {date.today().isoformat()} |",
        "| **Format** | Grouped by **class**; each method: Does · Needs · Calls · Returns |",
        "| **Use-case guide** | [HIMA-Prooftest-Layer-Functions.md](./HIMA-Prooftest-Layer-Functions.md) |",
        "| **Regenerate** | `python Dev tools/generate_function_catalog.py` |",
        f"| **Classes / modules** | {sum(len(m.classes) for m in modules)} classes in {len(modules)} files |",
        f"| **Functions / methods** | {n_methods} |",
        "",
        "Each entry uses:",
        "",
        "- **Does** — what the function accomplishes (from docstring or inference)",
        "- **Needs** — parameters and `self.*` dependencies",
        "- **Calls** — other functions/methods invoked (static analysis)",
        "- **Returns** — return type or inferred return value",
        "",
        "---",
        "",
    ]

    for layer in layer_order:
        if layer not in by_layer:
            continue
        out.append(f"## {layer}")
        out.append("")
        for mod in sorted(by_layer[layer], key=lambda m: m.rel_path.lower()):
            out.extend(render_module(mod))
        out.append("---")
        out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {OUT} ({n_methods} methods)")


if __name__ == "__main__":
    main()
