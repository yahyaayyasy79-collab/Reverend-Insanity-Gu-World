"""The mod's own map tiles as pixel-art dioramas (the user, 2026-11-02): like the HexaRealm (64x56) and FantasyHex
(32x28) tilesets, a three-quarter top view on a hexagonal grass frame, with details that stay readable when small.

Every tile is drawn natively at each tileset's size. A scene is written once in HexaRealm pixels (x 0..64 across the
hex, y 0..56 down it, negative y above it: the engine sizes a tile image by its width and lets a taller one rise above
the hex [src TileLayer.setHexagonSize]) and rasterised per tileset without antialiasing (k = 1 or 0.5). Each shape is
shaded by a five-tone ramp (darker same-hue outline, shadow, mid, light, highlight) lit from the top left and drops a
shadow to the bottom right. The hex rows and the grass and slab colours follow the tilesets' own Grassland so the tiles
sit among theirs; every scene shape is built here, nothing is traced or copied.
"""
from __future__ import annotations

import math
import zlib

import numpy as np
from PIL import Image, ImageDraw

# the hex: left edge of every pixel row (right edge = width - 1 - left), as on the tilesets' Grassland
HEX = {
    "HexaRealm": (64, (16, 16, 15, 15, 14, 13, 13, 12, 12, 11, 10, 10, 9, 8, 8, 7, 6, 6, 5, 4, 4, 3, 3, 2, 1, 1, 0, 0, 0,
                       0, 0, 0, 0, 1, 2, 2, 3, 3, 4, 5, 5, 6, 7, 7, 8, 9, 9, 10, 11, 11, 12, 12, 13, 14, 14, 15)),
    "FantasyHex": (32, (8, 7, 7, 6, 5, 5, 4, 4, 3, 2, 2, 1, 1, 0, 0, 0, 0, 0, 1, 2, 2, 3, 3, 4, 5, 5, 6, 6)),
}
# grass ramp, slab edge and its outer corner, first row of the side band and of the edge, bottom band rows, last-row edge
FRAME = {
    "HexaRealm": dict(grass=((62, 96, 40), (100, 138, 54), (118, 163, 64), (128, 176, 69), (179, 194, 43)),
                      edge=(0, 0, 0), corner=(0, 0, 0), band_row=27, edge_row=30, bottom=2, last=1, wide=True),
    "FantasyHex": dict(grass=((52, 110, 24), (86, 163, 28), (105, 193, 39), (132, 209, 25), (186, 226, 64)),
                       edge=(175, 82, 17), corner=(145, 69, 4), band_row=14, edge_row=15, bottom=1, last=2, wide=False),
}

# ramps: outline, shadow, mid, light, highlight
ROCK = ((46, 44, 56), (82, 80, 96), (118, 116, 130), (156, 154, 166), (204, 202, 212))
SOUL_ROCK = ((36, 28, 54), (64, 54, 90), (94, 84, 126), (130, 120, 164), (178, 168, 208))
CLIFF = ((50, 40, 36), (86, 72, 60), (122, 106, 88), (158, 142, 116), (200, 188, 160))
CRIMSON = ((28, 12, 16), (56, 24, 30), (86, 38, 40), (120, 56, 52), (160, 86, 72))
SNOW = ((118, 130, 164), (178, 190, 216), (222, 230, 242), (244, 247, 252), (255, 255, 255))
FROST = ((92, 70, 148), (152, 128, 206), (202, 184, 242), (232, 222, 252), (255, 255, 255))
LEAF = ((22, 58, 32), (36, 90, 44), (54, 122, 54), (82, 154, 64), (130, 190, 84))
MOSS = ((36, 52, 38), (56, 78, 52), (74, 98, 64), (92, 118, 76), (114, 140, 88))
BLOSSOM = ((120, 52, 90), (192, 102, 146), (232, 146, 182), (250, 190, 212), (255, 234, 242))
WOOD = ((50, 28, 16), (84, 52, 30), (120, 78, 46), (154, 106, 64), (188, 140, 90))
EARTH = ((64, 38, 24), (102, 64, 38), (140, 94, 56), (174, 126, 78), (206, 164, 106))
SAND = ((150, 120, 72), (196, 166, 106), (226, 200, 140), (242, 226, 172), (252, 244, 212))
WATER = ((20, 56, 116), (32, 92, 166), (50, 134, 206), (106, 186, 236), (222, 246, 255))
LAGOON = ((16, 90, 116), (26, 134, 166), (50, 178, 200), (116, 218, 228), (232, 252, 255))
AMBER = ((116, 56, 10), (188, 108, 20), (238, 168, 38), (255, 212, 98), (255, 248, 212))
GOLD = ((100, 60, 14), (164, 104, 26), (218, 162, 44), (246, 208, 92), (255, 244, 190))
WHITE = ((110, 106, 102), (164, 160, 154), (206, 202, 194), (234, 232, 226), (255, 255, 255))
BLACK = ((4, 4, 8), (18, 16, 24), (36, 32, 44), (58, 52, 68), (88, 80, 100))
ROOF = ((76, 18, 18), (126, 32, 28), (172, 52, 40), (210, 86, 60), (238, 136, 96))
PAPER = ((144, 128, 96), (196, 180, 146), (228, 216, 186), (246, 240, 222), (255, 255, 248))
BONE = ((114, 102, 84), (170, 158, 136), (214, 204, 180), (238, 232, 212), (255, 252, 240))
FIRE = ((110, 16, 10), (190, 42, 16), (242, 106, 26), (255, 180, 50), (255, 242, 170))
MIASMA = ((50, 28, 68), (96, 70, 118), (126, 136, 104), (166, 192, 108), (218, 238, 148))
JADE = ((20, 90, 80), (36, 140, 118), (76, 196, 166), (146, 236, 210), (228, 255, 244))
WHALE = ((14, 24, 48), (28, 46, 82), (46, 72, 116), (74, 106, 156), (116, 150, 196))
FUR = ((108, 104, 122), (182, 180, 196), (224, 224, 234), (244, 244, 250), (255, 255, 255))
FELT = ((112, 90, 58), (176, 148, 102), (218, 196, 148), (238, 224, 188), (255, 250, 230))
CLOUD = ((126, 138, 172), (182, 192, 220), (220, 226, 242), (242, 245, 252), (255, 255, 255))
ASH = ((34, 28, 28), (56, 48, 46), (78, 68, 64), (102, 92, 86), (130, 120, 112))
STONE = ((88, 86, 82), (142, 138, 130), (184, 180, 170), (214, 210, 200), (240, 238, 230))
SOUL = ((78, 38, 148), (128, 78, 218), (180, 130, 255), (220, 194, 255), (255, 255, 255))
WIND = ((108, 138, 168), (158, 194, 218), (204, 230, 244), (234, 248, 252), (255, 255, 255))
LIFE = ((150, 118, 56), (218, 186, 106), (244, 224, 156), (255, 244, 204), (255, 255, 255))
DEATH = ((12, 4, 22), (38, 14, 62), (66, 30, 106), (106, 58, 156), (166, 118, 216))
EMBER = ((90, 20, 20), (200, 40, 30), (255, 70, 40), (255, 170, 110), (255, 240, 210))
BOOKS = (((68, 16, 16), (122, 32, 28), (166, 50, 42), (202, 84, 64), (230, 128, 98)),
         ((18, 32, 74), (34, 60, 128), (54, 90, 170), (90, 128, 202), (138, 174, 228)),
         ((16, 58, 38), (32, 98, 60), (50, 136, 80), (84, 170, 102), (134, 204, 138)),
         ((94, 62, 12), (154, 110, 26), (202, 158, 50), (230, 196, 94), (248, 228, 158)),
         ((50, 22, 68), (86, 42, 114), (122, 68, 154), (158, 106, 188), (198, 154, 220)))


