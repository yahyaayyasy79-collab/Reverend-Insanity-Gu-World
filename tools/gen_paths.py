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

# Tiers: MOD_SPEC_3 C3 put tiers 1-2 into Slice 1; MOD_SPEC_2 C3 added the Great Grandmaster (rank six, the immortal
# move) and C5 the Supreme Grandmaster (rank eight).
MAX_TIER = 4
TIERS = ["Master", "Grandmaster", "Great Grandmaster", "Supreme Grandmaster"]
TIERS_ZH = ["大师", "宗师", "大宗师", "无上大宗师"]
TIERS_ID = ["Ahli", "Mahaguru", "Mahaguru Agung", "Mahaguru Tertinggi"]
TIER_STRENGTH = [10, 15, 20, 25]
# Grandmaster from rank 3: units whose required tech lies outside the Rank One-Two era [src BaseUnit.matchesSingleFilter:
# a unit filter matches the era of the unit's required tech]
TIER_GATE = [None, "Only available <for [non-[Rank One-Two era]] units>", "Only available <for [post-[Rank Five era]] units>",
             "Only available <for [post-[Rank Seven era]] units>"]
# PATHS.md: the space path's Supreme Grandmaster walks through anything (a permanent promotion: the unique is cached)
SUPREME_EXTRA = {"space": ["Can pass through impassable tiles"]}
SUPREME_MARKER = "Supreme Attainment"  # filter marker: the Venerable Ascension counts rank-eight holders (MOD_SPEC_3)
MOVE_COST = "<costs [+15 Gold] stats> <requires [1] movement>"
IMMORTAL_MOVE_COST = "<costs [5] [Green Grape Immortal Essence]> <requires [1] movement>"  # MOD_SPEC_2 #5
# MOD_SPEC_2 #4: dao marks. Every immortal Gu carries its path's marker; a path's Master gains per mark of its own path
# and loses per mark of a path it clashes with strongly (data/path_conflicts.csv at -25 or worse)
DAO_MARK, DAO_CLASH, STRONG_CLASH = 5, -5, -25
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
IMMORTAL_GU = table("immortal_gu.csv")  # MOD_SPEC_2 C3: their path markers are the dao marks
FAMILIES = {r["family"]: r for r in table("path_families.csv")}
STATUSES = table("path_statuses.csv")
KEY = {p["key"]: p for p in PATHS}
# D2 (the user, 2026-10-19): one Gu per path, granted with the Master. Rows with no name_id are Slice 1 Gu that
# already exist (Moonlight Gu, White Boar Gu, Liquor Worm); the rest are new promotions built here.
PATH_GU = table("path_gu.csv")
GU_OF = {p["key"]: [g for g in PATH_GU if g["path"] == p["key"]] for p in PATHS}
assert all(GU_OF.values()), "every path needs its Gu (data/path_gu.csv)"
# a Gu of rank r needs a unit of rank r or higher; a unit's era is its required tech's era [src BaseUnit.matchesFilter].
# Since MOD_SPEC_2 C1 the rank-5 Gu wait for the Rank Five Gu Master (they waited at rank four before).
RANK_GATE = {1: "", 2: "<for [non-[Rank One Gu Master]] units>", 3: "<for [non-[Rank One-Two era]] units>",
             4: "<for [post-[Rank Three era]] units>", 5: "<for [post-[Rank Four era]] units>"}
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


def path_marker(key: str) -> str:
    return f"{KEY[key]['name']} Path"


def dao_mark_lines(p: dict) -> list[str]:
    marked = {g["path"] for g in IMMORTAL_GU}
    out = [f"[+{DAO_MARK}]% Strength <for every [1] [[{path_marker(p['key'])}] Buildings]>"] if p["key"] in marked else []
    for (a, b), v in pair_strength().items():
        if v <= STRONG_CLASH and p["key"] in (a, b):
            other = b if a == p["key"] else a
            if other in marked:
                out.append(f"[{DAO_CLASH}]% Strength <for every [1] [[{path_marker(other)}] Buildings]>")
    return out


def move_uniques(p: dict, immortal: bool = False) -> list[str]:
    name = p["immortal" if immortal else "mortal"]
    return [u.replace("{n}", name) for u in split(FAMILIES[p["family"]]["immortal_uniques" if immortal else "mortal_uniques"])]


