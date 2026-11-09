#!/usr/bin/env python3
"""Generate the mod's original art: flat icons (tools/art/glyphs.py), pixel-art units and terrain, and the rest.

* Icons follow Unciv's flat-icon style: a one-colour silhouette on a transparent 100x100 canvas; white for units,
  nations, techs, promotions and policies, black for buildings, resources and improvements (as in the base game's
  atlases). Unciv draws them on coloured circles.
* Attack animations: Images.Units/TileSets/<unitset>/Units/<attacker unit name>-attack-<n>.png, played over the unit that
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

from art import arcart, csart, cultart, foodart, glyphs, glyphs2, guart, heroart, pathart, pixeltiles, pixelunits  # noqa: E402
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
    # map sprites and attack frames get their own atlas (Units.png): with the icons they spilled into a second game
    # texture, which costs texture swaps on phones (Images-and-Audio.md, "Multiple texture atlases")
    tiles = args.mod / "Images.Units" / "TileSets" / UNITSET / "Units"
    written, kept, sheet = 0, [], []
    # the path promotions (several hundred icons) get their own atlas, Paths.png: with the other icons they spilled into a
    # second game texture (game2.png)
    path_icons = {(folder, name) for folder, name, _, _ in pathart.icons()}
    # the path branches, their policies and halls (2026-11-01) get a fifth atlas, Policies.png
    policy_icons = {(folder, name) for folder, name, _, _ in pathart.policy_icons()}
    # the immortal tiers and moves (MOD_SPEC_2 C3/C5) overflowed Paths.png in turn: a third atlas, Arc.png
    import gen_paths
    arc_names = {m for p in gen_paths.PATHS for m in (p["immortal"], gen_paths.tier_name(p, 2), gen_paths.tier_name(p, 3))}
    # Phase D: the Gu catalog's icons join the Arc atlas, which had room (2048 x 1024)
    gu_icons = {(folder, name) for folder, name, _, _ in guart.icons() + guart.combo_icons()}
    path_icons |= gu_icons
    arc_names |= {name for _, name in gu_icons}
    registry = (glyphs.ICONS + glyphs2.ICONS2 + pathart.icons() + arcart.ICONS3 + arcart.inheritance_icons()
                + arcart.rank78_gu_icons() + pathart.policy_icons() + arcart.realm_icons() + guart.icons() + guart.combo_icons()
                # Regions II: every city-state's nation icon (Unciv drew a bare circle without one)
                + csart.icons()
                # reference audit Layer 1: the small stages, the rank relics, the extreme physique
                + cultart.icons()
                # the user (2026-11-08): the heroes' emblems
                + heroart.icons() + foodart.icons())
    # the paths' basic foods (2026-11-09) and their Gu's hunger meters overflowed game.png and Paths.png (Unciv warns
    # on a game2.png): they get their own atlas, Foods.png
    import path_foods
    new_foods = {r["food"] for r in path_foods.NEW}
    food_gu = {g["name"] for g in gen_paths.PATH_GU if g["food"] in new_foods}
    food_icons = {("ResourceIcons", f) for f in new_foods}
    for folder, name, _, _ in registry:
        if folder == "UnitPromotionIcons" and " Hunger " in name and name.split(" Hunger ")[0] in food_gu:
            food_icons.add((folder, name))
    for folder, name, draw, ink in registry:
        if (folder, name) in food_icons:
            for old_dir in (images, args.mod / "Images.Paths", args.mod / "Images.Arc"):
                stale = old_dir / folder / f"{name}.png"
                if stale.exists() and ours(stale):
                    stale.unlink()
            target = args.mod / "Images.Foods" / folder / f"{name}.png"
        elif (folder, name) in policy_icons:
            target = args.mod / "Images.Policies" / folder / f"{name}.png"
        elif (folder, name) in path_icons:
            stale = images / folder / f"{name}.png"
            if stale.exists() and ours(stale):
                stale.unlink()
            target = args.mod / ("Images.Arc" if name in arc_names else "Images.Paths") / folder / f"{name}.png"
            other = args.mod / ("Images.Paths" if name in arc_names else "Images.Arc") / folder / f"{name}.png"
            if other.exists() and ours(other):
                other.unlink()
        else:
            target = images / folder / f"{name}.png"
        im = draw().image(INK[ink])
        circle = {"NationIcons": (30, 40, 90), "UnitPromotionIcons": (60, 110, 60), "TechIcons": (40, 90, 140),
                  "PolicyIcons": (120, 60, 120), "PolicyBranchIcons": (90, 40, 100), "CityStateIcons": (110, 90, 40)}.get(
            folder, (150, 40, 40) if ink == "white" else (214, 182, 96))
        sheet.append((name, im, circle))
        if save(im, target):
            written += 1
        else:
            kept.append(f"{folder}/{name}")
    # Gold is shown as primeval stones (tools/gen_translations.py): the stat icon and the in-text emoji become a stone
    for path, px in (("StatIcons/Gold", 100), ("EmojiIcons/Gold", 50)):
        written += save(glyphs2.primeval_stone_icon(px), images / f"{path}.png")
    # the units as pixel art in the HexaRealm / FantasyHex style (tools/art/pixelunits.py, the user 2026-11-02): the
    # 64 x 56 sprite for the default unit set and HexaRealm's, the 32 x 28 one for FantasyHex's, each with its civ colour
    # layers (<name>-1 tinted by the nation's inner colour, <name>-2 by its outer [src TileLayerUnitSprite]); attack
    # frames for the default unit set; diorama portraits (the unit on its grass hex)
    unit_files = set()
    for name in pixelunits.SPRITES:
        layers = pixelunits.sprite(name)
        for unitset, ts in ((UNITSET, "HexaRealm"), ("HexaRealm", "HexaRealm"), ("FantasyHex", "FantasyHex")):
            folder = args.mod / "Images.Units" / "TileSets" / unitset / "Units"
            for suffix, key in (("", "base"), ("-1", "layer1"), ("-2", "layer2")):
                im = layers[ts][key]
                if suffix and im.getbbox() is None:
                    continue   # no clan colour in this sprite: no empty layer in the atlas
                unit_files.add(folder / f"{name}{suffix}.png")
                written += save(im, folder / f"{name}{suffix}.png")
        for n, im in enumerate(pixelunits.attack_frames(name), start=1):
            unit_files.add(tiles / f"{name}-attack-{n}.png")
            written += save(im, tiles / f"{name}-attack-{n}.png")
        written += save(pixelunits.portrait(name), args.mod / "Images.Units" / "UnitPortraits" / f"{name}.png")
    for path in (args.mod / "Images.Units" / "TileSets").glob("*/Units/*.png"):   # sprites and frames no longer drawn
        if path not in unit_files and ours(path):
            path.unlink()
    # the secret realms' natural-wonder tiles (MOD_SPEC_2 #13) and the five region walls (Five Regions map), drawn as
    # pixel-art dioramas natively for the default tileset and its fallback (the user, 2026-11-02)
    for name in {**pixeltiles.REALMS, **pixeltiles.WALLS}:
        for tileset, im in pixeltiles.tile(name).items():
            written += save(im, images / "TileSets" / tileset / "Tiles" / f"{name}.png")
    # Phase D: the attack sounds (tools/art/sfx.py: rank body, path x attainment tier, dao marks, killer moves)
    # the Ink Night art pass (the user chose style D, 2026-11-02): full-colour portraits for every icon, backgrounds,
    # wonder splash screens, leader portraits, victory illustrations, unit type icons (tools/art/inkpass.py)
    from art import inkpass
    written += inkpass.build(registry, args.mod, save)
    from art import sfx
    written += sfx.build(args.mod)
    if args.sheet:
        contact_sheet(sheet, args.sheet)
    if not args.quiet:
        print(f"[gen_art] wrote {written} image(s); kept {len(kept)} file(s) that are real art: {', '.join(kept) or '-'}")
        print("[gen_art] repack the Android atlas: tools/unciv_ci.py --pack")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
