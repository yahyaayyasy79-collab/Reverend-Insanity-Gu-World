#!/usr/bin/env python3
"""Build the mod's hand-made maps: Qing Mao Mountain (maps/Qing Mao Mountain), the canon setting of Slice 1, and
the Five Regions (maps/Five Regions), the world of the immortal arc (see five_regions() below).

The random map generator places terrain by latitude and cannot put three clan villages on one mountain, so the mod
ships a map (the user's D5, docs/CANON_OVERHAUL.md part D; canon from the geography research):

* Qing Mao Mountain (青茅山) in the middle, ringed by spear-bamboo forest and lower hills: the Bai village by the
  back-slope waterfall and its deep pool (north), Gu Yue halfway up (centre), Xiong on the front slope (south)
  (R V1c65). At least three or four spirit springs on a famous mountain (R V2c183): one under each village and three
  contested ones on the slopes.
* A lightning-wolf nest low on the mountain (R V1c31); a tributary of the Yellow Dragon River at its foot, with the
  foothill mortal villages beside it (R V1c117, V1c124); the Jia village on its own mountain (R V1c45); the hairy men
  in the western rainforest; a rotting swamp to the south-east (R V2c8-9).
* The Wu clan's Wu Yi Mountain to the east, by its river (R V5c300; the Wu are a Southern Border super clan drawn
  closer to make a four-clan game).

The design below is data; Unciv's own classes write the file (tools/autoplay/MakeMap.java), so it loads exactly as a
map saved by the game's editor would. `--check` rebuilds it in a temporary folder and compares.

Usage: tools/make_map.py [--check] [--quiet]           (builds or checks both maps)
"""
from __future__ import annotations

import argparse
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import REF_DIR, REPO_ROOT, ref_tag  # noqa: E402

W, H = 40, 26
MOD_NAME = "Reverend Insanity Gu World"
MAPS_DIR = REPO_ROOT / "maps"
JAVA = Path(__file__).resolve().parent / "autoplay" / "MakeMap.java"

QING_MAO = (18, 12)
STARTS = {  # (column, row) with row 0 at the top (north)
    "Bai Clan": (19, 4), "Gu Yue Clan": (18, 12), "Xiong Clan": (17, 20), "Wu Clan": (33, 19),
    "Foothill Villages": (10, 23), "Jia Clan": (32, 5), "Hairy Man Tribe": (4, 12),
}
SPRINGS = [(18, 4), (19, 12), (16, 20), (24, 11), (12, 15), (22, 17), (34, 19), (32, 18), (35, 15), (31, 5)]
RESOURCES = {
    "Moon Orchid": [(17, 11), (19, 13), (13, 8), (21, 6)],
    "Wild Boar": [(14, 18), (20, 21), (11, 13), (28, 18), (31, 10), (5, 8), (25, 6)],
    "Jade": [(15, 11), (21, 15), (26, 9), (36, 14), (9, 10)],
    "Furs": [(2, 3), (37, 3), (5, 24), (38, 24)],
}
RUINS = [(10, 6), (25, 3), (6, 20), (29, 15), (22, 23), (14, 2)]
LAIRS = [(8, 17), (27, 7)]
LAKE = [(21, 3), (22, 3), (22, 4), (21, 2)]            # the deep pool under the back-slope waterfall
RIDGE = [(14, 9), (15, 8), (17, 8), (18, 8), (20, 8), (21, 9), (23, 10), (13, 10)]   # Qing Mao's peaks
WU_PEAKS = [(35, 11), (36, 12), (37, 16), (36, 17)]
EDGE_PEAKS = [(0, 0), (1, 0), (39, 0), (39, 1), (0, 25), (39, 25), (19, 0), (38, 9), (0, 16)]


def dist(a, b):
    return math.hypot(a[0] - b[0], (a[1] - b[1]) * 1.15)