def _rng(key: str):
    return np.random.default_rng(zlib.crc32(key.encode()))


def _nb(m, dx, dy):
    """out[y, x] = m[y + dy, x + dx]; False beyond the canvas."""
    h, w = m.shape
    out = np.zeros_like(m)
    y0, y1, x0, x1 = max(0, -dy), min(h, h - dy), max(0, -dx), min(w, w - dx)
    if y0 < y1 and x0 < x1:
        out[y0:y1, x0:x1] = m[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    return out


def _edge(m):
    return m & ~(_nb(m, 1, 0) & _nb(m, -1, 0) & _nb(m, 0, 1) & _nb(m, 0, -1))


def _seg(X, Y, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    u = np.clip(((X - x0) * dx + (Y - y0) * dy) / (dx * dx + dy * dy + 1e-9), 0, 1)
    return np.hypot(X - x0 - u * dx, Y - y0 - u * dy)


def _noise(seed, cell):
    """Smooth value noise in scene units: f(x, z) in 0..1."""
    g = _rng("noise" + seed).random((48, 48))

    def f(x, z):
        u, v = x / cell + 12, z / cell + 12
        i, j = np.floor(u).astype(int) % 47, np.floor(v).astype(int) % 47
        su, sv = u - np.floor(u), v - np.floor(v)
        su, sv = su * su * (3 - 2 * su), sv * sv * (3 - 2 * sv)
        return ((g[j, i] * (1 - su) + g[j, i + 1] * su) * (1 - sv) + (g[j + 1, i] * (1 - su) + g[j + 1, i + 1] * su) * sv)
    return f


def _ridged(seed, cell):
    n = _noise(seed, cell)
    return lambda x, z: 1 - np.abs(2 * n(x, z) - 1)


def _peak(x, z, px, pz, ph, rx, rz, p=1.3):
    """A mountain of height ph at (px, pz) on the ground plane, its flanks steepening toward the top when p > 1."""
    return ph * np.clip(1 - np.hypot((x - px) / rx, (z - pz) / rz), 0, None) ** p


class Canvas:
    """One tile at one tileset's size; scene coordinates are HexaRealm pixels."""

    def __init__(self, tileset: str, top: int = 0):
        self.ts, self.k, self.top = tileset, (1.0 if tileset == "HexaRealm" else 0.5), top
        w, rows = HEX[tileset]
        self.oy = round(top * self.k)
        self.w, self.h, self.rows = w, len(rows) + self.oy, rows
        self.rgb = np.zeros((self.h, w, 3), np.float32)
        self.a = np.zeros((self.h, w), bool)
        self.hex = np.zeros((self.h, w), bool)
        for y, left in enumerate(rows):
            self.hex[self.oy + y, left:w - left] = True
        self.ok = self.hex.copy()
        self.ok[:self.oy] = True                     # tall things rise above the hex; nothing spills off its sides
        yy, xx = np.mgrid[0:self.h, 0:w]
        self.X, self.Y = (xx + 0.5) / self.k, (yy + 0.5) / self.k - top
        self.f = FRAME[tileset]
        self.grass = self.f["grass"]

    # ---- masks (scene coordinates)
    def _pil(self, fn):
        im = Image.new("L", (self.w, self.h), 0)
        fn(ImageDraw.Draw(im), lambda pts: [(x * self.k - 0.5, (y + self.top) * self.k - 0.5) for x, y in pts])
        return np.asarray(im) > 0

    def poly(self, pts):
        return self._pil(lambda d, P: d.polygon(P(pts), fill=255))

    def line(self, pts, width=1.0):
        return self._pil(lambda d, P: d.line(P(pts), fill=255, width=max(1, round(width * self.k)), joint="curve"))

    def ellipse(self, cx, cy, rx, ry):
        m = ((self.X - cx) / max(rx, 0.5 / self.k)) ** 2 + ((self.Y - cy) / max(ry, 0.5 / self.k)) ** 2 <= 1
        return m if m.any() else self.spot(cx, cy)

    def rect(self, x0, y0, x1, y1):
        m = (self.X >= x0) & (self.X < x1) & (self.Y >= y0) & (self.Y < y1)
        return m if m.any() else self.spot((x0 + x1) / 2, (y0 + y1) / 2)

    def spot(self, x, y):
        m = np.zeros((self.h, self.w), bool)
        px, py = int(x * self.k), int((y + self.top) * self.k)
        if 0 <= px < self.w and 0 <= py < self.h:
            m[py, px] = True
        return m

    def hexagon(self, inset):
        c = (32, 26.5)
        pts = [(16, 0), (47, 0), (63, 26.5), (47, 52), (16, 52), (0, 26.5)]
        s = 1 - inset / 30
        return self.poly([(c[0] + (x - c[0]) * s, c[1] + (y - c[1]) * s) for x, y in pts])

    # ---- painting
    def paint(self, m, col):
        m = m & self.ok
        col = np.asarray(col, np.float32)
        self.rgb[m] = col if col.ndim == 1 else col[m]
        self.a |= m

    def tone(self, m, t, ramp):
        self.paint(m, np.asarray(ramp, np.float32)[np.clip(t, 0, 4)])

    def dot(self, x, y, col):
        self.paint(self.spot(x, y), col)

    def drop(self, m, f=0.72):
        """A shadow cast to the bottom right on whatever lies there already."""
        d = max(1, round(2 * self.k))
        s = _nb(m, -d, -1) & ~m & self.a & self.ok
        self.rgb[s] *= f

    # ---- shading: tone maps (0 outline .. 4 highlight)
    def rim(self, m, outline=True):
        t = np.full(m.shape, 2)
        for i in range(1, max(1, round(2 * self.k)) + 1):
            t[~_nb(m, i, i) | ~_nb(m, 0, i)] = 1
        t[~_nb(m, -1, -1) | ~_nb(m, 0, -1)] = 3
        if outline:
            t[~_nb(m, 1, 0) | ~_nb(m, -1, 0) | ~_nb(m, 0, 1)] = 0
        return t

    def ball(self, m, outline=True, light=(-0.5, -0.75, 0.45)):
        ys, xs = np.nonzero(m)
        if not len(xs):
            return np.zeros(m.shape, int)
        cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
        rx, ry = (xs.max() - xs.min() + 1) / 2, (ys.max() - ys.min() + 1) / 2
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        nx, ny = (xx + 0.5 - cx) / rx, (yy + 0.5 - cy) / ry
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        lx, ly, lz = np.asarray(light) / np.linalg.norm(light)
        i = nx * lx + ny * ly + nz * lz
        t = 1 + (i > 0.2).astype(int) + (i > 0.56) + (i > 0.86)
        if outline:
            t[_edge(m) & (t <= 2)] = 0
        return t

    # ---- building blocks
    def solid(self, m, ramp, shade="rim", drop=True, outline=True):
        if drop:
            self.drop(m)
        self.tone(m, self.rim(m, outline) if shade == "rim" else self.ball(m, outline), ramp)
        return m

    def relief(self, H, ramp, snow=None, snow_h=None, face=None, z=(-14.0, 56.0), light=(-0.62, 0.7, 0.35),
               cuts=(0.25, 0.6, 0.88), min_h=0.4):
        """Render the heightfield H(x, z) (heights in scene units over the hex's ground plane) in the three-quarter
        view, front to back like a voxel landscape: screen y = z - h. Slopes are lit by their normal from the top
        left and quantised to the ramp with a light ordered dither; the exposed faces of steps take `face` (or a
        darker tone), heights above snow_h(x, z) take the snow ramp. Returns the mask of drawn pixels."""
        k = self.k
        H0 = H

        def H(x, z):   # the land stays on the hex: heights fall to nothing a few pixels inside its edge
            half = 31.5 - 16 * np.abs(z - 26.5) / 26.5
            return H0(x, z) * np.clip((half - np.abs(x - 31.5) - 2) / 5, 0, 1) * np.clip((25 - np.abs(z - 26.5)) / 5, 0, 1)

        zs = np.arange(z[1], z[0], -0.25 / k)
        Xg, Zg = np.meshgrid((np.arange(self.w) + 0.5) / k, zs)
        h, e = H(Xg, Zg), 0.5
        hx = (H(Xg + e, Zg) - H(Xg - e, Zg)) / (2 * e)
        hz = (H(Xg, Zg + e) - H(Xg, Zg - e)) / (2 * e)
        lx, ly, lz = np.asarray(light) / np.linalg.norm(light)
        lam = (-hx * lx + ly - hz * lz) / np.sqrt(hx * hx + 1 + hz * hz)
        cold = h > snow_h(Xg, Zg) if snow is not None else np.zeros(h.shape, bool)
        top = np.floor((Zg - h + self.top) * k).astype(int)
        horizon = np.full(self.w, self.h)
        lit = np.full((self.h, self.w), np.nan)
        depth = np.full((self.h, self.w), -1e9)
        cap, steep = np.zeros((self.h, self.w), bool), np.zeros((self.h, self.w), bool)
        for i in range(len(zs)):
            for c in np.nonzero(top[i] < horizon)[0]:
                y0, y1 = max(top[i, c], 0), min(horizon[c], self.h)
                if h[i, c] > min_h and y0 < y1:
                    lit[y0:y1, c], depth[y0:y1, c], cap[y0:y1, c] = lam[i, c], zs[i], cold[i, c]
                    steep[y0 + 1:y1, c] = True
                horizon[c] = top[i, c]
        m = ~np.isnan(lit) & self.ok
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - 0.47
        lv = np.nan_to_num(lit) + bayer[yy % 4, xx % 4] * (0.1 if k == 1 else 0.0)   # flat tones when small
        t = 1 + (lv > cuts[0]).astype(int) + (lv > cuts[1]) + (lv > cuts[2])
        t[steep & (t > 1)] -= 1
        below = np.vstack([depth[1:], np.full((1, self.w), -1e9)])
        t[m & (below - depth > 2.5) & (t > 1)] = 1   # a far slope just above a nearer ridge: a shadow line
        ed = _edge(m)
        t[ed] = 0
        t[ed & ~_nb(m, 0, -1) & (lv > cuts[1])] = 4
        self.drop(m)
        body = m & ~cap
        if face is not None:
            self.tone(body & ~steep, t, ramp)
            self.tone(body & steep, t, face)
        else:
            self.tone(body, t, ramp)
        if snow is not None:
            self.tone(m & cap, t, snow)
        return m

    def water(self, m, ramp, bank=EARTH, seed="water", ripples=6):
        """Water sunk into the ground: the far bank shows its earth face, the near shore is shallow."""
        face = np.zeros_like(m)
        for i in range(1, max(1, round(2 * self.k)) + 1):
            face |= ~_nb(m, 0, -i)
        face &= m
        t = np.full(m.shape, 2)
        t[m & ~face & _nb(face, 0, -1)] = 1
        t[~_nb(m, 0, 1)] = 3
        self.tone(m & ~face, t, ramp)
        self.tone(face, np.where(~_nb(m, 0, -1), 2, 1), bank)
        self.ripples(m & ~face, ramp, seed, ripples)

    def ripples(self, m, ramp, seed, n):
        rng = _rng("ripples" + seed)
        ys, xs = np.nonzero(m & _nb(m, 2, 0) & _nb(m, -2, 0))
        for _ in range(n if len(xs) else 0):
            i = rng.integers(len(xs))
            x, y = xs[i], ys[i]
            for dx in range(-1, 2 if self.k == 1 else 0):
                if 0 <= x + dx < self.w:
                    self.rgb[y, x + dx] = ramp[3]
            if self.k == 1:
                self.rgb[y, x] = ramp[4]

    def patch(self, m, ramp, seed="patch", specks=0.08):
        """A flush patch of another ground: speckled, its lower lip darker."""
        rng = _rng("patch" + seed)
        t = np.full(m.shape, 2)
        r = rng.random(m.shape)
        t[r < specks] = 1
        t[r > 1 - specks] = 3
        t[_edge(m) & ~_nb(m, 0, 1)] = 1
        self.tone(m, t, ramp)

    def tree(self, x, y, r, ramp=LEAF, trunk=WOOD):
        stem = self.rect(x - 0.9, y - r * 0.9, x + 0.9, y + 0.5)
        crown = self.ellipse(x, y - r * 1.3, r, r * 0.8)
        self.drop(stem | crown)
        self.tone(stem, np.full(stem.shape, 1), trunk)
        self.tone(crown, self.ball(crown), ramp)
        if ramp is BLOSSOM and self.k == 1:   # a few open flowers
            rng = _rng(f"blossom{x}{y}")
            for _ in range(int(r)):
                self.dot(x + rng.uniform(-r * 0.6, r * 0.5), y - r * 1.3 + rng.uniform(-r * 0.6, r * 0.4), ramp[4])

    def cloud(self, x, y, r):
        for dx, dy, s in ((-0.75, 0.25, 0.62), (0.75, 0.2, 0.68), (0.0, -0.25, 1.0)):
            m = self.ellipse(x + dx * r, y + dy * r, r * s, r * s * 0.72)
            self.tone(m, self.ball(m), CLOUD)

    def wisp(self, x, y, ramp):
        """A small soul flame: a white core in a coloured halo, its tail flickering upward."""
        pts = ({(0, 0): 4, (0, 1): 4, (-1, 0): 3, (1, 0): 3, (-1, 1): 3, (1, 1): 3, (0, 2): 3, (-1, 2): 2, (1, 2): 2,
                (0, -1): 3, (1, -1): 2, (0, -2): 2} if self.k == 1 else {(0, 0): 4, (0, -1): 2})
        px, py = int(x * self.k), int((y + self.top) * self.k)
        for (dx, dy), t in pts.items():
            if 0 <= px + dx < self.w and 0 <= py + dy < self.h:
                self.rgb[py + dy, px + dx] = ramp[t]
                self.a[py + dy, px + dx] = True

    def sparkle(self, x, y, col=(255, 255, 255)):
        px, py = int(x * self.k), int((y + self.top) * self.k)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)) if self.k == 1 else ((0, 0),):
            if 0 <= px + dx < self.w and 0 <= py + dy < self.h:
                self.rgb[py + dy, px + dx] = col
                self.a[py + dy, px + dx] = True

    # ---- the frame: grass on top, a darker side band and the slab's edge along the lower sides
    def frame(self):
        f, g = self.f, self.grass
        w, rows, n = self.w, self.rows, len(self.rows)
        self.paint(self.hex, g[2])

        def put(x, y, col):
            for xx in {x, w - 1 - x}:
                self.rgb[self.oy + y, xx] = col

        for y in range(f["band_row"], n):
            left, l1, l2 = rows[y], rows[min(y + 1, n - 1)], rows[min(y + 2, n - 1)]
            if y == n - 1:
                run = list(range(left, left + f["last"]))
            elif y >= f["edge_row"]:
                run = list(range(left, max(left, l1) + 1))
            else:
                run = []
            start = run[-1] + 1 if run else left
            end = (l2 + 1 if f["wide"] else start) if run else (l2 if f["wide"] else left)
            if y >= n - f["bottom"]:
                end = w - 1 - start
            for x in range(start, end + 1):
                put(x, y, g[1])
            for i, x in enumerate(run):
                put(x, y, f["corner"] if len(run) > 1 and i == 0 else f["edge"])

    def tufts(self, seed, n=None):
        """Grass clumps scattered on the top face, away from its edges."""
        rng = _rng("tufts" + seed)
        g = self.grass
        inner = self.hex.copy()
        r = round(4 * self.k)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 2):
                inner &= _nb(self.hex, dx, dy)
        inner[self.Y > 46] = False
        ys, xs = np.nonzero(inner)
        clump = ({(0, 0): 3, (2, 0): 3, (0, 1): 3, (1, 1): 4, (2, 1): 3, (0, 2): 1, (1, 2): 1, (2, 2): 1}
                 if self.k == 1 else {(0, 0): 3, (0, 1): 1})
        for _ in range(n or (9 if self.k == 1 else 6)):
            i = rng.integers(len(xs))
            for (dx, dy), t in clump.items():
                if inner[min(ys[i] + dy, self.h - 1), min(xs[i] + dx, self.w - 1)]:
                    self.rgb[ys[i] + dy, xs[i] + dx] = g[t]

    def image(self) -> Image.Image:
        out = np.zeros((self.h, self.w, 4), np.uint8)
        out[..., :3] = np.clip(self.rgb + 0.5, 0, 255).astype(np.uint8)
        out[..., 3] = self.a * 255
        return Image.fromarray(out, "RGBA")


