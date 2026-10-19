"""Path icons (MOD_SPEC_3 C3, the user's D2/D6: every object that shows an image gets a designed one).

One white silhouette per path (`SYMBOLS`, drawn on the 0..100 canvas around the centre), composed into:

* the Master: the symbol alone;
* the Grandmaster: the symbol inside a ring;
* the mortal killer move (a one-turn status): the symbol with a burst of rays;
* the path Gu: the symbol with a small Gu beetle at its foot;
* the five signature statuses: their own small designs.

The names come from tools/gen_paths.py, so a new path or Gu without a symbol fails loudly here.
"""
from __future__ import annotations

import math

from PIL import Image, ImageChops

from .glyphs import G, N, S, fist, gu_beetle, human
from .glyphs2 import bowl, coin, flame, octagon_array, regular


def _star(g: G, cx, cy, r, v=255, n=5, inner=0.45):
    pts = []
    for k in range(2 * n):
        rr = r if k % 2 == 0 else r * inner
        a = math.radians(90 + 180 * k / n)
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    g.poly(pts, v)


def _heart(g: G, cx, cy, r, v=255):
    g.circ(cx - r * 0.5, cy - r * 0.2, r * 0.55, v)
    g.circ(cx + r * 0.5, cy - r * 0.2, r * 0.55, v)
    g.poly([(cx - r * 1.02, cy - r * 0.05), (cx + r * 1.02, cy - r * 0.05), (cx, cy + r * 0.95)], v)


def _ghost(g: G, cx, cy, r, v=255):
    g.circ(cx, cy - r * 0.25, r * 0.7, v)
    g.poly([(cx - r * 0.7, cy - r * 0.25), (cx + r * 0.7, cy - r * 0.25), (cx + r * 0.7, cy + r * 0.8),
            (cx + r * 0.35, cy + r * 0.55), (cx, cy + r * 0.85), (cx - r * 0.35, cy + r * 0.55), (cx - r * 0.7, cy + r * 0.8)], v)


def _skull(g: G, cx, cy, r, v=255):
    g.circ(cx, cy - r * 0.15, r * 0.75, v)
    g.poly([(cx - r * 0.45, cy + r * 0.3), (cx + r * 0.45, cy + r * 0.3), (cx + r * 0.38, cy + r * 0.85),
            (cx - r * 0.38, cy + r * 0.85)], v)
    cut = 0 if v else 255
    g.circ(cx - r * 0.3, cy - r * 0.1, r * 0.2, cut); g.circ(cx + r * 0.3, cy - r * 0.1, r * 0.2, cut)
    g.poly([(cx, cy + r * 0.12), (cx - r * 0.1, cy + r * 0.32), (cx + r * 0.1, cy + r * 0.32)], cut)
    for x in (-0.18, 0, 0.18):
        g.line([(cx + r * x, cy + r * 0.55), (cx + r * x, cy + r * 0.85)], r * 0.06, cut)


def _cloud(g: G, cx, cy, r, v=255):
    for dx, dy, rr in ((-0.5, 0.1, 0.38), (0, -0.15, 0.5), (0.5, 0.1, 0.38)):
        g.circ(cx + r * dx, cy + r * dy, r * rr, v)
    g.poly([(cx - r * 0.85, cy + r * 0.1), (cx + r * 0.85, cy + r * 0.1), (cx + r * 0.85, cy + r * 0.48),
            (cx - r * 0.85, cy + r * 0.48)], v)


# ---------------------------------------------------------------- one symbol per path (0..100, centre 50,50)
def s_strength(g): fist(g, 50, 44, 1.15)


def s_transformation(g):
    # a beast's paw print: the transformation path grows a beast's body
    from .glyphs2 import paw
    paw(g, 50, 54, 1.45)


def s_bone(g):
    g.line([(26, 74), (74, 26)], 11)
    for x, y in ((26, 74), (74, 26)):
        for dx, dy in ((-7, -3), (3, 7)):
            g.circ(x + dx * (1 if x < 50 else -1), y + dy * (1 if x < 50 else -1), 8)


