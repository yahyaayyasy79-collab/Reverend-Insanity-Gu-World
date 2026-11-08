#!/usr/bin/env python3
"""The Gu catalog (Phase D, the user 2026-11-02: "buat gu tambahan sekitaran 100 lagi", canon first, the rest adapted).

data/gu_catalog.csv holds one row per Gu: its rank 1-9, path, role, icon form, food and the canon source. A unit refines
a catalog Gu by spending XP on it (a promotion), once it holds the path's Master and its rank reaches the Gu's; the AI
buys them too. What the Gu does follows from its role and rank (ROLES), so a rank-9 Gu of a role is always stronger
than a rank-1 Gu of the same role:

* mortal Gu (ranks 1-5) eat primeval stones (more upkeep) or, for the two whose canon food the mod has, Moon Orchid
  and Wine through the hunger meter (tools/gu_rules.py);
* immortal Gu (ranks 6-9) eat the immortal essence of their rank and sleep while the clan has none in store.

Every Gu has its own icon (tools/art/guart.py) and its own refinement sound (tools/art/sfx.py), played when the unit
gains it. Imported by tools/gen_paths.py (promotions, translations, the PATHS.md table); numpy-free.
"""
from __future__ import annotations

import csv
import re

from common import REPO_ROOT

DATA = REPO_ROOT / "data" / "gu_catalog.csv"
ROWS = list(csv.DictReader(DATA.open(encoding="utf-8", newline="")))
# reference audit Layer 2 (2026-11-08): canon fusion recipes. A fused Gu needs its ingredients (every one in `needs`) and
# uses up those in `spends` when refined, as the novel's fusions do (R V1c47, V1c64, V1c121, V1c155). Only chains a
# single-path unit can climb are gated: Moonglow (Moonlight + Little Light, a light-path Gu) and the water-path half of
# Sky Canopy would shut out the AI, which walks one path per unit; Sky Canopy keeps its White Jade (the Strength killer
# move of Slice 1 needs it).
with (REPO_ROOT / "data" / "gu_fusions.csv").open(encoding="utf-8", newline="") as _f:
    FUSIONS = {r["name"]: r for r in csv.DictReader(_f)}


def fusion_lines(name: str) -> list[str]:
    f = FUSIONS.get(name)
    if not f:
        return []
    return ([f"Unavailable <for units without [{g}]>" for g in f["needs"].split("|") if g]
            + [f"[This Unit] loses the [{g}] promotion" for g in f["spends"].split("|") if g])

# a Gu of rank r needs a unit of rank r or higher (a unit's era is its required tech's era [src BaseUnit.matchesFilter])
GATE = {1: "", 2: "<for [non-[Rank One Gu Master]] units>", 3: "<for [non-[Rank One-Two era]] units>",
        4: "<for [post-[Rank Three era]] units>", 5: "<for [post-[Rank Four era]] units>",
        6: "<for [post-[Rank Five era]] units>", 7: "<for [post-[Rank Six era]] units>",
        8: "<for [post-[Rank Seven era]] units>", 9: "<for [post-[Rank Eight era]] units>"}
ESSENCE = {6: "Green Grape Immortal Essence", 7: "Red Date Immortal Essence", 8: "White Lychee Immortal Essence",
           9: "Yellow Apricot Immortal Essence"}
ESSENCE_ID = {6: "Esensi Abadi Anggur Hijau", 7: "Esensi Abadi Kurma Merah", 8: "Esensi Abadi Leci Putih",
              9: "Esensi Abadi Aprikot Kuning"}
UPKEEP = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}           # % more upkeep for a stone-eating mortal Gu
AI_WEIGHT = "[+100]% weight to this choice for AI decisions"
HIT = "<upon damaging a [Military] unit> <when attacking>"


