"""The mod's own map tiles as small 3D dioramas (art pass, the user 2026-11-02: units and terrain "100x better").

The twelve secret realms (natural wonders) and the five region walls of the Five Regions map were flat clip art on a
plain hex. Here each is a scene of primitives rendered by tools/art/render3d.py from a high three-quarter view, set
on a painted hex of its ground, shadowed, then reduced to the tilesets' sizes (HexaRealm 64x56, FantasyHex 32x28) so it
sits among their painted tiles. Every shape is built here; nothing is traced or copied.
"""
from __future__ import annotations

import math
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .render3d import Mat, Scene, render

TW, TH = 256, 224          # working size (4x HexaRealm)
CAM = dict(size=(TW, TH), scale=2.55, center=(0.0, 0.55), yaw=0.0, elevation=36.0, shadow=False, layers=False)

MATS = {
    "rock": Mat((112, 108, 118)), "rock_dark": Mat((70, 66, 78)), "snow": Mat((236, 240, 246), spec=0.2),
    "grass": Mat((104, 158, 72)), "soil": Mat((122, 92, 62)), "violet": Mat((190, 120, 255), emissive=True),
    "wisp": Mat((190, 225, 255), emissive=True), "mist": Mat((206, 212, 224)), "water": Mat((84, 160, 226), spec=0.7),
    "foam": Mat((236, 246, 255), emissive=True), "gold": Mat((240, 200, 90), spec=0.8), "time": Mat((255, 214, 120), emissive=True),
    "white_stone": Mat((236, 232, 222), spec=0.3), "black_stone": Mat((40, 36, 46), spec=0.4),
    "life": Mat((250, 250, 230), emissive=True), "death": Mat((120, 60, 170), emissive=True),
    "red_book": Mat((170, 52, 46)), "blue_book": Mat((52, 86, 150)), "green_book": Mat((56, 122, 80)),
    "paper": Mat((236, 224, 196)), "ember": Mat((255, 110, 40), emissive=True), "flame": Mat((255, 196, 70), emissive=True),
    "bone": Mat((232, 222, 196), spec=0.3), "whale": Mat((70, 96, 130), spec=0.3), "whale_belly": Mat((210, 220, 228)),
    "horn": Mat((236, 214, 150), spec=0.4), "cloud": Mat((240, 242, 250)), "roof_red": Mat((168, 50, 44), spec=0.2),
    "wood": Mat((122, 86, 54)), "yurt": Mat((236, 214, 150), spec=0.2), "banner": Mat((210, 60, 40)),
    "blossom": Mat((246, 170, 200)), "fox": Mat((246, 246, 250), spec=0.2), "toxic": Mat((150, 210, 90), emissive=True),
    "miasma": Mat((110, 140, 80)), "dead_wood": Mat((60, 50, 46)), "root": Mat((112, 76, 46)), "root_dark": Mat((78, 52, 34)),
    "jade": Mat((120, 200, 150), spec=0.9), "rune": Mat((150, 230, 220), emissive=True), "eye": Mat((255, 60, 40), emissive=True),
    "cave": Mat((14, 10, 14)),
}


def _rng(key):
    return np.random.default_rng(zlib.crc32(key.encode()))


def _hex(w, h, inset=0.0):
    pts = [(w * 0.25, 0), (w * 0.75, 0), (w, h / 2), (w * 0.75, h), (w * 0.25, h), (0, h / 2)]
    return [(w / 2 + (x - w / 2) * (1 - inset), h / 2 + (y - h / 2) * (1 - inset)) for x, y in pts]


GROUNDS = {   # (field colour, rim colour, texture strength)
    "grass": ((112, 164, 74), (84, 128, 58), 0.10), "plains": ((168, 160, 96), (130, 122, 72), 0.10),
    "ocean": ((48, 112, 170), (36, 84, 136), 0.08), "rock": ((92, 88, 96), (64, 60, 70), 0.14),
    "ash": ((84, 70, 64), (58, 46, 42), 0.12), "swamp": ((84, 104, 64), (60, 76, 46), 0.12),
}


