"""Regions II (2026-11-08): a nation icon for every city-state, in the flat style and motif language of glyphs.py.

Without one Unciv draws a city-state's portrait as a bare circle in its colours [src Portrait.PortraitNation]. Every
emblem is built from geometric primitives (MOD_SPEC rule 6); the motif comes from the canon fact the civilopedia
gives for the city-state (docs/LORE_MAPPING.md "Regions II", "Phase D: regional conflict").
"""
from __future__ import annotations

import math

from .arcart import _cloud
from .glyphs import G, human, wolf_head
from .glyphs2 import coin, ding, flame, roof, waves


def _petal(g: G, cx, cy, length, width, angle, v=255):
    """A pointed petal or wing from (cx, cy) outwards at `angle` degrees (0 = east, y up)."""
    a = math.radians(angle)
    tip = (cx + length * math.cos(a), cy - length * math.sin(a))
    mid = (cx + length * 0.5 * math.cos(a), cy - length * 0.5 * math.sin(a))
    n = (-math.sin(a) * width, -math.cos(a) * width)
    g.poly([(cx, cy), (mid[0] + n[0], mid[1] + n[1]), tip, (mid[0] - n[0], mid[1] - n[1])], v)


# ---------------------------------------------------------------- Southern Border
def hairy_man_tribe():
    """Lang Ya's kin, the hairy-men refiners: a shaggy head over a refining cauldron."""
    g = G()
    for k in range(14):                                                            # mane
        a = math.radians(-20 + k * 220 / 13)
        g.line([(50 + 16 * math.cos(a), 34 - 16 * math.sin(a)), (50 + 28 * math.cos(a), 34 - 28 * math.sin(a))], 5)
    g.circ(50, 34, 17)
    g.circ(43, 32, 3, 0); g.circ(57, 32, 3, 0)
    ding(g, 50, 74, 0.72)
    return g


def foothill_villages():
    """Mortal villages at the foot of the mountain."""
    g = G()
    g.poly([(10, 66), (36, 22), (50, 40), (62, 26), (90, 66)])                    # mountain
    g.poly([(36, 22), (44, 35), (38, 33), (33, 38), (30, 32)], 0)                 # snow line
    for x in (30, 66):                                                            # two houses
        roof(g, x, 70, 16, 12)
        g.poly([(x - 11, 72), (x + 11, 72), (x + 11, 90), (x - 11, 90)])
        g.poly([(x - 4, 79), (x + 4, 79), (x + 4, 90), (x - 4, 90)], 0)
    return g


def jia_clan():
    """The Jia merchants: a tied money pouch over a coin."""
    g = G()
    g.ell(22, 34, 78, 90)                                                         # pouch
    g.poly([(38, 20), (62, 20), (56, 38), (44, 38)])                              # neck
    g.line([(36, 38), (64, 38)], 5, 0)                                            # the cord
    coin(g, 50, 64, 15, 0)
    return g


# ---------------------------------------------------------------- Northern Plains
def lang_ya_sect():
    """The Lang Ya blessed land: a floating island carrying a refining cauldron."""
    g = G()
    ding(g, 50, 36, 0.62)
    g.poly([(12, 56), (88, 56), (72, 70), (60, 86), (50, 94), (40, 84), (28, 70)])
    g.line([(20, 60), (80, 60)], 2.5, 0)
    _cloud(g, 18, 82, 12); _cloud(g, 84, 82, 12)
    return g


def man_tribe():
    """The Man tribe of Red Flame Valley: a war spear through a flame."""
    g = G()
    flame(g, 50, 92, 74)
    g.line([(50, 96), (50, 20)], 5, 0)
    g.line([(50, 92), (50, 24)], 3.2)
    g.poly([(50, 4), (60, 22), (50, 18), (40, 22)])                               # spearhead
    return g


