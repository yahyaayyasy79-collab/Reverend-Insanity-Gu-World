"""The mod's characters as 3D scenes for tools/art/render3d.py: Gu Masters by path and rank, mortals, lightning wolves,
and the Gu attack effects. Rank shows as essence colour (canon: rank one green copper, two red iron, three white
silver, four yellow gold), build and ornaments. Every part is a primitive; nothing is traced or copied."""
from __future__ import annotations

import math

from .render3d import Scene

ESSENCE = {1: "essence1", 2: "essence2", 3: "essence3", 4: "essence4", 5: "essence5", 6: "essence6", 7: "essence7",
           8: "essence8", 9: "essence9"}


def _arm(s: Scene, side, shoulder, elbow, hand, r_upper=0.075, r_fore=0.065, sleeve=None, hand_r=0.07):
    if sleeve:  # wide cultivator sleeve
        s.add("cone", shoulder, elbow, 0.10, sleeve, mat="robe", blend=0.03)
        s.add("cone", elbow, hand, sleeve, sleeve * 1.15, mat="robe", blend=0.02)
    else:
        s.add("capsule", shoulder, elbow, r_upper, mat="skin", blend=0.03)
        s.add("capsule", elbow, hand, r_fore, mat="skin", blend=0.02)
    s.add("sphere", hand, hand_r, mat="skin", blend=0.02)


def cultivator(s: Scene, x=0.0, height=1.0, build=1.0, robe=True, bun=True, pose="ready", sash=True, young=False):
    """A standing figure facing +z. pose: ready (hands low), cast (right hand forward), fists (both fists up)."""
    h = height
    head_y = 1.72 * h
    s.add("sphere", (x, head_y, 0.0), 0.15 * h, mat="skin")                               # head
    for side in (-1, 1):
        s.add("sphere", (x + side * 0.055 * h, head_y + 0.01 * h, 0.135 * h), 0.02 * h, mat="hair")   # eyes
    s.add("ellipsoid", (x, head_y + 0.05 * h, -0.03), (0.158 * h, 0.13 * h, 0.16 * h), mat="hair", blend=0.02)  # hair cap
    if bun:
        s.add("sphere", (x, head_y + 0.19 * h, -0.07), 0.07 * h, mat="hair", blend=0.02)  # topknot
    s.add("capsule", (x, 1.48 * h, 0), (x, 1.58 * h, 0), 0.055 * h, mat="skin")          # neck
    sh = 0.21 * h * build
    if robe:
        s.add("cone", (x, 1.45 * h, 0), (x, 0.95 * h, 0), 0.20 * h * build, 0.17 * h * build, mat="robe", blend=0.04)   # chest
        s.add("cone", (x, 0.95 * h, 0), (x, 0.02, 0), 0.17 * h * build, 0.36 * h * build, mat="robe", blend=0.04)       # skirt
        if sash:
            s.add("torus", (x, 0.98 * h, 0), 0.175 * h * build, 0.035 * h, mat="trim")
        s.add("box", (x, 1.32 * h, 0.17 * h * build), (0.03, 0.12 * h, 0.012), mat="trim")   # collar line
    else:   # bare-chested strength cultivator with trousers
        s.add("ellipsoid", (x, 1.25 * h, 0), (0.26 * h * build, 0.26 * h, 0.17 * h * build), mat="skin", blend=0.05)
        s.add("ellipsoid", (x, 0.98 * h, 0), (0.2 * h * build, 0.14 * h, 0.14 * h * build), mat="skin", blend=0.05)
        s.add("torus", (x, 0.9 * h, 0), 0.19 * h * build, 0.045 * h, mat="trim")
        for side in (-1, 1):
            s.add("cone", (x + side * 0.1 * h * build, 0.86 * h, 0), (x + side * 0.15 * h * build, 0.08, 0.02),
                  0.11 * h * build, 0.09 * h, mat="robe", blend=0.03)
            s.add("ellipsoid", (x + side * 0.15 * h * build, 0.05, 0.06), (0.08, 0.05, 0.12), mat="leather")
    sy = 1.42 * h
    for side in (-1, 1):
        shoulder = (x + side * sh, sy, 0.0)
        if pose == "fists":
            elbow = (x + side * (sh + 0.16 * h * build), sy - 0.18 * h, 0.08)
            hand = (x + side * (sh + 0.1 * h * build), sy + 0.1 * h, 0.2)
        elif pose == "cast" and side == 1:
            elbow = (x + sh + 0.1 * h, sy - 0.12 * h, 0.18)
            hand = (x + sh + 0.16 * h, sy - 0.08 * h, 0.42 * h)
        else:
            elbow = (x + side * (sh + 0.06 * h), sy - 0.3 * h, 0.02)
            hand = (x + side * (sh + 0.04 * h), sy - 0.58 * h, 0.08)
        if robe:
            _arm(s, side, shoulder, elbow, hand, sleeve=0.10 * h, hand_r=0.065 * h)
        else:
            r = 0.085 * h * build
            _arm(s, side, shoulder, elbow, hand, r_upper=r, r_fore=r * 0.9, hand_r=r * 1.05)
    return s