# mechanics audit P2 (the user, 2026-11-03: "Gu jarahan"): the victor takes the Gu of the fallen, as Fang Yuan lives on.
# A Gu Master that defeats a unit takes each of its mortal catalog Gu with this chance (one roll per Gu, E5) when its own
# rank can hold the Gu (GATE). The Gu Master unit types carry the lines, so every Gu Master loots, barbarians too; the
# defeated unit still holds its promotions when the trigger runs [src Battle.triggerVictoryUniques]. Slice 1's ladder Gu
# and the path Gu are not taken (the ladder and the Master hand them out).
SPOILS_CHANCE = 25
SPOILS = (f"Spoils: defeating a unit takes each of its catalog Gu of rank 1-5 with a {SPOILS_CHANCE}% chance, when this "
          "unit's rank can hold it",
          f"Rampasan: mengalahkan sebuah unit merampas tiap Gu katalog tingkat 1-5 miliknya dengan peluang {SPOILS_CHANCE}%, "
          "bila tingkat unit ini sanggup memegangnya")


def spoils() -> list[str]:
    """The uniques of every Gu Master unit type: a visible comment, then one hidden line per mortal catalog Gu."""
    out = [f"Comment [{SPOILS[0]}]"]
    for row in (x for x in ROWS if not immortal(x)):
        n = row["name"]
        out.append(" ".join(x for x in (f"[This Unit] gains the [{n}] promotion <upon defeating a [{n}] unit>",
                                         f"<with [{SPOILS_CHANCE}]% chance>", f"<for units without [{n}]>",
                                         GATE[int(row["rank"])], "<hidden from users>") if x))
    return out


def sound(name: str) -> str:
    """The Gu's refinement sound (sounds/<this>.ogg)."""
    return "gu-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def status_of(row: dict) -> str:
    return row["role"].split(":", 1)[1] if row["role"].startswith("status:") else ""


def effects(row: dict) -> list[tuple[str, str, str]]:
    """(unique, English, Indonesian) per effect; magnitudes grow with the rank."""
    r, role = int(row["rank"]), row["role"].split(":")[0]
    if role == "str":
        n = 5 + 3 * r
        return [(f"[+{n}]% Strength", f"{n}% stronger", f"{n}% lebih kuat")]
    if role == "atk":
        n = 8 + 4 * r
        return [(f"[+{n}]% Strength <when attacking>", f"{n}% stronger when attacking", f"{n}% lebih kuat saat menyerang")]
    if role == "def":
        n = 8 + 4 * r
        return [(f"[+{n}]% Strength <when defending>", f"{n}% stronger when defending", f"{n}% lebih kuat saat bertahan")]
    if role == "dmg":
        n = 2 + 2 * r
        return [(f"[Target Unit] takes [{n}] damage {HIT}", f"each hit deals {n} more damage",
                 f"setiap serangan memberi {n} kerusakan tambahan")]
    if role == "status":
        from gen_paths import STATUSES
        st = next(s for s in STATUSES if s["name"] == status_of(row))
        turns, n = 1 + r // 3, r + 2
        return [(f"[Target Unit] gains the [{st['name']}] status for [{turns}] turn(s) {HIT}",
                 f"its hits leave the enemy {st['name']} for {turns} turn(s)",
                 f"serangannya membuat musuh {st['name_id']} selama {turns} giliran"),
                (f"[+{n}]% Strength <when attacking>", f"{n}% stronger when attacking", f"{n}% lebih kuat saat menyerang")]
    if role == "move":
        m, n = (1 if r < 7 else 2), 1 + r
        return [(f"[+{m}] Movement", f"+{m} movement", f"+{m} gerak"),
                (f"[+{n}]% Strength", f"{n}% stronger", f"{n}% lebih kuat")]
    if role == "heal":
        n = 4 + 3 * r
        out = [(f"[+{n}] HP when healing", f"heals {n} HP more a turn", f"pulih {n} HP lebih banyak per giliran")]
        if r >= 4:
            k = 5 + 2 * r
            out.append((f"Heals [{k}] damage if it kills a unit", f"heals {k} HP after a kill",
                        f"pulih {k} HP setelah membunuh"))
        return out
    if role == "sight":
        s, n = (1 if r < 5 else 2), r + 1
        return [(f"[+{s}] Sight", f"+{s} sight", f"+{s} jarak pandang"),
                (f"[+{n}]% Strength", f"{n}% stronger", f"{n}% lebih kuat")]
    if role == "stealth":
        n = 2 + 2 * r
        return [("Invisible to non-adjacent units", "unseen except from an adjacent tile",
                 "tak terlihat kecuali dari petak di sebelahnya"),
                (f"[+{n}]% Strength <when defending>", f"{n}% stronger when defending", f"{n}% lebih kuat saat bertahan")]
    if role == "aura":
        n = 2 + r
        return [(f"[-{n}]% Strength for enemy [Military] units in adjacent [All] tiles",
                 f"enemy soldiers beside it fight {n}% weaker", f"prajurit musuh di sampingnya bertarung {n}% lebih lemah")]
    if role == "xp":
        n = 10 + 5 * r
        return [(f"[+{n}]% XP gained from combat", f"{n}% more XP from combat", f"XP dari pertempuran {n}% lebih banyak")]
    if role == "econ":
        n = 4 + 2 * r
        return [(f"[-{n}]% maintenance costs", f"its unit costs {n}% less upkeep",
                 f"pemeliharaan unitnya {n}% lebih murah")]
    if role == "beast":   # Layer 2: an enslavement Gu, the beasts it drives fight it badly
        n = 10 + 5 * r
        return [(f"[+{n}]% Strength <vs [Beast] units>", f"{n}% stronger against beasts",
                 f"{n}% lebih kuat melawan binatang")]
    if role == "theft":
        n = 10 + 5 * r
        return [(f"Earn [{n}]% of killed [Military] unit's [Cost] as [Gold]",
                 f"takes {n}% of a slain soldier's cost as stones", f"merampas {n}% harga prajurit yang dibunuh sebagai batu")]
    raise KeyError(row["role"])


