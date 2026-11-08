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
import lifespan as LS  # immortal lifespan numbers (tools/lifespan.py), shared with the Tutorial page
import sound_names as sfx  # sound file names (tools/art/sfx.py synthesizes them)
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
       "<for units without [Aptitude C]> <for units without [Aptitude D]> <for units without [Extreme Physique]>")

# ---------------- Reference audit Layer 1 (docs/REFERENCE_AUDIT.md): small stages, rank relics, extreme physiques ----
# Every rank has four small stages, initial, middle, upper and peak; from a rank's peak to the next rank's initial is the
# big breakthrough, far harder, and it burns many primeval stones (R V1c63, V1c81, V1c90). Initial is the bare rank. A Gu
# Master climbs the stages by itself: a countdown status, shorter for a better aptitude and twice as long once immortal
# (an immortal's small stage takes years of aperture time, ADAPTED); each stage adds STAGE_BONUS % Strength. A rank change
# starts again at initial: the new unit's creation triggers run after its promotions are copied [src
# UnitManager.placeUnitNearTile], so STAGE_RESET on every rank unit drops the old rank's stages, ascension included.
from cultivation import (CULTIVATING, EARLY_PREMIUM, IMMORTAL_STAGE_FACTOR, PEAK_DISCOUNT, PHYSIQUE, PHYSIQUE_CHANCE,  # noqa: E402,E501
                         PHYSIQUE_DOOM, DOOMED, RELICS, STAGE_BONUS, STAGE_TURNS, STAGES)
STAGE_RESET = [f"[This Unit] loses the [{s}] promotion" for s in reversed(STAGES)]


def stage_step(trigger=""):
    """One small stage more, highest first so a single trigger climbs one stage only (as dao_step)."""
    t = f" {trigger}" if trigger else ""
    return [f"[This Unit] gains the [Peak Stage] promotion{t} <for units with [Upper Stage]>",
            f"[This Unit] gains the [Upper Stage] promotion{t} <for units with [Middle Stage]> <for units without [Upper Stage]>",
            f"[This Unit] gains the [Middle Stage] promotion{t} <for units without [Middle Stage]>"]


def stage_lines():
    """The Gu Master unit type's cultivation: one countdown per aptitude, mortal or immortal, and game speed."""
    out = []
    for apt, base in STAGE_TURNS.items():
        for factor, who in ((1, "<for [pre-[Rank Six era]] units>"), (IMMORTAL_STAGE_FACTOR, "<for [post-[Rank Five era]] units>")):
            out += per_speed(lambda m, apt=apt, n=base * factor, who=who:
                             f"[This Unit] gains the [{CULTIVATING}] status for [{turns(n, m)}] turn(s) <upon turn start> "
                             f"<for units without [{CULTIVATING}]> <for units without [Peak Stage]> <for units with [{apt}]> "
                             f"{who} <for [non-[Venerable]] units>")
    return out + stage_step(f"<upon losing the [{CULTIVATING}] status>")


# Relic Gu (舍利蛊): used once, it raises a Gu Master one small stage at once; one colour for every mortal rank, and a
# rank-two relic sells for thousands of stones (R V1c53, V1c111, V1c112). A kept promotion (E4) that pays its stones and
# climbs one stage on purchase, then is spent at the next turn start; closed at the peak, where it would do nothing.
def relic(colour, only, stones):
    name = f"{colour} Relic Gu"
    return {"name": name, "unitTypes": GM_TYPES, "uniques": [
        f"Only available {only}", "Unavailable <for units with [Peak Stage]>", f"Unavailable <when below [{stones}] [Gold]>",
        f"Gain [-{stones}] [Gold]", *stage_step(), f"[This Unit] loses the [{name}] promotion <upon turn start>", w("+50")]}


# The ten extreme physiques (十绝体): the essence fills the whole aperture, cultivation quickens as the rank rises, and
# heaven does not suffer them: the aperture finally bursts; only becoming an immortal saves them (R V1c135, V1c140,
# V1c144, V3c159, V3c181). One awakening in a hundred; the bearer cultivates a stage in 5 turns and dies when the
# Doomed Aperture runs out, unless it has ascended by then (numbers in tools/cultivation.py).
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


AI_LATE_UPKEEP = 30  # Phase D: the AI's late-game upkeep relief, percent (GlobalUniques)


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
# the user (2026-11-05): immortals fly, so they cross the Eastern Sea and every water, yet land units can still strike
# them. A land unit with this unique is never embarked [src MapUnit.isEmbarked], so it fights at full strength over
# water, and land melee units may attack it there once embarkation is known [src TargetHelper], which the first tech
# grants. Both uniques are cached: permanent on the unit, never on a status.
FLIGHT = ["May travel on Water tiles without embarking", "Ignores terrain cost"]
# a region wall drags the strong harder (canon research 2026-11-08: R V5c535, V4c286): on top of the wall's own damage,
# an immortal that ends its turn inside takes this much more by rank; desolate beasts "belong to their region" the
# same way (R V5c24). Rank nine is beyond the walls.
WALLS = ["Miasma Wall", "Licorice Wall", "Azure Water Wall", "Raging Flame Wall", "Sage Wall"]
WALL_STRAIN = {6: 10, 7: 30, 8: 60}


# Regions II: every year the earth tide thins the Azure Water wall and immortals of three regions slip into the Eastern
# Sea (R V4c170): the sea's wall drags an immortal half as hard as the others
EARTH_TIDE_WALL = "Azure Water Wall"


def wall_strain(n):
    return [f"[This Unit] takes [{n // 2 if w == EARTH_TIDE_WALL else n}] damage <upon ending a turn in a [{w}] tile>"
            for w in WALLS]
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
MATERIALS = gen_paths.GC.MATERIALS
# audit P5: an immortal aperture grows immortal materials (the refiners' stock); higher grades grow more
LAND_MATERIALS = {"Lower": 1, "Middle": 1, "Upper": 2, "Super": 2}
GROTTO_MATERIALS = 3


