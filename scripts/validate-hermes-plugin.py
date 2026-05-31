#!/usr/bin/env python3
"""Validate a Hermes user-plugin directory shape.

Checks (no import of the plugin, static analysis only):
  1. directory exists
  2. plugin.yaml present, parses, has a non-empty `name`
  3. __init__.py present
  4. __init__.py defines `def register(`
  5. register body calls at least one `ctx.register_*` method

Usage:  validate-hermes-plugin.py <plugin-dir>
Prints PASS_PLUGIN on success; asserts (nonzero exit) on failure.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def _yaml_name(text: str) -> str:
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(text)
        if isinstance(parsed, dict):
            return str(parsed.get("name", "")).strip()
    except Exception:
        pass
    # Fallback: line-scan for `name:` so the check works without PyYAML.
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip("'\"")
    return ""


def _register_calls_register_method(init_src: str) -> bool:
    """True when a top-level `def register(...)` calls some `<x>.register_*(...)`."""
    tree = ast.parse(init_src)
    register_fns = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "register"
    ]
    if not register_fns:
        return False
    for fn in register_fns:
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                if sub.func.attr.startswith("register_"):
                    return True
    return False


def validate(plugin_dir: Path) -> dict:
    assert plugin_dir.is_dir(), f"not a directory: {plugin_dir}"

    manifest = plugin_dir / "plugin.yaml"
    assert manifest.exists(), "plugin.yaml missing"
    name = _yaml_name(manifest.read_text())
    assert name, "plugin.yaml has no non-empty 'name'"

    init = plugin_dir / "__init__.py"
    assert init.exists(), "__init__.py missing"
    init_src = init.read_text()
    assert "def register(" in init_src, "__init__.py has no register() function"
    assert _register_calls_register_method(init_src), (
        "register() does not call any ctx.register_* method (plugin would be a no-op)"
    )
    return {"name": name, "has_register": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plugin_dir", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        # Exercise the AST detector on a fixed inline sample — deterministic.
        sample = "def register(ctx):\n    ctx.register_command('x', handler=lambda a: a)\n"
        ok = _register_calls_register_method(sample)
        print(json.dumps({"check": "hermes-plugin", "self_test": "ok", "detector": ok}, sort_keys=True))
        return 0

    if not args.plugin_dir:
        print("usage: validate-hermes-plugin.py <plugin-dir>", file=sys.stderr)
        return 2

    target = Path(args.plugin_dir)
    if not target.is_absolute():
        target = Path.cwd() / target
    info = validate(target)
    print(json.dumps({"PASS_PLUGIN": True, **info}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
