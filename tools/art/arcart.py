"""Immortal arc icons (MOD_SPEC_2 Phase C; the user's D6: every object that shows an image gets a designed one).

C1, ascension: the three qi and green grape essence (black, resources), the techs Purple Crystal Essence, Three Qi and
Calamity Lore (white), the Rank Five Gu Master and the Rank Six Gu Immortal (white, units), the Ascension promotion
and the four blessed-land grades (white, promotions). Every shape is built from primitives; nothing is copied.
"""
from __future__ import annotations

import math

from .glyphs import G, gu_beetle, human, pips
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
]
