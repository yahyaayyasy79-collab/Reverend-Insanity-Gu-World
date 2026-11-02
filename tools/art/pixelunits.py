"""The mod's units as pixel-art sprites in the style of the HexaRealm (64x56) and FantasyHex (32x28) unit sets (the
user, 2026-11-02: "redo every unit, better and canon, in the HexaRealm / FantasyHex pixel style").

Each sprite is drawn natively at both sizes from one scene written in HexaRealm pixels (tools/art/pixeltiles.py), as
the tilesets' own units are: a figure and a soft ground shadow on a transparent hex-sized canvas, soldiers on the right
half and civilians on the left so two units on one tile do not overlap. There is no grass frame on the map: the engine
draws a unit image over the whole hex [src TileLayerUnitSprite], so a frame would hide the terrain (the user agreed);
the portraits are the dioramas, a unit standing on the tilesets' grass hex.

Clan colours: the robe is a greyscale layer <name>-1 that Unciv tints with the nation's inner colour, the trim a layer
<name>-2 tinted with its outer colour [src TileLayerUnitSprite, ImageGetter.getLayeredImageColored].
Canon cues: rank shows as essence colour (green copper, red iron, white silver, yellow gold, purple crystal; immortal
green grape, red date, white lychee, yellow apricot) and as regalia; Gu Yue holds the Moonlight Gu's crescent, Bai the
Stream Gu's water, Xiong and the strength path a beast's phantom, Wu the wind; the Thunder Crown Wolf wears a crown of
gold fur (docs/LORE_MAPPING.md). Every shape is built here; nothing is traced or copied.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from .pixeltiles import (ASH, BLACK, BONE, CLOUD, EARTH, GOLD, JADE, LEAF, MIASMA, ROCK, ROOF, STONE, WATER, WOOD,
                         Canvas, _edge, _nb, _rng)

SKIN = ((86, 46, 32), (170, 106, 76), (220, 158, 118), (238, 188, 148), (250, 214, 180))
PALE = ((54, 64, 58), (110, 128, 116), (150, 170, 156), (184, 204, 188), (214, 232, 216))   # a zombie's skin
HAIR = ((8, 6, 10), (22, 18, 26), (38, 32, 44), (60, 52, 68), (92, 82, 100))
GREY = ((60, 60, 64), (146, 146, 152), (200, 200, 206), (234, 234, 238), (255, 255, 255))  # tinted by the engine
CLOTH = ((40, 34, 30), (74, 62, 54), (104, 90, 78), (134, 118, 102), (168, 150, 130))       # untinted plain cloth
STRAW = ((96, 72, 26), (166, 132, 58), (206, 174, 90), (232, 206, 128), (248, 232, 176))
WOLF = ((30, 40, 66), (58, 76, 114), (92, 116, 158), (138, 164, 202), (200, 218, 242))
BEAST = ((40, 26, 20), (74, 48, 34), (108, 72, 50), (146, 104, 72), (186, 146, 104))
OUTLINE = (20, 14, 26)
# primeval and immortal essence by rank (canon): green copper, red iron, white silver, yellow gold, purple crystal,
# green grape, red date, white lychee, yellow apricot
ESSENCE = {1: (110, 220, 150), 2: (240, 90, 70), 3: (235, 240, 255), 4: (255, 214, 90), 5: (190, 120, 255),
           6: (170, 235, 110), 7: (215, 60, 55), 8: (250, 248, 236), 9: (255, 196, 70)}
MOON = (190, 230, 255)
SOLDIER, CIVILIAN = 48.0, 14.0   # body centre: soldiers on the right half of the hex, civilians on the left
FEET = 40.0


def _lift(c, f):
    return tuple(int(min(255, max(0, v * f))) for v in c)


def _ramp(c):
    """A five-tone ramp around one colour."""
    return (_lift(c, 0.3), _lift(c, 0.62), c, _lift(c, 1.18), _lift(c, 1.4))


class Sprite(Canvas):
    """A unit sprite: a base image, two greyscale civ layers, semi-transparent shadow and glows."""

    def __init__(self, tileset: str, top: int = 0):
        super().__init__(tileset, top)
        self.ok[:] = True
        self.own = np.zeros((self.h, self.w), np.int8)       # 0 base, 1 inner-colour layer, 2 outer-colour layer
        self.op = np.zeros((self.h, self.w), np.float32)     # opacity
        self.solid = np.zeros((self.h, self.w), bool)        # opaque figure pixels (get the outline)

    def put(self, m, col, layer=0):
        col = np.asarray(col, np.float32)
        self.rgb[m] = col if col.ndim == 1 else col[m]
        self.own[m], self.op[m] = layer, 1.0
        self.solid |= m
        self.a |= m

    def shade(self, m, t, ramp, layer=0):
        self.put(m, np.asarray(ramp, np.float32)[np.clip(t, 0, 4)], layer)

    def flat(self, m, ramp, tone=2, layer=0):
        self.shade(m, np.full(m.shape, tone), ramp, layer)

    def body(self, m, ramp, layer=0, edge=False):
        """Lit from the left: light third, mid third, shadowed third, darker bottom row; `edge` outlines the part."""
        ys, xs = np.nonzero(m)
        if not len(xs):
            return
        x0, x1 = xs.min(), xs.max() + 1
        u = (np.arange(self.w) + 0.5 - x0) / max(1, x1 - x0)
        t = np.broadcast_to(np.where(u < 0.38, 3, np.where(u < 0.72, 2, 1))[None, :], m.shape).copy()
        t[~_nb(m, 0, 1) & (t > 1)] -= 1
        if edge:
            t[_edge(m) & ~(~_nb(m, 0, -1) & (u[None, :] < 0.5))] = 0
        self.shade(m, t, ramp, layer)

    def cloth(self, m, ramp, layer=0, folds=(0.46, 0.64), below=None):
        """A robe: a lit left side, a shadowed right, fold lines below the sash, a darker hem."""
        ys, xs = np.nonzero(m)
        if not len(xs):
            return
        x0, x1 = xs.min(), xs.max() + 1
        u = np.broadcast_to(((np.arange(self.w) + 0.5 - x0) / max(1, x1 - x0))[None, :], m.shape)
        t = np.where(u < 0.3, 3, np.where(u < 0.74, 2, 1))
        if self.k == 1 and below is not None:
            px = 1 / max(1, x1 - x0)
            for f in folds:
                t[(np.abs(u - f) < px * 0.6) & (self.Y > below)] -= 1
        t[~_nb(m, 0, 1)] = np.maximum(t[~_nb(m, 0, 1)] - 1, 0)
        t[~_nb(m, 0, -1) & (u < 0.5)] = 4
        self.shade(m, np.clip(t, 0, 4), ramp, layer)

    def round(self, m, ramp, layer=0):
        self.shade(m, self.ball(m, outline=False), ramp, layer)

    def glow(self, m, col, a=0.45):
        """Light behind the figure: tints only what is still transparent or translucent."""
        m = m & ~self.solid
        new = m & (self.op < a)
        self.rgb[new] = np.asarray(col, np.float32)
        self.op[new] = a
        self.own[new] = 0
        self.a |= new

    def shadow(self, cx, cy, rx, ry, a=0.3):
        m = self.ellipse(cx, cy, rx, ry) & (self.op == 0)
        self.rgb[m] = 0
        self.op[m] = a
        self.a |= m

    def light(self, x, y, col):
        """A one-pixel spark that ignores the outline (drawn after it)."""
        m = self.spot(x, y)
        self.rgb[m], self.op[m], self.own[m] = col, 1.0, 0
        self.a |= m

    def light_mask(self, m, col):
        self.rgb[m], self.op[m], self.own[m] = col, 1.0, 0
        self.a |= m

    def outline(self):
        ring = np.zeros_like(self.solid)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ring |= _nb(self.solid, dx, dy)
        ring &= ~self.solid
        self.rgb[ring], self.op[ring], self.own[ring] = OUTLINE, 1.0, 0
        self.a |= ring

    def layers(self) -> dict[str, Image.Image]:
        out = {}
        for key, which in (("base", 0), ("layer1", 1), ("layer2", 2)):
            im = np.zeros((self.h, self.w, 4), np.uint8)
            m = self.a & (self.own == which)
            im[m, :3] = np.clip(self.rgb[m] + 0.5, 0, 255)
            im[m, 3] = np.clip(self.op[m] * 255 + 0.5, 0, 255)
            out[key] = Image.fromarray(im, "RGBA")
        return out


# ---------------------------------------------------------------- people
def person(s: Sprite, cx, feet=FEET, *, arm="raise", robe=GREY, trim=GREY, sash=None, skin=SKIN, hair="bun",
           cape=False, mantle=False, cap=False, pouch=False, band=False, bare=False, tall=1.0, legs=True,
           float_=False, hem=None):
    """A Gu Master in a cross-collared robe with wide sleeves, three-quarter front view. `robe`/`trim` GREY means the
    civ colour layers (-1 inner, -2 outer); any other ramp is a fixed colour. Returns the casting hand's position."""
    small = s.k < 1

    def P(dx, dy):
        return cx + dx, feet + dy * tall

    def poly(pts):
        return s.poly([P(x, y) for x, y in pts])

    def rect(x0, y0, x1, y1):
        return s.rect(cx + x0, feet + y0 * tall, cx + x1, feet + y1 * tall)

    def ell(x, y, rx, ry):
        return s.ellipse(cx + x, feet + y * tall, rx, ry * tall)

    rl, tl = (1 if robe is GREY else 0), (2 if trim is GREY else 0)
    sash_ramp, sl = (GREY, 1) if sash is GREY else ((sash, 0) if sash is not None else (trim, tl))
    edge = not small
    w = 1.2 if bare else 1.0
    bottom = -0.5 if float_ else -5
    if cape:   # a long cape behind the shoulders
        s.body(poly([(-6, -22.5), (6, -22.5), (8.6, bottom + 2), (-8.6, bottom + 2)]), trim, tl)
    if legs and not float_:
        for x0 in (-3.0, 0.6):
            s.flat(rect(x0, -6, x0 + 2.4, -0.5), CLOTH, 1)
            s.flat(rect(x0 - 0.5, -1.2, x0 + 2.6, 0.6), BLACK, 1)
    skirt = [(-5 * w, -22.6), (5 * w, -22.6), (6.8 * w, bottom), (-6.8 * w, bottom)]
    if hem == "torn":
        skirt = skirt[:2] + [(6.8, bottom), (4.5, bottom - 2.2), (2.6, bottom), (0.4, bottom - 2.4), (-1.8, bottom),
                             (-4, bottom - 2), (-6.8, bottom)]
    s.cloth(poly(skirt), robe, rl, below=feet - 13 * tall)
    if bare:   # the strength path: a vest open on a narrow V of bare chest
        s.flat(poly([(-2.2, -22.4), (2.2, -22.4), (0, -16)]), skin, 2)
    else:
        s.flat(poly([(-2.8, -22.6), (2.8, -22.6), (0, -18.6)]), skin, 3)
        if not small:
            s.flat(s.line([P(-2.6, -22.4), P(2.6, -15.2)], 1.1), trim, 2, tl)   # the lapel, right over left
    s.flat(rect(-5.9 * w, -14.6, 5.9 * w, -12.9), sash_ramp, 2, sl)
    if pouch:
        s.flat(rect(2.6, -13.2, 5.2, -10.2), EARTH, 2)
    if mantle:
        s.body(poly([(-6.6, -23.4), (6.6, -23.4), (7.6, -18.4), (-7.6, -18.4)]), trim, tl, edge=edge)
    if bare:
        arm_ramp, arm_layer = skin, 0
        s.body(poly([(-5, -22.6), (-8.8, -21.4), (-10, -14.6), (-7.2, -13.6), (-6.2, -18.6)]), skin, edge=edge)
        s.round(ell(-8.6, -13, 1.9, 1.8), skin)
    else:   # the hanging arm in a wide sleeve that flares at the cuff
        arm_ramp, arm_layer = robe, rl
        s.body(poly([(-4.6, -22.2), (-7.4, -19.6), (-9.8, -10.8), (-5.4, -10.2), (-4.4, -17.5)]), robe, rl, edge=edge)
        s.round(ell(-7.4, -9.6, 1.3, 1.2), skin)
    if arm == "raise":
        s.body(poly([(4.6, -22.2), (8.4, -23.2), (10.6, -28.4), (8.4, -29.6), (6.8, -25.6), (6.6, -19.2), (4.8, -19.6)]),
               arm_ramp, arm_layer, edge=edge)
        hand = (9.6, -29.6)
    elif arm == "forward":   # reaching ahead (the zombie's stiff arms, a settler's pull)
        s.body(poly([(4.4, -22.4), (11.6, -21.6), (11.6, -18.6), (4.6, -18.8)]), arm_ramp, arm_layer, edge=edge)
        hand = (12.4, -20)
    elif arm == "fist":   # a flexed arm: the upper arm out, the forearm up
        s.body(poly([(4.6, -22.6), (10.6, -21.4), (10.8, -18.2), (5.2, -18.6)]), skin, edge=edge)
        s.body(poly([(8.6, -21.6), (11.6, -21.4), (12.2, -28), (9.2, -28.4)]), skin, edge=edge)
        hand = (10.8, -29.4)
    else:   # "staff": the hand holds a staff upright
        s.body(poly([(4.4, -22), (7.4, -21.6), (8.8, -14.6), (6, -14), (5, -18)]), arm_ramp, arm_layer, edge=edge)
        hand = (8.2, -14)
    s.round(ell(hand[0], hand[1], 1.6 if bare else 1.4, 1.5 if bare else 1.3), skin)
    s.round(ell(0, -27.2, 3.9, 4.1), skin)
    hr = BONE if hair == "white" else HAIR
    if hair in ("bun", "long", "white"):
        cap_m = (ell(0, -28.9, 4.2, 3.0) & (s.Y < feet - 27.6 * tall)) | rect(-4.1, -29, -2.9, -24.2) | rect(2.9, -29, 4.1, -24.2)
        s.shade(cap_m, np.where(s.X < cx - 0.5, 3, 1), hr)
        if hair in ("long", "white"):
            s.body(rect(-4.6, -27.8, -3.0, -18.6) | rect(3.0, -27.8, 4.6, -18.6), hr)
        if hair == "white":   # an elder's beard
            s.flat(poly([(-2.2, -25), (2.2, -25), (0.6, -19.6), (-0.6, -19.6)]), BONE, 3)
        if cap:   # rank four and up: a guan cap of gold over the topknot
            s.round(rect(-1.9, -35, 1.9, -31.2), GOLD)
            s.flat(rect(-2.8, -31.8, 2.8, -30.6), GOLD, 1)
        else:
            s.round(ell(0, -33, 2.0, 1.7), hr)
            s.flat(rect(-1.2, -31.8, 1.3, -31), trim, 2, tl)
    elif hair == "wild":   # loose, spiky demonic hair
        s.shade(poly([(-4.8, -25.4), (-5.6, -31.4), (-3.2, -30), (-2.2, -34.4), (0.2, -31), (2.6, -34.2), (3.4, -30),
                      (5.8, -31.4), (4.8, -25.4), (4, -28.6), (-4, -28.6)]), np.where(s.X < cx, 3, 1), HAIR)
    elif hair == "hat":   # the lone cultivator's wide bamboo hat
        s.round(poly([(-9, -28.8), (0, -35), (9, -28.8), (6.4, -27.8), (-6.4, -27.8)]), STRAW)
        s.flat(rect(-6.4, -29.2, 6.4, -28.2), STRAW, 1)
    elif hair == "straw":   # a mortal's conical straw hat
        s.round(poly([(-7, -28.6), (0, -34.2), (7, -28.6), (5, -27.8), (-5, -27.8)]), STRAW)
    if band:
        s.flat(rect(-3.9, -29.6, 3.9, -28.7), trim, 2, tl)
    return cx + hand[0], feet + hand[1] * tall


