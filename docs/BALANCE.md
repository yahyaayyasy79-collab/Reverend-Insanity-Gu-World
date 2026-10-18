# Balance — Slice 1

Every tunable number of the ruleset (MOD_SPEC §10). Part 1 is the short list of knobs that decide how the game plays,
with the autoplay evidence behind each value (`docs/AUTOPLAY.md`). Part 2 is the full inventory, generated from
`jsons/`: every number, its file, object, field or unique, and where to edit it.

Rules that bind tuning: the user's round-4 rule (autoplay decides, Strategic Balance ON, the rank-1 hunger death rate
decides the rank-1 threshold) and the round-5 delegation ("bebas, yang sesuai dan seru seperti di novelnya").

## How to tune

1. Change the source named in the inventory's last column: a `data/*.csv` table or a section of
   `tools/gen_ruleset.py`.
2. A/B first, on a throwaway copy: `tools/gen_ruleset.py --out /tmp/variant`, copy the mod's `Images/` and atlas into
   it if the run needs them, then `tools/autoplay.py --mod /tmp/variant --games 12 --turns 200 --difficulty King
   --out /tmp/ap-variant`. AI randomness is not tied to the seed: compare pooled numbers, never one game; hunger
   deaths need at least 36 games (identical 12-game batches differ twofold, AUTOPLAY.md round 6b).
3. Apply: `tools/gen_ruleset.py && tools/gen_balance.py && tools/gen_translations.py`, then `tools/check_all`
   (it runs the refinement-ladder check). The self-tests name the uniques `docs/LORE_MAPPING.md` must re-quote.
4. Record the run in `docs/AUTOPLAY.md` and the step in `CHANGELOG.md`.

## Part 1 — the knobs that matter

| Knob | Now | Edit in | Evidence (AUTOPLAY.md) | Turn it when |
|---|---|---|---|---|
| Hunger meter, rank-1 Gu | status 3 turns: first death roll 2 turns after the first turn start in deficit, then every 3 | `data/hunger.csv` rank 1 `status_turns` | 0.90 hunger deaths per clan per 100 turns, 36 games (6b; single 12-game batches range 0.52–1.13); about 1.2% of rank-1 holder-turns in deficit | The user's rule: raise to 4–5 only if the trade economy collapses. There is no trade economy to collapse (0.1–0.2 deals per civ), so it stays |
| Hunger meter, rank-2 Gu | status 5 turns (roll after 4, then every 5) | `data/hunger.csv` rank 2 | 3 episodes in 30 games, all recovered (round 5) | Rank-2 Gu should hurt more to lose; leave until a human game shows otherwise |
| Hunger death chance | 50% per roll | `data/hunger.csv` `death_chance` | The user's option B | User's decision; do not tune |
| Cultivation | +2 XP per turn in a city with a Gu Academy (or the Martial Arena), until Killer Move | `data/gu_masters.csv` `cultivationXP` | 0 → 2 XP: rank-2 Gu per clan 0.71 → 5.1, Killer Move 0.04 → 2.8 (5d); 3 XP gives 5.4 / 3.7 | Lower to 1 if Killer Moves become common before Rank Four Cultivation |
| Refinement odds (careful / reckless) | rung 1 85 / 50, fusion 70 / 40, fusion with a tusk 90 / 60, Killer Move 85 / 50 % | `tools/gen_ruleset.py` `ladder()` arguments | 38.8 attempts bought per clan by T200 (5d); no dominated choice | Careful must stay clearly safer than reckless, or it is not worth its stones (no dominated choice, §10) |
| Refinement cost (careful) | 40 / 70 / 100 stones by era, gated at 80 / 140 / 200 | `tools/gen_ruleset.py` `Events` | Lowest stones 6–13 on average at King (5b); 4 of 144 clans spent 20+ turns in the red, all at war, none in a disband spiral (6b) | Raise if late treasuries keep growing (see "What the data says is off") |
| City strength from techs | `cityStrengthFromTechsFullMultiplier` 0.1 (+12 with every tech) | `tools/gen_ruleset.py` `ModOptions` | 1.0: 0 cities captured in 12 games; 0.1: 16 captured, 8 clans eliminated (5b) | Re-tune whenever the tech tree or unit strengths change (E8) |
| Gu Master strength, Strength path | 8 (Rank One), 14 / 22 / 32 | `data/gu_masters.csv` `strength` | Strength clans capture 8 cities per 12 games (5c) | Together with the Moon row |
| Gu Master strength, Moon path | 13 / 20 / 29, melee, moon blade 40% of melee strength before each clash with a unit | `data/gu_masters.csv` `strength`, `extra_uniques` | Ranged Moon armies captured 0 cities; melee + 40% blade: 5 (5c) | If Gu Yue or Bai are eliminated in more than 2 of 12 games |
| Gu Master upkeep | Rank One +25%; Strength +100 / +175 / +275%; Moon +75 / +150 / +225% | `data/gu_masters.csv` `maintenance` | Upkeep is 20% of gross income in T1–50 and 60% in T151–200 (round 5) | See "What the data says is off": the spec asks for about 40% early |
| Free upkeep | none for majors: `[-3] units cost no maintenance` cancels the engine's 3 free units [src CivInfoStatsForNextTurn.getUnitMaintenance]; the Demonic policy Lone Cultivators gives 2 back | `tools/gen_ruleset.py` `GlobalUniques`, `Policies` | — | Already at the floor; push early pressure through Gu Master upkeep instead |
| Wild Gu | 6% per Gu Master per turn, then a 1-in-5 die (weights +300 / +0): 1.2% | `WILD_GU_TRIGGER`, `Events` `Wild Gu` | 1.55 Jade Skin and 2.19 Black Boar per clan by T200, 36 games (6b) | The user asked for about 1.2%; change the die, not the trigger (E5) |
| Buried inheritance | 1% per Gu Master per turn in foreign land after Inheritance Lore, then 1 in 2 | `INHERITANCE_TRIGGER`, `Events` `Inheritance Rumour` | 1.75 inheritances per game, 36 games (6b; 1 in 8 gave 0.42) | If fewer than 1 per game, the clans have nothing to fight over |
| Inheritance claim | takes the land tiles in a 1-tile radius (−10 relations per tile, engine), +20 XP; or strip it for 60 stones and +30 XP | `Events` `Buried Inheritance` | The AI claims 2 times in 3 (weights +100 / +0, E1) | Radius 2 makes it a war trigger; try it only with a human game in hand |
| Gu Inheritance yield | tile 3 science, 2 culture, 2 stones; Inheritance Dig +2 science, +2 stones; +20% combat XP while held | `Resources`, `Improvements`, `GlobalUniques` | — | — |
| Beast tide | 3% per turn after T30, another 2% after T90 | `GlobalUniques` | Pillage 7–10× Vanilla's (round 5) | Lower if pillage starves clans in human games |
| Betrayal | 8% per turn while unhappy, 3% while above 300 stones | `GlobalUniques` | — | — |
| Stone shortage | 25% per turn with a negative treasury and income | `GlobalUniques` | — | — |
| Happiness | every difficulty +6 base happiness (one luxury only) | `tools/gen_ruleset.py` `Nations (Difficulties)` | — | — |
| Spirit Spring | 1 deposit per start (Strategic Balance), Spring Cave +3 stones, 6 turns | `Resources`, `Improvements` | Improved late: the AI keeps one laborer (experiments, baseline) | The user wants laborers produced, not given: do not add a free laborer |
| Gu food deposits | minor 1 / 1 / 2, major 2 / 2 / 3 (sparse / default / abundant) | `tools/gen_ruleset.py` `DEP` | Every clan ends with a surplus of every food (round 5) | Lower majors to 1 / 1 / 2 if hunger should matter in peace |
| Barbarian XP cap | 90 XP | `ModOptions` `maxXPfromBarbarians` | — | — |

