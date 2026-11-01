"""Immortal arc icons (MOD_SPEC_2 Phase C; the user's D6: every object that shows an image gets a designed one).

C1, ascension: the three qi and green grape essence (black, resources), the techs Purple Crystal Essence, Three Qi and
Calamity Lore (white), the Rank Five Gu Master and the Rank Six Gu Immortal (white, units), the Ascension promotion
and the four blessed-land grades (white, promotions). Every shape is built from primitives; nothing is copied.
"""
from __future__ import annotations

import math

from .glyphs import G, fist, gu_beetle, human, pips
from .glyphs2 import aperture, coin, octagon_array, ranked_gu_master, roof


def _cloud(g: G, cx, cy, w, v=255):
    """A flat-bottomed cloud of three puffs."""
    g.circ(cx - w * 0.3, cy, w * 0.22, v)
    g.circ(cx, cy - w * 0.1, w * 0.3, v)
    g.circ(cx + w * 0.32, cy + w * 0.02, w * 0.2, v)
    g.poly([(cx - w * 0.5, cy + w * 0.02), (cx + w * 0.5, cy + w * 0.02), (cx + w * 0.5, cy + w * 0.2),
            (cx - w * 0.5, cy + w * 0.2)], v)


def _bars(g: G, cx, cy, w, broken, v=255, gap=10):
    """A trigram: three bars, solid (heaven) or broken (earth)."""
    for k in range(3):
        y = cy + (k - 1) * gap
        if broken:
            g.line([(cx - w / 2, y), (cx - w * 0.1, y)], 6, v)
            g.line([(cx + w * 0.1, y), (cx + w / 2, y)], 6, v)
        else:
            g.line([(cx - w / 2, y), (cx + w / 2, y)], 6, v)


def heaven_qi():
    """The heaven trigram over a drifting cloud."""
    g = G(); _bars(g, 50, 26, 56, broken=False); _cloud(g, 50, 70, 70); return g


def earth_qi():
    """A mountain over the earth trigram."""
    g = G()
    g.poly([(14, 58), (40, 16), (54, 36), (64, 24), (88, 58)])
    _bars(g, 50, 72, 60, broken=True, gap=11)
    return g


def human_qi():
    """A person inside a ring of rising qi."""
    g = G()
    g.arc_band(50, 52, 42, 35, 110, 430)
    human(g, 50, 16, 1.05, arms="down")
    for k in range(3):
        g.circ(50 + 38.5 * math.cos(math.radians(90 + 120 * k)), 52 - 38.5 * math.sin(math.radians(90 + 120 * k)), 3, 0)
    return g


def green_grape_essence():
    """A cluster of grapes (the rank-six essence) under a leaf, with a drop of essence."""
    g = G()
    rows = [(4, 34), (3, 50), (2, 64), (1, 77)]
    for n, y in rows:
        for i in range(n):
            g.circ(50 + (i - (n - 1) / 2) * 15, y, 7.6)
    g.line([(50, 26), (52, 12)], 4)
    g.poly([(52, 16), (74, 6), (80, 22), (60, 24)])
    g.poly([(22, 10), (28, 22), (22, 28), (16, 22)])
    return g


def purple_crystal_essence():
    """A faceted crystal inside the aperture ring (rank five's purple crystal essence)."""
    g = G()
    g.arc_band(50, 50, 44, 37, 0, 360)
    g.poly([(50, 16), (68, 34), (62, 80), (38, 80), (32, 34)])
    g.line([(50, 18), (50, 78)], 2.5, 0)
    g.line([(33, 35), (50, 46), (67, 35)], 2.5, 0)
    return g


def three_qi():
    """Three comma-shaped qi swirls (heaven, earth, human) chasing one another around a centre."""
    g = G()
    for k in range(3):
        a = 90 + 120 * k
        g.arc_band(50, 50, 38, 28, a, a + 95)                                            # tail
        g.circ(50 + 30 * math.cos(math.radians(a)), 50 - 30 * math.sin(math.radians(a)), 11)   # head
    g.circ(50, 50, 7)
    return g


def calamity_lore():
    """A storm cloud with a falling bolt: calamities come on a schedule and can be prepared for."""
    g = G(); _cloud(g, 50, 32, 78); g.bolt([54, 40, 58, 44], 46, 84, 6); return g


def rank_five_gu_master():
    return ranked_gu_master(5)


