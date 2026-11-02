"""The Ink Night art pass (Phase D; the user chose style D and the full package, 2026-11-02).

Builds, from the mod's own designed silhouettes and 3D characters:

* a full-colour portrait for every building, tech, resource, improvement, promotion and nation icon
  (`Images.Portraits/<Type>Portraits/<name>.png`, 96 px), with one `Background.png` per type at the same size so Unciv
  draws the portrait at full size instead of shrinking it into its white circle [src ui/images/Portrait.kt];
  units have pixel-art diorama portraits (tools/art/pixelunits.py) set on an Ink Night background
  (`Images.Units/UnitPortraits/Background.png`);
* a splash screen for every wonder (`Images.Wonders/WonderImages/<name>.png`, 2:1);
* the eight majors' leader portraits (`Images/LeaderIcons/<leader>.png`);
* the victory illustrations (`Images.Victories/VictoryIllustrations/<victory>/...`);
* Civilopedia icons for the unit types (`Images/UnitTypeIcons/<type>.png`).

Policy icons stay flat white: Unciv tints them by state (pickable, adopted) [src PolicyPickerScreen.PolicyButton].
Colours: a path's family colour for everything of a path (with its red seal), the era's essence colour for techs,
the nation's brighter colour for nations, and a small fixed palette for the rest.
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
            if name.startswith("Aptitude"):
                return (240, 205, 110), None
        return NEUTRAL, None


# ---------------------------------------------------------------- the jobs (forked workers share these globals)
_JOBS: list = []


def _render(i):
    folder, name, draw, colour, seal_key = _JOBS[i]
    from .pathart import symbol
    im = P.ink_night(draw(), colour, key=name, seal=symbol(seal_key) if seal_key else None, part="figure")
    return i, im.resize((PX, PX), Image.LANCZOS).tobytes()


# each portrait type's backdrop colour (the ensō and the disc's glow); the object's own colour is its glowing shape
TYPE_COLOUR = {"BuildingPortraits": (225, 185, 105), "TechPortraits": (120, 175, 230), "ResourcePortraits": (130, 200, 150),
               "ImprovementPortraits": (200, 170, 120), "UnitPromotionPortraits": (200, 190, 165),
               "NationPortraits": (215, 205, 185), "UnitPortraits": (190, 180, 160)}


def background(px: int, ptype: str = "UnitPortraits") -> Image.Image:
    """The Ink Night disc with its ensō: what Unciv draws behind every portrait of a type."""
    from .glyphs import G
    return P.ink_night(G(), TYPE_COLOUR[ptype], key="background " + ptype, part="backdrop").resize((px, px), Image.LANCZOS)


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
def splash(draw, colour, key, seal=None, w=256, h=128) -> Image.Image:
    """An ink landscape at night: layered ridges in mist, a moon, the wonder's shape glowing in an ensō."""
    rng = P._rng("splash" + key)
    W, H = w * 2, h * 2
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = np.dstack([np.full((H, W), c, np.float32) for c in (0.05, 0.06, 0.12)])
    sky += (yy / H)[..., None] * np.asarray([0.08, 0.07, 0.10], np.float32)
    col = np.asarray(colour, np.float32) / 255.0
    mx, my = rng.uniform(0.12, 0.3) * W, rng.uniform(0.18, 0.32) * H
    d = np.hypot(xx - mx, yy - my)
    moon = np.clip((H * 0.07 - d) / 2, 0, 1)
    sky += np.clip(1 - d / (H * 0.35), 0, 1)[..., None] ** 2 * col * 0.25
    img = sky * (1 - moon[..., None]) + moon[..., None] * np.asarray([0.95, 0.93, 0.85], np.float32)
    for layer in range(4):   # ridges, far (pale, misty, tinted) to near (dark ink)
        base = H * (0.50 + 0.12 * layer)
        amp = H * (0.18 - 0.03 * layer)
        xs = np.arange(W, dtype=np.float32)
        ridge = base - amp * (np.sin(xs / W * math.pi * rng.uniform(1.5, 3.5) + rng.uniform(0, 6)) * 0.6
                              + np.sin(xs / W * math.pi * rng.uniform(5, 9) + rng.uniform(0, 6)) * 0.3
                              + (rng.random(W) - 0.5).cumsum() / W * 4)
        mask = (yy > ridge[None, :]).astype(np.float32)
        far = 1 - layer / 3                                                # 1 far .. 0 near
        tone = np.asarray([0.30, 0.31, 0.38], np.float32) * far + np.asarray([0.05, 0.05, 0.07], np.float32) * (1 - far)
        tone = tone + col * 0.10 * far
        depth = np.clip((yy - ridge[None, :]) / (H * 0.22), 0, 1)        # mist pooling at each ridge's foot
        shade = tone[None, None, :] * (1.15 - 0.45 * depth[..., None]) + (0.10 * far) * (1 - depth[..., None])
        img = img * (1 - mask[..., None]) + shade * mask[..., None]
        band = np.exp(-((yy - (base + H * 0.06)) / (H * 0.035)) ** 2) * 0.18 * far   # a mist band
        img = img + band[..., None] * np.asarray([0.75, 0.78, 0.85], np.float32)
    rgb = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    emblem = P.ink_night(draw(), colour, key=key, seal=seal).resize((int(H * 0.86), int(H * 0.86)), Image.LANCZOS)
    rgb.alpha_composite(emblem, (int(W * 0.62 - emblem.width / 2), int(H * 0.07)))
    edge = Image.new("L", (W, H), 0)
    ImageDraw.Draw(edge).rounded_rectangle([2, 2, W - 3, H - 3], radius=14, fill=255)
    rgb.putalpha(edge)
    return rgb.resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- leader portraits
