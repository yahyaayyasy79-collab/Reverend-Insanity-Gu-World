#!/usr/bin/env python3
"""MOD_SPEC_3 Phase A3 (throwaway branch): the shipped jsons/ plus one test object per capability.
Usage: build_test_mod.py OUT_DIR  ->  OUT_DIR/mods/A3TEST/jsons"""
import json, shutil, sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1]) / "mods" / "A3TEST" / "jsons"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(repo / "jsons", out)
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
print(out)