## What the data says is off

Not fixed, because each needs either a human game or the user's taste:

1. **Early upkeep is light.** The spec asks for upkeep near 40% of stone income early; autoplay measures 20% in
   T1–50 and 30–38% by T100. Majors already pay for every unit, so the candidates are Rank One upkeep +25% → +50%
   or a stone upkeep on the Gu Academy and Gu Feeding House (1 → 2).
2. **The late game is not tense.** Treasuries grow (mean 420 stones in T151–200 at King). Candidates: costlier
   careful refinement in rank four, or upkeep on Killer Move above +25%.
3. **Food is abundant in peace.** Hunger only bites when wars pillage camps and plantations. That fits the novel (Gu
   starve in sieges, not in good years), so it stays unless the user wants hunger in peacetime.
4. **A few AI clans go broke in long wars:** 4 of 144 spent 20+ turns in the red (6b). No disband spiral, so the
   spec's line holds, but it is the number to watch in the user's 100-turn game.
5. **The tech tree ends near T113–123.** Slice 1 has 15 techs; the rest of the game is Dao Comprehension. Slice 2 adds
   the next ranks.

## Part 2 — inventory

<!-- inventory:start (tools/gen_balance.py) -->

Generated from `jsons/` by `tools/gen_balance.py`; the self-tests fail when it is stale. Edit the source in the last column, regenerate (`tools/gen_ruleset.py && tools/gen_balance.py`), run `tools/check_all`.

### ModOptions.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| ModOptions | constants.maxXPfromBarbarians | 90 | tools/gen_ruleset.py `ModOptions / Globals` |
| ModOptions | constants.cityStrengthFromTechsFullMultiplier | 0.1 | tools/gen_ruleset.py `ModOptions / Globals` |

### GlobalUniques.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| GlobalUniques | `[-75]% growth [in all cities] <when between [-10] and [-1] [Happiness]>` | -75, -10, -1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Nullifies Growth [in all cities] <when below [-10] [Happiness]>` | -10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-50]% [Production] [in all cities] <when below [-10] [Happiness]>` | -50, -10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-33]% Strength <for [All] units> <when below [-10] [Happiness]>` | -33, -10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Rebel units may spawn <when below [-20] [Happiness]>` | -20 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-3] units cost no maintenance <for [Major] Civilizations>` | -3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-20]% Strength <when below [0] [Gold]>` | -20, 0 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [30]> <with [3]% chance> <for [Major] Civilizations>` | 30, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [90]> <with [2]% chance> <for [Major] Civilizations>` | 90, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [8]% chance> <for [Major] Civilizations>` | 0, 8 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [3]% chance> <for [Major] Civilizations>` | 300, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [25]% chance> <for [Major] Civilizations>` | 0, 0, 25 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[+20]% XP gained from combat <with [Gu Inheritance]>` | +20 | tools/gen_ruleset.py `ModOptions / Globals` |

### Difficulties.json

Vanilla's eight levels, edited in tools/gen_ruleset.py `Nations (Difficulties)` (`baseHappiness` is Vanilla + 6; the starting-unit and free-tech lists are counts, renamed to this ruleset's units and techs).

| Field | Settler | Chieftain | Warlord | Prince | King | Emperor | Immortal | Deity |
|---|---|---|---|---|---|---|---|---|
| baseHappiness | 21 | 18 | 18 | 15 | 15 | 15 | 15 | 15 |
| extraHappinessPerLuxury | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| researchCostModifier | 0.9 | 0.95 | 1 | 1 | 1 | 1 | 1 | 1 |
| unitCostModifier | 0.5 | 0.67 | 0.85 | 1 | 1 | 1 | 1 | 1 |
| unitSupplyBase | 10 | 7 | 7 | 5 | 5 | 5 | 5 | 5 |
| unitSupplyPerCity | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 |
| buildingCostModifier | 0.5 | 0.67 | 0.85 | 1 | 1 | 1 | 1 | 1 |
| policyCostModifier | 0.5 | 0.67 | 0.85 | 1 | 1 | 1 | 1 | 1 |
| unhappinessModifier | 0.4 | 0.6 | 0.75 | 1 | 1 | 1 | 1 | 1 |
| barbarianBonus | 0.75 | 0.5 | 0.4 | 0.33 | 0.25 | 0.2 | 0.1 | 0 |
| barbarianSpawnDelay | 8 | 5 | 3 | 0 | 0 | 0 | 0 | 0 |
| aiCityGrowthModifier | 1.6 | 1.3 | 1.1 | 1 | 0.9 | 0.85 | 0.75 | 0.6 |
| aiUnitCostModifier | 1.75 | 1.3 | 1.1 | 1 | 0.85 | 0.8 | 0.65 | 0.5 |
| aiBuildingCostModifier | 1.6 | 1.3 | 1.1 | 1 | 0.85 | 0.8 | 0.65 | 0.5 |
| aiWonderCostModifier | 1.6 | 1.3 | 1.1 | 1 | 1 | 1 | 1 | 1 |
| aiBuildingMaintenanceModifier | 1 | 1 | 1 | 1 | 0.85 | 0.8 | 0.65 | 0.5 |
| aiUnitMaintenanceModifier | 1 | 1 | 1 | 1 | 0.8 | 0.75 | 0.65 | 0.5 |
| aiUnitSupplyModifier | 0 | 0 | 0.1 | 0 | 0.3 | 0.3 | 0.4 | 0.5 |
| aiUnhappinessModifier | 1 | 1 | 1 | 1 | 0.9 | 0.85 | 0.75 | 0.6 |
| turnBarbariansCanEnterPlayerTiles | 10000 | 60 | 20 | 0 | 0 | 0 | 0 | 0 |
| clearBarbarianCampReward | 50 | 40 | 30 | 25 | 25 | 25 | 25 | 25 |
| playerBonusStartingUnits | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| aiMajorCivBonusStartingUnits | 0 | 0 | 0 | 0 | 1 | 2 | 4 | 6 |
| aiCityStateBonusStartingUnits | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| aiFreeTechs | 0 | 0 | 0 | 0 | 1 | 2 | 3 | 4 |

