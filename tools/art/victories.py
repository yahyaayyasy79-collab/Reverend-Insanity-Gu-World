"""Victory illustrations (Phase D art pass, fixed 2026-11-02 after the user saw "only the white disc").

Unciv stacks a victory's images [src VictoryScreenIllustrations.FadeTo]: `Background.png` is always shown, and each
milestone's image, `Won.png` or `Lost.png` is laid over it once reached. So the background is a whole scene on its own,
and every other image is a transparent overlay that adds to it:

* Southern Border Supremacy: Qing Mao's ridges at night with four clan villages; the milestone raises a banner of
  conquest over every village and the summit;
* Endurance: the river of time winding to the horizon past waymarks; the milestone lights the great sundial at its end;
* Eternal Life: the heavenly stair climbing into the clouds to an empty summit; the milestone raises the gate of
  eternal life on it, with its pillar of light;
* Won: a golden dawn behind the scene; Lost: an ink veil and a broken ensō.

Each victory also gets its tab icon (`VictoryTypeIcons/<name>.png`). Every shape is drawn here from primitives.
"""
from __future__ import annotations

import math
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 400, 240
SS = 2   # supersampling


def _rng(key):
    return np.random.default_rng(zlib.crc32(key.encode()))


def _sky(rng, top=(10, 12, 28), bottom=(40, 38, 60), moon=(0.2, 0.22)):
    w, h = W * SS, H * SS
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (yy / h)[..., None]
    img = np.asarray(top, np.float32) / 255 * (1 - t) + np.asarray(bottom, np.float32) / 255 * t
    stars = (rng.random((h, w)) > 0.9985).astype(np.float32) * (yy < h * 0.55)
    img += np.clip(stars, 0, 1)[..., None] * 0.8
    if moon:
        mx, my = moon[0] * w, moon[1] * h
        d = np.hypot(xx - mx, yy - my)
        glow = np.clip(1 - d / (h * 0.45), 0, 1) ** 2 * 0.18
        img += glow[..., None]
        disc = np.clip((h * 0.075 - d) / 2, 0, 1)
        img = img * (1 - disc[..., None]) + disc[..., None] * np.asarray([0.96, 0.94, 0.86], np.float32)
    return img


def _ridges(img, rng, layers=4, base=0.52, tint=(0.0, 0.0, 0.0)):
    h, w = img.shape[:2]
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    xs = np.arange(w, dtype=np.float32)
    tops = []
    for layer in range(layers):
        b = h * (base + 0.11 * layer)
        amp = h * (0.17 - 0.03 * layer)
        ridge = b - amp * (np.sin(xs / w * math.pi * rng.uniform(1.4, 3.2) + rng.uniform(0, 6)) * 0.6
                           + np.sin(xs / w * math.pi * rng.uniform(5, 9) + rng.uniform(0, 6)) * 0.3
                           + (rng.random(w) - 0.5).cumsum() / w * 4)
        tops.append(ridge)
        mask = (yy > ridge[None, :]).astype(np.float32)
        far = 1 - layer / max(1, layers - 1)
        tone = np.asarray([0.30, 0.31, 0.38], np.float32) * far + np.asarray([0.05, 0.05, 0.07], np.float32) * (1 - far)
        tone = tone + np.asarray(tint, np.float32) * far
        depth = np.clip((yy - ridge[None, :]) / (h * 0.22), 0, 1)
        shade = tone[None, None, :] * (1.15 - 0.45 * depth[..., None]) + (0.10 * far) * (1 - depth[..., None])
        img = img * (1 - mask[..., None]) + shade * mask[..., None]
        band = np.exp(-((yy - (b + h * 0.06)) / (h * 0.035)) ** 2) * 0.16 * far
        img = img + band[..., None] * np.asarray([0.75, 0.78, 0.85], np.float32)
    return img, tops


def _to_image(img):
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")


