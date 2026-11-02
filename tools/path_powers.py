"""Path power scaling (the user, 2026-11-02: "powerscalling sangat jelas dan detail"): data/path_powers.csv.

Five layers make a Gu Master's power, and each one is visible in game:
  1. rank (the unit's base strength);
  2. path attainment, four stacking tiers (+10/+15/+20/+25% Strength), each unlocking a new kind of effect:
     Master the path's hit (every attack), Grandmaster a second effect (and the mortal killer move), Great
     Grandmaster a domain (and the immortal killer move), Supreme Grandmaster the path's peak;
  3. dao marks I-V (+5..+30% Strength), which also raise every path's hit: one extra line per tier on the Master,
     so the promotion screen shows what each tier adds;
  4. Gu (path Gu, immortal Gu and their dao-mark lines);
  5. conflicts between paths (dao marks interfere).
Killer moves are the family's burst plus the path's hit at full power (the AI never presses them: human power).

describe() turns each unique this module writes into short English and Indonesian text, so the civilopedia and the
Tutorial pages always say what the rules do (an unknown pattern stops the build).
"""
from __future__ import annotations

import re

DAO_TIERS = ["Dao Marks I", "Dao Marks II", "Dao Marks III", "Dao Marks IV", "Dao Marks V"]  # gen_ruleset.DAO
# Phase D power rebuild (the user, 2026-11-02: "kekuatan gu abadi maupun master tergantung gu, tapi kalo bertarung
# tanpa gu ... mengandalkan dao dan pemahaman"): a cultivator's own body is worth about 40% less (ranks 1-2 lose 25%,
# so the first wolves stay beatable); the Gu, the dao marks and the path's attainment (comprehension) carry the rest.
# data/gu_masters.csv keeps the full numbers; gen_ruleset writes the scaled ones.
BASE_SHARE = {1: 0.75, 2: 0.75, 3: 0.65, 4: 0.65, 5: 0.65}  # every other rank: DEFAULT_SHARE
DEFAULT_SHARE = 0.6
ROGUE_SHARE = 0.8  # lone and demonic Gu Masters carry Gu but no clan's comprehension (barbarians)


def body_strength(strength: int, rank: int) -> int:
    """A cultivator's strength without Gu, dao marks or comprehension."""
    return max(1, round(strength * BASE_SHARE.get(rank, DEFAULT_SHARE)))


VENERABLE_STRENGTH = body_strength(280, 9)  # gen_ruleset asserts the Venerable unit's strength
# Dao Marks I..V themselves (tools/gen_ruleset.py DAO_EFFECTS, asserted there), for the Tutorial page
DAO_STRENGTH = (["+10%", "+20%", "+30%", "+40% and +10 HP healing", "+55% and +15 HP healing"],
                ["+10%", "+20%", "+30%", "+40% dan +10 HP pemulihan", "+55% dan +15 HP pemulihan"])
# the hit's amount with no dao marks, then with dao marks I..V
SCALE = {"dmg": [4, 5, 6, 8, 10, 12], "dur": [2, 2, 2, 3, 3, 4], "heal": [5, 6, 8, 10, 12, 15], "xp": [2, 3, 4, 5, 6, 8],
         "earn": [10, 15, 20, 25, 30, 40], "movegain": [1, 1, 1, 1, 2, 2], "moveloss": [1, 1, 1, 1, 2, 2]}
# a status lasts at least two turns: it ticks at the target's own turn start, so one turn would end before the
# target moves (E7)
MAX_KINDS = {"dur"}  # reapplying a status keeps the longer timer: the tier lines carry the full value


UPON_HIT = "<upon damaging a [Military] unit>"
# a hit is the path's attack: it fires when the unit attacks, never when it is attacked (autoplay, Five Regions 6 x 350:
# with hits on defence too, besiegers took every defender's hit while cities take none; clans destroyed fell 7 -> 1)
ATTACK = "<when attacking>"


def attack_only(u: str) -> str:
    return u.replace(UPON_HIT, f"{UPON_HIT} {ATTACK}") if UPON_HIT in u and ATTACK not in u else u


def cell(pw: dict, col: str) -> list[str]:
    """A tier's uniques from data/path_powers.csv ('|'-separated), hits made attack-only."""
    return [attack_only(x) for x in pw[col].split("|") if x]


def amounts(pw: dict) -> list[int]:
    base = SCALE[pw["hit_kind"]]
    if pw["hit_kind"] in MAX_KINDS:
        return list(base)
    m = float(pw["mult"] or 1)
    return [max(1, round(v * m)) for v in base]