def rank_six_gu_immortal():
    """A Gu Immortal standing on a cloud, a halo behind the head."""
    g = G()
    g.arc_band(50, 21, 17, 13, 0, 360)
    human(g, 50, 8, 1.05, arms="raised")
    _cloud(g, 50, 82, 74)
    return g


def ascension():
    """A figure rising out of a broken aperture ring."""
    g = G()
    for a0 in (200, 290, 380):
        g.arc_band(50, 66, 34, 27, a0, a0 + 60)
    human(g, 50, 6, 0.95, arms="raised")
    for y in (80, 90):
        g.line([(38, y + 4), (50, y - 4), (62, y + 4)], 4)
    return g


def blessed_land(grade):
    """A floating land with a peak and a tree; one diamond per grade step."""
    def draw():
        g = G()
        g.poly([(12, 50), (88, 50), (66, 70), (56, 82), (44, 78), (32, 70)])          # floating rock
        g.poly([(46, 50), (60, 18), (74, 50)])                                          # peak
        g.line([(30, 50), (30, 32)], 4); g.circ(30, 28, 9)                              # tree
        _cloud(g, 26, 14, 26)
        if grade:
            pips(g, grade, y=91)
        return g
    return draw


def _hourglass(g: G, cx, cy, h, v=255):
    w = h * 0.55
    g.poly([(cx - w, cy - h), (cx + w, cy - h), (cx + 4, cy), (cx + w, cy + h), (cx - w, cy + h), (cx - 4, cy)], v)
    g.line([(cx - w - 4, cy - h), (cx + w + 4, cy - h)], 5, v)
    g.line([(cx - w - 4, cy + h), (cx + w + 4, cy + h)], 5, v)


# ---- C2: calamities, tribulations, lifespan
def lifespan_gu():
    """A Gu curled in the lower bulb of an hourglass: a lifespan Gu holds years."""
    g = G(); _hourglass(g, 50, 50, 38)
    g.poly([(36, 20), (64, 20), (52, 44), (48, 44)], 0)                      # upper bulb, hollow
    g.poly([(48, 56), (52, 56), (66, 84), (34, 84)], 0)                      # lower bulb, hollow
    gu_beetle(g, 50, 74, 0.42, legs=False)
    return g


def formation_ward():
    """A formation ring under a protective dome."""
    g = G(); g.arc_band(50, 66, 44, 37, 0, 180); octagon_array(g, 50, 66, 26); return g


def stockpile_vault():
    """A storehouse with stacked stones before its door."""
    g = G()
    roof(g, 50, 30, 42, 20)
    g.poly([(18, 34), (82, 34), (82, 66), (18, 66)])
    g.poly([(42, 44), (58, 44), (58, 66), (42, 66)], 0)
    for x, y in ((30, 80), (50, 80), (70, 80), (40, 70), (60, 70)):
        coin(g, x, y, 9)
    return g


def calamity_countdown():
    """An hourglass under a small storm cloud."""
    g = G(); _hourglass(g, 50, 60, 30); _cloud(g, 50, 16, 46); return g


def tribulation_countdown():
    """A falling bolt inside a ring of time marks."""
    g = G()
    for k in range(12):
        a = math.radians(90 - 30 * k)
        g.line([(50 + 34 * math.cos(a), 50 - 34 * math.sin(a)), (50 + 44 * math.cos(a), 50 - 44 * math.sin(a))], 5)
    g.bolt([56, 40, 60, 44], 16, 80, 7)
    return g


def ravaged_land():
    """The floating blessed land split by a crack."""
    g = blessed_land(0)()
    g.line([(40, 44), (52, 56), (44, 66), (54, 84)], 5, 0)
    return g



# ---- C3: immortal Gu (world wonders, black) and the recipe tech
def _halo(g: G):
    g.arc_band(50, 50, 48, 44, 0, 360)


def spring_autumn_cicada():
    """A cicada with long folded wings inside a halo."""
    g = G(); _halo(g)
    g.ell(42, 22, 58, 70)                                                          # body
    g.circ(50, 20, 8)                                                              # head
    for side in (-1, 1):
        g.poly([(50 + side * 6, 30), (50 + side * 26, 40), (50 + side * 20, 82), (50 + side * 4, 66)])   # wings
        g.circ(50 + side * 6, 17, 3, 0)                                            # eyes
    g.line([(50, 32), (50, 68)], 2, 0)
    return g


