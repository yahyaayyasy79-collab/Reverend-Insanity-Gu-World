"""Attack animations (Unciv: <unitset>/Units/<unit type or unit name>-attack-<n>.png, played over the unit that takes
the damage, keyed by the ATTACKER's type or name [docs Creating-a-custom-tileset.md, src BattleTableHelpers]).
Pixel-art frames: drawn on a 32x32 grid, scaled 3x with nearest-neighbour to match the AbsoluteUnits unit set."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

GRID, SCALE = 32, 3


def frame():
    im = Image.new("RGBA", (GRID, GRID), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def up(im):
    return im.resize((GRID * SCALE, GRID * SCALE), Image.NEAREST)


def ring(d, cx, cy, r, col, w=1):
    for a in range(0, 360, 4):
        for k in range(w):
            x = cx + (r - k) * math.cos(math.radians(a)); y = cy + (r - k) * math.sin(math.radians(a))
            d.point((round(x), round(y)), fill=col)


def crescent_px(d, cx, cy, r, cut, angle, col):
    """Pixel crescent: points inside r and outside the offset circle."""
    ox, oy = cut * math.cos(math.radians(angle)), cut * math.sin(math.radians(angle))
    for y in range(GRID):
        for x in range(GRID):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and (x - cx - ox) ** 2 + (y - cy - oy) ** 2 > (r * 0.9) ** 2:
                d.point((x, y), fill=col)


MOON = [(235, 240, 255, 255), (170, 195, 255, 255), (110, 140, 230, 200)]
EARTH = [(255, 245, 220, 255), (240, 170, 70, 255), (150, 90, 40, 220)]
VOLT = [(255, 255, 220, 255), (120, 200, 255, 255), (60, 90, 255, 210)]
ESSENCE = [(220, 255, 230, 255), (90, 200, 130, 255), (40, 120, 80, 200)]  # rank-one essence: green copper


def moon_blade():
    """A moon blade sweeps across the target and shatters into moonlight motes."""
    out = []
    for k, (cx, cy, r) in enumerate(((6, 12, 9), (13, 14, 11), (20, 16, 11))):
        im, d = frame()
        crescent_px(d, cx, cy, r + 1, 5, 180, MOON[2])
        crescent_px(d, cx, cy, r, 5, 180, MOON[1])
        crescent_px(d, cx + 1, cy, r - 2, 5, 180, MOON[0])
        for t in range(k):                                       # trailing motes
            d.point((cx - 8 - 3 * t, cy + 6 - 2 * t), fill=MOON[1])
        out.append(up(im))
    im, d = frame()
    for a in range(0, 360, 30):                                  # shatter
        r = 8 + (a % 60) / 15
        d.rectangle((round(16 + r * math.cos(math.radians(a))), round(16 + r * math.sin(math.radians(a))),
                     round(16 + r * math.cos(math.radians(a))) + 1, round(16 + r * math.sin(math.radians(a))) + 1), fill=MOON[a % 90 // 30])
    out.append(up(im))
    return out


def boar_charge():
    """The strength of boars slams down: dust, impact star, shock rings."""
    out = []
    im, d = frame()
    for x, y in ((8, 24), (12, 26), (20, 25), (24, 23), (16, 27)):
        d.rectangle((x, y, x + 1, y + 1), fill=EARTH[2])
    d.polygon([(10, 6), (16, 14), (22, 6), (16, 10)], fill=EARTH[1])   # tusks coming down
    out.append(up(im))
    im, d = frame()
    pts = []
    for k in range(16):
        r = 12 if k % 2 == 0 else 5
        a = math.radians(k * 22.5)
        pts.append((16 + r * math.cos(a), 17 + r * math.sin(a)))
    d.polygon(pts, fill=EARTH[1]); d.ellipse((13, 14, 19, 20), fill=EARTH[0])
    out.append(up(im))
    for r in (9, 13):
        im, d = frame()
        ring(d, 16, 18, r, EARTH[1], 2); ring(d, 16, 18, r - 3, EARTH[2], 1)
        out.append(up(im))
    return out


def lightning_bite():
    """A lightning wolf's strike: a bolt from above, a flash, crackling sparks."""
    out = []
    path = [(18, 0), (13, 8), (19, 12), (12, 21), (17, 24), (14, 31)]
    im, d = frame()
    d.line(path[:3], fill=VOLT[1], width=1)
    out.append(up(im))
    im, d = frame()
    d.line(path, fill=VOLT[2], width=3); d.line(path, fill=VOLT[1], width=2); d.line(path, fill=VOLT[0], width=1)
    out.append(up(im))
    im, d = frame()
    d.ellipse((6, 14, 26, 30), fill=(120, 200, 255, 120)); d.line(path[2:], fill=VOLT[0], width=2)
    out.append(up(im))
    im, d = frame()
    for x, y in ((6, 14), (24, 12), (9, 26), (26, 24), (16, 8)):
        d.line([(x, y), (x + 2, y + 2), (x + 1, y + 4)], fill=VOLT[1], width=1)
    out.append(up(im))
    return out


def essence_burst():
    """A rank-one Gu Master's strike: a burst of green-copper primeval essence."""
    out = []
    for r in (4, 8, 12):
        im, d = frame()
        d.ellipse((16 - r, 16 - r, 16 + r, 16 + r), fill=ESSENCE[2])
        d.ellipse((16 - r * 0.6, 16 - r * 0.6, 16 + r * 0.6, 16 + r * 0.6), fill=ESSENCE[1])
        d.ellipse((16 - r * 0.25, 16 - r * 0.25, 16 + r * 0.25, 16 + r * 0.25), fill=ESSENCE[0])
        out.append(up(im))
    return out


ANIMS = {"Moon Gu Master": moon_blade, "Strength Gu Master": boar_charge, "Beast": lightning_bite,
         "Gu Master": essence_burst}