def ground(kind: str, key: str) -> Image.Image:
    """A painted hex: the field with soft noise and a few tufts, a darker rim, shaded from the top left."""
    field, rim, k = GROUNDS[kind]
    rng = _rng("ground" + key)
    small = rng.random((14, 16)).astype(np.float32)
    noise = np.asarray(Image.fromarray((small * 255).astype(np.uint8), "L").resize((TW, TH), Image.BICUBIC), np.float32) / 255
    fine = np.asarray(Image.fromarray((rng.random((56, 64)) * 255).astype(np.uint8), "L").resize((TW, TH), Image.BICUBIC),
                      np.float32) / 255
    yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32)
    light = 1.06 - 0.12 * (xx / TW + yy / TH) / 2
    shade = (1 + k * (noise - 0.5) * 2 + k * 0.6 * (fine - 0.5)) * light
    col = np.asarray(field, np.float32)[None, None, :] / 255 * shade[..., None]
    img = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")
    mask = Image.new("L", (TW, TH), 0)
    ImageDraw.Draw(mask).polygon(_hex(TW, TH, 0.02), fill=255)
    inner = Image.new("L", (TW, TH), 0)
    ImageDraw.Draw(inner).polygon(_hex(TW, TH, 0.12), fill=255)
    inner = inner.filter(ImageFilter.GaussianBlur(6))
    rim_layer = Image.new("RGBA", (TW, TH), rim + (255,))
    rim_layer.putalpha(Image.fromarray(255 - np.asarray(inner), "L"))
    img.alpha_composite(rim_layer)
    if kind in ("grass", "plains", "swamp"):   # tufts
        d = ImageDraw.Draw(img)
        for _ in range(40):
            x, y = rng.uniform(0.15, 0.85) * TW, rng.uniform(0.15, 0.85) * TH
            c = tuple(int(v * rng.uniform(0.8, 1.15)) for v in field)
            d.line([(x, y), (x - 2, y - 6)], fill=c, width=2)
            d.line([(x, y), (x + 2, y - 5)], fill=c, width=2)
    if kind == "ocean":
        d = ImageDraw.Draw(img)
        for _ in range(14):
            x, y = rng.uniform(0.15, 0.8) * TW, rng.uniform(0.2, 0.8) * TH
            d.arc([x, y, x + 30, y + 10], 200, 340, fill=(120, 180, 225), width=2)
    img.putalpha(mask)
    return img


def _soft_shadow(fig: Image.Image, dx=10, dy=8, blur=8, alpha=0.45) -> Image.Image:
    a = fig.getchannel("A").point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", fig.size, (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", fig.size, (10, 8, 14, 255)), (dx, dy), a)
    return sh.filter(ImageFilter.GaussianBlur(blur))


# ---------------------------------------------------------------- scenes (y up; the hex spans about x, z in -1..1)
def _mountain(s, x, z, r, h, mat="rock", cap=None):
    s.add("cone", (x, 0, z), (x, h, z), r, 0.015, mat=mat)
    s.add("cone", (x + r * 0.35, 0, z + r * 0.2), (x + r * 0.2, h * 0.62, z + r * 0.1), r * 0.55, 0.02, mat=mat, blend=0.05)
    if cap:
        s.add("cone", (x, h * 0.72, z), (x, h + 0.02, z), r * 0.32, 0.03, mat=cap, blend=0.02)


def dang_hun():
    s = Scene()
    _mountain(s, 0.0, -0.1, 0.62, 1.35, "rock_dark", "snow")
    _mountain(s, -0.5, 0.15, 0.36, 0.7, "rock")
    _mountain(s, 0.48, 0.2, 0.32, 0.6, "rock")
    for y, r in ((0.45, 0.6), (0.8, 0.42)):
        s.add("torus", (0, y, -0.1), r, 0.025, mat="violet")
    for x, y, z in ((-0.3, 0.9, 0.3), (0.35, 1.1, 0.1), (0.1, 1.5, 0.2), (-0.5, 0.6, -0.2)):
        s.add("sphere", (x, y, z), 0.06, mat="violet")
    return s, "grass"


def luo_po():
    s = Scene()
    s.add("ellipsoid", (-0.62, 0.0, 0.0), (0.42, 0.6, 0.9), mat="rock")
    s.add("ellipsoid", (0.62, 0.0, 0.0), (0.42, 0.55, 0.9), mat="rock_dark")
    s.add("ellipsoid", (0.0, 0.02, 0.0), (0.3, 0.06, 0.8), mat="mist")
    for x, y, z in ((-0.1, 0.3, 0.4), (0.12, 0.45, 0.0), (-0.05, 0.25, -0.4), (0.18, 0.2, 0.55), (0.0, 0.6, 0.2)):
        s.add("sphere", (x, y, z), 0.055, mat="wisp")
    return s, "plains"


