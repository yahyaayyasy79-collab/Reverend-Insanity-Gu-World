"""The paths' basic foods (the user, 2026-11-09; data/path_foods.csv): one resource icon each.

Flat glyphs in the style of glyphs.py, built from geometric primitives (MOD_SPEC rule 6); the enamel portraits colour
each in its path's family colour (inkpass.Palette). Moon Orchid, Wild Boar and Wine keep their Slice 1 icons.
"""
from __future__ import annotations

import math

from .glyphs import G
from .glyphs2 import flame, paw, scroll


def _petals(g: G, cx, cy, n, r, pr, rot=90, v=255):
    for k in range(n):
        a = math.radians(rot + k * 360 / n)
        g.circ(cx + r * math.cos(a), cy - r * math.sin(a), pr, v)


def wild_deer():
    """A deer's head with branching antlers."""
    g = G()
    g.poly([(40, 44), (60, 44), (58, 70), (50, 88), (42, 70)])                      # the face
    g.poly([(36, 44), (22, 36), (30, 50)]); g.poly([(64, 44), (78, 36), (70, 50)])  # ears
    for s in (-1, 1):                                                               # antlers
        x = 50 + s * 6
        g.line([(x, 44), (x + s * 10, 26), (x + s * 14, 8)], 3.6)
        g.line([(x + s * 10, 26), (x + s * 24, 20)], 3.2)
        g.line([(x + s * 12, 16), (x + s * 4, 6)], 3)
    g.circ(44, 56, 2.6, 0); g.circ(56, 56, 2.6, 0)
    return g


def beast_milk():
    """A milk jug, drops falling from its lip."""
    g = G()
    g.poly([(32, 34), (68, 34), (74, 88), (26, 88)])
    g.poly([(30, 26), (70, 26), (68, 36), (32, 36)])
    g.poly([(30, 26), (20, 20), (24, 32)])                                          # the lip
    g.arc_band(74, 58, 14, 8, -80, 80)                                              # the handle
    for x, y in ((14, 44), (18, 60)):
        g.poly([(x, y - 7), (x + 4, y), (x, y + 4), (x - 4, y)])
    g.line([(34, 50), (66, 50)], 3, 0)
    return g


def python_blood():
    """A coiled python and a drop of its blood."""
    g = G()
    pts = [(50 + 30 * math.cos(t) * (1 - t / 18), 46 - 26 * math.sin(t) * (1 - t / 18)) for t in [i * 0.35 for i in range(40)]]
    g.line(pts, 9)
    g.circ(pts[0][0] + 4, pts[0][1], 7)
    g.circ(pts[0][0] + 6, pts[0][1] - 2, 1.8, 0)
    g.poly([(76, 64), (86, 82), (80, 92), (72, 92), (66, 82)])                      # the drop
    return g


def _ingot(g: G, cx, cy, w, h, v=255):
    g.poly([(cx - w, cy + h), (cx + w, cy + h), (cx + w * 0.7, cy - h), (cx - w * 0.7, cy - h)], v)


def fine_iron():
    """A bar of fine iron with a sword's outline cut in it."""
    g = G()
    _ingot(g, 50, 62, 40, 22)
    g.line([(30, 64), (70, 64)], 4, 0)
    g.poly([(70, 60), (78, 64), (70, 68)], 0)
    g.line([(28, 58), (28, 70)], 4, 0)
    g.line([(50, 8), (50, 34)], 5); g.line([(40, 30), (60, 30)], 4)                 # a sword above
    return g


def old_blades():
    """Two broken blades crossed."""
    g = G()
    for s in (-1, 1):
        cx = 50 + s * 4
        g.poly([(cx - s * 30, 90), (cx - s * 22, 92), (cx + s * 14, 30), (cx + s * 8, 26)])
        g.poly([(cx + s * 14, 30), (cx + s * 22, 22), (cx + s * 12, 24)])           # the broken tip
        g.line([(cx - s * 34, 80), (cx - s * 18, 92)], 6)                            # the guard
    return g


def rooster_iron():
    """A rooster's comb and beak over a bed of iron."""
    g = G()
    g.poly([(10, 92), (20, 70), (40, 64), (62, 70), (82, 62), (92, 92)])            # the iron bed
    g.circ(30, 80, 3, 0); g.circ(56, 78, 3, 0); g.circ(76, 82, 3, 0)
    g.ell(36, 26, 66, 56)                                                           # the head
    for k, x in enumerate((40, 50, 60)):                                            # the comb
        g.circ(x, 24 - 2 * (k == 1), 7)
    g.poly([(64, 38), (80, 42), (64, 46)])                                          # the beak
    g.circ(56, 38, 2.6, 0)
    g.poly([(58, 52), (62, 62), (54, 58)])                                          # the wattle
    return g


