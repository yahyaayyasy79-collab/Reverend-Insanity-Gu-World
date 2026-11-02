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
import path_powers as PP  # noqa: E402  (power scaling: data/path_powers.csv)
import sound_names as sfx  # noqa: E402  (sound file names; tools/art/sfx.py synthesizes the files)
import gu_catalog as GC  # noqa: E402  (Phase D: the Gu catalog, data/gu_catalog.csv)
import gu_combos as GCO  # noqa: E402  (Phase D: combination killer moves, data/gu_combos.csv)

DATA = REPO_ROOT / "data"
DOC = REPO_ROOT / "docs" / "PATHS.md"

# Tiers: MOD_SPEC_3 C3 put tiers 1-2 into Slice 1; MOD_SPEC_2 C3 added the Great Grandmaster (rank six, the immortal
# move) and C5 the Supreme Grandmaster (rank eight).
MAX_TIER = 4
TIERS = ["Master", "Grandmaster", "Great Grandmaster", "Supreme Grandmaster"]
TIERS_ZH = ["大师", "宗师", "大宗师", "无上大宗师"]
TIERS_ID = ["Ahli", "Mahaguru", "Mahaguru Agung", "Mahaguru Tertinggi"]
TIER_STRENGTH = [20, 25, 30, 35]  # Phase D power rebuild: comprehension carries more (was 10/15/20/25)
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
# Phase D power scaling (the user, 2026-11-02): each path's hit, tier unlocks and peak (tools/path_powers.py)
POWERS = {r["key"]: r for r in table("path_powers.csv")}
assert set(POWERS) == set(KEY), "data/path_powers.csv needs exactly one row per path"
PP.STATUS_ID.update({s["name"]: s["name_id"] for s in STATUSES})
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
    marked = {g["path"] for g in IMMORTAL_GU} | {r["path"] for r in GC.IMMORTAL_ROWS}  # Phase D: catalog wonders too
    out = [f"[+{DAO_MARK}]% Strength <for every [1] [[{path_marker(p['key'])}] Buildings]>"] if p["key"] in marked else []
    for (a, b), v in pair_strength().items():
        if v <= STRONG_CLASH and p["key"] in (a, b):
            other = b if a == p["key"] else a
            if other in marked:
                out.append(f"[{DAO_CLASH}]% Strength <for every [1] [[{path_marker(other)}] Buildings]>")
    return out


def move_uniques(p: dict, immortal: bool = False) -> list[str]:
    name = p["immortal" if immortal else "mortal"]
    return [u.replace("{n}", name) for u in split(FAMILIES[p["family"]]["immortal_uniques" if immortal else "mortal_uniques"])] \
        + [PP.move_burst(POWERS[p["key"]], immortal),
           # the Gu attack's own sound when the move is used (a human player hears it; tools/art/sfx.py)
           f"Play [{sfx.move_sound(p['key'], immortal)}] sound <upon gaining the [{name}] status>"]


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


def hunger_rank(g: dict) -> int:
    return min(int(g["rank"]), 4)  # data/hunger.csv has ranks 1-4


def gu_promotions() -> list[dict]:
    """The new path Gu: a food eater follows the Slice 1 hunger meter (tools/gu_rules.py, with its percent statuses),
    the others eat stones (their upkeep); every Gu says what it eats (a visible comment)."""
    from gu_rules import gu_promotion, hunger_statuses, items, stone_comment
    out, statuses = [], []
    for g in (g for g in PATH_GU if new_gu(g)):
        if g["food"]:
            d = gu_promotion({**g, "rank": str(hunger_rank(g)), "extra_uniques": ""})
            statuses += hunger_statuses(g["name"], g["food"], hunger_rank(g))
        else:
            d = {"name": g["name"], "uniques": [f"Comment [{stone_comment(int(g['upkeep'] or 0))[0]}]"] + items(g["effects"])
                 + ([f"[+{g['upkeep']}]% maintenance costs"] if g["upkeep"] != "0" else [])}
        d["civilopediaText"] = [{"text": g["pedia"]}]
        out.append(d)
    return out + statuses


