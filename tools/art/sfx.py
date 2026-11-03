"""Original sound effects, synthesized from code with Chinese instrument models (numpy; ffmpeg encodes Ogg Vorbis).
Nothing is sampled or copied.

The user (2026-11-02): "sesuaikan sfx nya juga dan pas sesuai dengan serangan-serangannya"; then (2026-11-03): better,
clearer and still readable, in the voice of Chinese instruments. Unciv picks a unit's attack sound by unit, never by
promotion [src BattleTable: UncivSound(unit name), else attackSound], but any triggerable can "Play [name] sound" for
a human player [src UniqueTriggerActivation PlaySound: skipped for the AI]. So an attack layers up to three sounds:

  low   gu-rank-<1..9>          the blow: a tanggu drum for mortals, growing to the great dagu; immortals add a gong,
                                the Venerable a gong and a chord of bronze bells (attackSound)
  mid   path-<key>-<1..4>       the path's own instrument (47 recipes: guqin, pipa, dizi, xiao, erhu, bells, chimes,
                                gongs, cymbals, drums, woodblocks); each attainment tier adds an echo strike
                                (Grandmaster), a great drum and a hall (Great Grandmaster), a gong and a shimmer of
                                bells (Supreme Grandmaster). Only the highest tier held plays.
  high  dao-<1..5>              dao marks: bianzhong bells, one small bell at I to a three-bell chord at V
  move  move-<key>[-immortal]   a killer move: a cymbal roll swelling into the path's strike, the immortal one with a
                                great gong

The instruments are physical or additive models: Karplus-Strong strings with a wooden body (guqin, pipa), additive
winds with breath and the dizi's membrane buzz, a bowed erhu with formants, inharmonic bronze (bianzhong two-tone bells,
gongs that bend in pitch, cymbals), membranes (tanggu, dagu) and woodblocks. Melodic notes keep to the pentatonic
scale. Every sound gets a hall reverb, a low cut, a soft limiter and a loudness set per kind (RMS), so they are clean,
never harsh, and sit at even volumes.

Usage: python3 -m art.sfx from tools/ (or tools/gen_art.py, which calls build()).
"""
from __future__ import annotations

import io
import math
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 32000
RNG = np.random.default_rng(20261103)
PENTA = [1.0, 9 / 8, 5 / 4, 3 / 2, 5 / 3]   # gong, shang, jue, zhi, yu


