"""The mod's characters as 3D scenes for tools/art/render3d.py: Gu Masters by path and rank, mortals, lightning wolves,
and the Gu attack effects. Rank shows as essence colour (canon: rank one green copper, two red iron, three white
silver, four yellow gold), build and ornaments. Every part is a primitive; nothing is traced or copied."""
from __future__ import annotations

import math

from .render3d import Scene

ESSENCE = {1: "essence1", 2: "essence2", 3: "essence3", 4: "essence4"}


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
    else:   # rank one, unpathed: a youth with a green-copper essence orb over the palm
        cultivator(s, height=0.94, build=0.9, robe=True, bun=True, pose="cast", young=True)
        s.add("sphere", (0.36, 1.45, 0.5), 0.09, mat="essence1")
        s.add("torus", (0, 0.02, 0), 0.42, 0.016, mat="essence1")
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


def essence_frame(i, rank=1):
    s = Scene()
    s.add("sphere", (0, 0.9, 0), 0.12 + 0.12 * i, mat=ESSENCE[rank])
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
    "Lightning Wolf": lambda: wolf(0.85),
    "Bold Lightning Wolf": lambda: wolf(1.05, mane=True),
    "Thunder Crown Wolf": lambda: wolf(1.25, mane=True, crown=True),
}

# attack frames per unit name (Unciv plays them over the unit that takes damage)
ATTACKS = {
    "Rank One Gu Master": [lambda i=i: essence_frame(i, 1) for i in range(3)],
    **{f"Rank {w} Moon Gu Master": [lambda i=i, r=r: moon_blade_frame(i, r) for i in range(4)]
       for w, r in (("Two", 2), ("Three", 3), ("Four", 4))},
    **{f"Rank {w} Strength Gu Master": [lambda i=i, r=r: boar_charge_frame(i, r) for i in range(4)]
       for w, r in (("Two", 2), ("Three", 3), ("Four", 4))},
    "Lightning Wolf": [lambda i=i: lightning_frame(i) for i in range(4)],
    "Bold Lightning Wolf": [lambda i=i: lightning_frame(i) for i in range(4)],
    "Thunder Crown Wolf": [lambda i=i: lightning_frame(i, crown=True) for i in range(4)],
}

# portraits are single images (no civ tint): the robe takes the path's colour
PORTRAIT_ROBE = {"Clan Settler": (120, 92, 64), "Mortal Laborer": (140, 110, 80), "Rank One Gu Master": (70, 120, 90),
                 "Rank Two Strength Gu Master": (120, 40, 34), "Rank Three Strength Gu Master": (120, 40, 34),
                 "Rank Four Strength Gu Master": (120, 40, 34), "Rank Two Moon Gu Master": (40, 60, 130),
                 "Rank Three Moon Gu Master": (40, 60, 130), "Rank Four Moon Gu Master": (40, 60, 130)}
PORTRAIT_TRIM = (225, 215, 190)
