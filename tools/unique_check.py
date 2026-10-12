#!/usr/bin/env python3
"""Quick pattern check for loose unique strings (one per line on stdin or as arguments).

Checks only that the base and every <modifier> match a documented pattern in uniques.md (case-sensitive) and
shows the documented "Applicable to" targets. Object names are NOT checked here - lint_uniques.py does that once
the strings sit in a ruleset. Exit 1 if any string matches no pattern.

  echo "Triggers a [Beast Tide] event <upon turn start>" | tools/unique_check.py
"""
from __future__ import annotations

import difflib
import sys

from common import require_ref
from uniques_db import load_db, modifiers_of, placeholder_key, remove_modifiers


def check(text: str, db) -> list[str]:
    problems = []
    base = remove_modifiers(text)
    key = placeholder_key(base)
    if key not in db.base:
        close = difflib.get_close_matches(key, list(db.base), n=2, cutoff=0.75)
        problems.append(f"base \"{base}\" matches no pattern" + (f" (close: {close})" if close else ""))
    for mod in modifiers_of(text):
        mkey = placeholder_key(mod)
        if mkey not in db.modifiers:
            close = difflib.get_close_matches(mkey, list(db.modifiers), n=2, cutoff=0.75)
            problems.append(f"modifier <{mod}> matches no pattern" + (f" (close: {close})" if close else ""))
    return problems


def main(argv: list[str]) -> int:
    require_ref()
    db = load_db()
    lines = argv or [l.rstrip("\n") for l in sys.stdin if l.strip()]
    bad = 0
    for text in lines:
        problems = check(text, db)
        if problems:
            bad += 1
            print(f"UNKNOWN {text}\n        " + "\n        ".join(problems))
        else:
            targets = sorted({t for p in db.base[placeholder_key(remove_modifiers(text))] for t in p.targets})
            print(f"OK      {text}   [applicable to: {', '.join(targets)}]")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