def s_blood(g):
    g.circ(50, 62, 24)
    g.poly([(28, 54), (72, 54), (50, 10)])


def s_sword(g):
    g.poly([(46, 70), (54, 70), (54, 22), (50, 10), (46, 22)])                          # blade
    g.poly([(32, 70), (68, 70), (68, 76), (32, 76)])                                    # guard
    g.line([(50, 76), (50, 90)], 6); g.circ(50, 92, 4)


def s_blade(g):
    # a broad saber (dao): curved back, straight edge, ring pommel
    pts = [(24 + 60 * t, 74 - 62 * t - 14 * math.sin(math.pi * t)) for t in [i / 16 for i in range(17)]]
    edge = [(84, 12), (70, 22), (24, 82)]
    g.poly(pts + edge)
    g.line([(24, 78), (12, 92)], 6)
    g.poly([(16, 70), (32, 84), (28, 88), (12, 74)])
    g.circ(10, 94, 4)


def s_metal(g):
    g.poly([(20, 70), (80, 70), (70, 36), (30, 36)])                                    # ingot
    g.poly([(14, 70), (86, 70), (86, 78), (14, 78)])
    g.poly([(34, 42), (46, 42), (42, 64), (30, 64)], 0)                                 # shine


def s_weapon(g):
    g.line([(20, 82), (80, 22)], 5); g.poly([(80, 12), (90, 22), (74, 30)])             # spear
    g.line([(20, 22), (80, 82)], 5); g.poly([(12, 14), (28, 18), (18, 28)])             # arrow
    for k in range(2):
        g.line([(76 - k * 6, 86 - k * 6), (86 - k * 6, 78 - k * 6)], 3)                 # fletching


def s_killing(g): _skull(g, 50, 46, 40)


def s_fire(g):
    # a teardrop flame with two flicks and a hollow heart
    g.circ(50, 66, 26)
    g.poly([(24, 64), (76, 64), (60, 34), (50, 6), (40, 34)])
    g.poly([(26, 60), (30, 34), (40, 50)]); g.poly([(74, 60), (70, 30), (60, 50)])
    g.circ(50, 72, 12, 0)
    g.poly([(38, 72), (62, 72), (50, 48)], 0)


def s_water(g):
    for k, y in enumerate((36, 56, 76)):
        pts = [(12 + i * 3.2, y + 6 * math.sin(i * math.pi / 6 + k)) for i in range(25)]
        g.line(pts, 6)


def s_wood(g):
    g.poly([(50, 8), (78, 36), (74, 66), (50, 86), (26, 66), (22, 36)])                 # leaf
    g.line([(50, 18), (50, 92)], 3.2, 0)
    for k in range(3):
        g.line([(50, 36 + k * 14), (36, 28 + k * 14)], 2.4, 0); g.line([(50, 36 + k * 14), (64, 28 + k * 14)], 2.4, 0)
    g.line([(50, 84), (50, 96)], 4)


def s_earth(g):
    g.poly([(6, 84), (40, 24), (62, 62), (72, 46), (94, 84)])
    g.poly([(34, 36), (40, 24), (46, 36), (40, 32)], 0)                                 # snow-free notch


def s_wind(g):
    for k, (r, a1) in enumerate(((36, 300), (24, 280), (12, 260))):
        g.arc_band(50, 50, r + 4, r - 2, 20 + k * 30, a1)
    g.line([(10, 86), (44, 86)], 5); g.line([(20, 76), (48, 76)], 4)


def s_cloud(g): _cloud(g, 50, 46, 42)


def s_ice(g):
    for a in (90, 30, 150):
        x, y = 38 * math.cos(math.radians(a)), 38 * math.sin(math.radians(a))
        g.line([(50 - x, 50 + y), (50 + x, 50 - y)], 6)
        for sgn in (1, -1):
            bx, by = 50 + sgn * x * 0.62, 50 - sgn * y * 0.62
            for d in (40, -40):
                aa = math.radians(a + (0 if sgn > 0 else 180) + 180 + d)
                g.line([(bx, by), (bx + 12 * math.cos(aa), by - 12 * math.sin(aa))], 4)


