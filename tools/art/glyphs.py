"""Original procedural glyphs for the Gu World mod, in Unciv's flat-icon style (one-colour silhouette, 100x100,
transparent). Drawn on a 4x supersampled mask, then downsampled. Every shape here is built from primitives."""
from __future__ import annotations

import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

S = 4          # supersampling
N = 100 * S    # canvas


class G:
    """A glyph mask in 0..100 coordinates; ink() adds, cut() removes."""

    def __init__(self):
        self.m = Image.new("L", (N, N), 0)
        self.d = ImageDraw.Draw(self.m)

    @staticmethod
    def p(pts):
        return [(x * S, y * S) for x, y in pts]

    def poly(self, pts, v=255):
        self.d.polygon(self.p(pts), fill=v)

    def ell(self, x0, y0, x1, y1, v=255):
        self.d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=v)

    def circ(self, cx, cy, r, v=255):
        self.ell(cx - r, cy - r, cx + r, cy + r, v)

    def line(self, pts, w, v=255):
        self.d.line(self.p(pts), fill=v, width=int(w * S), joint="curve")
        for x, y in (pts[0], pts[-1]):
            self.circ(x, y, w / 2, v)

    def arc_band(self, cx, cy, r_out, r_in, a0, a1, v=255, steps=64):
        """A thick arc (annulus sector) from angle a0 to a1 in degrees (0 = east, counter-clockwise, y up)."""
        outer = [(cx + r_out * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
                  cy - r_out * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
        inner = [(cx + r_in * math.cos(math.radians(a1 - (a1 - a0) * i / steps)),
                  cy - r_in * math.sin(math.radians(a1 - (a1 - a0) * i / steps))) for i in range(steps + 1)]
        self.poly(outer + inner, v)

    def crescent(self, cx, cy, r, shift, angle=0, v=255):
        """A crescent: disc minus an offset disc; `angle` points the hollow side (degrees, 0 = east)."""
        c = G()
        c.circ(cx, cy, r)
        dx, dy = shift * math.cos(math.radians(angle)), -shift * math.sin(math.radians(angle))
        c.circ(cx + dx, cy + dy, r * 0.92, 0)
        self.paste(c, v)

    def paste(self, other: "G", v=255):
        if v:
            self.m = ImageChops.lighter(self.m, other.m)
        else:
            self.m = ImageChops.subtract(self.m, other.m)
        self.d = ImageDraw.Draw(self.m)

    def bolt(self, pts_x, y0, y1, w, v=255):
        """A zig-zag lightning bolt through the given x positions, evenly spread from y0 to y1."""
        n = len(pts_x) - 1
        pts = [(x, y0 + (y1 - y0) * i / n) for i, x in enumerate(pts_x)]
        self.line(pts, w, v)
        self.poly([(pts[-1][0] - w * 1.2, pts[-1][1] - w), (pts[-1][0] + w * 1.2, pts[-1][1] - w * 0.4),
                   (pts[-1][0] + w * 0.3, pts[-1][1] + w * 2.2)], v)

    def image(self, colour=(255, 255, 255), size=100) -> Image.Image:
        mask = self.m.resize((size, size), Image.LANCZOS)
        out = Image.new("RGBA", (size, size), colour + (0,))
        out.putalpha(mask)
        return out


# ---------------------------------------------------------------- motifs
def gu_beetle(g: G, cx, cy, s, v=255, legs=True):
    """The generic Gu: an oval shell split by a seam, a small head, six legs."""
    g.ell(cx - 9 * s, cy - 12 * s, cx + 9 * s, cy + 12 * s, v)
    g.circ(cx, cy - 15 * s, 4.5 * s, v)
    if legs:
        for side in (-1, 1):
            for k, dy in enumerate((-6, 1, 8)):
                g.line([(cx + side * 7 * s, cy + dy * s), (cx + side * 15 * s, cy + (dy - 4 + 4 * k) * s)], 2.4 * s, v)
    g.line([(cx, cy - 8 * s), (cx, cy + 11 * s)], 1.6 * s, 0 if v else 255)  # wing seam


def pips(g: G, n, y=91):
    """Rank marks along the bottom: n small diamonds."""
    xs = [50 + (i - (n - 1) / 2) * 9 for i in range(n)]
    for x in xs:
        g.poly([(x, y - 4), (x + 3.5, y), (x, y + 4), (x - 3.5, y)])


def boar_head(g: G, cx, cy, s, v=255):
    """Front view of a wild boar: wide skull, sideways ears, long flat snout disc, big upcurved tusks."""
    g.poly([(cx - 20 * s, cy - 22 * s), (cx + 20 * s, cy - 22 * s), (cx + 26 * s, cy - 2 * s),
            (cx + 16 * s, cy + 18 * s), (cx - 16 * s, cy + 18 * s), (cx - 26 * s, cy - 2 * s)], v)
    for side in (-1, 1):                                                    # ears, sideways
        g.poly([(cx + side * 16 * s, cy - 20 * s), (cx + side * 36 * s, cy - 30 * s), (cx + side * 26 * s, cy - 8 * s)], v)
    g.circ(cx - 10 * s, cy - 8 * s, 3 * s, 0); g.circ(cx + 10 * s, cy - 8 * s, 3 * s, 0)   # eyes
    g.ell(cx - 15 * s, cy + 6 * s, cx + 15 * s, cy + 28 * s, v)            # snout disc
    g.ell(cx - 11 * s, cy + 9 * s, cx + 11 * s, cy + 25 * s, 0)
    g.ell(cx - 7 * s, cy + 13 * s, cx - 2 * s, cy + 21 * s, v)              # nostrils (ink inside the hole)
    g.ell(cx + 2 * s, cy + 13 * s, cx + 7 * s, cy + 21 * s, v)
    for side in (-1, 1):                                                    # tusks: thick hooks curling up outside
        g.arc_band(cx + side * 24 * s, cy + 14 * s, 13 * s, 7 * s, 180 if side < 0 else -90, 300 if side < 0 else 30, v)
        g.poly([(cx + side * 24 * s + side * 10 * s, cy + 2 * s), (cx + side * 24 * s + side * 13 * s, cy - 8 * s),
                (cx + side * 24 * s + side * 6 * s, cy + 1 * s)], v)


def wolf_head(g: G, cx, cy, s, v=255):
    """Profile facing left: tall ears, sloped forehead, long snout, open jaw with fangs, shaggy mane."""
    g.poly([(cx + 22 * s, cy + 26 * s), (cx + 26 * s, cy + 4 * s), (cx + 20 * s, cy - 14 * s),
            (cx + 16 * s, cy - 34 * s), (cx + 6 * s, cy - 20 * s), (cx + 0 * s, cy - 34 * s),
            (cx - 6 * s, cy - 16 * s), (cx - 18 * s, cy - 10 * s), (cx - 36 * s, cy - 2 * s),
            (cx - 38 * s, cy + 3 * s), (cx - 20 * s, cy + 4 * s), (cx - 34 * s, cy + 12 * s),
            (cx - 30 * s, cy + 16 * s), (cx - 12 * s, cy + 14 * s), (cx + 0 * s, cy + 24 * s),
            (cx + 10 * s, cy + 22 * s)], v)
    for k in range(4):                                                      # mane tufts
        g.poly([(cx + 20 * s, cy + (k * 8 - 6) * s), (cx + 32 * s, cy + (k * 8 - 2) * s), (cx + 22 * s, cy + (k * 8 + 2) * s)], v)
    g.poly([(cx - 8 * s, cy - 8 * s), (cx - 1 * s, cy - 10 * s), (cx - 3 * s, cy - 5 * s)], 0)   # eye
    g.poly([(cx - 28 * s, cy + 4 * s), (cx - 26 * s, cy + 9 * s), (cx - 24 * s, cy + 4 * s)], 0)  # fang gap


def fist(g: G, cx, cy, s, v=255):
    """A clenched fist, knuckles up: palm block, four finger rolls, thumb across."""
    g.poly([(cx - 20 * s, cy - 6 * s), (cx + 20 * s, cy - 6 * s), (cx + 18 * s, cy + 26 * s), (cx - 16 * s, cy + 26 * s)], v)
    for k in range(4):
        x = cx - 15 * s + k * 10 * s
        g.ell(x - 6 * s, cy - 20 * s, x + 6 * s, cy + 2 * s, v)
        if k:
            g.line([(x - 5 * s, cy - 14 * s), (x - 5 * s, cy - 2 * s)], 1.6 * s, 0)
    g.ell(cx - 24 * s, cy - 2 * s, cx + 6 * s, cy + 12 * s, v)              # thumb
    g.line([(cx - 20 * s, cy + 1 * s), (cx + 4 * s, cy + 1 * s)], 1.6 * s, 0)
    g.poly([(cx - 12 * s, cy + 26 * s), (cx + 12 * s, cy + 26 * s), (cx + 10 * s, cy + 36 * s), (cx - 10 * s, cy + 36 * s)], v)  # wrist


def human(g: G, cx, top, s, v=255, arms="down"):
    """A robed cultivator: topknot, head, wide sleeves, long robe."""
    g.circ(cx, top + 3 * s, 3 * s, v)                                        # topknot
    g.circ(cx, top + 10 * s, 6.5 * s, v)                                     # head
    g.poly([(cx - 9 * s, top + 18 * s), (cx + 9 * s, top + 18 * s), (cx + 16 * s, top + 62 * s),
            (cx - 16 * s, top + 62 * s)], v)                                 # robe
    if arms == "raised":
        g.line([(cx + 8 * s, top + 22 * s), (cx + 22 * s, top + 8 * s)], 6 * s, v)
        g.line([(cx - 8 * s, top + 22 * s), (cx - 18 * s, top + 36 * s)], 6 * s, v)
    elif arms == "forward":
        g.line([(cx + 8 * s, top + 22 * s), (cx + 26 * s, top + 26 * s)], 6 * s, v)
        g.line([(cx - 8 * s, top + 22 * s), (cx - 16 * s, top + 38 * s)], 6 * s, v)
    g.line([(cx - 10 * s, top + 40 * s), (cx + 10 * s, top + 40 * s)], 2 * s, 0)  # sash


# ---------------------------------------------------------------- icons
def rank_one_gu_master():
    g = G(); human(g, 42, 8, 1.25, arms="raised"); gu_beetle(g, 76, 14, 0.5, legs=False); pips(g, 1); return g


def moon_gu_master(rank):
    g = G(); human(g, 32, 8, 1.2, arms="forward")
    g.crescent(72, 40, 18 + 2.5 * rank, 9, angle=180)                         # moon blade, hollow toward the master
    pips(g, rank); return g


def strength_gu_master(rank):
    g = G(); fist(g, 50, 44, 1.15)
    for side in (-1, 1):                                                    # boar tusks flanking the fist
        g.arc_band(50 + side * 34, 44, 16, 10, 190 if side < 0 else -80, 280 if side < 0 else 10)
    pips(g, rank); return g


def lightning_wolf(crown=False, bold=False):
    g = G(); wolf_head(g, 56, 54 if not crown else 60, 1.0 if not bold else 1.08)
    g.bolt([84, 70, 86, 72], 52, 94, 6)
    if crown:
        for i, x in enumerate((36, 50, 64)):
            g.bolt([x, x + 5, x - 3, x + 2], 4, 22, 3.2)
    return g


def moonlight_gu():
    g = G(); g.crescent(46, 50, 36, 16, angle=0); gu_beetle(g, 66, 50, 0.62); return g


def white_boar_gu():
    g = G(); boar_head(g, 50, 48, 1.12); return g


def jade_skin_gu():
    g = G()
    for cx, cy in ((50, 30), (32, 52), (68, 52), (50, 74)):
        pts = [(cx + 17 * math.cos(math.radians(30 + 60 * k)), cy - 17 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
        g.poly(pts)
        inner = [(cx + 10 * math.cos(math.radians(30 + 60 * k)), cy - 10 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
        g.poly(inner, 0)
    return g


def liquor_worm():
    g = G()
    g.poly([(26, 46), (74, 46), (66, 70), (34, 70)])                         # cup
    g.line([(50, 70), (50, 82)], 6); g.poly([(36, 82), (64, 82), (60, 88), (40, 88)])
    g.ell(30, 49, 70, 56, 0)                                                 # wine surface
    for i in range(5):                                                       # worm: chain of beads
        g.circ(36 + i * 7, 38 - 10 * math.sin(i * 0.9), 5.2 - i * 0.4)
    return g


def killer_move():
    g = G()
    for k in range(12):                                                      # burst
        a = math.radians(k * 30 + 15)
        g.poly([(50 + 20 * math.cos(a - 0.12), 50 - 20 * math.sin(a - 0.12)), (50 + 46 * math.cos(a), 50 - 46 * math.sin(a)),
                (50 + 20 * math.cos(a + 0.12), 50 - 20 * math.sin(a + 0.12))])
    g.circ(50, 50, 22, 0)
    g.crescent(46, 50, 17, 8, angle=0)
    g.arc_band(56, 58, 14, 9, 120, 250)
    return g


# black glyphs
def spirit_spring():
    g = G()
    g.ell(10, 70, 90, 94)                                                    # pool
    g.ell(20, 75, 80, 88, 0)
    g.ell(30, 77, 70, 86)                                                    # inner ripple
    g.ell(38, 79, 62, 84, 0)
    g.line([(50, 76), (50, 30)], 7)                                          # central jet
    for side in (-1, 1):                                                     # falling arcs
        g.arc_band(50 + side * 18, 46, 20, 15, 0 if side > 0 else 90, 90 if side > 0 else 180)
        g.line([(50 + side * 38, 46), (50 + side * 38, 62)], 3.5)
    for x, y in ((50, 12), (28, 24), (72, 24)):                              # primeval stones, faceted
        g.poly([(x, y - 9), (x + 7, y - 2), (x + 4, y + 7), (x - 4, y + 7), (x - 7, y - 2)])
        g.line([(x - 4, y - 1), (x + 4, y - 1)], 1.4, 0)
    return g


def moon_orchid():
    g = G()
    for k in range(5):
        a = math.radians(90 + k * 72)
        cx, cy = 50 + 18 * math.cos(a), 52 - 18 * math.sin(a)
        g.ell(cx - 12, cy - 12, cx + 12, cy + 12)
    g.circ(50, 52, 7, 0); g.circ(50, 52, 3.5)
    g.crescent(78, 18, 13, 6, angle=200)
    g.line([(50, 72), (46, 94)], 4)
    return g


def jade():
    g = G()
    g.circ(50, 44, 30); g.circ(50, 44, 11, 0)                                # bi disc
    g.line([(50, 74), (50, 84)], 4); g.poly([(44, 84), (56, 84), (60, 96), (40, 96)])  # tassel
    for k in range(8):
        a = math.radians(k * 45)
        g.circ(50 + 21 * math.cos(a), 44 - 21 * math.sin(a), 2.3, 0)
    return g


def wine():
    g = G()
    g.ell(26, 34, 74, 92)                                                    # jar body
    g.poly([(38, 22), (62, 22), (58, 38), (42, 38)])                         # neck
    g.ell(32, 12, 68, 26)                                                    # cloth cap
    g.line([(36, 22), (64, 22)], 3, 0)
    g.poly([(40, 52), (60, 52), (60, 74), (40, 74)], 0)                      # label
    g.line([(45, 58), (55, 58)], 2.5); g.line([(45, 66), (55, 66)], 2.5)
    return g


def clan_head_pavilion():
    g = G()
    g.poly([(8, 44), (50, 22), (92, 44), (84, 46), (50, 32), (16, 46)])      # upper roof with upturned eaves
    g.poly([(26, 46), (74, 46), (74, 50), (26, 50)])
    g.poly([(14, 66), (50, 50), (86, 66), (78, 68), (50, 58), (22, 68)])     # lower roof
    for x in (30, 44, 56, 70):
        g.line([(x, 68), (x, 88)], 5)
    g.poly([(18, 88), (82, 88), (86, 94), (14, 94)])
    g.circ(50, 16, 4)
    return g


def refinement_chamber():
    g = G()
    g.ell(20, 40, 80, 80)                                                    # ding cauldron
    g.poly([(18, 40), (82, 40), (78, 50), (22, 50)])
    for x in (30, 50, 70):
        g.line([(x, 76), (x - (50 - x) * 0.15, 92)], 6)
    for x in (30, 70):
        g.arc_band(x, 36, 8, 4, 0, 180)                                      # handles
    for x, ph in ((38, 0), (50, 1), (62, 2)):                                # steam
        g.line([(x, 30), (x + 4, 22), (x - 2, 14), (x + 3, 6 + ph)], 3)
    return g


def awakening_grounds():
    g = G()
    g.arc_band(50, 70, 44, 34, 0, 180)                                       # cave mouth
    g.poly([(6, 70), (94, 70), (94, 76), (6, 76)])
    for i, x in enumerate((24, 38, 50, 62, 76)):                             # flower sea
        cy = 58 - (6 if i == 2 else 0)
        for k in range(4):
            a = math.radians(45 + 90 * k)
            g.ell(x + 4 * math.cos(a) - 4, cy - 4 * math.sin(a) - 4, x + 4 * math.cos(a) + 4, cy - 4 * math.sin(a) + 4)
        g.line([(x, cy + 4), (x, 70)], 2)
    g.crescent(50, 30, 9, 4, angle=200)
    g.ell(14, 80, 86, 94)                                                    # the spring
    g.ell(24, 84, 76, 90, 0)
    return g


def gu_yue_nation():
    g = G()
    g.crescent(50, 46, 34, 14, angle=30)
    g.poly([(14, 86), (36, 56), (50, 70), (64, 50), (86, 86)])               # Qing Mao peaks
    g.poly([(30, 86), (36, 74), (42, 86)], 0)
    return g


ICONS = [  # (folder, object name, drawing, ink)
    ("UnitIcons", "Rank One Gu Master", rank_one_gu_master, "white"),
    ("UnitIcons", "Rank Two Moon Gu Master", lambda: moon_gu_master(2), "white"),
    ("UnitIcons", "Rank Four Moon Gu Master", lambda: moon_gu_master(4), "white"),
    ("UnitIcons", "Rank Two Strength Gu Master", lambda: strength_gu_master(2), "white"),
    ("UnitIcons", "Lightning Wolf", lightning_wolf, "white"),
    ("UnitIcons", "Thunder Crown Wolf", lambda: lightning_wolf(crown=True, bold=True), "white"),
    ("UnitPromotionIcons", "Moonlight Gu", moonlight_gu, "white"),
    ("UnitPromotionIcons", "White Boar Gu", white_boar_gu, "white"),
    ("UnitPromotionIcons", "Jade Skin Gu", jade_skin_gu, "white"),
    ("UnitPromotionIcons", "Liquor Worm", liquor_worm, "white"),
    ("UnitPromotionIcons", "Killer Move", killer_move, "white"),
    ("NationIcons", "Gu Yue Clan", gu_yue_nation, "white"),
    ("ResourceIcons", "Spirit Spring", spirit_spring, "black"),
    ("ResourceIcons", "Moon Orchid", moon_orchid, "black"),
    ("ResourceIcons", "Jade", jade, "black"),
    ("ResourceIcons", "Wine", wine, "black"),
    ("BuildingIcons", "Clan Head Pavilion", clan_head_pavilion, "black"),
    ("BuildingIcons", "Refinement Chamber", refinement_chamber, "black"),
    ("BuildingIcons", "Awakening Grounds", awakening_grounds, "black"),
]