def gu_master(rank: int, path: str | None):
    s = Scene()
    if path == "Strength":
        build = {2: 1.15, 3: 1.28, 4: 1.4}[rank]
        cultivator(s, height=1.0 + 0.03 * rank, build=build, robe=False, bun=True, pose="fists")
        # boar-tusk necklace; bracers from rank 3; boar-skull pauldrons at rank 4
        for side in (-1, 1):
            s.add("cone", (0.06 * side, 1.38, 0.2), (0.13 * side, 1.27, 0.24), 0.025, 0.008, mat="bone")
        if rank >= 3:
            for side in (-1, 1):
                s.add("capsule", (side * 0.38, 1.28, 0.12), (side * 0.36, 1.42, 0.17), 0.075, mat="metal")
        if rank >= 4:
            for side in (-1, 1):
                s.add("ellipsoid", (side * 0.33, 1.5, 0.0), (0.13, 0.08, 0.12), mat="bone", blend=0.02)
                s.add("cone", (side * 0.4, 1.5, 0.08), (side * 0.5, 1.62, 0.12), 0.03, 0.006, mat="bone")
        s.add("torus", (0, 0.02, 0), 0.42 + 0.04 * rank, 0.018, mat=ESSENCE[rank])                # essence ring
    elif path == "Moon":
        cultivator(s, height=1.0, build=0.95, robe=True, bun=True, pose="cast")
        # moon blades orbit the master: one at rank two, two at rank three, three at rank four
        orbit = [((0.55, 1.3, 0.42), 0.6, 0.3), ((-0.6, 1.2, 0.25), -0.7, -0.2), ((0.0, 2.3, 0.15), 0.0, 0.2)]
        for (c, ang, tilt) in orbit[:{2: 1, 3: 2, 4: 3}[rank]]:
            s.add("crescent", c, 0.2 + 0.03 * rank, 0.02, 0.09, ang, tilt, mat="moon")
        if rank >= 4:
            s.add("crescent", (0.0, 1.75, -0.32), 0.42, 0.015, 0.16, 0.0, 0.0, mat="moon")          # moon behind the back
        s.add("torus", (0, 0.02, 0), 0.42 + 0.04 * rank, 0.018, mat=ESSENCE[rank])
    elif path == "Water":
        # the Bai clan (water path, Stream Gu): water ribbons circle the master, one more per rank
        cultivator(s, height=1.0, build=0.95, robe=True, bun=True, pose="cast")
        for k in range(rank - 1):
            s.add("torus", (0, 0.7 + 0.45 * k, 0), 0.42 + 0.05 * k, 0.03, mat="water")
        s.add("sphere", (0.36, 1.45, 0.5), 0.08 + 0.02 * rank, mat="water")
        s.add("torus", (0, 0.02, 0), 0.42 + 0.04 * rank, 0.018, mat=ESSENCE[rank])
    elif path == "Wind":
        # the Wu clan (D3: its strongest tradition is the wind path, R V6c130): gust rings spiral up the robe, one
        # more per rank, and a whirl over the palm
        cultivator(s, height=1.0, build=1.0, robe=True, bun=True, pose="cast")
        for k in range(rank):
            s.add("torus", (0.05 * (k % 2 * 2 - 1), 0.25 + 0.24 * k, 0), 0.64 + 0.04 * k, 0.014, mat="wind")
        for k in range(3):
            s.add("torus", (0.36, 1.32 + 0.1 * k, 0.5), 0.07 + 0.04 * k + 0.01 * rank, 0.015, mat="wind")
        s.add("torus", (0, 0.02, 0), 0.42 + 0.04 * rank, 0.018, mat=ESSENCE[rank])
    elif rank > 1:   # any other path (C3: the path is a promotion): a grown cultivator with an orb of his rank's essence
        cultivator(s, height=1.0, build=1.0, robe=True, bun=True, pose="cast")
        s.add("sphere", (0.36, 1.45, 0.5), 0.08 + 0.02 * rank, mat=ESSENCE[rank])
        s.add("torus", (0, 0.02, 0), 0.42 + 0.04 * rank, 0.018, mat=ESSENCE[rank])
    else:   # rank one, unpathed: a youth with a green-copper essence orb over the palm
        cultivator(s, height=0.94, build=0.9, robe=True, bun=True, pose="cast", young=True)
        s.add("sphere", (0.36, 1.45, 0.5), 0.09, mat="essence1")
        s.add("torus", (0, 0.02, 0), 0.42, 0.016, mat="essence1")
    return s


