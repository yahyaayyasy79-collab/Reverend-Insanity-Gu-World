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
        return list(csv.DictReader(f))


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


# ---------------- ModOptions / Globals ----------------
dump("ModOptions.json", {"isBaseRuleset": True,
                         "uniques": ["Disable religion", "Can only start games from the starting era"],
                         # R5: the engine adds (share of techs known x 5.5)^2.8 x this to every city's strength [src
                         # CityCombatant.getCityStrength]; with a 15-tech tree the default 1.0 gave +118 by turn ~120 and
                         # no city was ever taken. 0.1 caps it at +12 (autoplay, docs/AUTOPLAY.md round 5).
                         "constants": {"maxXPfromBarbarians": 90, "cityStrengthFromTechsFullMultiplier": 0.1}})
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
] + per_speed(lambda m: f"Triggers a [{TIDE}] event <upon turn start> <after turn number [{turn_gate(30, m)}]> "
                       f"<with [{chance(3, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [{TIDE}] event <upon turn start> <after turn number [{turn_gate(90, m)}]> "
              f"<with [{chance(2, m)}]% chance> <for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [{chance(8, m)}]% chance> "
              "<for [Major] Civilizations>") + per_speed(
    lambda m: f"Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [{chance(3, m)}]% chance> "
              "<for [Major] Civilizations>") + per_speed(
    lambda m: "Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] "
              f"is less than [0]> <with [{chance(25, m)}]% chance> <for [Major] Civilizations>") + [
    # R6: a held (excavated) inheritance teaches the clan's Gu Masters
    "[+20]% XP gained from combat <with [Gu Inheritance]>",
]})

# ---------------- Eras (iconRGB = essence colours: green copper / white silver / yellow gold, verified) ----------------
dump("Eras.json", [
    {"name": E12, "researchAgreementCost": 150, "iconRGB": [72, 140, 100], "startingSettlerUnit": "Clan Settler",
     "startingWorkerCount": 1, "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master",
     "startingGold": 50, "baseUnitBuyCost": 200},
    {"name": E3, "researchAgreementCost": 250, "iconRGB": [205, 205, 215], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 300},
    {"name": E4, "researchAgreementCost": 350, "iconRGB": [230, 190, 60], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 400},
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
                        ["Civilian", "Gu Master", "Moon Gu Master", "Strength Gu Master", "Beast"]])


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
    u["uniques"] += [WILD_GU_TRIGGER, INHERITANCE_TRIGGER]
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


# R3 hunger meter (the user's design). A Gu whose food is in deficit is first WEAKENED: its effects carry
# <when above [-1] [food]> and switch off (the engine adds its own -25% missing-resource malus [src BattleDamage]).
# At the first turn start in deficit the unit gets a timed hunger status (one per food); if the food is still short when
# the status runs out, the Gu dies with the death chance of data/hunger.csv (R4, the user's option B: no mass death, because the
# civ's resource count is not refreshed between units [src]); a survivor gets the status again at the next turn start.
# The status is removed early, harmlessly, once the food is back. Statuses tick down at the end of startTurn, after the
# triggers [src UnitTurnManager.startTurn], so a status of N turns runs out at the (N-1)th turn start after the first:
# rank-1 Gu (eat often in canon) roll after 2 turns and then every 3, rank-2 Gu after 4 and then every 5. The roll is
# seeded per unit (name, tile, movement) and turn [src Conditionals.getStateBasedRandom, GameContext.hashCode].
HUNGER = {r["food"]: r["hunger_status"] for r in table("gu_foods.csv")}
HUNGER_RANKS = {int(r["rank"]): (int(r["status_turns"]), int(r["death_chance"])) for r in table("hunger.csv")}


def fed(unique, food):
    """The Gu's effect works only while its food is not in deficit (WEAKENED otherwise)."""
    return f"{unique} <when above [-1] [{food}]>"


def hunger(gu, food, rank):
    status = HUNGER[food]
    turns, chance = HUNGER_RANKS[rank]
    return [f"[This Unit] gains the [{status}] status for [{turns}] turn(s) <upon turn start> <when below [0] [{food}]> <for units without [{status}]>",
            f"[This Unit] loses the [{gu}] promotion <upon losing the [{status}] status> <when below [0] [{food}]> "
            f"<with [{chance}]% chance>"]


def gu_promotion(r):
    """data/gu.csv: effects work only while fed (fed()), then the food, the hunger meter, the extra uniques."""
    return {"name": r["name"], "uniques": [fed(e, r["food"]) for e in items(r["effects"])]
            + [f"Consumes [{r['eats']}] [{r['food']}]"] + hunger(r["name"], r["food"], int(r["rank"]))
            + items(r["extra_uniques"])}


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
    # R3 hunger statuses (timers; see hunger()); each removes itself once its food is back
] + [{"name": status, "uniques": [f"[This Unit] loses the [{status}] status <upon turn start> <when above [-1] [{food}]>"]}
     for food, status in HUNGER.items()]
    # C3 (MOD_SPEC_3): every canonical path's attainment tiers, killer moves and signature statuses (docs/PATHS.md)
    + gen_paths.promotions(GM_TYPES))

