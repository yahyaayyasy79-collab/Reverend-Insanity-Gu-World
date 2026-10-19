#!/usr/bin/env python3
"""Path content (MOD_SPEC_3, docs/PATHS.md) from data/paths.csv, data/path_families.csv, data/path_conflicts.csv and
data/path_statuses.csv.

tools/gen_ruleset.py imports this module for the promotions (each path's attainment tiers, its killer-move statuses,
the signature statuses) and tools/gen_translations.py for their Indonesian names and civilopedia. Run on its own, it
writes the generated tables of docs/PATHS.md (between the <!-- name:start --> / <!-- name:end --> markers).

Usage: tools/gen_paths.py [--check] [--quiet]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import REPO_ROOT  # noqa: E402

DATA = REPO_ROOT / "data"
DOC = REPO_ROOT / "docs" / "PATHS.md"

# Tiers shipped so far: MOD_SPEC_3 C3 puts tiers 1-2 into Slice 1; tiers 3-4 and the immortal moves need the Gu
# Immortal unit type and essence (MOD_SPEC_2 C1/C3).
MAX_TIER = 2
TIERS = ["Master", "Grandmaster", "Great Grandmaster", "Supreme Grandmaster"]
TIERS_ZH = ["大师", "宗师", "大宗师", "无上大宗师"]
TIERS_ID = ["Ahli", "Mahaguru", "Mahaguru Agung", "Mahaguru Tertinggi"]
TIER_STRENGTH = [10, 15, 20, 25]
# Grandmaster from rank 3: units whose required tech lies outside the Rank One-Two era [src BaseUnit.matchesSingleFilter:
# a unit filter matches the era of the unit's required tech]
TIER_GATE = [None, "Only available <for [non-[Rank One-Two era]] units>", None, None]
MOVE_COST = "<costs [+15 Gold] stats> <requires [1] movement>"
MARKER = "Path Master"  # filter marker on every Master (tools/unique_allowlist.txt)
SIGNATURE_SHARE = 0.85  # MOD_SPEC_3: a signature clan keeps >=80% of its path promotions on its path
TIER_WEIGHT = "[+400]% weight to this choice for AI decisions"
ONE_PATH = f"Unavailable <for [AI player] Civilizations> <for [{MARKER}] units>"
COMMENT = "Every other path this unit holds costs Strength: dao marks interfere"
CONFLICT = re.compile(r"^\[-?\d+\]% Strength <for units with \[.+ Master\]> <hidden from users>$")


def table(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


PATHS = table("paths.csv")
FAMILIES = {r["family"]: r for r in table("path_families.csv")}
STATUSES = table("path_statuses.csv")
KEY = {p["key"]: p for p in PATHS}
# D2 (the user, 2026-10-19): one Gu per path, granted with the Master. Rows with no name_id are Slice 1 Gu that
# already exist (Moonlight Gu, White Boar Gu, Liquor Worm); the rest are new promotions built here.
PATH_GU = table("path_gu.csv")
GU_OF = {p["key"]: [g for g in PATH_GU if g["path"] == p["key"]] for p in PATHS}
assert all(GU_OF.values()), "every path needs its Gu (data/path_gu.csv)"
# a Gu of rank r needs a unit of rank r (the rank-5 Gu wait at rank four until the immortal arc; ADAPTED); a unit's
# era is its required tech's era [src BaseUnit.matchesFilter]
RANK_GATE = {1: "", 2: "<for [non-[Rank One Gu Master]] units>", 3: "<for [non-[Rank One-Two era]] units>",
             4: "<for [Rank Four era] units>", 5: "<for [Rank Four era] units>"}
assert len({p["signature"] for p in PATHS}) == len(PATHS), "two paths share a signature unique"
ROOTS = sum(1 for p in PATHS if not p["parent"])
SIGNATURE_WEIGHT = round((SIGNATURE_SHARE / (1 - SIGNATURE_SHARE) * (ROOTS - 1) - 1) * 100)


def split(cell: str) -> list[str]:
    return [x for x in cell.split("|") if x]


def tier_name(p: dict, t: int) -> str:
    return f"{p['name']} {TIERS[t]}"


def tier_name_id(p: dict, t: int) -> str:
    return f"{TIERS_ID[t]} Jalur {p['name_id']}"


def pair_strength() -> dict[tuple[str, str], int]:
    """Strength per pair of paths: the default row (*,*), then path-wide rows (x,*), then exact pairs win."""
    rows = table("path_conflicts.csv")
    default = next(int(r["strength"]) for r in rows if r["a"] == r["b"] == "*")
    wide = {r["a"]: int(r["strength"]) for r in rows if r["b"] == "*" and r["a"] != "*"}
    exact = {tuple(sorted((r["a"], r["b"]))): int(r["strength"]) for r in rows if "*" not in (r["a"], r["b"])}
    out = {}
    for a, b in combinations([p["key"] for p in PATHS], 2):
        s = tuple(sorted((a, b)))
        if s in exact:
            v = exact[s]
        elif a in wide or b in wide:
            v = max(wide.get(a, -999), wide.get(b, -999))
        else:
            v = default
        out[(a, b)] = v
    return out


def conflict_lines(p: dict) -> list[str]:
    """On the earlier path's Master, one line per later path whose pair costs Strength."""
    return [f"[{v}]% Strength <for units with [{tier_name(KEY[b], 0)}]> <hidden from users>"
            for (a, b), v in pair_strength().items() if a == p["key"] and v]