### Units.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Clan Settler | movement | 2 | tools/gen_ruleset.py `Units` |
| Clan Settler | cost | 80 | tools/gen_ruleset.py `Units` |
| Clan Settler | `Requires at least [2] population` | 2 | tools/gen_ruleset.py `Units` |
| Clan Settler | `Can only be built <when above [-11] [Happiness]>` | -11 | tools/gen_ruleset.py `Units` |
| Mortal Laborer | movement | 2 | tools/gen_ruleset.py `Units` |
| Mortal Laborer | cost | 45 | tools/gen_ruleset.py `Units` |
| Rank One Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank One Gu Master | strength | 8 | data/gu_masters.csv `strength` |
| Rank One Gu Master | cost | 35 | data/gu_masters.csv `cost` |
| Rank One Gu Master | `[+25]% maintenance costs` | +25 | data/gu_masters.csv `maintenance` |
| Rank One Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank One Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank One Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Two Strength Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Two Strength Gu Master | strength | 14 | data/gu_masters.csv `strength` |
| Rank Two Strength Gu Master | cost | 60 | data/gu_masters.csv `cost` |
| Rank Two Strength Gu Master | `[+100]% maintenance costs` | +100 | data/gu_masters.csv `maintenance` |
| Rank Two Strength Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Two Strength Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Two Strength Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Three Strength Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Three Strength Gu Master | strength | 22 | data/gu_masters.csv `strength` |
| Rank Three Strength Gu Master | cost | 95 | data/gu_masters.csv `cost` |
| Rank Three Strength Gu Master | `[+175]% maintenance costs` | +175 | data/gu_masters.csv `maintenance` |
| Rank Three Strength Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Three Strength Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Three Strength Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Four Strength Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Four Strength Gu Master | strength | 32 | data/gu_masters.csv `strength` |
| Rank Four Strength Gu Master | cost | 140 | data/gu_masters.csv `cost` |
| Rank Four Strength Gu Master | `[+275]% maintenance costs` | +275 | data/gu_masters.csv `maintenance` |
| Rank Four Strength Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Four Strength Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Four Strength Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Two Moon Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Two Moon Gu Master | strength | 13 | data/gu_masters.csv `strength` |
| Rank Two Moon Gu Master | cost | 60 | data/gu_masters.csv `cost` |
| Rank Two Moon Gu Master | `[+75]% maintenance costs` | +75 | data/gu_masters.csv `maintenance` |
| Rank Two Moon Gu Master | `Before engaging in combat performs an extra ranged attack with [40]% of melee combat strength` | 40 | data/gu_masters.csv `extra_uniques` |
| Rank Two Moon Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Two Moon Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Two Moon Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Three Moon Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Three Moon Gu Master | strength | 20 | data/gu_masters.csv `strength` |
| Rank Three Moon Gu Master | cost | 95 | data/gu_masters.csv `cost` |
| Rank Three Moon Gu Master | `[+150]% maintenance costs` | +150 | data/gu_masters.csv `maintenance` |
| Rank Three Moon Gu Master | `Before engaging in combat performs an extra ranged attack with [40]% of melee combat strength` | 40 | data/gu_masters.csv `extra_uniques` |
| Rank Three Moon Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Three Moon Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Three Moon Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Four Moon Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Four Moon Gu Master | strength | 29 | data/gu_masters.csv `strength` |
| Rank Four Moon Gu Master | cost | 140 | data/gu_masters.csv `cost` |
| Rank Four Moon Gu Master | `[+225]% maintenance costs` | +225 | data/gu_masters.csv `maintenance` |
| Rank Four Moon Gu Master | `Before engaging in combat performs an extra ranged attack with [40]% of melee combat strength` | 40 | data/gu_masters.csv `extra_uniques` |
| Rank Four Moon Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Four Moon Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Four Moon Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Lightning Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | strength | 9 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | cost | 30 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | `[+50]% maintenance costs` | +50 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | strength | 16 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | cost | 60 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | `[+15]% Strength bonus for [Lightning Wolf] units within [2] tiles` | +15, 2 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | `[+100]% maintenance costs` | +100 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | strength | 28 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | cost | 120 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | `[+20]% Strength bonus for [Beast] units within [2] tiles` | +20, 2 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | `[+200]% maintenance costs` | +200 | tools/gen_ruleset.py `Units` |