# ---------------- Events (9: the spec's 5 + wild Gu and inheritances, R6) ----------------
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
             f"Unavailable <when below [200] [Gold]> <during the [{E4}]>",
             f"Gain [-40] [Gold] <during the [{E12}]>", f"Gain [-70] [Gold] <during the [{E3}]>",
             f"Gain [-100] [Gold] <during the [{E4}]>"]
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
            f"A [Thunder Crown Wolf] rebels <during the [{E4}]>",
            w("+0")]},
        {"text": "Hire demonic Gu Masters to thin the pack", "uniques": [
            "Only available <when above [60] [Gold]>",
            f"Unavailable <when below [100] [Gold]> <during the [{E3}]>",
            f"Unavailable <when below [150] [Gold]> <during the [{E4}]>",
            f"Gain [-60] [Gold] <during the [{E12}]>", f"Gain [-100] [Gold] <during the [{E3}]>",
            f"Gain [-150] [Gold] <during the [{E4}]>",
            w("+0")]},
        # R7: was "[-1] population [in all cities]": free in cities at population 1 (losses stop at 1 [src]) and the
        # largest drain on every clan (autoplay: capitals at 1.8-4 by turn 320, 8.4 without population choices).
        # The fields lie fallow for a while instead.
        {"text": "Abandon the outer fields", "uniques": ["[-50]% growth [in all cities] <for [10] turns>", w("-30")]},
        {"text": "Man the stockade walls", "uniques": [
            "Only available <if [Stockade Wall] is constructed> <when above [70] [Gold]>",
            f"Gain [-40] [Gold] <during the [{E3}]>", f"Gain [-70] [Gold] <during the [{E4}]>",
            "[-20]% [Production] <for [5] turns>", w("+50")]},
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
        {"text": "Rob a passing caravan", "uniques": [
            "Only available <after adopting [Demonic Path]>", "Gain [70] [Gold]",
            "Triggers a [Betrayal] event <with [25]% chance>", w("+50")]},
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
    {"name": "Tavern", "requiredTech": "Wine Brewing", "cost": 60, "maintenance": 1, "happiness": 1,
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
])

# ---------------- Policies (4 branches) ----------------
dump("Policies.json", [
    {"name": "Righteous Path", "era": E12, "priorities": {"Southern Border Supremacy": 2, "Endurance": 6}, "uniques": [
        "Only available <before adopting [Demonic Path]>",
        "Resting point for Influence with City-States is increased by [15]",
        "[-25]% maintenance costs <in [Friendly Land] tiles>"], "policies": [
        {"name": "Clan Rules", "row": 1, "column": 1, "uniques": ["[-15]% Unhappiness from [Population] [in all cities]"]},
        {"name": "Righteous Alliance", "row": 1, "column": 3, "uniques": [
            "City-State Influence recovers at twice the normal rate",
            "Gifts of Gold to City-States generate [+25]% more Influence"]},
        {"name": "Guardian Formations", "row": 2, "column": 2, "requires": ["Clan Rules"],
         "uniques": ["[+25]% Strength for cities", "[+10]% Strength <when defending>"]},
        {"name": "Righteous Path Complete", "uniques": ["[-10]% maintenance costs"]}]},
    {"name": "Demonic Path", "era": E12, "priorities": {"Southern Border Supremacy": 6, "Endurance": 2}, "uniques": [
        "Only available <before adopting [Righteous Path]>",
        "Earn [50]% of killed [Military] unit's [Cost] as [Gold]",
        "[+50]% City-State Influence degradation",
        "Triggers a [Betrayal] event <upon turn start> <with [3]% chance>"], "policies": [
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
        "Provides [2] [Wild Boar]",
        "[+5]% Strength <for [Strength Master] units> <for every [Adopted [[Strength Path] branch] Policies]>"], "policies": [
        {"name": "Boar Strength", "row": 1, "column": 1, "uniques": ["[+15]% Strength <for units with [White Boar Gu]>",
                                                                   "[+15]% Strength <for units with [White Jade Gu]>"]},
        {"name": "Beast Hunters", "row": 1, "column": 3, "uniques": ["Provides [2] [Wild Boar]",
                                                                   "[+25]% Strength <vs [Barbarians] units>"]},
        {"name": "Unyielding Body", "row": 2, "column": 2, "requires": ["Boar Strength"],
         "uniques": ["Heals [10] damage if it kills a unit"]},
        {"name": "Strength Path Complete", "uniques": ["[1] Movement <for [Strength Master] units>"]}]},
])

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
])

# ---------------- Terrains (Vanilla minus natural wonders and Fallout) ----------------
ter = [t for t in json5.load(open(os.path.join(VAN, "Terrains.json")))
       if t.get("type") != "NaturalWonder" and t["name"] != "Fallout"]
