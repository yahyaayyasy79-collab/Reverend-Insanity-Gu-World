#!/usr/bin/env python3
"""Exhaustive check of the refinement ladder (MOD_SPEC pillar 2, CAPABILITIES E4/E5) in a generated ruleset.

Models the engine as read in the 4.22.8 source [src Event.triggerChoice, UnitPromotions]: a choice's uniques fire in
list order and promotion conditionals are read live. For every reachable unit state (unit type x Gu held x Killer
Moves known x each Gu food at 0/1/2 x stones) it checks, for each refining choice of the Refinement Attempt event:

  1. at most one 'gains' chance line matches (one roll per attempt, E5);
  2. the choice's Unavailable lines close exactly the states in which no 'gains' line matches (no empty attempts);
  3. firing the matching line plus the deterministic 'loses' lines after it climbs at most one rung;
  4. a successful rung never pushes a Gu food below zero (foods are read from 'Consumes [n] [resource]');
and that Refine Gu (and the Unfinished Refinement ruin, which opens the event without it) is unavailable exactly where
neither a rung nor the Liquor Worm lure is possible. A unit whose rank-2 Gu starved keeps Killer Move until the next turn
start; in that transient state everything must simply be closed.

  tools/ladder_check.py OUT_DIR        # OUT_DIR as written by tools/slice1_prototype.py
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from pathlib import Path

GAIN = re.compile(r"\[This Unit\] gains the \[(.+?)\] promotion")
LOSE = re.compile(r"\[This Unit\] loses the \[(.+?)\] promotion")
CONSUMES = re.compile(r"^Consumes \[(\d+)\] \[(.+?)\]$")
TYPES = ["Gu Master", "Moon Gu Master", "Strength Gu Master"]
# Modifiers that do not depend on the unit state modelled here (eras, buildings, HP, the careful stone reserve).
IGNORED = ("if [", "during the", "starting from the", "upon turn start", " HP", "when above [80] [Gold]",
           "when below [140] [Gold]", "when below [200] [Gold]", "when below [150] [Gold]")


def modifiers(u: str) -> list[str]:
    return re.findall(r"<([^>]*)>", u)


def holds(c: str, s: dict) -> bool:
    if c.startswith("with [") and c.endswith("% chance"):
        return True  # every roll is assumed to succeed; the checks are about which lines CAN fire
    for pattern, test in (
        (r"for \[(.+)\] units", lambda m: s["type"] == m[1]),
        (r"for units with \[(.+)\]", lambda m: m[1] in s["gu"]),
        (r"for units without \[(.+)\]", lambda m: m[1] not in s["gu"]),
        (r"(after|before) discovering \[Killer Moves\]", lambda m: s["km"] == (m[1] == "after")),
        (r"when above \[(-?\d+)\] \[(.+)\]", lambda m: s[m[2]] > int(m[1])),
        (r"when below \[(-?\d+)\] \[(.+)\]", lambda m: s[m[2]] < int(m[1])),
    ):
        m = re.fullmatch(pattern, c)
        if m:
            return test(m)
    raise ValueError(f"ladder_check does not model the modifier <{c}>")


def applies(u: str, s: dict) -> bool:
    return all(holds(c, s) for c in modifiers(u) if not any(i in c for i in IGNORED))


def closed(uniques: list[str], s: dict) -> bool:
    return any(applies(u, s) for u in uniques if u.startswith("Unavailable") and " HP>" not in u
               and "Gold]> <during" not in u)


def fire(uniques: list[str], s: dict) -> tuple[list[str], set[str]]:
    gu, fired = set(s["gu"]), []
    for u in uniques:
        g, l = GAIN.match(u), LOSE.match(u)
        if not (g or l) or not applies(u, {**s, "gu": gu}):
            continue
        if g and g[1] not in gu:
            gu.add(g[1])
            fired.append(g[1])
        elif l:
            gu.discard(l[1])
    return fired, gu


def reachable(t: str, gu: set[str], km: bool) -> bool:
    """Unit states the ladder can actually produce (the round-2 plan in docs/LORE_MAPPING.md)."""
    rank_two = {"White Boar Gu", "Black Boar Gu", "White Jade Gu", "Moon Raiment", "Killer Move"}
    if t == "Gu Master" and gu & rank_two:
        return False
    if t != "Gu Master" and "Liquor Worm" in gu:
        return False
    if t == "Moon Gu Master" and gu & {"White Boar Gu", "Black Boar Gu", "White Jade Gu"}:
        return False
    if t == "Strength Gu Master" and "Moon Raiment" in gu:
        return False
    if "White Jade Gu" in gu and gu & {"White Boar Gu", "Jade Skin Gu"}:
        return False
    if "Moon Raiment" in gu and gu & {"Moonlight Gu", "Jade Skin Gu"}:
        return False
    if "Killer Move" in gu and not km:
        return False
    return True


def transient(gu: set[str]) -> bool:
    """Killer Move whose rank-2 Gu starved: it is removed at the next turn start."""
    return "Killer Move" in gu and not gu & {"White Jade Gu", "Moon Raiment"}


def check(mod_root: Path) -> tuple[int, list[str]]:
    jsons = Path(mod_root) / "jsons"
    events = {e["name"]: e for e in json.loads((jsons / "Events.json").read_text(encoding="utf-8"))}
    promos = {p["name"]: p for p in json.loads((jsons / "UnitPromotions.json").read_text(encoding="utf-8"))}
    choices = events["Refinement Attempt"]["choices"]
    refining = [c for c in choices if any(GAIN.match(u) and "Liquor Worm" not in u for u in c["uniques"])]
    lure = next(c for c in choices if any(GAIN.match(u) and "[Liquor Worm]" in u for u in c["uniques"]))
    refine_gu = promos["Refine Gu"]["uniques"]
    ruins = {r["name"]: r for r in json.loads((jsons / "Ruins.json").read_text(encoding="utf-8"))}
    ruin = next((r["uniques"] for r in ruins.values() if "Triggers a [Refinement Attempt] event" in r["uniques"]), None)
    eats = {name: {m[2]: int(m[1]) for u in p.get("uniques", []) if (m := CONSUMES.match(u))}
            for name, p in promos.items()}
    foods = sorted({r for d in eats.values() for r in d})
    ladder_gu = sorted({g[1] for c in refining for u in c["uniques"] if (g := GAIN.match(u) or LOSE.match(u))}
                       | {"Black Boar Gu", "Liquor Worm"})

    def eaten(gu: set[str]) -> dict[str, int]:
        total: dict[str, int] = {}
        for g in gu:
            for r, n in eats.get(g, {}).items():
                total[r] = total.get(r, 0) + n
        return total

    errors, states = [], 0
    for t, bits, km in itertools.product(TYPES, itertools.product([0, 1], repeat=len(ladder_gu)), (False, True)):
        gu = {g for g, b in zip(ladder_gu, bits) if b}
        if not reachable(t, gu, km):
            continue
        for amounts, gold in itertools.product(itertools.product([0, 1, 2], repeat=len(foods)), (0, 1000)):
            s = {"type": t, "gu": gu, "km": km, "Gold": gold, **dict(zip(foods, amounts))}
            states += 1
            if transient(gu):
                if not all(closed(u, s) for u in [c["uniques"] for c in refining] + [refine_gu] + ([ruin] if ruin else [])):
                    errors.append(f"a starved Killer Move state is not closed: {s}")
                continue
            for c in refining:
                gains = [u for u in c["uniques"] if GAIN.match(u) and applies(u, s)]
                if len(gains) > 1:
                    errors.append(f"two chance lines match ({c['text']}): {s} {gains}")
                if closed(c["uniques"], s) != (not gains):
                    errors.append(f"Unavailable does not match the ladder ({c['text']}): {s} {gains}")
                if gains:
                    fired, after = fire(c["uniques"], s)
                    if len(fired) > 1:
                        errors.append(f"two rungs in one attempt ({c['text']}): {s} {fired}")
                    before_eat, after_eat = eaten(gu), eaten(after)
                    for r in foods:
                        if after_eat.get(r, 0) - before_eat.get(r, 0) > s[r]:
                            errors.append(f"a rung overdraws {r} ({c['text']}): {s} {fired}")
            rung = any(GAIN.match(u) and applies(u, s) for c in refining for u in c["uniques"])
            can_lure = all(applies(u, s) for u in lure["uniques"] if u.startswith("Only available"))
            if closed(refine_gu, s) != (not rung and not can_lure):
                errors.append(f"Refine Gu availability is wrong: {s} rung={rung} lure={can_lure}")
            if ruin is not None and closed(ruin, s) != closed(refine_gu, s):
                errors.append(f"the refinement ruin and Refine Gu disagree: {s}")
    return states, errors


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.exit("usage: ladder_check.py OUT_DIR")
    states, errors = check(Path(argv[0]))
    for e in errors[:50]:
        print("ERROR", e)
    print(f"[ladder_check] {states} unit states, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