def grant(g: dict) -> str:
    """The Master hands its path's Gu to the unit at a turn start, once the unit's rank and the Gu's food allow; a Gu
    that starved comes back only when its food is in surplus again."""
    # a Gu that eats a Gu food comes only from a spare of two, one unit in four per turn: the civ's resource count is
    # not refreshed between units at a turn start [src], so a looser gate fed one spare to every Master at once and
    # they starved together (autoplay, canon overhaul 4)
    gates = [g["gate"] or RANK_GATE[int(g["rank"])]] + (
        [f"<when above [1] [{g['food']}]>", "<with [25]% chance>"] if g["food"] else [])
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
        u = ([p["signature"]] + u + conflict_lines(p) + [f"Comment [{COMMENT}]", MARKER] + [grant(g) for g in GU_OF[p["key"]]]
             + dao_mark_lines(p))
    if t == 1:
        u.append(f"[This Unit] gains the [{p['mortal']}] status for [1] turn(s) {MOVE_COST}")
    if t == 2:
        u.append(f"[This Unit] gains the [{p['immortal']}] status for [1] turn(s) {IMMORTAL_MOVE_COST}")
    if t == 3:
        u += SUPREME_EXTRA.get(p["key"], []) + [SUPREME_MARKER]
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
    if t == 3:
        return (f"{p['name']} path, Supreme Grandmaster attainment ({TIERS_ZH[3]}): it raises the path's ceiling; all "
                f"ten Venerables reached it. Rank eight and up.",
                f"Jalur {p['name_id']}, pencapaian {TIERS_ID[3]} ({TIERS_ZH[3]}): menaikkan batas jalur itu; kesepuluh "
                f"Yang Mulia mencapainya. Tingkat delapan ke atas.")
    if t == 2:
        return (f"{p['name']} path, Great Grandmaster attainment ({TIERS_ZH[2]}): where most rank-eight immortals end; a "
                f"rank-six immortal that reaches it opens the immortal killer move {p['immortal']} (5 green grape essence).",
                f"Jalur {p['name_id']}, pencapaian {TIERS_ID[2]} ({TIERS_ZH[2]}): tempat kebanyakan abadi tingkat delapan "
                f"berhenti; abadi tingkat enam yang mencapainya membuka jurus pamungkas abadi {p['immortal_id']} "
                f"(5 esensi anggur hijau).")
    return (f"{p['name']} path, Grandmaster attainment ({TIERS_ZH[1]}): deep enough to bend other paths' methods to "
            f"its own Gu. Opens the killer move {p['mortal']}.",
            f"Jalur {p['name_id']}, pencapaian {TIERS_ID[1]} ({TIERS_ZH[1]}): cukup dalam untuk meminjam cara jalur lain "
            f"dengan Gu sendiri. Membuka jurus pamungkas {p['mortal_id']}.")


def immortal_move_pedia(p: dict) -> tuple[str, str]:
    zh = f" ({p['immortal_zh']})" if p["immortal_zh"] else ""
    f = FAMILIES[p["family"]]
    return (f"{p['immortal']}{zh}: a {p['name'].lower()}-path immortal killer move for one turn: {f['immortal_text']}.",
            f"{p['immortal_id']}{zh}: jurus pamungkas abadi jalur {p['name_id']} selama satu giliran: "
            f"{f['immortal_text_id']}.")


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
        if MAX_TIER > 2:
            out.append({"name": p["immortal"], "uniques": move_uniques(p, immortal=True),
                        "civilopediaText": [{"text": immortal_move_pedia(p)[0]}]})
    out += [{"name": s["name"], "uniques": split(s["uniques"]), "civilopediaText": [{"text": s["pedia"]}]} for s in STATUSES]
    return out


# ---------------- policy branches and halls (the user, 2026-11-01: "semua 47 jalur") ----------------
# One policy branch per canonical path beside Slice 1's Moon and Strength branches (kept as they are): an opener that
# grows the path's Masters with every adopted policy of the branch, three policies and a completion bonus from the
# path's family, and a hall building (unlocked by the opener) whose newly trained Gu Masters hold the path's Master.
# Paths whose dao marks clash strongly (data/path_conflicts.csv at -25) exclude each other's branch.
SLICE1_BRANCHES = {"moon", "strength"}
FAMILY_ERA = {"A": "Rank Three era", "B": "Rank Three era", "C": "Rank Three era", "D": "Rank Four era",
              "E": "Rank Four era", "F": "Rank Five era", "G": "Rank Five era"}
ERA_TECH = {"Rank One-Two era": "Rank Two Cultivation", "Rank Three era": "Rank Three Cultivation",
            "Rank Four era": "Rank Four Cultivation", "Rank Five era": "Purple Crystal Essence"}