def ascended(grade, weight, a, d):
    return {"text": f"{'An' if grade == 'Upper' else 'A'} {grade.lower()}-grade blessed land opens", "uniques": [
        f"[This Unit] gains the [{grade} Grade Blessed Land] promotion", f"Instantly provides [{LS.GRANT[6]}] [{LIFESPAN}]",
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
        f"Gain [{stones}] [Gold] <upon turn start> <for units without [{RAVAGED}]>",
        f"Instantly provides [{LAND_MATERIALS[grade]}] [{MATERIALS}] <upon turn start> <for units without [{RAVAGED}]>"]
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
# Phase D (the user, 2026-11-02): a higher rank lives longer, so it burns its Lifespan Gu more slowly (tools/lifespan.py)
def immortal_life(rank):
    return [f"Instantly consumes [1] [{LIFESPAN}] <upon turn start> <every [{turns(LS.BURN[rank], m)}] turns> "
            f"<on [{n}] game speed>" for n, m in SPEEDS] + [
        f"Can only heal by pillaging <when below [1] [{LIFESPAN}]>",
        f"[This Unit] takes [{LS.STARVE_DAMAGE}] damage <upon turn start> <when below [1] [{LIFESPAN}]>"]


# Phase D: an immortal cultivates wherever it stands (its aperture is its own academy); in autoplay the AI's
# immortals lacked the XP for the Great and Supreme Grandmaster tiers and never reached a Venerable
IMMORTAL_XP = ["[This Unit] gains [3] XP <upon turn start>",
               "[This Unit] gains [5] XP <upon turn start> <for [Rank Eight Gu Immortal] units>"]  # a grotto-heaven: faster insight
IMMORTAL_RANK = {"Rank Six Gu Immortal": 6, "Rank Seven Gu Immortal": 7, "Rank Eight Gu Immortal": 8}


# Regions (canon research 2026-11-08, docs/REGIONS.md): each region starts as old and as strong as the canon makes it.
# The head start lands once, when a civ founds its first city [src CityFounder: the trigger runs with that city].
FIRST_CITY = "<upon founding a city> <when number of [Cities] is less than [2]>"
# autoplay (8 x 450, 2026-11-08): with the contest's XP lasting as long as the gap between contests (13 turns) and +5
# happiness, the Huang Jin tribes held 7.4 cities at T150 (4.5 before), raised a Venerable in 5 of 8 games and won 3,
# while the Southern Border raised none. The canon gives the contest's winners shelter and the blessed land's
# inheritances, not a standing school, and makes the plains short of rank eights (R V4c164): the XP lasts 5 turns and
# the war economy gives +3
CONTEST_XP_TURNS, HJ_HAPPINESS = 5, 3


def head_start(techs, units=0, unit=""):
    return ([f"[{techs}] Free Technologies {FIRST_CITY}"] if techs else []) + (
        [f"[{units}] free [{unit}] units appear {FIRST_CITY}"] if units else [])


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
DAO_EFFECTS = [["[+10]% Strength"], ["[+20]% Strength"], ["[+30]% Strength"], ["[+40]% Strength", "[+10] HP when healing"],
               ["[+55]% Strength", "[+15] HP when healing"]]  # Phase D power rebuild (was 5/10/15/20/30)
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
           "[This Unit] gains the [Advancing] status for [1] turn(s)",
           # the user (2026-11-02): each rank climbed lengthens the immortal's life
           f"Instantly provides [{LS.GRANT[7 if target == 'Rank Seven' else 8]}] [{LIFESPAN}]"] + extra
        + ["[This Unit] upgrades for free including special upgrades", w("+200")]}


# ---------------- MOD_SPEC_2 C5b: the Venerable, Eternal Life, Gu Houses ----------------
# Rank nine is never an era (MOD_SPEC_2): a Venerable rises when a clan holding a rank-eight immortal of supreme
# attainment builds the Venerable Ascension (one in the world at a time). The Venerable is unbeatable in its era but
# only long-lived (R V6/105, V3/194): it burns Lifespan Gu like every immortal, while its yellow apricot essence pays for
# Eternal Life, Fang Yuan's goal and the arc's victory (MOD_SPEC_3). When it dies its ascension is removed (the race
# reopens, Phase A2) and its clan gains the seal of its true inheritance.
APRICOT = "Yellow Apricot Immortal Essence"  # rank nine (R V6/249)
ETERNAL_COST = 300  # yellow apricot essence for Eternal Life on Standard (was 150 until Phase D, 2026-11-02)
VEN_ELSEWHERE = "<if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed>"
VENERABLE = "Venerable"
HOUSE_MATERIALS = 60  # audit P5: a Gu House is refined from immortal materials too
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
    f"Gain [12] [Gold] <upon turn start> <for units without [{RAVAGED}]>",
    f"Instantly provides [{GROTTO_MATERIALS}] [{MATERIALS}] <upon turn start> <for units without [{RAVAGED}]>"]
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
] + per_speed(
    # Phase D: unit upkeep grows with the game's progress p, x(1 + p) and then ^(1 + p/3) [src CivInfoStatsForNextTurn.
    # getUnitMaintenance], and the engine's AI keeps its army regardless: after T300 a third of AI clan-turns ran in
    # debt and clans touched the -200 disband line (autoplay, Five Regions, 8 x 450; upkeep 67 against income 83 a
    # turn at T330-400). From 60% of the game on, an AI clan's units cost 30% less; a player's cost the same.
    lambda m: f"[-{AI_LATE_UPKEEP}]% maintenance costs <for [AI player] Civilizations> <after turn number [{turn_gate(300, m)}]>"
) + [
    # reference audit Layer 1: the big breakthrough is cheap from the peak and dear before it
    f"[-{PEAK_DISCOUNT}]% Gold cost of upgrading <for units with [Peak Stage]>",
    f"[+{EARLY_PREMIUM}]% Gold cost of upgrading <for units without [Peak Stage]>",
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
                        f"<with [{chance(3, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    # Phase D: demonic raids and lone Gu Masters reach every clan in every region
    lambda m: f"Triggers a [Demonic Raid] event <upon turn start> <after turn number [{turn_gate(60, m)}]> "
              f"<with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Wandering Gu Master] event <upon turn start> <after turn number [{turn_gate(30, m)}]> "
              f"<with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    # Regions II: the Refinement Conference, once every hundred years (R V4c179)
    lambda m: f"Triggers a [Refinement Conference] event <upon turn start> <every [{turns(130, m)}] turns> "
              f"<for [Major] Civilizations>") + per_speed(
    # demonic Gu Masters prey on the small clans of every region (faction research: R ch443, ch704, ch1650)
    lambda m: f"A [Demonic Gu Master] rebels <upon turn start> <after turn number [{turn_gate(40, m)}]> "
              f"<every [{max(1, round(m))}] turns> <with [1]% chance> <for [City-States] Civilizations>")})

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
dump("UnitTypes.json", [{"name": n, "movementType": "Land", **({"uniques": gen_paths.GC.spoils()
                                                                  + (stage_lines() if n == "Gu Master" else [])}
                                                                 if "Gu Master" in n else {})}
                        for n in ["Civilian", "Gu Master", "Moon Gu Master", "Strength Gu Master", "Beast", "Gu House"]])


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
RANK_WORD = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8}


