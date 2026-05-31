#!/usr/bin/env python3
"""Check whether SKILL.md is readable by weak models."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def body_without_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    closing = re.search(r"\n---\s*\n", text[3:])
    if not closing:
        return text
    return text[closing.end() + 3 :]


def workflow_section(body: str) -> str:
    match = re.search(r"^## Ordered workflow\s*$", body, re.M)
    if not match:
        return ""
    next_match = re.search(r"^## ", body[match.end() :], re.M)
    end = match.end() + next_match.start() if next_match else len(body)
    return body[match.end() : end]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", nargs="?", default="SKILL.md")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "dumb-model-readability", "self_test": "ok"}, sort_keys=True))
        return 0

    path = Path(args.skill)
    if not path.is_absolute():
        path = Path.cwd() / path
    text = path.read_text()
    body = body_without_frontmatter(text)
    lines = body.splitlines()

    assert len(text) <= 100000, "SKILL.md exceeds 100000 chars"
    assert len(lines) <= 500, "SKILL.md body exceeds 500 lines"
    first_80 = "\n".join(lines[:80])
    assert "## CRITICAL RULES" in first_80, "CRITICAL RULES not front-loaded"
    assert "## Gotchas" in first_80, "Gotchas not front-loaded"
    assert len(re.findall(r"^\d+\.\s+", body, re.M)) >= 20, "expected numbered procedural steps"

    workflow = workflow_section(body)
    assert workflow, "Ordered workflow section missing"
    forbidden = [r"or use whatever", r"either .{0,120} or"]
    for pattern in forbidden:
        assert not re.search(pattern, workflow, re.I | re.S), f"branching menu found in workflow: {pattern}"

    headings = re.findall(r"^## .+$", body, re.M)
    assert headings and headings[-1] == "## Verification checklist", "SKILL.md must end with Verification checklist section"
    assert "front-loaded" in body and "book-end" in body, "book-ended critical rules not present"
    print(json.dumps({"PASS_READABILITY": True, "body_lines": len(lines), "numbered_steps": len(re.findall(r'^\d+\.\s+', body, re.M))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
