#!/usr/bin/env python3
"""MOD_SPEC_3 Phase A3 (throwaway branch): the shipped jsons/ plus one test object per capability.
Usage: build_test_mod.py OUT_DIR [SHIPPED_JSONS]  ->  OUT_DIR/mods/A3TEST/jsons
SHIPPED_JSONS: the real mod's jsons/ (default: this checkout's; on the test branch pass the main checkout's)."""
import json, shutil, sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1]) / "mods" / "A3TEST" / "jsons"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(Path(sys.argv[2]) if len(sys.argv) > 2 else repo / "jsons", out)
load = lambda f: json.loads((out / f).read_text(encoding="utf-8"))  # noqa: E731
save = lambda f, d: (out / f).write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")  # noqa: E731
TYPES = ["Gu Master", "Gu Immortal", "Venerable"]

ut = load("UnitTypes.json")
ut += [{"name": "Gu Immortal", "movementType": "Land"}, {"name": "Venerable", "movementType": "Land"}]
save("UnitTypes.json", ut)

units = load("Units.json")
units += [
    # test 1 and 2: a rank chain across unit types
    {"name": "Test Rank Five", "unitType": "Gu Master", "movement": 2, "strength": 40, "cost": 10,
     "upgradesTo": "Test Rank Six"},
    {"name": "Test Rank Six", "unitType": "Gu Immortal", "movement": 2, "strength": 60, "cost": 10,
     "upgradesTo": "Test Venerable"},
    # test 3 and 4: one per civ, reached by upgrade, dies of its own turn damage
    {"name": "Test Venerable", "unitType": "Venerable", "movement": 2, "strength": 100, "cost": 10,
     "uniques": ["Limited to [1] per Civilization", "Unbuildable", "Cannot be purchased",
                 "[This Unit] takes [30] damage <upon turn start>"]},
]
save("Units.json", units)

promos = load("UnitPromotions.json")
promos += [
    # test 1: one promotion limited to the old unit type, one open to all three
    {"name": "Test Path Old Type", "unitTypes": ["Gu Master"], "uniques": ["[2] Sight"]},
    {"name": "Test Path All", "unitTypes": TYPES, "uniques": ["[1] Movement"]},
    # test 2: a tier behind a prerequisite and a unit conditional
    {"name": "Test Tier Immortal", "unitTypes": TYPES, "prerequisites": ["Test Path All"],
     "uniques": ["Only available <for [Gu Immortal] units>", "[+20]% Strength"]},
    # test 5: per-civ AI weights (a main path for Wu, one for Bai)
    {"name": "Test Wu Path", "unitTypes": TYPES, "uniques": [
        "[+5]% Strength", "[-95]% weight to this choice for AI decisions",
        "[+19900]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>"]},
    {"name": "Test Bai Path", "unitTypes": TYPES, "uniques": [
        "[+5]% Strength", "[-95]% weight to this choice for AI decisions",
        "[+19900]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>"]},
]
save("UnitPromotions.json", promos)

b = load("Buildings.json")
b += [{"name": "Test Ascension", "isWonder": True, "cost": 10, "uniques": ["Unbuildable", "Cannot be purchased"]},
      {"name": "Test True Inheritance", "isWonder": True, "cost": 10, "uniques": ["Unbuildable", "Cannot be purchased"]}]
save("Buildings.json", b)

g = load("GlobalUniques.json")
g["uniques"] += [
    # test 4: the Venerable's death reopens the race and leaves an inheritance
    "Gain [1000] [Gold] <upon losing a [Test Venerable] unit>",
    "Remove [Test Ascension] [in all cities] <upon losing a [Test Venerable] unit>",
    "Gain a free [Test True Inheritance] [in capital] <upon losing a [Test Venerable] unit>",
    # test 4 side effect: does an upgrade count as losing the old unit?
    "Gain [7] [Gold] <upon losing a [Test Rank Six] unit>",
]
save("GlobalUniques.json", g)
# ---------------- MOD_SPEC_2 Phase A: one test object per risky pattern ----------------
w0 = "[+0]% weight to this choice for AI decisions"
res = load("TileResources.json")
res += [{"name": "Test Lifespan Gu", "resourceType": "Strategic", "terrainsCanBeFoundOn": [], "uniques": ["Stockpiled"]},
        {"name": "Test Trial Counter", "resourceType": "Strategic", "terrainsCanBeFoundOn": [], "uniques": ["Stockpiled"]}]