def fixed_immortal_travel():
    """A Gu beetle leaving a curved trail of three steps toward a ring."""
    g = G(); _halo(g)
    gu_beetle(g, 34, 62, 0.9)
    for k, (x, y) in enumerate(((52, 50), (62, 38), (70, 28))):
        g.circ(x, y, 4 + k)
    g.arc_band(72, 26, 13, 9, 0, 360)
    return g


def man_as_before():
    """A person beside an hourglass."""
    g = G(); _halo(g); human(g, 36, 20, 0.95); _hourglass(g, 66, 50, 22); return g


def unravel_mystery():
    """A key turning in a ring of knots."""
    g = G(); _halo(g)
    g.arc_band(36, 42, 16, 9, 0, 360)
    g.line([(48, 52), (78, 82)], 7)
    g.line([(66, 70), (74, 62)], 6); g.line([(72, 76), (80, 68)], 6)
    return g


def connect_luck():
    """Two linked rings with a star between them."""
    g = G(); _halo(g)
    g.arc_band(38, 54, 20, 14, 0, 360); g.arc_band(62, 54, 20, 14, 0, 360)
    from .pathart import _star
    _star(g, 50, 24, 11)
    return g


def self_strength():
    g = G(); _halo(g); fist(g, 50, 42, 1.1); return g


def womans_heart():
    from .pathart import _heart
    g = G(); _halo(g); _heart(g, 50, 46, 26); g.poly([(50, 70), (56, 82), (50, 88), (44, 82)]); return g


def bone_spike():
    """Three bone spikes rising from a ridge."""
    g = G(); _halo(g)
    g.poly([(18, 74), (82, 74), (78, 82), (22, 82)])
    for x, h in ((32, 34), (50, 18), (68, 34)):
        g.poly([(x - 8, 74), (x, h), (x + 8, 74)])
        g.circ(x, h + 4, 4)
    return g


def star_eyes():
    """An eye whose pupil is a star."""
    from .pathart import _star
    g = G(); _halo(g)
    g.poly([(14, 50), (32, 32), (68, 32), (86, 50), (68, 68), (32, 68)])
    g.circ(50, 50, 15, 0)
    _star(g, 50, 50, 12)
    return g


def divert_disaster():
    """A shield turning a falling bolt aside."""
    g = G(); _halo(g)
    g.poly([(30, 44), (70, 44), (68, 66), (50, 82), (32, 66)])
    g.bolt([28, 18, 30, 22], 12, 38, 4)
    g.line([(70, 40), (84, 26)], 4)
    return g


def immortal_gu_recipes():
    """A recipe scroll under a Gu with a halo."""
    from .glyphs2 import scroll
    g = G(); scroll(g, 50, 66, 34, 22); gu_beetle(g, 50, 28, 0.7); g.arc_band(50, 28, 22, 18, 20, 160); return g


# ---- C4: inheritances (a stele carved with the path's symbol), their seals, the desolate beast, immortal materials
def _path_symbol(key):
    from .pathart import symbol
    return symbol(key)


def inheritance(key):
    """A tall stele under a roof, the path's symbol cut into its face."""
    from .pathart import place
    def draw():
        g = G()
        roof(g, 50, 18, 36, 14)
        g.poly([(28, 22), (72, 22), (70, 84), (30, 84)])
        g.poly([(18, 84), (82, 84), (82, 92), (18, 92)])
        place(g, _path_symbol(key), 50, 52, 0.42, 0)
        return g
    return draw


def seal(key):
    """A square seal stamp with a knob, the path's symbol cut into the face."""
    from .pathart import place
    def draw():
        g = G()
        g.poly([(20, 44), (80, 44), (80, 92), (20, 92)])
        g.ell(36, 12, 64, 40); g.poly([(42, 30), (58, 30), (60, 46), (40, 46)])
        place(g, _path_symbol(key), 50, 68, 0.4, 0)
        return g
    return draw


def desolate_beast_icon():
    """A horned beast head with ember eyes."""
    g = G()
    g.poly([(28, 34), (72, 34), (80, 58), (64, 88), (36, 88), (20, 58)])
    for side in (-1, 1):
        g.poly([(50 + side * 18, 38), (50 + side * 44, 6), (50 + side * 30, 42)])
        g.circ(50 + side * 12, 56, 5, 0)
    g.poly([(40, 72), (60, 72), (56, 80), (44, 80)], 0)
    return g


