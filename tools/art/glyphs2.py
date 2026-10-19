"""Second art pass: every remaining Slice 1 object, in the same flat style and motif language as glyphs.py."""
from __future__ import annotations

import math

from PIL import ImageFont

from .glyphs import (G, boar_head, fist, gu_beetle, human, lightning_wolf, moon_gu_master, pips, strength_gu_master,
                     wolf_head, S)


def font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def letter(g: G, ch, cx, cy, size, v=255):
    g.d.text((cx * S, cy * S), ch, fill=v, font=font(int(size * S)), anchor="mm")


def regular(cx, cy, r, n, rot=90):
    return [(cx + r * math.cos(math.radians(rot + 360 * k / n)), cy - r * math.sin(math.radians(rot + 360 * k / n)))
            for k in range(n)]


def gem(g: G, x, y, r, v=255):
    """A primeval stone: a faceted gem."""
    g.poly([(x, y - r), (x + r * 0.8, y - r * 0.2), (x + r * 0.45, y + r), (x - r * 0.45, y + r), (x - r * 0.8, y - r * 0.2)], v)
    g.line([(x - r * 0.45, y - r * 0.1), (x + r * 0.45, y - r * 0.1)], max(1.2, r * 0.18), 0 if v else 255)


def coin(g: G, cx, cy, r, v=255):
    """A round coin with a square hole."""
    g.circ(cx, cy, r, v)
    g.circ(cx, cy, r * 0.8, 0 if v else 255)
    g.circ(cx, cy, r * 0.68, v)
    h = r * 0.24
    g.poly([(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)], 0 if v else 255)


def roof(g: G, cx, y, w, h, v=255):
    """A pagoda roof with upturned eaves."""
    g.poly([(cx - w, y + h * 0.15), (cx, y - h), (cx + w, y + h * 0.15), (cx + w * 0.85, y + h * 0.3),
            (cx, y - h * 0.45), (cx - w * 0.85, y + h * 0.3)], v)


def bowl(g: G, cx, cy, w, v=255):
    g.ell(cx - w, cy - w * 0.35, cx + w, cy + w * 0.75, v)
    g.poly([(cx - w - 1, cy - w * 0.35), (cx + w + 1, cy - w * 0.35), (cx + w + 1, cy + 0.5), (cx - w - 1, cy + 0.5)], v)
    g.ell(cx - w * 0.85, cy - w * 0.48, cx + w * 0.85, cy - w * 0.12, 0 if v else 255)  # mouth
    g.poly([(cx - w * 0.4, cy + w * 0.7), (cx + w * 0.4, cy + w * 0.7), (cx + w * 0.5, cy + w * 0.9), (cx - w * 0.5, cy + w * 0.9)], v)


def ding(g: G, cx, cy, s, v=255):
    """A three-legged refining cauldron."""
    g.ell(cx - 26 * s, cy - 18 * s, cx + 26 * s, cy + 18 * s, v)
    g.poly([(cx - 28 * s, cy - 18 * s), (cx + 28 * s, cy - 18 * s), (cx + 24 * s, cy - 8 * s), (cx - 24 * s, cy - 8 * s)], v)
    for x in (-14, 0, 14):
        g.line([(cx + x * s, cy + 12 * s), (cx + x * 1.2 * s, cy + 26 * s)], 5 * s, v)
    for side in (-1, 1):
        g.arc_band(cx + side * 16 * s, cy - 22 * s, 7 * s, 3.5 * s, 0, 180, v)


def flame(g: G, cx, base, h, v=255):
    g.poly([(cx - h * 0.35, base), (cx - h * 0.25, base - h * 0.5), (cx - h * 0.05, base - h * 0.35), (cx, base - h),
            (cx + h * 0.12, base - h * 0.45), (cx + h * 0.28, base - h * 0.6), (cx + h * 0.35, base)], v)


def scroll(g: G, cx, cy, w, h, v=255):
    g.poly([(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h)], v)
    for side in (-1, 1):
        g.ell(cx + side * w - 4, cy - h - 3, cx + side * w + 4, cy + h + 3, v)
    for k in range(3):
        g.line([(cx - w * 0.6, cy - h * 0.5 + k * h * 0.5), (cx + w * 0.6, cy - h * 0.5 + k * h * 0.5)], 2.2, 0 if v else 255)


def orchid(g: G, cx, cy, r, v=255):
    for k in range(5):
        a = math.radians(90 + k * 72)
        x, y = cx + r * math.cos(a), cy - r * math.sin(a)
        g.ell(x - r * 0.68, y - r * 0.68, x + r * 0.68, y + r * 0.68, v)
    g.circ(cx, cy, r * 0.38, 0 if v else 255)
    g.circ(cx, cy, r * 0.2, v)


