#!/usr/bin/env python3
"""Validation prototype of the Slice 1 plan in docs/LORE_MAPPING.md. NOT the mod.

Writes OUT_DIR/jsons/*.json: a throwaway ruleset holding every object, field and unique the plan names, so the
plan can be checked in context by the repo's checkers and by Unciv's own validator before any real JSON exists:

  tools/slice1_prototype.py /tmp/slice1 && tools/check_all --mod /tmp/slice1 --no-self-test

Phase 2 replaces it with data/*.csv + tools/gen_*.py (MOD_SPEC section 9). Until then, change the plan here and in
docs/LORE_MAPPING.md together; tools/tests checks that every unique the document quotes is generated here.
Comments marked "R2" are round-2 changes (the user's lore answers plus the verified research, 2026-10-13).
"""
import json
import os
import sys

import json5

from common import VANILLA_JSONS

if len(sys.argv) != 2:
    sys.exit("usage: slice1_prototype.py OUT_DIR")
OUT = os.path.join(sys.argv[1], "jsons")
VAN = str(VANILLA_JSONS)
os.makedirs(OUT, exist_ok=True)
ALL_UNIQUES = []


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


def dump(name, obj):
    collect(obj)
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


E12, E3, E4 = "Rank One-Two era", "Rank Three era", "Rank Four era"
GM_TYPES = ["Gu Master", "Moon Gu Master", "Strength Gu Master"]
APT = ("Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> "
       "<for units without [Aptitude C]> <for units without [Aptitude D]>")
NB = "Never appears as a Barbarian unit"
TIDE = "Beast Tide"           # the spec's generic name; in Slice 1 the beasts are the canon wolf tide (lang chao)
SPRING = "Awakening Grounds"  # R2 T6: the cave behind the clan-head pavilion: the clan's primeval spring and flower sea
PAVILION = "Clan Head Pavilion"  # R2 T6: was "Clan Hall"; the ancestral hall (ci tang) is inside it


def w(x, cond=""):
    return f"[{x}]% weight to this choice for AI decisions" + (f" {cond}" if cond else "")


# ---------------- ModOptions / Globals ----------------
dump("ModOptions.json", {"isBaseRuleset": True,
                         "uniques": ["Disable religion", "Can only start games from the starting era"],
                         "constants": {"maxXPfromBarbarians": 90}})