# ---------------------------------------------------------------- the twelve secret realms
def dang_hun(cv):
    """Dang Hun Mountain: a violet-grey massif in a ring of soul light, soul flames drifting around it."""
    rid, fine = _ridged("dang hun", 7.0), _noise("dang hun fine", 2.5)

    def ring(front):
        th = max(1.2, 1.0 / cv.k)
        m = cv.ellipse(32, 14, 28, 6.5) & ~cv.ellipse(32, 14, 28 - th, 6.5 - th)
        m &= (cv.Y >= 14) if front else (cv.Y < 14)
        t = np.full(m.shape, 3 if front else 2)
        t[m & (np.abs(cv.X - 20) < 3)] = 4
        cv.tone(m, t, SOUL)

    def H(x, z):
        h = np.maximum.reduce([_peak(x, z, 31, 30, 34, 19, 14, 1.25), _peak(x, z, 45, 27, 22, 12, 10),
                               _peak(x, z, 18, 29, 20, 11, 9), _peak(x, z, 10, 42, 9, 7, 5), _peak(x, z, 54, 42, 8, 7, 5)])
        return h * (0.78 + 0.38 * rid(x, z)) + (h > 0.5) * 1.5 * fine(x, z)

    ring(False)
    cv.relief(H, SOUL_ROCK, snow=FROST, snow_h=lambda x, z: 24 + 4 * fine(x, z))
    ring(True)
    for x, y in ((8, 20), (56, 14), (18, -2), (46, -6), (6, 34), (58, 31)):
        cv.wisp(x, y, SOUL)