def aperture(g: G, cx, cy, r, v=255):
    """The aperture: a ring with an inner opening and four light rays."""
    g.circ(cx, cy, r, v); g.circ(cx, cy, r * 0.62, 0 if v else 255); g.circ(cx, cy, r * 0.32, v)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        g.poly([(cx + r * 1.08 * math.cos(a - 0.12), cy - r * 1.08 * math.sin(a - 0.12)),
                (cx + r * 1.45 * math.cos(a), cy - r * 1.45 * math.sin(a)),
                (cx + r * 1.08 * math.cos(a + 0.12), cy - r * 1.08 * math.sin(a + 0.12))], v)


def octagon_array(g: G, cx, cy, r, v=255):
    """A formation: an octagon ring with broken and whole bars (trigram-like marks)."""
    g.poly(regular(cx, cy, r, 8, 22.5), v); g.poly(regular(cx, cy, r * 0.78, 8, 22.5), 0 if v else 255)
    for k in range(8):
        a = math.radians(22.5 + 45 * k + 22.5)
        x, y = cx + r * 0.6 * math.cos(a), cy - r * 0.6 * math.sin(a)
        g.circ(x, y, r * 0.08, v)
    g.circ(cx, cy, r * 0.3, v); g.circ(cx, cy, r * 0.16, 0 if v else 255)


def bear_head(g: G, cx, cy, s, v=255):
    g.circ(cx - 20 * s, cy - 18 * s, 9 * s, v); g.circ(cx + 20 * s, cy - 18 * s, 9 * s, v)     # ears
    g.ell(cx - 26 * s, cy - 22 * s, cx + 26 * s, cy + 24 * s, v)
    g.circ(cx - 10 * s, cy - 6 * s, 3 * s, 0); g.circ(cx + 10 * s, cy - 6 * s, 3 * s, 0)
    g.ell(cx - 11 * s, cy + 4 * s, cx + 11 * s, cy + 20 * s, 0)                                # muzzle
    g.ell(cx - 5 * s, cy + 5 * s, cx + 5 * s, cy + 11 * s, v)                                  # nose


def paw(g: G, cx, cy, s, v=255):
    g.ell(cx - 18 * s, cy - 4 * s, cx + 18 * s, cy + 24 * s, v)
    for k, (dx, dy) in enumerate(((-20, -14), (-8, -24), (8, -24), (20, -14))):
        g.ell(cx + (dx - 6) * s, cy + (dy - 7) * s, cx + (dx + 6) * s, cy + (dy + 7) * s, v)
        g.poly([(cx + (dx - 3) * s, cy + (dy - 6) * s), (cx + dx * s, cy + (dy - 15) * s), (cx + (dx + 3) * s, cy + (dy - 6) * s)], v)


def waves(g: G, cx, cy, w, n=3, v=255):
    for k in range(n):
        y = cy + (k - (n - 1) / 2) * 14
        pts = [(cx - w + i * (2 * w / 24), y + 4 * math.sin(i * math.pi / 4)) for i in range(25)]
        g.line(pts, 4.5, v)


def slash(g: G, v=0, w=7):
    """A diagonal strike-through (cut out of the glyph by default)."""
    g.line([(14, 86), (86, 14)], w, v)


def boar_body(g: G, v=255):
    """Side view of a wild boar, facing left: bristled back, short legs, tusk."""
    g.ell(26, 34, 84, 72, v)
    g.poly([(30, 38), (12, 48), (8, 58), (16, 62), (30, 64)], v)                      # head and snout
    for x in (34, 46, 64, 76):
        g.poly([(x - 4, 66), (x + 4, 66), (x + 3, 84), (x - 3, 84)], v)                # legs
    for k in range(7):                                                               # bristles
        x = 36 + k * 6
        g.poly([(x - 3, 37), (x, 26 + (k % 2) * 3), (x + 3, 37)], v)
    g.poly([(84, 46), (92, 40), (88, 52)], v)                                        # tail
    g.circ(22, 50, 2.2, 0)                                                           # eye
    g.arc_band(14, 58, 8, 5, 200, 300, 0 if v else 255)                              # mouth line
    g.poly([(12, 60), (16, 52), (19, 60)], v)                                        # tusk


# ---------------------------------------------------------------- units (white)
def clan_settler():
    g = G(); human(g, 42, 12, 1.2)
    g.line([(66, 8), (66, 86)], 4); g.poly([(68, 10), (92, 18), (68, 28)])            # clan banner
    g.ell(16, 52, 34, 70)                                                            # bundle
    return g


def mortal_laborer():
    g = G()
    g.line([(20, 86), (66, 22)], 6); g.poly([(58, 12), (82, 22), (74, 34), (62, 28)])  # hoe
    g.line([(80, 86), (36, 28)], 6); g.poly([(26, 14), (44, 18), (42, 34), (30, 32)])  # spade
    return g


def bold_lightning_wolf():
    g = lightning_wolf(bold=True)
    g.bolt([16, 26, 12, 22], 4, 40, 5)
    return g