def lone_gu_master():
    """Phase D: a lone Gu Master (散修) on the road: a wide straw hat, a staff, a gourd at the hip, a red-iron orb."""
    s = Scene()
    cultivator(s, height=1.0, build=0.95, robe=True, bun=False, pose="cast")
    s.add("ellipsoid", (0, 1.86, 0.0), (0.36, 0.035, 0.36), mat="straw")                       # straw hat brim
    s.add("cone", (0, 1.86, 0.0), (0, 2.02, 0.0), 0.16, 0.02, mat="straw", blend=0.02)           # and crown
    s.add("capsule", (-0.42, 0.02, 0.12), (-0.38, 1.7, 0.16), 0.03, mat="wood")               # staff
    s.add("sphere", (0.26, 0.86, 0.12), 0.08, mat="leather")                                   # gourd
    s.add("sphere", (0.26, 0.98, 0.12), 0.055, mat="leather", blend=0.02)
    s.add("sphere", (0.36, 1.45, 0.5), 0.1, mat=ESSENCE[2])
    s.add("torus", (0, 0.02, 0), 0.5, 0.018, mat=ESSENCE[2])
    return s


def demonic_gu_master(rank=3):
    """Phase D: a demonic-path Gu Master (魔道蛊师): a hooded robe, bone horns, an ember orb and, for an elder, a blood
    halo and a skull staff."""
    s = Scene()
    cultivator(s, height=1.0 + 0.03 * (rank - 3), build=1.0 + 0.06 * (rank - 3), robe=True, bun=False, pose="cast")
    s.add("ellipsoid", (0, 1.76, -0.04), (0.2, 0.2, 0.2), mat="hide_dark", blend=0.03)        # hood
    for side in (-1, 1):                                                                       # bone horns
        s.add("cone", (0.1 * side, 1.9, 0.0), (0.2 * side, 2.12, -0.06), 0.035, 0.008, mat="bone")
    s.add("sphere", (0.36, 1.45, 0.5), 0.1 + 0.02 * (rank - 3), mat="ember")
    s.add("torus", (0, 0.02, 0), 0.46 + 0.04 * rank, 0.02, mat=ESSENCE[7])                   # a blood-red ring
    if rank >= 5:
        s.add("torus", (0, 1.95, -0.1), 0.24, 0.02, mat=ESSENCE[7])                          # blood halo
        s.add("capsule", (-0.42, 0.02, 0.12), (-0.38, 1.85, 0.16), 0.035, mat="wood")         # staff
        s.add("sphere", (-0.38, 1.92, 0.16), 0.08, mat="bone")                                # skull
    return s


def clan_settler():
    s = Scene()
    cultivator(s, height=1.0, build=1.0, robe=True, bun=True, pose="ready", sash=True)
    s.add("ellipsoid", (0.0, 1.15, -0.32), (0.22, 0.26, 0.16), mat="cloth", blend=0.02)          # bundle on the back
    s.add("capsule", (-0.42, 0.0, 0.1), (-0.42, 2.25, 0.1), 0.025, mat="wood")                    # banner pole
    s.add("box", (-0.25, 2.0, 0.1), (0.17, 0.2, 0.012), mat="trim")                               # clan banner
    return s


def mortal_laborer():
    s = Scene()
    cultivator(s, height=0.95, build=1.0, robe=True, bun=False, pose="ready", sash=False)
    s.add("cone", (0, 1.83, 0), (0, 2.02, 0), 0.32, 0.02, mat="straw")                            # straw hat
    s.add("capsule", (0.45, 0.1, 0.25), (-0.1, 1.75, -0.15), 0.025, mat="wood")                   # hoe handle
    s.add("box", (-0.13, 1.8, -0.12), (0.12, 0.03, 0.06), mat="metal")
    return s


