#!/usr/bin/env python3
"""Validation prototype of the Slice 1 plan in docs/LORE_MAPPING.md. NOT the mod.

Writes OUT_DIR/jsons/*.json: a throwaway ruleset holding every object, field and unique the plan names, so the
plan can be checked in context by the repo's checkers and by Unciv's own validator before any real JSON exists:

  tools/slice1_prototype.py /tmp/slice1 && tools/check_all --mod /tmp/slice1 --no-self-test

Phase 2 replaces it with data/*.csv + tools/gen_*.py (MOD_SPEC section 9). Until then, change the plan here and in
docs/LORE_MAPPING.md together; tools/tests checks that every unique the document quotes is generated here.
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


def w(x, cond=""):
    return f"[{x}]% weight to this choice for AI decisions" + (f" {cond}" if cond else "")


# ---------------- ModOptions / Globals ----------------
dump("ModOptions.json", {"isBaseRuleset": True,
                         "uniques": ["Disable religion", "Can only start games from the starting era"],
                         "constants": {"maxXPfromBarbarians": 90}})
dump("Beliefs.json", [])
dump("Religions.json", [])
dump("GlobalUniques.json", {"name": "GlobalUniques", "uniques": [
    # Vanilla unhappiness effects (engine-coupled infrastructure, retargeted to our settler)
    "[-75]% growth [in all cities] <when between [-10] and [-1] [Happiness]>",
    "Nullifies Growth [in all cities] <when below [-10] [Happiness]>",
    "[-50]% [Production] [in all cities] <when below [-10] [Happiness]>",
    "[-33]% Strength <for [All] units> <when below [-10] [Happiness]>",
    "Cannot build [Clan Settler] units <when below [-10] [Happiness]>",
    "Rebel units may spawn <when below [-20] [Happiness]>",
    # Pillar 1: every Gu eats; starving treasury weakens everyone
    "[-3] units cost no maintenance <for [Major] Civilizations>",
    "[-20]% Strength <when below [0] [Gold]>",
    # Pillar 3 / 5 / 1: the world, traitors and hunger
    "Triggers a [Beast Tide] event <upon turn start> <after turn number [30]> <with [3]% chance> <for [Major] Civilizations>",
    "Triggers a [Beast Tide] event <upon turn start> <after turn number [90]> <with [2]% chance> <for [Major] Civilizations>",
    "Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [8]% chance> <for [Major] Civilizations>",
    "Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [3]% chance> <for [Major] Civilizations>",
    "Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [25]% chance> <for [Major] Civilizations>",
]})

# ---------------- Eras ----------------
dump("Eras.json", [
    {"name": E12, "researchAgreementCost": 150, "iconRGB": [72, 140, 100], "startingSettlerUnit": "Clan Settler",
     "startingWorkerCount": 1, "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master",
     "startingGold": 50, "baseUnitBuyCost": 200},
    {"name": E3, "researchAgreementCost": 250, "iconRGB": [205, 205, 215], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 300},
    {"name": E4, "researchAgreementCost": 350, "iconRGB": [230, 190, 60], "startingSettlerUnit": "Clan Settler",
     "startingWorkerUnit": "Mortal Laborer", "startingMilitaryUnit": "Rank One Gu Master", "baseUnitBuyCost": 400},
])

# ---------------- Techs (15) ----------------
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
    {"name": "Electric Wolf", "unitType": "Beast", "movement": 3, "strength": 9, "cost": 30, "uniqueTo": "Barbarians",
     "uniques": ["[+50]% maintenance costs"]},
    {"name": "Electric Wolf King", "unitType": "Beast", "movement": 3, "strength": 16, "cost": 60,
     "requiredTech": "Rank Three Cultivation", "uniqueTo": "Barbarians",
     "uniques": ["[+15]% Strength bonus for [Electric Wolf] units within [2] tiles", "[+100]% maintenance costs"]},
    {"name": "Thunder Crown Wolf", "unitType": "Beast", "movement": 3, "strength": 28, "cost": 120,
     "uniqueTo": "Barbarians",
     "uniques": ["Unbuildable", "[+20]% Strength bonus for [Beast] units within [2] tiles", "[+200]% maintenance costs"]},
])

# States in which no ladder line can fire. They close the refining choices AND the Refine Gu promotion, so the
# AI never pays XP or stones for an attempt that cannot succeed (mechanics review, must-fix 1 and 3).
DEAD = [
    "Unavailable <for units with [Killer Move]>",
    "Unavailable <for [Gu Master] units> <for units with [White Jade Gu]>",
    "Unavailable <for units with [White Jade Gu]> <for units with [Moonlight Gu]> <before discovering [Killer Moves]>",
    "Unavailable <for units with [White Jade Gu]> <for units with [Black Boar Gu]> <before discovering [Killer Moves]>",
    "Unavailable <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <when below [1] [Moon Orchid]>",
    "Unavailable <for [Strength Gu Master] units> <for units without [Black Boar Gu]> <for units without [Moonlight Gu]> <when below [1] [Wild Boar]>",
]


# ---------------- Promotions (10) ----------------
dump("UnitPromotions.json", [
    {"name": "Aptitude A", "uniques": ["[+15]% Strength", "[-20]% maintenance costs", "[+25]% XP gained from combat"]},
    {"name": "Aptitude B", "uniques": ["[+5]% Strength", "[-10]% maintenance costs", "[+10]% XP gained from combat"]},
    {"name": "Aptitude C", "uniques": []},
    {"name": "Aptitude D", "uniques": ["[-10]% Strength", "[+20]% maintenance costs", "[-25]% XP gained from combat"]},
    {"name": "Refine Gu", "unitTypes": GM_TYPES, "uniques": [
        "Only available <after discovering [Gu Refinement]>",
        "Unavailable <when below [50] HP>"] + DEAD + [
        "Triggers a [Refinement Attempt] event",
        "[This Unit] loses the [Refine Gu] promotion <upon turn start>"]},
    {"name": "Moonlight Gu", "uniques": ["[+20]% Strength <when attacking>", "Consumes [1] [Moon Orchid]",
                                         "[-10]% Strength <for [Strength Gu Master] units>"]},
    {"name": "Black Boar Gu", "uniques": ["[+15]% Strength", "Consumes [1] [Wild Boar]",
                                          "[-10]% Strength <for [Moon Gu Master] units>"]},
    {"name": "White Jade Gu", "uniques": ["[+25]% Strength <when defending>", "[+20]% maintenance costs"]},
    {"name": "Liquor Worm", "uniques": ["[+50]% XP gained from combat", "Consumes [1] [Wine]"]},
    {"name": "Killer Move", "uniques": ["[+25]% Strength <when attacking>", "[+25]% maintenance costs"]},
])

# ---------------- Events (exactly 5) ----------------
def ladder(chance):
    # Highest rung first: choice uniques fire in list order and promotion conditionals are read live, so one
    # attempt climbs at most one rung. Every unit state matches at most one line (one roll per attempt, E5).
    c = f"<with [{chance}]% chance>"
    return [
        f"[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units with [Moonlight Gu]> <after discovering [Killer Moves]> {c}",
        f"[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units with [Black Boar Gu]> <after discovering [Killer Moves]> {c}",
        f"[This Unit] gains the [White Jade Gu] promotion <for units with [Moonlight Gu]> <for units without [White Jade Gu]> {c}",
        f"[This Unit] gains the [White Jade Gu] promotion <for units with [Black Boar Gu]> <for units without [White Jade Gu]> {c}",
        f"[This Unit] gains the [Moonlight Gu] promotion <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <when above [0] [Moon Orchid]> {c}",
        f"[This Unit] gains the [Black Boar Gu] promotion <for [Strength Gu Master] units> <for units without [Black Boar Gu]> <for units without [Moonlight Gu]> <when above [0] [Wild Boar]> {c}",
        f"[This Unit] gains the [White Jade Gu] promotion <for [Gu Master] units> <for units without [White Jade Gu]> <for units without [Moonlight Gu]> {c}",
    ]




ALTAR = "<if [Awakening Grounds] is constructed>"
BAI = "<for [Bai Clan] Civilizations>"
dump("Events.json", [
    {"name": "Aptitude Awakening", "presentation": "None", "choices": [
        {"text": "Grade A aptitude", "uniques": ["[This Unit] gains the [Aptitude A] promotion", w("-95"),
                                                 w("+100", ALTAR), w("+100", BAI)]},
        {"text": "Grade B aptitude", "uniques": ["[This Unit] gains the [Aptitude B] promotion", w("-80"),
                                                 w("+50", ALTAR), w("+25", BAI)]},
        {"text": "Grade C aptitude", "uniques": ["[This Unit] gains the [Aptitude C] promotion", w("-65")]},
        {"text": "Grade D aptitude", "uniques": ["[This Unit] gains the [Aptitude D] promotion", w("-60"),
                                                 w("-25", ALTAR)]},
    ]},
    {"name": "Refinement Attempt", "text": "The furnace is lit. How far will you risk it?", "choices": [
        {"text": "Refine carefully", "uniques":
            ["Only available <if [Refinement Chamber] is constructed> <when above [80] [Gold]>",
             f"Unavailable <when below [140] [Gold]> <during the [{E3}]>",
             f"Unavailable <when below [200] [Gold]> <during the [{E4}]>",
             f"Gain [-40] [Gold] <during the [{E12}]>", f"Gain [-70] [Gold] <during the [{E3}]>",
             f"Gain [-100] [Gold] <during the [{E4}]>"]
            + DEAD + ladder(85) + [w("+50"), w("-60", "<when below [150] [Gold]>")]},
        {"text": "Refine recklessly", "uniques": DEAD + ["Unavailable <when below [31] HP>"] + ladder(50)
            + ["[This Unit] takes [30] damage", w("+0"), w("-90", "<when below [50] HP>")]},
        {"text": "Lure a wild Liquor Worm with wine", "uniques": [
            "Only available <for units without [Liquor Worm]> <when above [0] [Wine]> <when above [20] [Gold]>",
            "Unavailable <for [Beast] units>",
            "Gain [-20] [Gold]", "[This Unit] gains the [Liquor Worm] promotion <with [70]% chance>", w("+0")]},
        {"text": "Let the furnace cool", "uniques": ["[This Unit] gains [5] XP", w("-95")]},
    ]},
    {"name": "Beast Tide", "text": "A beast tide pours down the mountain toward your villages.", "choices": [
        {"text": "Meet the tide in the field", "uniques": [
            f"[2] [Electric Wolf]s rebel <during the [{E12}]>",
            f"[3] [Electric Wolf]s rebel <starting from the [{E3}]>",
            f"A [Electric Wolf King] rebels <starting from the [{E3}]>",
            f"A [Thunder Crown Wolf] rebels <during the [{E4}]>",
            w("+0")]},
        {"text": "Pay rogue cultivators to thin the pack", "uniques": [
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
            w("+0")]},
        {"text": "Judge the traitor by clan law", "uniques": ["Only available <after adopting [Righteous Path]>",
                                                     "[-1] population [in capital]", "[+2 Happiness] <for [10] turns>",
                                                     w("+100")]},
        {"text": "Strike first and take the traitor's Gu", "uniques": ["Only available <after adopting [Demonic Path]>",
                                                            "Gain [40] [Gold]", "[-1] population [in capital]",
                                                            "[-3 Happiness] <for [10] turns>", w("+100")]},
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

# ---------------- Buildings (12: 9 + 1 national wonder + 2 world wonders; Clan Hall counted) ----------------
dump("Buildings.json", [
    {"name": "Clan Hall", "isNationalWonder": True, "cost": 0, "production": 3, "gold": 5, "science": 2,
     "culture": 1, "cityStrength": 3, "uniques": ["Indicates the capital city"]},
    {"name": "Ancestral Hall", "requiredTech": "Aperture Awakening", "cost": 45, "maintenance": 1, "culture": 2,
     "happiness": 1},
    {"name": "Awakening Grounds", "isNationalWonder": True, "requiredTech": "Aperture Awakening", "cost": 75,
     "culture": 1},
    {"name": "Gu Academy", "requiredTech": "Gu Feeding", "cost": 65, "maintenance": 1, "science": 1,
     "uniques": ["[+1 Science] per [2] population [in this city]", "New [Military] units start with [10] XP [in this city]"]},
    {"name": "Gu Feeding House", "requiredTech": "Gu Feeding", "cost": 70, "maintenance": 1,
     "uniques": ["Provides [1] [Moon Orchid]", "Provides [1] [Wild Boar]"]},
    {"name": "Moon Orchid Terrace", "uniqueTo": "Gu Yue Clan", "replaces": "Gu Feeding House",
     "requiredTech": "Gu Feeding", "cost": 70, "maintenance": 1, "food": 1,
     "uniques": ["Provides [2] [Moon Orchid]", "Provides [1] [Wild Boar]"]},
    {"name": "Wine Cellar", "requiredTech": "Wine Brewing", "cost": 60, "maintenance": 1, "happiness": 1,
     "uniques": ["Provides [1] [Wine]"]},
    {"name": "Refinement Chamber", "requiredTech": "Gu Refinement", "cost": 90, "maintenance": 1, "production": 1,
     "science": 1},
    {"name": "Formation Platform", "requiredTech": "Gu Formations", "cost": 110, "maintenance": 1, "cityStrength": 8,
     "cityHealth": 50},
    {"name": "Trading House", "requiredTech": "Merchant Caravans", "cost": 130, "gold": 2,
     "percentStatBonus": {"gold": 20}},
    {"name": "Flower Wine Monk Inheritance", "isWonder": True, "requiredTech": "Inheritance Lore", "cost": 240,
     "culture": 3, "uniques": ["Provides [2] [Wine]", "[+25]% XP gained from combat"]},
    {"name": "Shang Clan City", "isWonder": True, "requiredTech": "Super Clan Commerce", "cost": 300, "gold": 5,
     "uniques": ["[+2 Gold] from all [Trading House] buildings",
                 "Gifts of Gold to City-States generate [+50]% more Influence"]},
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
        {"name": "Blood Harvest", "row": 1, "column": 3, "uniques": ["Heals [15] damage if it kills a unit",
                                                                   "[+25]% XP gained from combat"]},
        {"name": "Ruthless Cultivation", "row": 2, "column": 2, "requires": ["Plunder"], "uniques": [
            "Upon capturing a city, receive [3] times its [Gold] production as [Gold] immediately",
            "[-20]% maintenance costs <when at war>",
            "[+20]% Unhappiness from [Population] [in all cities]"]},
        {"name": "Demonic Path Complete", "uniques": ["[+15]% Strength <when attacking>"]}]},
    {"name": "Moon Path", "era": E12, "priorities": {"Southern Border Supremacy": 5, "Endurance": 5}, "uniques": [
        "Only available <before adopting [Strength Path]>",
        "Provides [2] [Moon Orchid]",
        "[+5]% Strength <for [Moon Gu Master] units> <for every [Adopted [[Moon Path] branch] Policies]>"], "policies": [
        {"name": "Moonlight Mastery", "row": 1, "column": 1, "uniques": ["[+15]% Strength <for units with [Moonlight Gu]>"]},
        {"name": "Orchid Terraces", "row": 1, "column": 3, "uniques": ["Provides [2] [Moon Orchid]",
                                                                     "[-15]% maintenance costs <for [Moon Gu Master] units>"]},
        {"name": "Moon Blade Step", "row": 2, "column": 2, "requires": ["Moonlight Mastery"],
         "uniques": ["[1] Movement <for [Moon Gu Master] units>"]},
        {"name": "Moon Path Complete", "uniques": ["New [Moon Gu Master] units start with [10] XP [in all cities]"]}]},
    {"name": "Strength Path", "era": E12, "priorities": {"Southern Border Supremacy": 5, "Endurance": 5}, "uniques": [
        "Only available <before adopting [Moon Path]>",
        "Provides [2] [Wild Boar]",
        "[+5]% Strength <for [Strength Gu Master] units> <for every [Adopted [[Strength Path] branch] Policies]>"], "policies": [
        {"name": "Boar Strength", "row": 1, "column": 1, "uniques": ["[+15]% Strength <for units with [Black Boar Gu]>"]},
        {"name": "Beast Hunters", "row": 1, "column": 3, "uniques": ["Provides [2] [Wild Boar]",
                                                                   "[+25]% Strength <vs [Barbarians] units>"]},
        {"name": "Unyielding Body", "row": 2, "column": 2, "requires": ["Boar Strength"],
         "uniques": ["Heals [10] damage if it kills a unit"]},
        {"name": "Strength Path Complete", "uniques": ["[1] Movement <for [Strength Gu Master] units>"]}]},
])

# ---------------- Resources (6) ----------------
DEP = {"minorDepositAmount": {"sparse": 1, "default": 1, "abundant": 2},
       "majorDepositAmount": {"sparse": 2, "default": 2, "abundant": 3}}
dump("TileResources.json", [
    {"name": "Primeval Stone Vein", "resourceType": "Bonus", "terrainsCanBeFoundOn": ["Hill", "Plains", "Tundra", "Desert"],
     "gold": 1, "improvement": "Stone Mine", "improvementStats": {"gold": 2}},
    dict({"name": "Moon Orchid", "resourceType": "Strategic", "revealedBy": "Gu Feeding",
          "terrainsCanBeFoundOn": ["Grassland", "Plains", "Forest"], "food": 1, "improvement": "Plantation",
          "improvementStats": {"food": 1}, "uniques": ["Guaranteed with Strategic Balance resource option"]}, **DEP),
    dict({"name": "Wild Boar", "resourceType": "Strategic", "revealedBy": "Gu Feeding",
          "terrainsCanBeFoundOn": ["Forest", "Jungle", "Grassland", "Hill"], "food": 1, "improvement": "Camp",
          "improvementStats": {"production": 1}, "uniques": ["Guaranteed with Strategic Balance resource option"]}, **DEP),
    {"name": "Wine", "resourceType": "Strategic", "terrainsCanBeFoundOn": []},
    {"name": "Jade", "resourceType": "Luxury", "terrainsCanBeFoundOn": ["Hill"], "gold": 2,
     "improvement": "Mine", "improvementStats": {"gold": 1}},
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
     "uniques": ["Triggers a [Refinement Attempt] event", "Only available <for [Military] units>", "Unavailable <for [Beast] units>"]},
    {"name": "Inheritance Trial", "notification": "The inheritance tests our Gu Master.", "weight": 2,
     "uniques": ["[This Unit] gains [30] XP", "[This Unit] takes [40] damage", "Only available <for [Military] units>", "Unavailable <for [Beast] units>"]},
    {"name": "Inheritance Trap", "notification": "The inheritance was guarded by a trap!", "weight": 1,
     "uniques": ["[This Unit] takes [40] damage", "Only available <for [Military] units> <after turn number [10]>"]},
    {"name": "Wandering Rogue Cultivator", "notification": "A rogue cultivator sheltering in the ruins joins us.",
     "weight": 1, "uniques": ["Free [Rank One Gu Master] found in the ruins"]},
])

# ---------------- Nations ----------------
def nation(name, leader, pers, outer, inner, cities, uniques):
    return {"name": name, "leaderName": leader, "adjective": [name], "personality": pers, "outerColor": outer,
            "innerColor": inner, "cities": cities, "uniques": uniques}


dump("Nations.json", [
    nation("Gu Yue Clan", "Gu Yue Bo", "Gu Yue Temperament", [30, 40, 90], [220, 220, 240],
           ["Gu Yue Village", "Orchid Slope", "Bamboo Ridge", "Cold Spring"],
           ["All newly-trained [Rank One Gu Master] units [in all cities] receive the [Moonlight Gu] promotion <after discovering [Gu Feeding]> <when above [0] [Moon Orchid]>",
            "Start bias [Hill]"]),
    nation("Bai Clan", "Bai Ning Bing", "Bai Temperament", [230, 230, 230], [40, 70, 120],
           ["Bai Village", "White Stone Gully", "Frost Pine Slope"],
           ["[+15]% Strength <for units with [Aptitude A]>", "Start bias [Plains]"]),
    nation("Xiong Clan", "Xiong Lin", "Xiong Temperament", [90, 50, 20], [240, 200, 140],
           ["Xiong Village", "Bear Den Ridge", "Boar Hollow"],
           ["Starts with [Strength Path] adopted", "[+15]% Strength <vs [Barbarians] units>", "Start bias [Forest]"]),
    nation("Rogue Cultivators", "Fang Yuan", "Rogue Temperament", [20, 20, 20], [200, 30, 30],
           ["Hidden Cave", "Wolf Ravine", "Nameless Camp"],
           ["[+15]% [Science]", "[1] units cost no maintenance", "[+50]% unhappiness from the number of cities",
            "Triggers a [Beast Tide] event <upon turn start> <after turn number [20]> <with [2]% chance>"]),
    {"name": "Hairy Man Tribe", "cityStateType": "Refiner Tribe", "outerColor": [60, 30, 10], "innerColor": [255, 230, 180],
     "cities": ["Hairy Man Hollow"]},
    {"name": "Stone Man Tribe", "cityStateType": "Stone Tribe", "outerColor": [90, 90, 90], "innerColor": [250, 250, 250],
     "cities": ["Stone Man Crag"]},
    {"name": "Jia Clan", "cityStateType": "Merchant Clan", "outerColor": [120, 90, 0], "innerColor": [255, 230, 120],
     "cities": ["Jia Caravan Camp"]},
    {"name": "Barbarians", "outerColor": [0, 0, 0], "innerColor": [185, 12, 12],
     "uniques": ["Can only heal by pillaging", "Excluded from map editor"]},
    {"name": "Spectator", "outerColor": [255, 255, 255]},
])
dump("CityStateTypes.json", [
    {"name": "Refiner Tribe", "color": [180, 120, 60], "friendBonusUniques": ["[+2 Science] [in capital]"],
     "allyBonusUniques": ["[+2 Science] [in capital]", "[+20]% XP gained from combat"]},
    {"name": "Stone Tribe", "color": [130, 130, 130], "friendBonusUniques": ["[+2 Production] [in capital]"],
     "allyBonusUniques": ["[+2 Production] [in capital]", "[+20]% Strength for cities"]},
    {"name": "Merchant Clan", "color": [255, 216, 0], "friendBonusUniques": ["[+2 Gold] [in capital]"],
     "allyBonusUniques": ["[+3 Gold] [in capital]", "[+10]% [Gold]"]},
])
dump("Personalities.json", [
    {"name": "Gu Yue Temperament", "science": 7, "culture": 6, "gold": 5, "military": 4, "aggressive": 3,
     "priorities": {"Moon Path": 10, "Righteous Path": 6},
     "uniques": ["[+50]% weight to [Moon Orchid Terrace] for AI decisions", "[+100]% weight to [Awakening Grounds] for AI decisions"]},
    {"name": "Bai Temperament", "gold": 7, "production": 6, "science": 6, "military": 4, "aggressive": 3,
     "priorities": {"Moon Path": 8, "Righteous Path": 7},
     "uniques": ["[+50]% weight to [Gu Academy] for AI decisions", "[+100]% weight to [Awakening Grounds] for AI decisions"]},
    {"name": "Xiong Temperament", "military": 7, "aggressive": 6, "production": 6,
     "priorities": {"Strength Path": 10, "Righteous Path": 5, "Demonic Path": 3},
     "uniques": ["[+50]% weight to [Formation Platform] for AI decisions", "[+100]% weight to [Awakening Grounds] for AI decisions"]},
    {"name": "Rogue Temperament", "military": 7, "aggressive": 7, "expansion": 3, "loyal": 0,
     "priorities": {"Strength Path": 12, "Demonic Path": 10},
     "uniques": ["[+50]% weight to [Refinement Chamber] for AI decisions", "[+50]% weight to [Wine Cellar] for AI decisions",
                 "[+100]% weight to [Awakening Grounds] for AI decisions"]},
])
dump("VictoryTypes.json", [
    {"name": "Southern Border Supremacy", "milestones": ["Capture all capitals"]},
    {"name": "Endurance", "milestones": ["Have highest score after max turns"]},
])

# Difficulties: Vanilla 8 levels, bonus units / free techs remapped, AI upkeep softened
TECHMAP = {"Pottery": "Primeval Stone Mining", "Animal Husbandry": "Gu Feeding", "Mining": "Wine Brewing",
           "The Wheel": "Gu Refinement"}
diffs = json5.load(open(os.path.join(VAN, "Difficulties.json")))
for d in diffs:
    for k in ("playerBonusStartingUnits", "aiMajorCivBonusStartingUnits", "aiCityStateBonusStartingUnits"):
        d[k] = [{"Scout": "Rank One Gu Master", "Settler": "Clan Settler", "Worker": "Mortal Laborer"}.get(u, u) for u in d.get(k, [])]
    d["aiFreeTechs"] = [TECHMAP[t] for t in d.get("aiFreeTechs", [])]
dump("Difficulties.json", diffs)
dump("Speeds.json", json5.load(open(os.path.join(VAN, "Speeds.json"))))

print(f"{len(set(ALL_UNIQUES))} distinct uniques in {len(os.listdir(OUT))} files written to {OUT}")
