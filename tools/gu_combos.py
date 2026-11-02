#!/usr/bin/env python3
"""Combination killer moves (Phase D, the user 2026-11-02: "jurus pamungkas itu terdiri dari gu² kombinasi"; decided:
about 40 curated combinations).

data/gu_combos.csv holds one row per move: two component Gu (A and B: catalog Gu or path Gu), a kind and the canon
source. The move is a unit-action button on Gu A's promotion, shown only to a unit that also holds Gu B (an action's
conditionals must apply [src UnitActionsFromUniques.getTriggerableActions]). Pressing it costs stones (mortal moves) or
the immortal essence of the move's rank (rank 6+) and one movement, and gives the unit the move's one-turn status.

* **Rank.** The move's rank is its strongest component's rank; its effect grows with that rank.
* **AI.** The AI never presses custom action buttons, so these moves are the human player's optional power
  (MOD_SPEC rule 7).
* **Look and sound.** Each move has its own icon (tools/art/guart.py `combo_icon`) and sound (tools/art/sfx.py
  `combo_strike`).

Imported by tools/gen_paths.py (statuses, translations, the PATHS.md table, the Tutorial page) and tools/gen_ruleset.py
(the action lines); numpy-free.
"""
from __future__ import annotations

import csv
import re

from common import REPO_ROOT

DATA = REPO_ROOT / "data" / "gu_combos.csv"
ROWS = list(csv.DictReader(DATA.open(encoding="utf-8", newline="")))
HIT = "<upon damaging a [Military] unit> <when attacking>"
KIND_ID = {"assault": "serbuan", "bind": "jerat", "ward": "perisai", "heal": "pemulihan", "mobility": "gerak",
           "aura": "aura", "plunder": "rampasan", "insight": "wawasan"}


def sound(name: str) -> str:
    return "combo-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def gu_info() -> dict[str, tuple[int, str]]:
    """{Gu name: (rank, path key)} for every Gu a unit can hold as a promotion."""
    import gu_catalog
    from gen_paths import PATH_GU
    out = {r["name"]: (int(r["rank"]), r["path"]) for r in gu_catalog.ROWS}
    out.update({g["name"]: (int(g["rank"]), g["path"]) for g in PATH_GU})
    return out


def rank(row: dict) -> int:
    info = gu_info()
    return max(info[row["gu_a"]][0], info[row["gu_b"]][0])


def cost(row: dict) -> tuple[str, str, str]:
    """(modifier, English, Indonesian)."""
    import gu_catalog
    r = rank(row)
    if r >= 6:
        ess = gu_catalog.ESSENCE[r]
        return f"<costs [3] [{ess}]>", f"3 {ess}", f"3 {gu_catalog.ESSENCE_ID[r]}"
    n = 10 + 5 * r
    return f"<costs [+{n} Gold] stats>", f"{n} stones", f"{n} batu"


def effects(row: dict) -> list[tuple[str, str, str]]:
    """(unique, English, Indonesian) of the move's one-turn status."""
    r, k, name = rank(row), row["kind"], row["name"]
    gain = f"<upon gaining the [{name}] status>"
    if k == "assault":
        a, d = 10 + 4 * r, 4 + 3 * r
        return [(f"[+{a}]% Strength <when attacking>", f"+{a}% when attacking", f"+{a}% saat menyerang"),
                (f"[Target Unit] takes [{d}] damage {HIT}", f"each hit deals {d} more damage",
                 f"setiap serangan memberi {d} kerusakan tambahan")]
    if k == "bind":
        from gen_paths import STATUSES
        st = next(s for s in STATUSES if s["name"] == row["status"])
        t, a = 2 + r // 4, 6 + 3 * r
        return [(f"[Target Unit] gains the [{st['name']}] status for [{t}] turn(s) {HIT}",
                 f"its hits leave the enemy {st['name']} for {t} turns", f"serangannya membuat musuh {st['name_id']} "
                 f"selama {t} giliran"),
                (f"[+{a}]% Strength <when attacking>", f"+{a}% when attacking", f"+{a}% saat menyerang")]
    if k == "ward":
        a, h = 15 + 5 * r, 5 + 3 * r
        return [(f"[+{a}]% Strength <when defending>", f"+{a}% when defending", f"+{a}% saat bertahan"),
                (f"[This Unit] heals [{h}] HP {gain}", f"heals {h} HP at once", f"langsung pulih {h} HP")]
    if k == "heal":
        h, a = 15 + 5 * r, 5 + 2 * r
        return [(f"[This Unit] heals [{h}] HP {gain}", f"heals {h} HP at once", f"langsung pulih {h} HP"),
                (f"[+{a}]% Strength", f"+{a}% strength", f"+{a}% kekuatan")]
    if k == "mobility":
        a = 8 + 3 * r
        return [(f"[This Unit] gains [2] movement {gain}", "+2 movement at once", "langsung +2 gerak"),
                (f"[+{a}]% Strength <when attacking>", f"+{a}% when attacking", f"+{a}% saat menyerang")]
    if k == "aura":
        e, a = 6 + 2 * r, 5 + 2 * r
        return [(f"[-{e}]% Strength for enemy [Military] units in adjacent [All] tiles",
                 f"enemy soldiers beside it fight {e}% weaker", f"prajurit musuh di sampingnya {e}% lebih lemah"),
                (f"[+{a}]% Strength", f"+{a}% strength", f"+{a}% kekuatan")]
    if k == "plunder":
        g, d = 20 + 5 * r, 4 + 3 * r
        return [(f"Earn [{g}]% of killed [Military] unit's [Cost] as [Gold]",
                 f"takes {g}% of a slain soldier's cost as stones", f"merampas {g}% harga prajurit yang dibunuh"),
                (f"[Target Unit] takes [{d}] damage {HIT}", f"each hit deals {d} more damage",
                 f"setiap serangan memberi {d} kerusakan tambahan")]
    if k == "insight":
        x, h = 30 + 5 * r, 5 + 2 * r
        return [(f"[+{x}]% XP gained from combat", f"{x}% more XP from combat", f"XP pertempuran {x}% lebih banyak"),
                (f"[This Unit] heals [{h}] HP {gain}", f"heals {h} HP at once", f"langsung pulih {h} HP")]
    raise KeyError(k)


