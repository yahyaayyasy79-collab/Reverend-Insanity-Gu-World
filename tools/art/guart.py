"""Gu catalog icons (Phase D, the user 2026-11-02: "desain gu yang kreatif dari gambar, efek, suara").

Every catalog Gu (data/gu_catalog.csv, tools/gu_catalog.py) gets one white silhouette built from three parts:

* its **form**, the creature or thing the Gu is (`FORMS`: beetle, moth, centipede, sword, gong, web...), drawn large;
* its **path**, the path's symbol on a small badge in the top-right corner (tools/art/pathart.py);
* its **rank**: one diamond per rank along the bottom for mortal Gu (1-5), a halo ring with one star per rank above
  five for immortal Gu (6-9).

Every shape is built from primitives here; nothing is copied.
"""
from __future__ import annotations

import math

from .glyphs import G, fist, gu_beetle, human, pips
from .glyphs2 import flame, scroll
from .pathart import _cloud, _star, place, symbol


def _ring_of(g: G, cx, cy, r, n, rr, v=255):
    for k in range(n):
        a = 2 * math.pi * k / n
        g.circ(cx + r * math.cos(a), cy + r * math.sin(a), rr, v)


# ---------------------------------------------------------------- forms (drawn around (46, 46), within y 8..82)
def f_beetle(g): gu_beetle(g, 46, 48, 2.1)


def f_beetle_horn(g):
    gu_beetle(g, 46, 52, 1.9)
    g.poly([(42, 22), (46, 4), (52, 10), (50, 24)])                                   # the long horn


def f_fist(g): fist(g, 46, 36, 1.25)


def f_shell(g):
    g.ell(10, 22, 82, 80); g.poly([(6, 70), (86, 70), (86, 80), (6, 80)])
    for x in (28, 46, 64):                                                            # plates
        g.line([(x, 30), (x, 70)], 2.6, 0)
    g.arc_band(46, 70, 26, 23, 0, 180, 0)


def f_crystal(g):
    for cx, h, w in ((46, 70, 14), (26, 46, 9), (66, 50, 10)):
        g.poly([(cx, 82 - h), (cx + w, 82 - h + w * 1.4), (cx + w, 82), (cx - w, 82), (cx - w, 82 - h + w * 1.4)])
        g.line([(cx, 82 - h + 4), (cx, 78)], 1.6, 0)


def f_leaf(g):
    pts = [(46 + 30 * math.sin(math.pi * t) * (1 if k == 0 else -1), 82 - 74 * t)
           for k in (0, 1) for t in ([i / 24 for i in range(25)] if k == 0 else [1 - i / 24 for i in range(25)])]
    g.poly(pts)
    g.line([(46, 82), (46, 14)], 2.4, 0)
    for k in range(4):
        y = 70 - 13 * k
        g.line([(46, y), (30, y - 10)], 1.6, 0); g.line([(46, y), (62, y - 10)], 1.6, 0)


def f_flower(g):
    for k in range(6):
        a = math.radians(90 + 60 * k)
        g.ell(46 + 20 * math.cos(a) - 12, 44 - 20 * math.sin(a) - 12, 46 + 20 * math.cos(a) + 12, 44 - 20 * math.sin(a) + 12)
    g.circ(46, 44, 10, 0); g.circ(46, 44, 6)
    g.line([(46, 64), (46, 84)], 3)


def f_lotus(g):
    for k, a in enumerate((90, 55, 125, 25, 155)):
        r = math.radians(a)
        cx, cy = 46 + 22 * math.cos(r), 62 - 22 * math.sin(r)
        g.poly([(46, 64), (cx - 10, cy + 2), (cx, cy - 18), (cx + 10, cy + 2)])
    g.ell(16, 62, 76, 78)


def f_worm(g):
    for k in range(7):
        t = k / 6
        g.circ(18 + 56 * t, 46 + 18 * math.sin(t * 2 * math.pi), 12 - 4 * t)
    g.circ(16, 42, 2.2, 0)


def f_centipede(g):
    for k in range(8):
        y = 14 + 9 * k
        x = 46 + 8 * math.sin(k * 0.9)
        g.ell(x - 9, y - 5, x + 9, y + 5)
        g.line([(x - 8, y), (x - 20, y + 4)], 2.2); g.line([(x + 8, y), (x + 20, y + 4)], 2.2)
    g.line([(42, 10), (34, 2)], 2); g.line([(50, 10), (58, 2)], 2)