def move_uniques(p: dict, immortal: bool = False) -> list[str]:
    name = p["immortal" if immortal else "mortal"]
    return [u.replace("{n}", name) for u in split(FAMILIES[p["family"]]["immortal_uniques" if immortal else "mortal_uniques"])]


def grant(g: dict) -> str:
    """The Master hands its path's Gu to the unit at a turn start, once the unit's rank and the Gu's food allow; a Gu
    that starved comes back only when its food is in surplus again."""
    gates = [g["gate"] or RANK_GATE[int(g["rank"])]] + ([f"<when above [0] [{g['food']}]>"] if g["food"] else [])
    return " ".join([f"[This Unit] gains the [{g['name']}] promotion <upon turn start> <for units without [{g['name']}]>"]
                    + [x for x in gates if x])


def new_gu(g: dict) -> bool:
    return bool(g["name_id"])


def gu_promotions() -> list[dict]:
    """The new path Gu: a food eater follows the Slice 1 hunger meter (tools/gu_rules.py), the others eat stones."""
    from gu_rules import gu_promotion, items
    out = []
    for g in (g for g in PATH_GU if new_gu(g)):
        if g["food"]:
            d = gu_promotion({**g, "rank": str(min(int(g["rank"]), 4)), "extra_uniques": ""})
        else:
            d = {"name": g["name"], "uniques": items(g["effects"])
                 + ([f"[+{g['upkeep']}]% maintenance costs"] if g["upkeep"] != "0" else [])}
        d["civilopediaText"] = [{"text": g["pedia"]}]
        out.append(d)
    return out


def tier_uniques(p: dict, t: int) -> list[str]:
    u = [f"[+{TIER_STRENGTH[t]}]% Strength"]
    if t == 0:
        u = [p["signature"]] + u + conflict_lines(p) + [f"Comment [{COMMENT}]", MARKER] + [grant(g) for g in GU_OF[p["key"]]]
    if t == 1:
        u.append(f"[This Unit] gains the [{p['mortal']}] status for [1] turn(s) {MOVE_COST}")
    if TIER_GATE[t]:
        u.append(TIER_GATE[t])
    u.append(TIER_WEIGHT)
    if t == 0:
        if not p["parent"]:  # one path per AI unit; a sub-path stays open to its parent's holders
            u.append(ONE_PATH)
        u += [f"[+{SIGNATURE_WEIGHT}]% weight to this choice for AI decisions <for [{c}] Civilizations>"
              for c in split(p["signature_clans"])]
    return u