def ge_tribe():
    """The Ge tribe's camp: a round felt tent with its lattice band and smoke ring."""
    g = G()
    g.ell(10, 26, 90, 86)                                                         # dome
    g.poly([(10, 56), (90, 56), (90, 88), (10, 88)])                              # wall
    g.line([(12, 58), (88, 58)], 3, 0)
    for x in range(18, 86, 9):                                                    # lattice
        g.line([(x, 62), (x + 6, 70)], 1.6, 0)
    g.poly([(40, 88), (40, 70), (60, 70), (60, 88)], 0)                           # door
    g.circ(50, 26, 7, 0); g.arc_band(50, 26, 7, 4, 0, 180)                        # smoke ring
    return g


# ---------------------------------------------------------------- Central Continent: the ten great sects
def spirit_affinity_house():
    """Spirit Affinity House: two linked rings of affinity under a hall roof."""
    g = G()
    roof(g, 50, 30, 40, 22)
    for x in (38, 62):
        g.circ(x, 64, 20); g.circ(x, 64, 14, 0)
    g.arc_band(38, 64, 20, 14, -60, 60)                                           # re-ink the left ring's crossing
    return g


def combat_immortal_sect():
    """Combat Immortal Sect, famed for battle: a war drum with two crossed drumsticks."""
    g = G()
    for a, b in (((18, 8), (62, 40)), ((82, 8), (38, 40))):                       # drumsticks
        g.line([a, b], 5)
        g.circ(*a, 6)
    g.ell(16, 40, 84, 58)                                                         # drum head
    g.poly([(16, 49), (84, 49), (80, 86), (20, 86)])                              # body
    g.ell(20, 78, 80, 94)
    g.ell(22, 43, 78, 55, 0); g.ell(26, 45, 74, 53)                               # the skin's rim
    for x in (26, 38, 50, 62, 74):                                                # studs
        g.circ(x, 66, 2.6, 0)
    return g


def immortal_crane_sect():
    """The Immortal Crane Sect of Fei He Mountain: a crane in flight."""
    g = G()
    _petal(g, 46, 54, 48, 11, 150)                                                # wings
    _petal(g, 54, 54, 48, 11, 30)
    g.ell(36, 46, 64, 64)                                                         # body
    g.line([(62, 54), (78, 40), (84, 26)], 4)                                     # neck
    g.circ(86, 23, 5)
    g.poly([(89, 21), (99, 25), (89, 26)])                                        # beak
    g.circ(87, 20, 2, 0)                                                          # the red crown, cut out
    g.line([(38, 60), (16, 76)], 3); g.line([(40, 62), (22, 82)], 3)              # legs
    return g


def heavenly_lotus_sect():
    """Heavenly Lotus Sect: a lotus in bloom on its blessed water."""
    g = G()
    for a in (90, 125, 55, 160, 20):
        _petal(g, 50, 66, 46 if a == 90 else 38, 10, a)
    g.ell(30, 62, 70, 74)
    waves(g, 50, 86, 34, n=1)
    return g


def spirit_butterfly_valley():
    """Spirit Butterfly Valley, masters of the information path: a butterfly."""
    g = G()
    for side in (-1, 1):
        g.ell(50 + side * 6 - (36 if side < 0 else 0), 16, 50 + side * 6 + (36 if side > 0 else 0), 54)
        g.ell(50 + side * 6 - (26 if side < 0 else 0), 50, 50 + side * 6 + (26 if side > 0 else 0), 82)
        g.circ(50 + side * 24, 34, 6, 0)                                          # eye spots
    g.ell(45, 22, 55, 82)                                                         # body
    g.line([(48, 24), (36, 6)], 2.5); g.line([(52, 24), (64, 6)], 2.5)            # antennae
    g.line([(47, 24), (47, 80)], 2, 0); g.line([(53, 24), (53, 80)], 2, 0)
    return g


def ancient_soul_sect():
    """Ancient Soul Sect above the Earth Abyss: a soul fire rising out of a chasm."""
    g = G()
    g.poly([(6, 66), (36, 66), (44, 94), (56, 94), (64, 66), (94, 66), (94, 98), (6, 98)])  # the abyss
    g.poly([(50, 4), (64, 30), (66, 46), (58, 60), (50, 64), (42, 60), (34, 46), (36, 30)])
    g.poly([(50, 22), (56, 38), (54, 52), (50, 56), (46, 52), (44, 38)], 0)
    g.circ(50, 44, 5)
    return g