def design() -> list[str]:
    rng = random.Random(7)
    tiles = {}
    for c in range(W):
        for r in range(H):
            d = dist((c, r), QING_MAO)
            base, feats = "Grassland", []
            if c <= 7 and 7 <= r <= 18:
                feats = ["Jungle"] if rng.random() < 0.75 else []                # the hairy men's rainforest
            elif 25 <= c <= 30 and r >= 22:
                feats = ["Marsh"] if rng.random() < 0.7 else []                  # the rotting swamp
            elif d < 7.5:
                feats = ["Hill"] + (["Forest"] if rng.random() < 0.45 else [])   # Qing Mao's slopes, spear bamboo
            elif d < 10:
                feats = ["Forest"] if rng.random() < 0.6 else (["Hill"] if rng.random() < 0.3 else [])
            elif dist((c, r), (34, 15)) < 4.5:
                feats = ["Hill"] + (["Forest"] if rng.random() < 0.3 else [])    # Wu Yi Mountain
            else:
                base = "Plains" if rng.random() < 0.45 else "Grassland"
                feats = ["Forest"] if rng.random() < 0.35 else (["Hill"] if rng.random() < 0.12 else [])
            if r <= 1 or r >= 24 and c <= 3:
                base = "Tundra" if rng.random() < 0.5 else base
            tiles[(c, r)] = [base, feats, "-", 0, "-", ""]
    for p in RIDGE + WU_PEAKS + EDGE_PEAKS:
        tiles[p] = ["Mountain", [], "-", 0, "-", ""]
    for p in LAKE:
        tiles[p] = ["Lakes", [], "-", 0, "-", ""]
    for name, (c, r) in STARTS.items():                                          # open, buildable village sites
        t = tiles[(c, r)]
        t[0] = "Plains" if name in ("Foothill Villages", "Wu Clan") else "Grassland"
        t[1] = ["Hill"] if name in ("Gu Yue Clan", "Xiong Clan", "Jia Clan", "Bai Clan") else []
    for p in SPRINGS:
        t = tiles[p]; t[0] = "Grassland"; t[1] = ["Hill"] if "Hill" in t[1] else []; t[2], t[3] = "Spirit Spring", 1
    for res, spots in RESOURCES.items():
        for p in spots:
            t = tiles[p]
            if res == "Jade":
                t[0], t[1] = "Grassland", ["Hill"]
            elif res == "Wild Boar":
                t[0], t[1] = "Grassland", ["Forest"]
            elif res == "Furs":
                t[0], t[1] = "Tundra", ["Forest"]
            else:
                t[0], t[1] = "Grassland", []
            t[2], t[3] = res, (0 if res == "Furs" else 2)
    for p in RUINS:
        tiles[p][4] = "Inheritance Site"
    for p in LAIRS:
        t = tiles[p]; t[0], t[1], t[4] = "Grassland", ["Forest"], "Beast Lair"
    # the Yellow Dragon tributary along the foot of the mountain, and the Wu river joining it from the north-east
    for c in range(2, 37):
        tiles[(c, 22)][5] += "br"
    for r in range(14, 22):
        tiles[(32, r)][5] += "r"
    lines = [f"size\t{W}\t{H}"]
    for (c, r), (base, feats, res, amount, imp, riv) in sorted(tiles.items()):
        col, row = c - W // 2, (H - 1 - r) - H // 2
        lines.append("\t".join(["tile", str(col), str(row), base, "+".join(feats) or "-", res, str(amount), imp,
                                riv or "-"]))
    for name, (c, r) in STARTS.items():
        lines.append(f"start\t{c - W // 2}\t{(H - 1 - r) - H // 2}\t{name}")
    return lines


# ---------------- the Five Regions (MOD_SPEC_2 T3; the user, 2026-11-01: "sempurnakan") ----------------
# Canon geography: the Central Continent in the middle, the Northern Plains, the Southern Border, the Eastern Sea and
# the Western Desert around it, each sealed by its region wall (界壁, R V5/22, V4/61, V4/279), which only immortals
# cross. Nations start in their canon regions (B1, B2); the secret realms stand in theirs (volume settings: V2 Southern
# Border, V3 Northern Plains; the River of Time and Lang Ya placed in the centre, ADAPTED).
FW, FH = 60, 40
WALL_OF = {"south": "Miasma Wall", "north": "Licorice Wall", "east": "Azure Water Wall", "west": "Raging Flame Wall",
           "central": "Sage Wall"}
