#!/usr/bin/env python3
"""Generate placeholder icons at the exact paths Unciv looks up (Images/<Category>Icons/<Name>.png).

* Only objects whose icon exists neither in the mod nor in the base game get one.
* Colour encodes the category; the label is the object's initials.
* Every generated PNG carries the text chunk `Placeholder=true`, so real art is never overwritten:
  --force regenerates placeholders only, and --report counts placeholders vs real art.
* --preview writes preview.png (mod-manager thumbnail, MOD_SPEC §11) if it is missing.

Usage: tools/make_placeholders.py [--mod PATH] [--dry-run] [--force] [--report] [--preview]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

from common import BUILTIN_IMAGES, Ruleset, mod_root_from_args, require_ref
from check_refs import expected_images

SIZE = 100  # docs (Images-and-Audio.md): "100x100 pixels is good enough for most icons"
COLORS = {  # folder -> RGB, chosen to be distinguishable at a glance
    "UnitIcons": (178, 34, 34), "BuildingIcons": (70, 110, 180), "TechIcons": (46, 139, 87),
    "ResourceIcons": (218, 165, 32), "ImprovementIcons": (139, 90, 43), "UnitPromotionIcons": (148, 0, 211),
    "NationIcons": (40, 40, 40), "PolicyIcons": (0, 139, 139), "PolicyBranchIcons": (0, 95, 95),
    "ReligionIcons": (199, 21, 133), "CityStateIcons": (105, 105, 105),
}


def initials(name: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", name)
    if not words:
        return "?"
    if len(words) == 1:
        return words[0][:2].capitalize()
    return "".join(w[0].upper() for w in words[:3])


def is_placeholder(path: Path) -> bool:
    try:
        with Image.open(path) as img:
            return img.info.get("Placeholder") == "true"
    except OSError:
        return False


def font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def draw_icon(path: Path, label: str, color: tuple[int, int, int]) -> None:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, SIZE - 5, SIZE - 5), fill=color + (255,), outline=(255, 255, 255, 255), width=4)
    f = font(40 if len(label) <= 2 else 30)
    box = d.textbbox((0, 0), label, font=f)
    d.text(((SIZE - (box[2] - box[0])) / 2 - box[0], (SIZE - (box[3] - box[1])) / 2 - box[1]),
           label, font=f, fill=(255, 255, 255, 255))
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Placeholder", "true")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, pnginfo=meta)


def draw_preview(path: Path, title: str) -> None:
    img = Image.new("RGB", (512, 256), (20, 24, 32))
    d = ImageDraw.Draw(img)
    d.rectangle((8, 8, 503, 247), outline=(200, 170, 90), width=3)
    f = font(34)
    for i, line in enumerate(title.split("\n")):
        box = d.textbbox((0, 0), line, font=f)
        d.text(((512 - (box[2] - box[0])) / 2, 70 + i * 60), line, font=f, fill=(230, 210, 150))
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Placeholder", "true")
    img.save(path, pnginfo=meta)


def main(argv: list[str]) -> int:
    require_ref()
    mod_root = mod_root_from_args(argv)
    dry, force = "--dry-run" in argv, "--force" in argv
    rs = Ruleset(mod_root).load()
    if not rs.exists:
        print("no jsons/ folder yet - no objects need icons")
        return 0

    builtin = set(BUILTIN_IMAGES.read_text().split("\n")) if BUILTIN_IMAGES.exists() else set()
    mod_images = {}
    for folder in mod_root.glob("Images*"):
        if folder.is_dir():
            for png in folder.rglob("*.png"):
                mod_images[png.relative_to(folder).with_suffix("").as_posix()] = png

    created = skipped = placeholders = real = 0
    for kind, name, candidates in expected_images(rs):
        existing = next((mod_images[c] for c in candidates if c in mod_images), None)
        if existing is not None:
            if is_placeholder(existing):
                placeholders += 1
                if not force:
                    continue
            else:
                real += 1
                continue
        elif any(c in builtin for c in candidates):
            skipped += 1
            continue
        target = existing or (mod_root / "Images" / f"{candidates[0]}.png")
        folder = candidates[0].split("/")[0]
        if dry:
            print(f"would create {target.relative_to(mod_root)}")
        else:
            draw_icon(target, initials(name), COLORS.get(folder, (90, 90, 90)))
        if existing is None:
            created += 1

    if "--preview" in argv and not (mod_root / "preview.png").exists() and not dry:
        draw_preview(mod_root / "preview.png", "Reverend Insanity\nGu World")
        print("created preview.png")

    verb = "would create" if dry else "created"
    print(f"{verb} {created} placeholder(s); {placeholders} existing placeholder(s), {real} real icon(s), "
          f"{skipped} icon(s) provided by the base game")
    if "--report" in argv and placeholders + created:
        print(f"art still needed for {placeholders + created} object(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