def s_lightning(g): g.bolt([58, 36, 62, 40], 6, 82, 9)


def s_poison(g):
    g.circ(50, 64, 28)                                                                  # flask
    g.poly([(42, 14), (58, 14), (58, 42), (42, 42)])
    g.poly([(38, 10), (62, 10), (62, 16), (38, 16)])
    for x, y, r in ((40, 66, 6), (58, 58, 4), (54, 74, 5)):
        g.circ(x, y, r, 0)                                                              # bubbles


def s_light(g):
    g.circ(50, 50, 20)
    for k in range(8):
        a = math.radians(k * 45)
        g.line([(50 + 28 * math.cos(a), 50 - 28 * math.sin(a)), (50 + 44 * math.cos(a), 50 - 44 * math.sin(a))], 6)


def s_dark(g):
    g.circ(50, 50, 44)
    g.ell(16, 34, 84, 66, 0)                                                            # an eye opening in the dark
    g.circ(50, 50, 13)
    g.circ(50, 50, 5, 0)


def s_shadow(g):
    human(g, 60, 14, 1.15)                                                              # the shadow behind
    human(g, 40, 22, 1.15, v=0)
    human(g, 40, 26, 1.0)


def s_star(g): _star(g, 50, 52, 44)


def s_moon(g): g.crescent(50, 50, 40, 22, angle=45)


def s_sound(g):
    g.poly([(10, 40), (26, 40), (44, 22), (44, 78), (26, 60), (10, 60)])                # speaker horn
    for r in (16, 28, 40):
        g.arc_band(44, 50, r + 4, r, -50, 50)


def s_illusion(g):
    g.ell(18, 14, 82, 90)                                                               # mask
    g.ell(28, 38, 44, 50, 0); g.ell(56, 38, 72, 50, 0)                                  # eyes
    g.arc_band(50, 62, 16, 11, 200, 340, 0)                                             # smile
    g.line([(50, 14), (50, 90)], 2.5, 0)                                                # two faces


def s_wisdom(g):
    g.ell(8, 30, 92, 70)
    g.ell(16, 36, 84, 64, 0)
    g.circ(50, 50, 15); g.circ(50, 50, 6, 0)
    for k in range(5):
        a = math.radians(30 + k * 30)
        g.line([(50 + 34 * math.cos(a), 34 - 18 * math.sin(a) * 0 - 4), (50 + 44 * math.cos(a), 30 - 14 * math.sin(a))], 3)


def s_emotion(g): _heart(g, 50, 50, 40)


def s_enchantment(g):
    _heart(g, 44, 54, 30)
    _heart(g, 72, 26, 14)
    g.line([(14, 86), (86, 14)], 4, 0)
    g.line([(14, 86), (80, 20)], 3)
    g.poly([(86, 14), (72, 18), (82, 28)])


def s_soul(g):
    g.circ(50, 58, 28)
    g.poly([(24, 50), (76, 50), (62, 26), (54, 34), (50, 8), (44, 30), (36, 22)])       # flame crown
    g.circ(40, 58, 5, 0); g.circ(60, 58, 5, 0)


def s_dream(g):
    g.crescent(42, 54, 34, 18, angle=30)
    _star(g, 76, 24, 10); _star(g, 84, 50, 6); _star(g, 64, 10, 5)


def s_enslavement(g):
    # two interlocked chain links
    for cx in (36, 64):
        g.d.ellipse([(cx - 26) * S, 34 * S, (cx + 26) * S, 66 * S], outline=255, width=int(8 * S))
    g.poly([(56, 30), (66, 30), (66, 40), (56, 40)], 0)                                 # the right link passes under
    g.d.arc([38 * S, 34 * S, 90 * S, 66 * S], 200, 250, fill=255, width=int(8 * S))


def s_time(g):
    g.poly([(22, 10), (78, 10), (54, 50), (78, 90), (22, 90), (46, 50)])
    g.poly([(30, 16), (70, 16), (52, 44), (48, 44)], 0)
    g.poly([(48, 60), (52, 60), (70, 84), (30, 84)], 0)
    g.poly([(40, 84), (60, 84), (50, 70)])                                              # the fallen sand


