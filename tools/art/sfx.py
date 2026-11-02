"""Original attack sounds, synthesized from code (numpy; ffmpeg encodes Ogg Vorbis). Nothing is sampled or copied.

The user (2026-11-02): "sesuaikan sfx nya juga dan pas sesuai dengan serangan-serangannya". Unciv picks a unit's
attack sound by unit, never by promotion [src BattleTable: UncivSound(unit name), else attackSound], but any
triggerable can "Play [name] sound" for a human player [src UniqueTriggerActivation PlaySound: skipped for the AI].
So an attack layers up to three sounds, each scaling with what the unit has:

  low   gu-rank-<1..9>          the body of the blow: heavier, deeper and longer with every rank (attackSound)
  mid   path-<key>-<1..4>       the path's own timbre (47 recipes); each attainment tier adds a layer: an echo strike
                                (Grandmaster), a sub thump and space (Great Grandmaster), a shimmer and a long tail
                                (Supreme Grandmaster). Only the highest tier held plays.
  high  dao-<1..5>              dao marks: a bell, brighter and fuller from tier I to V
  move  move-<key>[-immortal]   a killer move (a Gu attack): a rising swell into the path's Great Grandmaster or
                                Supreme strike, the immortal one with a falling sub drop

Usage: python3 -m tools.art.sfx  (or tools/gen_art.py, which calls build()).
"""
from __future__ import annotations

import io
import math
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 22050
RNG = np.random.default_rng(20261102)


# ---------------------------------------------------------------- primitives
def _env(n, a, d, at=0.0):
    t = np.arange(n) / SR - at
    e = np.where(t < 0, 0.0, (1 - np.exp(-np.maximum(t, 0) / max(a, 1e-4))) * np.exp(-np.maximum(t, 0) / max(d, 1e-4)))
    return e


def _sweep(n, f0, f1):
    """Per-sample frequency, exponential from f0 to f1 over n samples."""
    if f1 is None or f1 == f0:
        return np.full(n, float(f0))
    return f0 * (f1 / f0) ** (np.arange(n) / max(n - 1, 1))


def _band_noise(n, lo, hi, lo2=None, hi2=None):
    """White noise band-passed frame by frame (FFT masking, Hann overlap-add), the band sweeping to (lo2, hi2)."""
    lo2, hi2 = lo2 or lo, hi2 or hi
    frame, hop = 512, 256
    x = RNG.standard_normal(n + frame)
    out = np.zeros(n + frame)
    win = np.hanning(frame)
    freqs = np.fft.rfftfreq(frame, 1 / SR)
    steps = max(1, (n + hop - 1) // hop)
    for k in range(steps):
        s = k * hop
        frac = min(1.0, s / max(n, 1))
        a = lo * (lo2 / lo) ** frac
        b = hi * (hi2 / hi) ** frac
        spec = np.fft.rfft(x[s:s + frame] * win)
        mask = 1 / (1 + np.exp(-(freqs - a) / (0.08 * a + 20))) * (1 / (1 + np.exp((freqs - b) / (0.08 * b + 20))))
        out[s:s + frame] += np.fft.irfft(spec * mask, frame) * win
    out = out[:n]
    return out / (np.max(np.abs(out)) + 1e-9)


def _osc(freq, wave="sine", vib=None, fm=None):
    n = len(freq)
    t = np.arange(n) / SR
    f = freq.copy()
    if vib:
        f = f + vib[1] * np.sin(2 * math.pi * vib[0] * t)
    ph = 2 * math.pi * np.cumsum(f) / SR
    if fm:
        ph = ph + fm[1] * np.sin(ph * fm[0])
    if wave == "sine":
        return np.sin(ph)
    frac = (ph / (2 * math.pi)) % 1.0
    if wave == "saw":
        return 2 * frac - 1
    if wave == "square":
        return np.where(frac < 0.5, 1.0, -1.0)
    return 2 * np.abs(2 * frac - 1) - 1  # triangle


def _pluck(n, f, d):
    """Karplus-Strong string, vectorized per period."""
    period = max(2, int(SR / f))
    buf = RNG.uniform(-1, 1, period)
    out = np.zeros(n)
    decay = math.exp(-period / (SR * max(d, 1e-3)))
    pos = 0
    while pos < n:
        seg = min(period, n - pos)
        out[pos:pos + seg] = buf[:seg]
        buf = decay * 0.5 * (buf + np.roll(buf, -1))
        pos += period
    return out


def _metal(n, f, d, ratios):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, r in enumerate(ratios):
        out += np.sin(2 * math.pi * f * r * t + k) * np.exp(-t / (d / (1 + 0.6 * k))) / (1 + 0.5 * k)
    return out


def _clicks(n, rate, lo, hi):
    imp = (RNG.random(n) < rate / SR).astype(float) * RNG.uniform(0.3, 1.0, n)
    band = _band_noise(n, lo, hi)
    return np.convolve(imp, band[:64] * np.hanning(64), mode="same")


def _reverb(x, seconds, wet):
    """Convolution with an exponentially decaying, low-passed noise tail."""
    if seconds <= 0 or wet <= 0:
        return x
    m = int(SR * seconds)
    ir = RNG.standard_normal(m) * np.exp(-np.arange(m) / (SR * seconds / 5))
    ir = np.convolve(ir, np.ones(6) / 6, mode="same")
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    size = 1 << int(np.ceil(np.log2(len(x) + m)))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x) + m]
    out = np.zeros(len(x) + m)
    out[:len(x)] += x * (1 - wet)
    return out + wet * y / (np.max(np.abs(y)) + 1e-9) * np.max(np.abs(x))