def hit_lines(pw: dict) -> list[str]:
    """The Master's hit: the plain line, then one line per dao-mark tier with what that tier adds (each unit holds one
    tier at a time, so exactly one tier line applies)."""
    a, tpl = amounts(pw), attack_only(pw["hit"])
    out = [tpl.replace("{n}", str(a[0]))]
    for i, d in enumerate(DAO_TIERS, 1):
        v = a[i] if pw["hit_kind"] in MAX_KINDS else a[i] - a[0]
        if (pw["hit_kind"] in MAX_KINDS and a[i] == a[0]) or v <= 0:
            continue
        out.append(f"{tpl.replace('{n}', str(v))} <for units with [{d}]>")
    return out


def move_burst(pw: dict, immortal: bool) -> str:
    """The path's hit at full power inside a killer move: dao marks V's amount, doubled for the immortal move."""
    a = amounts(pw)
    if pw["hit_kind"] in MAX_KINDS:
        n = a[5] + (2 if immortal else 0)
    else:
        n = a[5] * (2 if immortal else 1)
    return attack_only(pw["hit"]).replace("{n}", str(n))


# ---- describe: unique -> (English, Indonesian)
STATUS_ID: dict[str, str] = {}  # filled by gen_paths from data/path_statuses.csv
FILTER_ID = {"Wounded": ("wounded", "terluka"), "Beast": ("beast", "binatang"), "Hill": ("hills", "bukit"),
             "Friendly Land": ("its own land", "tanah sendiri"), "Jungle": ("jungle", "rimba"), "Forest": ("forest", "hutan"),
             "Military": ("soldier", "prajurit"), "Barbarians": ("barbarian", "barbar")}


def _f(name: str, lang: int) -> str:
    return FILTER_ID.get(name, (name.lower(), name.lower()))[lang]


PLURAL = {"Military": ("soldiers", "prajurit"), "Beast": ("beasts", "binatang")}


def _g(name: str, lang: int) -> str:
    return PLURAL.get(name, (name.lower(), name.lower()))[lang]


def _st(name: str, lang: int) -> str:
    return name if lang == 0 else STATUS_ID.get(name, name)


def _pct(v: str) -> str:
    return v if v.startswith(("+", "-")) else "+" + v


