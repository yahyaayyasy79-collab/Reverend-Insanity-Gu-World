#!/usr/bin/env python3
"""Generate the inventory of docs/BALANCE.md: every tunable number of jsons/, with its file, object, field or unique,
and where to edit it (MOD_SPEC section 10: "List every tunable number with its file and field").

The inventory is written between the markers below; the hand-written part of docs/BALANCE.md (the knobs that matter,
autoplay evidence, how to tune) stays as it is. Logic numbers are left out: Gu-food presence gates
(`<when above [0] [Jade]>` and the like, which the refinement ladder's invariants fix) and colours and tech-tree or
policy positions. Terrains and Speeds are Vanilla copies and get one line each.

Usage: tools/gen_balance.py [--check] [--quiet]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import REPO_ROOT  # noqa: E402
import gen_paths  # noqa: E402

DOC = REPO_ROOT / "docs" / "BALANCE.md"
START, END = "<!-- inventory:start (tools/gen_balance.py) -->", "<!-- inventory:end -->"
GEN = "tools/gen_ruleset.py"
FOODS = ("Moon Orchid", "Wild Boar", "Jade", "Wine", "Gu Inheritance")
FOOD_GATE = re.compile(r"<when (?:above|below) \[-?\d+\] \[(?:" + "|".join(FOODS) + r")\]>")
NUMBER = re.compile(r"\[(\d+)\]-\[(\d+)\]|\[([+-]?\d+(?:\.\d+)?)\]|\[([+-]?\d+) [A-Z][a-z]+\]")
SKIP_FIELDS = {"row", "column", "columnNumber", "outerColor", "innerColor", "iconRGB", "color", "aiDifficultyLevel"}
# the generator section that writes each file
SECTION = {"ModOptions.json": "ModOptions / Globals", "GlobalUniques.json": "ModOptions / Globals", "Eras.json": "Eras",
           "Techs.json": "Techs", "UnitTypes.json": "Unit types", "Units.json": "Units", "UnitPromotions.json": "Promotions",
           "Events.json": "Events", "Buildings.json": "Buildings", "Policies.json": "Policies",
           "TileResources.json": "Resources", "TileImprovements.json": "Improvements", "Ruins.json": "Ruins",
           "Nations.json": "Nations", "CityStateTypes.json": "Nations", "Personalities.json": "Nations",
           "Difficulties.json": "Nations (Difficulties)"}
ORDER = ["ModOptions.json", "GlobalUniques.json", "Difficulties.json", "Units.json", "UnitPromotions.json", "Events.json",
         "Buildings.json", "Techs.json", "Policies.json", "TileResources.json", "TileImprovements.json", "Ruins.json",
         "Nations.json", "CityStateTypes.json", "Personalities.json", "Eras.json", "UnitTypes.json"]


def table(name: str) -> list[dict]:
    with open(REPO_ROOT / "data" / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def numbers(unique: str) -> list[str]:
    """The tunable numbers of a unique: bracketed numbers, stat amounts ([+2 Gold]) and ranges ([30]-[60]), minus
    Gu-food presence gates."""
    out = []
    for m in NUMBER.finditer(FOOD_GATE.sub("", unique)):
        out.append(f"{m.group(1)}-{m.group(2)}" if m.group(1) else m.group(3) or m.group(4))
    return out


def fields(obj: dict, prefix: str = "") -> list[tuple[str, str]]:
    """Numeric fields (nested dicts flattened as a.b), without colours and positions."""
    out = []
    for k, v in obj.items():
        if k in SKIP_FIELDS:
            continue
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            out.append((prefix + k, str(v)))
        elif isinstance(v, dict):
            out += fields(v, prefix + k + ".")
    return out


class Source:
    """Where to edit a number: the data table that holds it, else the generator section."""

    def __init__(self):
        self.gm = {r["name"] for r in table("gu_masters.csv")}
        # C3: clan units copy their rank's row (gen_ruleset asserts it) and legacy units only bridge old saves
        self.copies = {r["name"] for r in table("gu_masters.csv") if r["uniqueTo"] or r["legacyPath"]}
        self.paths = {p["name"] for p in gen_paths.promotions([])}
        self.gu = {r["name"] for r in table("gu.csv")}

    def __call__(self, file: str, obj: str, what: str) -> str:
        gen = f"{GEN} `{SECTION.get(file, file)}`"
        if file == "Units.json" and obj in self.gm:
            if what.startswith("Triggers a [Wild Gu]"):
                return f"{GEN} `WILD_GU_TRIGGER`"
            if what.startswith("Triggers a [Inheritance Rumour]"):
                return f"{GEN} `INHERITANCE_TRIGGER`"
            if "XP <upon turn start>" in what:
                return "data/gu_masters.csv `cultivationXP`"
            if "maintenance costs" in what:
                return "data/gu_masters.csv `maintenance`"
            if what in ("cost", "strength", "rangedStrength"):
                return f"data/gu_masters.csv `{what}`"
            if "<" not in what and "[" in what:
                return "data/gu_masters.csv `extra_uniques`"
            return f"{GEN} `gm()`"
        if file == "UnitPromotions.json" and obj in self.gu:
            if "status for" in what or "upon losing the" in what:
                return "data/hunger.csv"
            if what.startswith("Consumes"):
                return "data/gu.csv `eats`"
            return "data/gu.csv `effects` / `extra_uniques`"
        if file == "Events.json" and "Refinement Attempt" in obj and "% chance>" in what:
            return f"{GEN} `ladder()` arguments"
        if file == "Techs.json":
            return "data/techs.csv `uniques`"
        return gen


def code(s: str) -> str:
    return "`" + s.replace("|", "\\|") + "`"


def rows_for(file: str, data, source: Source) -> list[tuple[str, str, str, str]]:
    rows = []

    def add(obj: str, what: str, value: str, unique: bool):
        rows.append((obj, code(what) if unique else what, value, source(file, obj, what)))

    def visit(obj: dict, name: str):
        for f, v in fields({k: v for k, v in obj.items() if k not in ("choices", "techs", "policies")}):
            add(name, f, v, False)
        for key in ("uniques", "friendBonusUniques", "allyBonusUniques"):
            for u in obj.get(key, []):
                n = numbers(u)
                if n:
                    add(name + ("" if key == "uniques" else f" ({key})"), u, ", ".join(n), True)

    items = data if isinstance(data, list) else [data]
    for o in items:
        name = o.get("name", file[:-5])
        if (file == "Units.json" and name in source.copies) or (file == "UnitPromotions.json" and name in source.paths):
            continue
        if file == "Techs.json":
            col = f"Column {o['columnNumber']} ({', '.join(t['name'] for t in o['techs'])})"
            rows.append((col, "techCost", str(o["techCost"]), "data/tech_columns.csv `techCost`"))
            for k in ("buildingCost", "wonderCost"):
                rows.append((col, k, str(o[k]), f"data/tech_columns.csv `{k}`: inert while every building sets its own "
                                                "cost [src Ruleset.updateBuildingCosts]"))
            for t in o["techs"]:
                visit(t, t["name"])
            continue
        if file == "Policies.json":
            visit(o, name)
            for p in o["policies"]:
                visit(p, f"{name} › {p['name']}")
            continue
        if file == "Events.json":
            for c in o["choices"]:
                visit(c, f"{name} › {c['text']}")
            continue
        visit(o, name)
    return rows


def difficulties(diffs: list[dict]) -> list[str]:
    keys = [k for k, v in diffs[0].items() if isinstance(v, (int, float)) and not isinstance(v, bool)
            and k not in SKIP_FIELDS]
    lines = ["| Field | " + " | ".join(d["name"] for d in diffs) + " |", "|---|" + "---|" * len(diffs)]
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(str(d.get(k, "")) for d in diffs) + " |")
    starts = ("playerBonusStartingUnits", "aiMajorCivBonusStartingUnits", "aiCityStateBonusStartingUnits", "aiFreeTechs")
    for k in starts:
        lines.append(f"| {k} | " + " | ".join(str(len(d.get(k, []))) for d in diffs) + " |")
    return lines


def path_rows() -> list[tuple[str, str, str, str]]:
    src = "tools/gen_paths.py"
    rows = [(f"every {t}", code(f"[+{n}]% Strength"), f"+{n}", f"{src} `TIER_STRENGTH`")
            for t, n in zip(gen_paths.TIERS[:gen_paths.MAX_TIER], gen_paths.TIER_STRENGTH)]
    rows.append(("every move", code(gen_paths.MOVE_COST), ", ".join(numbers(gen_paths.MOVE_COST)), f"{src} `MOVE_COST`"))
    rows.append(("every tier", code(gen_paths.TIER_WEIGHT), "+400", f"{src} `TIER_WEIGHT`"))
    rows.append(("signature Masters", "AI weight for the clan's signature path",
                 f"+{gen_paths.SIGNATURE_WEIGHT} (share {gen_paths.SIGNATURE_SHARE})", f"{src} `SIGNATURE_SHARE`"))
    for r in table("path_conflicts.csv"):
        rows.append((f"conflict {r['a']} / {r['b']}", "Strength of a unit holding both", r["strength"],
                     "data/path_conflicts.csv"))
    for f in gen_paths.FAMILIES.values():
        for col in ("mortal_uniques", "immortal_uniques"):
            for u in gen_paths.split(f[col]):
                if numbers(u):
                    rows.append((f"family {f['family']} ({f['name']}) move", code(u), ", ".join(numbers(u)),
                                 f"data/path_families.csv `{col}`"))
    for p in gen_paths.PATHS:
        if numbers(p["signature"]):
            rows.append((f"{p['name']} Master", code(p["signature"]), ", ".join(numbers(p["signature"])),
                         "data/paths.csv `signature`"))
    for st in gen_paths.STATUSES:
        for u in gen_paths.split(st.get("uniques", "")):
            if numbers(u):
                rows.append((st["name"], code(u), ", ".join(numbers(u)), "data/path_statuses.csv `uniques`"))
    return rows


def inventory() -> str:
    jsons = REPO_ROOT / "jsons"
    files = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in jsons.glob("*.json")}
    source = Source()
    out = [START, "",
           "Generated from `jsons/` by `tools/gen_balance.py`; the self-tests fail when it is stale. Edit the source in "
           "the last column, regenerate (`tools/gen_ruleset.py && tools/gen_balance.py`), run `tools/check_all`.", ""]
    total = 0
    for name in ORDER:
        data = files[name]
        out.append(f"### {name}")
        out.append("")
        if name == "Difficulties.json":
            out.append(f"Vanilla's eight levels, edited in {GEN} `{SECTION[name]}` (`baseHappiness` is Vanilla + 6; "
                       "the starting-unit and free-tech lists are counts, renamed to this ruleset's units and techs).")
            out.append("")
            out += difficulties(data)
            total += sum(1 for line in difficulties(data)[2:])
            out.append("")
            continue
        rows = rows_for(name, data, source)
        total += len(rows)
        if name == "Units.json":
            out += ["The 12 clan units (ranks 2-4 of Gu Yue, Bai, Xiong and Wu) copy their rank's numbers: tune the rank's "
                    "row and its clan rows in data/gu_masters.csv together (tools/gen_ruleset.py asserts they match). "
                    "The 6 legacy units only carry old saves into the rank chain and are left out.", ""]
        if name == "UnitPromotions.json":
            out += ["The path promotions and their statuses are listed under 'Paths' below.", ""]
        if not rows:
            out += ["No tunable numbers.", ""]
            continue
        out.append("| Object | Field or unique | Value | Edit in |")
        out.append("|---|---|---|---|")
        out += [f"| {o} | {w} | {v} | {s} |" for o, w, v, s in rows]
        out.append("")
    rows = path_rows()
    total += len(rows)
    out += ["### Paths (tools/gen_paths.py)", "",
            "Every path promotion is built from these knobs; the hidden conflict lines follow data/path_conflicts.csv "
            "(an exact pair wins, then the milder of the two paths' `x,*` rows, then `*,*`).", "",
            "| Object | Field or unique | Value | Edit in |", "|---|---|---|---|"]
    out += [f"| {o} | {w} | {v} | {s} |" for o, w, v, s in rows]
    out.append("")
    out += ["### Terrains.json, Speeds.json", "",
            f"Vanilla copies ({GEN} `Terrains (Vanilla minus natural wonders and Fallout)` and the Speeds line in "
            f"`Nations (Difficulties)`); the only change is that no terrain grants an extra Spirit Spring. Tune them "
            "there if a playtest asks for it; until then the Vanilla numbers stand.", "",
            f"{total} numbers listed.", "", END]
    return "\n".join(out)


def splice(text: str, inv: str) -> str:
    if START not in text or END not in text:
        raise SystemExit(f"[gen_balance] {DOC} lacks the inventory markers")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    return head + inv + tail


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if docs/BALANCE.md's inventory is out of date")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    text = DOC.read_text(encoding="utf-8")
    new = splice(text, inventory())
    if args.check:
        if new != text:
            print("[gen_balance] docs/BALANCE.md inventory is out of date; run tools/gen_balance.py")
            return 1
        return 0
    DOC.write_text(new, encoding="utf-8")
    if not args.quiet:
        print(f"[gen_balance] wrote the inventory of {DOC.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