def note(base: float, step: int) -> float:
    """The step-th note of the pentatonic scale above base (steps past 4 climb octaves)."""
    return base * PENTA[step % 5] * 2 ** (step // 5)


# ---------------------------------------------------------------- building blocks (each returns samples)
def _t(n):
    return np.arange(n) / SR


def _env(n, a, d, at=0.0):
    t = _t(n) - at
    tt = np.maximum(t, 0)
    return np.where(t < 0, 0.0, (1 - np.exp(-tt / max(a, 1e-4))) * np.exp(-tt / max(d, 1e-4)))


def _lp(x, cutoff):
    """One-pole low-pass (vectorised through the FFT: a gentle 6 dB/octave roll-off)."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(np.fft.rfft(x) / np.sqrt(1 + (f / cutoff) ** 2), n)


def _hp(x, cutoff):
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    h = (f / cutoff) / np.sqrt(1 + (f / cutoff) ** 2)
    return np.fft.irfft(np.fft.rfft(x) * h, n)


def _band(n, lo, hi, lo2=None, hi2=None):
    """White noise band-passed frame by frame, the band sweeping to (lo2, hi2)."""
    lo2, hi2 = lo2 or lo, hi2 or hi
    frame, hop = 512, 256
    x = RNG.standard_normal(n + frame)
    out = np.zeros(n + frame)
    win = np.hanning(frame)
    freqs = np.fft.rfftfreq(frame, 1 / SR)
    for k in range(max(1, (n + hop - 1) // hop)):
        s = k * hop
        frac = min(1.0, s / max(n, 1))
        a, b = lo * (lo2 / lo) ** frac, hi * (hi2 / hi) ** frac
        mask = 1 / (1 + np.exp(-(freqs - a) / (0.1 * a + 20))) / (1 + np.exp((freqs - b) / (0.1 * b + 20)))
        out[s:s + frame] += np.fft.irfft(np.fft.rfft(x[s:s + frame] * win) * mask, frame) * win
    out = out[:n]
    return out / (np.max(np.abs(out)) + 1e-9)


def _phase(freq):
    return 2 * math.pi * np.cumsum(freq) / SR


def string(f, d, bright=0.5, n=None, body=True):
    """A plucked string (Karplus-Strong): bright 0 is a guqin's warm silk string, 1 a pipa's sharp pluck; the wooden
    body adds three soft resonances."""
    n = n or int(SR * (d * 3 + 0.05))
    period = max(2, int(round(SR / f)))
    exc = RNG.uniform(-1, 1, period)
    exc = _lp(np.concatenate([exc, np.zeros(period)]), 1200 + 6000 * bright)[:period]
    pos = max(1, int(period * (0.12 + 0.1 * (1 - bright))))
    exc = exc - np.roll(exc, pos)                                  # where the finger plucks
    out = np.zeros(n)
    buf = exc.copy()
    loss = math.exp(-period / (SR * max(d, 1e-3)))
    mix = 0.5 - 0.3 * bright                                       # brighter: less smoothing per round
    p = 0
    while p < n:
        seg = min(period, n - p)
        out[p:p + seg] = buf[:seg]
        buf = loss * ((1 - mix) * buf + mix * np.roll(buf, -1))
        p += period
    if body:
        t = _t(160 * SR // 1000)
        ir = sum(np.sin(2 * math.pi * fr * t) * np.exp(-t / dc) * g for fr, dc, g in
                 ((190, 0.05, 1.0), (360, 0.035, 0.6), (560, 0.025, 0.4)))
        out = out + 0.35 * np.convolve(out, ir / np.sum(np.abs(ir)), mode="full")[:n]
    return out / (np.max(np.abs(out)) + 1e-9)


def wind(f, d, a=0.05, n=None, breath=0.15, buzz=0.0, vib=(5.5, 0.012), slide=None):
    """A bamboo flute: a few harmonics, vibrato, breath noise and (dizi) the membrane's buzz; `slide` glides the pitch
    from f*slide to f in the first 120 ms."""
    n = n or int(SR * (a + d * 3 + 0.05))
    t = _t(n)
    freq = np.full(n, float(f))
    if slide:
        freq *= 1 + (slide - 1) * np.exp(-t / 0.04)
    freq *= 1 + vib[1] * np.sin(2 * math.pi * vib[0] * t) * np.clip(t / 0.15, 0, 1)
    ph = _phase(freq)
    tone = sum(g * np.sin(k * ph) for k, g in ((1, 1.0), (2, 0.42), (3, 0.2), (4, 0.09), (5, 0.04)))
    if buzz:
        tone = tone + buzz * np.tanh(3 * sum(np.sin(k * ph) / k for k in range(3, 9)))
    env = _env(n, a, d)
    noise = _band(n, f * 1.5, min(f * 6, SR / 2 - 200)) * breath
    chiff = _band(n, 1500, 6000) * np.exp(-t / 0.02) * 0.25
    return (tone * env + noise * env * 0.8 + chiff) / 1.6


def erhu(f, d, a=0.06, n=None, slide=1.0, vib=(6.0, 0.02)):
    """A bowed erhu: additive harmonics shaped by the snake-skin body's formants, a slow bow attack, vibrato and a
    slide into the note."""
    n = n or int(SR * (a + d * 3 + 0.05))
    t = _t(n)
    freq = f * (1 + (slide - 1) * np.exp(-t / 0.08)) * (1 + vib[1] * np.sin(2 * math.pi * vib[0] * t) * np.clip(t / 0.2, 0, 1))
    ph = _phase(freq)
    out = np.zeros(n)
    for k in range(1, 24):
        fk = f * k
        if fk > SR / 2 - 500:
            break
        formant = sum(g * math.exp(-((fk - c) / w) ** 2) for c, w, g in ((650, 260, 1.0), (1400, 420, 0.6), (2600, 700, 0.3)))
        out += (1 / k) * (0.25 + formant) * np.sin(k * ph)
    bow = _band(n, 2000, 6000) * 0.04
    return (out + bow) * _env(n, a, d) / 2.2


def bronze(f, d, ratios, n=None, bend=0.0, strike=0.3, beat=0.0, decays=None):
    """Inharmonic bronze: partials at f*ratio, higher ones dying faster; `bend` glides every partial (an opera gong's
    swoop), `beat` detunes pairs into a slow shimmer, `strike` is the mallet's noise."""
    n = n or int(SR * (d * 4 + 0.05))
    t = _t(n)
    glide = 1 + bend * (1 - np.exp(-t / 0.25))
    out = np.zeros(n)
    for k, r in enumerate(ratios):
        fk = f * r
        if fk > SR / 2 - 400:
            continue
        dk = (decays[k] if decays else d / (1 + 0.45 * k))
        amp = 1 / (1 + 0.35 * k)
        ph = _phase(fk * glide)
        part = np.sin(ph + k)
        if beat:
            part = 0.5 * (part + np.sin(_phase(fk * (1 + beat) * glide) + 2 * k))
        out += amp * part * np.exp(-t / dk)
    out += strike * _band(n, 800, 9000) * np.exp(-t / 0.012)
    return out / (np.max(np.abs(out)) + 1e-9)


BELL = (0.5, 1.0, 1.19, 1.5, 2.0, 2.42, 3.0, 4.07)          # bianzhong: hum, strike tone, the minor-third side tone, ...
GONG = (1.0, 1.52, 2.03, 2.61, 3.32, 4.17, 5.08)
CHIME = (1.0, 2.76, 5.4, 8.93)                               # a stone chime (qing) or a small bar
CYMBAL = tuple(1 + 0.37 * k + 0.11 * k * k for k in range(14))


def bell(f, d=1.2):
    return bronze(f, d, BELL, strike=0.15, beat=0.0015, decays=[d * 1.4, d, d * 0.8, d * 0.5, d * 0.45, d * 0.3, d * 0.22, d * 0.15])


def gong(f, d=1.6, bend=-0.06):
    """bend < 0: the great gong (daluo) sinking; > 0: the small gong (xiaoluo) rising."""
    return bronze(f, d, GONG, bend=bend, strike=0.35, beat=0.004)


def chime(f, d=0.5):
    return bronze(f, d, CHIME, strike=0.05)


def cymbal(d=0.5, f=420.0, n=None):
    """Nao/bo cymbals: dense bronze partials over a bright noise."""
    n = n or int(SR * (d * 3 + 0.05))
    t = _t(n)
    metal = bronze(f, d, CYMBAL, n=n, strike=0.0, beat=0.006)
    hiss = _band(n, 3000, 12000) * np.exp(-t / (d * 0.8))
    x = 0.6 * metal + 0.7 * hiss + 0.5 * _band(n, 900, 5000) * np.exp(-t / 0.03)
    return x / (np.max(np.abs(x)) + 1e-9)


def drum(f0, f1, d, n=None, skin=0.35, size=1.0):
    """A tanggu (size 1) or the great dagu (size 2): a membrane thump falling from f0 to f1, the skin's slap."""
    n = n or int(SR * (d * 4 + 0.05))
    t = _t(n)
    freq = f1 + (f0 - f1) * np.exp(-t / (0.03 * size))
    body = (np.sin(_phase(freq)) * np.exp(-t / d) + 0.4 * np.sin(_phase(freq * 1.5)) * np.exp(-t / (d * 0.5))
            + 0.25 * np.sin(_phase(freq * 2.3)) * np.exp(-t / (d * 0.3)))   # overtones a small speaker can play
    slap = _band(n, 300 / size, 3000 / size) * np.exp(-t / (0.015 * size)) * skin
    x = body + slap
    return x / (np.max(np.abs(x)) + 1e-9)


def woodblock(f, d=0.04, n=None):
    """A muyu / bangzi woodblock: two quickly damped modes and a click."""
    n = n or int(SR * 0.25)
    t = _t(n)
    x = np.sin(2 * math.pi * f * t) * np.exp(-t / d) + 0.4 * np.sin(2 * math.pi * f * 2.7 * t) * np.exp(-t / (d * 0.5))
    x += 0.3 * _band(n, 2000, 8000) * np.exp(-t / 0.004)
    return x / (np.max(np.abs(x)) + 1e-9)


def swish(d, lo, hi, lo2, hi2, a=0.01, n=None):
    """Air cut by a blade or a sleeve: a band of noise sweeping."""
    n = n or int(SR * (a + d * 3 + 0.05))
    return _band(n, lo, hi, lo2, hi2) * _env(n, a, d)


def drops(f, count, gap, d=0.05):
    """Water drops or bubbles: short sine chirps rising."""
    n = int(SR * (gap * count + d * 5))
    out = np.zeros(n)
    for k in range(count):
        s = int(SR * k * gap)
        m = int(SR * d * 4)
        t = _t(m)
        fk = f * (1 + 0.15 * (k % 3))
        out[s:s + m] += np.sin(_phase(fk * (1 + 1.4 * (1 - np.exp(-t / 0.012))))) * np.exp(-t / d)
    return out


def crackle(d, rate=90.0, n=None):
    """Fire: random clicks in a warm band."""
    n = n or int(SR * d * 3)
    imp = (RNG.random(n) < rate / SR).astype(float) * RNG.uniform(0.3, 1.0, n)
    tick = _band(256, 1200, 6000) * np.hanning(256)
    return np.convolve(imp, tick, mode="same") * np.exp(-_t(n) / d)


# ---------------------------------------------------------------- mixing
class Mix:
    """Events placed in time; render() sums them."""

    def __init__(self):
        self.parts = []

    def add(self, sig, at=0.0, g=1.0):
        self.parts.append((int(at * SR), sig * g))
        return self

    def render(self) -> np.ndarray:
        if not self.parts:
            return np.zeros(1)
        n = max(s + len(x) for s, x in self.parts)
        out = np.zeros(n)
        for s, x in self.parts:
            out[s:s + len(x)] += x
        return out


def hall(x, seconds=1.2, wet=0.25, pre=0.015):
    """A hall: early reflections, then a smooth tail whose highs die first."""
    if seconds <= 0 or wet <= 0:
        return x
    m = int(SR * seconds)
    rng = np.random.default_rng(len(x) + m)
    t = _t(m)
    lowtail = _lp(rng.standard_normal(m), 2500) * np.exp(-t / (seconds / 5.5))
    hightail = _hp(rng.standard_normal(m), 2500) * np.exp(-t / (seconds / 11))
    ir = lowtail + 0.5 * hightail
    for dt, g in ((0.011, 0.5), (0.019, 0.35), (0.027, 0.3), (0.041, 0.2)):
        ir[int(dt * SR)] += g * 4
    ir = np.concatenate([np.zeros(int(pre * SR)), ir])
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    size = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:len(x) + len(ir)]
    y *= (np.sqrt(np.mean(x ** 2)) + 1e-9) / (np.sqrt(np.mean(y[:len(x)] ** 2)) + 1e-9)
    out = np.zeros(len(y))
    out[:len(x)] = x
    return out + wet * y