FIVE_STARTS = {  # nation: (region, target column, target row)
    "Gu Yue Clan": ("south", 25, 33), "Bai Clan": ("south", 29, 31), "Xiong Clan": ("south", 23, 36),
    "Wu Clan": ("south", 36, 34), "Hairy Man Tribe": ("south", 16, 35), "Foothill Villages": ("south", 31, 37),
    "Jia Clan": ("south", 41, 37), "Huang Jin Family": ("north", 30, 3), "Zombie Alliance": ("east", 52, 20),
    "Merman Imperial Court": ("east", 55, 11), "Fang Clan": ("west", 6, 20), "Heavenly Court": ("central", 30, 18),
    "Lang Ya Sect": ("north", 46, 8), "Spirit Affinity House": ("central", 37, 15),
    "Combat Immortal Sect": ("central", 30, 26),
    # Phase D: minor clans in every region (faction research R; Lang Ya is a Northern Plains sect, R ch461/464)
    "Man Tribe": ("north", 20, 8), "Ge Tribe": ("north", 11, 6), "Lan Clan": ("west", 5, 11),
    "Xiao Clan": ("west", 12, 15), "Mo Clan": ("west", 6, 29), "Song Clan": ("east", 50, 29),
    "Xia Clan": ("east", 57, 24), "Immortal Crane Sect": ("central", 21, 16),
    # Regions II: the other seven great sects (R V6c358): Ancient Soul in the far west of the continent (V4c79), Myriad
    # Dragon Dock beside the Immortal Crane Sect's lands (V4c48); the Wan clan's Gao Song Oasis in the desert (V6c281).
    # The sects sit on the region's rim: placed around the Court they held it to 3.4 cities (5.1 before) and halved
    # its immortals (autoplay 8 x 450, 2026-11-08); the Combat Immortal Sect moved two tiles south for the same reason
    "Heavenly Lotus Sect": ("central", 24, 26), "Spirit Butterfly Valley": ("central", 41, 13),
    "Ancient Soul Sect": ("central", 19, 24), "Heaven's Envy Tower": ("central", 19, 13),
    "Wind Cloud Manor": ("central", 40, 19), "Black Heaven Temple": ("central", 36, 25),
    "Myriad Dragon Dock": ("central", 22, 20), "Wan Clan": ("west", 13, 25),
    # reference audit Layer 4: the variant humans (R V4c215 Yu Sheng City; V3c132 the Great Snow Mountain; V4c13 Ink Man
    # City; V3c4 the rockmen south of the Hu Immortal blessed land)
    # the snowmen on the far north-west tundra: 7 tiles from the Huang Jin capital they fell by T84-157 in 10 of 16
    # autoplay games, shield or no shield (8 x 450, 6edf4a8 and 997e679); the canon places the Great Snow Mountain in a
    # blessed land, not beside the golden tribes
    "Feathermen": ("west", 11, 21), "Snowmen": ("north", 6, 2), "Inkmen": ("north", 52, 5),
    "Rockmen": ("south", 12, 31),
    # Layer 7: more super forces. At 14-15 tiles from the Huang Jin capital the Ma and Liu tribes fell in 2 and 3 of 8
    # autoplay games and fed a Huang Jin snowball (4 of 8 wins); the Tang clan 6 tiles from the Fang capital cut its
    # cities from 2.1 to 1.6 at T300. So the golden tribes sit 20+ tiles from the Huang Jin, the Tang in the desert's
    # far south-west.
    "Tie Clan": ("south", 47, 36), "Tang Clan": ("west", 1, 34), "Shen Clan": ("east", 57, 33),
    "Ma Tribe": ("north", 1, 1), "Liu Tribe": ("north", 50, 0), "Dong Fang Tribe": ("north", 57, 2)}
FIVE_REALMS = {  # realm: (region, column, row)
    "Hu Immortal Blessed Land": ("south", 20, 31), "Dang Hun Mountain": ("south", 19, 33), "Tian Ti Mountain": ("south", 33, 30),
    "Luo Po Valley": ("south", 44, 33), "Door of Life and Death": ("south", 12, 37), "Imperial Court Blessed Land": ("north", 24, 4),
    "Crazed Demon Cave": ("north", 38, 2), "Book Mountain": ("north", 16, 5), "Reverse Flow River": ("north", 44, 5),
    "Dragon Whale Paradise": ("east", 56, 28), "Lang Ya Blessed Land": ("north", 40, 9), "River of Time": ("central", 35, 21)}