def eyes(s: Sprite, cx, feet=FEET, tall=1.0, col=(34, 22, 22)):
    for ex in (-1.4, 1.4):
        s.light(cx + ex, feet - 26.8 * tall, col)


def gu_glow(s: Sprite, x, y, col, r=3.4):
    s.glow(s.ellipse(x, y, r, r), col, 0.3)
    s.glow(s.ellipse(x, y, r * 0.62, r * 0.62), _lift(col, 1.1), 0.55)


def held_gu(s: Sprite, x, y, rank, path):
    """The Gu in the casting hand: the Moonlight Gu's crescent, the Stream Gu's water, a wind, or an essence orb."""
    if path == "Moon":
        gu_glow(s, x + 1, y - 3.4, MOON, 4.6)
        s.put(s.ellipse(x + 1, y - 3.4, 3.2, 3.2) & ~s.ellipse(x + 2.6, y - 4.4, 2.6, 2.6), (226, 246, 255))
    elif path == "Water":
        gu_glow(s, x, y - 2.4, (120, 200, 255), 4.4)
        s.put(s.line([(x - 2.6, y + 3.6), (x + 2.6, y + 1.2), (x - 2.2, y - 1.4), (x + 2, y - 3.8), (x, y - 6)], 1.3),
              (150, 214, 255))
    elif path == "Wind":
        for i, r in enumerate((3.6, 5.6)):
            arc = s.ellipse(x, y - 1.5, r, r * 0.55) & ~s.ellipse(x, y - 1.5, r - 1.2, r * 0.55 - 1.2) & (s.Y < y - 1 + i)
            s.put(arc, (214, 246, 226))
    else:
        col = ESSENCE[min(rank, 9)]
        gu_glow(s, x, y - 2.6, col, 3.4 + 0.3 * min(rank, 6))
        s.put(s.ellipse(x, y - 2.6, 1.5, 1.5), _lift(col, 1.12))