# ---------------------------------------------------------------- promotions (white)
def aptitude(grade):
    def draw():
        g = G()
        g.circ(50, 50, 40); g.circ(50, 50, 32, 0)
        rays = {"A": 8, "B": 4, "C": 0, "D": 0}[grade]
        for k in range(rays):
            a = math.radians(90 + 360 * k / rays)
            g.poly([(50 + 40 * math.cos(a - 0.1), 50 - 40 * math.sin(a - 0.1)), (50 + 50 * math.cos(a), 50 - 50 * math.sin(a)),
                    (50 + 40 * math.cos(a + 0.1), 50 - 40 * math.sin(a + 0.1))])
        if grade == "D":
            g.line([(30, 14), (40, 30), (34, 40)], 4, 0)                                  # a cracked aperture
        letter(g, grade, 50, 52, 46)
        return g
    return draw


def bear_strength_gu():
    g = G(); paw(g, 50, 56, 1.2); return g


def black_boar_gu():
    g = G(); g.circ(50, 50, 46)
    inner = G(); boar_head(inner, 50, 50, 0.95); g.paste(inner, 0)                   # the boar cut out of a dark disc
    return g


def white_jade_gu():
    g = G(); g.circ(50, 52, 30); g.circ(50, 52, 12, 0)
    for k in range(6):
        a = math.radians(30 + 60 * k)
        g.circ(50 + 21 * math.cos(a), 52 - 21 * math.sin(a), 2.4, 0)
    for side in (-1, 1):
        g.arc_band(50 + side * 34, 30, 14, 9, 190 if side < 0 else -80, 280 if side < 0 else 10)
    return g


def moon_raiment():
    g = G()
    g.poly([(36, 14), (64, 14), (90, 34), (80, 46), (70, 40), (72, 90), (28, 90), (30, 40), (20, 46), (10, 34)])
    g.poly([(42, 14), (58, 14), (50, 28)], 0)                                        # collar
    g.crescent(50, 58, 13, 6, angle=0, v=0)
    return g


def refine_gu():
    g = G(); ding(g, 50, 62, 1.0)
    gu_beetle(g, 50, 22, 0.55, legs=False)
    return g


def stream_gu():
    g = G(); waves(g, 50, 52, 36); return g


def hunger(food_draw):
    def draw():
        g = G()
        bowl(g, 50, 70, 26)
        food_draw(g)
        slash(g, 0, 8)
        return g
    return draw


def _orchid_small(g): orchid(g, 50, 30, 12)
def _boar_small(g): boar_head(g, 50, 32, 0.55)
def _jade_small(g): g.circ(50, 30, 16); g.circ(50, 30, 6, 0)
def _wine_small(g):
    g.ell(38, 22, 62, 50); g.poly([(44, 12), (56, 12), (54, 24), (46, 24)])


# ---------------------------------------------------------------- resources, improvements, buildings (black)
def wild_boar():
    g = G(); boar_body(g); return g


def spring_cave():
    g = G()
    g.arc_band(50, 74, 42, 30, 0, 180); g.poly([(4, 74), (96, 74), (96, 80), (4, 80)])
    g.ell(30, 62, 70, 74); g.ell(36, 64, 64, 71, 0)
    gem(g, 50, 46, 9)
    return g


def beast_lair():
    g = G()
    g.poly([(4, 90), (18, 44), (34, 24), (50, 16), (66, 24), (82, 44), (96, 90)])       # rock
    g.arc_band(50, 90, 36, 32, 0, 180, 0)                                               # outline of the den mouth
    for x in (40, 60):
        g.poly([(x - 6, 70), (x + 6, 67), (x + 3, 75), (x - 3, 75)], 0)                 # eyes glowing in the dark
    for k, x in enumerate((26, 74)):                                                  # bones at the entrance
        g.line([(x - 8, 94 - k * 2), (x + 8, 90 + k * 2)], 3)
    return g


def inheritance_site():
    g = G()
    g.poly([(30, 22), (70, 22), (74, 84), (26, 84)]); g.ell(30, 12, 70, 32)           # stele
    g.poly([(18, 84), (82, 84), (86, 94), (14, 94)])
    orchid(g, 50, 52, 9, v=0)
    return g


def flower_wine_monk_inheritance():
    g = G()
    for k, a in enumerate((90, 60, 120, 30, 150)):                                    # lotus
        r = math.radians(a); cx, cy = 42 + 16 * math.cos(r), 64 - 16 * math.sin(r)
        g.poly([(42, 66), (cx - 8, cy), (cx, cy - 16), (cx + 8, cy)])
    g.ell(18, 64, 66, 76)
    g.ell(66, 34, 90, 62); g.ell(70, 18, 86, 38); g.line([(78, 10), (78, 20)], 4)      # wine gourd
    g.line([(74, 38), (82, 38)], 2.5, 0)
    return g