HIT = "<upon damaging a [Military] unit> <when attacking>"
R = [  # (regex, english, indonesian); groups are formatted in, s(...) for a status, f(...) for a filter
    (r"\[Target Unit\] takes \[(\d+)\] damage " + re.escape(HIT),
     "each attack deals {0} extra damage", "tiap serangan memberi {0} kerusakan tambahan"),
    (r"\[Target Unit\] takes \[(\d+)\] damage <upon entering combat>",
     "whoever fights it takes {0} damage", "siapa pun yang bertarung dengannya menerima {0} kerusakan"),
    (r"\[Target Unit\] gains the \[(.+?)\] status for \[(\d+)\] turn\(s\) " + re.escape(HIT) + r" <with \[(\d+)\]% chance>",
     "{2}% of hits inflict {s0} for {1} turns", "{2}% serangan menimbulkan {s0} selama {1} giliran"),
    (r"\[Target Unit\] gains the \[(.+?)\] status for \[(\d+)\] turn\(s\) " + re.escape(HIT),
     "each attack inflicts {s0} for {1} turns", "tiap serangan menimbulkan {s0} selama {1} giliran"),
    (r"\[Target Unit\] gains the \[(.+?)\] status for \[(\d+)\] turn\(s\) <upon entering combat>",
     "whoever fights it suffers {s0} for {1} turns", "siapa pun yang bertarung dengannya terkena {s0} selama {1} giliran"),
    (r"\[Target Unit\] loses \[(\d+)\] movement " + re.escape(HIT),
     "each attack takes {0} movement from the target", "tiap serangan merampas {0} gerak sasaran"),
    (r"\[This Unit\] heals \[(\d+)\] HP " + re.escape(HIT), "heals {0} HP with each attack", "pulih {0} HP tiap serangan"),
    (r"\[This Unit\] gains \[(\d+)\] movement " + re.escape(HIT), "gains {0} movement with each attack", "mendapat {0} gerak tiap serangan"),
    (r"\[This Unit\] gains \[(\d+)\] XP " + re.escape(HIT), "gains {0} XP with each attack", "mendapat {0} XP tiap serangan"),
    (r"\[This Unit\] heals \[(\d+)\] HP <upon defeating a \[Military\] unit>", "heals {0} HP per kill", "pulih {0} HP per korban"),
    (r"\[This Unit\] gains \[(\d+)\] XP <upon defeating a \[Military\] unit>", "{0} XP per kill", "{0} XP per korban"),
    (r"\[This Unit\] gains \[(\d+)\] movement <upon defeating a \[Military\] unit>", "{0} movement per kill", "{0} gerak per korban"),
    (r"\[This Unit\] gains the \[(.+?)\] status for \[(\d+)\] turn\(s\) <upon losing at least \[(\d+)\] HP in a single attack>",
     "after losing {2}+ HP in one blow it gains {s0} for {1} turn", "setelah kehilangan {2}+ HP dalam satu pukulan ia mendapat {s0} selama {1} giliran"),
    (r"Heals \[(\d+)\] damage if it kills a unit", "heals {0} HP per kill", "pulih {0} HP per korban"),
    (r"Earn \[(\d+)\]% of the damage done to \[Military\] units as \[Gold\]",
     "earns stones worth {0}% of the damage it deals", "mendapat batu senilai {0}% kerusakan yang diberikannya"),
    (r"Earn \[(\d+)\]% of killed \[Military\] unit's \[Cost\] as \[Gold\]",
     "earns stones worth {0}% of each slain soldier's cost", "mendapat batu senilai {0}% biaya tiap prajurit yang dibunuhnya"),
    (r"\[([+-]\d+)\]% Strength", "{p0}% strength", "{p0}% kekuatan"),
    (r"\[([+-]\d+)\]% Strength <when attacking>", "{p0}% strength when attacking", "{p0}% kekuatan saat menyerang"),
    (r"\[([+-]\d+)\]% Strength <when defending>", "{p0}% strength when defending", "{p0}% kekuatan saat bertahan"),
    (r"\[([+-]\d+)\]% Strength <vs cities>", "{p0}% strength against villages", "{p0}% kekuatan melawan desa"),
    (r"\[([+-]\d+)\]% Strength <vs \[(.+?)\] units>", "{p0}% strength against {f1} units", "{p0}% kekuatan melawan unit {f1}"),
    (r"\[([+-]\d+)\]% Strength <when below \[(\d+)\] HP>", "{p0}% strength below {1} HP", "{p0}% kekuatan di bawah {1} HP"),
    (r"\[([+-]\d+)\]% Strength <when above \[(\d+)\] movement>", "{p0}% strength with more than {1} movement left",
     "{p0}% kekuatan dengan sisa gerak lebih dari {1}"),
    (r"\[([+-]\d+)\]% Strength <when fighting in \[(.+?)\] tiles>", "{p0}% strength on {f1}", "{p0}% kekuatan di {f1}"),
    (r"\[([+-]\d+)\]% Strength <when adjacent to a \[Military\] unit>", "{p0}% strength beside a soldier",
     "{p0}% kekuatan di samping prajurit"),
    (r"\[([+-]\d+)\]% Strength <with \[(\d+)\]% chance>", "{p0}% strength in {1}% of fights", "{p0}% kekuatan pada {1}% pertarungan"),
    (r"\[([+-]\d+)\]% Strength <when fighting units from a Civilization with more Cities than you>",
     "{p0}% strength against clans with more villages", "{p0}% kekuatan melawan klan dengan lebih banyak desa"),
    (r"\[-(\d+)\]% Strength for enemy \[Military\] units in adjacent \[All\] tiles",
     "domain: enemies beside it fight {0}% weaker", "domain: musuh di sampingnya bertarung {0}% lebih lemah"),
    (r"\[\+(\d+)\]% Strength bonus for \[(.+?)\] units within \[(\d+)\] tiles",
     "domain: own {g1} within a {2}-tile radius fight {0}% harder",
     "domain: {g1} sekutu dalam radius {2} petak bertarung {0}% lebih kuat"),
    (r"All adjacent units heal \[(\d+)\] HP when healing", "domain: units beside it heal {0} HP more",
     "domain: unit di sampingnya pulih {0} HP lebih banyak"),
    (r"Before engaging in combat performs an extra ranged attack with \[(\d+)\]% of melee combat strength",
     "strikes first from range at {0}% strength", "menyerang lebih dulu dari jauh dengan {0}% kekuatan"),
    (r"\[(\d+)\] additional attacks per turn", "{0} more attack per turn", "{0} serangan tambahan per giliran"),
    (r"\[([+-]?\d+)\] Movement", "{p0} movement", "{p0} gerak"),
    (r"\[([+-]?\d+)\] Sight", "{p0} sight", "{p0} penglihatan"),
    (r"\[([+-]?\d+)\] Strength", "{p0} flat strength", "{p0} kekuatan tetap"),
    (r"\[(\d+)\] HP when healing", "+{0} HP when healing", "+{0} HP saat pulih"),
    (r"All healing effects doubled", "all healing doubled", "semua penyembuhan berlipat dua"),
    (r"Double movement in \[(.+?)\]", "double movement in {f0}", "gerak ganda di {f0}"),
    (r"\[\+(\d+)\]% XP gained from combat", "+{0}% battle XP", "+{0}% XP tempur"),
    (r"\[-(\d+)\]% Gold cost of upgrading", "upgrades cost {0}% fewer stones", "peningkatan {0}% lebih murah"),
    (r"\[-(\d+)\]% maintenance costs", "upkeep {0}% lower", "pemeliharaan {0}% lebih rendah"),
    (r"\[\+(\d+)\]% to Flank Attack bonuses", "flanking bonus +{0}%", "bonus serangan sayap +{0}%"),
    (r"May capture killed \[(.+?)\] units", "captures slain {f0} units", "menawan unit {f0} yang dibunuhnya"),
    (r"Can see invisible \[All\] units", "sees invisible units", "melihat unit tak kasatmata"),
    (r"Can move after attacking", "can move after attacking", "bisa bergerak setelah menyerang"),
    (r"Invisible to others", "invisible to others", "tak terlihat oleh pihak lain"),
    (r"Withdraws before melee combat", "slips away from melee", "menghindar dari pertarungan jarak dekat"),
    (r"Ignores Zone of Control", "ignores zones of control", "mengabaikan zona kendali"),
    (r"Ignores terrain cost", "ignores terrain cost", "mengabaikan biaya medan"),
    (r"All tiles cost 1 movement", "every tile costs 1 movement", "setiap petak hanya 1 gerak"),
    (r"Can see over obstacles", "sees over obstacles", "melihat melewati rintangan"),
    (r"Can pass through impassable tiles", "passes through impassable tiles", "menembus petak yang tak bisa dilalui"),
    (r"Destroys tile improvements when attacking", "destroys improvements when attacking",
     "menghancurkan bangunan petak saat menyerang"),
    (r"No damage penalty for wounded units", "no penalty for wounds", "tanpa penalti saat terluka"),
    (r"May travel on Water tiles without embarking", "walks on water without embarking", "berjalan di atas air tanpa naik perahu"),
    (r"Unit will heal every turn, even if it performs an action", "heals every turn, even after acting",
     "pulih setiap giliran, meski telah bertindak"),
]
_COMPILED = [(re.compile("^" + r + "$"), en, idt) for r, en, idt in R]


