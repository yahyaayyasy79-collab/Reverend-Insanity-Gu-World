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


HUNGER = {r["food"]: r["hunger_status"] for r in table("gu_foods.csv")}  # legacy single statuses (old saves)
HUNGER_RANKS = {int(r["rank"]): (int(r["status_turns"]), int(r["death_chance"])) for r in table("hunger.csv")}
ID_NAMES = {r["key"]: r["id"] for r in table("translations_id.csv")}


def fed(unique: str, food: str) -> str:
    """The Gu's effect works only while its food is not in deficit (WEAKENED otherwise)."""
    return f"{unique} <when above [-1] [{food}]>"


# ---- the hunger meter in percent (the user, 2026-11-02: "kasih rate persentase seberapa lapar dan apa makanannya")
# Each hungry Gu shows its own meter as a status, "<Gu> Hunger <p>%", rising one step at every turn start in deficit:
# N steps for a Gu whose hunger.csv row says N turns (rank 1: 33%, 67%, 100%). The death roll comes at the turn start
# that brings 100%, as the single status did before (N-1 turns after the first turn start in deficit, then every N
# turns), and the meter starts again. Each step is a 2-turn status: given at a turn start it is still there at the next
# turn start's triggers, then runs out (E7). The lines run highest first, so a turn start climbs one step only
# (tools/gen_ruleset.py dao_step uses the same order). A step clears itself at a turn start with the food back.
def stages(rank: int) -> list[int]:
    n = HUNGER_RANKS[rank][0]
    return [round(100 * j / n) for j in range(1, n + 1)]


def stage_name(gu: str, p: int) -> str:
    return f"{gu} Hunger {p}%"


def hunger(gu: str, food: str, rank: int) -> list[str]:
    n, chance = HUNGER_RANKS[rank]
    names = [stage_name(gu, p) for p in stages(rank)]
    dry = f"<when below [0] [{food}]>"
    out = [f"[This Unit] loses the [{gu}] promotion <upon turn start> {dry} <for units with [{names[-2]}]> "
           f"<with [{chance}]% chance>"]
    for j in range(n - 1, 0, -1):
        out.append(f"[This Unit] gains the [{names[j]}] status for [2] turn(s) <upon turn start> {dry} "
                   f"<for units with [{names[j - 1]}]>")
    # the meter starts again one turn start after the roll: the 100% step is still there, the step before it is not
    # (at the roll's own turn start both are, so this line cannot fire then, whatever order the engine evaluates in)
    out.append(f"[This Unit] gains the [{names[0]}] status for [2] turn(s) <upon turn start> {dry} "
               f"<for units with [{names[-1]}]> <for units without [{names[-2]}]>")
    out.append(f"[This Unit] gains the [{names[0]}] status for [2] turn(s) <upon turn start> {dry} "
               + " ".join(f"<for units without [{x}]>" for x in names))
    return out


def stage_comment(p: int, chance: int) -> str:
    if p == 100:
        return f"Starving: 100%. This turn the Gu had a {chance}% chance to die; the meter starts again"
    return f"Starving: {p}%. At 100% the Gu has a {chance}% chance to die"


def stage_comment_id(p: int, chance: int) -> str:
    if p == 100:
        return f"Kelaparan: 100%. Giliran ini Gu itu berpeluang {chance}% mati; meteran mulai lagi"
    return f"Kelaparan: {p}%. Pada 100% Gu itu berpeluang {chance}% mati"


def stage_pedia(gu: str, gu_id: str, food: str, rank: int, p: int) -> tuple[str, str]:
    chance = HUNGER_RANKS[rank][1]
    return (f"The hunger meter of {gu}: {p}%. It rises {stages(rank)[0]}% each turn the clan lacks {food}; at 100% the Gu "
            f"has a {chance}% chance to die, then the meter starts again. Feeding the clan clears it.",
            f"Meteran lapar {gu_id or ID_NAMES.get(gu, gu)}: {p}%. Naik {stages(rank)[0]}% tiap giliran klan kekurangan "
            f"{ID_NAMES.get(food, food)}; pada 100% Gu itu berpeluang {chance}% mati, lalu meteran mulai lagi. Memberi makan "
            f"klan menghapusnya.")


def hunger_statuses(gu: str, food: str, rank: int) -> list[dict]:
    chance = HUNGER_RANKS[rank][1]
    return [{"name": stage_name(gu, p), "uniques": [
        f"[This Unit] loses the [{stage_name(gu, p)}] status <upon turn start> <when above [-1] [{food}]>",
        f"Comment [{stage_comment(p, chance)}]"],
        "civilopediaText": [{"text": stage_pedia(gu, "", food, rank, p)[0]}]} for p in stages(rank)]


def food_comment(food: str, eats: str, rank: int) -> tuple[str, str]:
    """What the Gu eats and how fast hunger rises without it (English, Indonesian)."""
    st, (n, chance) = stages(rank), HUNGER_RANKS[rank]
    step = st[0]
    food_id = ID_NAMES.get(food, food)
    return (f"Food: {eats} {food} a turn. Short of it: weakened at once, hunger +{step}% a turn, at 100% a {chance}% "
            f"chance to die",
            f"Makanan: {eats} {food_id} per giliran. Bila kurang: langsung melemah, lapar +{step}% per giliran, pada "
            f"100% berpeluang {chance}% mati")


def stone_comment(upkeep: int) -> tuple[str, str]:
    return (f"Food: primeval stones, {upkeep}% more upkeep. With the clan's stones below zero every unit fights 20% "
            f"weaker",
            f"Makanan: batu primordial, pemeliharaan {upkeep}% lebih tinggi. Bila batu klan di bawah nol setiap unit "
            f"bertarung 20% lebih lemah")


def gu_promotion(r: dict) -> dict:
    """A Gu that eats a Gu food: effects work only while fed (fed()), then the food, the hunger meter, the extras."""
    rank = int(r["rank"])
    return {"name": r["name"], "uniques": [f"Comment [{food_comment(r['food'], r['eats'], rank)[0]}]"]
            + [fed(e, r["food"]) for e in items(r["effects"])]
            + [f"Consumes [{r['eats']}] [{r['food']}]"] + hunger(r["name"], r["food"], rank)
            + items(r.get("extra_uniques", ""))}


def hunger_translations(gus: list[tuple[str, str, str, str, str]]) -> list[tuple[str, str]]:
    """(English, Indonesian) for the meters and comments of (name, name_id, food, rank, eats) Gu."""
    out = []
    for name, name_id, food, rank, eats in gus:
        r = int(rank)
        chance = HUNGER_RANKS[r][1]
        out.append(food_comment(food, eats, r))
        for p in stages(r):
            out += [(stage_name(name, p), f"{name_id or ID_NAMES.get(name, name)} Lapar {p}%"),
                    (stage_comment(p, chance), stage_comment_id(p, chance)), stage_pedia(name, name_id, food, r, p)]
    return out