def stockade_wall():
    """The village's stockade wall (寨墙): sharpened spear-bamboo stakes bound by two bands, a gate in the middle."""
    g = G()
    for k in range(8):
        x = 9 + k * 11.7
        if k in (3, 4):
            continue                                                                    # the gate
        top = 18 if k % 2 else 24
        g.poly([(x - 4.5, 90), (x + 4.5, 90), (x + 4.5, top + 9), (x, top), (x - 4.5, top + 9)])
    g.poly([(36, 90), (64, 90), (64, 44), (50, 34), (36, 44)])                         # gate tower
    g.poly([(42, 90), (58, 90), (58, 56), (42, 56)], 0)                                 # gate opening
    for y in (52, 74):
        g.line([(4, y), (36, y)], 3.5); g.line([(64, y), (96, y)], 3.5)                # binding bands
    return g


def gu_academy():
    g = G(); roof(g, 50, 30, 44, 20)
    g.poly([(18, 36), (82, 36), (82, 40), (18, 40)])
    scroll(g, 50, 64, 26, 16)
    gu_beetle(g, 50, 8, 0.32, legs=False)
    return g


def gu_feeding_house():
    g = G(); bowl(g, 50, 62, 36)
    gu_beetle(g, 50, 30, 0.75)
    return g


def martial_arena():
    g = G()
    g.poly([(8, 70), (92, 70), (84, 92), (16, 92)])                                    # stage
    g.poly([(24, 70), (76, 70), (72, 62), (28, 62)])
    for x in (14, 86):
        g.line([(x, 70), (x, 22)], 4); g.poly([(x - 6, 22), (x + 6, 22), (x, 14)])       # banner poles
    fist(g, 50, 36, 0.62)
    return g


def moon_orchid_flower_sea():
    g = G()
    g.crescent(50, 18, 15, 7, angle=270)
    for x, y, r in ((24, 58, 12), (76, 58, 12), (50, 78, 12)):
        orchid(g, x, y, r)
        g.line([(x, y + 12), (x, 96)], 3)
    return g


def shang_clan_city():
    g = G()
    g.poly([(6, 92), (6, 40), (18, 40), (18, 48), (30, 48), (30, 40), (42, 40), (42, 48), (58, 48), (58, 40), (70, 40),
            (70, 48), (82, 48), (82, 40), (94, 40), (94, 92)])
    g.ell(34, 62, 66, 94, 0); g.poly([(34, 78), (66, 78), (66, 94), (34, 94)], 0)        # gate
    coin(g, 50, 20, 16)
    return g


def tavern():
    g = G()
    g.line([(20, 8), (20, 92)], 5); g.line([(20, 14), (60, 14)], 4)
    g.poly([(30, 18), (58, 18), (58, 62), (44, 54), (30, 62)])                          # wine flag
    g.ell(56, 52, 90, 92); g.poly([(64, 46), (82, 46), (80, 56), (66, 56)])               # jar
    g.line([(36, 30), (52, 30)], 3, 0); g.line([(36, 40), (52, 40)], 3, 0)
    return g


def trading_house():
    g = G()
    for x, y, r in ((28, 72, 14), (54, 74, 15), (76, 70, 12), (40, 50, 13), (64, 50, 12), (52, 28, 13)):
        gem(g, x, y, r)
    return g


# ---------------------------------------------------------------- city-state types, nations (white)
def merchant_clan():
    g = G(); coin(g, 50, 50, 40); return g


def mortal_villages():
    g = G()
    roof(g, 46, 40, 34, 24); g.poly([(20, 44), (72, 44), (72, 84), (20, 84)])
    g.poly([(38, 60), (54, 60), (54, 84), (38, 84)], 0)
    g.line([(84, 88), (84, 30)], 3)                                                    # rice stalk
    for k in range(5):
        g.ell(80 - (k % 2) * 6, 26 + k * 8, 88 - (k % 2) * 6, 34 + k * 8)
    return g


def refiner_tribe():
    g = G(); ding(g, 44, 64, 0.95)
    g.line([(70, 46), (88, 14)], 5); g.poly([(78, 8), (96, 18), (90, 26), (72, 16)])     # hammer
    return g


def bai_clan():
    g = G()
    g.poly([(8, 88), (40, 20), (56, 50), (66, 36), (92, 88)])                           # mountain
    g.poly([(40, 20), (50, 40), (44, 38), (40, 46), (34, 34)], 0)                       # snow line
    waves(g, 50, 74, 30, n=2, v=0)
    return g


def xiong_clan():
    g = G(); bear_head(g, 50, 52, 1.35); return g


