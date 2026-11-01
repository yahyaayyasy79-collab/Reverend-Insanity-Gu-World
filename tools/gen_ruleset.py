#!/usr/bin/env python3
"""Generate the Slice 1 ruleset (jsons/*.json) from data/*.csv and the structured content below (MOD_SPEC section 9).

  tools/gen_ruleset.py                 # writes <repo>/jsons, the mod itself; commit data/ and jsons/ together
  tools/gen_ruleset.py --out DIR       # writes DIR/jsons, a throwaway copy (experiments, autoplay variants)
  tools/gen_ruleset.py --check         # exit 1 if <repo>/jsons differs from what the tables generate

Tables (data/): tech_columns.csv + techs.csv (tech tree), gu_masters.csv (Gu Master units: the rank chain, the
signature clans' chains, the hidden legacy path x rank units), paths*.csv (via tools/gen_paths.py), gu.csv (Gu
promotions: effects, food, rank), gu_foods.csv (food -> hunger status), hunger.csv (the hunger meter per rank: status
length and death chance, the user's main tuning lever). civilopedia.csv: the English civilopedia text of every object (its
Indonesian column feeds tools/gen_translations.py). One-of-a-kind content stays below. docs/LORE_MAPPING.md is the
design record; tools/tests checks that it quotes exactly the uniques generated here. Comments marked R2/R3/R4 record
design rounds (docs/LORE_MAPPING.md, "How this plan was made").
"""
import argparse
import csv
import filecmp
import json
import os
import sys
import tempfile
from pathlib import Path

import json5

import gen_paths
from common import REPO_ROOT, VANILLA_JSONS

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--out", help="mod folder to write into (default: the repo root)")
ap.add_argument("--check", action="store_true", help="only compare the repo's jsons/ with a fresh generation")
ap.add_argument("--quiet", action="store_true")
ARGS = ap.parse_args()
TARGET = Path(ARGS.out).resolve() if ARGS.out else REPO_ROOT
_TMP = tempfile.TemporaryDirectory() if ARGS.check else None
OUT = os.path.join(_TMP.name if _TMP else str(TARGET), "jsons")
DATA = REPO_ROOT / "data"
VAN = str(VANILLA_JSONS)
os.makedirs(OUT, exist_ok=True)
ALL_UNIQUES = []
WRITTEN = []