def immortal_materials():
    """Crystals and a bone heaped together."""
    g = G()
    for cx, h in ((34, 40), (52, 52), (70, 36)):
        g.poly([(cx - 9, 80), (cx - 7, 80 - h * 0.7), (cx, 80 - h), (cx + 7, 80 - h * 0.7), (cx + 9, 80)])
    g.line([(16, 86), (84, 86)], 7)
    g.circ(16, 86, 6); g.circ(84, 86, 6)
    return g


# ---- C5: ranks seven and eight
def rank_immortal(rank):
    def draw():
        g = rank_six_gu_immortal()
        pips(g, rank, y=6)
        return g
    return draw


def immortal_gu_generic(key, rank):
    """A rank-seven or rank-eight immortal Gu: the path's symbol in a double halo, the rank in diamonds."""
    from .pathart import place
    def draw():
        g = G(); g.arc_band(50, 46, 44, 40, 0, 360); g.arc_band(50, 46, 36, 34, 0, 360)
        place(g, _path_symbol(key), 50, 46, 0.5)
        pips(g, rank, y=94)
        return g
    return draw


def red_date():
    """A date fruit with its stem: rank-seven essence."""
    g = G(); g.ell(30, 26, 70, 86); g.line([(50, 26), (56, 10)], 4); g.poly([(56, 14), (76, 8), (70, 22)])
    g.ell(38, 38, 46, 58, 0)
    return g


def white_lychee():
    """A round, bumpy lychee: rank-eight essence."""
    g = G(); g.circ(50, 54, 32)
    for k in range(10):
        a = math.radians(36 * k)
        g.circ(50 + 22 * math.cos(a), 54 - 22 * math.sin(a), 3, 0)
    g.line([(50, 22), (54, 8)], 4)
    return g


def recipes_rank(rank):
    def draw():
        g = immortal_gu_recipes(); pips(g, rank, y=94); return g
    return draw


def grotto_heaven():
    """A cave arch opening onto stars: the rank-eight aperture."""
    from .pathart import _star
    g = G()
    g.arc_band(50, 66, 42, 30, 0, 180)
    g.poly([(8, 66), (20, 66), (20, 92), (8, 92)]); g.poly([(80, 66), (92, 66), (92, 92), (80, 92)])
    for x, y, r in ((50, 52, 10), (36, 70, 6), (64, 72, 6)):
        _star(g, x, y, r)
    return g


def tribulation_survivor():
    """A figure standing under a broken bolt."""
    g = G(); human(g, 50, 30, 0.95, arms="raised")
    g.bolt([20, 30, 24, 34], 4, 30, 4); g.bolt([70, 80, 74, 84], 4, 30, 4)
    return g


def advancing():
    g = G()
    for y in (30, 52, 74):
        g.line([(24, y + 12), (50, y - 8), (76, y + 12)], 8)
    return g


def advance_to(rank):
    def draw():
        g = G(); g.arc_band(50, 50, 46, 40, 0, 360)
        g.poly([(50, 14), (72, 40), (58, 40), (58, 72), (42, 72), (42, 40), (28, 40)])
        pips(g, rank, y=84)
        return g
    return draw


# ---- C5b: the Venerable, Eternal Life, Gu Houses
def venerable():
    """The Venerable: an immortal before a sun disc with nine rays."""
    g = G()
    for k in range(9):
        a = math.radians(90 + 40 * k)
        g.line([(50 + 34 * math.cos(a), 34 - 34 * math.sin(a)), (50 + 46 * math.cos(a), 34 - 46 * math.sin(a))], 4)
    g.circ(50, 34, 28); g.circ(50, 34, 24, 0)
    human(g, 50, 14, 1.1, arms="raised")
    return g


def venerable_ascension():
    """A figure on a peak under nine rays."""
    g = G()
    g.poly([(10, 92), (50, 46), (90, 92)])
    human(g, 50, 14, 0.7, arms="raised")
    for k in range(9):
        a = math.radians(20 + 17.5 * k)
        g.line([(50 + 30 * math.cos(a), 30 - 30 * math.sin(a) + 6), (50 + 44 * math.cos(a), 30 - 44 * math.sin(a) + 6)], 3)
    return g