def heavens_envy_tower():
    """Heaven's Envy Tower: a three-storey tower."""
    g = G()
    for k, (y, w) in enumerate(((26, 26), (48, 32), (70, 38))):
        roof(g, 50, y, w, 14)
        g.poly([(50 - w * 0.6, y + 2), (50 + w * 0.6, y + 2), (50 + w * 0.6, y + 14), (50 - w * 0.6, y + 14)])
        g.poly([(46, y + 5), (54, y + 5), (54, y + 14), (46, y + 14)], 0)
    g.line([(50, 12), (50, 2)], 3)
    g.poly([(24, 84), (76, 84), (82, 94), (18, 94)])
    return g


def wind_cloud_manor():
    """Wind Cloud Manor, famed for Gu formations: clouds over a swirl of wind."""
    g = G()
    _cloud(g, 50, 40, 36)
    for k in range(3):
        y = 60 + k * 11
        g.line([(16 + k * 8, y), (72 - k * 4, y)], 4)
        g.arc_band(72 - k * 4, y - 5, 6, 2, -90, 90)
    return g


def black_heaven_temple():
    """Black Heaven Temple: a temple roof under a black sun."""
    g = G()
    g.circ(50, 30, 24); g.circ(50, 30, 17, 0); g.circ(50, 30, 12)
    roof(g, 50, 66, 44, 16)
    for x in (24, 40, 60, 76):
        g.line([(x, 70), (x, 92)], 5)
    g.line([(14, 94), (86, 94)], 5)
    return g


def myriad_dragon_dock():
    """Myriad Dragon Dock on its island in Dragon Lake: a dragon rising over the waves after a pearl."""
    g = G()
    body = [(10 + i * 2.6, 70 - i * 1.5 - 11 * math.sin(i / 4.0)) for i in range(26)]
    g.line(body, 10)
    for x, y in body[3:-3:4]:
        g.poly([(x - 4, y - 3), (x + 1, y - 14), (x + 5, y - 3)])                  # dorsal fins
    hx, hy = body[-1]
    g.ell(hx - 6, hy - 12, hx + 14, hy + 6)                                        # head
    g.poly([(hx + 10, hy - 8), (hx + 26, hy - 4), (hx + 12, hy - 1)])             # upper jaw
    g.poly([(hx + 10, hy + 1), (hx + 22, hy + 6), (hx + 8, hy + 5)])              # lower jaw
    g.line([(hx, hy - 10), (hx - 6, hy - 22)], 3); g.line([(hx + 6, hy - 11), (hx + 6, hy - 24)], 3)  # horns
    g.line([(hx + 14, hy - 2), (hx + 26, hy + 10)], 1.8)                          # whisker
    g.circ(hx + 5, hy - 5, 2.2, 0)                                                # eye
    g.circ(86, 18, 8); g.circ(86, 18, 4, 0)                                       # the pearl
    waves(g, 50, 88, 42, n=1)
    return g


# ---------------------------------------------------------------- Eastern Sea
def merman_imperial_court():
    """The merfolk's court: a crowned fish tail."""
    g = G()
    g.poly([(24, 30), (32, 14), (42, 26), (50, 8), (58, 26), (68, 14), (76, 30)])  # crown
    g.ell(38, 36, 62, 70)
    g.poly([(44, 66), (56, 66), (52, 82), (48, 82)])
    _petal(g, 50, 80, 30, 8, 215); _petal(g, 50, 80, 30, 8, 325)                   # tail fins
    return g


def song_clan():
    """The Song clan's Heavy Water Blessed Land: a heavy drop over the sea."""
    g = G()
    g.poly([(50, 6), (64, 30), (70, 46), (66, 58), (50, 66), (34, 58), (30, 46), (36, 30)])
    g.ell(30, 30, 70, 66)
    g.ell(40, 38, 50, 52, 0)
    waves(g, 50, 82, 40, n=2)
    return g