def table(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    # an unquoted comma splits a cell and shifts the rest into extra columns (the audit found four such rows)
    bad = [r.get(next(iter(r))) for r in rows if None in r or None in r.values()]
    if bad:
        raise SystemExit(f"data/{name}: rows with the wrong number of columns (quote cells holding commas): {bad}")
    return rows


def items(cell):
    """A list cell: entries separated by '|' (no unique contains that character)."""
    return [x for x in cell.split("|") if x] if cell else []


def collect(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("uniques", "friendBonusUniques", "allyBonusUniques") and isinstance(v, list):
                ALL_UNIQUES.extend(v)
            else:
                collect(v)
    elif isinstance(o, list):
        for x in o:
            collect(x)


PEDIA = {}  # (file, object name) -> English civilopedia text, from data/civilopedia.csv


def pedia(name, obj):
    """Attach civilopediaText to every object of this file that has an entry (techs and policies are nested)."""
    if not PEDIA:
        PEDIA.update({(r["file"], r["name"]): r["en"] for r in table("civilopedia.csv")})
    items = obj if isinstance(obj, list) else []
    if name == "Techs.json":
        items = [t for col in obj for t in col["techs"]]
    elif name == "Policies.json":
        items = obj + [p for branch in obj for p in branch["policies"]]
    for o in items:
        if isinstance(o, dict) and (name, o.get("name")) in PEDIA:
            o["civilopediaText"] = [{"text": PEDIA[(name, o["name"])]}]


def dump(name, obj):
    pedia(name, obj)
    collect(obj)
    WRITTEN.append(name)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


E12, E3, E4 = "Rank One-Two era", "Rank Three era", "Rank Four era"
E5, E6 = "Rank Five era", "Rank Six era"  # MOD_SPEC_2 C1
E7, E8 = "Rank Seven era", "Rank Eight era"  # MOD_SPEC_2 C5
E9 = "Rank Nine era"  # the user (2026-11-01): rank nine as an era, overriding MOD_SPEC_2 "never an era"
GM_TYPES = ["Gu Master", "Moon Gu Master", "Strength Gu Master"]  # the last two only carry the hidden legacy units
# C3 (MOD_SPEC_3): the path is a promotion now, not the unit type. The refinement ladder keys on the two Slice 1 paths
# that have Gu; a unit holding both Masters (only a human can) climbs the Moon ladder.
MOON = "<for units with [Moon Master]>"
STR = "<for units with [Strength Master]> <for units without [Moon Master]>"
UNPATHED = "<for units without [Moon Master]> <for units without [Strength Master]>"
RANK1 = "<for [Rank One Gu Master] units>"  # the Liquor Worm refines rank-one essence only (canon)
RANK2 = "<for [non-[Rank One Gu Master]] units>"  # a fused rank-two Gu needs a rank-two aperture
APT = ("Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> "
       "<for units without [Aptitude C]> <for units without [Aptitude D]>")
NB = "Never appears as a Barbarian unit"
WILD_GU_TRIGGER = "Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>"
# "Add [resource] to this tile" deletes the tile's resource [src UniqueTriggerActivation OneTimeAddResource]: never on a
# Spirit Spring or a Gu food ("resource" matches every resource the civ can see; all are revealed by Inheritance Lore)
INHERITANCE_TRIGGER = ("Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> "
                       "<in tiles without [resource]> <after discovering [Inheritance Lore]>")
TIDE = "Beast Tide"           # the spec's generic name; in Slice 1 the beasts are the canon wolf tide (lang chao)
SPRING = "Awakening Grounds"  # R2 T6: the cave behind the clan-head pavilion: the clan's primeval spring and flower sea
PAVILION = "Clan Head Pavilion"  # R2 T6: was "Clan Hall"; the ancestral hall (ci tang) is inside it


def w(x, cond=""):
    return f"[{x}]% weight to this choice for AI decisions" + (f" {cond}" if cond else "")


# R7 (the user's Marathon game, 2026-10-18): every random event rolls per turn, but a slower speed has more turns per
# era (Speeds.json modifier: Quick 0.67, Standard 1, Epic 1.5, Marathon 3), so Marathon met three times the tides,
# betrayals and shortages per era. Chances divide by the modifier and turn gates multiply by it, one line per speed
# (`<on [speed] game speed>`); chances stay whole numbers [docs nonNegativeAmount], so the slowest speeds round up.
SPEEDS = [(s["name"], s["modifier"]) for s in json5.load(open(os.path.join(VAN, "Speeds.json")))]


def per_speed(make):
    """make(modifier) -> unique without a speed conditional; one line per game speed."""
    return [f"{make(m)} <on [{name}] game speed>" for name, m in SPEEDS]


def chance(base, m):
    return max(1, round(base / m))


def turn_gate(base, m):
    return round(base * m)


def die_weights(p_standard, m):
    """Weights for the silent 'nothing happens' choice of a two-stage die whose second stage fires with p_standard on
    Standard: per speed, multiply its weight so the second stage fires with p_standard / m (weights multiply [src
    IHasUniques.getWeightForAiDecision])."""
    nothing = 1 / p_standard - 1
    return round(100 * ((1 / (p_standard / m) - 1) / nothing - 1))


# ---------------- MOD_SPEC_2 C1: ascension (docs/LORE_MAPPING.md "Phase C1: ascension") ----------------
# The three qi of ascension (R V5/346) are stockpiles fed by the land, the springs and the people; the ascension
# spends them. Income is per turn and the same on every speed; the costs scale with the speed instead (a slower speed
# has more turns per era, R7), one line per speed.
QI = ["Heaven Qi", "Earth Qi", "Human Qi"]
GREEN = "Green Grape Immortal Essence"
RED, WHITE = "Red Date Immortal Essence", "White Lychee Immortal Essence"  # C5: ranks seven and eight (R V4/141, V5/613)
IMMORTALS = {"Rank Six Gu Immortal": GREEN, "Rank Seven Gu Immortal": RED, "Rank Eight Gu Immortal": WHITE}
IMMORTAL = "post-[Rank Five era]"  # unit filter: every Gu Immortal (their required techs lie after the Rank Five era)
THREE_QI = "<after discovering [Three Qi]> <for [Major] Civilizations>"
QI_SOURCES = [
    f"Instantly provides [1] [Heaven Qi] <upon turn start> <for every [15] [Owned [Land] Tiles]> {THREE_QI}",
    f"Instantly provides [1] [Earth Qi] <upon turn start> <for every [1] [Owned [Spring Cave] Tiles]> {THREE_QI}",
    f"Instantly provides [1] [Earth Qi] <upon turn start> <for every [8] [Owned [Hill] Tiles]> {THREE_QI}",
    f"Instantly provides [1] [Human Qi] <upon turn start> <for every [10] [[Population] in [in all cities] Cities]> {THREE_QI}",
    # human qi is what a master gathers through deeds (R V5/468): battle feeds it
    f"Earn [5]% of the damage done to [All] units as [Human Qi] {THREE_QI}",
]
ASCEND = {"Balance the three qi": 60, "Ascend in haste": 30}  # qi of each kind, Standard speed


def qi_cost(amount, m):
    return max(1, round(amount * m))


# a die outcome: the immortal's blessed land (a promotion: the aperture belongs to the immortal and dies with it) and
# the upgrade, or the collapse. Aptitude is the foundation canon names (R V4/290): grade A raises the odds, D lowers them
GRADES = [("Lower", 1, 2), ("Middle", 2, 4), ("Upper", 3, 6), ("Super", 5, 10)]  # essence, stones per turn


def ascended(grade, weight, a, d):
    return {"text": f"{'An' if grade == 'Upper' else 'A'} {grade.lower()}-grade blessed land opens", "uniques": [
        f"[This Unit] gains the [{grade} Grade Blessed Land] promotion", f"Instantly provides [5] [{LIFESPAN}]",
        "Triggers a [Immortal Ascension] event",
        # an upgrade copies the promotions and re-fires their direct effects on the new unit [src UnitManager.
        # placeUnitNearTile]: the Ascension promotion would throw the event again on the immortal being placed, and a
        # second collapse destroyed it mid-placement (autoplay crash, NullPointerException in performUpgrade)
        "[This Unit] loses the [Ascension] promotion",
        "[This Unit] upgrades for free including special upgrades",
        w(weight), w(a, "<for units with [Aptitude A]>"), w(d, "<for units with [Aptitude D]>")]}


def collapse(weight, a, d):
    return {"text": "The aperture collapses", "uniques": [
        "Triggers a [Aperture Collapse] event", "[This Unit] is destroyed",
        w(weight), w(a, "<for units with [Aptitude A]>"), w(d, "<for units with [Aptitude D]>")]}


# ---------------- MOD_SPEC_2 C2: calamities, tribulations, Heaven's Will, lifespan ----------------
# A blessed land meets an earthly calamity every ten aperture-years and a heavenly tribulation every hundred (R V4/91):
# timed statuses on the immortal (the user's decision) whose end throws the event (E7). Higher grades run faster, so
# their calamities come sooner (R V4/44). Turns per speed scale like the event chances (R7).
LIFESPAN = "Lifespan Gu"
CALAMITY_TURNS = {"Lower": 14, "Middle": 13, "Upper": 12, "Super": 11}
TRIBULATION_TURNS = 60
RAVAGED = "Ravaged Land"


def turns(base, m):
    return max(2, round(base * m))


def countdown(status, base, event, extra=""):
    return [f"[This Unit] gains the [{status}] status for [{turns(base, m)}] turn(s) <upon turn start> "
            f"<for units without [{status}]>{extra} <on [{n}] game speed>" for n, m in SPEEDS] + [
        f"Triggers a [{event}] event <upon losing the [{status}] status>"]


def ravage(base):
    return [f"[This Unit] gains the [{RAVAGED}] status for [{turns(base, m)}] turn(s) <on [{n}] game speed>"
            for n, m in SPEEDS]


def blessed_land(grade, essence, stones):
    # C5: the blessed land makes the essence of its immortal's rank (rank seven: red date)
    return {"name": f"{grade} Grade Blessed Land", "uniques": [
        f"Instantly provides [{essence}] [{e}] <upon turn start> <for units without [{RAVAGED}]> <for [{u}] units>"
        for u, e in list(IMMORTALS.items())[:2]] + [
        # the Zombie Alliance's immortals never age but make no essence (LORE_MAPPING, its nation row): the provide line
        # is cancelled for it, since a nation filter has no negation. Autoplay (Five Regions, 6 x 500) without this:
        # its immortals hoarded 65-116 red date essence and it won 5 of 6 games through a Venerable at T369-395
        f"Instantly consumes [{essence}] [{e}] <upon turn start> <for units without [{RAVAGED}]> <for [{u}] units> "
        f"<for [Zombie Alliance] Civilizations>" for u, e in list(IMMORTALS.items())[:2]] + [
        f"Gain [{stones}] [Gold] <upon turn start> <for units without [{RAVAGED}]>"]
        + countdown("Calamity Countdown", CALAMITY_TURNS[grade], "Earthly Calamity")
        # Phase D: heavenly tribulations every 100 aperture-years at rank six, every 50 at rank seven (R V4/91, V4/177)
        + countdown("Tribulation Countdown", TRIBULATION_TURNS, "Heavenly Tribulation", " <for [Rank Six Gu Immortal] units>")
        + countdown("Tribulation Countdown", TRIBULATION_TURNS // 2, "Heavenly Tribulation", " <for [Rank Seven Gu Immortal] units>")[:-1]}


# Lifespan Gu (R V3/194, V4/298): made only by heaven and earth where life teems, never refined. Each immortal burns
# one every ten turns; without any it cannot heal and wastes away in about fifteen turns (MOD_SPEC_2 tension target).
# Autoplay (C2): at one every five turns and 20% per 10 forest or jungle tiles most immortals died in debt
LIFESPAN_SOURCES = [u for t in ("Forest", "Jungle", "Marsh") for u in per_speed(
    lambda m, t=t: f"Instantly provides [1] [{LIFESPAN}] <upon turn start> <for every [8] [Owned [{t}] Tiles]> "
                   f"<with [{chance(15, m)}]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations>")]
IMMORTAL_LIFE = [f"Instantly consumes [1] [{LIFESPAN}] <upon turn start> <every [{turns(10, m)}] turns> <on [{n}] game speed>"
                 for n, m in SPEEDS] + [
    f"Can only heal by pillaging <when below [1] [{LIFESPAN}]>",
    f"[This Unit] takes [7] damage <upon turn start> <when below [1] [{LIFESPAN}]>",
    # Phase D: an immortal cultivates wherever it stands (its aperture is its own academy); in autoplay the AI's
    # immortals lacked the XP for the Great and Supreme Grandmaster tiers and never reached a Venerable
    "[This Unit] gains [3] XP <upon turn start>",
    "[This Unit] gains [5] XP <upon turn start> <for [Rank Eight Gu Immortal] units>"]  # a grotto-heaven: faster insight


def toll(text, effects, weight):
    return {"text": text, "uniques": effects + [w(weight)]}


DIVERT = toll("Divert the disaster", ["Only available <if [Divert Disaster] is constructed>"], "+300")
# ---------------- dao marks (道痕; the user, 2026-11-01: "dao marknya mana?") ----------------
# Dao marks are engraved in a cultivator's body and aperture; the more of its path, the stronger its methods, and the
# marks of different paths interfere (R ch1077, ch1804; docs/PATHS.md "Conflicts"). Visible as five promotion tiers that
# replace one another. A path's Master of rank three or more comprehends a tier every 20 turns; an immortal also takes
# a tier from every immortal it kills and from every heavenly tribulation it survives. Mortals hold at most tier II;
# rank seven needs II, rank eight III, the Venerable IV (canon: a Venerable holds hundreds of thousands, R V6/119).
DAO = ["Dao Marks I", "Dao Marks II", "Dao Marks III", "Dao Marks IV", "Dao Marks V"]
DAO_EFFECTS = [["[+5]% Strength"], ["[+10]% Strength"], ["[+15]% Strength"], ["[+20]% Strength", "[+10] HP when healing"],
               ["[+30]% Strength", "[+15] HP when healing"]]
IMMORTAL_ONLY = "<for [post-[Rank Five era]] units>"


def dao_step(trigger=""):
    """One tier more, highest first so a single trigger climbs one tier only (each tier removes the one below when
    gained)."""
    t = f" {trigger}" if trigger else ""
    out = []
    for i in range(len(DAO) - 1, 0, -1):
        cap = f" {IMMORTAL_ONLY}" if i >= 2 else ""
        out.append(f"[This Unit] gains the [{DAO[i]}] promotion{t} <for units with [{DAO[i - 1]}]>{cap}")
    out.append(f"[This Unit] gains the [{DAO[0]}] promotion{t} " + " ".join(f"<for units without [{d}]>" for d in DAO))
    return out


def dao_at_least(i):
    """Unavailable unless the unit holds tier i (0-based) or higher."""
    return "Unavailable " + " ".join(f"<for units without [{d}]>" for d in DAO[i:])


DAO_LINES = per_speed(lambda m: f"[This Unit] gains the [Dao Comprehension] status for [{turns(20, m)}] turn(s) <upon turn start> "
                                "<for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units>") \
    + dao_step("<upon losing the [Dao Comprehension] status>") \
    + [u + f" {IMMORTAL_ONLY}" for u in dao_step("<upon defeating a [post-[Rank Five era]] unit>")]
SURVIVOR = "Tribulation Survivor"  # C5: surviving a heavenly tribulation opens the next rank (300 aperture-years, R V4/177)
SURVIVED = f"[This Unit] gains the [{SURVIVOR}] promotion"
SURVIVE = [SURVIVED] + dao_step()  # a survived tribulation also tempers the immortal's dao marks

# ---------------- MOD_SPEC_2 C5: ranks seven and eight ----------------
# An immortal climbs a rank after surviving a heavenly tribulation and gathering its rank's essence (R V4/177): a kept
# promotion (E4) whose purchase pays the essence and upgrades the unit through the special upgrade (C1's route).
# Statuses and the foreign-land guard as for the ascension (C3 crash fix); the Advancing status keeps the upgrade from
# counting as a lost immortal for Spring Autumn Cicada [src: losing a unit also fires on upgrade, E9].
ADVANCE = {"Rank Seven": ("Rank Six Gu Immortal", "Red Date Essence", GREEN), "Rank Eight": ("Rank Seven Gu Immortal", "Grotto-Heaven", RED)}
ADVANCE_COST = 60


def advance(target):
    unit, tech, essence = ADVANCE[target]
    name = f"Advance to {target}"
    extra = ([f"[This Unit] loses the [{g} Grade Blessed Land] promotion" for g, _, _ in GRADES]
             + ["[This Unit] gains the [Grotto-Heaven Aperture] promotion"]) if target == "Rank Eight" else []
    return {"name": name, "unitTypes": GM_TYPES, "uniques": [
        f"Only available <for [{unit}] units> <after discovering [{tech}]> <for units with [{SURVIVOR}]>",
        dao_at_least(1 if target == "Rank Seven" else 2),
        "Unavailable <in [Foreign Land] tiles>", "Unavailable <in [Water] tiles>"]
        + [f"Unavailable <when below [{qi_cost(ADVANCE_COST, m)}] [{essence}]> <on [{n}] game speed>" for n, m in SPEEDS]
        + [f"Instantly consumes [{qi_cost(ADVANCE_COST, m)}] [{essence}] <on [{n}] game speed>" for n, m in SPEEDS]
        + [f"[This Unit] loses the [{SURVIVOR}] promotion", f"[This Unit] loses the [{name}] promotion",
           "[This Unit] gains the [Advancing] status for [1] turn(s)"] + extra
        + ["[This Unit] upgrades for free including special upgrades", w("+200")]}


# ---------------- MOD_SPEC_2 C5b: the Venerable, Eternal Life, Gu Houses ----------------
# Rank nine is never an era (MOD_SPEC_2): a Venerable rises when a clan holding a rank-eight immortal of supreme
# attainment builds the Venerable Ascension (one in the world at a time). The Venerable is unbeatable in its era but
# only long-lived (R V6/105, V3/194): it loses HP every turn and cannot heal, while its yellow apricot essence pays for
# Eternal Life, Fang Yuan's goal and the arc's victory (MOD_SPEC_3). When it dies its ascension is removed (the race
# reopens, Phase A2) and its clan gains the seal of its true inheritance.
APRICOT = "Yellow Apricot Immortal Essence"  # rank nine (R V6/249)
VEN_ELSEWHERE = "<if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed>"
VENERABLE = "Venerable"
GU_HOUSES = [  # (name, immortal Gu it needs, strength, movement, extra uniques); R V4/356, V5/694, V6/68, V6/14
    ("Calamity Luck Altar", "Connect Luck", 140, 2, ["[+50]% Strength <when defending>"]),
    ("Myriad Year Flying Warship", "Years Flow Like Water", 150, 5, ["Ignores terrain cost"]),
    ("Dragon Palace", "Dream Token", 160, 3, ["[+20]% Strength <vs [post-[Rank Five era]] units>"]),
    # C5c: the Heavenly Court's rank-nine Gu House around Fate Gu, which shrugs off calamities (R V4/356, V4/358)
    ("Heaven Overseeing Tower", "Fate Gu", 190, 2, ["[+25]% Strength <when defending>", "[+2] Sight"]),
]


# the rank-eight aperture: a grotto-heaven (R V5/745) makes white lychee essence; its calamities come faster
GROTTO = {"name": "Grotto-Heaven Aperture", "uniques": [
    f"Instantly provides [3] [{WHITE}] <upon turn start> <for units without [{RAVAGED}]>",
    f"Instantly consumes [3] [{WHITE}] <upon turn start> <for units without [{RAVAGED}]> <for [Zombie Alliance] Civilizations>",
    f"Gain [12] [Gold] <upon turn start> <for units without [{RAVAGED}]>"]
    + countdown("Calamity Countdown", 10, "Earthly Calamity") + countdown("Tribulation Countdown", 50, "Heavenly Tribulation")}

# ---------------- MOD_SPEC_2 C3: immortal Gu (data/immortal_gu.csv) ----------------
# World wonders (each immortal Gu is unique in the world, R V4/100): a recipe tech, essence on top of production,
# kept on capture (Phase A2: conquest seizes the Gu), the Immortal Gu marker and its path's marker (dao marks,
# tools/gen_paths.py). Never granted free (A3). Their completion rolls the refinement die (仙蛊成劫, R V5/54).
IMMORTAL_GU = table("immortal_gu.csv")
REALMS = table("secret_realms.csv")  # the secret realms (natural wonders, Terrains section below)
IMMORTAL_GU_RECIPES = {"6": "Immortal Gu Recipes", "7": "Rank Seven Immortal Gu Recipes",
                       "8": "Rank Eight Immortal Gu Recipes"}
IMMORTAL_GU_ESSENCE = {"6": GREEN, "7": RED, "8": WHITE, "9": APRICOT}
IMMORTAL_GU_RECIPES["9"] = "Rank Nine Immortal Gu Recipes"

# ---------------- MOD_SPEC_2 C5c: the arc's nations, Fate Gu, the Fate War ----------------
# Fate Gu (R V5/720, V5/694; the user's Phase A decision): a wonder unique to the Heavenly Court and built by it. A rival
# that conquers the city holding it fights the Fate War: shatter it (as Fang Yuan did, R V5/939: the qi tides follow and
# it can never be rebuilt, B4) or seize it.
HC, HJ, ZA, FANG = "Heavenly Court", "Huang Jin Family", "Zombie Alliance", "Fang Clan"
ZOMBIE = "Immortal Zombie"
FATE_WEAK = "[-15]% Strength <if [Fate Gu] is constructed by anybody>"  # a zombie's dead fate holds while Fate Gu stands

# ---------------- MOD_SPEC_2 C4: inheritances, desolate beasts, the market ----------------
# Inheritances (data/inheritances.csv; the user's Phase A decision): a trial die grants a seal that unlocks BUILDING
# the inheritance, a world wonder, so a rival with the same seal can race for it and conquest can seize it. The trial
# is thrown by the owned-tile trigger (Phase A4); preparation (Masters of the inheritance's path) raises the odds.
INHERITANCES = table("inheritances.csv")
MATERIALS = "Immortal Materials"
DESOLATE = "Desolate Beast"
ANCIENT, IMMEMORIAL = "Ancient Desolate Beast", "Immemorial Desolate Beast"  # C5: about ranks seven and eight (R V5/14)


def path_master(key):
    return gen_paths.tier_name(gen_paths.KEY[key], 0)


def trial_won(i):
    return {"text": f"{i['name']}: the trial is passed", "uniques": [
        f"Unavailable <if [{i['name']}] is constructed by anybody>", f"Unavailable <if [{i['seal']}] is constructed>"]
        + items(i["gate"]) + [f"Gain a free [{i['seal']}] [in capital]", "Triggers a [Inheritance Won] event",
                              w("-90"), w("+300", f"<when number of [[{path_master(i['path'])}] Units] is more than [0]>")]}


# ---------------- ModOptions / Globals ----------------
dump("ModOptions.json", {"isBaseRuleset": True,
                         "uniques": ["Disable religion", "Can only start games from the starting era"],
                         # R5: the engine adds (share of techs known x 5.5)^2.8 x this to every city's strength [src
                         # CityCombatant.getCityStrength]; with a 15-tech tree the default 1.0 gave +118 by turn ~120 and
                         # no city was ever taken. 0.1 caps it at +12 (autoplay, docs/AUTOPLAY.md round 5).
                         "constants": {"maxXPfromBarbarians": 90, "cityStrengthFromTechsFullMultiplier": 0.1,
                                       # MOD_SPEC_2 #13: random maps place only 1-5 natural wonders by default; the
                                       # twelve secret realms want more (Small about 5, Huge about 12)
                                       "naturalWonderCountMultiplier": 0.3, "naturalWonderCountAddedConstant": 1.0}})
dump("Beliefs.json", [])
dump("Religions.json", [])
dump("GlobalUniques.json", {"name": "GlobalUniques", "uniques": [
    "[-75]% growth [in all cities] <when between [-10] and [-1] [Happiness]>",
    "Nullifies Growth [in all cities] <when below [-10] [Happiness]>",
    "[-50]% [Production] [in all cities] <when below [-10] [Happiness]>",
    "[-33]% Strength <for [All] units> <when below [-10] [Happiness]>",
    "Rebel units may spawn <when below [-20] [Happiness]>",
    "[-3] units cost no maintenance <for [Major] Civilizations>",
    "[-20]% Strength <when below [0] [Gold]>",
    # Phase D: a clan's new villages are settled by its own kin. With one luxury (Furs) and few happiness buildings,
    # every village past the second pushed a clan below zero (autoplay, Five Regions T280: happiness -5.5, 39 of 44
    # clans unhappy, growth -75%, population stuck near 18 whatever the number of villages). With this and the
    # Tavern's +2: population 27 at T280 (Qing Mao: no change in debt, stones per turn -1.5 -> +1.3)
    "[-33]% unhappiness from the number of cities",
] + per_speed(lambda m: f"Triggers a [{TIDE}] event <upon turn start> <after turn number [{turn_gate(30, m)}]> "
                       f"<with [{chance(3, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [{TIDE}] event <upon turn start> <after turn number [{turn_gate(90, m)}]> "
              f"<with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [{chance(8, m)}]% chance> "
              "<for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [{chance(3, m)}]% chance> "
              "<for [Major] Civilizations>") + per_speed(
    lambda m: "Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] "
              f"is less than [0]> <with [{chance(25, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    # C8: a righteous clan friendly with a demonic one, or conquering a city, may be exposed
    lambda m: "Triggers a [Collusion Exposed] event <upon turn start> <after adopting [Righteous Path]> "
              "<when number of [Adopted [[Demonic Path] branch] Policies by [Friendly] Civilizations] is more than [0]> "
              f"<with [{chance(3, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: "Triggers a [Whitewashed Name] event <upon turn start> <after adopting [Demonic Path]> "
              f"<if [Shang Clan City] is constructed by anybody> <with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Clan Contest] event <upon turn start> <after turn number [{turn_gate(60, m)}]> <when not at war> "
              f"<with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + [
    "Triggers a [Collusion Exposed] event <upon conquering a city> <after adopting [Righteous Path]> <with [25]% chance> "
    "<for [Major] Civilizations>",
    "Triggers a [Blood Lake] event <upon discovering [Inheritance Lore] technology> <for [Gu Yue Clan] Civilizations>",
    # R6: a held (excavated) inheritance teaches the clan's Gu Masters
    "[+20]% XP gained from combat <with [Gu Inheritance]>",
] + QI_SOURCES + LIFESPAN_SOURCES + per_speed(
    # Heaven's Will trims the strong (R V5/54): a clan with more than two immortals draws extra calamities
    lambda m: f"Triggers a [Heaven's Will] event <upon turn start> <when number of [[{IMMORTAL}] Units] is more "
              f"than [2]> <if [Divination Tortoise Shell] is not constructed> <with [{chance(3, m)}]% chance> "
              f"<for [Major] Civilizations>") + per_speed(
    # C3: so does a clan holding more than two immortal Gu (MOD_SPEC_2 #10)
    lambda m: f"Triggers a [Heaven's Will] event <upon turn start> <when number of [[Immortal Gu] Buildings] is more "
              f"than [2]> <if [Divination Tortoise Shell] is not constructed> <with [{chance(3, m)}]% chance> "
              f"<for [Major] Civilizations>")
    + [u for g in IMMORTAL_GU for u in items(g["global_effects"])] + per_speed(
    # C4: a clan holding enough land hears of a Venerable's inheritance now and then
    lambda m: f"Triggers a [Inheritance Trial] event <upon turn start> <when number of [Owned [Land] Tiles] is more than "
              f"[30]> <after discovering [Calamity Lore]> <with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Desolate Beast Tide] event <upon turn start> <after discovering [Three Qi]> "
              f"<with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Treasure Yellow Heaven] event <upon turn start> <when number of [[{IMMORTAL}] Units] "
              f"is more than [0]> <with [{chance(4, m)}]% chance> <for [Major] Civilizations>") + [
    # a desolate beast's corpse is a heap of immortal materials (R V5/734)
] + [f"Earn [10]% of killed [{b}] unit's [Cost] as [{MATERIALS}]" for b in (DESOLATE, ANCIENT, IMMEMORIAL)] + [
    # C5b: a Venerable's death (it never upgrades, so losing it means its death, E9)
    f"Remove [Venerable Ascension] [in all cities] <upon losing a [{VENERABLE}] unit>",
    f"Gain a free [True Inheritance Seal] [in capital] <upon losing a [{VENERABLE}] unit>",
    f"Triggers a [Venerable Falls] event <upon losing a [{VENERABLE}] unit>",
    # the user (2026-11-01): while a Venerable lives the world is afraid. Every other clan fights weaker and is unhappy,
    # Heaven's Will thins the Lifespan Gu of every clan (R V5/54), and the Venerable's own clan thrives
    f"[-10]% Strength {VEN_ELSEWHERE}", f"[-2 Happiness] {VEN_ELSEWHERE}",
    f"Instantly consumes [1] [{LIFESPAN}] <upon turn start> <every [10] turns> <if [Venerable Ascension] is constructed by anybody> "
    "<for [Major] Civilizations>",
    "[+20]% [Production] [in all cities] <if [Venerable Ascension] is constructed>",
    "[+3 Happiness] <if [Venerable Ascension] is constructed>",
    # C5c
    f"Triggers a [Fate War] event <upon conquering a city> <if [Fate Gu] is constructed> <if [Fate Seized] is not "
    f"constructed> <for [non-[{HC}]] Civilizations>",
] + per_speed(
    # dream realms surface before the Fate War and burn the soul, but pour attainment into survivors (R V4/74-85; B4)
    lambda m: f"Triggers a [Dream Realm] event <upon turn start> <starting from the [{E7}]> <if [Shattered Fate] is not "
              f"constructed by anybody> <with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    # the Shadow Sect: Spectral Soul's split souls working to revive him (R V4/367)
    lambda m: f"Triggers a [Shadow Sect Envoy] event <upon turn start> <starting from the [{E6}]> "
              f"<with [{chance(1, m)}]% chance> <for [Major] Civilizations>") + per_speed(lambda m: f"Triggers a [Venerable's Shadow] event <upon turn start> {VEN_ELSEWHERE} "
                        f"<with [{chance(4, m)}]% chance> <for [Major] Civilizations>") + per_speed(lambda m: f"Triggers a [Qi Tides] event <upon turn start> <if [Shattered Fate] is constructed by anybody> "
                        f"<with [{chance(3, m)}]% chance> <for [Major] Civilizations>")})

# ---------------- Eras (iconRGB = essence colours: green copper / white silver / yellow gold, verified) ----------------
dump("Eras.json", [
    {"name": E12, "researchAgreementCost": 150, "iconRGB": [72, 140, 100], "startingSettlerUnit": "Clan Settler",
     "startingWorkerCount": 1, "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master",
     "startingGold": 50, "baseUnitBuyCost": 200},
    {"name": E3, "researchAgreementCost": 250, "iconRGB": [205, 205, 215], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 300},
    {"name": E4, "researchAgreementCost": 350, "iconRGB": [230, 190, 60], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 400},
    # MOD_SPEC_2 C1: purple crystal (rank five, R V2/180) and green grape (rank six, R V3/232)
    {"name": E5, "researchAgreementCost": 450, "iconRGB": [170, 110, 230], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 500},
    {"name": E6, "researchAgreementCost": 550, "iconRGB": [160, 215, 100], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 600},
    # C5: red date (rank seven) and white lychee (rank eight)
    {"name": E7, "researchAgreementCost": 650, "iconRGB": [200, 60, 60], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 700},
    {"name": E8, "researchAgreementCost": 750, "iconRGB": [240, 236, 222], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 800},
    {"name": E9, "researchAgreementCost": 900, "iconRGB": [255, 196, 70], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 900},
])


# ---------------- Techs (data/tech_columns.csv, data/techs.csv) ----------------
def tech(t):
    d = {"name": t["name"], "row": int(t["row"])}
    if t["prerequisites"]:
        d["prerequisites"] = items(t["prerequisites"])
    if t["uniques"]:
        d["uniques"] = items(t["uniques"])
    return d


TECHS = table("techs.csv")
dump("Techs.json", [{"columnNumber": int(c["column"]), "era": c["era"], "techCost": int(c["techCost"]),
                     "buildingCost": int(c["buildingCost"]), "wonderCost": int(c["wonderCost"]),
                     "techs": [tech(t) for t in TECHS if t["column"] == c["column"]]}
                    for c in table("tech_columns.csv")])

# ---------------- Unit types ----------------
dump("UnitTypes.json", [{"name": n, "movementType": "Land"} for n in
                        ["Civilian", "Gu Master", "Moon Gu Master", "Strength Gu Master", "Beast", "Gu House"]])


# ---------------- Units ----------------
def gm(name, utype, tech, cost, strength, maint, extra, ranged=None, upgrades=None, legacy=False):
    u = {"name": name, "unitType": utype, "movement": 2, "strength": strength, "cost": cost, "requiredTech": tech,
         "uniques": [f"[{maint}]% maintenance costs", NB] + ([] if legacy else [APT]) + extra}
    if ranged:
        u["rangedStrength"] = ranged
        u["range"] = 2
    if upgrades:
        u["upgradesTo"] = upgrades
    return u


def legacy(path):
    """C3 M4: Unciv deletes a save's units that the ruleset no longer has [src BackwardCompatibility.
    removeUnitsAndPromotions], so the old path x rank units stay, hidden, and turn into their rank's unit (the clan's
    own, through getEquivalentUnit) with their path's Master at the next turn start; promotions survive (A3 test 1)."""
    return ["Unbuildable", "Cannot be purchased", "Will not be displayed in Civilopedia",
            f"[This Unit] gains the [{path} Master] promotion <upon turn start>", "[This Unit] upgrades for free <upon turn start>"]


GU_MASTERS = [gm(r["name"], r["unitType"], r["requiredTech"], int(r["cost"]), int(r["strength"]), r["maintenance"],
                 items(r["extra_uniques"]) + (legacy(r["legacyPath"]) if r["legacyPath"] else []),
                 ranged=int(r["rangedStrength"]) if r["rangedStrength"] else None, upgrades=r["upgradesTo"] or None,
                 legacy=bool(r["legacyPath"]))
              for r in table("gu_masters.csv")]
for u, r in zip(GU_MASTERS, table("gu_masters.csv")):
    u["attackSound"] = r["attackSound"]  # R5: each path sounds different (built-in sounds, Images-and-Audio.md)
    if r["uniqueTo"]:
        # C3 (the user's choice A.b): a signature clan keeps its path's look and attack effect through its own chain,
        # since Unciv picks attack animations by unit name or type only [src BattleTableHelpers.getAttackAnimationLocation]
        u["uniqueTo"], u["replaces"] = r["uniqueTo"], r["replaces"]
        base = next(b for b in table("gu_masters.csv") if b["name"] == r["replaces"])
        same = ("unitType", "requiredTech", "cost", "strength", "rangedStrength", "maintenance", "upgradesTo",
                "extra_uniques", "cultivationXP")
        assert all(r[k] == base[k] for k in same), f"{r['name']} must keep {r['replaces']}'s numbers (tune both rows)"
    if r["legacyPath"]:
        continue
    if int(r["cultivationXP"]):
        # R5: cultivation in the clan's academy (the Wu Martial Arena counts: it replaces the Gu Academy [src
        # containsBuildingOrEquivalent]). Without it XP came only from battle and the ladder stalled at rung 1.
        u["uniques"].append(f"[This Unit] gains [{r['cultivationXP']}] XP <upon turn start> <in cities with a [Gu Academy]> "
                            "<for units without [Killer Move]>")
    # R6 (the user's request): wild Gu and buried inheritances are found by Gu Masters in the field. Chances are whole
    # numbers [docs Unique-parameters nonNegativeAmount], so each is a small trigger followed by a weighted die (E1):
    # 6% x 1/5 = 1.2% per Gu Master per turn for a wild Gu; 1% x 1/2 per turn in foreign land for an inheritance
    # (1/8 gave 0.4 inheritances per game in autoplay; 1/2 aims at about 1.5).
    u["uniques"] += [WILD_GU_TRIGGER, INHERITANCE_TRIGGER] + DAO_LINES
    if r["name"] in IMMORTALS:
        u["uniques"] += IMMORTAL_LIFE  # MOD_SPEC_2 C2: every immortal burns Lifespan Gu
        u["uniques"].append("Can pass through impassable tiles")  # immortals cross mountains and the region walls
dump("Units.json", [
    {"name": "Clan Settler", "unitType": "Civilian", "movement": 2, "cost": 80, "requiredTech": "Aperture Awakening",
     # R8: mortals live off the land, not off primeval stones (late-game AI bankruptcy, docs/AUTOPLAY.md round 8)
     "uniques": ["Founds a new city <by consuming this unit>", "Excess Food converted to Production when under construction",
                 "[-100]% maintenance costs",
                 "Requires at least [2] population",
                 # Vanilla's "Cannot build [Settler] units <when below [-10] [Happiness]>" hides the unit without a word
                 # (CannotBeBuilt is never shown [src BaseUnit.shouldBeDisplayed]); a player with a big city thought
                 # settlers were broken. Same rule, kept in the list, greyed, with the reason shown.
                 "Can only be built <when above [-11] [Happiness]>", "Shown while unbuilable", NB]},
    {"name": "Mortal Laborer", "unitType": "Civilian", "movement": 2, "cost": 45, "requiredTech": "Aperture Awakening",
     "uniques": ["Can build [Land] improvements on tiles", "Automation is a primary action", "[-100]% maintenance costs", NB]},
] + GU_MASTERS + [
    # R2 T5: the canon wolf-tide tiers (plain / hundred-beast tier / ten-thousand-beast king)
    {"name": "Lightning Wolf", "unitType": "Beast", "movement": 3, "strength": 9, "cost": 30, "attackSound": "shot", "uniqueTo": "Barbarians",
     "uniques": ["[+50]% maintenance costs"]},
    {"name": "Bold Lightning Wolf", "unitType": "Beast", "movement": 3, "strength": 16, "cost": 60, "attackSound": "shot",
     "requiredTech": "Rank Three Cultivation", "uniqueTo": "Barbarians",
     "uniques": ["[+15]% Strength bonus for [Lightning Wolf] units within [2] tiles", "[+100]% maintenance costs"]},
    # C4: a desolate beast (荒兽), about a rank-six immortal (R V5/14); only events bring one
    {"name": DESOLATE, "unitType": "Beast", "movement": 3, "strength": 62, "cost": 200, "attackSound": "shot",
     "uniqueTo": "Barbarians", "uniques": ["Unbuildable", "[+15]% Strength <when defending>", "[+200]% maintenance costs"]},
    {"name": ANCIENT, "unitType": "Beast", "movement": 3, "strength": 85, "cost": 300, "attackSound": "shot",
     "uniqueTo": "Barbarians", "uniques": ["Unbuildable", "[+15]% Strength <when defending>", "[+250]% maintenance costs"]},
    {"name": IMMEMORIAL, "unitType": "Beast", "movement": 3, "strength": 115, "cost": 500, "attackSound": "shot",
     "uniqueTo": "Barbarians", "uniques": ["Unbuildable", "[+15]% Strength <when defending>", "[+300]% maintenance costs"]},
    # C5b: the Venerable and the Gu Houses
    # the user (2026-11-01): rank nine dominates and terrifies. A Venerable is unbeatable in its era (R V6/105): it strikes
    # three times, walks through anything, enslaves the defeated, cows every enemy beside it, and burns its own life
    {"name": VENERABLE, "unitType": "Gu Master", "movement": 5, "strength": 280, "cost": 1000, "requiredTech": "Dao Lord",
     "attackSound": "throw", "uniques": ["Unbuildable", "Cannot be purchased", "Limited to [1] per Civilization", NB,
                                         "[This Unit] takes [3] damage <upon turn start>", "Can only heal by pillaging",
                                         f"Instantly provides [6] [{APRICOT}] <upon turn start>", "[+300]% maintenance costs",
                                         "[2] additional attacks per turn", "Can move after attacking", "Ignores terrain cost",
                                         "Can pass through impassable tiles", "May capture killed [Military] units",
                                         "[-25]% Strength for enemy [Military] units in adjacent [All] tiles",
                                         "[+50]% Strength <vs cities>", "Destroys tile improvements when attacking",
                                         "[This Unit] gains [5] XP <upon turn start>", *DAO_LINES,
                                         f"[This Unit] gains the [Venerable Killer Move] status for [1] turn(s) <costs [20] [{APRICOT}]> <requires [1] movement>"]
     # a Venerable buys time only with slaughter: every kill restores some of its burning life
     + ["Heals [10] damage if it kills a unit"] + countdown("Chaos Countdown", 25, "Chaos Calamity")},
] + [{"name": n, "unitType": "Gu House", "movement": mv, "strength": st, "cost": 650, "requiredTech": "Gu House Formation",
      "attackSound": "throw", **({"uniqueTo": HC} if gu == "Fate Gu" else {}),
      "uniques": [f"Only available <if [{gu}] is constructed>", "Limited to [1] per Civilization",
                  "Can pass through impassable tiles",
                                          f"Costs [50] [{WHITE}]", "[+500]% maintenance costs", NB] + extra}
     for n, gu, st, mv, extra in GU_HOUSES] + [
    {"name": ZOMBIE, "unitType": "Gu Master", "movement": 2, "strength": 70, "cost": 300, "requiredTech": "Calamity Lore",
     "attackSound": "throw", "uniques": ["Unbuildable", "Cannot be purchased", NB, "Can only heal by pillaging", FATE_WEAK,
                                         "Can pass through impassable tiles",
                                         "[+100]% maintenance costs"]},
] + [
    {"name": "Thunder Crown Wolf", "unitType": "Beast", "movement": 3, "strength": 28, "cost": 120, "attackSound": "shot",
     "uniqueTo": "Barbarians",
     "uniques": ["Unbuildable", "[+20]% Strength bonus for [Beast] units within [2] tiles", "[+200]% maintenance costs"]},
])

# ---------------- R2 T4: refinement ladder with the canon recipes ----------------
# Moon (Fang Zheng's line):      Moonlight Gu -> Moon Raiment (Moonlight + Jade Skin, fused) -> Killer Move
# Strength (Fang Yuan's line):   White Boar Gu -> White Jade Gu (White Boar + Jade Skin, fused; boar strength kept;
#                                a spare wild boar = the tusk catalyst, +20 points) -> Killer Move
# Unpathed (no Moon or Strength Master; any rank since C3): Jade Skin Gu (the cap); carried into a path, it saves the
# fusion's jade.
# Black Boar Gu is OFF the ladder: bought from the Jia caravan (Jia ally bonus), stacks as a second boar.
# Dead states: no ladder line can fire -> the careful and reckless choices close.
LADDER_DEAD = [
    "Unavailable <for units with [Killer Move]>",
    f"Unavailable {MOON} <for units with [Moon Raiment]> <before discovering [Killer Moves]>",
    f"Unavailable {STR} <for units with [White Jade Gu]> <before discovering [Killer Moves]>",
    f"Unavailable {MOON} <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when below [1] [Moon Orchid]>",
    f"Unavailable {MOON} <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when below [1] [Jade]>",
    f"Unavailable {STR} <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when below [1] [Wild Boar]>",
    f"Unavailable {STR} <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when below [1] [Jade]>",
    f"Unavailable {STR} <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when below [2] [Jade]>",
    f"Unavailable {MOON} <for units with [Moonlight Gu]> {RANK1}",
    f"Unavailable {STR} <for units with [White Boar Gu]> {RANK1}",
]
RO_DEAD = [
    f"Unavailable {UNPATHED} <for units with [Jade Skin Gu]>",
    f"Unavailable {UNPATHED} <when below [1] [Jade]>",
]
# Refine Gu closes where no rung AND (for an unpathed unit) no Liquor Worm lure can happen.
LW_IMPOSSIBLE = ["<for units with [Liquor Worm]>", "<when below [1] [Wine]>", "<when below [31] [Gold]>", RANK2]
# since C3 a Rank One may already hold a path, so every dead state counts only where the lure is impossible too
PROMO_DEAD = [f"{d} {c}" for d in LADDER_DEAD + RO_DEAD for c in LW_IMPOSSIBLE if not (RANK1 in d and c == RANK2)]


# R3 hunger meter: tools/gu_rules.py (shared with the path Gu of tools/gen_paths.py).
from gu_rules import HUNGER, gu_promotion  # noqa: E402


def ladder(base, fusion, tusk):
    """Highest rung first: choice uniques fire in list order and promotion conditionals are read live, so one attempt
    climbs at most one rung. Every unit state matches at most one 'gains' line (one chance roll per attempt, E5).
    The 'loses' lines are deterministic: they remove the two ingredients only after a successful fusion."""
    b, f, t = (f"<with [{x}]% chance>" for x in (base, fusion, tusk))
    NK = "<for units without [Killer Move]>"  # a killer move ends the climb on every ladder (C3: a human may hold both paths)
    return [
        f"[This Unit] gains the [Killer Move] promotion {MOON} <for units with [Moon Raiment]> <for units without [Killer Move]> <after discovering [Killer Moves]> {b}",
        f"[This Unit] gains the [Killer Move] promotion {STR} <for units with [White Jade Gu]> <for units without [Killer Move]> <after discovering [Killer Moves]> {b}",
        f"[This Unit] gains the [White Jade Gu] promotion {STR} {RANK2} <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when above [0] [Wild Boar]> {NK} {t}",
        f"[This Unit] gains the [White Jade Gu] promotion {STR} {RANK2} <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when below [1] [Wild Boar]> {NK} {f}",
        f"[This Unit] gains the [White Jade Gu] promotion {STR} {RANK2} <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when above [0] [Wild Boar]> {NK} {t}",
        f"[This Unit] gains the [White Jade Gu] promotion {STR} {RANK2} <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when below [1] [Wild Boar]> {NK} {f}",
        "[This Unit] loses the [White Boar Gu] promotion <for units with [White Jade Gu]>",
        "[This Unit] loses the [Jade Skin Gu] promotion <for units with [White Jade Gu]>",
        f"[This Unit] gains the [Moon Raiment] promotion {MOON} {RANK2} <for units with [Moonlight Gu]> <for units with [Jade Skin Gu]> {NK} {f}",
        f"[This Unit] gains the [Moon Raiment] promotion {MOON} {RANK2} <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> {NK} {f}",
        "[This Unit] loses the [Moonlight Gu] promotion <for units with [Moon Raiment]>",
        "[This Unit] loses the [Jade Skin Gu] promotion <for units with [Moon Raiment]>",
        f"[This Unit] gains the [White Boar Gu] promotion {STR} <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when above [0] [Wild Boar]> {NK} {b}",
        f"[This Unit] gains the [Moonlight Gu] promotion {MOON} <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when above [0] [Moon Orchid]> {NK} {b}",
        f"[This Unit] gains the [Jade Skin Gu] promotion {UNPATHED} <for units without [Jade Skin Gu]> <when above [0] [Jade]> {NK} {b}",
    ]


# ---------------- Promotions (Gu from data/gu.csv) ----------------
dump("UnitPromotions.json", [
    {"name": "Aptitude A", "uniques": ["[+15]% Strength", "[-20]% maintenance costs", "[+25]% XP gained from combat"]},
    {"name": "Aptitude B", "uniques": ["[+5]% Strength", "[-10]% maintenance costs", "[+10]% XP gained from combat"]},
    {"name": "Aptitude C", "uniques": []},
    {"name": "Aptitude D", "uniques": ["[-10]% Strength", "[+20]% maintenance costs", "[-25]% XP gained from combat"]},
    {"name": "Refine Gu", "unitTypes": GM_TYPES, "uniques": [
        "Only available <after discovering [Gu Refinement]>",
        "Unavailable <when below [50] HP>"] + PROMO_DEAD + [
        "Triggers a [Refinement Attempt] event",
        "[This Unit] loses the [Refine Gu] promotion <upon turn start>"]},
] + [gu_promotion(r) for r in table("gu.csv")] + [
    {"name": "Killer Move", "uniques": ["[+25]% Strength <when attacking>", "[+25]% maintenance costs",
                                        # a killer move needs its rank-2 Gu; if that Gu died of hunger, the move goes too
                                        "[This Unit] loses the [Killer Move] promotion <upon turn start> <for units without [White Jade Gu]> <for units without [Moon Raiment]>"]},
    # clan emblem Gu (canon names, ch22); effects and foods unknown, so they eat stones
    {"name": "Bear Strength Gu", "uniques": ["[+10]% Strength", "[+10]% maintenance costs"]},
    {"name": "Stream Gu", "uniques": ["[+10] HP when healing", "[+10]% maintenance costs"]},
    # C1 (canon overhaul, conflicts research): the righteous hunt demonic cultivators and post bounties on them (R V2c29,
    # V2c35). A marker on every military unit of a Demonic Path clan; it clears itself once the clan's camp changes.
    {"name": "Demonic Infamy", "uniques": [
        "Comment [Righteous clans fight harder against this unit and pay a bounty for it]",
        "[This Unit] loses the [Demonic Infamy] promotion <upon turn start> <before adopting [Demonic Path]>"]},
    # R3 hunger statuses (timers; see hunger()); each removes itself once its food is back
] + [{"name": status, "uniques": [f"[This Unit] loses the [{status}] status <upon turn start> <when above [-1] [{food}]>"]}
     for food, status in HUNGER.items()]
    # C3 (MOD_SPEC_3): every canonical path's attainment tiers, killer moves and signature statuses (docs/PATHS.md)
    + gen_paths.promotions(GM_TYPES) + gen_paths.gu_promotions() + [
    # MOD_SPEC_2 C1: the ascension is bought like Refine Gu (E4: kept, self-removing); the human may try with the hasty
    # amount of qi, the AI only with the balanced one (it never wastes the XP on an attempt it would rush)
    {"name": "Ascension", "unitTypes": GM_TYPES, "uniques": [
        "Only available <for [Rank Five Gu Master] units> <after discovering [Calamity Lore]>",
        # an upgrade anywhere fails in foreign land without open borders, and Unciv then crashes restoring the old unit
        # [src UnitUpgradeManager.performUpgrade, TileMap.placeUnitNearTile]: ascend at home (autoplay crash, C3)
        "Unavailable <in [Foreign Land] tiles>",
        # a Water Master walks on water, but the upgraded unit is placed before its promotions are copied: at sea it
        # finds no tile and Unciv crashes restoring the old one (autoplay crash, C5)
        "Unavailable <in [Water] tiles>"]
        + [f"Unavailable <when below [{qi_cost(ASCEND['Ascend in haste'], m)}] [{q}]> <on [{n}] game speed>"
           for q in QI for n, m in SPEEDS]
        + [f"Unavailable <when below [{qi_cost(ASCEND['Balance the three qi'], m)}] [{q}]> <for [AI player] Civilizations> "
           f"<on [{n}] game speed>" for q in QI for n, m in SPEEDS]
        + ["Triggers a [Ascension] event <for [Rank Five Gu Master] units>",
           "[This Unit] loses the [Ascension] promotion <upon turn start>"]},
] + [blessed_land(g, e, st) for g, e, st in GRADES] + [
    {"name": "Calamity Countdown", "uniques": ["Comment [When it runs out, the blessed land meets an earthly calamity]"]},
    {"name": "Tribulation Countdown", "uniques": ["Comment [When it runs out, the immortal meets a heavenly tribulation]"]},
    {"name": RAVAGED, "uniques": ["Comment [The blessed land yields nothing until it heals]"]},
    # C5
    {"name": SURVIVOR, "uniques": ["Comment [Survived a heavenly tribulation: may climb to the next rank]"]},
    {"name": "Dao Comprehension", "uniques": ["Comment [When it runs out, the unit's dao marks grow by one tier]"]},
] + [{"name": d, "uniques": DAO_EFFECTS[i] + ([f"[This Unit] loses the [{DAO[i - 1]}] promotion"] if i else [])}
     for i, d in enumerate(DAO)] + [
    {"name": "Advancing", "uniques": ["Comment [Climbing to the next rank]"]},
    GROTTO, advance("Rank Seven"), advance("Rank Eight"),
    {"name": "Venerable Killer Move", "uniques": ["[+100]% Strength"]},
    # the arc's victory: the Venerable spends its yellow apricot essence on eternal life before its lifespan runs out
    {"name": "Seek Eternal Life", "unitTypes": GM_TYPES, "uniques": [
        f"Only available <for [{VENERABLE}] units>", "Unavailable <if [Eternal Life] is constructed by anybody>"]
        + [f"Unavailable <when below [{qi_cost(150, m)}] [{APRICOT}]> <on [{n}] game speed>" for n, m in SPEEDS]
        + [f"Instantly consumes [{qi_cost(150, m)}] [{APRICOT}] <on [{n}] game speed>" for n, m in SPEEDS]
        + ["Gain a free [Eternal Life] [in capital]", "[This Unit] loses the [Seek Eternal Life] promotion", w("+1000")]},
    {"name": "Ascend to Venerable", "unitTypes": GM_TYPES, "uniques": [
        f"Only available <for [{{Rank Eight Gu Immortal}} {{{gen_paths.SUPREME_MARKER}}}] units> <after discovering [Dao Lord]>",
        "Unavailable <if [Venerable Ascension] is constructed by anybody>", dao_at_least(3), "Unavailable <in [Foreign Land] tiles>",
        "Unavailable <in [Water] tiles>"]
        + [f"Unavailable <when below [{qi_cost(60, m)}] [{WHITE}]> <on [{n}] game speed>" for n, m in SPEEDS]
        + [f"Instantly consumes [{qi_cost(60, m)}] [{WHITE}] <on [{n}] game speed>" for n, m in SPEEDS]
        + ["Gain a free [Venerable Ascension] [in capital]", "[This Unit] loses the [Ascend to Venerable] promotion",
           # an upgrade keeps every promotion [src MapUnit.copyStatisticsTo]: without this the Venerable kept the
           # grotto-heaven's calamity and tribulation countdowns, whose essence choices stop at rank eight
           "[This Unit] loses the [Grotto-Heaven Aperture] promotion",
           "[This Unit] gains the [Advancing] status for [1] turn(s)", "[This Unit] upgrades for free including special upgrades",
           w("+500")]},
] + [{"name": r["promotion"], "uniques": [r["promotion_effect"]]} for r in REALMS] + [
    {"name": "Chaos Countdown", "uniques": ["Comment [When it runs out, a chaos calamity falls on the Venerable]"]},
])

# ---------------- Events (13: the spec's 5, wild Gu and inheritances (R6), world conflicts (canon overhaul)) ----------------
BAI = "<for [Bai Clan] Civilizations>"
# R7: a capital population cost needs a capital to pay it: at population 1 the loss is void [src] and the reward free
CAP_POP = "Only available <when number of [[Population] in [in capital] Cities] is more than [3]>"
SPR = f"<if [{SPRING}] is constructed>"  # containsBuildingOrEquivalent: Gu Yue's Moon Orchid Flower Sea counts [src]
dump("Events.json", [
    {"name": "Aptitude Awakening", "presentation": "None", "choices": [
        {"text": "Grade A aptitude", "uniques": ["[This Unit] gains the [Aptitude A] promotion", w("-95"),
                                                 w("+100", SPR), w("+100", BAI)]},
        {"text": "Grade B aptitude", "uniques": ["[This Unit] gains the [Aptitude B] promotion", w("-80"),
                                                 w("+50", SPR), w("+25", BAI)]},
        {"text": "Grade C aptitude", "uniques": ["[This Unit] gains the [Aptitude C] promotion", w("-65")]},
        {"text": "Grade D aptitude", "uniques": ["[This Unit] gains the [Aptitude D] promotion", w("-60"),
                                                 w("-25", SPR)]},
    ]},
    {"name": "Refinement Attempt", "text": "Your essence pours into the Gu and its materials. How far will you push it?", "choices": [
        {"text": "Refine carefully", "uniques":
            ["Only available <if [Refinement Chamber] is constructed> <when above [80] [Gold]>",
             f"Unavailable <when below [140] [Gold]> <during the [{E3}]>",
             f"Unavailable <when below [200] [Gold]> <starting from the [{E4}]>",
             f"Gain [-40] [Gold] <during the [{E12}]>", f"Gain [-70] [Gold] <during the [{E3}]>",
             f"Gain [-100] [Gold] <starting from the [{E4}]>"]
            + LADDER_DEAD + RO_DEAD + ladder(85, 70, 90) + [w("+50"), w("-60", "<when below [150] [Gold]>")]},
        {"text": "Refine recklessly", "uniques": LADDER_DEAD + RO_DEAD + ["Unavailable <when below [31] HP>"]
            + ladder(50, 40, 60) + ["[This Unit] takes [30] damage", w("+0"), w("-90", "<when below [50] HP>")]},
        # R2 T4/T9: canon lure (Green Bamboo Wine) and canon refining cost (at least 30 stones); rank one only
        {"text": "Lure a wild Liquor Worm with Green Bamboo Wine", "uniques": [
            f"Only available {RANK1} <for units without [Liquor Worm]> <when above [0] [Wine]> <when above [30] [Gold]>",
            "Gain [-30] [Gold]", "[This Unit] gains the [Liquor Worm] promotion <with [70]% chance>", w("+0")]},
        {"text": "Stop and recover your essence", "uniques": ["[This Unit] gains [5] XP", w("-95")]},
    ]},
    {"name": TIDE, "text": "Lightning wolves pour down the mountain toward your villages.", "choices": [
        {"text": "Meet the wolves in the field", "uniques": [
            f"[2] [Lightning Wolf]s rebel <during the [{E12}]>",
            f"[3] [Lightning Wolf]s rebel <starting from the [{E3}]>",
            f"A [Bold Lightning Wolf] rebels <starting from the [{E3}]>",
            f"A [Thunder Crown Wolf] rebels <starting from the [{E4}]>",
            w("+0")]},
        {"text": "Hire demonic Gu Masters to thin the pack", "uniques": [
            "Only available <when above [60] [Gold]>",
            f"Unavailable <when below [100] [Gold]> <during the [{E3}]>",
            f"Unavailable <when below [150] [Gold]> <starting from the [{E4}]>",
            f"Gain [-60] [Gold] <during the [{E12}]>", f"Gain [-100] [Gold] <during the [{E3}]>",
            f"Gain [-150] [Gold] <starting from the [{E4}]>",
            w("+0")]},
        # R7: was "[-1] population [in all cities]": free in cities at population 1 (losses stop at 1 [src]) and the
        # largest drain on every clan (autoplay: capitals at 1.8-4 by turn 320, 8.4 without population choices).
        # The fields lie fallow for a while instead.
        {"text": "Abandon the outer fields", "uniques": ["[-50]% growth [in all cities] <for [10] turns>", w("-30")]},
        {"text": "Man the stockade walls", "uniques": [
            "Only available <if [Stockade Wall] is constructed> <when above [70] [Gold]>",
            f"Gain [-40] [Gold] <during the [{E3}]>", f"Gain [-70] [Gold] <starting from the [{E4}]>",
            "[-20]% [Production] <for [5] turns>", w("+50")]},
        # C3: canon answers a wolf tide with an alliance of the clans and a split of the spoils (R V1c124, V1c127,
        # V1c179); the wolves still come, the clan fights them stronger and pays its share. Not while at war.
        {"text": "Call the clans' alliance", "uniques": [
            "Only available <when number of [Known [Major] Civilizations] is more than [1]> <when not at war>",
            f"[2] [Lightning Wolf]s rebel <during the [{E12}]>", f"[3] [Lightning Wolf]s rebel <starting from the [{E3}]>",
            f"A [Bold Lightning Wolf] rebels <starting from the [{E3}]>",
            "[+30]% Strength <vs [Barbarians] units> <for [10] turns>", "[-10]% [Gold] <for [10] turns>", w("+30")]},
    ]},
    {"name": "Betrayal", "text": "A clan member has sold you out and fled with stones and Gu.", "choices": [
        {"text": "Let the traitor go", "uniques": ["Only available <when above [60] [Gold]>", "Gain [-60] [Gold]",
                                                   w("+0")]},
        {"text": "Hunt the traitor down", "uniques": [
            "A [Rank Two Gu Master] rebels <after adopting [Strength Path]>",
            "A [Rank Two Gu Master] rebels <after adopting [Moon Path]>",
            "A [Rank One Gu Master] rebels <before adopting [Strength Path]> <before adopting [Moon Path]>",
            w("+0")]},
        {"text": "Judge the traitor by clan law", "uniques": ["Only available <after adopting [Righteous Path]>", CAP_POP,
                                                     "[-1] population [in capital]", "[+2 Happiness] <for [10] turns>",
                                                     w("+100")]},
        {"text": "Strike first and take the traitor's Gu", "uniques": ["Only available <after adopting [Demonic Path]>", CAP_POP,
                                                            "Gain [40] [Gold]", "[-1] population [in capital]",
                                                            "[-3 Happiness] <for [10] turns>", w("+100"),
                                                            w("-75", "<when below [0] [Happiness]>")]},
    ]},
    {"name": "Stone Shortage", "text": "The stone vaults are empty and the Gu are going hungry.", "choices": [
        {"text": "Ration the Gu feed", "uniques": ["[-40]% maintenance costs <for [8] turns>",
                                                  "[-15]% Strength <for [8] turns>", w("+100")]},
        {"text": "Borrow from the merchant caravans", "uniques": [
            "Only available <when above [-100] [Gold]>", "Gain [80] [Gold]", "[-6 Gold] <for [20] turns>", w("-80")]},
        {"text": "Squeeze the mortals", "uniques": [CAP_POP, "Gain [50] [Gold]", "[-1] population [in capital]", w("-20")]},
        # C7: merchants shun a clan that robs caravans (R V1c55-57); a righteous clan that does it risks exposure
        {"text": "Rob a passing caravan", "uniques": [
            "Gain [70] [Gold]", "Triggers a [Betrayal] event <with [25]% chance>",
            "[+100]% City-State Influence degradation <for [10] turns>",
            "Triggers a [Collusion Exposed] event <after adopting [Righteous Path]> <with [50]% chance>",
            w("+50"), w("-80", "<after adopting [Righteous Path]>")]},
    ]},
    # C8 (conflicts research M4): a righteous clan caught dealing with demons, or grabbing land without a pretext, is
    # pressed by the others and may be branded demonic, as the Fang clan was (R V5c595-596, V6c287). `Remove` takes the
    # branch and its members [src Policy.matchesSingleFilter, UniqueTriggerActivation.OneTimeRemovePolicy]; `Adopt`
    # ignores the opener's own gate [src PolicyManager.adopt]; checked headless (docs/AUTOPLAY.md, canon overhaul 4).
    {"name": "Collusion Exposed", "text": "Word spreads that your clan deals with demonic cultivators. The righteous clans demand an answer.", "choices": [
        {"text": "Pay to bury the scandal", "uniques": ["Only available <when above [100] [Gold]>", "Gain [-100] [Gold]", w("+50")]},
        {"text": "Ride it out", "uniques": ["[-3 Happiness] <for [10] turns>",
                                           "[+100]% City-State Influence degradation <for [10] turns>", w("+0")]},
        {"text": "Walk the demonic path openly", "uniques": ["Remove [[Righteous Path] branch]", "Adopt [Demonic Path]",
                                                            w("-50")]},
    ]},
    # C8 (M4b): a demonic clan can buy a righteous name in the Shang clan's battle district (R V2c60, V2c66)
    {"name": "Whitewashed Name", "text": "The Shang clan's battle stage will wash any name white, for a price.", "choices": [
        {"text": "Buy a righteous name", "uniques": ["Only available <when above [150] [Gold]>", "Gain [-150] [Gold]",
                                                    "Remove [[Demonic Path] branch]", "Adopt [Righteous Path]", w("-50")]},
        {"text": "Stay what you are", "uniques": [w("+0")]},
    ]},
    # C9 (M11): a peacetime contest between the clans splits the mountain's gains (R V1c179); a silent die
    {"name": "Clan Contest", "presentation": "None", "choices": [
        {"text": "Your young Gu Masters carry the day", "uniques": [
            "Gain [60] [Gold]", "New [Gu Master] units start with [10] XP [in all cities] <for [10] turns>", w("+0"),
            w("+100", "<if [Martial Arena] is constructed>"), w("+100", "<when number of [[Military] Units] is more than [8]>")]},
        {"text": "Your young Gu Masters are beaten", "uniques": ["Gain [-30] [Gold]", "[-3 Happiness] <for [10] turns>", w("+0")]},
    ]},
    # D4 (the user: the twist is used): Gu Yue's first clan head took a Blood Sea Ancestor inheritance, became a blood
    # zombie and lay hidden under the Blood Lake; the Tie constable came to root out the blood disaster (R V1c181-185,
    # V1c192, V1c195). Fired once, for Gu Yue, when it learns Inheritance Lore.
    {"name": "Blood Lake", "text": "Beneath the spring cave the elders have found a blood-red lake and, in it, the coffin of the clan's founder. Something in the coffin is still alive.", "choices": [
        {"text": "Seal the lake and speak of it to no one", "uniques": ["Only available <when above [80] [Gold]>",
                                                                       "Gain [-80] [Gold]", w("+50")]},
        {"text": "Send for the Tie clan's constable", "uniques": ["A [Rank Four Gu Master] rebels",
                                                                 "[+2 Happiness] <for [10] turns>", w("+0")]},
        {"text": "Claim the founder's blood inheritance", "uniques": [
            "Remove [[Righteous Path] branch]", "Adopt [Demonic Path]", "Gain [150] [Gold]",
            "[+15]% Strength <for [10] turns>", w("-50")]},
    ]},
    # R6: wild Gu. Stage 1 is silent (None): 1 in 5 goes on to stage 2, a popup for the human (Alert; the AI rolls).
    # Only Gu that live wild in canon or plausibly so: the Liquor Worm (lured wild in canon), Jade Skin Gu, Black Boar
    # Gu; never the Moonlight Gu, which only Gu Yue breeds. Each is food-gated and keeps the ladder's invariants.
    {"name": "Wild Gu", "presentation": "None", "choices": [
        {"text": "Only the wind in the grass", "uniques": [w("+300")] + [w(f"{die_weights(0.2, m):+d}", f"<on [{n}] game speed>")
                                                                     for n, m in SPEEDS if m != 1]},
        {"text": "A wild Gu stirs nearby", "uniques": ["Triggers a [Wild Gu Caught] event", w("+0")]},
    ]},
    {"name": "Wild Gu Caught", "text": "Your Gu Master has cornered a wild Gu. Which one will it be?", "choices": [
        {"text": "Capture the wild Liquor Worm", "uniques": [
            f"Only available {RANK1} <for units without [Liquor Worm]> <when above [0] [Wine]>",
            "[This Unit] gains the [Liquor Worm] promotion", w("+0")]},
        {"text": "Capture the wild Jade Skin Gu", "uniques": [
            "Only available <for units without [Jade Skin Gu]> <for units without [White Jade Gu]> <for units without [Moon Raiment]> <when above [0] [Jade]>",
            "[This Unit] gains the [Jade Skin Gu] promotion", w("+0")]},
        {"text": "Capture the wild Black Boar Gu", "uniques": [
            f"Only available {STR} <for units without [Black Boar Gu]> <when above [0] [Wild Boar]>",
            "[This Unit] gains the [Black Boar Gu] promotion", w("+0")]},
    ]},
    # R6: a buried inheritance. Silent rumour (1 in 2 is real), then the popup. Claiming it puts a Gu Inheritance on
    # the tile and takes the tiles around it, from whoever owns them (diplomatic penalty for stealing territory [src
    # OneTimeTakeOverTilesInRadius]): the clans fight over it.
    {"name": "Inheritance Rumour", "presentation": "None", "choices": [
        {"text": "An empty cave", "uniques": [w("+0")] + [w(f"{die_weights(0.5, m):+d}", f"<on [{n}] game speed>")
                                                       for n, m in SPEEDS if m != 1]},
        {"text": "Something is buried here", "uniques": ["Triggers a [Buried Inheritance] event", w("+0")]},
    ]},
    {"name": "Buried Inheritance", "text": "Your Gu Master has unearthed a buried Gu inheritance. Word will spread fast.", "choices": [
        {"text": "Claim it for the clan", "uniques": [
            "Add [Gu Inheritance] to this tile", "Gain control over [Land] tiles in a [1]-tile radius",
            "[This Unit] gains [20] XP", w("+100")]},
        {"text": "Strip it and vanish", "uniques": ["Gain [60] [Gold]", "[This Unit] gains [30] XP", w("+0")]},
    ]},
    # MOD_SPEC_2 C1: crush the aperture, draw in and balance the three qi, survive (R V3/201, V5/346, V3/222)
    {"name": "Ascension", "text": "Your rank-five Gu Master is ready to crush the aperture and draw in the three qi. "
                                  "Balanced qi gives the best odds; haste costs less and risks everything.", "choices": [
        {"text": text, "uniques": ["Unavailable <in [Foreign Land] tiles>", "Unavailable <in [Water] tiles>"] + [
            f"Unavailable <when below [{qi_cost(a, m)}] [{q}]> <on [{n}] game speed>"
                                   for q in QI for n, m in SPEEDS]
            + [f"Instantly consumes [{qi_cost(a, m)}] [{q}] <on [{n}] game speed>" for q in QI for n, m in SPEEDS]
            + [f"Triggers a [{trial}] event", w(weight)]}
        for (text, a), (trial, weight) in zip(ASCEND.items(), (("Ascension Trial", "+200"), ("Hasty Ascension Trial", "-80")))
    ] + [{"text": "Not yet", "uniques": [w("-100")]}]},
    # silent dice: balanced qi succeeds 80% (lower 40, middle 28, upper 10, super 2); haste 50% (lower 36, middle 14)
    {"name": "Ascension Trial", "presentation": "None", "choices": [
        ascended("Lower", "+0", "+0", "+0"), ascended("Middle", "-30", "+0", "+0"),
        ascended("Upper", "-75", "+100", "-50"), ascended("Super", "-96", "+150", "-100"), collapse("-50", "-50", "+100")]},
    {"name": "Hasty Ascension Trial", "presentation": "None", "choices": [
        ascended("Lower", "+0", "+0", "+0"), ascended("Middle", "-60", "+50", "-50"), collapse("+40", "-40", "+60")]},
    {"name": "Immortal Ascension", "text": "The calamity passes. Your Gu Master is a Gu Immortal now, and its aperture "
                                           "has become a blessed land (its grade is shown among the immortal's promotions).",
     "choices": [{"text": "Enter the blessed land", "uniques": [w("+0")]}]},
    {"name": "Aperture Collapse", "text": "The three qi would not balance. The aperture collapsed, and your Gu Master "
                                          "with it.", "choices": [{"text": "Mourn the fallen", "uniques": [w("+0")]}]},
    # MOD_SPEC_2 C2: prepared choices cost little (tension target: under 10% of the land's output); enduring a
    # calamity unprepared costs about a third (the land lies ravaged half the time for most of a cycle) or the
    # immortal's health
    {"name": "Earthly Calamity", "text": "An earthly calamity strikes your immortal's blessed land: floods, fire, a "
                                         "swarm. How will it be met?", "choices": [
        DIVERT,
        toll("Beckon it to the land's edge", ["Only available <if [Calamity Beckoning] is constructed>", "[This Unit] takes [5] damage",
                                              f"Instantly provides [10] [{MATERIALS}]"], "+150"),
        toll("Raise the formation ward", ["Only available <if [Formation Ward] is constructed>", "[This Unit] takes [10] damage"], "+100"),
        toll("Rebuild from the vault", ["Only available <if [Stockpile Vault] is constructed>", "Unavailable <when below [40] [Gold]>",
                                        "Gain [-40] [Gold]"], "+50"),
        # C5: each rank pours its own essence (autoplay: rank-seven immortals made no green grape and faced bare)
        *[toll("Pour essence into the land", [f"Only available <for [{u}] units>", f"Unavailable <when below [10] [{e}]>",
                                              f"Instantly consumes [10] [{e}]", "[This Unit] takes [15] damage"], "-60")
          for u, e in IMMORTALS.items()],  # Phase D: the AI poured away the white lychee its Venerable needed
        toll("Endure it", ["Triggers a [Calamity Toll] event"], "-30")]},
    {"name": "Calamity Toll", "presentation": "None", "choices": [   # 50 / 30 / 20
        toll("The land is ravaged", ravage(8), "+0"),
        toll("The immortal is hurt", ["[This Unit] takes [40] damage"], "-40"),
        toll("It passes", [], "-60")]},
    {"name": "Heavenly Tribulation", "text": "A heavenly tribulation gathers over your immortal: heaven itself tests "
                                             "whether it may go on living.", "choices": [
        toll("Divert the disaster", ["Only available <if [Divert Disaster] is constructed>", *SURVIVE], "+300"),
        *[toll("Ward and essence together", ["Only available <if [Formation Ward] is constructed>", f"Only available <for [{u}] units>",
                                             *SURVIVE, f"Unavailable <when below [30] [{e}]>", f"Instantly consumes [30] [{e}]",
                                             "[This Unit] takes [30] damage"], "+100") for u, e in IMMORTALS.items()],
        *[toll("Pour essence into the land", [f"Only available <for [{u}] units>", f"Unavailable <when below [50] [{e}]>",
                                              f"Instantly consumes [50] [{e}]", "[This Unit] takes [50] damage", *SURVIVE], "-60")
          for u, e in IMMORTALS.items()],
        toll("Face it bare", ["Triggers a [Tribulation Toll] event"], "-30")]},
    {"name": "Tribulation Toll", "presentation": "None", "choices": [   # 25 / 45 / 30
        toll("The tribulation kills it", ["[This Unit] is destroyed"], "-44"),
        toll("It survives, its land ravaged", ravage(10) + ["[This Unit] takes [50] damage", *SURVIVE], "+0"),
        toll("It survives", ["[This Unit] takes [30] damage", *SURVIVE], "-33")]},
    # C3: an immortal Gu's birth may call down its own calamity (R V5/54); civ-level, in the city that refined it
    {"name": "Immortal Gu Refinement", "presentation": "None", "choices": [   # 75 / 25
        toll("The Gu takes shape", [], "+0"),
        toll("Its birth calls down a calamity", ["[-2] population [in this city]", "[2] [Bold Lightning Wolf]s rebel"], "-67")]},
    # civ-level: no unit context
    {"name": "Heaven's Will", "text": "Heaven's Will turns against a clan with too many immortals. Beasts go mad and "
                                      "luck runs thin.", "choices": [
        toll("Lie low", ["[-20]% Strength <for [10] turns>"], "+0"),
        toll("Pay heaven its due", [f"Unavailable <when below [30] [{GREEN}]>", f"Instantly consumes [30] [{GREEN}]"], "+50"),
        toll("Defy heaven", [f"A [{DESOLATE}] rebels", "[2] [Bold Lightning Wolf]s rebel"], "-30")]},
    {"name": "Venerable Falls", "text": "Your Venerable has fallen. Its ascension is gone, so a new Venerable "
                                        "may rise anywhere; its true inheritance's seal lies in your capital.",
     "choices": [toll("Guard the true inheritance", [], "+0")]},
    {"name": "Dream Realm", "text": "A dream realm has surfaced near your land: a dead man's dream, full of his dao. It burns "
                                    "the soul, and pours attainment into whoever survives it.", "choices": [
        toll("Enter the dream", ["[+50]% XP gained from combat <for [10] turns>", "[-10]% Strength <for [10] turns>"], "+50"),
        toll("Leave it to fade", [], "+0")]},
    {"name": "Shadow Sect Envoy", "text": "An envoy of the Shadow Sect offers essence for a favour no one may ever learn of.",
     "choices": [
        toll("Accept their help", [f"Instantly provides [30] [{GREEN}]",
                                   "Triggers a [Collusion Exposed] event <after adopting [Righteous Path]> <with [50]% chance>"], "+0"),
        toll("Turn them away", [], "+50"),
        toll("Hunt the envoy", ["Unavailable <when below [100] [Gold]>", "Gain [-100] [Gold]", "[+15]% Strength <for [10] turns>"], "+0")]},
    {"name": "Venerable's Shadow", "text": "A Venerable walks the world. Its gaze has fallen on your clan; whole regions "
                                           "have vanished for less.", "choices": [
        toll("Send tribute", ["Unavailable <when below [150] [Gold]>", "Gain [-150] [Gold]"], "+50"),
        toll("Hide the clan's Gu", ["[-25]% [Production] [in all cities] <for [8] turns>"], "+0"),
        toll("Defy the Venerable", [CAP_POP, "[-2] population [in capital]", "[+20]% Strength <for [10] turns>"], "-40")]},
    # the rank-nine trial from outside the world (混沌大难, R V6/280): a countdown on the Venerable
    {"name": "Chaos Calamity", "text": "A chaos calamity, older than the world, falls on your Venerable.", "choices": [
        toll("Pour yellow apricot essence", [f"Unavailable <when below [40] [{APRICOT}]>", f"Instantly consumes [40] [{APRICOT}]",
                                             "[This Unit] takes [10] damage"], "+100"),
        toll("Endure it", ["[This Unit] takes [25] damage"], "+0")]},
    {"name": "Fate War", "text": "Fate Gu is in your hands. The Heavenly Court guarded it since Primordial Origin. Shatter "
                                 "it and set every being's fate free, or keep it?", "choices": [
        toll("Shatter Fate Gu", ["Remove [Fate Gu] [in all cities]", "Gain a free [Shattered Fate] [in capital]",
                                 "[+20]% Strength <for [20] turns>"], "+50"),
        toll("Seize Fate Gu", ["Gain a free [Fate Seized] [in capital]"], "+0")]},
    # the qi tides after the Fate War (R V6/1, V6/13; B4): they hamper fighting and fling qi about
    {"name": "Qi Tides", "text": "With Fate Gu shattered, tides of qi sweep the five regions.", "choices": [
        toll("Shelter the cities", ["[-25]% [Production] [in all cities] <for [5] turns>"], "+0"),
        toll("Ride the tide", ["Instantly provides [10] [Heaven Qi]", "Instantly provides [10] [Earth Qi]",
                               "[-20]% Strength <for [5] turns>"], "+50")]},
    # C4: inheritance trial (silent die) and its two result popups
    {"name": "Inheritance Trial", "presentation": "None", "choices": [
        toll("Nothing surfaces", [], "+100"),
        toll("The trial claims its seekers", [CAP_POP, "[-2] population [in capital]", "Triggers a [Inheritance Lost] event"], "-80"),
    ] + [trial_won(i) for i in INHERITANCES]},
    {"name": "Inheritance Won", "text": "Your seekers passed a Venerable's trial. Its seal now lies in your capital: the "
                                        "inheritance can be built (see the wonders). A rival may win the same seal; the "
                                        "first to build it keeps it, and a conqueror takes it.",
     "choices": [toll("Begin the work", [], "+0")]},
    {"name": "Inheritance Lost", "text": "The inheritance was a trap. Its trial killed the seekers, and the clan mourns.",
     "choices": [toll("Bury the dead", [], "+0")]},
    # C4: under Heaven's Will even gentle beasts turn frenzied (R V4/359); a desolate beast is about a rank-six immortal
    # (R V5/14) and its corpse is immortal materials
    {"name": "Desolate Beast Tide", "text": "A desolate beast has come down from the wild into your land.", "choices": [
        toll("Hunt it for its corpse", [f"A [{DESOLATE}] rebels <before the [{E7}]>", f"A [{ANCIENT}] rebels <during the [{E7}]>",
                                         f"A [{IMMEMORIAL}] rebels <starting from the [{E8}]>"], "+50"),
        toll("Turn it aside with the formation ward", ["Only available <if [Formation Ward] is constructed>",
                                                       "Unavailable <when below [80] [Gold]>", "Gain [-80] [Gold]"], "+0"),
        toll("Let it rampage", ["[-30]% [Production] [in all cities] <for [5] turns>"], "-30")]},
    # C4: the immortals' market, a grotto-heaven where treasure light prices goods (R V3/61; MOD_SPEC_2 #16)
    {"name": "Treasure Yellow Heaven", "text": "Treasure Yellow Heaven opens to your immortals. What will you trade?", "choices": [
        toll("Buy green grape essence", ["Unavailable <when below [150] [Gold]>", "Gain [-150] [Gold]",
                                         f"Instantly provides [20] [{GREEN}]"], "+50"),
        {"text": "Buy Lifespan Gu", "uniques": ["Unavailable <when below [120] [Gold]>", "Gain [-120] [Gold]",
                                                f"Instantly provides [3] [{LIFESPAN}]", w("+0"),
                                                w("+300", f"<when below [3] [{LIFESPAN}]>")]},
        toll("Sell immortal materials", [f"Unavailable <when below [20] [{MATERIALS}]>", f"Instantly consumes [20] [{MATERIALS}]",
                                         f"Instantly provides [25] [{GREEN}]"], "+100"),
        toll("Sell essence for stones", [f"Unavailable <when below [40] [{GREEN}]>", f"Instantly consumes [40] [{GREEN}]",
                                         "Gain [200] [Gold]"], "+0"),
        toll("Appraise with treasure light", ["Only available <if [Treasure Light Gu] is constructed>",
                                              "Unavailable <when below [150] [Gold]>", "Gain [-150] [Gold]",
                                              f"Instantly provides [35] [{GREEN}]"], "+150"),
        toll("Leave the market", [], "-50")]},
])

# ---------------- Buildings (12: 7 + 1 Wu unique + 2 national wonders + 2 world wonders) ----------------
SPRING_TAKEN = "Unavailable <if [Flower Wine Monk Inheritance] is constructed>"
dump("Buildings.json", [
    # R2 T6: the palace is the clan-head pavilion; its ancestral hall (old 'Ancestral Hall' building) is folded in
    {"name": PAVILION, "isNationalWonder": True, "cost": 0, "production": 3, "gold": 5, "science": 2,
     "culture": 3, "happiness": 1, "cityStrength": 3, "uniques": ["Indicates the capital city"]},
    # R2 T6: the clan's primeval spring and the flower sea around it (was 'Awakening Grounds')
    # R3: the awakening is held at a clan's spirit spring, so it needs an improved Spirit Spring inside the city
    {"name": SPRING, "isNationalWonder": True, "requiredTech": "Aperture Awakening", "cost": 75, "culture": 1,
     "gold": 2, "requiredNearbyImprovedResources": ["Spirit Spring"], "uniques": [SPRING_TAKEN]},
    {"name": "Moon Orchid Flower Sea", "isNationalWonder": True, "uniqueTo": "Gu Yue Clan", "replaces": SPRING,
     "requiredTech": "Aperture Awakening", "cost": 75, "culture": 1, "gold": 2,
     "requiredNearbyImprovedResources": ["Spirit Spring"], "uniques": [SPRING_TAKEN, "Provides [2] [Moon Orchid]"]},
    {"name": "Gu Academy", "requiredTech": "Gu Feeding", "cost": 65, "maintenance": 1, "science": 1, "culture": 1,
     "uniques": ["[+1 Science] per [2] population [in this city]", "New [Military] units start with [10] XP [in this city]"]},
    {"name": "Gu Feeding House", "requiredTech": "Gu Feeding", "cost": 70, "maintenance": 1,
     "uniques": ["Provides [1] [Moon Orchid]", "Provides [1] [Wild Boar]"]},
    # R2 T8: canon tavern (jiu si) selling Green Bamboo Wine; was 'Wine Cellar'
    {"name": "Tavern", "requiredTech": "Wine Brewing", "cost": 60, "maintenance": 1, "happiness": 2,
     "uniques": ["Provides [1] [Wine]"]},
    # R2 T8: refining materials include jade, so every clan has an early jade source that does not depend on map luck
    {"name": "Refinement Chamber", "requiredTech": "Gu Refinement", "cost": 90, "maintenance": 1, "production": 1,
     "science": 1, "uniques": ["Provides [1] [Jade]"]},
    {"name": "Stockade Wall", "requiredTech": "Gu Formations", "cost": 110, "maintenance": 1, "cityStrength": 8,
     "cityHealth": 50},
    # R3: Wu unique building - the Wu clan's battle stage, the largest in the Southern Border (vol2 ch122)
    {"name": "Martial Arena", "uniqueTo": "Wu Clan", "replaces": "Gu Academy", "requiredTech": "Gu Feeding", "cost": 65,
     "maintenance": 1, "science": 1, "culture": 1,
     "uniques": ["[+1 Science] per [2] population [in this city]", "New [Military] units start with [20] XP [in this city]"]},
    {"name": "Trading House", "requiredTech": "Merchant Caravans", "cost": 130, "gold": 2,
     "percentStatBonus": {"gold": 20}},
    # R2 T9: canon contents - the jade-eyed stone monkeys' forest (jade), the Heavenly Essence Treasure Lotus planted in
    # the clan's own spring (stones; taking it wrecks the spring), the trial (XP), the heir's oath against Gu Yue
    {"name": "Flower Wine Monk Inheritance", "isWonder": True, "requiredTech": "Inheritance Lore", "cost": 240,
     "culture": 3, "gold": 4, "uniques": ["Provides [2] [Jade]", "[+15]% XP gained from combat",
                                          "[+15]% Strength <vs [Gu Yue Clan] units>",
                                          f"Remove [{SPRING}] [in all cities]"]},
    # R2 T1: the free market that fences demonic loot (vol2 ch30)
    {"name": "Shang Clan City", "isWonder": True, "requiredTech": "Super Clan Commerce", "cost": 300, "gold": 5,
     "uniques": ["[+2 Gold] from all [Trading House] buildings",
                 "Receive [+50]% Gold from Barbarian encampments and pillaging Cities"]},
    # MOD_SPEC_2 C2: calamity preparations (R V5/22, V5/70): one per clan opens the safer calamity choices
    {"name": "Formation Ward", "isNationalWonder": True, "requiredTech": "Calamity Lore", "cost": 220, "maintenance": 2,
     "cityStrength": 4},
    {"name": "Stockpile Vault", "isNationalWonder": True, "requiredTech": "Calamity Lore", "cost": 160, "maintenance": 1,
     "gold": 2},
] + [{"name": g["name"], "isWonder": True, "requiredTech": IMMORTAL_GU_RECIPES[g["rank"]], "cost": int(g["cost"]),
      "uniques": [f"Costs [{g['essence']}] [{IMMORTAL_GU_ESSENCE[g['rank']]}]", "Never destroyed when the city is captured", "Immortal Gu",
                  gen_paths.path_marker(g["path"]), "Triggers a [Immortal Gu Refinement] event"] + items(g["effects"])
      # autoplay (C3): without it the AI built only the two stat wonders, after turn 275
      + [w("+300")]}
     for g in IMMORTAL_GU
] + [b for i in INHERITANCES for b in (
    {"name": i["name"], "isWonder": True, "requiredTech": "Calamity Lore", "cost": 420,
     "uniques": [f"Only available <if [{i['seal']}] is constructed>", "Never destroyed when the city is captured"]
     + items(i["effects"]) + [w("+300")]},
    # the seal is a free grant: it need not be seizable (Phase A3), it only unlocks building the inheritance
    {"name": i["seal"], "isNationalWonder": True, "cost": 1, "uniques": ["Unbuildable", "Cannot be purchased"]})
] + [
    # Phase D: the AI never queued this wonder even with every condition met (probe: available, only the essence
    # missing; autoplay: 625 white lychee and no build in 110 turns). The immortal now becomes the Venerable through a
    # promotion (canon: the immortal itself ascends); the wonder is only the one-Venerable-in-the-world marker, granted
    # free by that promotion and removed when the Venerable dies
    {"name": "Venerable Ascension", "isWonder": True, "requiredTech": "Dao Lord", "cost": 700,
     # safe [src CivConstructions.addFreeBuildings]: the grant is a one-time trigger of a promotion that removes itself,
     # and only standing (non-trigger) grants are re-applied each turn
     "uniques": ["Unbuildable", "Cannot be purchased",
                 "Suppress warning [is both granted free and could possibly be removed by triggers]"]},
    # Phase D: granted by the Venerable's own promotion (the AI never queues these wonders); unbuildable
    {"name": "Eternal Life", "isWonder": True, "requiredTech": "Dao Lord", "cost": 1200,
     "uniques": ["Unbuildable", "Cannot be purchased"]},
    {"name": "True Inheritance", "isWonder": True, "requiredTech": "Dao Lord", "cost": 600,
     "uniques": ["Only available <if [True Inheritance Seal] is constructed>", "Never destroyed when the city is captured",
                 "[+25]% XP gained from combat", "[+20]% Strength <for [post-[Rank Five era]] units>", w("+300")]},
    {"name": "True Inheritance Seal", "isNationalWonder": True, "cost": 1, "uniques": ["Unbuildable", "Cannot be purchased"]}
] + [
    {"name": "Fate Gu", "isWonder": True, "uniqueTo": HC, "requiredTech": "Immortal Gu Recipes", "cost": 600,
     "uniques": [f"Costs [60] [{GREEN}]", "Never destroyed when the city is captured", "Immortal Gu",
                 "Unavailable <if [Shattered Fate] is constructed by anybody>", "[+15]% Strength <for [post-[Rank Five era]] units>",
                 "[+2 Happiness]", w("+500")]},
    {"name": "Shattered Fate", "isNationalWonder": True, "cost": 1, "uniques": ["Unbuildable", "Cannot be purchased"]},
    {"name": "Fate Seized", "isNationalWonder": True, "cost": 1, "uniques": ["Unbuildable", "Cannot be purchased"]}
] + gen_paths.halls() + [
])

# ---------------- Policies (4 branches) ----------------
dump("Policies.json", [
    {"name": "Righteous Path", "era": E12, "priorities": {"Southern Border Supremacy": 2, "Endurance": 6}, "uniques": [
        "Only available <before adopting [Demonic Path]>",
        "Resting point for Influence with City-States is increased by [15]",
        "[-25]% maintenance costs <in [Friendly Land] tiles>",
        "[+10]% Strength <vs [Demonic Infamy] units>"], "policies": [
        {"name": "Clan Rules", "row": 1, "column": 1, "uniques": ["[-15]% Unhappiness from [Population] [in all cities]"]},
        {"name": "Righteous Alliance", "row": 1, "column": 3, "uniques": [
            "City-State Influence recovers at twice the normal rate",
            "Gifts of Gold to City-States generate [+25]% more Influence",
            # C2: the written three-village alliance (R V1c127); demonic clans can never pact
            "Enables Defensive Pacts"]},
        {"name": "Guardian Formations", "row": 2, "column": 2, "requires": ["Clan Rules"],
         # canon overhaul: +25% made every righteous village unassailable once all four clans started righteous (no
         # war in 12 autoplay games); +10% leaves a war worth starting (3 of 12)
         "uniques": ["[+10]% Strength for cities", "[+10]% Strength <when defending>"]},
        {"name": "Righteous Path Complete", "uniques": ["[-10]% maintenance costs",
                                                        "Earn [100]% of killed [Demonic Infamy] unit's [Cost] as [Gold]"]}]},
    {"name": "Demonic Path", "era": E12, "priorities": {"Southern Border Supremacy": 6, "Endurance": 2}, "uniques": [
        "Only available <before adopting [Righteous Path]>",
        "Earn [50]% of killed [Military] unit's [Cost] as [Gold]",
        "[+50]% City-State Influence degradation",
        "Triggers a [Betrayal] event <upon turn start> <with [3]% chance>",
        # C1: a demonic clan is marked; the first line fires once, on adoption [src PolicyManager.adopt]
        "[Military] units gain the [Demonic Infamy] promotion",
        "All newly-trained [Military] units [in all cities] receive the [Demonic Infamy] promotion"], "policies": [
        {"name": "Plunder", "row": 1, "column": 1, "uniques": ["[+100]% Yield from pillaging tiles",
                                                             "Receive [+100]% Gold from Barbarian encampments and pillaging Cities"]},
        # R2 T1: the S6 'rogue cultivator' strategy (demonic Gu Masters are lone cultivators, vol2 ch81); was Blood Harvest
        {"name": "Lone Cultivators", "row": 1, "column": 3, "uniques": ["[2] units cost no maintenance",
                                                                      "[+30]% unhappiness from the number of cities"]},
        {"name": "Ruthless Cultivation", "row": 2, "column": 2, "requires": ["Plunder"], "uniques": [
            "Upon capturing a city, receive [3] times its [Gold] production as [Gold] immediately",
            "[-20]% maintenance costs <when at war>",
            "[+20]% Unhappiness from [Population] [in all cities]"]},
        {"name": "Demonic Path Complete", "uniques": ["[+15]% Strength <when attacking>"]}]},
    {"name": "Moon Path", "era": E12, "priorities": {"Southern Border Supremacy": 5, "Endurance": 5}, "uniques": [
        "Only available <before adopting [Strength Path]>",
        "Provides [2] [Moon Orchid]",
        "[+5]% Strength <for [Moon Master] units> <for every [Adopted [[Moon Path] branch] Policies]>"], "policies": [
        {"name": "Moonlight Mastery", "row": 1, "column": 1, "uniques": ["[+15]% Strength <for units with [Moonlight Gu]>",
                                                                       "[+15]% Strength <for units with [Moon Raiment]>"]},
        {"name": "Orchid Beds", "row": 1, "column": 3, "uniques": ["Provides [2] [Moon Orchid]",
                                                                     "[-15]% maintenance costs <for [Moon Master] units>"]},
        {"name": "Moon Blade Step", "row": 2, "column": 2, "requires": ["Moonlight Mastery"],
         "uniques": ["[1] Movement <for [Moon Master] units>"]},
        {"name": "Moon Path Complete", "uniques": ["New [Gu Master] units start with [10] XP [in all cities]"]}]},
    {"name": "Strength Path", "era": E12, "priorities": {"Southern Border Supremacy": 5, "Endurance": 5}, "uniques": [
        "Only available <before adopting [Moon Path]>",
        # the 47-branch update: strength's dao marks clash strongly with water and metal (docs/PATHS.md), both ways
        "Only available <before adopting [Water Path]>", "Only available <before adopting [Metal Path]>",
        "Provides [2] [Wild Boar]",
        "[+5]% Strength <for [Strength Master] units> <for every [Adopted [[Strength Path] branch] Policies]>"], "policies": [
        {"name": "Boar Strength", "row": 1, "column": 1, "uniques": ["[+15]% Strength <for units with [White Boar Gu]>",
                                                                   "[+15]% Strength <for units with [White Jade Gu]>"]},
        {"name": "Beast Hunters", "row": 1, "column": 3, "uniques": ["Provides [2] [Wild Boar]",
                                                                   "[+25]% Strength <vs [Barbarians] units>"]},
        {"name": "Unyielding Body", "row": 2, "column": 2, "requires": ["Boar Strength"],
         "uniques": ["Heals [10] damage if it kills a unit"]},
        {"name": "Strength Path Complete", "uniques": ["[1] Movement <for [Strength Master] units>"]}]},
] + gen_paths.policy_branches())  # the other 45 canonical paths (the user, 2026-11-01)

# ---------------- Resources (7: Spirit Spring, 4 strategic Gu foods, Gu Inheritance, 1 luxury) ----------------
DEP = {"minorDepositAmount": {"sparse": 1, "default": 1, "abundant": 2},
       "majorDepositAmount": {"sparse": 2, "default": 2, "abundant": 3}}
SB = ["Guaranteed with Strategic Balance resource option"]
dump("TileResources.json", [
    # R3: canon primeval stones come from spirit springs (ch15; one per Qing Mao clan, ch180): rare, rich, not
    # tradeable, one guaranteed near each start with the Strategic Balance option; majors start near one
    dict({"name": "Spirit Spring", "resourceType": "Strategic", "terrainsCanBeFoundOn": ["Hill", "Grassland", "Plains", "Forest"],
          "gold": 2, "improvement": "Spring Cave", "improvementStats": {"gold": 3},
          "uniques": ["Cannot be traded", "Guaranteed with Strategic Balance resource option"]},
         minorDepositAmount={"sparse": 1, "default": 1, "abundant": 1},
         majorDepositAmount={"sparse": 1, "default": 1, "abundant": 1}),
    dict({"name": "Moon Orchid", "resourceType": "Strategic", "revealedBy": "Gu Feeding",
          "terrainsCanBeFoundOn": ["Grassland", "Plains", "Forest"], "food": 1, "improvement": "Plantation",
          "improvementStats": {"food": 1}, "uniques": SB}, **DEP),
    dict({"name": "Wild Boar", "resourceType": "Strategic", "revealedBy": "Gu Feeding",
          "terrainsCanBeFoundOn": ["Forest", "Jungle", "Grassland", "Hill"], "food": 1, "improvement": "Camp",
          "improvementStats": {"production": 1}, "uniques": SB}, **DEP),
    # R2 T4/T8: Jade Skin Gu eats jade -> Strategic (a consumed luxury is a non-decision [src])
    dict({"name": "Jade", "resourceType": "Strategic", "revealedBy": "Spirit Spring Lore",
          "terrainsCanBeFoundOn": ["Hill"], "gold": 1, "improvement": "Mine", "improvementStats": {"gold": 1},
          "uniques": SB}, **DEP),
    {"name": "Wine", "resourceType": "Strategic", "terrainsCanBeFoundOn": []},
    # R6: a buried inheritance, placed only by the Buried Inheritance event (never generated); not tradeable
    {"name": "Gu Inheritance", "resourceType": "Strategic",
     "terrainsCanBeFoundOn": ["Grassland", "Plains", "Tundra", "Desert", "Snow", "Hill", "Forest", "Jungle", "Marsh",
                              "Flood plains", "Oasis"],
     "science": 3, "culture": 2, "gold": 2, "improvement": "Inheritance Dig", "improvementStats": {"science": 2, "gold": 2},
     "uniques": ["Doesn't generate naturally", "Cannot be traded"]},
    {"name": "Furs", "resourceType": "Luxury", "terrainsCanBeFoundOn": ["Forest", "Tundra", "Jungle"], "gold": 2,
     "improvement": "Camp", "improvementStats": {"gold": 1}},
    # MOD_SPEC_2 C1: the three qi and rank-six essence; essence never regenerates by itself (MOD_SPEC_2 #2)
] + [{"name": r, "resourceType": "Strategic", "terrainsCanBeFoundOn": [], "uniques": ["Stockpiled", "Cannot be traded"]}
     for r in QI + [GREEN, LIFESPAN, MATERIALS, RED, WHITE, APRICOT]])

# ---------------- Terrains (Vanilla minus natural wonders and Fallout) ----------------
ter = [t for t in json5.load(open(os.path.join(VAN, "Terrains.json")))
       if t.get("type") != "NaturalWonder" and t["name"] != "Fallout"]
for t in ter:
    t["uniques"] = [u for u in t.get("uniques", []) if "receive an extra [Sheep]" not in u]  # R3: no extra springs
# the twelve secret realms of heaven and earth (MOD_SPEC_2 #13, data/secret_realms.csv) as natural wonders; each grants a
# promotion to land units beside it, and the two hazardous ones hurt units that end their turn inside
def realm(r):
    t = {"name": r["name"], "type": "NaturalWonder", "occursOn": items(r["occurs_on"]), "turnsInto": r["turns_into"],
         "impassable": r["impassable"] == "true", "unbuildable": True, "weight": 10,
         "uniques": [f"Grants [{r['promotion']}] ([{r['comment']}]) to adjacent [{{Military}} {{Land}}] units for the rest of the game",
                     "Tile provides yield without assigned population"]
         + (["Must be adjacent to [6] [Water] tiles"] if r["turns_into"] == "Ocean" else ["Must be adjacent to [0] [Coast] tiles"])
         + ([f"Units ending their turn on this terrain take [{r['hazard']}] damage"] if r["hazard"] else [])}
    for kv in items(r["stats"]):
        k, v = kv.split(":")
        t[k] = int(v)
    return t


ter += [realm(r) for r in REALMS]
# the five regions' walls (界壁, R V5/22, V4/61, V4/279; T3 of docs/CANON_OVERHAUL.md), only on the Five Regions map:
# impassable to mortals; immortals cross them ("Can pass through impassable tiles") but suffer if they stop inside
REGION_WALLS = {"Miasma Wall": ((90, 130, 70), 25), "Licorice Wall": ((200, 180, 120), 20),
                "Azure Water Wall": ((60, 120, 190), 20), "Raging Flame Wall": ((220, 90, 40), 30),
                "Sage Wall": ((235, 230, 210), 20)}
ter += [{"name": n, "type": "Land", "impassable": True, "defenceBonus": 0.5, "RGB": list(rgb),
         "uniques": [f"Units ending their turn on this terrain take [{dmg}] damage",
                     "Has an elevation of [3] for visibility calculations",
                     "Considered [Undesirable] when determining start locations"]}
        for n, (rgb, dmg) in REGION_WALLS.items()]
dump("Terrains.json", ter)

# ---------------- Improvements ----------------
imp = [
    {"name": "Farm", "techRequired": "Aperture Awakening", "terrainsCanBeBuiltOn": ["Plains", "Grassland", "Desert", "Flood plains"],
     "food": 1, "turnsToBuild": 7, "uniques": ["Can also be built on tiles adjacent to fresh water"]},
    {"name": "Mine", "techRequired": "Spirit Spring Lore", "terrainsCanBeBuiltOn": ["Hill"], "production": 1, "turnsToBuild": 7},
    {"name": "Spring Cave", "techRequired": "Spirit Spring Lore", "turnsToBuild": 6,
     "uniques": ["Can only be built to improve a resource", "Pillaging this improvement yields approximately [+20 Gold]"]},
    {"name": "Plantation", "techRequired": "Gu Feeding", "turnsToBuild": 6,
     "uniques": ["Can only be built to improve a resource", "Does not need removal of [Forest]"]},
    {"name": "Camp", "techRequired": "Gu Feeding", "turnsToBuild": 6,
     "uniques": ["Does not need removal of [Forest]", "Does not need removal of [Jungle]", "Can only be built to improve a resource"]},
    {"name": "Road", "techRequired": "Spirit Spring Lore", "terrainsCanBeBuiltOn": ["Land"], "turnsToBuild": 4,
     "uniques": ["Can be built outside your borders", "Costs [1] [Gold] per turn when in your territory"]},
    {"name": "Beast Lair", "terrainsCanBeBuiltOn": ["Land"],
     "uniques": ["Unpillagable", "Unbuildable", "Excluded from map editor", "Marks a barbarian camp"]},
    {"name": "Inheritance Dig", "techRequired": "Inheritance Lore", "turnsToBuild": 5,
     "uniques": ["Can only be built to improve a resource", "Does not need removal of [Forest]", "Does not need removal of [Jungle]"]},
    {"name": "Inheritance Site", "terrainsCanBeBuiltOn": ["Land"],
     "uniques": ["Unpillagable", "Provides a random bonus when entered", "Unbuildable",
                 "Does not need removal of [Forest]", "Does not need removal of [Jungle]"]},
]
van_imp = {i["name"]: i for i in json5.load(open(os.path.join(VAN, "TileImprovements.json")))}
for n, tech in (("Remove Forest", "Spirit Spring Lore"), ("Remove Jungle", "Gu Formations"), ("Remove Marsh", "Gu Formations"),
                ("Remove Road", None), ("Cancel improvement order", None), ("Repair", None), ("City ruins", None),
                ("City center", None)):
    i = dict(van_imp[n])
    if tech:
        i["techRequired"] = tech
    else:
        i.pop("techRequired", None)
    imp.append(i)
dump("TileImprovements.json", imp)

# ---------------- Ruins (6) ----------------
dump("Ruins.json", [
    {"name": "Primeval Stone Cache", "notification": "We found [goldAmount] primeval stones in a dead Gu Master's cache!",
     "weight": 4, "uniques": ["Gain [30]-[60] [Gold]"]},
    {"name": "Cultivation Notes", "notification": "A dead Gu Master's notes yield new insight.", "weight": 3,
     "uniques": ["Gain [15]-[30] [Science]"]},
    {"name": "Unfinished Refinement", "notification": "An unfinished refinement waits in the inheritance.", "weight": 3,
     "uniques": ["Triggers a [Refinement Attempt] event", "Only available <for [Military] units>", "Unavailable <for [Beast] units>",
                 "Unavailable <when below [50] HP>"] + PROMO_DEAD},
    {"name": "Inheritance Trial", "notification": "The inheritance tests our Gu Master.", "weight": 2,
     "uniques": ["[This Unit] gains [30] XP", "[This Unit] takes [40] damage", "Only available <for [Military] units>", "Unavailable <for [Beast] units>",
                 "Unavailable <when below [41] HP>"]},
    {"name": "Inheritance Trap", "notification": "The inheritance was guarded by a trap!", "weight": 1,
     "uniques": ["[This Unit] takes [40] damage", "Only available <for [Military] units> <after turn number [10]>"]},
    # R2 T1: was 'Wandering Rogue Cultivator' (no rogue-cultivator faction on Qing Mao; clans hire lone demonic GMs, ch74)
    {"name": "Lone Demonic Gu Master", "notification": "A lone demonic Gu Master sheltering in the ruins offers us his services.",
     "weight": 1, "uniques": ["Free [Rank One Gu Master] found in the ruins"]},
])


# ---------------- Nations ----------------
# D4 (the user, 2026-10-19): all four majors start righteous, as in canon; the demonic camp is reached through the
# Collusion Exposed and Blood Lake events (a camp can flip both ways, as for the Fang clan and Wei Yang in canon)
RIGHTEOUS_START = "Starts with [Righteous Path] adopted"
# C5: canon voices in the mod's own words (conflicts research, M7)
VOICES = {
    "Gu Yue Clan": ("I am Gu Yue Bo of the Gu Yue clan. Our village has stood on Qing Mao longer than any other; speak, and be brief.",
                    "The covenant of the alliance slope does not shelter you. The Gu Yue will settle this themselves.",
                    "Take the village. The spring beneath it will outlast you too."),
    "Bai Clan": ("The Bai clan bows to no overlord any more. Remember that when you speak.",
                 "One spring makes a village; three make a clan. Yours will be the second.",
                 "Centuries under another clan's heel, and it ends like this."),
    "Xiong Clan": ("Xiong village. Count our Gu Masters before you call us weak.",
                   "You spent your strength on the wolves. We kept ours.",
                   "Even a bear has to sleep."),
    "Heavenly Court": ("Duke Long of the Heavenly Court. Fate keeps the world in order; we keep Fate.",
                       "You have strayed from your fate. The Court will set it right.",
                       "Fate itself was broken here. Remember who broke it."),
    "Huang Jin Family": ("The Huang Jin answer to no one on the plains. Speak plainly.",
                         "The blood of Giant Sun does not ask permission.",
                         "Scatter us if you can; one Huang Jin line always survives."),
    "Zombie Alliance": ("The Zombie Alliance greets you. We are righteous, of course. Ask anyone still breathing.",
                        "Your immortals will keep. Ours never age.",
                        "Dead again. It was bound to happen."),
    "Fang Clan": ("The Fang clan builds what lasts. What have you built?",
                  "Our Gu Houses are already moving. You should have counted them.",
                  "A fortress falls once. Our name will outlast it."),
    "Wu Clan": ("Wu Ji of the Wu clan. The Southern Border keeps me busy; state your purpose.",
                "The righteous never strike without a reason. Here is ours.",
                "Write it down: the Wu fell to you. Few will believe it."),
}


def nation(name, leader, pers, outer, inner, cities, uniques):
    d = {"name": name, "leaderName": leader, "adjective": [name], "personality": pers, "outerColor": outer,
         "innerColor": inner, "cities": cities, "uniques": uniques}
    if name in VOICES:
        d["introduction"], d["declaringWar"], d["defeated"] = VOICES[name]
    return d


def emblem(gu, extra=""):
    # R2 T3: canon - new students pick their first Gu free from the academy Gu room; most take the clan emblem Gu
    return (f"All newly-trained [Rank One Gu Master] units [in all cities] receive the [{gu}] promotion "
            f"<in cities with a [Gu Academy]>" + (f" {extra}" if extra else ""))


dump("Nations.json", [
    nation("Gu Yue Clan", "Gu Yue Bo", "Gu Yue Temperament", [30, 40, 90], [220, 220, 240],
           ["Gu Yue Village", "Alliance Slope", "Spear Bamboo Grove", "Stone Forest"],
           [emblem("Moonlight Gu", "<when above [0] [Moon Orchid]>"), RIGHTEOUS_START, "Start bias [Spirit Spring]",
            "Start bias [Hill]"]),
    # R2 T2: the Bai and Xiong leaders are never named in canon (bai jia zu zhang / xiong jia zu zhang)
    nation("Bai Clan", "Bai Clan Leader", "Bai Temperament", [230, 230, 230], [40, 70, 120],
           ["Bai Village", "Back-Slope Waterfall", "Deep Pool", "Bitter Shell Pool"],
           [emblem("Stream Gu"), "[+15]% Strength <vs [Barbarians] units>", RIGHTEOUS_START, "Start bias [Spirit Spring]",
            "Start bias [Fresh Water]"]),
    nation("Xiong Clan", "Xiong Clan Leader", "Xiong Temperament", [90, 50, 20], [240, 200, 140],
           ["Xiong Village", "Front Slope", "Honey Hollow"],
           [emblem("Bear Strength Gu"), "Starts with [Strength Path] adopted", RIGHTEOUS_START, "Start bias [Spirit Spring]",
            "Start bias [Hill]"]),
    # canon start biases (geography research): Xiong on the front slope (R V1c65), Wu by the rivers (R V2c1)
    # R3: the fourth major is the Wu clan, the Southern Border's first clan (user's choice); leader Wu Ji (vol2 ch84)
    nation("Wu Clan", "Wu Ji", "Wu Temperament", [120, 20, 20], [250, 210, 120],
           ["Wu Yi Mountain", "Moon Bowl", "Golden Cloud Canyon", "Xuan Ming Mountain"],
           [RIGHTEOUS_START, "Start bias [Spirit Spring]", "Start bias [River]"]),
    # C5c: the arc's majors (LORE_MAPPING "Nations"; B1, B2); all start righteous (D4; the Zombie Alliance shows a
    # righteous face, R V4c242)
    nation(HC, "Duke Long", "Heavenly Court Temperament", [235, 225, 180], [70, 60, 140],
           ["Heavenly Court", "Tian Ti Mountain", "Fate Pavilion", "Central Continent Gate"],
           [RIGHTEOUS_START, f"[+15]% Strength <vs [{ZOMBIE}] units>", "Start bias [Hill]"]),
    nation(HJ, "Huang Jin Patriarch", "Huang Jin Temperament", [200, 160, 40], [90, 40, 20],
           ["Imperial Court", "Golden Tent", "Northern Plains Camp"],
           [RIGHTEOUS_START, "[+15]% Strength <when defending>", "Start bias [Grassland]"]),
    nation(ZA, "Zombie Alliance Elder", "Zombie Alliance Temperament", [60, 80, 70], [180, 220, 190],
           ["Eastern Sea Hall", "Bone Isle", "Still Tide Harbour"],
           [RIGHTEOUS_START, "Start bias [Coast]",
            f"Free [{ZOMBIE}] appears <upon losing a [{{post-[Rank Five era]}} {{non-[Advancing]}} {{non-[{ZOMBIE}]}}] unit>"]
           + per_speed(lambda m: f"Instantly provides [1] [{LIFESPAN}] <upon turn start> <every [{turns(10, m)}] turns> "
                                 f"<for every [1] [[post-[Rank Five era]] Units]>")),
    nation(FANG, "Fang Clan Head", "Fang Temperament", [150, 110, 60], [240, 230, 200],
           ["Fang Fortress", "Sand Gate", "Dune Workshop"],
           [RIGHTEOUS_START, "[+50]% Production when constructing [Gu House] units [in all cities]",
            "[+10]% [Science] [in all cities]", "Start bias [Desert]"]),
    # R2 T7
    {"name": "Hairy Man Tribe", "cityStateType": "Refiner Tribe", "outerColor": [60, 30, 10], "innerColor": [255, 230, 180],
     "cities": ["Bronze Hall"]},
    {"name": "Foothill Villages", "cityStateType": "Mortal Villages", "outerColor": [110, 90, 50],
     "innerColor": [240, 240, 210], "cities": ["Qing Mao Foothills"]},
    {"name": "Jia Clan", "cityStateType": "Merchant Clan", "outerColor": [120, 90, 0], "innerColor": [255, 230, 120],
     "cities": ["Jia Village"]},
    # C5c: four arc city-states (R V3/55, V4/55, V5/640)
    {"name": "Lang Ya Sect", "cityStateType": "Refiner Tribe", "outerColor": [90, 60, 30], "innerColor": [230, 210, 160],
     "cities": ["Lang Ya Blessed Land"]},
    {"name": "Spirit Affinity House", "cityStateType": "Immortal Sect", "outerColor": [150, 90, 130],
     "innerColor": [250, 240, 245], "cities": ["Spirit Affinity House"]},
    {"name": "Combat Immortal Sect", "cityStateType": "Immortal Sect", "outerColor": [140, 30, 30],
     "innerColor": [240, 220, 200], "cities": ["Combat Immortal Peak"]},
    {"name": "Merman Imperial Court", "cityStateType": "Merchant Clan", "outerColor": [30, 90, 130],
     "innerColor": [200, 240, 250], "cities": ["Merman Court"], "uniques": ["Start bias [Coast]"]},
    {"name": "Barbarians", "outerColor": [0, 0, 0], "innerColor": [185, 12, 12],
     "uniques": ["Can only heal by pillaging", "Excluded from map editor"]},
    {"name": "Spectator", "outerColor": [255, 255, 255]},
])
dump("CityStateTypes.json", [
    # C5c: the ten great ancient sects' city-states
    {"name": "Immortal Sect", "color": [150, 120, 200], "friendBonusUniques": ["[+2 Culture] [in capital]"],
     "allyBonusUniques": ["[+2 Culture] [in capital]", "[+15]% Strength <for [post-[Rank Five era]] units>"]},
    {"name": "Refiner Tribe", "color": [180, 120, 60], "friendBonusUniques": ["[+2 Science] [in capital]"],
     "allyBonusUniques": ["[+2 Science] [in capital]", "[+20]% XP gained from combat"]},
    {"name": "Mortal Villages", "color": [150, 130, 80], "friendBonusUniques": ["[+2 Food] [in capital]"],
     "allyBonusUniques": ["[+2 Food] [in capital]", "[+2 Production] [in capital]"]},
    # R2 T4/T7: the caravan's tree-house Gu shop sold Fang Yuan his Black Boar Gu (before he chose a path, so since C3
    # every newly trained Gu Master may get one: a new unit holds no path yet)
    {"name": "Merchant Clan", "color": [255, 216, 0], "friendBonusUniques": ["[+2 Gold] [in capital]"],
     "allyBonusUniques": ["[+3 Gold] [in capital]", "[+10]% [Gold]",
                          "All newly-trained [Gu Master] units [in all cities] receive the [Black Boar Gu] promotion <when above [0] [Wild Boar]>"]},
])
dump("Personalities.json", [
    # C4 (conflicts research M6): Gu Yue the declining overlord that brokers alliances and lives off caravans; Bai the
    # rising aggressor after all three springs; Xiong the free-rider; Wu the coalition leader. Never declareWar 0 [src].
    {"name": "Gu Yue Temperament", "science": 7, "culture": 6, "gold": 5, "military": 4, "aggressive": 3,
     "declareWar": 3, "diplomacy": 7, "commerce": 7, "loyal": 6,
     "priorities": {"Moon Path": 10, "Righteous Path": 6},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions",
                 "Will not build [Flower Wine Monk Inheritance]"]},
    {"name": "Bai Temperament", "gold": 7, "production": 6, "science": 6, "military": 6, "aggressive": 8,
     "declareWar": 9, "expansion": 7, "diplomacy": 3, "loyal": 3, "preferredVictoryType": "Southern Border Supremacy",
     "priorities": {"Righteous Path": 8},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
    {"name": "Xiong Temperament", "military": 7, "aggressive": 6, "production": 6, "declareWar": 5, "loyal": 2,
     "diplomacy": 6,
     "preferredVictoryType": "Southern Border Supremacy",
     "priorities": {"Strength Path": 10, "Righteous Path": 3},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
    {"name": "Heavenly Court Temperament", "science": 8, "military": 6, "aggressive": 4, "declareWar": 4, "diplomacy": 6,
     "loyal": 7, "uniques": ["[+500]% weight to [Fate Gu] for AI decisions"]},
    {"name": "Huang Jin Temperament", "military": 7, "aggressive": 6, "declareWar": 6, "expansion": 6, "loyal": 5},
    {"name": "Zombie Alliance Temperament", "gold": 7, "military": 6, "aggressive": 5, "declareWar": 5, "commerce": 7,
     "loyal": 3},
    {"name": "Fang Temperament", "production": 8, "science": 6, "military": 5, "declareWar": 4, "diplomacy": 5,
     "uniques": ["[+200]% weight to [Gu House Formation] for AI decisions"]},
    {"name": "Wu Temperament", "military": 7, "aggressive": 4, "production": 6, "loyal": 7, "expansion": 5,
     "declareWar": 6, "diplomacy": 7,
     "preferredVictoryType": "Southern Border Supremacy",
     "priorities": {"Righteous Path": 10, "Strength Path": 4},  # D3: the clan walks wind; Wu Ji alone walks strength
     "uniques": ["[+50]% weight to [Martial Arena] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
])
dump("VictoryTypes.json", [
    {"name": "Southern Border Supremacy", "milestones": ["Capture all capitals"]},
    {"name": "Endurance", "milestones": ["Have highest score after max turns"]},
    # C5b (MOD_SPEC_3): Fang Yuan's goal, beyond any Venerable
    {"name": "Eternal Life", "milestones": ["Build [Eternal Life]"]},
])

TECHMAP = {"Pottery": "Spirit Spring Lore", "Animal Husbandry": "Gu Feeding", "Mining": "Wine Brewing",
           "The Wheel": "Gu Refinement"}
diffs = json5.load(open(os.path.join(VAN, "Difficulties.json")))
for d in diffs:
    for k in ("playerBonusStartingUnits", "aiMajorCivBonusStartingUnits", "aiCityStateBonusStartingUnits"):
        d[k] = [{"Scout": "Rank One Gu Master", "Settler": "Clan Settler", "Worker": "Mortal Laborer"}.get(u, u) for u in d.get(k, [])]
    d["aiFreeTechs"] = [TECHMAP[t] for t in d.get("aiFreeTechs", [])]
    d["baseHappiness"] = d.get("baseHappiness", 0) + 6  # Slice 1 has one luxury (Furs) instead of Vanilla's many
dump("Difficulties.json", diffs)
dump("Speeds.json", json5.load(open(os.path.join(VAN, "Speeds.json"))))



# ---------------- Write-out ----------------
stale = sorted(set(os.listdir(OUT)) - set(WRITTEN))
if ARGS.check:
    repo = REPO_ROOT / "jsons"
    diff = [n for n in WRITTEN if not (repo / n).is_file() or not filecmp.cmp(repo / n, Path(OUT) / n, shallow=False)]
    extra = sorted(p.name for p in repo.glob("*.json") if p.name not in WRITTEN) if repo.is_dir() else []
    _TMP.cleanup()
    if diff or extra:
        print("[gen_ruleset] jsons/ is out of date; run tools/gen_ruleset.py and commit: " + ", ".join(diff + extra))
        sys.exit(1)
    if not ARGS.quiet:
        print(f"[gen_ruleset] jsons/ matches data/ ({len(WRITTEN)} files)")
    sys.exit(0)
for n in stale:
    if n.endswith(".json"):
        os.remove(os.path.join(OUT, n))  # a file the generator no longer writes would go on loading in game
if not ARGS.quiet:
    print(f"[gen_ruleset] wrote {len(WRITTEN)} files to {OUT}, {len(set(ALL_UNIQUES))} distinct uniques"
          + (f"; removed stale {', '.join(n for n in stale if n.endswith('.json'))}" if any(n.endswith('.json') for n in stale) else ""))