for t in ter:
    t["uniques"] = [u for u in t.get("uniques", []) if "receive an extra [Sheep]" not in u]  # R3: no extra springs
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
def nation(name, leader, pers, outer, inner, cities, uniques):
    return {"name": name, "leaderName": leader, "adjective": [name], "personality": pers, "outerColor": outer,
            "innerColor": inner, "cities": cities, "uniques": uniques}


def emblem(gu, extra=""):
    # R2 T3: canon - new students pick their first Gu free from the academy Gu room; most take the clan emblem Gu
    return (f"All newly-trained [Rank One Gu Master] units [in all cities] receive the [{gu}] promotion "
            f"<in cities with a [Gu Academy]>" + (f" {extra}" if extra else ""))


dump("Nations.json", [
    nation("Gu Yue Clan", "Gu Yue Bo", "Gu Yue Temperament", [30, 40, 90], [220, 220, 240],
           ["Gu Yue Village", "Alliance Slope", "Spear Bamboo Grove", "Stone Forest"],
           [emblem("Moonlight Gu", "<when above [0] [Moon Orchid]>"), "Start bias [Spirit Spring]", "Start bias [Hill]"]),
    # R2 T2: the Bai and Xiong leaders are never named in canon (bai jia zu zhang / xiong jia zu zhang)
    nation("Bai Clan", "Bai Clan Leader", "Bai Temperament", [230, 230, 230], [40, 70, 120],
           ["Bai Village", "Back-Slope Waterfall", "Deep Pool", "Bitter Shell Pool"],
           [emblem("Stream Gu"), "[+15]% Strength <vs [Barbarians] units>", "Start bias [Spirit Spring]", "Start bias [Fresh Water]"]),
    nation("Xiong Clan", "Xiong Clan Leader", "Xiong Temperament", [90, 50, 20], [240, 200, 140],
           ["Xiong Village", "Front Slope", "Honey Hollow"],
           [emblem("Bear Strength Gu"), "Starts with [Strength Path] adopted", "Start bias [Spirit Spring]", "Start bias [Hill]"]),
    # canon start biases (geography research): Xiong on the front slope (R V1c65), Wu by the rivers (R V2c1)
    # R3: the fourth major is the Wu clan, the Southern Border's first clan (user's choice); leader Wu Ji (vol2 ch84)
    nation("Wu Clan", "Wu Ji", "Wu Temperament", [120, 20, 20], [250, 210, 120],
           ["Wu Yi Mountain", "Moon Bowl", "Golden Cloud Canyon", "Xuan Ming Mountain"],
           ["Starts with [Righteous Path] adopted", "Start bias [Spirit Spring]", "Start bias [River]"]),
    # R2 T7
    {"name": "Hairy Man Tribe", "cityStateType": "Refiner Tribe", "outerColor": [60, 30, 10], "innerColor": [255, 230, 180],
     "cities": ["Bronze Hall"]},
    {"name": "Foothill Villages", "cityStateType": "Mortal Villages", "outerColor": [110, 90, 50],
     "innerColor": [240, 240, 210], "cities": ["Qing Mao Foothills"]},
    {"name": "Jia Clan", "cityStateType": "Merchant Clan", "outerColor": [120, 90, 0], "innerColor": [255, 230, 120],
     "cities": ["Jia Village"]},
    {"name": "Barbarians", "outerColor": [0, 0, 0], "innerColor": [185, 12, 12],
     "uniques": ["Can only heal by pillaging", "Excluded from map editor"]},
    {"name": "Spectator", "outerColor": [255, 255, 255]},
])
dump("CityStateTypes.json", [
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
    {"name": "Gu Yue Temperament", "science": 7, "culture": 6, "gold": 5, "military": 4, "aggressive": 3,
     "priorities": {"Moon Path": 10, "Righteous Path": 6},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions",
                 "Will not build [Flower Wine Monk Inheritance]"]},
    {"name": "Bai Temperament", "gold": 7, "production": 6, "science": 6, "military": 4, "aggressive": 3,
     "priorities": {"Righteous Path": 8},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
    {"name": "Xiong Temperament", "military": 7, "aggressive": 6, "production": 6,
     "preferredVictoryType": "Southern Border Supremacy",
     "priorities": {"Strength Path": 10, "Demonic Path": 6, "Righteous Path": 3},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
    {"name": "Wu Temperament", "military": 7, "aggressive": 4, "production": 6, "loyal": 7, "expansion": 5,
     "preferredVictoryType": "Southern Border Supremacy",
     "priorities": {"Righteous Path": 10, "Strength Path": 10},
     "uniques": ["[+50]% weight to [Martial Arena] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
])
dump("VictoryTypes.json", [
    {"name": "Southern Border Supremacy", "milestones": ["Capture all capitals"]},
    {"name": "Endurance", "milestones": ["Have highest score after max turns"]},
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