ERA_COST = {"Rank One-Two era": 90, "Rank Three era": 120, "Rank Four era": 170, "Rank Five era": 240}
# (policy 1, policy 2, policy 3, completion); {m} is the path's Master
FAMILY_POLICIES = {
    "A": ("[+15]% Strength <when defending> <for [{m}] units>", "[+1 Production] [in all cities]",
          "Heals [15] damage if it kills a unit <for [{m}] units>", "[+10] HP when healing <for [{m}] units>"),
    "B": ("[+15]% Strength <when attacking> <for [{m}] units>", "[+10]% Production when constructing [Military] units [in all cities]",
          "[1] Movement <for [{m}] units>", "[+15]% Strength <vs cities> <for [{m}] units>"),
    "C": ("[+10]% Strength <for [{m}] units>", "[+1 Food] [in all cities]", "[+10] HP when healing <for [{m}] units>",
          "[+10]% [Food] [in all cities]"),
    "D": ("[1] Sight <for [{m}] units>", "[+1 Culture] [in all cities]", "[+15]% Strength <when attacking> <for [{m}] units>",
          "[1] Movement <for [{m}] units>"),
    "E": ("[+15]% XP gained from combat <for [{m}] units>", "[+1 Science] [in all cities]", "[+10]% Strength <for [{m}] units>",
          "[+10]% [Science] [in all cities]"),
    "F": ("[+10]% Strength <for [{m}] units>", "[+1 Gold] [in all cities]", "[+1 Happiness]", "[+10]% [Gold] [in all cities]"),
    "G": ("[+10]% Production when constructing [All] wonders [in all cities]", "[+1 Production] [in all cities]",
          "[+10]% Strength <for [{m}] units>", "[+10]% [Production] [in all cities]"),
}
MEMBER_NAMES = [("Lineage", "Garis Keturunan"), ("Insight", "Wawasan"), ("Doctrine", "Doktrin")]
# what each of the four family policies does, in words (EN, ID), for the civilopedia
FAMILY_POLICY_TEXT = {
    "A": [("its Masters defend 15% harder", "para Ahlinya bertahan 15% lebih kuat"), ("+1 production in every city", "+1 produksi di setiap kota"),
          ("its Masters heal 15 HP when they kill", "para Ahlinya pulih 15 HP saat membunuh"), ("its Masters heal 10 HP more", "para Ahlinya pulih 10 HP lebih banyak")],
    "B": [("its Masters attack 15% harder", "para Ahlinya menyerang 15% lebih kuat"), ("military units are built 10% faster", "unit militer dibangun 10% lebih cepat"),
          ("its Masters move 1 tile farther", "para Ahlinya bergerak 1 petak lebih jauh"), ("its Masters fight 15% harder against cities", "para Ahlinya bertarung 15% lebih kuat melawan kota")],
    "C": [("its Masters fight 10% harder", "para Ahlinya bertarung 10% lebih kuat"), ("+1 food in every city", "+1 makanan di setiap kota"),
          ("its Masters heal 10 HP more", "para Ahlinya pulih 10 HP lebih banyak"), ("+10% food", "+10% makanan")],
    "D": [("its Masters see 1 tile farther", "para Ahlinya melihat 1 petak lebih jauh"), ("+1 culture in every city", "+1 budaya di setiap kota"),
          ("its Masters attack 15% harder", "para Ahlinya menyerang 15% lebih kuat"), ("its Masters move 1 tile farther", "para Ahlinya bergerak 1 petak lebih jauh")],
    "E": [("its Masters gain 15% more XP", "para Ahlinya mendapat 15% XP lebih banyak"), ("+1 science in every city", "+1 sains di setiap kota"),
          ("its Masters fight 10% harder", "para Ahlinya bertarung 10% lebih kuat"), ("+10% science", "+10% sains")],
    "F": [("its Masters fight 10% harder", "para Ahlinya bertarung 10% lebih kuat"), ("+1 stone in every city", "+1 batu di setiap kota"),
          ("+1 happiness", "+1 kebahagiaan"), ("+10% stones", "+10% batu")],
    "G": [("wonders are built 10% faster", "keajaiban dibangun 10% lebih cepat"), ("+1 production in every city", "+1 produksi di setiap kota"),
          ("its Masters fight 10% harder", "para Ahlinya bertarung 10% lebih kuat"), ("+10% production", "+10% produksi")],
}


def member_pedia(p: dict, i: int) -> tuple[str, str]:
    en, idn = FAMILY_POLICY_TEXT[p["family"]][i]
    what = ("Completing the branch: " if i == 3 else f"A policy of the {branch_name(p)}: ")
    what_id = ("Menuntaskan cabang ini: " if i == 3 else f"Kebijakan cabang Jalur {p['name_id']}: ")
    return what + en + ".", what_id + idn + "."