def phantom(s: Sprite, cx, cy, kind):
    """The strength path's beast phantom over the shoulders: a bear (Xiong's Bear Strength Gu) or a boar (the
    Black-White Boar Gu)."""
    col, dark = ((176, 112, 66), (255, 214, 120)) if kind == "bear" else ((206, 206, 216), (255, 120, 90))
    head = s.ellipse(cx, cy, 8.5, 7.4)
    if kind == "bear":
        head |= s.ellipse(cx - 5.6, cy - 5.4, 2.6, 2.6) | s.ellipse(cx + 5.6, cy - 5.4, 2.6, 2.6)
        snout = s.ellipse(cx, cy + 2.6, 3, 2.2)
    else:
        head |= (s.poly([(cx - 6.5, cy - 3), (cx - 5, cy - 9), (cx - 2.5, cy - 4.5)])
                 | s.poly([(cx + 6.5, cy - 3), (cx + 5, cy - 9), (cx + 2.5, cy - 4.5)]))
        snout = s.ellipse(cx, cy + 3, 3.4, 2.4)
    s.glow(_edge(head), _lift(col, 0.6), 0.75)
    s.glow(head, col, 0.55)
    s.glow(snout, _lift(col, 1.25), 0.7)
    for ex in (-3, 3):
        s.glow(s.spot(cx + ex, cy - 1), dark, 1.0)
    if kind == "boar":
        for tx in (-3.6, 3.6):
            s.glow(s.line([(cx + tx, cy + 4), (cx + tx * 1.25, cy + 1.2)], 1), (250, 250, 255), 0.8)


def gu_master(rank: int, path: str | None = None, beast="boar"):
    """Ranks one to five. Regalia: two adds a pouch and headband, three a mantle, four a guan cap and an orbiting jade
    Gu, five a cape, a gold hairpin and a second Gu."""
    def draw(s: Sprite):
        cx = SOLDIER
        s.shadow(cx, FEET + 0.4, 8.5, 2.2)
        if path == "Strength" and s.k == 1:   # at 32 px the phantom would only be a blot
            phantom(s, cx - 6, FEET - 31, beast)
        hand = person(s, cx, bare=path == "Strength", arm="fist" if path == "Strength" else "raise", pouch=rank >= 2,
                      band=rank == 2, mantle=rank >= 3, cap=rank >= 4, cape=rank >= 5)
        s.outline()
        eyes(s, cx)
        if path == "Strength":
            gu_glow(s, hand[0], hand[1], ESSENCE[rank], 3.2)
        else:
            held_gu(s, hand[0] + 0.6, hand[1] - 0.6, rank, path)
        if rank >= 4:
            s.light(cx - 9.6, FEET - 31, (150, 236, 200))
        if rank >= 5:
            s.light(cx + 9, FEET - 36, ESSENCE[5])
            s.light(cx - 1.6, FEET - 34.6, GOLD[4])
        if path == "Wind":
            for y, x0 in ((FEET - 2.6, cx - 12), (FEET - 10, cx + 7)):
                s.put(s.line([(x0, y), (x0 + 3, y - 1.2), (x0 + 6, y)], 1), (214, 246, 226))
    return draw


def ribbon(s: Sprite, cx, cy, col, phase=0.0, r=10.0):
    """An essence ribbon curving around an immortal."""
    pts = [(cx + r * math.cos(t), cy + 0.42 * r * math.sin(t) + 6 * math.sin(t * 0.5 + phase))
           for t in np.linspace(0.3 + phase, 2 * math.pi - 0.6 + phase, 24)]
    s.glow(s.line(pts, 3.2), col, 0.4)
    s.glow(s.line(pts, 1.4), _lift(col, 1.2), 0.95)


def gu_immortal(rank: int):
    """Ranks six to eight float on a wisp of cloud in long robes, ribbons of their immortal essence around them; seven
    adds a halo, eight (a grotto-heaven's master) a second one."""
    def draw(s: Sprite):
        cx, feet = SOLDIER, FEET - 4
        col = ESSENCE[rank]
        s.shadow(cx, FEET + 0.4, 6.5, 1.8, a=0.2)
        for i in range(1 if rank == 6 else 2 if rank == 7 else 3):
            ribbon(s, cx, feet - 16, col, phase=i * 2.1, r=10 + 1.5 * i)
        if rank >= 7:
            s.glow(s.ellipse(cx, feet - 28, 7.6, 7.6) & ~s.ellipse(cx, feet - 28, 6.2, 6.2), _lift(col, 1.2), 0.9)
        if rank >= 8:
            s.glow(s.ellipse(cx, feet - 28, 10.2, 10.2) & ~s.ellipse(cx, feet - 28, 9.0, 9.0), col, 0.6)
        hand = person(s, cx, feet, float_=True, hair="long", mantle=True, cape=True, cap=True)
        for x, r in ((cx - 6, 3.8), (cx + 1, 4.8), (cx + 7.5, 3.6)):
            s.round(s.ellipse(x, feet + 0.8, r, r * 0.62), CLOUD)
        s.outline()
        eyes(s, cx, feet)
        gu_glow(s, hand[0] + 0.6, hand[1] - 2.6, col, 4.6)
        s.put(s.ellipse(hand[0] + 0.6, hand[1] - 2.6, 1.7, 1.7), _lift(col, 1.1))
    return draw


def venerable(s: Sprite):
    """Rank nine: a towering figure in a yellow-apricot aura, a crown of gold, dao marks orbiting."""
    cx, feet = SOLDIER - 1, FEET - 3
    col = ESSENCE[9]
    s.shadow(cx, FEET + 0.4, 7, 1.8, a=0.22)
    s.glow(s.ellipse(cx, feet - 22, 15, 21), col, 0.22)
    s.glow(s.ellipse(cx, feet - 22, 11, 17), col, 0.3)
    for i in range(3):
        ribbon(s, cx, feet - 18, col, phase=i * 2.1, r=12 + 1.4 * i)
    hand = person(s, cx, feet, float_=True, hair="long", mantle=True, cape=True, cap=True, tall=1.18)
    s.outline()
    eyes(s, cx, feet, 1.18)
    gu_glow(s, hand[0] + 0.6, hand[1] - 3, col, 5.4)
    s.put(s.ellipse(hand[0] + 0.6, hand[1] - 3, 2.0, 2.0), (255, 236, 170))
    for x, y in ((cx - 13, feet - 34), (cx + 12, feet - 40), (cx - 15, feet - 14), (cx + 15, feet - 18)):   # dao marks
        s.light(x, y, (255, 240, 180))
        if s.k == 1:
            s.light(x + 1, y, col)
            s.light(x, y + 1, col)


def lone_gu_master(s: Sprite):
    """A lone cultivator (散修): a bamboo hat, a travelling robe and bundle, a staff, a red-iron Gu at hand."""
    cx = SOLDIER
    s.shadow(cx, FEET + 0.4, 8.5, 2.2)
    s.body(s.rect(cx - 8.6, FEET - 24, cx - 3.4, FEET - 15), CLOTH)   # the bundle on his back
    hand = person(s, cx, arm="staff", robe=CLOTH, trim=CLOTH, sash=GREY, hair="hat")
    s.flat(s.rect(hand[0] - 0.6, FEET - 32, hand[0] + 0.7, FEET + 0.4), WOOD, 2)
    s.outline()
    eyes(s, cx)
    gu_glow(s, cx - 9, FEET - 12, ESSENCE[2], 2.8)
    s.put(s.spot(cx - 9, FEET - 12), _lift(ESSENCE[2], 1.1))


