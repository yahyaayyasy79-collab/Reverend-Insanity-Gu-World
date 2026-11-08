"""Reference audit Layer 1 (2026-11-08): icons for the small stages, the rank relics and the extreme physique.

Flat white glyphs in the style of glyphs.py; the enamel portraits colour them (inkpass.Palette). Every shape is drawn
from geometric primitives (MOD_SPEC rule 6).
"""
from __future__ import annotations

import math

from .glyphs import G, human


def _aperture(g: G, cx, cy, r, level, v=255):
    """The aperture as a ring holding an essence sea filled to `level` (0..1), a wave on its surface."""
    g.circ(cx, cy, r, v)
    g.circ(cx, cy, r * 0.8, 0 if v else 255)
    top = cy + r * 0.8 - 2 * r * 0.8 * level
    sea = G()
    sea.circ(cx, cy, r * 0.8)
    cut = G()
    pts = [(cx - r, top)] + [(cx - r + i * (2 * r / 16), top + 2.2 * math.sin(i * math.pi / 4)) for i in range(17)]
    cut.poly(pts + [(cx + r, cy - r - 2), (cx - r, cy - r - 2)])
    sea.paste(cut, 0)
    g.paste(sea, v)


def _stage(level, crest=False):
    def draw():
        g = G()
        _aperture(g, 50, 52, 40, level)
        if crest:                                                             # the peak: essence brimming over
            for k in range(5):
                a = math.radians(50 + k * 20)
                g.poly([(50 + 42 * math.cos(a - 0.07), 52 - 42 * math.sin(a - 0.07)),
                        (50 + 52 * math.cos(a), 52 - 52 * math.sin(a)),
                        (50 + 42 * math.cos(a + 0.07), 52 - 42 * math.sin(a + 0.07))])
        return g
    return draw


def stage_cultivation():
    """A cultivator sitting still, qi rising around him."""
    g = G()
    human(g, 50, 30, 0.72)
    for side in (-1, 1):
        g.arc_band(50 + side * 2, 52, 40, 36, 100 if side < 0 else -20, 200 if side < 0 else 80)
    g.circ(50, 10, 4)
    return g


def _relic(pips):
    def draw():
        """A relic Gu: a faceted bead with a halo; one pip for each rank it serves."""
        g = G()
        g.circ(50, 44, 30)
        g.circ(50, 44, 24, 0)
        g.poly([(50, 24), (66, 38), (60, 62), (40, 62), (34, 38)])                # the bead's facets
        g.line([(34, 38), (66, 38)], 2.4, 0)
        g.line([(50, 24), (50, 62)], 2.4, 0)
        for k in range(8):                                                        # halo rays
            a = math.radians(k * 45 + 22.5)
            g.line([(50 + 34 * math.cos(a), 44 - 34 * math.sin(a)), (50 + 42 * math.cos(a), 44 - 42 * math.sin(a))], 3)
        w = 12 * (pips - 1)
        for i in range(pips):
            g.circ(50 - w / 2 + 12 * i, 88, 4.5)
        return g
    return draw


def extreme_physique():
    """An aperture whose essence floods past its wall: a full ring with essence bursting out on every side."""
    g = G()
    g.circ(50, 50, 26)
    for k in range(12):
        a = math.radians(k * 30)
        g.poly([(50 + 24 * math.cos(a - 0.16), 50 - 24 * math.sin(a - 0.16)), (50 + 48 * math.cos(a), 50 - 48 * math.sin(a)),
                (50 + 24 * math.cos(a + 0.16), 50 - 24 * math.sin(a + 0.16))])
    g.circ(50, 50, 14, 0)
    g.circ(50, 50, 7)
    return g


def doomed_aperture():
    """The aperture cracking: a ring split by a jagged fault, shards flying."""
    g = G()
    g.circ(50, 50, 34); g.circ(50, 50, 26, 0)
    g.line([(30, 14), (44, 40), (36, 52), (56, 66), (50, 86)], 6, 0)            # the fault
    for x, y, a in ((80, 22, 30), (86, 70, -20), (16, 74, 200)):
        r = math.radians(a)
        g.poly([(x, y), (x + 9 * math.cos(r + 0.5), y - 9 * math.sin(r + 0.5)), (x + 12 * math.cos(r), y - 12 * math.sin(r))])
    return g


def frenzy_lightning_wolf():
    """Layer 3: the thousand-beast king of the wolf tide: the wolf's head with thunder wings forking up behind it."""
    from .glyphs import lightning_wolf
    g = lightning_wolf(bold=True)
    for x in (14, 26):
        g.bolt([x, x + 8, x + 2, x + 10], 4, 36, 4)
    return g


RELIC_COLOURS = {"Green Copper": (120, 200, 150), "Red Iron": (220, 95, 80), "White Silver": (230, 232, 240),
                 "Yellow Gold": (245, 200, 80), "Purple Crystal": (190, 130, 235)}


def icons():
    out = [("UnitPromotionIcons", "Middle Stage", _stage(0.5), "white"),
           ("UnitPromotionIcons", "Upper Stage", _stage(0.75), "white"),
           ("UnitPromotionIcons", "Peak Stage", _stage(1.0, crest=True), "white"),
           ("UnitPromotionIcons", "Stage Cultivation", stage_cultivation, "white"),
           ("UnitPromotionIcons", "Extreme Physique", extreme_physique, "white"),
           ("UnitPromotionIcons", "Doomed Aperture", doomed_aperture, "white")]
    out += [("UnitPromotionIcons", f"{c} Relic Gu", _relic(i + 1), "white") for i, c in enumerate(RELIC_COLOURS)]
    out.append(("UnitIcons", "Frenzy Lightning Wolf", frenzy_lightning_wolf, "white"))
    return out