def luo_po(cv):
    """Luo Po Valley: a gorge between cliffs where a pale wind spins and loosened souls drift."""
    rid, grain = _ridged("luo po", 6.0), _ridged("luo po grain", 2.2)
    cv.patch(cv.poly([(20, 2), (44, 2), (54, 50), (10, 50)]), MOSS, "luo po")

    def H(x, z):   # two ridges closing toward the back: a V-shaped gorge
        back = np.clip((46 - z) / 30, 0, 1)
        left = np.clip(1 - np.abs(x - (6 + (46 - z) * 0.42)) / 11, 0, None)
        right = np.clip(1 - np.abs(x - (58 - (46 - z) * 0.42)) / 11, 0, None)
        h = (10 + 9 * back) * np.maximum(left, right) ** 0.8 * np.clip((z + 6) / 14, 0, 1)
        return h * (0.6 + 0.4 * rid(x, z) + 0.15 * grain(x, z))

    cv.relief(H, CLIFF)
    a = np.linspace(0, 3.4 * math.pi, 40)
    r = 1.2 + 1.5 * a
    swirl = cv.line([(32 + rr * math.cos(t), 33 + 0.45 * rr * math.sin(t)) for rr, t in zip(r, a)])
    cv.tone(swirl, np.full(swirl.shape, 3), WIND)
    for x, y in ((25, 33), (41, 31), (32, 26)):
        cv.sparkle(x, y, WIND[4])
    for x, y in ((29, 16), (37, 43), (27, 45), (36, 10)):
        cv.wisp(x, y, WIND)


def reverse_flow(cv):
    """Reverse Flow River: water leaves a pool and climbs a terraced hill, spouting skyward at the top."""
    def H(x, z):
        dome = 30 * np.clip(1 - np.hypot((x - 35) / 21, (z - 28) / 15), 0, None) ** 0.8
        return np.floor(dome / 7.5) * 7.5

    cv.relief(H, cv.grass, face=CLIFF, min_h=0.5)
    cv.water(cv.ellipse(14, 44, 8, 4), WATER, seed="reverse pool", ripples=2)
    path = [(17, 42), (22, 38), (26, 32), (29, 25), (32, 17), (34, 10), (35, 5), (35.5, 2)]
    river = cv.line(path[:3], 5) | cv.line(path[2:5], 4) | cv.line(path[4:], 3)
    t = np.full(river.shape, 2)
    t[_edge(river)] = 1
    cv.tone(river, t, WATER)
    for x, y in path[1:-1]:   # chevrons: the current runs uphill
        cv.dot(x, y - 1, WATER[4])
        if cv.k == 1:
            cv.dot(x - 1, y, WATER[3])
            cv.dot(x + 1, y, WATER[3])
    jet = cv.rect(34, -9, 37, 3)
    cv.tone(jet, np.where(np.abs(cv.X - 35.5) < 0.6, 4, 3), WATER)
    for x, y in ((31, -8), (40, -7), (33, -10), (38, -10), (30, -4), (41, -3)):
        cv.dot(x, y, WATER[4] if (x + y) % 2 else WATER[3])