### UnitPromotions.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Aptitude A | `[+15]% Strength` | +15 | tools/gen_ruleset.py `Promotions` |
| Aptitude A | `[-20]% maintenance costs` | -20 | tools/gen_ruleset.py `Promotions` |
| Aptitude A | `[+25]% XP gained from combat` | +25 | tools/gen_ruleset.py `Promotions` |
| Aptitude B | `[+5]% Strength` | +5 | tools/gen_ruleset.py `Promotions` |
| Aptitude B | `[-10]% maintenance costs` | -10 | tools/gen_ruleset.py `Promotions` |
| Aptitude B | `[+10]% XP gained from combat` | +10 | tools/gen_ruleset.py `Promotions` |
| Aptitude D | `[-10]% Strength` | -10 | tools/gen_ruleset.py `Promotions` |
| Aptitude D | `[+20]% maintenance costs` | +20 | tools/gen_ruleset.py `Promotions` |
| Aptitude D | `[-25]% XP gained from combat` | -25 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <when below [50] HP>` | 50 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for [Gu Master] units> <for units with [Jade Skin Gu]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for [Gu Master] units> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Moonlight Gu | `[+20]% Strength <when attacking> <when above [-1] [Moon Orchid]>` | +20 | data/gu.csv `effects` / `extra_uniques` |
| Moonlight Gu | `Consumes [1] [Moon Orchid]` | 1 | data/gu.csv `eats` |
| Moonlight Gu | `[This Unit] gains the [Orchid Hunger] status for [3] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units without [Orchid Hunger]>` | 3 | data/hunger.csv |
| Moonlight Gu | `[This Unit] loses the [Moonlight Gu] promotion <upon losing the [Orchid Hunger] status> <when below [0] [Moon Orchid]> <with [50]% chance>` | 50 | data/hunger.csv |
| Moonlight Gu | `[-10]% Strength <for [Strength Gu Master] units>` | -10 | data/gu.csv `effects` / `extra_uniques` |
| White Boar Gu | `[+15]% Strength <when above [-1] [Wild Boar]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| White Boar Gu | `Consumes [1] [Wild Boar]` | 1 | data/gu.csv `eats` |
| White Boar Gu | `[This Unit] gains the [Pork Hunger] status for [3] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units without [Pork Hunger]>` | 3 | data/hunger.csv |
| White Boar Gu | `[This Unit] loses the [White Boar Gu] promotion <upon losing the [Pork Hunger] status> <when below [0] [Wild Boar]> <with [50]% chance>` | 50 | data/hunger.csv |
| Black Boar Gu | `[+15]% Strength <when above [-1] [Wild Boar]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| Black Boar Gu | `Consumes [1] [Wild Boar]` | 1 | data/gu.csv `eats` |
| Black Boar Gu | `[This Unit] gains the [Pork Hunger] status for [3] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units without [Pork Hunger]>` | 3 | data/hunger.csv |
| Black Boar Gu | `[This Unit] loses the [Black Boar Gu] promotion <upon losing the [Pork Hunger] status> <when below [0] [Wild Boar]> <with [50]% chance>` | 50 | data/hunger.csv |
| Jade Skin Gu | `[+15]% Strength <when defending> <when above [-1] [Jade]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| Jade Skin Gu | `Consumes [1] [Jade]` | 1 | data/gu.csv `eats` |
| Jade Skin Gu | `[This Unit] gains the [Jade Hunger] status for [3] turn(s) <upon turn start> <when below [0] [Jade]> <for units without [Jade Hunger]>` | 3 | data/hunger.csv |
| Jade Skin Gu | `[This Unit] loses the [Jade Skin Gu] promotion <upon losing the [Jade Hunger] status> <when below [0] [Jade]> <with [50]% chance>` | 50 | data/hunger.csv |
| Liquor Worm | `[+50]% XP gained from combat <when above [-1] [Wine]>` | +50 | data/gu.csv `effects` / `extra_uniques` |
| Liquor Worm | `Consumes [1] [Wine]` | 1 | data/gu.csv `eats` |
| Liquor Worm | `[This Unit] gains the [Wine Hunger] status for [3] turn(s) <upon turn start> <when below [0] [Wine]> <for units without [Wine Hunger]>` | 3 | data/hunger.csv |
| Liquor Worm | `[This Unit] loses the [Liquor Worm] promotion <upon losing the [Wine Hunger] status> <when below [0] [Wine]> <with [50]% chance>` | 50 | data/hunger.csv |
| White Jade Gu | `[+15]% Strength <when above [-1] [Jade]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| White Jade Gu | `[+30]% Strength <when defending> <when above [-1] [Jade]>` | +30 | data/gu.csv `effects` / `extra_uniques` |
| White Jade Gu | `Consumes [2] [Jade]` | 2 | data/gu.csv `eats` |
| White Jade Gu | `[This Unit] gains the [Jade Hunger] status for [5] turn(s) <upon turn start> <when below [0] [Jade]> <for units without [Jade Hunger]>` | 5 | data/hunger.csv |
| White Jade Gu | `[This Unit] loses the [White Jade Gu] promotion <upon losing the [Jade Hunger] status> <when below [0] [Jade]> <with [50]% chance>` | 50 | data/hunger.csv |
| Moon Raiment | `[+20]% Strength <when attacking> <when above [-1] [Moon Orchid]>` | +20 | data/gu.csv `effects` / `extra_uniques` |
| Moon Raiment | `[+20]% Strength <when defending> <when above [-1] [Moon Orchid]>` | +20 | data/gu.csv `effects` / `extra_uniques` |
| Moon Raiment | `[+10]% Strength bonus for [Military] units within [1] tiles <when above [-1] [Moon Orchid]>` | +10, 1 | data/gu.csv `effects` / `extra_uniques` |
| Moon Raiment | `Consumes [1] [Moon Orchid]` | 1 | data/gu.csv `eats` |
| Moon Raiment | `[This Unit] gains the [Orchid Hunger] status for [5] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units without [Orchid Hunger]>` | 5 | data/hunger.csv |
| Moon Raiment | `[This Unit] loses the [Moon Raiment] promotion <upon losing the [Orchid Hunger] status> <when below [0] [Moon Orchid]> <with [50]% chance>` | 50 | data/hunger.csv |
| Killer Move | `[+25]% Strength <when attacking>` | +25 | tools/gen_ruleset.py `Promotions` |
| Killer Move | `[+25]% maintenance costs` | +25 | tools/gen_ruleset.py `Promotions` |
| Bear Strength Gu | `[+10]% Strength` | +10 | tools/gen_ruleset.py `Promotions` |
| Bear Strength Gu | `[+10]% maintenance costs` | +10 | tools/gen_ruleset.py `Promotions` |
| Stream Gu | `[+10] HP when healing` | +10 | tools/gen_ruleset.py `Promotions` |
| Stream Gu | `[+10]% maintenance costs` | +10 | tools/gen_ruleset.py `Promotions` |

### Events.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Aptitude Awakening › Grade A aptitude | `[-95]% weight to this choice for AI decisions` | -95 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade A aptitude | `[+100]% weight to this choice for AI decisions <if [Awakening Grounds] is constructed>` | +100 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade A aptitude | `[+100]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | +100 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade B aptitude | `[-80]% weight to this choice for AI decisions` | -80 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade B aptitude | `[+50]% weight to this choice for AI decisions <if [Awakening Grounds] is constructed>` | +50 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade B aptitude | `[+25]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | +25 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade C aptitude | `[-65]% weight to this choice for AI decisions` | -65 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade D aptitude | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › Grade D aptitude | `[-25]% weight to this choice for AI decisions <if [Awakening Grounds] is constructed>` | -25 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Only available <if [Refinement Chamber] is constructed> <when above [80] [Gold]>` | 80 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Unavailable <when below [140] [Gold]> <during the [Rank Three era]>` | 140 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Unavailable <when below [200] [Gold]> <during the [Rank Four era]>` | 200 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Gain [-40] [Gold] <during the [Rank One-Two era]>` | -40 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Gain [-70] [Gold] <during the [Rank Three era]>` | -70 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Gain [-100] [Gold] <during the [Rank Four era]>` | -100 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Killer Move] promotion <for units with [Moon Raiment]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when above [0] [Wild Boar]> <with [90]% chance>` | 90 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when below [1] [Wild Boar]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when above [0] [Wild Boar]> <with [90]% chance>` | 90 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when below [1] [Wild Boar]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Moon Raiment] promotion <for [Moon Gu Master] units> <for units with [Moonlight Gu]> <for units with [Jade Skin Gu]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Moon Raiment] promotion <for [Moon Gu Master] units> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Boar Gu] promotion <for [Strength Gu Master] units> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when above [0] [Wild Boar]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Moonlight Gu] promotion <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when above [0] [Moon Orchid]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Jade Skin Gu] promotion <for [Gu Master] units> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `[-60]% weight to this choice for AI decisions <when below [150] [Gold]>` | -60, 150 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `Unavailable <when below [31] HP>` | 31 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Killer Move] promotion <for units with [Moon Raiment]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when above [0] [Wild Boar]> <with [60]% chance>` | 60 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when below [1] [Wild Boar]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when above [0] [Wild Boar]> <with [60]% chance>` | 60 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for [Strength Gu Master] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when below [1] [Wild Boar]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Moon Raiment] promotion <for [Moon Gu Master] units> <for units with [Moonlight Gu]> <for units with [Jade Skin Gu]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Moon Raiment] promotion <for [Moon Gu Master] units> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Boar Gu] promotion <for [Strength Gu Master] units> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when above [0] [Wild Boar]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Moonlight Gu] promotion <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when above [0] [Moon Orchid]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Jade Skin Gu] promotion <for [Gu Master] units> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] takes [30] damage` | 30 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `[-90]% weight to this choice for AI decisions <when below [50] HP>` | -90, 50 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `Only available <for [Gu Master] units> <for units without [Liquor Worm]> <when above [0] [Wine]> <when above [30] [Gold]>` | 30 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `Gain [-30] [Gold]` | -30 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `[This Unit] gains the [Liquor Worm] promotion <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Let the furnace cool | `[This Unit] gains [5] XP` | 5 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Let the furnace cool | `[-95]% weight to this choice for AI decisions` | -95 | tools/gen_ruleset.py `Events` |
| Beast Tide › Meet the wolves in the field | `[2] [Lightning Wolf]s rebel <during the [Rank One-Two era]>` | 2 | tools/gen_ruleset.py `Events` |
| Beast Tide › Meet the wolves in the field | `[3] [Lightning Wolf]s rebel <starting from the [Rank Three era]>` | 3 | tools/gen_ruleset.py `Events` |
| Beast Tide › Meet the wolves in the field | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Only available <when above [60] [Gold]>` | 60 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Unavailable <when below [100] [Gold]> <during the [Rank Three era]>` | 100 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Unavailable <when below [150] [Gold]> <during the [Rank Four era]>` | 150 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Gain [-60] [Gold] <during the [Rank One-Two era]>` | -60 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Gain [-100] [Gold] <during the [Rank Three era]>` | -100 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Gain [-150] [Gold] <during the [Rank Four era]>` | -150 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Beast Tide › Abandon the outer fields | `[-1] population [in all cities]` | -1 | tools/gen_ruleset.py `Events` |
| Beast Tide › Abandon the outer fields | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Beast Tide › Raise the formation | `Only available <if [Formation Platform] is constructed> <when above [70] [Gold]>` | 70 | tools/gen_ruleset.py `Events` |
| Beast Tide › Raise the formation | `Gain [-40] [Gold] <during the [Rank Three era]>` | -40 | tools/gen_ruleset.py `Events` |
| Beast Tide › Raise the formation | `Gain [-70] [Gold] <during the [Rank Four era]>` | -70 | tools/gen_ruleset.py `Events` |
| Beast Tide › Raise the formation | `[-20]% [Production] <for [5] turns>` | -20, 5 | tools/gen_ruleset.py `Events` |
| Beast Tide › Raise the formation | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Betrayal › Let the traitor go | `Only available <when above [60] [Gold]>` | 60 | tools/gen_ruleset.py `Events` |
| Betrayal › Let the traitor go | `Gain [-60] [Gold]` | -60 | tools/gen_ruleset.py `Events` |
| Betrayal › Let the traitor go | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Betrayal › Hunt the traitor down | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Betrayal › Judge the traitor by clan law | `[-1] population [in capital]` | -1 | tools/gen_ruleset.py `Events` |
| Betrayal › Judge the traitor by clan law | `[+2 Happiness] <for [10] turns>` | +2, 10 | tools/gen_ruleset.py `Events` |
| Betrayal › Judge the traitor by clan law | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Betrayal › Strike first and take the traitor's Gu | `Gain [40] [Gold]` | 40 | tools/gen_ruleset.py `Events` |
| Betrayal › Strike first and take the traitor's Gu | `[-1] population [in capital]` | -1 | tools/gen_ruleset.py `Events` |
| Betrayal › Strike first and take the traitor's Gu | `[-3 Happiness] <for [10] turns>` | -3, 10 | tools/gen_ruleset.py `Events` |
| Betrayal › Strike first and take the traitor's Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Betrayal › Strike first and take the traitor's Gu | `[-75]% weight to this choice for AI decisions <when below [0] [Happiness]>` | -75, 0 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Ration the Gu feed | `[-40]% maintenance costs <for [8] turns>` | -40, 8 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Ration the Gu feed | `[-15]% Strength <for [8] turns>` | -15, 8 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Ration the Gu feed | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Borrow from the merchant caravans | `Only available <when above [-100] [Gold]>` | -100 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Borrow from the merchant caravans | `Gain [80] [Gold]` | 80 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Borrow from the merchant caravans | `[-6 Gold] <for [20] turns>` | -6, 20 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Borrow from the merchant caravans | `[-80]% weight to this choice for AI decisions` | -80 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Squeeze the mortals | `Gain [50] [Gold]` | 50 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Squeeze the mortals | `[-1] population [in capital]` | -1 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Squeeze the mortals | `[-20]% weight to this choice for AI decisions` | -20 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `Gain [70] [Gold]` | 70 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `Triggers a [Betrayal] event <with [25]% chance>` | 25 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Wild Gu › Only the wind in the grass | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Events` |
| Wild Gu › A wild Gu stirs nearby | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Wild Gu Caught › Capture the wild Liquor Worm | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Wild Gu Caught › Capture the wild Jade Skin Gu | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Wild Gu Caught › Capture the wild Black Boar Gu | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Inheritance Rumour › An empty cave | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Inheritance Rumour › Something is buried here | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Claim it for the clan | `Gain control over [Land] tiles in a [1]-tile radius` | 1 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Claim it for the clan | `[This Unit] gains [20] XP` | 20 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Claim it for the clan | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Strip it and vanish | `Gain [60] [Gold]` | 60 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Strip it and vanish | `[This Unit] gains [30] XP` | 30 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Strip it and vanish | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |

### Buildings.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Clan Head Pavilion | cost | 0 | tools/gen_ruleset.py `Buildings` |
| Clan Head Pavilion | production | 3 | tools/gen_ruleset.py `Buildings` |
| Clan Head Pavilion | gold | 5 | tools/gen_ruleset.py `Buildings` |
| Clan Head Pavilion | science | 2 | tools/gen_ruleset.py `Buildings` |
| Clan Head Pavilion | culture | 3 | tools/gen_ruleset.py `Buildings` |
| Clan Head Pavilion | happiness | 1 | tools/gen_ruleset.py `Buildings` |
| Clan Head Pavilion | cityStrength | 3 | tools/gen_ruleset.py `Buildings` |
| Awakening Grounds | cost | 75 | tools/gen_ruleset.py `Buildings` |
| Awakening Grounds | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Awakening Grounds | gold | 2 | tools/gen_ruleset.py `Buildings` |
| Moon Orchid Flower Sea | cost | 75 | tools/gen_ruleset.py `Buildings` |
| Moon Orchid Flower Sea | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Moon Orchid Flower Sea | gold | 2 | tools/gen_ruleset.py `Buildings` |
| Moon Orchid Flower Sea | `Provides [2] [Moon Orchid]` | 2 | tools/gen_ruleset.py `Buildings` |
| Gu Academy | cost | 65 | tools/gen_ruleset.py `Buildings` |
| Gu Academy | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Gu Academy | science | 1 | tools/gen_ruleset.py `Buildings` |
| Gu Academy | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Gu Academy | `[+1 Science] per [2] population [in this city]` | +1, 2 | tools/gen_ruleset.py `Buildings` |
| Gu Academy | `New [Military] units start with [10] XP [in this city]` | 10 | tools/gen_ruleset.py `Buildings` |
| Gu Feeding House | cost | 70 | tools/gen_ruleset.py `Buildings` |
| Gu Feeding House | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Gu Feeding House | `Provides [1] [Moon Orchid]` | 1 | tools/gen_ruleset.py `Buildings` |
| Gu Feeding House | `Provides [1] [Wild Boar]` | 1 | tools/gen_ruleset.py `Buildings` |
| Tavern | cost | 60 | tools/gen_ruleset.py `Buildings` |
| Tavern | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Tavern | happiness | 1 | tools/gen_ruleset.py `Buildings` |
| Tavern | `Provides [1] [Wine]` | 1 | tools/gen_ruleset.py `Buildings` |
| Refinement Chamber | cost | 90 | tools/gen_ruleset.py `Buildings` |
| Refinement Chamber | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Refinement Chamber | production | 1 | tools/gen_ruleset.py `Buildings` |
| Refinement Chamber | science | 1 | tools/gen_ruleset.py `Buildings` |
| Refinement Chamber | `Provides [1] [Jade]` | 1 | tools/gen_ruleset.py `Buildings` |
| Formation Platform | cost | 110 | tools/gen_ruleset.py `Buildings` |
| Formation Platform | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Formation Platform | cityStrength | 8 | tools/gen_ruleset.py `Buildings` |
| Formation Platform | cityHealth | 50 | tools/gen_ruleset.py `Buildings` |
| Martial Arena | cost | 65 | tools/gen_ruleset.py `Buildings` |
| Martial Arena | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Martial Arena | science | 1 | tools/gen_ruleset.py `Buildings` |
| Martial Arena | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Martial Arena | `[+1 Science] per [2] population [in this city]` | +1, 2 | tools/gen_ruleset.py `Buildings` |
| Martial Arena | `New [Military] units start with [20] XP [in this city]` | 20 | tools/gen_ruleset.py `Buildings` |
| Trading House | cost | 130 | tools/gen_ruleset.py `Buildings` |
| Trading House | gold | 2 | tools/gen_ruleset.py `Buildings` |
| Trading House | percentStatBonus.gold | 20 | tools/gen_ruleset.py `Buildings` |
| Flower Wine Monk Inheritance | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Flower Wine Monk Inheritance | culture | 3 | tools/gen_ruleset.py `Buildings` |
| Flower Wine Monk Inheritance | gold | 4 | tools/gen_ruleset.py `Buildings` |
| Flower Wine Monk Inheritance | `Provides [2] [Jade]` | 2 | tools/gen_ruleset.py `Buildings` |
| Flower Wine Monk Inheritance | `[+15]% XP gained from combat` | +15 | tools/gen_ruleset.py `Buildings` |
| Flower Wine Monk Inheritance | `[+15]% Strength <vs [Gu Yue Clan] units>` | +15 | tools/gen_ruleset.py `Buildings` |
| Shang Clan City | cost | 300 | tools/gen_ruleset.py `Buildings` |
| Shang Clan City | gold | 5 | tools/gen_ruleset.py `Buildings` |
| Shang Clan City | `[+2 Gold] from all [Trading House] buildings` | +2 | tools/gen_ruleset.py `Buildings` |
| Shang Clan City | `Receive [+50]% Gold from Barbarian encampments and pillaging Cities` | +50 | tools/gen_ruleset.py `Buildings` |

