"""Secret realms (MOD_SPEC_2 #13): the icon of the blessing each realm grants. The realms' map tiles are drawn by
tools/art/pixeltiles.py. Nothing is traced or copied."""
from __future__ import annotations

from .glyphs import G, human


def promotion_icon(name: str) -> G:
    """The realm's blessing: a hex outline around a small figure."""
    g = G()
    pts = [(25, 8), (75, 8), (98, 50), (75, 92), (25, 92), (2, 50)]
    g.poly(pts)
    g.poly([(x * 0.8 + 10, y * 0.8 + 10) for x, y in pts], 0)
    human(g, 50, 22, 0.85, arms="raised")
    return g