def eternal_life():
    """An endless loop around a small figure: Fang Yuan's goal."""
    g = G()
    g.arc_band(30, 50, 22, 14, 0, 360); g.arc_band(70, 50, 22, 14, 0, 360)
    g.circ(50, 50, 9, 0)
    human(g, 50, 36, 0.45)
    return g


def true_inheritance():
    """A stele crowned with nine points."""
    g = inheritance("rule")()
    for k in range(5):
        x = 30 + 10 * k
        g.poly([(x - 4, 10), (x, 0), (x + 4, 10)])
    return g


def true_inheritance_seal():
    g = seal("rule")()
    for k in range(3):
        x = 40 + 10 * k
        g.poly([(x - 4, 12), (x, 2), (x + 4, 12)], 0)
    return g


def dao_lord():
    """A figure inside a ring of dao marks."""
    g = G()
    for k in range(24):
        a = math.radians(15 * k)
        g.line([(50 + 38 * math.cos(a), 50 - 38 * math.sin(a)), (50 + 46 * math.cos(a), 50 - 46 * math.sin(a))], 3 if k % 2 else 5)
    human(g, 50, 18, 0.95, arms="raised")
    return g


def gu_house_formation():
    """A pagoda over a formation ring."""
    g = G(); octagon_array(g, 50, 70, 24)
    roof(g, 50, 22, 26, 12); g.poly([(36, 24), (64, 24), (62, 42), (38, 42)])
    return g


def yellow_apricot():
    """An apricot with a leaf: rank-nine essence."""
    g = G(); g.circ(50, 56, 30); g.line([(50, 26), (52, 12)], 4); g.poly([(52, 16), (74, 10), (68, 26)])
    g.arc_band(50, 56, 26, 23, 100, 170, 0)
    return g


def calamity_luck_altar():
    g = G()
    for k, w in enumerate((40, 30, 20)):
        y = 86 - 16 * k
        g.poly([(50 - w, y), (50 + w, y), (50 + w, y - 12), (50 - w, y - 12)])
    g.circ(50, 26, 12)
    for x in (16, 84):
        g.line([(x, 88), (x, 40)], 5)
    return g


def flying_warship():
    g = G()
    g.poly([(10, 58), (90, 58), (78, 74), (22, 74)])
    g.line([(50, 58), (50, 12)], 4)
    g.poly([(52, 16), (80, 30), (52, 50)])
    _cloud(g, 50, 84, 70)
    return g


def dragon_palace():
    g = G()
    for k, w in enumerate((40, 30, 20)):
        y = 82 - 24 * k
        roof(g, 50, y - 12, w + 8, 10)
        g.poly([(50 - w + 6, y - 10), (50 + w - 6, y - 10), (50 + w - 6, y + 6), (50 - w + 6, y + 6)])
    g.circ(50, 14, 5)
    return g


# ---- C5c: the arc's nations, Fate Gu, the Fate War
def heavenly_court():
    """A palace gate on clouds under a single eye of fate."""
    g = G(); _cloud(g, 50, 80, 80)
    roof(g, 50, 40, 36, 14); g.poly([(26, 42), (74, 42), (74, 70), (26, 70)]); g.poly([(42, 52), (58, 52), (58, 70), (42, 70)], 0)
    g.ell(36, 8, 64, 26); g.circ(50, 17, 5, 0)
    return g


def huang_jin():
    """A golden sun over the plains' horizon."""
    g = G()
    for k in range(12):
        a = math.radians(30 * k)
        g.line([(50 + 26 * math.cos(a), 46 - 26 * math.sin(a)), (50 + 40 * math.cos(a), 46 - 40 * math.sin(a))], 5)
    g.circ(50, 46, 20); g.poly([(4, 82), (96, 82), (96, 90), (4, 90)])
    return g


def zombie_alliance():
    """A skull above sea waves."""
    from .glyphs2 import waves
    g = G(); g.circ(50, 38, 26); g.poly([(36, 54), (64, 54), (60, 70), (40, 70)])
    for x in (40, 60):
        g.circ(x, 38, 7, 0)
    g.poly([(47, 50), (53, 50), (50, 44)], 0)
    waves(g, 50, 84, 40, n=2)
    return g


def fang_clan():
    """A fortress tower on a dune."""
    g = G(); g.ell(4, 70, 96, 110)
    g.poly([(32, 72), (68, 72), (64, 24), (36, 24)])
    for x in (36, 46, 56):
        g.poly([(x, 24), (x + 8, 24), (x + 8, 14), (x, 14)])
    g.poly([(45, 52), (55, 52), (55, 72), (45, 72)], 0)
    return g