# ---------------------------------------------------------------- layers (a recipe is a list of these)
def N(lo, hi, a, d, g, lo2=None, hi2=None, at=0.0):
    return ("noise", dict(lo=lo, hi=hi, lo2=lo2, hi2=hi2, a=a, d=d, g=g, at=at))


def T(f, a, d, g, f2=None, wave="sine", vib=None, fm=None, at=0.0):
    return ("tone", dict(f=f, f2=f2, wave=wave, vib=vib, fm=fm, a=a, d=d, g=g, at=at))


def M(f, d, g, ratios=(1.0, 2.76, 5.4), at=0.0):
    return ("metal", dict(f=f, d=d, g=g, ratios=ratios, at=at))


def P(f, d, g, at=0.0):
    return ("pluck", dict(f=f, d=d, g=g, at=at))


def C(rate, lo, hi, d, g, at=0.0):
    return ("clicks", dict(rate=rate, lo=lo, hi=hi, d=d, g=g, at=at))


def K(f0, f1, d, g, at=0.0):
    """A thump: a sine falling from f0 to f1."""
    return ("tone", dict(f=f0, f2=f1, wave="sine", vib=None, fm=None, a=0.002, d=d, g=g, at=at))


def R(layers, times, gap):
    """Repeat layers `times` times, `gap` seconds apart."""
    out = []
    for k in range(times):
        for kind, p in layers:
            out.append((kind, {**p, "at": p["at"] + k * gap}))
    return out


def _length(layers):
    return max(p["at"] + 5 * p["d"] for _, p in layers) + 0.02


def render(layers, extra=0.0):
    n = int(SR * (_length(layers) + extra))
    out = np.zeros(n)
    for kind, p in layers:
        s0 = int(p["at"] * SR)
        m = n - s0
        if m <= 0:
            continue
        if kind == "noise":
            sig = _band_noise(m, p["lo"], p["hi"], p["lo2"], p["hi2"]) * _env(m, p["a"], p["d"])
        elif kind == "tone":
            sig = _osc(_sweep(m, p["f"], p["f2"]), p["wave"], p["vib"], p["fm"]) * _env(m, p["a"], p["d"])
        elif kind == "metal":
            sig = _metal(m, p["f"], p["d"], p["ratios"])
        elif kind == "pluck":
            sig = _pluck(m, p["f"], p["d"])
        else:
            sig = _clicks(m, p["rate"], p["lo"], p["hi"]) * _env(m, 0.005, p["d"])
        out[s0:] += p["g"] * sig
    fade = min(int(0.015 * SR), n)          # no step where the dry signal ends (the reverb tail continues it)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out