dump("Beliefs.json", [])
dump("Religions.json", [])
dump("GlobalUniques.json", {"name": "GlobalUniques", "uniques": [
    "[-75]% growth [in all cities] <when between [-10] and [-1] [Happiness]>",
    "Nullifies Growth [in all cities] <when below [-10] [Happiness]>",
    "[-50]% [Production] [in all cities] <when below [-10] [Happiness]>",
    "[-33]% Strength <for [All] units> <when below [-10] [Happiness]>",
    "Cannot build [Clan Settler] units <when below [-10] [Happiness]>",
    "Rebel units may spawn <when below [-20] [Happiness]>",
    "[-3] units cost no maintenance <for [Major] Civilizations>",
    "[-20]% Strength <when below [0] [Gold]>",
    f"Triggers a [{TIDE}] event <upon turn start> <after turn number [30]> <with [3]% chance> <for [Major] Civilizations>",
    f"Triggers a [{TIDE}] event <upon turn start> <after turn number [90]> <with [2]% chance> <for [Major] Civilizations>",
    "Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [8]% chance> <for [Major] Civilizations>",
    "Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [3]% chance> <for [Major] Civilizations>",
    "Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [25]% chance> <for [Major] Civilizations>",
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


# ---------------- Techs (15, names unchanged) ----------------
def col(n, era, cost, bcost, wcost, techs):
    return {"columnNumber": n, "era": era, "techCost": cost, "buildingCost": bcost, "wonderCost": wcost, "techs": techs}


dump("Techs.json", [
    col(1, E12, 20, 45, 75, [{"name": "Aperture Awakening", "row": 2, "uniques": ["Starting tech"]}]),
    col(2, E12, 40, 60, 140, [
        {"name": "Primeval Stone Mining", "row": 1, "prerequisites": ["Aperture Awakening"]},
        {"name": "Gu Feeding", "row": 3, "prerequisites": ["Aperture Awakening"]}]),
    col(3, E12, 65, 75, 170, [
        {"name": "Wine Brewing", "row": 1, "prerequisites": ["Gu Feeding"]},
        {"name": "Gu Refinement", "row": 2, "prerequisites": ["Primeval Stone Mining", "Gu Feeding"]},
        {"name": "Rank Two Cultivation", "row": 3, "prerequisites": ["Gu Feeding"]}]),
    col(4, E3, 120, 100, 220, [
        {"name": "Gu Formations", "row": 1, "prerequisites": ["Gu Refinement"]},
        {"name": "Rank Three Cultivation", "row": 3, "prerequisites": ["Rank Two Cultivation", "Gu Refinement"]}]),
    col(5, E3, 170, 130, 240, [
        {"name": "Merchant Caravans", "row": 1, "prerequisites": ["Gu Formations", "Wine Brewing"],
         "uniques": ["Enables Open Borders agreements"]},
        {"name": "Inheritance Lore", "row": 2, "prerequisites": ["Gu Formations", "Rank Three Cultivation"]},
        {"name": "Killer Moves", "row": 3, "prerequisites": ["Rank Three Cultivation"]}]),
    col(6, E4, 250, 160, 300, [
        {"name": "Super Clan Commerce", "row": 1, "prerequisites": ["Merchant Caravans"]},
        {"name": "Beast Enslavement", "row": 2, "prerequisites": ["Inheritance Lore", "Killer Moves"],
         "uniques": ["When defeating a [Beast] unit, earn [10] Gold and recruit it <when number of [[Gold] Per Turn] is more than [4]>"]},
        {"name": "Rank Four Cultivation", "row": 3, "prerequisites": ["Killer Moves"]}]),
    col(7, E4, 350, 200, 350, [
        {"name": "Dao Comprehension", "row": 2,
         "prerequisites": ["Super Clan Commerce", "Beast Enslavement", "Rank Four Cultivation"],
         "uniques": ["Can be continually researched"]}]),
])

# ---------------- Unit types ----------------
dump("UnitTypes.json", [{"name": n, "movementType": "Land"} for n in
                        ["Civilian", "Gu Master", "Moon Gu Master", "Strength Gu Master", "Beast"]])


# ---------------- Units (12) ----------------
def gm(name, utype, tech, cost, strength, maint, extra, ranged=None, upgrades=None):
    u = {"name": name, "unitType": utype, "movement": 2, "strength": strength, "cost": cost, "requiredTech": tech,
         "uniques": [f"[{maint}]% maintenance costs", NB, APT] + extra}
    if ranged:
        u["rangedStrength"] = ranged
        u["range"] = 2
    if upgrades:
        u["upgradesTo"] = upgrades
    return u


MOON = ["Only available <after adopting [Moon Path]>"]
STR = ["Only available <after adopting [Strength Path]>"]
dump("Units.json", [
    {"name": "Clan Settler", "unitType": "Civilian", "movement": 2, "cost": 80, "requiredTech": "Aperture Awakening",
     "uniques": ["Founds a new city <by consuming this unit>", "Excess Food converted to Production when under construction",
                 "Requires at least [2] population", NB]},
    {"name": "Mortal Laborer", "unitType": "Civilian", "movement": 2, "cost": 45, "requiredTech": "Aperture Awakening",
     "uniques": ["Can build [Land] improvements on tiles", "Automation is a primary action", NB]},
    gm("Rank One Gu Master", "Gu Master", "Aperture Awakening", 35, 8, "+25",
       ["Can upgrade to [Rank Two Moon Gu Master]", "Can upgrade to [Rank Two Strength Gu Master]"]),
    gm("Rank Two Strength Gu Master", "Strength Gu Master", "Rank Two Cultivation", 60, 14, "+100", STR,
       upgrades="Rank Three Strength Gu Master"),
    gm("Rank Three Strength Gu Master", "Strength Gu Master", "Rank Three Cultivation", 95, 22, "+175", STR,
       upgrades="Rank Four Strength Gu Master"),
    gm("Rank Four Strength Gu Master", "Strength Gu Master", "Rank Four Cultivation", 140, 32, "+275", STR),
    gm("Rank Two Moon Gu Master", "Moon Gu Master", "Rank Two Cultivation", 60, 8, "+75", MOON, ranged=13,
       upgrades="Rank Three Moon Gu Master"),
    gm("Rank Three Moon Gu Master", "Moon Gu Master", "Rank Three Cultivation", 95, 12, "+150", MOON, ranged=20,
       upgrades="Rank Four Moon Gu Master"),
    gm("Rank Four Moon Gu Master", "Moon Gu Master", "Rank Four Cultivation", 140, 18, "+225", MOON, ranged=29),
    # R2 T5: the canon wolf-tide tiers (plain / hundred-beast tier / ten-thousand-beast king)
    {"name": "Lightning Wolf", "unitType": "Beast", "movement": 3, "strength": 9, "cost": 30, "uniqueTo": "Barbarians",
     "uniques": ["[+50]% maintenance costs"]},
    {"name": "Bold Lightning Wolf", "unitType": "Beast", "movement": 3, "strength": 16, "cost": 60,
     "requiredTech": "Rank Three Cultivation", "uniqueTo": "Barbarians",
     "uniques": ["[+15]% Strength bonus for [Lightning Wolf] units within [2] tiles", "[+100]% maintenance costs"]},
    {"name": "Thunder Crown Wolf", "unitType": "Beast", "movement": 3, "strength": 28, "cost": 120,
     "uniqueTo": "Barbarians",
     "uniques": ["Unbuildable", "[+20]% Strength bonus for [Beast] units within [2] tiles", "[+200]% maintenance costs"]},
])

# ---------------- R2 T4: refinement ladder with the canon recipes ----------------
# Moon (Fang Zheng's line):      Moonlight Gu -> Moon Raiment (Moonlight + Jade Skin, fused) -> Killer Move
# Strength (Fang Yuan's line):   White Boar Gu -> White Jade Gu (White Boar + Jade Skin, fused; boar strength kept;
#                                a spare wild boar = the tusk catalyst, +20 points) -> Killer Move
# Rank One (unpathed, any clan): Jade Skin Gu (the cap); it is carried into a path and saves the fusion's jade.
# Black Boar Gu is OFF the ladder: bought from the Jia caravan (Jia ally bonus), stacks as a second boar.
# Dead states: no ladder line can fire -> the careful and reckless choices close.
LADDER_DEAD = [
    "Unavailable <for units with [Killer Move]>",
    "Unavailable <for units with [Moon Raiment]> <before discovering [Killer Moves]>",
    "Unavailable <for units with [White Jade Gu]> <before discovering [Killer Moves]>",
    "Unavailable <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when below [1] [Moon Orchid]>",
    "Unavailable <for [Moon Gu Master] units> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when below [1] [Jade]>",
    "Unavailable <for [Strength Gu Master] units> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when below [1] [Wild Boar]>",
    "Unavailable <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when below [1] [Jade]>",
    "Unavailable <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when below [2] [Jade]>",
]
RO_DEAD = [
    "Unavailable <for [Gu Master] units> <for units with [Jade Skin Gu]>",
    "Unavailable <for [Gu Master] units> <when below [1] [Jade]>",
]
# Refine Gu closes where no rung AND (for a Rank One) no Liquor Worm lure can happen.
LW_IMPOSSIBLE = ["<for units with [Liquor Worm]>", "<when below [1] [Wine]>", "<when below [31] [Gold]>"]
PROMO_DEAD = LADDER_DEAD + [f"{d} {c}" for d in RO_DEAD for c in LW_IMPOSSIBLE]


def starve(gu, food):
    """Canon: a Gu that is not fed starves (MOD_SPEC section 5). While its food is in deficit, each holder loses it at 10% a
    turn, so an overdraw (the AI promotes on a stale resource count [src]) heals itself instead of lasting forever."""
    return f"[This Unit] loses the [{gu}] promotion <upon turn start> <when below [0] [{food}]> <with [10]% chance>"


def ladder(base, fusion, tusk):
    """Highest rung first: choice uniques fire in list order and promotion conditionals are read live, so one attempt
    climbs at most one rung. Every unit state matches at most one 'gains' line (one chance roll per attempt, E5).
    The 'loses' lines are deterministic: they remove the two ingredients only after a successful fusion."""
    b, f, t = (f"<with [{x}]% chance>" for x in (base, fusion, tusk))
    return [
        f"[This Unit] gains the [Killer Move] promotion <for units with [Moon Raiment]> <for units without [Killer Move]> <after discovering [Killer Moves]> {b}",
        f"[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units without [Killer Move]> <after discovering [Killer Moves]> {b}",
        f"[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when above [0] [Wild Boar]> {t}",
        f"[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when below [1] [Wild Boar]> {f}",
        f"[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when above [0] [Wild Boar]> {t}",
        f"[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when below [1] [Wild Boar]> {f}",
        "[This Unit] loses the [White Boar Gu] promotion <for units with [White Jade Gu]>",
        "[This Unit] loses the [Jade Skin Gu] promotion <for units with [White Jade Gu]>",
        f"[This Unit] gains the [Moon Raiment] promotion <for [Moon Gu Master] units> <for units with [Moonlight Gu]> <for units with [Jade Skin Gu]> {f}",
        f"[This Unit] gains the [Moon Raiment] promotion <for [Moon Gu Master] units> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> {f}",
        "[This Unit] loses the [Moonlight Gu] promotion <for units with [Moon Raiment]>",
        "[This Unit] loses the [Jade Skin Gu] promotion <for units with [Moon Raiment]>",
        f"[This Unit] gains the [White Boar Gu] promotion <for [Strength Gu Master] units> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when above [0] [Wild Boar]> {b}",
        f"[This Unit] gains the [Moonlight Gu] promotion <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when above [0] [Moon Orchid]> {b}",
        f"[This Unit] gains the [Jade Skin Gu] promotion <for [Gu Master] units> <for units without [Jade Skin Gu]> <when above [0] [Jade]> {b}",
    ]


# ---------------- Promotions (15) ----------------
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
    # rank-1 Gu (canon)
    {"name": "Moonlight Gu", "uniques": ["[+20]% Strength <when attacking>", "Consumes [1] [Moon Orchid]", starve("Moonlight Gu", "Moon Orchid"),
                                         "[-10]% Strength <for [Strength Gu Master] units>",
                                         # canon: D-grade students could not refine it (fires when added, E4) [src order]
                                         "[This Unit] loses the [Moonlight Gu] promotion <for [Gu Master] units> <for units with [Aptitude D]>"]},
    {"name": "White Boar Gu", "uniques": ["[+15]% Strength", "Consumes [1] [Wild Boar]", starve("White Boar Gu", "Wild Boar")]},
    {"name": "Black Boar Gu", "uniques": ["[+15]% Strength", "Consumes [1] [Wild Boar]", starve("Black Boar Gu", "Wild Boar")]},
    {"name": "Jade Skin Gu", "uniques": ["[+15]% Strength <when defending>", "Consumes [1] [Jade]", starve("Jade Skin Gu", "Jade")]},
    {"name": "Liquor Worm", "uniques": ["[+50]% XP gained from combat", "Consumes [1] [Wine]", starve("Liquor Worm", "Wine"),
                                        # canon: it refines rank-one essence only; after the breakthrough it is let go
                                        "[This Unit] loses the [Liquor Worm] promotion <upon turn start> <for [Moon Gu Master] units>",
                                        "[This Unit] loses the [Liquor Worm] promotion <upon turn start> <for [Strength Gu Master] units>"]},
    # rank-2 fusions (canon recipes); each keeps what its ingredients gave
    {"name": "White Jade Gu", "uniques": ["[+15]% Strength", "[+30]% Strength <when defending>", "Consumes [2] [Jade]",
                                          starve("White Jade Gu", "Jade")]},
    {"name": "Moon Raiment", "uniques": ["[+20]% Strength <when attacking>", "[+20]% Strength <when defending>",
                                         "[+10]% Strength bonus for [Military] units within [1] tiles",
                                         "Consumes [1] [Moon Orchid]", starve("Moon Raiment", "Moon Orchid")]},
    {"name": "Killer Move", "uniques": ["[+25]% Strength <when attacking>", "[+25]% maintenance costs",
                                        # a killer move needs its rank-2 Gu; if that Gu starved, the move goes too
                                        "[This Unit] loses the [Killer Move] promotion <upon turn start> <for units without [White Jade Gu]> <for units without [Moon Raiment]>"]},
    # clan emblem Gu (canon names, ch22); effects and foods unknown, so they eat stones
    {"name": "Bear Strength Gu", "uniques": ["[+10]% Strength", "[+10]% maintenance costs"]},
    {"name": "Stream Gu", "uniques": ["[+10] HP when healing", "[+10]% maintenance costs"]},
])

# ---------------- Events (exactly 5) ----------------
BAI = "<for [Bai Clan] Civilizations>"
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
    {"name": "Refinement Attempt", "text": "The furnace is lit. How far will you risk it?", "choices": [
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
            "Only available <for [Gu Master] units> <for units without [Liquor Worm]> <when above [0] [Wine]> <when above [30] [Gold]>",
            "Gain [-30] [Gold]", "[This Unit] gains the [Liquor Worm] promotion <with [70]% chance>", w("+0")]},
        {"text": "Let the furnace cool", "uniques": ["[This Unit] gains [5] XP", w("-95")]},
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
        {"text": "Abandon the outer fields", "uniques": ["[-1] population [in all cities]", w("-30")]},
        {"text": "Raise the formation", "uniques": [
            "Only available <if [Formation Platform] is constructed> <when above [70] [Gold]>",
            f"Gain [-40] [Gold] <during the [{E3}]>", f"Gain [-70] [Gold] <during the [{E4}]>",
            "[-20]% [Production] <for [5] turns>", w("+50")]},
    ]},
    {"name": "Betrayal", "text": "A clan member has sold you out and fled with stones and Gu.", "choices": [
        {"text": "Let the traitor go", "uniques": ["Only available <when above [60] [Gold]>", "Gain [-60] [Gold]",
                                                   w("+0")]},
        {"text": "Hunt the traitor down", "uniques": [
            "A [Rank Two Strength Gu Master] rebels <after adopting [Strength Path]>",
            "A [Rank Two Moon Gu Master] rebels <after adopting [Moon Path]>",
            "A [Rank One Gu Master] rebels <before adopting [Strength Path]> <before adopting [Moon Path]>",
            w("+0"), w("+200", "<for [Tie Clan] Civilizations>")]},  # R2 T1: the constables hunt
        {"text": "Judge the traitor by clan law", "uniques": ["Only available <after adopting [Righteous Path]>",
                                                     "[-1] population [in capital]", "[+2 Happiness] <for [10] turns>",
                                                     w("+100")]},
        {"text": "Strike first and take the traitor's Gu", "uniques": ["Only available <after adopting [Demonic Path]>",
                                                            "Gain [40] [Gold]", "[-1] population [in capital]",
                                                            "[-3 Happiness] <for [10] turns>", w("+100"),
                                                            w("-75", "<when below [0] [Happiness]>")]},
    ]},
    {"name": "Stone Shortage", "text": "The stone vaults are empty and the Gu are going hungry.", "choices": [
        {"text": "Ration the Gu feed", "uniques": ["[-40]% maintenance costs <for [8] turns>",
                                                  "[-15]% Strength <for [8] turns>", w("+100")]},
        {"text": "Borrow from the merchant caravans", "uniques": [
            "Only available <when above [-100] [Gold]>", "Gain [80] [Gold]", "[-6 Gold] <for [20] turns>", w("-80")]},
        {"text": "Squeeze the mortals", "uniques": ["Gain [50] [Gold]", "[-1] population [in capital]", w("-20")]},
        {"text": "Rob a passing caravan", "uniques": [
            "Only available <after adopting [Demonic Path]>", "Gain [70] [Gold]",
            "Triggers a [Betrayal] event <with [25]% chance>", w("+50")]},
    ]},
])