def wu_clan():
    g = G()
    for k in range(12):                                                               # aura
        a = math.radians(k * 30)
        g.poly([(50 + 30 * math.cos(a - 0.14), 48 - 30 * math.sin(a - 0.14)), (50 + 46 * math.cos(a), 48 - 46 * math.sin(a)),
                (50 + 30 * math.cos(a + 0.14), 48 - 30 * math.sin(a + 0.14))])
    g.circ(50, 48, 31, 0)
    fist(g, 50, 46, 0.78)
    return g


# ---------------------------------------------------------------- policy branches and policies (white)
def righteous_path():
    g = G()
    for k in range(10):                                                               # radiance behind the blade
        a = math.radians(90 + k * 36)
        g.poly([(50 + 22 * math.cos(a - 0.13), 40 - 22 * math.sin(a - 0.13)), (50 + 40 * math.cos(a), 40 - 40 * math.sin(a)),
                (50 + 22 * math.cos(a + 0.13), 40 - 22 * math.sin(a + 0.13))])
    g.circ(50, 40, 20, 0)
    g.poly([(45, 4), (55, 4), (55, 66), (50, 74), (45, 66)])                           # straight sword (jian)
    g.line([(50, 10), (50, 62)], 1.6, 0)
    g.poly([(30, 66), (70, 66), (66, 74), (34, 74)]); g.line([(50, 74), (50, 90)], 7); g.circ(50, 93, 4)
    return g


def demonic_path():
    g = G()
    g.poly([(26, 34), (8, 4), (20, 8), (38, 26)]); g.poly([(74, 34), (92, 4), (80, 8), (62, 26)])   # horns
    g.ell(20, 18, 80, 72)                                                              # cranium
    g.poly([(30, 60), (70, 60), (66, 86), (34, 86)])                                   # jaw
    g.ell(28, 38, 46, 56, 0); g.ell(54, 38, 72, 56, 0)                                 # sockets
    g.poly([(50, 56), (45, 66), (55, 66)], 0)                                           # nose
    for x in (38, 46, 54, 62):
        g.line([(x, 72), (x, 84)], 2.2, 0)                                              # teeth
    return g


def moon_path():
    g = G(); g.crescent(46, 50, 38, 16, angle=20)
    g.poly(regular(74, 30, 9, 4, 90)); g.poly(regular(80, 62, 6, 4, 90))
    return g


def strength_path():
    g = G(); fist(g, 50, 46, 1.2); return g


def clan_rules():
    g = G(); scroll(g, 50, 46, 30, 26)
    g.poly([(58, 70), (78, 70), (78, 90), (58, 90)])                                   # seal
    return g


def righteous_alliance():
    g = G()
    for cx in (36, 64):
        g.circ(cx, 50, 26); g.circ(cx, 50, 19, 0)
    g.arc_band(36, 50, 26, 19, -40, 40)                                                 # interlock
    return g


def guardian_formations():
    g = G()
    g.poly([(50, 6), (88, 18), (84, 58), (50, 94), (16, 58), (12, 18)])
    g.poly([(50, 14), (80, 24), (77, 56), (50, 86), (23, 56), (20, 24)], 0)
    octagon_array(g, 50, 46, 22)
    return g


def plunder():
    g = G(); g.ell(18, 36, 82, 94); g.poly([(36, 20), (64, 20), (58, 40), (42, 40)])
    g.line([(38, 38), (62, 38)], 3, 0)
    gem(g, 50, 66, 12, v=0)
    return g


def lone_cultivators():
    g = G(); human(g, 44, 10, 1.25)
    g.line([(72, 14), (66, 92)], 4)                                                    # walking staff
    g.crescent(84, 14, 9, 4, angle=200)
    return g


def ruthless_cultivation():
    g = G()
    g.poly([(46, 6), (54, 6), (56, 60), (50, 70), (44, 60)]); g.poly([(30, 60), (70, 60), (70, 66), (30, 66)])
    g.line([(50, 66), (50, 84)], 6)
    for x, y in ((24, 30), (78, 42), (70, 82)):                                         # drops
        g.circ(x, y, 6); g.poly([(x - 5.5, y - 2), (x, y - 14), (x + 5.5, y - 2)])
    return g


def moonlight_mastery():
    g = G(); g.crescent(50, 50, 30, 13, angle=0); gu_beetle(g, 66, 50, 0.5)
    for k in range(8):
        a = math.radians(k * 45)
        g.line([(50 + 38 * math.cos(a), 50 - 38 * math.sin(a)), (50 + 46 * math.cos(a), 50 - 46 * math.sin(a))], 3.5)
    return g


def orchid_beds():
    """Orchid beds in the spring cave: a cave arch with stalactites over a bed of moon orchids."""
    g = G()
    g.arc_band(50, 64, 48, 40, 0, 180)                                                  # cave mouth
    for x, l in ((30, 14), (44, 9), (58, 16), (70, 10)):
        g.poly([(x - 3, 26), (x + 3, 26), (x, 26 + l)])                                  # stalactites
    g.poly([(8, 82), (92, 82), (92, 90), (8, 90)])                                      # the bed
    for x, y, r in ((28, 66, 9), (50, 60, 11), (72, 66, 9)):
        orchid(g, x, y, r); g.line([(x, y + r), (x, 82)], 2.5)
    return g