def s_space(g):
    g.circ(50, 50, 20)
    g.d.ellipse([6 * S, 38 * S, 94 * S, 62 * S], outline=255, width=int(5 * S))
    g.circ(86, 44, 6)


def s_rule(g):
    g.line([(50, 14), (50, 86)], 5)
    g.poly([(34, 86), (66, 86), (60, 80), (40, 80)])
    g.line([(12, 26), (88, 26)], 5)
    for x in (18, 82):
        g.line([(x, 26), (x - 10, 54)], 2.2); g.line([(x, 26), (x + 10, 54)], 2.2)
        g.arc_band(x, 54, 14, 0, 180, 360)


def s_phantom(g):
    _ghost(g, 50, 50, 42)
    _ghost(g, 50, 50, 32, 0)
    g.circ(40, 40, 5); g.circ(60, 40, 5)


def s_restriction(g):
    g.arc_band(50, 44, 24, 15, 0, 180)                                                  # shackle
    g.poly([(26, 44), (34, 44), (34, 50), (26, 50)]); g.poly([(66, 44), (74, 44), (74, 50), (66, 50)])
    g.poly([(18, 48), (82, 48), (82, 90), (18, 90)])                                    # body
    g.circ(50, 64, 7, 0); g.poly([(47, 66), (53, 66), (55, 80), (45, 80)], 0)           # keyhole


def s_luck(g): coin(g, 50, 50, 44)


def s_heaven(g):
    # the heaven trigram (qian, three unbroken lines) under the round sky
    g.arc_band(50, 54, 44, 38, 0, 180)
    for y in (46, 62, 78):
        g.poly([(16, y), (84, y), (84, y + 9), (16, y + 9)])


def s_qi(g):
    for k, x in enumerate((30, 50, 70)):
        pts = [(x + 8 * math.sin(i * math.pi / 5 + k), 90 - i * 4) for i in range(19)]
        g.line(pts, 5)
    g.circ(50, 14, 7)


def s_refinement(g):
    # two Gu fuse into one: two small shells flow into a larger one
    gu_beetle(g, 26, 30, 0.85, legs=False); gu_beetle(g, 74, 30, 0.85, legs=False)
    g.line([(30, 50), (46, 64)], 4); g.line([(70, 50), (54, 64)], 4)
    gu_beetle(g, 50, 78, 1.0, legs=False)


def s_formation(g): octagon_array(g, 50, 50, 42)


def s_food(g):
    bowl(g, 50, 60, 36)
    g.line([(62, 10), (44, 50)], 3.5); g.line([(76, 12), (54, 50)], 3.5)               # chopsticks


def s_pill(g):
    # a calabash gourd, the pill-maker's bottle
    g.circ(50, 66, 26); g.circ(50, 34, 16)
    g.poly([(44, 22), (56, 22), (54, 10), (46, 10)])
    g.line([(56, 12), (68, 6)], 3)


def s_information(g):
    g.poly([(10, 26), (90, 26), (90, 78), (10, 78)])                                    # a letter
    g.line([(10, 26), (50, 56), (90, 26)], 4, 0)
    g.line([(10, 78), (40, 50)], 3, 0); g.line([(90, 78), (60, 50)], 3, 0)


def s_human(g): human(g, 50, 6, 1.4, arms="raised")


def s_painting(g):
    g.line([(80, 12), (40, 64)], 6)                                                     # brush handle
    g.poly([(40, 64), (30, 66), (20, 86), (36, 82), (46, 72)])                          # brush tip
    g.line([(54, 88), (90, 82)], 4)                                                     # the stroke


def s_theft(g):
    # a grasping hand
    g.ell(26, 44, 74, 92)
    for k, x in enumerate((30, 42, 54, 66)):
        g.ell(x - 5.5, 16 + abs(k - 1.5) * 4, x + 5.5, 62)
    g.ell(64, 52, 92, 66)                                                               # thumb


SYMBOLS = {k[2:]: f for k, f in globals().items() if k.startswith("s_")}