def finish(x, rms_db, cap, peak=0.94):
    """Low cut, loudness set by RMS over the sound's loud part (measured above 180 Hz, as a phone speaker plays it), a
    soft limiter, the near-silent tail cut (at most `cap` seconds) and a fade, so game sounds stay short, even in volume
    on any speaker, and never click."""
    x = _hp(x - np.mean(x), 45)
    x = _lp(x, 9000)
    heard = _hp(x, 180)   # loudness as a phone speaker hears it: little below 200 Hz
    loud = np.abs(heard) > np.max(np.abs(heard)) * 0.05
    core = heard[loud] if loud.any() else heard
    x = x * (10 ** (rms_db / 20) / (np.sqrt(np.mean(core ** 2)) + 1e-9))
    x = peak * np.tanh(x / peak)
    keep = np.nonzero(np.abs(x) > 0.002)[0]
    end = min(len(x), (keep[-1] if len(keep) else len(x)) + int(0.02 * SR), int(cap * SR))
    x = x[:end].copy()
    fade = min(int(0.06 * SR), len(x))
    x[-fade:] *= np.linspace(1, 0, fade) ** 2
    return x


# ---------------------------------------------------------------- the 47 paths' instruments
D4 = 293.66   # the paths' tonic (the pentatonic on D)