def iron_ore():
    """A lump of ore, flecked."""
    g = G()
    g.poly([(16, 70), (26, 40), (50, 26), (76, 34), (88, 60), (76, 86), (36, 90)])
    for x, y, r in ((40, 48, 5), (62, 44, 4), (56, 68, 6), (34, 72, 4), (74, 66, 3.5)):
        g.circ(x, y, r, 0)
    return g


def battlefield_bones():
    """A skull over crossed bones."""
    g = G()
    for s in (-1, 1):
        g.line([(50 - s * 32, 66), (50 + s * 32, 94)], 7)
        for x, y in ((50 - s * 32, 66), (50 + s * 32, 94)):
            g.circ(x - 3, y - 3, 5); g.circ(x + 3, y + 3, 5)
    g.ell(28, 8, 72, 52); g.poly([(36, 44), (64, 44), (60, 64), (40, 64)])
    g.circ(40, 32, 6, 0); g.circ(60, 32, 6, 0)
    g.poly([(50, 40), (54, 48), (46, 48)], 0)
    for x in (44, 50, 56):
        g.line([(x, 56), (x, 64)], 2, 0)
    return g


def fire_charcoal():
    """Lumps of charcoal glowing, a flame rising from them."""
    g = G()
    g.poly([(50, 6), (64, 26), (70, 44), (62, 58), (50, 62), (38, 58), (30, 44), (36, 26)])   # the flame
    g.poly([(50, 28), (58, 42), (54, 54), (46, 54), (42, 42)], 0)
    for x, y, w in ((26, 80, 18), (74, 80, 18), (50, 86, 16)):
        g.poly([(x - w, y + 8), (x - w * 0.7, y - 8), (x + w * 0.6, y - 10), (x + w, y + 4), (x + w * 0.5, y + 12)])
        g.circ(x - 2, y, 2.4, 0)
    return g


def dragonfish():
    """A fish with a dragon's whiskers."""
    g = G()
    g.ell(18, 34, 74, 70)
    g.poly([(70, 52), (94, 30), (88, 52), (94, 74)])                                # the tail
    g.poly([(40, 34), (56, 16), (60, 36)])                                          # the fin
    g.circ(30, 46, 3.4, 0)
    g.line([(20, 56), (8, 66), (6, 80)], 2.6); g.line([(22, 48), (6, 42), (4, 30)], 2.6)
    for x in (44, 54, 64):
        g.arc_band(x, 52, 8, 6, 60, 300, 0)
    return g


def lingzhi():
    """A lingzhi's kidney-shaped cap with growth rings, on its stalk."""
    g = G()
    g.ell(12, 22, 88, 66)
    g.ell(30, 50, 70, 70, 0)
    for r in (26, 18):
        g.arc_band(50, 48, r + 2, r, 20, 160, 0)
    g.poly([(44, 60), (56, 60), (60, 94), (40, 94)])
    return g


def marsh_mud():
    """A mound of mud with bubbles, a crab's claw rising from it."""
    g = G()
    g.poly([(6, 92), (14, 70), (34, 60), (60, 62), (84, 70), (94, 92)])
    for x, y, r in ((30, 72, 4), (52, 70, 5), (70, 78, 3.5)):
        g.circ(x, y, r, 0)
    g.line([(64, 62), (68, 34)], 5)
    g.poly([(68, 34), (58, 14), (66, 22), (70, 30)]); g.poly([(68, 34), (82, 16), (76, 30)])
    return g


def wind_knot_grass():
    """Blades of grass tied in a knot, the wind passing."""
    g = G()
    for x in (34, 46, 58, 70):
        g.line([(x, 94), (x + 2, 60), (50 + (x - 50) * 0.3, 40), (x - 6, 10)], 3.6)
    g.ell(38, 36, 64, 52); g.ell(44, 40, 58, 48, 0)
    for y in (24, 70):
        g.line([(8, y), (24, y - 4), (30, y + 2)], 2.6)
    return g