# ---------------------------------------------------------------- the 47 paths' timbres
PATHS = {
    "strength": [K(90, 45, 0.18, 1.0), N(100, 600, 0.002, 0.06, 0.5)],
    "transformation": [T(85, 0.01, 0.3, 0.5, f2=70, wave="saw", vib=(28, 6)),
                       N(1500, 5000, 0.005, 0.1, 0.4, lo2=600, hi2=2000, at=0.05)],
    "bone": [N(2000, 8000, 0.0005, 0.02, 0.6), M(900, 0.08, 0.5, ratios=(1, 1.6, 2.3)), K(150, 80, 0.06, 0.4)],
    "blood": [K(60, 40, 0.12, 0.8), N(200, 900, 0.01, 0.15, 0.5, lo2=120, hi2=500), K(60, 40, 0.1, 0.6, at=0.22)],
    "sword": [N(2000, 7000, 0.01, 0.1, 0.6, lo2=4000, hi2=9000), M(1800, 0.3, 0.35)],
    "blade": [N(900, 4000, 0.015, 0.13, 0.7, lo2=2000, hi2=6000), M(1100, 0.25, 0.3, ratios=(1, 2.4, 4.1)),
              K(110, 60, 0.08, 0.4)],
    "metal": [M(420, 0.4, 0.7, ratios=(1, 2.32, 4.25, 6.63)), N(1000, 5000, 0.001, 0.03, 0.4)],
    "weapon": R([N(2500, 7000, 0.005, 0.05, 0.5, lo2=3500, hi2=8000)], 3, 0.06) + [M(1500, 0.18, 0.25, at=0.12)],
    "killing": [N(3000, 9000, 0.003, 0.07, 0.6, lo2=5000, hi2=10000), T(55, 0.05, 0.4, 0.45, f2=48, wave="saw")],
    "fire": [N(200, 2500, 0.02, 0.3, 0.6, lo2=400, hi2=4000), C(120, 1500, 6000, 0.35, 0.35)],
    "water": [N(500, 2500, 0.003, 0.15, 0.6, lo2=250, hi2=1200), T(600, 0.002, 0.05, 0.25, f2=1400, at=0.05),
              T(500, 0.002, 0.04, 0.2, f2=1200, at=0.11), T(700, 0.002, 0.04, 0.2, f2=1600, at=0.16)],
    "wood": [M(320, 0.13, 0.6, ratios=(1, 2.1, 3.3)), N(3000, 9000, 0.02, 0.15, 0.25)],
    "earth": [N(40, 250, 0.01, 0.35, 0.8), K(80, 40, 0.18, 0.7), N(300, 1200, 0.001, 0.04, 0.4)],
    "wind": [N(300, 1200, 0.08, 0.3, 0.6, lo2=800, hi2=3000)],
    "cloud": [N(200, 900, 0.1, 0.35, 0.4, lo2=400, hi2=1500), T(330, 0.12, 0.4, 0.15), T(495, 0.12, 0.4, 0.1)],
    "ice": [N(5000, 10000, 0.0005, 0.03, 0.5), M(3200, 0.22, 0.4, ratios=(1, 1.41, 2.0, 2.83)),
            T(4200, 0.001, 0.12, 0.2)],
    "lightning": [T(1200, 0.001, 0.2, 0.5, f2=80, fm=(0.5, 4)), N(2000, 9000, 0.0005, 0.03, 0.5),
                  C(300, 2000, 8000, 0.25, 0.4)],
    "poison": [N(4000, 10000, 0.05, 0.25, 0.4), T(300, 0.002, 0.04, 0.2, f2=700, at=0.08),
               T(260, 0.002, 0.04, 0.2, f2=650, at=0.17), T(320, 0.002, 0.04, 0.2, f2=720, at=0.26)],
    "light": [T(1500, 0.002, 0.3, 0.3, vib=(12, 30)), T(2250, 0.002, 0.3, 0.2), T(3000, 0.002, 0.25, 0.15),
              N(6000, 11000, 0.0005, 0.02, 0.3)],
    "dark": [T(55, 0.2, 0.35, 0.6, f2=45), N(150, 600, 0.25, 0.25, 0.3)],
    "shadow": [N(300, 1500, 0.005, 0.08, 0.6, lo2=150, hi2=800), T(70, 0.01, 0.18, 0.4, f2=50)],
    "star": [T(2600, 0.001, 0.12, 0.2), T(3300, 0.001, 0.12, 0.2, at=0.06), T(2900, 0.001, 0.12, 0.2, at=0.12),
             T(3900, 0.001, 0.16, 0.2, at=0.18), N(5000, 10000, 0.001, 0.04, 0.2)],
    "moon": [N(2500, 7000, 0.01, 0.1, 0.5, lo2=3500, hi2=9000), T(1200, 0.002, 0.4, 0.3, vib=(5, 8)),
             T(1800, 0.002, 0.3, 0.15)],
    "sound": [P(220, 0.5, 0.6), P(330, 0.4, 0.35, at=0.04), M(160, 0.6, 0.35, ratios=(1, 1.5, 2.0, 2.7))],
    "illusion": [T(600, 0.05, 0.4, 0.25, vib=(6, 15)), T(606, 0.05, 0.4, 0.25, vib=(5, 15)), T(903, 0.05, 0.3, 0.15),
                 N(3000, 8000, 0.05, 0.25, 0.15)],
    "wisdom": [M(880, 0.5, 0.5, ratios=(1, 2.0, 3.0, 4.2)), T(1320, 0.005, 0.3, 0.15)],
    "emotion": [N(400, 1200, 0.08, 0.28, 0.4, lo2=250, hi2=800), K(60, 40, 0.1, 0.5), K(60, 40, 0.1, 0.4, at=0.25)],
    "enchantment": [M(1046, 0.35, 0.4, ratios=(1, 2, 3)), T(784, 0.005, 0.25, 0.2, f2=1568)],
    "soul": [T(420, 0.12, 0.4, 0.4, f2=300, vib=(6, 20)), N(800, 2500, 0.1, 0.3, 0.25)],
    "dream": [T(440, 0.15, 0.45, 0.25), T(554, 0.15, 0.45, 0.2), T(659, 0.15, 0.45, 0.18), M(1760, 0.4, 0.15)],
    "enslavement": [T(80, 0.02, 0.3, 0.5, f2=65, wave="saw", vib=(20, 5)), N(200, 1200, 0.02, 0.28, 0.4)]
                   + R([M(2400, 0.05, 0.2, ratios=(1, 1.7, 2.9))], 4, 0.05),
    "time": [M(2000, 0.05, 0.4, ratios=(1, 2.7)), M(1500, 0.05, 0.4, ratios=(1, 2.7), at=0.18),
             T(300, 0.2, 0.25, 0.3, f2=600)],
    "space": [T(900, 0.01, 0.3, 0.4, f2=150, vib=(30, 40)), N(500, 3000, 0.05, 0.28, 0.3, lo2=200, hi2=1000)],
    "rule": [K(100, 60, 0.08, 0.7), M(700, 0.4, 0.35, ratios=(1, 2.0, 3.0))],
    "phantom": [N(400, 1500, 0.03, 0.25, 0.5, lo2=800, hi2=2500), T(220, 0.05, 0.25, 0.2, vib=(9, 10))],
    "restriction": R([M(1800, 0.07, 0.3, ratios=(1, 1.8, 2.7))], 3, 0.05) + [K(90, 50, 0.1, 0.6, at=0.16)],
    "luck": R([M(2600, 0.1, 0.3, ratios=(1, 2.4, 3.9))], 5, 0.035) + [T(1318, 0.005, 0.25, 0.15, at=0.18)],
    "heaven": [T(262, 0.1, 0.45, 0.25, vib=(5, 4)), T(330, 0.1, 0.45, 0.2, vib=(5, 4)), T(392, 0.1, 0.45, 0.2, vib=(5, 4)),
               N(40, 300, 0.01, 0.4, 0.6, at=0.05), N(1000, 6000, 0.0005, 0.04, 0.4, at=0.05)],
    "qi": [N(80, 1500, 0.01, 0.25, 0.7, lo2=60, hi2=400), K(70, 40, 0.18, 0.6)],
    "refinement": [N(300, 2000, 0.05, 0.25, 0.4), M(2200, 0.25, 0.4, ratios=(1, 2.6, 4.3), at=0.1)],
    "formation": [T(110, 0.05, 0.4, 0.4), T(112, 0.05, 0.4, 0.4), T(220, 0.05, 0.3, 0.2), N(3000, 8000, 0.001, 0.03, 0.4)],
    "food": [N(200, 1500, 0.003, 0.05, 0.6), N(200, 1500, 0.003, 0.05, 0.6, at=0.12), T(180, 0.01, 0.08, 0.3, f2=120, at=0.25)],
    "pill": R([N(3000, 7000, 0.001, 0.02, 0.3)], 5, 0.03) + [T(250, 0.02, 0.12, 0.4, f2=150, at=0.2)],
    "information": [N(1500, 6000, 0.01, 0.12, 0.35), N(1500, 6000, 0.01, 0.1, 0.3, at=0.08), T(1760, 0.002, 0.2, 0.25, at=0.15)],
    "human": [N(300, 700, 0.03, 0.28, 0.4), N(800, 1300, 0.03, 0.25, 0.3), N(2200, 3000, 0.03, 0.2, 0.2), K(90, 55, 0.1, 0.4)],
    "painting": [N(1500, 5000, 0.03, 0.15, 0.35, lo2=800, hi2=3000), T(300, 0.002, 0.1, 0.3, f2=900, at=0.16)],
    "theft": [N(3000, 9000, 0.003, 0.06, 0.5, lo2=5000, hi2=10000)] + R([M(3000, 0.06, 0.25, ratios=(1, 2.3))], 2, 0.05),
}