def path_core(key: str) -> np.ndarray:
    """One strike in the path's own voice."""
    m = Mix()
    k = key
    if k == "strength":
        m.add(drum(110, 52, 0.22, size=2), g=1.0).add(gong(140, 0.5, -0.04), at=0.02, g=0.35)
    elif k == "transformation":
        m.add(erhu(note(D4, 2), 0.25, slide=0.7), g=0.8).add(swish(0.12, 1500, 5000, 600, 2000), at=0.05, g=0.35)
    elif k == "bone":
        for i, f in enumerate((1250, 980, 1400)):
            m.add(woodblock(f, 0.03), at=i * 0.045, g=0.7)
        m.add(string(note(D4, 0), 0.12, bright=0.9), at=0.02, g=0.35)
    elif k == "blood":
        m.add(drum(80, 45, 0.16), g=1.0).add(drum(80, 45, 0.14), at=0.24, g=0.75).add(erhu(D4 / 2, 0.3, slide=0.85), g=0.3)
    elif k == "sword":
        m.add(swish(0.09, 2500, 7000, 4500, 10000), g=0.6).add(string(note(D4, 7), 0.35, bright=1.0), at=0.03, g=0.55)
        m.add(chime(note(D4, 12), 0.3), at=0.03, g=0.3)
    elif k == "blade":
        m.add(swish(0.12, 900, 4000, 2000, 7000), g=0.6).add(string(note(D4, 3), 0.25, bright=0.9), at=0.04, g=0.5)
        m.add(gong(520, 0.25, 0.03), at=0.04, g=0.3)
    elif k == "metal":
        m.add(bell(note(D4, 0), 0.6), g=0.8).add(cymbal(0.12), g=0.25)
    elif k == "weapon":
        for i in range(3):
            m.add(cymbal(0.05, 600 + 80 * i), at=i * 0.06, g=0.45)
        m.add(bell(note(D4, 5), 0.3), at=0.12, g=0.4)
    elif k == "killing":
        m.add(cymbal(0.18, 360), g=0.55).add(erhu(D4 / 2, 0.3, slide=1.2), at=0.02, g=0.45)
    elif k == "fire":
        m.add(crackle(0.35, 140), g=0.6).add(cymbal(0.35, 300), at=0.03, g=0.3).add(drum(90, 50, 0.15), g=0.5)
    elif k == "water":
        m.add(string(note(D4, 5), 0.6, bright=0.2), g=0.6).add(drops(900, 4, 0.06), at=0.05, g=0.45)
    elif k == "wood":
        m.add(woodblock(720, 0.05), g=0.8).add(string(note(D4, 3), 0.5, bright=0.25), at=0.03, g=0.5)
    elif k == "earth":
        m.add(drum(70, 38, 0.35, size=2), g=1.0).add(swish(0.25, 40, 300, 40, 200), g=0.5)
    elif k == "wind":
        m.add(wind(note(D4, 7), 0.22, a=0.04, breath=0.45, buzz=0.12, slide=0.8), g=0.6)
        m.add(swish(0.25, 400, 1500, 900, 3500, a=0.06), g=0.5)
    elif k == "cloud":
        m.add(wind(note(D4, 5), 0.35, a=0.12, breath=0.5), g=0.55).add(swish(0.35, 200, 900, 400, 1500, a=0.1), g=0.3)
    elif k == "ice":
        m.add(chime(note(D4, 14), 0.4), g=0.6).add(chime(note(D4, 17), 0.3), at=0.05, g=0.4)
        m.add(swish(0.03, 5000, 11000, 5000, 11000, a=0.001), g=0.35)
    elif k == "lightning":
        m.add(cymbal(0.12, 500), g=0.6).add(swish(0.02, 2000, 11000, 2000, 11000, a=0.0005), g=0.7)
        zap = np.sin(_phase(np.geomspace(1800, 90, int(SR * 0.22)))) * np.exp(-_t(int(SR * 0.22)) / 0.08)
        m.add(zap, g=0.45)
    elif k == "poison":
        m.add(swish(0.25, 4000, 10000, 3000, 8000, a=0.05), g=0.35).add(drops(320, 3, 0.09, 0.06), at=0.06, g=0.5)
        m.add(erhu(note(D4, 1), 0.25, slide=1.15), at=0.02, g=0.3)
    elif k == "light":
        for i, s in enumerate((7, 9, 11)):
            m.add(bell(note(D4, s), 0.5), at=i * 0.02, g=0.45)
    elif k == "dark":
        m.add(gong(D4 / 4, 0.6, -0.08), g=0.8).add(erhu(D4 / 2, 0.35, a=0.1, slide=0.9), g=0.3)
    elif k == "shadow":
        m.add(swish(0.08, 300, 1500, 150, 800), g=0.6).add(drum(70, 45, 0.15), at=0.03, g=0.5)
    elif k == "star":
        for i, s in enumerate((10, 12, 11, 14)):
            m.add(chime(note(D4, s), 0.25), at=i * 0.06, g=0.4)
    elif k == "moon":
        m.add(swish(0.08, 2500, 7000, 3500, 9000), g=0.45).add(wind(note(D4, 9), 0.3, a=0.03, breath=0.2), at=0.02, g=0.45)
        m.add(bell(note(D4, 9), 0.4), at=0.03, g=0.3)
    elif k == "sound":
        for i, s in enumerate((0, 3, 5)):
            m.add(string(note(D4 / 2, s), 0.6, bright=0.3), at=i * 0.02, g=0.5)
        m.add(gong(220, 0.6, 0.02), at=0.04, g=0.3)
    elif k == "illusion":
        m.add(bell(note(D4, 7), 0.5), g=0.4).add(bell(note(D4, 7) * 1.012, 0.5), at=0.03, g=0.4)
        m.add(wind(note(D4, 9), 0.3, a=0.1, breath=0.3, vib=(7, 0.03)), g=0.3)
    elif k == "wisdom":
        m.add(bell(note(D4, 5), 0.7), g=0.7).add(bell(note(D4, 7), 0.6), at=0.12, g=0.4)
    elif k == "emotion":
        m.add(erhu(note(D4, 3), 0.35, slide=0.8), g=0.6).add(drum(70, 45, 0.12), g=0.4).add(drum(70, 45, 0.1), at=0.25, g=0.3)
    elif k == "enchantment":
        m.add(chime(note(D4, 10), 0.35), g=0.45).add(string(note(D4, 5), 0.3, bright=0.7), at=0.04, g=0.4)
        m.add(string(note(D4, 7), 0.3, bright=0.7), at=0.09, g=0.35)
    elif k == "soul":
        m.add(erhu(note(D4, 2), 0.4, a=0.12, slide=1.1, vib=(5, 0.035)), g=0.6).add(swish(0.3, 800, 2500, 600, 1800, a=0.1), g=0.25)
    elif k == "dream":
        for i, s in enumerate((5, 7, 9, 10, 12)):
            m.add(string(note(D4, s), 0.4, bright=0.35), at=i * 0.045, g=0.35)
        m.add(bell(note(D4, 12), 0.5), at=0.2, g=0.25)
    elif k == "enslavement":
        m.add(drum(80, 50, 0.2), g=0.7).add(erhu(D4 / 2, 0.3, slide=0.9), g=0.3)
        for i in range(4):
            m.add(chime(2400 + 150 * i, 0.05), at=0.05 + i * 0.05, g=0.25)
    elif k == "time":
        m.add(woodblock(1300, 0.03), g=0.7).add(woodblock(950, 0.03), at=0.18, g=0.65).add(bell(note(D4, 5), 0.5), at=0.2, g=0.35)
    elif k == "space":
        m.add(gong(260, 0.6, 0.12), g=0.6).add(swish(0.25, 500, 3000, 200, 1000, a=0.04), g=0.4)
    elif k == "rule":
        m.add(bell(note(D4, 0), 0.8), g=0.8).add(drum(100, 55, 0.12), g=0.6)
    elif k == "phantom":
        m.add(swish(0.2, 400, 1500, 800, 2500, a=0.02), g=0.5).add(wind(note(D4, 4), 0.25, a=0.05, breath=0.4, vib=(8, 0.04)), g=0.35)
    elif k == "restriction":
        for i in range(3):
            m.add(chime(1800 + 100 * i, 0.07), at=i * 0.05, g=0.35)
        m.add(drum(95, 55, 0.12), at=0.16, g=0.6)
    elif k == "luck":
        for i, s in enumerate((10, 12, 14, 12, 15)):
            m.add(chime(note(D4, s), 0.15), at=i * 0.035, g=0.3)
        m.add(string(note(D4, 7), 0.3, bright=0.8), at=0.18, g=0.3)
    elif k == "heaven":
        for i, s in enumerate((0, 2, 4)):
            m.add(bell(note(D4 / 2, s), 1.0), at=i * 0.03, g=0.4)
        m.add(gong(D4 / 4, 1.0, -0.04), at=0.05, g=0.45)
    elif k == "qi":
        m.add(swish(0.25, 80, 1500, 60, 400, a=0.02), g=0.6).add(drum(75, 40, 0.18, size=2), g=0.7)
    elif k == "refinement":
        m.add(gong(330, 0.4, 0.04), g=0.5).add(crackle(0.25, 80), at=0.08, g=0.45)
    elif k == "formation":
        for i in range(3):
            m.add(drum(120 - 10 * i, 60, 0.1), at=i * 0.07, g=0.55)
        m.add(bell(note(D4, 3), 0.5), at=0.2, g=0.35)
    elif k == "food":
        m.add(woodblock(600, 0.04), g=0.6).add(woodblock(600, 0.04), at=0.12, g=0.5).add(chime(note(D4, 7), 0.3), at=0.25, g=0.3)
    elif k == "pill":
        for i in range(5):
            m.add(chime(3000 + 200 * (i % 3), 0.04), at=i * 0.03, g=0.25)
        m.add(gong(250, 0.25, 0.05), at=0.2, g=0.4)
    elif k == "information":
        for i in range(6):
            m.add(string(note(D4, 7), 0.06, bright=0.8, body=False), at=i * 0.03, g=0.35)
        m.add(chime(note(D4, 12), 0.2), at=0.2, g=0.3)
    elif k == "human":
        m.add(drum(90, 55, 0.12), g=0.6).add(erhu(note(D4, 0), 0.3, slide=0.9), at=0.02, g=0.45)
    elif k == "painting":
        m.add(swish(0.15, 1500, 5000, 800, 3000, a=0.03), g=0.45).add(string(note(D4, 4), 0.4, bright=0.3), at=0.15, g=0.45)
    elif k == "theft":
        m.add(swish(0.06, 3000, 9000, 5000, 11000), g=0.5)
        for i in range(2):
            m.add(chime(3000 + 300 * i, 0.06), at=0.05 + i * 0.05, g=0.3)
    else:
        raise KeyError(key)
    return m.render()