save("TileResources.json", res)

b = load("Buildings.json")
b += [
    # A1 for-every Strength: path-marker buildings (filter markers "Strength Path" / "Wisdom Path")
    {"name": "Test Strength Gu A", "cost": 10, "uniques": ["Strength Path"]},
    {"name": "Test Strength Gu B", "cost": 10, "uniques": ["Strength Path"]},
    {"name": "Test Wisdom Gu A", "cost": 10, "uniques": ["Wisdom Path"]},
    # A2 Remove on a wonder; also capture of a built wonder
    {"name": "Test Immortal Gu", "isWonder": True, "cost": 10,
     "uniques": ["Immortal Gu", "Strength Path", "Never destroyed when the city is captured"]},
    # A3 Unbuildable plus free grant (Fate Gu stand-in), granted once by a nation unique
    {"name": "Test Fate Gu", "isWonder": True, "cost": 10,
     "uniques": ["Unbuildable", "Cannot be purchased", "Never destroyed when the city is captured"]},
    # A4 the inheritance that closes the trial for everybody
    {"name": "Test Inheritance Wonder", "isWonder": True, "cost": 10,
     "uniques": ["Unbuildable", "Cannot be purchased", "Never destroyed when the city is captured"]},
    # A6 max() countable: single-path mastery
    {"name": "Test Venerable Ascension", "isWonder": True, "cost": 10,
     "uniques": ["Only available <when number of [max([[Strength Path] Buildings], [[Wisdom Path] Buildings])] is more than [1]>"]},
]
save("Buildings.json", b)

units = load("Units.json")
units += [
    # A1: dao marks of its path amplify it, a conflicting path weakens it
    {"name": "Test Dao Unit", "unitType": "Gu Master", "movement": 2, "strength": 20, "cost": 10,
     "uniques": ["[+5]% Strength <for every [1] [[Strength Path] Buildings]>",
                 "[-5]% Strength <for every [1] [[Wisdom Path] Buildings]>"]},
    # A5: an immortal that decays once the clan's lifespan Gu run out
    {"name": "Test Immortal", "unitType": "Gu Immortal", "movement": 2, "strength": 60, "cost": 10,
     "uniques": ["[This Unit] takes [30] damage <upon turn start> <when below [1] [Test Lifespan Gu]>"]},
]
save("Units.json", units)

g = load("GlobalUniques.json")
g["uniques"] += [
    # A5 lifespan: one lifespan Gu per immortal, every 2 turns
    "Instantly consumes [1] [Test Lifespan Gu] <upon turn start> <every [2] turns> <for every [1] [[Test Immortal] Units]>",
    # A4 owned-tile trigger, throttled
    "Triggers a [Test Trial] event <upon turn start> <when number of [Owned [Land] Tiles] is more than [6]> <every [3] turns>",
]
save("GlobalUniques.json", g)

ev = load("Events.json")
ev += [{"name": "Test Trial", "presentation": "None",
        "uniques": ["Unavailable <if [Test Inheritance Wonder] is constructed by anybody>"],
        "choices": [{"text": "Test trial passed", "uniques": ["Instantly provides [1] [Test Trial Counter]", w0]}]}]
save("Events.json", ev)

imp = load("TileImprovements.json")
imp += [
    # A7 camp gate, two variants: the conditional on the camp marker itself, and Only available on the improvement
    {"name": "Test Dream Camp", "terrainsCanBeBuiltOn": ["Land"],
     "uniques": ["Marks a barbarian camp <if [Test Fate Gu] is not constructed by anybody>", "Unbuildable", "Unpillagable",
                 "Excluded from map editor"]},
    {"name": "Test Gated Camp", "terrainsCanBeBuiltOn": ["Land"],
     "uniques": ["Marks a barbarian camp", "Only available <if [Test Fate Gu] is not constructed by anybody>", "Unbuildable",
                 "Unpillagable", "Excluded from map editor"]},
]
save("TileImprovements.json", imp)

nations = load("Nations.json")
for n in nations:
    if n["name"] == "Bai Clan":  # stand-in for the Heavenly Court: Fate Gu once, at its first city
        n["uniques"].append("Gain a free [Test Fate Gu] [in capital] <upon founding a city> <if [Test Fate Gu] is not constructed by anybody>")
save("Nations.json", nations)
print(out)
