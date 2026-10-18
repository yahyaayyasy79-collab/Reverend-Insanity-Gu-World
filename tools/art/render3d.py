"""A small 3D renderer for the mod's characters: signed distance fields, ray-marched with numpy, toon-shaded.

Unciv draws 2D images only, so the characters are pre-rendered from 3D scenes (like the sprites of older strategy
games): map sprites with civ-colour layers, UI portraits, and the frames of the Gu attack effects. Every shape is a
geometric primitive placed by tools/art/characters.py; nothing is traced or copied.

Coordinates: y up, the model stands on y = 0, about 2 units tall, facing +z. The camera is orthographic, looks down
at ELEVATION degrees and is turned YAW degrees, which gives the three-quarter view of Unciv's unit sprites.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageFilter

EPS = 1e-3


# ---------------------------------------------------------------- primitives (vectorised over points p: (N, 3))
def _len(v):
    return np.sqrt(np.einsum("ij,ij->i", v, v))


def sd_sphere(p, c, r):
    return _len(p - np.asarray(c, np.float32)) - r


def sd_ellipsoid(p, c, radii):
    q = (p - np.asarray(c, np.float32))
    r = np.asarray(radii, np.float32)
    k0 = _len(q / r)
    k1 = _len(q / (r * r))
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def sd_capsule(p, a, b, r):
    a, b = np.asarray(a, np.float32), np.asarray(b, np.float32)
    pa, ba = p - a, b - a
    h = np.clip((pa @ ba) / float(ba @ ba), 0.0, 1.0)
    return _len(pa - h[:, None] * ba) - r


def sd_round_cone(p, a, b, ra, rb):
    """Inigo Quilez's round cone between points a and b with end radii ra and rb."""
    a, b = np.asarray(a, np.float32), np.asarray(b, np.float32)
    ba = b - a
    l2 = float(ba @ ba)
    rr = ra - rb
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = p - a
    y = pa @ ba
    z = y - l2
    xv = pa * l2 - y[:, None] * ba
    x2 = np.einsum("ij,ij->i", xv, xv)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d1 = np.sqrt(x2 + z2) * il2 - rb
    d2 = np.sqrt(x2 + y2) * il2 - ra
    d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0.0)) + y * rr) * il2 - ra
    return np.where(np.sign(z) * a2 * z2 > k, d1, np.where(np.sign(y) * a2 * y2 < k, d2, d3))


def sd_box(p, c, half, r=0.0):
    q = np.abs(p - np.asarray(c, np.float32)) - (np.asarray(half, np.float32) - r)
    return _len(np.maximum(q, 0.0)) + np.minimum(np.max(q, axis=1), 0.0) - r


def sd_torus(p, c, big, small):
    q = p - np.asarray(c, np.float32)
    xz = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2) - big
    return np.sqrt(xz * xz + q[:, 1] ** 2) - small


def sd_crescent(p, c, r, thick, cut, axis_angle=0.0, tilt=0.0):
    """A flat crescent blade: a thin disc minus an offset disc, in a plane rotated by axis_angle around y and tilted."""
    q = p - np.asarray(c, np.float32)
    ca, sa = math.cos(axis_angle), math.sin(axis_angle)
    x = q[:, 0] * ca - q[:, 2] * sa
    z = q[:, 0] * sa + q[:, 2] * ca
    y = q[:, 1]
    ct, st = math.cos(tilt), math.sin(tilt)
    y, z = y * ct - z * st, y * st + z * ct
    flat = np.abs(z) - thick
    d_out = np.sqrt(x * x + y * y) - r
    d_in = np.sqrt((x - cut) ** 2 + y * y) - r * 0.86
    disc = np.maximum(d_out, -d_in)
    return np.maximum(disc, flat)


@dataclass
class Prim:
    kind: str
    args: tuple
    mat: str
    blend: float = 0.0  # smooth-union radius with what came before


@dataclass
class Scene:
    prims: list[Prim] = field(default_factory=list)

    def add(self, kind, *args, mat="robe", blend=0.0):
        self.prims.append(Prim(kind, args, mat, blend))
        return self

    def eval(self, p):
        """(distance, primitive index of the closest primitive)."""
        fn = {"sphere": sd_sphere, "ellipsoid": sd_ellipsoid, "capsule": sd_capsule, "cone": sd_round_cone,
              "box": sd_box, "torus": sd_torus, "crescent": sd_crescent}
        d = np.full(len(p), 1e9, np.float32)
        idx = np.full(len(p), -1, np.int32)
        for i, pr in enumerate(self.prims):
            di = fn[pr.kind](p, *pr.args).astype(np.float32)
            if pr.blend > 0:
                h = np.clip(0.5 + 0.5 * (d - di) / pr.blend, 0.0, 1.0)
                d = d * (1 - h) + di * h - pr.blend * h * (1 - h)
            else:
                d = np.minimum(d, di)
            closer = di <= d + 1e-4
            idx = np.where(closer, i, idx)
        return d, idx