def immortal(row: dict) -> bool:
    return int(row["rank"]) >= 6


def asleep(u: str, row: dict) -> str:
    """An immortal Gu works only while the clan has its rank's immortal essence in store."""
    return f"{u} <when above [0] [{ESSENCE[int(row['rank'])]}]>" if immortal(row) else u


def food_lines(row: dict) -> tuple[list[str], list[dict], tuple[str, str]]:
    """(uniques, hunger statuses, (English, Indonesian) food sentence)."""
    from gu_rules import hunger_statuses, stone_comment
    r = int(row["rank"])
    if row["food"]:
        return [], hunger_statuses(row["name"], row["food"], min(r, 4)), ("", "")
    if immortal(row):
        en = f"Food: {ESSENCE[r]}. With none in store the Gu sleeps"
        idn = f"Makanan: {ESSENCE_ID[r]}. Bila persediaan habis Gu ini tertidur"
        return [f"Comment [{en}]"], [], (en, idn)
    en, idn = stone_comment(UPKEEP[r])
    return [f"Comment [{en}]", f"[+{UPKEEP[r]}]% maintenance costs"], [], (en, idn)


def pedia(row: dict) -> tuple[str, str]:
    from gen_paths import KEY, tier_name, tier_name_id
    p, r = KEY[row["path"]], int(row["rank"])
    zh = f" ({row['chinese']})" if row["chinese"] else ""
    eff = effects(row)
    en_eff, id_eff = "; ".join(e[1] for e in eff), "; ".join(e[2] for e in eff)
    note_en = {"INVENTED": " Invented for the mod: the novel names no Gu of this path at this level.",
               }.get(row["verdict"], "")
    note_id = {"INVENTED": " Rekaan mod: novel tidak menyebut Gu jalur ini pada tingkat ini."}.get(row["verdict"], "")
    f = FUSIONS.get(row["name"])
    if f:
        from gu_rules import ID_NAMES
        need = [g for g in f["needs"].split("|") if g]
        spent = [g for g in f["spends"].split("|") if g]
        idn_of = lambda g: next((x["name_id"] for x in ROWS if x["name"] == g), ID_NAMES.get(g, g))
        note_en += f" Fused from {' and '.join(need)}" + (f", which {'are' if len(spent) > 1 else 'is'} used up." if spent
                                                         else ", which stays.")
        note_id += f" Dilebur dari {' dan '.join(idn_of(g) for g in need)}" + (", yang habis terpakai." if spent
                                                                               else ", yang tetap ada.")
    if immortal(row):
        note_en += " In the novel every immortal Gu is one of a kind; here each immortal refines its own."
        note_id += " Dalam novel setiap Gu abadi hanya ada satu; di sini setiap abadi memurnikan miliknya sendiri."
    en = (f"{row['name']}{zh}, a rank-{r} {p['name']} path Gu: {row['fn']}. {en_eff[0].upper() + en_eff[1:]}. "
          f"Refined with XP by {'an' if tier_name(p, 0)[0] in 'AEIOU' else 'a'} {tier_name(p, 0)} of rank {r} or "
          f"higher.{note_en}")
    idn = (f"{row['name_id']}{zh}, Gu jalur {p['name_id']} tingkat {r}: {row['fn_id']}. {id_eff[0].upper() + id_eff[1:]}. "
           f"Dimurnikan dengan XP oleh {tier_name_id(p, 0)} tingkat {r} atau lebih tinggi.{note_id}")
    return en, idn


