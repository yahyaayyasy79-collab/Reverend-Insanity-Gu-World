#!/usr/bin/env python3
"""Packaging guard: would Unciv's "Download mod from URL" accept this repository as a mod?

Mirrors GithubAPI.isValidModFolder (core/.../logic/github/GithubAPI.kt, 4.22.8): top-level entries
matching the lists below count as mod content; the archive is accepted only if they outnumber the rest.

Usage: tools/check_package.py [--mod PATH]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from common import Reporter, mod_root_from_args

# core/.../logic/github/GithubAPI.kt (4.22.8): top-level entries counted as mod content
GOOD_FOLDERS = [r"Images", r"jsons", r"maps", r"music", r"scenarios", r"sounds", r"voices", r"Images\..*", r"\.github"]
GOOD_FILES = [r".*\.atlas", r".*\.png", r"preview.jpg", r".*\.md", r"Atlases.json", r"\.nomedia", r"license"]
IGNORED = {".git", "ref"}  # not part of a GitHub download / gitignored


def check_packaging(mod_root: Path) -> Reporter:
    r = Reporter("packaging")
    good, bad = [], []
    for entry in sorted(mod_root.iterdir()):
        if entry.name in IGNORED:
            continue
        patterns = GOOD_FOLDERS if entry.is_dir() else GOOD_FILES
        (good if any(re.fullmatch(p, entry.name, re.I) for p in patterns) else bad).append(entry.name)
    if not (good and len(good) > len(bad)):
        r.error("(mod root)", f"Unciv would reject the archive: {len(good)} mod entries {good} vs "
                              f"{len(bad)} other {bad}. Move tooling into fewer folders or add .md files.")
    else:
        r.info("(mod root)", f"archive structure OK: {len(good)} mod entries vs {len(bad)} other ({', '.join(bad)})")
    return r


def main(argv: list[str]) -> int:
    r = check_packaging(mod_root_from_args(argv))
    r.print()
    return r.exit_code()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