# ---------------------------------------------------------------- materials
@dataclass
class Mat:
    color: tuple
    spec: float = 0.0       # specular strength (metal, jade)
    emissive: bool = False  # unlit, glows
    layer: int = 0          # 0 base image, 1 = civ inner colour layer (-1), 2 = civ outer colour layer (-2)


DEFAULT_MATS = {
    "skin": Mat((232, 190, 152)), "hair": Mat((34, 28, 30), spec=0.25), "robe": Mat((214, 214, 220), layer=1),
    "trim": Mat((220, 220, 220), layer=2), "cloth": Mat((150, 120, 90)), "leather": Mat((110, 72, 46)),
    "metal": Mat((170, 170, 180), spec=0.8), "jade": Mat((120, 200, 150), spec=0.9), "wood": Mat((120, 84, 52)),
    "straw": Mat((214, 180, 96)), "fur": Mat((112, 128, 150)), "fur_dark": Mat((70, 80, 100)), "bone": Mat((232, 224, 200), spec=0.3),
    "eye": Mat((255, 240, 160), emissive=True), "moon": Mat((210, 230, 255), emissive=True),
    "essence1": Mat((110, 220, 150), emissive=True), "essence2": Mat((240, 90, 70), emissive=True),
    "essence3": Mat((235, 240, 255), emissive=True), "essence4": Mat((255, 214, 90), emissive=True),
    "volt": Mat((150, 210, 255), emissive=True), "volt_gold": Mat((255, 236, 120), emissive=True),
    "earth": Mat((200, 140, 70)), "shadow": Mat((0, 0, 0)),
}


