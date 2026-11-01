"""Secret realms (MOD_SPEC_2 #13): natural-wonder tiles for the HexaRealm tileset (64x56, the 4.22.8 default) and its
FantasyHex fallback (32x28), plus the promotion each realm grants. Every tile is a flat-topped hex painted from
primitives in a small pixel style: a grass rim and the realm's own scene. Nothing is traced or copied."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from .glyphs import G, human

S = 4  # supersampling for the tiles


def _hex(w, h):
    return [(w * 0.25, 0), (w * 0.75, 0), (w, h / 2), (w * 0.75, h), (w * 0.25, h), (0, h / 2)]


def _base(rim=(96, 150, 70), field=(120, 170, 85)):
    w, h = 64 * S, 56 * S
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(_hex(w, h), fill=rim + (255,))
    inner = [(x * 0.84 + w * 0.08, y * 0.84 + h * 0.08) for x, y in _hex(w, h)]
    d.polygon(inner, fill=field + (255,))
    return im, d, w, h


def _mountain(d, w, h, col, snow=None, x=0.5, top=0.12, base=0.8, half=0.32):
    pts = [(w * (x - half), h * base), (w * x, h * top), (w * (x + half), h * base)]
    d.polygon(pts, fill=col)
    if snow:
        d.polygon([(w * x, h * top), (w * (x - half * 0.3), h * (top + 0.18)), (w * (x + half * 0.3), h * (top + 0.18))], fill=snow)


def dang_hun(d, w, h):
    _mountain(d, w, h, (120, 120, 130), (230, 230, 240))
    for k in range(3):   # a soul swirl around the peak
        r = w * (0.12 + 0.06 * k)
        d.arc([w * 0.5 - r, h * 0.3 - r * 0.6, w * 0.5 + r, h * 0.3 + r * 0.6], 200, 340, fill=(190, 130, 230), width=S * 2)


def luo_po(d, w, h):
    d.polygon([(w * 0.1, h * 0.2), (w * 0.4, h * 0.75), (w * 0.6, h * 0.75), (w * 0.9, h * 0.2), (w * 0.9, h * 0.85),
               (w * 0.1, h * 0.85)], fill=(70, 80, 70))
    for k in range(4):   # soul-loosening fog
        y = h * (0.3 + 0.12 * k)
        d.line([(w * 0.15, y), (w * 0.85, y + S * 3)], fill=(200, 200, 215), width=S * 3)


def reverse_flow(d, w, h):
    d.ellipse([w * 0.18, h * 0.22, w * 0.82, h * 0.78], outline=(70, 130, 220), width=S * 6)
    for x in (0.32, 0.68):   # the current turns back
        d.polygon([(w * x, h * 0.36), (w * (x - 0.06), h * 0.5), (w * (x + 0.06), h * 0.5)], fill=(230, 240, 255))


def river_of_time(d, w, h):
    d.line([(w * 0.1, h * 0.7), (w * 0.4, h * 0.45), (w * 0.6, h * 0.55), (w * 0.9, h * 0.3)], fill=(230, 190, 80), width=S * 7)
    for x, y in ((0.35, 0.3), (0.65, 0.72)):   # stone lotus islands
        d.ellipse([w * (x - 0.07), h * (y - 0.05), w * (x + 0.07), h * (y + 0.05)], fill=(240, 170, 190))


def door(d, w, h):
    d.rectangle([w * 0.32, h * 0.18, w * 0.5, h * 0.82], fill=(245, 245, 245))
    d.rectangle([w * 0.5, h * 0.18, w * 0.68, h * 0.82], fill=(30, 30, 35))
    d.arc([w * 0.32, h * 0.06, w * 0.68, h * 0.34], 180, 360, fill=(140, 140, 150), width=S * 3)


def book_mountain(d, w, h):
    cols = [(150, 90, 60), (90, 110, 150), (160, 140, 70), (110, 70, 110)]
    for k in range(5):   # stacked books narrowing upward
        ww = 0.3 - 0.05 * k
        d.rectangle([w * (0.5 - ww), h * (0.78 - 0.12 * k), w * (0.5 + ww), h * (0.88 - 0.12 * k)], fill=cols[k % 4])
    d.line([(w * 0.72, h * 0.25), (w * 0.72, h * 0.8)], fill=(20, 20, 30), width=S * 4)   # ink waterfall


def demon_cave(d, w, h):
    _mountain(d, w, h, (90, 70, 70), half=0.38, top=0.15, base=0.85)
    d.ellipse([w * 0.36, h * 0.48, w * 0.64, h * 0.84], fill=(20, 10, 10))
    for x in (0.45, 0.55):
        d.ellipse([w * x - S * 3, h * 0.6 - S * 2, w * x + S * 3, h * 0.6 + S * 2], fill=(240, 40, 30))


def dragon_whale(d, w, h):
    d.ellipse([w * 0.18, h * 0.32, w * 0.78, h * 0.7], fill=(60, 120, 170))
    d.polygon([(w * 0.75, h * 0.5), (w * 0.92, h * 0.32), (w * 0.92, h * 0.68)], fill=(60, 120, 170))
    d.ellipse([w * 0.28, h * 0.42, w * 0.32, h * 0.47], fill=(20, 20, 20))
    d.line([(w * 0.42, h * 0.32), (w * 0.4, h * 0.14)], fill=(30, 20, 40), width=S * 3)   # black fire plume


def tian_ti(d, w, h):
    for k in range(6):   # a ruined stair rising toward the sky
        x0 = 0.2 + 0.1 * k
        d.rectangle([w * x0, h * (0.78 - 0.1 * k), w * (x0 + 0.12), h * 0.84], fill=(180 - 8 * k, 170 - 8 * k, 160 - 8 * k))
    d.ellipse([w * 0.68, h * 0.08, w * 0.92, h * 0.24], fill=(250, 245, 220))


def lang_ya(d, w, h):
    d.polygon([(w * 0.3, h * 0.55), (w * 0.5, h * 0.3), (w * 0.7, h * 0.55)], fill=(150, 80, 50))
    d.rectangle([w * 0.35, h * 0.55, w * 0.65, h * 0.8], fill=(170, 120, 80))
    for x, y in ((0.2, 0.2), (0.78, 0.25)):
        d.ellipse([w * (x - 0.1), h * (y - 0.05), w * (x + 0.1), h * (y + 0.05)], fill=(245, 245, 250))


def imperial_court(d, w, h):
    d.polygon([(w * 0.25, h * 0.75), (w * 0.5, h * 0.25), (w * 0.75, h * 0.75)], fill=(220, 180, 60))
    d.rectangle([w * 0.45, h * 0.55, w * 0.55, h * 0.75], fill=(120, 70, 20))
    for k in range(10):   # snow
        x, y = 0.15 + 0.07 * k, 0.15 + 0.06 * (k % 3)
        d.ellipse([w * x - S, h * y - S, w * x + S, h * y + S], fill=(250, 250, 255))


def hu_immortal(d, w, h):
    d.polygon([(w * 0.2, h * 0.55), (w * 0.8, h * 0.55), (w * 0.62, h * 0.8), (w * 0.38, h * 0.8)], fill=(120, 100, 80))
    d.polygon([(w * 0.2, h * 0.55), (w * 0.8, h * 0.55), (w * 0.7, h * 0.45), (w * 0.3, h * 0.45)], fill=(100, 170, 80))
    d.ellipse([w * 0.55, h * 0.18, w * 0.85, h * 0.36], fill=(240, 150, 60))   # a fox tail curling over the land
    d.ellipse([w * 0.78, h * 0.2, w * 0.88, h * 0.3], fill=(250, 250, 250))


SCENES = {"Dang Hun Mountain": dang_hun, "Luo Po Valley": luo_po, "Reverse Flow River": reverse_flow,
          "River of Time": river_of_time, "Door of Life and Death": door, "Book Mountain": book_mountain,
          "Crazed Demon Cave": demon_cave, "Dragon Whale Paradise": dragon_whale, "Tian Ti Mountain": tian_ti,
          "Lang Ya Blessed Land": lang_ya, "Imperial Court Blessed Land": imperial_court,
          "Hu Immortal Blessed Land": hu_immortal}
WATER = {"Dragon Whale Paradise"}


def tile(name: str) -> dict[str, Image.Image]:
    """{"HexaRealm": 64x56, "FantasyHex": 32x28} images of the realm."""
    if name in WATER:
        im, d, w, h = _base(rim=(40, 90, 150), field=(50, 110, 170))
    else:
        im, d, w, h = _base()
    SCENES[name](d, w, h)
    return {"HexaRealm": im.resize((64, 56), Image.LANCZOS), "FantasyHex": im.resize((32, 28), Image.LANCZOS)}


def promotion_icon(name: str) -> G:
    """The realm's blessing: a hex outline around a small figure."""
    g = G()
    pts = [(25, 8), (75, 8), (98, 50), (75, 92), (25, 92), (2, 50)]
    g.poly(pts)
    g.poly([(x * 0.8 + 10, y * 0.8 + 10) for x, y in pts], 0)
    human(g, 50, 22, 0.85, arms="raised")
    return g