def pedia(p: dict, t: int) -> tuple[str, str]:
    if t == 0:
        return (f"{p['name']} path ({p['chinese']}), Master attainment ({TIERS_ZH[0]}): {p['hook']}.",
                f"Jalur {p['name_id']} ({p['chinese']}), pencapaian {TIERS_ID[0]} ({TIERS_ZH[0]}): {p['hook_id']}.")
    return (f"{p['name']} path, Grandmaster attainment ({TIERS_ZH[1]}): deep enough to bend other paths' methods to "
            f"its own Gu. Opens the killer move {p['mortal']}.",
            f"Jalur {p['name_id']}, pencapaian {TIERS_ID[1]} ({TIERS_ZH[1]}): cukup dalam untuk meminjam cara jalur lain "
            f"dengan Gu sendiri. Membuka jurus pamungkas {p['mortal_id']}.")


def move_pedia(p: dict) -> tuple[str, str]:
    zh = f" ({p['mortal_zh']})" if p["mortal_zh"] else ""
    f = FAMILIES[p["family"]]
    return (f"{p['mortal']}{zh}: a {p['name'].lower()}-path killer move for one turn: {f['mortal_text']}.",
            f"{p['mortal_id']}{zh}: jurus pamungkas jalur {p['name_id']} selama satu giliran: {f['mortal_text_id']}.")


def promotions(unit_types: list[str]) -> list[dict]:
    out = []
    for p in PATHS:
        for t in range(MAX_TIER):
            d = {"name": tier_name(p, t), "unitTypes": unit_types, "uniques": tier_uniques(p, t),
                 "civilopediaText": [{"text": pedia(p, t)[0]}]}
            if t:
                d["prerequisites"] = [tier_name(p, t - 1)]
            elif p["parent"]:
                parents = [p["parent"]] + (["wisdom"] if p["key"] == "enchantment" else [])
                d["prerequisites"] = [tier_name(KEY[x], 0) for x in parents]
            out.append(d)
        out.append({"name": p["mortal"], "uniques": move_uniques(p), "civilopediaText": [{"text": move_pedia(p)[0]}]})
    out += [{"name": s["name"], "uniques": split(s["uniques"]), "civilopediaText": [{"text": s["pedia"]}]} for s in STATUSES]
    return out


def translations() -> list[tuple[str, str]]:
    """(English, Indonesian) for every name and civilopedia text this module writes."""
    out = [(COMMENT, "Setiap jalur lain yang dipegang unit ini memotong Kekuatan: jejak dao saling mengganggu")]
    for p in PATHS:
        for t in range(MAX_TIER):
            out += [(tier_name(p, t), tier_name_id(p, t)), pedia(p, t)]
        out += [(p["mortal"], p["mortal_id"]), move_pedia(p)]
    for s in STATUSES:
        out += [(s["name"], s["name_id"]), (s["pedia"], s["pedia_id"])]
    for g in (g for g in PATH_GU if new_gu(g)):
        out += [(g["name"], g["name_id"]), (g["pedia"], g["pedia_id"])]
    return out


# ---------------- docs/PATHS.md tables ----------------
def code(s: str) -> str:
    return "`" + s.replace("|", "\\|") + "`"