# Each region's riches beyond the start rings (autoplay 6 × 400: with nothing but the start ring's spring, 42 of 48
# clans spent 20+ turns in the red). Counts bring every region near Qing Mao Mountain's density (a spirit spring per
# ~100 land tiles, jade per ~200); the Eastern Sea has 100 land tiles, the Southern Border is Qing Mao's own country.
RICHES = {  # region: [(resource or improvement, count)]
    # the user, 2026-11-09 ("sebarkanlah sumber daya itu ke seluruh 5 benua"): the springs, jade and sites are spread
    # evenly; the Gu foods are placed by path (food_spots below), each in its home region and one more
    "south": [("Spirit Spring", 4), ("Jade", 2), ("Furs", 1), ("Inheritance Site", 2), ("Beast Lair", 2)],
    "central": [("Spirit Spring", 4), ("Jade", 2), ("Inheritance Site", 2), ("Beast Lair", 1), ("Demonic Den", 2)],
    "north": [("Spirit Spring", 4), ("Jade", 2), ("Furs", 3), ("Inheritance Site", 2), ("Beast Lair", 1),
              ("Demonic Den", 2)],
    "west": [("Spirit Spring", 4), ("Jade", 2), ("Inheritance Site", 2), ("Beast Lair", 1), ("Demonic Den", 2)],
    "east": [("Spirit Spring", 2), ("Jade", 1), ("Inheritance Site", 1), ("Demonic Den", 1)],
}
# every path's basic food: two tiles in its home region, one in its second (data/path_foods.csv); Wine is brewed
FOOD_HOME, FOOD_SECOND = 2, 1