def river_of_time(cv):
    """River of Time: a golden river that flows back into itself around an island with an hourglass."""
    cv.water(cv.ellipse(32, 27, 26, 16) & ~cv.ellipse(32, 25, 13, 7), AMBER, seed="time", ripples=8)
    cv.solid(cv.rect(26, 27, 39, 29.5), GOLD)
    glass = cv.poly([(27.5, 13.5), (37.5, 13.5), (33.3, 20), (31.7, 20)]) | cv.poly([(31.7, 20), (33.3, 20), (37.5, 27),
                                                                                      (27.5, 27)])
    cv.tone(glass, cv.rim(glass), CLOUD)
    sand = (cv.poly([(32, 22.5), (33, 22.5), (36.5, 27), (28.5, 27)]) | cv.poly([(30, 16), (35, 16), (33, 19.5), (32, 19.5)])
            | cv.rect(32, 19, 33, 23))
    cv.tone(sand, np.where(cv.X < 32.5, 3, 2), AMBER)
    cv.solid(cv.rect(26.5, 13.5, 28, 27) | cv.rect(37, 13.5, 38.5, 27), GOLD, drop=False)
    cv.solid(cv.rect(26, 11, 39, 13.5), GOLD)
    for x, y in ((12, 22), (50, 30), (22, 38), (46, 16), (40, 40), (20, 8), (44, 6)):
        cv.sparkle(x, y, AMBER[4])
    for x, y in ((8, 30), (56, 22), (30, 4), (36, 46)):
        cv.dot(x, y, AMBER[3])


def door(cv):
    """Door of Life and Death: a gate whose left leaf shines with life and whose right leaf is dark with death."""
    plaza = cv.ellipse(32, 41, 23, 7)
    cv.patch(plaza & (cv.X < 32), WHITE, "life plaza")
    cv.patch(plaza & (cv.X >= 32), BLACK, "death plaza")
    life, death = cv.rect(21, 4, 32, 41), cv.rect(32, 4, 43, 41)
    t = 2 + (np.abs(cv.X - 31) < 6).astype(int) + (np.abs(cv.X - 31) < 3)
    cv.tone(life, t, LIFE)
    t = 2 - (np.abs(cv.X - 33) < 6).astype(int) - (np.abs(cv.X - 33) < 3)
    cv.tone(death, t, DEATH)
    sun = cv.ellipse(26.5, 18, 3, 3)
    cv.tone(sun, np.full(sun.shape, 4), LIFE)
    moon = cv.ellipse(37.5, 18, 3, 3) & ~cv.ellipse(39, 17, 2.6, 2.6)
    cv.tone(moon, np.full(moon.shape, 4), DEATH)
    cv.solid(cv.rect(14, -2, 21, 39), WHITE)
    cv.solid(cv.rect(43, -2, 50, 39), BLACK)
    cv.solid(cv.rect(12, 36, 23, 43), STONE)
    cv.solid(cv.rect(41, 36, 52, 43), ASH)
    cv.solid(cv.rect(10, 0, 54, 5), ROOF)
    cv.solid(cv.poly([(3, -11), (10, -7), (54, -7), (61, -11), (59, -3), (5, -3)]), BLACK)
    cv.solid(cv.rect(28, -6, 37, 2), GOLD)
    cv.dot(32, -2, GOLD[0])
    for x, y in ((24, 44), (18, 47), (28, 48)):
        cv.dot(x, y, LIFE[4])
    for x, y in ((40, 44), (46, 47)):
        cv.wisp(x, y, DEATH)


def book_mountain(cv):
    """Book Mountain: a hill of stacked books crowned by an open book shedding its pages."""
    rng = _rng("book mountain")
    yb, half = 47.0, 24.0
    for tier in range(6):
        x = 32 - half
        cuts = np.sort(rng.uniform(0.3, 0.7, int(rng.integers(1, 3))))
        edges = [x] + [x + 2 * half * c for c in cuts] + [32 + half]
        for x0, x1 in zip(edges, edges[1:]):
            ramp = BOOKS[int(rng.integers(len(BOOKS)))]
            top, front = cv.rect(x0, yb - 7, x1 - 1, yb - 4), cv.rect(x0, yb - 4, x1 - 1, yb)
            cv.drop(top | front)
            t = np.full(top.shape, 3)
            t[~_nb(top, 0, -1)] = 4
            t[~_nb(top, -1, 0) | ~_nb(top, 1, 0)] = 1
            cv.tone(top, t, ramp)
            rows = np.select([cv.Y < yb - 3, cv.Y >= yb - 1], [2, 1], 9)
            cv.tone(front & (rows != 9), rows, ramp)
            pages = front & (rows == 9)
            cv.tone(pages, np.where((cv.X > x1 - 3) | (np.round(cv.Y) % 2 == 0), 2, 3), PAPER)
            cv.tone(front & (~_nb(front, -1, 0) | ~_nb(front, 1, 0)), np.zeros(front.shape, int), ramp)
        yb -= 7
        half -= 3.6
    cv.solid(cv.poly([(21, yb), (32, yb + 2.5), (43, yb), (43, yb + 1.6), (32, yb + 4), (21, yb + 1.6)]), BOOKS[0])
    left = cv.poly([(22, yb - 0.5), (32, yb + 1.5), (32, yb - 6), (23, yb - 8)])
    right = cv.poly([(32, yb + 1.5), (42, yb - 0.5), (41, yb - 8), (32, yb - 6)])
    cv.tone(left, np.where(_edge(left), 1, 4), PAPER)
    cv.tone(right, np.where(_edge(right), 1, 3), PAPER)
    if cv.k == 1:
        for i in range(3):   # lines of writing
            cv.tone(cv.line([(24.5, yb - 6 + i * 2), (30, yb - 4 + i * 2)]), np.full((cv.h, cv.w), 3), BLACK)
            cv.tone(cv.line([(34, yb - 4 + i * 2), (39.5, yb - 6 + i * 2)]), np.full((cv.h, cv.w), 3), BLACK)
    for x, y in ((32, yb - 11), (26, yb - 12), (38, yb - 13)):
        cv.sparkle(x, y, GOLD[4])
    for x, y in ((12, 6), (50, 2), (17, -6), (46, -9), (9, 20), (55, 18)):
        page = cv.rect(x, y, x + 3, y + 2)
        cv.tone(page, np.where(_edge(page) & ~_nb(page, 0, 1), 1, 3), PAPER)


def demon_cave(cv):
    """Crazed Demon Cave: a jagged crimson crag, a fanged cave mouth with red eyes, bones before it."""
    rid = _ridged("crazed demon", 4.5)
    cv.patch(cv.ellipse(32, 43, 25, 8), ASH, "demon ash", specks=0.12)

    def H(x, z):
        h = np.maximum.reduce([_peak(x, z, 32, 26, 26, 21, 14, 1.1), _peak(x, z, 17, 30, 18, 10, 8, 1.4),
                               _peak(x, z, 47, 28, 20, 10, 8, 1.4), _peak(x, z, 25, 20, 24, 8, 6, 1.5),
                               _peak(x, z, 40, 20, 25, 8, 6, 1.5)])
        return h * (0.6 + 0.6 * rid(x, z))

    cv.relief(H, CRIMSON)
    mouth = cv.ellipse(32, 33, 7, 7) | cv.rect(25, 33, 39, 42)
    lip = (cv.ellipse(32, 33, 8.5, 8.5) | cv.rect(23.5, 33, 40.5, 42)) & ~mouth
    cv.tone(lip, np.full(lip.shape, 0), CRIMSON)
    t = np.full(mouth.shape, 0)
    t[_edge(mouth) & ~_nb(mouth, 0, -1)] = 2
    cv.tone(mouth, t, BLACK)
    for x in (26.5, 29.75, 33, 36.25) if cv.k == 1 else ():   # fangs only where they stay fangs
        fang = cv.poly([(x, 27 + abs(x - 31) * 0.5), (x + 2.2, 27 + abs(x - 31) * 0.5), (x + 1.1, 31)])
        cv.tone(fang, np.full(fang.shape, 3), BONE)
    for x in (28.5, 34.5):
        eye = cv.rect(x, 34, x + 2, 35)
        cv.tone(eye, np.full(eye.shape, 2), EMBER)
        cv.dot(x + 0.5, 34, EMBER[4])
    for x, y in ((15, 45), (48, 44)):
        skull = cv.ellipse(x, y, 2.6, 2.2)
        cv.solid(skull, BONE, shade="ball")
        for dx in (-1, 1):
            cv.dot(x + dx * 0.9, y, BLACK[0])
    for x0, y0, x1, y1 in ((19, 47, 24, 46), (40, 47, 44, 48)):
        cv.solid(cv.line([(x0, y0), (x1, y1)], 1.2), BONE, drop=False, outline=False)
    for x, y in ((20, 6), (44, 2), (35, -4), (14, 22)):
        cv.wisp(x, y, EMBER)