FAMILY_TEXT = {k: (r["name"], r["name_id"]) for k, r in FAMILIES.items()}


def branch_name(p: dict) -> str:
    return f"{p['name']} Path"


def hall_name(p: dict) -> str:
    return f"{p['name']} Hall"


def member_names(p: dict) -> list[tuple[str, str]]:
    return [(f"{p['name']} {en}", f"{idn} {p['name_id']}") for en, idn in MEMBER_NAMES]


def clashes(p: dict) -> list[str]:
    return [b if a == p["key"] else a for (a, b), v in pair_strength().items() if v <= STRONG_CLASH and p["key"] in (a, b)]


def policy_branches() -> list[dict]:
    out = []
    for p in PATHS:
        if p["key"] in SLICE1_BRANCHES:
            continue
        m = tier_name(p, 0)
        f = FAMILY_POLICIES[p["family"]]
        names = [n for n, _ in member_names(p)]
        out.append({
            "name": branch_name(p), "era": FAMILY_ERA[p["family"]],
            "priorities": {"Southern Border Supremacy": 3, "Endurance": 3},
            "uniques": [f"[+5]% Strength <for [{m}] units> <for every [Adopted [[{branch_name(p)}] branch] Policies]>"]
            + [f"Only available <before adopting [{branch_name(KEY[c])}]>" for c in clashes(p)],
            "civilopediaText": [{"text": branch_pedia(p)[0]}],
            "policies": [
                {"name": names[0], "row": 1, "column": 1, "uniques": [f[0].format(m=m)]},
                {"name": names[1], "row": 1, "column": 3, "uniques": [f[1].format(m=m)]},
                {"name": names[2], "row": 2, "column": 2, "requires": [names[0]], "uniques": [f[2].format(m=m)]},
                {"name": f"{branch_name(p)} Complete", "uniques": [f[3].format(m=m)]}]})
        for i, pol in enumerate(out[-1]["policies"]):
            pol["civilopediaText"] = [{"text": member_pedia(p, i)[0]}]
    return out


def era_of_branch(p: dict) -> str:
    return "Rank One-Two era" if p["key"] in SLICE1_BRANCHES else FAMILY_ERA[p["family"]]


def halls() -> list[dict]:
    out = []
    for p in PATHS:
        era = era_of_branch(p)
        out.append({"name": hall_name(p), "requiredTech": ERA_TECH[era], "cost": ERA_COST[era], "maintenance": 2,
                    "culture": 1, "uniques": [f"Only available <after adopting [{branch_name(p)}]>",
                                              f"All newly-trained [Gu Master] units [in this city] receive the [{tier_name(p, 0)}] promotion"],
                    "civilopediaText": [{"text": hall_pedia(p)[0]}]})
    return out


def branch_pedia(p: dict) -> tuple[str, str]:
    fam, fam_id = FAMILY_TEXT[p["family"]]
    return (f"The {p['name'].lower()} path ({p['chinese']}) as a clan's tradition ({fam}): its Masters grow with every "
            f"policy of the branch, and it opens the {hall_name(p)}.",
            f"Jalur {p['name_id']} ({p['chinese']}) sebagai tradisi klan ({fam_id}): para Ahlinya menguat dengan setiap "
            f"kebijakan cabang ini, dan cabang ini membuka Aula Jalur {p['name_id']}.")


def hall_pedia(p: dict) -> tuple[str, str]:
    return (f"The clan's {p['name'].lower()}-path hall: every Gu Master trained in this city starts as a "
            f"{tier_name(p, 0)}. Needs the {branch_name(p)} policy branch.",
            f"Aula jalur {p['name_id']} milik klan: setiap Gu Master yang dilatih di kota ini langsung menjadi "
            f"{tier_name_id(p, 0)}. Butuh cabang kebijakan Jalur {p['name_id']}.")


def policy_translations() -> list[tuple[str, str]]:
    out = []
    for p in PATHS:
        out += [(hall_name(p), f"Aula Jalur {p['name_id']}"), hall_pedia(p)]
        if p["key"] in SLICE1_BRANCHES:
            continue
        out += [(branch_name(p), f"Jalur {p['name_id']}"), branch_pedia(p),
                (f"{branch_name(p)} Complete", f"Jalur {p['name_id']} Tuntas")] + member_names(p) + [
            member_pedia(p, i) for i in range(4)]
    return out


