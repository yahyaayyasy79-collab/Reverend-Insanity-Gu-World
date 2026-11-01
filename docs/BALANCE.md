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
| Gu Master upkeep | Rank One +50%; Strength +100 / +125 / +175%; Moon +75 / +100 / +150% (round 8; were +25%, +100 / +175 / +275%, +75 / +150 / +225%) | `data/gu_masters.csv` `maintenance` | Prince, Standard, T320: clans 20+ turns in the red 38 → 11 of 48, upkeep 111% → 90% of gross income in the last quarter, 17% in T1–50 (round 8) | Ranks 3–4 compound with the engine's turn-number growth: raise them only with a 320-turn A/B. The spec asks for about 40% early |
| Free upkeep | Clan Settler and Mortal Laborer `[-100]% maintenance costs` (round 8: mortals do not eat primeval stones); otherwise none for majors: `[-3] units cost no maintenance` cancels the engine's 3 free units [src CivInfoStatsForNextTurn.getUnitMaintenance]; the Demonic policy Lone Cultivators gives 2 back | `tools/gen_ruleset.py` `Units`, `GlobalUniques`, `Policies` | Free mortals alone: 38 → 26 of 48 clans in the red (round 8, v1) | Already at the floor; push early pressure through Gu Master upkeep instead |
| Wild Gu | 6% per Gu Master per turn, then a 1-in-5 die (weights +300 / +0): 1.2% on Standard; the die keeps the rate per era on other speeds (`die_weights`: Marathon 0.4%) | `WILD_GU_TRIGGER`, `Events` `Wild Gu` | 1.55 Jade Skin and 2.19 Black Boar per clan by T200, 36 games (6b) | The user asked for about 1.2%; change the die, not the trigger (E5) |
| Buried inheritance | 1% per Gu Master per turn in foreign land after Inheritance Lore, then 1 in 2 on Standard (Marathon 1 in 6) | `INHERITANCE_TRIGGER`, `Events` `Inheritance Rumour` | 1.75 inheritances per game, 36 games (6b; 1 in 8 gave 0.42) | If fewer than 1 per game, the clans have nothing to fight over |
| Inheritance claim | takes the land tiles in a 1-tile radius (−10 relations per tile, engine), +20 XP; or strip it for 60 stones and +30 XP | `Events` `Buried Inheritance` | The AI claims 2 times in 3 (weights +100 / +0, E1) | Radius 2 makes it a war trigger; try it only with a human game in hand |
| Gu Inheritance yield | tile 3 science, 2 culture, 2 stones; Inheritance Dig +2 science, +2 stones; +20% combat XP while held | `Resources`, `Improvements`, `GlobalUniques` | — | — |
| Beast tide | Standard: 3% per turn after T30, another 2% after T90. Per speed (round 7): Quick 4% / 3% after T20 / T60, Epic 2% / 1% after T45 / T135, Marathon 1% / 1% after T90 / T270 | `GlobalUniques` (`per_speed`, `chance`, `turn_gate`) | Pillage 7–10× Vanilla's (round 5) | Lower if pillage starves clans in human games |
| Betrayal | Standard: 8% per turn while unhappy, 3% while above 300 stones (Quick 12 / 4, Epic 5 / 2, Marathon 3 / 1) | `GlobalUniques` | — | — |
| Stone shortage | Standard: 25% per turn with a negative treasury and income (Quick 37, Epic 17, Marathon 8) | `GlobalUniques` | — | — |
| Population-cost choices | Judge, Strike first, Squeeze: only while the capital has more than 3 population; Abandon the outer fields: −50% growth in every city for 10 turns (was −1 population in every city) | `Events` (`CAP_POP`) | Round 7 (AUTOPLAY.md) | Keep every population cost gated: at population 1 a loss is void and the reward free |
| Happiness | every difficulty +6 base happiness (one luxury only) | `tools/gen_ruleset.py` `Nations (Difficulties)` | — | — |
| Spirit Spring | 1 deposit per start (Strategic Balance), Spring Cave +3 stones, 6 turns | `Resources`, `Improvements` | Improved late: the AI keeps one laborer (experiments, baseline) | The user wants laborers produced, not given: do not add a free laborer |
| Gu food deposits | minor 1 / 1 / 2, major 2 / 2 / 3 (sparse / default / abundant) | `tools/gen_ruleset.py` `DEP` | Every clan ends with a surplus of every food (round 5) | Lower majors to 1 / 1 / 2 if hunger should matter in peace |
| Barbarian XP cap | 90 XP | `ModOptions` `maxXPfromBarbarians` | — | — |

## What the data says is off

Not fixed, because each needs either a human game or the user's taste:

1. **Early upkeep is light.** The spec asks for upkeep near 40% of stone income early; autoplay measures 17% in
   T1–50 (round 8: Rank One went +25% → +50%, but mortals stopped paying). The candidate left is a stone upkeep on the
   Gu Academy and Gu Feeding House (1 → 2).
2. **The late game is not tense.** Treasuries grow: mean 431 stones in T151–200 at King after round 8 (244 before).
   Candidates: costlier careful refinement in rank four, or upkeep on Killer Move above +25%. The immortal arc's
   essence and lifespan Gu (MOD_SPEC_2) are the real sink; tune this after they exist.
3. **Food is abundant in peace.** Hunger only bites when wars pillage camps and plantations. That fits the novel (Gu
   starve in sieges, not in good years), so it stays unless the user wants hunger in peacetime.
4. **A few AI clans go broke in long wars:** 4 of 144 spent 20+ turns in the red (6b). No disband spiral, so the
   spec's line holds, but it is the number to watch in the user's 100-turn game.
5. **The late-game stone economy at Prince: mostly fixed (round 8).** By turn 320 on Standard, 38 of 48 AI clans had
   spent 20+ turns in the red; after round 8, 11 of 48 (mean treasury −69 → 101 stones). Those 11 keep their armies;
   the rest of the deficit is war and the engine's upkeep growth with the turn number. A richer Trading House ended
   it but piled up 400–700 stones (AUTOPLAY.md round 8), so it was left out. The tech tree ending near T120 (item 6)
   is the root: Slice 2's ranks give late income something to buy.
6. **The tech tree ends near T113–123.** Slice 1 has 15 techs; the rest of the game is Dao Comprehension. Slice 2 adds
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
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [20]> <with [4]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 20, 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [30]> <with [3]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 30, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [45]> <with [2]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 45, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [90]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 90, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [60]> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 60, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [90]> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 90, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [135]> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 135, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Beast Tide] event <upon turn start> <after turn number [270]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 270, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [12]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 0, 12 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [8]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 0, 8 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [5]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 0, 5 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [3]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 0, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [4]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 300, 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [3]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 300, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [2]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 300, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 300, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [37]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 0, 0, 37 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [25]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 0, 0, 25 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [17]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 0, 0, 17 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [8]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 0, 0, 8 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Collusion Exposed] event <upon turn start> <after adopting [Righteous Path]> <when number of [Adopted [[Demonic Path] branch] Policies by [Friendly] Civilizations] is more than [0]> <with [4]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 0, 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Collusion Exposed] event <upon turn start> <after adopting [Righteous Path]> <when number of [Adopted [[Demonic Path] branch] Policies by [Friendly] Civilizations] is more than [0]> <with [3]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 0, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Collusion Exposed] event <upon turn start> <after adopting [Righteous Path]> <when number of [Adopted [[Demonic Path] branch] Policies by [Friendly] Civilizations] is more than [0]> <with [2]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 0, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Collusion Exposed] event <upon turn start> <after adopting [Righteous Path]> <when number of [Adopted [[Demonic Path] branch] Policies by [Friendly] Civilizations] is more than [0]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 0, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Whitewashed Name] event <upon turn start> <after adopting [Demonic Path]> <if [Shang Clan City] is constructed by anybody> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Whitewashed Name] event <upon turn start> <after adopting [Demonic Path]> <if [Shang Clan City] is constructed by anybody> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Whitewashed Name] event <upon turn start> <after adopting [Demonic Path]> <if [Shang Clan City] is constructed by anybody> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Whitewashed Name] event <upon turn start> <after adopting [Demonic Path]> <if [Shang Clan City] is constructed by anybody> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Clan Contest] event <upon turn start> <after turn number [40]> <when not at war> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 40, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Clan Contest] event <upon turn start> <after turn number [60]> <when not at war> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 60, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Clan Contest] event <upon turn start> <after turn number [90]> <when not at war> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 90, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Clan Contest] event <upon turn start> <after turn number [180]> <when not at war> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 180, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Collusion Exposed] event <upon conquering a city> <after adopting [Righteous Path]> <with [25]% chance> <for [Major] Civilizations>` | 25 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[+20]% XP gained from combat <with [Gu Inheritance]>` | +20 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Heaven Qi] <upon turn start> <for every [15] [Owned [Land] Tiles]> <after discovering [Three Qi]> <for [Major] Civilizations>` | 1, 15 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Earth Qi] <upon turn start> <for every [1] [Owned [Spring Cave] Tiles]> <after discovering [Three Qi]> <for [Major] Civilizations>` | 1, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Earth Qi] <upon turn start> <for every [8] [Owned [Hill] Tiles]> <after discovering [Three Qi]> <for [Major] Civilizations>` | 1, 8 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Human Qi] <upon turn start> <for every [10] [[Population] in [in all cities] Cities]> <after discovering [Three Qi]> <for [Major] Civilizations>` | 1, 10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Earn [5]% of the damage done to [All] units as [Human Qi] <after discovering [Three Qi]> <for [Major] Civilizations>` | 5 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Forest] Tiles]> <with [22]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Quick] game speed>` | 1, 8, 22 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Forest] Tiles]> <with [15]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Standard] game speed>` | 1, 8, 15 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Forest] Tiles]> <with [10]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Epic] game speed>` | 1, 8, 10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Forest] Tiles]> <with [5]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Marathon] game speed>` | 1, 8, 5 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Jungle] Tiles]> <with [22]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Quick] game speed>` | 1, 8, 22 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Jungle] Tiles]> <with [15]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Standard] game speed>` | 1, 8, 15 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Jungle] Tiles]> <with [10]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Epic] game speed>` | 1, 8, 10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Jungle] Tiles]> <with [5]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Marathon] game speed>` | 1, 8, 5 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Marsh] Tiles]> <with [22]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Quick] game speed>` | 1, 8, 22 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Marsh] Tiles]> <with [15]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Standard] game speed>` | 1, 8, 15 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Marsh] Tiles]> <with [10]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Epic] game speed>` | 1, 8, 10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly provides [1] [Lifespan Gu] <upon turn start> <for every [8] [Owned [Marsh] Tiles]> <with [5]% chance> <after discovering [Calamity Lore]> <for [Major] Civilizations> <on [Marathon] game speed>` | 1, 8, 5 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [4]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 2, 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [3]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 2, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [2]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 2, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 2, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[Immortal Gu] Buildings] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [4]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 2, 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[Immortal Gu] Buildings] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [3]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 2, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[Immortal Gu] Buildings] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [2]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 2, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Heaven's Will] event <upon turn start> <when number of [[Immortal Gu] Buildings] is more than [2]> <if [Divination Tortoise Shell] is not constructed> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 2, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Free [Rank Six Gu Immortal] appears <upon losing a [{post-[Rank Five era]} {non-[Advancing]}] unit> <if [Spring Autumn Cicada] is constructed> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Free [Rank Six Gu Immortal] appears <upon losing a [{post-[Rank Five era]} {non-[Advancing]}] unit> <if [Connect Luck] is constructed> <if [Spring Autumn Cicada] is constructed> <with [25]% chance>` | 25 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Inheritance Trial] event <upon turn start> <when number of [Owned [Land] Tiles] is more than [30]> <after discovering [Calamity Lore]> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 30, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Inheritance Trial] event <upon turn start> <when number of [Owned [Land] Tiles] is more than [30]> <after discovering [Calamity Lore]> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 30, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Inheritance Trial] event <upon turn start> <when number of [Owned [Land] Tiles] is more than [30]> <after discovering [Calamity Lore]> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 30, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Inheritance Trial] event <upon turn start> <when number of [Owned [Land] Tiles] is more than [30]> <after discovering [Calamity Lore]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 30, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Desolate Beast Tide] event <upon turn start> <after discovering [Three Qi]> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Desolate Beast Tide] event <upon turn start> <after discovering [Three Qi]> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Desolate Beast Tide] event <upon turn start> <after discovering [Three Qi]> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Desolate Beast Tide] event <upon turn start> <after discovering [Three Qi]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Treasure Yellow Heaven] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [0]> <with [6]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 0, 6 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Treasure Yellow Heaven] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [0]> <with [4]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 0, 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Treasure Yellow Heaven] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [0]> <with [3]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 0, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Treasure Yellow Heaven] event <upon turn start> <when number of [[post-[Rank Five era]] Units] is more than [0]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 0, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Earn [10]% of killed [Desolate Beast] unit's [Cost] as [Immortal Materials]` | 10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Earn [10]% of killed [Ancient Desolate Beast] unit's [Cost] as [Immortal Materials]` | 10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Earn [10]% of killed [Immemorial Desolate Beast] unit's [Cost] as [Immortal Materials]` | 10 | tools/gen_ruleset.py `ModOptions / Globals` |

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

