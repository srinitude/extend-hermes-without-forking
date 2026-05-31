#!/usr/bin/env python3
"""Confirm shipped scripts have deterministic self-test output."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_self_test(script: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        [sys.executable, str(script), "--self-test"],
        cwd=str(skill_root()),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"check": "determinism", "self_test": "ok"}, sort_keys=True))
        return 0

    scripts = sorted((skill_root() / "scripts").glob("*.py"))
    assert scripts, "no scripts found"
    checked = []
    for script in scripts:
        first = run_self_test(script)
        second = run_self_test(script)
        assert first == second, f"nondeterministic self-test output: {script.name}"
        assert first[0] == 0, f"self-test failed for {script.name}: {first[2]}"
        checked.append(script.name)
    print(json.dumps({"PASS_DETERMINISM": True, "scripts": checked}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