def xia_clan():
    """The Xia clan's harbour: an anchor."""
    g = G()
    g.circ(50, 14, 9); g.circ(50, 14, 4.5, 0)
    g.line([(50, 22), (50, 84)], 7)
    g.line([(32, 34), (68, 34)], 6)
    g.arc_band(50, 64, 30, 23, 180, 360)
    g.poly([(14, 62), (26, 58), (24, 70)]); g.poly([(86, 62), (74, 58), (76, 70)])  # flukes
    return g


# ---------------------------------------------------------------- Western Desert
def lan_clan():
    """The Lan clan of Zhou Xi Oasis: a palm over the oasis pool."""
    g = G()
    g.line([(50, 84), (52, 60), (50, 36)], 6)
    for a in (20, 60, 120, 160, 95):
        _petal(g, 50, 34, 34, 7, a)
    g.ell(18, 80, 82, 96)
    return g


def xiao_clan():
    """The Xiao merchants of the Silk Corridor: a camel with its load."""
    g = G()
    g.ell(24, 34, 76, 66)                                                         # body
    g.ell(34, 22, 52, 42); g.ell(50, 24, 66, 42)                                  # humps
    g.line([(74, 46), (84, 26)], 7); g.ell(80, 16, 96, 30)                        # neck, head
    for x in (30, 40, 62, 72):
        g.line([(x, 62), (x, 92)], 5)
    g.poly([(36, 40), (64, 40), (64, 50), (36, 50)], 0)                           # the silk bale's band
    return g


def mo_clan():
    """The Mo clan of Sand Wolf City: a howling wolf over a dune."""
    g = G()
    wolf_head(g, 50, 40, 0.8)
    g.poly([(4, 96), (30, 78), (56, 86), (80, 72), (96, 80), (96, 98), (4, 98)])
    return g


def wan_clan():
    """The Wan clan of Gao Song (tall pine) Oasis: a tall pine over the oasis water."""
    g = G()
    g.line([(50, 86), (50, 12)], 5)
    for k, (y, w) in enumerate(((22, 14), (38, 22), (54, 30), (70, 36))):
        g.poly([(50, y - 12), (50 + w, y + 6), (50 - w, y + 6)])
    g.ell(16, 82, 84, 96)
    return g


# ---------------------------------------------------------------- reference audit Layer 4: the variant humans
def _wing(g: G, cx, cy, side, s=1.0):
    """One feathered wing from the shoulder at (cx, cy), spreading sideways to `side` (-1 left, +1 right)."""
    for k, (ln, wd) in enumerate(((44, 8), (40, 7), (34, 6), (27, 5))):
        a = (150 + 16 * k) if side < 0 else (30 - 16 * k)
        _petal(g, cx, cy, ln * s, wd * s, a)


def feathermen():
    """Yu Sheng City's feathermen: a robed figure with wings spread wide."""
    g = G()
    _wing(g, 44, 44, -1, 0.95); _wing(g, 56, 44, 1, 0.95)
    g.circ(50, 24, 9)
    g.poly([(42, 38), (58, 38), (64, 92), (36, 92)])
    g.line([(50, 44), (50, 90)], 2.2, 0)
    return g


def snowmen():
    """The Great Snow Mountain: a white-capped peak under a six-armed snowflake."""
    g = G()
    g.poly([(8, 94), (50, 40), (92, 94)])
    g.poly([(50, 40), (62, 56), (55, 52), (50, 60), (45, 52), (38, 56)], 0)
    for k in range(6):
        a = math.radians(90 + k * 60)
        g.line([(50, 20), (50 + 16 * math.cos(a), 20 - 16 * math.sin(a))], 3.2)
    g.circ(50, 20, 4)
    return g


def inkmen():
    """Ink Man City: a figure brushed in ink, an ink drop for a head, standing in its own pool of ink."""
    g = G()
    g.poly([(50, 4), (59, 18), (61, 26), (55, 33), (45, 33), (39, 26), (41, 18)])          # the ink-drop head
    g.poly([(42, 38), (58, 38), (62, 60), (56, 82), (44, 82), (38, 60)])                     # a brushed body
    g.line([(42, 42), (28, 62), (24, 74)], 6); g.line([(58, 42), (72, 62), (76, 74)], 6)    # arms hanging
    g.circ(24, 80, 3.5); g.circ(76, 80, 3.5)                                                 # drips
    g.ell(20, 84, 80, 96)                                                                    # the pool
    return g