def sand_gull_earth():
    """A gull flying over a mound of sand with an egg in it."""
    g = G()
    g.poly([(4, 94), (24, 72), (50, 64), (76, 72), (96, 94)])
    g.ell(42, 70, 58, 88, 0); g.ell(45, 73, 55, 85)
    g.poly([(14, 30), (34, 22), (50, 34), (66, 22), (86, 30), (66, 28), (50, 42), (34, 28)])   # the gull
    g.ell(46, 30, 54, 40)
    return g


def dancing_snow():
    """Snowflakes turning on the wind."""
    g = G()
    for cx, cy, r in ((34, 34, 20), (68, 58, 16), (36, 78, 11)):
        for k in range(6):
            a = math.radians(k * 60 + cx)
            g.line([(cx, cy), (cx + r * math.cos(a), cy - r * math.sin(a))], 3.2)
        g.circ(cx, cy, r * 0.2)
    g.arc_band(56, 40, 40, 36, -60, 40)
    return g


def lightning_eel():
    """An eel whose body is a lightning bolt."""
    g = G()
    g.line([(12, 30), (36, 24), (30, 50), (60, 44), (52, 72), (86, 66)], 7)
    g.circ(12, 30, 7); g.circ(10, 28, 1.8, 0)
    g.poly([(86, 66), (96, 56), (94, 76)])
    return g


def rotten_frozen_mud():
    """A frozen mound with an ice crystal, its stink rising."""
    g = G()
    g.poly([(6, 92), (16, 68), (40, 58), (66, 62), (88, 72), (94, 92)])
    g.poly([(50, 64), (58, 76), (50, 88), (42, 76)], 0)                             # the ice crystal
    g.poly([(50, 68), (55, 76), (50, 84), (45, 76)])
    for x in (30, 50, 70):
        g.line([(x, 50), (x - 5, 40), (x + 2, 30), (x - 3, 18)], 2.6)
    return g


def flame_swan_stone():
    """A stone with a swan of flame rising from it."""
    g = G()
    g.poly([(14, 92), (22, 70), (50, 62), (78, 70), (86, 92)])
    g.line([(56, 64), (62, 40), (52, 22), (40, 26)], 6)                             # the swan's neck
    g.poly([(40, 26), (30, 30), (40, 32)])                                          # the beak
    g.poly([(56, 62), (82, 46), (74, 62)])                                          # a wing of flame
    g.poly([(52, 62), (28, 48), (34, 62)])
    return g


def _mushroom(g: G, cx, base, w, h, v=255):
    g.ell(cx - w, base - h, cx + w, base - h * 0.35, v)
    g.poly([(cx - w * 0.3, base - h * 0.5), (cx + w * 0.3, base - h * 0.5), (cx + w * 0.35, base), (cx - w * 0.35, base)], v)


def dark_fragrant_mushroom():
    """Two dark mushrooms, their scent curling up."""
    g = G()
    _mushroom(g, 38, 94, 24, 48); _mushroom(g, 70, 94, 16, 32)
    for x in (30, 70):
        g.line([(x, 34), (x + 6, 24), (x - 2, 16), (x + 4, 6)], 2.6)
    return g


def white_shadow_grass():
    """A tuft of grass over its own dark shadow."""
    g = G()
    g.ell(14, 82, 90, 96)
    g.ell(20, 84, 84, 92, 0)
    for k, a in enumerate((100, 80, 120, 60, 140, 40)):
        r = math.radians(a)
        g.line([(50, 86), (50 + 46 * math.cos(r), 86 - 70 * math.sin(r) * (0.7 + 0.1 * (k % 2)))], 3.6)
    return g


def arrow_bamboo():
    """Stalks of bamboo whose tips are arrowheads."""
    g = G()
    for x, top in ((32, 18), (52, 8), (72, 22)):
        g.line([(x, 94), (x, top + 10)], 6)
        for y in range(top + 26, 94, 18):
            g.line([(x - 5, y), (x + 5, y)], 2.4, 0)
        g.poly([(x - 8, top + 12), (x, top), (x + 8, top + 12)])
    return g


def wave_sound_conch():
    from .csart import shen_clan
    return shen_clan()


def illusion_peach():
    """A peach and the shimmer of the illusion around it."""
    g = G()
    g.circ(42, 58, 20); g.circ(58, 58, 20); g.poly([(30, 66), (70, 66), (50, 88)])
    g.line([(50, 46), (50, 72)], 2.4, 0)
    g.poly([(50, 40), (64, 26), (72, 32)])                                          # the leaf
    for k in range(12):                                                             # the shimmering ring
        a0 = k * 30
        g.arc_band(50, 60, 46, 42, a0, a0 + 16)
    return g