# ---- the five region walls (界壁): a towering barrier in each region's colour
def _wall(base, accent, motif):
    def scene(d, w, h):
        d.rectangle([w * 0.05, h * 0.18, w * 0.95, h * 0.86], fill=base)
        for k in range(5):   # the wall's rising ridge
            x = 0.12 + 0.19 * k
            d.polygon([(w * (x - 0.1), h * 0.3), (w * x, h * 0.06), (w * (x + 0.1), h * 0.3)], fill=base)
        motif(d, w, h, accent)
    return scene


def _miasma(d, w, h, a):
    for k in range(4):
        d.ellipse([w * (0.1 + 0.2 * k), h * 0.45, w * (0.3 + 0.2 * k), h * 0.62], fill=a)


def _licorice(d, w, h, a):
    for k in range(6):
        x = 0.15 + 0.14 * k
        d.line([(w * x, h * 0.75), (w * (x + 0.05), h * 0.38)], fill=a, width=S * 3)


def _azure(d, w, h, a):
    for k in range(3):
        y = 0.42 + 0.14 * k
        d.arc([w * 0.08, h * (y - 0.08), w * 0.92, h * (y + 0.08)], 0, 180, fill=a, width=S * 3)


def _flame(d, w, h, a):
    for k in range(4):
        x = 0.2 + 0.2 * k
        d.polygon([(w * (x - 0.07), h * 0.75), (w * x, h * 0.35), (w * (x + 0.07), h * 0.75)], fill=a)


def _sage(d, w, h, a):
    for k in range(3):
        y = 0.4 + 0.13 * k
        d.line([(w * 0.2, h * y), (w * 0.8, h * y)], fill=a, width=S * 2)


WALLS = {"Miasma Wall": _wall((60, 90, 50), (150, 190, 110), _miasma),
         "Licorice Wall": _wall((150, 120, 80), (220, 200, 140), _licorice),
         "Azure Water Wall": _wall((30, 70, 140), (140, 200, 250), _azure),
         "Raging Flame Wall": _wall((120, 40, 20), (250, 150, 40), _flame),
         "Sage Wall": _wall((200, 196, 180), (120, 110, 90), _sage)}


def wall_tile(name: str) -> dict[str, Image.Image]:
    im, d, w, h = _base(rim=(70, 70, 70), field=(90, 90, 90))
    WALLS[name](d, w, h)
    return {"HexaRealm": im.resize((64, 56), Image.LANCZOS), "FantasyHex": im.resize((32, 28), Image.LANCZOS)}