def rank_attack_sound(name, fallback):
    """Phase D: the blow's body by rank (tools/art/sfx.py, sounds/gu-rank-<n>.ogg); the path, its tier and the dao marks
    layer their own sounds over it through Play-sound uniques."""
    w = name.split()
    return sfx.rank_sound(RANK_WORD[w[1]]) if len(w) > 1 and w[0] == "Rank" and w[1] in RANK_WORD else fallback


for u, r in zip(GU_MASTERS, table("gu_masters.csv")):
    u["attackSound"] = rank_attack_sound(r["name"], r["attackSound"])  # R5 had one built-in sound per path
    # Phase D power rebuild: the body alone is weaker; Gu, dao marks and comprehension carry the rest (path_powers.py)
    u["strength"] = gen_paths.PP.body_strength(int(r["strength"]), RANK_WORD[r["name"].split()[1]])
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
    u["uniques"] += [WILD_GU_TRIGGER, INHERITANCE_TRIGGER] + DAO_LINES + STAGE_RESET
    if r["name"] in IMMORTALS:
        u["uniques"] += immortal_life(IMMORTAL_RANK[r["name"]]) + IMMORTAL_XP  # MOD_SPEC_2 C2: immortals burn Lifespan Gu
        u["uniques"].append("Can pass through impassable tiles")  # immortals cross mountains and the region walls
        u["uniques"] += FLIGHT + wall_strain(WALL_STRAIN[IMMORTAL_RANK[r["name"]]])
        u["uniques"].append(gen_paths.PP.chasm())  # audit P1: the chasm between mortal and immortal
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
    # reference audit Layer 3: a beast group climbs hundred-, thousand- and ten-thousand-beast king, then beast emperor
    # (R V3c4); in the wolf tide the bold wolf is the hundred-beast king, the frenzy wolf the thousand-beast king and the
    # thunder crown wolf the ten-thousand (R V1c114, V1c130, V1c131). Frenzy wolves carry thunder wings (R V1c150)
    {"name": "Frenzy Lightning Wolf", "unitType": "Beast", "movement": 3, "strength": 22, "cost": 90, "attackSound": "shot",
     "requiredTech": "Rank Four Cultivation", "uniqueTo": "Barbarians",
     "uniques": ["[+15]% Strength bonus for [Beast] units within [2] tiles", "[+150]% maintenance costs"]},
    # C4: a desolate beast (荒兽), about a rank-six immortal (R V5/14); only events bring one
    {"name": DESOLATE, "unitType": "Beast", "movement": 3, "strength": 62, "cost": 200, "attackSound": "shot",
     "uniqueTo": "Barbarians", "uniques": ["Unbuildable", "[+15]% Strength <when defending>", "[+200]% maintenance costs",
                                           *wall_strain(WALL_STRAIN[6])]},
    {"name": ANCIENT, "unitType": "Beast", "movement": 3, "strength": 85, "cost": 300, "attackSound": "shot",
     "uniqueTo": "Barbarians", "uniques": ["Unbuildable", "[+15]% Strength <when defending>", "[+250]% maintenance costs",
                                           *wall_strain(WALL_STRAIN[7])]},
    {"name": IMMEMORIAL, "unitType": "Beast", "movement": 3, "strength": 115, "cost": 500, "attackSound": "shot",
     "uniqueTo": "Barbarians", "uniques": ["Unbuildable", "[+15]% Strength <when defending>", "[+300]% maintenance costs",
                                           *wall_strain(WALL_STRAIN[8])]},
    # C5b: the Venerable and the Gu Houses
    # the user (2026-11-01): rank nine dominates and terrifies. A Venerable is unbeatable in its era (R V6/105): it strikes
    # three times, walks through anything, enslaves the defeated, cows every enemy beside it. Its life is long but not
    # eternal: like every immortal it burns Lifespan Gu and wastes away without them (the user, 2026-11-02: "kenapa
    # venerable darahnya setiap langkah berkurang terus?" -- it lost 3 HP every turn and healed only by pillaging;
    # lifespan is now the Lifespan Gu stock, HP is only battle damage)
    {"name": VENERABLE, "unitType": "Gu Master", "movement": 5, "strength": gen_paths.PP.VENERABLE_STRENGTH, "cost": 1000,
     "requiredTech": "Dao Lord",
     "attackSound": sfx.rank_sound(9), "uniques": ["Unbuildable", "Cannot be purchased", "Limited to [1] per Civilization", NB,
                                         *immortal_life(9),
                                         f"Instantly provides [6] [{APRICOT}] <upon turn start>", "[+300]% maintenance costs",
                                         "[2] additional attacks per turn", "Can move after attacking", *FLIGHT,
                                         "Can pass through impassable tiles", "May capture killed [Military] units",
                                         "[-25]% Strength for enemy [Military] units in adjacent [All] tiles",
                                         "[+50]% Strength <vs cities>", "Destroys tile improvements when attacking",
                                         gen_paths.PP.chasm(gen_paths.PP.VENERABLE_CHASM),
                                         "[This Unit] gains [5] XP <upon turn start>", *DAO_LINES,
                                         f"[This Unit] gains the [Venerable Killer Move] status for [1] turn(s) <costs [20] [{APRICOT}]> <requires [1] movement>"]
     # slaughter restores it too
     + ["Heals [10] damage if it kills a unit"] + countdown("Chaos Countdown", 25, "Chaos Calamity")},
] + [{"name": n, "unitType": "Gu House", "movement": mv, "strength": st, "cost": 650, "requiredTech": "Gu House Formation",
      "attackSound": sfx.rank_sound(8), **({"uniqueTo": HC} if gu == "Fate Gu" else {}),
      "uniques": [f"Only available <if [{gu}] is constructed>", "Limited to [1] per Civilization",
                  "Can pass through impassable tiles", gen_paths.PP.chasm(), *wall_strain(WALL_STRAIN[8]),
                                          f"Costs [50] [{WHITE}]", f"Costs [{HOUSE_MATERIALS}] [{MATERIALS}]",
                                          "[+500]% maintenance costs", NB] + extra}
     for n, gu, st, mv, extra in GU_HOUSES] + [
    {"name": ZOMBIE, "unitType": "Gu Master", "movement": 2, "strength": gen_paths.PP.body_strength(70, 6), "cost": 300, "requiredTech": "Calamity Lore",
     "attackSound": sfx.rank_sound(6), "uniques": ["Unbuildable", "Cannot be purchased", NB, "Can only heal by pillaging", FATE_WEAK,
                                         "Can pass through impassable tiles", gen_paths.PP.chasm(), *FLIGHT,
                                         *wall_strain(WALL_STRAIN[6]),
                                         "[+100]% maintenance costs"]},
] + [
    {"name": "Thunder Crown Wolf", "unitType": "Beast", "movement": 3, "strength": 28, "cost": 120, "attackSound": "shot",
     "uniqueTo": "Barbarians",
     "uniques": ["Unbuildable", "[+20]% Strength bonus for [Beast] units within [2] tiles", "[+200]% maintenance costs"]},
] + [
    # Phase D (the user, 2026-11-02: "buat konflik ... dengan gu master penyendiri maupun gu master iblis"): lone and
    # demonic Gu Masters prey on every region. Camps (Beast Lairs, Demonic Dens) spawn any military unit the barbarians
    # can build once every clan knows its tech [src BarbarianManager.chooseBarbarianUnit, updateBarbarianTech], and the
    # Demonic Raid and Wandering Gu Master events bring them to a clan's door
    {"name": n, "unitType": "Gu Master", "movement": 2, "strength": round(st * gen_paths.PP.ROGUE_SHARE), "cost": cost,
     "requiredTech": tech,
     "attackSound": sfx.rank_sound(rank), "uniqueTo": "Barbarians", "uniques": extra}
    for n, st, cost, tech, rank, extra in (
        ("Lone Gu Master", 14, 60, "Rank Two Cultivation", 2, ["[+20]% Strength <when defending>"]),
        ("Demonic Gu Master", 22, 95, "Rank Three Cultivation", 3,
         ["[+20]% Strength <when attacking>", "Heals [15] damage if it kills a unit"]),
        ("Demonic Elder", 44, 190, "Purple Crystal Essence", 5,
         ["[+20]% Strength <when attacking>", "Heals [20] damage if it kills a unit",
          "[-10]% Strength for enemy [Military] units in adjacent [All] tiles"]))
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
from gu_rules import HUNGER, gu_promotion, hunger_statuses, stone_comment  # noqa: E402


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
def with_combos(promotions):
    """Phase D: each combination killer move's button on its first Gu, and the moves' one-turn statuses (tools/gu_combos.py)."""
    gen_paths.GCO.attach(promotions)
    return promotions + gen_paths.GCO.statuses()


dump("UnitPromotions.json", with_combos([
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
    {"name": "Bear Strength Gu", "uniques": [f"Comment [{stone_comment(10)[0]}]", "[+10]% Strength", "[+10]% maintenance costs"]},
    {"name": "Stream Gu", "uniques": [f"Comment [{stone_comment(10)[0]}]", "[+10] HP when healing", "[+10]% maintenance costs"]},
    # C1 (canon overhaul, conflicts research): the righteous hunt demonic cultivators and post bounties on them (R V2c29,
    # V2c35). A marker on every military unit of a Demonic Path clan; it clears itself once the clan's camp changes.
    {"name": "Demonic Infamy", "uniques": [
        "Comment [Righteous clans fight harder against this unit and pay a bounty for it]",
        "[This Unit] loses the [Demonic Infamy] promotion <upon turn start> <before adopting [Demonic Path]>"]},
    # R3 hunger statuses (timers; see hunger()); each removes itself once its food is back
] + [{"name": status, "uniques": [f"[This Unit] loses the [{status}] status <upon turn start> <when above [-1] [{food}]>"]}
     for food, status in HUNGER.items()]  # legacy since Phase D: kept so old saves load; nothing grants them now
    # Phase D: each Gu's hunger meter in percent (tools/gu_rules.py)
    + [st for r in table("gu.csv") for st in hunger_statuses(r["name"], r["food"], int(r["rank"]))]
    # C3 (MOD_SPEC_3): every canonical path's attainment tiers, killer moves and signature statuses (docs/PATHS.md)
    + gen_paths.promotions(GM_TYPES) + gen_paths.gu_promotions() + gen_paths.GC.promotions(GM_TYPES)
    + gen_paths.GC.bearers(GM_TYPES) + [
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
    # reference audit Layer 1: the small stages, their countdown, the rank relics, the extreme physique
    {"name": CULTIVATING, "uniques": ["Comment [When it runs out, the unit climbs one small stage]"]},
    # stages and the physique come from triggers only: with unitTypes the AI bought them with XP (autoplay, 98af8c4)
    *[{"name": st, "uniques": [f"[+{STAGE_BONUS}]% Strength"]} for st in STAGES],
    *[relic(c, only, stones) for c, only, stones in RELICS],
    {"name": PHYSIQUE, "uniques": [
        "[+20]% Strength", "[+50]% XP gained from combat", "[-20]% maintenance costs",
        f"[This Unit] is destroyed <upon losing the [{DOOMED}] status> <for [pre-[Rank Six era]] units>"]},
    {"name": DOOMED, "uniques": ["Comment [When it runs out, the aperture of a mortal bearer bursts and it dies]"]},
] + [{"name": d, "uniques": DAO_EFFECTS[i] + ([f"[This Unit] loses the [{DAO[i - 1]}] promotion"] if i else [])
         # Phase D: the marks ring over every attack, brighter with each tier (tools/art/sfx.py)
         + [f"Play [{sfx.dao_sound(i + 1)}] sound <upon damaging a [Military] unit> <when attacking>"]}
     for i, d in enumerate(DAO)] + [
    {"name": "Advancing", "uniques": ["Comment [Climbing to the next rank]"]},
    GROTTO, advance("Rank Seven"), advance("Rank Eight"),
    {"name": "Venerable Killer Move", "uniques": ["[+100]% Strength"]},
    # the arc's victory: the Venerable spends its yellow apricot essence on eternal life before its lifespan runs out
    # Phase D (2026-11-02): with immortals' lifespan growing by rank, every Five Regions autoplay game (6 x 400) raised a
    # Venerable (T314-378) and four won Eternal Life 30-35 turns later at 150. At ETERNAL_COST the Venerable reigns, and
    # can be hunted, for about twice as long: rank nine stays hard and long, as the user expects
    {"name": "Seek Eternal Life", "unitTypes": GM_TYPES, "uniques": [
        f"Only available <for [{VENERABLE}] units>", "Unavailable <if [Eternal Life] is constructed by anybody>",
        # Regions: the Court keeps fate and Heaven's Will; eternal life is the fate-defiers' dream, never its own
        f"Unavailable <for [{HC}] Civilizations>"]
        + [f"Unavailable <when below [{qi_cost(ETERNAL_COST, m)}] [{APRICOT}]> <on [{n}] game speed>" for n, m in SPEEDS]
        + [f"Instantly consumes [{qi_cost(ETERNAL_COST, m)}] [{APRICOT}] <on [{n}] game speed>" for n, m in SPEEDS]
        + ["Gain a free [Eternal Life] [in capital]", "[This Unit] loses the [Seek Eternal Life] promotion", w("+1000")]},
    {"name": "Ascend to Venerable", "unitTypes": GM_TYPES, "uniques": [
        f"Only available <for [{{Rank Eight Gu Immortal}} {{{gen_paths.SUPREME_MARKER}}}] units> <after discovering [Dao Lord]>",
        "Unavailable <if [Venerable Ascension] is constructed by anybody>", dao_at_least(3), "Unavailable <in [Foreign Land] tiles>",
        "Unavailable <in [Water] tiles>"]
        + [f"Unavailable <when below [{qi_cost(60, m)}] [{WHITE}]> <on [{n}] game speed>" for n, m in SPEEDS]
        + [f"Instantly consumes [{qi_cost(60, m)}] [{WHITE}] <on [{n}] game speed>" for n, m in SPEEDS]
        + ["Gain a free [Venerable Ascension] [in capital]", "[This Unit] loses the [Ascend to Venerable] promotion",
           f"Instantly provides [{LS.GRANT[9]}] [{LIFESPAN}]",
           # an upgrade keeps every promotion [src MapUnit.copyStatisticsTo]: without this the Venerable kept the
           # grotto-heaven's calamity and tribulation countdowns, whose essence choices stop at rank eight
           "[This Unit] loses the [Grotto-Heaven Aperture] promotion",
           "[This Unit] gains the [Advancing] status for [1] turn(s)", "[This Unit] upgrades for free including special upgrades",
           w("+500")]},
] + [{"name": r["promotion"], "uniques": [r["promotion_effect"]]} for r in REALMS] + [
    {"name": "Chaos Countdown", "uniques": ["Comment [When it runs out, a chaos calamity falls on the Venerable]"]},
]))

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
        # reference audit Layer 1: one of the ten extreme physiques, one awakening in a hundred
        {"text": "One of the ten extreme physiques", "uniques": [f"[This Unit] gains the [{PHYSIQUE}] promotion"]
         + per_speed(lambda m: f"[This Unit] gains the [{DOOMED}] status for [{turns(PHYSIQUE_DOOM, m)}] turn(s)") + [w(f"-{100 - PHYSIQUE_CHANCE}")]},
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
            # Layer 3: the thousand-beast king from rank four, the ten-thousand-beast king from rank five (was rank four)
            f"A [Frenzy Lightning Wolf] rebels <starting from the [{E4}]>",
            "A [Thunder Crown Wolf] rebels <starting from the [Rank Five era]>",
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
    # Regions: the golden tribes' contest for the Imperial Court every ten years, before the killing blizzard. Only
    # mortals fight, the immortals look on (Giant Sun's rule, R V3c120); the winners shelter in the blessed land and
    # take its inheritances, the losers face the blizzard (R V3c84, V3c147). A die, not a choice: the bigger army
    # wins more often
    {"name": "Imperial Court Contest", "presentation": "None", "text": "The golden tribes' contest for the Imperial "
     "Court opens before the killing blizzard. Only mortal Gu Masters may fight; the immortals look on.", "choices": [
        {"text": "Our Gu Masters take the court", "uniques": [
            "Gain [60] [Gold]", f"New [Gu Master] units start with [15] XP [in all cities] <for [{CONTEST_XP_TURNS}] turns>",
            w("+0"), w("+200", "<when number of [[Military] Units] is more than [8]>")]},
        {"text": "Another tribe takes the court, and the blizzard falls on our camps", "uniques": [
            "[-50]% growth [in all cities] <for [10] turns>", w("+0")]}]},
    # Regions: the Court hunts those who slipped their fate, for each one killed helps mend Fate Gu; immortal
    # zombies are its first quarry (R V4c131, V4c307)
    {"name": "Fate Hunt", "text": "Heavenly Court envoys hunt those who slipped their fate. Your immortal zombies are on "
     "their list.", "choices": [
        toll("Go to ground in the Yellow Springs Sea", ["[-25]% Strength <for [10] turns>"], "+0"),
        toll("Pay informants to lose the trail", ["Unavailable <when below [120] [Gold]>", "Gain [-120] [Gold]"], "+50")]},
    # Regions II: the Refinement Conference of the Central Continent draws hundreds of thousands of Gu Masters, from the
    # Eastern Sea and the Western Desert too; each refiner brings his own materials and the champion takes an
    # undefeated inheritance (R V4c179, V4c85). One every hundred years (GlobalUniques)
    {"name": "Refinement Conference", "text": "The Refinement Conference opens in the Central Continent. Refiners "
     "from all five regions come, each with his own materials; the champion takes an undefeated inheritance.",
     "choices": [
        {"text": "Send our best refiners to compete", "uniques": [
            "Unavailable <when below [150] [Gold]>", "Gain [-150] [Gold]", f"Instantly provides [20] [{MATERIALS}]",
            "[+33]% Production when constructing [Immortal Gu] wonders [in all cities] <for [20] turns>",
            w("+0"), w("+100", "<when above [400] [Gold]>")]},
        toll("Trade for materials at the fair", ["Unavailable <when below [60] [Gold]>", "Gain [-60] [Gold]",
                                                 f"Instantly provides [8] [{MATERIALS}]"], "+0"),
        toll("Stay home", [], "-50")]},
    # Regions II: the Wan clan calls the Western Desert's righteous families to punish the Fang clan, which swallowed
    # their resource points; the Court promises to stay out, and the siege fails (R V6c256, V6c279, V6c285)
    {"name": "Wan Coalition", "text": "The Wan clan calls the desert's righteous families to punish your clan for "
     "swallowing their oases. The Heavenly Court has promised to stay out of it.", "choices": [
        toll("Pay the families to go home", ["Unavailable <when below [200] [Gold]>", "Gain [-200] [Gold]"], "+50"),
        toll("Meet the coalition in the sand", ["[2] [Rank Five Gu Master]s rebel"], "+0")]},
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
    # Phase D: demonic Gu Masters raid a clan (the rebels belong to the barbarians and spawn near its capital)
    {"name": "Demonic Raid", "text": "Demonic Gu Masters raid your lands, hunting Gu, primeval stones and captives.", "choices": [
        toll("Meet them in battle", ["[2] [Demonic Gu Master]s rebel <before discovering [Purple Crystal Essence]>",
                                     "A [Demonic Elder] rebels <after discovering [Purple Crystal Essence]>",
                                     "[2] [Demonic Gu Master]s rebel <after discovering [Purple Crystal Essence]>"], "+100"),
        toll("Pay them off", ["Unavailable <when below [80] [Gold]>", "Gain [-80] [Gold]"], "-30")]},
    # a lone Gu Master (散修) asks to serve; robbing him makes an enemy
    {"name": "Wandering Gu Master", "text": "A lone Gu Master wanders into your village and offers his service for "
                                            "primeval stones.", "choices": [
        toll("Hire him", ["Unavailable <when below [60] [Gold]>", "Gain [-60] [Gold]", "Free [Rank Two Gu Master] appears"], "+50"),
        toll("Send him on his way", [], "+0"),
        toll("Rob him", ["Gain [40] [Gold]", "A [Lone Gu Master] rebels"], "-20")]},
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
        # audit P5: only a surplus is sold, the stock a rank-six immortal Gu needs stays
        toll("Sell immortal materials", [f"Unavailable <when below [{gen_paths.GC.WONDER_MATERIALS[6] + 20}] [{MATERIALS}]>",
                                         f"Instantly consumes [20] [{MATERIALS}]",
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
      "uniques": [f"Costs [{g['essence']}] [{IMMORTAL_GU_ESSENCE[g['rank']]}]",
                  f"Costs [{gen_paths.GC.WONDER_MATERIALS[int(g['rank'])]}] [{MATERIALS}]",
                  "Never destroyed when the city is captured", "Immortal Gu",
                  gen_paths.path_marker(g["path"]), "Triggers a [Immortal Gu Refinement] event"] + items(g["effects"])
      # autoplay (C3): without it the AI built only the two stat wonders, after turn 275
      + [w("+300")]}
     for g in IMMORTAL_GU
] + gen_paths.GC.wonders(IMMORTAL_GU_RECIPES, gen_paths.path_marker) + [b for i in INHERITANCES for b in (
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
# Regions (canon research 2026-11-08, docs/REGIONS.md): a region wall stops the strong, not the weak. A rank-4 Fang Yuan
# crossed and crowds of mortal Gu Masters cross to the Refinement Conference; for immortals it is hard at rank six, very
# dangerous at seven and all but impossible at eight (R V4c61, V5c535, V5c899). So every unit may enter (slow going),
# every unit that ends its turn inside is hurt, and an immortal is hurt more the higher its rank (WALL_STRAIN). The
# engine's AI never ends a turn on damaging terrain without need [src UnitAutomation], so the regions stay apart.
REGION_WALLS = {"Miasma Wall": ((90, 130, 70), 15), "Licorice Wall": ((200, 180, 120), 10),
                "Azure Water Wall": ((60, 120, 190), 10), "Raging Flame Wall": ((220, 90, 40), 15),
                "Sage Wall": ((235, 230, 210), 10)}
ter += [{"name": n, "type": "Land", "movementCost": 3, "defenceBonus": 0.5, "RGB": list(rgb),
         "uniques": [f"Units ending their turn on this terrain take [{dmg}] damage",
                     "Has an elevation of [3] for visibility calculations",
                     "Considered [Undesirable] when determining start locations"]}
        for n, (rgb, dmg) in REGION_WALLS.items()]
assert list(REGION_WALLS) == WALLS
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
    # Phase D: a demonic Gu Masters' den; new camps pick a Beast Lair or a Demonic Den at random [src createNewCamp]
    {"name": "Demonic Den", "terrainsCanBeBuiltOn": ["Land"],
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


SECTS = [  # (name, outer colour, inner colour, seat); three colour pairs are the official validator's suggestions
    ("Heavenly Lotus Sect", [198, 121, 147], [255, 250, 208], "Heavenly Lotus Blessed Land"),
    ("Spirit Butterfly Valley", [36, 138, 121], [255, 225, 140], "Spirit Butterfly Valley"),
    ("Ancient Soul Sect", [70, 50, 100], [210, 200, 160], "Earth Abyss"),
    ("Heaven's Envy Tower", [40, 120, 80], [250, 225, 150], "Heaven's Envy Tower"),
    ("Wind Cloud Manor", [109, 145, 190], [255, 255, 250], "Wind Cloud Manor"),
    ("Black Heaven Temple", [20, 20, 24], [235, 235, 225], "Black Heaven Temple"),
    ("Myriad Dragon Dock", [90, 20, 120], [250, 200, 60], "Dragon Lake Isle"),
]
EAST_SEA_RAIDS = per_speed(  # Phase D: the Eastern Sea has the most and strongest lone and demonic cultivators (R ch1650)
    lambda m: f"A [Demonic Gu Master] rebels <upon turn start> <after turn number [{turn_gate(40, m)}]> "
              f"<every [{max(1, round(m))}] turns> <with [4]% chance>")
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
           [RIGHTEOUS_START, f"[+15]% Strength <vs [{ZOMBIE}] units>", "Start bias [Hill]",
            # Phase D: the Demon Extermination List (诛魔榜, R ch700, ch710)
            "[+25]% Strength <vs [Barbarian] units>",
            # Regions: the strongest region, with the richest qi and the most immortals, its order three million years
            # old (R V2c135, V4c55, V5c519, V5c704). Its many immortals sleep in the Immortal Tomb and wake only when
            # the Court is truly threatened (R V5c49, V5c560): when a clan declares war on it, two rank-seven immortals
            # take the field. They have no blessed land, so no calamities (R V5c55), and they burn their last life
            # (Lifespan Gu) as the canon's sleepers do.
            *head_start(6, 2, "Rank Three Gu Master"), "[+15]% [Science] [in all cities]", "[+15]% [Production] [in all cities]",
            "[+50]% Strength for cities",
            "[2] free [Rank Seven Gu Immortal] units appear <upon being declared war on by [All] Civilizations> "
            "<when number of [[Rank Seven Gu Immortal] Units] is less than [3]>"]),
    nation(HJ, "Huang Jin Patriarch", "Huang Jin Temperament", [200, 160, 40], [90, 40, 20],
           ["Imperial Court", "Golden Tent", "Northern Plains Camp"],
           [RIGHTEOUS_START, "[+15]% Strength <when defending>", "Start bias [Grassland]",
            # Regions: the second fighting power after the Central Continent and the poorest land; the most Gu
            # Masters and the best fighters, tribes always at war (R V3c153, V3c20, V4c170). The engine's AI declares
            # war only while content (E14): the war economy of captives and loot keeps the tribes so
            *head_start(3, 3, "Rank Two Gu Master"), "[-15]% [Gold] [in all cities]",
            "[+25]% Production when constructing [Military] units [in all cities]", f"[+{HJ_HAPPINESS} Happiness]"]
           # the golden tribes' contest for the Imperial Court, every ten years, before the killing blizzard (R V3c117)
           + per_speed(lambda m: f"Triggers a [Imperial Court Contest] event <upon turn start> <every [{turns(13, m)}] turns>")),
    nation(ZA, "Zombie Alliance Elder", "Zombie Alliance Temperament", [60, 80, 70], [180, 220, 190],
           ["Eastern Sea Hall", "Bone Isle", "Still Tide Harbour"],
           [RIGHTEOUS_START, "Start bias [Coast]",
            f"Free [{ZOMBIE}] appears <upon losing a [{{post-[Rank Five era]}} {{non-[Advancing]}} {{non-[{ZOMBIE}]}}] unit>",
            # Regions: the richest region (R V4c243, V5c669)
            *head_start(3), "[+25]% [Gold] [in all cities]"]
           # fate escapees: killing them helps mend Fate Gu, and immortal zombies are the Court's first quarry (R V4c131)
           + per_speed(lambda m: f"Triggers a [Fate Hunt] event <upon turn start> <when number of [[{ZOMBIE}] Units] is more "
                                 f"than [0]> <if [Fate Gu] is constructed by anybody> <with [{chance(3, m)}]% chance>")
           + per_speed(lambda m: f"Instantly provides [1] [{LIFESPAN}] <upon turn start> <every [{turns(10, m)}] turns> "
                                 f"<for every [1] [[post-[Rank Five era]] Units]>")
           + EAST_SEA_RAIDS),
    nation(FANG, "Fang Clan Head", "Fang Temperament", [150, 110, 60], [240, 230, 200],
           ["Fang Fortress", "Sand Gate", "Dune Workshop"],
           [RIGHTEOUS_START, "[+50]% Production when constructing [Gu House] units [in all cities]",
            "[+10]% [Science] [in all cities]", "Start bias [Desert]",
            # Regions: the most trade-minded region, poorer than the sea and richer than the plains (R V3c20, V5c475)
            *head_start(2), "[+20]% [Gold] [in all cities]"]
           # Regions II: a Fang clan that swallows more oases than its own three draws the Wan coalition (R V6c256)
           + per_speed(lambda m: f"Triggers a [Wan Coalition] event <upon turn start> <when number of [Cities] is more "
                                 f"than [3]> <with [{chance(2, m)}]% chance>")),
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
    # Regions: the ten great sects, the Court's lower sects, hold 80% of the Central Continent's resources from seats a
    # hundred thousand years old (R V4c55, V4c9): their cities are the hardest to take
    {"name": "Spirit Affinity House", "cityStateType": "Immortal Sect", "outerColor": [150, 90, 130],
     "innerColor": [250, 240, 245], "cities": ["Spirit Affinity House"], "uniques": ["[+50]% Strength for cities"]},
    {"name": "Combat Immortal Sect", "cityStateType": "Immortal Sect", "outerColor": [140, 30, 30],
     "innerColor": [240, 220, 200], "cities": ["Combat Immortal Peak"], "uniques": ["[+50]% Strength for cities"]},
    {"name": "Merman Imperial Court", "cityStateType": "Merchant Clan", "outerColor": [30, 90, 130],
     "innerColor": [200, 240, 250], "cities": ["Merman Court"], "uniques": ["Start bias [Coast]"] + EAST_SEA_RAIDS},
    # Phase D (the user: conflict in every region; faction research R, see LORE_MAPPING "Phase D: regional conflict")
    {"name": "Man Tribe", "cityStateType": "Battle Tribe", "personality": "Hostile", "outerColor": [150, 40, 20],
     "innerColor": [255, 200, 120], "cities": ["Red Flame Valley"]},
    {"name": "Ge Tribe", "cityStateType": "Mortal Villages", "personality": "Friendly", "outerColor": [90, 110, 60],
     "innerColor": [235, 240, 200], "cities": ["Ge Tribe Camp"]},
    {"name": "Lan Clan", "cityStateType": "Refiner Tribe", "outerColor": [70, 120, 150], "innerColor": [230, 245, 250],
     "cities": ["Zhou Xi Oasis"]},
    {"name": "Mo Clan", "cityStateType": "Battle Tribe", "outerColor": [110, 80, 50], "innerColor": [240, 220, 170],
     "cities": ["Sand Wolf City"]},
    {"name": "Xiao Clan", "cityStateType": "Merchant Clan", "outerColor": [170, 120, 30], "innerColor": [255, 245, 210],
     "cities": ["Silk Corridor"]},
    {"name": "Song Clan", "cityStateType": "Immortal Sect", "outerColor": [20, 60, 120], "innerColor": [210, 230, 255],
     "cities": ["Heavy Water Blessed Land"], "uniques": ["Start bias [Coast]"] + EAST_SEA_RAIDS},
    {"name": "Xia Clan", "cityStateType": "Battle Tribe", "outerColor": [40, 110, 110], "innerColor": [220, 250, 240],
     "cities": ["Xia Harbour"], "uniques": ["Start bias [Coast]"] + EAST_SEA_RAIDS},
    {"name": "Immortal Crane Sect", "cityStateType": "Immortal Sect", "outerColor": [230, 230, 235],
     "innerColor": [170, 30, 40], "cities": ["Fei He Mountain"], "uniques": ["[+50]% Strength for cities"]},
    # Regions II: the other seven of the ten great ancient sects (R V6c358), on their canon seats where the text names
    # one: Heavenly Lotus's blessed land on a mountain rich in natural dao marks (V4c351, V6c322), Ancient Soul above the
    # Earth Abyss in the far west of the continent (V4c79, V6c80), Myriad Dragon Dock's island in Dragon Lake (V6c358)
    *[{"name": n, "cityStateType": "Immortal Sect", "outerColor": o, "innerColor": i, "cities": [c],
       "uniques": ["[+50]% Strength for cities"]} for n, o, i, c in SECTS],
    # Regions II: the Wan clan of Gao Song Oasis, the desert's second resource point, leads the coalition against the
    # Fang clan (R V6c281, V6c256)
    {"name": "Wan Clan", "cityStateType": "Battle Tribe", "outerColor": [230, 200, 140], "innerColor": [120, 60, 20],
     "cities": ["Gao Song Oasis"]},
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
    # Phase D: warlike tribes and clans send Gu Masters to their friends (Vanilla's Militaristic numbers)
    {"name": "Battle Tribe", "color": [200, 60, 40], "friendBonusUniques": ["Provides military units every ≈[20] turns"],
     "allyBonusUniques": ["Provides military units every ≈[17] turns"]},
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
    # Phase D (the user: no conflict outside the south; autoplay 4 x 200: the four arc majors never went to war):
    # the Northern Plains tribes swallow small tribes (R ch443), the desert's clans gang up on rivals (R ch1775),
    # the Eastern Sea's lone and demonic immortals are the strongest (R ch1650); the Court hunts demons
    # Regions (canon research 2026-11-08): the Court wages no ordinary war, it guards fate and strikes only at
    # threats (R V5c49, V4c131, V4c314); declareWar 0 means it never declares one [docs Personalities], but it fights
    # back. The plains are the most warlike (R V4c170); the sea's houses are many, opportunistic and none a hegemon
    # (R V4c336, V5c864); the desert's clans trade and cooperate, since no one marches across the sand for another
    # oasis (R V3c20, V5c596)
    {"name": "Heavenly Court Temperament", "science": 9, "military": 8, "aggressive": 2, "declareWar": 0, "diplomacy": 8,
     "loyal": 9, "commerce": 6, "uniques": ["[+500]% weight to [Fate Gu] for AI decisions"]},
    {"name": "Huang Jin Temperament", "military": 10, "aggressive": 10, "declareWar": 10, "expansion": 8, "loyal": 5,
     "diplomacy": 3},
    {"name": "Zombie Alliance Temperament", "gold": 8, "military": 7, "aggressive": 7, "declareWar": 6, "commerce": 8,
     "loyal": 2},
    {"name": "Fang Temperament", "production": 8, "science": 6, "military": 6, "aggressive": 3, "declareWar": 2,
     "diplomacy": 9, "commerce": 9,
     "uniques": ["[+200]% weight to [Gu House Formation] for AI decisions"]},
    {"name": "Wu Temperament", "military": 7, "aggressive": 4, "production": 6, "loyal": 7, "expansion": 5,
     "declareWar": 6, "diplomacy": 7,
     "preferredVictoryType": "Southern Border Supremacy",
     "priorities": {"Righteous Path": 10, "Strength Path": 4},  # D3: the clan walks wind; Wu Ji alone walks strength
     "uniques": ["[+50]% weight to [Martial Arena] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
])
for _k in (("UnitPromotions.json", "Seek Eternal Life"), ("Buildings.json", "Eternal Life"), ("TileResources.json", APRICOT)):
    assert f"{ETERNAL_COST} " in PEDIA[_k], f"civilopedia {_k[1]}: Eternal Life costs {ETERNAL_COST}"
# the lifespan texts quote tools/lifespan.py: stop the build when they drift apart
_lg = PEDIA[("TileResources.json", LS.LIFESPAN)]
assert (f"{LS.GRANT[6]}, {LS.GRANT[7]}, {LS.GRANT[8]} and {LS.GRANT[9]}" in _lg
        and f"{LS.BURN[6]}, {LS.BURN[7]}, {LS.BURN[8]} or {LS.BURN[9]} turns" in _lg
        and f"{LS.STARVE_DAMAGE} HP a turn" in _lg), "data/civilopedia.csv Lifespan Gu: update its numbers (tools/lifespan.py)"
for _n, _g in (("Ascension", 6), ("Advance to Rank Seven", 7), ("Advance to Rank Eight", 8), ("Ascend to Venerable", 9)):
    assert f"brings {LS.GRANT[_g]} Lifespan Gu" in PEDIA[("UnitPromotions.json", _n)], f"civilopedia {_n}: lifespan grant"
assert f"brings {LS.GRANT[9]} Lifespan Gu" in PEDIA[("Units.json", VENERABLE)], "civilopedia Venerable: lifespan grant"
# Phase D: the power-scaling pages in Civilopedia > Tutorials (tools/gen_paths.py, tools/path_powers.py)
assert [x[0] for x in DAO_EFFECTS] == [f"[{v[:-1]}]% Strength" for v in (d.split()[0] for d in gen_paths.PP.DAO_STRENGTH[0])] \
    and DAO == gen_paths.PP.DAO_TIERS, "update tools/path_powers.py"
dump("Tutorials.json", gen_paths.tutorials())
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