PATHS = ["strength", "transformation", "bone", "blood", "sword", "blade", "metal", "weapon", "killing", "fire", "water",
         "wood", "earth", "wind", "cloud", "ice", "lightning", "poison", "light", "dark", "shadow", "star", "moon",
         "sound", "illusion", "wisdom", "emotion", "enchantment", "soul", "dream", "enslavement", "time", "space",
         "rule", "phantom", "restriction", "luck", "heaven", "qi", "refinement", "formation", "food", "pill",
         "information", "human", "painting", "theft"]


def path_hit(key, tier):
    """Attainment tier 1-4: the path's voice; an echo strike (Grandmaster); a great drum and a hall (Great
    Grandmaster); a gong and a shimmer of bells with a long tail (Supreme Grandmaster)."""
    core = path_core(key)
    m = Mix().add(core)
    if tier >= 2:
        m.add(core, at=0.08, g=0.45)
    if tier >= 3:
        m.add(drum(72, 38, 0.25, size=2), g=0.6)
    if tier >= 4:
        m.add(gong(D4 / 4, 1.2, -0.05), at=0.03, g=0.45)
        for i, s in enumerate((12, 14, 17)):
            m.add(chime(note(D4, s), 0.4), at=0.1 + i * 0.04, g=0.18)
    x = hall(m.render(), (0, 0.35, 0.6, 1.0, 1.6)[tier], (0, 0.12, 0.18, 0.25, 0.32)[tier])
    return finish(x, (0, -19, -18, -17, -16)[tier], (0, 0.9, 1.1, 1.4, 1.9)[tier])