def moon_blade_step():
    g = G(); g.crescent(62, 42, 26, 11, angle=180)
    for k in range(3):
        g.line([(10, 30 + k * 14), (34 - k * 4, 30 + k * 14)], 4)
    for x, y in ((24, 82), (44, 88)):
        g.ell(x - 6, y - 9, x + 6, y + 9)                                              # footprints
    return g


def boar_strength():
    g = G(); boar_head(g, 50, 48, 1.05); return g


def beast_hunters():
    g = G(); wolf_head(g, 46, 54, 0.85)
    g.line([(18, 92), (90, 10)], 4.5); g.poly([(84, 6), (96, 4), (92, 16)])             # spear
    return g


def unyielding_body():
    g = G()
    g.circ(50, 22, 10)
    g.poly([(30, 36), (70, 36), (64, 86), (36, 86)])                                   # torso
    for side in (-1, 1):                                                              # flexed arms, fists up
        g.line([(50 + side * 18, 40), (50 + side * 36, 52), (50 + side * 38, 30)], 9)
        g.circ(50 + side * 38, 24, 7.5)
    g.line([(50, 46), (50, 70)], 2, 0); g.line([(40, 56), (60, 56)], 2, 0)              # chest lines
    return g


# ---------------------------------------------------------------- techs (white)
def aperture_awakening():
    g = G(); aperture(g, 50, 50, 28); return g


def rank_cultivation(n):
    def draw():
        g = G(); aperture(g, 50, 42, 22)
        pips(g, n, y=88)
        return g
    return draw


def tech_spirit_spring_lore():
    from .glyphs import spirit_spring
    return spirit_spring()


def gu_feeding():
    g = G(); bowl(g, 50, 66, 30); gu_beetle(g, 50, 32, 0.7); return g


def wine_brewing():
    g = G(); g.ell(24, 34, 70, 90); g.poly([(36, 22), (58, 22), (56, 36), (38, 36)]); g.ell(32, 12, 62, 26)
    for x, y in ((80, 40), (86, 60), (76, 76)):
        g.circ(x, y, 5); g.poly([(x - 4.5, y - 2), (x, y - 11), (x + 4.5, y - 2)])
    return g


def gu_refinement():
    g = G(); ding(g, 50, 60, 1.05)
    for x in (40, 50, 60):
        flame(g, x, 34, 20)
    return g


def gu_formations():
    g = G(); octagon_array(g, 50, 50, 42); return g


def merchant_caravans():
    g = G(); g.circ(36, 64, 22); g.circ(36, 64, 16, 0); g.circ(36, 64, 5)
    for k in range(8):
        a = math.radians(k * 45)
        g.line([(36, 64), (36 + 16 * math.cos(a), 64 - 16 * math.sin(a))], 2.5)
    coin(g, 72, 30, 20)
    return g


def inheritance_lore():
    g = G(); scroll(g, 50, 56, 30, 22); orchid(g, 50, 18, 10); return g


def killer_moves_tech():
    from .glyphs import killer_move
    return killer_move()


def super_clan_commerce():
    g = G(); roof(g, 50, 30, 44, 22); coin(g, 50, 66, 24); return g


def beast_enslavement():
    g = G(); wolf_head(g, 52, 46, 0.95)
    for k in range(4):                                                                 # chain
        x = 16 + k * 14
        g.ell(x - 7, 80, x + 7, 92); g.ell(x - 4, 83, x + 4, 89, 0)
    return g


def dao_comprehension():
    g = G()
    pts = [(50 + (3 + 3.6 * t) * math.cos(t), 50 - (3 + 3.6 * t) * math.sin(t)) for t in [i * 0.12 for i in range(100)]]
    g.line(pts, 5)
    return g


def gu_inheritance():
    """A sealed inheritance chest with a Gu on its lid."""
    g = G()
    g.poly([(14, 46), (86, 46), (82, 90), (18, 90)])                                    # chest
    g.ell(14, 26, 86, 60); g.poly([(14, 44), (86, 44), (86, 48), (14, 48)])
    g.line([(14, 46), (86, 46)], 3, 0)
    g.poly([(44, 56), (56, 56), (56, 72), (44, 72)], 0); g.circ(50, 62, 3)               # lock
    gu_beetle(g, 50, 18, 0.45, legs=False, v=0)
    for k in range(7):
        a = math.radians(30 + k * 20)
        g.line([(50 + 40 * math.cos(a), 30 - 26 * math.sin(a)), (50 + 48 * math.cos(a), 30 - 32 * math.sin(a))], 2.5)
    return g