def action(row: dict) -> str:
    """The button, on Gu A's promotion: shown only to a unit that also holds Gu B and is not already in the move."""
    return (f"[This Unit] gains the [{row['name']}] status for [1] turn(s) {cost(row)[0]} <requires [1] movement> "
            f"<for units with [{row['gu_b']}]> <for units without [{row['name']}]>")


def pedia(row: dict) -> tuple[str, str]:
    from gu_rules import ID_NAMES
    import gu_catalog
    names_id = {r["name"]: r["name_id"] for r in gu_catalog.ROWS}
    from gen_paths import PATH_GU
    names_id.update({g["name"]: g["name_id"] or ID_NAMES.get(g["name"], g["name"]) for g in PATH_GU})
    zh = f" ({row['chinese']})" if row["chinese"] else ""
    fx = effects(row)
    c = cost(row)
    a_id, b_id = names_id.get(row["gu_a"], row["gu_a"]), names_id.get(row["gu_b"], row["gu_b"])
    note_en = " Invented for the mod." if row["verdict"] == "INVENTED" else ""
    note_id = " Rekaan mod." if row["verdict"] == "INVENTED" else ""
    en = (f"{row['name']}{zh}, a rank-{rank(row)} combination killer move ({row['kind']}): {row['fn']}. Needs "
          f"{row['gu_a']} and {row['gu_b']} on the same unit; the button is on {row['gu_a']}. For one turn: "
          + "; ".join(e[1] for e in fx) + f". Costs {c[1]} and 1 movement.{note_en}")
    idn = (f"{row['name_id']}{zh}, jurus pamungkas kombinasi tingkat {rank(row)} ({KIND_ID[row['kind']]}): {row['fn_id']}. "
           f"Butuh {a_id} dan {b_id} pada unit yang sama; tombolnya ada di {a_id}. Selama satu giliran: "
           + "; ".join(e[2] for e in fx) + f". Biaya {c[2]} dan 1 gerak.{note_id}")
    return en, idn


def statuses() -> list[dict]:
    return [{"name": r["name"], "uniques": [e[0] for e in effects(r)]
             + [f"Play [{sound(r['name'])}] sound <upon gaining the [{r['name']}] status>"],
             "civilopediaText": [{"text": pedia(r)[0]}]} for r in ROWS]


def attach(promotions: list[dict]) -> None:
    """Add each move's button to its Gu A promotion (in place)."""
    by = {p["name"]: p for p in promotions}
    for r in ROWS:
        by[r["gu_a"]]["uniques"].append(action(r))


def translations() -> list[tuple[str, str]]:
    out = []
    for r in ROWS:
        out += [(r["name"], r["name_id"]), pedia(r)]
    return out


def tutorial_lines() -> list[tuple[str, str, dict]]:
    L = [("Combination killer moves", "Jurus pamungkas kombinasi", {"header": 2}),
         (f"{len(ROWS)} killer moves need two Gu on the same unit. When a unit holds both, a button appears among its "
          "actions: one turn of power for stones (immortal moves: immortal essence) and one movement. Only you press "
          "these buttons; the AI never does. Each move's rank is its strongest Gu's rank, and its power grows with it.",
          f"{len(ROWS)} jurus pamungkas butuh dua Gu pada unit yang sama. Bila sebuah unit memegang keduanya, sebuah "
          "tombol muncul di antara aksinya: satu giliran kekuatan dengan biaya batu (jurus abadi: esensi abadi) dan "
          "satu gerak. Hanya kamu yang menekan tombol ini; AI tidak pernah. Tingkat tiap jurus sama dengan tingkat Gu "
          "terkuatnya, dan kekuatannya tumbuh bersamanya.", {})]
    for r in sorted(ROWS, key=lambda x: (rank(x), x["name"])):
        fx, c = effects(r), cost(r)
        L.append((f"{r['name']} (rank {rank(r)}): {r['gu_a']} + {r['gu_b']}. " + "; ".join(e[1] for e in fx)
                  + f". Cost {c[1]}.",
                  f"{r['name_id']} (tingkat {rank(r)}): {r['gu_a']} + {r['gu_b']}. " + "; ".join(e[2] for e in fx)
                  + f". Biaya {c[2]}.", {}))
    return L


def doc_table() -> list[str]:
    from gen_paths import code
    lines = ["| Move | Chinese | Rank | Gu A (button) | Gu B | Kind | Button | Status uniques | Verdict | Source |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(ROWS, key=lambda x: (rank(x), x["name"])):
        st = " ".join(code(u) for u in statuses()[ROWS.index(r)]["uniques"])
        lines.append(f"| {r['name']} | {r['chinese'] or '—'} | {rank(r)} | {r['gu_a']} | {r['gu_b']} | {r['kind']} | "
                     f"{code(action(r))} | {st} | {r['verdict']} | {r['source']} |")
    return lines