def immortal_sect():
    """Crossed swords over a halo: the ancient sects."""
    g = G(); g.arc_band(50, 50, 44, 38, 0, 360)
    g.line([(26, 74), (74, 26)], 6); g.line([(26, 26), (74, 74)], 6)
    g.circ(50, 50, 10)
    return g


def fate_gu():
    """A Gu whose shell is an eye, inside threads of fate."""
    g = G()
    for k in range(6):
        a = math.radians(30 * k)
        g.line([(50 + 46 * math.cos(a), 50 - 46 * math.sin(a)), (50 - 46 * math.cos(a), 50 + 46 * math.sin(a))], 2.5)
    g.circ(50, 50, 30, 0); g.ell(24, 30, 76, 70); g.circ(50, 50, 10, 0); g.circ(50, 50, 5)
    return g


def shattered_fate():
    g = fate_gu(); g.line([(30, 16), (46, 44), (40, 58), (62, 84)], 6, 0); return g


def fate_seized():
    g = fate_gu(); fist(g, 50, 70, 0.6); return g


def immortal_zombie_icon():
    """A stiff figure with arms forward and a dead halo."""
    g = G(); human(g, 50, 18, 1.05, arms="forward")
    g.arc_band(50, 18, 18, 14, 200, 340)
    return g


def heaven_overseeing_tower():
    """A tall tower crowned with an eye."""
    g = G()
    for k, w in enumerate((30, 24, 18, 12)):
        y = 90 - 18 * k
        g.poly([(50 - w, y), (50 + w, y), (50 + w - 4, y - 14), (50 - w + 4, y - 14)])
    g.ell(38, 6, 62, 22); g.circ(50, 14, 4, 0)
    return g