def doc_tables() -> dict[str, str]:
    paths = ["| # | Path | Chinese | Family | Sub-path of | Source | Verdict | Signature (one unique) | Lore hook |",
             "|---|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(PATHS, 1):
        parent = KEY[p["parent"]]["name"] if p["parent"] else ""
        paths.append(f"| {i} | {p['name']} | {p['chinese']} | {p['family']} | {parent} | {p['source']} | {p['verdict']} | "
                     f"{code(p['signature'])} | {p['hook']} |")
    fams = ["| Family | Paths | Play feel | Mortal move template | Immortal move template | Icon colour |",
            "|---|---|---|---|---|---|"]
    for k, f in FAMILIES.items():
        members = ", ".join(p["name"] for p in PATHS if p["family"] == k)
        fams.append(f"| {k}. {f['name']} | {members} | {f['feel']} | {f['mortal_text']} | {f['immortal_text']} | "
                    f"[{f['color'].replace(' ', ', ')}] |")
    moves = ["| Path | Family template | Mortal move (Grandmaster) | Tag | Immortal move (Great Grandmaster) | Tag |",
             "|---|---|---|---|---|---|"]
    for p in PATHS:
        m = p["mortal"] + (f" {p['mortal_zh']}" if p["mortal_zh"] else "")
        im = p["immortal"] + (f" {p['immortal_zh']}" if p["immortal_zh"] else "")
        moves.append(f"| {p['name']} | {p['family']} | {m} | {p['mortal_tag']} | {im} | {p['immortal_tag']} |")
    uniq = [f"Tiers 1-{MAX_TIER} ship in Slice 1. Every Master also carries one hidden conflict line per later path "
            "whose pair costs Strength (`[relativeAmount]% Strength` `<for units with [promotion]>` "
            "`<hidden from users>`, values from data/path_conflicts.csv) and a visible comment line.", "",
            "| Path | Master | Grandmaster | Mortal move status |", "|---|---|---|---|"]
    for p in PATHS:
        master = [u for u in tier_uniques(p, 0) if not CONFLICT.match(u)]
        cells = [" ".join(code(u) for u in master), " ".join(code(u) for u in tier_uniques(p, 1)),
                 " ".join(code(u) for u in move_uniques(p))]
        uniq.append(f"| {p['name']} | " + " | ".join(cells) + " |")
    uniq += ["", "| Status | Uniques |", "|---|---|"]
    uniq += [f"| {s['name']} | " + " ".join(code(u) for u in split(s["uniques"])) + " |" for s in STATUSES]
    gu = ["Granted at a turn start to a unit holding the path's Master (the line is in the Master's column above), once "
          "the unit's rank reaches the Gu's (a rank-5 Gu at rank four until the immortal arc) and, for a food eater, "
          "while that food is in surplus. Moonlight Gu, White Boar Gu and the Liquor Worm are the Slice 1 Gu.", "",
          "| Path | Gu | Chinese | Rank | Food | Uniques | Verdict | Source |", "|---|---|---|---|---|---|---|---|"]
    built = {d["name"]: d for d in gu_promotions()}
    for g in PATH_GU:
        uniques = " ".join(code(u) for u in built[g["name"]]["uniques"]) if g["name"] in built else "Slice 1 Gu"
        gu.append(f"| {KEY[g['path']]['name']} | {g['name']} | {g['chinese'] or '—'} | {g['rank']} | {g['food'] or 'stones'} "
                  f"| {uniques} | {g['verdict']} | {g['source']} |")
    return {"paths": "\n".join(paths), "families": "\n".join(fams), "moves": "\n".join(moves), "uniques": "\n".join(uniq),
            "gu": "\n".join(gu)}


def splice(text: str, tables: dict[str, str]) -> str:
    for name, body in tables.items():
        start, end = f"<!-- {name}:start (tools/gen_paths.py) -->", f"<!-- {name}:end -->"
        if start not in text or end not in text:
            raise SystemExit(f"[gen_paths] {DOC.name} lacks the markers for '{name}'")
        head, rest = text.split(start, 1)
        _, tail = rest.split(end, 1)
        text = f"{head}{start}\n{body}\n{end}{tail}"
    return text


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if the tables in docs/PATHS.md are out of date")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    sigs = [p["signature"] for p in PATHS]
    if len(set(sigs)) != len(sigs):
        raise SystemExit("[gen_paths] two paths share a signature (MOD_SPEC_3)")
    text = DOC.read_text(encoding="utf-8")
    new = splice(text, doc_tables())
    if args.check:
        if new != text:
            print("[gen_paths] docs/PATHS.md tables are out of date; run tools/gen_paths.py")
            return 1
        return 0
    DOC.write_text(new, encoding="utf-8")
    if not args.quiet:
        print(f"[gen_paths] {len(PATHS)} paths, tiers 1-{MAX_TIER}; wrote the tables of {DOC.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
