"""The Gu promotion rules shared by tools/gen_ruleset.py (data/gu.csv) and tools/gen_paths.py (data/path_gu.csv).

R3 hunger meter (the user's design). A Gu whose food is in deficit is first WEAKENED: its effects carry
<when above [-1] [food]> and switch off (the engine adds its own -25% missing-resource malus [src BattleDamage]).
At the first turn start in deficit the unit gets a timed hunger status (one per food); if the food is still short when
the status runs out, the Gu dies with the death chance of data/hunger.csv (R4, the user's option B: no mass death,
because the civ's resource count is not refreshed between units [src]); a survivor gets the status again at the next
turn start. The status is removed early, harmlessly, once the food is back. Statuses tick down at the end of
startTurn, after the triggers [src UnitTurnManager.startTurn], so a status of N turns runs out at the (N-1)th turn
start after the first. The roll is seeded per unit (name, tile, movement) and turn [src
Conditionals.getStateBasedRandom, GameContext.hashCode].
"""
from __future__ import annotations

import csv

from common import REPO_ROOT

DATA = REPO_ROOT / "data"


def table(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def items(cell: str) -> list[str]:
    """A list cell: entries separated by '|' (no unique contains that character)."""
    return [x for x in cell.split("|") if x] if cell else []


HUNGER = {r["food"]: r["hunger_status"] for r in table("gu_foods.csv")}
HUNGER_RANKS = {int(r["rank"]): (int(r["status_turns"]), int(r["death_chance"])) for r in table("hunger.csv")}


def fed(unique: str, food: str) -> str:
    """The Gu's effect works only while its food is not in deficit (WEAKENED otherwise)."""
    return f"{unique} <when above [-1] [{food}]>"


def hunger(gu: str, food: str, rank: int) -> list[str]:
    status = HUNGER[food]
    turns, chance = HUNGER_RANKS[rank]
    return [f"[This Unit] gains the [{status}] status for [{turns}] turn(s) <upon turn start> <when below [0] [{food}]> <for units without [{status}]>",
            f"[This Unit] loses the [{gu}] promotion <upon losing the [{status}] status> <when below [0] [{food}]> "
            f"<with [{chance}]% chance>"]


def gu_promotion(r: dict) -> dict:
    """A Gu that eats a Gu food: effects work only while fed (fed()), then the food, the hunger meter, the extras."""
    return {"name": r["name"], "uniques": [fed(e, r["food"]) for e in items(r["effects"])]
            + [f"Consumes [{r['eats']}] [{r['food']}]"] + hunger(r["name"], r["food"], int(r["rank"]))
            + items(r.get("extra_uniques", ""))}