def promotions(unit_types: list[str]) -> list[dict]:
    from gen_paths import KEY, tier_name
    from gu_rules import gu_promotion
    out, statuses = [], []
    for row in (x for x in ROWS if not immortal(x)):   # immortal Gu are one of a kind: wonders(), bearers()
        r = int(row["rank"])
        fx = [asleep(e[0], row) for e in effects(row)]
        food, hunger, _ = food_lines(row)
        if row["food"]:
            d = gu_promotion({"name": row["name"], "rank": str(min(r, 4)), "food": row["food"], "eats": "1",
                              "effects": "|".join(fx), "extra_uniques": ""})
            uniques = d["uniques"]
            statuses += hunger
        else:
            uniques = food + fx
        uniques += fusion_lines(row["name"])
        uniques += [f"Play [{sound(row['name'])}] sound <upon gaining the [{row['name']}] promotion>"]
        if GATE[r]:
            uniques.append(f"Only available {GATE[r]}")
        uniques.append(AI_WEIGHT)
        out.append({"name": row["name"], "unitTypes": unit_types, "prerequisites": [tier_name(KEY[row["path"]], 0)],
                    "uniques": uniques, "civilopediaText": [{"text": pedia(row)[0]}]})
    return out + statuses


# ---------------------------------------------------------------- immortal Gu: one of a kind (the user, 2026-11-02)
# "buat gu abadi tetap 1 sesuai kanon tapi bervariasi": every immortal Gu exists once in the world (仙蛊唯一, V5c666).
# Each is a world wonder (refined in a city, seized with it); one immortal of the owning clan carries it (the bearer
# promotion). A bearer whose clan lost the wonder keeps the promotion but its Gu sleeps.
WONDER_COST = {6: 340, 7: 380, 8: 420, 9: 700}      # the mean of the canon wonders of data/immortal_gu.csv per rank
WONDER_ESSENCE = {6: 35, 7: 35, 8: 35, 9: 60}
# mechanics audit P5 (the user, 2026-11-03: "lanjut"): immortal Gu are refined from immortal materials (仙材). Before,
# materials had one use (sold at the market). Autoplay (Five Regions, 18 x 300): 29 of the 50 immortal Gu wonders the
# AI built were begun with no materials at all, so a cost alone would have halved the race; blessed lands now grow a
# little every turn (tools/gen_ruleset.py LAND_MATERIALS), and a slain desolate beast still yields a windfall. Costs:
# with 15/20/25/40 the AI held 41-195 when it began a wonder (median 108, 18 games), so they were doubled; no build
# would have been delayed at 2x
MATERIALS = "Immortal Materials"
WONDER_MATERIALS = {6: 30, 7: 40, 8: 50, 9: 80}
IMMORTAL_ROWS = [r for r in ROWS if int(r["rank"]) >= 6]