def rockmen():
    """The rockmen: an angular figure of cut stone gripping a digging pick."""
    g = G()
    g.poly([(38, 10), (60, 8), (66, 22), (58, 34), (40, 34), (34, 22)])                      # a faceted head
    g.poly([(28, 38), (70, 36), (76, 58), (66, 72), (32, 72), (24, 56)])                     # a stone torso
    g.poly([(32, 74), (48, 74), (46, 94), (30, 94)]); g.poly([(52, 74), (68, 74), (70, 94), (54, 94)])
    g.line([(40, 34), (46, 50), (36, 66)], 2.4, 0); g.line([(46, 50), (70, 52)], 2.4, 0)    # cracks
    g.circ(44, 21, 2.6, 0); g.circ(56, 20, 2.6, 0)
    g.line([(76, 34), (92, 80)], 5)                                                          # the pick
    g.poly([(64, 30), (92, 22), (88, 32), (72, 36)])
    return g


def winged_folk():
    g = G(); _wing(g, 46, 56, -1, 1.1); _wing(g, 54, 56, 1, 1.1); g.circ(50, 56, 6); return g


def snow_folk():
    g = G()
    for k in range(6):
        a = math.radians(90 + k * 60)
        x, y = 50 + 40 * math.cos(a), 50 - 40 * math.sin(a)
        g.line([(50, 50), (x, y)], 5)
        for t in (0.55, 0.8):
            bx, by = 50 + 40 * t * math.cos(a), 50 - 40 * t * math.sin(a)
            for d in (-0.6, 0.6):
                g.line([(bx, by), (bx + 10 * math.cos(a + d), by - 10 * math.sin(a + d))], 3.4)
    g.circ(50, 50, 7)
    return g


def ink_folk():
    """A brush and its ink drop."""
    g = G()
    g.line([(22, 20), (62, 60)], 7)
    g.poly([(56, 54), (74, 60), (82, 78), (68, 70), (60, 66)])
    g.poly([(70, 6), (80, 22), (82, 30), (76, 36), (64, 36), (58, 30), (60, 22)])
    g.ell(18, 80, 82, 94)
    return g


def stone_folk():
    """A cut stone and a pick."""
    g = G()
    g.poly([(18, 54), (40, 40), (70, 46), (84, 66), (66, 88), (30, 86), (14, 72)])
    g.line([(40, 40), (46, 62), (30, 86)], 2.6, 0); g.line([(46, 62), (84, 66)], 2.6, 0)
    g.line([(54, 34), (80, 8)], 5)
    g.poly([(66, 4), (92, 22), (86, 26), (64, 12)])
    return g



# ---------------------------------------------------------------- reference audit Layer 7: more super forces
def tie_clan():
    """The Tie (iron) clan's Demon-Suppressing Tower, where demonic Gu Masters are held: an iron pagoda whose barred
    gate is shut."""
    g = G()
    w, y = 40.0, 94.0
    for tier in range(5):
        h = 13 - 2 * tier
        g.poly([(50 - w / 2, y), (50 + w / 2, y), (50 + w / 2, y - h), (50 - w / 2, y - h)])
        roof(g, 50, y - h - 1, w / 2 + 7, 7)
        y -= h + 7
        w -= 6
    g.line([(50, y + 2), (50, y - 8)], 3.2)
    g.circ(50, y - 9, 3.4)
    g.poly([(42, 94), (58, 94), (58, 80), (42, 80)], 0)                            # the gate
    for x in (45.5, 50, 54.5):                                                    # its bars
        g.line([(x, 80), (x, 94)], 2.2)
    return g