def demonic(rank: int):
    """A demonic-path Gu Master (魔道): wild hair, a black robe, a blood-red aura and Gu; the elder (rank five) is white
    haired and bearded, leaning on a staff crowned with a skull."""
    def draw(s: Sprite):
        cx = SOLDIER
        elder = rank >= 5
        tall = 0.96 if elder else 1.0
        s.shadow(cx, FEET + 0.4, 8.5, 2.2)
        s.glow(s.ellipse(cx, FEET - 17, 12, 18), (170, 20, 30), 0.2)
        hand = person(s, cx, robe=BLACK, trim=GREY, sash=GREY, hair="white" if elder else "wild",
                      arm="staff" if elder else "raise", mantle=elder, tall=tall)
        if elder:
            s.flat(s.rect(hand[0] - 0.6, FEET - 34, hand[0] + 0.7, FEET + 0.4), WOOD, 2)
            s.round(s.ellipse(hand[0], FEET - 35.5, 2.4, 2.2), BONE)
        s.outline()
        eyes(s, cx, tall=tall, col=(230, 40, 40))
        if elder:
            s.light(hand[0] - 0.8, FEET - 35.6, BLACK[0])
            s.light(hand[0] + 0.8, FEET - 35.6, BLACK[0])
            gu_glow(s, cx - 9, FEET - 13, ESSENCE[5], 3.4)
        else:
            gu_glow(s, hand[0] + 0.6, hand[1] - 2.4, (220, 30, 40), 4)
            s.put(s.ellipse(hand[0] + 0.6, hand[1] - 2.4, 1.4, 1.6), (240, 50, 50))
    return draw


def immortal_zombie(s: Sprite):
    """An immortal zombie (仙僵): grey-green skin, stiff arms held out, a torn robe, pale glowing eyes, ghost fire."""
    cx = SOLDIER - 1
    s.shadow(cx, FEET + 0.4, 9, 2.2)
    s.glow(s.ellipse(cx, FEET - 2, 11, 3.4), (60, 110, 80), 0.35)
    person(s, cx, arm="forward", skin=PALE, hair="long", hem="torn", mantle=True)
    s.outline()
    eyes(s, cx, col=(190, 255, 200))
    for x, y in ((cx - 11, FEET - 22), (cx + 14, FEET - 28), (cx - 8, FEET - 34)):
        s.glow(s.ellipse(x, y, 1.8, 2.6), (120, 230, 160), 0.6)
        s.light(x, y + 0.5, (210, 255, 220))


# ---------------------------------------------------------------- civilians (left half)
def clan_settler(s: Sprite):
    """A branch family leaving to raise a village: a handcart of bundles under the clan banner, pulled by a settler."""
    cx = CIVILIAN + 4
    s.shadow(cx - 4, FEET + 0.6, 12, 2.4)
    s.flat(s.rect(2.5, FEET - 30, 3.6, FEET - 6), WOOD, 2)                              # the banner pole
    s.body(s.poly([(3.6, FEET - 30), (11, FEET - 28.4), (3.6, FEET - 25)]), GREY, 2)
    s.body(s.rect(1.5, FEET - 12, 13.5, FEET - 6.5), WOOD)                               # the cart bed
    for x, y, r, ramp in ((4.5, FEET - 15, 3.4, CLOTH), (10, FEET - 15.5, 3.6, CLOTH), (7, FEET - 19, 3, STRAW)):
        s.round(s.ellipse(x, y, r, r * 0.8), ramp)
    s.round(s.ellipse(7, FEET - 4.2, 3.4, 3.4), WOOD)                                    # the wheel
    s.flat(s.ellipse(7, FEET - 4.2, 1.2, 1.2), WOOD, 0)
    s.flat(s.line([(13, FEET - 10), (cx - 5, FEET - 16)], 1.2), WOOD, 1)                 # the shafts
    person(s, cx, arm="forward", band=True)
    s.outline()
    eyes(s, cx)


def mortal_laborer(s: Sprite):
    """A mortal (凡人) of the clan's fields: a conical straw hat, a hoe on the shoulder, a basket at the hip."""
    cx = CIVILIAN
    s.shadow(cx, FEET + 0.4, 8, 2.2)
    s.flat(s.line([(cx - 9, FEET - 34), (cx + 7, FEET - 17)], 1.3), WOOD, 2)             # the hoe's handle
    s.flat(s.poly([(cx - 11.5, FEET - 33.6), (cx - 7.6, FEET - 36.4), (cx - 6.8, FEET - 34.6), (cx - 10, FEET - 31.6)]),
           STONE, 1)
    person(s, cx, arm="staff", robe=CLOTH, trim=CLOTH, sash=GREY, hair="straw")
    s.round(s.ellipse(cx - 8.6, FEET - 9, 3.2, 2.6), STRAW)                              # the basket
    s.outline()
    eyes(s, cx)


# ---------------------------------------------------------------- beasts (facing left)
def wolf(f=1.0, bx=46.0, mane=False, crown=False, streaks=1):
    """A lightning wolf (电狼): blue-grey fur crackling with lightning. The bold wolf is larger and maned; the Thunder
    Crown Wolf, a ten-thousand-beast king the size of a small hill, wears a crown of gold fur (canon)."""
    def draw(s: Sprite):
        def P(x, y):
            return bx + x * f, FEET + y * f

        def poly(pts):
            return s.poly([P(x, y) for x, y in pts])

        def ell(x, y, rx, ry):
            return s.ellipse(bx + x * f, FEET + y * f, rx * f, ry * f)

        s.shadow(bx + 1 * f, FEET + 0.4, 13.5 * f, 2.2 * f)
        for x0 in (-4.6, 6.8):   # far legs
            s.flat(s.rect(bx + x0 * f, FEET - 6.5 * f, bx + (x0 + 1.9) * f, FEET + 0.4), WOLF, 1)
        s.body(poly([(9.5, -9.8), (15.6, -12.2), (17.2, -9.8), (16, -7.2), (10, -7)]), WOLF)          # bushy tail
        s.flat(poly([(15.4, -11.6), (17.2, -9.8), (16.4, -8.4)]), WOLF, 4)
        trunk = ell(1.5, -8.6, 10, 4.0) | poly([(-8, -10), (-5, -13.6), (0, -11), (-4, -5.2)])
        s.body(trunk, WOLF)
        s.flat(ell(0.5, -6.2, 8, 1.7) & trunk, WOLF, 3)                                          # pale belly
        s.flat(ell(2.5, -11.6, 8.4, 1.3) & trunk, WOLF, 1)                                       # dark back
        for x0 in (-6.8, 5.2):   # near legs, with paws
            s.body(s.rect(bx + x0 * f, FEET - 6.5 * f, bx + (x0 + 2.1) * f, FEET + 0.4), WOLF)
            s.flat(s.rect(bx + (x0 - 0.4) * f, FEET - 1.1 * f, bx + (x0 + 2.4) * f, FEET + 0.4), WOLF, 1)
        if mane or crown:
            s.body(poly([(-12, -15), (-10, -17.4), (-7, -16), (-4, -17), (-2.6, -13.6), (-1, -11), (-3, -8),
                         (-7.4, -7), (-10.6, -9.6)]), WOLF)
        s.round(ell(-10, -12.2, 3.6, 3.0), WOLF)
        s.body(poly([(-12.4, -13.2), (-17.8, -11.4), (-17.4, -9.6), (-12.4, -9.2)]), WOLF)          # snout
        s.flat(poly([(-12.6, -10.6), (-17.4, -10.2), (-17.2, -9.6), (-12.6, -9.4)]), WOLF, 3)
        s.body(poly([(-10.6, -14.6), (-9.4, -18.4), (-8, -14.6)]) | poly([(-12.6, -14.2), (-12.8, -17.8), (-10.8, -14.6)]),
               WOLF)                                                                                # ears
        if crown:   # the crown of gold fur
            s.round(poly([(-13.6, -15.4), (-13.4, -20.6), (-12, -17.6), (-11, -22.4), (-9.6, -17.8), (-8, -21.6),
                          (-7, -16.8), (-5.4, -19.2), (-6, -14.6)]), GOLD)
        s.outline()
        for i in range(streaks):   # lightning along the back
            y = -10.8 + i * 2.6
            pts = [P(-5, y), P(-2, y + 1.8), P(0.6, y - 0.8), P(3.6, y + 1.4), P(6.6, y - 0.6)]
            s.glow(s.line(pts, 2.6), (120, 200, 255), 0.4)
            s.light_mask(s.line(pts, 1), (255, 240, 140))
        s.light(bx - 10.8 * f, FEET - 12.8 * f, (255, 236, 110))
        s.light(bx - 17.8 * f, FEET - 11.2 * f, BLACK[0])
        for x, y in ((-2, -22), (8, -19), (14, -9), (-14, -8)):
            s.light(bx + x * f, FEET + y * f, (190, 230, 255))
        if crown:
            for x, y in ((-15, -23), (-4, -23), (-17, -16)):
                s.light(bx + x * f, FEET + y * f, (255, 250, 200))
    return draw


