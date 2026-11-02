"""Full-colour portraits (Phase D art pass, the user 2026-11-02: "desain gambar mod keseluruhan ... 100x lebih baik").

Unciv draws flat one-colour icons inside tinted circles; a mod may instead supply uncoloured "Portraits"
(`Images/<entityType>Portraits/<name>.png`, docs Images-and-Audio "Adding Portraits") and a `Background.png` per type.
This module turns the existing silhouettes (tools/art/glyphs*.py, pathart, arcart, guart) into lit, textured
portraits, so every object keeps its designed shape and gains depth, material and colour.

Three candidate styles for the user's choice (STYLES); each takes a glyph mask and a palette:

* ink_jade:  rice paper, an ink-wash bloom in the object's colour, the shape carved in jade with an ink outline, a
             red seal in the corner (xianxia scroll-painting look);
* bronze:    an ancient bronze medallion with patina, the shape embossed in gold;
* spirit:    a night-dark disc, the shape glowing in essence light with sparks.

Nothing is copied: textures are noise, every shape is the mod's own primitive art. Needs numpy.
"""
from __future__ import annotations

import math
import zlib

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

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


def _noise(rng, size, cells) -> np.ndarray:
    """Smooth value noise in 0..1."""
    small = rng.random((cells, cells)).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8), "L").resize((size, size), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255.0


def _fractal(rng, size, octaves=(4, 8, 16, 48)) -> np.ndarray:
    out, w = np.zeros((size, size), np.float32), 0.0
    for i, c in enumerate(octaves):
        a = 0.6 ** i
        out += a * _noise(rng, size, c)
        w += a
    return out / w


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


def _rgb(a: np.ndarray, c) -> np.ndarray:
    return a[..., None] * np.asarray(c, np.float32)[None, None, :] / 255.0


def _compose(layers) -> Image.Image:
    """layers: [(rgb float HxWx3 in 0..1, alpha HxW in 0..1)], painted in order."""
    rgb = np.zeros((SIZE, SIZE, 3), np.float32)
    alpha = np.zeros((SIZE, SIZE), np.float32)
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


def _radial(size=SIZE) -> np.ndarray:
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    return np.hypot(xx - size / 2, yy - size / 2) / (size / 2)


def _outline(mask: np.ndarray, width=3) -> np.ndarray:
    im = Image.fromarray((mask * 255).astype(np.uint8), "L").filter(ImageFilter.MaxFilter(width * 2 + 1))
    return np.clip(np.asarray(im, np.float32) / 255.0 - mask * 0.0, 0, 1)


def _mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- style A: ink and jade
def ink_jade(g, color, key="", seal=None) -> Image.Image:
    rng = _rng("ink" + key)
    m = _mask_from_glyph(g, scale=0.70, dy=-0.02)
    # rice paper square with a brushed, ragged edge
    yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    edge = np.minimum.reduce([xx, yy, SIZE - 1 - xx, SIZE - 1 - yy]) / SIZE
    rag = _fractal(rng, SIZE, (6, 24, 64)) * 0.05
    paper_a = np.clip((edge - 0.035 - rag) * 60, 0, 1)
    fib = _fractal(rng, SIZE, (8, 32, 96))
    paper = np.dstack([np.full((SIZE, SIZE), c / 255.0, np.float32) for c in (238, 228, 204)]) * (0.9 + 0.12 * fib[..., None])
    # ink-wash bloom of the object's colour behind the shape
    bloom = _blur(m, 18) * 1.6 + _disc(r=0.36, soft=40) * 0.5
    bloom *= 0.55 + 0.6 * _fractal(rng, SIZE, (5, 12, 30))
    wash = np.clip(bloom, 0, 0.85)
    wash_col = _mix(color, (40, 40, 48), 0.25)
    # the shape: jade relief, an ink outline, a soft shadow
    diff, spec = _shade(m, radius=4.0, depth=5.0)
    base = np.asarray(_mix(color, (255, 255, 255), 0.15), np.float32) / 255.0
    body = base[None, None, :] * (0.35 + 0.8 * diff[..., None]) + spec[..., None] * 0.55
    body = body * (0.92 + 0.12 * _fractal(rng, SIZE, (10, 40))[..., None])
    ink = _blur(_outline(m, 3), 0.8)
    shadow = _blur(np.roll(np.roll(m, 5, 0), 4, 1), 4) * 0.45
    layers = [(paper, paper_a), (_rgb(np.ones_like(m), wash_col), wash * paper_a),
              (np.zeros((SIZE, SIZE, 3), np.float32), shadow * paper_a),
              (np.full((SIZE, SIZE, 3), 0.08, np.float32), ink * paper_a), (np.clip(body, 0, 1), m)]
    im = _compose(layers)
    if seal is not None:   # a red seal with the path's symbol, bottom right
        st = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(st)
        x0, y0, s = SIZE - 74, SIZE - 74, 52
        d.rounded_rectangle([x0, y0, x0 + s, y0 + s], radius=6, fill=(176, 30, 28, 235))
        sm = seal.m.resize((s - 12, s - 12), Image.LANCZOS)
        white = Image.new("RGBA", sm.size, (250, 236, 220, 255))
        st.paste(white, (x0 + 6, y0 + 6), sm)
        grit = (_fractal(rng, SIZE, (40, 90)) > 0.38).astype(np.uint8) * 255
        st.putalpha(ImageChops.multiply(st.getchannel("A"), Image.fromarray(grit, "L")))
        im = Image.alpha_composite(im, st)
    return im


# ---------------------------------------------------------------- style B: bronze medallion
def bronze(g, color, key="", seal=None) -> Image.Image:
    rng = _rng("bronze" + key)
    m = _mask_from_glyph(g, scale=0.62)
    r = _radial()
    disc = _disc(r=0.48, soft=1.2)
    rim = np.clip((r - 0.80) * 40, 0, 1) * disc
    tex = _fractal(rng, SIZE, (6, 16, 48))
    bronze_c = np.asarray((150, 104, 52), np.float32) / 255.0
    field = bronze_c[None, None, :] * (0.55 + 0.35 * (1 - r)[..., None]) * (0.85 + 0.25 * tex[..., None])
    patina = np.clip((_fractal(rng, SIZE, (5, 14, 40)) - 0.58) * 4, 0, 1) * 0.65
    patina_c = np.asarray((70, 140, 120), np.float32) / 255.0
    field = field * (1 - patina[..., None]) + patina_c[None, None, :] * patina[..., None] * (0.8 + 0.3 * tex[..., None])
    # the rim: a raised band with notches
    ang = np.arctan2(*np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)[::-1] - SIZE / 2)
    notch = (np.sin(ang * 24) > 0.6).astype(np.float32) * np.clip((r - 0.86) * 60, 0, 1) * np.clip((0.93 - r) * 60, 0, 1)
    rd, rs = _shade(rim, radius=3, depth=4)
    rim_col = np.asarray((196, 150, 80), np.float32)[None, None, :] / 255.0 * (0.45 + 0.7 * rd[..., None]) + rs[..., None] * 0.6
    # the shape in gold relief, tinted with the object's colour
    diff, spec = _shade(m, radius=3.5, depth=6.0)
    gold = np.asarray(_mix((232, 190, 90), color, 0.25), np.float32) / 255.0
    body = gold[None, None, :] * (0.3 + 0.85 * diff[..., None]) + spec[..., None] * 0.8
    shadow = _blur(np.roll(np.roll(m, 4, 0), 3, 1), 3) * 0.6
    layers = [(np.clip(field, 0, 1), disc), (np.zeros((SIZE, SIZE, 3), np.float32), shadow * disc),
              (np.clip(rim_col, 0, 1), rim), (np.full((SIZE, SIZE, 3), 0.15, np.float32), notch * 0.7),
              (np.clip(body, 0, 1), m * disc)]
    return _compose(layers)