def dragon_whale(cv):
    """Dragon Whale Paradise: an atoll whose lagoon holds a horned dragon whale blowing a spout."""
    ang = np.arctan2((cv.Y - 27) / 14, (cv.X - 32) / 23)
    rad = np.hypot((cv.X - 32) / 23, (cv.Y - 27) / 14) / (1 + 0.07 * np.sin(3 * ang + 1) + 0.05 * np.sin(5 * ang + 2))
    lagoon = rad <= 1
    cv.patch((rad <= 1.18) & ~lagoon, SAND, "atoll")
    cv.water(lagoon, LAGOON, bank=SAND, seed="lagoon", ripples=7)
    swell = cv.ellipse(30, 31.5, 18, 7.5) & ~cv.ellipse(30, 31, 16, 6.5)
    cv.tone(swell, np.full(swell.shape, 4), LAGOON)
    tail = cv.poly([(16, 31), (10, 24), (5, 22), (8, 27), (5, 31), (11, 30)])
    cv.solid(tail, WHALE, drop=False)
    body = cv.ellipse(30, 30, 15, 6.5)
    cv.tone(body, cv.ball(body), WHALE)
    belly = body & (cv.Y > 32.5)
    cv.tone(belly, np.where(_edge(body), 1, 3), FUR)
    for hx in (36, 40):
        horn = cv.line([(hx, 25), (hx + 2, 19), (hx + 4, 16)], 1.4) | cv.line([(hx + 1.5, 21), (hx + 5, 20)], 1)
        cv.tone(horn, np.full(horn.shape, 3), GOLD)
    cv.tone(cv.line([(44, 32), (48, 34), (51, 33)], 1), np.full((cv.h, cv.w), 3), GOLD)
    cv.dot(41, 29, WHALE[0])
    if cv.k == 1:
        cv.dot(41, 28, (255, 255, 255))
    jet = cv.rect(33, 6, 35, 24)
    cv.tone(jet, np.where(np.abs(cv.X - 34) < 0.6, 4, 3), LAGOON)
    for x, y in ((30, 7), (38, 6), (32, 3), (36, 2), (29, 11), (39, 10)):
        cv.dot(x, y, LAGOON[4])
    for x, y, r in ((11, 18, 3.2), (53, 37, 3.2), (49, 9, 2.8), (14, 43, 2.8)):
        cv.tree(x, y, r)


def tian_ti(cv):
    """Tian Ti Mountain: a sheer snowy peak, a white stair zigzagging to a gate on its top through a belt of cloud."""
    rid = _ridged("tian ti", 6.0)
    for x, y, r in ((9, 14, 5), (55, 12, 5), (20, 6, 4), (45, 4, 4)):
        cv.cloud(x, y, r)

    def H(x, z):
        h = np.maximum.reduce([_peak(x, z, 32, 32, 38, 17, 12, 1.5), _peak(x, z, 21, 31, 16, 10, 8, 1.2),
                               _peak(x, z, 43, 31, 18, 10, 8, 1.2)])
        return h * (0.85 + 0.3 * rid(x, z))

    cv.relief(H, ROCK, snow=SNOW, snow_h=lambda x, z: 17 + 3 * rid(x * 2, z * 2))
    stair = [(31, 45), (39, 37), (27, 29), (36, 20), (29, 11), (34, 2), (32, -8)]
    for (x0, y0), (x1, y1) in zip(stair, stair[1:]):   # treads and their shadowed risers
        n = int(max(2, math.hypot(x1 - x0, y1 - y0) / 2.2))
        for i in range(n):
            x, y = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
            cv.paint(cv.rect(x - 1.5, y + 0.6, x + 1.5, y + 1.6), WHITE[1])
            cv.paint(cv.rect(x - 1.5, y - 0.6, x + 1.5, y + 0.6), WHITE[4])
    gate = cv.rect(29.5, -12, 30.7, -8) | cv.rect(33.3, -12, 34.5, -8) | cv.rect(28.5, -13.5, 35.5, -12)
    cv.tone(gate, np.full(gate.shape, 2), ROOF)
    for x, y, r in ((7, 24, 5), (57, 22, 5), (16, 30, 4), (49, 30, 4)):
        cv.cloud(x, y, r)


def lang_ya(cv):
    """Lang Ya Blessed Land: an island floating over a sea of cloud, its pagoda and refining cauldron on top."""
    for x, y, r in ((12, 36, 6), (52, 35, 6), (24, 38, 7), (41, 38, 7)):
        cv.cloud(x, y, r)
    under = cv.poly([(11, 13), (53, 13), (46, 22), (38, 31), (33, 37), (28, 31), (19, 22)])
    t = cv.rim(under)
    t[(np.round(cv.Y) % 4 == 0) & (t == 2)] = 1
    cv.tone(under, t, EARTH)
    for x0, y0, x1, y1 in ((22, 22, 21, 28), (42, 24, 44, 30), (31, 34, 31, 40)):
        cv.tone(cv.line([(x0, y0), (x1, y1)], 1), np.full((cv.h, cv.w), 1), WOOD)
    top = cv.ellipse(32, 12, 22, 7)
    t = np.full(top.shape, 2)
    t[~_nb(top, 0, -1)] = 3
    t[~_nb(top, 0, 1)] = 1
    cv.tone(top, t, cv.grass)
    cv.solid(cv.rect(27, 3, 39, 12), WHITE)
    cv.tone(cv.rect(31, 6, 35, 12), np.full((cv.h, cv.w), 1), WOOD)
    cv.solid(cv.poly([(21, 4), (25, 0), (41, 0), (45, 4), (41, 3), (25, 3)]), ROOF)
    cv.solid(cv.rect(29, -5, 37, 0), WHITE)
    cv.solid(cv.poly([(24, -4), (28, -8), (38, -8), (42, -4), (38, -5), (28, -5)]), ROOF)
    cv.solid(cv.rect(32, -12, 34, -8), GOLD, drop=False)
    cv.solid(cv.ellipse(16, 10, 4, 3), GOLD, shade="ball")
    glow = cv.ellipse(16, 7.6, 2.6, 0.9)
    cv.tone(glow, np.full(glow.shape, 4), FIRE)
    cv.cloud(18, 1, 2.6)
    cv.tree(48, 10, 3.6)
    for x, y, r in ((8, 45, 6), (21, 47, 7), (37, 47, 7), (53, 45, 6), (30, 42, 5)):
        cv.cloud(x, y, r)