def _shift(layers, dt, gain):
    return [(k, {**p, "at": p["at"] + dt, "g": p["g"] * gain}) for k, p in layers]


def _norm(x, peak, cap):
    """Scale to the peak, cut the near-silent tail (below -50 dB of the peak), keep at most `cap` seconds, and fade the
    last 60 ms: game sounds stay short and never click."""
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    loud = np.nonzero(np.abs(x) > peak * 0.003)[0]
    end = min(len(x), (loud[-1] if len(loud) else len(x)) + int(0.02 * SR), int(cap * SR))
    x = x[:end].copy()
    fade = min(int(0.06 * SR), len(x))
    x[-fade:] *= np.linspace(1, 0, fade) ** 2
    return x


def path_hit(key, tier):
    """Attainment tier 1-4: the path's timbre, then an echo strike, a sub thump and space, a shimmer and a long tail."""
    base = PATHS[key]
    layers = list(base)
    if tier >= 2:
        layers += _shift(base, 0.07, 0.55)
    if tier >= 3:
        layers += [K(70, 38, 0.22, 0.7)]
    if tier >= 4:
        layers += [K(55, 30, 0.4, 0.9), T(2600, 0.02, 0.35, 0.12, vib=(9, 25)), T(3900, 0.02, 0.3, 0.08, vib=(7, 30))]
    x = render(layers)
    x = _reverb(x, (0, 0.0, 0.25, 0.6, 1.1)[tier], (0, 0.0, 0.12, 0.22, 0.32)[tier])
    return _norm(x, (0, 0.62, 0.72, 0.82, 0.92)[tier], (0, 0.8, 1.0, 1.3, 1.7)[tier])