def f_firefly(g):
    g.arc_band(46, 50, 34, 30, 0, 360); g.arc_band(46, 50, 24, 22, 0, 360)          # glow rings
    g.ell(38, 34, 54, 70)
    g.ell(20, 30, 42, 46); g.ell(50, 30, 72, 46)                                       # wings
    g.circ(46, 64, 6, 0)                                                               # lantern


def f_moth(g):
    g.ell(8, 18, 44, 52); g.ell(48, 18, 84, 52)                                        # fore wings
    g.ell(16, 46, 44, 74); g.ell(48, 46, 76, 74)                                       # hind wings
    g.circ(26, 34, 5, 0); g.circ(66, 34, 5, 0)                                         # eye spots
    g.ell(42, 18, 50, 76)
    g.line([(44, 18), (36, 6)], 1.8); g.line([(48, 18), (56, 6)], 1.8)


def f_cicada(g):
    g.ell(36, 16, 56, 72)
    for side in (-1, 1):                                                               # long clear wings
        g.poly([(46 + side * 6, 26), (46 + side * 34, 50), (46 + side * 22, 84), (46 + side * 8, 60)])
        g.poly([(46 + side * 10, 36), (46 + side * 28, 52), (46 + side * 20, 74), (46 + side * 10, 58)], 0)
    g.circ(38, 18, 4); g.circ(54, 18, 4)


def f_spider(g):
    g.circ(46, 52, 16); g.circ(46, 30, 9)
    for side in (-1, 1):
        for k in range(4):
            y = 36 + 7 * k
            g.line([(46 + side * 10, y), (46 + side * 26, y - 10 + 2 * k), (46 + side * 38, y + 6 + 4 * k)], 2.4)
    g.circ(42, 28, 2, 0); g.circ(50, 28, 2, 0)


def f_scorpion(g):
    for k in range(3):                                                                 # body segments
        g.ell(34, 46 + 9 * k, 58, 58 + 9 * k)
    g.ell(36, 36, 56, 50)                                                              # head
    for side in (-1, 1):                                                               # pincers on arms
        g.line([(46 + side * 8, 42), (46 + side * 22, 30), (46 + side * 26, 16)], 4)
        g.poly([(46 + side * 20, 18), (46 + side * 34, 6), (46 + side * 34, 18), (46 + side * 28, 24)])
        for k in range(3):                                                             # legs
            g.line([(46 + side * 11, 52 + 8 * k), (46 + side * 26, 56 + 9 * k)], 2)
    pts = [(46, 72), (46, 84), (58, 88), (70, 80), (74, 66), (70, 54)]                 # the tail curling up
    g.line(pts, 5)
    g.poly([(66, 52), (78, 44), (74, 58)])


def f_serpent(g):
    pts = [(10 + 66 * t, 48 + 22 * math.sin(t * 2.4 * math.pi)) for t in [i / 30 for i in range(31)]]
    g.line(pts, 9)
    g.ell(70, 32, 88, 46)
    g.line([(86, 38), (92, 34)], 1.6); g.line([(86, 40), (92, 44)], 1.6)


def f_bird(g):
    g.poly([(8, 30), (40, 44), (46, 36), (52, 44), (84, 30), (60, 56), (46, 76), (32, 56)])
    g.circ(46, 34, 7)
    g.poly([(46, 26), (52, 22), (50, 30)])


def f_bat(g):
    g.poly([(4, 30), (16, 36), (22, 28), (30, 40), (40, 34), (46, 44), (52, 34), (62, 40), (70, 28), (76, 36), (88, 30),
            (78, 62), (66, 54), (56, 66), (46, 58), (36, 66), (26, 54), (14, 62)])
    g.circ(46, 40, 8)


def f_wing(g):
    for side in (-1, 1):
        for k in range(5):
            x0 = 46 + side * 4
            g.line([(x0, 70 - 6 * k), (46 + side * (16 + 7 * k), 18 + 9 * k)], 5 - 0.5 * k)
        g.poly([(46 + side * 4, 74), (46 + side * 40, 20), (46 + side * 38, 40), (46 + side * 6, 82)])