def wolf(size=1.0, mane=False, crown=False):
    """A lightning wolf, three-quarter view: deep chest, lowered head, bent legs, bushy tail."""
    s = Scene()
    k = size
    s.add("ellipsoid", (0, 0.55 * k, -0.12 * k), (0.22 * k, 0.21 * k, 0.5 * k), mat="fur")                 # body
    s.add("ellipsoid", (0, 0.62 * k, 0.28 * k), (0.25 * k, 0.27 * k, 0.26 * k), mat="fur", blend=0.1 * k)   # chest
    s.add("sphere", (0, 0.8 * k, 0.56 * k), 0.15 * k, mat="fur", blend=0.07 * k)                           # head
    s.add("cone", (0, 0.77 * k, 0.64 * k), (0, 0.7 * k, 0.92 * k), 0.095 * k, 0.045 * k, mat="fur_dark", blend=0.04 * k)  # snout
    s.add("sphere", (0, 0.71 * k, 0.93 * k), 0.035 * k, mat="hair")                                         # nose
    for side in (-1, 1):
        s.add("cone", (side * 0.08 * k, 0.9 * k, 0.5 * k), (side * 0.13 * k, 1.1 * k, 0.46 * k), 0.065 * k, 0.012, mat="fur_dark")
        s.add("sphere", (side * 0.075 * k, 0.84 * k, 0.68 * k), 0.024 * k, mat="eye")
        for z, back in ((0.32, False), (-0.48, True)):                                                       # bent legs
            top = (side * 0.13 * k, 0.5 * k, z * k)
            knee = (side * 0.14 * k, 0.26 * k, (z + (-0.1 if back else 0.06)) * k)
            paw = (side * 0.14 * k, 0.04, (z + 0.05) * k)
            s.add("capsule", top, knee, 0.075 * k, mat="fur_dark", blend=0.04 * k)
            s.add("capsule", knee, paw, 0.055 * k, mat="fur_dark", blend=0.02 * k)
            s.add("ellipsoid", (paw[0], 0.04, paw[2] + 0.03 * k), (0.06 * k, 0.04 * k, 0.08 * k), mat="fur_dark", blend=0.02)
    s.add("cone", (0, 0.6 * k, -0.6 * k), (0, 0.42 * k, -1.05 * k), 0.09 * k, 0.05 * k, mat="fur", blend=0.05 * k)   # tail
    for i in range(3 if mane else 2):                                                                        # lightning on the spine
        z = 0.1 - 0.3 * i
        s.add("cone", (0, 0.74 * k, z * k), (0.04, 0.98 * k, (z - 0.1) * k), 0.035 * k, 0.005, mat="volt")
    if mane:
        s.add("ellipsoid", (0, 0.78 * k, 0.3 * k), (0.3 * k, 0.25 * k, 0.2 * k), mat="fur_dark", blend=0.06 * k)
    if crown:
        for a in (-50, -25, 0, 25, 50):
            ar = math.radians(a)
            s.add("cone", (0.11 * math.sin(ar) * k, 0.94 * k, 0.53 * k), (0.19 * math.sin(ar) * k, 1.24 * k, 0.5 * k),
                  0.03 * k, 0.004, mat="volt_gold")
    return s


# ---------------------------------------------------------------- attack effects (rendered as 3D frames)
def moon_blade_frame(i, rank):
    s = Scene()
    n = {1: 1, 2: 1, 3: 2, 4: 3}[rank]
    for b in range(n):
        x = -0.9 + 0.55 * i - 0.25 * b
        s.add("crescent", (x, 1.0 + 0.18 * b, 0.0), 0.32 + 0.04 * rank, 0.03, 0.14, 0.2, 0.5, mat="moon")
    return s


def boar_charge_frame(i, rank):
    s = Scene()
    k = 0.6 + 0.1 * rank
    if i < 2:   # a phantom boar head charges in
        z = -0.6 + 0.6 * i
        s.add("sphere", (0, 0.8, z), 0.3 * k, mat=ESSENCE[rank])
        s.add("cone", (0, 0.75, z + 0.2 * k), (0, 0.7, z + 0.55 * k), 0.2 * k, 0.12 * k, mat=ESSENCE[rank], blend=0.05)
        for side in (-1, 1):
            s.add("cone", (side * 0.15 * k, 0.62, z + 0.45 * k), (side * 0.28 * k, 0.95, z + 0.6 * k), 0.05 * k, 0.005, mat="bone")
    else:       # shock rings on impact
        r = 0.4 + 0.35 * (i - 1)
        s.add("torus", (0, 0.3, 0), r * k, 0.05, mat=ESSENCE[rank])
        s.add("torus", (0, 0.32, 0), r * k * 0.7, 0.035, mat="earth")
    return s


def lightning_frame(i, crown=False):
    s = Scene()
    mat = "volt_gold" if crown else "volt"
    pts = [(0.1, 2.4, 0), (-0.15, 1.8, 0.05), (0.15, 1.3, 0), (-0.1, 0.8, 0.05), (0.05, 0.3, 0)]
    upto = min(len(pts) - 1, 1 + 2 * i)
    for a, b in zip(pts[:upto], pts[1:upto + 1]):
        s.add("capsule", a, b, 0.05 if i < 2 else 0.07, mat=mat)
    if i >= 2:
        s.add("sphere", (0, 0.5, 0), 0.3 + 0.1 * (i - 2), mat=mat)
    return s