def reverse_flow():
    s = Scene()
    s.add("ellipsoid", (0.2, 0.0, -0.2), (0.75, 0.75, 0.7), mat="rock")
    for i in range(14):   # the river climbs the hill
        t = i / 13
        x = -0.9 + 1.1 * t
        y = 0.04 + 0.66 * t ** 1.4
        z = 0.5 - 0.62 * t
        s.add("ellipsoid", (x, y, z), (0.16, 0.035, 0.12), mat="water")
    s.add("capsule", (0.2, 0.7, -0.12), (0.2, 1.15, -0.12), 0.05, mat="foam")   # it spouts upward at the top
    for x, z in ((-0.5, 0.65), (-0.75, 0.25), (0.6, 0.45)):
        s.add("sphere", (x, 0.06, z), 0.1, mat="rock_dark")
    return s, "grass"


def river_of_time():
    s = Scene()
    for i in range(22):
        t = i / 21
        x = -1.0 + 2.0 * t
        z = 0.35 * math.sin(t * 6.0)
        s.add("ellipsoid", (x, 0.03, z), (0.14, 0.03, 0.17), mat="time")
    rng = _rng("time")
    for _ in range(12):
        x, z = rng.uniform(-0.9, 0.9), rng.uniform(-0.5, 0.5)
        s.add("sphere", (x, rng.uniform(0.15, 0.7), z), 0.03, mat="time")
    s.add("cone", (0.55, 0.05, -0.5), (0.55, 0.32, -0.5), 0.14, 0.01, mat="gold")       # an hourglass on the bank
    s.add("cone", (0.55, 0.6, -0.5), (0.55, 0.33, -0.5), 0.14, 0.01, mat="gold")
    return s, "ash"


def door():
    s = Scene()
    s.add("box", (-0.42, 0.55, 0.0), (0.1, 0.55, 0.1), 0.02, mat="white_stone")
    s.add("box", (0.42, 0.55, 0.0), (0.1, 0.55, 0.1), 0.02, mat="black_stone")
    s.add("box", (0.0, 1.14, 0.0), (0.62, 0.07, 0.14), 0.02, mat="wood")
    s.add("box", (-0.16, 0.55, 0.0), (0.16, 0.5, 0.02), mat="life")
    s.add("box", (0.16, 0.55, 0.0), (0.16, 0.5, 0.02), mat="death")
    for x in (-0.7, 0.7):
        s.add("sphere", (x, 0.08, 0.4), 0.12, mat="rock")
    return s, "plains"


def book_mountain():
    s = Scene()
    rng = _rng("books")
    mats = ["red_book", "blue_book", "green_book", "paper"]
    for layer in range(6):
        r = 0.8 - layer * 0.12
        for k in range(max(1, 7 - layer)):
            a = 2 * math.pi * k / max(1, 7 - layer) + layer
            x, z = math.cos(a) * r * 0.6, math.sin(a) * r * 0.5
            s.add("box", (x, 0.08 + layer * 0.15, z), (0.17, 0.06, 0.12), 0.01, mat=mats[int(rng.integers(0, 4))])
    s.add("capsule", (-0.1, 1.0, 0.0), (0.15, 1.0, 0.0), 0.05, mat="paper")   # an open scroll on the summit
    return s, "grass"


def demon_cave():
    s = Scene()
    s.add("ellipsoid", (0.0, 0.0, -0.1), (0.85, 0.7, 0.75), mat="rock_dark")
    s.add("ellipsoid", (0.0, 0.18, 0.5), (0.26, 0.22, 0.12), mat="cave")
    for x in (-0.07, 0.07):
        s.add("sphere", (x, 0.24, 0.6), 0.03, mat="eye")
    for x, z, h in ((-0.7, 0.4, 0.4), (0.7, 0.35, 0.45), (-0.4, 0.7, 0.3), (0.45, 0.68, 0.32), (0.0, -0.6, 0.5)):
        s.add("cone", (x, 0, z), (x, h, z), 0.06, 0.005, mat="bone")
    return s, "ash"


def dragon_whale():
    s = Scene()
    s.add("ellipsoid", (0.0, 0.08, 0.0), (0.75, 0.22, 0.32), mat="whale")
    s.add("ellipsoid", (0.0, 0.0, 0.1), (0.7, 0.12, 0.28), mat="whale_belly", blend=0.04)
    s.add("cone", (-0.7, 0.1, 0.0), (-1.0, 0.32, 0.0), 0.12, 0.05, mat="whale")          # tail
    for z in (-0.12, 0.12):
        s.add("cone", (0.55, 0.22, z), (0.75, 0.55, z * 1.6), 0.04, 0.01, mat="horn")  # dragon horns
    s.add("capsule", (0.35, 0.25, 0.0), (0.35, 0.8, 0.0), 0.05, mat="foam")             # its spout
    s.add("ellipsoid", (-0.5, 0.02, -0.65), (0.28, 0.1, 0.18), mat="grass")             # a small isle
    return s, "ocean"