The 12 clan units (ranks 2-4 of Gu Yue, Bai, Xiong and Wu) copy their rank's numbers: tune the rank's row and its clan rows in data/gu_masters.csv together (tools/gen_ruleset.py asserts they match). The 6 legacy units only carry old saves into the rank chain and are left out.

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Clan Settler | movement | 2 | tools/gen_ruleset.py `Units` |
| Clan Settler | cost | 80 | tools/gen_ruleset.py `Units` |
| Clan Settler | `[-100]% maintenance costs` | -100 | tools/gen_ruleset.py `Units` |
| Clan Settler | `Requires at least [2] population` | 2 | tools/gen_ruleset.py `Units` |
| Clan Settler | `Can only be built <when above [-11] [Happiness]>` | -11 | tools/gen_ruleset.py `Units` |
| Mortal Laborer | movement | 2 | tools/gen_ruleset.py `Units` |
| Mortal Laborer | cost | 45 | tools/gen_ruleset.py `Units` |
| Mortal Laborer | `[-100]% maintenance costs` | -100 | tools/gen_ruleset.py `Units` |
| Rank One Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank One Gu Master | strength | 8 | data/gu_masters.csv `strength` |
| Rank One Gu Master | cost | 35 | data/gu_masters.csv `cost` |
| Rank One Gu Master | `[+50]% maintenance costs` | +50 | data/gu_masters.csv `maintenance` |
| Rank One Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank One Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank One Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Two Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Two Gu Master | strength | 14 | data/gu_masters.csv `strength` |
| Rank Two Gu Master | cost | 60 | data/gu_masters.csv `cost` |
| Rank Two Gu Master | `[+100]% maintenance costs` | +100 | data/gu_masters.csv `maintenance` |
| Rank Two Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Two Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Two Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Three Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Three Gu Master | strength | 22 | data/gu_masters.csv `strength` |
| Rank Three Gu Master | cost | 95 | data/gu_masters.csv `cost` |
| Rank Three Gu Master | `[+125]% maintenance costs` | +125 | data/gu_masters.csv `maintenance` |
| Rank Three Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Three Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Three Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Four Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Four Gu Master | strength | 32 | data/gu_masters.csv `strength` |
| Rank Four Gu Master | cost | 140 | data/gu_masters.csv `cost` |
| Rank Four Gu Master | `[+175]% maintenance costs` | +175 | data/gu_masters.csv `maintenance` |
| Rank Four Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Four Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Four Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Five Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Five Gu Master | strength | 44 | data/gu_masters.csv `strength` |
| Rank Five Gu Master | cost | 190 | data/gu_masters.csv `cost` |
| Rank Five Gu Master | `[+225]% maintenance costs` | +225 | data/gu_masters.csv `maintenance` |
| Rank Five Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Five Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Five Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Six Gu Immortal | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | strength | 60 | data/gu_masters.csv `strength` |
| Rank Six Gu Immortal | cost | 260 | data/gu_masters.csv `cost` |
| Rank Six Gu Immortal | `[+300]% maintenance costs` | +300 | data/gu_masters.csv `maintenance` |
| Rank Six Gu Immortal | `[+15]% Strength <when above [9] [Green Grape Immortal Essence]>` | +15, 9 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Six Gu Immortal | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Six Gu Immortal | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [7] turns> <on [Quick] game speed>` | 1, 7 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [10] turns> <on [Standard] game speed>` | 1, 10 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [15] turns> <on [Epic] game speed>` | 1, 15 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [30] turns> <on [Marathon] game speed>` | 1, 30 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Can only heal by pillaging <when below [1] [Lifespan Gu]>` | 1 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] takes [7] damage <upon turn start> <when below [1] [Lifespan Gu]>` | 7, 1 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | strength | 85 | data/gu_masters.csv `strength` |
| Rank Seven Gu Immortal | cost | 330 | data/gu_masters.csv `cost` |
| Rank Seven Gu Immortal | `[+350]% maintenance costs` | +350 | data/gu_masters.csv `maintenance` |
| Rank Seven Gu Immortal | `[+15]% Strength <when above [9] [Red Date Immortal Essence]>` | +15, 9 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Seven Gu Immortal | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Seven Gu Immortal | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [7] turns> <on [Quick] game speed>` | 1, 7 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [10] turns> <on [Standard] game speed>` | 1, 10 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [15] turns> <on [Epic] game speed>` | 1, 15 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [30] turns> <on [Marathon] game speed>` | 1, 30 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Can only heal by pillaging <when below [1] [Lifespan Gu]>` | 1 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] takes [7] damage <upon turn start> <when below [1] [Lifespan Gu]>` | 7, 1 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | strength | 115 | data/gu_masters.csv `strength` |
| Rank Eight Gu Immortal | cost | 400 | data/gu_masters.csv `cost` |
| Rank Eight Gu Immortal | `[+400]% maintenance costs` | +400 | data/gu_masters.csv `maintenance` |
| Rank Eight Gu Immortal | `[+15]% Strength <when above [9] [White Lychee Immortal Essence]>` | +15, 9 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Eight Gu Immortal | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Eight Gu Immortal | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [7] turns> <on [Quick] game speed>` | 1, 7 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [10] turns> <on [Standard] game speed>` | 1, 10 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [15] turns> <on [Epic] game speed>` | 1, 15 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [30] turns> <on [Marathon] game speed>` | 1, 30 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Can only heal by pillaging <when below [1] [Lifespan Gu]>` | 1 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] takes [7] damage <upon turn start> <when below [1] [Lifespan Gu]>` | 7, 1 | tools/gen_ruleset.py `gm()` |
| Lightning Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | strength | 9 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | cost | 30 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | `[+50]% maintenance costs` | +50 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | strength | 16 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | cost | 60 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | `[+15]% Strength bonus for [Lightning Wolf] units within [2] tiles` | +15, 2 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | `[+100]% maintenance costs` | +100 | tools/gen_ruleset.py `Units` |
| Desolate Beast | movement | 3 | tools/gen_ruleset.py `Units` |
| Desolate Beast | strength | 62 | tools/gen_ruleset.py `Units` |
| Desolate Beast | cost | 200 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[+200]% maintenance costs` | +200 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | movement | 3 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | strength | 85 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | cost | 300 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[+250]% maintenance costs` | +250 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | movement | 3 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | strength | 115 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | cost | 500 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[+300]% maintenance costs` | +300 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | strength | 28 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | cost | 120 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | `[+20]% Strength bonus for [Beast] units within [2] tiles` | +20, 2 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | `[+200]% maintenance costs` | +200 | tools/gen_ruleset.py `Units` |

### UnitPromotions.json

The path promotions and their statuses are listed under 'Paths' below.

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
| Refine Gu | `Unavailable <for units with [Killer Move]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Moon Master]> <for units with [Moon Raiment]> <before discovering [Killer Moves]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Jade Gu]> <before discovering [Killer Moves]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Moon Master]> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when below [1] [Moon Orchid]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Moon Master]> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when below [1] [Wild Boar]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when below [2] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Moon Master]> <for units with [Moonlight Gu]> <for [Rank One Gu Master] units> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Boar Gu]> <for [Rank One Gu Master] units> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units without [Moon Master]> <for units without [Strength Master]> <for units with [Jade Skin Gu]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Refine Gu | `Unavailable <for units without [Moon Master]> <for units without [Strength Master]> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Promotions` |
| Moonlight Gu | `[+20]% Strength <when attacking> <when above [-1] [Moon Orchid]>` | +20 | data/gu.csv `effects` / `extra_uniques` |
| Moonlight Gu | `Consumes [1] [Moon Orchid]` | 1 | data/gu.csv `eats` |
| Moonlight Gu | `[This Unit] gains the [Orchid Hunger] status for [3] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units without [Orchid Hunger]>` | 3 | data/hunger.csv |
| Moonlight Gu | `[This Unit] loses the [Moonlight Gu] promotion <upon losing the [Orchid Hunger] status> <when below [0] [Moon Orchid]> <with [50]% chance>` | 50 | data/hunger.csv |
| Moonlight Gu | `[-10]% Strength <for units with [Strength Master]>` | -10 | data/gu.csv `effects` / `extra_uniques` |
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
| Ascension | `Unavailable <when below [20] [Heaven Qi]> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [30] [Heaven Qi]> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [45] [Heaven Qi]> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [90] [Heaven Qi]> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [20] [Earth Qi]> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [30] [Earth Qi]> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [45] [Earth Qi]> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [90] [Earth Qi]> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [20] [Human Qi]> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [30] [Human Qi]> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [45] [Human Qi]> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [90] [Human Qi]> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [40] [Heaven Qi]> <for [AI player] Civilizations> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [60] [Heaven Qi]> <for [AI player] Civilizations> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [90] [Heaven Qi]> <for [AI player] Civilizations> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [180] [Heaven Qi]> <for [AI player] Civilizations> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [40] [Earth Qi]> <for [AI player] Civilizations> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [60] [Earth Qi]> <for [AI player] Civilizations> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [90] [Earth Qi]> <for [AI player] Civilizations> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [180] [Earth Qi]> <for [AI player] Civilizations> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [40] [Human Qi]> <for [AI player] Civilizations> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [60] [Human Qi]> <for [AI player] Civilizations> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [90] [Human Qi]> <for [AI player] Civilizations> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascension | `Unavailable <when below [180] [Human Qi]> <for [AI player] Civilizations> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `Instantly provides [1] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units>` | 1 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `Instantly provides [1] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units>` | 1 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `Gain [2] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [9] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 9 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [14] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 14 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [21] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 21 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [42] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 42 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Instantly provides [2] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units>` | 2 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Instantly provides [2] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units>` | 2 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Gain [4] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 4 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [9] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 9 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [13] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 13 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [20] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [39] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 39 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Instantly provides [3] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units>` | 3 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Instantly provides [3] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units>` | 3 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Gain [6] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 6 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [8] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 8 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [12] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 12 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [18] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 18 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [36] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 36 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Instantly provides [5] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units>` | 5 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Instantly provides [5] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units>` | 5 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Gain [10] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 10 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [7] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 7 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [11] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 11 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [16] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 16 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [33] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 33 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `Instantly provides [3] [White Lychee Immortal Essence] <upon turn start> <for units without [Ravaged Land]>` | 3 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `Gain [12] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 12 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Calamity Countdown] status for [7] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 7 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Calamity Countdown] status for [10] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 10 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Calamity Countdown] status for [15] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 15 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Calamity Countdown] status for [30] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Tribulation Countdown] status for [34] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Quick] game speed>` | 34 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Tribulation Countdown] status for [50] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Standard] game speed>` | 50 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Tribulation Countdown] status for [75] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Epic] game speed>` | 75 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `[This Unit] gains the [Tribulation Countdown] status for [150] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <on [Marathon] game speed>` | 150 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Unavailable <when below [40] [Green Grape Immortal Essence]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Unavailable <when below [60] [Green Grape Immortal Essence]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Unavailable <when below [90] [Green Grape Immortal Essence]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Unavailable <when below [180] [Green Grape Immortal Essence]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Instantly consumes [40] [Green Grape Immortal Essence] <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Instantly consumes [60] [Green Grape Immortal Essence] <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Instantly consumes [90] [Green Grape Immortal Essence] <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `Instantly consumes [180] [Green Grape Immortal Essence] <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `[This Unit] gains the [Advancing] status for [1] turn(s)` | 1 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Seven | `[+200]% weight to this choice for AI decisions` | +200 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Unavailable <when below [40] [Red Date Immortal Essence]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Unavailable <when below [60] [Red Date Immortal Essence]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Unavailable <when below [90] [Red Date Immortal Essence]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Unavailable <when below [180] [Red Date Immortal Essence]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Instantly consumes [40] [Red Date Immortal Essence] <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Instantly consumes [60] [Red Date Immortal Essence] <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Instantly consumes [90] [Red Date Immortal Essence] <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `Instantly consumes [180] [Red Date Immortal Essence] <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `[This Unit] gains the [Advancing] status for [1] turn(s)` | 1 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `[+200]% weight to this choice for AI decisions` | +200 | tools/gen_ruleset.py `Promotions` |

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
| Refinement Attempt › Refine carefully | `Unavailable <when below [200] [Gold]> <starting from the [Rank Four era]>` | 200 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Gain [-40] [Gold] <during the [Rank One-Two era]>` | -40 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Gain [-70] [Gold] <during the [Rank Three era]>` | -70 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `Gain [-100] [Gold] <starting from the [Rank Four era]>` | -100 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Killer Move] promotion <for units with [Moon Master]> <for units with [Moon Raiment]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Killer Move] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Jade Gu]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when above [0] [Wild Boar]> <for units without [Killer Move]> <with [90]% chance>` | 90 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when below [1] [Wild Boar]> <for units without [Killer Move]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when above [0] [Wild Boar]> <for units without [Killer Move]> <with [90]% chance>` | 90 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when below [1] [Wild Boar]> <for units without [Killer Move]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Moon Raiment] promotion <for units with [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [Moonlight Gu]> <for units with [Jade Skin Gu]> <for units without [Killer Move]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Moon Raiment] promotion <for units with [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <for units without [Killer Move]> <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [White Boar Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when above [0] [Wild Boar]> <for units without [Killer Move]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Moonlight Gu] promotion <for units with [Moon Master]> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when above [0] [Moon Orchid]> <for units without [Killer Move]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[This Unit] gains the [Jade Skin Gu] promotion <for units without [Moon Master]> <for units without [Strength Master]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <for units without [Killer Move]> <with [85]% chance>` | 85 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine carefully | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine carefully | `[-60]% weight to this choice for AI decisions <when below [150] [Gold]>` | -60, 150 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `Unavailable <when below [31] HP>` | 31 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Killer Move] promotion <for units with [Moon Master]> <for units with [Moon Raiment]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Killer Move] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Jade Gu]> <for units without [Killer Move]> <after discovering [Killer Moves]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when above [0] [Wild Boar]> <for units without [Killer Move]> <with [60]% chance>` | 60 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when above [0] [Jade]> <when below [1] [Wild Boar]> <for units without [Killer Move]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when above [0] [Wild Boar]> <for units without [Killer Move]> <with [60]% chance>` | 60 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Jade Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when above [1] [Jade]> <when below [1] [Wild Boar]> <for units without [Killer Move]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Moon Raiment] promotion <for units with [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [Moonlight Gu]> <for units with [Jade Skin Gu]> <for units without [Killer Move]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Moon Raiment] promotion <for units with [Moon Master]> <for [non-[Rank One Gu Master]] units> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <for units without [Killer Move]> <with [40]% chance>` | 40 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [White Boar Gu] promotion <for units with [Strength Master]> <for units without [Moon Master]> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when above [0] [Wild Boar]> <for units without [Killer Move]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Moonlight Gu] promotion <for units with [Moon Master]> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when above [0] [Moon Orchid]> <for units without [Killer Move]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] gains the [Jade Skin Gu] promotion <for units without [Moon Master]> <for units without [Strength Master]> <for units without [Jade Skin Gu]> <when above [0] [Jade]> <for units without [Killer Move]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Refine recklessly | `[This Unit] takes [30] damage` | 30 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Refine recklessly | `[-90]% weight to this choice for AI decisions <when below [50] HP>` | -90, 50 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `Only available <for [Rank One Gu Master] units> <for units without [Liquor Worm]> <when above [0] [Wine]> <when above [30] [Gold]>` | 30 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `Gain [-30] [Gold]` | -30 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `[This Unit] gains the [Liquor Worm] promotion <with [70]% chance>` | 70 | tools/gen_ruleset.py `ladder()` arguments |
| Refinement Attempt › Lure a wild Liquor Worm with Green Bamboo Wine | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Stop and recover your essence | `[This Unit] gains [5] XP` | 5 | tools/gen_ruleset.py `Events` |
| Refinement Attempt › Stop and recover your essence | `[-95]% weight to this choice for AI decisions` | -95 | tools/gen_ruleset.py `Events` |
| Beast Tide › Meet the wolves in the field | `[2] [Lightning Wolf]s rebel <during the [Rank One-Two era]>` | 2 | tools/gen_ruleset.py `Events` |
| Beast Tide › Meet the wolves in the field | `[3] [Lightning Wolf]s rebel <starting from the [Rank Three era]>` | 3 | tools/gen_ruleset.py `Events` |
| Beast Tide › Meet the wolves in the field | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Only available <when above [60] [Gold]>` | 60 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Unavailable <when below [100] [Gold]> <during the [Rank Three era]>` | 100 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Unavailable <when below [150] [Gold]> <starting from the [Rank Four era]>` | 150 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Gain [-60] [Gold] <during the [Rank One-Two era]>` | -60 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Gain [-100] [Gold] <during the [Rank Three era]>` | -100 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `Gain [-150] [Gold] <starting from the [Rank Four era]>` | -150 | tools/gen_ruleset.py `Events` |
| Beast Tide › Hire demonic Gu Masters to thin the pack | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Beast Tide › Abandon the outer fields | `[-50]% growth [in all cities] <for [10] turns>` | -50, 10 | tools/gen_ruleset.py `Events` |
| Beast Tide › Abandon the outer fields | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Beast Tide › Man the stockade walls | `Only available <if [Stockade Wall] is constructed> <when above [70] [Gold]>` | 70 | tools/gen_ruleset.py `Events` |
| Beast Tide › Man the stockade walls | `Gain [-40] [Gold] <during the [Rank Three era]>` | -40 | tools/gen_ruleset.py `Events` |
| Beast Tide › Man the stockade walls | `Gain [-70] [Gold] <starting from the [Rank Four era]>` | -70 | tools/gen_ruleset.py `Events` |
| Beast Tide › Man the stockade walls | `[-20]% [Production] <for [5] turns>` | -20, 5 | tools/gen_ruleset.py `Events` |
| Beast Tide › Man the stockade walls | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Beast Tide › Call the clans' alliance | `Only available <when number of [Known [Major] Civilizations] is more than [1]> <when not at war>` | 1 | tools/gen_ruleset.py `Events` |
| Beast Tide › Call the clans' alliance | `[2] [Lightning Wolf]s rebel <during the [Rank One-Two era]>` | 2 | tools/gen_ruleset.py `Events` |
| Beast Tide › Call the clans' alliance | `[3] [Lightning Wolf]s rebel <starting from the [Rank Three era]>` | 3 | tools/gen_ruleset.py `Events` |
| Beast Tide › Call the clans' alliance | `[+30]% Strength <vs [Barbarians] units> <for [10] turns>` | +30, 10 | tools/gen_ruleset.py `Events` |
| Beast Tide › Call the clans' alliance | `[-10]% [Gold] <for [10] turns>` | -10, 10 | tools/gen_ruleset.py `Events` |
| Beast Tide › Call the clans' alliance | `[+30]% weight to this choice for AI decisions` | +30 | tools/gen_ruleset.py `Events` |
| Betrayal › Let the traitor go | `Only available <when above [60] [Gold]>` | 60 | tools/gen_ruleset.py `Events` |
| Betrayal › Let the traitor go | `Gain [-60] [Gold]` | -60 | tools/gen_ruleset.py `Events` |
| Betrayal › Let the traitor go | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Betrayal › Hunt the traitor down | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Betrayal › Judge the traitor by clan law | `Only available <when number of [[Population] in [in capital] Cities] is more than [3]>` | 3 | tools/gen_ruleset.py `Events` |
| Betrayal › Judge the traitor by clan law | `[-1] population [in capital]` | -1 | tools/gen_ruleset.py `Events` |
| Betrayal › Judge the traitor by clan law | `[+2 Happiness] <for [10] turns>` | +2, 10 | tools/gen_ruleset.py `Events` |
| Betrayal › Judge the traitor by clan law | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Betrayal › Strike first and take the traitor's Gu | `Only available <when number of [[Population] in [in capital] Cities] is more than [3]>` | 3 | tools/gen_ruleset.py `Events` |
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
| Stone Shortage › Squeeze the mortals | `Only available <when number of [[Population] in [in capital] Cities] is more than [3]>` | 3 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Squeeze the mortals | `Gain [50] [Gold]` | 50 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Squeeze the mortals | `[-1] population [in capital]` | -1 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Squeeze the mortals | `[-20]% weight to this choice for AI decisions` | -20 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `Gain [70] [Gold]` | 70 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `Triggers a [Betrayal] event <with [25]% chance>` | 25 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `[+100]% City-State Influence degradation <for [10] turns>` | +100, 10 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `Triggers a [Collusion Exposed] event <after adopting [Righteous Path]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Stone Shortage › Rob a passing caravan | `[-80]% weight to this choice for AI decisions <after adopting [Righteous Path]>` | -80 | tools/gen_ruleset.py `Events` |
| Collusion Exposed › Pay to bury the scandal | `Only available <when above [100] [Gold]>` | 100 | tools/gen_ruleset.py `Events` |
| Collusion Exposed › Pay to bury the scandal | `Gain [-100] [Gold]` | -100 | tools/gen_ruleset.py `Events` |
| Collusion Exposed › Pay to bury the scandal | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Collusion Exposed › Ride it out | `[-3 Happiness] <for [10] turns>` | -3, 10 | tools/gen_ruleset.py `Events` |
| Collusion Exposed › Ride it out | `[+100]% City-State Influence degradation <for [10] turns>` | +100, 10 | tools/gen_ruleset.py `Events` |
| Collusion Exposed › Ride it out | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Collusion Exposed › Walk the demonic path openly | `[-50]% weight to this choice for AI decisions` | -50 | tools/gen_ruleset.py `Events` |
| Whitewashed Name › Buy a righteous name | `Only available <when above [150] [Gold]>` | 150 | tools/gen_ruleset.py `Events` |
| Whitewashed Name › Buy a righteous name | `Gain [-150] [Gold]` | -150 | tools/gen_ruleset.py `Events` |
| Whitewashed Name › Buy a righteous name | `[-50]% weight to this choice for AI decisions` | -50 | tools/gen_ruleset.py `Events` |
| Whitewashed Name › Stay what you are | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters carry the day | `Gain [60] [Gold]` | 60 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters carry the day | `New [Gu Master] units start with [10] XP [in all cities] <for [10] turns>` | 10, 10 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters carry the day | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters carry the day | `[+100]% weight to this choice for AI decisions <if [Martial Arena] is constructed>` | +100 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters carry the day | `[+100]% weight to this choice for AI decisions <when number of [[Military] Units] is more than [8]>` | +100, 8 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters are beaten | `Gain [-30] [Gold]` | -30 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters are beaten | `[-3 Happiness] <for [10] turns>` | -3, 10 | tools/gen_ruleset.py `Events` |
| Clan Contest › Your young Gu Masters are beaten | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Blood Lake › Seal the lake and speak of it to no one | `Only available <when above [80] [Gold]>` | 80 | tools/gen_ruleset.py `Events` |
| Blood Lake › Seal the lake and speak of it to no one | `Gain [-80] [Gold]` | -80 | tools/gen_ruleset.py `Events` |
| Blood Lake › Seal the lake and speak of it to no one | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Blood Lake › Send for the Tie clan's constable | `[+2 Happiness] <for [10] turns>` | +2, 10 | tools/gen_ruleset.py `Events` |
| Blood Lake › Send for the Tie clan's constable | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Blood Lake › Claim the founder's blood inheritance | `Gain [150] [Gold]` | 150 | tools/gen_ruleset.py `Events` |
| Blood Lake › Claim the founder's blood inheritance | `[+15]% Strength <for [10] turns>` | +15, 10 | tools/gen_ruleset.py `Events` |
| Blood Lake › Claim the founder's blood inheritance | `[-50]% weight to this choice for AI decisions` | -50 | tools/gen_ruleset.py `Events` |
| Wild Gu › Only the wind in the grass | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Events` |
| Wild Gu › Only the wind in the grass | `[-41]% weight to this choice for AI decisions <on [Quick] game speed>` | -41 | tools/gen_ruleset.py `Events` |
| Wild Gu › Only the wind in the grass | `[+62]% weight to this choice for AI decisions <on [Epic] game speed>` | +62 | tools/gen_ruleset.py `Events` |
| Wild Gu › Only the wind in the grass | `[+250]% weight to this choice for AI decisions <on [Marathon] game speed>` | +250 | tools/gen_ruleset.py `Events` |
| Wild Gu › A wild Gu stirs nearby | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Wild Gu Caught › Capture the wild Liquor Worm | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Wild Gu Caught › Capture the wild Jade Skin Gu | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Wild Gu Caught › Capture the wild Black Boar Gu | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Inheritance Rumour › An empty cave | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Inheritance Rumour › An empty cave | `[-66]% weight to this choice for AI decisions <on [Quick] game speed>` | -66 | tools/gen_ruleset.py `Events` |
| Inheritance Rumour › An empty cave | `[+100]% weight to this choice for AI decisions <on [Epic] game speed>` | +100 | tools/gen_ruleset.py `Events` |
| Inheritance Rumour › An empty cave | `[+400]% weight to this choice for AI decisions <on [Marathon] game speed>` | +400 | tools/gen_ruleset.py `Events` |
| Inheritance Rumour › Something is buried here | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Claim it for the clan | `Gain control over [Land] tiles in a [1]-tile radius` | 1 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Claim it for the clan | `[This Unit] gains [20] XP` | 20 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Claim it for the clan | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Strip it and vanish | `Gain [60] [Gold]` | 60 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Strip it and vanish | `[This Unit] gains [30] XP` | 30 | tools/gen_ruleset.py `Events` |
| Buried Inheritance › Strip it and vanish | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [40] [Heaven Qi]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [60] [Heaven Qi]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [90] [Heaven Qi]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [180] [Heaven Qi]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [40] [Earth Qi]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [60] [Earth Qi]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [90] [Earth Qi]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [180] [Earth Qi]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [40] [Human Qi]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [60] [Human Qi]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [90] [Human Qi]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Unavailable <when below [180] [Human Qi]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [40] [Heaven Qi] <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [60] [Heaven Qi] <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [90] [Heaven Qi] <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [180] [Heaven Qi] <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [40] [Earth Qi] <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [60] [Earth Qi] <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [90] [Earth Qi] <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [180] [Earth Qi] <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [40] [Human Qi] <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [60] [Human Qi] <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [90] [Human Qi] <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `Instantly consumes [180] [Human Qi] <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Events` |
| Ascension › Balance the three qi | `[+200]% weight to this choice for AI decisions` | +200 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [20] [Heaven Qi]> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [30] [Heaven Qi]> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [45] [Heaven Qi]> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [90] [Heaven Qi]> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [20] [Earth Qi]> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [30] [Earth Qi]> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [45] [Earth Qi]> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [90] [Earth Qi]> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [20] [Human Qi]> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [30] [Human Qi]> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [45] [Human Qi]> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Unavailable <when below [90] [Human Qi]> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [20] [Heaven Qi] <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [30] [Heaven Qi] <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [45] [Heaven Qi] <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [90] [Heaven Qi] <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [20] [Earth Qi] <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [30] [Earth Qi] <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [45] [Earth Qi] <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [90] [Earth Qi] <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [20] [Human Qi] <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [30] [Human Qi] <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [45] [Human Qi] <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `Instantly consumes [90] [Human Qi] <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Ascension › Ascend in haste | `[-80]% weight to this choice for AI decisions` | -80 | tools/gen_ruleset.py `Events` |
| Ascension › Not yet | `[-100]% weight to this choice for AI decisions` | -100 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A lower-grade blessed land opens | `Instantly provides [5] [Lifespan Gu]` | 5 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `Instantly provides [5] [Lifespan Gu]` | 5 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `Instantly provides [5] [Lifespan Gu]` | 5 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `[-75]% weight to this choice for AI decisions` | -75 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `[+100]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +100 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `[-50]% weight to this choice for AI decisions <for units with [Aptitude D]>` | -50 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `Instantly provides [5] [Lifespan Gu]` | 5 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `[-96]% weight to this choice for AI decisions` | -96 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `[+150]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +150 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `[-100]% weight to this choice for AI decisions <for units with [Aptitude D]>` | -100 | tools/gen_ruleset.py `Events` |
| Ascension Trial › The aperture collapses | `[-50]% weight to this choice for AI decisions` | -50 | tools/gen_ruleset.py `Events` |
| Ascension Trial › The aperture collapses | `[-50]% weight to this choice for AI decisions <for units with [Aptitude A]>` | -50 | tools/gen_ruleset.py `Events` |
| Ascension Trial › The aperture collapses | `[+100]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +100 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `Instantly provides [5] [Lifespan Gu]` | 5 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +0 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +0 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A middle-grade blessed land opens | `Instantly provides [5] [Lifespan Gu]` | 5 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A middle-grade blessed land opens | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A middle-grade blessed land opens | `[+50]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +50 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A middle-grade blessed land opens | `[-50]% weight to this choice for AI decisions <for units with [Aptitude D]>` | -50 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › The aperture collapses | `[+40]% weight to this choice for AI decisions` | +40 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › The aperture collapses | `[-40]% weight to this choice for AI decisions <for units with [Aptitude A]>` | -40 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › The aperture collapses | `[+60]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +60 | tools/gen_ruleset.py `Events` |
| Immortal Ascension › Enter the blessed land | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Aperture Collapse › Mourn the fallen | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Divert the disaster | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Beckon it to the land's edge | `[This Unit] takes [5] damage` | 5 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Beckon it to the land's edge | `Instantly provides [10] [Immortal Materials]` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Beckon it to the land's edge | `[+150]% weight to this choice for AI decisions` | +150 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Raise the formation ward | `[This Unit] takes [10] damage` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Raise the formation ward | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Rebuild from the vault | `Unavailable <when below [40] [Gold]>` | 40 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Rebuild from the vault | `Gain [-40] [Gold]` | -40 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Rebuild from the vault | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Unavailable <when below [10] [Green Grape Immortal Essence]>` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Instantly consumes [10] [Green Grape Immortal Essence]` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[This Unit] takes [15] damage` | 15 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Unavailable <when below [10] [Red Date Immortal Essence]>` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Instantly consumes [10] [Red Date Immortal Essence]` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[This Unit] takes [15] damage` | 15 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Unavailable <when below [10] [White Lychee Immortal Essence]>` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Instantly consumes [10] [White Lychee Immortal Essence]` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[This Unit] takes [15] damage` | 15 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Endure it | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Calamity Toll › The land is ravaged | `[This Unit] gains the [Ravaged Land] status for [5] turn(s) <on [Quick] game speed>` | 5 | tools/gen_ruleset.py `Events` |
| Calamity Toll › The land is ravaged | `[This Unit] gains the [Ravaged Land] status for [8] turn(s) <on [Standard] game speed>` | 8 | tools/gen_ruleset.py `Events` |
| Calamity Toll › The land is ravaged | `[This Unit] gains the [Ravaged Land] status for [12] turn(s) <on [Epic] game speed>` | 12 | tools/gen_ruleset.py `Events` |
| Calamity Toll › The land is ravaged | `[This Unit] gains the [Ravaged Land] status for [24] turn(s) <on [Marathon] game speed>` | 24 | tools/gen_ruleset.py `Events` |
| Calamity Toll › The land is ravaged | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Calamity Toll › The immortal is hurt | `[This Unit] takes [40] damage` | 40 | tools/gen_ruleset.py `Events` |
| Calamity Toll › The immortal is hurt | `[-40]% weight to this choice for AI decisions` | -40 | tools/gen_ruleset.py `Events` |
| Calamity Toll › It passes | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Divert the disaster | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `Unavailable <when below [30] [Green Grape Immortal Essence]>` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `Instantly consumes [30] [Green Grape Immortal Essence]` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `[This Unit] takes [30] damage` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `Unavailable <when below [30] [Red Date Immortal Essence]>` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `Instantly consumes [30] [Red Date Immortal Essence]` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `[This Unit] takes [30] damage` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `Unavailable <when below [30] [White Lychee Immortal Essence]>` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `Instantly consumes [30] [White Lychee Immortal Essence]` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `[This Unit] takes [30] damage` | 30 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Ward and essence together | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Unavailable <when below [50] [Green Grape Immortal Essence]>` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Instantly consumes [50] [Green Grape Immortal Essence]` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[This Unit] takes [50] damage` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Unavailable <when below [50] [Red Date Immortal Essence]>` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Instantly consumes [50] [Red Date Immortal Essence]` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[This Unit] takes [50] damage` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Unavailable <when below [50] [White Lychee Immortal Essence]>` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Instantly consumes [50] [White Lychee Immortal Essence]` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[This Unit] takes [50] damage` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Face it bare | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › The tribulation kills it | `[-44]% weight to this choice for AI decisions` | -44 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives, its land ravaged | `[This Unit] gains the [Ravaged Land] status for [7] turn(s) <on [Quick] game speed>` | 7 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives, its land ravaged | `[This Unit] gains the [Ravaged Land] status for [10] turn(s) <on [Standard] game speed>` | 10 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives, its land ravaged | `[This Unit] gains the [Ravaged Land] status for [15] turn(s) <on [Epic] game speed>` | 15 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives, its land ravaged | `[This Unit] gains the [Ravaged Land] status for [30] turn(s) <on [Marathon] game speed>` | 30 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives, its land ravaged | `[This Unit] takes [50] damage` | 50 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives, its land ravaged | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives | `[This Unit] takes [30] damage` | 30 | tools/gen_ruleset.py `Events` |
| Tribulation Toll › It survives | `[-33]% weight to this choice for AI decisions` | -33 | tools/gen_ruleset.py `Events` |
| Immortal Gu Refinement › The Gu takes shape | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Immortal Gu Refinement › Its birth calls down a calamity | `[-2] population [in this city]` | -2 | tools/gen_ruleset.py `Events` |
| Immortal Gu Refinement › Its birth calls down a calamity | `[2] [Bold Lightning Wolf]s rebel` | 2 | tools/gen_ruleset.py `Events` |
| Immortal Gu Refinement › Its birth calls down a calamity | `[-67]% weight to this choice for AI decisions` | -67 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Lie low | `[-20]% Strength <for [10] turns>` | -20, 10 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Lie low | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Pay heaven its due | `Unavailable <when below [30] [Green Grape Immortal Essence]>` | 30 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Pay heaven its due | `Instantly consumes [30] [Green Grape Immortal Essence]` | 30 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Pay heaven its due | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Defy heaven | `[2] [Bold Lightning Wolf]s rebel` | 2 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Defy heaven | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Nothing surfaces | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › The trial claims its seekers | `Only available <when number of [[Population] in [in capital] Cities] is more than [3]>` | 3 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › The trial claims its seekers | `[-2] population [in capital]` | -2 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › The trial claims its seekers | `[-80]% weight to this choice for AI decisions` | -80 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Primordial Origin Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Primordial Origin Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Qi Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Star Constellation Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Star Constellation Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Wisdom Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Limitless Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Limitless Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Rule Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Reckless Savage Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Reckless Savage Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Strength Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Red Lotus Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Red Lotus Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Time Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Genesis Lotus Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Genesis Lotus Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Wood Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Thieving Heaven Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Thieving Heaven Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Theft Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Giant Sun Luck Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Giant Sun Luck Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Luck Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Spectral Soul Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Spectral Soul Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Soul Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Paradise Earth Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Paradise Earth Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Earth Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Three Kings Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Three Kings Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Enslavement Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Long Hair Ancestor Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Long Hair Ancestor Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Refinement Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Hu Immortal Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Hu Immortal Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Human Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Blood Sea Inheritance: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › Blood Sea Inheritance: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Blood Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
| Inheritance Won › Begin the work | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Inheritance Lost › Bury the dead | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Desolate Beast Tide › Hunt it for its corpse | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Desolate Beast Tide › Turn it aside with the formation ward | `Unavailable <when below [80] [Gold]>` | 80 | tools/gen_ruleset.py `Events` |
| Desolate Beast Tide › Turn it aside with the formation ward | `Gain [-80] [Gold]` | -80 | tools/gen_ruleset.py `Events` |
| Desolate Beast Tide › Turn it aside with the formation ward | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Desolate Beast Tide › Let it rampage | `[-30]% [Production] [in all cities] <for [5] turns>` | -30, 5 | tools/gen_ruleset.py `Events` |
| Desolate Beast Tide › Let it rampage | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy green grape essence | `Unavailable <when below [150] [Gold]>` | 150 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy green grape essence | `Gain [-150] [Gold]` | -150 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy green grape essence | `Instantly provides [20] [Green Grape Immortal Essence]` | 20 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy green grape essence | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy Lifespan Gu | `Unavailable <when below [120] [Gold]>` | 120 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy Lifespan Gu | `Gain [-120] [Gold]` | -120 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy Lifespan Gu | `Instantly provides [3] [Lifespan Gu]` | 3 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy Lifespan Gu | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Buy Lifespan Gu | `[+300]% weight to this choice for AI decisions <when below [3] [Lifespan Gu]>` | +300, 3 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell immortal materials | `Unavailable <when below [20] [Immortal Materials]>` | 20 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell immortal materials | `Instantly consumes [20] [Immortal Materials]` | 20 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell immortal materials | `Instantly provides [25] [Green Grape Immortal Essence]` | 25 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell immortal materials | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell essence for stones | `Unavailable <when below [40] [Green Grape Immortal Essence]>` | 40 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell essence for stones | `Instantly consumes [40] [Green Grape Immortal Essence]` | 40 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell essence for stones | `Gain [200] [Gold]` | 200 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Sell essence for stones | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Appraise with treasure light | `Unavailable <when below [150] [Gold]>` | 150 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Appraise with treasure light | `Gain [-150] [Gold]` | -150 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Appraise with treasure light | `Instantly provides [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Appraise with treasure light | `[+150]% weight to this choice for AI decisions` | +150 | tools/gen_ruleset.py `Events` |
| Treasure Yellow Heaven › Leave the market | `[-50]% weight to this choice for AI decisions` | -50 | tools/gen_ruleset.py `Events` |

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
| Stockade Wall | cost | 110 | tools/gen_ruleset.py `Buildings` |
| Stockade Wall | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Stockade Wall | cityStrength | 8 | tools/gen_ruleset.py `Buildings` |
| Stockade Wall | cityHealth | 50 | tools/gen_ruleset.py `Buildings` |
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
| Formation Ward | cost | 220 | tools/gen_ruleset.py `Buildings` |
| Formation Ward | maintenance | 2 | tools/gen_ruleset.py `Buildings` |
| Formation Ward | cityStrength | 4 | tools/gen_ruleset.py `Buildings` |
| Stockpile Vault | cost | 160 | tools/gen_ruleset.py `Buildings` |
| Stockpile Vault | maintenance | 1 | tools/gen_ruleset.py `Buildings` |
| Stockpile Vault | gold | 2 | tools/gen_ruleset.py `Buildings` |
| Spring Autumn Cicada | cost | 390 | tools/gen_ruleset.py `Buildings` |
| Spring Autumn Cicada | `Costs [50] [Green Grape Immortal Essence]` | 50 | tools/gen_ruleset.py `Buildings` |
| Spring Autumn Cicada | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | `Costs [40] [Green Grape Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | `[+1] Movement <for [post-[Rank Five era]] units>` | +1 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Man as Before | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Man as Before | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Man as Before | `[+20] HP when healing <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Man as Before | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | `[+15]% [Science] [in all cities]` | +15 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | `[+10]% Strength <for [post-[Rank Five era]] units>` | +10 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Self Strength | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Self Strength | `Costs [40] [Green Grape Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Self Strength | `[+15]% Strength <for units with [Strength Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Self Strength | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | `[+20]% Strength <vs [Wounded] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | `[+20]% Strength <when defending> <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | cost | 300 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | `Costs [30] [Green Grape Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | `[+2] Sight <for [post-[Rank Five era]] units>` | +2 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Divert Disaster | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Divert Disaster | `Costs [40] [Green Grape Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Divert Disaster | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | `Costs [40] [Red Date Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | `[+20]% Strength <for units with [Strength Master]>` | +20 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Year Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Year Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Year Gu | `Instantly provides [1] [Lifespan Gu] <upon turn start> <every [3] turns>` | 1, 3 | tools/gen_ruleset.py `Buildings` |
| Year Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | `[+15]% Strength <when adjacent to a [Military] unit> <for [Military] units>` | +15 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | `[+30]% Strength <vs [Beast] units>` | +30 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | `Costs [30] [Red Date Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | `Earn [20]% of killed [Beast] unit's [Cost] as [Immortal Materials]` | 20 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Calamity Beckoning | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Calamity Beckoning | `Costs [30] [Red Date Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Calamity Beckoning | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Change Soul | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Change Soul | `Costs [30] [Red Date Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Change Soul | `[+20]% XP gained from combat <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Change Soul | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | `[+20]% Strength <when attacking> <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | cost | 480 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `Costs [40] [White Lychee Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `Instantly provides [1] [White Lychee Immortal Essence] <upon turn start>` | 1 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `Instantly provides [2] [Green Grape Immortal Essence] <upon turn start>` | 2 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | cost | 440 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `Costs [40] [White Lychee Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `Instantly provides [2] [Lifespan Gu] <upon turn start> <every [5] turns> <when above [9] [Green Grape Immortal Essence]>` | 2, 5, 9 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `Instantly consumes [10] [Green Grape Immortal Essence] <upon turn start> <every [5] turns> <when above [9] [Green Grape Immortal Essence]>` | 10, 5, 9 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dream Token | cost | 440 | tools/gen_ruleset.py `Buildings` |
| Dream Token | `Costs [40] [White Lychee Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Dream Token | `[+20]% Strength <vs [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Dream Token | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | `[4] units cost no maintenance` | 4 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | `[+30]% Production when constructing [Immortal Gu] wonders [in all cities]` | +30 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Steal Life | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Steal Life | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Steal Life | `Heals [25] damage if it kills a unit <for [post-[Rank Five era]] units>` | 25 | tools/gen_ruleset.py `Buildings` |
| Steal Life | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | `Instantly provides [3] [Human Qi] <upon turn start>` | 3 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Primordial Origin Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Primordial Origin Inheritance | `Instantly provides [2] [Human Qi] <upon turn start>` | 2 | tools/gen_ruleset.py `Buildings` |
| Primordial Origin Inheritance | `[+15]% Strength <for units with [Qi Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Primordial Origin Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Primordial Origin Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Star Constellation Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Star Constellation Inheritance | `[+20]% [Science] [in all cities]` | +20 | tools/gen_ruleset.py `Buildings` |
| Star Constellation Inheritance | `[+15]% Strength <for units with [Wisdom Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Star Constellation Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Star Constellation Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Limitless Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Limitless Inheritance | `[-25]% maintenance cost for [All] buildings [in all cities]` | -25 | tools/gen_ruleset.py `Buildings` |
| Limitless Inheritance | `[+15]% Strength <for units with [Rule Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Limitless Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Limitless Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Reckless Savage Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Reckless Savage Inheritance | `[+25]% Strength <for units with [Strength Master]>` | +25 | tools/gen_ruleset.py `Buildings` |
| Reckless Savage Inheritance | `[+10]% Strength <for units with [Transformation Master]>` | +10 | tools/gen_ruleset.py `Buildings` |
| Reckless Savage Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Reckless Savage Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Red Lotus Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Red Lotus Inheritance | `Instantly provides [1] [Lifespan Gu] <upon turn start> <every [5] turns>` | 1, 5 | tools/gen_ruleset.py `Buildings` |
| Red Lotus Inheritance | `[+15]% Strength <for units with [Time Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Red Lotus Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Red Lotus Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Genesis Lotus Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Genesis Lotus Inheritance | `Instantly provides [2] [Green Grape Immortal Essence] <upon turn start>` | 2 | tools/gen_ruleset.py `Buildings` |
| Genesis Lotus Inheritance | `[+15]% Strength <for units with [Wood Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Genesis Lotus Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Genesis Lotus Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Thieving Heaven Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Thieving Heaven Inheritance | `Earn [50]% of killed [Military] unit's [Cost] as [Gold]` | 50 | tools/gen_ruleset.py `Buildings` |
| Thieving Heaven Inheritance | `[+15]% Strength <for units with [Theft Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Thieving Heaven Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Thieving Heaven Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Giant Sun Luck Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Giant Sun Luck Inheritance | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Buildings` |
| Giant Sun Luck Inheritance | `[+15]% Strength <for units with [Luck Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Giant Sun Luck Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Giant Sun Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Spectral Soul Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Spectral Soul Inheritance | `[+25]% XP gained from combat` | +25 | tools/gen_ruleset.py `Buildings` |
| Spectral Soul Inheritance | `[+15]% Strength <for units with [Soul Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Spectral Soul Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Spectral Soul Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Paradise Earth Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Paradise Earth Inheritance | `Instantly provides [2] [Earth Qi] <upon turn start>` | 2 | tools/gen_ruleset.py `Buildings` |
| Paradise Earth Inheritance | `[+15]% Strength <for units with [Earth Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Paradise Earth Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Paradise Earth Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Three Kings Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Three Kings Inheritance | `[3] units cost no maintenance` | 3 | tools/gen_ruleset.py `Buildings` |
| Three Kings Inheritance | `[+15]% Strength <for units with [Enslavement Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Three Kings Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Three Kings Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Long Hair Ancestor Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Long Hair Ancestor Inheritance | `[+25]% Production when constructing [Immortal Gu] wonders [in all cities]` | +25 | tools/gen_ruleset.py `Buildings` |
| Long Hair Ancestor Inheritance | `[+15]% Strength <for units with [Refinement Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Long Hair Ancestor Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Long Hair Ancestor Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Hu Immortal Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Hu Immortal Inheritance | `[+2 Happiness]` | +2 | tools/gen_ruleset.py `Buildings` |
| Hu Immortal Inheritance | `Instantly provides [1] [Heaven Qi] <upon turn start>` | 1 | tools/gen_ruleset.py `Buildings` |
| Hu Immortal Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Hu Immortal Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Blood Sea Inheritance | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Blood Sea Inheritance | `[+25]% Strength <for units with [Blood Master]>` | +25 | tools/gen_ruleset.py `Buildings` |
| Blood Sea Inheritance | `Earn [25]% of killed [Military] unit's [Cost] as [Human Qi]` | 25 | tools/gen_ruleset.py `Buildings` |
| Blood Sea Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Blood Sea Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |

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
| Column 7 (Purple Crystal Essence) | techCost | 480 | data/tech_columns.csv `techCost` |
| Column 7 (Purple Crystal Essence) | buildingCost | 240 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 7 (Purple Crystal Essence) | wonderCost | 400 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 8 (Three Qi) | techCost | 620 | data/tech_columns.csv `techCost` |
| Column 8 (Three Qi) | buildingCost | 280 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 8 (Three Qi) | wonderCost | 450 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 9 (Calamity Lore, Immortal Gu Recipes) | techCost | 800 | data/tech_columns.csv `techCost` |
| Column 9 (Calamity Lore, Immortal Gu Recipes) | buildingCost | 320 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 9 (Calamity Lore, Immortal Gu Recipes) | wonderCost | 500 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 10 (Red Date Essence, Rank Seven Immortal Gu Recipes) | techCost | 1100 | data/tech_columns.csv `techCost` |
| Column 10 (Red Date Essence, Rank Seven Immortal Gu Recipes) | buildingCost | 400 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 10 (Red Date Essence, Rank Seven Immortal Gu Recipes) | wonderCost | 600 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 11 (Grotto-Heaven, Rank Eight Immortal Gu Recipes) | techCost | 1300 | data/tech_columns.csv `techCost` |
| Column 11 (Grotto-Heaven, Rank Eight Immortal Gu Recipes) | buildingCost | 440 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 11 (Grotto-Heaven, Rank Eight Immortal Gu Recipes) | wonderCost | 650 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 12 (Dao Comprehension) | techCost | 1500 | data/tech_columns.csv `techCost` |
| Column 12 (Dao Comprehension) | buildingCost | 480 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 12 (Dao Comprehension) | wonderCost | 700 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |

### Policies.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Righteous Path | priorities.Southern Border Supremacy | 2 | tools/gen_ruleset.py `Policies` |
| Righteous Path | priorities.Endurance | 6 | tools/gen_ruleset.py `Policies` |
| Righteous Path | `Resting point for Influence with City-States is increased by [15]` | 15 | tools/gen_ruleset.py `Policies` |
| Righteous Path | `[-25]% maintenance costs <in [Friendly Land] tiles>` | -25 | tools/gen_ruleset.py `Policies` |
| Righteous Path | `[+10]% Strength <vs [Demonic Infamy] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Clan Rules | `[-15]% Unhappiness from [Population] [in all cities]` | -15 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Righteous Alliance | `Gifts of Gold to City-States generate [+25]% more Influence` | +25 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Guardian Formations | `[+10]% Strength for cities` | +10 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Guardian Formations | `[+10]% Strength <when defending>` | +10 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Righteous Path Complete | `[-10]% maintenance costs` | -10 | tools/gen_ruleset.py `Policies` |
| Righteous Path › Righteous Path Complete | `Earn [100]% of killed [Demonic Infamy] unit's [Cost] as [Gold]` | 100 | tools/gen_ruleset.py `Policies` |
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
| Moon Path | `[+5]% Strength <for [Moon Master] units> <for every [Adopted [[Moon Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moonlight Mastery | `[+15]% Strength <for units with [Moonlight Gu]>` | +15 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moonlight Mastery | `[+15]% Strength <for units with [Moon Raiment]>` | +15 | tools/gen_ruleset.py `Policies` |
| Moon Path › Orchid Beds | `Provides [2] [Moon Orchid]` | 2 | tools/gen_ruleset.py `Policies` |
| Moon Path › Orchid Beds | `[-15]% maintenance costs <for [Moon Master] units>` | -15 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moon Blade Step | `[1] Movement <for [Moon Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Moon Path › Moon Path Complete | `New [Gu Master] units start with [10] XP [in all cities]` | 10 | tools/gen_ruleset.py `Policies` |
| Strength Path | priorities.Southern Border Supremacy | 5 | tools/gen_ruleset.py `Policies` |
| Strength Path | priorities.Endurance | 5 | tools/gen_ruleset.py `Policies` |
| Strength Path | `Provides [2] [Wild Boar]` | 2 | tools/gen_ruleset.py `Policies` |
| Strength Path | `[+5]% Strength <for [Strength Master] units> <for every [Adopted [[Strength Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Strength Path › Boar Strength | `[+15]% Strength <for units with [White Boar Gu]>` | +15 | tools/gen_ruleset.py `Policies` |
| Strength Path › Boar Strength | `[+15]% Strength <for units with [White Jade Gu]>` | +15 | tools/gen_ruleset.py `Policies` |
| Strength Path › Beast Hunters | `Provides [2] [Wild Boar]` | 2 | tools/gen_ruleset.py `Policies` |
| Strength Path › Beast Hunters | `[+25]% Strength <vs [Barbarians] units>` | +25 | tools/gen_ruleset.py `Policies` |
| Strength Path › Unyielding Body | `Heals [10] damage if it kills a unit` | 10 | tools/gen_ruleset.py `Policies` |
| Strength Path › Strength Path Complete | `[1] Movement <for [Strength Master] units>` | 1 | tools/gen_ruleset.py `Policies` |

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
| Unfinished Refinement | `Unavailable <for units with [Killer Move]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Moon Master]> <for units with [Moon Raiment]> <before discovering [Killer Moves]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Jade Gu]> <before discovering [Killer Moves]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Moon Master]> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when below [1] [Moon Orchid]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Moon Master]> <for units with [Moonlight Gu]> <for units without [Jade Skin Gu]> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units without [White Boar Gu]> <for units without [White Jade Gu]> <when below [1] [Wild Boar]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Boar Gu]> <for units with [Jade Skin Gu]> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Boar Gu]> <for units without [Jade Skin Gu]> <when below [2] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Moon Master]> <for units with [Moonlight Gu]> <for [Rank One Gu Master] units> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units with [Strength Master]> <for units without [Moon Master]> <for units with [White Boar Gu]> <for [Rank One Gu Master] units> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units without [Moon Master]> <for units without [Strength Master]> <for units with [Jade Skin Gu]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
| Unfinished Refinement | `Unavailable <for units without [Moon Master]> <for units without [Strength Master]> <when below [1] [Jade]> <when below [31] [Gold]>` | 31 | tools/gen_ruleset.py `Ruins` |
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
| Gu Yue Temperament | declareWar | 3 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | diplomacy | 7 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | commerce | 7 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | loyal | 6 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | priorities.Moon Path | 10 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | priorities.Righteous Path | 6 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | `[+50]% weight to [Gu Academy] for AI decisions` | +50 | tools/gen_ruleset.py `Nations` |
| Gu Yue Temperament | `[+100]% weight to [Awakening Grounds] for AI decisions` | +100 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | gold | 7 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | production | 6 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | science | 6 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | military | 6 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | aggressive | 8 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | declareWar | 9 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | expansion | 7 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | diplomacy | 3 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | loyal | 3 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | priorities.Righteous Path | 8 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | `[+50]% weight to [Gu Academy] for AI decisions` | +50 | tools/gen_ruleset.py `Nations` |
| Bai Temperament | `[+100]% weight to [Awakening Grounds] for AI decisions` | +100 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | military | 7 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | aggressive | 6 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | production | 6 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | declareWar | 5 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | loyal | 2 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | diplomacy | 6 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | priorities.Strength Path | 10 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | priorities.Righteous Path | 3 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | `[+50]% weight to [Gu Academy] for AI decisions` | +50 | tools/gen_ruleset.py `Nations` |
| Xiong Temperament | `[+100]% weight to [Awakening Grounds] for AI decisions` | +100 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | military | 7 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | aggressive | 4 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | production | 6 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | loyal | 7 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | expansion | 5 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | declareWar | 6 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | diplomacy | 7 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | priorities.Righteous Path | 10 | tools/gen_ruleset.py `Nations` |
| Wu Temperament | priorities.Strength Path | 4 | tools/gen_ruleset.py `Nations` |
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
| Rank Five era | researchAgreementCost | 450 | tools/gen_ruleset.py `Eras` |
| Rank Five era | baseUnitBuyCost | 500 | tools/gen_ruleset.py `Eras` |
| Rank Six era | researchAgreementCost | 550 | tools/gen_ruleset.py `Eras` |
| Rank Six era | baseUnitBuyCost | 600 | tools/gen_ruleset.py `Eras` |
| Rank Seven era | researchAgreementCost | 650 | tools/gen_ruleset.py `Eras` |
| Rank Seven era | baseUnitBuyCost | 700 | tools/gen_ruleset.py `Eras` |
| Rank Eight era | researchAgreementCost | 750 | tools/gen_ruleset.py `Eras` |
| Rank Eight era | baseUnitBuyCost | 800 | tools/gen_ruleset.py `Eras` |

### UnitTypes.json

No tunable numbers.

### Paths (tools/gen_paths.py)

Every path promotion and path Gu is built from these knobs; the hidden conflict lines follow data/path_conflicts.csv (an exact pair wins, then the milder of the two paths' `x,*` rows, then `*,*`).

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| every Master | `[+10]% Strength` | +10 | tools/gen_paths.py `TIER_STRENGTH` |
| every Grandmaster | `[+15]% Strength` | +15 | tools/gen_paths.py `TIER_STRENGTH` |
| every Great Grandmaster | `[+20]% Strength` | +20 | tools/gen_paths.py `TIER_STRENGTH` |
| every Supreme Grandmaster | `[+25]% Strength` | +25 | tools/gen_paths.py `TIER_STRENGTH` |
| every move | `<costs [+15 Gold] stats> <requires [1] movement>` | +15, 1 | tools/gen_paths.py `MOVE_COST` |
| every tier | `[+400]% weight to this choice for AI decisions` | +400 | tools/gen_paths.py `TIER_WEIGHT` |
| signature Masters | AI weight for the clan's signature path | +23133 (share 0.85) | tools/gen_paths.py `SIGNATURE_SHARE` |
| conflict * / * | Strength of a unit holding both | -10 | data/path_conflicts.csv |
| conflict earth / water | Strength of a unit holding both | -25 | data/path_conflicts.csv |
| conflict earth / fire | Strength of a unit holding both | -25 | data/path_conflicts.csv |
| conflict strength / water | Strength of a unit holding both | -25 | data/path_conflicts.csv |
| conflict metal / strength | Strength of a unit holding both | -25 | data/path_conflicts.csv |
| conflict dark / light | Strength of a unit holding both | -25 | data/path_conflicts.csv |
| conflict sound / * | Strength of a unit holding both | -5 | data/path_conflicts.csv |
| conflict human / * | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict enslavement / soul | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict soul / wisdom | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict enslavement / wisdom | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict restriction / rule | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict phantom / rule | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict emotion / wisdom | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict emotion / enchantment | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict enchantment / wisdom | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict dark / shadow | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict light / shadow | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| conflict lightning / sound | Strength of a unit holding both | 0 | data/path_conflicts.csv |
| family A (Body & Beast) move | `[+25]% Strength` | +25 | data/path_families.csv `mortal_uniques` |
| family A (Body & Beast) move | `[+50]% Strength` | +50 | data/path_families.csv `immortal_uniques` |
| family A (Body & Beast) move | `[This Unit] heals [30] HP <upon gaining the [{n}] status>` | 30 | data/path_families.csv `immortal_uniques` |
| family B (Edge & War) move | `[+40]% Strength <when attacking>` | +40 | data/path_families.csv `mortal_uniques` |
| family B (Edge & War) move | `[+80]% Strength <when attacking>` | +80 | data/path_families.csv `immortal_uniques` |
| family C (Five Phases & Weather) move | `[+20]% Strength` | +20 | data/path_families.csv `mortal_uniques` |
| family C (Five Phases & Weather) move | `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` | 10 | data/path_families.csv `mortal_uniques` |
| family C (Five Phases & Weather) move | `[+40]% Strength` | +40 | data/path_families.csv `immortal_uniques` |
| family C (Five Phases & Weather) move | `[Target Unit] takes [25] damage <upon damaging a [Military] unit>` | 25 | data/path_families.csv `immortal_uniques` |
| family D (Sky & Shade) move | `[+20]% Strength <when attacking>` | +20 | data/path_families.csv `mortal_uniques` |
| family D (Sky & Shade) move | `[This Unit] gains [2] movement <upon gaining the [{n}] status>` | 2 | data/path_families.csv `mortal_uniques` |
| family D (Sky & Shade) move | `[+40]% Strength <when attacking>` | +40 | data/path_families.csv `immortal_uniques` |
| family D (Sky & Shade) move | `[This Unit] gains [3] movement <upon gaining the [{n}] status>` | 3 | data/path_families.csv `immortal_uniques` |
| family E (Mind & Spirit) move | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` | 2 | data/path_families.csv `mortal_uniques` |
| family E (Mind & Spirit) move | `[+30]% Strength` | +30 | data/path_families.csv `immortal_uniques` |
| family E (Mind & Spirit) move | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` | 2 | data/path_families.csv `immortal_uniques` |
| family F (Law & Cosmos) move | `[1] additional attacks per turn` | 1 | data/path_families.csv `mortal_uniques` |
| family F (Law & Cosmos) move | `[1] additional attacks per turn` | 1 | data/path_families.csv `immortal_uniques` |
| family F (Law & Cosmos) move | `[+40]% Strength` | +40 | data/path_families.csv `immortal_uniques` |
| family G (Craft & Society) move | `[+15]% Strength` | +15 | data/path_families.csv `mortal_uniques` |
| family G (Craft & Society) move | `[This Unit] heals [40] HP <upon gaining the [{n}] status>` | 40 | data/path_families.csv `mortal_uniques` |
| family G (Craft & Society) move | `[+30]% Strength` | +30 | data/path_families.csv `immortal_uniques` |
| family G (Craft & Society) move | `[This Unit] heals [80] HP <upon gaining the [{n}] status>` | 80 | data/path_families.csv `immortal_uniques` |
| Bone Master | `[+20]% Strength <when defending>` | +20 | data/paths.csv `signature` |
| Blood Master | `Heals [20] damage if it kills a unit` | 20 | data/paths.csv `signature` |
| Sword Master | `[+25]% Strength <when attacking>` | +25 | data/paths.csv `signature` |
| Blade Master | `[+50]% to Flank Attack bonuses` | +50 | data/paths.csv `signature` |
| Metal Master | `[+30]% Strength <vs cities>` | +30 | data/paths.csv `signature` |
| Weapon Master | `[+20]% Strength <when adjacent to a [Military] unit>` | +20 | data/paths.csv `signature` |
| Killing Master | `[This Unit] gains [1] movement <upon defeating a [Military] unit>` | 1 | data/paths.csv `signature` |
| Wood Master | `[15] HP when healing` | 15 | data/paths.csv `signature` |
| Earth Master | `[+25]% Strength <when fighting in [Hill] tiles>` | +25 | data/paths.csv `signature` |
| Wind Master | `[1] Movement` | 1 | data/paths.csv `signature` |
| Ice Snow Master | `[Target Unit] loses [1] movement <upon damaging a [Military] unit>` | 1 | data/paths.csv `signature` |
| Lightning Master | `[+30]% Strength <when above [1] movement>` | +30, 1 | data/paths.csv `signature` |
| Poison Master | `[Target Unit] gains the [Poisoned] status for [3] turn(s) <upon damaging a [Military] unit>` | 3 | data/paths.csv `signature` |
| Shadow Master | `[+30]% Strength <vs [Wounded] units>` | +30 | data/paths.csv `signature` |
| Star Master | `[2] Sight` | 2 | data/paths.csv `signature` |
| Moon Master | `Before engaging in combat performs an extra ranged attack with [40]% of melee combat strength` | 40 | data/paths.csv `signature` |
| Sound Master | `[-10]% Strength for enemy [Military] units in adjacent [All] tiles` | -10 | data/paths.csv `signature` |
| Emotion Master | `[+25]% Strength <when below [50] HP>` | +25, 50 | data/paths.csv `signature` |
| Enchantment Master | `[Target Unit] gains the [Charmed] status for [1] turn(s) <upon damaging a [Military] unit>` | 1 | data/paths.csv `signature` |
| Soul Master | `[This Unit] gains [10] XP <upon defeating a [Military] unit>` | 10 | data/paths.csv `signature` |
| Dream Master | `[+50]% XP gained from combat` | +50 | data/paths.csv `signature` |
| Time Master | `[1] additional attacks per turn` | 1 | data/paths.csv `signature` |
| Phantom Master | `[This Unit] gains the [Phantom Veil] status for [1] turn(s) <upon losing at least [30] HP in a single attack>` | 1, 30 | data/paths.csv `signature` |
| Restriction Master | `[Target Unit] gains the [Sealed] status for [2] turn(s) <upon damaging a [Military] unit>` | 2 | data/paths.csv `signature` |
| Luck Master | `[+30]% Strength <with [50]% chance>` | +30, 50 | data/paths.csv `signature` |
| Heaven Master | `[+25]% Strength <when fighting units from a Civilization with more Cities than you>` | +25 | data/paths.csv `signature` |
| Qi Master | `[+3] Strength` | +3 | data/paths.csv `signature` |
| Refinement Master | `[-30]% Gold cost of upgrading` | -30 | data/paths.csv `signature` |
| Formation Master | `[+15]% Strength bonus for [Military] units within [1] tiles` | +15, 1 | data/paths.csv `signature` |
| Food Master | `[-25]% maintenance costs` | -25 | data/paths.csv `signature` |
| Human Master | `All adjacent units heal [10] HP when healing` | 10 | data/paths.csv `signature` |
| Painting Master | `[+20]% Strength <when fighting in [Friendly Land] tiles>` | +20 | data/paths.csv `signature` |
| Theft Master | `Earn [50]% of killed [Military] unit's [Cost] as [Gold]` | 50 | data/paths.csv `signature` |
| Roaming Zombie Gu | `[+15]% Strength <when defending>` | +15 | data/path_gu.csv `effects` |
| Roaming Zombie Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Bone Spear Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Bone Spear Gu | eats Wild Boar | 1 | data/path_gu.csv `eats` (hunger: data/hunger.csv) |
| Blood Skull Gu | `[+25]% XP gained from combat` | +25 | data/path_gu.csv `effects` |
| Blood Skull Gu | eats Wild Boar | 1 | data/path_gu.csv `eats` (hunger: data/hunger.csv) |
| Sword Shadow Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Sword Shadow Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Sole Blade Gu | `[+25]% Strength <when attacking> <with [50]% chance>` | +25, 50 | data/path_gu.csv `effects` |
| Sole Blade Gu | eats Jade | 1 | data/path_gu.csv `eats` (hunger: data/hunger.csv) |
| Bronze Skin Gu | `[+15]% Strength <when defending>` | +15 | data/path_gu.csv `effects` |
| Bronze Skin Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Armoury Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Armoury Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Killing Intent Gu | `[+20]% Strength <vs [Wounded] units>` | +20 | data/path_gu.csv `effects` |
| Killing Intent Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Fiery Claw Gu | `[Target Unit] takes [5] damage <upon damaging a [Military] unit>` | 5 | data/path_gu.csv `effects` |
| Fiery Claw Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Water Shield Gu | `[+15]% Strength <when defending>` | +15 | data/path_gu.csv `effects` |
| Water Shield Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Heavenly Essence Treasure Lotus | `[-20]% maintenance costs` | -20 | data/path_gu.csv `effects` |
| Gruel Mud Gu | `[+15]% Strength <when fighting in [Hill] tiles>` | +15 | data/path_gu.csv `effects` |
| Gruel Mud Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Whirlwind Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Whirlwind Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Flying Cloud Gu | `[1] Movement` | 1 | data/path_gu.csv `effects` |
| Flying Cloud Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Frost Demon Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Frost Demon Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Thunderclap Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Thunderclap Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Poison Scorpion Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Poison Scorpion Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Little Light Gu | `[1] Sight` | 1 | data/path_gu.csv `effects` |
| Little Light Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Shadow Follower Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Shadow Follower Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Overlapping Shadow Gu | `[+20]% Strength <when attacking>` | +20 | data/path_gu.csv `effects` |
| Overlapping Shadow Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Star Dart Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Star Dart Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Heaven Earth Magnificent Sound Gu | `[+20]% Strength <when attacking>` | +20 | data/path_gu.csv `effects` |
| Heaven Earth Magnificent Sound Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Illusory Moon Gu | `[+15]% Strength <when defending>` | +15 | data/path_gu.csv `effects` |
| Illusory Moon Gu | eats Moon Orchid | 1 | data/path_gu.csv `eats` (hunger: data/hunger.csv) |
| Clear Mind Gu | `[+20]% XP gained from combat` | +20 | data/path_gu.csv `effects` |
| Clear Mind Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Emotion Poetry Gu | `[+15]% Strength <when below [50] HP>` | +15, 50 | data/path_gu.csv `effects` |
| Emotion Poetry Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Estrus Gu | `[+15]% Strength <vs [Barbarians] units>` | +15 | data/path_gu.csv `effects` |
| Estrus Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Soul Search Gu | `[+25]% XP gained from combat` | +25 | data/path_gu.csv `effects` |
| Soul Search Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Dream Pillow Gu | `[10] HP when healing` | 10 | data/path_gu.csv `effects` |
| Dream Pillow Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Wolf Enslavement Gu | `[+15]% Strength <vs [Barbarians] units>` | +15 | data/path_gu.csv `effects` |
| Wolf Enslavement Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Man as Before Gu | `[20] HP when healing` | 20 | data/path_gu.csv `effects` |
| Man as Before Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Warp Gu | `[1] Movement` | 1 | data/path_gu.csv `effects` |
| Warp Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Amplify Effect Gu | `[+10]% Strength` | +10 | data/path_gu.csv `effects` |
| Amplify Effect Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Turn Phantom Gu | `[+15]% Strength <when defending>` | +15 | data/path_gu.csv `effects` |
| Turn Phantom Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Primeval Break Gu | `[+15]% Strength <when attacking>` | +15 | data/path_gu.csv `effects` |
| Primeval Break Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Luck Inspection Gu | `[1] Sight` | 1 | data/path_gu.csv `effects` |
| Luck Inspection Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Ten-Year Lifespan Gu | `[10] HP when healing` | 10 | data/path_gu.csv `effects` |
| Ten-Year Lifespan Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Strength Qi Gu | `[+15]% Strength` | +15 | data/path_gu.csv `effects` |
| Strength Qi Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Revert Gu | `[+10]% Strength` | +10 | data/path_gu.csv `effects` |
| Revert Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Formation Heart Gu | `[+10]% Strength bonus for [Military] units within [1] tiles` | +10, 1 | data/path_gu.csv `effects` |
| Formation Heart Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Four Flavours Liquor Worm | `[+50]% XP gained from combat` | +50 | data/path_gu.csv `effects` |
| Four Flavours Liquor Worm | eats Wine | 1 | data/path_gu.csv `eats` (hunger: data/hunger.csv) |
| Pill Refiner Gu | `[10] HP when healing` | 10 | data/path_gu.csv `effects` |
| Pill Refiner Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Flying Sword Letter Gu | `[1] Sight` | 1 | data/path_gu.csv `effects` |
| Flying Sword Letter Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Relic Gu | `[+25]% XP gained from combat` | +25 | data/path_gu.csv `effects` |
| Relic Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Painting Idea Gu | `[+15]% Strength <when fighting in [Friendly Land] tiles>` | +15 | data/path_gu.csv `effects` |
| Painting Idea Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Plunder Gu | `Earn [25]% of killed [Military] unit's [Cost] as [Gold]` | 25 | data/path_gu.csv `effects` |
| Plunder Gu | `[+10]% maintenance costs` | +10 | data/path_gu.csv `upkeep` |
| Poisoned | `[This Unit] takes [10] damage <upon turn start>` | 10 | data/path_statuses.csv `uniques` |
| Charmed | `[-25]% Strength <when attacking>` | -25 | data/path_statuses.csv `uniques` |
| Phantom Veil | `[+50]% Strength <when defending>` | +50 | data/path_statuses.csv `uniques` |
| Shaken | `[-20]% Strength` | -20 | data/path_statuses.csv `uniques` |

### Terrains.json, Speeds.json

Vanilla copies (tools/gen_ruleset.py `Terrains (Vanilla minus natural wonders and Fallout)` and the Speeds line in `Nations (Difficulties)`); the only change is that no terrain grants an extra Spirit Spring. Tune them there if a playtest asks for it; until then the Vanilla numbers stand.

1400 numbers listed.

<!-- inventory:end -->
