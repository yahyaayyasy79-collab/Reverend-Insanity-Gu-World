"""Medallion portraits (the user's style B, 2026-11-03: "mewah, simple, masih terbaca walau kecil").

Unciv draws flat one-colour icons inside tinted circles; a mod may instead supply uncoloured "Portraits"
(`Images/<entityType>Portraits/<name>.png`, docs Images-and-Audio "Adding Portraits") and a `Background.png` per type.
This module turns the existing silhouettes (tools/art/glyphs*.py, pathart, arcart, guart) into medallions: the shape in
gold relief on enamel in the object's colour, in a thin gold bezel (`enamel`). Its gold ramp, enamel fill, bezel and
gold relief also draw the splash screens, leaders and victories (inkpass.py, victories.py).

Nothing is copied: every shape is the mod's own primitive art. Needs numpy.
"""
from __future__ import annotations

import math
import zlib

import numpy as np
from PIL import Image, ImageFilter

SIZE = 256


# ---------------------------------------------------------------- helpers
def _rng(key: str) -> np.random.Generator:
    return np.random.default_rng(zlib.crc32(key.encode()))


def _mask_from_glyph(g, size=SIZE, scale=0.78, dy=0.0) -> np.ndarray:
    """The glyph mask (0..1) centred and scaled into the portrait."""
    inner = int(size * scale)
    m = g.m.resize((inner, inner), Image.LANCZOS)
    canvas = Image.new("L", (size, size), 0)
    canvas.paste(m, ((size - inner) // 2, int((size - inner) / 2 + dy * size)))
    return np.asarray(canvas, dtype=np.float32) / 255.0


def _blur(a: np.ndarray, r: float) -> np.ndarray:
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im, dtype=np.float32) / 255.0


def _shade(mask: np.ndarray, radius=5.0, depth=6.0, light=(-0.6, -0.8, 0.9)) -> tuple[np.ndarray, np.ndarray]:
    """(diffuse 0..1, specular 0..1) of the mask seen as a rounded relief lit from the top left."""
    h = _blur(mask, radius)
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * depth * 10, -gy * depth * 10, np.ones_like(h)
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    lx, ly, lz = light
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    d = (nx * lx + ny * ly + nz * lz) / (n * ln)
    # specular: reflect the light about the normal, view straight on
    rz = 2 * d * (nz / n) - lz / ln
    spec = np.clip(rz, 0, 1) ** 24
    return np.clip(d, 0, 1), spec


def _compose(layers) -> Image.Image:
    """layers: [(rgb float HxWx3 in 0..1, alpha HxW in 0..1)], painted in order."""
    shape = np.shape(layers[0][1])
    rgb = np.zeros(shape + (3,), np.float32)
    alpha = np.zeros(shape, np.float32)
    for col, a in layers:
        a = np.clip(a, 0, 1)
        rgb = col * a[..., None] + rgb * (1 - a[..., None])
        alpha = a + alpha * (1 - a)
    out = np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)])
    return Image.fromarray((out * 255).astype(np.uint8), "RGBA")


def _disc(size=SIZE, r=0.47, soft=1.5) -> np.ndarray:
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.hypot(xx - size / 2 + 0.5, yy - size / 2 + 0.5) / size
    return np.clip((r - d) * size / soft, 0, 1)


def _outline(mask: np.ndarray, width=3) -> np.ndarray:
    im = Image.fromarray((mask * 255).astype(np.uint8), "L").filter(ImageFilter.MaxFilter(width * 2 + 1))
    return np.clip(np.asarray(im, np.float32) / 255.0 - mask * 0.0, 0, 1)


# ---------------------------------------------------------------- jewel enamel and gold (the user's style B, 2026-11-03)
# "Luxurious, simple, readable even when small": the shape in gold on a disc of enamel in the object's own colour,
# inside a thin gold bezel. No texture, no brush, no seal: the colour carries the path, era or kind, and the shape
# fills 70% of the disc so it reads at 32 px.
GOLD = ((84, 52, 14), (150, 104, 34), (222, 176, 74), (250, 216, 128), (255, 244, 200))


