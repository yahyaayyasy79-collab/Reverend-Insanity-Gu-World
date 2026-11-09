"""The mod's portraits and illustrations in jewel enamel and gold (the user chose style B, 2026-11-03: "mewah,
simple, masih terbaca walau kecil"; before it, the Ink Night pass of 2026-11-02).

Builds, from the mod's own designed silhouettes (and the 3D leader figures):

* a medallion portrait for every building, tech, resource, improvement, promotion and nation icon
  (`Images.Portraits/<Type>Portraits/<name>.png`, 96 px): the shape in gold relief on enamel in the object's colour,
  inside a gold bezel; one `Background.png` per type at the same size (a soft shadow) so Unciv draws the portrait at
  full size instead of shrinking it into its white circle [src ui/images/Portrait.kt]; the units' diorama portraits
  (tools/art/pixelunits.py) get the same shadow (`Images.Units/UnitPortraits/Background.png`);
* a splash screen for every wonder (`Images.Wonders/WonderImages/<name>.png`, 2:1): an enamel dusk, a gold sun,
  ridges edged in gold, the wonder's medallion, a double gold border;
* the eight majors' leader portraits (`Images/LeaderIcons/<leader>.png`): the leader in gold on the nation's enamel;
* the victory illustrations (tools/art/victories.py) and Civilopedia icons for the unit types.

Policy icons stay flat white: Unciv tints them by state (pickable, adopted) [src PolicyPickerScreen.PolicyButton].
Colours: a path's family colour for everything of a path, the era's essence colour for techs, the nation's brighter
colour for nations, and a small fixed palette for the rest.
"""
from __future__ import annotations

import csv
import json
import math
import multiprocessing as mp
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import portrait as P

PX = 96            # portrait size in the atlas (Unciv recommends 100-256; 96 keeps the atlas to a few pages)
UNIT_PX = 144      # the unit portraits' size (pixelunits.PORTRAIT): the background must match it (Portrait.kt scales by the ratio)
TYPE_OF = {"BuildingIcons": "BuildingPortraits", "TechIcons": "TechPortraits", "ResourceIcons": "ResourcePortraits",
           "ImprovementIcons": "ImprovementPortraits", "UnitPromotionIcons": "UnitPromotionPortraits",
           "NationIcons": "NationPortraits"}
NEUTRAL = (205, 195, 175)
WARN = (235, 140, 70)
DEBUFF = (225, 90, 90)


def _bright(c, floor=150):
    lum = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    if lum >= floor:
        return tuple(int(x) for x in c)
    t = min(1.0, (floor - lum) / 180)
    return tuple(int(x + (255 - x) * t) for x in c)


