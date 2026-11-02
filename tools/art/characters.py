"""The leaders' figures as 3D scenes for tools/art/render3d.py (tools/art/inkpass.py renders them as ink silhouettes):
Gu Masters by path and rank, Gu Immortals, the immortal zombie; the units themselves are pixel art (pixelunits.py).
Rank shows as essence colour (canon: rank one green copper, two red iron, three white silver, four yellow gold), build
and ornaments. Every part is a primitive; nothing is traced or copied."""
from __future__ import annotations

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
    if path != "Strength":
        regalia(s, rank)
    return s


def regalia(s: Scene, rank: int, x=0.0, h=1.0):
    """Rank marks that stack, so every rank has its own silhouette on the map (art pass 2026-11-02): a Gu pouch and a
    headband from rank two, a shoulder mantle in the clan's colour from three, a guan cap and an orbiting Gu from four,
    a long cape, a gold hairpin and a second Gu from five; immortals add ribbons of their essence."""
    head_y = 1.72 * h
    if rank >= 2:
        s.add("ellipsoid", (x + 0.2 * h, 0.93 * h, 0.13), (0.07, 0.085, 0.05), mat="leather")             # Gu pouch
        s.add("torus", (x, head_y + 0.06 * h, -0.01), 0.152 * h, 0.014 * h, mat="trim")                    # headband
    if rank >= 3:
        s.add("ellipsoid", (x, 1.42 * h, -0.02), (0.37 * h, 0.1 * h, 0.23 * h), mat="trim", blend=0.03)   # mantle
        s.add("cone", (x, 1.38 * h, 0.0), (x, 1.12 * h, 0.0), 0.3 * h, 0.2 * h, mat="trim", blend=0.03)
    if rank >= 4:
        s.add("box", (x, head_y + 0.27 * h, -0.07), (0.05, 0.05, 0.065), 0.01, mat="metal")               # guan cap
        s.add("ellipsoid", (x - 0.48, 1.22 * h, 0.28), (0.06, 0.035, 0.08), mat="jade")                   # orbiting Gu
        s.add("torus", (x - 0.48, 1.22 * h, 0.28), 0.1, 0.008, mat="jade")
    if rank >= 5:
        s.add("ellipsoid", (x, 0.86 * h, -0.24), (0.33 * h, 0.78 * h, 0.05), mat="trim", blend=0.04)      # cape
        s.add("capsule", (x - 0.1, head_y + 0.2 * h, -0.07), (x + 0.1, head_y + 0.2 * h, -0.07), 0.012, mat="metal")
        s.add("ellipsoid", (x + 0.52, 1.78 * h, -0.05), (0.06, 0.035, 0.08), mat="jade")
        s.add("torus", (x + 0.52, 1.78 * h, -0.05), 0.1, 0.008, mat="jade")
    if rank >= 6:   # immortal ribbons of essence flowing from the shoulders
        mat = ESSENCE[min(rank, 9)]
        for side in (-1, 1):
            s.add("capsule", (x + side * 0.24, 1.42 * h, -0.05), (x + side * 0.62, 1.12 * h, -0.25), 0.022, mat=mat)
            s.add("capsule", (x + side * 0.62, 1.12 * h, -0.25), (x + side * 0.78, 0.7 * h, -0.1), 0.018, mat=mat)


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
    regalia(s, rank, h=1.04)
    return s


def immortal_zombie():
    """C5c: an immortal zombie: a grey stiff figure, arms forward, a broken dull halo."""
    s = Scene()
    cultivator(s, height=1.0, build=0.95, robe=True, bun=True, pose="cast")
    s.add("torus", (0, 2.0, -0.05), 0.2, 0.02, mat="hide_pale")
    s.add("sphere", (0.36, 1.45, 0.5), 0.1, mat="hide_dark")
    return s