def gold_ramp(v: np.ndarray) -> np.ndarray:
    """v 0..1 (dark .. bright) -> RGB 0..1 along the gold ramp."""
    xs = np.array([0.0, 0.3, 0.6, 0.85, 1.0])
    cs = np.asarray(GOLD, np.float32) / 255.0
    return np.stack([np.interp(v, xs, cs[:, i]) for i in range(3)], -1).astype(np.float32)


def _grid(size=SIZE):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    return xx / size, yy / size


def enamel_fill(color, size=SIZE) -> np.ndarray:
    """The enamel: the colour deepened, brighter toward the top left, a soft gloss."""
    x, y = _grid(size)
    c = np.asarray(color, np.float32) / 255.0
    t = np.clip(1 - np.hypot(x - 0.38, y - 0.34) * 1.7, 0, 1)[..., None]
    fill = (c * 0.34)[None, None, :] * (1 - t) + (c * 0.64)[None, None, :] * t
    gloss = np.clip(1 - np.hypot((x - 0.36) / 0.22, (y - 0.24) / 0.1), 0, 1) ** 2 * 0.1
    return np.clip(fill + gloss[..., None], 0, 1)


def gold_bezel(layers, size=SIZE, r_out=0.475, r_in=0.445):
    """A thin gold ring, bright at the top left, with a dark line inside it."""
    x, y = _grid(size)
    band = np.clip(_disc(size, r_out, 1.2) - _disc(size, r_in, 1.2), 0, 1)
    lit = np.clip(0.55 - 0.63 * ((x - 0.5) + (y - 0.5)), 0, 1)
    layers += [(gold_ramp(np.clip(0.35 + 0.6 * lit, 0, 1)), band),
               (np.zeros((size, size, 3), np.float32), np.clip(_disc(size, r_in + 0.002, 1.2) - _disc(size, r_in - 0.008, 1.2), 0, 1) * 0.55)]


def gold_figure(layers, m: np.ndarray, size=SIZE, clip=None, shadow=0.55, outline=2):
    """The shape in gold relief: a drop shadow, a dark outline, metal lit from the top left."""
    x, y = _grid(size)
    clip = np.ones_like(m) if clip is None else clip
    sh = _blur(np.roll(np.roll(m, 5 * size // SIZE, 0), 4 * size // SIZE, 1), 3) * shadow
    diff, spec = _shade(m, radius=3.2, depth=3.2)
    v = np.clip(0.18 + 0.62 * diff + 0.22 * (1 - y) - 0.08 * x, 0, 1)
    body = np.clip(gold_ramp(v) + spec[..., None] * 0.55, 0, 1)
    layers += [(np.zeros((size, size, 3), np.float32), sh * clip),
               (np.broadcast_to(np.asarray((28, 18, 8), np.float32) / 255, (size, size, 3)).copy(), _outline(m, outline) * clip),
               (body, m * clip)]


def enamel(g, color, part="all", scale=0.7) -> Image.Image:
    """A medallion: enamel in the object's colour, its shape in gold, a gold bezel. `part` "backdrop" gives the
    per-type portrait background instead: only a soft shadow to ground the medallions on any screen."""
    if part == "backdrop":
        sh = _blur(np.roll(_disc(SIZE, 0.48, 1.5), SIZE // 60, 0), 4) * 0.45
        return _compose([(np.zeros((SIZE, SIZE, 3), np.float32), sh)])
    m = _mask_from_glyph(g, scale=scale)
    layers = [(enamel_fill(color), _disc(SIZE, 0.447, 1.2))]
    gold_bezel(layers)
    gold_figure(layers, m, clip=_disc(SIZE, 0.44, 1.2))
    return _compose(layers)