class Palette:
    """(colour, seal path key or None) for every icon name, read from the generated ruleset and the data tables."""

    def __init__(self, mod: Path):
        import gen_paths as GP
        import gu_catalog as GC
        import gu_combos as GCO
        js = lambda f: json.loads((mod / "jsons" / f).read_text(encoding="utf-8"))
        fam = {r["family"]: tuple(int(x) for x in r["color"].split()) for r in
               csv.DictReader((mod / "data" / "path_families.csv").open(encoding="utf-8"))}
        self.path_color = {p["key"]: _bright(fam[p["family"]]) for p in GP.PATHS}
        self.of_path = {}
        for p in GP.PATHS:
            k = p["key"]
            for t in range(GP.MAX_TIER):
                self.of_path[GP.tier_name(p, t)] = k
            self.of_path[p["mortal"]] = self.of_path[p["immortal"]] = self.of_path[GP.hall_name(p)] = k
        for g in GP.PATH_GU:
            self.of_path.setdefault(g["name"], g["path"])
        for r in GC.ROWS:
            self.of_path[r["name"]] = r["path"]
        for g in GC.all_immortal():
            self.of_path[g["name"]] = self.of_path[GC.bearer(g["name"])] = g["path"]
        for r in GCO.rows():
            self.of_path[r["name"]] = GCO.paths_of(r)[0]
        import path_foods as PF   # the paths' basic foods wear their path's colour
        for r in PF.ROWS:
            self.of_path.setdefault(r["food"], r["key"])
        eras = {e["name"]: _bright(tuple(e["iconRGB"])) for e in js("Eras.json")}
        self.tech = {t["name"]: eras[col["era"]] for col in js("Techs.json") for t in col["techs"]}
        self.nation = {}
        for n in js("Nations.json"):
            cs = [tuple(n[k]) for k in ("innerColor", "outerColor") if k in n]
            if cs:
                self.nation[n["name"]] = _bright(max(cs, key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]))
        self.wonders = {b["name"] for b in js("Buildings.json") if b.get("isWonder")}
        self.national = {b["name"] for b in js("Buildings.json") if b.get("isNationalWonder")}
        self.statuses = {s["name"] for s in GP.STATUSES}
        ess = {"Green Grape": (150, 215, 100), "Red Date": (215, 80, 70), "White Lychee": (240, 236, 222),
               "Yellow Apricot": (255, 200, 80)}
        self.resource = {}
        for r in js("TileResources.json"):
            c = next((v for k, v in ess.items() if r["name"].startswith(k)), None)
            self.resource[r["name"]] = c or {"Luxury": (235, 190, 90), "Bonus": (150, 205, 120)}.get(
                r.get("resourceType"), (120, 200, 210))

    def __call__(self, folder: str, name: str):
        k = self.of_path.get(name)
        if k:
            return self.path_color[k], k
        if folder == "TechIcons":
            return self.tech.get(name, NEUTRAL), None
        if folder == "NationIcons":
            return self.nation.get(name, NEUTRAL), None
        if folder == "ResourceIcons":
            return self.resource.get(name, NEUTRAL), None
        if folder == "BuildingIcons":
            return ((235, 200, 105) if name in self.wonders else (215, 220, 235) if name in self.national
                    else (215, 160, 100)), None
        if folder == "ImprovementIcons":
            return ((220, 90, 80) if "Den" in name or "Lair" in name else (200, 175, 125)), None
        if folder == "UnitPromotionIcons":
            if "Hunger" in name:
                return WARN, None
            if name in self.statuses:
                return DEBUFF, None
            if name.startswith("Dao Marks"):
                return (205, 175, 240), None
            if name.startswith("Aptitude") or name.endswith(" Stage") or name == "Stage Cultivation":
                return (240, 205, 110), None
            if name.endswith(" Relic Gu"):   # reference audit Layer 1: the relic's rank colour
                from .cultart import RELIC_COLOURS
                return RELIC_COLOURS[name[:-len(" Relic Gu")]], None
            if name == "Extreme Physique":
                return (150, 205, 250), None
            from .heroart import HERO_NATION   # the heroes wear their clan's colour
            if name in HERO_NATION:
                return self.nation.get(HERO_NATION[name], NEUTRAL), None
            if name == "Doomed Aperture":
                return DEBUFF, None
        return NEUTRAL, None


# ---------------------------------------------------------------- the jobs (forked workers share these globals)
_JOBS: list = []


def _render(i):
    folder, name, draw, colour, _ = _JOBS[i]
    return i, P.enamel(draw(), colour).resize((PX, PX), Image.LANCZOS).tobytes()


def background(px: int, ptype: str = "UnitPortraits") -> Image.Image:
    """What Unciv draws behind every portrait of a type: a soft shadow that grounds the medallions (and the units'
    diorama hexes) on any screen."""
    from .glyphs import G
    return P.enamel(G(), (0, 0, 0), part="backdrop").resize((px, px), Image.LANCZOS)


def portraits(registry, mod: Path, save) -> int:
    """Render every portrait (parallel), plus the backgrounds. registry: [(folder, name, draw, ink)]."""
    pal = Palette(mod)
    _JOBS.clear()
    seen = set()
    for folder, name, draw, _ in registry:
        if folder in TYPE_OF and (folder, name) not in seen:
            seen.add((folder, name))
            _JOBS.append((folder, name, draw) + pal(folder, name))
    written = 0
    ctx = mp.get_context("fork")
    with ctx.Pool(max(1, (mp.cpu_count() or 2))) as pool:
        for i, raw in pool.imap_unordered(_render, range(len(_JOBS)), chunksize=8):
            folder, name = _JOBS[i][0], _JOBS[i][1]
            im = Image.frombytes("RGBA", (PX, PX), raw)
            written += save(im, mod / "Images.Portraits" / TYPE_OF[folder] / f"{name}.png")
    for t in sorted(set(TYPE_OF.values())):
        written += save(background(PX, t), mod / "Images.Portraits" / t / "Background.png")
    written += save(background(UNIT_PX), mod / "Images.Units" / "UnitPortraits" / "Background.png")
    return written