def tang_clan():
    """The Tang clan, which found Thieving Heaven's dream realm in the desert: a dream spiral rising over the dunes,
    stars caught in it."""
    g = G()
    g.poly([(2, 98), (2, 86), (22, 76), (44, 86), (68, 72), (98, 84), (98, 98)])
    pts = []
    for i in range(80):
        t = i / 79 * 2.7 * math.pi
        r = 3 + t * 4.6
        pts.append((50 + r * math.cos(t), 38 - r * 0.86 * math.sin(t)))
    g.line(pts, 5.4)
    for x, y, r in ((18, 18, 4.2), (84, 30, 3.4), (76, 8, 2.8)):
        g.poly([(x, y - 2.4 * r), (x + r * 0.5, y - r * 0.5), (x + 2.4 * r, y), (x + r * 0.5, y + r * 0.5),
                (x, y + 2.4 * r), (x - r * 0.5, y + r * 0.5), (x - 2.4 * r, y), (x - r * 0.5, y - r * 0.5)])
    return g


def shen_clan():
    """The Shen clan of the sound path, whose sea makes the conch of wave-sound: a conch shell, sound rippling out of
    its mouth."""
    g = G()
    g.circ(46, 58, 25)                                                            # the body whorl
    g.poly([(28, 42), (58, 28), (92, 8), (72, 58), (62, 70)])                     # the spire
    for t in (0.2, 0.45, 0.7):                                                    # knobs on its shoulder
        x, y = 58 + 34 * t, 28 - 20 * t
        g.poly([(x - 5, y + 2), (x - 1, y - 8), (x + 4, y - 1)])
    for a, b in (((60, 38), (74, 48)), ((70, 28), (80, 36))):                     # sutures
        g.line([a, b], 2.4, 0)
    g.poly([(26, 70), (6, 94), (38, 80)])                                         # the canal
    g.poly([(30, 46), (42, 52), (46, 70), (36, 84), (26, 74), (24, 58)], 0)       # the mouth
    for r in (8, 15, 22):                                                         # the wave-sound
        g.arc_band(36, 66, r + 2.6, r, 128, 232)
    return g


def _sun(g: G, cx, cy, r, rays=12):
    g.circ(cx, cy, r)
    for k in range(rays):
        a = math.radians(k * 360 / rays)
        g.poly([(cx + (r + 3) * math.cos(a - 0.12), cy - (r + 3) * math.sin(a - 0.12)),
                (cx + (r + 10) * math.cos(a), cy - (r + 10) * math.sin(a)),
                (cx + (r + 3) * math.cos(a + 0.12), cy - (r + 3) * math.sin(a + 0.12))])


def ma_tribe():
    """The Ma (horse) tribe, a golden bloodline of Giant Sun: a horse's head before the sun."""
    g = G()
    _sun(g, 72, 24, 12)
    g.poly([(36, 96), (40, 70), (34, 56), (22, 58), (10, 54), (8, 46), (20, 32), (30, 22), (38, 10), (44, 20),
            (50, 18), (58, 30), (64, 50), (66, 70), (62, 96)])                    # head and neck, facing left
    for k in range(5):                                                            # the mane along the neck
        t = k / 4
        x, y = 50 + 16 * t, 20 + 50 * t
        g.ell(x - 3, y - 6, x + 7, y + 6)
    for k in range(4):                                                            # its strands, cut
        t = (k + 0.5) / 4
        g.line([(52 + 14 * t, 24 + 46 * t), (58 + 14 * t, 30 + 46 * t)], 1.6, 0)
    g.circ(30, 34, 3.2, 0)                                                        # eye
    g.circ(14, 50, 2, 0)                                                          # nostril
    return g


def liu_tribe():
    """The Liu tribe, a golden family of Giant Sun's line whose heir was famed for letters and war alike: a sword and
    a writing brush crossed beneath the sun."""
    g = G()
    _sun(g, 50, 20, 10)
    g.poly([(24, 84), (70, 40), (78, 34), (74, 44), (30, 90)])                    # the sword's blade, point up right
    g.line([(16, 76), (36, 96)], 5)                                               # its guard
    g.line([(24, 86), (12, 98)], 4.4); g.circ(10, 99, 3.6)                        # grip and pommel
    g.line([(84, 92), (46, 56)], 4)                                               # the brush's shaft
    g.ell(84, 90, 96, 102); g.ell(87, 93, 93, 99, 0)                              # its hanging loop
    g.circ(40, 50, 7.5)                                                           # the brush head: a teardrop
    g.poly([(45.3, 44.7), (34.7, 55.3), (22, 32)])
    return g


