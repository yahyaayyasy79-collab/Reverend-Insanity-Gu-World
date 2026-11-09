"""The paths' basic foods (the user, 2026-11-09: "tambahkan tiap jalur makanan dasar nya ... sebarkanlah sumber daya itu ke
seluruh 5 benua"), from data/path_foods.csv; docs/PATH_ECONOMY.md has the design and the numbers.

Every path has one basic food that its path Gu eats (data/path_gu.csv). A food is a luxury resource whose happiness is
switched off for every luxury (tools/gen_ruleset.py GlobalUniques): with 46 more strategic types the engine's random maps
would place none of any strategic resource on a Small map, as it splits one budget evenly over every strategic type and
rounds down [src MapGenerator.spreadStrategicResources]; luxuries share their budget by count instead [src
MapGenerator.spreadResources], a luxury tile gives one copy [src CityResources], and the top bar shows only strategic
resources [src WorldScreenTopBarResources]. A clan gets a path's food from its improved tiles (1 each), the path's branch
(2), each of its path halls (1) and the path's lore (1). Moon Orchid, Wild Boar and Wine stay the Slice 1 strategic
resources they were (Moon Orchid and Wild Boar are guaranteed near starts with the Strategic Balance option).
"""
from __future__ import annotations

import csv

from common import REPO_ROOT

with open(REPO_ROOT / "data" / "path_foods.csv", newline="", encoding="utf-8") as _f:
    ROWS = list(csv.DictReader(_f))
FOOD = {r["key"]: r for r in ROWS}
SLICE1 = {"Moon Orchid", "Wild Boar", "Wine"}   # already in the ruleset (strategic, Slice 1)
NEW = [r for r in ROWS if r["food"] not in SLICE1]

# Layer 9b (autoplay, 4 x 300: Bai's water and Wu's wind Masters held their Gu 1 time in 6, on a stock of about 3):
# every branch gives 2 on adoption and 2 more with its Insight policy (as the moon's Orchid Beds and the strength's
# Beast Hunters always did), each hall 1, the lore 2 (one Gu fed by the lore alone, a grant needing 2 spare)
BRANCH_FOOD, INSIGHT_FOOD, HALL_FOOD, LORE_FOOD = 2, 2, 1, 2
# kind -> (the improvement that works it, the tile's yield, the improved yield)
KIND = {"plant": ("Plantation", {"food": 1}, {"food": 1}),
        "beast": ("Camp", {"food": 1}, {"production": 1}),
        "sea": ("Camp", {"food": 1}, {"gold": 1}),
        "mineral": ("Mine", {"production": 1}, {"production": 1}),
        "water": ("Spring Cave", {"gold": 1}, {"food": 1}),
        "crafted": ("Inheritance Dig", {"science": 1}, {"science": 1})}
REGION = {"south": ("the Southern Border", "Perbatasan Selatan"), "north": ("the Northern Plains", "Dataran Utara"),
          "west": ("the Western Desert", "Gurun Barat"), "east": ("the Eastern Sea", "Laut Timur"),
          "central": ("the Central Continent", "Benua Tengah")}


def food_of(key: str) -> str:
    return FOOD[key]["food"]


def split(cell: str) -> list[str]:
    return [x for x in cell.split("|") if x]


def resources() -> list[dict]:
    """The new food resources for jsons/TileResources.json."""
    out = []
    for r in NEW:
        imp, base, better = KIND[r["kind"]]
        out.append({"name": r["food"], "resourceType": "Luxury", "terrainsCanBeFoundOn": split(r["terrains"]), **base,
                    "improvement": imp, "improvementStats": better,
                    "civilopediaText": [{"text": pedia(r)[0]}]})
    return out


def pedia(r: dict) -> tuple[str, str]:
    import gen_paths
    p = gen_paths.KEY[r["key"]]
    home, second = REGION[r["home"]], REGION[r["second"]]
    imp = KIND[r["kind"]][0]
    return (f"{r['food']} ({r['chinese']}), the basic food of the {p['name'].lower()} path's Gu: {r['note']}. It grows in "
            f"{home[0]}, and some in {second[0]}; a {imp} works it. A clan gets it from each worked tile (1), the "
            f"{p['name']} Path branch ({BRANCH_FOOD}) and its {p['name']} Insight ({INSIGHT_FOOD}), each {p['name']} Hall "
            f"({HALL_FOOD}) and the {p['name']} Path Lore ({LORE_FOOD}). It gives no happiness.",
            f"{r['food_id']} ({r['chinese']}), makanan dasar Gu jalur {p['name_id']}: {r['note_id']}. Tumbuh di "
            f"{home[1]}, sebagian di {second[1]}; dikerjakan dengan {imp}. Klan mendapatkannya dari tiap petak yang dikerjakan "
            f"(1), cabang Jalur {p['name_id']} ({BRANCH_FOOD}) dan Wawasan {p['name_id']}-nya ({INSIGHT_FOOD}), tiap Aula "
            f"Jalur {p['name_id']} ({HALL_FOOD}) dan Ilmu Jalur {p['name_id']} ({LORE_FOOD}). Tidak memberi kebahagiaan.")


def translations() -> list[tuple[str, str]]:
    return [x for r in NEW for x in ((r["food"], r["food_id"]), pedia(r))]