def splendid_overlord_flower():
    """A great flower of six pointed, spotted petals."""
    g = G()
    for k in range(6):
        a = math.radians(90 + k * 60)
        tip = (50 + 46 * math.cos(a), 50 - 46 * math.sin(a))
        n = (-math.sin(a) * 13, -math.cos(a) * 13)
        mid = (50 + 24 * math.cos(a), 50 - 24 * math.sin(a))
        g.poly([(50, 50), (mid[0] + n[0], mid[1] + n[1]), tip, (mid[0] - n[0], mid[1] - n[1])])
        g.circ(50 + 26 * math.cos(a), 50 - 26 * math.sin(a), 3.4, 0)
    g.circ(50, 50, 11, 0); g.circ(50, 50, 6)
    return g


def taize_flower():
    """A water flower of pointed petals, its mist drifting below."""
    g = G()
    for a in (90, 55, 125, 20, 160):
        r = math.radians(a)
        tip = (50 + 36 * math.cos(r), 62 - 40 * math.sin(r))
        n = (-math.sin(r) * 9, -math.cos(r) * 9)
        mid = (50 + 18 * math.cos(r), 62 - 20 * math.sin(r))
        g.poly([(50, 62), (mid[0] + n[0], mid[1] + n[1]), tip, (mid[0] - n[0], mid[1] - n[1])])
    g.ell(30, 60, 70, 74)
    for y in (82, 92):
        g.line([(8, y), (36, y - 4), (62, y + 2), (92, y - 3)], 3)
    return g


def peach_blossom():
    """Five round petals and their stamens."""
    g = G()
    _petals(g, 50, 50, 5, 22, 16)
    g.circ(50, 50, 10, 0)
    for k in range(5):
        a = math.radians(90 + 36 + k * 72)
        g.line([(50, 50), (50 + 10 * math.cos(a), 50 - 10 * math.sin(a))], 2)
    g.circ(50, 50, 3)
    return g


def white_lotus_silkworm():
    """A plump silkworm on a lotus pad."""
    g = G()
    g.ell(8, 66, 92, 94)
    g.poly([(50, 80), (40, 66), (60, 66)], 0)
    for k in range(6):
        x = 22 + k * 11
        g.circ(x, 50 - 4 * math.sin(k * 0.9), 9)
    g.circ(84, 44, 8); g.circ(87, 42, 1.8, 0)
    return g


def nine_bend_dream_flower():
    """A flower at the end of a nine-bend stem, a crescent of dream above."""
    g = G()
    pts = [(50 + (8 if k % 2 else -8), 96 - k * 7) for k in range(10)]
    g.line(pts, 3.2)
    _petals(g, 50, 26, 5, 10, 9)
    g.circ(50, 26, 5, 0)
    g.crescent(80, 14, 10, 5, angle=200)
    return g


def wolf_meat():
    """A cut of meat on the bone, a fang beside it."""
    g = G()
    g.ell(18, 26, 70, 70)
    g.ell(30, 36, 50, 54, 0); g.ell(34, 40, 46, 50)
    g.line([(62, 62), (84, 84)], 8)
    g.circ(84, 90, 6); g.circ(90, 84, 6)
    g.poly([(74, 10), (86, 10), (80, 34)])                                          # the fang
    return g


def time_river_water():
    """An hourglass whose sand is a running river."""
    g = G()
    g.line([(24, 8), (76, 8)], 6); g.line([(24, 92), (76, 92)], 6)
    g.poly([(28, 12), (72, 12), (54, 50), (72, 88), (28, 88), (46, 50)])
    g.poly([(34, 18), (66, 18), (51, 46), (49, 46)], 0)
    for y in (70, 80):
        g.line([(34, y), (44, y - 3), (56, y + 2), (66, y - 1)], 2.4, 0)
    return g


def nether_jellyfish():
    """A jellyfish: a bell and its trailing threads."""
    g = G()
    g.ell(18, 10, 82, 62)
    g.poly([(18, 40), (82, 40), (82, 52), (18, 52)], 0)
    g.poly([(18, 36), (82, 36), (78, 44), (22, 44)])
    for x in (28, 42, 58, 72):
        g.line([(x, 44), (x - 6, 62), (x + 4, 78), (x - 2, 94)], 2.8)
    g.circ(40, 26, 3, 0); g.circ(60, 26, 3, 0)
    return g