def imperial_court(cv):
    """Imperial Court Blessed Land: the golden royal tent of the northern plains among white tents and banners."""
    for x, y, rx in ((10, 29, 5), (55, 27, 4), (25, 46, 6), (44, 45, 4)):
        cv.patch(cv.ellipse(x, y, rx, rx * 0.4), SNOW, f"snow{x}")

    def tent(cx, by, r, hw, ramp):
        wall = cv.rect(cx - r, by - hw, cx + r, by) | cv.ellipse(cx, by, r, r * 0.3)
        dome = (cv.ellipse(cx, by - hw, r * 1.06, r * 0.8) & (cv.Y < by - hw + 0.5)) | cv.ellipse(cx, by - hw, r * 1.06, r * 0.28)
        cv.drop(wall | dome)
        t = cv.rim(wall)
        t[(np.round(cv.X - cx) % 3 == 0) & (t == 2)] = 1
        cv.tone(wall, t, FELT)
        cv.tone(cv.rect(cx - r, by - hw, cx + r, by - hw + 1) & wall, np.full(wall.shape, 3), GOLD)
        cv.solid(cv.rect(cx - r * 0.28, by - hw * 0.75, cx + r * 0.28, by + r * 0.25), ROOF, drop=False)
        cv.tone(dome, cv.ball(dome), ramp)
        cv.dot(cx, by - hw - r * 0.8 - 1, GOLD[4])

    tent(15, 19, 6, 5, FELT)
    tent(49, 18, 6, 5, FELT)
    for x in (22, 42):
        cv.tone(cv.rect(x, 2, x + 1, 24), np.full((cv.h, cv.w), 1), WOOD)
        flag = cv.poly([(x + 1, 2), (x + 8, 4.5), (x + 1, 7)])
        cv.tone(flag, cv.rim(flag), ROOF)
    tent(32, 34, 12, 9, GOLD)
    tent(13, 42, 6, 5, FELT)
    tent(51, 42, 6, 5, FELT)


def hu_immortal(cv):
    """Hu Immortal Blessed Land: peach blossoms, a red shrine, a pond, and the white fox with its fox fire."""
    cv.water(cv.ellipse(16, 41, 8, 4), WATER, seed="hu pond", ripples=2)
    cv.solid(cv.rect(23, 13, 41, 16), STONE)
    cv.solid(cv.rect(25, 5, 39, 14), WHITE)
    cv.tone(cv.rect(25, 5, 27, 14) | cv.rect(37, 5, 39, 14), np.full((cv.h, cv.w), 2), ROOF)
    cv.tone(cv.rect(30, 8, 34, 14), np.full((cv.h, cv.w), 1), WOOD)
    cv.solid(cv.poly([(19, 7), (23, 1), (41, 1), (45, 7), (41, 6), (23, 6)]), ROOF)
    for x, y, r in ((10, 27, 6), (54, 25, 6), (48, 43, 5)):
        cv.tree(x, y, r, BLOSSOM)
    tail = cv.ellipse(25, 31, 4.5, 4) | cv.ellipse(23, 27, 3, 3)
    body = cv.ellipse(31, 34, 5.5, 3.5)
    head = cv.ellipse(37.5, 30, 3.2, 2.7)
    ears = cv.poly([(35, 29), (35.5, 25.5), (37.5, 28)]) | cv.poly([(38.5, 28), (40.5, 25.5), (41, 29)])
    snout = cv.poly([(39.5, 29.5), (43.5, 31), (39.5, 32.5)])
    legs = cv.rect(28, 36, 29.5, 39) | cv.rect(33, 36, 34.5, 39)
    cv.drop(tail | body | head | ears | snout | legs)
    for part in (legs, tail, body, head, ears, snout):
        cv.tone(part, cv.ball(part), FUR)
    cv.dot(38.5, 29.5, BLACK[0])
    cv.dot(43, 31, BLACK[0])
    for x, y in ((45, 22), (21, 21)):
        cv.wisp(x, y, WIND)
    rng = _rng("hu petals")
    for _ in range(8):
        cv.dot(rng.uniform(8, 56), rng.uniform(16, 48), BLOSSOM[3])


# ---------------------------------------------------------------- the five region walls
def _crest(x, flat=-2.0, base=36.0):
    """The wall's top: level across the middle, sloping to the ground near the hex's side corners."""
    d = max(0.0, (abs(x - 32) - 17) / 13)
    return flat + (base - 4 - flat) * min(1.0, d) ** 1.6


def _wall(cv, wave, seed, base=36.0):
    rng = _rng("wall" + seed)
    xs = np.arange(2, 63, 1.0)
    crest = [(x, _crest(x) + wave(x, rng)) for x in xs]
    return cv.poly([(2, base)] + crest + [(62, base)] + [(32 + 30 * math.cos(a), base + 2 * math.sin(a))
                                                        for a in np.linspace(0, math.pi, 9)])


def azure_wall(cv):
    """Azure Water Wall: a standing curtain of sea, foam on its crest and at its foot, fish shadows inside."""
    m = _wall(cv, lambda x, r: 1.5 * math.sin(x * 0.45) + r.uniform(-0.5, 0.5), "azure")
    t = np.full(m.shape, 2)
    t[np.round(cv.X / cv.k).astype(int) % 5 == 0] = 3
    t[np.round(cv.X / cv.k).astype(int) % 7 == 3] = 1
    t[cv.Y > 28] = np.minimum(t[cv.Y > 28], 2)
    top = np.zeros_like(m)
    for i in range(1, max(1, round(3 * cv.k)) + 1):
        top |= ~_nb(m, 0, -i)
    t[_edge(m) & ~top] = 0
    cv.drop(m)
    cv.tone(m, t, WATER)
    cv.tone(top & m, np.where(~_nb(m, 0, -1), 4, 3), CLOUD)
    for x in range(6, 60, 7):
        cv.cloud(x, 36.5 + (x % 3) * 0.5, 2.6)
    for x, y in ((20, 14), (40, 22)):
        fish = cv.ellipse(x, y, 3, 1.2) | cv.poly([(x + 2.5, y), (x + 5, y - 1.6), (x + 5, y + 1.6)])
        cv.tone(fish, np.full(fish.shape, 1), WATER)
    rng = _rng("azure spray")
    for _ in range(8):
        x = rng.uniform(16, 48)
        cv.dot(x, _crest(x) - rng.uniform(2, 6), CLOUD[4])


def flame_wall(cv):
    """Raging Flame Wall: a rampart of fire, white-hot at its root, its tongues licking above the hex."""
    m = _wall(cv, lambda x, r: -5 * abs(math.sin(x * 0.33 + r.uniform(-0.3, 0.3))) + 3, "flame")
    yrel = cv.Y - np.array([_crest(x) for x in cv.X[0]])[None, :]
    t = np.select([yrel < 4, yrel < 12, cv.Y < 30], [1, 2, 3], 4)
    t[_edge(m) & ~_nb(m, 0, -1)] = 0
    cv.tone(m, t, FIRE)
    rng = _rng("flame tongues")
    for _ in range(7):
        x = rng.uniform(14, 50)
        tongue = cv.poly([(x - 2.5, 30), (x, rng.uniform(10, 18)), (x + 2.5, 30)])
        cv.tone(tongue, np.full(tongue.shape, 4), FIRE)
    scorch = cv.ellipse(32, 38, 29, 3) & ~m
    cv.tone(scorch, np.full(scorch.shape, 1), ASH)
    for _ in range(10):
        cv.dot(rng.uniform(8, 56), rng.uniform(-9, 4), FIRE[rng.integers(3, 5)])