# ---------------- Buildings (12: 7 + 1 Tie unique + 2 national wonders + 2 world wonders) ----------------
SPRING_TAKEN = "Unavailable <if [Flower Wine Monk Inheritance] is constructed>"
dump("Buildings.json", [
    # R2 T6: the palace is the clan-head pavilion; its ancestral hall (old 'Ancestral Hall' building) is folded in
    {"name": PAVILION, "isNationalWonder": True, "cost": 0, "production": 3, "gold": 5, "science": 2,
     "culture": 3, "happiness": 1, "cityStrength": 3, "uniques": ["Indicates the capital city"]},
    # R2 T6: the clan's primeval spring and the flower sea around it (was 'Awakening Grounds')
    {"name": SPRING, "isNationalWonder": True, "requiredTech": "Aperture Awakening", "cost": 75, "culture": 1,
     "gold": 2, "uniques": ["Can only be built <in [Capital] cities>", SPRING_TAKEN]},
    {"name": "Moon Orchid Flower Sea", "isNationalWonder": True, "uniqueTo": "Gu Yue Clan", "replaces": SPRING,
     "requiredTech": "Aperture Awakening", "cost": 75, "culture": 1, "gold": 2,
     "uniques": ["Can only be built <in [Capital] cities>", SPRING_TAKEN, "Provides [2] [Moon Orchid]"]},
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
    {"name": "Formation Platform", "requiredTech": "Gu Formations", "cost": 110, "maintenance": 1, "cityStrength": 8,
     "cityHealth": 50},
    # R2 T1: Tie unique building (replacement counts for 'Raise the formation' [src containsBuildingOrEquivalent])
    {"name": "Demon Suppression Tower", "uniqueTo": "Tie Clan", "replaces": "Formation Platform",
     "requiredTech": "Gu Formations", "cost": 110, "maintenance": 1, "cityStrength": 12, "cityHealth": 75,
     "happiness": 1},
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
        "[+5]% Strength <for [Moon Gu Master] units> <for every [Adopted [[Moon Path] branch] Policies]>"], "policies": [
        {"name": "Moonlight Mastery", "row": 1, "column": 1, "uniques": ["[+15]% Strength <for units with [Moonlight Gu]>",
                                                                       "[+15]% Strength <for units with [Moon Raiment]>"]},
        {"name": "Orchid Terraces", "row": 1, "column": 3, "uniques": ["Provides [2] [Moon Orchid]",
                                                                     "[-15]% maintenance costs <for [Moon Gu Master] units>"]},
        {"name": "Moon Blade Step", "row": 2, "column": 2, "requires": ["Moonlight Mastery"],
         "uniques": ["[1] Movement <for [Moon Gu Master] units>"]},
        {"name": "Moon Path Complete", "uniques": ["New [Moon Gu Master] units start with [10] XP [in all cities]"]}]},
    {"name": "Strength Path", "era": E12, "priorities": {"Southern Border Supremacy": 5, "Endurance": 5}, "uniques": [
        "Only available <before adopting [Moon Path]>",
        "Provides [2] [Wild Boar]",
        "[+5]% Strength <for [Strength Gu Master] units> <for every [Adopted [[Strength Path] branch] Policies]>"], "policies": [
        {"name": "Boar Strength", "row": 1, "column": 1, "uniques": ["[+15]% Strength <for units with [White Boar Gu]>",
                                                                   "[+15]% Strength <for units with [White Jade Gu]>"]},
        {"name": "Beast Hunters", "row": 1, "column": 3, "uniques": ["Provides [2] [Wild Boar]",
                                                                   "[+25]% Strength <vs [Barbarians] units>"]},
        {"name": "Unyielding Body", "row": 2, "column": 2, "requires": ["Boar Strength"],
         "uniques": ["Heals [10] damage if it kills a unit"]},
        {"name": "Strength Path Complete", "uniques": ["[1] Movement <for [Strength Gu Master] units>"]}]},
])