# ---------------------------------------------------------------- wonder splash screens (2:1)
def splash(draw, colour, key, w=256, h=128) -> Image.Image:
    """An enamel screen: the wonder's colour as a dusk sky, a gold sun in a ring, three ridges edged in gold, the
    wonder's medallion, a double gold border."""
    rng = P._rng("splash" + key)
    W, H = w * 2, h * 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    c = np.asarray(colour, np.float32) / 255.0
    t = (yy / H)[..., None]
    img = (c * 0.2)[None, None, :] * (1 - t) + (c * 0.5)[None, None, :] * t
    sx, sy, sr = W * rng.uniform(0.14, 0.3), H * rng.uniform(0.24, 0.34), H * 0.085
    d = np.hypot(xx - sx, yy - sy)
    sun, ring = np.clip(sr - d, 0, 1), np.clip(1 - np.abs(d - sr * 1.5) / 1.4, 0, 1) * 0.8
    img = img * (1 - sun[..., None]) + sun[..., None] * P.gold_ramp(np.clip(0.95 - (yy - sy + sr) / (sr * 4), 0, 1))
    img = img * (1 - ring[..., None]) + ring[..., None] * P.gold_ramp(np.full_like(d, 0.7))
    xs = np.arange(W, dtype=np.float32)
    for layer in range(3):   # far to near, darker, each crest a gold line
        base, amp = H * (0.58 + 0.13 * layer), H * (0.16 - 0.035 * layer)
        ridge = base - amp * (np.sin(xs / W * math.pi * rng.uniform(1.4, 2.6) + rng.uniform(0, 6)) * 0.7
                              + np.sin(xs / W * math.pi * rng.uniform(4, 7) + rng.uniform(0, 6)) * 0.3)
        mask = (yy > ridge[None, :]).astype(np.float32)
        img = img * (1 - mask[..., None]) + (c * (0.42 - 0.1 * layer))[None, None, :] * mask[..., None]
        crest = np.clip(1 - np.abs(yy - ridge[None, :]) / (1.2 + 0.5 * layer), 0, 1) * 0.9
        img = img * (1 - crest[..., None]) + crest[..., None] * P.gold_ramp(np.full_like(yy, 0.55 + 0.12 * layer))
    rgb = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    medal = P.enamel(draw(), colour).resize((int(H * 0.84), int(H * 0.84)), Image.LANCZOS)
    rgb.alpha_composite(medal, (int(W * 0.66 - medal.width / 2), int(H * 0.08)))
    d = ImageDraw.Draw(rgb)
    d.rounded_rectangle([3, 3, W - 4, H - 4], radius=16, outline=(222, 176, 74, 255), width=4)
    d.rounded_rectangle([12, 12, W - 13, H - 13], radius=10, outline=(150, 104, 34, 255), width=2)
    edge = Image.new("L", (W, H), 0)
    ImageDraw.Draw(edge).rounded_rectangle([2, 2, W - 3, H - 3], radius=16, fill=255)
    rgb.putalpha(edge)
    return rgb.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- leader portraits
LEADER_LOOK = {   # nation: (figure, rank)
    "Gu Yue Clan": ("moon", 4), "Bai Clan": ("water", 4), "Xiong Clan": ("strength", 4), "Wu Clan": ("wind", 4),
    "Heavenly Court": ("immortal", 8), "Huang Jin Family": ("immortal", 6), "Zombie Alliance": ("zombie", 6),
    "Fang Clan": ("plain", 5)}


def leader(nation: dict, px=256) -> Image.Image:
    """The clan's leader in gold relief on an enamel medallion in the nation's colour, a pale moon behind."""
    from . import characters as C
    from . import render3d
    kind, rank = LEADER_LOOK[nation["name"]]
    build = {"moon": lambda: C.gu_master(rank, "Moon"), "water": lambda: C.gu_master(rank, "Water"),
             "strength": lambda: C.gu_master(rank, "Strength"), "wind": lambda: C.gu_master(rank, "Wind"),
             "immortal": lambda: C.gu_immortal(rank), "zombie": C.immortal_zombie,
             "plain": lambda: C.gu_master(rank, None)}[kind]
    S = px * 2
    fig = render3d.render(build(), size=(S, S), scale=2.7, center=(0.0, 1.05), yaw=24, elevation=8,
                          shadow=False, layers=False)["base"]
    a = np.asarray(fig.getchannel("A"), np.float32) / 255.0
    colour = _bright(max((tuple(nation[k]) for k in ("innerColor", "outerColor")),
                         key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]))
    inside = P._disc(S, 0.44, 1.2)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    moon = np.clip((S * 0.27 - np.hypot(xx - S * 0.5, yy - S * 0.4)) / 2, 0, 1) * 0.3
    layers = [(P.enamel_fill(colour, S), P._disc(S, 0.447, 1.2)), (np.ones((S, S, 3), np.float32), moon * inside)]
    P.gold_bezel(layers, S)
    P.gold_figure(layers, a, size=S, clip=inside, outline=4)
    return P._compose(layers).resize((px, px), Image.LANCZOS)