def water_frame(i, rank):
    """A wave of water rolls in and breaks over the target."""
    s = Scene()
    k = 0.6 + 0.1 * rank
    if i < 2:
        z = -0.7 + 0.6 * i
        s.add("ellipsoid", (0, 0.5, z), (0.6 * k, 0.35 * k, 0.2 * k), mat="water")
        s.add("crescent", (0, 0.85, z + 0.1), 0.35 * k, 0.04, 0.15, 0.0, 1.2, mat="water")
    else:
        r = 0.35 + 0.3 * (i - 1)
        s.add("torus", (0, 0.25, 0), r * k, 0.05, mat="water")
        s.add("sphere", (0, 0.6, 0), 0.12 * (i - 1), mat="water")
    return s


def wind_frame(i, rank):
    """A whirlwind sweeps over the target and tears outward."""
    s = Scene()
    k = 0.6 + 0.1 * rank
    if i < 3:
        sway = (-0.4, 0.0, 0.3)[i]
        for h in range(5):
            s.add("torus", (sway + 0.08 * h * (1 if i % 2 else -1), 0.1 + 0.42 * h, 0), (0.22 + 0.14 * h) * k, 0.04,
                  mat="wind")
    else:
        for r in (0.5, 0.8):
            s.add("torus", (0, 0.3, 0), r * k, 0.04, mat="wind")
    return s


def desolate_beast(k=1.35, hide="hide", dark="hide_dark"):
    """MOD_SPEC_2 C4: a desolate beast (荒兽): a hill-shouldered horned brute, dark hide, ember eyes, bone plates (C5: the
    ancient one larger and red, the immemorial one larger still and pale)."""
    s = Scene()
    s.add("ellipsoid", (0, 0.62 * k, -0.1 * k), (0.32 * k, 0.3 * k, 0.55 * k), mat=hide)                      # body
    s.add("ellipsoid", (0, 0.72 * k, 0.32 * k), (0.34 * k, 0.34 * k, 0.3 * k), mat=hide, blend=0.12 * k)      # hump
    s.add("sphere", (0, 0.72 * k, 0.66 * k), 0.19 * k, mat=hide, blend=0.08 * k)                              # head
    s.add("cone", (0, 0.66 * k, 0.76 * k), (0, 0.6 * k, 0.98 * k), 0.12 * k, 0.07 * k, mat=dark, blend=0.04 * k)
    for side in (-1, 1):
        s.add("cone", (side * 0.12 * k, 0.84 * k, 0.6 * k), (side * 0.42 * k, 1.12 * k, 0.5 * k), 0.06 * k, 0.012, mat="bone")  # horns
        s.add("sphere", (side * 0.09 * k, 0.78 * k, 0.8 * k), 0.03 * k, mat="ember")
        for z in (0.3, -0.45):
            top = (side * 0.2 * k, 0.55 * k, z * k)
            paw = (side * 0.22 * k, 0.05, (z + 0.04) * k)
            s.add("capsule", top, paw, 0.1 * k, mat=dark, blend=0.05 * k)
    for i in range(4):                                                                                           # spine plates
        z = 0.35 - 0.25 * i
        s.add("cone", (0, 0.92 * k, z * k), (0, 1.15 * k, (z - 0.08) * k), 0.07 * k, 0.01, mat="bone")
    s.add("cone", (0, 0.62 * k, -0.62 * k), (0, 0.4 * k, -1.0 * k), 0.12 * k, 0.04 * k, mat=hide, blend=0.05 * k)
    return s


def gu_immortal(rank=6):
    """MOD_SPEC_2 C1: a Gu Immortal standing on a cloud, a halo of its rank's essence over the head and an essence orb
    over the palm (rank six green grape; C5: rank seven red date, rank eight white lychee with a second halo)."""
    mat = ESSENCE[rank]
    s = Scene()
    cultivator(s, height=1.04, build=1.0, robe=True, bun=True, pose="cast")
    for x, y, z, r in ((-0.55, 0.08, 0.15, 0.24), (-0.22, 0.12, 0.3, 0.3), (0.18, 0.1, 0.32, 0.3), (0.55, 0.06, 0.12, 0.24),
                       (0.0, 0.05, -0.25, 0.32)):
        s.add("sphere", (x, y, z), r, mat="cloud", blend=0.1)
    s.add("torus", (0, 2.02, -0.05), 0.2, 0.022, mat=mat)
    if rank >= 8:
        s.add("torus", (0, 2.12, -0.05), 0.27, 0.018, mat=mat)
    if rank >= 9:   # the Venerable: a third, wide halo and a sun disc behind the back
        s.add("torus", (0, 2.22, -0.05), 0.34, 0.016, mat=mat)
        s.add("ellipsoid", (0, 1.85, -0.7), (0.38, 0.38, 0.02), mat=mat)
    s.add("sphere", (0.36, 1.45, 0.5), 0.13 + 0.01 * (rank - 6), mat=mat)
    return s


