#!/usr/bin/env python3
"""Rewrite the generated "Exact uniques" blocks of docs/LORE_MAPPING.md's MOD_SPEC_2 Phase C sections from jsons/.

Each Phase C section ends with a line starting "Exact uniques (" followed by blocks written here; the self-test
(tests/test_tools.py LoreMapping) then sees every generated unique quoted. Run after tools/gen_ruleset.py.

Usage: tools/lore_blocks.py [--check]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "LORE_MAPPING.md"

# section heading -> objects per file; "Globals" lists GlobalUniques lines containing one of the given markers
SECTIONS = {
    "## Phase C1:": {"Units.json": ["Rank Five Gu Master", "Rank Six Gu Immortal"],
                     "UnitPromotions.json": ["Ascension", "Lower Grade Blessed Land", "Middle Grade Blessed Land",
                                             "Upper Grade Blessed Land", "Super Grade Blessed Land"],
                     "Events.json": ["Ascension", "Ascension Trial", "Hasty Ascension Trial", "Immortal Ascension",
                                     "Aperture Collapse"],
                     "TileResources.json": ["Heaven Qi"],
                     "Globals": ["Qi]"]},
    "## Phase C2:": {"UnitPromotions.json": ["Calamity Countdown", "Tribulation Countdown", "Ravaged Land"],
                     "Events.json": ["Earthly Calamity", "Calamity Toll", "Heavenly Tribulation", "Tribulation Toll",
                                     "Heaven's Will"],
                     "Buildings.json": ["Formation Ward", "Stockpile Vault"],
                     "Globals": ["[Lifespan Gu]", "[Heaven's Will]"]},
    "## Phase C3:": {"Buildings.json": ["Spring Autumn Cicada", "Fixed Immortal Travel", "Man as Before", "Unravel Mystery",
                                        "Connect Luck", "Self Strength", "Woman's Heart", "Bone Spike", "Star Eyes",
                                        "Divert Disaster"],
                     "Events.json": ["Immortal Gu Refinement"],
                     "Globals": ["appears <upon losing"]},
}


def blocks(spec: dict) -> str:
    out = []
    for f, names in spec.items():
        if f == "Globals":
            g = json.loads((ROOT / "jsons" / "GlobalUniques.json").read_text(encoding="utf-8"))["uniques"]
            out.append("**GlobalUniques**\n\n```\n" + "\n".join(u for u in g if any(m in u for m in names)) + "\n```\n")
            continue
        objs = {o["name"]: o for o in json.loads((ROOT / "jsons" / f).read_text(encoding="utf-8"))}
        for n in names:
            o = objs[n]
            if f == "Events.json":
                out.append(f"**{n}** ({'silent die' if o.get('presentation') == 'None' else 'popup'})\n")
                out += [f"* {c['text']}\n\n```\n" + "\n".join(c["uniques"]) + "\n```\n" for c in o["choices"]]
            else:
                fields = {k: v for k, v in o.items() if k not in ("name", "uniques")}
                out.append(f"**{n}** ({f}{'; ' + json.dumps(fields) if fields else ''})\n\n```\n"
                           + "\n".join(o.get("uniques", [])) + "\n```\n")
    return "\n".join(out)


def render(text: str) -> str:
    for heading, spec in SECTIONS.items():
        start = text.index("\n" + heading)
        nxt = text.find("\n## ", start + 1)
        end = len(text) if nxt < 0 else nxt
        sec = text[start:end]
        cut = sec.index("\nExact uniques (")
        cut = sec.index("\n", cut + 1) + 1
        text = text[:start] + sec[:cut] + "\n" + blocks(spec) + ("\n" if nxt >= 0 else "") + text[end:]
    return text


def main(argv: list[str]) -> int:
    old = DOC.read_text(encoding="utf-8")
    new = render(old)
    if "--check" in argv:
        if new != old:
            print("[lore_blocks] docs/LORE_MAPPING.md blocks are out of date; run tools/lore_blocks.py")
            return 1
        return 0
    DOC.write_text(new, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