def killer_move(key, immortal):
    """A Gu attack: a rising swell into the path's Great Grandmaster (mortal move) or Supreme (immortal move) strike."""
    swell = 0.4 if immortal else 0.25
    rise = render([N(200, 3000, swell, 0.02, 0.6, lo2=600, hi2=7000)], extra=swell)[: int(SR * swell)]
    rise *= np.linspace(0, 1, len(rise)) ** 2
    hit = path_hit(key, 4 if immortal else 3)
    if immortal:
        drop = render([T(80, 0.01, 0.5, 0.8, f2=28)])
        hit[: len(drop)] += 0.6 * drop[: len(hit)]
    return _norm(np.concatenate([rise, hit]), 0.95 if immortal else 0.88, 2.4 if immortal else 1.7)


def rank_body(rank):
    """The blow itself (attackSound), by rank 1-9: deeper, longer, wider."""
    f0 = 140 - 9 * rank
    layers = [K(f0, f0 * 0.5, 0.06 + 0.025 * rank, 0.9),
              N(400, 2500, 0.004, 0.05 + 0.012 * rank, 0.5, lo2=300, hi2=1500)]
    if rank >= 3:
        layers += [N(60, 300, 0.005, 0.08 + 0.02 * rank, 0.4)]
    if rank >= 6:   # immortals: the aperture's qi hums under the blow
        layers += [T(110, 0.02, 0.3 + 0.05 * rank, 0.25), T(113, 0.02, 0.3 + 0.05 * rank, 0.25)]
    if rank >= 9:   # the Venerable: the sky answers
        layers += [K(50, 25, 0.8, 1.0), T(196, 0.08, 0.9, 0.18, vib=(4, 3)), T(247, 0.08, 0.9, 0.14, vib=(4, 3)),
                   T(294, 0.08, 0.9, 0.12, vib=(4, 3)), N(30, 200, 0.02, 0.7, 0.6, at=0.05)]
    x = render(layers)
    x = _reverb(x, 0.15 + 0.12 * rank, min(0.08 + 0.03 * rank, 0.35))
    return _norm(x, 0.55 + 0.04 * rank, 2.6 if rank == 9 else 0.35 + 0.12 * rank)