def all_food_gu() -> list[tuple[str, str, str, str, str]]:
    """(name, Indonesian name, food, hunger rank, eats) of every Gu with a hunger meter: Slice 1's and the path Gu."""
    from gu_rules import table as gtable
    out = [(r["name"], "", r["food"], r["rank"], r["eats"]) for r in gtable("gu.csv")]
    out += [(g["name"], g["name_id"], g["food"], str(hunger_rank(g)), g["eats"]) for g in PATH_GU if new_gu(g) and g["food"]]
    return out + GC.food_gu()


def tier_uniques(p: dict, t: int) -> list[str]:
    pw = POWERS[p["key"]]
    u = [f"[+{TIER_STRENGTH[t]}]% Strength"]
    if t == 0:
        u = ([p["signature"]] + u + PP.hit_lines(pw) + conflict_lines(p) + [f"Comment [{COMMENT}]", MARKER]
             + [grant(g) for g in GU_OF[p["key"]]] + dao_mark_lines(p))
    if t == 1:
        u += PP.cell(pw, "gm") + [f"[This Unit] gains the [{p['mortal']}] status for [1] turn(s) {MOVE_COST}"]
    if t == 2:
        u += PP.cell(pw, "ggm") + [f"[This Unit] gains the [{p['immortal']}] status for [1] turn(s) {IMMORTAL_MOVE_COST}"]
    if t == 3:
        u += PP.cell(pw, "sup") + SUPREME_EXTRA.get(p["key"], []) + [SUPREME_MARKER]
    # the path's sound on every attack, from the highest tier held only (tools/art/sfx.py: each tier adds a layer)
    u.append(f"Play [{sfx.path_sound(p['key'], t + 1)}] sound {PP.UPON_HIT} {PP.ATTACK}"
             + (f" <for units without [{tier_name(p, t + 1)}]>" if t + 1 < MAX_TIER else ""))
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
    """The tier's lore line, then what it does (written from the uniques by tools/path_powers.py)."""
    en, idt = _pedia_lore(p, t)
    pw = POWERS[p["key"]]
    if t == 0:
        sig, hit = PP.describe(p["signature"]), PP.hit_summary(pw)
        return (f"{en} +10% strength. Signature: {sig[0]}. Hit: {hit[0]}.",
                f"{idt} +10% kekuatan. Ciri khas: {sig[1]}. Serangan: {hit[1]}.")
    label = {1: ("unlocks", "membuka"), 2: ("adds", "menambah"), 3: ("peak", "puncak")}[t]
    eff = PP.describe_all(PP.cell(pw, ("gm", "ggm", "sup")[t - 1]))
    return (f"{en} +{TIER_STRENGTH[t]}% strength; {label[0]}: {eff[0]}.",
            f"{idt} +{TIER_STRENGTH[t]}% kekuatan; {label[1]}: {eff[1]}.")


def _pedia_lore(p: dict, t: int) -> tuple[str, str]:
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
    b = PP.describe(PP.move_burst(POWERS[p["key"]], True))
    return (f"{p['immortal']}{zh}: a {p['name'].lower()}-path immortal killer move for one turn: {f['immortal_text']}; "
            f"{b[0]}.",
            f"{p['immortal_id']}{zh}: jurus pamungkas abadi jalur {p['name_id']} selama satu giliran: "
            f"{f['immortal_text_id']}; {b[1]}.")


