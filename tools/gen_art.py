#!/usr/bin/env python3
"""Generate the mod's original art: flat icons (tools/art/glyphs.py) and attack animations (tools/art/anims.py).

* Icons follow Unciv's flat-icon style: a one-colour silhouette on a transparent 100x100 canvas; white for units,
  nations, techs, promotions and policies, black for buildings, resources and improvements (as in the base game's
  atlases). Unciv draws them on coloured circles.
* Attack animations: Images/TileSets/<unitset>/Units/<attacker unit type>-attack-<n>.png, played over the unit that
  takes the damage [docs Creating-a-custom-tileset.md, src BattleTableHelpers]; written for the default unit set
  (AbsoluteUnits).
* Every file carries the PNG text chunk GeneratedArt=gen_art. The tool overwrites only its own files and
  placeholders (make_placeholders.py), never other art. Objects without a design keep their placeholder.

Every shape is drawn from geometric primitives: nothing is copied from the novel, manhua or fan art (MOD_SPEC rule 6).

Usage: tools/gen_art.py [--mod PATH] [--sheet FILE] [--quiet]     (--sheet also writes a contact sheet PNG)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin

sys.path.insert(0, str(Path(__file__).resolve().parent))

from art import anims, characters, glyphs, glyphs2, render3d  # noqa: E402
from common import REPO_ROOT  # noqa: E402

TAG = ("GeneratedArt", "gen_art")
UNITSET = "AbsoluteUnits"  # Constants.defaultUnitset in 4.22.8 [src Constants.kt]
INK = {"white": (255, 255, 255), "black": (0, 0, 0)}


def ours(path: Path) -> bool:
    """True if the file may be overwritten: missing, a placeholder, or written by this tool."""
    if not path.exists():
        return True
    try:
        with Image.open(path) as img:
            return img.info.get("Placeholder") == "true" or img.info.get(TAG[0]) == TAG[1]
    except OSError:
        return False


def save(img: Image.Image, path: Path) -> bool:
    if not ours(path):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = PngImagePlugin.PngInfo()
    meta.add_text(*TAG)
    img.save(path, pnginfo=meta, optimize=True)
    return True


def contact_sheet(items: list[tuple[str, Image.Image, tuple]], out: Path) -> None:
    cols = 7
    sheet = Image.new("RGBA", (cols * 150, ((len(items) + cols - 1) // cols) * 160), (40, 42, 50, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, im, circle) in enumerate(items):
        tile = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        ImageDraw.Draw(tile).ellipse((0, 0, 119, 119), fill=circle)
        tile.alpha_composite(im, (10, 10))
        x, y = (i % cols) * 150 + 15, (i // cols) * 160 + 8
        sheet.alpha_composite(tile, (x, y))
        d.text((x + 60, y + 132), name, fill=(230, 230, 230), anchor="mm")
    sheet.save(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", type=Path, default=REPO_ROOT)
    ap.add_argument("--sheet", type=Path, default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    images = args.mod / "Images"
    written, kept, sheet = 0, [], []
    for folder, name, draw, ink in glyphs.ICONS + glyphs2.ICONS2:
        im = draw().image(INK[ink])
        circle = {"NationIcons": (30, 40, 90), "UnitPromotionIcons": (60, 110, 60), "TechIcons": (40, 90, 140),
                  "PolicyIcons": (120, 60, 120), "PolicyBranchIcons": (90, 40, 100), "CityStateIcons": (110, 90, 40)}.get(
            folder, (150, 40, 40) if ink == "white" else (214, 182, 96))
        sheet.append((name, im, circle))
        if save(im, images / folder / f"{name}.png"):
            written += 1
        else:
            kept.append(f"{folder}/{name}")
    for unit_type, make in anims.ANIMS.items():
        for n, im in enumerate(make(), start=1):
            if save(im, images / "TileSets" / UNITSET / "Units" / f"{unit_type}-attack-{n}.png"):
                written += 1
            else:
                kept.append(f"{unit_type}-attack-{n}")
    # pre-rendered 3D characters (tools/art/characters.py, render3d.py): map sprites with civ-colour layers
    # (<name>-1 tinted by the nation's inner colour, <name>-2 by its outer colour [src TileLayerUnitSprite]),
    # UI portraits, and per-unit attack effects (played over the unit that takes the damage)
    units = images / "TileSets" / UNITSET / "Units"
    for name, build in characters.UNITS.items():
        wolf = "Wolf" in name
        frame = dict(size=(128, 110), scale=3.4 if wolf else 4.4, center=(0.0, 0.7 if wolf else 0.95))
        out = render3d.render(build(), **frame)
        for suffix, key in (("", "base"), ("-1", "layer1"), ("-2", "layer2")):
            written += save(out[key], units / f"{name}{suffix}.png")
        mats = {"robe": render3d.Mat(characters.PORTRAIT_ROBE.get(name, (120, 120, 120))),
                "trim": render3d.Mat(characters.PORTRAIT_TRIM)}
        pscale, pcenter = ((1.7, (0.1, 0.8)) if name == "Lightning Wolf" else (2.0, (0.1, 0.9)) if wolf
                           else (1.5, (0.0, 1.5)))
        portrait = render3d.render(build(), size=(128, 128), scale=pscale * (1.12 if name == "Thunder Crown Wolf" else 1.0),
                                   center=pcenter, yaw=30, elevation=12, shadow=False, layers=False, mats=mats)
        written += save(portrait["base"], images / "UnitPortraits" / f"{name}.png")
        for n, effect in enumerate(characters.ATTACKS.get(name, []), start=1):
            fx = render3d.render(effect(), **frame, shadow=False, layers=False, glow=1.2)
            written += save(fx["base"], units / f"{name}-attack-{n}.png")
    if args.sheet:
        contact_sheet(sheet, args.sheet)
    if not args.quiet:
        print(f"[gen_art] wrote {written} image(s); kept {len(kept)} file(s) that are real art: {', '.join(kept) or '-'}")
        print("[gen_art] repack the Android atlas: tools/unciv_ci.py --pack")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