def desolate_beast(s: Sprite):
    """A desolate beast (荒兽, about rank six): a horned, plated boar-rhino as big as a house, in a green-grape aura."""
    bx, f = 40.0, 1.5
    s.shadow(bx + 3, FEET + 0.6, 21, 3.2)
    s.glow(s.ellipse(bx + 3, FEET - 17, 24, 17), ESSENCE[6], 0.18)
    for x0 in (-4.6, 9):   # far legs
        s.flat(s.rect(bx + x0 * f, FEET - 9 * f, bx + (x0 + 3.2) * f, FEET + 0.4), BEAST, 1)
    s.body(s.ellipse(bx + 2.5 * f, FEET - 12 * f, 13 * f, 7.6 * f), BEAST)
    for x in (-3, 2.4, 7.8):   # bone plates on the spine
        s.round(s.poly([(bx + (x - 2.2) * f, FEET - 18 * f), (bx + x * f, FEET - 24 * f), (bx + (x + 2.4) * f, FEET - 18.4 * f)]),
                BONE)
    for x0 in (-7.6, 6):   # near legs
        s.body(s.rect(bx + x0 * f, FEET - 9 * f, bx + (x0 + 3.4) * f, FEET + 0.4), BEAST)
    s.round(s.ellipse(bx - 10.6 * f, FEET - 10 * f, 5.4 * f, 4.8 * f), BEAST)
    s.round(s.poly([(bx - 14 * f, FEET - 11 * f), (bx - 15.4 * f, FEET - 18 * f), (bx - 12 * f, FEET - 13 * f)]), BONE)
    s.flat(s.line([(bx - 13.4 * f, FEET - 7.4 * f), (bx - 16 * f, FEET - 10.6 * f)], 1.4), BONE, 3)
    s.outline()
    s.light(bx - 11.4 * f, FEET - 11.4 * f, (255, 60, 40))


SERPENT = ((30, 46, 30), (52, 84, 48), (78, 120, 66), (112, 156, 88), (160, 196, 120))


def ancient_beast(s: Sprite):
    """An ancient desolate beast (上古荒兽, about rank seven): a horned, frilled serpent coiled to strike, red-date aura."""
    s.shadow(44, FEET + 0.6, 19, 3.2)
    s.glow(s.ellipse(44, FEET - 18, 21, 20), ESSENCE[7], 0.2)
    coil = [(60, FEET - 4), (50, FEET - 1), (36, FEET - 3), (30, FEET - 9), (38, FEET - 14), (52, FEET - 13),
            (57, FEET - 19), (50, FEET - 25), (40, FEET - 27), (34, FEET - 32)]
    body = s.line(coil, 6.6)
    s.body(body, SERPENT)
    s.flat(s.line(coil, 2.2) & body, BONE, 2)
    s.round(s.ellipse(31, FEET - 34, 5, 4), SERPENT)
    s.body(s.poly([(33, FEET - 39), (40, FEET - 44), (39, FEET - 36)]) | s.poly([(28, FEET - 38), (25, FEET - 45), (31, FEET - 39)]),
           ROOF)                                                                                                   # frill
    s.round(s.poly([(29, FEET - 37), (27, FEET - 44), (31, FEET - 38)]), BONE)
    s.outline()
    s.light(29.4, FEET - 35, (255, 70, 50))
    s.put(s.line([(26.5, FEET - 31.5), (23.5, FEET - 30), (22.5, FEET - 31.6)], 1), (220, 40, 50))        # the tongue


HIDE = ((34, 30, 44), (62, 56, 80), (94, 86, 116), (132, 124, 156), (178, 170, 200))


def immemorial_beast(s: Sprite):
    """An immemorial desolate beast (太古荒兽, about rank eight): a winged, horned colossus in a white-lychee aura."""
    s.shadow(42, FEET + 0.6, 19, 3.2)
    s.glow(s.ellipse(42, FEET - 22, 23, 24), ESSENCE[8], 0.2)
    s.flat(s.poly([(38, FEET - 18), (33, FEET - 42), (27, FEET - 47), (28, FEET - 33), (24, FEET - 26), (33, FEET - 16)]),
           HIDE, 1)                                                                                 # the far wing
    s.body(s.line([(54, FEET - 10), (60, FEET - 7), (64, FEET - 2)], 3.4), HIDE)                  # the tail
    for x0 in (37.6, 52):   # far legs
        s.flat(s.rect(x0, FEET - 9, x0 + 3.8, FEET + 0.4), HIDE, 1)
    s.body(s.ellipse(45, FEET - 13, 14.5, 8.6), HIDE)
    s.flat(s.ellipse(44, FEET - 9.4, 11, 3) & s.ellipse(45, FEET - 13, 14.5, 8.6), HIDE, 3)
    s.body(s.poly([(46, FEET - 18), (53, FEET - 45), (63, FEET - 50), (61, FEET - 36), (64, FEET - 27), (56, FEET - 15)]), HIDE)
    for x0, y0 in ((53, FEET - 45), (61, FEET - 36)):
        s.flat(s.line([(47, FEET - 19), (x0, y0)], 1), BONE, 2)
    for x0 in (34, 48.6):
        s.body(s.rect(x0, FEET - 9, x0 + 4, FEET + 0.4), HIDE)
    s.body(s.line([(34, FEET - 15), (28, FEET - 24), (26, FEET - 29)], 5), HIDE)                  # the neck
    s.round(s.ellipse(24.6, FEET - 31, 4.8, 3.8), HIDE)
    s.round(s.poly([(25, FEET - 34), (30, FEET - 42), (28, FEET - 34)]) | s.poly([(21.5, FEET - 33.6), (20, FEET - 41), (23.6, FEET - 34)]),
            BONE)
    s.outline()
    s.light(22.8, FEET - 31.6, (230, 255, 255))


# ---------------------------------------------------------------- Gu Houses (仙蛊屋): fortresses that walk, sail or fly
WHITE_T = ((110, 106, 102), (176, 172, 164), (220, 216, 206), (240, 238, 230), (255, 255, 255))
AMBER_W = ((96, 54, 14), (170, 104, 30), (226, 160, 52), (250, 204, 104), (255, 240, 190))


def luck_altar(s: Sprite):
    """Calamity Luck Altar (劫运坛): a tiered stone altar walking on four pillars, a bronze cauldron of luck fire on
    top, red threads of luck streaming from it, the clan's banners on its sides."""
    s.shadow(44, FEET + 0.6, 18, 3)
    for x in (30, 36, 52, 58):
        s.body(s.rect(x - 1.8, FEET - 8, x + 1.8, FEET + 0.4), STONE)
    for x0, x1, y in ((26, 62, FEET - 8), (31, 57, FEET - 15), (36, 52, FEET - 21)):
        s.body(s.rect(x0, y - 5, x1, y), STONE)
        s.flat(s.rect(x0, y - 7, x1, y - 5), STONE, 3)
    s.round(s.ellipse(44, FEET - 31, 6, 4.6), GOLD)
    for x in (31, 57):   # the clan's banners hanging on the lowest tier
        s.body(s.poly([(x - 2, FEET - 14), (x + 2, FEET - 14), (x + 2, FEET - 7), (x, FEET - 8.6), (x - 2, FEET - 7)]), GREY, 2)
    s.flat(s.rect(37.6, FEET - 35, 50.4, FEET - 33.4), GOLD, 1)
    s.outline()
    for i, (x, y) in enumerate(((35, FEET - 46), (44, FEET - 49), (53, FEET - 45), (28, FEET - 38), (60, FEET - 37))):
        s.put(s.line([(44, FEET - 36), ((44 + x) / 2 + (i - 2), (FEET - 36 + y) / 2 - 2), (x, y)], 1), (220, 40, 50))
    s.glow(s.ellipse(44, FEET - 38, 4.2, 3.4), (255, 150, 60), 0.6)
    s.put(s.poly([(42, FEET - 36), (44, FEET - 42), (46, FEET - 36)]), (255, 210, 90))


def flying_warship(s: Sprite):
    """Myriad Year Flying Warship (万年斗飞车): a flying war-chariot of time sailing on cloud, its great wheels geared
    and glowing amber, the clan's sail above."""
    s.shadow(44, FEET + 0.6, 16, 2.4, a=0.18)
    for x, r in ((30, 5), (40, 6), (52, 5.4), (60, 4)):
        s.round(s.ellipse(x, FEET - 4, r, r * 0.62), CLOUD)
    s.body(s.poly([(22, FEET - 22), (62, FEET - 22), (57, FEET - 10), (27, FEET - 10)]), WOOD)
    s.flat(s.rect(24, FEET - 24, 61, FEET - 22), GOLD, 2)
    s.body(s.rect(38, FEET - 30, 54, FEET - 24), ROOF)
    s.flat(s.rect(45, FEET - 50, 46.4, FEET - 24), WOOD, 1)
    s.body(s.poly([(46.4, FEET - 49), (58, FEET - 45), (58, FEET - 33), (46.4, FEET - 34)]), GREY, 1)
    s.round(s.poly([(18, FEET - 24), (23, FEET - 22), (24, FEET - 19), (20, FEET - 20)]), GOLD)    # the prow
    for x in (32, 50):
        s.round(s.ellipse(x, FEET - 13, 5.6, 5.6), AMBER_W)
        s.flat(s.ellipse(x, FEET - 13, 1.6, 1.6), WOOD, 1)
    s.outline()
    for x in (32, 50):
        for a in range(0, 360, 60):
            s.light(x + 3.6 * math.cos(math.radians(a)), FEET - 13 + 3.6 * math.sin(math.radians(a)), (255, 236, 160))
    for r in (7, 10):   # time ripples behind it
        s.glow(s.ellipse(64, FEET - 16, r, r * 0.8) & ~s.ellipse(64, FEET - 16, r - 1.2, r * 0.8 - 1.2), (255, 200, 90), 0.5)