def gu_house(kind: str):
    """MOD_SPEC_2 C5b: Gu Houses, formation-path fortresses (R V4/356): a tiered luck altar, a flying warship over
    clouds, a dragon palace pagoda. Civ colour on the walls and sails."""
    s = Scene()
    if kind == "altar":
        for k, (w, h) in enumerate(((0.9, 0.18), (0.68, 0.18), (0.46, 0.18))):
            s.add("box", (0, 0.09 + 0.2 * k, 0), (w / 2, h / 2, w / 2), mat="robe" if k == 1 else "metal")
        for x in (-0.38, 0.38):
            for z in (-0.38, 0.38):
                s.add("capsule", (x, 0.1, z), (x, 0.95, z), 0.04, mat="jade")
        s.add("sphere", (0, 0.92, 0), 0.18, mat="essence9")
    elif kind == "warship":
        s.add("ellipsoid", (0, 0.55, 0), (0.36, 0.2, 1.0), mat="wood")
        s.add("box", (0, 0.7, -0.1), (0.2, 0.08, 0.4), mat="trim")
        s.add("capsule", (0, 0.7, 0.1), (0, 1.5, 0.1), 0.03, mat="wood")
        s.add("box", (0, 1.15, 0.12), (0.32, 0.3, 0.015), mat="sail")
        for x, z, r in ((-0.3, 0.3, 0.24), (0.25, -0.2, 0.26), (0.0, 0.5, 0.2), (0.1, -0.6, 0.22)):
            s.add("sphere", (x, 0.2, z), r, mat="cloud", blend=0.1)
    else:   # palace
        for k, w in enumerate((0.55, 0.42, 0.3)):
            y = 0.22 + 0.46 * k
            s.add("box", (0, y, 0), (w * 0.75, 0.14, w * 0.75), mat="robe")
            s.add("ellipsoid", (0, y + 0.18, 0), (w * 1.15, 0.06, w * 1.15), mat="roof")      # flat eaves (a round
            s.add("ellipsoid", (0, y + 0.23, 0), (w * 0.7, 0.05, w * 0.7), mat="roof")        # cone would be a ball)
        s.add("capsule", (0, 1.3, 0), (0, 1.55, 0), 0.03, mat="metal")
        s.add("sphere", (0, 1.6, 0), 0.08, mat="essence8")
        s.add("box", (0, 0.04, 0), (0.6, 0.04, 0.6), mat="metal")
    return s


def immortal_zombie():
    """C5c: an immortal zombie: a grey stiff figure, arms forward, a broken dull halo."""
    s = Scene()
    cultivator(s, height=1.0, build=0.95, robe=True, bun=True, pose="cast")
    s.add("torus", (0, 2.0, -0.05), 0.2, 0.02, mat="hide_pale")
    s.add("sphere", (0.36, 1.45, 0.5), 0.1, mat="hide_dark")
    return s


def overseeing_tower():
    """C5c: the Heaven Overseeing Tower: a tall tiered tower with an eye of fate on top."""
    s = Scene()
    for k, w in enumerate((0.42, 0.34, 0.26, 0.18)):
        y = 0.16 + 0.34 * k
        s.add("box", (0, y, 0), (w, 0.14, w), mat="robe")
        s.add("ellipsoid", (0, y + 0.16, 0), (w * 1.25, 0.04, w * 1.25), mat="roof")
    s.add("ellipsoid", (0, 1.62, 0), (0.18, 0.12, 0.08), mat="essence9")
    return s


def essence_frame(i, rank=1):
    s = Scene()
    s.add("sphere", (0, 0.9, 0), 0.12 + 0.12 * i, mat=ESSENCE[rank])
    return s


# Phase D (the user, 2026-11-02: "efek serangan ... dengan tingkatan yang jelas dan sesuai scaling"): the strike grows
# with the attacker's rank, in its essence colour. Rank 1-2: a burst and sparks; 3-4: a shock ring; 5: two rings; 6
# (immortal): a qi pillar rises; 7: rays tear outward; 8 (grotto-heaven): a halo opens above; 9 (Venerable): four
# rings, a crown of light and a ground shockwave. Higher ranks also play more frames.
STRIKE_FRAMES = {1: 3, 2: 3, 3: 4, 4: 4, 5: 4, 6: 5, 7: 5, 8: 5, 9: 6}
STRIKE_RINGS = {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 4}