def killer_move(key, immortal):
    """A Gu attack: a cymbal roll swelling into the path's Great Grandmaster (mortal) or Supreme (immortal) strike, the
    immortal one under a great gong."""
    swell = 0.45 if immortal else 0.3
    n = int(SR * swell)
    roll = _band(n, 2500, 9000) * np.linspace(0, 1, n) ** 2
    tremolo = 0.6 + 0.4 * np.sin(2 * math.pi * 18 * _t(n))
    m = Mix().add(roll * tremolo, g=0.35)
    hit = path_hit(key, 4 if immortal else 3)
    m.add(hit, at=swell)
    if immortal:
        m.add(gong(D4 / 8, 1.8, -0.08), at=swell, g=0.55)
    return finish(m.render(), -15 if immortal else -16, 2.6 if immortal else 1.9)


def rank_body(rank):
    """The blow itself (attackSound), by rank 1-9: a tanggu growing to the great dagu; immortals add a gong; the
    Venerable a sinking great gong and a chord of bronze bells."""
    size = 1 + 0.15 * min(rank, 5)
    m = Mix().add(drum(230 - 12 * rank, 115 - 6 * rank, 0.08 + 0.025 * rank, size=size))
    m.add(string(note(D4, 3 - min(rank, 3)), 0.1 + 0.02 * rank, bright=0.9, body=False), at=0.005, g=0.25)
    if rank >= 3:
        m.add(drum(70, 40, 0.15 + 0.02 * rank, size=2), g=0.5)
    if rank >= 6:   # an immortal: the aperture's gong
        m.add(gong(D4 / 2 * (1 - 0.05 * (rank - 6)), 0.5 + 0.15 * rank, -0.05), at=0.02, g=0.45)
    if rank >= 9:   # the Venerable: the sky answers
        m.add(gong(D4 / 8, 2.4, -0.1), at=0.02, g=0.7)
        for i, s in enumerate((0, 2, 4)):
            m.add(bell(note(D4 / 2, s), 1.6), at=0.05 + i * 0.03, g=0.3)
    x = hall(m.render(), 0.25 + 0.15 * rank, min(0.1 + 0.03 * rank, 0.36))
    return finish(x, -17 + 0.4 * rank, 2.8 if rank == 9 else 0.4 + 0.13 * rank)