def dragon_palace(s: Sprite):
    """Dragon Palace (龙宫): a palace of red walls and golden roofs on a floating rock, a jade dragon coiled around its
    base, dream mist drifting."""
    s.shadow(44, FEET + 0.6, 14, 2.4, a=0.18)
    s.glow(s.ellipse(44, FEET - 6, 18, 5), (180, 140, 255), 0.35)
    s.body(s.poly([(24, FEET - 18), (62, FEET - 18), (54, FEET - 10), (44, FEET - 3), (32, FEET - 10)]), ROCK)
    s.body(s.rect(30, FEET - 28, 58, FEET - 18), ROOF)
    for x in (34, 41, 48, 55):
        s.flat(s.rect(x, FEET - 25, x + 2, FEET - 18), BLACK, 2)
    s.round(s.poly([(25, FEET - 27), (30, FEET - 33), (58, FEET - 33), (63, FEET - 27)]), GOLD)
    s.body(s.rect(36, FEET - 39, 52, FEET - 33), ROOF)
    s.round(s.poly([(32, FEET - 38), (36, FEET - 44), (52, FEET - 44), (56, FEET - 38)]), GOLD)
    s.flat(s.rect(42, FEET - 48, 46, FEET - 44), GREY, 2, 2)
    dragon = [(22, FEET - 12), (30, FEET - 7), (40, FEET - 9), (50, FEET - 5), (60, FEET - 10), (64, FEET - 18)]
    s.body(s.line(dragon, 3), JADE)
    s.round(s.ellipse(21, FEET - 13.5, 3, 2.4), JADE)
    s.outline()
    s.light(20.4, FEET - 14, (255, 236, 110))


def overseeing_tower(s: Sprite):
    """Heaven Overseeing Tower (监天塔): the Heavenly Court's tall pagoda of white walls and golden eaves around Fate
    Gu, whose light burns at its top, clouds at its foot."""
    s.shadow(44, FEET + 0.6, 14, 2.6)
    w, y = 22.0, FEET - 1
    for tier in range(5):
        h = 8 - tier
        s.body(s.rect(44 - w / 2, y - h, 44 + w / 2, y), WHITE_T)
        s.flat(s.rect(44 - 1.4, y - h + 2, 44 + 1.4, y), BLACK, 2)
        s.round(s.poly([(44 - w / 2 - 4, y - h + 1), (44 - w / 2, y - h - 3), (44 + w / 2, y - h - 3), (44 + w / 2 + 4, y - h + 1)]),
                GOLD)
        y -= h + 3
        w -= 3.6
    s.flat(s.rect(43.3, y - 6, 44.7, y + 1), GOLD, 2)
    for x, r in ((30, 4.6), (40, 5.4), (50, 5), (58, 4)):
        s.round(s.ellipse(x, FEET - 1, r, r * 0.6), CLOUD)
    s.outline()
    s.glow(s.ellipse(44, y - 8, 4.6, 4.6), (255, 220, 120), 0.5)
    s.put(s.ellipse(44, y - 8, 1.8, 1.8), (255, 246, 200))


# ---------------------------------------------------------------- attack effects (played over the unit hit)
FX_SIZE = (128, 110)   # the frames' canvas, as before: drawn at 64 x 55 and doubled, so its pixels match the sprites'


def _fx(draw, n):
    """n frames of an effect, drawn on a 64 x 55 HexaRealm-pixel canvas around (32, 28) and doubled."""
    frames = []
    for i in range(n):
        s = Sprite("HexaRealm")
        draw(s, i, n)
        im = s.layers()["base"].crop((0, 0, 64, 55))
        frames.append(im.resize(FX_SIZE, Image.NEAREST))
    return frames


def _ring(s, cx, cy, r, col, a=0.9, th=1.2):
    s.glow(s.ellipse(cx, cy, r, r * 0.8) & ~s.ellipse(cx, cy, r - th, r * 0.8 - th), col, a)


def _burst(s, cx, cy, r, col, rays=8, rot=0.0):
    for k in range(rays):
        t = rot + 2 * math.pi * k / rays
        ln = r * (1 if k % 2 == 0 else 0.6)
        s.glow(s.line([(cx, cy), (cx + ln * math.cos(t), cy + ln * 0.8 * math.sin(t))], 2.2), col, 0.5)
        s.glow(s.line([(cx, cy), (cx + ln * 0.8 * math.cos(t), cy + ln * 0.64 * math.sin(t))], 1), _lift(col, 1.3), 0.95)
    s.glow(s.ellipse(cx, cy, r * 0.3, r * 0.3), (255, 255, 255), 0.95)


def _sparks(s, key, cx, cy, r, col, n=8):
    rng = _rng("sparks" + key)
    for _ in range(n):
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.4, 1.0) * r
        s.glow(s.spot(cx + d * math.cos(a), cy + 0.8 * d * math.sin(a)), col, 1.0)


def strike(rank):
    """A Gu strike in the attacker's essence colour: a flash, rays, rings that grow with rank, sparks."""
    col, rings = ESSENCE[min(rank, 9)], 1 + rank // 3

    def draw(s, i, n):
        t = (i + 1) / n
        if i < n - 1:
            _burst(s, 32, 28, 4 + 10 * t, col, rays=6 + 2 * (rank >= 5), rot=i * 0.4)
        for k in range(rings):
            r = 5 + 16 * t - 4 * k
            if r > 2:
                _ring(s, 32, 28, r, col, a=0.85 - 0.15 * k)
        _sparks(s, f"strike{rank}{i}", 32, 28, 8 + 14 * t, _lift(col, 1.2), 6 + 2 * i)
    return draw, {1: 3, 2: 3, 3: 4, 4: 4, 5: 4, 6: 5, 7: 5, 8: 5, 9: 6}[min(rank, 9)]


def moon_blade(rank):
    """The Moonlight Gu's crescent blade (月刃) sweeping across the target, leaving a trail of pale light."""
    def draw(s, i, n):
        x = 14 + 12 * i
        if i < 3:
            r = 6 + 1.2 * rank
            blade = s.ellipse(x, 28, r * 0.7, r) & ~s.ellipse(x - 2.6, 28, r * 0.62, r * 0.92)
            s.glow(s.line([(x - 14, 28), (x - 3, 28)], 3), MOON, 0.35)
            s.glow(blade, (226, 246, 255), 1.0)
        else:
            s.glow(s.line([(14, 36), (50, 20)], 2), (226, 246, 255), 0.9)
            _sparks(s, f"moon{i}", 32, 28, 14, (226, 246, 255), 10)
    return draw, 4


def beast_charge(kind):
    """The strength path: the Gu's beast phantom (a boar, or Xiong's bear) charges and bursts on the target."""
    col = (206, 206, 216) if kind == "boar" else (176, 112, 66)

    def draw(s, i, n):
        if i < 2:
            phantom(s, 20 + 9 * i, 28, kind)
        else:
            _ring(s, 32, 28, 6 + 6 * (i - 2), col, 0.9, 2.0)
            _burst(s, 32, 28, 10 + 4 * (i - 2), _lift(col, 1.2), 8)
        if i == 3:
            _sparks(s, "dust", 32, 34, 16, (170, 150, 120), 10)
    return draw, 4


def water_whip(rank):
    """The Stream Gu's water lashing out like a whip, then bursting into droplets."""
    def draw(s, i, n):
        if i < 3:
            pts = [(6 + 4 * k, 28 - 7 * math.sin(k * 0.8 + i * 0.9)) for k in range(4 + 3 * i)]
            s.glow(s.line(pts, 3.4), (90, 170, 240), 0.6)
            s.glow(s.line(pts, 1.4), (190, 236, 255), 1.0)
        _sparks(s, f"water{i}", 32, 28, 6 + 5 * i, (160, 220, 255), 4 + 3 * i)
    return draw, 4