def _finish(im: Image.Image, rounded=True):
    w, h = im.size
    if rounded:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([2, 2, w - 3, h - 3], radius=16 * SS, fill=255)
        im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m)), "L"))
    return im.resize((W, H), Image.LANCZOS)


def _overlay():
    return Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))


def _glow(layer: Image.Image, radius, strength=1.0):
    a = layer.getchannel("A").filter(ImageFilter.GaussianBlur(radius))
    g = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    col = layer.copy().filter(ImageFilter.GaussianBlur(radius))
    col.putalpha(a.point(lambda v: int(min(255, v * strength))))
    g.alpha_composite(col)
    g.alpha_composite(layer)
    return g


# ---------------------------------------------------------------- Southern Border Supremacy
VILLAGES = [(0.16, 0.74), (0.37, 0.80), (0.63, 0.79), (0.84, 0.73)]
SUMMIT = (0.5, 0.30)


def _hut(d, x, y, s, lit=True):
    d.polygon([(x - 14 * s, y), (x, y - 12 * s), (x + 14 * s, y)], fill=(38, 30, 34))
    d.rectangle([x - 10 * s, y, x + 10 * s, y + 10 * s], fill=(52, 42, 44))
    if lit:
        d.rectangle([x - 3 * s, y + 3 * s, x + 3 * s, y + 9 * s], fill=(255, 196, 110))


def supremacy_bg():
    rng = _rng("supremacy")
    img = _sky(rng, moon=(0.82, 0.2))
    img, _ = _ridges(img, rng, base=0.48)
    im = _to_image(img)
    d = ImageDraw.Draw(im)
    w, h = im.size
    # Qing Mao Mountain: one tall peak in the middle, the summit still empty
    d.polygon([(w * 0.28, h * 0.78), (w * SUMMIT[0], h * SUMMIT[1]), (w * 0.72, h * 0.78)], fill=(26, 30, 38))
    d.polygon([(w * 0.5, h * 0.30), (w * 0.56, h * 0.42), (w * 0.52, h * 0.41), (w * 0.5, h * 0.46), (w * 0.47, h * 0.40),
               (w * 0.45, h * 0.41)], fill=(150, 170, 180))
    lanterns = _overlay()
    ld = ImageDraw.Draw(lanterns)
    for x, y in VILLAGES:
        for k in range(3):
            _hut(d, w * x + (k - 1) * 30, h * y + (k % 2) * 6, 1.0)
            ld.ellipse([w * x + (k - 1) * 30 - 3, h * y + (k % 2) * 6 + 3, w * x + (k - 1) * 30 + 3,
                        h * y + (k % 2) * 6 + 9], fill=(255, 190, 100, 255))
    im.alpha_composite(_glow(lanterns, 8, 1.4))
    return _finish(im)


def _banner(d, x, y, s, col=(200, 40, 34)):
    d.line([(x, y), (x, y - 46 * s)], fill=(60, 44, 34), width=int(3 * s))
    d.polygon([(x, y - 46 * s), (x + 28 * s, y - 40 * s), (x + 22 * s, y - 33 * s), (x + 28 * s, y - 26 * s),
               (x, y - 28 * s)], fill=col)


def supremacy_milestone():
    o = _overlay()
    d = ImageDraw.Draw(o)
    w, h = o.size
    fire = _overlay()
    fd = ImageDraw.Draw(fire)
    for x, y in VILLAGES:
        _banner(d, w * x + 30, h * y - 2, 1.0)
        fd.ellipse([w * x - 40, h * y - 18, w * x + 40, h * y + 10], fill=(255, 120, 40, 90))
    _banner(d, w * SUMMIT[0], h * SUMMIT[1] + 4, 1.7)
    out = _glow(fire, 18, 1.0)
    out.alpha_composite(o)
    return _finish(out, rounded=False)


# ---------------------------------------------------------------- Endurance: the river of time
def _river_points(w, h):
    pts = []
    for i in range(41):
        t = i / 40
        y = h * (0.42 + 0.56 * t ** 1.4)
        x = w * (0.62 + 0.22 * math.sin(t * 5.2) * t)
        pts.append((x, y, 2 + 46 * t ** 1.5))
    return pts