def food_spots() -> dict:
    """{region: [(food, count)]} from data/path_foods.csv, the brewed Wine left out; each region places its own foods
    before the ones it holds as a second region, so a crowded region keeps room for its home foods."""
    import csv
    out, second = {}, {}
    with open(REPO_ROOT / "data" / "path_foods.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["food"] == "Wine":
                continue
            out.setdefault(r["home"], []).append((r["food"], FOOD_HOME))
            second.setdefault(r["second"], []).append((r["food"], FOOD_SECOND))
    return {g: out.get(g, []) + second.get(g, []) for g in set(out) | set(second)}


def food_regions() -> dict:
    """{food: (home, second)} from data/path_foods.csv."""
    import csv
    with open(REPO_ROOT / "data" / "path_foods.csv", newline="", encoding="utf-8") as f:
        return {r["food"]: (r["home"], r["second"]) for r in csv.DictReader(f)}


# each major's own foods beside its capital: the four Southern Border clans their signature paths', the arc majors
# two of their region's (the Court heaven and emotion, the Huang Jin qi and enslavement, the Fang wisdom and blade, the
# Zombie Alliance water and lightning)
START_FOODS = {"Gu Yue Clan": ("Moon Orchid", "Wild Boar"), "Bai Clan": ("Dragonfish", "Lingzhi"),
               "Xiong Clan": ("Wild Boar", "Python Blood"), "Wu Clan": ("Wind Knot Grass", "Arrow Bamboo"),
               "Heavenly Court": ("Brocade Cloud", "Taize Flower"), "Huang Jin Family": ("Heavy Gold", "Wolf Meat"),
               "Fang Clan": ("Splendid Overlord Flower", "Old Blades"), "Zombie Alliance": ("Dragonfish", "Lightning Eel")}

IMPROVEMENT_SITES = {"Inheritance Site", "Beast Lair", "Demonic Den"}
# Fair starts (autoplay, Layer 9: the scatter put 10-11 riches within 3.5 tiles of the Court, the Fang and the Zombie
# Alliance, 5 and a beast lair beside the Wu, who fell in 6 of 8 games): every major gets the same kit (a spirit spring,
# jade, its two foods at one copy each, an inheritance site), nothing else lands within MAJOR_CLEAR tiles of a capital,
# at most MAJOR_RING_CAP scattered riches lie within MAJOR_RING tiles, and no barbarian camp within CAMP_CLEAR
MAJOR_CLEAR, MAJOR_RING, MAJOR_RING_CAP, CAMP_CLEAR = 3.5, 6.0, 4, 6.0
SLICE1_FOODS = ("Moon Orchid", "Wild Boar")   # strategic: one tile holds two copies
SEA_RING_CAP = 8   # the Eastern Sea's few islands lie mostly near the Zombie Alliance; the canon sea is the richest


# the tile a resource needs: hills for jade and minerals, forest for beasts of the wood, open land for the rest
_FOOD_KIND = None


def food_kind(res: str) -> str:
    global _FOOD_KIND
    if _FOOD_KIND is None:
        import csv
        with open(REPO_ROOT / "data" / "path_foods.csv", newline="", encoding="utf-8") as f:
            _FOOD_KIND = {r["food"]: (r["kind"], r["terrains"]) for r in csv.DictReader(f)}
    return _FOOD_KIND.get(res, ("", ""))[0]


def fit_tile(t, res):
    """Make the tile one the resource can stand on and its improvement can work."""
    kind = food_kind(res)
    if res == "Jade" or kind == "mineral":
        t[1] = ["Hill"]
    elif res == "Wild Boar":
        t[1] = ["Forest"]
    elif res == "Spirit Spring":
        t[1] = [f for f in t[1] if f == "Hill"]
    elif res in ("Lingzhi", "Dark Fragrant Mushroom", "Arrow Bamboo", "Flying Bear Flesh"):
        t[1] = ["Forest"]
    elif res in ("Python Blood",):
        t[1] = ["Jungle"] if t[0] in ("Grassland", "Plains") else ["Forest"]
    elif kind == "water" or res in ("Taize Flower", "White Lotus Silkworm", "Rotten Frozen Mud"):
        t[1] = ["Marsh"] if t[0] in ("Grassland",) else []
    else:
        t[1] = []
    if t[0] == "Desert" and res not in ("Jade",) and kind not in ("mineral",) and res not in (
            "Sand Gull Earth", "Splendid Overlord Flower", "Battlefield Bones", "Marsh Mud", "Old Scrolls"):
        t[0] = "Plains"
    if t[0] == "Tundra" and res not in ("Dancing Snow", "Rotten Frozen Mud", "Wild Deer", "Wolf Meat", "Hound Dung",
                                         "North Ban Licorice", "Flying Bear Flesh", "Battlefield Bones", "Furs"):
        t[0] = "Plains"


def scatter_riches(tiles, reg, wall, taken, starts):
    rng = random.Random(23)
    placed = list(taken)
    cells = sorted(tiles)
    rng.shuffle(cells)
    wanted = {g: list(RICHES.get(g, [])) + food_spots().get(g, []) for g in set(RICHES) | set(food_spots())}
    capitals = [starts[m] for m in START_FOODS]
    ring = {m: 0 for m in capitals}
    cap = {m: SEA_RING_CAP if reg[m] == "east" else MAJOR_RING_CAP for m in capitals}
    def place(region, what, count, tight=False):
        for q in cells:
            if count == 0:
                break
            t = tiles[q]
            if reg[q] != region or q in wall or t[2] != "-" or t[4] != "-" or t[6] != "-" \
                    or t[0] in ("Ocean", "Coast", "Mountain", "Lakes"):
                continue
            gap = SEA_GAP if region == "east" or tight else MIN_GAP
            if any(math.hypot(q[0] - a, q[1] - b) < gap for a, b in placed):
                continue
            near = [m for m in capitals if math.hypot(q[0] - m[0], q[1] - m[1]) <= MAJOR_RING]
            if any(math.hypot(q[0] - m[0], q[1] - m[1]) <= MAJOR_CLEAR for m in near) \
                    or any(ring[m] >= cap[m] for m in near) \
                    or (what in ("Beast Lair", "Demonic Den") and any(
                        math.hypot(q[0] - m[0], q[1] - m[1]) <= CAMP_CLEAR for m in near)):
                continue
            if food_kind(what) == "sea" and region == "east" and not near_sea(tiles, q):
                continue   # in the sea region a sea creature lives on a shore; elsewhere in rivers and marshes
            for m in near:
                ring[m] += 1
            if what == "Furs" and region == "north":
                t[0], t[1] = "Tundra", ["Forest"]
            elif what == "Furs":
                t[1] = ["Jungle"]
            elif what in ("Beast Lair", "Demonic Den"):
                t[1] = ["Jungle"] if "Jungle" in t[1] else ["Forest"]
            elif what not in IMPROVEMENT_SITES:
                fit_tile(t, what)
            if t[0] == "Desert" and what in ("Spirit Spring", "Beast Lair", "Demonic Den", "Furs"):
                t[0] = "Plains"
            if t[0] == "Tundra" and what in ("Spirit Spring",):
                t[0] = "Plains"
            if what in IMPROVEMENT_SITES:
                t[4] = what
            else:
                t[2], t[3] = what, (0 if what == "Furs" or food_kind(what) else 1 if what == "Spirit Spring" else 2)
            placed.append(q)
            count -= 1
        return count

    homes = food_regions()
    for region, wants in sorted(wanted.items()):
        for what, count in wants:
            count = place(region, what, count)
            if count and what in homes:   # a food with no room left in one of its regions spills into the other
                other = homes[what][1] if region == homes[what][0] else homes[what][0]
                count = place(other, what, count)
                count = place(other, what, place(region, what, count, tight=True), tight=True)   # crowded: only not touching
            if count:
                print(f"[make_map] {region}: {count} {what} could not be placed", file=sys.stderr)


MIN_GAP = 2.0   # tiles between two riches; 2.5 left no room for the foods in the Eastern Sea's islands
SEA_GAP = 1.5   # on the Eastern Sea's islands two riches only must not touch


def near_sea(tiles, q):
    """A sea creature lives on a shore tile."""
    return any(tiles.get((q[0] + dc, q[1] + dr), ["Ocean"])[0] in ("Coast", "Ocean")
               for dc in (-1, 0, 1) for dr in (-1, 0, 1) if (dc, dr) != (0, 0))


def region_of(c, r):
    dx, dy = (c - (FW - 1) / 2) / (FW / 2), (r - (FH - 1) / 2) / (FH / 2)
    if max(abs(dx), abs(dy)) < 0.42:
        return "central"
    if abs(dy) * 1.2 > abs(dx):
        return "north" if dy < 0 else "south"
    return "east" if dx > 0 else "west"


def five_regions() -> list[str]:
    import csv
    rng = random.Random(11)
    with open(REPO_ROOT / "data" / "secret_realms.csv", newline="", encoding="utf-8") as f:
        realm_base = {row["name"]: row["turns_into"] for row in csv.DictReader(f)}
    reg = {(c, r): region_of(c, r) for c in range(FW) for r in range(FH)}
    wall = {}
    for (c, r), g in reg.items():
        others = {reg.get((c + dc, r + dr), g) for dc in (-1, 0, 1) for dr in (-1, 0, 1)} - {g}
        if others:
            outer = g if g != "central" else sorted(others)[0]
            wall[(c, r)] = WALL_OF[outer]
    land = {}
    for (c, r), g in reg.items():
        if g == "east":   # the Eastern Sea: water with islands
            # autoplay: on one small island the Zombie Alliance never grew past one city
            isl = any(math.hypot(c - x, (r - y) * 1.2) < rr
                      for x, y, rr in ((52, 20, 4.6), (55, 11, 2.6), (50, 29, 3.4), (56, 33, 2.4), (57, 24, 2.0)))
            land[(c, r)] = isl
        else:
            land[(c, r)] = True
    tiles = {}
    for (c, r), g in reg.items():
        if (c, r) in wall:
            tiles[(c, r)] = [wall[(c, r)], [], "-", 0, "-", "", "-"]
            continue
        if not land[(c, r)]:
            near = any(land.get((c + dc, r + dr)) and reg.get((c + dc, r + dr)) == "east" for dc in (-1, 0, 1) for dr in (-1, 0, 1))
            tiles[(c, r)] = ["Coast" if near else "Ocean", [], "-", 0, "-", "", "-"]
            continue
        x = rng.random()
        if g == "south":
            base, feats = ("Grassland" if x < 0.6 else "Plains"), (["Jungle"] if x < 0.25 else ["Forest"] if x < 0.5 else ["Hill"] if x < 0.68 else ["Hill", "Forest"] if x < 0.75 else [])
            if rng.random() < 0.04:
                base, feats = "Mountain", []
        elif g == "north":
            base = "Tundra" if r < 3 else ("Grassland" if x < 0.55 else "Plains")
            feats = ["Forest"] if rng.random() < 0.1 else (["Hill"] if rng.random() < 0.06 else [])
        elif g == "west":
            base = "Desert" if x < 0.78 else "Plains"
            feats = ["Hill"] if rng.random() < 0.14 else []
            if rng.random() < 0.03:
                base, feats = "Mountain", []
        elif g == "east":
            base, feats = ("Grassland" if x < 0.6 else "Plains"), (["Forest"] if rng.random() < 0.3 else [])
        else:
            base = "Grassland" if x < 0.55 else "Plains"
            feats = ["Forest"] if rng.random() < 0.3 else (["Hill"] if rng.random() < 0.15 else [])
            if rng.random() < 0.02:
                base, feats = "Lakes", []
        tiles[(c, r)] = [base, feats, "-", 0, "-", "", "-"]

    def nearest(region, c0, r0, taken):
        best = None
        for (c, r), t in tiles.items():
            if reg[(c, r)] != region or (c, r) in wall or t[0] in ("Ocean", "Coast", "Mountain", "Lakes") or (c, r) in taken:
                continue
            if any(math.hypot(c - a, r - b) < 3 for a, b in taken):
                continue
            d = math.hypot(c - c0, r - r0)
            if best is None or d < best[0]:
                best = (d, (c, r))
        return best[1]

    taken, starts = [], {}
    for name, (g, c0, r0) in FIVE_STARTS.items():
        pos = nearest(g, c0, r0, taken)
        taken.append(pos)
        starts[name] = pos
        t = tiles[pos]
        t[0] = "Plains" if g in ("north", "west") else "Grassland"
        t[1] = []
    for name, (g, c0, r0) in FIVE_REALMS.items():
        if g == "east":
            pos = min(((c, r) for (c, r), t in tiles.items() if t[0] == "Ocean"
                       and all(tiles.get((c + dc, r + dr), ["Ocean"])[0] in ("Ocean", "Coast") for dc in (-1, 0, 1) for dr in (-1, 0, 1))),
                      key=lambda q: math.hypot(q[0] - c0, q[1] - r0))
        else:
            pos = nearest(g, c0, r0, taken)
        taken.append(pos)
        tiles[pos] = [realm_base[name], [], "-", 0, "-", "", name]
    # the clans' spirit springs and Gu foods, near the Southern Border villages and across the other regions
    # the Fang clan's oasis: on bare desert the AI's settler never founded a city (autoplay, 6 of 6 games)
    # (Regions II: the Wan clan's Gao Song Oasis likewise)
    for oasis in ("Fang Clan", "Wan Clan"):
        fc, fr = starts[oasis]
        for (c, r), t in tiles.items():
            d = math.hypot(c - fc, r - fr)
            if 0 < d <= 2.5 and t[0] == "Desert" and (c, r) not in wall:
                t[0], t[1] = ("Plains" if (c + r) % 3 else "Grassland"), []
            elif 2.5 < d <= 3.5 and t[0] == "Desert" and (c + 2 * r) % 4 == 0 and (c, r) not in wall:
                t[1] = ["Oasis"]
    for name in ("Gu Yue Clan", "Bai Clan", "Xiong Clan", "Wu Clan", "Heavenly Court", "Huang Jin Family", "Fang Clan"):
        c0, r0 = starts[name]
        fa, fb = START_FOODS[name]
        # two copies of the first food (its signature path's: the Gu Yue emblem eats Moon Orchid), one of the second
        two = ((-1, 2, fa, 2),) if fa in SLICE1_FOODS else ((-1, 2, fa, 1), (1, -2, fa, 1))
        for dc, dr, res, amt in ((1, 1, "Spirit Spring", 1), *two, (2, -1, fb, 1), (-2, 0, "Jade", 2)):
            q = (c0 + dc, r0 + dr)
            if q in tiles and q not in wall and q not in taken and tiles[q][0] not in ("Ocean", "Coast", "Mountain", "Lakes"):
                t = tiles[q]
                t[2], t[3] = res, amt
                fit_tile(t, res)
    za = starts["Zombie Alliance"]
    for q, res in (((za[0] + 1, za[1]), "Spirit Spring"), ((za[0], za[1] + 1), "Spirit Spring"),
                   ((za[0] - 1, za[1]), START_FOODS["Zombie Alliance"][0]), ((za[0] - 1, za[1] + 1), START_FOODS["Zombie Alliance"][0]),
                   ((za[0], za[1] - 1), START_FOODS["Zombie Alliance"][1])):
        if q in tiles and tiles[q][0] not in ("Ocean", "Coast") and q not in taken:
            tiles[q][2], tiles[q][3] = res, 1
            fit_tile(tiles[q], res)
    for name in START_FOODS:   # one inheritance site three tiles out, the same for every major
        c0, r0 = starts[name]
        for dc, dr in ((0, -3), (3, 0), (-3, 0), (0, 3), (2, -2), (-2, 2), (2, 2), (-2, -2)):
            q = (c0 + dc, r0 + dr)
            t = tiles.get(q)
            if t and q not in wall and q not in taken and t[0] not in ("Ocean", "Coast", "Mountain", "Lakes") \
                    and t[2] == "-" and t[4] == "-" and t[6] == "-":
                t[4] = "Inheritance Site"
                if t[0] == "Desert":
                    t[0] = "Plains"
                break
        else:
            print(f"[make_map] {name}: no tile for its inheritance site", file=sys.stderr)
    scatter_riches(tiles, reg, wall, taken, starts)
    # the Yellow Dragon River along the Southern Border, north of the villages (Qing Mao Mountain has its tributary)
    for c in range(FW):
        if reg[(c, 29)] == "south" and (c, 29) not in wall and (c, 30) not in wall and tiles[(c, 29)][0] not in ("Mountain",):
            tiles[(c, 29)][5] += "b"
    lines = [f"size\t{FW}\t{FH}"]
    for (c, r), (base, feats, res, amount, imp, riv, wonder) in sorted(tiles.items()):
        col, row = c - FW // 2, (FH - 1 - r) - FH // 2
        lines.append("\t".join(["tile", str(col), str(row), base, "+".join(feats) or "-", res, str(amount), imp,
                                riv or "-", wonder]))
    for name, (c, r) in starts.items():
        lines.append(f"start\t{c - FW // 2}\t{(FH - 1 - r) - FH // 2}\t{name}")
    return lines


MAPS = {"Qing Mao Mountain": design, "Five Regions": five_regions}


def build_all(out_dir: Path, quiet: bool) -> None:
    for name, make in MAPS.items():
        build(out_dir / name, quiet, make(), name)


def build(out: Path, quiet: bool, lines: list[str], name: str) -> None:
    jar = REF_DIR / f"Unciv-{ref_tag()}.jar"
    if not (jar.exists() and shutil.which("java") and shutil.which("javac")):
        sys.exit(f"make_map needs java, javac and {jar} (tools/fetch_ref.sh)")
    with tempfile.TemporaryDirectory(prefix="make_map-") as tmp:
        work = Path(tmp)
        classes = work / "classes"
        classes.mkdir()
        r = subprocess.run(["javac", "-nowarn", "-encoding", "UTF-8", "-cp", str(jar), "-d", str(classes), str(JAVA)],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("javac failed:\n" + r.stderr)
        shutil.copytree(REPO_ROOT / "jsons", work / "mods" / MOD_NAME / "jsons")
        spec = work / "spec.txt"
        spec.write_text("\n".join(lines) + "\n", encoding="utf-8")
        out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["java", "-Dfile.encoding=UTF-8", "-cp", f"{jar}{':'}{classes}", "MakeMap", str(work),
                            MOD_NAME, str(spec), str(out), name], cwd=work, capture_output=True, text=True, timeout=300)
        if r.returncode:
            sys.exit("MakeMap failed:\n" + "\n".join((r.stderr or r.stdout).splitlines()[-25:]))
        if not quiet:
            print(r.stdout.strip())


def decoded(path: Path):
    """The map as JSON: the game zips it (base64 of gzip, whose header carries a timestamp)."""
    import base64, gzip, json
    raw = path.read_text(encoding="utf-8").strip()
    try:
        raw = gzip.decompress(base64.b64decode(raw)).decode("utf-8")
    except Exception:  # noqa: BLE001 - an unzipped map is plain JSON
        pass
    return json.loads(raw)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if maps/ is out of date")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            build_all(Path(tmp), True)
            stale = [n for n in MAPS if not (MAPS_DIR / n).exists() or decoded(Path(tmp) / n) != decoded(MAPS_DIR / n)]
            if stale:
                print(f"[make_map] maps/ is out of date ({', '.join(stale)}); run tools/make_map.py")
                return 1
        return 0
    build_all(MAPS_DIR, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