DAO_BELLS = {1: [9], 2: [10], 3: [10, 12], 4: [11, 13], 5: [10, 12, 14]}


def dao_bell(tier):
    """Dao marks I-V: bianzhong bells over the strike, one small bell at I to a chord of three at V (kept soft: it
    rings on every attack)."""
    m = Mix()
    for i, s in enumerate(DAO_BELLS[tier]):
        m.add(bell(note(D4, s), 0.35 + 0.08 * tier), at=i * 0.025, g=0.5)
    x = hall(m.render(), 0.4 + 0.15 * tier, 0.18)
    return finish(x, -25 + tier, 0.5 + 0.15 * tier)


# ---------------------------------------------------------------- the Gu catalog: a refinement sound per Gu
FORM_VOICE = {**{f: "wings" for f in ("moth", "cicada", "bat", "bird", "wing", "firefly")},
              **{f: "clicks" for f in ("beetle", "beetle_horn", "centipede", "spider", "scorpion", "worm")},
              **{f: "chime" for f in ("crystal", "orb", "lotus", "flower", "leaf", "sun", "eye", "ear")},
              **{f: "metal" for f in ("blade", "sword", "rod", "fang", "hammer", "gong", "shell", "fist", "bone", "drill")},
              **{f: "flow" for f in ("cloud", "wheel", "serpent", "flame", "web", "scroll", "mask", "puppet")}}