def endurance_bg():
    rng = _rng("endurance")
    img = _sky(rng, top=(8, 10, 26), bottom=(34, 30, 56), moon=(0.16, 0.2))
    img, _ = _ridges(img, rng, base=0.44, layers=3)
    im = _to_image(img)
    w, h = im.size
    river = _overlay()
    rd = ImageDraw.Draw(river)
    for x, y, r in _river_points(w, h):
        rd.ellipse([x - r, y - r * 0.35, x + r, y + r * 0.35], fill=(220, 190, 110, 230))
    for k in range(60):   # motes of time drifting over the water
        x, y, r = _river_points(w, h)[int(rng.integers(5, 41))]
        dx = rng.uniform(-r, r)
        up = rng.uniform(0, 30)
        rd.ellipse([x + dx - 2, y - 14 - up, x + dx + 2, y - 10 - up], fill=(255, 236, 170, 200))
    im.alpha_composite(_glow(river, 10, 1.2))
    d = ImageDraw.Draw(im)
    for i, (x, y, r) in enumerate(_river_points(w, h)[8::8]):   # waymark stones along the bank
        s = 0.5 + i * 0.35
        d.rectangle([x - r - 18 * s, y - 16 * s, x - r - 8 * s, y + 4 * s], fill=(70, 72, 82))
    return _finish(im)


def endurance_milestone():
    o = _overlay()
    d = ImageDraw.Draw(o)
    w, h = o.size
    cx, cy, r = w * 0.62, h * 0.36, h * 0.13   # the great sundial where the river begins
    d.ellipse([cx - r, cy - r * 0.5, cx + r, cy + r * 0.5], fill=(240, 210, 120, 255))
    d.ellipse([cx - r * 0.8, cy - r * 0.4, cx + r * 0.8, cy + r * 0.4], fill=(120, 96, 50, 255))
    for k in range(12):
        a = math.radians(30 * k)
        d.line([(cx, cy), (cx + math.cos(a) * r * 0.78, cy + math.sin(a) * r * 0.39)], fill=(250, 230, 160, 255), width=3)
    d.polygon([(cx, cy), (cx - 6, cy - r * 0.9), (cx + 6, cy - r * 0.9)], fill=(255, 240, 190, 255))   # the gnomon
    return _finish(_glow(o, 16, 1.3), rounded=False)


# ---------------------------------------------------------------- Eternal Life: the heavenly stair
def eternal_bg():
    rng = _rng("eternal")
    img = _sky(rng, top=(14, 12, 34), bottom=(52, 44, 70), moon=None)
    img, _ = _ridges(img, rng, base=0.62, layers=3)
    im = _to_image(img)
    w, h = im.size
    d = ImageDraw.Draw(im)
    d.polygon([(w * 0.3, h * 0.95), (w * 0.5, h * 0.18), (w * 0.7, h * 0.95)], fill=(30, 28, 40))
    stair = _overlay()
    sd = ImageDraw.Draw(stair)
    pts = [(w * (0.5 + 0.12 * math.sin(t * 9) * (1 - t)), h * (0.92 - 0.72 * t)) for t in [i / 30 for i in range(31)]]
    sd.line(pts, fill=(220, 210, 240, 230), width=5, joint="curve")
    im.alpha_composite(_glow(stair, 6, 1.1))
    clouds = _overlay()
    cd = ImageDraw.Draw(clouds)
    for k in range(9):
        x, y = rng.uniform(0.1, 0.9) * w, rng.uniform(0.15, 0.42) * h
        cd.ellipse([x - 70, y - 14, x + 70, y + 14], fill=(200, 196, 220, 120))
    im.alpha_composite(clouds.filter(ImageFilter.GaussianBlur(6)))
    return _finish(im)