def f_blade(g):
    g.poly([(30, 70), (70, 14), (76, 20), (40, 76)])
    g.line([(24, 66), (40, 82)], 4); g.line([(30, 74), (18, 86)], 5)


def f_sword(g):
    g.poly([(44, 8), (48, 2), (52, 8), (52, 64), (44, 64)])
    g.line([(30, 64), (66, 64)], 5); g.line([(48, 66), (48, 84)], 5); g.circ(48, 86, 4)


def f_rod(g):
    g.line([(18, 82), (74, 10)], 7)
    for t in (0.15, 0.5, 0.85):
        x, y = 18 + 56 * t, 82 - 72 * t
        g.line([(x - 6, y - 5), (x + 6, y + 5)], 3, 0)


def f_fang(g):
    g.poly([(30, 10), (62, 10), (52, 50), (46, 82), (40, 50)])
    g.line([(36, 20), (56, 20)], 2.4, 0)


def f_orb(g):
    g.circ(46, 46, 32); g.circ(46, 46, 24, 0)
    g.arc_band(46, 46, 20, 12, 30, 250)
    g.circ(46, 46, 6)


def f_sun(g):
    g.circ(46, 46, 20)
    for k in range(12):
        a = math.radians(30 * k)
        g.poly([(46 + 24 * math.cos(a - 0.12), 46 - 24 * math.sin(a - 0.12)), (46 + 38 * math.cos(a), 46 - 38 * math.sin(a)),
                (46 + 24 * math.cos(a + 0.12), 46 - 24 * math.sin(a + 0.12))])


def f_flame(g):
    flame(g, 46, 84, 76)
    flame(g, 46, 84, 40, 0)
    flame(g, 46, 84, 24)


def f_cloud(g):
    _cloud(g, 34, 32, 26)
    _cloud(g, 58, 60, 28)
    for k in range(3):                                                                 # wind trails
        g.line([(10 + 8 * k, 72 + 5 * k), (30 + 8 * k, 72 + 5 * k)], 2.4)


def f_wheel(g):
    g.arc_band(46, 46, 36, 28, 0, 360)
    for k in range(6):
        a = math.radians(60 * k + 15)
        g.line([(46, 46), (46 + 30 * math.cos(a), 46 - 30 * math.sin(a))], 3)
    g.circ(46, 46, 8)
    for k in range(3):                                                                 # wind streaks
        g.arc_band(46, 46, 44 - 2 * k, 41 - 2 * k, 100 + 120 * k, 150 + 120 * k)


def f_drill(g):
    g.poly([(26, 14), (66, 14), (46, 84)])
    for k in range(4):
        y = 22 + 14 * k
        w = 18 - 4.5 * k
        g.line([(46 - w, y), (46 + w, y + 6)], 2.4, 0)


def f_eye(g):
    g.poly([(6, 46), (26, 28), (46, 22), (66, 28), (86, 46), (66, 64), (46, 70), (26, 64)])
    g.circ(46, 46, 16, 0); g.circ(46, 46, 10); g.circ(42, 42, 3, 0)


def f_ear(g):
    g.arc_band(48, 42, 30, 20, -60, 200)
    g.arc_band(48, 44, 12, 6, -40, 200)
    g.line([(34, 66), (40, 82)], 6)
    for k in range(3):                                                                 # the grass it grows from
        g.line([(30 + 12 * k, 86), (26 + 14 * k, 72)], 2)


def f_mask(g):
    g.poly([(18, 18), (74, 18), (76, 48), (64, 74), (46, 82), (28, 74), (16, 48)])
    g.ell(26, 32, 42, 44, 0); g.ell(50, 32, 66, 44, 0)
    g.line([(34, 62), (46, 58), (58, 62)], 3, 0)
    g.poly([(18, 18), (28, 4), (36, 18)]); g.poly([(56, 18), (64, 4), (74, 18)])     # horns


def f_gong(g):
    g.line([(14, 82), (14, 12), (78, 12), (78, 82)], 4)
    g.circ(46, 46, 24); g.circ(46, 46, 8, 0)
    g.line([(30, 16), (36, 24)], 2); g.line([(62, 16), (56, 24)], 2)
    g.line([(64, 80), (86, 62)], 3); g.circ(86, 60, 5)                                 # mallet