### Techs.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Column 1 (Aperture Awakening) | techCost | 20 | data/tech_columns.csv `techCost` |
| Column 1 (Aperture Awakening) | buildingCost | 45 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 1 (Aperture Awakening) | wonderCost | 75 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 2 (Spirit Spring Lore, Gu Feeding) | techCost | 40 | data/tech_columns.csv `techCost` |
| Column 2 (Spirit Spring Lore, Gu Feeding) | buildingCost | 60 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 2 (Spirit Spring Lore, Gu Feeding) | wonderCost | 140 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 3 (Wine Brewing, Gu Refinement, Rank Two Cultivation) | techCost | 65 | data/tech_columns.csv `techCost` |
| Column 3 (Wine Brewing, Gu Refinement, Rank Two Cultivation) | buildingCost | 75 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 3 (Wine Brewing, Gu Refinement, Rank Two Cultivation) | wonderCost | 170 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 4 (Gu Formations, Rank Three Cultivation) | techCost | 120 | data/tech_columns.csv `techCost` |
| Column 4 (Gu Formations, Rank Three Cultivation) | buildingCost | 100 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 4 (Gu Formations, Rank Three Cultivation) | wonderCost | 220 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 5 (Merchant Caravans, Inheritance Lore, Killer Moves) | techCost | 170 | data/tech_columns.csv `techCost` |
| Column 5 (Merchant Caravans, Inheritance Lore, Killer Moves) | buildingCost | 130 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 5 (Merchant Caravans, Inheritance Lore, Killer Moves) | wonderCost | 240 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 6 (Super Clan Commerce, Beast Enslavement, Rank Four Cultivation) | techCost | 250 | data/tech_columns.csv `techCost` |
| Column 6 (Super Clan Commerce, Beast Enslavement, Rank Four Cultivation) | buildingCost | 160 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 6 (Super Clan Commerce, Beast Enslavement, Rank Four Cultivation) | wonderCost | 300 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Beast Enslavement | `When defeating a [Beast] unit, earn [10] Gold and recruit it <when number of [[Gold] Per Turn] is more than [4]>` | 10, 4 | data/techs.csv `uniques` |
| Column 7 (Dao Comprehension) | techCost | 350 | data/tech_columns.csv `techCost` |
| Column 7 (Dao Comprehension) | buildingCost | 200 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 7 (Dao Comprehension) | wonderCost | 350 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |

