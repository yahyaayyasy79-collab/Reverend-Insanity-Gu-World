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
    "Combat Immortal Sect": ("central", 30, 24),
    # Phase D: minor clans in every region (faction research R; Lang Ya is a Northern Plains sect, R ch461/464)
    "Man Tribe": ("north", 20, 8), "Ge Tribe": ("north", 11, 6), "Lan Clan": ("west", 5, 11),
    "Xiao Clan": ("west", 12, 15), "Mo Clan": ("west", 6, 29), "Song Clan": ("east", 50, 29),
    "Xia Clan": ("east", 57, 24), "Immortal Crane Sect": ("central", 21, 16)}
FIVE_REALMS = {  # realm: (region, column, row)
    "Hu Immortal Blessed Land": ("south", 20, 31), "Dang Hun Mountain": ("south", 19, 33), "Tian Ti Mountain": ("south", 33, 30),
    "Luo Po Valley": ("south", 44, 33), "Door of Life and Death": ("south", 12, 37), "Imperial Court Blessed Land": ("north", 24, 4),
    "Crazed Demon Cave": ("north", 38, 2), "Book Mountain": ("north", 16, 5), "Reverse Flow River": ("north", 44, 5),
    "Dragon Whale Paradise": ("east", 56, 28), "Lang Ya Blessed Land": ("north", 40, 9), "River of Time": ("central", 35, 21)}


# Each region's riches beyond the start rings (autoplay 6 × 400: with nothing but the start ring's spring, 42 of 48
# clans spent 20+ turns in the red). Counts bring every region near Qing Mao Mountain's density (a spirit spring per
# ~100 land tiles, jade per ~200); the Eastern Sea has 100 land tiles, the Southern Border is Qing Mao's own country.
RICHES = {  # region: [(resource or improvement, count)]
    "south": [("Spirit Spring", 6), ("Jade", 3), ("Wild Boar", 4), ("Moon Orchid", 2), ("Furs", 2),
              ("Inheritance Site", 3), ("Beast Lair", 2)],
    # Phase D (the user: conflict in every region): demonic dens where one clan stood alone
    "central": [("Spirit Spring", 4), ("Jade", 2), ("Wild Boar", 2), ("Moon Orchid", 1), ("Inheritance Site", 2),
                ("Beast Lair", 1), ("Demonic Den", 2)],
    "north": [("Spirit Spring", 5), ("Jade", 3), ("Wild Boar", 3), ("Furs", 4), ("Inheritance Site", 2),
              ("Beast Lair", 1), ("Demonic Den", 2)],
    "west": [("Spirit Spring", 3), ("Jade", 3), ("Wild Boar", 1), ("Inheritance Site", 2), ("Beast Lair", 1),
             ("Demonic Den", 2)],
    "east": [("Spirit Spring", 1), ("Jade", 1), ("Wild Boar", 2), ("Moon Orchid", 1), ("Inheritance Site", 1),
             ("Demonic Den", 1)],
}
IMPROVEMENT_SITES = {"Inheritance Site", "Beast Lair", "Demonic Den"}


def scatter_riches(tiles, reg, wall, taken, starts):
    rng = random.Random(23)
    placed = list(taken)
    cells = sorted(tiles)
    rng.shuffle(cells)
    for region, wants in RICHES.items():
        for what, count in wants:
            for q in cells:
                if count == 0:
                    break
                t = tiles[q]
                if reg[q] != region or q in wall or t[2] != "-" or t[4] != "-" or t[6] != "-" \
                        or t[0] in ("Ocean", "Coast", "Mountain", "Lakes"):
                    continue
                if any(math.hypot(q[0] - a, q[1] - b) < 2.5 for a, b in placed):
                    continue
                if what == "Furs" and region == "north":
                    t[0], t[1] = "Tundra", ["Forest"]
                elif what == "Furs":
                    t[1] = ["Jungle"]
                elif what == "Jade":
                    t[1] = ["Hill"]
                elif what in ("Wild Boar", "Beast Lair", "Demonic Den"):
                    t[1] = ["Jungle"] if "Jungle" in t[1] else ["Forest"]
                elif what == "Spirit Spring":
                    t[1] = [f for f in t[1] if f == "Hill"]
                elif what == "Moon Orchid":
                    t[1] = []
                if t[0] == "Desert" and what not in ("Jade", "Inheritance Site"):
                    t[0] = "Plains"
                if t[0] == "Tundra" and what in ("Spirit Spring", "Moon Orchid"):
                    t[0] = "Plains"
                if what in IMPROVEMENT_SITES:
                    t[4] = what
                else:
                    t[2], t[3] = what, (0 if what == "Furs" else 1 if what == "Spirit Spring" else 2)
                placed.append(q)
                count -= 1


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
    fc, fr = starts["Fang Clan"]
    for (c, r), t in tiles.items():
        d = math.hypot(c - fc, r - fr)
        if 0 < d <= 2.5 and t[0] == "Desert" and (c, r) not in wall:
            t[0], t[1] = ("Plains" if (c + r) % 3 else "Grassland"), []
        elif 2.5 < d <= 3.5 and t[0] == "Desert" and (c + 2 * r) % 4 == 0 and (c, r) not in wall:
            t[1] = ["Oasis"]
    for name in ("Gu Yue Clan", "Bai Clan", "Xiong Clan", "Wu Clan", "Heavenly Court", "Huang Jin Family", "Fang Clan"):
        c0, r0 = starts[name]
        for dc, dr, res, amt in ((1, 1, "Spirit Spring", 1), (-1, 2, "Moon Orchid", 2), (2, -1, "Wild Boar", 2), (-2, 0, "Jade", 2)):
            q = (c0 + dc, r0 + dr)
            if q in tiles and q not in wall and q not in taken and tiles[q][0] not in ("Ocean", "Coast", "Mountain", "Lakes"):
                t = tiles[q]
                t[2], t[3] = res, amt
                if res == "Jade":
                    t[1] = ["Hill"]
                elif res == "Wild Boar":
                    t[1] = ["Forest"]
                elif res == "Spirit Spring":
                    t[1] = [f for f in t[1] if f == "Hill"]
                else:
                    t[1] = []
                if t[0] == "Desert" and res != "Jade":
                    t[0] = "Plains"
    za = starts["Zombie Alliance"]
    for q in ((za[0] + 1, za[1]), (za[0], za[1] + 1)):
        if q in tiles and tiles[q][0] not in ("Ocean", "Coast"):
            tiles[q][2], tiles[q][3] = "Spirit Spring", 1
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