def miasma_wall(cv):
    """Miasma Wall: a bank of poison fog fading at its foot, dead trees and a skull before it, bubbles rising."""
    rng = _rng("miasma")
    fade = (cv.Y > 33) & ((np.arange(cv.w)[None, :] + np.arange(cv.h)[:, None]) % 2 == 0)
    union = np.zeros((cv.h, cv.w), bool)
    bank = _wall(cv, lambda x, r: 2.5 * math.sin(x * 0.6) + r.uniform(-1, 1), "miasma bank")
    for row, (y, r) in enumerate(((1, 9), (11, 10), (21, 10), (30, 8))):
        for x in np.arange(4 + (row % 2) * 5, 62, 10):
            puff = cv.ellipse(x + rng.uniform(-2, 2), y + rng.uniform(-2, 2), r, r * 0.7) & bank & ~fade
            cv.tone(puff, cv.ball(puff, outline=False), MIASMA)
            union |= puff
    top = _edge(union) & ~_nb(union, 0, -1)
    cv.tone(top, np.zeros(top.shape, int), MIASMA)
    for x0, lean in ((13, -1), (51, 1)):
        tree = (cv.line([(x0, 44), (x0 + lean, 34), (x0 - 3 * lean, 28)], 1.6) | cv.line([(x0 + lean, 37), (x0 + 5 * lean, 31)], 1)
                | cv.line([(x0 - 3 * lean, 28), (x0 - 5 * lean, 27)], 1))
        cv.drop(tree)
        cv.tone(tree, np.where(_edge(tree) & ~_nb(tree, 0, -1), 2, 1), BLACK)
    skull = cv.ellipse(32, 44, 2.6, 2.2)
    cv.solid(skull, BONE, shade="ball")
    for dx in (-1, 1):
        cv.dot(32 + dx * 0.9, 44, BLACK[0])
    for x, y in ((22, 30), (42, 26), (27, 18), (38, 9)):
        b = cv.ellipse(x, y, 1.6, 1.6)
        cv.tone(b, np.where(_edge(b), 4, 3), MIASMA)


def _bezier(p0, p1, p2, n=12):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


def licorice_wall(cv):
    """Licorice Wall: a barrier of giant tangled roots, crowned with feathery licorice leaves and purple flowers."""
    mass = _wall(cv, lambda x, r: 1.5 * math.sin(x * 0.5) + r.uniform(-1, 1), "licorice")
    cv.drop(mass)
    cv.tone(mass, np.zeros(mass.shape, int), WOOD)
    rng = _rng("licorice roots")
    for _ in range(15):
        x0 = rng.uniform(0, 64)
        x1 = x0 + rng.uniform(-24, 24)
        pts = _bezier((x0, 39), ((x0 + x1) / 2 + rng.uniform(-8, 8), rng.uniform(10, 26)), (x1, -4))
        root = cv.line(pts, rng.uniform(3.5, 5.5)) & mass
        cv.tone(root, cv.rim(root), EARTH if rng.random() > 0.35 else WOOD)
    for x in np.arange(4, 61, 3.2):
        y = _crest(x)
        if y < 31:
            leaf = cv.ellipse(x + rng.uniform(-1, 1), y - 0.5 + rng.uniform(-1, 1), 2.6, 1.6)
            cv.tone(leaf, cv.ball(leaf), LEAF)
    for x in (12, 22, 33, 43, 52):
        cv.dot(x, _crest(x) - 2.5, BOOKS[4][3])
        if cv.k == 1:
            cv.dot(x + 1, _crest(x) - 2, BOOKS[4][2])


def sage_wall(cv):
    """Sage Wall: a stepped rampart of pale stone blocks, crenels on its walks, jade runes glowing on its face."""
    base = 37
    period, joint = (4, 6) if cv.k == 1 else (3, 4)
    py, px = np.round(cv.Y * cv.k).astype(int), np.round(cv.X * cv.k).astype(int)
    for x0, x1, top in ((3, 10, 21), (10, 19, 10), (19, 45, -1), (45, 54, 10), (54, 61, 21)):
        merlons = np.zeros((cv.h, cv.w), bool)
        for x in np.arange(x0 + 0.5, x1 - 2, 4):
            merlons |= cv.rect(x, top - 1.5, x + 2.5, top + 3)
        face = cv.rect(x0, top + 3, x1, base) | merlons
        walk = cv.rect(x0, top, x1, top + 3) & ~face
        cv.drop(face | walk)
        cv.tone(walk, np.where(~_nb(walk, 0, -1), 2, 3), STONE)
        t = cv.rim(face)
        course = (py - round((top + 3) * cv.k)) % period == 0
        seam = (px + ((py - round((top + 3) * cv.k)) // period % 2) * (joint // 2)) % joint == 0
        t[(course | seam) & (t >= 2)] = 1
        t[_nb(course, 0, -1) & (t == 2)] = 3
        cv.tone(face, t, STONE)
    for x in (24, 32, 40):
        rune = cv.rect(x - 0.8, 10, x + 0.8, 22) | cv.rect(x - 3, 13, x + 3, 14.6) | cv.rect(x - 2.4, 18, x + 2.4, 19.6)
        cv.tone(rune, np.full(rune.shape, 3), JADE)
        cv.dot(x, 11, JADE[4])


REALMS = {"Dang Hun Mountain": (dang_hun, 10), "Luo Po Valley": (luo_po, 10), "Reverse Flow River": (reverse_flow, 10),
          "River of Time": (river_of_time, 0), "Door of Life and Death": (door, 12), "Book Mountain": (book_mountain, 10),
          "Crazed Demon Cave": (demon_cave, 10), "Dragon Whale Paradise": (dragon_whale, 0), "Tian Ti Mountain": (tian_ti, 14),
          "Lang Ya Blessed Land": (lang_ya, 12), "Imperial Court Blessed Land": (imperial_court, 4),
          "Hu Immortal Blessed Land": (hu_immortal, 4)}
WALLS = {"Azure Water Wall": (azure_wall, 10), "Raging Flame Wall": (flame_wall, 12), "Miasma Wall": (miasma_wall, 8),
         "Licorice Wall": (licorice_wall, 8), "Sage Wall": (sage_wall, 8)}


def tile(name: str) -> dict[str, Image.Image]:
    """{"HexaRealm": 64 x (56 + top), "FantasyHex": 32 x (28 + top / 2)} images of a realm or a wall."""
    fn, top = {**REALMS, **WALLS}[name]
    out = {}
    for ts in HEX:
        cv = Canvas(ts, top)
        cv.frame()
        cv.tufts(name)
        fn(cv)
        out[ts] = cv.image()
    return out


if __name__ == "__main__":   # self-check: every tile has its tileset's width, the hex rows, and an opaque frame
    for nm in {**REALMS, **WALLS}:
        for ts, im in tile(nm).items():
            w, rows = HEX[ts]
            assert im.width == w and im.height >= len(rows), (nm, ts, im.size)
            alpha = np.asarray(im)[..., 3]
            assert (alpha[im.height - len(rows):][[0, -1]] > 0).sum() > 0, (nm, ts)
    print("pixeltiles ok")