# ---------------------------------------------------------------- style C: spirit glow
def spirit(g, color, key="", seal=None) -> Image.Image:
    rng = _rng("spirit" + key)
    m = _mask_from_glyph(g, scale=0.64)
    r = _radial()
    disc = _disc(r=0.48, soft=1.2)
    night = np.asarray((14, 16, 34), np.float32) / 255.0
    glowc = np.asarray(color, np.float32) / 255.0
    bg = night[None, None, :] * (1.0 + 0.6 * (1 - r)[..., None]) + glowc[None, None, :] * 0.18 * np.clip(1 - r, 0, 1)[..., None] ** 2
    stars = (rng.random((SIZE, SIZE)) > 0.996).astype(np.float32)
    stars = _blur(stars, 0.6) * 3
    ring = np.clip(1 - np.abs(r - 0.9) * 40, 0, 1)
    halo = _blur(m, 14) * 1.4 + _blur(m, 5) * 0.8
    diff, spec = _shade(m, radius=3, depth=3)
    core = np.clip(glowc[None, None, :] * (0.55 + 0.6 * diff[..., None]) + 0.45 * _blur(m, 1.5)[..., None] * diff[..., None]
                   + spec[..., None] * 0.7, 0, 1)
    sparks = np.zeros((SIZE, SIZE), np.float32)
    for _ in range(14):
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.25, 0.8)
        x, y = int(SIZE / 2 + math.cos(a) * d * SIZE / 2), int(SIZE / 2 + math.sin(a) * d * SIZE / 2)
        L = int(rng.uniform(3, 8))
        sparks[max(0, y - L):y + L, x] = 1
        sparks[y, max(0, x - L):x + L] = 1
    sparks = _blur(sparks, 0.8) * 1.5
    white = np.ones((SIZE, SIZE, 3), np.float32)
    layers = [(np.clip(bg, 0, 1), disc), (white, stars * disc * 0.8), (_rgb(np.ones_like(m), color), ring * disc * 0.9),
              (_rgb(np.ones_like(m), color), np.clip(halo, 0, 1) * disc * 0.85), (white, sparks * disc * 0.7),
              (core, m * disc)]
    return _compose(layers)