def pearl_thread_water():
    """A drop of water with a thread of pearls through it."""
    g = G()
    g.poly([(50, 6), (74, 44), (78, 64), (70, 82), (50, 92), (30, 82), (22, 64), (26, 44)])
    for k in range(5):
        y = 34 + k * 12
        x = 50 + 10 * math.sin(k * 1.2)
        g.circ(x, y, 5, 0)
        g.circ(x, y, 2.4)
    return g


def flying_bear_flesh():
    """A bear's paw with a wing behind it."""
    g = G()
    for k in range(5):
        a = math.radians(160 - k * 22)
        g.poly([(50, 50), (50 + 46 * math.cos(a), 50 - 40 * math.sin(a)), (50 + 40 * math.cos(a - 0.2), 50 - 34 * math.sin(a - 0.2))])
    paw(g, 50, 64, 1.0)
    return g


def north_ban_licorice():
    """A twisted licorice root under the north's star."""
    g = G()
    g.line([(50, 30), (40, 46), (58, 58), (42, 72), (54, 84), (48, 96)], 6)
    g.line([(46, 50), (24, 60)], 3); g.line([(54, 68), (76, 74)], 3); g.line([(44, 78), (28, 90)], 2.6)
    for k in range(4):
        a = math.radians(90 + k * 90)
        g.poly([(50, 14), (50 + 14 * math.cos(a + 0.3), 14 - 14 * math.sin(a + 0.3)),
                (50 + 3 * math.cos(a + 0.8), 14 - 3 * math.sin(a + 0.8))])
    return g


def hound_dung():
    """A dog's paw print beside a coiled pile."""
    g = G()
    for k, (w, y) in enumerate(((30, 84), (22, 66), (14, 50))):
        g.ell(40 - w, y - 10, 40 + w, y + 10)
    g.poly([(40, 34), (46, 44), (34, 44)])
    for x, y in ((78, 52), (70, 40), (78, 32), (88, 40)):
        g.circ(x, y, 4)
    g.ell(70, 52, 90, 70)
    return g


def brocade_cloud():
    """A cloud woven with brocade spirals."""
    g = G()
    for x, y, r in ((30, 56, 18), (50, 44, 22), (72, 56, 18)):
        g.circ(x, y, r)
    g.poly([(12, 56), (90, 56), (90, 74), (12, 74)])
    for x in (30, 50, 70):
        g.arc_band(x, 60, 8, 5, 0, 300, 0)
    return g


def heavy_gold():
    """Stacked gold ingots, heavy and boat-shaped."""
    g = G()
    for cx, cy, w in ((32, 78, 22), (68, 78, 22), (50, 50, 24)):
        g.poly([(cx - w, cy - 10), (cx - w * 0.5, cy + 8), (cx + w * 0.5, cy + 8), (cx + w, cy - 10), (cx + w * 0.4, cy - 4),
                (cx, cy - 14), (cx - w * 0.4, cy - 4)])
        g.ell(cx - w * 0.3, cy - 16, cx + w * 0.3, cy - 4)
    return g


def ash():
    """A pile of ash, embers still in it."""
    g = G()
    g.poly([(6, 92), (24, 62), (50, 44), (76, 62), (94, 92)])
    for x, y, r in ((40, 66, 3.6), (58, 72, 3), (30, 82, 2.6), (68, 84, 3.2), (50, 58, 2.4)):
        g.circ(x, y, r, 0)
    for x in (40, 60):
        g.line([(x, 38), (x + 4, 28), (x - 2, 18)], 2.4)
    return g


def star_cave_stone():
    """A stone with a star-shaped hollow."""
    g = G()
    g.poly([(10, 70), (20, 30), (50, 14), (80, 26), (92, 66), (70, 90), (28, 90)])
    pts = []
    for k in range(10):
        a = math.radians(90 + k * 36)
        r = 22 if k % 2 == 0 else 9
        pts.append((50 + r * math.cos(a), 54 - r * math.sin(a)))
    g.poly(pts, 0)
    return g