def f_web(g):
    for k in range(8):
        a = math.radians(45 * k)
        g.line([(46, 46), (46 + 40 * math.cos(a), 46 - 40 * math.sin(a))], 2)
    for r in (12, 24, 36):
        pts = [(46 + r * math.cos(math.radians(45 * k)), 46 - r * math.sin(math.radians(45 * k))) for k in range(9)]
        g.line(pts, 2)
    g.circ(46, 46, 5)


def f_scroll(g): scroll(g, 46, 46, 26, 30)


def f_hammer(g):
    g.poly([(18, 12), (74, 12), (74, 38), (18, 38)])
    g.line([(46, 38), (46, 86)], 7)
    g.line([(24, 25), (68, 25)], 2.2, 0)
    for x in (6, 86):                                                                  # sparks
        g.line([(x, 20), (x + (8 if x < 50 else -8), 30)], 2)


def f_puppet(g):
    human(g, 46, 18, 0.95)
    for x in (34, 46, 58):                                                             # the strings
        g.line([(x, 4), (x, 30)], 1.4)
    g.line([(26, 4), (66, 4)], 3)


def f_bone(g):
    g.line([(22, 70), (70, 22)], 9)
    for cx, cy in ((22, 70), (70, 22)):
        g.circ(cx - 7, cy - 2, 8); g.circ(cx + 2, cy + 7, 8)


FORMS = {k[2:]: f for k, f in globals().items() if k.startswith("f_")}


# ---------------------------------------------------------------- the composed icon
def gu_icon(form: str, path_key: str, rank: int) -> G:
    g = G()
    body = G(); FORMS[form](body)
    place(g, body, 46, 46, 0.86)
    badge = G(); badge.circ(50, 50, 50)
    place(g, badge, 82, 18, 0.36, 0)                                                   # a margin around the badge
    place(g, symbol(path_key), 82, 18, 0.28)
    if rank <= 5:
        cut = G(); cut.poly([(0, 84), (100, 84), (100, 100), (0, 100)])
        g.paste(cut, 0)
        pips(g, rank, y=92)
    else:
        g.arc_band(50, 50, 50, 47, 0, 360)
        for k in range(rank - 5):                                                      # a star per rank above five
            a = math.radians(270 + (k - (rank - 6) / 2) * 22)
            x, y = 50 + 48 * math.cos(a), 50 - 48 * math.sin(a)
            star = G(); star.circ(x, y, 7)
            g.paste(star, 0)
            _star(g, x, y, 6)
    return g


def icons() -> list[tuple[str, str, object, str]]:
    import gu_catalog
    return [("UnitPromotionIcons", r["name"], (lambda r=r: gu_icon(r["form"], r["path"], int(r["rank"]))), "white")
            for r in gu_catalog.ROWS]


# ---------------------------------------------------------------- combination killer moves (tools/gu_combos.py)
KIND_MARK = {"assault": 8, "bind": 6, "ward": 4, "heal": 5, "mobility": 3, "aura": 12, "plunder": 7, "insight": 9}


def combo_icon(path_a: str, path_b: str, kind: str, rank: int) -> G:
    """Two path symbols crossing inside a burst: the burst's ray count tells the kind, a halo marks an immortal move."""
    g = G()
    n = KIND_MARK[kind] * 2
    for k in range(n):
        a = math.radians(90 + 360 * k / n)
        r0, r1 = (38, 48) if k % 2 == 0 else (40, 45)
        g.line([(50 + r0 * math.cos(a), 50 - r0 * math.sin(a)), (50 + r1 * math.cos(a), 50 - r1 * math.sin(a))],
               4 if k % 2 == 0 else 2.5)
    if rank >= 6:
        g.arc_band(50, 50, 50, 47, 0, 360)
    disc = G(); disc.circ(50, 50, 33)
    g.paste(disc, 0)
    for cx, cy, key in ((37, 39, path_a), (63, 61, path_b)):
        cut = G(); cut.circ(50, 50, 50)
        place(g, cut, cx, cy, 0.56, 0)
        place(g, symbol(key), cx, cy, 0.5)
    return g


def combo_icons() -> list[tuple[str, str, object, str]]:
    import gu_combos
    info = gu_combos.gu_info()
    return [("UnitPromotionIcons", r["name"],
             (lambda r=r: combo_icon(info[r["gu_a"]][1], info[r["gu_b"]][1], r["kind"], gu_combos.rank(r))), "white")
            for r in gu_combos.ROWS]
