#!/usr/bin/env python3
"""Fail-closed merge gate for skipped or failed test jobs.

Usage:
  python tools/ci_gate.py --test-result skipped|success|failure|cancelled \\ 
      --base origin/main --head HEAD

If any non-docs path changed, the test job must have succeeded.
A docs-only label is ignored. Only the diff decides whether tests were required.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DOCS_SUFFIXES = {".md", ".txt", ".rst"}
DOCS_NAMES = {"LICENSE", "AUTHORS", "CHANGELOG"}


def changed_files(base: str, head: str) -> list[str]:
    p = subprocess.run(
        ["git", "diff", "--name-only", "%s...%s" % (base, head)],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in p.stdout.splitlines() if line.strip()]


def is_docs(path: str) -> bool:
    name = Path(path).name
    if name in DOCS_NAMES:
        return True
    return Path(path).suffix.lower() in DOCS_SUFFIXES


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--test-result", required=True)
    p.add_argument("--base", default="")
    p.add_argument("--head", default="HEAD")
    args = p.parse_args(argv)
    result = args.test_result.strip().lower()
    files = changed_files(args.base, args.head) if args.base else []
    non_docs = [f for f in files if not is_docs(f)]
    print("ci-gate: test_result=%s" % result)
    print("ci-gate: changed_files=%s" % (files or ["<none>"]))
    print("ci-gate: non_docs=%s" % (non_docs or ["<none>"]))
    if result == "success":
        print("ci-gate: OK (tests passed)")
        return 0
    if result in {"failure", "cancelled"}:
        print("ci-gate: REJECT (test job was %s)" % result, file=sys.stderr)
        return 1
    if not args.base:
        print("ci-gate: REJECT (test job was %s and no diff was provided)" % result, file=sys.stderr)
        return 1
    if non_docs:
        print("ci-gate: REJECT (test job was %s but non-docs files changed: %s)" % (result, ", ".join(non_docs)), file=sys.stderr)
        return 1
    if result == "skipped":
        print("ci-gate: OK (pure docs diff, tests skipped)")
        return 0
    print("ci-gate: REJECT (unexpected test result %s)" % result, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