def wind_blades(rank):
    """Wu's wind: thin crescent blades of air crossing the target, then a dying swirl."""
    def draw(s, i, n):
        for k in range(min(i + 1, 3)):
            y = 20 + 7 * k
            arc = s.ellipse(32, y + 6, 15, 7) & ~s.ellipse(32, y + 7.4, 14, 6.4) & (s.Y < y + 6)
            s.glow(arc, (214, 246, 226), 0.95 - 0.2 * (i - k > 1))
        if i == 3:
            s.glow(s.ellipse(32, 28, 8, 5) & ~s.ellipse(32, 28, 6.8, 3.8), (214, 246, 226), 0.6)
    return draw, 4


def lightning(crown=False):
    """A lightning wolf's strike: a bolt, a flash, claw marks crackling (the Thunder Crown Wolf's is gold)."""
    col = (255, 220, 90) if crown else (150, 210, 255)

    def draw(s, i, n):
        if i < 2:
            bolt = [(30, 0), (35, 8), (29, 14), (36, 22), (31, 28)]
            s.glow(s.line(bolt, 3.4), col, 0.55)
            s.glow(s.line(bolt, 1.2), (255, 255, 240), 1.0)
            if i == 1:
                _burst(s, 31, 28, 9, col, 8)
        else:
            for k in range(3):
                x = 25 + 5 * k
                s.glow(s.line([(x, 20), (x + 6, 36)], 2.4), col, 0.6)
                s.glow(s.line([(x, 20), (x + 6, 36)], 1), (255, 255, 240), 1.0 - 0.3 * (i - 2))
            _sparks(s, f"bolt{i}", 32, 28, 14, col, 8)
    return draw, 4


def claws(rank):
    """A desolate beast's claws raking the target in an essence-coloured flash."""
    col = ESSENCE[rank]

    def draw(s, i, n):
        if i == 0:
            s.glow(s.ellipse(32, 28, 10, 8), col, 0.4)
        for k in range(3):
            x = 22 + 7 * k
            ln = min(1.0, (i + 1) / 2)
            s.glow(s.line([(x, 14), (x + 10 * ln, 14 + 24 * ln)], 3.4), col, 0.55)
            s.glow(s.line([(x, 14), (x + 10 * ln, 14 + 24 * ln)], 1.2), (255, 255, 255), 1.0 - 0.25 * max(0, i - 1))
        if i >= 2:
            _sparks(s, f"claw{rank}{i}", 32, 28, 16, col, 10)
    return draw, 4


def blood_slash(rank):
    """A demonic strike: a crescent of blood across the target, drops flying."""
    def draw(s, i, n):
        if i < 3:
            r = 9 + 3 * i
            arc = s.ellipse(32, 30, r, r * 0.7) & ~s.ellipse(32, 32, r * 0.92, r * 0.62) & (s.Y < 31)
            s.glow(arc, (210, 20, 30), 1.0)
            if rank >= 5:
                s.glow(arc & _nb(arc, 0, 1), ESSENCE[5], 0.9)
        _sparks(s, f"blood{i}", 32, 30, 8 + 5 * i, (180, 10, 20), 6 + 2 * i)
    return draw, 4


def miasma_claw():
    """An immortal zombie's strike: ghost-green claws trailing miasma."""
    def draw(s, i, n):
        s.glow(s.ellipse(32, 30, 8 + 3 * i, 6 + 2 * i), (70, 120, 90), 0.35)
        for k in range(3):
            x = 24 + 6 * k
            ln = min(1.0, (i + 1) / 2)
            s.glow(s.line([(x, 16), (x + 8 * ln, 16 + 22 * ln)], 2), (150, 240, 180), 0.95 - 0.2 * max(0, i - 2))
        _sparks(s, f"zombie{i}", 32, 28, 14, (190, 255, 210), 6)
    return draw, 5


def house_fx(kind):
    """The Gu Houses' killer moves: luck threads drawing tight, time rippling, a dream dragon coiling, Fate's beam."""
    def draw(s, i, n):
        t = (i + 1) / n
        if kind == "luck":
            for k in range(6):
                a = 2 * math.pi * k / 6 + i * 0.3
                r = 26 * (1 - t) + 4
                s.glow(s.line([(32 + r * math.cos(a), 28 + 0.8 * r * math.sin(a)), (32, 28)], 1), (220, 40, 50), 0.95)
            if i >= n - 2:
                _burst(s, 32, 28, 12, (255, 200, 90), 8)
        elif kind == "time":
            for k in range(3):
                r = 4 + 18 * t - 5 * k
                if r > 2:
                    _ring(s, 32, 28, r, (255, 200, 90), 0.9 - 0.2 * k)
            s.glow(s.line([(32, 28), (32 + 8 * math.cos(i), 28 + 8 * math.sin(i))], 1.2), (255, 240, 190), 1.0)
        elif kind == "dream":
            pts = [(32 + (16 - 3 * i) * math.cos(a + i), 28 + 0.7 * (16 - 3 * i) * math.sin(a + i))
                   for a in np.linspace(0, 1.6 * math.pi, 14)]
            s.glow(s.line(pts, 3.2), (180, 140, 255), 0.6)
            s.glow(s.line(pts, 1.2), (230, 210, 255), 1.0)
            s.glow(s.ellipse(*pts[-1], 2.4, 2), (150, 236, 200), 1.0)
        else:   # fate: a golden beam from above
            w = 2 + 3 * min(t, 0.7)
            s.glow(s.rect(32 - w, 0, 32 + w, 30), (255, 220, 120), 0.5)
            s.glow(s.rect(32 - w / 3, 0, 32 + w / 3, 30), (255, 250, 220), 1.0)
            if i >= 2:
                _burst(s, 32, 30, 12, (255, 220, 120), 10)
        _sparks(s, f"{kind}{i}", 32, 28, 16, (255, 236, 180), 3 + i)
    return draw, 5


WORDS = (("One", 1), ("Two", 2), ("Three", 3), ("Four", 4), ("Five", 5))
SPRITES = {   # name: (draw, design rows above the hex for tall subjects)
    **{f"Rank {w} Gu Master": (gu_master(r), 0) for w, r in WORDS},
    **{f"Rank {w} Moon Gu Master": (gu_master(r, "Moon"), 0) for w, r in WORDS[1:4]},
    **{f"Rank {w} Strength Gu Master": (gu_master(r, "Strength", "boar"), 0) for w, r in WORDS[1:4]},
    **{f"Rank {w} {clan} Gu Master": (gu_master(r, path, "bear"), 0)
       for clan, path in (("Gu Yue", "Moon"), ("Bai", "Water"), ("Xiong", "Strength"), ("Wu", "Wind")) for w, r in WORDS[1:4]},
    "Rank Six Gu Immortal": (gu_immortal(6), 4), "Rank Seven Gu Immortal": (gu_immortal(7), 6),
    "Rank Eight Gu Immortal": (gu_immortal(8), 8), "Venerable": (venerable, 10),
    "Lone Gu Master": (lone_gu_master, 0), "Demonic Gu Master": (demonic(3), 0), "Demonic Elder": (demonic(5), 0),
    "Immortal Zombie": (immortal_zombie, 0),
    "Clan Settler": (clan_settler, 0), "Mortal Laborer": (mortal_laborer, 0),
    "Lightning Wolf": (wolf(), 0), "Bold Lightning Wolf": (wolf(1.2, 44, mane=True, streaks=2), 0),
    "Thunder Crown Wolf": (wolf(1.55, 37, mane=True, crown=True, streaks=2), 6),
    "Desolate Beast": (desolate_beast, 4), "Ancient Desolate Beast": (ancient_beast, 8),
    "Immemorial Desolate Beast": (immemorial_beast, 12),
    "Calamity Luck Altar": (luck_altar, 12), "Myriad Year Flying Warship": (flying_warship, 12),
    "Dragon Palace": (dragon_palace, 10), "Heaven Overseeing Tower": (overseeing_tower, 16),
}