def dong_fang_tribe():
    """The Dong Fang (east) tribe of the wisdom path in Jade Pool Blessed Land: the sun rising over the jade pool,
    its light in the water."""
    g = G()
    c = G()
    c.circ(50, 58, 22)
    for k in range(9):
        a = math.radians(10 + k * 20)
        c.poly([(50 + 25 * math.cos(a - 0.08), 58 - 25 * math.sin(a - 0.08)), (50 + 40 * math.cos(a), 58 - 40 * math.sin(a)),
                (50 + 25 * math.cos(a + 0.08), 58 - 25 * math.sin(a + 0.08))])
    c.poly([(0, 60), (100, 60), (100, 100), (0, 100)], 0)                        # cut at the horizon
    g.paste(c)
    g.line([(6, 62), (94, 62)], 3)
    for y, w in ((72, 34), (82, 24), (91, 14)):                                  # the pool's ripples and the light
        g.line([(50 - w, y), (50 + w, y)], 3.2)
    return g

def shadow_sect():
    """Layer 13: the Shadow Sect: a cultivator whose long shadow stands up on its own, a soul flame above it."""
    g = G(); human(g, 36, 22, 0.95)
    g.poly([(52, 96), (90, 96), (84, 56), (70, 50)])                            # the shadow, risen
    g.circ(78, 40, 9); g.poly([(70, 38), (86, 38), (78, 10)])                   # its soul flame
    return g


def shadow_sect_type():
    """Layer 13: the Shadow Sect's kind: a soul flame splitting into three."""
    g = G()
    for dx, top in ((-22, 30), (0, 6), (22, 30)):
        g.circ(50 + dx, top + 36, 12); g.poly([(50 + dx - 11, top + 32), (50 + dx + 11, top + 32), (50 + dx, top)])
    g.circ(50, 84, 8)
    return g


CITY_STATE_ICONS = [(n, f) for n, f in (
    ("Hairy Man Tribe", hairy_man_tribe), ("Foothill Villages", foothill_villages), ("Jia Clan", jia_clan),
    ("Lang Ya Sect", lang_ya_sect), ("Man Tribe", man_tribe), ("Ge Tribe", ge_tribe),
    ("Spirit Affinity House", spirit_affinity_house), ("Combat Immortal Sect", combat_immortal_sect),
    ("Immortal Crane Sect", immortal_crane_sect), ("Heavenly Lotus Sect", heavenly_lotus_sect),
    ("Spirit Butterfly Valley", spirit_butterfly_valley), ("Ancient Soul Sect", ancient_soul_sect),
    ("Heaven's Envy Tower", heavens_envy_tower), ("Wind Cloud Manor", wind_cloud_manor),
    ("Black Heaven Temple", black_heaven_temple), ("Myriad Dragon Dock", myriad_dragon_dock),
    ("Merman Imperial Court", merman_imperial_court), ("Song Clan", song_clan), ("Xia Clan", xia_clan),
    ("Lan Clan", lan_clan), ("Xiao Clan", xiao_clan), ("Mo Clan", mo_clan), ("Wan Clan", wan_clan),
    ("Feathermen", feathermen), ("Snowmen", snowmen), ("Inkmen", inkmen), ("Rockmen", rockmen),
    ("Tie Clan", tie_clan), ("Tang Clan", tang_clan), ("Shen Clan", shen_clan), ("Ma Tribe", ma_tribe),
    ("Liu Tribe", liu_tribe), ("Dong Fang Tribe", dong_fang_tribe), ("Shadow Sect", shadow_sect))]
FOLK_ICONS = [("Winged Folk", winged_folk), ("Snow Folk", snow_folk), ("Ink Folk", ink_folk), ("Stone Folk", stone_folk),
              ("Shadow Sect", shadow_sect_type)]


def icons():
    return ([("NationIcons", name, draw, "white") for name, draw in CITY_STATE_ICONS]
            + [("CityStateIcons", name, draw, "white") for name, draw in FOLK_ICONS])