def inheritance_dig():
    g = G()
    g.poly([(26, 22), (74, 22), (78, 70), (22, 70)]); g.ell(26, 10, 74, 34)             # stele
    g.circ(50, 42, 9, 0); g.circ(50, 42, 4)
    g.line([(60, 94), (88, 58)], 5); g.poly([(84, 50), (96, 58), (90, 66), (80, 60)])     # spade
    g.ell(8, 74, 60, 94)                                                                 # dug earth
    return g


def primeval_stone_icon(size=100):
    """A coloured primeval stone (the Gold stat icon): a faceted gem in three tones with a dark rim, like the base
    game's coloured stat icons."""
    from PIL import Image, ImageDraw
    k = 4
    n = size * k
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    P = lambda pts: [(x * n / 100, y * n / 100) for x, y in pts]  # noqa: E731
    outer = [(50, 6), (86, 30), (80, 74), (50, 94), (20, 74), (14, 30)]
    d.polygon(P(outer), fill=(46, 70, 66))
    inner = [(50, 12), (80, 32), (75, 71), (50, 88), (25, 71), (20, 32)]
    d.polygon(P(inner), fill=(160, 205, 190))
    d.polygon(P([(50, 12), (80, 32), (50, 44), (20, 32)]), fill=(232, 246, 238))      # top facet
    d.polygon(P([(20, 32), (50, 44), (50, 88), (25, 71)]), fill=(196, 228, 214))      # left facet
    d.polygon(P([(80, 32), (75, 71), (50, 88), (50, 44)]), fill=(122, 170, 156))      # right facet, in shade
    d.polygon(P([(36, 22), (48, 18), (40, 30)]), fill=(255, 255, 255))                # glint
    return im.resize((size, size), Image.LANCZOS)


def ranked_gu_master(rank):
    """C3 rank chain, any path: a cultivator raising an essence orb; pips give the rank."""
    g = G(); human(g, 42, 8, 1.25, arms="raised"); g.circ(78, 20, 9 + rank); pips(g, rank); return g


def water_gu_master(rank):
    """The Bai clan's water path (Stream Gu): a cultivator behind a breaking wave."""
    g = G(); human(g, 32, 8, 1.2, arms="forward")
    g.arc_band(74, 62, 22 + 2 * rank, 13 + 2 * rank, 0, 180)                   # wave crest
    g.circ(62, 50, 6)                                                          # spray
    pips(g, rank); return g


def demonic_infamy():
    """A horned demon mask with a bounty notch: the mark righteous clans hunt."""
    g = G()
    g.ell(22, 26, 78, 90)
    for side in (-1, 1):
        g.poly([(50 + side * 18, 34), (50 + side * 40, 6), (50 + side * 28, 40)])         # horns
    g.poly([(32, 50), (46, 56), (34, 60)], 0); g.poly([(68, 50), (54, 56), (66, 60)], 0)  # slanted eyes
    g.poly([(38, 74), (62, 74), (58, 80), (50, 76), (42, 80)], 0)                       # fanged mouth
    return g


