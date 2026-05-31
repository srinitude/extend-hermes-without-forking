#!/usr/bin/env python3
"""Validate SKILL.md frontmatter.

Prefers the live Hermes validators (`tools.skill_manager_tool`) when importable
— this is the source of truth locally. In a clean CI runner where Hermes is not
installed, it falls back to a standalone check that mirrors the same rules:
starts with `---`, closed frontmatter, `name` matches the parent directory,
`description` present and <= 1024 chars, non-empty body.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_CONTENT_CHARS = 100_000


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def try_load_hermes():
    candidates = [Path.cwd(), Path.home() / ".hermes" / "hermes-agent"]
    for candidate in candidates:
        if (candidate / "tools" / "skill_manager_tool.py").exists():
            sys.path.insert(0, str(candidate))
            try:
                from tools.skill_manager_tool import (  # type: ignore
                    MAX_DESCRIPTION_LENGTH as MDL,
                    _validate_content_size,
                    _validate_frontmatter,
                )
                return MDL, _validate_content_size, _validate_frontmatter
            except Exception:
                return None
    return None


def parse_frontmatter(content: str) -> dict:
    end = content[3:].find("\n---")
    if end < 0:
        raise AssertionError("frontmatter closing marker missing")
    raw = content[3 : end + 3]
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(raw)
    except Exception:
        # Minimal line-scan fallback so PyYAML is not required in CI.
        parsed = {}
        for line in raw.splitlines():
            m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
            if m and m.group(2):
                parsed[m.group(1)] = m.group(2).strip()
    if not isinstance(parsed, dict):
        raise AssertionError("frontmatter is not a mapping")
    return parsed


def standalone_validate(content: str) -> None:
    assert content.startswith("---"), "SKILL.md must start with frontmatter"
    end = re.search(r"\n---\s*\n", content[3:])
    assert end is not None, "frontmatter not closed with '---'"
    assert len(content) <= MAX_SKILL_CONTENT_CHARS, "SKILL.md exceeds content limit"
    body = content[end.end() + 3 :].strip()
    assert body, "SKILL.md must have a body after frontmatter"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "skill-frontmatter", "self_test": "ok"}, sort_keys=True))
        return 0

    root = skill_root()
    content = (root / "SKILL.md").read_text()

    hermes = try_load_hermes()
    if hermes is not None:
        max_description, validate_size, validate_frontmatter = hermes
        fm_error = validate_frontmatter(content)
        size_error = validate_size(content)
        assert fm_error is None, fm_error
        assert size_error is None, size_error
        mode = "hermes"
    else:
        standalone_validate(content)
        max_description = MAX_DESCRIPTION_LENGTH
        mode = "standalone"

    parsed = parse_frontmatter(content)
    assert parsed.get("name") == root.name, "frontmatter name must match parent directory"
    assert "description" in parsed, "frontmatter must include description"
    assert len(str(parsed["description"])) <= max_description, "description exceeds limit"
    print(json.dumps({"PASS_FRONTMATTER": True, "mode": mode, "name": parsed.get("name")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