### Policies.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Righteous Path | priorities.Southern Border Supremacy | 2 | tools/gen_ruleset.py `Policies` |
| Righteous Path | priorities.Endurance | 6 | tools/gen_ruleset.py `Policies` |
| Righteous Path | `Resting point for Influence with City-States is increased by [15]` | 15 | tools/gen_ruleset.py `Policies` |
| Righteous Path | `[-25]% maintenance costs <in [Friendly Land] tiles>` | -25 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Clan Rules | `[-15]% Unhappiness from [Population] [in all cities]` | -15 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Righteous Alliance | `Gifts of Gold to City-States generate [+25]% more Influence` | +25 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Guardian Formations | `[+25]% Strength for cities` | +25 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Guardian Formations | `[+10]% Strength <when defending>` | +10 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Righteous Path Complete | `[-10]% maintenance costs` | -10 | tools/gen_ruleset.py `Policies` |
| Demonic Path | priorities.Southern Border Supremacy | 6 | tools/gen_ruleset.py `Policies` |
| Demonic Path | priorities.Endurance | 2 | tools/gen_ruleset.py `Policies` |
| Demonic Path | `Earn [50]% of killed [Military] unit's [Cost] as [Gold]` | 50 | tools/gen_ruleset.py `Policies` |
| Demonic Path | `[+50]% City-State Influence degradation` | +50 | tools/gen_ruleset.py `Policies` |
| Demonic Path | `Triggers a [Betrayal] event <upon turn start> <with [3]% chance>` | 3 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Plunder | `[+100]% Yield from pillaging tiles` | +100 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Plunder | `Receive [+100]% Gold from Barbarian encampments and pillaging Cities` | +100 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Lone Cultivators | `[2] units cost no maintenance` | 2 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Lone Cultivators | `[+30]% unhappiness from the number of cities` | +30 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Ruthless Cultivation | `Upon capturing a city, receive [3] times its [Gold] production as [Gold] immediately` | 3 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Ruthless Cultivation | `[-20]% maintenance costs <when at war>` | -20 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Ruthless Cultivation | `[+20]% Unhappiness from [Population] [in all cities]` | +20 | tools/gen_ruleset.py `Policies` |
| Demonic Path › Demonic Path Complete | `[+15]% Strength <when attacking>` | +15 | tools/gen_ruleset.py `Policies` |
| Moon Path | priorities.Southern Border Supremacy | 5 | tools/gen_ruleset.py `Policies` |
| Moon Path | priorities.Endurance | 5 | tools/gen_ruleset.py `Policies` |
| Moon Path | `Provides [2] [Moon Orchid]` | 2 | tools/gen_ruleset.py `Policies` |
| Moon Path | `[+5]% Strength <for [Moon Gu Master] units> <for every [Adopted [[Moon Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moonlight Mastery | `[+15]% Strength <for units with [Moonlight Gu]>` | +15 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moonlight Mastery | `[+15]% Strength <for units with [Moon Raiment]>` | +15 | tools/gen_ruleset.py `Policies` |
| Moon Path › Orchid Terraces | `Provides [2] [Moon Orchid]` | 2 | tools/gen_ruleset.py `Policies` |
| Moon Path › Orchid Terraces | `[-15]% maintenance costs <for [Moon Gu Master] units>` | -15 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moon Blade Step | `[1] Movement <for [Moon Gu Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moon Path Complete | `New [Moon Gu Master] units start with [10] XP [in all cities]` | 10 | tools/gen_ruleset.py `Policies` |
| Strength Path | priorities.Southern Border Supremacy | 5 | tools/gen_ruleset.py `Policies` |
| Strength Path | priorities.Endurance | 5 | tools/gen_ruleset.py `Policies` |
| Strength Path | `Provides [2] [Wild Boar]` | 2 | tools/gen_ruleset.py `Policies` |
| Strength Path | `[+5]% Strength <for [Strength Gu Master] units> <for every [Adopted [[Strength Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Strength Path › Boar Strength | `[+15]% Strength <for units with [White Boar Gu]>` | +15 | tools/gen_ruleset.py `Policies` |
| Strength Path › Boar Strength | `[+15]% Strength <for units with [White Jade Gu]>` | +15 | tools/gen_ruleset.py `Policies` |
| Strength Path › Beast Hunters | `Provides [2] [Wild Boar]` | 2 | tools/gen_ruleset.py `Policies` |
| Strength Path › Beast Hunters | `[+25]% Strength <vs [Barbarians] units>` | +25 | tools/gen_ruleset.py `Policies` |
| Strength Path › Unyielding Body | `Heals [10] damage if it kills a unit` | 10 | tools/gen_ruleset.py `Policies` |
| Strength Path › Strength Path Complete | `[1] Movement <for [Strength Gu Master] units>` | 1 | tools/gen_ruleset.py `Policies` |

### TileResources.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Spirit Spring | gold | 2 | tools/gen_ruleset.py `Resources` |
| Spirit Spring | improvementStats.gold | 3 | tools/gen_ruleset.py `Resources` |
| Spirit Spring | minorDepositAmount.sparse | 1 | tools/gen_ruleset.py `Resources` |
| Spirit Spring | minorDepositAmount.default | 1 | tools/gen_ruleset.py `Resources` |
| Spirit Spring | minorDepositAmount.abundant | 1 | tools/gen_ruleset.py `Resources` |
| Spirit Spring | majorDepositAmount.sparse | 1 | tools/gen_ruleset.py `Resources` |
| Spirit Spring | majorDepositAmount.default | 1 | tools/gen_ruleset.py `Resources` |
| Spirit Spring | majorDepositAmount.abundant | 1 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | food | 1 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | improvementStats.food | 1 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | minorDepositAmount.sparse | 1 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | minorDepositAmount.default | 1 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | minorDepositAmount.abundant | 2 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | majorDepositAmount.sparse | 2 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | majorDepositAmount.default | 2 | tools/gen_ruleset.py `Resources` |
| Moon Orchid | majorDepositAmount.abundant | 3 | tools/gen_ruleset.py `Resources` |
| Wild Boar | food | 1 | tools/gen_ruleset.py `Resources` |
| Wild Boar | improvementStats.production | 1 | tools/gen_ruleset.py `Resources` |
| Wild Boar | minorDepositAmount.sparse | 1 | tools/gen_ruleset.py `Resources` |
| Wild Boar | minorDepositAmount.default | 1 | tools/gen_ruleset.py `Resources` |
| Wild Boar | minorDepositAmount.abundant | 2 | tools/gen_ruleset.py `Resources` |
| Wild Boar | majorDepositAmount.sparse | 2 | tools/gen_ruleset.py `Resources` |
| Wild Boar | majorDepositAmount.default | 2 | tools/gen_ruleset.py `Resources` |
| Wild Boar | majorDepositAmount.abundant | 3 | tools/gen_ruleset.py `Resources` |
| Jade | gold | 1 | tools/gen_ruleset.py `Resources` |
| Jade | improvementStats.gold | 1 | tools/gen_ruleset.py `Resources` |
| Jade | minorDepositAmount.sparse | 1 | tools/gen_ruleset.py `Resources` |
| Jade | minorDepositAmount.default | 1 | tools/gen_ruleset.py `Resources` |
| Jade | minorDepositAmount.abundant | 2 | tools/gen_ruleset.py `Resources` |
| Jade | majorDepositAmount.sparse | 2 | tools/gen_ruleset.py `Resources` |
| Jade | majorDepositAmount.default | 2 | tools/gen_ruleset.py `Resources` |
| Jade | majorDepositAmount.abundant | 3 | tools/gen_ruleset.py `Resources` |
| Gu Inheritance | science | 3 | tools/gen_ruleset.py `Resources` |
| Gu Inheritance | culture | 2 | tools/gen_ruleset.py `Resources` |
| Gu Inheritance | gold | 2 | tools/gen_ruleset.py `Resources` |
| Gu Inheritance | improvementStats.science | 2 | tools/gen_ruleset.py `Resources` |
| Gu Inheritance | improvementStats.gold | 2 | tools/gen_ruleset.py `Resources` |
| Furs | gold | 2 | tools/gen_ruleset.py `Resources` |
| Furs | improvementStats.gold | 1 | tools/gen_ruleset.py `Resources` |

### TileImprovements.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Farm | food | 1 | tools/gen_ruleset.py `Improvements` |
| Farm | turnsToBuild | 7 | tools/gen_ruleset.py `Improvements` |
| Mine | production | 1 | tools/gen_ruleset.py `Improvements` |
| Mine | turnsToBuild | 7 | tools/gen_ruleset.py `Improvements` |
| Spring Cave | turnsToBuild | 6 | tools/gen_ruleset.py `Improvements` |
| Spring Cave | `Pillaging this improvement yields approximately [+20 Gold]` | +20 | tools/gen_ruleset.py `Improvements` |
| Plantation | turnsToBuild | 6 | tools/gen_ruleset.py `Improvements` |
| Camp | turnsToBuild | 6 | tools/gen_ruleset.py `Improvements` |
| Road | turnsToBuild | 4 | tools/gen_ruleset.py `Improvements` |
| Road | `Costs [1] [Gold] per turn when in your territory` | 1 | tools/gen_ruleset.py `Improvements` |
| Inheritance Dig | turnsToBuild | 5 | tools/gen_ruleset.py `Improvements` |
| Remove Forest | turnsToBuild | 4 | tools/gen_ruleset.py `Improvements` |
| Remove Jungle | turnsToBuild | 7 | tools/gen_ruleset.py `Improvements` |
| Remove Marsh | turnsToBuild | 6 | tools/gen_ruleset.py `Improvements` |
| Remove Road | turnsToBuild | 2 | tools/gen_ruleset.py `Improvements` |
| Repair | turnsToBuild | 2 | tools/gen_ruleset.py `Improvements` |

### Ruins.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Primeval Stone Cache | weight | 4 | tools/gen_ruleset.py `Ruins` |
| Primeval Stone Cache | `Gain [30]-[60] [Gold]` | 30-60 | tools/gen_ruleset.py `Ruins` |
| Cultivation Notes | weight | 3 | tools/gen_ruleset.py `Ruins` |
| Cultivation Notes | `Gain [15]-[30] [Science]` | 15-30 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | weight | 3 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <when below [50] HP>` | 50 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for [Gu Master] units> <for units with [Jade Skin Gu]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for [Gu Master] units> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Inheritance Trial | weight | 2 | tools/gen_ruleset.py `Ruins` |
| Inheritance Trial | `[This Unit] gains [30] XP` | 30 | tools/gen_ruleset.py `Ruins` |
| Inheritance Trial | `[This Unit] takes [40] damage` | 40 | tools/gen_ruleset.py `Ruins` |
| Inheritance Trial | `Unavailable <when below [41] HP>` | 41 | tools/gen_ruleset.py `Ruins` |
| Inheritance Trap | weight | 1 | tools/gen_ruleset.py `Ruins` |
| Inheritance Trap | `[This Unit] takes [40] damage` | 40 | tools/gen_ruleset.py `Ruins` |
| Inheritance Trap | `Only available <for [Military] units> <after turn number [10]>` | 10 | tools/gen_ruleset.py `Ruins` |
| Lone Demonic Gu Master | weight | 1 | tools/gen_ruleset.py `Ruins` |

### Nations.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Bai Clan | `[+15]% Strength <vs [Barbarians] units>` | +15 | tools/gen_ruleset.py `Nations` |

### CityStateTypes.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Refiner Tribe (friendBonusUniques) | `[+2 Science] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Refiner Tribe (allyBonusUniques) | `[+2 Science] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Refiner Tribe (allyBonusUniques) | `[+20]% XP gained from combat` | +20 | tools/gen_ruleset.py `Nations` |
| Mortal Villages (friendBonusUniques) | `[+2 Food] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Mortal Villages (allyBonusUniques) | `[+2 Food] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Mortal Villages (allyBonusUniques) | `[+2 Production] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Merchant Clan (friendBonusUniques) | `[+2 Gold] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Merchant Clan (allyBonusUniques) | `[+3 Gold] [in capital]` | +3 | tools/gen_ruleset.py `Nations` |
| Merchant Clan (allyBonusUniques) | `[+10]% [Gold]` | +10 | tools/gen_ruleset.py `Nations` |

### Personalities.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Gu Yue Temperament | science | 7 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | culture | 6 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | gold | 5 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | military | 4 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | aggressive | 3 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | priorities.Moon Path | 10 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | priorities.Righteous Path | 6 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | `[+50]% weight to [Gu Academy] for AI decisions` | +50 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | `[+100]% weight to [Awakening Grounds] for AI decisions` | +100 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | gold | 7 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | production | 6 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | science | 6 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | military | 4 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | aggressive | 3 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | priorities.Moon Path | 8 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | priorities.Righteous Path | 7 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | `[+50]% weight to [Gu Academy] for AI decisions` | +50 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | `[+100]% weight to [Awakening Grounds] for AI decisions` | +100 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | military | 7 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | aggressive | 6 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | production | 6 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | priorities.Strength Path | 10 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | priorities.Demonic Path | 6 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | priorities.Righteous Path | 3 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | `[+50]% weight to [Gu Academy] for AI decisions` | +50 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | `[+100]% weight to [Awakening Grounds] for AI decisions` | +100 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | military | 7 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | aggressive | 4 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | production | 6 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | loyal | 7 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | expansion | 5 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | priorities.Righteous Path | 10 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | priorities.Strength Path | 10 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | `[+50]% weight to [Martial Arena] for AI decisions` | +50 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | `[+100]% weight to [Awakening Grounds] for AI decisions` | +100 | tools/gen_ruleset.py `Nations` |

### Eras.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Rank One-Two era | researchAgreementCost | 150 | tools/gen_ruleset.py `Eras` |
| Rank One-Two era | startingWorkerCount | 1 | tools/gen_ruleset.py `Eras` |
| Rank One-Two era | startingGold | 50 | tools/gen_ruleset.py `Eras` |
| Rank One-Two era | baseUnitBuyCost | 200 | tools/gen_ruleset.py `Eras` |
| Rank Three era | researchAgreementCost | 250 | tools/gen_ruleset.py `Eras` |
| Rank Three era | baseUnitBuyCost | 300 | tools/gen_ruleset.py `Eras` |
| Rank Four era | researchAgreementCost | 350 | tools/gen_ruleset.py `Eras` |
| Rank Four era | baseUnitBuyCost | 400 | tools/gen_ruleset.py `Eras` |

### UnitTypes.json

No tunable numbers.

### Terrains.json, Speeds.json

Vanilla copies (tools/gen_ruleset.py `Terrains (Vanilla minus natural wonders and Fallout)` and the Speeds line in `Nations (Difficulties)`); the only change is that no terrain grants an extra Spirit Spring. Tune them there if a playtest asks for it; until then the Vanilla numbers stand.

510 numbers listed.

<!-- inventory:end -->