# ---------------------------------------------------------------- compositions
def symbol(key: str) -> G:
    g = G(); SYMBOLS[key](g); return g


def place(target: G, src: G, cx: float, cy: float, scale: float, v=255):
    """Paste src (a full-canvas glyph) scaled around its centre to (cx, cy)."""
    size = max(1, int(N * scale))
    small = src.m.resize((size, size), Image.LANCZOS)
    layer = Image.new("L", (N, N), 0)
    layer.paste(small, (int((cx - 50 * scale) * S), int((cy - 50 * scale) * S)))
    target.m = ImageChops.lighter(target.m, layer) if v else ImageChops.subtract(target.m, layer)
    target.d = target.d.__class__(target.m)


def master(key: str) -> G:
    g = G(); place(g, symbol(key), 50, 50, 0.92); return g


def grandmaster(key: str) -> G:
    g = G(); g.arc_band(50, 50, 49, 43, 0, 360)
    for a in (90, 210, 330):
        g.poly(regular(50 + 46 * math.cos(math.radians(a)), 50 - 46 * math.sin(math.radians(a)), 6, 4))
    place(g, symbol(key), 50, 50, 0.66)
    return g


def move(key: str) -> G:
    g = G()
    for k in range(12):
        a = math.radians(k * 30 + 15)
        g.line([(50 + 36 * math.cos(a), 50 - 36 * math.sin(a)), (50 + 48 * math.cos(a), 50 - 48 * math.sin(a))],
               3.5 if k % 2 else 5)
    place(g, symbol(key), 50, 50, 0.6)
    return g


def path_gu(key: str) -> G:
    g = G()
    place(g, symbol(key), 42, 42, 0.74)
    shield = G(); gu_beetle(shield, 76, 74, 1.45)
    place(g, shield, 50, 50, 1.0, 0)                                                    # a margin around the Gu
    gu_beetle(g, 76, 74, 1.1)
    return g


def status(name: str) -> G:
    g = G()
    if name == "Poisoned":
        place(g, symbol("poison"), 46, 50, 0.8)
        g.poly([(80, 60), (86, 74), (80, 80), (74, 74)])                                # a drip
    elif name == "Charmed":
        _heart(g, 50, 50, 38); _heart(g, 50, 50, 22, 0); _heart(g, 50, 52, 12)
    elif name == "Sealed":
        place(g, symbol("restriction"), 50, 50, 0.9)
    elif name == "Phantom Veil":
        place(g, symbol("phantom"), 50, 50, 0.9)
        for y in (30, 56, 82):
            g.line([(4, y), (20, y)], 3)
    elif name == "Shaken":
        g.circ(50, 58, 26)
        for k, (x, y) in enumerate(((22, 22), (50, 12), (78, 22))):
            _star(g, x, y, 9)
        g.line([(44, 36), (54, 54), (46, 64), (56, 82)], 3.5, 0)                        # a crack
    else:
        raise KeyError(name)
    return g


def icons() -> list[tuple[str, str, object, str]]:
    """(folder, object name, drawing, ink) for gen_art.py, from the names tools/gen_paths.py writes."""
    import gen_paths
    out = []
    for p in gen_paths.PATHS:
        k = p["key"]
        if k not in SYMBOLS:
            raise SystemExit(f"[pathart] no symbol for the {p['name']} path")
        out += [("UnitPromotionIcons", gen_paths.tier_name(p, 0), (lambda k=k: master(k)), "white"),
                ("UnitPromotionIcons", gen_paths.tier_name(p, 1), (lambda k=k: grandmaster(k)), "white"),
                ("UnitPromotionIcons", p["mortal"], (lambda k=k: move(k)), "white")]
    for gu in gen_paths.PATH_GU:
        if gen_paths.new_gu(gu):
            out.append(("UnitPromotionIcons", gu["name"], (lambda k=gu["path"]: path_gu(k)), "white"))
    for s in gen_paths.STATUSES:
        out.append(("UnitPromotionIcons", s["name"], (lambda n=s["name"]: status(n)), "white"))
    return out