def ginseng_whiskers():
    """A ginseng root with its fine whiskers."""
    g = G()
    g.ell(38, 22, 62, 66)
    g.line([(44, 62), (34, 86)], 6); g.line([(56, 62), (66, 86)], 6)
    g.line([(40, 40), (24, 52)], 4); g.line([(60, 40), (76, 52)], 4)
    g.poly([(42, 24), (50, 6), (58, 24)])
    for x0, y0, x1, y1 in ((34, 86, 26, 96), (66, 86, 74, 96), (24, 52, 14, 60), (76, 52, 86, 60), (50, 66, 50, 82)):
        g.line([(x0, y0), (x1, y1)], 1.6)
    return g


def old_scrolls():
    """Two old scrolls, one open."""
    g = G()
    scroll(g, 50, 40, 32, 20)
    g.ell(18, 70, 82, 84); g.ell(14, 66, 26, 88); g.ell(74, 66, 86, 88)
    return g


def rice():
    """A bowl heaped with rice, chopsticks across it."""
    g = G()
    g.ell(22, 30, 78, 62)                                                           # the heap of rice
    for x, y in ((38, 42), (50, 38), (62, 44), (44, 52), (58, 54)):
        g.ell(x - 3, y - 2, x + 3, y + 3, 0)
    g.poly([(12, 56), (88, 56), (80, 76), (62, 86), (38, 86), (20, 76)])           # the bowl
    g.poly([(36, 86), (64, 86), (60, 94), (40, 94)])
    g.line([(64, 30), (94, 8)], 3.4); g.line([(70, 34), (98, 16)], 3.4)             # chopsticks
    return g


def danqing_incense():
    """An incense stick in its holder, its smoke curling like a brushstroke."""
    g = G()
    g.ell(22, 72, 78, 94); g.poly([(28, 72), (72, 72), (66, 62), (34, 62)])
    g.line([(50, 66), (50, 30)], 4.4)
    g.circ(50, 28, 4.4)
    g.line([(50, 22), (62, 14), (46, 8), (60, 2)], 4.4)
    g.poly([(70, 10), (92, 40), (82, 46), (70, 20)])                                # a brush tip
    return g


def jade_eye_monkey():
    """A monkey's face with round jade eyes."""
    g = G()
    g.circ(50, 50, 32)
    g.circ(16, 46, 10); g.circ(84, 46, 10)                                          # ears
    g.ell(26, 36, 74, 84, 0)                                                        # the face
    for x in (38, 62):
        g.circ(x, 52, 9); g.circ(x, 52, 4, 0)
    g.ell(42, 66, 58, 76)
    return g


FOODS = {"Wild Deer": wild_deer, "Beast Milk": beast_milk, "Python Blood": python_blood, "Fine Iron": fine_iron,
         "Old Blades": old_blades, "Rooster Iron": rooster_iron, "Iron Ore": iron_ore,
         "Battlefield Bones": battlefield_bones, "Fire Charcoal": fire_charcoal, "Dragonfish": dragonfish,
         "Lingzhi": lingzhi, "Marsh Mud": marsh_mud, "Wind Knot Grass": wind_knot_grass,
         "Sand Gull Earth": sand_gull_earth, "Dancing Snow": dancing_snow, "Lightning Eel": lightning_eel,
         "Rotten Frozen Mud": rotten_frozen_mud, "Flame Swan Stone": flame_swan_stone,
         "Dark Fragrant Mushroom": dark_fragrant_mushroom, "White Shadow Grass": white_shadow_grass,
         "Arrow Bamboo": arrow_bamboo, "Wave Sound Conch": wave_sound_conch, "Illusion Peach": illusion_peach,
         "Splendid Overlord Flower": splendid_overlord_flower, "Taize Flower": taize_flower,
         "Peach Blossom": peach_blossom, "White Lotus Silkworm": white_lotus_silkworm,
         "Nine-Bend Dream Flower": nine_bend_dream_flower, "Wolf Meat": wolf_meat, "Time River Water": time_river_water,
         "Nether Jellyfish": nether_jellyfish, "Pearl Thread Water": pearl_thread_water,
         "Flying Bear Flesh": flying_bear_flesh, "North Ban Licorice": north_ban_licorice, "Hound Dung": hound_dung,
         "Brocade Cloud": brocade_cloud, "Heavy Gold": heavy_gold, "Ash": ash, "Star Cave Stone": star_cave_stone,
         "Ginseng Whiskers": ginseng_whiskers, "Old Scrolls": old_scrolls, "Rice": rice,
         "Danqing Incense": danqing_incense, "Jade-Eye Monkey": jade_eye_monkey}


def icons():
    return [("ResourceIcons", n, f, "black") for n, f in FOODS.items()]