def gu_awaken(name, key, rank, form):
    """A Gu wakes in its master's aperture: its own voice (a pipa's tremolo for wings, woodblock clicks, a chime, a
    small gong, a xiao's breath), then its path's strike pitched to the Gu; an immortal Gu adds the dao bells."""
    import zlib
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    pitch = float(rng.choice([0.84, 0.94, 1.0, 1.12, 1.26]))
    voice = FORM_VOICE[form]
    head = Mix()
    if voice == "wings":
        for i in range(8):
            head.add(string(note(D4, 7) * pitch, 0.05, bright=0.7, body=False), at=i * 0.03, g=0.3 * (1 - i / 10))
    elif voice == "clicks":
        for i in range(4):
            head.add(woodblock(1100 * pitch + 90 * (i % 2), 0.025), at=i * 0.05, g=0.45)
    elif voice == "chime":
        head.add(chime(note(D4, 10) * pitch, 0.5), g=0.5).add(chime(note(D4, 12) * pitch, 0.4), at=0.06, g=0.3)
    elif voice == "metal":
        head.add(gong(380 * pitch, 0.4, 0.05), g=0.45).add(cymbal(0.06, 520 * pitch), g=0.2)
    else:
        head.add(wind(note(D4, 5) * pitch, 0.3, a=0.12, breath=0.55), g=0.45)
    tier = 1 if rank <= 2 else 2 if rank <= 4 else 3 if rank <= 6 else 4
    body = path_hit(key, tier)
    body = np.interp(np.arange(0, len(body) - 1, pitch), np.arange(len(body)), body)
    m = Mix().add(head.render()).add(body, at=0.15, g=0.8)
    if rank >= 6:
        m.add(dao_bell(min(5, rank - 4)), at=0.22, g=0.7)
    return finish(m.render(), -19 + 0.3 * rank, 1.0 + 0.12 * rank)


def combo_strike(name, key_a, key_b, rank):
    """A combination killer move: a cymbal swell, the first Gu's path strike, the second's a beat later; immortal
    moves (rank 6+) add a great gong and the dao bells."""
    import zlib
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    swell = 0.2 + 0.03 * min(rank, 6)
    n = int(SR * swell)
    roll = _band(n, 2500, 9000) * np.linspace(0, 1, n) ** 2 * (0.6 + 0.4 * np.sin(2 * math.pi * 18 * _t(n)))
    tier = 2 if rank <= 3 else 3 if rank <= 5 else 4
    a, b = path_hit(key_a, tier), path_hit(key_b, tier)
    pitch = float(rng.choice([0.94, 1.0, 1.06, 1.12]))
    b = np.interp(np.arange(0, len(b) - 1, pitch), np.arange(len(b)), b)
    m = Mix().add(roll, g=0.35).add(a, at=swell).add(b, at=swell + 0.11, g=0.85)
    if rank >= 6:
        m.add(gong(D4 / 8, 1.6, -0.08), at=swell, g=0.5).add(dao_bell(min(5, rank - 4)), at=swell + 0.11, g=0.5)
    return finish(m.render(), -15 if rank >= 6 else -16, 2.6 if rank >= 6 else 1.9)


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
    """Ogg Vorbis, mono 32 kHz, bit-exact (no encoder tags) so a rebuild leaves unchanged files unchanged."""
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


def _job(name):
    global RNG
    RNG = np.random.default_rng(sum(map(ord, name)) * 7919 + len(name))   # reproducible per sound
    return name, all_sounds()[name]()


def build(mod: Path, only: set[str] | None = None) -> int:
    import multiprocessing as mp
    folder = mod / "sounds"
    folder.mkdir(exist_ok=True)
    names = all_sounds()
    todo = [n for n in names if not only or n in only]
    written = 0
    with mp.get_context("fork").Pool(max(1, mp.cpu_count() or 2)) as pool:
        for name, x in pool.imap_unordered(_job, todo, chunksize=4):
            written += encode_ogg(x, folder / f"{name}.ogg")
    for stale in folder.glob("*.ogg"):   # sounds no longer generated
        if stale.stem not in names:
            stale.unlink()
            written += 1
    return written


if __name__ == "__main__":   # self-check: every kind renders, in range, at its loudness, within its length cap
    for nm, mk in [("path-moon-1", lambda: path_hit("moon", 1)), ("path-strength-4", lambda: path_hit("strength", 4)),
                   ("gu-rank-9", lambda: rank_body(9)), ("dao-5", lambda: dao_bell(5)), ("move-fire-immortal",
                   lambda: killer_move("fire", True))]:
        x = mk()
        assert np.all(np.isfinite(x)) and np.max(np.abs(x)) <= 0.95 and 0.1 < len(x) / SR <= 2.8, (nm, len(x) / SR)
    for key in PATHS:
        assert np.max(np.abs(path_core(key))) > 0, key
    print("sfx ok")