def strike_frame(i, rank=1):
    n = STRIKE_FRAMES[rank]
    p = i / (n - 1)
    mat = ESSENCE[rank]
    s = Scene()
    core = (0.2 + 0.05 * rank) * (0.3 + 0.7 * math.sin(math.pi * min(1.0, p * 1.1)))   # peak 0.25 (rank 1) .. 0.65 (9)
    s.add("sphere", (0, 0.9, 0), core, mat=mat)
    motes = min(2 + rank, 11)
    spread = 0.18 + 0.6 * p * (1 + 0.08 * rank)
    for k in range(motes):
        a = 2 * math.pi * k / motes + 0.4 * rank
        s.add("sphere", (spread * math.cos(a), 0.9 + 0.12 * math.sin(3 * a), spread * math.sin(a)),
              (0.055 + 0.003 * rank) * (1 - 0.35 * p), mat=mat)
    for j in range(STRIKE_RINGS[rank]):
        big = p * (0.55 + 0.13 * rank) - 0.16 * j
        if big > 0.06:
            s.add("torus", (0, 0.9 - 0.18 * j * p, 0), big, 0.02 + 0.004 * rank, mat=mat)
    if rank >= 6 and p > 0:     # the aperture's qi rises as a pillar
        s.add("capsule", (0, 0.0, 0), (0, 1.1 + 1.1 * p, 0), (0.05 + 0.012 * (rank - 5)) * (1 - 0.4 * p), mat=mat)
    if rank >= 7 and 0 < p < 1:  # rays tear outward
        for k in range(6):
            a = math.pi * k / 3
            r0, r1 = 0.2, 0.35 + 0.95 * p
            s.add("capsule", (r0 * math.cos(a), 0.95, r0 * math.sin(a)), (r1 * math.cos(a), 1.0 + 0.35 * p, r1 * math.sin(a)),
                  0.045, mat=mat)
    if rank >= 8 and p > 0.2:    # a grotto-heaven: a halo opens above the strike
        s.add("torus", (0, 1.7 + 0.2 * p, 0), 0.25 + 0.35 * p, 0.03, mat=mat)
    if rank >= 9:                # the Venerable: a crown of light and a ground shockwave
        for k in range(8):
            a = 2 * math.pi * k / 8
            s.add("sphere", ((0.4 + 0.3 * p) * math.cos(a), 2.0, (0.4 + 0.3 * p) * math.sin(a)), 0.05, mat=mat)
        if p >= 0.6:
            s.add("torus", (0, 0.1, 0), 0.6 + 1.1 * p, 0.05, mat=mat)
    return s


UNITS = {
    "Clan Settler": clan_settler,
    "Mortal Laborer": mortal_laborer,
    "Rank One Gu Master": lambda: gu_master(1, None),
    "Rank Two Strength Gu Master": lambda: gu_master(2, "Strength"),
    "Rank Three Strength Gu Master": lambda: gu_master(3, "Strength"),
    "Rank Four Strength Gu Master": lambda: gu_master(4, "Strength"),
    "Rank Two Moon Gu Master": lambda: gu_master(2, "Moon"),
    "Rank Three Moon Gu Master": lambda: gu_master(3, "Moon"),
    "Rank Four Moon Gu Master": lambda: gu_master(4, "Moon"),
    # C3: the rank chain, and the signature clans' own chains (their path's look; the user's choice A.b)
    **{f"Rank {w} Gu Master": (lambda r=r: gu_master(r, None)) for w, r in (("Two", 2), ("Three", 3), ("Four", 4), ("Five", 5))},
    "Rank Six Gu Immortal": gu_immortal,
    **{f"Rank {w} {clan} Gu Master": (lambda r=r, pth=pth: gu_master(r, pth))
       for clan, pth in (("Gu Yue", "Moon"), ("Bai", "Water"), ("Xiong", "Strength"), ("Wu", "Wind"))
       for w, r in (("Two", 2), ("Three", 3), ("Four", 4))},
    "Lightning Wolf": lambda: wolf(0.85),
    "Bold Lightning Wolf": lambda: wolf(1.05, mane=True),
    "Thunder Crown Wolf": lambda: wolf(1.25, mane=True, crown=True),
    "Desolate Beast": desolate_beast,
    "Ancient Desolate Beast": lambda: desolate_beast(1.5, "hide_red", "hide_dark"),
    "Immemorial Desolate Beast": lambda: desolate_beast(1.65, "hide_pale", "hide_red"),
    "Rank Seven Gu Immortal": lambda: gu_immortal(7),
    "Rank Eight Gu Immortal": lambda: gu_immortal(8),
    "Venerable": lambda: gu_immortal(9),
    "Lone Gu Master": lone_gu_master,
    "Demonic Gu Master": lambda: demonic_gu_master(3),
    "Demonic Elder": lambda: demonic_gu_master(5),
    "Calamity Luck Altar": lambda: gu_house("altar"),
    "Myriad Year Flying Warship": lambda: gu_house("warship"),
    "Dragon Palace": lambda: gu_house("palace"),
    "Immortal Zombie": immortal_zombie,
    "Heaven Overseeing Tower": overseeing_tower,
}