# ---------------- Resources (6: 1 bonus, 4 strategic Gu foods, 1 luxury) ----------------
DEP = {"minorDepositAmount": {"sparse": 1, "default": 1, "abundant": 2},
       "majorDepositAmount": {"sparse": 2, "default": 2, "abundant": 3}}
SB = ["Guaranteed with Strategic Balance resource option"]
dump("TileResources.json", [
    {"name": "Primeval Stone Vein", "resourceType": "Bonus", "terrainsCanBeFoundOn": ["Hill", "Plains", "Tundra", "Desert"],
     "gold": 1, "improvement": "Stone Mine", "improvementStats": {"gold": 2}},
    dict({"name": "Moon Orchid", "resourceType": "Strategic", "revealedBy": "Gu Feeding",
          "terrainsCanBeFoundOn": ["Grassland", "Plains", "Forest"], "food": 1, "improvement": "Plantation",
          "improvementStats": {"food": 1}, "uniques": SB}, **DEP),
    dict({"name": "Wild Boar", "resourceType": "Strategic", "revealedBy": "Gu Feeding",
          "terrainsCanBeFoundOn": ["Forest", "Jungle", "Grassland", "Hill"], "food": 1, "improvement": "Camp",
          "improvementStats": {"production": 1}, "uniques": SB}, **DEP),
    # R2 T4/T8: Jade Skin Gu eats jade -> Strategic (a consumed luxury is a non-decision [src])
    dict({"name": "Jade", "resourceType": "Strategic", "revealedBy": "Primeval Stone Mining",
          "terrainsCanBeFoundOn": ["Hill"], "gold": 1, "improvement": "Mine", "improvementStats": {"gold": 1},
          "uniques": SB}, **DEP),
    {"name": "Wine", "resourceType": "Strategic", "terrainsCanBeFoundOn": []},
    {"name": "Furs", "resourceType": "Luxury", "terrainsCanBeFoundOn": ["Forest", "Tundra", "Jungle"], "gold": 2,
     "improvement": "Camp", "improvementStats": {"gold": 1}},
])