def _fmt(tpl: str, groups: tuple, lang: int) -> str:
    def rep(m):
        key = m.group(1)
        if key[0] == "s":
            return _st(groups[int(key[1:])], lang)
        if key[0] == "f":
            return _f(groups[int(key[1:])], lang)
        if key[0] == "p":
            return _pct(groups[int(key[1:])])
        if key[0] == "g":
            return _g(groups[int(key[1:])], lang)
        return groups[int(key)]
    return re.sub(r"\{([spfg]?\d+)\}", rep, tpl)


def describe(u: str) -> tuple[str, str]:
    if UPON_HIT in u and ATTACK not in u:   # a Slice 1 signature hit works both ways
        en, idt = describe(attack_only(u))
        return (en.replace("each attack", "each blow, attacking or defending,").replace("with each attack", "with each blow"),
                idt.replace("tiap serangan", "tiap pukulan, menyerang maupun bertahan,"))
    for rx, en, idt in _COMPILED:
        m = rx.match(u)
        if m:
            return _fmt(en, m.groups(), 0), _fmt(idt, m.groups(), 1)
    raise SystemExit(f"[path_powers] no description for: {u}")


def describe_all(cell: list[str]) -> tuple[str, str]:
    parts = [describe(u) for u in cell]
    return "; ".join(p[0] for p in parts), "; ".join(p[1] for p in parts)


def hit_summary(pw: dict) -> tuple[str, str]:
    """The hit with its dao-mark scaling, e.g. 'each attack deals 4 extra damage (dao marks I-V: 5/6/8/10/12)'."""
    a = amounts(pw)
    en, idt = describe(attack_only(pw["hit"]).replace("{n}", str(a[0])))
    tail = "/".join(str(x) for x in a[1:])
    return f"{en} (dao marks I-V: {tail})", f"{idt} (jejak dao I-V: {tail})"