ICONS2 = [
    ("ResourceIcons", "Gu Inheritance", gu_inheritance, "black"),
    ("ImprovementIcons", "Inheritance Dig", inheritance_dig, "black"),
    ("UnitIcons", "Clan Settler", clan_settler, "white"),
    ("UnitIcons", "Mortal Laborer", mortal_laborer, "white"),
    ("UnitIcons", "Rank Three Moon Gu Master", lambda: moon_gu_master(3), "white"),
    ("UnitIcons", "Rank Three Strength Gu Master", lambda: strength_gu_master(3), "white"),
    ("UnitIcons", "Rank Four Strength Gu Master", lambda: strength_gu_master(4), "white"),
    ("UnitIcons", "Bold Lightning Wolf", bold_lightning_wolf, "white"),
    # C3: the rank chain and the signature clans' chains (their path's emblem)
    *[("UnitIcons", f"Rank {w} {clan}Gu Master", (lambda r=r, f=f: f(r)), "white")
      for w, r in (("Two", 2), ("Three", 3), ("Four", 4))
      for clan, f in (("", ranked_gu_master), ("Gu Yue ", moon_gu_master), ("Bai ", water_gu_master),
                      ("Xiong ", strength_gu_master), ("Wu ", strength_gu_master))],
    ("UnitPromotionIcons", "Aptitude A", aptitude("A"), "white"),
    ("UnitPromotionIcons", "Aptitude B", aptitude("B"), "white"),
    ("UnitPromotionIcons", "Aptitude C", aptitude("C"), "white"),
    ("UnitPromotionIcons", "Aptitude D", aptitude("D"), "white"),
    ("UnitPromotionIcons", "Bear Strength Gu", bear_strength_gu, "white"),
    ("UnitPromotionIcons", "Black Boar Gu", black_boar_gu, "white"),
    ("UnitPromotionIcons", "White Jade Gu", white_jade_gu, "white"),
    ("UnitPromotionIcons", "Moon Raiment", moon_raiment, "white"),
    ("UnitPromotionIcons", "Refine Gu", refine_gu, "white"),
    ("UnitPromotionIcons", "Stream Gu", stream_gu, "white"),
    ("UnitPromotionIcons", "Orchid Hunger", hunger(_orchid_small), "white"),
    ("UnitPromotionIcons", "Pork Hunger", hunger(_boar_small), "white"),
    ("UnitPromotionIcons", "Jade Hunger", hunger(_jade_small), "white"),
    ("UnitPromotionIcons", "Wine Hunger", hunger(_wine_small), "white"),
    ("ResourceIcons", "Wild Boar", wild_boar, "black"),
    ("ImprovementIcons", "Spring Cave", spring_cave, "black"),
    ("ImprovementIcons", "Beast Lair", beast_lair, "black"),
    ("ImprovementIcons", "Inheritance Site", inheritance_site, "black"),
    ("BuildingIcons", "Flower Wine Monk Inheritance", flower_wine_monk_inheritance, "black"),
    ("BuildingIcons", "Stockade Wall", stockade_wall, "black"),
    ("BuildingIcons", "Gu Academy", gu_academy, "black"),
    ("BuildingIcons", "Gu Feeding House", gu_feeding_house, "black"),
    ("BuildingIcons", "Martial Arena", martial_arena, "black"),
    ("BuildingIcons", "Moon Orchid Flower Sea", moon_orchid_flower_sea, "black"),
    ("BuildingIcons", "Shang Clan City", shang_clan_city, "black"),
    ("BuildingIcons", "Tavern", tavern, "black"),
    ("BuildingIcons", "Trading House", trading_house, "black"),
    ("CityStateIcons", "Merchant Clan", merchant_clan, "white"),
    ("CityStateIcons", "Mortal Villages", mortal_villages, "white"),
    ("CityStateIcons", "Refiner Tribe", refiner_tribe, "white"),
    ("NationIcons", "Bai Clan", bai_clan, "white"),
    ("NationIcons", "Xiong Clan", xiong_clan, "white"),
    ("NationIcons", "Wu Clan", wu_clan, "white"),
    ("PolicyBranchIcons", "Righteous Path", righteous_path, "white"),
    ("PolicyBranchIcons", "Demonic Path", demonic_path, "white"),
    ("PolicyBranchIcons", "Moon Path", moon_path, "white"),
    ("PolicyBranchIcons", "Strength Path", strength_path, "white"),
    ("PolicyIcons", "Clan Rules", clan_rules, "white"),
    ("PolicyIcons", "Righteous Alliance", righteous_alliance, "white"),
    ("PolicyIcons", "Guardian Formations", guardian_formations, "white"),
    ("PolicyIcons", "Plunder", plunder, "white"),
    ("PolicyIcons", "Lone Cultivators", lone_cultivators, "white"),
    ("PolicyIcons", "Ruthless Cultivation", ruthless_cultivation, "white"),
    ("PolicyIcons", "Moonlight Mastery", moonlight_mastery, "white"),
    ("PolicyIcons", "Orchid Beds", orchid_beds, "white"),
    ("UnitPromotionIcons", "Demonic Infamy", demonic_infamy, "white"),
    ("PolicyIcons", "Moon Blade Step", moon_blade_step, "white"),
    ("PolicyIcons", "Boar Strength", boar_strength, "white"),
    ("PolicyIcons", "Beast Hunters", beast_hunters, "white"),
    ("PolicyIcons", "Unyielding Body", unyielding_body, "white"),
    ("TechIcons", "Aperture Awakening", aperture_awakening, "white"),
    ("TechIcons", "Spirit Spring Lore", tech_spirit_spring_lore, "white"),
    ("TechIcons", "Gu Feeding", gu_feeding, "white"),
    ("TechIcons", "Wine Brewing", wine_brewing, "white"),
    ("TechIcons", "Gu Refinement", gu_refinement, "white"),
    ("TechIcons", "Rank Two Cultivation", rank_cultivation(2), "white"),
    ("TechIcons", "Gu Formations", gu_formations, "white"),
    ("TechIcons", "Rank Three Cultivation", rank_cultivation(3), "white"),
    ("TechIcons", "Merchant Caravans", merchant_caravans, "white"),
    ("TechIcons", "Inheritance Lore", inheritance_lore, "white"),
    ("TechIcons", "Killer Moves", killer_moves_tech, "white"),
    ("TechIcons", "Super Clan Commerce", super_clan_commerce, "white"),
    ("TechIcons", "Beast Enslavement", beast_enslavement, "white"),
    ("TechIcons", "Rank Four Cultivation", rank_cultivation(4), "white"),
    ("TechIcons", "Dao Comprehension", dao_comprehension, "white"),
]
