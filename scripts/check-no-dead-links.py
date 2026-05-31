#!/usr/bin/env python3
"""Check referenced skill-relative files under known resource dirs exist."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


LINK_RE = re.compile(r"(?<![A-Za-z0-9_-])((?:references|scripts|assets|evals)/[A-Za-z0-9._/-]+\.[A-Za-z0-9]+)")


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def scan_file(path: Path, root: Path) -> list[str]:
    text = path.read_text()
    misses = []
    for match in LINK_RE.findall(text):
        candidate = root / match.rstrip(".,;:")
        if not candidate.exists():
            misses.append(f"{path.relative_to(root)} -> {match}")
    return misses


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "no-dead-links", "self_test": "ok"}, sort_keys=True))
        return 0

    root = skill_root()
    files = [root / "SKILL.md"] + sorted((root / "references").glob("*.md"))
    misses: list[str] = []
    for path in files:
        misses.extend(scan_file(path, root))
    assert not misses, "dead links found:\n" + "\n".join(misses)
    print(json.dumps({"PASS_DEADLINKS": True, "files_scanned": [str(p.relative_to(root)) for p in files]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