LEADER_LOOK = {   # nation: (scene builder, path symbol for the seal)
    "Gu Yue Clan": ("moon", 4), "Bai Clan": ("water", 4), "Xiong Clan": ("strength", 4), "Wu Clan": ("wind", 4),
    "Heavenly Court": ("immortal", 8), "Huang Jin Family": ("immortal", 6), "Zombie Alliance": ("zombie", 6),
    "Fang Clan": ("plain", 5)}
SEAL_OF = {"Gu Yue Clan": "moon", "Bai Clan": "water", "Xiong Clan": "strength", "Wu Clan": "wind",
           "Heavenly Court": "heaven", "Huang Jin Family": "human", "Zombie Alliance": "transformation",
           "Fang Clan": "refinement"}


def leader(nation: dict, px=256) -> Image.Image:
    """An ink silhouette of the clan's leader, rim-lit in the nation's colour, before a great moon inside an ensō."""
    from PIL import ImageFilter
    from . import characters as C
    from . import render3d
    from .pathart import symbol
    kind, rank = LEADER_LOOK[nation["name"]]
    build = {"moon": lambda: C.gu_master(rank, "Moon"), "water": lambda: C.gu_master(rank, "Water"),
             "strength": lambda: C.gu_master(rank, "Strength"), "wind": lambda: C.gu_master(rank, "Wind"),
             "immortal": lambda: C.gu_immortal(rank), "zombie": C.immortal_zombie,
             "plain": lambda: C.gu_master(rank, None)}[kind]
    fig = render3d.render(build(), size=(px * 2, px * 2), scale=2.7, center=(0.0, 1.05), yaw=24, elevation=8,
                          shadow=False, layers=False)["base"]
    a = np.asarray(fig.getchannel("A"), np.float32) / 255.0
    colour = _bright(max((tuple(nation[k]) for k in ("innerColor", "outerColor")),
                         key=lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]))
    S = px * 2
    from .glyphs import G
    bg = P.ink_night(G(), colour, key="leader" + nation["name"]).resize((S, S), Image.LANCZOS)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.hypot(xx - S * 0.5, yy - S * 0.42)
    moon = np.clip((S * 0.27 - d) / 3, 0, 1)
    glow = np.clip(1 - d / (S * 0.5), 0, 1) ** 2
    col = np.asarray(colour, np.float32) / 255.0
    base = np.asarray(bg, np.float32)[..., :3] / 255.0
    base = base + glow[..., None] * col * 0.35
    base = base * (1 - moon[..., None]) + moon[..., None] * (0.72 + 0.28 * col)
    # silhouette with a rim of light on the moon side (up), a faint inner sheen
    er = np.asarray(fig.getchannel("A").filter(ImageFilter.MinFilter(7)), np.float32) / 255.0
    shifted = np.asarray(fig.getchannel("A").transform((S, S), Image.AFFINE, (1, 0, 0, 0, 1, 6)), np.float32) / 255.0
    rim = np.clip(a - np.minimum(er, shifted), 0, 1)
    ink = np.asarray([0.06, 0.06, 0.08], np.float32)
    out = base * (1 - a[..., None]) + a[..., None] * ink[None, None, :]
    out = out + rim[..., None] * (0.55 * col + 0.45)
    disc = Image.new("L", (S, S), 0)
    ImageDraw.Draw(disc).ellipse([S * 0.03, S * 0.03, S * 0.97, S * 0.97], fill=255)
    im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    alpha = np.minimum(np.asarray(bg.getchannel("A")), np.asarray(disc))
    im.putalpha(Image.fromarray(alpha.astype(np.uint8), "L"))
    enso = P.ink_night(G(), colour, key="leader" + nation["name"], seal=symbol(SEAL_OF[nation["name"]])).resize((S, S), Image.LANCZOS)
    ea = np.asarray(enso, np.float32) / 255.0
    ring = np.clip((_radial_s(S) - 0.72) * 6, 0, 1)                        # keep the ensō and seal, not the disc
    seal_zone = ((xx > S * 0.6) & (yy > S * 0.6)).astype(np.float32)
    keep = np.maximum(ring, seal_zone * (ea[..., 0] > 0.5) * (ea[..., 1] < 0.4))
    over = Image.fromarray((ea * 255).astype(np.uint8), "RGBA")
    over.putalpha(Image.fromarray((ea[..., 3] * keep * 255).astype(np.uint8), "L"))
    im.alpha_composite(over)
    return im.resize((px, px), Image.LANCZOS)