ICONS3 = [
    ("ResourceIcons", "Heaven Qi", heaven_qi, "black"),
    ("ResourceIcons", "Earth Qi", earth_qi, "black"),
    ("ResourceIcons", "Human Qi", human_qi, "black"),
    ("ResourceIcons", "Green Grape Immortal Essence", green_grape_essence, "black"),
    ("TechIcons", "Purple Crystal Essence", purple_crystal_essence, "white"),
    ("TechIcons", "Three Qi", three_qi, "white"),
    ("TechIcons", "Calamity Lore", calamity_lore, "white"),
    ("UnitIcons", "Rank Five Gu Master", rank_five_gu_master, "white"),
    ("UnitIcons", "Rank Six Gu Immortal", rank_six_gu_immortal, "white"),
    ("UnitPromotionIcons", "Ascension", ascension, "white"),
    *[("UnitPromotionIcons", f"{grade} Grade Blessed Land", blessed_land(n), "white")
      for n, grade in enumerate(("Lower", "Middle", "Upper", "Super"), start=1)],
    ("ResourceIcons", "Lifespan Gu", lifespan_gu, "black"),
    ("BuildingIcons", "Formation Ward", formation_ward, "black"),
    ("BuildingIcons", "Stockpile Vault", stockpile_vault, "black"),
    ("UnitPromotionIcons", "Calamity Countdown", calamity_countdown, "white"),
    ("UnitPromotionIcons", "Tribulation Countdown", tribulation_countdown, "white"),
    ("UnitPromotionIcons", "Ravaged Land", ravaged_land, "white"),
    ("BuildingIcons", "Spring Autumn Cicada", spring_autumn_cicada, "black"),
    ("BuildingIcons", "Fixed Immortal Travel", fixed_immortal_travel, "black"),
    ("BuildingIcons", "Man as Before", man_as_before, "black"),
    ("BuildingIcons", "Unravel Mystery", unravel_mystery, "black"),
    ("BuildingIcons", "Connect Luck", connect_luck, "black"),
    ("BuildingIcons", "Self Strength", self_strength, "black"),
    ("BuildingIcons", "Woman's Heart", womans_heart, "black"),
    ("BuildingIcons", "Bone Spike", bone_spike, "black"),
    ("BuildingIcons", "Star Eyes", star_eyes, "black"),
    ("BuildingIcons", "Divert Disaster", divert_disaster, "black"),
    ("TechIcons", "Immortal Gu Recipes", immortal_gu_recipes, "white"),
    ("UnitIcons", "Desolate Beast", desolate_beast_icon, "white"),
    ("ResourceIcons", "Immortal Materials", immortal_materials, "black"),
    ("UnitIcons", "Rank Seven Gu Immortal", rank_immortal(7), "white"),
    ("UnitIcons", "Rank Eight Gu Immortal", rank_immortal(8), "white"),
    ("UnitIcons", "Ancient Desolate Beast", lambda: _beast_pips(2), "white"),
    ("UnitIcons", "Immemorial Desolate Beast", lambda: _beast_pips(3), "white"),
    ("TechIcons", "Red Date Essence", red_date, "white"),
    ("TechIcons", "Rank Seven Immortal Gu Recipes", recipes_rank(7), "white"),
    ("TechIcons", "Grotto-Heaven", grotto_heaven, "white"),
    ("TechIcons", "Rank Eight Immortal Gu Recipes", recipes_rank(8), "white"),
    ("ResourceIcons", "Red Date Immortal Essence", red_date, "black"),
    ("ResourceIcons", "White Lychee Immortal Essence", white_lychee, "black"),
    ("UnitPromotionIcons", "Tribulation Survivor", tribulation_survivor, "white"),
    ("UnitPromotionIcons", "Advancing", advancing, "white"),
    ("UnitPromotionIcons", "Grotto-Heaven Aperture", grotto_heaven, "white"),
    ("UnitPromotionIcons", "Advance to Rank Seven", advance_to(7), "white"),
    ("UnitPromotionIcons", "Advance to Rank Eight", advance_to(8), "white"),
    ("UnitIcons", "Venerable", venerable, "white"),
    ("UnitIcons", "Calamity Luck Altar", calamity_luck_altar, "white"),
    ("UnitIcons", "Myriad Year Flying Warship", flying_warship, "white"),
    ("UnitIcons", "Dragon Palace", dragon_palace, "white"),
    ("BuildingIcons", "Venerable Ascension", venerable_ascension, "black"),
    ("BuildingIcons", "Eternal Life", eternal_life, "black"),
    ("BuildingIcons", "True Inheritance", true_inheritance, "black"),
    ("BuildingIcons", "True Inheritance Seal", true_inheritance_seal, "black"),
    ("TechIcons", "Dao Lord", dao_lord, "white"),
    ("TechIcons", "Gu House Formation", gu_house_formation, "white"),
    ("ResourceIcons", "Yellow Apricot Immortal Essence", yellow_apricot, "black"),
    ("NationIcons", "Heavenly Court", heavenly_court, "white"),
    ("NationIcons", "Huang Jin Family", huang_jin, "white"),
    ("NationIcons", "Zombie Alliance", zombie_alliance, "white"),
    ("NationIcons", "Fang Clan", fang_clan, "white"),
    ("CityStateIcons", "Immortal Sect", immortal_sect, "white"),
    ("BuildingIcons", "Fate Gu", fate_gu, "black"),
    ("BuildingIcons", "Shattered Fate", shattered_fate, "black"),
    ("BuildingIcons", "Fate Seized", fate_seized, "black"),
    ("UnitIcons", "Immortal Zombie", immortal_zombie_icon, "white"),
    ("UnitIcons", "Heaven Overseeing Tower", heaven_overseeing_tower, "white"),
    ("TechIcons", "Rank Nine Immortal Gu Recipes", recipes_rank(9), "white"),
]


def _beast_pips(n):
    g = desolate_beast_icon(); pips(g, n, y=95); return g


def rank78_gu_icons():
    """C5: the rank-seven and rank-eight immortal Gu (data/immortal_gu.csv), one generic design each."""
    import csv
    from common import REPO_ROOT
    with open(REPO_ROOT / "data" / "immortal_gu.csv", newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["rank"] in ("7", "8", "9")]
    return [("BuildingIcons", r["name"], immortal_gu_generic(r["path"], int(r["rank"])), "black") for r in rows]


def inheritance_icons():
    """C4: one stele and one seal per inheritance (data/inheritances.csv)."""
    import csv
    from common import REPO_ROOT
    with open(REPO_ROOT / "data" / "inheritances.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [x for i in rows for x in (
        ("BuildingIcons", i["name"], inheritance(i["path"]), "black"),
        ("BuildingIcons", i["seal"], seal(i["path"]), "black"))]