DAO_BELLS = {1: [1200], 2: [1350], 3: [1500, 2250], 4: [1700, 2550], 5: [2000, 2500, 3000]}


def dao_bell(tier):
    """Dao marks I-V: a bell over the strike, brighter and fuller with every tier (kept quiet: it rings every attack)."""
    layers = [M(f, 0.12 + 0.06 * tier, 0.5, ratios=(1, 2.0, 3.01, 4.1)) for f in DAO_BELLS[tier]]
    x = _reverb(render(layers), 0.2 + 0.1 * tier, 0.15)
    return _norm(x, 0.3 + 0.04 * tier, 0.45 + 0.15 * tier)


# ---------------------------------------------------------------- the Gu catalog: a refinement sound per Gu
FORM_VOICE = {**{f: "wings" for f in ("moth", "cicada", "bat", "bird", "wing", "firefly")},
              **{f: "clicks" for f in ("beetle", "beetle_horn", "centipede", "spider", "scorpion", "worm")},
              **{f: "chime" for f in ("crystal", "orb", "lotus", "flower", "leaf", "sun", "eye", "ear")},
              **{f: "metal" for f in ("blade", "sword", "rod", "fang", "hammer", "gong", "shell", "fist", "bone", "drill")},
              **{f: "flow" for f in ("cloud", "wheel", "serpent", "flame", "web", "scroll", "mask", "puppet")}}


def gu_awaken(name, key, rank, form):
    """A Gu wakes in its master's aperture: its own voice (wings, clicks, a chime, ringing metal or a rushing flow),
    then its path's strike pitched to the Gu, grander with the rank; an immortal Gu adds a dao bell."""
    import zlib
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    pitch = float(rng.uniform(0.82, 1.22))
    voice = FORM_VOICE[form]
    if voice == "wings":
        layers = [T(200 * pitch, 0.01, 0.32, 0.35, vib=(26 + 6 * pitch, 45)), N(2000, 5200, 0.005, 0.25, 0.25)]
    elif voice == "clicks":
        layers = [C(40 + 30 * pitch, 1500, 5200, 0.3, 0.55), K(260 * pitch, 140 * pitch, 0.06, 0.4)]
    elif voice == "chime":
        layers = [M(900 * pitch, 0.5, 0.42, ratios=(1, 2.0, 3.01)), M(1350 * pitch, 0.4, 0.22, ratios=(1, 2.0), at=0.06)]
    elif voice == "metal":
        layers = [M(420 * pitch, 0.45, 0.5, ratios=(1.0, 2.76, 5.4)), N(1800, 6000, 0.002, 0.08, 0.35)]
    else:
        layers = [N(250, 1600, 0.06, 0.35, 0.45, lo2=900, hi2=4200)]
    head = render(layers)
    tier = 1 if rank <= 2 else 2 if rank <= 4 else 3 if rank <= 6 else 4
    body = path_hit(key, tier)
    idx = np.arange(0, len(body) - 1, pitch)
    body = np.interp(idx, np.arange(len(body)), body)
    off = int(SR * 0.14)
    x = np.zeros(max(len(head), off + len(body)))
    x[: len(head)] += head
    x[off: off + len(body)] += 0.8 * body
    if rank >= 6:
        bell = dao_bell(min(5, rank - 4))
        b0 = int(SR * 0.2)
        x = np.concatenate([x, np.zeros(max(0, b0 + len(bell) - len(x)))])
        x[b0: b0 + len(bell)] += 0.7 * bell
    return _norm(x, 0.6 + 0.03 * rank, 1.0 + 0.12 * rank)