ATTACKS = {   # name: (draw, frames); every unit has its own, so the unit-type fallbacks are never needed
    **{f"Rank {w} Gu Master": strike(r) for w, r in WORDS},
    **{f"Rank {w} Moon Gu Master": moon_blade(r) for w, r in WORDS[1:4]},
    **{f"Rank {w} Strength Gu Master": beast_charge("boar") for w, r in WORDS[1:4]},
    **{f"Rank {w} Gu Yue Gu Master": moon_blade(r) for w, r in WORDS[1:4]},
    **{f"Rank {w} Bai Gu Master": water_whip(r) for w, r in WORDS[1:4]},
    **{f"Rank {w} Xiong Gu Master": beast_charge("bear") for w, r in WORDS[1:4]},
    **{f"Rank {w} Wu Gu Master": wind_blades(r) for w, r in WORDS[1:4]},
    "Rank Six Gu Immortal": strike(6), "Rank Seven Gu Immortal": strike(7), "Rank Eight Gu Immortal": strike(8),
    "Venerable": strike(9), "Lone Gu Master": strike(2), "Demonic Gu Master": blood_slash(3),
    "Demonic Elder": blood_slash(5), "Immortal Zombie": miasma_claw(), "Clan Settler": None, "Mortal Laborer": None,
    "Lightning Wolf": lightning(), "Bold Lightning Wolf": lightning(), "Thunder Crown Wolf": lightning(crown=True),
    "Desolate Beast": claws(6), "Ancient Desolate Beast": claws(7), "Immemorial Desolate Beast": claws(8),
    "Calamity Luck Altar": house_fx("luck"), "Myriad Year Flying Warship": house_fx("time"),
    "Dragon Palace": house_fx("dream"), "Heaven Overseeing Tower": house_fx("fate"),
}


def attack_frames(name: str) -> list[Image.Image]:
    spec = ATTACKS.get(name)
    return _fx(*spec) if spec else []


# ---------------------------------------------------------------- portraits: the unit on its diorama hex
PORTRAIT = 144   # 72 x 72 HexaRealm pixels doubled; Images.Units/UnitPortraits/Background.png has the same size
CLAN = {"Gu Yue": ((220, 220, 240), (30, 40, 90)), "Bai": ((40, 70, 120), (230, 230, 230)),
        "Xiong": ((240, 200, 140), (90, 50, 20)), "Wu": ((250, 210, 120), (120, 20, 20)),
        "Barbarians": ((185, 12, 12), (40, 30, 34)), "Heavenly Court": ((70, 60, 140), (235, 225, 180)),
        "Zombie Alliance": ((180, 220, 190), (60, 80, 70)), "Fang Clan": ((240, 230, 200), (150, 110, 60))}
PATH_COLOUR = {None: ((200, 196, 186), (70, 110, 90)), "Moon": ((200, 214, 240), (40, 60, 130)),
               "Strength": ((214, 170, 120), (120, 40, 34))}


def _portrait_colours(name):
    for clan in ("Gu Yue", "Bai", "Xiong", "Wu"):
        if f" {clan} " in name:
            return CLAN[clan]
    if name in ("Lone Gu Master", "Demonic Gu Master", "Demonic Elder") or "Wolf" in name or "Desolate" in name:
        return CLAN["Barbarians"]
    if name == "Heaven Overseeing Tower" or "Immortal" in name and "Zombie" not in name or name == "Venerable":
        return CLAN["Heavenly Court"]
    if name == "Immortal Zombie":
        return CLAN["Zombie Alliance"]
    if name in ("Calamity Luck Altar", "Myriad Year Flying Warship", "Dragon Palace"):
        return CLAN["Fang Clan"]
    return PATH_COLOUR["Moon" if "Moon" in name else "Strength" if "Strength" in name else None]


def _ground(cv: Canvas, name: str):
    """The diorama's ground inside the grass frame, kept to the back and sides so the unit stands clear."""
    rng = _rng("ground" + name)
    if "Wolf" in name:
        for x, y, r in ((14, 18, 4.6), (25, 13, 4.2), (44, 13, 4.4), (53, 20, 4)):
            cv.tree(x, y, r)
    elif "Desolate" in name:
        cv.patch(cv.ellipse(32, 30, 22, 13), ASH, "beast ground", specks=0.12)
        for x, y in ((14, 24), (50, 20)):
            cv.solid(cv.ellipse(x, y, 3, 2), BONE, shade="ball")
    elif "Zombie" in name:
        cv.patch(cv.ellipse(32, 30, 23, 13), MIASMA, "zombie ground", specks=0.1)
        cv.tone(cv.line([(48, 26), (49, 14), (45, 9)], 1.4) | cv.line([(49, 18), (53, 13)], 1), np.zeros((cv.h, cv.w), int), BLACK)
    elif "Demonic" in name:
        cv.patch(cv.ellipse(32, 30, 22, 12), ((44, 10, 14), (76, 18, 22), (104, 30, 30), (134, 50, 44), (170, 80, 64)),
                 "blood ground", specks=0.1)
    elif "Immortal" in name or name == "Venerable" or name in ("Dragon Palace", "Myriad Year Flying Warship"):
        for x, y, r in ((12, 22, 4.4), (52, 20, 4.4), (20, 40, 4), (46, 42, 4.2), (32, 10, 4)):
            cv.cloud(x, y, r)
    elif name in ("Calamity Luck Altar", "Heaven Overseeing Tower"):
        cv.patch(cv.hexagon(9), STONE, "terrace", specks=0.05)
    elif name in ("Clan Settler", "Mortal Laborer"):
        field = cv.ellipse(32, 28, 22, 12)
        cv.patch(field, EARTH, "field", specks=0.05)
        cv.tone(field & (np.round(cv.Y) % 4 == 0), np.full((cv.h, cv.w), 3), LEAF)
    else:   # a Gu Master: flagstones of the clan's courtyard, and its own touch
        cv.patch(cv.ellipse(32, 30, 17, 9), STONE, "court" + name, specks=0.05)
        if " Bai " in name:
            cv.water(cv.poly([(10, 12), (54, 8), (55, 13), (11, 17)]), WATER, seed="bai stream", ripples=3)
        elif "Strength" in name or " Xiong " in name:
            for x, y in ((12, 22), (52, 16)):
                cv.solid(cv.ellipse(x, y, 3.6, 2.6), ROCK, shade="ball")
        elif " Wu " in name:
            cv.tufts("wind" + name, 14)
        else:
            for _ in range(5):
                cv.dot(rng.uniform(10, 54), rng.uniform(10, 44), (240, 236, 150) if rng.random() < 0.5 else (236, 150, 190))


def portrait(name: str) -> Image.Image:
    """The unit standing on the tilesets' grass hex, its own ground inside, in a clan's colours; 144 x 144."""
    cv = Canvas("HexaRealm")
    cv.frame()
    cv.tufts("portrait" + name)
    _ground(cv, name)
    spr = tinted(sprite(name)["HexaRealm"], *_portrait_colours(name))
    out = Image.new("RGBA", (72, 72), (0, 0, 0, 0))
    out.alpha_composite(cv.image(), (4, 16))
    dx = 18 if name in ("Clan Settler", "Mortal Laborer") else -16 if spr.height == 56 else -12
    out.alpha_composite(spr, (4 + dx, 16 + 56 - spr.height))
    return out.resize((PORTRAIT, PORTRAIT), Image.NEAREST)


def sprite(name: str) -> dict[str, dict[str, Image.Image]]:
    """{"HexaRealm": {"base", "layer1", "layer2"}, "FantasyHex": {...}} for one unit."""
    draw, top = SPRITES[name]
    out = {}
    for ts in ("HexaRealm", "FantasyHex"):
        s = Sprite(ts, top)
        draw(s)
        out[ts] = s.layers()
    return out


def tinted(layers: dict[str, Image.Image], inner, outer) -> Image.Image:
    """The sprite as the engine shows it for a nation with these colours."""
    out = layers["base"].copy()
    for key, col in (("layer1", inner), ("layer2", outer)):
        a = np.asarray(layers[key]).astype(np.float32)
        a[..., :3] *= np.asarray(col, np.float32) / 255
        out.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"))
    return out


if __name__ == "__main__":   # self-check: sizes, layers, the soldier/civilian halves, frames and portraits
    import json
    from .pixeltiles import HEX
    from common import REPO_ROOT
    units = {u["name"] for u in json.loads((REPO_ROOT / "jsons" / "Units.json").read_text(encoding="utf-8"))}
    assert units == set(SPRITES) == set(ATTACKS), sorted(units ^ set(SPRITES))
    for nm, (fn, top) in SPRITES.items():
        for tset, layers in sprite(nm).items():
            w, rows = HEX[tset]
            base = layers["base"]
            assert base.size == (w, len(rows) + round(top * (1 if tset == "HexaRealm" else 0.5))), (nm, tset, base.size)
            x0, _, x1, _ = Image.alpha_composite(base, layers["layer1"]).getbbox()
            if nm in ("Clan Settler", "Mortal Laborer"):
                assert x1 <= w * 0.55, (nm, tset, x1)       # civilians keep to the left half
            elif "Rank" in nm and "Immortal" not in nm:
                assert x0 >= w * 0.45, (nm, tset, x0)       # soldiers keep to the right half
        assert bool(attack_frames(nm)) != (ATTACKS[nm] is None)
        assert portrait(nm).size == (PORTRAIT, PORTRAIT)
    print("pixelunits ok")