def move_pedia(p: dict) -> tuple[str, str]:
    zh = f" ({p['mortal_zh']})" if p["mortal_zh"] else ""
    f = FAMILIES[p["family"]]
    b = PP.describe(PP.move_burst(POWERS[p["key"]], False))
    return (f"{p['mortal']}{zh}: a {p['name'].lower()}-path killer move for one turn: {f['mortal_text']}; {b[0]}.",
            f"{p['mortal_id']}{zh}: jurus pamungkas jalur {p['name_id']} selama satu giliran: {f['mortal_text_id']}; "
            f"{b[1]}.")


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
BRANCH_ERA = "Rank One-Two era"
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
            # the user (2026-11-02): "kebijakannya terbuka semua tanpa harus memandang era": every branch opens in the
            # first era; the halls still wait for their family's tech (halls())
            "name": branch_name(p), "era": BRANCH_ERA,
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
        # no upkeep: the AI builds a hall in every city, and at 2 stones each 12 of 24 Slice 1 clans spent 20+ turns in
        # the red against 4 of 24 without it (autoplay A/B, 6 x 320, Prince)
        out.append({"name": hall_name(p), "requiredTech": ERA_TECH[era], "cost": ERA_COST[era],
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
    from gu_rules import hunger_translations, stone_comment
    out += hunger_translations(all_food_gu())
    out += [stone_comment(u) for u in sorted({int(g["upkeep"] or 0) for g in PATH_GU if new_gu(g) and not g["food"]} | {10})]
    return out + GC.translations() + GCO.translations() + policy_translations() + tutorial_translations()


# ---------------- Tutorials (Civilopedia > Tutorials): the power-scaling pages (Phase D) ----------------
RANKS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8}
NUM_ID = {"One": "Satu", "Two": "Dua", "Three": "Tiga", "Four": "Empat", "Five": "Lima", "Six": "Enam", "Seven": "Tujuh",
          "Eight": "Delapan"}


def rank_strengths() -> list[tuple[str, str, int]]:
    rows = [r for r in table("gu_masters.csv") if r["name"].startswith("Rank ") and not r["uniqueTo"]
            and not r.get("legacyPath")]
    out = []
    for r in rows:
        word = r["name"].split()[1]
        out.append((f"Rank {word}", f"Tingkat {NUM_ID[word]}", PP.body_strength(int(r["strength"]), RANKS[word])))
    return out + [("the Venerable", "Yang Mulia", PP.VENERABLE_STRENGTH)]


def _lines_power() -> list[tuple[str, str, dict]]:
    ranks = rank_strengths()
    fire = POWERS["fire"]
    d, T = PP.DAO_STRENGTH, TIER_STRENGTH
    L = [("The five layers of power", "Lima lapis kekuatan", {"header": 2}),
         ("A cultivator's body alone is weak: most of its power comes from its Gu, its dao marks and its comprehension of "
          "its path. One who fights without Gu still fights, on dao marks and comprehension alone.",
          "Tubuh seorang kultivator saja lemah: sebagian besar kekuatannya datang dari Gu, jejak dao, dan pemahamannya "
          "atas jalurnya. Yang bertarung tanpa Gu tetap bisa bertarung, hanya dengan jejak dao dan pemahaman.", {}),
         ("1. Rank. The body's strength: " + ", ".join(f"{e} {v}" for e, _, v in ranks) + ". Clan Masters of a rank "
          "have the same strength.",
          "1. Tingkat. Kekuatan tubuh: " + ", ".join(f"{i} {v}" for _, i, v in ranks) + ". Gu Master klan pada tingkat "
          "yang sama punya kekuatan yang sama.", {}),
         (f"2. Path attainment (comprehension). Four tiers stack: Master +{T[0]}% at any rank, Grandmaster +{T[1]}% from "
          f"rank three, Great Grandmaster +{T[2]}% from rank six, Supreme Grandmaster +{T[3]}% from rank eight: "
          f"+{sum(T)}% at the top. Each "
          "tier opens a new kind of power: the Master the path's hit on every attack it makes, the Grandmaster a second effect and "
          "the mortal killer move, the Great Grandmaster a domain or a new art and the immortal killer move, the Supreme "
          "Grandmaster the path's peak.",
          f"2. Pencapaian jalur (pemahaman). Empat tingkat bertumpuk: Ahli +{T[0]}% di tingkat mana pun, Mahaguru +{T[1]}% "
          f"sejak tingkat tiga, Mahaguru Agung +{T[2]}% sejak tingkat enam, Mahaguru Tertinggi +{T[3]}% sejak tingkat "
          f"delapan: +{sum(T)}% di puncak. Tiap tingkat membuka jenis kekuatan baru: Ahli membuka serangan khas jalur pada setiap serangan, "
          "Mahaguru efek kedua dan jurus pamungkas fana, Mahaguru Agung sebuah domain atau seni baru dan jurus pamungkas "
          "abadi, Mahaguru Tertinggi puncak jalur itu.", {}),
         ("3. Dao marks, the quantity of dao. Tiers I to V give " + ", ".join(d[0]) + ". Every tier also raises the "
          "path's hit: extra damage " + "/".join(map(str, PP.SCALE['dmg'])) + ", status turns "
          + "/".join(map(str, PP.SCALE['dur'])) + ", healing " + "/".join(map(str, PP.SCALE['heal'])) + ", XP "
          + "/".join(map(str, PP.SCALE['xp'])) + ", stolen stones " + "/".join(map(str, PP.SCALE['earn'])) + "%, movement "
          + "/".join(map(str, PP.SCALE['movegain'])) + " (no marks, then I to V; a path may multiply them). The Master's "
          "promotion lists what each tier adds.",
          "3. Jejak dao, kuantitas dao. Tingkat I sampai V memberi " + ", ".join(d[1]) + ". Tiap tingkat juga menaikkan "
          "serangan khas jalur: kerusakan tambahan " + "/".join(map(str, PP.SCALE['dmg'])) + ", lama status "
          + "/".join(map(str, PP.SCALE['dur'])) + " giliran, pemulihan " + "/".join(map(str, PP.SCALE['heal'])) + ", XP "
          + "/".join(map(str, PP.SCALE['xp'])) + ", batu curian " + "/".join(map(str, PP.SCALE['earn'])) + "%, gerak "
          + "/".join(map(str, PP.SCALE['movegain'])) + " (tanpa jejak, lalu I sampai V; sebagian jalur mengalikannya). "
          "Promosi Ahli menuliskan tambahan tiap tingkat.", {}),
         ("Dao marks grow one tier every 20 turns on Standard for a path Master of rank three or more; an immortal also "
          "gains one for every immortal it kills and every heavenly tribulation it survives. Mortals stop at tier II. "
          "Rank seven needs tier II, rank eight tier III, the Venerable tier IV.",
          "Jejak dao naik satu tingkat tiap 20 giliran pada kecepatan Standar bagi Ahli jalur tingkat tiga ke atas; "
          "seorang abadi juga mendapat satu dari setiap abadi yang dibunuhnya dan setiap kesengsaraan langit yang "
          "dilaluinya. Manusia fana berhenti di tingkat II. Tingkat tujuh butuh tingkat II, tingkat delapan III, Yang "
          "Mulia IV.", {}),
         (f"4. Gu. Each path's Gu comes with its Master. A Master refines more with XP: {len(GC.ROWS)} catalog Gu of "
          "ranks 1 to 9, each waiting for a unit of its rank; a Gu's effect grows with its rank (a rank-one attack Gu "
          f"+{GC.effects({'rank': '1', 'role': 'atk'})[0][1].split('%')[0]}%, a rank-nine one "
          f"+{GC.effects({'rank': '9', 'role': 'atk'})[0][1].split('%')[0]}%). Immortal Gu sleep while the clan has no "
          "immortal essence of their rank. Every immortal Gu wonder of your own path that your clan owns adds 5% "
          "strength; one of a strongly clashing path takes 5% away.",
          f"4. Gu. Gu tiap jalur datang bersama Ahlinya. Seorang Ahli memurnikan lebih banyak dengan XP: {len(GC.ROWS)} "
          "Gu katalog tingkat 1 sampai 9, masing-masing menunggu unit setingkatnya; efek Gu tumbuh dengan tingkatnya "
          f"(Gu serang tingkat satu +{GC.effects({'rank': '1', 'role': 'atk'})[0][1].split('%')[0]}%, tingkat sembilan "
          f"+{GC.effects({'rank': '9', 'role': 'atk'})[0][1].split('%')[0]}%). Gu abadi tertidur bila klan tak punya "
          "esensi abadi setingkatnya. Setiap keajaiban Gu abadi dari jalurmu sendiri yang dimiliki klanmu menambah 5% "
          "kekuatan; dari jalur yang sangat bertentangan mengurangi 5%.", {}),
         ("5. Conflicts. A second path whose dao marks clash with the first costs 5% to 25% strength.",
          "5. Pertentangan. Jalur kedua yang jejak daonya berbenturan dengan jalur pertama memotong 5% sampai 25% "
          "kekuatan.", {}),
         ("Killer moves", "Jurus pamungkas", {"header": 3}),
         ("A unit-action button, so only you use them: for one turn the path family's burst plus the path's hit at full "
          "power (twice that for the immortal move). The mortal move costs 15 stones, the immortal move 5 green grape "
          "essence.",
          "Tombol aksi unit, jadi hanya kamu yang memakainya: selama satu giliran ledakan keluarga jalur ditambah "
          "serangan khas jalur pada kekuatan penuh (dua kali lipat untuk jurus abadi). Jurus fana 15 batu, jurus abadi "
          "5 esensi anggur hijau.", {})]
    # a worked example from the data
    ex = [r for _, _, r in ranks][5]
    hit = PP.describe(PP.attack_only(fire["hit"]).replace("{n}", str(PP.amounts(fire)[3])))
    gm, ggm = PP.describe_all(PP.cell(fire, "gm")), PP.describe_all(PP.cell(fire, "ggm"))
    L += [("Example", "Contoh", {"header": 3}),
          (f"A Rank Six fire-path Great Grandmaster with Dao Marks III: strength {ex}, +{sum(T[:3])}% from attainment "
           f"and {d[0][2]} from dao marks. {hit[0][0].upper() + hit[0][1:]}; {gm[0]}; {ggm[0]}.",
           f"Gu Abadi tingkat enam jalur api, Mahaguru Agung, dengan Jejak Dao III: kekuatan {ex}, +{sum(T[:3])}% dari "
           f"pencapaian dan {d[1][2]} dari jejak dao. {hit[1][0].upper() + hit[1][1:]}; {gm[1]}; {ggm[1]}.", {})]
    return L


def _lines_family(k: str) -> list[tuple[str, str, dict]]:
    L = []
    for p in (p for p in PATHS if p["family"] == k):
        pw = POWERS[p["key"]]
        sig, hit = PP.describe(p["signature"]), PP.hit_summary(pw)
        gm, ggm, sup = (PP.describe_all(PP.cell(pw, c)) for c in ("gm", "ggm", "sup"))
        mb, ib = PP.describe(PP.move_burst(pw, False)), PP.describe(PP.move_burst(pw, True))
        f = FAMILIES[k]
        L += [(f"{p['name']} path ({p['chinese']})", f"Jalur {p['name_id']} ({p['chinese']})", {"header": 3}),
              (f"Signature: {sig[0]}.", f"Ciri khas: {sig[1]}.", {}),
              (f"Master, +10%: {hit[0]}.", f"Ahli, +10%: {hit[1]}.", {}),
              (f"Grandmaster, +15%: {gm[0]}. Killer move {p['mortal']}: {f['mortal_text']}; {mb[0]}.",
               f"Mahaguru, +15%: {gm[1]}. Jurus pamungkas {p['mortal_id']}: {f['mortal_text_id']}; {mb[1]}.", {}),
              (f"Great Grandmaster, +20%: {ggm[0]}. Immortal move {p['immortal']}: {f['immortal_text']}; {ib[0]}.",
               f"Mahaguru Agung, +20%: {ggm[1]}. Jurus abadi {p['immortal_id']}: {f['immortal_text_id']}; {ib[1]}.", {}),
              (f"Supreme Grandmaster, +25%: {sup[0]}.", f"Mahaguru Tertinggi, +25%: {sup[1]}.", {})]
    return L


def _lines_statuses() -> list[tuple[str, str, dict]]:
    return [("What a path's hit leaves on its target. A status ticks at the start of the target's own turn.",
             "Apa yang ditinggalkan serangan khas jalur pada sasarannya. Status berkurang di awal giliran sasaran itu "
             "sendiri.", {})] + [(f"{s['name']}: {s['pedia']}", f"{s['name_id']}: {s['pedia_id']}", {}) for s in STATUSES]


def _lifespan_effects() -> list[tuple[str, str, str, str]]:
    """(name, Indonesian name, effect EN, effect ID) of every immortal Gu and inheritance that gives or takes Lifespan Gu."""
    rx = re.compile(r"Instantly (provides|consumes) \[(\d+)\] \[Lifespan Gu\] <upon turn start> <every \[(\d+)\] turns>"
                    r"( <when above \[(\d+)\] \[Green Grape Immortal Essence\]>)?")
    out = []
    for row, name, name_id in ([(r, r["name"], r["name_id"]) for r in IMMORTAL_GU]
                               + [(r, r["name"], r["name_id"]) for r in table("inheritances.csv")]):
        for cell in row.values():
            for m in rx.finditer(cell or ""):
                give, n, k, _, ess = m.groups()
                en = f"{'gives' if give == 'provides' else 'takes'} {n} every {k} turns"
                idt = f"{'memberi' if give == 'provides' else 'mengambil'} {n} tiap {k} giliran"
                cost = re.search(r"Instantly consumes \[(\d+)\] \[Green Grape Immortal Essence\] <upon turn start> "
                                 rf"<every \[{k}\] turns>", cell)
                if cost:
                    en += f" for {cost.group(1)} green grape essence"
                    idt += f" dengan {cost.group(1)} esensi anggur hijau"
                if ess:
                    en += f" while the clan holds more than {ess}"
                    idt += f" selama klan memegang lebih dari {ess}"
                out.append((name, name_id, en, idt))
    return out


def _lines_lifespan() -> list[tuple[str, str, dict]]:
    import lifespan as LS
    from gu_rules import ID_NAMES
    strength = [v for _, _, v in rank_strengths()]  # ranks one to eight, then the Venerable
    ranks = {r: strength[r - 1] for r in (5, 6, 7, 8)}
    L = [("How long an immortal lives", "Berapa lama seorang abadi hidup", {"header": 2}),
         ("A clan's Lifespan Gu are its immortals' lifespan. Reaching each rank adds to the stock and a higher rank burns "
          "it more slowly, so every rank climbed makes an immortal live longer. Numbers on Standard speed; the other "
          "speeds scale the turns.",
          "Gu Umur milik klan adalah umur para abadinya. Setiap rank yang dicapai menambah stok itu, dan rank yang lebih "
          "tinggi membakarnya lebih lambat, jadi setiap kenaikan rank memperpanjang hidup seorang abadi. Angka pada "
          "kecepatan Standar; kecepatan lain menyesuaikan jumlah giliran.", {})]
    for r in (6, 7, 8, 9):
        en, idt = LS.RANK_NAME[r]
        how = {6: ("on ascending", "saat naik menjadi abadi"), 7: ("on advancing", "saat naik rank"),
               8: ("on advancing", "saat naik rank"), 9: ("on becoming a Venerable", "saat menjadi Yang Mulia")}[r]
        L.append((f"{en}: +{LS.GRANT[r]} Lifespan Gu {how[0]}; burns one every {LS.BURN[r]} turns, so its own gift lasts "
                  f"about {LS.lasts(r)} turns.",
                  f"{idt}: +{LS.GRANT[r]} Gu Umur {how[1]}; membakar satu tiap {LS.BURN[r]} giliran, jadi pemberiannya "
                  f"sendiri bertahan sekitar {LS.lasts(r)} giliran.", {}))
    L += [("All the clan's immortals share one stock, each burning at its own rank's rate. With none left an immortal "
           f"wastes away ({LS.STARVE_DAMAGE} damage a turn) and heals only by pillaging; one Lifespan Gu ends that at once.",
           "Semua abadi klan berbagi satu stok, masing-masing membakar menurut rank-nya. Bila habis, seorang abadi merana "
           f"({LS.STARVE_DAMAGE} kerusakan per giliran) dan hanya pulih dengan menjarah; satu Gu Umur langsung "
           "menghentikannya.", {}),
          ("How to add lifespan", "Cara menambah umur", {"header": 3}),
          ("1. Climb. Every rank reached adds Lifespan Gu (above): the surest way.",
           "1. Naik rank. Setiap rank yang dicapai menambah Gu Umur (di atas): cara paling pasti.", {}),
          (f"2. Green land. From Calamity Lore, every {LS.WILD_TILES} owned forest, jungle or marsh tiles of each kind give "
           f"one with a {LS.WILD_CHANCE}% chance each turn: keep your woods and swamps, settle near them.",
           f"2. Tanah hijau. Sejak {ID_NAMES.get('Calamity Lore')}, setiap {LS.WILD_TILES} petak hutan, rimba, atau rawa milikmu (per jenis) "
           f"memberi satu dengan peluang {LS.WILD_CHANCE}% tiap giliran: jaga hutan dan rawamu, bangun desa di dekatnya.", {})]
    gives = [x for x in _lifespan_effects() if x[2].startswith("gives")]
    L.append(("3. Immortal Gu and inheritances: " + "; ".join(f"{n} {e}" for n, _, e, _ in gives) + ".",
              "3. Gu abadi dan warisan: " + "; ".join(f"{i or n} {d}" for n, i, _, d in gives) + ".", {}))
    L += [(f"4. The market. Treasure Yellow Heaven sells {LS.MARKET_GU} Lifespan Gu for {LS.MARKET_PRICE} stones.",
           f"4. Pasar. Treasure Yellow Heaven menjual {LS.MARKET_GU} Gu Umur seharga {LS.MARKET_PRICE} batu.", {}),
          ("5. Conquest. A captured city keeps its immortal Gu and inheritances, so the ones above can be seized.",
           "5. Penaklukan. Kota yang direbut tetap memegang Gu abadi dan warisannya, jadi yang di atas bisa direbut.", {}),
          ("What takes lifespan", "Apa yang menghabiskan umur", {"header": 3})]
    for name, name_id, en, idt in _lifespan_effects():
        if en.startswith("takes"):
            L.append((f"{name}: {en}.", f"{name_id or name}: {idt}.", {}))
    L += [(f"While a Venerable lives, every clan loses one each {LS.DREAD_TURNS} turns.",
           f"Selama seorang Yang Mulia hidup, setiap klan kehilangan satu tiap {LS.DREAD_TURNS} giliran.", {}),
          ("The Zombie Alliance's immortals never age (it gains one per immortal each 10 turns) but make no essence.",
           "Para abadi Aliansi Mayat Hidup tak pernah menua (mendapat satu per abadi tiap 10 giliran) tetapi tak menghasilkan "
           "esensi.", {}),
          ("Immortals against mortal clans", "Abadi melawan klan fana", {"header": 3}),
          (f"An immortal outclasses any mortal army: strength {ranks[6]}, {ranks[7]} and {ranks[8]} at ranks six to eight "
           f"against {ranks[5]} at rank five, before its path, and it crosses the region walls. That is the reward for a long, hard "
           "climb: ascension needs a rank-five Master, the three qi and luck, and every rank above needs a survived "
           "tribulation, dao marks and essence.",
           f"Seorang abadi jauh melampaui pasukan fana mana pun: kekuatan {ranks[6]}, {ranks[7]}, dan {ranks[8]} pada rank "
           f"enam sampai delapan melawan {ranks[5]} pada rank lima, belum termasuk jalurnya, dan ia menembus tembok wilayah. Itulah "
           "imbalan pendakian yang panjang dan berat: kenaikan abadi butuh Ahli rank lima, tiga qi, dan keberuntungan, dan "
           "setiap rank di atasnya butuh selamat dari kesengsaraan, jejak dao, dan esensi.", {})]
    return L


def _lines_hunger() -> list[tuple[str, str, dict]]:
    from gu_rules import HUNGER_RANKS, ID_NAMES, stages
    L = [("Every Gu eats", "Setiap Gu makan", {"header": 2}),
         ("A Gu that eats a Gu food (moon orchid, wild boar, jade or wine) takes it from the clan's stock every turn. "
          "When the clan is short, every Gu eating that food is weakened at once and its hunger meter rises each turn: a "
          "status on the unit shows the percent. At 100% the Gu rolls its chance to die, then the meter starts again. "
          "Feed the clan and the meter clears.",
          "Gu yang memakan makanan Gu (anggrek bulan, babi hutan, giok, atau arak) mengambilnya dari stok klan setiap "
          "giliran. Bila klan kekurangan, setiap Gu pemakan makanan itu langsung melemah dan meteran laparnya naik tiap "
          "giliran: sebuah status di unit menunjukkan persennya. Pada 100% Gu itu melempar peluang matinya, lalu meteran "
          "mulai lagi. Beri makan klan dan meteran itu hilang.", {}),
         ("Hunger rate by rank: " + ", ".join(f"rank {r} +{stages(r)[0]}% a turn ({HUNGER_RANKS[r][1]}% death chance at 100%)"
                                            for r in sorted(HUNGER_RANKS)) + ". The lower the rank, the faster the hunger.",
          "Laju lapar per rank: " + ", ".join(f"rank {r} +{stages(r)[0]}% per giliran (peluang mati {HUNGER_RANKS[r][1]}% "
                                              f"pada 100%)" for r in sorted(HUNGER_RANKS)) + ". Makin rendah rank-nya, makin "
          "cepat laparnya.", {}),
         ("Where the food comes from: moon orchid and wild boar from their improved tiles and the Gu Feeding House, jade "
          "from mined jade, wine only from the Tavern.",
          f"Asal makanan: anggrek bulan dan babi hutan dari petaknya yang dikelola dan {ID_NAMES['Gu Feeding House']}, "
          f"giok dari tambang giok, arak hanya dari {ID_NAMES['Tavern']}.", {}),
         ("Other Gu eat primeval stones: each raises its unit's upkeep, usually by 10%. When the clan's stones fall below "
          "zero, every unit fights 20% weaker.",
          "Gu lain memakan batu primordial: masing-masing menaikkan pemeliharaan unitnya, biasanya 10%. Bila batu klan "
          "di bawah nol, setiap unit bertarung 20% lebih lemah.", {}),
         ("Every Gu with a hunger meter", "Setiap Gu dengan meteran lapar", {"header": 3})]
    for name, name_id, food, rank, eats in all_food_gu():
        r = int(rank)
        L.append((f"{name}: {eats} {food} a turn; hunger +{stages(r)[0]}% a turn.",
                  f"{name_id or ID_NAMES.get(name, name)}: {eats} {ID_NAMES.get(food, food)} per giliran; lapar "
                  f"+{stages(r)[0]}% per giliran.", {}))
    stone = sorted(g["name"] for g in PATH_GU if new_gu(g) and not g["food"]) + ["Bear Strength Gu", "Stream Gu"]
    L += [("Gu that eat stones", "Gu pemakan batu", {"header": 3}),
          (", ".join(sorted(stone)) + ".", ", ".join(sorted(ID_NAMES.get(n) or next(
              (g["name_id"] for g in PATH_GU if g["name"] == n), n) for n in stone)) + ".", {})]
    return L


def _tutorial_specs() -> list[tuple[str, str, list]]:
    out = [("Gu World: Power Scaling", "Dunia Gu: Skala Kekuatan", _lines_power()),
           ("Gu World: Immortal Lifespan", "Dunia Gu: Umur Abadi", _lines_lifespan()),
           ("Gu World: Gu Hunger and Food", "Dunia Gu: Lapar dan Makanan Gu", _lines_hunger())]
    out += [(f"Gu World: {f['name'].replace('&', 'and')} Paths", f"Dunia Gu: Jalur {f['name_id'].replace('&', 'dan')}",
             _lines_family(k)) for k, f in FAMILIES.items()]
    out.append(("Gu World: Statuses", "Dunia Gu: Status", _lines_statuses()))
    out.append(("Gu World: Combination Killer Moves", "Dunia Gu: Jurus Pamungkas Kombinasi", GCO.tutorial_lines()))
    return out


def tutorials() -> list[dict]:
    """jsons/Tutorials.json: added to the game's own tutorials (a base ruleset's file extends them)."""
    return [{"name": n, "civilopediaText": [{"text": en, **extra} for en, _, extra in lines]}
            for n, _, lines in _tutorial_specs()]


def tutorial_translations() -> list[tuple[str, str]]:
    out = []
    for n, n_id, lines in _tutorial_specs():
        out.append((n, n_id))
        out += [(en, idt) for en, idt, _ in lines]
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
    pw = ["| Path | Signature | Master hit (no marks; dao marks I-V) | Grandmaster | Great Grandmaster | Supreme Grandmaster |",
          "|---|---|---|---|---|---|"]
    for p in PATHS:
        q = POWERS[p["key"]]
        pw.append(f"| {p['name']} | {PP.describe(p['signature'])[0]} | {PP.hit_summary(q)[0]} | "
                  + " | ".join(PP.describe_all(PP.cell(q, c))[0] for c in ("gm", "ggm", "sup")) + " |")
    from gu_rules import hunger_statuses, stages
    hu = ["| Gu | Food | Hunger rank | Steps | Each step's uniques |", "|---|---|---|---|---|"]
    for name, _, food, rank, eats in all_food_gu():
        st = hunger_statuses(name, food, int(rank))
        hu.append(f"| {name} | {eats} {food} | {rank} | " + ", ".join(f"{p}%" for p in stages(int(rank))) + " | "
                  + " ".join(code(u) for x in st for u in x["uniques"]) + " |")
    return {"paths": "\n".join(paths), "families": "\n".join(fams), "moves": "\n".join(moves), "uniques": "\n".join(uniq),
            "gu": "\n".join(gu), "branches": "\n".join(br), "powers": "\n".join(pw), "hunger": "\n".join(hu),
            "catalog": "\n".join(GC.doc_table() + GC.canon_bearer_table()), "combos": "\n".join(GCO.doc_table())}


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