def combo_strike(name, key_a, key_b, rank):
    """A combination killer move: a rising swell, the first Gu's path strike, then the second's on top a beat later;
    immortal moves (rank 6+) add a deep drop and a dao bell."""
    import zlib
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    swell = 0.18 + 0.03 * min(rank, 6)
    rise = render([N(200, 3000, swell, 0.02, 0.6, lo2=600, hi2=7000)], extra=swell)[: int(SR * swell)]
    rise *= np.linspace(0, 1, len(rise)) ** 2
    tier = 2 if rank <= 3 else 3 if rank <= 5 else 4
    a, b = path_hit(key_a, tier), path_hit(key_b, tier)
    pitch = float(rng.uniform(0.9, 1.12))
    b = np.interp(np.arange(0, len(b) - 1, pitch), np.arange(len(b)), b)
    off = int(SR * 0.11)
    hit = np.zeros(max(len(a), off + len(b)))
    hit[: len(a)] += a
    hit[off: off + len(b)] += 0.85 * b
    if rank >= 6:
        drop = render([T(80, 0.01, 0.5, 0.8, f2=28)])
        hit[: len(drop)] += 0.6 * drop[: len(hit)]
        bell = dao_bell(min(5, rank - 4))
        hit = np.concatenate([hit, np.zeros(max(0, off + len(bell) - len(hit)))])
        hit[off: off + len(bell)] += 0.5 * bell
    return _norm(np.concatenate([rise, hit]), 0.9 if rank >= 6 else 0.85, 2.4 if rank >= 6 else 1.8)


# ---------------------------------------------------------------- names and files
import sys as _sys  # noqa: E402
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sound_names import dao_sound, move_sound, path_sound, rank_sound  # noqa: E402,F401


def all_sounds():
    """{file name: callable returning float samples in -1..1}."""
    out = {}
    for key in PATHS:
        for t in range(1, 5):
            out[path_sound(key, t)] = (lambda k=key, t=t: path_hit(k, t))
        out[move_sound(key, False)] = (lambda k=key: killer_move(k, False))
        out[move_sound(key, True)] = (lambda k=key: killer_move(k, True))
    for r in range(1, 10):
        out[rank_sound(r)] = (lambda r=r: rank_body(r))
    for t in range(1, 6):
        out[dao_sound(t)] = (lambda t=t: dao_bell(t))
    import gu_catalog
    for r in gu_catalog.ROWS:
        if int(r["rank"]) < 6:
            out[gu_catalog.sound(r["name"])] = (lambda r=r: gu_awaken(r["name"], r["path"], int(r["rank"]), r["form"]))
    for g in gu_catalog.all_immortal():   # immortal Gu: one of a kind, heard when its bearer takes it up
        b = gu_catalog.bearer(g["name"])
        out[gu_catalog.sound(b)] = (lambda g=g: gu_awaken(g["name"], g["path"], int(g["rank"]), g["form"]))
    import gu_combos
    for r in gu_combos.rows():
        out[gu_combos.sound(r["name"])] = (lambda r=r: combo_strike(r["name"], *gu_combos.paths_of(r), gu_combos.rank(r)))
    return out


def _wav_bytes(x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)
    return b.getvalue()


def encode_ogg(x, dest: Path):
    """Ogg Vorbis, mono 22 kHz, bit-exact (no encoder tags) so a rebuild leaves unchanged files unchanged."""
    if not shutil.which("ffmpeg"):
        raise SystemExit("[sfx] ffmpeg is needed to encode the sounds (Ogg Vorbis)")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "wav", "-i", "pipe:0",
                        "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact",
                        "-c:a", "libvorbis", "-q:a", "2", "-ac", "1", "-ar", str(SR), "-f", "ogg", "pipe:1"],
                       input=_wav_bytes(x), capture_output=True)
    if r.returncode:
        raise SystemExit(f"[sfx] ffmpeg failed for {dest.name}: {r.stderr.decode()[:300]}")
    if dest.exists() and dest.read_bytes() == r.stdout:
        return 0
    dest.write_bytes(r.stdout)
    return 1


def build(mod: Path, only: set[str] | None = None) -> int:
    folder = mod / "sounds"
    folder.mkdir(exist_ok=True)
    written = 0
    names = all_sounds()
    for name, make in names.items():
        if only and name not in only:
            continue
        global RNG
        RNG = np.random.default_rng(sum(map(ord, name)) * 7919 + len(name))   # reproducible per sound
        written += encode_ogg(make(), folder / f"{name}.ogg")
    for stale in folder.glob("*.ogg"):   # sounds no longer generated
        if stale.stem not in names:
            stale.unlink()
            written += 1
    return written


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from common import REPO_ROOT
    print(f"[sfx] wrote {build(REPO_ROOT)} sound(s) to sounds/")