def tian_ti():
    s = Scene()
    _mountain(s, 0.0, 0.0, 0.55, 1.6, "rock", "snow")
    for i in range(18):   # the stair spirals up the mountain
        t = i / 17
        a = t * 3.4 * math.pi
        r = 0.5 * (1 - t) + 0.08
        s.add("box", (math.cos(a) * r, 0.05 + t * 1.45, math.sin(a) * r * 0.9 + 0.05), (0.05, 0.015, 0.04), mat="white_stone")
    s.add("torus", (0, 1.25, 0), 0.4, 0.07, mat="cloud")
    s.add("box", (0, 1.68, 0), (0.12, 0.08, 0.04), mat="time")
    return s, "grass"


def lang_ya():
    s = Scene()
    s.add("cone", (0, 0.55, 0), (0, 0.15, 0), 0.6, 0.05, mat="soil")                   # floating island
    s.add("ellipsoid", (0, 0.58, 0), (0.62, 0.08, 0.55), mat="grass")
    s.add("box", (0.05, 0.78, -0.05), (0.2, 0.14, 0.16), 0.02, mat="wood")             # pavilion
    s.add("cone", (0.05, 0.92, -0.05), (0.05, 1.2, -0.05), 0.34, 0.02, mat="roof_red")
    s.add("sphere", (-0.35, 0.72, 0.2), 0.12, mat="ember")                              # the refiners' furnace
    for x, z in ((-0.6, 0.4), (0.6, 0.3), (0.0, 0.6)):
        s.add("ellipsoid", (x, 0.12, z), (0.28, 0.07, 0.16), mat="cloud")
    return s, "grass"


def imperial_court():
    s = Scene()
    for x, z, r in ((0, -0.1, 0.36), (-0.55, 0.3, 0.22), (0.55, 0.3, 0.22), (-0.4, -0.45, 0.2), (0.45, -0.45, 0.2)):
        s.add("ellipsoid", (x, 0.0, z), (r, r * 0.9, r), mat="yurt")
        s.add("cone", (x, r * 0.8, z), (x, r * 0.8 + 0.12, z), 0.05, 0.01, mat="gold")
    s.add("capsule", (0, 0.3, -0.1), (0, 0.95, -0.1), 0.02, mat="wood")
    s.add("box", (0.12, 0.85, -0.1), (0.12, 0.07, 0.01), mat="banner")
    return s, "grass"


def hu_immortal():
    s = Scene()
    s.add("ellipsoid", (0, 0, -0.15), (0.8, 0.35, 0.65), mat="grass")
    s.add("box", (0.0, 0.42, -0.2), (0.15, 0.12, 0.12), 0.02, mat="wood")               # shrine
    s.add("cone", (0.0, 0.53, -0.2), (0.0, 0.75, -0.2), 0.26, 0.02, mat="roof_red")
    for x, z in ((-0.55, 0.15), (0.55, 0.1), (-0.3, -0.45), (0.4, -0.5)):              # peach blossom trees
        s.add("capsule", (x, 0.2, z), (x, 0.42, z), 0.03, mat="wood")
        s.add("sphere", (x, 0.5, z), 0.16, mat="blossom")
    s.add("ellipsoid", (0.25, 0.32, 0.35), (0.16, 0.08, 0.07), mat="fox")               # the white fox
    s.add("sphere", (0.39, 0.38, 0.35), 0.06, mat="fox")
    s.add("capsule", (0.1, 0.32, 0.35), (-0.05, 0.42, 0.42), 0.035, mat="fox")
    return s, "grass"


def azure_wall():
    s = Scene()
    rng = _rng("azure")
    for i in range(11):   # a curtain of water, its crest rising and falling, breaking into foam
        x = -0.95 + 1.9 * i / 10
        h = 0.95 + 0.25 * math.sin(i * 1.3)
        s.add("ellipsoid", (x, h / 2, 0.0), (0.16, h / 2 + 0.05, 0.16), mat="water", blend=0.08)
        for _ in range(2):
            s.add("sphere", (x + rng.uniform(-0.08, 0.08), h + rng.uniform(-0.02, 0.08), rng.uniform(-0.08, 0.1)),
                  rng.uniform(0.04, 0.07), mat="foam")
    for _ in range(8):
        s.add("sphere", (rng.uniform(-0.9, 0.9), 0.04, rng.uniform(0.2, 0.4)), 0.05, mat="foam")
    return s, "rock"