def _radial_s(S):
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    return np.hypot(xx - S / 2, yy - S / 2) / (S / 2)


# ---------------------------------------------------------------- victory illustrations
def victory(kind: str, state: str, w=400, h=240) -> Image.Image:
    """kind: the victory's symbol path key; state: 'bg', 'milestone', 'won' or 'lost'."""
    from .glyphs import G
    from .pathart import symbol
    colour = {"bg": (190, 180, 160), "milestone": (235, 200, 105), "won": (255, 215, 120), "lost": (150, 150, 165)}[state]
    g = symbol(kind) if state != "bg" else G()
    im = splash(lambda: g, colour, key=f"victory {kind} {state}", w=w, h=h)
    if state == "lost":
        im = Image.blend(im, Image.new("RGBA", im.size, (20, 20, 26, 255)), 0.45)
        im.putalpha(splash(lambda: g, colour, key=f"victory {kind} {state}", w=w, h=h).getchannel("A"))
    return im


VICTORY_SYMBOL = {"Southern Border Supremacy": "killing", "Endurance": "time", "Eternal Life": "heaven"}


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
    return P.ink_night(g, colour, key=utype).resize((PX, PX), Image.LANCZOS)   # Civilopedia shows it as it is


def build(registry, mod: Path, save) -> int:
    written = portraits(registry, mod, save)
    pal = Palette(mod)
    from .pathart import symbol
    draws = {name: draw for folder, name, draw, _ in registry if folder == "BuildingIcons"}
    for name in sorted(pal.wonders):
        if name in draws:
            colour, k = pal("BuildingIcons", name)
            written += save(splash(draws[name], colour, name, seal=symbol(k) if k else None),
                            mod / "Images.Wonders" / "WonderImages" / f"{name}.png")
    nations = json.loads((mod / "jsons" / "Nations.json").read_text(encoding="utf-8"))
    for n in nations:
        if n.get("leaderName") and n["name"] in LEADER_LOOK:
            written += save(leader(n), mod / "Images" / "LeaderIcons" / f"{n['leaderName']}.png")
    from . import victories   # layered scenes: Unciv stacks milestones, Won and Lost over the background
    written += victories.build(mod, json.loads((mod / "jsons" / "VictoryTypes.json").read_text(encoding="utf-8")), save)
    units = json.loads((mod / "jsons" / "Units.json").read_text(encoding="utf-8"))
    for t in sorted({u["unitType"] for u in units}):
        written += save(unit_type_icon(t), mod / "Images" / "UnitTypeIcons" / f"{t}.png")
    return written