# attack frames per unit name (Unciv plays them over the unit that takes damage)
ATTACKS = {
    "Rank One Gu Master": [lambda i=i: strike_frame(i, 1) for i in range(STRIKE_FRAMES[1])],
    **{f"Rank {w} Moon Gu Master": [lambda i=i, r=r: moon_blade_frame(i, r) for i in range(4)]
       for w, r in (("Two", 2), ("Three", 3), ("Four", 4))},
    **{f"Rank {w} Strength Gu Master": [lambda i=i, r=r: boar_charge_frame(i, r) for i in range(4)]
       for w, r in (("Two", 2), ("Three", 3), ("Four", 4))},
    **{f"Rank {w} Gu Master": [lambda i=i, r=r: strike_frame(i, r) for i in range(STRIKE_FRAMES[r])]
       for w, r in (("Two", 2), ("Three", 3), ("Four", 4), ("Five", 5))},
    "Rank Six Gu Immortal": [lambda i=i: strike_frame(i, 6) for i in range(STRIKE_FRAMES[6])],
    **{f"Rank {w} {clan} Gu Master": [lambda i=i, r=r, f=f: f(i, r) for i in range(4)]
       for clan, f in (("Gu Yue", moon_blade_frame), ("Bai", water_frame), ("Xiong", boar_charge_frame),
                       ("Wu", wind_frame))
       for w, r in (("Two", 2), ("Three", 3), ("Four", 4))},
    "Lightning Wolf": [lambda i=i: lightning_frame(i) for i in range(4)],
    "Bold Lightning Wolf": [lambda i=i: lightning_frame(i) for i in range(4)],
    "Thunder Crown Wolf": [lambda i=i: lightning_frame(i, crown=True) for i in range(4)],
    "Desolate Beast": [lambda i=i: strike_frame(i, 5) for i in range(STRIKE_FRAMES[5])],
    "Ancient Desolate Beast": [lambda i=i: strike_frame(i, 7) for i in range(STRIKE_FRAMES[7])],
    "Immemorial Desolate Beast": [lambda i=i: strike_frame(i, 8) for i in range(STRIKE_FRAMES[8])],
    "Rank Seven Gu Immortal": [lambda i=i: strike_frame(i, 7) for i in range(STRIKE_FRAMES[7])],
    "Rank Eight Gu Immortal": [lambda i=i: strike_frame(i, 8) for i in range(STRIKE_FRAMES[8])],
    "Venerable": [lambda i=i: strike_frame(i, 9) for i in range(STRIKE_FRAMES[9])],
    **{n: [lambda i=i: strike_frame(i, 8) for i in range(STRIKE_FRAMES[8])]
       for n in ("Calamity Luck Altar", "Myriad Year Flying Warship", "Dragon Palace", "Heaven Overseeing Tower")},
    "Immortal Zombie": [lambda i=i: strike_frame(i, 6) for i in range(STRIKE_FRAMES[6])],
    "Lone Gu Master": [lambda i=i: strike_frame(i, 2) for i in range(STRIKE_FRAMES[2])],
    "Demonic Gu Master": [lambda i=i: strike_frame(i, 3) for i in range(STRIKE_FRAMES[3])],
    "Demonic Elder": [lambda i=i: strike_frame(i, 5) for i in range(STRIKE_FRAMES[5])],
}

# portraits are single images (no civ tint): the robe takes the path's colour
PORTRAIT_ROBE = {"Clan Settler": (120, 92, 64), "Mortal Laborer": (140, 110, 80), "Rank One Gu Master": (70, 120, 90),
                 "Rank Two Strength Gu Master": (120, 40, 34), "Rank Three Strength Gu Master": (120, 40, 34),
                 "Rank Four Strength Gu Master": (120, 40, 34), "Rank Two Moon Gu Master": (40, 60, 130),
                 "Rank Three Moon Gu Master": (40, 60, 130), "Rank Four Moon Gu Master": (40, 60, 130),
                 **{f"Rank {w} {who}Gu Master": col for w in ("Two", "Three", "Four")
                    for who, col in (("", (90, 90, 100)), ("Gu Yue ", (40, 60, 130)), ("Bai ", (40, 110, 150)),
                                     ("Xiong ", (110, 60, 30)), ("Wu ", (60, 120, 95)))},
                 "Rank Five Gu Master": (110, 70, 150), "Rank Six Gu Immortal": (90, 140, 70),
                 "Rank Seven Gu Immortal": (140, 50, 45), "Rank Eight Gu Immortal": (200, 196, 182),
                 "Venerable": (200, 150, 50), "Calamity Luck Altar": (150, 120, 60), "Myriad Year Flying Warship": (120, 90, 60),
                 "Dragon Palace": (60, 80, 120), "Immortal Zombie": (90, 100, 95), "Heaven Overseeing Tower": (200, 190, 150),
                 "Lone Gu Master": (120, 110, 90), "Demonic Gu Master": (70, 30, 40), "Demonic Elder": (60, 20, 30)}
PORTRAIT_TRIM = (225, 215, 190)