def unit_type_icon(utype: str) -> Image.Image:
    from .glyphs import G, gu_beetle, human
    from .glyphs2 import roof
    from .pathart import symbol
    g = G()
    if utype == "Beast":
        g = symbol("enslavement")
    elif utype == "Gu House":
        roof(g, 50, 20, 70, 26); g.poly([(26, 46), (74, 46), (74, 86), (26, 86)])
    elif utype == "Civilian":
        human(g, 50, 10, 1.2)
    else:   # Gu Master and the two legacy types
        human(g, 40, 8, 1.2, arms="raised"); gu_beetle(g, 76, 22, 0.6, legs=False)
    colour = {"Beast": (215, 120, 90), "Gu House": (215, 190, 120), "Civilian": (190, 200, 210)}.get(utype, (150, 210, 180))
    return P.enamel(g, colour).resize((PX, PX), Image.LANCZOS)   # Civilopedia shows it as it is


def preview(registry, mod: Path) -> Image.Image:
    """The mod manager's banner (512 x 256): the Spring Autumn Cicada's medallion, the title in gold, the four signature
    paths' medallions, a double gold border on jade enamel."""
    from PIL import ImageFont
    from .pathart import symbol
    W, H = 1024, 512
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    glow = np.clip(1 - np.hypot((xx - W * 0.3) / W, (yy - H * 0.45) / H) * 1.8, 0, 1)[..., None]
    deep, light = np.asarray((14, 44, 44), np.float32) / 255, np.asarray((40, 112, 100), np.float32) / 255
    img = Image.fromarray((np.clip(deep * (1 - glow) + light * glow, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    cicada = next(d for f, n, d, _ in registry if n == "Spring Autumn Cicada")
    medal = P.enamel(cicada(), (110, 200, 150)).resize((400, 400), Image.LANCZOS)
    img.alpha_composite(medal, (60, 40))
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    for text, size, y in (("REVEREND INSANITY", 40, 128), ("Gu World", 92, 186)):
        f = ImageFont.truetype(font, size)
        box = ImageDraw.Draw(img).textbbox((0, 0), text, font=f)
        x = 728 - (box[2] - box[0]) / 2
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).text((x, y), text, font=f, fill=255)
        outline = Image.new("L", (W, H), 0)
        ImageDraw.Draw(outline).text((x, y), text, font=f, fill=255, stroke_width=4, stroke_fill=255)
        shade = np.clip(0.95 - (yy - y) / (size * 1.4), 0.2, 1)
        gold = Image.fromarray((P.gold_ramp(shade) * 255).astype(np.uint8), "RGB").convert("RGBA")
        gold.putalpha(mask)
        dark = Image.new("RGBA", (W, H), (28, 18, 8, 255))
        dark.putalpha(outline)
        img.alpha_composite(dark)
        img.alpha_composite(gold)
    for i, (k, col) in enumerate((("moon", (120, 150, 230)), ("water", (90, 170, 220)), ("strength", (200, 110, 80)),
                                  ("wind", (130, 200, 150)))):
        m = P.enamel(symbol(k), col).resize((92, 92), Image.LANCZOS)
        img.alpha_composite(m, (int(728 - 2 * 104 + 6 + i * 104), 345))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, W - 7, H - 7], radius=26, outline=(222, 176, 74, 255), width=8)
    d.rounded_rectangle([22, 22, W - 23, H - 23], radius=18, outline=(150, 104, 34, 255), width=3)
    return img.resize((512, 256), Image.LANCZOS).convert("RGB")


def build(registry, mod: Path, save) -> int:
    written = portraits(registry, mod, save)
    pal = Palette(mod)
    draws = {name: draw for folder, name, draw, _ in registry if folder == "BuildingIcons"}
    for name in sorted(pal.wonders):
        if name in draws:
            colour, k = pal("BuildingIcons", name)
            written += save(splash(draws[name], colour, name), mod / "Images.Wonders" / "WonderImages" / f"{name}.png")
    nations = json.loads((mod / "jsons" / "Nations.json").read_text(encoding="utf-8"))
    for n in nations:
        if n.get("leaderName") and n["name"] in LEADER_LOOK:
            written += save(leader(n), mod / "Images" / "LeaderIcons" / f"{n['leaderName']}.png")
    from . import victories   # layered scenes: Unciv stacks milestones, Won and Lost over the background
    written += victories.build(mod, json.loads((mod / "jsons" / "VictoryTypes.json").read_text(encoding="utf-8")), save)
    units = json.loads((mod / "jsons" / "Units.json").read_text(encoding="utf-8"))
    for t in sorted({u["unitType"] for u in units}):
        written += save(unit_type_icon(t), mod / "Images" / "UnitTypeIcons" / f"{t}.png")
    written += save(preview(registry, mod), mod / "preview.png")
    return written
