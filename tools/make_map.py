#!/usr/bin/env python3
"""Build the hand-made Qing Mao Mountain map (maps/Qing Mao Mountain), the canon setting of Slice 1.

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

Usage: tools/make_map.py [--check] [--quiet]
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
OUT = REPO_ROOT / "maps" / "Qing Mao Mountain"
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


def build(out: Path, quiet: bool) -> None:
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
        spec.write_text("\n".join(design()) + "\n", encoding="utf-8")
        out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["java", "-Dfile.encoding=UTF-8", "-cp", f"{jar}{':'}{classes}", "MakeMap", str(work),
                            MOD_NAME, str(spec), str(out)], cwd=work, capture_output=True, text=True, timeout=300)
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
            fresh = Path(tmp) / OUT.name
            build(fresh, True)
            if not OUT.exists() or decoded(fresh) != decoded(OUT):
                print("[make_map] maps/ is out of date; run tools/make_map.py")
                return 1
        return 0
    build(OUT, args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