def eternal_milestone():
    o = _overlay()
    d = ImageDraw.Draw(o)
    w, h = o.size
    cx, top = w * 0.5, h * 0.16
    d.rectangle([cx - 4, 0, cx + 4, top + 10], fill=(255, 236, 170, 200))          # the pillar of light
    d.rectangle([cx - 46, top + 10, cx - 34, top + 60], fill=(255, 220, 120, 255))     # the gate
    d.rectangle([cx + 34, top + 10, cx + 46, top + 60], fill=(255, 220, 120, 255))
    d.polygon([(cx - 62, top + 12), (cx, top - 8), (cx + 62, top + 12), (cx + 54, top + 18), (cx - 54, top + 18)],
              fill=(255, 230, 140, 255))
    d.rectangle([cx - 34, top + 22, cx + 34, top + 60], fill=(255, 250, 220, 160))
    return _finish(_glow(o, 20, 1.4), rounded=False)


# ---------------------------------------------------------------- won and lost (shared overlays)
def won_overlay(key):
    o = _overlay()
    w, h = o.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = np.arctan2(yy - h * 0.95, xx - w * 0.5)
    rays = (np.sin(ang * 22) > 0.55).astype(np.float32) * np.clip(1 - np.hypot(xx - w * 0.5, yy - h) / (w * 0.75), 0, 1)
    dawn = np.clip(1 - np.hypot(xx - w * 0.5, yy - h * 1.05) / (w * 0.6), 0, 1) ** 1.5
    a = np.clip(rays * 0.35 + dawn * 0.55, 0, 1)
    rgb = np.dstack([np.full((h, w), c, np.float32) for c in (1.0, 0.82, 0.42)])
    im = Image.fromarray((np.dstack([rgb, a]) * 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 6, w - 7, h - 7], radius=16 * SS, outline=(255, 214, 120, 255), width=6)
    return _finish(im, rounded=False)


def lost_overlay(key):
    rng = _rng("lost" + key)
    o = _overlay()
    w, h = o.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    tex = np.asarray(Image.fromarray((rng.random((12, 20)) * 255).astype(np.uint8), "L").resize((w, h), Image.BICUBIC),
                     np.float32) / 255
    a = np.clip(0.55 + 0.25 * tex, 0, 0.85)
    im = Image.fromarray((np.dstack([np.full((h, w, 3), 0.05, np.float32), a]) * 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    cx, cy, r = w * 0.5, h * 0.5, h * 0.3
    for a0, a1 in ((200, 290), (310, 380), (400, 470)):   # a broken ensō
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=(170, 160, 150, 230), width=10)
    return _finish(im, rounded=False)


VICTORIES = {   # name: (background, milestone overlay, tab icon path symbol)
    "Southern Border Supremacy": (supremacy_bg, supremacy_milestone, "killing"),
    "Endurance": (endurance_bg, endurance_milestone, "time"),
    "Eternal Life": (eternal_bg, eternal_milestone, "heaven"),
}


def tab_icon(path_key: str) -> Image.Image:
    from . import portrait as P
    from .pathart import symbol
    return P.ink_night(symbol(path_key), (240, 205, 120), key="victory tab " + path_key).resize((64, 64), Image.LANCZOS)


def build(mod, victories: list[dict], save) -> int:
    written = 0
    for v in victories:
        if v["name"] not in VICTORIES:
            continue
        bg, ms, sym = VICTORIES[v["name"]]
        base = mod / "Images.Victories" / "VictoryIllustrations" / v["name"]
        written += save(bg(), base / "Background.png")
        written += save(won_overlay(v["name"]), base / "Won.png")
        written += save(lost_overlay(v["name"]), base / "Lost.png")
        for m in v.get("milestones", []):
            written += save(ms(), base / f"{m.replace('[', '').replace(']', '')}.png")
        written += save(tab_icon(sym), mod / "Images.Victories" / "VictoryTypeIcons" / f"{v['name']}.png")
    return written