# ---------------------------------------------------------------- camera and renderer
def render(scene: Scene, size=(128, 110), scale=2.6, center=(0.0, 1.0), yaw=25.0, elevation=22.0, ss=2,
           mats=None, outline=(22, 18, 26), shadow=True, glow=1.0, layers=True):
    """Returns {'base': RGBA, 'layer1': RGBA, 'layer2': RGBA, 'emissive': RGBA} at `size`.

    scale: world units across the image width; center: world (x, y) at the image centre (before the view tilt)."""
    mats = {**DEFAULT_MATS, **(mats or {})}
    W, H = size[0] * ss, size[1] * ss
    yaw_r, el_r = math.radians(yaw), math.radians(elevation)
    # camera basis: forward looks toward -z rotated by yaw and tilted down by elevation
    fwd = np.array([-math.sin(yaw_r) * math.cos(el_r), -math.sin(el_r), -math.cos(yaw_r) * math.cos(el_r)], np.float32)
    right = np.array([math.cos(yaw_r), 0.0, -math.sin(yaw_r)], np.float32)
    up = np.cross(right, fwd)
    px = (np.arange(W, dtype=np.float32) + 0.5) / W - 0.5
    py = 0.5 - (np.arange(H, dtype=np.float32) + 0.5) / H
    gx, gy = np.meshgrid(px * scale, py * scale * H / W)
    target = np.array([0.0, center[1], 0.0], np.float32) + right * center[0]
    origin = target[None, :] + gx.reshape(-1, 1) * right + gy.reshape(-1, 1) * up - fwd * 6.0
    n = len(origin)
    t = np.zeros(n, np.float32)
    alive = np.ones(n, bool)
    hit = np.zeros(n, bool)
    for _ in range(96):
        ids = np.nonzero(alive)[0]
        if len(ids) == 0:
            break
        p = origin[ids] + fwd * t[ids, None]
        d, _ = scene.eval(p)
        t[ids] += np.maximum(d, EPS * 0.5)
        done = d < EPS * 2
        hit[ids[done]] = True
        far = t[ids] > 12.0
        alive[ids[done | far]] = False
    color = np.zeros((n, 3), np.float32)
    layer = np.zeros(n, np.int8)
    emis = np.zeros(n, bool)
    ids = np.nonzero(hit)[0]
    if len(ids):
        p = origin[ids] + fwd * t[ids, None]
        _, prim = scene.eval(p)
        e = 2e-3
        grads = []
        for axis in range(3):
            off = np.zeros(3, np.float32); off[axis] = e
            grads.append(scene.eval(p + off)[0] - scene.eval(p - off)[0])
        nrm = np.stack(grads, 1)
        nrm /= np.maximum(_len(nrm), 1e-6)[:, None]
        light = np.array([-0.55, 0.75, 0.45], np.float32); light /= np.linalg.norm(light)
        ndl = nrm @ light
        band = np.where(ndl > 0.55, 1.0, np.where(ndl > 0.1, 0.78, 0.55))           # three toon bands
        rim = np.clip(1.0 + nrm @ fwd, 0, 1) ** 3 * 0.35
        refl = 2 * ndl[:, None] * nrm - light
        spec_t = np.clip(-(refl @ fwd), 0, 1) ** 24
        for i, pr in enumerate(scene.prims):
            sel = prim == i
            if not sel.any():
                continue
            m = mats[pr.mat]
            base = np.asarray(m.color, np.float32)
            if m.emissive:
                color[ids[sel]] = base
                emis[ids[sel]] = True
            else:
                lit = base[None, :] * (band[sel, None] * 0.85 + 0.12) + 255 * rim[sel, None] + 255 * m.spec * spec_t[sel, None]
                color[ids[sel]] = lit
            layer[ids[sel]] = m.layer
    color = np.clip(color, 0, 255).reshape(H, W, 3)
    alpha = hit.reshape(H, W)
    layer = layer.reshape(H, W)
    emis = emis.reshape(H, W)
    depth = np.where(hit, t, 99).reshape(H, W)

    # outline: silhouette edge and depth jumps
    a = alpha.astype(np.uint8) * 255
    dil = np.array(Image.fromarray(a).filter(ImageFilter.MaxFilter(3))) > 0
    edge = dil & ~alpha
    dz = np.zeros_like(depth)
    dz[:, 1:] = np.maximum(dz[:, 1:], np.abs(np.diff(depth, axis=1)))
    dz[1:, :] = np.maximum(dz[1:, :], np.abs(np.diff(depth, axis=0)))
    inner_edge = alpha & (dz > 0.25) & ~emis
    rgba = np.zeros((H, W, 4), np.float32)
    rgba[..., :3] = color
    rgba[..., 3] = alpha * 255
    rgba[inner_edge, :3] = rgba[inner_edge, :3] * 0.35 + np.asarray(outline, np.float32) * 0.65
    rgba[edge, :3] = outline
    rgba[edge, 3] = 255

    def layer_img(which):
        img = np.zeros_like(rgba)
        if which == 0 and not layers:
            sel = np.ones_like(alpha)                                                 # one image: every material
        elif which == 0:
            sel = (layer == 0) | edge | ~alpha
        else:
            sel = (layer == which) & alpha
        img[sel] = rgba[sel]
        if which and layers:
            lum = img[..., :3].mean(axis=2, keepdims=True)                        # tinted by Unciv: keep light only
            img[..., :3] = np.clip(lum * 1.15, 0, 255)
        return img

    out = {}
    for name, which in (("base", 0), ("layer1", 1), ("layer2", 2)):
        img = layer_img(which)
        if name == "base" and shadow:
            sh = np.zeros((H, W, 4), np.float32)
            yy, xx = np.mgrid[0:H, 0:W]
            # ground shadow ellipse under the origin
            sx = W * 0.5 + (0 - center[0]) * W / scale
            foot = (np.array([0, 0, 0], np.float32) - target)
            sy = H * 0.5 - (foot @ up) * W / scale
            ell = ((xx - sx) / (W * 0.18)) ** 2 + ((yy - sy) / (H * 0.06)) ** 2 < 1
            sh[ell] = (0, 0, 0, 90)
            under = sh[..., 3] > 0
            keep = img[..., 3] == 0
            img[under & keep] = sh[under & keep]
        out[name] = Image.fromarray(img.astype(np.uint8), "RGBA").resize(size, Image.LANCZOS)
    if glow and emis.any():
        g = np.zeros((H, W, 4), np.float32)
        g[emis] = rgba[emis]
        gimg = Image.fromarray(g.astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(4 * ss * glow))
        base = out["base"]
        glow_small = gimg.resize(size, Image.LANCZOS)
        out["base"] = Image.alpha_composite(glow_small, base)
        out["emissive"] = glow_small
    return out