def bearer(name: str) -> str:
    return f"{name} Bearer"


def all_immortal() -> list[dict]:
    """Every immortal Gu wonder: the catalog's and data/immortal_gu.csv's (rank, path, names, role)."""
    from gu_rules import table
    out = [{"name": r["name"], "name_id": r["name_id"], "rank": r["rank"], "path": r["path"], "role": r["role"],
            "form": r["form"], "catalog": True, "row": r} for r in IMMORTAL_ROWS]
    out += [{"name": r["name"], "name_id": r["name_id"], "rank": r["rank"], "path": r["path"], "role": "str",
             "form": "orb", "catalog": False, "row": r} for r in table("immortal_gu.csv")]
    return out


def bearer_lines(g: dict) -> list[str]:
    r, name = int(g["rank"]), g["name"]
    fx = [f"{asleep(e[0], g)} <if [{name}] is constructed>" for e in effects(g)]
    en = f"Food: {ESSENCE[r]}. With none in store the Gu sleeps; it sleeps too while the clan does not own {name}"
    return ([f"Comment [{en}]"] + fx
            + [f"Play [{sound(bearer(name))}] sound <upon gaining the [{bearer(name)}] promotion>",
               f"Only available <if [{name}] is constructed>",
               f"Only available <when number of [[{bearer(name)}] Units] is less than [1]>",
               f"Only available {GATE[r]}", AI_WEIGHT])


def bearer_pedia(g: dict) -> tuple[str, str]:
    from gen_paths import KEY, tier_name, tier_name_id
    p, r, eff = KEY[g["path"]], int(g["rank"]), effects(g)
    en = (f"The one immortal who carries {g['name']}, a rank-{r} {p['name']} path immortal Gu. There is only one in the "
          f"world: the clan that owns the wonder lets one immortal of rank {r} or higher carry it; its combination "
          f"moves need the comprehension of the {p['name']} path. "
          + "; ".join(e[1] for e in eff).capitalize() + ". It sleeps without " + ESSENCE[r] + " or the wonder.")
    idn = (f"Satu-satunya abadi yang membawa {g['name_id']}, Gu abadi jalur {p['name_id']} tingkat {r}. Di dunia hanya ada "
           f"satu: klan pemilik keajaiban mengizinkan satu abadi tingkat {r} atau lebih membawanya; jurus kombinasinya "
           f"butuh pemahaman jalur {p['name_id']}. "
           + "; ".join(e[2] for e in eff).capitalize() + ". Ia tertidur tanpa " + ESSENCE_ID[r] + " atau keajaibannya.")
    return en, idn


def bearers(unit_types: list[str]) -> list[dict]:
    from gen_paths import KEY, tier_name
    # no path prerequisite: any immortal with the essence may carry an immortal Gu (autoplay: with the path's Master
    # required, the AI's one-path units matched their clan's wonders in 3 bearers over 4 games of 400 turns);
    # comprehension of the path gates the Gu's combination moves instead (tools/gu_combos.py)
    return [{"name": bearer(g["name"]), "unitTypes": unit_types,
             "uniques": bearer_lines(g), "civilopediaText": [{"text": bearer_pedia(g)[0]}]} for g in all_immortal()]


def wonder_pedia(row: dict) -> tuple[str, str]:
    en, idn = pedia(row)
    return (en.split(" Refined with XP")[0] + f" One of a kind: the clan that owns it lets one immortal carry it "
            f"({bearer(row['name'])}).",
            idn.split(" Dimurnikan dengan XP")[0] + f" Hanya ada satu: klan pemiliknya mengizinkan satu abadi "
            f"membawanya ({bearer(row['name'])}).")