# ---------------- Terrains (Vanilla minus natural wonders and Fallout) ----------------
ter = [t for t in json5.load(open(os.path.join(VAN, "Terrains.json")))
       if t.get("type") != "NaturalWonder" and t["name"] != "Fallout"]
for t in ter:
    t["uniques"] = [u.replace("receive an extra [Sheep]", "receive an extra [Primeval Stone Vein]") for u in t.get("uniques", [])]
dump("Terrains.json", ter)

# ---------------- Improvements ----------------
imp = [
    {"name": "Farm", "techRequired": "Aperture Awakening", "terrainsCanBeBuiltOn": ["Plains", "Grassland", "Desert", "Flood plains"],
     "food": 1, "turnsToBuild": 7, "uniques": ["Can also be built on tiles adjacent to fresh water"]},
    {"name": "Mine", "techRequired": "Primeval Stone Mining", "terrainsCanBeBuiltOn": ["Hill"], "production": 1, "turnsToBuild": 7},
    {"name": "Stone Mine", "techRequired": "Primeval Stone Mining", "turnsToBuild": 6,
     "uniques": ["Can only be built to improve a resource", "Pillaging this improvement yields approximately [+20 Gold]"]},
    {"name": "Plantation", "techRequired": "Gu Feeding", "turnsToBuild": 6,
     "uniques": ["Can only be built to improve a resource", "Does not need removal of [Forest]"]},
    {"name": "Camp", "techRequired": "Gu Feeding", "turnsToBuild": 6,
     "uniques": ["Does not need removal of [Forest]", "Does not need removal of [Jungle]", "Can only be built to improve a resource"]},
    {"name": "Road", "techRequired": "Primeval Stone Mining", "terrainsCanBeBuiltOn": ["Land"], "turnsToBuild": 4,
     "uniques": ["Can be built outside your borders", "Costs [1] [Gold] per turn when in your territory"]},
    {"name": "Beast Lair", "terrainsCanBeBuiltOn": ["Land"],
     "uniques": ["Unpillagable", "Unbuildable", "Excluded from map editor", "Marks a barbarian camp"]},
    {"name": "Inheritance Site", "terrainsCanBeBuiltOn": ["Land"],
     "uniques": ["Unpillagable", "Provides a random bonus when entered", "Unbuildable",
                 "Does not need removal of [Forest]", "Does not need removal of [Jungle]"]},
]
van_imp = {i["name"]: i for i in json5.load(open(os.path.join(VAN, "TileImprovements.json")))}
for n, tech in (("Remove Forest", "Primeval Stone Mining"), ("Remove Jungle", "Gu Formations"), ("Remove Marsh", "Gu Formations"),
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
           ["Gu Yue Village", "Orchid Slope", "Bamboo Ridge", "Cold Spring"],
           [emblem("Moonlight Gu", "<when above [0] [Moon Orchid]>"), "Start bias [Hill]"]),
    # R2 T2: the Bai and Xiong leaders are never named in canon (bai jia zu zhang / xiong jia zu zhang)
    nation("Bai Clan", "Bai Clan Leader", "Bai Temperament", [230, 230, 230], [40, 70, 120],
           ["Bai Village", "Waterfall Slope", "Frost Pine Slope"],
           [emblem("Stream Gu"), "[+15]% Strength <vs [Barbarians] units>", "Start bias [Fresh Water]"]),
    nation("Xiong Clan", "Xiong Clan Leader", "Xiong Temperament", [90, 50, 20], [240, 200, 140],
           ["Xiong Village", "Bear Den Ridge", "Boar Hollow"],
           [emblem("Bear Strength Gu"), "Starts with [Strength Path] adopted", "Start bias [Forest]"]),
    # R2 T1: the fourth major (was Rogue Cultivators led by Fang Yuan)
    nation("Tie Clan", "Tie Mu Bai", "Tie Temperament", [56, 56, 64], [213, 93, 93],
           ["Tie Clan City", "Iron Chain Pass", "Black Iron Ridge"],
           ["Starts with [Righteous Path] adopted", "Earn [50]% of killed [Barbarians] unit's [Cost] as [Gold]",
            "Start bias [Hill]"]),
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
    # R2 T4/T7: the caravan's tree-house Gu shop sold Fang Yuan his Black Boar Gu
    {"name": "Merchant Clan", "color": [255, 216, 0], "friendBonusUniques": ["[+2 Gold] [in capital]"],
     "allyBonusUniques": ["[+3 Gold] [in capital]", "[+10]% [Gold]",
                          "All newly-trained [Strength Gu Master] units [in all cities] receive the [Black Boar Gu] promotion <when above [0] [Wild Boar]>"]},
])
dump("Personalities.json", [
    {"name": "Gu Yue Temperament", "science": 7, "culture": 6, "gold": 5, "military": 4, "aggressive": 3,
     "priorities": {"Moon Path": 10, "Righteous Path": 6},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions",
                 "Will not build [Flower Wine Monk Inheritance]"]},
    {"name": "Bai Temperament", "gold": 7, "production": 6, "science": 6, "military": 4, "aggressive": 3,
     "priorities": {"Moon Path": 8, "Righteous Path": 7},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
    {"name": "Xiong Temperament", "military": 7, "aggressive": 6, "production": 6,
     "preferredVictoryType": "Southern Border Supremacy",
     "priorities": {"Strength Path": 10, "Demonic Path": 6, "Righteous Path": 3},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", f"[+100]% weight to [{SPRING}] for AI decisions"]},
    {"name": "Tie Temperament", "military": 6, "aggressive": 4, "production": 6, "loyal": 8, "expansion": 4,
     "priorities": {"Righteous Path": 10, "Strength Path": 8},
     "uniques": ["[+50]% weight to [Demon Suppression Tower] for AI decisions",
                 f"[+100]% weight to [{SPRING}] for AI decisions"]},
])
dump("VictoryTypes.json", [
    {"name": "Southern Border Supremacy", "milestones": ["Capture all capitals"]},
    {"name": "Endurance", "milestones": ["Have highest score after max turns"]},
])

TECHMAP = {"Pottery": "Primeval Stone Mining", "Animal Husbandry": "Gu Feeding", "Mining": "Wine Brewing",
           "The Wheel": "Gu Refinement"}
diffs = json5.load(open(os.path.join(VAN, "Difficulties.json")))
for d in diffs:
    for k in ("playerBonusStartingUnits", "aiMajorCivBonusStartingUnits", "aiCityStateBonusStartingUnits"):
        d[k] = [{"Scout": "Rank One Gu Master", "Settler": "Clan Settler", "Worker": "Mortal Laborer"}.get(u, u) for u in d.get(k, [])]
    d["aiFreeTechs"] = [TECHMAP[t] for t in d.get("aiFreeTechs", [])]
    d["baseHappiness"] = d.get("baseHappiness", 0) + 6  # Slice 1 has one luxury (Furs) instead of Vanilla's many
dump("Difficulties.json", diffs)
dump("Speeds.json", json5.load(open(os.path.join(VAN, "Speeds.json"))))

print(f"{len(set(ALL_UNIQUES))} distinct uniques in {len(os.listdir(OUT))} files written to {OUT}")
