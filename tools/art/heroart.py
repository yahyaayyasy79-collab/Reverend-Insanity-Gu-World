"""The heroes' emblems (the user, 2026-11-08; docs/REFERENCE_AUDIT.md, Layer 6).

Each emblem is a symbol of the hero's path and nature built from geometric primitives (MOD_SPEC rule 6): never a
likeness of a character, and nothing taken from the novel's illustrations, manhua or fan art.
"""
from __future__ import annotations

import math

from .glyphs import G, fist
from .glyphs2 import paw, regular


def _star(g: G, cx, cy, r, v=255):
    pts = []
    for k in range(10):
        a = math.radians(90 + k * 36)
        rr = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    g.poly(pts, v)


def fang_zheng():
    """Grade A aptitude in the moon clan: a moon blade cradling a star."""
    g = G()
    g.crescent(50, 54, 40, 18, angle=60)
    _star(g, 62, 40, 16)
    return g


def bai_ning_bing():
    """Northern Dark Ice Soul: a six-armed ice crystal split by a crack."""
    g = G()
    for k in range(6):
        a = math.radians(90 + k * 60)
        x, y = 50 + 42 * math.cos(a), 50 - 42 * math.sin(a)
        g.line([(50, 50), (x, y)], 6)
        bx, by = 50 + 26 * math.cos(a), 50 - 26 * math.sin(a)
        for d in (-0.7, 0.7):
            g.line([(bx, by), (bx + 11 * math.cos(a + d), by - 11 * math.sin(a + d))], 3.6)
    g.poly(regular(50, 50, 13, 6))
    g.line([(40, 30), (52, 46), (46, 56), (60, 72)], 3.4, 0)                   # the crack
    return g


def xiong_lin():
    """Born strength in the bear clan: a bear's paw over three bars of force."""
    g = G()
    paw(g, 50, 46, 1.25)
    for k, y in enumerate((80, 88, 96)):
        g.line([(30 + 6 * k, y), (70 - 6 * k, y)], 4)
    return g


def wu_shuai():
    """The Wu clan's leader: a war banner on a tall pole, wind streaming past it."""
    g = G()
    g.line([(26, 96), (26, 8)], 5)
    g.circ(26, 8, 4.5)
    g.poly([(28, 12), (84, 18), (70, 34), (86, 50), (28, 46)])
    g.poly([(40, 24), (58, 26), (56, 36), (40, 36)], 0)
    for k, y in enumerate((62, 74, 86)):
        g.line([(40 + 6 * k, y), (90 - 4 * k, y - 2)], 3.4)
    return g


def duke_long():
    """The Court's Dragon Duke: a dragon's head in profile, long snout, swept horns, open jaw and a flowing mane."""
    g = G()
    g.poly([(14, 46), (30, 32), (52, 26), (72, 30), (92, 40), (94, 48), (74, 50), (60, 52), (40, 58), (24, 62)])  # skull, snout
    g.poly([(40, 58), (60, 54), (88, 60), (90, 66), (62, 66), (44, 72)])          # the lower jaw, open
    for x in (66, 74, 82):                                                       # teeth
        g.poly([(x, 50), (x + 3, 50), (x + 1.5, 55)])
    g.poly([(30, 32), (10, 10), (20, 12), (40, 28)]); g.poly([(44, 26), (36, 4), (46, 8), (54, 26)])  # horns
    g.circ(58, 38, 4, 0); g.circ(58, 38, 1.6)                                    # eye
    g.line([(90, 44), (99, 30)], 1.8); g.line([(88, 64), (98, 80)], 1.8)         # whiskers
    for k in range(4):                                                           # the mane, flame-like
        x = 14 + k * 8
        g.poly([(x, 62 - k * 2), (x - 10, 80 + k * 3), (x + 8, 70 - k * 2)])
    return g


def hei_lou_lan():
    """Great Strength True Martial: a raised fist with force bursting from it."""
    g = G()
    fist(g, 50, 52, 0.95)
    for k in range(7):
        a = math.radians(30 + k * 20)
        g.poly([(50 + 36 * math.cos(a - 0.08), 46 - 36 * math.sin(a - 0.08)), (50 + 48 * math.cos(a), 46 - 48 * math.sin(a)),
                (50 + 36 * math.cos(a + 0.08), 46 - 36 * math.sin(a + 0.08))])
    return g


def bo_qing():
    """The zombie swordsman: a sword driven into the ground before a round-topped grave stone."""
    g = G()
    g.ell(22, 14, 78, 52); g.poly([(22, 34), (78, 34), (78, 94), (22, 94)])    # the grave stone
    g.ell(30, 22, 70, 50, 0); g.poly([(30, 36), (70, 36), (70, 86), (30, 86)], 0)
    g.line([(14, 96), (86, 96)], 4)                                              # the ground
    g.poly([(56, 10), (64, 10), (64, 66), (60, 74), (56, 66)])                   # the sword, in front, off-centre
    g.poly([(46, 66), (74, 66), (70, 72), (50, 72)])
    g.line([(60, 72), (60, 92)], 6)
    return g


def fang_di_chang():
    """The wisdom elder: an eye within a triangle, rays of thought around it."""
    g = G()
    g.poly([(50, 6), (94, 84), (6, 84)]); g.poly([(50, 20), (82, 76), (18, 76)], 0)
    g.ell(30, 44, 70, 68); g.ell(36, 48, 64, 64, 0); g.circ(50, 56, 7)
    for x in (20, 50, 80):
        g.circ(x, 94, 3.5)
    return g


def fang_yuan_icon():
    """The demon from beyond (the user, 2026-11-09): the Spring Autumn Cicada before a blood moon."""
    g = G()
    g.circ(50, 46, 40); g.circ(50, 46, 34, 0)                                   # the blood moon's rim
    g.ell(42, 26, 58, 74)                                                       # the cicada's body
    g.circ(50, 24, 7)
    for side in (-1, 1):                                                        # its four wings
        g.poly([(50, 36), (50 + side * 34, 22), (50 + side * 30, 44)])
        g.poly([(50, 48), (50 + side * 28, 52), (50 + side * 20, 66)])
    for y in (46, 56, 66):
        g.line([(43, y), (57, y)], 2, 0)
    g.line([(20, 94), (80, 94)], 4)
    return g


HEROES = [("Fang Zheng", fang_zheng), ("Bai Ning Bing", bai_ning_bing), ("Xiong Lin", xiong_lin),
          ("Wu Shuai", wu_shuai), ("Duke Long", duke_long), ("Hei Lou Lan", hei_lou_lan), ("Bo Qing", bo_qing),
          ("Fang Di Chang", fang_di_chang)]
HERO_NATION = {"Fang Zheng": "Gu Yue Clan", "Bai Ning Bing": "Bai Clan", "Xiong Lin": "Xiong Clan", "Wu Shuai": "Wu Clan",
               "Duke Long": "Heavenly Court", "Hei Lou Lan": "Huang Jin Family", "Bo Qing": "Zombie Alliance",
               "Fang Di Chang": "Fang Clan"}


def icons():
    return [("UnitPromotionIcons", n, f, "white") for n, f in HEROES] + [("UnitIcons", "Fang Yuan", fang_yuan_icon, "white")]