def flame_wall():
    s = Scene()
    rng = _rng("flame")
    for i in range(9):
        x = -0.9 + 1.8 * i / 8
        h = rng.uniform(0.7, 1.25)
        s.add("cone", (x, 0, rng.uniform(-0.2, 0.2)), (x, h, 0), 0.16, 0.01, mat="ember")
        s.add("cone", (x, 0, 0.12), (x, h * 0.6, 0.12), 0.09, 0.01, mat="flame")
    return s, "ash"


def miasma_wall():
    s = Scene()
    rng = _rng("miasma")
    for _ in range(10):
        s.add("ellipsoid", (rng.uniform(-0.85, 0.85), rng.uniform(0.15, 0.6), rng.uniform(-0.4, 0.4)),
              (rng.uniform(0.2, 0.32), rng.uniform(0.15, 0.25), rng.uniform(0.2, 0.3)), mat="miasma", blend=0.08)
    for _ in range(6):
        s.add("sphere", (rng.uniform(-0.8, 0.8), rng.uniform(0.5, 0.9), rng.uniform(-0.3, 0.3)), 0.05, mat="toxic")
    for x in (-0.65, 0.2, 0.7):
        s.add("capsule", (x, 0, 0.45), (x + 0.08, 0.7, 0.4), 0.035, mat="dead_wood")
        s.add("capsule", (x + 0.06, 0.5, 0.42), (x + 0.25, 0.65, 0.4), 0.02, mat="dead_wood")
    return s, "swamp"


def licorice_wall():
    s = Scene()
    rng = _rng("licorice")
    for _ in range(14):   # a wall of giant tangled roots
        x0, x1 = rng.uniform(-1, 1), rng.uniform(-1, 1)
        s.add("capsule", (x0, rng.uniform(0, 0.3), rng.uniform(-0.3, 0.3)),
              (x1, rng.uniform(0.5, 1.1), rng.uniform(-0.3, 0.3)), rng.uniform(0.05, 0.1),
              mat="root" if rng.random() > 0.4 else "root_dark", blend=0.03)
    return s, "soil" if False else "plains"


def sage_wall():
    s = Scene()
    rng = _rng("sage")
    for i in range(6):
        x = -0.85 + 1.7 * i / 5
        s.add("box", (x, 0.45, rng.uniform(-0.1, 0.1)), (0.15, rng.uniform(0.35, 0.6), 0.2), 0.04, mat="rock")
        s.add("box", (x, 0.4, 0.22), (0.05, 0.08, 0.005), mat="rune")
    return s, "rock"


REALMS = {"Dang Hun Mountain": dang_hun, "Luo Po Valley": luo_po, "Reverse Flow River": reverse_flow,
          "River of Time": river_of_time, "Door of Life and Death": door, "Book Mountain": book_mountain,
          "Crazed Demon Cave": demon_cave, "Dragon Whale Paradise": dragon_whale, "Tian Ti Mountain": tian_ti,
          "Lang Ya Blessed Land": lang_ya, "Imperial Court Blessed Land": imperial_court,
          "Hu Immortal Blessed Land": hu_immortal}
WALLS = {"Azure Water Wall": azure_wall, "Raging Flame Wall": flame_wall, "Miasma Wall": miasma_wall,
         "Licorice Wall": licorice_wall, "Sage Wall": sage_wall}


def tile(name: str) -> dict[str, Image.Image]:
    """{"HexaRealm": 64x56, "FantasyHex": 32x28}"""
    scene, kind = (REALMS.get(name) or WALLS[name])()
    out = render(scene, mats=MATS, outline=(28, 22, 30), glow=0.8, **CAM)
    fig = out["base"]
    im = ground(kind, name)
    im.alpha_composite(_soft_shadow(fig))
    im.alpha_composite(fig)
    mask = Image.new("L", (TW, TH), 0)
    ImageDraw.Draw(mask).polygon(_hex(TW, TH, 0.0), fill=255)
    a = np.minimum(np.asarray(im.getchannel("A")), np.asarray(mask))
    im.putalpha(Image.fromarray(a.astype(np.uint8), "L"))
    return {"HexaRealm": im.resize((64, 56), Image.LANCZOS), "FantasyHex": im.resize((32, 28), Image.LANCZOS)}