def translations() -> list[tuple[str, str]]:
    """(English, Indonesian) for every name and civilopedia text this module writes."""
    out = [(COMMENT, "Setiap jalur lain yang dipegang unit ini memotong Kekuatan: jejak dao saling mengganggu")]
    for p in PATHS:
        for t in range(MAX_TIER):
            out += [(tier_name(p, t), tier_name_id(p, t)), pedia(p, t)]
        out += [(p["mortal"], p["mortal_id"]), move_pedia(p)]
        if MAX_TIER > 2:
            out += [(p["immortal"], p["immortal_id"]), immortal_move_pedia(p)]
    for s in STATUSES:
        out += [(s["name"], s["name_id"]), (s["pedia"], s["pedia_id"])]
    for g in (g for g in PATH_GU if new_gu(g)):
        out += [(g["name"], g["name_id"]), (g["pedia"], g["pedia_id"])]
    return out + policy_translations()


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
    uniq = [f"Tiers 1-2 ship in Slice 1, tier 3 (Great Grandmaster, rank six) in MOD_SPEC_2 C3, tier 4 (Supreme Grandmaster, rank eight) in C5. Every Master also carries "
            "one hidden conflict line per later path whose pair costs Strength (`[relativeAmount]% Strength` "
            "`<for units with [promotion]>` `<hidden from users>`, values from data/path_conflicts.csv), a visible "
            "comment line and, where immortal Gu of its own or a strongly clashing path exist, its dao-mark lines.", "",
            "| Path | Master | Grandmaster | Mortal move status | Great Grandmaster | Immortal move status | Supreme Grandmaster |",
            "|---|---|---|---|---|---|---|"]
    for p in PATHS:
        master = [u for u in tier_uniques(p, 0) if not CONFLICT.match(u)]
        cells = [" ".join(code(u) for u in master), " ".join(code(u) for u in tier_uniques(p, 1)),
                 " ".join(code(u) for u in move_uniques(p)), " ".join(code(u) for u in tier_uniques(p, 2)),
                 " ".join(code(u) for u in move_uniques(p, immortal=True)), " ".join(code(u) for u in tier_uniques(p, 3))]
        uniq.append(f"| {p['name']} | " + " | ".join(cells) + " |")
    uniq += ["", "| Status | Uniques |", "|---|---|"]
    uniq += [f"| {s['name']} | " + " ".join(code(u) for u in split(s["uniques"])) + " |" for s in STATUSES]
    gu = ["Granted at a turn start to a unit holding the path's Master (the line is in the Master's column above), once "
          "the unit's rank reaches the Gu's and, for a food eater, "
          "while that food is in surplus. Moonlight Gu, White Boar Gu and the Liquor Worm are the Slice 1 Gu.", "",
          "| Path | Gu | Chinese | Rank | Food | Uniques | Verdict | Source |", "|---|---|---|---|---|---|---|---|"]
    built = {d["name"]: d for d in gu_promotions()}
    for g in PATH_GU:
        uniques = " ".join(code(u) for u in built[g["name"]]["uniques"]) if g["name"] in built else "Slice 1 Gu"
        gu.append(f"| {KEY[g['path']]['name']} | {g['name']} | {g['chinese'] or '—'} | {g['rank']} | {g['food'] or 'stones'} "
                  f"| {uniques} | {g['verdict']} | {g['source']} |")
    br = ["| Branch | Era | Opener | Policies (Lineage, Insight, Doctrine) | Complete | Hall |", "|---|---|---|---|---|---|"]
    halls_by = {h["name"]: h for h in halls()}
    for d in policy_branches():
        pol = d["policies"]
        key = next(p for p in PATHS if branch_name(p) == d["name"])
        hall = halls_by[hall_name(key)]
        br.append(f"| {d['name']} | {d['era']} | " + " ".join(code(u) for u in d["uniques"]) + " | "
                  + " ".join(code(u) for x in pol[:3] for u in x["uniques"]) + " | " + code(pol[3]["uniques"][0]) + " | "
                  + " ".join(code(u) for u in hall["uniques"]) + " |")
    for name in ("Moon", "Strength"):
        h = halls_by[f"{name} Hall"]
        br.append(f"| {name} Path (Slice 1) | Rank One-Two era | see LORE_MAPPING | — | — | " + " ".join(code(u) for u in h["uniques"]) + " |")
    return {"paths": "\n".join(paths), "families": "\n".join(fams), "moves": "\n".join(moves), "uniques": "\n".join(uniq),
            "gu": "\n".join(gu), "branches": "\n".join(br)}


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