STYLES = {"ink_jade": ink_jade, "bronze": bronze, "spirit": spirit}

# ---------------------------------------------------------------- style D: ink night (A's ink with C's light)
def _enso(rng, size=SIZE) -> np.ndarray:
    """A brush circle drawn in one stroke: thick at the start, thinning and breaking up (dry brush) at the end."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    ang = (np.arctan2(yy - size / 2, xx - size / 2) + math.pi) / (2 * math.pi)       # 0..1 around
    start = rng.uniform(0, 1)
    t = (ang - start) % 1.0                                                          # stroke progress
    r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
    width = 0.085 * (1 - 0.75 * t) + 0.01
    centre = 0.87 + 0.025 * np.sin(t * 6.3 + start * 9)
    band = np.clip(1 - np.abs(r - centre) / width, 0, 1) ** 0.6
    dry = _fractal(rng, size, (24, 64, 128))
    band *= np.clip((dry - t * 0.55) * 3.5 + 0.4, 0, 1)
    band *= (t < 0.93)
    return np.clip(band, 0, 1)


def ink_night(g, color, key="", seal=None, part="all") -> Image.Image:
    """part: "all"; "backdrop" (the ink disc and the ensō only); "figure" (the glowing shape, its halo and the seal on
    transparency). Portraits use "figure" over a per-type "backdrop" (Unciv's Portraits/Background.png): the disc is
    stored once per type instead of once per object, which keeps the atlas small."""
    rng = _rng("night" + key)
    m = _mask_from_glyph(g, scale=0.62)
    r = _radial()
    disc = _disc(r=0.47, soft=1.2)
    layers = []
    if part in ("all", "backdrop"):
        tex = _fractal(rng, SIZE, (5, 14, 40, 110))
        ink = np.asarray((22, 22, 28), np.float32) / 255.0
        bg = ink[None, None, :] * (0.75 + 0.5 * tex[..., None]) + np.asarray(color, np.float32)[None, None, :] / 255.0 \
            * 0.22 * np.clip(1 - r * 1.1, 0, 1)[..., None] ** 1.5
        enso = _enso(rng)
        enso_c = np.asarray(_mix(color, (245, 235, 210), 0.55), np.float32) / 255.0
        layers += [(np.clip(bg, 0, 1), disc), (np.broadcast_to(enso_c, (SIZE, SIZE, 3)).copy(), enso * disc)]
    if part in ("all", "figure"):
        halo = _blur(m, 12) * 1.2 + _blur(m, 4) * 0.7
        diff, spec = _shade(m, radius=3, depth=3.5)
        glow = np.asarray(color, np.float32) / 255.0
        core = np.clip(glow[None, None, :] * (0.5 + 0.65 * diff[..., None]) + 0.4 * diff[..., None] ** 3
                       + spec[..., None] * 0.6, 0, 1)
        rim = _blur(_outline(m, 2), 0.7)
        inner = _disc(r=0.40, soft=8)   # the halo fades before the ensō
        layers += [(_rgb(np.ones_like(m), color), np.clip(halo, 0, 1) * inner * 0.8),
                   (np.full((SIZE, SIZE, 3), 0.05, np.float32), rim * disc * 0.9), (core, m * disc)]
    im = _compose(layers)
    if seal is not None and part != "backdrop":   # a small red seal under the shape, bottom right inside the circle
        st = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(st)
        x0, y0, s = SIZE - 92, SIZE - 92, 40
        d.rounded_rectangle([x0, y0, x0 + s, y0 + s], radius=5, fill=(186, 32, 30, 240))
        sm = seal.m.resize((s - 10, s - 10), Image.LANCZOS)
        st.paste(Image.new("RGBA", sm.size, (252, 238, 222, 255)), (x0 + 5, y0 + 5), sm)
        im = Image.alpha_composite(im, st)
    return im


STYLES["ink_night"] = ink_night

