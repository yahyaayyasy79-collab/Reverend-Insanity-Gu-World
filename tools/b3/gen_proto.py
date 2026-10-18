#!/usr/bin/env python3
"""Throwaway B3 prototype: the shipped jsons/ plus every path line, so Unciv's validator and the linters check every
unique PATHS.md proposes.
Usage: tools/b3/gen_proto.py OUT_DIR && tools/check_all --mod OUT_DIR --no-self-test
(then tools/autoplay.py --mod OUT_DIR ... for the AI main-path share)."""
import json, shutil, sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths_data import (P, FAMILIES, SIG_STATUSES, MOVES, CLASH, CLASH_PAIR, LOW, LOW_PAIR, NEUTRAL, COMPATIBLE,
                        DEFAULT_PAIR, SIGNATURE, SIGNATURE_SHARE, MARKER)

SRC = Path(__file__).resolve().parents[2] / "jsons"
out = Path(sys.argv[1]); j = out / "jsons"
if j.exists(): shutil.rmtree(j)
shutil.copytree(SRC, j)
L = lambda f: json.loads((j / f).read_text()); W = lambda f, d: (j / f).write_text(json.dumps(d, indent=2, ensure_ascii=False))

TYPES = ["Gu Master", "Moon Gu Master", "Strength Gu Master"]  # Slice 1 stand-ins for Gu Master / Gu Immortal / Venerable
ESS = "Green Grape Immortal Essence"                               # stand-in name; MOD_SPEC_2 Phase B names the essences
TIERS = ["Master", "Grandmaster", "Great Grandmaster", "Supreme Grandmaster"]
TIER_STR = [10, 15, 20, 25]
# stand-in rank gates (C3 swaps in the rank chain's units): tier 2 rank 3+, tiers 3-4 immortal ranks
GATE = [None,
        "Only available <for [{non-[Rank One Gu Master]} {non-[Rank Two Strength Gu Master]} {non-[Rank Two Moon Gu Master]}] units>",
        "Only available <for [Rank Four Moon Gu Master] units>",
        "Only available <for [Rank Four Strength Gu Master] units>"]
key = {p[0]: p for p in P}
name = lambda k, t=0: f"{key[k][1]} {TIERS[t]}"


def pair_value(a, b):
    s = tuple(sorted((a, b)))
    if a in NEUTRAL or b in NEUTRAL or s in COMPATIBLE:
        return 0
    if s in CLASH:
        return CLASH_PAIR
    if a in LOW or b in LOW:
        return LOW_PAIR
    return DEFAULT_PAIR


VARIED = set(sys.argv[2:])  # optional: clans treated as having no signature path (to measure variety)
ROOTS = sum(1 for p in P if not p[4])
SIG_WEIGHT = round((SIGNATURE_SHARE / (1 - SIGNATURE_SHARE) * (ROOTS - 1) - 1) * 100)


def ai_lines(k, t, parent):
    out = ["[+400]% weight to this choice for AI decisions"]
    if t == 0:
        out.insert(0, MARKER)
        if not parent:  # one path per AI unit; sub-paths stay open to their parent's holders
            out.append(f"Unavailable <for [AI player] Civilizations> <for [{MARKER}] units>")
        out += [f"[+{SIG_WEIGHT}]% weight to this choice for AI decisions <for [{c}] Civilizations>"
                for c in SIGNATURE.get(k, []) if c not in VARIED]
    return out


promos = L("UnitPromotions.json")
order = [p[0] for p in P]
pairs = {}
for a, b in combinations(order, 2):
    v = pair_value(a, b)
    if v:
        pairs.setdefault(a, []).append((b, v))
for (k, en, zh, fam, parent, src, verdict, sig, why, mortal, immortal) in P:
    for t in range(4):
        u = [f"[+{TIER_STR[t]}]% Strength"]
        if t == 0:
            u.insert(0, sig)
            u += [f"[{v}]% Strength <for units with [{name(b)}]> <hidden from users>" for b, v in pairs.get(k, [])]
            u.append("Comment [Holding another path's Master tier costs Strength: dao marks interfere (see Civilopedia)]")
        if t == 1:
            u.append(f"[This Unit] gains the [{mortal[0]}] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>")
        if t == 2:
            u.append(f"[This Unit] gains the [{immortal[0]}] status for [1] turn(s) <costs [5] [{ESS}]> <requires [1] movement>")
        if t == 3 and k == "space":
            u.append("Can pass through impassable tiles")
        if GATE[t]:
            u.append(GATE[t])
        u += ai_lines(k, t, parent)
        pre = [name(k, t - 1)] if t else ([name(parent)] + ([name("wisdom")] if k == "enchantment" else []) if parent else [])
        d = {"name": name(k, t), "unitTypes": TYPES, "uniques": u}
        if pre:
            d["prerequisites"] = pre
        promos.append(d)
    for i, (mv, tmpl) in enumerate(((mortal, MOVES[fam][0]), (immortal, MOVES[fam][1]))):
        promos.append({"name": mv[0], "uniques": [x.replace("{n}", mv[0]) for x in tmpl]})
for n, u in SIG_STATUSES.items():
    promos.append({"name": n, "uniques": u})
W("UnitPromotions.json", promos)
res = L("TileResources.json")
res.append({"name": ESS, "resourceType": "Strategic", "terrainsCanBeFoundOn": [], "uniques": ["Stockpiled"]})
W("TileResources.json", res)
names = [p["name"] for p in promos]
dup = {n for n in names if names.count(n) > 1}
print("promotions", len(promos), "duplicates", dup or "none",
      "conflict lines", sum(len(v) for v in pairs.values()))