def wonders(recipe: dict, marker) -> list[dict]:
    """The catalog's immortal Gu as world wonders (refined like the canon ones; never destroyed on capture)."""
    out = []
    for row in IMMORTAL_ROWS:
        r = int(row["rank"])
        out.append({"name": row["name"], "isWonder": True, "requiredTech": recipe[str(r)], "cost": WONDER_COST[r],
                    "uniques": [f"Costs [{WONDER_ESSENCE[r]}] [{ESSENCE[r]}]", f"Costs [{WONDER_MATERIALS[r]}] [{MATERIALS}]",
                                "Never destroyed when the city is captured",
                                "Immortal Gu", marker(row["path"]), "Triggers a [Immortal Gu Refinement] event",
                                "[+300]% weight to this choice for AI decisions"],  # as the canon wonders (C3)
                    "civilopediaText": [{"text": wonder_pedia(row)[0]}]})
    return out


def food_gu() -> list[tuple[str, str, str, str, str]]:
    """(name, Indonesian name, food, hunger rank, eats) of the catalog Gu with a hunger meter."""
    return [(r["name"], r["name_id"], r["food"], str(min(int(r["rank"]), 4)), "1") for r in ROWS if r["food"]]


def translations() -> list[tuple[str, str]]:
    out = [SPOILS]
    for g in all_immortal():
        r = int(g["rank"])
        out += [(bearer(g["name"]), f"Pembawa {g['name_id']}"), bearer_pedia(g),
                (f"Food: {ESSENCE[r]}. With none in store the Gu sleeps; it sleeps too while the clan does not own "
                 f"{g['name']}", f"Makanan: {ESSENCE_ID[r]}. Bila persediaan habis Gu ini tertidur; ia juga tertidur "
                 f"selama klan tidak memiliki {g['name_id']}")]
    for row in IMMORTAL_ROWS:
        out.append(wonder_pedia(row))
    for row in ROWS:
        out += [(row["name"], row["name_id"])] + ([] if immortal(row) else [pedia(row)])
        en, idn = food_lines(row)[2]
        if en:
            out.append((en, idn))
    return out


def doc_table() -> list[str]:
    from gen_paths import KEY, code
    built = {d["name"]: d for d in promotions(["Gu Master"])}
    built.update({g["name"]: {"uniques": bearer_lines(g)} for g in all_immortal() if g["catalog"]})
    lines = ["| Rank | Gu | Chinese | Path | Role | Food | Uniques | Verdict | Source |",
             "|---|---|---|---|---|---|---|---|---|"]
    wonders_by = {w["name"]: w for w in wonders({"6": "-", "7": "-", "8": "-", "9": "-"}, lambda k: f"{KEY[k]['name']} Path")}
    for row in sorted(ROWS, key=lambda x: (int(x["rank"]), KEY[x["path"]]["name"], x["name"])):
        u = " ".join(code(x) for x in built[row["name"]]["uniques"])
        if row["name"] in wonders_by:   # an immortal Gu: the wonder's uniques, then its bearer's
            u = "wonder: " + " ".join(code(x) for x in wonders_by[row["name"]]["uniques"]) + "; bearer: " + u
        food = row["food"] or (ESSENCE[int(row["rank"])] if immortal(row) else "stones")
        lines.append(f"| {row['rank']} | {row['name']} | {row['chinese'] or '—'} | {KEY[row['path']]['name']} | "
                     f"{row['role']} | {food} | {u} | {row['verdict']} | {row['source']} |")
    return lines


def canon_bearer_table() -> list[str]:
    from gen_paths import KEY, code
    lines = ["", "The canon immortal Gu wonders (data/immortal_gu.csv) get a bearer too:", "",
             "| Rank | Immortal Gu (wonder) | Path | Bearer uniques |", "|---|---|---|---|"]
    for g in sorted((g for g in all_immortal() if not g["catalog"]), key=lambda x: (int(x["rank"]), x["name"])):
        lines.append(f"| {g['rank']} | {g['name']} | {KEY[g['path']]['name']} | "
                     + " ".join(code(x) for x in bearer_lines(g)) + " |")
    return lines

