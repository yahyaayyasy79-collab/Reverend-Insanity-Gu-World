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

## Path power scaling (Phase D, 2026-11-02)

Knobs: `tools/path_powers.py` SCALE (a hit's amount with no dao marks and at tiers I-V, per kind), `data/path_powers.csv`
(each path's hit kind, multiplier and its four tiers' uniques), the twelve statuses in `data/path_statuses.csv`, and
TIER_STRENGTH in `tools/gen_paths.py`. Evidence (Five Regions, 6 × 350): hits on both attack and defence made sieges
fail (captured cities 16 → 9, clans destroyed 7 → 1); attack-only hits gave 27 and 9. If wars feel too bloody, lower
the dmg and dur rows first.

## Immortal lifespan and the Eternal Life cost (Phase D, 2026-11-02)

Knobs: `tools/lifespan.py` GRANT (Lifespan Gu on reaching ranks 6/7/8/9: 20/25/35/60), BURN (one each 10/15/20/30
turns on Standard), WILD_CHANCE; ETERNAL_COST in `tools/gen_ruleset.py` (300). Evidence (Five Regions, 6 × 400–450):
immortals per clan at T350 2.2 → 3.6, rank eight reached by 10 clans (was 2), a Venerable in 6 of 6 games (was 0);
Eternal Life at 150 won 4 of 6 games 30–35 turns after the Venerable, at 300 5 of 6 games 59–66 turns after
(T391–T443). Lifespan stocks reach about 100 by T350: if immortals should feel mortal again, cut WILD_CHANCE first.

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

## Tension targets: MOD_SPEC_2 Phase D and MOD_SPEC_3 (2026-11-03)

How each target was measured: autoplay (`docs/AUTOPLAY.md`, "Phase D: tension targets"; Five Regions, Prince), the
ruleset's own numbers, or duels worked with Unciv's damage formula [src BattleDamage.damageModifier] at an average
roll. Duel loadouts: a rank-5 Gu Master with Master, Grandmaster, Dao Marks II and an attack Gu of its rank; an
immortal with Master to Great Grandmaster, Dao Marks III and its essence.

| Target (source) | Measured | Status |
|---|---|---|
| First tribulation 10-15 turns after ascension (MOD_SPEC_2) | First earthly calamity 13 turns after (lower land) to 10 (super): `CALAMITY_TURNS` 14-11, E7; first heavenly tribulation after 59 at rank six | Met |
| Unprepared: lose 30%+ of the land's output or a key building; prepared: under 10% (MOD_SPEC_2) | Calamity endured: 50% the land lies ravaged 8 turns of a ~13-turn cycle (31% of its output), 30% the immortal loses 40 HP, 20% nothing. Prepared: ward 10 HP, diversion nothing, vault 40 stones. Tribulation faced bare: 25% death, 45% ravaged 10 turns and 50 HP; with ward and essence, no loss | Met |
| Rank-6 essence pays about one killer move per immortal per 5 turns (MOD_SPEC_2) | A lower blessed land makes 1 green grape a turn; the immortal move costs 5 (the AI keeps 10 in reserve) | Met |
| An immortal without Lifespan Gu dies within about 15 turns (MOD_SPEC_2) | 7 HP a turn and no healing: 14 turns | Met |
| At least one AI contests each immortal Gu race (MOD_SPEC_2) | 66 immortal Gu (the user raised the cap of 30); the AI builds 1-3 by T300 and 5-20 by T450 (mean 14), so most races stay open, not contested | Not met, by the user's scope |
| The AI stays solvent and reaches rank 7 in 1 of 3 games (MOD_SPEC_2) | Rank 7 in 8 of 8 games (T247-291), rank 8 in 8 (T320-377), a Venerable in 8 (T340-406). Before the late-game relief a third of AI clan-turns after T300 ran in debt and every game touched the -200 disband line; with it, 10% in debt, 2.8 snapshots a game at the disband line (was 19.6), stones per turn after T300 -8 (was -21) | Met |
| No event choice strictly dominates another (MOD_SPEC_2, MOD_SPEC §10) | A scan of 128 choices in 38 events flags a free choice beside a costly one with the same gate: 5 flags, all explained (two are dice, not choices; three carry costs the scan cannot read: a betrayal risk, unhappiness, a strategic fork) | Met |
| A single-path unit beats an equal-rank three-path unit (MOD_SPEC_3) | Rank 3, three promotions each: Master and Grandmaster (strength 20.3) against three Masters with the default -10% conflicts (14.0): it deals 38 and takes 24 a fight | Met |
| A rank 6 survives four fresh rank-5 attacks (MOD_SPEC_3) | 81 of its 100 HP lost on average (97 at the highest rolls); 95 when the attackers use killer moves (+40%); 97 before the immortal chasm (P1) | Met, at the margin with killer moves |
| One immortal rank step is a strong edge, not an absolute one (MOD_SPEC_3) | Rank 7 against rank 6: kills in 2.7 hits, dies in 4.1; rank 8 against rank 7: 2.8 and 4.0 | Met |
| A Venerable takes any city alone and dies within its lifespan unless it pillages (MOD_SPEC_3) | Strength about 500 against cities (all four tiers of one path, Dao Marks IV, +50% against cities), a strong late city about 60 (base, population, techs, a garrison, walls): one hit. Its lifespan is Lifespan Gu since the user's change of 2026-11-02 | Met; the lifespan half superseded |
| AI units stay on their main path in 80% of path promotions (MOD_SPEC_3) | Each AI unit holds one root path (0.97-1.03 root Masters per Gu Master); 92% of path promotions are on that root path, the rest on its sub-paths. Signature clans after the halls fix: Gu Yue 85%, Bai 86%, Xiong 86%, Wu 73% (Bai 69% and Wu 57% before) | Met per unit; Wu's lean below the C3 decision's 85% |
| Early upkeep near 40% of stone income (MOD_SPEC §10) | 17% in T1-50 (round 8) | Not met: item 1 below |
| A careless player starves once, a careful one never (MOD_SPEC §10) | Needs a human game | Open |

Fixed in Phase D on the way (2026-11-03):

* **White Boar Gu starvation loop.** The Strength Master handed White Boar Gu back at every turn start without
  checking Wild Boar (`data/path_gu.csv` had no food on that row), so the Xiong clan ran short at once and lost about
  75 White Boar Gu a game to starvation. Since the vital Gu, each such death also wounded the Master. The grant now
  waits for a spare of two, like every other food-eating path Gu: 79 deaths per game by T300 fell to 0.2 (8 + 8 games).
* **Signature clans drifting off their path.** Halls hand their Master to every unit trained there; the four signature
  clans' AI now weighs other paths' halls at -90% (`tools/gen_paths.py` `OFF_PATH_HALL`).
* **Late-game AI debt.** Unit upkeep grows with the game's progress [src CivInfoStatsForNextTurn.getUnitMaintenance]
  and the engine's AI keeps its army: at T330-400 an AI clan paid 67 stones a turn for units and 40 for buildings and
  roads, against 83 of income. From turn 300 on Standard (per speed) an AI clan's units cost 30% less
  (`AI_LATE_UPKEEP`); a player's upkeep is unchanged, so this is a handicap for the AI, like a difficulty level's.
  8 + 8 games of 450 turns: clan-turns in debt after T300 32% -> 10%, snapshots at the disband line 19.6 -> 2.8 a
  game, soldiers at the end 89 -> 112, immortals 35 -> 41, majors alive 6.6 -> 6.8.

## Part 2 — inventory

## Path halls and the debt regression (2026-11-01)

After the 47 path branches and halls, 44 of 48 clans on the Five Regions map spent 20+ turns in the red. A/B on the
Slice 1 setup (four clans, Prince, 6 × 320): with halls at 2 stones upkeep, 12 of 24 clans 20+ turns in the red, 8 in
debt at the end, mean stones per turn −5.5; with no hall upkeep, 4 of 24, 2, +5.4. Halls now cost no upkeep. Unciv
disbands military units once the treasury is at −200 or below [src TurnManager.endTurn], so a broke clan also loses
its army.

## The Five Regions economy and wide clans' stability (2026-11-01)

The autoplay harness now records stones per turn and happiness by source (`goldBy`, `happyBy`). Five Regions, eight
majors, Prince, 6 × 280–400, against Qing Mao Mountain with the same eight majors:

* **Map riches.** The map had nothing beyond the start rings: one spirit spring per clan; stones per turn 3.0 at T80
  against 12.8 on Qing Mao. Scattering springs, jade, Gu foods, furs, inheritances and lairs at Qing Mao's density
  (`tools/make_map.py` RICHES): 6.1 at T80, 6.3 at T120 (was 1.7); 20+ turns in the red by T400 42 → 32 of 48.
* **Stability.** Base 15, −3 per village, −0.9 per person, and almost nothing to offset it (one luxury, Furs; the
  Pavilion and the Tavern at +1): at T280 happiness −5.5, 39 of 44 clans below zero, growth −75%, population stuck near
  18 however many villages. `[-33]% unhappiness from the number of cities` and the Tavern at +2: population 27 at T280,
  in the red at the end 14 → 8 clans (Five Regions T280); Qing Mao T300: 10 → 5, mean stones per turn −1.5 → +1.3.
* **What remains** is the engine's AI (KNOWN_ISSUES 19): it trains soldiers while stones per turn are positive (up to
  five per village outside war), and their upkeep rises with every rank they climb. Weighted upkeep at T280: rank-five
  Masters a third (3.5 per clan at 325%), captured lightning wolves (the Enslavement path; barbarians are many on a wide
  map) a sixth. Levers if a real game feels too poor: rank-five upkeep (`data/gu_masters.csv`), wolves' upkeep.

<!-- inventory:start (tools/gen_balance.py) -->

Generated from `jsons/` by `tools/gen_balance.py`; the self-tests fail when it is stale. Edit the source in the last column, regenerate (`tools/gen_ruleset.py && tools/gen_balance.py`), run `tools/check_all`.

### ModOptions.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| ModOptions | constants.maxXPfromBarbarians | 90 | tools/gen_ruleset.py `ModOptions / Globals` |
| ModOptions | constants.cityStrengthFromTechsFullMultiplier | 0.1 | tools/gen_ruleset.py `ModOptions / Globals` |
| ModOptions | constants.naturalWonderCountMultiplier | 0.3 | tools/gen_ruleset.py `ModOptions / Globals` |
| ModOptions | constants.naturalWonderCountAddedConstant | 1.0 | tools/gen_ruleset.py `ModOptions / Globals` |

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
| GlobalUniques | `[-33]% unhappiness from the number of cities` | -33 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-30]% maintenance costs <for [AI player] Civilizations> <after turn number [201]> <on [Quick] game speed>` | -30, 201 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-30]% maintenance costs <for [AI player] Civilizations> <after turn number [300]> <on [Standard] game speed>` | -30, 300 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-30]% maintenance costs <for [AI player] Civilizations> <after turn number [450]> <on [Epic] game speed>` | -30, 450 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-30]% maintenance costs <for [AI player] Civilizations> <after turn number [900]> <on [Marathon] game speed>` | -30, 900 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-30]% Gold cost of upgrading <for units with [Peak Stage]>` | -30 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[+50]% Gold cost of upgrading <for units without [Peak Stage]>` | +50 | tools/gen_ruleset.py `ModOptions / Globals` |
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
| GlobalUniques | `[-10]% Strength <if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed>` | -10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[-2 Happiness] <if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed>` | -2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [10] turns> <if [Venerable Ascension] is constructed by anybody> <for [Major] Civilizations>` | 1, 10 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[+20]% [Production] [in all cities] <if [Venerable Ascension] is constructed>` | +20 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `[+3 Happiness] <if [Venerable Ascension] is constructed>` | +3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Dream Realm] event <upon turn start> <starting from the [Rank Seven era]> <if [Shattered Fate] is not constructed by anybody> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Dream Realm] event <upon turn start> <starting from the [Rank Seven era]> <if [Shattered Fate] is not constructed by anybody> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Dream Realm] event <upon turn start> <starting from the [Rank Seven era]> <if [Shattered Fate] is not constructed by anybody> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Dream Realm] event <upon turn start> <starting from the [Rank Seven era]> <if [Shattered Fate] is not constructed by anybody> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Shadow Sect Envoy] event <upon turn start> <starting from the [Rank Six era]> <with [1]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Shadow Sect Envoy] event <upon turn start> <starting from the [Rank Six era]> <with [1]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Shadow Sect Envoy] event <upon turn start> <starting from the [Rank Six era]> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Shadow Sect Envoy] event <upon turn start> <starting from the [Rank Six era]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Venerable's Shadow] event <upon turn start> <if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed> <with [6]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 6 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Venerable's Shadow] event <upon turn start> <if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed> <with [4]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Venerable's Shadow] event <upon turn start> <if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed> <with [3]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Venerable's Shadow] event <upon turn start> <if [Venerable Ascension] is constructed by anybody> <if [Venerable Ascension] is not constructed> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Qi Tides] event <upon turn start> <if [Shattered Fate] is constructed by anybody> <with [4]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 4 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Qi Tides] event <upon turn start> <if [Shattered Fate] is constructed by anybody> <with [3]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Qi Tides] event <upon turn start> <if [Shattered Fate] is constructed by anybody> <with [2]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Qi Tides] event <upon turn start> <if [Shattered Fate] is constructed by anybody> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Demonic Raid] event <upon turn start> <after turn number [40]> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 40, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Demonic Raid] event <upon turn start> <after turn number [60]> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 60, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Demonic Raid] event <upon turn start> <after turn number [90]> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 90, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Demonic Raid] event <upon turn start> <after turn number [180]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 180, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Wandering Gu Master] event <upon turn start> <after turn number [20]> <with [3]% chance> <for [Major] Civilizations> <on [Quick] game speed>` | 20, 3 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Wandering Gu Master] event <upon turn start> <after turn number [30]> <with [2]% chance> <for [Major] Civilizations> <on [Standard] game speed>` | 30, 2 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Wandering Gu Master] event <upon turn start> <after turn number [45]> <with [1]% chance> <for [Major] Civilizations> <on [Epic] game speed>` | 45, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Wandering Gu Master] event <upon turn start> <after turn number [90]> <with [1]% chance> <for [Major] Civilizations> <on [Marathon] game speed>` | 90, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Refinement Conference] event <upon turn start> <every [87] turns> <for [Major] Civilizations> <on [Quick] game speed>` | 87 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Refinement Conference] event <upon turn start> <every [130] turns> <for [Major] Civilizations> <on [Standard] game speed>` | 130 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Refinement Conference] event <upon turn start> <every [195] turns> <for [Major] Civilizations> <on [Epic] game speed>` | 195 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `Triggers a [Refinement Conference] event <upon turn start> <every [390] turns> <for [Major] Civilizations> <on [Marathon] game speed>` | 390 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [27]> <every [1] turns> <with [1]% chance> <for [City-States] Civilizations> <on [Quick] game speed>` | 27, 1, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [40]> <every [1] turns> <with [1]% chance> <for [City-States] Civilizations> <on [Standard] game speed>` | 40, 1, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [60]> <every [2] turns> <with [1]% chance> <for [City-States] Civilizations> <on [Epic] game speed>` | 60, 2, 1 | tools/gen_ruleset.py `ModOptions / Globals` |
| GlobalUniques | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [120]> <every [3] turns> <with [1]% chance> <for [City-States] Civilizations> <on [Marathon] game speed>` | 120, 3, 1 | tools/gen_ruleset.py `ModOptions / Globals` |

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
| Rank One Gu Master | strength | 6 | data/gu_masters.csv `strength` |
| Rank One Gu Master | cost | 35 | data/gu_masters.csv `cost` |
| Rank One Gu Master | `[+50]% maintenance costs` | +50 | data/gu_masters.csv `maintenance` |
| Rank One Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank One Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank One Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank One Gu Master | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank One Gu Master | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank One Gu Master | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank One Gu Master | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Two Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Two Gu Master | strength | 10 | data/gu_masters.csv `strength` |
| Rank Two Gu Master | cost | 60 | data/gu_masters.csv `cost` |
| Rank Two Gu Master | `[+100]% maintenance costs` | +100 | data/gu_masters.csv `maintenance` |
| Rank Two Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Two Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Two Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Two Gu Master | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank Two Gu Master | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank Two Gu Master | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Two Gu Master | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Three Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Three Gu Master | strength | 14 | data/gu_masters.csv `strength` |
| Rank Three Gu Master | cost | 95 | data/gu_masters.csv `cost` |
| Rank Three Gu Master | `[+125]% maintenance costs` | +125 | data/gu_masters.csv `maintenance` |
| Rank Three Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Three Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Three Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Three Gu Master | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank Three Gu Master | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank Three Gu Master | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Three Gu Master | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Four Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Four Gu Master | strength | 21 | data/gu_masters.csv `strength` |
| Rank Four Gu Master | cost | 140 | data/gu_masters.csv `cost` |
| Rank Four Gu Master | `[+175]% maintenance costs` | +175 | data/gu_masters.csv `maintenance` |
| Rank Four Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Four Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Four Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Four Gu Master | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank Four Gu Master | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank Four Gu Master | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Four Gu Master | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Five Gu Master | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Five Gu Master | strength | 29 | data/gu_masters.csv `strength` |
| Rank Five Gu Master | cost | 190 | data/gu_masters.csv `cost` |
| Rank Five Gu Master | `[+225]% maintenance costs` | +225 | data/gu_masters.csv `maintenance` |
| Rank Five Gu Master | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Five Gu Master | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Five Gu Master | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Five Gu Master | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank Five Gu Master | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank Five Gu Master | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Five Gu Master | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | strength | 36 | data/gu_masters.csv `strength` |
| Rank Six Gu Immortal | cost | 260 | data/gu_masters.csv `cost` |
| Rank Six Gu Immortal | `[+300]% maintenance costs` | +300 | data/gu_masters.csv `maintenance` |
| Rank Six Gu Immortal | `[+15]% Strength <when above [9] [Green Grape Immortal Essence]>` | +15, 9 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Six Gu Immortal | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Six Gu Immortal | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Six Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [7] turns> <on [Quick] game speed>` | 1, 7 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [10] turns> <on [Standard] game speed>` | 1, 10 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [15] turns> <on [Epic] game speed>` | 1, 15 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [30] turns> <on [Marathon] game speed>` | 1, 30 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `Can only heal by pillaging <when below [1] [Lifespan Gu]>` | 1 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] takes [7] damage <upon turn start> <when below [1] [Lifespan Gu]>` | 7, 1 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] gains [3] XP <upon turn start>` | 3 | data/gu_masters.csv `cultivationXP` |
| Rank Six Gu Immortal | `[This Unit] gains [5] XP <upon turn start> <for [Rank Eight Gu Immortal] units>` | 5 | data/gu_masters.csv `cultivationXP` |
| Rank Six Gu Immortal | `[This Unit] takes [10] damage <upon ending a turn in a [Miasma Wall] tile>` | 10 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] takes [10] damage <upon ending a turn in a [Licorice Wall] tile>` | 10 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] takes [5] damage <upon ending a turn in a [Azure Water Wall] tile>` | 5 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] takes [10] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 10 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[This Unit] takes [10] damage <upon ending a turn in a [Sage Wall] tile>` | 10 | tools/gen_ruleset.py `gm()` |
| Rank Six Gu Immortal | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | strength | 51 | data/gu_masters.csv `strength` |
| Rank Seven Gu Immortal | cost | 330 | data/gu_masters.csv `cost` |
| Rank Seven Gu Immortal | `[+350]% maintenance costs` | +350 | data/gu_masters.csv `maintenance` |
| Rank Seven Gu Immortal | `[+15]% Strength <when above [9] [Red Date Immortal Essence]>` | +15, 9 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Seven Gu Immortal | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Seven Gu Immortal | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Seven Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [10] turns> <on [Quick] game speed>` | 1, 10 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [15] turns> <on [Standard] game speed>` | 1, 15 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [22] turns> <on [Epic] game speed>` | 1, 22 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [45] turns> <on [Marathon] game speed>` | 1, 45 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `Can only heal by pillaging <when below [1] [Lifespan Gu]>` | 1 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] takes [7] damage <upon turn start> <when below [1] [Lifespan Gu]>` | 7, 1 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] gains [3] XP <upon turn start>` | 3 | data/gu_masters.csv `cultivationXP` |
| Rank Seven Gu Immortal | `[This Unit] gains [5] XP <upon turn start> <for [Rank Eight Gu Immortal] units>` | 5 | data/gu_masters.csv `cultivationXP` |
| Rank Seven Gu Immortal | `[This Unit] takes [30] damage <upon ending a turn in a [Miasma Wall] tile>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] takes [30] damage <upon ending a turn in a [Licorice Wall] tile>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] takes [15] damage <upon ending a turn in a [Azure Water Wall] tile>` | 15 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] takes [30] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[This Unit] takes [30] damage <upon ending a turn in a [Sage Wall] tile>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Seven Gu Immortal | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | movement | 2 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | strength | 69 | data/gu_masters.csv `strength` |
| Rank Eight Gu Immortal | cost | 400 | data/gu_masters.csv `cost` |
| Rank Eight Gu Immortal | `[+400]% maintenance costs` | +400 | data/gu_masters.csv `maintenance` |
| Rank Eight Gu Immortal | `[+15]% Strength <when above [9] [White Lychee Immortal Essence]>` | +15, 9 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] gains [2] XP <upon turn start> <in cities with a [Gu Academy]> <for units without [Killer Move]>` | 2 | data/gu_masters.csv `cultivationXP` |
| Rank Eight Gu Immortal | `Triggers a [Wild Gu] event <upon turn start> <with [6]% chance>` | 6 | tools/gen_ruleset.py `WILD_GU_TRIGGER` |
| Rank Eight Gu Immortal | `Triggers a [Inheritance Rumour] event <upon turn start> <with [1]% chance> <in [Foreign Land] tiles> <in tiles without [resource]> <after discovering [Inheritance Lore]>` | 1 | tools/gen_ruleset.py `INHERITANCE_TRIGGER` |
| Rank Eight Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [13] turns> <on [Quick] game speed>` | 1, 13 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [20] turns> <on [Standard] game speed>` | 1, 20 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [30] turns> <on [Epic] game speed>` | 1, 30 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [60] turns> <on [Marathon] game speed>` | 1, 60 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `Can only heal by pillaging <when below [1] [Lifespan Gu]>` | 1 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] takes [7] damage <upon turn start> <when below [1] [Lifespan Gu]>` | 7, 1 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] gains [3] XP <upon turn start>` | 3 | data/gu_masters.csv `cultivationXP` |
| Rank Eight Gu Immortal | `[This Unit] gains [5] XP <upon turn start> <for [Rank Eight Gu Immortal] units>` | 5 | data/gu_masters.csv `cultivationXP` |
| Rank Eight Gu Immortal | `[This Unit] takes [60] damage <upon ending a turn in a [Miasma Wall] tile>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] takes [60] damage <upon ending a turn in a [Licorice Wall] tile>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] takes [30] damage <upon ending a turn in a [Azure Water Wall] tile>` | 30 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] takes [60] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[This Unit] takes [60] damage <upon ending a turn in a [Sage Wall] tile>` | 60 | tools/gen_ruleset.py `gm()` |
| Rank Eight Gu Immortal | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `gm()` |
| Lightning Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | strength | 9 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | cost | 30 | tools/gen_ruleset.py `Units` |
| Lightning Wolf | `[+50]% maintenance costs` | +50 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | strength | 16 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | cost | 60 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | `[+15]% Strength bonus for [Lightning Wolf] units within [2] tiles` | +15, 2 | tools/gen_ruleset.py `Units` |
| Bold Lightning Wolf | `[+100]% maintenance costs` | +100 | tools/gen_ruleset.py `Units` |
| Frenzy Lightning Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Frenzy Lightning Wolf | strength | 22 | tools/gen_ruleset.py `Units` |
| Frenzy Lightning Wolf | cost | 90 | tools/gen_ruleset.py `Units` |
| Frenzy Lightning Wolf | `[+15]% Strength bonus for [Beast] units within [2] tiles` | +15, 2 | tools/gen_ruleset.py `Units` |
| Frenzy Lightning Wolf | `[+150]% maintenance costs` | +150 | tools/gen_ruleset.py `Units` |
| Desolate Beast | movement | 3 | tools/gen_ruleset.py `Units` |
| Desolate Beast | strength | 62 | tools/gen_ruleset.py `Units` |
| Desolate Beast | cost | 200 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[+200]% maintenance costs` | +200 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[This Unit] takes [10] damage <upon ending a turn in a [Miasma Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[This Unit] takes [10] damage <upon ending a turn in a [Licorice Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[This Unit] takes [5] damage <upon ending a turn in a [Azure Water Wall] tile>` | 5 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[This Unit] takes [10] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Desolate Beast | `[This Unit] takes [10] damage <upon ending a turn in a [Sage Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | movement | 3 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | strength | 85 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | cost | 300 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[+250]% maintenance costs` | +250 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[This Unit] takes [30] damage <upon ending a turn in a [Miasma Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[This Unit] takes [30] damage <upon ending a turn in a [Licorice Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[This Unit] takes [15] damage <upon ending a turn in a [Azure Water Wall] tile>` | 15 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[This Unit] takes [30] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Ancient Desolate Beast | `[This Unit] takes [30] damage <upon ending a turn in a [Sage Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | movement | 3 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | strength | 115 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | cost | 500 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[+300]% maintenance costs` | +300 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[This Unit] takes [60] damage <upon ending a turn in a [Miasma Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[This Unit] takes [60] damage <upon ending a turn in a [Licorice Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[This Unit] takes [30] damage <upon ending a turn in a [Azure Water Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[This Unit] takes [60] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Immemorial Desolate Beast | `[This Unit] takes [60] damage <upon ending a turn in a [Sage Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Venerable | movement | 5 | tools/gen_ruleset.py `Units` |
| Venerable | strength | 168 | tools/gen_ruleset.py `Units` |
| Venerable | cost | 1000 | tools/gen_ruleset.py `Units` |
| Venerable | `Limited to [1] per Civilization` | 1 | tools/gen_ruleset.py `Units` |
| Venerable | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [20] turns> <on [Quick] game speed>` | 1, 20 | tools/gen_ruleset.py `Units` |
| Venerable | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [30] turns> <on [Standard] game speed>` | 1, 30 | tools/gen_ruleset.py `Units` |
| Venerable | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [45] turns> <on [Epic] game speed>` | 1, 45 | tools/gen_ruleset.py `Units` |
| Venerable | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [90] turns> <on [Marathon] game speed>` | 1, 90 | tools/gen_ruleset.py `Units` |
| Venerable | `Can only heal by pillaging <when below [1] [Lifespan Gu]>` | 1 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] takes [7] damage <upon turn start> <when below [1] [Lifespan Gu]>` | 7, 1 | tools/gen_ruleset.py `Units` |
| Venerable | `Instantly provides [6] [Yellow Apricot Immortal Essence] <upon turn start>` | 6 | tools/gen_ruleset.py `Units` |
| Venerable | `[+300]% maintenance costs` | +300 | tools/gen_ruleset.py `Units` |
| Venerable | `[2] additional attacks per turn` | 2 | tools/gen_ruleset.py `Units` |
| Venerable | `[-25]% Strength for enemy [Military] units in adjacent [All] tiles` | -25 | tools/gen_ruleset.py `Units` |
| Venerable | `[+50]% Strength <vs cities>` | +50 | tools/gen_ruleset.py `Units` |
| Venerable | `[+100]% Strength <vs [pre-[Rank Six era]] units>` | +100 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains [5] XP <upon turn start>` | 5 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Dao Comprehension] status for [13] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Quick] game speed>` | 13 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Dao Comprehension] status for [20] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Standard] game speed>` | 20 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Dao Comprehension] status for [30] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Epic] game speed>` | 30 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Dao Comprehension] status for [60] turn(s) <upon turn start> <for units without [Dao Comprehension]> <for [Path Master] units> <for [non-[Rank One-Two era]] units> <on [Marathon] game speed>` | 60 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Venerable Killer Move] status for [1] turn(s) <costs [20] [Yellow Apricot Immortal Essence]> <requires [1] movement>` | 1, 20, 1 | tools/gen_ruleset.py `Units` |
| Venerable | `Heals [10] damage if it kills a unit` | 10 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Chaos Countdown] status for [17] turn(s) <upon turn start> <for units without [Chaos Countdown]> <on [Quick] game speed>` | 17 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Chaos Countdown] status for [25] turn(s) <upon turn start> <for units without [Chaos Countdown]> <on [Standard] game speed>` | 25 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Chaos Countdown] status for [38] turn(s) <upon turn start> <for units without [Chaos Countdown]> <on [Epic] game speed>` | 38 | tools/gen_ruleset.py `Units` |
| Venerable | `[This Unit] gains the [Chaos Countdown] status for [75] turn(s) <upon turn start> <for units without [Chaos Countdown]> <on [Marathon] game speed>` | 75 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | movement | 2 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | strength | 140 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | cost | 650 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `Limited to [1] per Civilization` | 1 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[This Unit] takes [60] damage <upon ending a turn in a [Miasma Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[This Unit] takes [60] damage <upon ending a turn in a [Licorice Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[This Unit] takes [30] damage <upon ending a turn in a [Azure Water Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[This Unit] takes [60] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[This Unit] takes [60] damage <upon ending a turn in a [Sage Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `Costs [50] [White Lychee Immortal Essence]` | 50 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `Costs [60] [Immortal Materials]` | 60 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[+500]% maintenance costs` | +500 | tools/gen_ruleset.py `Units` |
| Calamity Luck Altar | `[+50]% Strength <when defending>` | +50 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | movement | 5 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | strength | 150 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | cost | 650 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `Limited to [1] per Civilization` | 1 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `[This Unit] takes [60] damage <upon ending a turn in a [Miasma Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `[This Unit] takes [60] damage <upon ending a turn in a [Licorice Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `[This Unit] takes [30] damage <upon ending a turn in a [Azure Water Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `[This Unit] takes [60] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `[This Unit] takes [60] damage <upon ending a turn in a [Sage Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `Costs [50] [White Lychee Immortal Essence]` | 50 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `Costs [60] [Immortal Materials]` | 60 | tools/gen_ruleset.py `Units` |
| Myriad Year Flying Warship | `[+500]% maintenance costs` | +500 | tools/gen_ruleset.py `Units` |
| Dragon Palace | movement | 3 | tools/gen_ruleset.py `Units` |
| Dragon Palace | strength | 160 | tools/gen_ruleset.py `Units` |
| Dragon Palace | cost | 650 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `Limited to [1] per Civilization` | 1 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[This Unit] takes [60] damage <upon ending a turn in a [Miasma Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[This Unit] takes [60] damage <upon ending a turn in a [Licorice Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[This Unit] takes [30] damage <upon ending a turn in a [Azure Water Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[This Unit] takes [60] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[This Unit] takes [60] damage <upon ending a turn in a [Sage Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `Costs [50] [White Lychee Immortal Essence]` | 50 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `Costs [60] [Immortal Materials]` | 60 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[+500]% maintenance costs` | +500 | tools/gen_ruleset.py `Units` |
| Dragon Palace | `[+20]% Strength <vs [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | movement | 2 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | strength | 190 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | cost | 650 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `Limited to [1] per Civilization` | 1 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[This Unit] takes [60] damage <upon ending a turn in a [Miasma Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[This Unit] takes [60] damage <upon ending a turn in a [Licorice Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[This Unit] takes [30] damage <upon ending a turn in a [Azure Water Wall] tile>` | 30 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[This Unit] takes [60] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[This Unit] takes [60] damage <upon ending a turn in a [Sage Wall] tile>` | 60 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `Costs [50] [White Lychee Immortal Essence]` | 50 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `Costs [60] [Immortal Materials]` | 60 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[+500]% maintenance costs` | +500 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[+25]% Strength <when defending>` | +25 | tools/gen_ruleset.py `Units` |
| Heaven Overseeing Tower | `[+2] Sight` | +2 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | movement | 2 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | strength | 42 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | cost | 300 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[-15]% Strength <if [Fate Gu] is constructed by anybody>` | -15 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[+50]% Strength <vs [pre-[Rank Six era]] units>` | +50 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[This Unit] takes [10] damage <upon ending a turn in a [Miasma Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[This Unit] takes [10] damage <upon ending a turn in a [Licorice Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[This Unit] takes [5] damage <upon ending a turn in a [Azure Water Wall] tile>` | 5 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[This Unit] takes [10] damage <upon ending a turn in a [Raging Flame Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[This Unit] takes [10] damage <upon ending a turn in a [Sage Wall] tile>` | 10 | tools/gen_ruleset.py `Units` |
| Immortal Zombie | `[+100]% maintenance costs` | +100 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | movement | 3 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | strength | 28 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | cost | 120 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | `[+20]% Strength bonus for [Beast] units within [2] tiles` | +20, 2 | tools/gen_ruleset.py `Units` |
| Thunder Crown Wolf | `[+200]% maintenance costs` | +200 | tools/gen_ruleset.py `Units` |
| Lone Gu Master | movement | 2 | tools/gen_ruleset.py `Units` |
| Lone Gu Master | strength | 11 | tools/gen_ruleset.py `Units` |
| Lone Gu Master | cost | 60 | tools/gen_ruleset.py `Units` |
| Lone Gu Master | `[+20]% Strength <when defending>` | +20 | tools/gen_ruleset.py `Units` |
| Demonic Gu Master | movement | 2 | tools/gen_ruleset.py `Units` |
| Demonic Gu Master | strength | 18 | tools/gen_ruleset.py `Units` |
| Demonic Gu Master | cost | 95 | tools/gen_ruleset.py `Units` |
| Demonic Gu Master | `[+20]% Strength <when attacking>` | +20 | tools/gen_ruleset.py `Units` |
| Demonic Gu Master | `Heals [15] damage if it kills a unit` | 15 | tools/gen_ruleset.py `Units` |
| Demonic Elder | movement | 2 | tools/gen_ruleset.py `Units` |
| Demonic Elder | strength | 35 | tools/gen_ruleset.py `Units` |
| Demonic Elder | cost | 190 | tools/gen_ruleset.py `Units` |
| Demonic Elder | `[+20]% Strength <when attacking>` | +20 | tools/gen_ruleset.py `Units` |
| Demonic Elder | `Heals [20] damage if it kills a unit` | 20 | tools/gen_ruleset.py `Units` |
| Demonic Elder | `[-10]% Strength for enemy [Military] units in adjacent [All] tiles` | -10 | tools/gen_ruleset.py `Units` |

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
| Moonlight Gu | `[This Unit] loses the [Moonlight Gu] promotion <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonlight Gu Hunger 67%]> <with [50]% chance>` | 50 | data/gu.csv `effects` / `extra_uniques` |
| Moonlight Gu | `[This Unit] gains the [Moonlight Gu Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonlight Gu Hunger 67%]>` | 2 | data/hunger.csv |
| Moonlight Gu | `[This Unit] gains the [Moonlight Gu Hunger 67%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonlight Gu Hunger 33%]>` | 2 | data/hunger.csv |
| Moonlight Gu | `[This Unit] gains the [Moonlight Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonlight Gu Hunger 100%]> <for units without [Moonlight Gu Hunger 67%]>` | 2 | data/hunger.csv |
| Moonlight Gu | `[This Unit] gains the [Moonlight Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units without [Moonlight Gu Hunger 33%]> <for units without [Moonlight Gu Hunger 67%]> <for units without [Moonlight Gu Hunger 100%]>` | 2 | data/hunger.csv |
| Moonlight Gu | `[-10]% Strength <for units with [Strength Master]>` | -10 | data/gu.csv `effects` / `extra_uniques` |
| White Boar Gu | `[+15]% Strength <when above [-1] [Wild Boar]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| White Boar Gu | `Consumes [1] [Wild Boar]` | 1 | data/gu.csv `eats` |
| White Boar Gu | `[This Unit] loses the [White Boar Gu] promotion <upon turn start> <when below [0] [Wild Boar]> <for units with [White Boar Gu Hunger 67%]> <with [50]% chance>` | 50 | data/gu.csv `effects` / `extra_uniques` |
| White Boar Gu | `[This Unit] gains the [White Boar Gu Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units with [White Boar Gu Hunger 67%]>` | 2 | data/hunger.csv |
| White Boar Gu | `[This Unit] gains the [White Boar Gu Hunger 67%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units with [White Boar Gu Hunger 33%]>` | 2 | data/hunger.csv |
| White Boar Gu | `[This Unit] gains the [White Boar Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units with [White Boar Gu Hunger 100%]> <for units without [White Boar Gu Hunger 67%]>` | 2 | data/hunger.csv |
| White Boar Gu | `[This Unit] gains the [White Boar Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units without [White Boar Gu Hunger 33%]> <for units without [White Boar Gu Hunger 67%]> <for units without [White Boar Gu Hunger 100%]>` | 2 | data/hunger.csv |
| Black Boar Gu | `[+15]% Strength <when above [-1] [Wild Boar]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| Black Boar Gu | `Consumes [1] [Wild Boar]` | 1 | data/gu.csv `eats` |
| Black Boar Gu | `[This Unit] loses the [Black Boar Gu] promotion <upon turn start> <when below [0] [Wild Boar]> <for units with [Black Boar Gu Hunger 67%]> <with [50]% chance>` | 50 | data/gu.csv `effects` / `extra_uniques` |
| Black Boar Gu | `[This Unit] gains the [Black Boar Gu Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units with [Black Boar Gu Hunger 67%]>` | 2 | data/hunger.csv |
| Black Boar Gu | `[This Unit] gains the [Black Boar Gu Hunger 67%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units with [Black Boar Gu Hunger 33%]>` | 2 | data/hunger.csv |
| Black Boar Gu | `[This Unit] gains the [Black Boar Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units with [Black Boar Gu Hunger 100%]> <for units without [Black Boar Gu Hunger 67%]>` | 2 | data/hunger.csv |
| Black Boar Gu | `[This Unit] gains the [Black Boar Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units without [Black Boar Gu Hunger 33%]> <for units without [Black Boar Gu Hunger 67%]> <for units without [Black Boar Gu Hunger 100%]>` | 2 | data/hunger.csv |
| Jade Skin Gu | `[+15]% Strength <when defending> <when above [-1] [Jade]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| Jade Skin Gu | `Consumes [1] [Jade]` | 1 | data/gu.csv `eats` |
| Jade Skin Gu | `[This Unit] loses the [Jade Skin Gu] promotion <upon turn start> <when below [0] [Jade]> <for units with [Jade Skin Gu Hunger 67%]> <with [50]% chance>` | 50 | data/gu.csv `effects` / `extra_uniques` |
| Jade Skin Gu | `[This Unit] gains the [Jade Skin Gu Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [Jade Skin Gu Hunger 67%]>` | 2 | data/hunger.csv |
| Jade Skin Gu | `[This Unit] gains the [Jade Skin Gu Hunger 67%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [Jade Skin Gu Hunger 33%]>` | 2 | data/hunger.csv |
| Jade Skin Gu | `[This Unit] gains the [Jade Skin Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [Jade Skin Gu Hunger 100%]> <for units without [Jade Skin Gu Hunger 67%]>` | 2 | data/hunger.csv |
| Jade Skin Gu | `[This Unit] gains the [Jade Skin Gu Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units without [Jade Skin Gu Hunger 33%]> <for units without [Jade Skin Gu Hunger 67%]> <for units without [Jade Skin Gu Hunger 100%]>` | 2 | data/hunger.csv |
| Liquor Worm | `[+50]% XP gained from combat <when above [-1] [Wine]>` | +50 | data/gu.csv `effects` / `extra_uniques` |
| Liquor Worm | `Consumes [1] [Wine]` | 1 | data/gu.csv `eats` |
| Liquor Worm | `[This Unit] loses the [Liquor Worm] promotion <upon turn start> <when below [0] [Wine]> <for units with [Liquor Worm Hunger 67%]> <with [50]% chance>` | 50 | data/gu.csv `effects` / `extra_uniques` |
| Liquor Worm | `[This Unit] gains the [Liquor Worm Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Liquor Worm Hunger 67%]>` | 2 | data/hunger.csv |
| Liquor Worm | `[This Unit] gains the [Liquor Worm Hunger 67%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Liquor Worm Hunger 33%]>` | 2 | data/hunger.csv |
| Liquor Worm | `[This Unit] gains the [Liquor Worm Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Liquor Worm Hunger 100%]> <for units without [Liquor Worm Hunger 67%]>` | 2 | data/hunger.csv |
| Liquor Worm | `[This Unit] gains the [Liquor Worm Hunger 33%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units without [Liquor Worm Hunger 33%]> <for units without [Liquor Worm Hunger 67%]> <for units without [Liquor Worm Hunger 100%]>` | 2 | data/hunger.csv |
| White Jade Gu | `[+15]% Strength <when above [-1] [Jade]>` | +15 | data/gu.csv `effects` / `extra_uniques` |
| White Jade Gu | `[+30]% Strength <when defending> <when above [-1] [Jade]>` | +30 | data/gu.csv `effects` / `extra_uniques` |
| White Jade Gu | `Consumes [2] [Jade]` | 2 | data/gu.csv `eats` |
| White Jade Gu | `[This Unit] loses the [White Jade Gu] promotion <upon turn start> <when below [0] [Jade]> <for units with [White Jade Gu Hunger 80%]> <with [50]% chance>` | 50 | data/gu.csv `effects` / `extra_uniques` |
| White Jade Gu | `[This Unit] gains the [White Jade Gu Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [White Jade Gu Hunger 80%]>` | 2 | data/hunger.csv |
| White Jade Gu | `[This Unit] gains the [White Jade Gu Hunger 80%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [White Jade Gu Hunger 60%]>` | 2 | data/hunger.csv |
| White Jade Gu | `[This Unit] gains the [White Jade Gu Hunger 60%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [White Jade Gu Hunger 40%]>` | 2 | data/hunger.csv |
| White Jade Gu | `[This Unit] gains the [White Jade Gu Hunger 40%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [White Jade Gu Hunger 20%]>` | 2 | data/hunger.csv |
| White Jade Gu | `[This Unit] gains the [White Jade Gu Hunger 20%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units with [White Jade Gu Hunger 100%]> <for units without [White Jade Gu Hunger 80%]>` | 2 | data/hunger.csv |
| White Jade Gu | `[This Unit] gains the [White Jade Gu Hunger 20%] status for [2] turn(s) <upon turn start> <when below [0] [Jade]> <for units without [White Jade Gu Hunger 20%]> <for units without [White Jade Gu Hunger 40%]> <for units without [White Jade Gu Hunger 60%]> <for units without [White Jade Gu Hunger 80%]> <for units without [White Jade Gu Hunger 100%]>` | 2 | data/hunger.csv |
| Moon Raiment | `[+20]% Strength <when attacking> <when above [-1] [Moon Orchid]>` | +20 | data/gu.csv `effects` / `extra_uniques` |
| Moon Raiment | `[+20]% Strength <when defending> <when above [-1] [Moon Orchid]>` | +20 | data/gu.csv `effects` / `extra_uniques` |
| Moon Raiment | `[+10]% Strength bonus for [Military] units within [1] tiles <when above [-1] [Moon Orchid]>` | +10, 1 | data/gu.csv `effects` / `extra_uniques` |
| Moon Raiment | `Consumes [1] [Moon Orchid]` | 1 | data/gu.csv `eats` |
| Moon Raiment | `[This Unit] loses the [Moon Raiment] promotion <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moon Raiment Hunger 80%]> <with [50]% chance>` | 50 | data/gu.csv `effects` / `extra_uniques` |
| Moon Raiment | `[This Unit] gains the [Moon Raiment Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moon Raiment Hunger 80%]>` | 2 | data/hunger.csv |
| Moon Raiment | `[This Unit] gains the [Moon Raiment Hunger 80%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moon Raiment Hunger 60%]>` | 2 | data/hunger.csv |
| Moon Raiment | `[This Unit] gains the [Moon Raiment Hunger 60%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moon Raiment Hunger 40%]>` | 2 | data/hunger.csv |
| Moon Raiment | `[This Unit] gains the [Moon Raiment Hunger 40%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moon Raiment Hunger 20%]>` | 2 | data/hunger.csv |
| Moon Raiment | `[This Unit] gains the [Moon Raiment Hunger 20%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moon Raiment Hunger 100%]> <for units without [Moon Raiment Hunger 80%]>` | 2 | data/hunger.csv |
| Moon Raiment | `[This Unit] gains the [Moon Raiment Hunger 20%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units without [Moon Raiment Hunger 20%]> <for units without [Moon Raiment Hunger 40%]> <for units without [Moon Raiment Hunger 60%]> <for units without [Moon Raiment Hunger 80%]> <for units without [Moon Raiment Hunger 100%]>` | 2 | data/hunger.csv |
| Killer Move | `[+25]% Strength <when attacking>` | +25 | tools/gen_ruleset.py `Promotions` |
| Killer Move | `[+25]% maintenance costs` | +25 | tools/gen_ruleset.py `Promotions` |
| Bear Strength Gu | `[+10]% Strength` | +10 | tools/gen_ruleset.py `Promotions` |
| Bear Strength Gu | `[+10]% maintenance costs` | +10 | tools/gen_ruleset.py `Promotions` |
| Stream Gu | `[+10] HP when healing` | +10 | tools/gen_ruleset.py `Promotions` |
| Stream Gu | `[+10]% maintenance costs` | +10 | tools/gen_ruleset.py `Promotions` |
| Jin Strength Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Jin Strength Gu | `[+8]% Strength` | +8 | tools/gen_ruleset.py `Promotions` |
| Jin Strength Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Brute Force Longhorn Beetle Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Brute Force Longhorn Beetle Gu | `[+12]% Strength <when attacking>` | +12 | tools/gen_ruleset.py `Promotions` |
| Brute Force Longhorn Beetle Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Stone Skin Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Stone Skin Gu | `[+12]% Strength <when defending>` | +12 | tools/gen_ruleset.py `Promotions` |
| Stone Skin Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Iron Skin Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Iron Skin Gu | `[+12]% Strength <when defending>` | +12 | tools/gen_ruleset.py `Promotions` |
| Iron Skin Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Iron Skin Gu | `[This Unit] gains the [Iron Stone Bastion] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement> <for units with [Stone Skin Gu]> <for units with [Metal Grandmaster]> <for units with [Earth Grandmaster]> <for units without [Iron Stone Bastion]>` | 1, +15, 1 | tools/gen_ruleset.py `Promotions` |
| Stealth Stone Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Stealth Stone Gu | `[+4]% Strength <when defending>` | +4 | tools/gen_ruleset.py `Promotions` |
| Stealth Stone Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Vitality Leaf | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Vitality Leaf | `[+7] HP when healing` | +7 | tools/gen_ruleset.py `Promotions` |
| Vitality Leaf | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Bookworm | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Bookworm | `[+15]% XP gained from combat` | +15 | tools/gen_ruleset.py `Promotions` |
| Bookworm | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Smelly Fart Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Smelly Fart Gu | `[Target Unit] gains the [Poisoned] status for [1] turn(s) <upon damaging a [Military] unit> <when attacking>` | 1 | tools/gen_ruleset.py `Promotions` |
| Smelly Fart Gu | `[+3]% Strength <when attacking>` | +3 | tools/gen_ruleset.py `Promotions` |
| Smelly Fart Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Flash Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Flash Gu | `[Target Unit] gains the [Blinded] status for [1] turn(s) <upon damaging a [Military] unit> <when attacking>` | 1 | tools/gen_ruleset.py `Promotions` |
| Flash Gu | `[+3]% Strength <when attacking>` | +3 | tools/gen_ruleset.py `Promotions` |
| Flash Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Flash Gu | `[This Unit] gains the [Blinding Palm] status for [1] turn(s) <costs [+25 Gold] stats> <requires [1] movement> <for units with [Hand Blade Gu]> <for units with [Light Grandmaster]> <for units with [Blade Grandmaster]> <for units without [Blinding Palm]>` | 1, +25, 1 | tools/gen_ruleset.py `Promotions` |
| Grass Puppet Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Grass Puppet Gu | `[-3]% Strength for enemy [Military] units in adjacent [All] tiles` | -3 | tools/gen_ruleset.py `Promotions` |
| Grass Puppet Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Grass Puppet Gu | `[This Unit] gains the [Grass Army Ambush] status for [1] turn(s) <costs [+30 Gold] stats> <requires [1] movement> <for units with [Grass Tree Army Gu]> <for units with [Enslavement Grandmaster]> <for units with [Wood Grandmaster]> <for units without [Grass Army Ambush]>` | 1, +30, 1 | tools/gen_ruleset.py `Promotions` |
| Clear Wind Wheel Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Clear Wind Wheel Gu | `[+1] Movement` | +1 | tools/gen_ruleset.py `Promotions` |
| Clear Wind Wheel Gu | `[+2]% Strength` | +2 | tools/gen_ruleset.py `Promotions` |
| Clear Wind Wheel Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Clear Wind Wheel Gu | `[This Unit] gains the [Twin Wheel Gale] status for [1] turn(s) <costs [+20 Gold] stats> <requires [1] movement> <for units with [Jade Wind Wheel Gu]> <for units with [Wind Grandmaster]> <for units without [Twin Wheel Gale]>` | 1, +20, 1 | tools/gen_ruleset.py `Promotions` |
| Jade Wind Wheel Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Jade Wind Wheel Gu | `[+16]% Strength <when attacking>` | +16 | tools/gen_ruleset.py `Promotions` |
| Jade Wind Wheel Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[+16]% Strength <when attacking> <when above [-1] [Moon Orchid]>` | +16 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `Consumes [1] [Moon Orchid]` | 1 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] loses the [Moonglow Gu] promotion <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonglow Gu Hunger 80%]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] gains the [Moonglow Gu Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonglow Gu Hunger 80%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] gains the [Moonglow Gu Hunger 80%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonglow Gu Hunger 60%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] gains the [Moonglow Gu Hunger 60%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonglow Gu Hunger 40%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] gains the [Moonglow Gu Hunger 40%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonglow Gu Hunger 20%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] gains the [Moonglow Gu Hunger 20%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units with [Moonglow Gu Hunger 100%]> <for units without [Moonglow Gu Hunger 80%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] gains the [Moonglow Gu Hunger 20%] status for [2] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units without [Moonglow Gu Hunger 20%]> <for units without [Moonglow Gu Hunger 40%]> <for units without [Moonglow Gu Hunger 60%]> <for units without [Moonglow Gu Hunger 80%]> <for units without [Moonglow Gu Hunger 100%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Moonglow Gu | `[This Unit] gains the [Bleeding Moon] status for [1] turn(s) <costs [+25 Gold] stats> <requires [1] movement> <for units with [Blood Moon Gu]> <for units with [Moon Grandmaster]> <for units with [Blood Grandmaster]> <for units without [Bleeding Moon]>` | 1, +25, 1 | tools/gen_ruleset.py `Promotions` |
| Stealth Scales Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Stealth Scales Gu | `[+6]% Strength <when defending>` | +6 | tools/gen_ruleset.py `Promotions` |
| Stealth Scales Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Ice Knife Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Ice Knife Gu | `[+16]% Strength <when attacking>` | +16 | tools/gen_ruleset.py `Promotions` |
| Ice Knife Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Ice Knife Gu | `[This Unit] gains the [Ice Blade Storm] status for [1] turn(s) <costs [+20 Gold] stats> <requires [1] movement> <for units with [Whirlwind Gu]> <for units with [Ice Snow Grandmaster]> <for units with [Wind Grandmaster]> <for units without [Ice Blade Storm]>` | 1, +20, 1 | tools/gen_ruleset.py `Promotions` |
| Icicle Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Icicle Gu | `[Target Unit] gains the [Frozen] status for [1] turn(s) <upon damaging a [Military] unit> <when attacking>` | 1 | tools/gen_ruleset.py `Promotions` |
| Icicle Gu | `[+4]% Strength <when attacking>` | +4 | tools/gen_ruleset.py `Promotions` |
| Icicle Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Nine Leaf Vitality Grass | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Nine Leaf Vitality Grass | `[+10] HP when healing` | +10 | tools/gen_ruleset.py `Promotions` |
| Nine Leaf Vitality Grass | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Earth Communication Ear Grass | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Earth Communication Ear Grass | `[+1] Sight` | +1 | tools/gen_ruleset.py `Promotions` |
| Earth Communication Ear Grass | `[+3]% Strength` | +3 | tools/gen_ruleset.py `Promotions` |
| Earth Communication Ear Grass | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Earth Communication Ear Grass | `[This Unit] gains the [Earth Listening Ambush] status for [1] turn(s) <costs [+20 Gold] stats> <requires [1] movement> <for units with [Stealth Scales Gu]> <for units with [Earth Grandmaster]> <for units without [Earth Listening Ambush]>` | 1, +20, 1 | tools/gen_ruleset.py `Promotions` |
| Spiral Bone Spear Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Spiral Bone Spear Gu | `[Target Unit] takes [6] damage <upon damaging a [Military] unit> <when attacking>` | 6 | tools/gen_ruleset.py `Promotions` |
| Spiral Bone Spear Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Spiral Bone Spear Gu | `[This Unit] gains the [Spiral Drill Star Spear] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Star River Gu]> <for units with [Bone Grandmaster]> <for units with [Star Grandmaster]> <for units without [Spiral Drill Star Spear]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Plasma Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Plasma Gu | `[Target Unit] takes [6] damage <upon damaging a [Military] unit> <when attacking>` | 6 | tools/gen_ruleset.py `Promotions` |
| Plasma Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Water Drill Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Water Drill Gu | `[+16]% Strength <when attacking>` | +16 | tools/gen_ruleset.py `Promotions` |
| Water Drill Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Living Steel Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Living Steel Gu | `[+10] HP when healing` | +10 | tools/gen_ruleset.py `Promotions` |
| Living Steel Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Eating Wind Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Eating Wind Gu | `[-8]% maintenance costs` | -8 | tools/gen_ruleset.py `Promotions` |
| Eating Wind Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Love Life Separation | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Love Life Separation | `[Target Unit] gains the [Poisoned] status for [1] turn(s) <upon damaging a [Military] unit> <when attacking>` | 1 | tools/gen_ruleset.py `Promotions` |
| Love Life Separation | `[+4]% Strength <when attacking>` | +4 | tools/gen_ruleset.py `Promotions` |
| Love Life Separation | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Love Life Separation | `[This Unit] gains the [Ten Thousand Poisons] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Jade Sky Gu]> <for units with [Poison Grandmaster]> <for units without [Ten Thousand Poisons]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Ghost Fire Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Ghost Fire Gu | `[Target Unit] takes [6] damage <upon damaging a [Military] unit> <when attacking>` | 6 | tools/gen_ruleset.py `Promotions` |
| Ghost Fire Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Ghost Fire Gu | `[This Unit] gains the [Soul Fire Burst] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Soul Explosion Gu]> <for units with [Soul Grandmaster]> <for units without [Soul Fire Burst]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Whip Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Whip Gu | `[Target Unit] takes [6] damage <upon damaging a [Military] unit> <when attacking>` | 6 | tools/gen_ruleset.py `Promotions` |
| Whip Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Blood Moon Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Blood Moon Gu | `[Target Unit] gains the [Bleeding] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Blood Moon Gu | `[+5]% Strength <when attacking>` | +5 | tools/gen_ruleset.py `Promotions` |
| Blood Moon Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Blue Bird Ice Coffin Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Blue Bird Ice Coffin Gu | `[Target Unit] gains the [Frozen] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Blue Bird Ice Coffin Gu | `[+5]% Strength <when attacking>` | +5 | tools/gen_ruleset.py `Promotions` |
| Blue Bird Ice Coffin Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Blue Bird Ice Coffin Gu | `[This Unit] gains the [Ice Coffin Prison] status for [1] turn(s) <costs [+25 Gold] stats> <requires [1] movement> <for units with [Water Prison Gu]> <for units with [Ice Snow Grandmaster]> <for units with [Water Grandmaster]> <for units without [Ice Coffin Prison]>` | 1, +25, 1 | tools/gen_ruleset.py `Promotions` |
| Lightning Wings Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Lightning Wings Gu | `[+1] Movement` | +1 | tools/gen_ruleset.py `Promotions` |
| Lightning Wings Gu | `[+4]% Strength` | +4 | tools/gen_ruleset.py `Promotions` |
| Lightning Wings Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Lightning Wings Gu | `[This Unit] gains the [Thunder Wing Dive] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Thunder Hammer Gu]> <for units with [Lightning Grandmaster]> <for units without [Thunder Wing Dive]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Lava Explosion Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Lava Explosion Gu | `[Target Unit] takes [8] damage <upon damaging a [Military] unit> <when attacking>` | 8 | tools/gen_ruleset.py `Promotions` |
| Lava Explosion Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Water Prison Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Water Prison Gu | `[Target Unit] gains the [Entangled] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Water Prison Gu | `[+5]% Strength <when attacking>` | +5 | tools/gen_ruleset.py `Promotions` |
| Water Prison Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Sight Blow Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Sight Blow Gu | `[Target Unit] takes [8] damage <upon damaging a [Military] unit> <when attacking>` | 8 | tools/gen_ruleset.py `Promotions` |
| Sight Blow Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Starlight Firefly Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Starlight Firefly Gu | `[+1] Sight` | +1 | tools/gen_ruleset.py `Promotions` |
| Starlight Firefly Gu | `[+4]% Strength` | +4 | tools/gen_ruleset.py `Promotions` |
| Starlight Firefly Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Starlight Firefly Gu | `[This Unit] gains the [Myriad Star Fireflies] status for [1] turn(s) <costs [+30 Gold] stats> <requires [1] movement> <for units with [Clear Mind Gu]> <for units with [Star Grandmaster]> <for units with [Wisdom Grandmaster]> <for units without [Myriad Star Fireflies]>` | 1, +30, 1 | tools/gen_ruleset.py `Promotions` |
| Self-Reliance Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Self-Reliance Gu | `[+13] HP when healing` | +13 | tools/gen_ruleset.py `Promotions` |
| Self-Reliance Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Self-Reliance Gu | `[This Unit] gains the [Eight Beast Phantoms] status for [1] turn(s) <costs [+25 Gold] stats> <requires [1] movement> <for units with [Strength Qi Gu]> <for units with [Strength Grandmaster]> <for units with [Qi Grandmaster]> <for units without [Eight Beast Phantoms]>` | 1, +25, 1 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[+25]% XP gained from combat <when above [-1] [Wine]>` | +25 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `Consumes [1] [Wine]` | 1 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] loses the [Seven Fragrances Liquor Worm] promotion <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 86%]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 100%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 86%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 86%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 71%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 71%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 57%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 57%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 43%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 43%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 29%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 29%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 14%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 14%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units with [Seven Fragrances Liquor Worm Hunger 100%]> <for units without [Seven Fragrances Liquor Worm Hunger 86%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[This Unit] gains the [Seven Fragrances Liquor Worm Hunger 14%] status for [2] turn(s) <upon turn start> <when below [0] [Wine]> <for units without [Seven Fragrances Liquor Worm Hunger 14%]> <for units without [Seven Fragrances Liquor Worm Hunger 29%]> <for units without [Seven Fragrances Liquor Worm Hunger 43%]> <for units without [Seven Fragrances Liquor Worm Hunger 57%]> <for units without [Seven Fragrances Liquor Worm Hunger 71%]> <for units without [Seven Fragrances Liquor Worm Hunger 86%]> <for units without [Seven Fragrances Liquor Worm Hunger 100%]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Seven Fragrances Liquor Worm | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Chainsaw Golden Centipede | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Chainsaw Golden Centipede | `[+20]% Strength <when attacking>` | +20 | tools/gen_ruleset.py `Promotions` |
| Chainsaw Golden Centipede | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Chainsaw Golden Centipede | `[This Unit] gains the [Golden Saw Tide] status for [1] turn(s) <costs [+25 Gold] stats> <requires [1] movement> <for units with [Living Steel Gu]> <for units with [Metal Grandmaster]> <for units without [Golden Saw Tide]>` | 1, +25, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Bone Shield Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Flying Bone Shield Gu | `[+20]% Strength <when defending>` | +20 | tools/gen_ruleset.py `Promotions` |
| Flying Bone Shield Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Hand Blade Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Hand Blade Gu | `[+20]% Strength <when attacking>` | +20 | tools/gen_ruleset.py `Promotions` |
| Hand Blade Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Dual Cloud Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Dual Cloud Gu | `[+1] Movement` | +1 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Dual Cloud Gu | `[+4]% Strength` | +4 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Dual Cloud Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Dual Cloud Gu | `[This Unit] gains the [Nine Cloud Ring] status for [1] turn(s) <costs [+30 Gold] stats> <requires [1] movement> <for units with [Flying Cloud Gu]> <for units with [Cloud Grandmaster]> <for units without [Nine Cloud Ring]>` | 1, +30, 1 | tools/gen_ruleset.py `Promotions` |
| Poison Vow Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Poison Vow Gu | `[-5]% Strength for enemy [Military] units in adjacent [All] tiles` | -5 | tools/gen_ruleset.py `Promotions` |
| Poison Vow Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Iron Rod Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Iron Rod Gu | `[+20]% Strength <when attacking>` | +20 | tools/gen_ruleset.py `Promotions` |
| Iron Rod Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Gentle Feelings Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Gentle Feelings Gu | `[Target Unit] gains the [Charmed] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Gentle Feelings Gu | `[+5]% Strength <when attacking>` | +5 | tools/gen_ruleset.py `Promotions` |
| Gentle Feelings Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Mirage Veil Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Mirage Veil Gu | `[+8]% Strength <when defending>` | +8 | tools/gen_ruleset.py `Promotions` |
| Mirage Veil Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Furnace Pill Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Furnace Pill Gu | `[+13] HP when healing` | +13 | tools/gen_ruleset.py `Promotions` |
| Furnace Pill Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Bone Wings Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Bone Wings Gu | `[+1] Movement` | +1 | tools/gen_ruleset.py `Promotions` |
| Bone Wings Gu | `[+5]% Strength` | +5 | tools/gen_ruleset.py `Promotions` |
| Bone Wings Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Bone Wings Gu | `[This Unit] gains the [Bone Spear Rain] status for [1] turn(s) <costs [+30 Gold] stats> <requires [1] movement> <for units with [Spiral Bone Spear Gu]> <for units with [Bone Grandmaster]> <for units without [Bone Spear Rain]>` | 1, +30, 1 | tools/gen_ruleset.py `Promotions` |
| Impermanence Bone Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Impermanence Bone Gu | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Impermanence Bone Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Golden Breeze Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Golden Breeze Gu | `[+16] HP when healing` | +16 | tools/gen_ruleset.py `Promotions` |
| Golden Breeze Gu | `Heals [13] damage if it kills a unit` | 13 | tools/gen_ruleset.py `Promotions` |
| Golden Breeze Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Fiery Snake Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Fiery Snake Gu | `[Target Unit] gains the [Burning] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Fiery Snake Gu | `[+6]% Strength <when attacking>` | +6 | tools/gen_ruleset.py `Promotions` |
| Fiery Snake Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Fiery Snake Gu | `[This Unit] gains the [Molten Serpent Coil] status for [1] turn(s) <costs [+30 Gold] stats> <requires [1] movement> <for units with [Lava Explosion Gu]> <for units with [Fire Grandmaster]> <for units without [Molten Serpent Coil]>` | 1, +30, 1 | tools/gen_ruleset.py `Promotions` |
| Water Curtain Skyflower Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Water Curtain Skyflower Gu | `[+24]% Strength <when defending>` | +24 | tools/gen_ruleset.py `Promotions` |
| Water Curtain Skyflower Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Instant Success Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Instant Success Gu | `[+30]% XP gained from combat` | +30 | tools/gen_ruleset.py `Promotions` |
| Instant Success Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Location Swap Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Location Swap Gu | `[+10]% Strength <when defending>` | +10 | tools/gen_ruleset.py `Promotions` |
| Location Swap Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Sword Qi Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Sword Qi Gu | `[Target Unit] takes [10] damage <upon damaging a [Military] unit> <when attacking>` | 10 | tools/gen_ruleset.py `Promotions` |
| Sword Qi Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Tiger Roar Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Tiger Roar Gu | `[-6]% Strength for enemy [Military] units in adjacent [All] tiles` | -6 | tools/gen_ruleset.py `Promotions` |
| Tiger Roar Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Grass Tree Army Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Grass Tree Army Gu | `[+24]% Strength <when defending>` | +24 | tools/gen_ruleset.py `Promotions` |
| Grass Tree Army Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Moonshadow Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Moonshadow Gu | `[Target Unit] gains the [Sealed] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Moonshadow Gu | `[+6]% Strength <when attacking>` | +6 | tools/gen_ruleset.py `Promotions` |
| Moonshadow Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Moonshadow Gu | `[This Unit] gains the [Sealed Moonshadow] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Search Lock Gu]> <for units with [Moon Grandmaster]> <for units with [Space Grandmaster]> <for units without [Sealed Moonshadow]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Rotation Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Rotation Gu | `[+16] HP when healing` | +16 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Rotation Gu | `Heals [13] damage if it kills a unit` | 13 | tools/gen_ruleset.py `Promotions` |
| Yin Yang Rotation Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Blood Frenzy Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Blood Frenzy Gu | `[-6]% Strength for enemy [Military] units in adjacent [All] tiles` | -6 | tools/gen_ruleset.py `Promotions` |
| Blood Frenzy Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| East Window Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| East Window Gu | `[+1] Sight` | +1 | tools/gen_ruleset.py `Promotions` |
| East Window Gu | `[+5]% Strength` | +5 | tools/gen_ruleset.py `Promotions` |
| East Window Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Play Phantom Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Play Phantom Gu | `[+10]% Strength <when defending>` | +10 | tools/gen_ruleset.py `Promotions` |
| Play Phantom Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Array Stone Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Array Stone Gu | `[+24]% Strength <when defending>` | +24 | tools/gen_ruleset.py `Promotions` |
| Array Stone Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Ink Beast Gu | `[+5]% maintenance costs` | +5 | tools/gen_ruleset.py `Promotions` |
| Ink Beast Gu | `[-6]% Strength for enemy [Military] units in adjacent [All] tiles` | -6 | tools/gen_ruleset.py `Promotions` |
| Ink Beast Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Blood Guillotine | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Blood Guillotine | `[Target Unit] takes [12] damage <upon damaging a [Military] unit> <when attacking>` | 12 | tools/gen_ruleset.py `Promotions` |
| Blood Guillotine | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Earth Overlord Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Earth Overlord Gu | `[+20]% Strength` | +20 | tools/gen_ruleset.py `Promotions` |
| Earth Overlord Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Earth Overlord Gu | `[This Unit] gains the [Four Arm Earth King] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Brute Force Longhorn Beetle Gu]> <for units with [Strength Grandmaster]> <for units without [Four Arm Earth King]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Extreme Light Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Extreme Light Gu | `[+28]% Strength <when attacking>` | +28 | tools/gen_ruleset.py `Promotions` |
| Extreme Light Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Extreme Light Gu | `[This Unit] gains the [My Glorious Spear] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Little Light Gu]> <for units with [Light Grandmaster]> <for units without [My Glorious Spear]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Star River Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Star River Gu | `[Target Unit] takes [12] damage <upon damaging a [Military] unit> <when attacking>` | 12 | tools/gen_ruleset.py `Promotions` |
| Star River Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Thunder Hammer Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Thunder Hammer Gu | `[+28]% Strength <when attacking>` | +28 | tools/gen_ruleset.py `Promotions` |
| Thunder Hammer Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Flash Bug Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Flash Bug Gu | `[+1] Movement` | +1 | tools/gen_ruleset.py `Promotions` |
| Flash Bug Gu | `[+6]% Strength` | +6 | tools/gen_ruleset.py `Promotions` |
| Flash Bug Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Treacherous Cloud Wave Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Treacherous Cloud Wave Gu | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Treacherous Cloud Wave Gu | `[+7]% Strength <when attacking>` | +7 | tools/gen_ruleset.py `Promotions` |
| Treacherous Cloud Wave Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Jade Sky Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Jade Sky Gu | `[Target Unit] gains the [Poisoned] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Jade Sky Gu | `[+7]% Strength <when attacking>` | +7 | tools/gen_ruleset.py `Promotions` |
| Jade Sky Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Fire Cape Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Fire Cape Gu | `[+28]% Strength <when defending>` | +28 | tools/gen_ruleset.py `Promotions` |
| Fire Cape Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Flying Snow Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Flying Snow Gu | `[-7]% Strength for enemy [Military] units in adjacent [All] tiles` | -7 | tools/gen_ruleset.py `Promotions` |
| Flying Snow Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Keep Silent Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Keep Silent Gu | `[Target Unit] gains the [Dazed] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Keep Silent Gu | `[+7]% Strength <when attacking>` | +7 | tools/gen_ruleset.py `Promotions` |
| Keep Silent Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Soul Explosion Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Soul Explosion Gu | `[Target Unit] takes [12] damage <upon damaging a [Military] unit> <when attacking>` | 12 | tools/gen_ruleset.py `Promotions` |
| Soul Explosion Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Asura Zombie Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Asura Zombie Gu | `[+20]% Strength` | +20 | tools/gen_ruleset.py `Promotions` |
| Asura Zombie Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Asura Zombie Gu | `[This Unit] gains the [Six Arm Heavenly Corpse King] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Transformation Grandmaster]> <for units without [Six Arm Heavenly Corpse King]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Search Lock Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Search Lock Gu | `[Target Unit] gains the [Sealed] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Search Lock Gu | `[+7]% Strength <when attacking>` | +7 | tools/gen_ruleset.py `Promotions` |
| Search Lock Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Search Lock Gu | `[This Unit] gains the [Limitless Search Lock] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Warp Gu]> <for units with [Space Grandmaster]> <for units without [Limitless Search Lock]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Dream Butterfly Gu | `[+6]% maintenance costs` | +6 | tools/gen_ruleset.py `Promotions` |
| Dream Butterfly Gu | `[+35]% XP gained from combat` | +35 | tools/gen_ruleset.py `Promotions` |
| Dream Butterfly Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Dream Butterfly Gu | `[This Unit] gains the [Unravel Dream] status for [1] turn(s) <costs [+35 Gold] stats> <requires [1] movement> <for units with [Dream Pillow Gu]> <for units with [Dream Grandmaster]> <for units without [Unravel Dream]>` | 1, +35, 1 | tools/gen_ruleset.py `Promotions` |
| Green Silk Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Green Silk Gu | `[+12]% Strength <when defending>` | +12 | tools/gen_ruleset.py `Promotions` |
| Green Silk Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Black Mane Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Black Mane Gu | `[+11]% Strength` | +11 | tools/gen_ruleset.py `Promotions` |
| Black Mane Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Steel Mane Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Steel Mane Gu | `[+14]% Strength` | +14 | tools/gen_ruleset.py `Promotions` |
| Steel Mane Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Stealth Rock Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Stealth Rock Gu | `[+4]% Strength <when defending>` | +4 | tools/gen_ruleset.py `Promotions` |
| Stealth Rock Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Rock Skin Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Rock Skin Gu | `[+12]% Strength <when defending>` | +12 | tools/gen_ruleset.py `Promotions` |
| Rock Skin Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Beast Skin Gu | `[+2]% maintenance costs` | +2 | tools/gen_ruleset.py `Promotions` |
| Beast Skin Gu | `[+12]% Strength <when defending>` | +12 | tools/gen_ruleset.py `Promotions` |
| Beast Skin Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Bear Enslavement Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Bear Enslavement Gu | `[+20]% Strength <vs [Beast] units>` | +20 | tools/gen_ruleset.py `Promotions` |
| Bear Enslavement Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Charred Thunder Potato Gu | `[+3]% maintenance costs` | +3 | tools/gen_ruleset.py `Promotions` |
| Charred Thunder Potato Gu | `[+16]% Strength <when defending>` | +16 | tools/gen_ruleset.py `Promotions` |
| Charred Thunder Potato Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Thunder Wings Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Thunder Wings Gu | `[+1] Movement` | +1 | tools/gen_ruleset.py `Promotions` |
| Thunder Wings Gu | `[+4]% Strength` | +4 | tools/gen_ruleset.py `Promotions` |
| Thunder Wings Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Sky Canopy Gu | `[+4]% maintenance costs` | +4 | tools/gen_ruleset.py `Promotions` |
| Sky Canopy Gu | `[+20]% Strength <when defending>` | +20 | tools/gen_ruleset.py `Promotions` |
| Sky Canopy Gu | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Star Mark Immortal Gu Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Star Mark Immortal Gu] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Star Mark Immortal Gu Bearer | `Only available <when number of [[Star Mark Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Star Mark Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Star Mark Immortal Gu Bearer | `[This Unit] gains the [Star Mark Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Star Dart Gu]> <for units with [Star Great Grandmaster]> <for units without [Star Mark Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Star Mark Immortal Gu Bearer | `[This Unit] gains the [Star Mark Moon Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Moonlight Gu]> <for units with [Star Great Grandmaster]> <for units with [Moon Grandmaster]> <for units without [Star Mark Moon Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Immortal Gu Bearer | `[+32]% Strength <when defending> <when above [0] [Green Grape Immortal Essence]> <if [Pulling Water Immortal Gu] is constructed>` | +32, 0 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Immortal Gu Bearer | `Only available <when number of [[Pulling Water Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Immortal Gu Bearer | `[This Unit] gains the [Pulling Water Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [White Boar Gu]> <for units with [Strength Great Grandmaster]> <for units without [Pulling Water Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Immortal Gu Bearer | `[This Unit] gains the [Pulling Water Transformation Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Strength Great Grandmaster]> <for units with [Transformation Grandmaster]> <for units without [Pulling Water Transformation Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Snack Immortal Gu Bearer | `[-16]% maintenance costs <when above [0] [Green Grape Immortal Essence]> <if [Snack Immortal Gu] is constructed>` | -16, 0 | tools/gen_ruleset.py `Promotions` |
| Snack Immortal Gu Bearer | `Only available <when number of [[Snack Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Snack Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Snack Immortal Gu Bearer | `[This Unit] gains the [Snack Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Liquor Worm]> <for units with [Food Great Grandmaster]> <for units without [Snack Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Snack Immortal Gu Bearer | `[This Unit] gains the [Snack Pill Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Pill Refiner Gu]> <for units with [Food Great Grandmaster]> <for units with [Pill Grandmaster]> <for units without [Snack Pill Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Immortal Gu Bearer | `[+32]% Strength <when attacking> <when above [0] [Green Grape Immortal Essence]> <if [Flying Bear Strength Immortal Gu] is constructed>` | +32, 0 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Immortal Gu Bearer | `Only available <when number of [[Flying Bear Strength Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Immortal Gu Bearer | `[This Unit] gains the [Flying Bear Strength Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [White Boar Gu]> <for units with [Strength Great Grandmaster]> <for units without [Flying Bear Strength Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Immortal Gu Bearer | `[This Unit] gains the [Flying Bear Strength Transformation Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Strength Great Grandmaster]> <for units with [Transformation Grandmaster]> <for units without [Flying Bear Strength Transformation Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Change Form Immortal Gu Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Change Form Immortal Gu] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Change Form Immortal Gu Bearer | `Only available <when number of [[Change Form Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Change Form Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Change Form Immortal Gu Bearer | `[This Unit] gains the [Flying Bear Transformation] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Flying Bear Strength Immortal Gu Bearer]> <for units with [Transformation Great Grandmaster]> <for units with [Strength Grandmaster]> <for units without [Flying Bear Transformation]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Change Form Immortal Gu Bearer | `[This Unit] gains the [Change Form Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Transformation Great Grandmaster]> <for units without [Change Form Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Change Form Immortal Gu Bearer | `[This Unit] gains the [Change Form Bone Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Bone Spear Gu]> <for units with [Transformation Great Grandmaster]> <for units with [Bone Grandmaster]> <for units without [Change Form Bone Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Immortal Gu Bearer | `[Target Unit] takes [14] damage <upon damaging a [Military] unit> <when attacking> <when above [0] [Green Grape Immortal Essence]> <if [Blood Asset Immortal Gu] is constructed>` | 14, 0 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Immortal Gu Bearer | `Only available <when number of [[Blood Asset Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Immortal Gu Bearer | `[This Unit] gains the [Blood Torrent] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Blood Skull Gu]> <for units with [Blood Great Grandmaster]> <for units without [Blood Torrent]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Immortal Gu Bearer | `[This Unit] gains the [Blood Healing Lake] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Blood Moon Gu]> <for units with [Blood Great Grandmaster]> <for units without [Blood Healing Lake]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Immortal Gu Bearer | `[This Unit] gains the [Blood Asset Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Blood Skull Gu]> <for units with [Blood Great Grandmaster]> <for units without [Blood Asset Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Immortal Gu Bearer | `[This Unit] gains the [Blood Asset Strength Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [White Boar Gu]> <for units with [Blood Great Grandmaster]> <for units with [Strength Grandmaster]> <for units without [Blood Asset Strength Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Immortal Gu Bearer | `[+22] HP when healing <when above [0] [Green Grape Immortal Essence]> <if [Cleanse Soul Immortal Gu] is constructed>` | +22, 0 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Immortal Gu Bearer | `Heals [17] damage if it kills a unit <when above [0] [Green Grape Immortal Essence]> <if [Cleanse Soul Immortal Gu] is constructed>` | 17, 0 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Immortal Gu Bearer | `Only available <when number of [[Cleanse Soul Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Immortal Gu Bearer | `[This Unit] gains the [Ghost Official Garment] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Soul Search Gu]> <for units with [Soul Great Grandmaster]> <for units without [Ghost Official Garment]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Immortal Gu Bearer | `[This Unit] gains the [Cleanse Soul Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Soul Search Gu]> <for units with [Soul Great Grandmaster]> <for units without [Cleanse Soul Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Immortal Gu Bearer | `[This Unit] gains the [Cleanse Soul Dream Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Dream Pillow Gu]> <for units with [Soul Great Grandmaster]> <for units with [Dream Grandmaster]> <for units without [Cleanse Soul Dream Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Immortal Gu Bearer | `[Target Unit] takes [14] damage <upon damaging a [Military] unit> <when attacking> <when above [0] [Green Grape Immortal Essence]> <if [Dark Arrow Immortal Gu] is constructed>` | 14, 0 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Immortal Gu Bearer | `Only available <when number of [[Dark Arrow Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Immortal Gu Bearer | `[This Unit] gains the [Dark Arrow Rain] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Shadow Follower Gu]> <for units with [Dark Great Grandmaster]> <for units without [Dark Arrow Rain]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Immortal Gu Bearer | `[This Unit] gains the [Dark Arrow Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Shadow Follower Gu]> <for units with [Dark Great Grandmaster]> <for units without [Dark Arrow Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Immortal Gu Bearer | `[This Unit] gains the [Dark Arrow Shadow Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Overlapping Shadow Gu]> <for units with [Dark Great Grandmaster]> <for units with [Shadow Grandmaster]> <for units without [Dark Arrow Shadow Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Immortal Gu Bearer | `[-8]% Strength for enemy [Military] units in adjacent [All] tiles <when above [0] [Green Grape Immortal Essence]> <if [Heavenly Gong Immortal Gu] is constructed>` | -8, 0 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Immortal Gu Bearer | `Only available <when number of [[Heavenly Gong Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Immortal Gu Bearer | `[This Unit] gains the [Silent Gong] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Keep Silent Gu]> <for units with [Sound Great Grandmaster]> <for units without [Silent Gong]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Immortal Gu Bearer | `[This Unit] gains the [Heavenly Gong Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Heaven Earth Magnificent Sound Gu]> <for units with [Sound Great Grandmaster]> <for units without [Heavenly Gong Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Immortal Gu Bearer | `[This Unit] gains the [Heavenly Gong Illusion Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Illusory Moon Gu]> <for units with [Sound Great Grandmaster]> <for units with [Illusion Grandmaster]> <for units without [Heavenly Gong Illusion Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Immortal Gu Bearer | `[Target Unit] gains the [Frozen] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking> <when above [0] [Green Grape Immortal Essence]> <if [Ice Soul Immortal Gu] is constructed>` | 3, 0 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Immortal Gu Bearer | `[+8]% Strength <when attacking> <when above [0] [Green Grape Immortal Essence]> <if [Ice Soul Immortal Gu] is constructed>` | +8, 0 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Immortal Gu Bearer | `Only available <when number of [[Ice Soul Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Immortal Gu Bearer | `[This Unit] gains the [Ice Soul Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Frost Demon Gu]> <for units with [Ice Snow Great Grandmaster]> <for units without [Ice Soul Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Immortal Gu Bearer | `[This Unit] gains the [Ice Soul Lightning Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Thunderclap Gu]> <for units with [Ice Snow Great Grandmaster]> <for units with [Lightning Grandmaster]> <for units without [Ice Soul Lightning Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Immortal Gu Bearer | `[+1] Movement <when above [0] [Green Grape Immortal Essence]> <if [Rising Azure Cloud Immortal Gu] is constructed>` | +1, 0 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Immortal Gu Bearer | `[+7]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Rising Azure Cloud Immortal Gu] is constructed>` | +7, 0 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Immortal Gu Bearer | `Only available <when number of [[Rising Azure Cloud Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Immortal Gu Bearer | `[This Unit] gains the [Rising Azure Cloud Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Flying Cloud Gu]> <for units with [Cloud Great Grandmaster]> <for units without [Rising Azure Cloud Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Immortal Gu Bearer | `[This Unit] gains the [Rising Azure Cloud Ice Snow Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Frost Demon Gu]> <for units with [Cloud Great Grandmaster]> <for units with [Ice Snow Grandmaster]> <for units without [Rising Azure Cloud Ice Snow Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Immortal Gu Bearer | `Invisible to non-adjacent units <when above [0] [Green Grape Immortal Essence]> <if [Dog Shit Luck Immortal Gu] is constructed>` | 0 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Immortal Gu Bearer | `[+14]% Strength <when defending> <when above [0] [Green Grape Immortal Essence]> <if [Dog Shit Luck Immortal Gu] is constructed>` | +14, 0 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Immortal Gu Bearer | `Only available <when number of [[Dog Shit Luck Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Immortal Gu Bearer | `[This Unit] gains the [Dog Shit Luck Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Luck Inspection Gu]> <for units with [Luck Great Grandmaster]> <for units without [Dog Shit Luck Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Immortal Gu Bearer | `[This Unit] gains the [Dog Shit Luck Heaven Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Ten-Year Lifespan Gu]> <for units with [Luck Great Grandmaster]> <for units with [Heaven Grandmaster]> <for units without [Dog Shit Luck Heaven Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Immortal Gu Bearer | `[+32]% Strength <when defending> <when above [0] [Green Grape Immortal Essence]> <if [Flying Bear Phantom Immortal Gu] is constructed>` | +32, 0 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Immortal Gu Bearer | `Only available <when number of [[Flying Bear Phantom Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Immortal Gu Bearer | `[This Unit] gains the [Flying Bear Phantom Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Turn Phantom Gu]> <for units with [Phantom Great Grandmaster]> <for units without [Flying Bear Phantom Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Immortal Gu Bearer | `[This Unit] gains the [Flying Bear Phantom Restriction Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Primeval Break Gu]> <for units with [Phantom Great Grandmaster]> <for units with [Restriction Grandmaster]> <for units without [Flying Bear Phantom Restriction Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Immortal Gu Bearer | `Invisible to non-adjacent units <when above [0] [Green Grape Immortal Essence]> <if [Split Shadow Immortal Gu] is constructed>` | 0 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Immortal Gu Bearer | `[+14]% Strength <when defending> <when above [0] [Green Grape Immortal Essence]> <if [Split Shadow Immortal Gu] is constructed>` | +14, 0 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Immortal Gu Bearer | `Only available <when number of [[Split Shadow Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Immortal Gu Bearer | `[This Unit] gains the [Split Shadow Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Overlapping Shadow Gu]> <for units with [Shadow Great Grandmaster]> <for units without [Split Shadow Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Immortal Gu Bearer | `[This Unit] gains the [Split Shadow Star Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Star Dart Gu]> <for units with [Shadow Great Grandmaster]> <for units with [Star Grandmaster]> <for units without [Split Shadow Star Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Immortal Gu Bearer | `[Target Unit] takes [16] damage <upon damaging a [Military] unit> <when attacking> <when above [0] [Red Date Immortal Essence]> <if [Flying Sword Immortal Gu] is constructed>` | 16, 0 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Immortal Gu Bearer | `Only available <when number of [[Flying Sword Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Immortal Gu Bearer | `[This Unit] gains the [Sword Marks Targeting Death] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sword Qi Gu]> <for units with [Sword Great Grandmaster]> <for units without [Sword Marks Targeting Death]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Immortal Gu Bearer | `[This Unit] gains the [Flying Sword Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sword Shadow Gu]> <for units with [Sword Great Grandmaster]> <for units without [Flying Sword Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Immortal Gu Bearer | `[This Unit] gains the [Flying Sword Blade Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sole Blade Gu]> <for units with [Sword Great Grandmaster]> <for units with [Blade Grandmaster]> <for units without [Flying Sword Blade Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Immortal Gu Bearer | `[+2] Movement <when above [0] [Red Date Immortal Essence]> <if [Sword Escape Immortal Gu] is constructed>` | +2, 0 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Immortal Gu Bearer | `[+8]% Strength <when above [0] [Red Date Immortal Essence]> <if [Sword Escape Immortal Gu] is constructed>` | +8, 0 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Immortal Gu Bearer | `Only available <when number of [[Sword Escape Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Immortal Gu Bearer | `[This Unit] gains the [One Sword Unrestrained] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sword Shadow Gu]> <for units with [Sword Great Grandmaster]> <for units without [One Sword Unrestrained]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Immortal Gu Bearer | `[This Unit] gains the [Sword Escape Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sword Shadow Gu]> <for units with [Sword Great Grandmaster]> <for units without [Sword Escape Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Immortal Gu Bearer | `[This Unit] gains the [Sword Escape Blade Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sole Blade Gu]> <for units with [Sword Great Grandmaster]> <for units with [Blade Grandmaster]> <for units without [Sword Escape Blade Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Edge Immortal Gu Bearer | `[+36]% Strength <when attacking> <when above [0] [Red Date Immortal Essence]> <if [Edge Immortal Gu] is constructed>` | +36, 0 | tools/gen_ruleset.py `Promotions` |
| Edge Immortal Gu Bearer | `Only available <when number of [[Edge Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Edge Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Edge Immortal Gu Bearer | `[This Unit] gains the [Edge Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sole Blade Gu]> <for units with [Blade Great Grandmaster]> <for units without [Edge Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Edge Immortal Gu Bearer | `[This Unit] gains the [Edge Metal Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Bronze Skin Gu]> <for units with [Blade Great Grandmaster]> <for units with [Metal Grandmaster]> <for units without [Edge Metal Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Great Thief Immortal Gu Bearer | `Earn [45]% of killed [Military] unit's [Cost] as [Gold] <when above [0] [Red Date Immortal Essence]> <if [Great Thief Immortal Gu] is constructed>` | 45, 0 | tools/gen_ruleset.py `Promotions` |
| Great Thief Immortal Gu Bearer | `Only available <when number of [[Great Thief Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Great Thief Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Great Thief Immortal Gu Bearer | `[This Unit] gains the [Ghostly Concealment] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Plunder Gu]> <for units with [Theft Great Grandmaster]> <for units without [Ghostly Concealment]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Great Thief Immortal Gu Bearer | `[This Unit] gains the [Great Thief Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Plunder Gu]> <for units with [Theft Great Grandmaster]> <for units without [Great Thief Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Great Thief Immortal Gu Bearer | `[This Unit] gains the [Great Thief Refinement Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Revert Gu]> <for units with [Theft Great Grandmaster]> <for units with [Refinement Grandmaster]> <for units without [Great Thief Refinement Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Immortal Gu Bearer | `[+36]% Strength <when attacking> <when above [0] [Red Date Immortal Essence]> <if [Crescent Moon Immortal Gu] is constructed>` | +36, 0 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Immortal Gu Bearer | `Only available <when number of [[Crescent Moon Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Immortal Gu Bearer | `[This Unit] gains the [Crescent Moon Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Moonlight Gu]> <for units with [Moon Great Grandmaster]> <for units without [Crescent Moon Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Immortal Gu Bearer | `[This Unit] gains the [Crescent Moon Sound Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Heaven Earth Magnificent Sound Gu]> <for units with [Moon Great Grandmaster]> <for units with [Sound Grandmaster]> <for units without [Crescent Moon Sound Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Perseverance Immortal Gu Bearer | `[+36]% Strength <when defending> <when above [0] [Red Date Immortal Essence]> <if [Perseverance Immortal Gu] is constructed>` | +36, 0 | tools/gen_ruleset.py `Promotions` |
| Perseverance Immortal Gu Bearer | `Only available <when number of [[Perseverance Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Perseverance Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Perseverance Immortal Gu Bearer | `[This Unit] gains the [Reverse Flow Protection Seal] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Pulling Water Immortal Gu Bearer]> <for units with [Human Great Grandmaster]> <for units with [Strength Grandmaster]> <for units without [Reverse Flow Protection Seal]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Perseverance Immortal Gu Bearer | `[This Unit] gains the [Perseverance Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Relic Gu]> <for units with [Human Great Grandmaster]> <for units without [Perseverance Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Perseverance Immortal Gu Bearer | `[This Unit] gains the [Perseverance Painting Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Painting Idea Gu]> <for units with [Human Great Grandmaster]> <for units with [Painting Grandmaster]> <for units without [Perseverance Painting Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Immortal Gu Bearer | `[+2] Movement <when above [0] [Red Date Immortal Essence]> <if [Qi Escape Immortal Gu] is constructed>` | +2, 0 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Immortal Gu Bearer | `[+8]% Strength <when above [0] [Red Date Immortal Essence]> <if [Qi Escape Immortal Gu] is constructed>` | +8, 0 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Immortal Gu Bearer | `Only available <when number of [[Qi Escape Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Immortal Gu Bearer | `[This Unit] gains the [Qi Escape Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Strength Qi Gu]> <for units with [Qi Great Grandmaster]> <for units without [Qi Escape Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Immortal Gu Bearer | `[This Unit] gains the [Qi Escape Time Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Man as Before Gu]> <for units with [Qi Great Grandmaster]> <for units with [Time Grandmaster]> <for units without [Qi Escape Time Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Immortal Gu Bearer | `[-9]% Strength for enemy [Military] units in adjacent [All] tiles <when above [0] [Red Date Immortal Essence]> <if [Expend Strength Immortal Gu] is constructed>` | -9, 0 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Immortal Gu Bearer | `Only available <when number of [[Expend Strength Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Immortal Gu Bearer | `[This Unit] gains the [Expend Strength Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [White Boar Gu]> <for units with [Strength Great Grandmaster]> <for units without [Expend Strength Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Immortal Gu Bearer | `[This Unit] gains the [Expend Strength Transformation Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Strength Great Grandmaster]> <for units with [Transformation Grandmaster]> <for units without [Expend Strength Transformation Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Immortal Gu Bearer | `[Target Unit] gains the [Entangled] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking> <when above [0] [Red Date Immortal Essence]> <if [Fixed Space Immortal Gu] is constructed>` | 3, 0 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Immortal Gu Bearer | `[+9]% Strength <when attacking> <when above [0] [Red Date Immortal Essence]> <if [Fixed Space Immortal Gu] is constructed>` | +9, 0 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Immortal Gu Bearer | `Only available <when number of [[Fixed Space Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Immortal Gu Bearer | `[This Unit] gains the [Fixed Space Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Warp Gu]> <for units with [Space Great Grandmaster]> <for units without [Fixed Space Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Immortal Gu Bearer | `[This Unit] gains the [Fixed Space Rule Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Amplify Effect Gu]> <for units with [Space Great Grandmaster]> <for units with [Rule Grandmaster]> <for units without [Fixed Space Rule Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Limit Immortal Gu Bearer | `[-9]% Strength for enemy [Military] units in adjacent [All] tiles <when above [0] [Red Date Immortal Essence]> <if [Limit Immortal Gu] is constructed>` | -9, 0 | tools/gen_ruleset.py `Promotions` |
| Limit Immortal Gu Bearer | `Only available <when number of [[Limit Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Limit Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Limit Immortal Gu Bearer | `[This Unit] gains the [Limit Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Amplify Effect Gu]> <for units with [Rule Great Grandmaster]> <for units without [Limit Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Limit Immortal Gu Bearer | `[This Unit] gains the [Limit Phantom Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Turn Phantom Gu]> <for units with [Rule Great Grandmaster]> <for units with [Phantom Grandmaster]> <for units without [Limit Phantom Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Region Immortal Gu Bearer | `[-10]% Strength for enemy [Military] units in adjacent [All] tiles <when above [0] [White Lychee Immortal Essence]> <if [Region Immortal Gu] is constructed>` | -10, 0 | tools/gen_ruleset.py `Promotions` |
| Region Immortal Gu Bearer | `Only available <when number of [[Region Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Region Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Region Immortal Gu Bearer | `[This Unit] gains the [Five Restriction Profound Light Qi] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Limit Immortal Gu Bearer]> <for units with [Rule Great Grandmaster]> <for units without [Five Restriction Profound Light Qi]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Region Immortal Gu Bearer | `[This Unit] gains the [Region Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Amplify Effect Gu]> <for units with [Rule Great Grandmaster]> <for units without [Region Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Region Immortal Gu Bearer | `[This Unit] gains the [Region Phantom Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Turn Phantom Gu]> <for units with [Rule Great Grandmaster]> <for units with [Phantom Grandmaster]> <for units without [Region Phantom Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Immortal Gu Bearer | `[Target Unit] takes [18] damage <upon damaging a [Military] unit> <when attacking> <when above [0] [White Lychee Immortal Essence]> <if [Wisdom Sword Immortal Gu] is constructed>` | 18, 0 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Immortal Gu Bearer | `Only available <when number of [[Wisdom Sword Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Immortal Gu Bearer | `[This Unit] gains the [Wisdom Sword Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Clear Mind Gu]> <for units with [Wisdom Great Grandmaster]> <for units without [Wisdom Sword Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Immortal Gu Bearer | `[This Unit] gains the [Wisdom Sword Emotion Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Emotion Poetry Gu]> <for units with [Wisdom Great Grandmaster]> <for units with [Emotion Grandmaster]> <for units without [Wisdom Sword Emotion Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Regret Immortal Gu Bearer | `[Target Unit] gains the [Charmed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking> <when above [0] [White Lychee Immortal Essence]> <if [Regret Immortal Gu] is constructed>` | 3, 0 | tools/gen_ruleset.py `Promotions` |
| Regret Immortal Gu Bearer | `[+10]% Strength <when attacking> <when above [0] [White Lychee Immortal Essence]> <if [Regret Immortal Gu] is constructed>` | +10, 0 | tools/gen_ruleset.py `Promotions` |
| Regret Immortal Gu Bearer | `Only available <when number of [[Regret Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Regret Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Regret Immortal Gu Bearer | `[This Unit] gains the [Regret Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Emotion Poetry Gu]> <for units with [Emotion Great Grandmaster]> <for units without [Regret Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Regret Immortal Gu Bearer | `[This Unit] gains the [Regret Enchantment Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Estrus Gu]> <for units with [Emotion Great Grandmaster]> <for units with [Enchantment Grandmaster]> <for units without [Regret Enchantment Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Attitude Immortal Gu Bearer | `Invisible to non-adjacent units <when above [0] [White Lychee Immortal Essence]> <if [Attitude Immortal Gu] is constructed>` | 0 | tools/gen_ruleset.py `Promotions` |
| Attitude Immortal Gu Bearer | `[+18]% Strength <when defending> <when above [0] [White Lychee Immortal Essence]> <if [Attitude Immortal Gu] is constructed>` | +18, 0 | tools/gen_ruleset.py `Promotions` |
| Attitude Immortal Gu Bearer | `Only available <when number of [[Attitude Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Attitude Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Attitude Immortal Gu Bearer | `[This Unit] gains the [Attitude Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Clear Mind Gu]> <for units with [Wisdom Great Grandmaster]> <for units without [Attitude Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Attitude Immortal Gu Bearer | `[This Unit] gains the [Attitude Emotion Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Emotion Poetry Gu]> <for units with [Wisdom Great Grandmaster]> <for units with [Emotion Grandmaster]> <for units without [Attitude Emotion Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Immortal Gu Bearer | `[+40]% Strength <when attacking> <when above [0] [White Lychee Immortal Essence]> <if [Eight-Faced Prestige Wind Immortal Gu] is constructed>` | +40, 0 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Immortal Gu Bearer | `Only available <when number of [[Eight-Faced Prestige Wind Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Immortal Gu Bearer | `[This Unit] gains the [Eight Winds Dominion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Jade Wind Wheel Gu]> <for units with [Wind Great Grandmaster]> <for units without [Eight Winds Dominion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Immortal Gu Bearer | `[This Unit] gains the [Eight-Faced Prestige Wind Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Whirlwind Gu]> <for units with [Wind Great Grandmaster]> <for units without [Eight-Faced Prestige Wind Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Immortal Gu Bearer | `[This Unit] gains the [Eight-Faced Prestige Wind Cloud Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Flying Cloud Gu]> <for units with [Wind Great Grandmaster]> <for units with [Cloud Grandmaster]> <for units without [Eight-Faced Prestige Wind Cloud Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Immortal Gu Bearer | `[+28] HP when healing <when above [0] [White Lychee Immortal Essence]> <if [Water Refinement Immortal Gu] is constructed>` | +28, 0 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Immortal Gu Bearer | `Heals [21] damage if it kills a unit <when above [0] [White Lychee Immortal Essence]> <if [Water Refinement Immortal Gu] is constructed>` | 21, 0 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Immortal Gu Bearer | `Only available <when number of [[Water Refinement Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Immortal Gu Bearer | `[This Unit] gains the [Water Refinement Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Revert Gu]> <for units with [Refinement Great Grandmaster]> <for units without [Water Refinement Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Immortal Gu Bearer | `[This Unit] gains the [Water Refinement Formation Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Formation Heart Gu]> <for units with [Refinement Great Grandmaster]> <for units with [Formation Grandmaster]> <for units without [Water Refinement Formation Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Immortal Gu Bearer | `[+2] Sight <when above [0] [White Lychee Immortal Essence]> <if [Heavenly Secret Immortal Gu] is constructed>` | +2, 0 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Immortal Gu Bearer | `[+9]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Heavenly Secret Immortal Gu] is constructed>` | +9, 0 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Immortal Gu Bearer | `Only available <when number of [[Heavenly Secret Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Immortal Gu Bearer | `[This Unit] gains the [Heavenly Secret Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Ten-Year Lifespan Gu]> <for units with [Heaven Great Grandmaster]> <for units without [Heavenly Secret Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Immortal Gu Bearer | `[This Unit] gains the [Heavenly Secret Qi Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Strength Qi Gu]> <for units with [Heaven Great Grandmaster]> <for units with [Qi Grandmaster]> <for units without [Heavenly Secret Qi Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Immortal Gu Bearer | `[Target Unit] gains the [Doomed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking> <when above [0] [White Lychee Immortal Essence]> <if [Heaven's Envy Immortal Gu] is constructed>` | 3, 0 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Immortal Gu Bearer | `[+10]% Strength <when attacking> <when above [0] [White Lychee Immortal Essence]> <if [Heaven's Envy Immortal Gu] is constructed>` | +10, 0 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Immortal Gu Bearer | `Only available <when number of [[Heaven's Envy Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Immortal Gu Bearer | `[This Unit] gains the [Heaven Envies Heroic Geniuses] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Heavenly Secret Immortal Gu Bearer]> <for units with [Heaven Great Grandmaster]> <for units without [Heaven Envies Heroic Geniuses]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Immortal Gu Bearer | `[This Unit] gains the [Heaven's Envy Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Ten-Year Lifespan Gu]> <for units with [Heaven Great Grandmaster]> <for units without [Heaven's Envy Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Immortal Gu Bearer | `[This Unit] gains the [Heaven's Envy Qi Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Strength Qi Gu]> <for units with [Heaven Great Grandmaster]> <for units with [Qi Grandmaster]> <for units without [Heaven's Envy Qi Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Kill Immortal Gu Bearer | `[Target Unit] takes [18] damage <upon damaging a [Military] unit> <when attacking> <when above [0] [White Lychee Immortal Essence]> <if [Kill Immortal Gu] is constructed>` | 18, 0 | tools/gen_ruleset.py `Promotions` |
| Kill Immortal Gu Bearer | `Only available <when number of [[Kill Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Kill Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Kill Immortal Gu Bearer | `[This Unit] gains the [Kill Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Killing Intent Gu]> <for units with [Killing Great Grandmaster]> <for units without [Kill Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Kill Immortal Gu Bearer | `[This Unit] gains the [Kill Sword Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Sword Shadow Gu]> <for units with [Killing Great Grandmaster]> <for units with [Sword Grandmaster]> <for units without [Kill Sword Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Light Gu Bearer | `[+44]% Strength <when attacking> <when above [0] [Yellow Apricot Immortal Essence]> <if [Light Gu] is constructed>` | +44, 0 | tools/gen_ruleset.py `Promotions` |
| Light Gu Bearer | `Only available <when number of [[Light Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Light Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Light Gu Bearer | `[This Unit] gains the [Sun Descends] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Fire Gu Bearer]> <for units with [Light Great Grandmaster]> <for units with [Fire Grandmaster]> <for units without [Sun Descends]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Light Gu Bearer | `[This Unit] gains the [Light Resonance] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Little Light Gu]> <for units with [Light Great Grandmaster]> <for units without [Light Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Light Gu Bearer | `[This Unit] gains the [Light Dark Fusion] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Shadow Follower Gu]> <for units with [Light Great Grandmaster]> <for units with [Dark Grandmaster]> <for units without [Light Dark Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Fire Gu Bearer | `[Target Unit] takes [20] damage <upon damaging a [Military] unit> <when attacking> <when above [0] [Yellow Apricot Immortal Essence]> <if [Fire Gu] is constructed>` | 20, 0 | tools/gen_ruleset.py `Promotions` |
| Fire Gu Bearer | `Only available <when number of [[Fire Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Fire Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Fire Gu Bearer | `[This Unit] gains the [Fire Resonance] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Fiery Claw Gu]> <for units with [Fire Great Grandmaster]> <for units without [Fire Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Fire Gu Bearer | `[This Unit] gains the [Fire Water Fusion] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Water Shield Gu]> <for units with [Fire Great Grandmaster]> <for units with [Water Grandmaster]> <for units without [Fire Water Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Love Gu Bearer | `[+31] HP when healing <when above [0] [Yellow Apricot Immortal Essence]> <if [Love Gu] is constructed>` | +31, 0 | tools/gen_ruleset.py `Promotions` |
| Love Gu Bearer | `Heals [23] damage if it kills a unit <when above [0] [Yellow Apricot Immortal Essence]> <if [Love Gu] is constructed>` | 23, 0 | tools/gen_ruleset.py `Promotions` |
| Love Gu Bearer | `Only available <when number of [[Love Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Love Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Love Gu Bearer | `[This Unit] gains the [Love and Regret] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Regret Immortal Gu Bearer]> <for units with [Emotion Great Grandmaster]> <for units without [Love and Regret]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Love Gu Bearer | `[This Unit] gains the [Love Resonance] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Emotion Poetry Gu]> <for units with [Emotion Great Grandmaster]> <for units without [Love Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Love Gu Bearer | `[This Unit] gains the [Love Enchantment Fusion] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Estrus Gu]> <for units with [Emotion Great Grandmaster]> <for units with [Enchantment Grandmaster]> <for units without [Love Enchantment Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Immortal Gu Bearer | `[Target Unit] gains the [Entangled] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking> <when above [0] [Yellow Apricot Immortal Essence]> <if [Heavenly Web Immortal Gu] is constructed>` | 4, 0 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Immortal Gu Bearer | `[+11]% Strength <when attacking> <when above [0] [Yellow Apricot Immortal Essence]> <if [Heavenly Web Immortal Gu] is constructed>` | +11, 0 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Immortal Gu Bearer | `Only available <when number of [[Heavenly Web Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Immortal Gu Bearer | `[This Unit] gains the [Heavenly Net] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Fixed Space Immortal Gu Bearer]> <for units with [Heaven Great Grandmaster]> <for units with [Space Grandmaster]> <for units without [Heavenly Net]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Immortal Gu Bearer | `[This Unit] gains the [Heavenly Web Resonance] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Ten-Year Lifespan Gu]> <for units with [Heaven Great Grandmaster]> <for units without [Heavenly Web Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Immortal Gu Bearer | `[This Unit] gains the [Heavenly Web Qi Fusion] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Strength Qi Gu]> <for units with [Heaven Great Grandmaster]> <for units with [Qi Grandmaster]> <for units without [Heavenly Web Qi Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Spring Autumn Cicada] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Bearer | `Only available <when number of [[Spring Autumn Cicada Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Bearer | `[This Unit] gains the [Spring Autumn Cicada Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Man as Before Gu]> <for units with [Time Great Grandmaster]> <for units without [Spring Autumn Cicada Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Bearer | `[This Unit] gains the [Spring Autumn Cicada Space Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Warp Gu]> <for units with [Time Great Grandmaster]> <for units with [Space Grandmaster]> <for units without [Spring Autumn Cicada Space Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Fixed Immortal Travel] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Bearer | `Only available <when number of [[Fixed Immortal Travel Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Bearer | `[This Unit] gains the [Fixed Immortal Travel Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Warp Gu]> <for units with [Space Great Grandmaster]> <for units without [Fixed Immortal Travel Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Bearer | `[This Unit] gains the [Fixed Immortal Travel Rule Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Amplify Effect Gu]> <for units with [Space Great Grandmaster]> <for units with [Rule Grandmaster]> <for units without [Fixed Immortal Travel Rule Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Man as Before Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Man as Before] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Man as Before Bearer | `Only available <when number of [[Man as Before Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Man as Before Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Man as Before Bearer | `[This Unit] gains the [Man as Before Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Man as Before Gu]> <for units with [Time Great Grandmaster]> <for units without [Man as Before Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Man as Before Bearer | `[This Unit] gains the [Man as Before Space Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Warp Gu]> <for units with [Time Great Grandmaster]> <for units with [Space Grandmaster]> <for units without [Man as Before Space Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Unravel Mystery] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Bearer | `Only available <when number of [[Unravel Mystery Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Bearer | `[This Unit] gains the [Unravel Mystery Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Clear Mind Gu]> <for units with [Wisdom Great Grandmaster]> <for units without [Unravel Mystery Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Bearer | `[This Unit] gains the [Unravel Mystery Emotion Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Emotion Poetry Gu]> <for units with [Wisdom Great Grandmaster]> <for units with [Emotion Grandmaster]> <for units without [Unravel Mystery Emotion Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Connect Luck] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Bearer | `Only available <when number of [[Connect Luck Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Bearer | `[This Unit] gains the [Connect Luck Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Luck Inspection Gu]> <for units with [Luck Great Grandmaster]> <for units without [Connect Luck Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Bearer | `[This Unit] gains the [Connect Luck Heaven Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Ten-Year Lifespan Gu]> <for units with [Luck Great Grandmaster]> <for units with [Heaven Grandmaster]> <for units without [Connect Luck Heaven Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Self Strength Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Self Strength] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Self Strength Bearer | `Only available <when number of [[Self Strength Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Self Strength Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Self Strength Bearer | `[This Unit] gains the [Self Strength Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [White Boar Gu]> <for units with [Strength Great Grandmaster]> <for units without [Self Strength Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Self Strength Bearer | `[This Unit] gains the [Self Strength Transformation Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Strength Great Grandmaster]> <for units with [Transformation Grandmaster]> <for units without [Self Strength Transformation Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Woman's Heart] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Bearer | `Only available <when number of [[Woman's Heart Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Bearer | `[This Unit] gains the [Woman's Heart Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Poison Scorpion Gu]> <for units with [Poison Great Grandmaster]> <for units without [Woman's Heart Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Bearer | `[This Unit] gains the [Woman's Heart Fire Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Fiery Claw Gu]> <for units with [Poison Great Grandmaster]> <for units with [Fire Grandmaster]> <for units without [Woman's Heart Fire Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Bone Spike] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Bearer | `Only available <when number of [[Bone Spike Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Bearer | `[This Unit] gains the [Bone Spike Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Bone Spear Gu]> <for units with [Bone Great Grandmaster]> <for units without [Bone Spike Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Bearer | `[This Unit] gains the [Bone Spike Blood Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Blood Skull Gu]> <for units with [Bone Great Grandmaster]> <for units with [Blood Grandmaster]> <for units without [Bone Spike Blood Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Star Eyes] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Bearer | `Only available <when number of [[Star Eyes Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Bearer | `[This Unit] gains the [Star Eyes Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Star Dart Gu]> <for units with [Star Great Grandmaster]> <for units without [Star Eyes Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Bearer | `[This Unit] gains the [Star Eyes Moon Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Moonlight Gu]> <for units with [Star Great Grandmaster]> <for units with [Moon Grandmaster]> <for units without [Star Eyes Moon Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Bearer | `[+23]% Strength <when above [0] [Green Grape Immortal Essence]> <if [Divert Disaster] is constructed>` | +23, 0 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Bearer | `Only available <when number of [[Divert Disaster Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Bearer | `[This Unit] gains the [Divert Disaster Resonance] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Luck Inspection Gu]> <for units with [Luck Great Grandmaster]> <for units without [Divert Disaster Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Bearer | `[This Unit] gains the [Divert Disaster Heaven Fusion] status for [1] turn(s) <costs [3] [Green Grape Immortal Essence]> <requires [1] movement> <for units with [Ten-Year Lifespan Gu]> <for units with [Luck Great Grandmaster]> <for units with [Heaven Grandmaster]> <for units without [Divert Disaster Heaven Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Dragon Strength] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Bearer | `Only available <when number of [[Dragon Strength Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Bearer | `[This Unit] gains the [Dragon Strength Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [White Boar Gu]> <for units with [Strength Great Grandmaster]> <for units without [Dragon Strength Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Bearer | `[This Unit] gains the [Dragon Strength Transformation Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Strength Great Grandmaster]> <for units with [Transformation Grandmaster]> <for units without [Dragon Strength Transformation Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Year Gu Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Year Gu] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Year Gu Bearer | `Only available <when number of [[Year Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Year Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Year Gu Bearer | `[This Unit] gains the [Year Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Man as Before Gu]> <for units with [Time Great Grandmaster]> <for units without [Year Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Year Gu Bearer | `[This Unit] gains the [Year Space Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Warp Gu]> <for units with [Time Great Grandmaster]> <for units with [Space Grandmaster]> <for units without [Year Space Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Formation Flag] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Bearer | `Only available <when number of [[Formation Flag Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Bearer | `[This Unit] gains the [Formation Flag Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Formation Heart Gu]> <for units with [Formation Great Grandmaster]> <for units without [Formation Flag Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Bearer | `[This Unit] gains the [Formation Flag Food Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Liquor Worm]> <for units with [Formation Great Grandmaster]> <for units with [Food Grandmaster]> <for units without [Formation Flag Food Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Divination Tortoise Shell] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Bearer | `Only available <when number of [[Divination Tortoise Shell Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Bearer | `[This Unit] gains the [Divination Tortoise Shell Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Clear Mind Gu]> <for units with [Wisdom Great Grandmaster]> <for units without [Divination Tortoise Shell Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Bearer | `[This Unit] gains the [Divination Tortoise Shell Emotion Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Emotion Poetry Gu]> <for units with [Wisdom Great Grandmaster]> <for units with [Emotion Grandmaster]> <for units without [Divination Tortoise Shell Emotion Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Dragon Centipede] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Bearer | `Only available <when number of [[Dragon Centipede Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Bearer | `[This Unit] gains the [Dragon Centipede Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sword Shadow Gu]> <for units with [Sword Great Grandmaster]> <for units without [Dragon Centipede Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Bearer | `[This Unit] gains the [Dragon Centipede Blade Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Sole Blade Gu]> <for units with [Sword Great Grandmaster]> <for units with [Blade Grandmaster]> <for units without [Dragon Centipede Blade Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Reputation Restriction] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Bearer | `Only available <when number of [[Reputation Restriction Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Bearer | `[This Unit] gains the [Reputation Restriction Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Flying Sword Letter Gu]> <for units with [Information Great Grandmaster]> <for units without [Reputation Restriction Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Bearer | `[This Unit] gains the [Reputation Restriction Human Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Relic Gu]> <for units with [Information Great Grandmaster]> <for units with [Human Grandmaster]> <for units without [Reputation Restriction Human Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Calamity Beckoning] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Bearer | `Only available <when number of [[Calamity Beckoning Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Bearer | `[This Unit] gains the [Calamity Beckoning Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Luck Inspection Gu]> <for units with [Luck Great Grandmaster]> <for units without [Calamity Beckoning Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Bearer | `[This Unit] gains the [Calamity Beckoning Heaven Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Ten-Year Lifespan Gu]> <for units with [Luck Great Grandmaster]> <for units with [Heaven Grandmaster]> <for units without [Calamity Beckoning Heaven Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Change Soul Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Change Soul] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Change Soul Bearer | `Only available <when number of [[Change Soul Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Change Soul Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Change Soul Bearer | `[This Unit] gains the [Change Soul Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Soul Search Gu]> <for units with [Soul Great Grandmaster]> <for units without [Change Soul Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Change Soul Bearer | `[This Unit] gains the [Change Soul Dream Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Dream Pillow Gu]> <for units with [Soul Great Grandmaster]> <for units with [Dream Grandmaster]> <for units without [Change Soul Dream Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bearer | `[+26]% Strength <when above [0] [Red Date Immortal Essence]> <if [Dragon Breath] is constructed>` | +26, 0 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bearer | `Only available <when number of [[Dragon Breath Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bearer | `[This Unit] gains the [Dragon Breath Resonance] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Roaming Zombie Gu]> <for units with [Transformation Great Grandmaster]> <for units without [Dragon Breath Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bearer | `[This Unit] gains the [Dragon Breath Bone Fusion] status for [1] turn(s) <costs [3] [Red Date Immortal Essence]> <requires [1] movement> <for units with [Bone Spear Gu]> <for units with [Transformation Great Grandmaster]> <for units with [Bone Grandmaster]> <for units without [Dragon Breath Bone Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Heavenly Essence Treasure Imperial Lotus] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Bearer | `Only available <when number of [[Heavenly Essence Treasure Imperial Lotus Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Bearer | `[This Unit] gains the [Heavenly Essence Treasure Imperial Lotus Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Heavenly Essence Treasure Lotus]> <for units with [Wood Great Grandmaster]> <for units without [Heavenly Essence Treasure Imperial Lotus Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Bearer | `[This Unit] gains the [Heavenly Essence Treasure Imperial Lotus Earth Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Gruel Mud Gu]> <for units with [Wood Great Grandmaster]> <for units with [Earth Grandmaster]> <for units without [Heavenly Essence Treasure Imperial Lotus Earth Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Years Flow Like Water] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Bearer | `Only available <when number of [[Years Flow Like Water Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Bearer | `[This Unit] gains the [Years Flow Like Water Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Man as Before Gu]> <for units with [Time Great Grandmaster]> <for units without [Years Flow Like Water Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Bearer | `[This Unit] gains the [Years Flow Like Water Space Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Warp Gu]> <for units with [Time Great Grandmaster]> <for units with [Space Grandmaster]> <for units without [Years Flow Like Water Space Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dream Token Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Dream Token] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Dream Token Bearer | `Only available <when number of [[Dream Token Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Dream Token Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Dream Token Bearer | `[This Unit] gains the [Dream Token Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Dream Pillow Gu]> <for units with [Dream Great Grandmaster]> <for units without [Dream Token Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Dream Token Bearer | `[This Unit] gains the [Dream Token Enslavement Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Wolf Enslavement Gu]> <for units with [Dream Great Grandmaster]> <for units with [Enslavement Grandmaster]> <for units without [Dream Token Enslavement Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Soul Beast Token] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Bearer | `Only available <when number of [[Soul Beast Token Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Bearer | `[This Unit] gains the [Soul Beast Token Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Wolf Enslavement Gu]> <for units with [Enslavement Great Grandmaster]> <for units without [Soul Beast Token Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Bearer | `[This Unit] gains the [Soul Beast Token Wisdom Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Clear Mind Gu]> <for units with [Enslavement Great Grandmaster]> <for units with [Wisdom Grandmaster]> <for units without [Soul Beast Token Wisdom Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Gu Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Treasure Light Gu] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Gu Bearer | `Only available <when number of [[Treasure Light Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Gu Bearer | `[This Unit] gains the [Treasure Light Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Little Light Gu]> <for units with [Light Great Grandmaster]> <for units without [Treasure Light Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Gu Bearer | `[This Unit] gains the [Treasure Light Dark Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Shadow Follower Gu]> <for units with [Light Great Grandmaster]> <for units with [Dark Grandmaster]> <for units without [Treasure Light Dark Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Gu Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Advance Refinement Gu] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Gu Bearer | `Only available <when number of [[Advance Refinement Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Gu Bearer | `[This Unit] gains the [Advance Refinement Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Revert Gu]> <for units with [Refinement Great Grandmaster]> <for units without [Advance Refinement Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Gu Bearer | `[This Unit] gains the [Advance Refinement Formation Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Formation Heart Gu]> <for units with [Refinement Great Grandmaster]> <for units with [Formation Grandmaster]> <for units without [Advance Refinement Formation Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Steal Life Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Steal Life] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Steal Life Bearer | `Only available <when number of [[Steal Life Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Steal Life Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Steal Life Bearer | `[This Unit] gains the [Steal Life Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Plunder Gu]> <for units with [Theft Great Grandmaster]> <for units without [Steal Life Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Steal Life Bearer | `[This Unit] gains the [Steal Life Refinement Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Revert Gu]> <for units with [Theft Great Grandmaster]> <for units with [Refinement Grandmaster]> <for units without [Steal Life Refinement Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Human Qi Immortal Gu Bearer | `[+29]% Strength <when above [0] [White Lychee Immortal Essence]> <if [Human Qi Immortal Gu] is constructed>` | +29, 0 | tools/gen_ruleset.py `Promotions` |
| Human Qi Immortal Gu Bearer | `Only available <when number of [[Human Qi Immortal Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Human Qi Immortal Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Human Qi Immortal Gu Bearer | `[This Unit] gains the [Human Qi Resonance] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Strength Qi Gu]> <for units with [Qi Great Grandmaster]> <for units without [Human Qi Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Human Qi Immortal Gu Bearer | `[This Unit] gains the [Human Qi Time Fusion] status for [1] turn(s) <costs [3] [White Lychee Immortal Essence]> <requires [1] movement> <for units with [Man as Before Gu]> <for units with [Qi Great Grandmaster]> <for units with [Time Grandmaster]> <for units without [Human Qi Time Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Wisdom Gu Bearer | `[+32]% Strength <when above [0] [Yellow Apricot Immortal Essence]> <if [Wisdom Gu] is constructed>` | +32, 0 | tools/gen_ruleset.py `Promotions` |
| Wisdom Gu Bearer | `Only available <when number of [[Wisdom Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Wisdom Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Wisdom Gu Bearer | `[This Unit] gains the [Wisdom Resonance] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Clear Mind Gu]> <for units with [Wisdom Great Grandmaster]> <for units without [Wisdom Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Wisdom Gu Bearer | `[This Unit] gains the [Wisdom Emotion Fusion] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Emotion Poetry Gu]> <for units with [Wisdom Great Grandmaster]> <for units with [Emotion Grandmaster]> <for units without [Wisdom Emotion Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Derivation Gu Bearer | `[+32]% Strength <when above [0] [Yellow Apricot Immortal Essence]> <if [Derivation Gu] is constructed>` | +32, 0 | tools/gen_ruleset.py `Promotions` |
| Derivation Gu Bearer | `Only available <when number of [[Derivation Gu Bearer] Units] is less than [1]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Derivation Gu Bearer | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Promotions` |
| Derivation Gu Bearer | `[This Unit] gains the [Derivation Resonance] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Amplify Effect Gu]> <for units with [Rule Great Grandmaster]> <for units without [Derivation Resonance]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
| Derivation Gu Bearer | `[This Unit] gains the [Derivation Phantom Fusion] status for [1] turn(s) <costs [3] [Yellow Apricot Immortal Essence]> <requires [1] movement> <for units with [Turn Phantom Gu]> <for units with [Rule Great Grandmaster]> <for units with [Phantom Grandmaster]> <for units without [Derivation Phantom Fusion]>` | 1, 3, 1 | tools/gen_ruleset.py `Promotions` |
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
| Lower Grade Blessed Land | `Instantly consumes [1] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 1 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `Instantly consumes [1] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 1 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `Gain [2] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `Instantly provides [1] [Immortal Materials] <upon turn start> <for units without [Ravaged Land]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [9] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 9 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [14] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 14 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [21] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 21 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [42] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 42 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [20] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [30] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [45] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Promotions` |
| Lower Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Instantly provides [2] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units>` | 2 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Instantly provides [2] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units>` | 2 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Instantly consumes [2] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 2 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Instantly consumes [2] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 2 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Gain [4] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 4 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `Instantly provides [1] [Immortal Materials] <upon turn start> <for units without [Ravaged Land]>` | 1 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [9] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 9 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [13] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 13 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [20] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [39] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 39 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [20] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [30] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [45] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Promotions` |
| Middle Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Instantly provides [3] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units>` | 3 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Instantly provides [3] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units>` | 3 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Instantly consumes [3] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 3 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Instantly consumes [3] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 3 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Gain [6] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 6 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `Instantly provides [2] [Immortal Materials] <upon turn start> <for units without [Ravaged Land]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [8] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 8 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [12] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 12 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [18] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 18 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [36] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 36 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [20] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [30] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [45] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Promotions` |
| Upper Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Instantly provides [5] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units>` | 5 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Instantly provides [5] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units>` | 5 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Instantly consumes [5] [Green Grape Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Six Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 5 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Instantly consumes [5] [Red Date Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Rank Seven Gu Immortal] units> <for [Zombie Alliance] Civilizations>` | 5 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Gain [10] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 10 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `Instantly provides [2] [Immortal Materials] <upon turn start> <for units without [Ravaged Land]>` | 2 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [7] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Quick] game speed>` | 7 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [11] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Standard] game speed>` | 11 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [16] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Epic] game speed>` | 16 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Calamity Countdown] status for [33] turn(s) <upon turn start> <for units without [Calamity Countdown]> <on [Marathon] game speed>` | 33 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [40] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [60] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [180] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Six Gu Immortal] units> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [20] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Quick] game speed>` | 20 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [30] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Standard] game speed>` | 30 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [45] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Epic] game speed>` | 45 | tools/gen_ruleset.py `Promotions` |
| Super Grade Blessed Land | `[This Unit] gains the [Tribulation Countdown] status for [90] turn(s) <upon turn start> <for units without [Tribulation Countdown]> <for [Rank Seven Gu Immortal] units> <on [Marathon] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Middle Stage | `[+5]% Strength` | +5 | tools/gen_ruleset.py `Promotions` |
| Upper Stage | `[+5]% Strength` | +5 | tools/gen_ruleset.py `Promotions` |
| Peak Stage | `[+5]% Strength` | +5 | tools/gen_ruleset.py `Promotions` |
| Green Copper Relic Gu | `Unavailable <when below [25] [Gold]>` | 25 | tools/gen_ruleset.py `Promotions` |
| Green Copper Relic Gu | `Gain [-25] [Gold]` | -25 | tools/gen_ruleset.py `Promotions` |
| Green Copper Relic Gu | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Promotions` |
| Red Iron Relic Gu | `Unavailable <when below [40] [Gold]>` | 40 | tools/gen_ruleset.py `Promotions` |
| Red Iron Relic Gu | `Gain [-40] [Gold]` | -40 | tools/gen_ruleset.py `Promotions` |
| Red Iron Relic Gu | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Promotions` |
| White Silver Relic Gu | `Unavailable <when below [60] [Gold]>` | 60 | tools/gen_ruleset.py `Promotions` |
| White Silver Relic Gu | `Gain [-60] [Gold]` | -60 | tools/gen_ruleset.py `Promotions` |
| White Silver Relic Gu | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Promotions` |
| Yellow Gold Relic Gu | `Unavailable <when below [90] [Gold]>` | 90 | tools/gen_ruleset.py `Promotions` |
| Yellow Gold Relic Gu | `Gain [-90] [Gold]` | -90 | tools/gen_ruleset.py `Promotions` |
| Yellow Gold Relic Gu | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Promotions` |
| Purple Crystal Relic Gu | `Unavailable <when below [130] [Gold]>` | 130 | tools/gen_ruleset.py `Promotions` |
| Purple Crystal Relic Gu | `Gain [-130] [Gold]` | -130 | tools/gen_ruleset.py `Promotions` |
| Purple Crystal Relic Gu | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Promotions` |
| Extreme Physique | `[+20]% Strength` | +20 | tools/gen_ruleset.py `Promotions` |
| Extreme Physique | `[+50]% XP gained from combat` | +50 | tools/gen_ruleset.py `Promotions` |
| Extreme Physique | `[-20]% maintenance costs` | -20 | tools/gen_ruleset.py `Promotions` |
| Dao Marks I | `[+10]% Strength` | +10 | tools/gen_ruleset.py `Promotions` |
| Dao Marks II | `[+20]% Strength` | +20 | tools/gen_ruleset.py `Promotions` |
| Dao Marks III | `[+30]% Strength` | +30 | tools/gen_ruleset.py `Promotions` |
| Dao Marks IV | `[+40]% Strength` | +40 | tools/gen_ruleset.py `Promotions` |
| Dao Marks IV | `[+10] HP when healing` | +10 | tools/gen_ruleset.py `Promotions` |
| Dao Marks V | `[+55]% Strength` | +55 | tools/gen_ruleset.py `Promotions` |
| Dao Marks V | `[+15] HP when healing` | +15 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `Instantly provides [3] [White Lychee Immortal Essence] <upon turn start> <for units without [Ravaged Land]>` | 3 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `Instantly consumes [3] [White Lychee Immortal Essence] <upon turn start> <for units without [Ravaged Land]> <for [Zombie Alliance] Civilizations>` | 3 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `Gain [12] [Gold] <upon turn start> <for units without [Ravaged Land]>` | 12 | tools/gen_ruleset.py `Promotions` |
| Grotto-Heaven Aperture | `Instantly provides [3] [Immortal Materials] <upon turn start> <for units without [Ravaged Land]>` | 3 | tools/gen_ruleset.py `Promotions` |
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
| Advance to Rank Seven | `Instantly provides [25] [Lifespan Gu]` | 25 | tools/gen_ruleset.py `Promotions` |
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
| Advance to Rank Eight | `Instantly provides [35] [Lifespan Gu]` | 35 | tools/gen_ruleset.py `Promotions` |
| Advance to Rank Eight | `[+200]% weight to this choice for AI decisions` | +200 | tools/gen_ruleset.py `Promotions` |
| Venerable Killer Move | `[+100]% Strength` | +100 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Unavailable <when below [201] [Yellow Apricot Immortal Essence]> <on [Quick] game speed>` | 201 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Unavailable <when below [300] [Yellow Apricot Immortal Essence]> <on [Standard] game speed>` | 300 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Unavailable <when below [450] [Yellow Apricot Immortal Essence]> <on [Epic] game speed>` | 450 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Unavailable <when below [900] [Yellow Apricot Immortal Essence]> <on [Marathon] game speed>` | 900 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Instantly consumes [201] [Yellow Apricot Immortal Essence] <on [Quick] game speed>` | 201 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Instantly consumes [300] [Yellow Apricot Immortal Essence] <on [Standard] game speed>` | 300 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Instantly consumes [450] [Yellow Apricot Immortal Essence] <on [Epic] game speed>` | 450 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `Instantly consumes [900] [Yellow Apricot Immortal Essence] <on [Marathon] game speed>` | 900 | tools/gen_ruleset.py `Promotions` |
| Seek Eternal Life | `[+1000]% weight to this choice for AI decisions` | +1000 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Unavailable <when below [40] [White Lychee Immortal Essence]> <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Unavailable <when below [60] [White Lychee Immortal Essence]> <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Unavailable <when below [90] [White Lychee Immortal Essence]> <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Unavailable <when below [180] [White Lychee Immortal Essence]> <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Instantly consumes [40] [White Lychee Immortal Essence] <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Instantly consumes [60] [White Lychee Immortal Essence] <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Instantly consumes [90] [White Lychee Immortal Essence] <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Instantly consumes [180] [White Lychee Immortal Essence] <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `Instantly provides [60] [Lifespan Gu]` | 60 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `[This Unit] gains the [Advancing] status for [1] turn(s)` | 1 | tools/gen_ruleset.py `Promotions` |
| Ascend to Venerable | `[+500]% weight to this choice for AI decisions` | +500 | tools/gen_ruleset.py `Promotions` |
| Soul Tempered | `[+15]% XP gained from combat` | +15 | tools/gen_ruleset.py `Promotions` |
| Soul Loosened | `[+10]% Strength` | +10 | tools/gen_ruleset.py `Promotions` |
| Reverse Flow Seal | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Promotions` |
| Time Touched | `[+10]% Strength` | +10 | tools/gen_ruleset.py `Promotions` |
| Life and Death Glimpse | `[+10] HP when healing` | +10 | tools/gen_ruleset.py `Promotions` |
| Ink Wisdom | `[+20]% XP gained from combat` | +20 | tools/gen_ruleset.py `Promotions` |
| Demon Sound Steeled | `[+15]% Strength <when attacking>` | +15 | tools/gen_ruleset.py `Promotions` |
| Whale Blessing | `[+10] HP when healing` | +10 | tools/gen_ruleset.py `Promotions` |
| Heavenly Stair | `[1] Sight` | 1 | tools/gen_ruleset.py `Promotions` |
| Lang Ya Craft | `[+10]% Strength` | +10 | tools/gen_ruleset.py `Promotions` |
| Imperial Shelter | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Promotions` |
| Fox Spirit Favor | `[1] Movement` | 1 | tools/gen_ruleset.py `Promotions` |
| Four Arm Earth King | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Four Arm Earth King | `[Target Unit] takes [19] damage <upon damaging a [Military] unit> <when attacking>` | 19 | tools/gen_ruleset.py `Promotions` |
| Four Arm Earth King | `[+15]% Strength <for units with [Strength Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Eight Beast Phantoms | `[+22]% Strength <when attacking>` | +22 | tools/gen_ruleset.py `Promotions` |
| Eight Beast Phantoms | `[Target Unit] takes [13] damage <upon damaging a [Military] unit> <when attacking>` | 13 | tools/gen_ruleset.py `Promotions` |
| Eight Beast Phantoms | `[+11]% Strength <for units with [Strength Supreme Grandmaster]>` | +11 | tools/gen_ruleset.py `Promotions` |
| Reverse Flow Protection Seal | `[+50]% Strength <when defending>` | +50 | tools/gen_ruleset.py `Promotions` |
| Reverse Flow Protection Seal | `[This Unit] heals [26] HP <upon gaining the [Reverse Flow Protection Seal] status>` | 26 | tools/gen_ruleset.py `Promotions` |
| Reverse Flow Protection Seal | `[+19]% Strength <for units with [Human Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Spiral Drill Star Spear | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Spiral Drill Star Spear | `[Target Unit] takes [19] damage <upon damaging a [Military] unit> <when attacking>` | 19 | tools/gen_ruleset.py `Promotions` |
| Spiral Drill Star Spear | `[+15]% Strength <for units with [Bone Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Myriad Star Fireflies | `[-14]% Strength for enemy [Military] units in adjacent [All] tiles` | -14 | tools/gen_ruleset.py `Promotions` |
| Myriad Star Fireflies | `[+13]% Strength` | +13 | tools/gen_ruleset.py `Promotions` |
| Myriad Star Fireflies | `[+13]% Strength <for units with [Star Supreme Grandmaster]>` | +13 | tools/gen_ruleset.py `Promotions` |
| Blood Torrent | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Blood Torrent | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Blood Torrent | `[+17]% Strength <for units with [Blood Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Blood Healing Lake | `[This Unit] heals [45] HP <upon gaining the [Blood Healing Lake] status>` | 45 | tools/gen_ruleset.py `Promotions` |
| Blood Healing Lake | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Blood Healing Lake | `[+17]% Strength <for units with [Blood Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Sword Marks Targeting Death | `[Target Unit] gains the [Doomed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Sword Marks Targeting Death | `[+27]% Strength <when attacking>` | +27 | tools/gen_ruleset.py `Promotions` |
| Sword Marks Targeting Death | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| One Sword Unrestrained | `[This Unit] gains [2] movement <upon gaining the [One Sword Unrestrained] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| One Sword Unrestrained | `[+29]% Strength <when attacking>` | +29 | tools/gen_ruleset.py `Promotions` |
| One Sword Unrestrained | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Transformation | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Transformation | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Transformation | `[+17]% Strength <for units with [Transformation Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Ghost Official Garment | `[+45]% Strength <when defending>` | +45 | tools/gen_ruleset.py `Promotions` |
| Ghost Official Garment | `[This Unit] heals [23] HP <upon gaining the [Ghost Official Garment] status>` | 23 | tools/gen_ruleset.py `Promotions` |
| Ghost Official Garment | `[+17]% Strength <for units with [Soul Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Ghostly Concealment | `Earn [55]% of killed [Military] unit's [Cost] as [Gold]` | 55 | tools/gen_ruleset.py `Promotions` |
| Ghostly Concealment | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Ghostly Concealment | `[+19]% Strength <for units with [Theft Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Five Restriction Profound Light Qi | `[Target Unit] gains the [Sealed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Five Restriction Profound Light Qi | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Five Restriction Profound Light Qi | `[+21]% Strength <for units with [Rule Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Limitless Search Lock | `[Target Unit] gains the [Entangled] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Limitless Search Lock | `[+21]% Strength <when attacking>` | +21 | tools/gen_ruleset.py `Promotions` |
| Limitless Search Lock | `[+15]% Strength <for units with [Space Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Ice Blade Storm | `[+18]% Strength <when attacking>` | +18 | tools/gen_ruleset.py `Promotions` |
| Ice Blade Storm | `[Target Unit] takes [10] damage <upon damaging a [Military] unit> <when attacking>` | 10 | tools/gen_ruleset.py `Promotions` |
| Ice Blade Storm | `[+9]% Strength <for units with [Ice Snow Supreme Grandmaster]>` | +9 | tools/gen_ruleset.py `Promotions` |
| Heaven Envies Heroic Geniuses | `[-22]% Strength for enemy [Military] units in adjacent [All] tiles` | -22 | tools/gen_ruleset.py `Promotions` |
| Heaven Envies Heroic Geniuses | `[+21]% Strength` | +21 | tools/gen_ruleset.py `Promotions` |
| Heaven Envies Heroic Geniuses | `[+21]% Strength <for units with [Heaven Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| My Glorious Spear | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| My Glorious Spear | `[Target Unit] takes [19] damage <upon damaging a [Military] unit> <when attacking>` | 19 | tools/gen_ruleset.py `Promotions` |
| My Glorious Spear | `[+15]% Strength <for units with [Light Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Nine Cloud Ring | `[+35]% Strength <when defending>` | +35 | tools/gen_ruleset.py `Promotions` |
| Nine Cloud Ring | `[This Unit] heals [17] HP <upon gaining the [Nine Cloud Ring] status>` | 17 | tools/gen_ruleset.py `Promotions` |
| Nine Cloud Ring | `[+13]% Strength <for units with [Cloud Supreme Grandmaster]>` | +13 | tools/gen_ruleset.py `Promotions` |
| Six Arm Heavenly Corpse King | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Six Arm Heavenly Corpse King | `[Target Unit] takes [19] damage <upon damaging a [Military] unit> <when attacking>` | 19 | tools/gen_ruleset.py `Promotions` |
| Six Arm Heavenly Corpse King | `[+15]% Strength <for units with [Transformation Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Unravel Dream | `[+55]% XP gained from combat` | +55 | tools/gen_ruleset.py `Promotions` |
| Unravel Dream | `[This Unit] heals [15] HP <upon gaining the [Unravel Dream] status>` | 15 | tools/gen_ruleset.py `Promotions` |
| Unravel Dream | `[+15]% Strength <for units with [Dream Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| One Song of Yang Pass | `[-16]% Strength for enemy [Military] units in adjacent [All] tiles` | -16 | tools/gen_ruleset.py `Promotions` |
| One Song of Yang Pass | `[+15]% Strength` | +15 | tools/gen_ruleset.py `Promotions` |
| One Song of Yang Pass | `[+15]% Strength <for units with [Sound Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Splendid Star Armour | `[+30]% Strength <when defending>` | +30 | tools/gen_ruleset.py `Promotions` |
| Splendid Star Armour | `[This Unit] heals [14] HP <upon gaining the [Splendid Star Armour] status>` | 14 | tools/gen_ruleset.py `Promotions` |
| Splendid Star Armour | `[+11]% Strength <for units with [Star Supreme Grandmaster]>` | +11 | tools/gen_ruleset.py `Promotions` |
| Bleeding Moon | `[Target Unit] gains the [Bleeding] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Bleeding Moon | `[+15]% Strength <when attacking>` | +15 | tools/gen_ruleset.py `Promotions` |
| Bleeding Moon | `[+11]% Strength <for units with [Moon Supreme Grandmaster]>` | +11 | tools/gen_ruleset.py `Promotions` |
| Ice Coffin Prison | `[Target Unit] gains the [Frozen] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Ice Coffin Prison | `[+15]% Strength <when attacking>` | +15 | tools/gen_ruleset.py `Promotions` |
| Ice Coffin Prison | `[+11]% Strength <for units with [Ice Snow Supreme Grandmaster]>` | +11 | tools/gen_ruleset.py `Promotions` |
| Thunder Wing Dive | `[This Unit] gains [2] movement <upon gaining the [Thunder Wing Dive] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Thunder Wing Dive | `[+23]% Strength <when attacking>` | +23 | tools/gen_ruleset.py `Promotions` |
| Thunder Wing Dive | `[+15]% Strength <for units with [Lightning Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Molten Serpent Coil | `[Target Unit] gains the [Burning] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Molten Serpent Coil | `[+18]% Strength <when attacking>` | +18 | tools/gen_ruleset.py `Promotions` |
| Molten Serpent Coil | `[+13]% Strength <for units with [Fire Supreme Grandmaster]>` | +13 | tools/gen_ruleset.py `Promotions` |
| Ten Thousand Poisons | `[Target Unit] gains the [Poisoned] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Ten Thousand Poisons | `[+21]% Strength <when attacking>` | +21 | tools/gen_ruleset.py `Promotions` |
| Ten Thousand Poisons | `[+15]% Strength <for units with [Poison Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Bone Spear Rain | `[+26]% Strength <when attacking>` | +26 | tools/gen_ruleset.py `Promotions` |
| Bone Spear Rain | `[Target Unit] takes [16] damage <upon damaging a [Military] unit> <when attacking>` | 16 | tools/gen_ruleset.py `Promotions` |
| Bone Spear Rain | `[+13]% Strength <for units with [Bone Supreme Grandmaster]>` | +13 | tools/gen_ruleset.py `Promotions` |
| Iron Stone Bastion | `[+20]% Strength <when defending>` | +20 | tools/gen_ruleset.py `Promotions` |
| Iron Stone Bastion | `[This Unit] heals [8] HP <upon gaining the [Iron Stone Bastion] status>` | 8 | tools/gen_ruleset.py `Promotions` |
| Iron Stone Bastion | `[+7]% Strength <for units with [Metal Supreme Grandmaster]>` | +7 | tools/gen_ruleset.py `Promotions` |
| Golden Saw Tide | `[+22]% Strength <when attacking>` | +22 | tools/gen_ruleset.py `Promotions` |
| Golden Saw Tide | `[Target Unit] takes [13] damage <upon damaging a [Military] unit> <when attacking>` | 13 | tools/gen_ruleset.py `Promotions` |
| Golden Saw Tide | `[+11]% Strength <for units with [Metal Supreme Grandmaster]>` | +11 | tools/gen_ruleset.py `Promotions` |
| Twin Wheel Gale | `[This Unit] gains [2] movement <upon gaining the [Twin Wheel Gale] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Twin Wheel Gale | `[+14]% Strength <when attacking>` | +14 | tools/gen_ruleset.py `Promotions` |
| Twin Wheel Gale | `[+9]% Strength <for units with [Wind Supreme Grandmaster]>` | +9 | tools/gen_ruleset.py `Promotions` |
| Grass Army Ambush | `[-14]% Strength for enemy [Military] units in adjacent [All] tiles` | -14 | tools/gen_ruleset.py `Promotions` |
| Grass Army Ambush | `[+13]% Strength` | +13 | tools/gen_ruleset.py `Promotions` |
| Grass Army Ambush | `[+13]% Strength <for units with [Enslavement Supreme Grandmaster]>` | +13 | tools/gen_ruleset.py `Promotions` |
| Earth Listening Ambush | `[+18]% Strength <when attacking>` | +18 | tools/gen_ruleset.py `Promotions` |
| Earth Listening Ambush | `[Target Unit] takes [10] damage <upon damaging a [Military] unit> <when attacking>` | 10 | tools/gen_ruleset.py `Promotions` |
| Earth Listening Ambush | `[+9]% Strength <for units with [Earth Supreme Grandmaster]>` | +9 | tools/gen_ruleset.py `Promotions` |
| Soul Fire Burst | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Soul Fire Burst | `[Target Unit] takes [19] damage <upon damaging a [Military] unit> <when attacking>` | 19 | tools/gen_ruleset.py `Promotions` |
| Soul Fire Burst | `[+15]% Strength <for units with [Soul Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Blinding Palm | `[Target Unit] gains the [Blinded] status for [2] turn(s) <upon damaging a [Military] unit> <when attacking>` | 2 | tools/gen_ruleset.py `Promotions` |
| Blinding Palm | `[+15]% Strength <when attacking>` | +15 | tools/gen_ruleset.py `Promotions` |
| Blinding Palm | `[+11]% Strength <for units with [Light Supreme Grandmaster]>` | +11 | tools/gen_ruleset.py `Promotions` |
| Sealed Moonshadow | `[Target Unit] gains the [Sealed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Sealed Moonshadow | `[+21]% Strength <when attacking>` | +21 | tools/gen_ruleset.py `Promotions` |
| Sealed Moonshadow | `[+15]% Strength <for units with [Moon Supreme Grandmaster]>` | +15 | tools/gen_ruleset.py `Promotions` |
| Silent Gong | `[-18]% Strength for enemy [Military] units in adjacent [All] tiles` | -18 | tools/gen_ruleset.py `Promotions` |
| Silent Gong | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Silent Gong | `[+17]% Strength <for units with [Sound Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Rain | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Rain | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Rain | `[+17]% Strength <for units with [Dark Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Eight Winds Dominion | `[-22]% Strength for enemy [Military] units in adjacent [All] tiles` | -22 | tools/gen_ruleset.py `Promotions` |
| Eight Winds Dominion | `[+21]% Strength` | +21 | tools/gen_ruleset.py `Promotions` |
| Eight Winds Dominion | `[+21]% Strength <for units with [Wind Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Sun Descends | `[+46]% Strength <when attacking>` | +46 | tools/gen_ruleset.py `Promotions` |
| Sun Descends | `[Target Unit] takes [31] damage <upon damaging a [Military] unit> <when attacking>` | 31 | tools/gen_ruleset.py `Promotions` |
| Sun Descends | `[+23]% Strength <for units with [Light Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Heavenly Net | `[Target Unit] gains the [Entangled] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Heavenly Net | `[+33]% Strength <when attacking>` | +33 | tools/gen_ruleset.py `Promotions` |
| Heavenly Net | `[+23]% Strength <for units with [Heaven Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Love and Regret | `[Target Unit] gains the [Charmed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Love and Regret | `[+33]% Strength <when attacking>` | +33 | tools/gen_ruleset.py `Promotions` |
| Love and Regret | `[+23]% Strength <for units with [Emotion Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Star Mark Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Star Mark Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Star Mark Resonance | `[+17]% Strength <for units with [Star Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Star Mark Moon Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Star Mark Moon Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Star Mark Moon Fusion | `[+17]% Strength <for units with [Star Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Resonance | `[+45]% Strength <when defending>` | +45 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Resonance | `[This Unit] heals [23] HP <upon gaining the [Pulling Water Resonance] status>` | 23 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Resonance | `[+17]% Strength <for units with [Strength Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Transformation Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Transformation Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Pulling Water Transformation Fusion | `[+17]% Strength <for units with [Strength Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Snack Resonance | `[+60]% XP gained from combat` | +60 | tools/gen_ruleset.py `Promotions` |
| Snack Resonance | `[This Unit] heals [17] HP <upon gaining the [Snack Resonance] status>` | 17 | tools/gen_ruleset.py `Promotions` |
| Snack Resonance | `[+17]% Strength <for units with [Food Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Snack Pill Fusion | `[This Unit] heals [45] HP <upon gaining the [Snack Pill Fusion] status>` | 45 | tools/gen_ruleset.py `Promotions` |
| Snack Pill Fusion | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Snack Pill Fusion | `[+17]% Strength <for units with [Food Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Resonance | `[+17]% Strength <for units with [Strength Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Transformation Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Transformation Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Strength Transformation Fusion | `[+17]% Strength <for units with [Strength Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Change Form Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Change Form Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Change Form Resonance | `[+17]% Strength <for units with [Transformation Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Change Form Bone Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Change Form Bone Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Change Form Bone Fusion | `[+17]% Strength <for units with [Transformation Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Resonance | `[+17]% Strength <for units with [Blood Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Strength Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Strength Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Blood Asset Strength Fusion | `[+17]% Strength <for units with [Blood Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Resonance | `[This Unit] heals [45] HP <upon gaining the [Cleanse Soul Resonance] status>` | 45 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Resonance | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Resonance | `[+17]% Strength <for units with [Soul Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Dream Fusion | `[+60]% XP gained from combat` | +60 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Dream Fusion | `[This Unit] heals [17] HP <upon gaining the [Cleanse Soul Dream Fusion] status>` | 17 | tools/gen_ruleset.py `Promotions` |
| Cleanse Soul Dream Fusion | `[+17]% Strength <for units with [Soul Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Resonance | `[+17]% Strength <for units with [Dark Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Shadow Fusion | `[+45]% Strength <when defending>` | +45 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Shadow Fusion | `[This Unit] heals [23] HP <upon gaining the [Dark Arrow Shadow Fusion] status>` | 23 | tools/gen_ruleset.py `Promotions` |
| Dark Arrow Shadow Fusion | `[+17]% Strength <for units with [Dark Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Resonance | `[-18]% Strength for enemy [Military] units in adjacent [All] tiles` | -18 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Resonance | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Resonance | `[+17]% Strength <for units with [Sound Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Illusion Fusion | `[+45]% Strength <when defending>` | +45 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Illusion Fusion | `[This Unit] heals [23] HP <upon gaining the [Heavenly Gong Illusion Fusion] status>` | 23 | tools/gen_ruleset.py `Promotions` |
| Heavenly Gong Illusion Fusion | `[+17]% Strength <for units with [Sound Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Resonance | `[Target Unit] gains the [Frozen] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Resonance | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Resonance | `[+17]% Strength <for units with [Ice Snow Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Lightning Fusion | `[Target Unit] gains the [Shocked] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Lightning Fusion | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Ice Soul Lightning Fusion | `[+17]% Strength <for units with [Ice Snow Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Resonance | `[This Unit] gains [2] movement <upon gaining the [Rising Azure Cloud Resonance] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Resonance | `[+26]% Strength <when attacking>` | +26 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Resonance | `[+17]% Strength <for units with [Cloud Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Ice Snow Fusion | `[Target Unit] gains the [Frozen] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Ice Snow Fusion | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Rising Azure Cloud Ice Snow Fusion | `[+17]% Strength <for units with [Cloud Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Resonance | `[+45]% Strength <when defending>` | +45 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Resonance | `[This Unit] heals [23] HP <upon gaining the [Dog Shit Luck Resonance] status>` | 23 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Resonance | `[+17]% Strength <for units with [Luck Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Heaven Fusion | `[-18]% Strength for enemy [Military] units in adjacent [All] tiles` | -18 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Heaven Fusion | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Dog Shit Luck Heaven Fusion | `[+17]% Strength <for units with [Luck Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Resonance | `[+45]% Strength <when defending>` | +45 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Resonance | `[This Unit] heals [23] HP <upon gaining the [Flying Bear Phantom Resonance] status>` | 23 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Resonance | `[+17]% Strength <for units with [Phantom Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Restriction Fusion | `[Target Unit] gains the [Sealed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Restriction Fusion | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Flying Bear Phantom Restriction Fusion | `[+17]% Strength <for units with [Phantom Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Resonance | `[+45]% Strength <when defending>` | +45 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Resonance | `[This Unit] heals [23] HP <upon gaining the [Split Shadow Resonance] status>` | 23 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Resonance | `[+17]% Strength <for units with [Shadow Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Star Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Star Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Split Shadow Star Fusion | `[+17]% Strength <for units with [Shadow Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Resonance | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Blade Fusion | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Blade Fusion | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Flying Sword Blade Fusion | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Resonance | `[This Unit] gains [2] movement <upon gaining the [Sword Escape Resonance] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Resonance | `[+29]% Strength <when attacking>` | +29 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Resonance | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Blade Fusion | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Blade Fusion | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Sword Escape Blade Fusion | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Edge Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Edge Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Edge Resonance | `[+19]% Strength <for units with [Blade Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Edge Metal Fusion | `[+50]% Strength <when defending>` | +50 | tools/gen_ruleset.py `Promotions` |
| Edge Metal Fusion | `[This Unit] heals [26] HP <upon gaining the [Edge Metal Fusion] status>` | 26 | tools/gen_ruleset.py `Promotions` |
| Edge Metal Fusion | `[+19]% Strength <for units with [Blade Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Great Thief Resonance | `Earn [55]% of killed [Military] unit's [Cost] as [Gold]` | 55 | tools/gen_ruleset.py `Promotions` |
| Great Thief Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Great Thief Resonance | `[+19]% Strength <for units with [Theft Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Great Thief Refinement Fusion | `[This Unit] heals [50] HP <upon gaining the [Great Thief Refinement Fusion] status>` | 50 | tools/gen_ruleset.py `Promotions` |
| Great Thief Refinement Fusion | `[+19]% Strength` | +19 | tools/gen_ruleset.py `Promotions` |
| Great Thief Refinement Fusion | `[+19]% Strength <for units with [Theft Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Resonance | `[+19]% Strength <for units with [Moon Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Sound Fusion | `[Target Unit] gains the [Dazed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Sound Fusion | `[+27]% Strength <when attacking>` | +27 | tools/gen_ruleset.py `Promotions` |
| Crescent Moon Sound Fusion | `[+19]% Strength <for units with [Moon Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Perseverance Resonance | `[+50]% Strength <when defending>` | +50 | tools/gen_ruleset.py `Promotions` |
| Perseverance Resonance | `[This Unit] heals [26] HP <upon gaining the [Perseverance Resonance] status>` | 26 | tools/gen_ruleset.py `Promotions` |
| Perseverance Resonance | `[+19]% Strength <for units with [Human Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Perseverance Painting Fusion | `[-20]% Strength for enemy [Military] units in adjacent [All] tiles` | -20 | tools/gen_ruleset.py `Promotions` |
| Perseverance Painting Fusion | `[+19]% Strength` | +19 | tools/gen_ruleset.py `Promotions` |
| Perseverance Painting Fusion | `[+19]% Strength <for units with [Human Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Resonance | `[This Unit] gains [2] movement <upon gaining the [Qi Escape Resonance] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Resonance | `[+29]% Strength <when attacking>` | +29 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Resonance | `[+19]% Strength <for units with [Qi Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Time Fusion | `[Target Unit] gains the [Aged] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Time Fusion | `[+27]% Strength <when attacking>` | +27 | tools/gen_ruleset.py `Promotions` |
| Qi Escape Time Fusion | `[+19]% Strength <for units with [Qi Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Resonance | `[-20]% Strength for enemy [Military] units in adjacent [All] tiles` | -20 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Resonance | `[+19]% Strength` | +19 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Resonance | `[+19]% Strength <for units with [Strength Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Transformation Fusion | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Transformation Fusion | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Expend Strength Transformation Fusion | `[+19]% Strength <for units with [Strength Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Resonance | `[Target Unit] gains the [Entangled] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Resonance | `[+27]% Strength <when attacking>` | +27 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Resonance | `[+19]% Strength <for units with [Space Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Rule Fusion | `[Target Unit] gains the [Sealed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Rule Fusion | `[+27]% Strength <when attacking>` | +27 | tools/gen_ruleset.py `Promotions` |
| Fixed Space Rule Fusion | `[+19]% Strength <for units with [Space Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Limit Resonance | `[-20]% Strength for enemy [Military] units in adjacent [All] tiles` | -20 | tools/gen_ruleset.py `Promotions` |
| Limit Resonance | `[+19]% Strength` | +19 | tools/gen_ruleset.py `Promotions` |
| Limit Resonance | `[+19]% Strength <for units with [Rule Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Limit Phantom Fusion | `[+50]% Strength <when defending>` | +50 | tools/gen_ruleset.py `Promotions` |
| Limit Phantom Fusion | `[This Unit] heals [26] HP <upon gaining the [Limit Phantom Fusion] status>` | 26 | tools/gen_ruleset.py `Promotions` |
| Limit Phantom Fusion | `[+19]% Strength <for units with [Rule Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Region Resonance | `[-22]% Strength for enemy [Military] units in adjacent [All] tiles` | -22 | tools/gen_ruleset.py `Promotions` |
| Region Resonance | `[+21]% Strength` | +21 | tools/gen_ruleset.py `Promotions` |
| Region Resonance | `[+21]% Strength <for units with [Rule Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Region Phantom Fusion | `[+55]% Strength <when defending>` | +55 | tools/gen_ruleset.py `Promotions` |
| Region Phantom Fusion | `[This Unit] heals [29] HP <upon gaining the [Region Phantom Fusion] status>` | 29 | tools/gen_ruleset.py `Promotions` |
| Region Phantom Fusion | `[+21]% Strength <for units with [Rule Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Resonance | `[+21]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Emotion Fusion | `[Target Unit] gains the [Charmed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Emotion Fusion | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Wisdom Sword Emotion Fusion | `[+21]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Regret Resonance | `[Target Unit] gains the [Charmed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Regret Resonance | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Regret Resonance | `[+21]% Strength <for units with [Emotion Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Regret Enchantment Fusion | `[Target Unit] gains the [Charmed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Regret Enchantment Fusion | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Regret Enchantment Fusion | `[+21]% Strength <for units with [Emotion Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Attitude Resonance | `[+55]% Strength <when defending>` | +55 | tools/gen_ruleset.py `Promotions` |
| Attitude Resonance | `[This Unit] heals [29] HP <upon gaining the [Attitude Resonance] status>` | 29 | tools/gen_ruleset.py `Promotions` |
| Attitude Resonance | `[+21]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Attitude Emotion Fusion | `[Target Unit] gains the [Charmed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Attitude Emotion Fusion | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Attitude Emotion Fusion | `[+21]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Resonance | `[+21]% Strength <for units with [Wind Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Cloud Fusion | `[Target Unit] gains the [Blinded] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Cloud Fusion | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Eight-Faced Prestige Wind Cloud Fusion | `[+21]% Strength <for units with [Wind Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Resonance | `[This Unit] heals [55] HP <upon gaining the [Water Refinement Resonance] status>` | 55 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Resonance | `[+21]% Strength` | +21 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Resonance | `[+21]% Strength <for units with [Refinement Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Formation Fusion | `[+55]% Strength <when defending>` | +55 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Formation Fusion | `[This Unit] heals [29] HP <upon gaining the [Water Refinement Formation Fusion] status>` | 29 | tools/gen_ruleset.py `Promotions` |
| Water Refinement Formation Fusion | `[+21]% Strength <for units with [Refinement Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Resonance | `[+70]% XP gained from combat` | +70 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Resonance | `[This Unit] heals [21] HP <upon gaining the [Heavenly Secret Resonance] status>` | 21 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Resonance | `[+21]% Strength <for units with [Heaven Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Qi Fusion | `[+55]% Strength <when defending>` | +55 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Qi Fusion | `[This Unit] heals [29] HP <upon gaining the [Heavenly Secret Qi Fusion] status>` | 29 | tools/gen_ruleset.py `Promotions` |
| Heavenly Secret Qi Fusion | `[+21]% Strength <for units with [Heaven Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Resonance | `[Target Unit] gains the [Doomed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Resonance | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Resonance | `[+21]% Strength <for units with [Heaven Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Qi Fusion | `[+55]% Strength <when defending>` | +55 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Qi Fusion | `[This Unit] heals [29] HP <upon gaining the [Heaven's Envy Qi Fusion] status>` | 29 | tools/gen_ruleset.py `Promotions` |
| Heaven's Envy Qi Fusion | `[+21]% Strength <for units with [Heaven Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Kill Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Kill Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Kill Resonance | `[+21]% Strength <for units with [Killing Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Kill Sword Fusion | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Kill Sword Fusion | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Kill Sword Fusion | `[+21]% Strength <for units with [Killing Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Light Resonance | `[+46]% Strength <when attacking>` | +46 | tools/gen_ruleset.py `Promotions` |
| Light Resonance | `[Target Unit] takes [31] damage <upon damaging a [Military] unit> <when attacking>` | 31 | tools/gen_ruleset.py `Promotions` |
| Light Resonance | `[+23]% Strength <for units with [Light Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Light Dark Fusion | `[-24]% Strength for enemy [Military] units in adjacent [All] tiles` | -24 | tools/gen_ruleset.py `Promotions` |
| Light Dark Fusion | `[+23]% Strength` | +23 | tools/gen_ruleset.py `Promotions` |
| Light Dark Fusion | `[+23]% Strength <for units with [Light Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Fire Resonance | `[+46]% Strength <when attacking>` | +46 | tools/gen_ruleset.py `Promotions` |
| Fire Resonance | `[Target Unit] takes [31] damage <upon damaging a [Military] unit> <when attacking>` | 31 | tools/gen_ruleset.py `Promotions` |
| Fire Resonance | `[+23]% Strength <for units with [Fire Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Fire Water Fusion | `[Target Unit] gains the [Entangled] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Fire Water Fusion | `[+33]% Strength <when attacking>` | +33 | tools/gen_ruleset.py `Promotions` |
| Fire Water Fusion | `[+23]% Strength <for units with [Fire Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Love Resonance | `[This Unit] heals [60] HP <upon gaining the [Love Resonance] status>` | 60 | tools/gen_ruleset.py `Promotions` |
| Love Resonance | `[+23]% Strength` | +23 | tools/gen_ruleset.py `Promotions` |
| Love Resonance | `[+23]% Strength <for units with [Emotion Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Love Enchantment Fusion | `[Target Unit] gains the [Charmed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Love Enchantment Fusion | `[+33]% Strength <when attacking>` | +33 | tools/gen_ruleset.py `Promotions` |
| Love Enchantment Fusion | `[+23]% Strength <for units with [Emotion Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Resonance | `[Target Unit] gains the [Entangled] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Resonance | `[+33]% Strength <when attacking>` | +33 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Resonance | `[+23]% Strength <for units with [Heaven Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Qi Fusion | `[+60]% Strength <when defending>` | +60 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Qi Fusion | `[This Unit] heals [32] HP <upon gaining the [Heavenly Web Qi Fusion] status>` | 32 | tools/gen_ruleset.py `Promotions` |
| Heavenly Web Qi Fusion | `[+23]% Strength <for units with [Heaven Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Resonance | `[+17]% Strength <for units with [Time Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Space Fusion | `[This Unit] gains [2] movement <upon gaining the [Spring Autumn Cicada Space Fusion] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Space Fusion | `[+26]% Strength <when attacking>` | +26 | tools/gen_ruleset.py `Promotions` |
| Spring Autumn Cicada Space Fusion | `[+17]% Strength <for units with [Time Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Resonance | `[+17]% Strength <for units with [Space Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Rule Fusion | `[Target Unit] gains the [Sealed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Rule Fusion | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Fixed Immortal Travel Rule Fusion | `[+17]% Strength <for units with [Space Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Man as Before Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Man as Before Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Man as Before Resonance | `[+17]% Strength <for units with [Time Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Man as Before Space Fusion | `[This Unit] gains [2] movement <upon gaining the [Man as Before Space Fusion] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Man as Before Space Fusion | `[+26]% Strength <when attacking>` | +26 | tools/gen_ruleset.py `Promotions` |
| Man as Before Space Fusion | `[+17]% Strength <for units with [Time Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Resonance | `[+17]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Emotion Fusion | `[Target Unit] gains the [Charmed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Emotion Fusion | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Unravel Mystery Emotion Fusion | `[+17]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Resonance | `[+17]% Strength <for units with [Luck Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Heaven Fusion | `[-18]% Strength for enemy [Military] units in adjacent [All] tiles` | -18 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Heaven Fusion | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Connect Luck Heaven Fusion | `[+17]% Strength <for units with [Luck Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Self Strength Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Self Strength Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Self Strength Resonance | `[+17]% Strength <for units with [Strength Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Self Strength Transformation Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Self Strength Transformation Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Self Strength Transformation Fusion | `[+17]% Strength <for units with [Strength Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Resonance | `[+17]% Strength <for units with [Poison Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Fire Fusion | `[Target Unit] gains the [Burning] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Fire Fusion | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Woman's Heart Fire Fusion | `[+17]% Strength <for units with [Poison Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Resonance | `[+17]% Strength <for units with [Bone Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Blood Fusion | `[Target Unit] gains the [Bleeding] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Blood Fusion | `[+24]% Strength <when attacking>` | +24 | tools/gen_ruleset.py `Promotions` |
| Bone Spike Blood Fusion | `[+17]% Strength <for units with [Bone Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Resonance | `[+17]% Strength <for units with [Star Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Moon Fusion | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Moon Fusion | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Star Eyes Moon Fusion | `[+17]% Strength <for units with [Star Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Resonance | `[+34]% Strength <when attacking>` | +34 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Resonance | `[Target Unit] takes [22] damage <upon damaging a [Military] unit> <when attacking>` | 22 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Resonance | `[+17]% Strength <for units with [Luck Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Heaven Fusion | `[-18]% Strength for enemy [Military] units in adjacent [All] tiles` | -18 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Heaven Fusion | `[+17]% Strength` | +17 | tools/gen_ruleset.py `Promotions` |
| Divert Disaster Heaven Fusion | `[+17]% Strength <for units with [Luck Supreme Grandmaster]>` | +17 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Resonance | `[+19]% Strength <for units with [Strength Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Transformation Fusion | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Transformation Fusion | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Dragon Strength Transformation Fusion | `[+19]% Strength <for units with [Strength Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Year Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Year Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Year Resonance | `[+19]% Strength <for units with [Time Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Year Space Fusion | `[This Unit] gains [2] movement <upon gaining the [Year Space Fusion] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Year Space Fusion | `[+29]% Strength <when attacking>` | +29 | tools/gen_ruleset.py `Promotions` |
| Year Space Fusion | `[+19]% Strength <for units with [Time Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Resonance | `[+19]% Strength <for units with [Formation Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Food Fusion | `[This Unit] heals [50] HP <upon gaining the [Formation Flag Food Fusion] status>` | 50 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Food Fusion | `[+19]% Strength` | +19 | tools/gen_ruleset.py `Promotions` |
| Formation Flag Food Fusion | `[+19]% Strength <for units with [Formation Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Resonance | `[+19]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Emotion Fusion | `[Target Unit] gains the [Charmed] status for [3] turn(s) <upon damaging a [Military] unit> <when attacking>` | 3 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Emotion Fusion | `[+27]% Strength <when attacking>` | +27 | tools/gen_ruleset.py `Promotions` |
| Divination Tortoise Shell Emotion Fusion | `[+19]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Resonance | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Blade Fusion | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Blade Fusion | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Dragon Centipede Blade Fusion | `[+19]% Strength <for units with [Sword Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Resonance | `[+19]% Strength <for units with [Information Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Human Fusion | `[+50]% Strength <when defending>` | +50 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Human Fusion | `[This Unit] heals [26] HP <upon gaining the [Reputation Restriction Human Fusion] status>` | 26 | tools/gen_ruleset.py `Promotions` |
| Reputation Restriction Human Fusion | `[+19]% Strength <for units with [Information Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Resonance | `[+19]% Strength <for units with [Luck Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Heaven Fusion | `[-20]% Strength for enemy [Military] units in adjacent [All] tiles` | -20 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Heaven Fusion | `[+19]% Strength` | +19 | tools/gen_ruleset.py `Promotions` |
| Calamity Beckoning Heaven Fusion | `[+19]% Strength <for units with [Luck Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Change Soul Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Change Soul Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Change Soul Resonance | `[+19]% Strength <for units with [Soul Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Change Soul Dream Fusion | `[+65]% XP gained from combat` | +65 | tools/gen_ruleset.py `Promotions` |
| Change Soul Dream Fusion | `[This Unit] heals [19] HP <upon gaining the [Change Soul Dream Fusion] status>` | 19 | tools/gen_ruleset.py `Promotions` |
| Change Soul Dream Fusion | `[+19]% Strength <for units with [Soul Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Resonance | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Resonance | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Resonance | `[+19]% Strength <for units with [Transformation Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bone Fusion | `[+38]% Strength <when attacking>` | +38 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bone Fusion | `[Target Unit] takes [25] damage <upon damaging a [Military] unit> <when attacking>` | 25 | tools/gen_ruleset.py `Promotions` |
| Dragon Breath Bone Fusion | `[+19]% Strength <for units with [Transformation Supreme Grandmaster]>` | +19 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Resonance | `[+21]% Strength <for units with [Wood Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Earth Fusion | `[Target Unit] gains the [Weighted] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Earth Fusion | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Heavenly Essence Treasure Imperial Lotus Earth Fusion | `[+21]% Strength <for units with [Wood Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Resonance | `[+21]% Strength <for units with [Time Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Space Fusion | `[This Unit] gains [2] movement <upon gaining the [Years Flow Like Water Space Fusion] status>` | 2 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Space Fusion | `[+32]% Strength <when attacking>` | +32 | tools/gen_ruleset.py `Promotions` |
| Years Flow Like Water Space Fusion | `[+21]% Strength <for units with [Time Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Dream Token Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Dream Token Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Dream Token Resonance | `[+21]% Strength <for units with [Dream Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Dream Token Enslavement Fusion | `[-22]% Strength for enemy [Military] units in adjacent [All] tiles` | -22 | tools/gen_ruleset.py `Promotions` |
| Dream Token Enslavement Fusion | `[+21]% Strength` | +21 | tools/gen_ruleset.py `Promotions` |
| Dream Token Enslavement Fusion | `[+21]% Strength <for units with [Dream Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Resonance | `[+21]% Strength <for units with [Enslavement Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Wisdom Fusion | `[Target Unit] gains the [Shaken] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Wisdom Fusion | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Soul Beast Token Wisdom Fusion | `[+21]% Strength <for units with [Enslavement Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Resonance | `[+21]% Strength <for units with [Light Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Dark Fusion | `[-22]% Strength for enemy [Military] units in adjacent [All] tiles` | -22 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Dark Fusion | `[+21]% Strength` | +21 | tools/gen_ruleset.py `Promotions` |
| Treasure Light Dark Fusion | `[+21]% Strength <for units with [Light Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Resonance | `[+21]% Strength <for units with [Refinement Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Formation Fusion | `[+55]% Strength <when defending>` | +55 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Formation Fusion | `[This Unit] heals [29] HP <upon gaining the [Advance Refinement Formation Fusion] status>` | 29 | tools/gen_ruleset.py `Promotions` |
| Advance Refinement Formation Fusion | `[+21]% Strength <for units with [Refinement Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Steal Life Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Steal Life Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Steal Life Resonance | `[+21]% Strength <for units with [Theft Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Steal Life Refinement Fusion | `[This Unit] heals [55] HP <upon gaining the [Steal Life Refinement Fusion] status>` | 55 | tools/gen_ruleset.py `Promotions` |
| Steal Life Refinement Fusion | `[+21]% Strength` | +21 | tools/gen_ruleset.py `Promotions` |
| Steal Life Refinement Fusion | `[+21]% Strength <for units with [Theft Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Human Qi Resonance | `[+42]% Strength <when attacking>` | +42 | tools/gen_ruleset.py `Promotions` |
| Human Qi Resonance | `[Target Unit] takes [28] damage <upon damaging a [Military] unit> <when attacking>` | 28 | tools/gen_ruleset.py `Promotions` |
| Human Qi Resonance | `[+21]% Strength <for units with [Qi Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Human Qi Time Fusion | `[Target Unit] gains the [Aged] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Human Qi Time Fusion | `[+30]% Strength <when attacking>` | +30 | tools/gen_ruleset.py `Promotions` |
| Human Qi Time Fusion | `[+21]% Strength <for units with [Qi Supreme Grandmaster]>` | +21 | tools/gen_ruleset.py `Promotions` |
| Wisdom Resonance | `[+46]% Strength <when attacking>` | +46 | tools/gen_ruleset.py `Promotions` |
| Wisdom Resonance | `[Target Unit] takes [31] damage <upon damaging a [Military] unit> <when attacking>` | 31 | tools/gen_ruleset.py `Promotions` |
| Wisdom Resonance | `[+23]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Wisdom Emotion Fusion | `[Target Unit] gains the [Charmed] status for [4] turn(s) <upon damaging a [Military] unit> <when attacking>` | 4 | tools/gen_ruleset.py `Promotions` |
| Wisdom Emotion Fusion | `[+33]% Strength <when attacking>` | +33 | tools/gen_ruleset.py `Promotions` |
| Wisdom Emotion Fusion | `[+23]% Strength <for units with [Wisdom Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Derivation Resonance | `[+46]% Strength <when attacking>` | +46 | tools/gen_ruleset.py `Promotions` |
| Derivation Resonance | `[Target Unit] takes [31] damage <upon damaging a [Military] unit> <when attacking>` | 31 | tools/gen_ruleset.py `Promotions` |
| Derivation Resonance | `[+23]% Strength <for units with [Rule Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |
| Derivation Phantom Fusion | `[+60]% Strength <when defending>` | +60 | tools/gen_ruleset.py `Promotions` |
| Derivation Phantom Fusion | `[This Unit] heals [32] HP <upon gaining the [Derivation Phantom Fusion] status>` | 32 | tools/gen_ruleset.py `Promotions` |
| Derivation Phantom Fusion | `[+23]% Strength <for units with [Rule Supreme Grandmaster]>` | +23 | tools/gen_ruleset.py `Promotions` |

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
| Aptitude Awakening › One of the ten extreme physiques | `[This Unit] gains the [Doomed Aperture] status for [40] turn(s) <on [Quick] game speed>` | 40 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › One of the ten extreme physiques | `[This Unit] gains the [Doomed Aperture] status for [60] turn(s) <on [Standard] game speed>` | 60 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › One of the ten extreme physiques | `[This Unit] gains the [Doomed Aperture] status for [90] turn(s) <on [Epic] game speed>` | 90 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › One of the ten extreme physiques | `[This Unit] gains the [Doomed Aperture] status for [180] turn(s) <on [Marathon] game speed>` | 180 | tools/gen_ruleset.py `Events` |
| Aptitude Awakening › One of the ten extreme physiques | `[-99]% weight to this choice for AI decisions` | -99 | tools/gen_ruleset.py `Events` |
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
| Ascension Trial › A lower-grade blessed land opens | `Instantly provides [20] [Lifespan Gu]` | 20 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `Instantly provides [20] [Lifespan Gu]` | 20 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A middle-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +0 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `Instantly provides [20] [Lifespan Gu]` | 20 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `[-75]% weight to this choice for AI decisions` | -75 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `[+100]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +100 | tools/gen_ruleset.py `Events` |
| Ascension Trial › An upper-grade blessed land opens | `[-50]% weight to this choice for AI decisions <for units with [Aptitude D]>` | -50 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `Instantly provides [20] [Lifespan Gu]` | 20 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `[-96]% weight to this choice for AI decisions` | -96 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `[+150]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +150 | tools/gen_ruleset.py `Events` |
| Ascension Trial › A super-grade blessed land opens | `[-100]% weight to this choice for AI decisions <for units with [Aptitude D]>` | -100 | tools/gen_ruleset.py `Events` |
| Ascension Trial › The aperture collapses | `[-50]% weight to this choice for AI decisions` | -50 | tools/gen_ruleset.py `Events` |
| Ascension Trial › The aperture collapses | `[-50]% weight to this choice for AI decisions <for units with [Aptitude A]>` | -50 | tools/gen_ruleset.py `Events` |
| Ascension Trial › The aperture collapses | `[+100]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +100 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `Instantly provides [20] [Lifespan Gu]` | 20 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude A]>` | +0 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A lower-grade blessed land opens | `[+0]% weight to this choice for AI decisions <for units with [Aptitude D]>` | +0 | tools/gen_ruleset.py `Events` |
| Hasty Ascension Trial › A middle-grade blessed land opens | `Instantly provides [20] [Lifespan Gu]` | 20 | tools/gen_ruleset.py `Events` |
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
| Earthly Calamity › Pour essence into the land | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Unavailable <when below [10] [Red Date Immortal Essence]>` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Instantly consumes [10] [Red Date Immortal Essence]` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[This Unit] takes [15] damage` | 15 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Unavailable <when below [10] [White Lychee Immortal Essence]>` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `Instantly consumes [10] [White Lychee Immortal Essence]` | 10 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[This Unit] takes [15] damage` | 15 | tools/gen_ruleset.py `Events` |
| Earthly Calamity › Pour essence into the land | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
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
| Heavenly Tribulation › Pour essence into the land | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Unavailable <when below [50] [Red Date Immortal Essence]>` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Instantly consumes [50] [Red Date Immortal Essence]` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[This Unit] takes [50] damage` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Unavailable <when below [50] [White Lychee Immortal Essence]>` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `Instantly consumes [50] [White Lychee Immortal Essence]` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[This Unit] takes [50] damage` | 50 | tools/gen_ruleset.py `Events` |
| Heavenly Tribulation › Pour essence into the land | `[-60]% weight to this choice for AI decisions` | -60 | tools/gen_ruleset.py `Events` |
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
| Imperial Court Contest › Our Gu Masters take the court | `Gain [60] [Gold]` | 60 | tools/gen_ruleset.py `Events` |
| Imperial Court Contest › Our Gu Masters take the court | `New [Gu Master] units start with [15] XP [in all cities] <for [5] turns>` | 15, 5 | tools/gen_ruleset.py `Events` |
| Imperial Court Contest › Our Gu Masters take the court | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Imperial Court Contest › Our Gu Masters take the court | `[+200]% weight to this choice for AI decisions <when number of [[Military] Units] is more than [8]>` | +200, 8 | tools/gen_ruleset.py `Events` |
| Imperial Court Contest › Another tribe takes the court, and the blizzard falls on our camps | `[-50]% growth [in all cities] <for [10] turns>` | -50, 10 | tools/gen_ruleset.py `Events` |
| Imperial Court Contest › Another tribe takes the court, and the blizzard falls on our camps | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Fate Hunt › Go to ground in the Yellow Springs Sea | `[-25]% Strength <for [10] turns>` | -25, 10 | tools/gen_ruleset.py `Events` |
| Fate Hunt › Go to ground in the Yellow Springs Sea | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Fate Hunt › Pay informants to lose the trail | `Unavailable <when below [120] [Gold]>` | 120 | tools/gen_ruleset.py `Events` |
| Fate Hunt › Pay informants to lose the trail | `Gain [-120] [Gold]` | -120 | tools/gen_ruleset.py `Events` |
| Fate Hunt › Pay informants to lose the trail | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Send our best refiners to compete | `Unavailable <when below [150] [Gold]>` | 150 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Send our best refiners to compete | `Gain [-150] [Gold]` | -150 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Send our best refiners to compete | `Instantly provides [20] [Immortal Materials]` | 20 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Send our best refiners to compete | `[+33]% Production when constructing [Immortal Gu] wonders [in all cities] <for [20] turns>` | +33, 20 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Send our best refiners to compete | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Send our best refiners to compete | `[+100]% weight to this choice for AI decisions <when above [400] [Gold]>` | +100, 400 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Trade for materials at the fair | `Unavailable <when below [60] [Gold]>` | 60 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Trade for materials at the fair | `Gain [-60] [Gold]` | -60 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Trade for materials at the fair | `Instantly provides [8] [Immortal Materials]` | 8 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Trade for materials at the fair | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Refinement Conference › Stay home | `[-50]% weight to this choice for AI decisions` | -50 | tools/gen_ruleset.py `Events` |
| Wan Coalition › Pay the families to go home | `Unavailable <when below [200] [Gold]>` | 200 | tools/gen_ruleset.py `Events` |
| Wan Coalition › Pay the families to go home | `Gain [-200] [Gold]` | -200 | tools/gen_ruleset.py `Events` |
| Wan Coalition › Pay the families to go home | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Wan Coalition › Meet the coalition in the sand | `[2] [Rank Five Gu Master]s rebel` | 2 | tools/gen_ruleset.py `Events` |
| Wan Coalition › Meet the coalition in the sand | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Lie low | `[-20]% Strength <for [10] turns>` | -20, 10 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Lie low | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Pay heaven its due | `Unavailable <when below [30] [Green Grape Immortal Essence]>` | 30 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Pay heaven its due | `Instantly consumes [30] [Green Grape Immortal Essence]` | 30 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Pay heaven its due | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Defy heaven | `[2] [Bold Lightning Wolf]s rebel` | 2 | tools/gen_ruleset.py `Events` |
| Heaven's Will › Defy heaven | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Venerable Falls › Guard the true inheritance | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Dream Realm › Enter the dream | `[+50]% XP gained from combat <for [10] turns>` | +50, 10 | tools/gen_ruleset.py `Events` |
| Dream Realm › Enter the dream | `[-10]% Strength <for [10] turns>` | -10, 10 | tools/gen_ruleset.py `Events` |
| Dream Realm › Enter the dream | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Dream Realm › Leave it to fade | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Demonic Raid › Meet them in battle | `[2] [Demonic Gu Master]s rebel <before discovering [Purple Crystal Essence]>` | 2 | tools/gen_ruleset.py `Events` |
| Demonic Raid › Meet them in battle | `[2] [Demonic Gu Master]s rebel <after discovering [Purple Crystal Essence]>` | 2 | tools/gen_ruleset.py `Events` |
| Demonic Raid › Meet them in battle | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Demonic Raid › Pay them off | `Unavailable <when below [80] [Gold]>` | 80 | tools/gen_ruleset.py `Events` |
| Demonic Raid › Pay them off | `Gain [-80] [Gold]` | -80 | tools/gen_ruleset.py `Events` |
| Demonic Raid › Pay them off | `[-30]% weight to this choice for AI decisions` | -30 | tools/gen_ruleset.py `Events` |
| Wandering Gu Master › Hire him | `Unavailable <when below [60] [Gold]>` | 60 | tools/gen_ruleset.py `Events` |
| Wandering Gu Master › Hire him | `Gain [-60] [Gold]` | -60 | tools/gen_ruleset.py `Events` |
| Wandering Gu Master › Hire him | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Wandering Gu Master › Send him on his way | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Wandering Gu Master › Rob him | `Gain [40] [Gold]` | 40 | tools/gen_ruleset.py `Events` |
| Wandering Gu Master › Rob him | `[-20]% weight to this choice for AI decisions` | -20 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Accept their help | `Instantly provides [30] [Green Grape Immortal Essence]` | 30 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Accept their help | `Triggers a [Collusion Exposed] event <after adopting [Righteous Path]> <with [50]% chance>` | 50 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Accept their help | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Turn them away | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Hunt the envoy | `Unavailable <when below [100] [Gold]>` | 100 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Hunt the envoy | `Gain [-100] [Gold]` | -100 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Hunt the envoy | `[+15]% Strength <for [10] turns>` | +15, 10 | tools/gen_ruleset.py `Events` |
| Shadow Sect Envoy › Hunt the envoy | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Send tribute | `Unavailable <when below [150] [Gold]>` | 150 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Send tribute | `Gain [-150] [Gold]` | -150 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Send tribute | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Hide the clan's Gu | `[-25]% [Production] [in all cities] <for [8] turns>` | -25, 8 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Hide the clan's Gu | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Defy the Venerable | `Only available <when number of [[Population] in [in capital] Cities] is more than [3]>` | 3 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Defy the Venerable | `[-2] population [in capital]` | -2 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Defy the Venerable | `[+20]% Strength <for [10] turns>` | +20, 10 | tools/gen_ruleset.py `Events` |
| Venerable's Shadow › Defy the Venerable | `[-40]% weight to this choice for AI decisions` | -40 | tools/gen_ruleset.py `Events` |
| Chaos Calamity › Pour yellow apricot essence | `Unavailable <when below [40] [Yellow Apricot Immortal Essence]>` | 40 | tools/gen_ruleset.py `Events` |
| Chaos Calamity › Pour yellow apricot essence | `Instantly consumes [40] [Yellow Apricot Immortal Essence]` | 40 | tools/gen_ruleset.py `Events` |
| Chaos Calamity › Pour yellow apricot essence | `[This Unit] takes [10] damage` | 10 | tools/gen_ruleset.py `Events` |
| Chaos Calamity › Pour yellow apricot essence | `[+100]% weight to this choice for AI decisions` | +100 | tools/gen_ruleset.py `Events` |
| Chaos Calamity › Endure it | `[This Unit] takes [25] damage` | 25 | tools/gen_ruleset.py `Events` |
| Chaos Calamity › Endure it | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Fate War › Shatter Fate Gu | `[+20]% Strength <for [20] turns>` | +20, 20 | tools/gen_ruleset.py `Events` |
| Fate War › Shatter Fate Gu | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
| Fate War › Seize Fate Gu | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Qi Tides › Shelter the cities | `[-25]% [Production] [in all cities] <for [5] turns>` | -25, 5 | tools/gen_ruleset.py `Events` |
| Qi Tides › Shelter the cities | `[+0]% weight to this choice for AI decisions` | +0 | tools/gen_ruleset.py `Events` |
| Qi Tides › Ride the tide | `Instantly provides [10] [Heaven Qi]` | 10 | tools/gen_ruleset.py `Events` |
| Qi Tides › Ride the tide | `Instantly provides [10] [Earth Qi]` | 10 | tools/gen_ruleset.py `Events` |
| Qi Tides › Ride the tide | `[-20]% Strength <for [5] turns>` | -20, 5 | tools/gen_ruleset.py `Events` |
| Qi Tides › Ride the tide | `[+50]% weight to this choice for AI decisions` | +50 | tools/gen_ruleset.py `Events` |
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
| Inheritance Trial › 88 True Yang Building: the trial is passed | `[-90]% weight to this choice for AI decisions` | -90 | tools/gen_ruleset.py `Events` |
| Inheritance Trial › 88 True Yang Building: the trial is passed | `[+300]% weight to this choice for AI decisions <when number of [[Luck Master] Units] is more than [0]>` | +300, 0 | tools/gen_ruleset.py `Events` |
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
| Treasure Yellow Heaven › Sell immortal materials | `Unavailable <when below [50] [Immortal Materials]>` | 50 | tools/gen_ruleset.py `Events` |
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
| Tavern | happiness | 2 | tools/gen_ruleset.py `Buildings` |
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
| Spring Autumn Cicada | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Spring Autumn Cicada | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | `Costs [40] [Green Grape Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | `[+1] Movement <for [post-[Rank Five era]] units>` | +1 | tools/gen_ruleset.py `Buildings` |
| Fixed Immortal Travel | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Man as Before | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Man as Before | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Man as Before | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Man as Before | `[+20] HP when healing <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Man as Before | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | `[+15]% [Science] [in all cities]` | +15 | tools/gen_ruleset.py `Buildings` |
| Unravel Mystery | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | `[+10]% Strength <for [post-[Rank Five era]] units>` | +10 | tools/gen_ruleset.py `Buildings` |
| Connect Luck | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Self Strength | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Self Strength | `Costs [40] [Green Grape Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Self Strength | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Self Strength | `[+15]% Strength <for units with [Strength Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| Self Strength | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | `[+20]% Strength <vs [Wounded] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Woman's Heart | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | cost | 330 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | `[+20]% Strength <when defending> <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Bone Spike | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | cost | 300 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | `Costs [30] [Green Grape Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | `[+2] Sight <for [post-[Rank Five era]] units>` | +2 | tools/gen_ruleset.py `Buildings` |
| Star Eyes | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Divert Disaster | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Divert Disaster | `Costs [40] [Green Grape Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Divert Disaster | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Divert Disaster | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | `Costs [40] [Red Date Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | `[+20]% Strength <for units with [Strength Master]>` | +20 | tools/gen_ruleset.py `Buildings` |
| Dragon Strength | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Year Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Year Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Year Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Year Gu | `Instantly provides [1] [Lifespan Gu] <upon turn start> <every [3] turns>` | 1, 3 | tools/gen_ruleset.py `Buildings` |
| Year Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | `[+15]% Strength <when adjacent to a [Military] unit> <for [Military] units>` | +15 | tools/gen_ruleset.py `Buildings` |
| Formation Flag | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Buildings` |
| Divination Tortoise Shell | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | `[+30]% Strength <vs [Beast] units>` | +30 | tools/gen_ruleset.py `Buildings` |
| Dragon Centipede | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | `Costs [30] [Red Date Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | `Earn [20]% of killed [Beast] unit's [Cost] as [Immortal Materials]` | 20 | tools/gen_ruleset.py `Buildings` |
| Reputation Restriction | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Calamity Beckoning | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Calamity Beckoning | `Costs [30] [Red Date Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Calamity Beckoning | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Calamity Beckoning | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Change Soul | cost | 360 | tools/gen_ruleset.py `Buildings` |
| Change Soul | `Costs [30] [Red Date Immortal Essence]` | 30 | tools/gen_ruleset.py `Buildings` |
| Change Soul | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Change Soul | `[+20]% XP gained from combat <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Change Soul | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | `[+20]% Strength <when attacking> <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Dragon Breath | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | cost | 480 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `Costs [40] [White Lychee Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `Instantly provides [1] [White Lychee Immortal Essence] <upon turn start>` | 1 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `Instantly provides [2] [Green Grape Immortal Essence] <upon turn start>` | 2 | tools/gen_ruleset.py `Buildings` |
| Heavenly Essence Treasure Imperial Lotus | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | cost | 440 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `Costs [40] [White Lychee Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `Instantly provides [2] [Lifespan Gu] <upon turn start> <every [5] turns> <when above [9] [Green Grape Immortal Essence]>` | 2, 5, 9 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `Instantly consumes [10] [Green Grape Immortal Essence] <upon turn start> <every [5] turns> <when above [9] [Green Grape Immortal Essence]>` | 10, 5, 9 | tools/gen_ruleset.py `Buildings` |
| Years Flow Like Water | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dream Token | cost | 440 | tools/gen_ruleset.py `Buildings` |
| Dream Token | `Costs [40] [White Lychee Immortal Essence]` | 40 | tools/gen_ruleset.py `Buildings` |
| Dream Token | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Dream Token | `[+20]% Strength <vs [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| Dream Token | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | `[4] units cost no maintenance` | 4 | tools/gen_ruleset.py `Buildings` |
| Soul Beast Token | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Buildings` |
| Treasure Light Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | `[+30]% Production when constructing [Immortal Gu] wonders [in all cities]` | +30 | tools/gen_ruleset.py `Buildings` |
| Advance Refinement Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Steal Life | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Steal Life | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Steal Life | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Steal Life | `Heals [25] damage if it kills a unit <for [post-[Rank Five era]] units>` | 25 | tools/gen_ruleset.py `Buildings` |
| Steal Life | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | cost | 400 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | `Instantly provides [3] [Human Qi] <upon turn start>` | 3 | tools/gen_ruleset.py `Buildings` |
| Human Qi Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Wisdom Gu | cost | 700 | tools/gen_ruleset.py `Buildings` |
| Wisdom Gu | `Costs [60] [Yellow Apricot Immortal Essence]` | 60 | tools/gen_ruleset.py `Buildings` |
| Wisdom Gu | `Costs [80] [Immortal Materials]` | 80 | tools/gen_ruleset.py `Buildings` |
| Wisdom Gu | `[+30]% [Science] [in all cities]` | +30 | tools/gen_ruleset.py `Buildings` |
| Wisdom Gu | `Instantly consumes [1] [Lifespan Gu] <upon turn start> <every [5] turns>` | 1, 5 | tools/gen_ruleset.py `Buildings` |
| Wisdom Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Derivation Gu | cost | 700 | tools/gen_ruleset.py `Buildings` |
| Derivation Gu | `Costs [60] [Yellow Apricot Immortal Essence]` | 60 | tools/gen_ruleset.py `Buildings` |
| Derivation Gu | `Costs [80] [Immortal Materials]` | 80 | tools/gen_ruleset.py `Buildings` |
| Derivation Gu | `[+30]% Production when constructing [All] buildings [in all cities]` | +30 | tools/gen_ruleset.py `Buildings` |
| Derivation Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Star Mark Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Star Mark Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Star Mark Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Star Mark Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Pulling Water Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Pulling Water Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Pulling Water Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Pulling Water Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Snack Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Snack Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Snack Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Snack Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Strength Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Strength Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Strength Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Strength Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Change Form Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Change Form Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Change Form Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Change Form Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Blood Asset Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Blood Asset Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Blood Asset Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Blood Asset Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Cleanse Soul Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Cleanse Soul Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Cleanse Soul Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Cleanse Soul Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dark Arrow Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Dark Arrow Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Dark Arrow Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Dark Arrow Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Heavenly Gong Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Heavenly Gong Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Heavenly Gong Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Heavenly Gong Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Ice Soul Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Ice Soul Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Ice Soul Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Ice Soul Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Rising Azure Cloud Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Rising Azure Cloud Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Rising Azure Cloud Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Rising Azure Cloud Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Dog Shit Luck Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Dog Shit Luck Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Dog Shit Luck Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Dog Shit Luck Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Phantom Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Phantom Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Phantom Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Flying Bear Phantom Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Split Shadow Immortal Gu | cost | 340 | tools/gen_ruleset.py `Buildings` |
| Split Shadow Immortal Gu | `Costs [35] [Green Grape Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Split Shadow Immortal Gu | `Costs [30] [Immortal Materials]` | 30 | tools/gen_ruleset.py `Buildings` |
| Split Shadow Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Flying Sword Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Flying Sword Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Flying Sword Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Flying Sword Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Sword Escape Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Sword Escape Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Sword Escape Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Sword Escape Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Edge Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Edge Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Edge Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Edge Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Great Thief Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Great Thief Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Great Thief Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Great Thief Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Crescent Moon Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Crescent Moon Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Crescent Moon Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Crescent Moon Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Perseverance Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Perseverance Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Perseverance Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Perseverance Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Qi Escape Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Qi Escape Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Qi Escape Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Qi Escape Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Expend Strength Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Expend Strength Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Expend Strength Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Expend Strength Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Fixed Space Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Fixed Space Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Fixed Space Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Fixed Space Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Limit Immortal Gu | cost | 380 | tools/gen_ruleset.py `Buildings` |
| Limit Immortal Gu | `Costs [35] [Red Date Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Limit Immortal Gu | `Costs [40] [Immortal Materials]` | 40 | tools/gen_ruleset.py `Buildings` |
| Limit Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Region Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Region Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Region Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Region Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Wisdom Sword Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Wisdom Sword Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Wisdom Sword Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Wisdom Sword Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Regret Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Regret Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Regret Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Regret Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Attitude Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Attitude Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Attitude Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Attitude Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Eight-Faced Prestige Wind Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Eight-Faced Prestige Wind Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Eight-Faced Prestige Wind Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Eight-Faced Prestige Wind Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Water Refinement Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Water Refinement Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Water Refinement Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Water Refinement Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Heavenly Secret Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Heavenly Secret Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Heavenly Secret Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Heavenly Secret Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Heaven's Envy Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Heaven's Envy Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Heaven's Envy Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Heaven's Envy Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Kill Immortal Gu | cost | 420 | tools/gen_ruleset.py `Buildings` |
| Kill Immortal Gu | `Costs [35] [White Lychee Immortal Essence]` | 35 | tools/gen_ruleset.py `Buildings` |
| Kill Immortal Gu | `Costs [50] [Immortal Materials]` | 50 | tools/gen_ruleset.py `Buildings` |
| Kill Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Light Gu | cost | 700 | tools/gen_ruleset.py `Buildings` |
| Light Gu | `Costs [60] [Yellow Apricot Immortal Essence]` | 60 | tools/gen_ruleset.py `Buildings` |
| Light Gu | `Costs [80] [Immortal Materials]` | 80 | tools/gen_ruleset.py `Buildings` |
| Light Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Fire Gu | cost | 700 | tools/gen_ruleset.py `Buildings` |
| Fire Gu | `Costs [60] [Yellow Apricot Immortal Essence]` | 60 | tools/gen_ruleset.py `Buildings` |
| Fire Gu | `Costs [80] [Immortal Materials]` | 80 | tools/gen_ruleset.py `Buildings` |
| Fire Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Love Gu | cost | 700 | tools/gen_ruleset.py `Buildings` |
| Love Gu | `Costs [60] [Yellow Apricot Immortal Essence]` | 60 | tools/gen_ruleset.py `Buildings` |
| Love Gu | `Costs [80] [Immortal Materials]` | 80 | tools/gen_ruleset.py `Buildings` |
| Love Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| Heavenly Web Immortal Gu | cost | 700 | tools/gen_ruleset.py `Buildings` |
| Heavenly Web Immortal Gu | `Costs [60] [Yellow Apricot Immortal Essence]` | 60 | tools/gen_ruleset.py `Buildings` |
| Heavenly Web Immortal Gu | `Costs [80] [Immortal Materials]` | 80 | tools/gen_ruleset.py `Buildings` |
| Heavenly Web Immortal Gu | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
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
| 88 True Yang Building | cost | 420 | tools/gen_ruleset.py `Buildings` |
| 88 True Yang Building | `[+15]% [Gold] [in all cities]` | +15 | tools/gen_ruleset.py `Buildings` |
| 88 True Yang Building | `[+15]% Strength <for units with [Luck Master]>` | +15 | tools/gen_ruleset.py `Buildings` |
| 88 True Yang Building | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| True Yang Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Venerable Ascension | cost | 700 | tools/gen_ruleset.py `Buildings` |
| Eternal Life | cost | 1200 | tools/gen_ruleset.py `Buildings` |
| True Inheritance | cost | 600 | tools/gen_ruleset.py `Buildings` |
| True Inheritance | `[+25]% XP gained from combat` | +25 | tools/gen_ruleset.py `Buildings` |
| True Inheritance | `[+20]% Strength <for [post-[Rank Five era]] units>` | +20 | tools/gen_ruleset.py `Buildings` |
| True Inheritance | `[+300]% weight to this choice for AI decisions` | +300 | tools/gen_ruleset.py `Buildings` |
| True Inheritance Seal | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Fate Gu | cost | 600 | tools/gen_ruleset.py `Buildings` |
| Fate Gu | `Costs [60] [Green Grape Immortal Essence]` | 60 | tools/gen_ruleset.py `Buildings` |
| Fate Gu | `[+15]% Strength <for [post-[Rank Five era]] units>` | +15 | tools/gen_ruleset.py `Buildings` |
| Fate Gu | `[+2 Happiness]` | +2 | tools/gen_ruleset.py `Buildings` |
| Fate Gu | `[+500]% weight to this choice for AI decisions` | +500 | tools/gen_ruleset.py `Buildings` |
| Shattered Fate | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Fate Seized | cost | 1 | tools/gen_ruleset.py `Buildings` |
| Strength Hall | cost | 90 | tools/gen_ruleset.py `Buildings` |
| Strength Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Strength Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Strength Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Strength Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Transformation Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Transformation Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Transformation Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Transformation Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Transformation Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Transformation Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Bone Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Bone Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Bone Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Bone Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Bone Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Bone Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blood Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Blood Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Blood Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blood Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blood Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blood Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sword Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Sword Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Sword Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sword Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sword Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sword Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blade Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Blade Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Blade Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blade Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blade Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Blade Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Metal Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Metal Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Metal Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Metal Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Metal Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Metal Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Weapon Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Weapon Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Weapon Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Weapon Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Weapon Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Weapon Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Killing Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Killing Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Killing Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Killing Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Killing Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Killing Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Fire Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Fire Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Fire Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Fire Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Fire Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Fire Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Water Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Water Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Water Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Water Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Water Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wood Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Wood Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Wood Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wood Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wood Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wood Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Earth Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Earth Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Earth Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Earth Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Earth Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Earth Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wind Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Wind Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Wind Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wind Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wind Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Cloud Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Cloud Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Cloud Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Cloud Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Cloud Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Cloud Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Ice Snow Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Ice Snow Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Ice Snow Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Ice Snow Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Ice Snow Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Ice Snow Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Lightning Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Lightning Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Lightning Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Lightning Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Lightning Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Lightning Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Poison Hall | cost | 120 | tools/gen_ruleset.py `Buildings` |
| Poison Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Poison Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Poison Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Poison Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Poison Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Light Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Light Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Light Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Light Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Light Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Light Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dark Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Dark Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Dark Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dark Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dark Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dark Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Shadow Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Shadow Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Shadow Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Shadow Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Shadow Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Shadow Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Star Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Star Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Star Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Star Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Star Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Star Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Moon Hall | cost | 90 | tools/gen_ruleset.py `Buildings` |
| Moon Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Moon Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Moon Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Moon Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sound Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Sound Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Sound Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sound Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sound Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Sound Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Illusion Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Illusion Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Illusion Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Illusion Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Illusion Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Illusion Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wisdom Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Wisdom Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Wisdom Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wisdom Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wisdom Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Wisdom Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Emotion Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Emotion Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Emotion Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Emotion Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Emotion Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Emotion Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enchantment Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Enchantment Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Enchantment Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enchantment Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enchantment Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enchantment Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Soul Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Soul Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Soul Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Soul Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Soul Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Soul Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dream Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Dream Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Dream Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dream Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dream Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Dream Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enslavement Hall | cost | 170 | tools/gen_ruleset.py `Buildings` |
| Enslavement Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Enslavement Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enslavement Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enslavement Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Enslavement Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Time Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Time Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Time Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Time Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Time Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Time Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Space Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Space Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Space Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Space Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Space Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Space Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Rule Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Rule Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Rule Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Rule Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Rule Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Rule Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Phantom Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Phantom Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Phantom Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Phantom Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Phantom Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Phantom Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Restriction Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Restriction Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Restriction Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Restriction Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Restriction Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Restriction Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Luck Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Luck Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Luck Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Luck Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Luck Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Luck Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Heaven Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Heaven Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Heaven Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Heaven Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Heaven Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Heaven Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Qi Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Qi Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Qi Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Qi Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Qi Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Qi Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Refinement Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Refinement Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Refinement Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Refinement Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Refinement Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Refinement Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Formation Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Formation Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Formation Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Formation Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Formation Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Formation Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Food Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Food Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Food Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Food Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Food Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Food Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Pill Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Pill Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Pill Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Pill Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Pill Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Pill Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Information Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Information Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Information Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Information Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Information Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Information Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Human Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Human Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Human Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Human Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Human Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Human Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Painting Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Painting Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Painting Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Painting Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Painting Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Painting Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Theft Hall | cost | 240 | tools/gen_ruleset.py `Buildings` |
| Theft Hall | culture | 1 | tools/gen_ruleset.py `Buildings` |
| Theft Hall | `[-90]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Theft Hall | `[-90]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Theft Hall | `[-90]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |
| Theft Hall | `[-90]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | -90 | tools/gen_ruleset.py `Buildings` |

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
| Column 12 (Dao Lord, Gu House Formation) | techCost | 1500 | data/tech_columns.csv `techCost` |
| Column 12 (Dao Lord, Gu House Formation) | buildingCost | 480 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 12 (Dao Lord, Gu House Formation) | wonderCost | 700 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 13 (Rank Nine Immortal Gu Recipes, Venerable Dominion) | techCost | 1700 | data/tech_columns.csv `techCost` |
| Column 13 (Rank Nine Immortal Gu Recipes, Venerable Dominion) | buildingCost | 520 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 13 (Rank Nine Immortal Gu Recipes, Venerable Dominion) | wonderCost | 750 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 14 (Dao Comprehension) | techCost | 1900 | data/tech_columns.csv `techCost` |
| Column 14 (Dao Comprehension) | buildingCost | 560 | data/tech_columns.csv `buildingCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |
| Column 14 (Dao Comprehension) | wonderCost | 800 | data/tech_columns.csv `wonderCost`: inert while every building sets its own cost [src Ruleset.updateBuildingCosts] |

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
| Transformation Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Transformation Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Transformation Path | `[+5]% Strength <for [Transformation Master] units> <for every [Adopted [[Transformation Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Transformation Path › Transformation Lineage | `[+15]% Strength <when defending> <for [Transformation Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Transformation Path › Transformation Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Transformation Path › Transformation Doctrine | `Heals [15] damage if it kills a unit <for [Transformation Master] units>` | 15 | tools/gen_ruleset.py `Policies` |
| Transformation Path › Transformation Path Complete | `[+10] HP when healing <for [Transformation Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Bone Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Bone Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Bone Path | `[+5]% Strength <for [Bone Master] units> <for every [Adopted [[Bone Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Bone Path › Bone Lineage | `[+15]% Strength <when defending> <for [Bone Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Bone Path › Bone Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Bone Path › Bone Doctrine | `Heals [15] damage if it kills a unit <for [Bone Master] units>` | 15 | tools/gen_ruleset.py `Policies` |
| Bone Path › Bone Path Complete | `[+10] HP when healing <for [Bone Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Blood Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Blood Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Blood Path | `[+5]% Strength <for [Blood Master] units> <for every [Adopted [[Blood Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Blood Path › Blood Lineage | `[+15]% Strength <when defending> <for [Blood Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Blood Path › Blood Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Blood Path › Blood Doctrine | `Heals [15] damage if it kills a unit <for [Blood Master] units>` | 15 | tools/gen_ruleset.py `Policies` |
| Blood Path › Blood Path Complete | `[+10] HP when healing <for [Blood Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Sword Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Sword Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Sword Path | `[+5]% Strength <for [Sword Master] units> <for every [Adopted [[Sword Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Sword Path › Sword Lineage | `[+15]% Strength <when attacking> <for [Sword Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Sword Path › Sword Insight | `[+10]% Production when constructing [Military] units [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Sword Path › Sword Doctrine | `[1] Movement <for [Sword Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Sword Path › Sword Path Complete | `[+15]% Strength <vs cities> <for [Sword Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Blade Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Blade Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Blade Path | `[+5]% Strength <for [Blade Master] units> <for every [Adopted [[Blade Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Blade Path › Blade Lineage | `[+15]% Strength <when attacking> <for [Blade Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Blade Path › Blade Insight | `[+10]% Production when constructing [Military] units [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Blade Path › Blade Doctrine | `[1] Movement <for [Blade Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Blade Path › Blade Path Complete | `[+15]% Strength <vs cities> <for [Blade Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Metal Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Metal Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Metal Path | `[+5]% Strength <for [Metal Master] units> <for every [Adopted [[Metal Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Metal Path › Metal Lineage | `[+15]% Strength <when attacking> <for [Metal Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Metal Path › Metal Insight | `[+10]% Production when constructing [Military] units [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Metal Path › Metal Doctrine | `[1] Movement <for [Metal Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Metal Path › Metal Path Complete | `[+15]% Strength <vs cities> <for [Metal Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Weapon Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Weapon Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Weapon Path | `[+5]% Strength <for [Weapon Master] units> <for every [Adopted [[Weapon Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Weapon Path › Weapon Lineage | `[+15]% Strength <when attacking> <for [Weapon Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Weapon Path › Weapon Insight | `[+10]% Production when constructing [Military] units [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Weapon Path › Weapon Doctrine | `[1] Movement <for [Weapon Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Weapon Path › Weapon Path Complete | `[+15]% Strength <vs cities> <for [Weapon Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Killing Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Killing Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Killing Path | `[+5]% Strength <for [Killing Master] units> <for every [Adopted [[Killing Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Killing Path › Killing Lineage | `[+15]% Strength <when attacking> <for [Killing Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Killing Path › Killing Insight | `[+10]% Production when constructing [Military] units [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Killing Path › Killing Doctrine | `[1] Movement <for [Killing Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Killing Path › Killing Path Complete | `[+15]% Strength <vs cities> <for [Killing Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Fire Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Fire Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Fire Path | `[+5]% Strength <for [Fire Master] units> <for every [Adopted [[Fire Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Fire Path › Fire Lineage | `[+10]% Strength <for [Fire Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Fire Path › Fire Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Fire Path › Fire Doctrine | `[+10] HP when healing <for [Fire Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Fire Path › Fire Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Water Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Water Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Water Path | `[+5]% Strength <for [Water Master] units> <for every [Adopted [[Water Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Water Path › Water Lineage | `[+10]% Strength <for [Water Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Water Path › Water Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Water Path › Water Doctrine | `[+10] HP when healing <for [Water Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Water Path › Water Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Wood Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Wood Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Wood Path | `[+5]% Strength <for [Wood Master] units> <for every [Adopted [[Wood Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Wood Path › Wood Lineage | `[+10]% Strength <for [Wood Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Wood Path › Wood Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Wood Path › Wood Doctrine | `[+10] HP when healing <for [Wood Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Wood Path › Wood Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Earth Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Earth Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Earth Path | `[+5]% Strength <for [Earth Master] units> <for every [Adopted [[Earth Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Earth Path › Earth Lineage | `[+10]% Strength <for [Earth Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Earth Path › Earth Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Earth Path › Earth Doctrine | `[+10] HP when healing <for [Earth Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Earth Path › Earth Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Wind Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Wind Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Wind Path | `[+5]% Strength <for [Wind Master] units> <for every [Adopted [[Wind Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Wind Path › Wind Lineage | `[+10]% Strength <for [Wind Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Wind Path › Wind Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Wind Path › Wind Doctrine | `[+10] HP when healing <for [Wind Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Wind Path › Wind Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Cloud Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Cloud Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Cloud Path | `[+5]% Strength <for [Cloud Master] units> <for every [Adopted [[Cloud Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Cloud Path › Cloud Lineage | `[+10]% Strength <for [Cloud Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Cloud Path › Cloud Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Cloud Path › Cloud Doctrine | `[+10] HP when healing <for [Cloud Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Cloud Path › Cloud Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Ice Snow Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Ice Snow Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Ice Snow Path | `[+5]% Strength <for [Ice Snow Master] units> <for every [Adopted [[Ice Snow Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Ice Snow Path › Ice Snow Lineage | `[+10]% Strength <for [Ice Snow Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Ice Snow Path › Ice Snow Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Ice Snow Path › Ice Snow Doctrine | `[+10] HP when healing <for [Ice Snow Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Ice Snow Path › Ice Snow Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Lightning Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Lightning Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Lightning Path | `[+5]% Strength <for [Lightning Master] units> <for every [Adopted [[Lightning Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Lightning Path › Lightning Lineage | `[+10]% Strength <for [Lightning Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Lightning Path › Lightning Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Lightning Path › Lightning Doctrine | `[+10] HP when healing <for [Lightning Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Lightning Path › Lightning Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Poison Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Poison Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Poison Path | `[+5]% Strength <for [Poison Master] units> <for every [Adopted [[Poison Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Poison Path › Poison Lineage | `[+10]% Strength <for [Poison Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Poison Path › Poison Insight | `[+1 Food] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Poison Path › Poison Doctrine | `[+10] HP when healing <for [Poison Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Poison Path › Poison Path Complete | `[+10]% [Food] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Light Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Light Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Light Path | `[+5]% Strength <for [Light Master] units> <for every [Adopted [[Light Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Light Path › Light Lineage | `[1] Sight <for [Light Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Light Path › Light Insight | `[+1 Culture] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Light Path › Light Doctrine | `[+15]% Strength <when attacking> <for [Light Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Light Path › Light Path Complete | `[1] Movement <for [Light Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Dark Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Dark Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Dark Path | `[+5]% Strength <for [Dark Master] units> <for every [Adopted [[Dark Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Dark Path › Dark Lineage | `[1] Sight <for [Dark Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Dark Path › Dark Insight | `[+1 Culture] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Dark Path › Dark Doctrine | `[+15]% Strength <when attacking> <for [Dark Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Dark Path › Dark Path Complete | `[1] Movement <for [Dark Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Shadow Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Shadow Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Shadow Path | `[+5]% Strength <for [Shadow Master] units> <for every [Adopted [[Shadow Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Shadow Path › Shadow Lineage | `[1] Sight <for [Shadow Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Shadow Path › Shadow Insight | `[+1 Culture] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Shadow Path › Shadow Doctrine | `[+15]% Strength <when attacking> <for [Shadow Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Shadow Path › Shadow Path Complete | `[1] Movement <for [Shadow Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Star Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Star Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Star Path | `[+5]% Strength <for [Star Master] units> <for every [Adopted [[Star Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Star Path › Star Lineage | `[1] Sight <for [Star Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Star Path › Star Insight | `[+1 Culture] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Star Path › Star Doctrine | `[+15]% Strength <when attacking> <for [Star Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Star Path › Star Path Complete | `[1] Movement <for [Star Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Sound Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Sound Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Sound Path | `[+5]% Strength <for [Sound Master] units> <for every [Adopted [[Sound Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Sound Path › Sound Lineage | `[1] Sight <for [Sound Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Sound Path › Sound Insight | `[+1 Culture] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Sound Path › Sound Doctrine | `[+15]% Strength <when attacking> <for [Sound Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Sound Path › Sound Path Complete | `[1] Movement <for [Sound Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Illusion Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Illusion Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Illusion Path | `[+5]% Strength <for [Illusion Master] units> <for every [Adopted [[Illusion Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Illusion Path › Illusion Lineage | `[1] Sight <for [Illusion Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Illusion Path › Illusion Insight | `[+1 Culture] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Illusion Path › Illusion Doctrine | `[+15]% Strength <when attacking> <for [Illusion Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Illusion Path › Illusion Path Complete | `[1] Movement <for [Illusion Master] units>` | 1 | tools/gen_ruleset.py `Policies` |
| Wisdom Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Wisdom Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Wisdom Path | `[+5]% Strength <for [Wisdom Master] units> <for every [Adopted [[Wisdom Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Wisdom Path › Wisdom Lineage | `[+15]% XP gained from combat <for [Wisdom Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Wisdom Path › Wisdom Insight | `[+1 Science] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Wisdom Path › Wisdom Doctrine | `[+10]% Strength <for [Wisdom Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Wisdom Path › Wisdom Path Complete | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Emotion Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Emotion Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Emotion Path | `[+5]% Strength <for [Emotion Master] units> <for every [Adopted [[Emotion Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Emotion Path › Emotion Lineage | `[+15]% XP gained from combat <for [Emotion Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Emotion Path › Emotion Insight | `[+1 Science] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Emotion Path › Emotion Doctrine | `[+10]% Strength <for [Emotion Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Emotion Path › Emotion Path Complete | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Enchantment Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Enchantment Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Enchantment Path | `[+5]% Strength <for [Enchantment Master] units> <for every [Adopted [[Enchantment Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Enchantment Path › Enchantment Lineage | `[+15]% XP gained from combat <for [Enchantment Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Enchantment Path › Enchantment Insight | `[+1 Science] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Enchantment Path › Enchantment Doctrine | `[+10]% Strength <for [Enchantment Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Enchantment Path › Enchantment Path Complete | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Soul Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Soul Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Soul Path | `[+5]% Strength <for [Soul Master] units> <for every [Adopted [[Soul Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Soul Path › Soul Lineage | `[+15]% XP gained from combat <for [Soul Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Soul Path › Soul Insight | `[+1 Science] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Soul Path › Soul Doctrine | `[+10]% Strength <for [Soul Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Soul Path › Soul Path Complete | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Dream Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Dream Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Dream Path | `[+5]% Strength <for [Dream Master] units> <for every [Adopted [[Dream Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Dream Path › Dream Lineage | `[+15]% XP gained from combat <for [Dream Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Dream Path › Dream Insight | `[+1 Science] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Dream Path › Dream Doctrine | `[+10]% Strength <for [Dream Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Dream Path › Dream Path Complete | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Enslavement Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Enslavement Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Enslavement Path | `[+5]% Strength <for [Enslavement Master] units> <for every [Adopted [[Enslavement Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Enslavement Path › Enslavement Lineage | `[+15]% XP gained from combat <for [Enslavement Master] units>` | +15 | tools/gen_ruleset.py `Policies` |
| Enslavement Path › Enslavement Insight | `[+1 Science] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Enslavement Path › Enslavement Doctrine | `[+10]% Strength <for [Enslavement Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Enslavement Path › Enslavement Path Complete | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Time Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Time Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Time Path | `[+5]% Strength <for [Time Master] units> <for every [Adopted [[Time Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Time Path › Time Lineage | `[+10]% Strength <for [Time Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Time Path › Time Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Time Path › Time Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Time Path › Time Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Space Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Space Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Space Path | `[+5]% Strength <for [Space Master] units> <for every [Adopted [[Space Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Space Path › Space Lineage | `[+10]% Strength <for [Space Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Space Path › Space Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Space Path › Space Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Space Path › Space Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Rule Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Rule Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Rule Path | `[+5]% Strength <for [Rule Master] units> <for every [Adopted [[Rule Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Rule Path › Rule Lineage | `[+10]% Strength <for [Rule Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Rule Path › Rule Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Rule Path › Rule Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Rule Path › Rule Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Phantom Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Phantom Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Phantom Path | `[+5]% Strength <for [Phantom Master] units> <for every [Adopted [[Phantom Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Phantom Path › Phantom Lineage | `[+10]% Strength <for [Phantom Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Phantom Path › Phantom Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Phantom Path › Phantom Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Phantom Path › Phantom Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Restriction Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Restriction Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Restriction Path | `[+5]% Strength <for [Restriction Master] units> <for every [Adopted [[Restriction Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Restriction Path › Restriction Lineage | `[+10]% Strength <for [Restriction Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Restriction Path › Restriction Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Restriction Path › Restriction Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Restriction Path › Restriction Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Luck Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Luck Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Luck Path | `[+5]% Strength <for [Luck Master] units> <for every [Adopted [[Luck Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Luck Path › Luck Lineage | `[+10]% Strength <for [Luck Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Luck Path › Luck Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Luck Path › Luck Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Luck Path › Luck Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Heaven Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Heaven Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Heaven Path | `[+5]% Strength <for [Heaven Master] units> <for every [Adopted [[Heaven Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Heaven Path › Heaven Lineage | `[+10]% Strength <for [Heaven Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Heaven Path › Heaven Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Heaven Path › Heaven Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Heaven Path › Heaven Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Qi Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Qi Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Qi Path | `[+5]% Strength <for [Qi Master] units> <for every [Adopted [[Qi Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Qi Path › Qi Lineage | `[+10]% Strength <for [Qi Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Qi Path › Qi Insight | `[+1 Gold] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Qi Path › Qi Doctrine | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Policies` |
| Qi Path › Qi Path Complete | `[+10]% [Gold] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Refinement Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Refinement Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Refinement Path | `[+5]% Strength <for [Refinement Master] units> <for every [Adopted [[Refinement Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Refinement Path › Refinement Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Refinement Path › Refinement Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Refinement Path › Refinement Doctrine | `[+10]% Strength <for [Refinement Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Refinement Path › Refinement Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Formation Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Formation Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Formation Path | `[+5]% Strength <for [Formation Master] units> <for every [Adopted [[Formation Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Formation Path › Formation Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Formation Path › Formation Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Formation Path › Formation Doctrine | `[+10]% Strength <for [Formation Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Formation Path › Formation Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Food Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Food Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Food Path | `[+5]% Strength <for [Food Master] units> <for every [Adopted [[Food Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Food Path › Food Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Food Path › Food Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Food Path › Food Doctrine | `[+10]% Strength <for [Food Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Food Path › Food Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Pill Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Pill Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Pill Path | `[+5]% Strength <for [Pill Master] units> <for every [Adopted [[Pill Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Pill Path › Pill Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Pill Path › Pill Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Pill Path › Pill Doctrine | `[+10]% Strength <for [Pill Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Pill Path › Pill Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Information Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Information Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Information Path | `[+5]% Strength <for [Information Master] units> <for every [Adopted [[Information Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Information Path › Information Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Information Path › Information Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Information Path › Information Doctrine | `[+10]% Strength <for [Information Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Information Path › Information Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Human Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Human Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Human Path | `[+5]% Strength <for [Human Master] units> <for every [Adopted [[Human Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Human Path › Human Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Human Path › Human Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Human Path › Human Doctrine | `[+10]% Strength <for [Human Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Human Path › Human Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Painting Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Painting Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Painting Path | `[+5]% Strength <for [Painting Master] units> <for every [Adopted [[Painting Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Painting Path › Painting Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Painting Path › Painting Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Painting Path › Painting Doctrine | `[+10]% Strength <for [Painting Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Painting Path › Painting Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Theft Path | priorities.Southern Border Supremacy | 3 | tools/gen_ruleset.py `Policies` |
| Theft Path | priorities.Endurance | 3 | tools/gen_ruleset.py `Policies` |
| Theft Path | `[+5]% Strength <for [Theft Master] units> <for every [Adopted [[Theft Path] branch] Policies]>` | +5 | tools/gen_ruleset.py `Policies` |
| Theft Path › Theft Lineage | `[+10]% Production when constructing [All] wonders [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |
| Theft Path › Theft Insight | `[+1 Production] [in all cities]` | +1 | tools/gen_ruleset.py `Policies` |
| Theft Path › Theft Doctrine | `[+10]% Strength <for [Theft Master] units>` | +10 | tools/gen_ruleset.py `Policies` |
| Theft Path › Theft Path Complete | `[+10]% [Production] [in all cities]` | +10 | tools/gen_ruleset.py `Policies` |

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
| Heavenly Court | `[+15]% Strength <vs [Immortal Zombie] units>` | +15 | tools/gen_ruleset.py `Nations` |
| Heavenly Court | `[+25]% Strength <vs [Barbarian] units>` | +25 | tools/gen_ruleset.py `Nations` |
| Heavenly Court | `[6] Free Technologies <upon founding a city> <when number of [Cities] is less than [2]>` | 6, 2 | tools/gen_ruleset.py `Nations` |
| Heavenly Court | `[2] free [Rank Three Gu Master] units appear <upon founding a city> <when number of [Cities] is less than [2]>` | 2, 2 | tools/gen_ruleset.py `Nations` |
| Heavenly Court | `[+15]% [Science] [in all cities]` | +15 | tools/gen_ruleset.py `Nations` |
| Heavenly Court | `[+15]% [Production] [in all cities]` | +15 | tools/gen_ruleset.py `Nations` |
| Heavenly Court | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Heavenly Court | `[2] free [Rank Seven Gu Immortal] units appear <upon being declared war on by [All] Civilizations> <when number of [[Rank Seven Gu Immortal] Units] is less than [3]>` | 2, 3 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `[+15]% Strength <when defending>` | +15 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `[3] Free Technologies <upon founding a city> <when number of [Cities] is less than [2]>` | 3, 2 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `[3] free [Rank Two Gu Master] units appear <upon founding a city> <when number of [Cities] is less than [2]>` | 3, 2 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `[-15]% [Gold] [in all cities]` | -15 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `[+25]% Production when constructing [Military] units [in all cities]` | +25 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `[+3 Happiness]` | +3 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `Triggers a [Imperial Court Contest] event <upon turn start> <every [9] turns> <on [Quick] game speed>` | 9 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `Triggers a [Imperial Court Contest] event <upon turn start> <every [13] turns> <on [Standard] game speed>` | 13 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `Triggers a [Imperial Court Contest] event <upon turn start> <every [20] turns> <on [Epic] game speed>` | 20 | tools/gen_ruleset.py `Nations` |
| Huang Jin Family | `Triggers a [Imperial Court Contest] event <upon turn start> <every [39] turns> <on [Marathon] game speed>` | 39 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `[3] Free Technologies <upon founding a city> <when number of [Cities] is less than [2]>` | 3, 2 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `[+25]% [Gold] [in all cities]` | +25 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Triggers a [Fate Hunt] event <upon turn start> <when number of [[Immortal Zombie] Units] is more than [0]> <if [Fate Gu] is constructed by anybody> <with [4]% chance> <on [Quick] game speed>` | 0, 4 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Triggers a [Fate Hunt] event <upon turn start> <when number of [[Immortal Zombie] Units] is more than [0]> <if [Fate Gu] is constructed by anybody> <with [3]% chance> <on [Standard] game speed>` | 0, 3 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Triggers a [Fate Hunt] event <upon turn start> <when number of [[Immortal Zombie] Units] is more than [0]> <if [Fate Gu] is constructed by anybody> <with [2]% chance> <on [Epic] game speed>` | 0, 2 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Triggers a [Fate Hunt] event <upon turn start> <when number of [[Immortal Zombie] Units] is more than [0]> <if [Fate Gu] is constructed by anybody> <with [1]% chance> <on [Marathon] game speed>` | 0, 1 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Instantly provides [1] [Lifespan Gu] <upon turn start> <every [7] turns> <for every [1] [[post-[Rank Five era]] Units]> <on [Quick] game speed>` | 1, 7, 1 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Instantly provides [1] [Lifespan Gu] <upon turn start> <every [10] turns> <for every [1] [[post-[Rank Five era]] Units]> <on [Standard] game speed>` | 1, 10, 1 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Instantly provides [1] [Lifespan Gu] <upon turn start> <every [15] turns> <for every [1] [[post-[Rank Five era]] Units]> <on [Epic] game speed>` | 1, 15, 1 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `Instantly provides [1] [Lifespan Gu] <upon turn start> <every [30] turns> <for every [1] [[post-[Rank Five era]] Units]> <on [Marathon] game speed>` | 1, 30, 1 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [27]> <every [1] turns> <with [4]% chance> <on [Quick] game speed>` | 27, 1, 4 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [40]> <every [1] turns> <with [4]% chance> <on [Standard] game speed>` | 40, 1, 4 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [60]> <every [2] turns> <with [4]% chance> <on [Epic] game speed>` | 60, 2, 4 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [120]> <every [3] turns> <with [4]% chance> <on [Marathon] game speed>` | 120, 3, 4 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `[+50]% Production when constructing [Gu House] units [in all cities]` | +50 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `[+10]% [Science] [in all cities]` | +10 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `[2] Free Technologies <upon founding a city> <when number of [Cities] is less than [2]>` | 2, 2 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `[+20]% [Gold] [in all cities]` | +20 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `Triggers a [Wan Coalition] event <upon turn start> <when number of [Cities] is more than [3]> <with [3]% chance> <on [Quick] game speed>` | 3, 3 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `Triggers a [Wan Coalition] event <upon turn start> <when number of [Cities] is more than [3]> <with [2]% chance> <on [Standard] game speed>` | 3, 2 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `Triggers a [Wan Coalition] event <upon turn start> <when number of [Cities] is more than [3]> <with [1]% chance> <on [Epic] game speed>` | 3, 1 | tools/gen_ruleset.py `Nations` |
| Fang Clan | `Triggers a [Wan Coalition] event <upon turn start> <when number of [Cities] is more than [3]> <with [1]% chance> <on [Marathon] game speed>` | 3, 1 | tools/gen_ruleset.py `Nations` |
| Spirit Affinity House | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Combat Immortal Sect | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Merman Imperial Court | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [27]> <every [1] turns> <with [4]% chance> <on [Quick] game speed>` | 27, 1, 4 | tools/gen_ruleset.py `Nations` |
| Merman Imperial Court | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [40]> <every [1] turns> <with [4]% chance> <on [Standard] game speed>` | 40, 1, 4 | tools/gen_ruleset.py `Nations` |
| Merman Imperial Court | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [60]> <every [2] turns> <with [4]% chance> <on [Epic] game speed>` | 60, 2, 4 | tools/gen_ruleset.py `Nations` |
| Merman Imperial Court | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [120]> <every [3] turns> <with [4]% chance> <on [Marathon] game speed>` | 120, 3, 4 | tools/gen_ruleset.py `Nations` |
| Song Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [27]> <every [1] turns> <with [4]% chance> <on [Quick] game speed>` | 27, 1, 4 | tools/gen_ruleset.py `Nations` |
| Song Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [40]> <every [1] turns> <with [4]% chance> <on [Standard] game speed>` | 40, 1, 4 | tools/gen_ruleset.py `Nations` |
| Song Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [60]> <every [2] turns> <with [4]% chance> <on [Epic] game speed>` | 60, 2, 4 | tools/gen_ruleset.py `Nations` |
| Song Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [120]> <every [3] turns> <with [4]% chance> <on [Marathon] game speed>` | 120, 3, 4 | tools/gen_ruleset.py `Nations` |
| Xia Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [27]> <every [1] turns> <with [4]% chance> <on [Quick] game speed>` | 27, 1, 4 | tools/gen_ruleset.py `Nations` |
| Xia Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [40]> <every [1] turns> <with [4]% chance> <on [Standard] game speed>` | 40, 1, 4 | tools/gen_ruleset.py `Nations` |
| Xia Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [60]> <every [2] turns> <with [4]% chance> <on [Epic] game speed>` | 60, 2, 4 | tools/gen_ruleset.py `Nations` |
| Xia Clan | `A [Demonic Gu Master] rebels <upon turn start> <after turn number [120]> <every [3] turns> <with [4]% chance> <on [Marathon] game speed>` | 120, 3, 4 | tools/gen_ruleset.py `Nations` |
| Immortal Crane Sect | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Heavenly Lotus Sect | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Spirit Butterfly Valley | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Ancient Soul Sect | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Heaven's Envy Tower | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Wind Cloud Manor | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Black Heaven Temple | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Myriad Dragon Dock | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |
| Snowmen | `[+50]% Strength for cities` | +50 | tools/gen_ruleset.py `Nations` |

### CityStateTypes.json

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| Immortal Sect (friendBonusUniques) | `[+2 Culture] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Immortal Sect (allyBonusUniques) | `[+2 Culture] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Immortal Sect (allyBonusUniques) | `[+15]% Strength <for [post-[Rank Five era]] units>` | +15 | tools/gen_ruleset.py `Nations` |
| Refiner Tribe (friendBonusUniques) | `[+2 Science] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Refiner Tribe (allyBonusUniques) | `[+2 Science] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Refiner Tribe (allyBonusUniques) | `[+20]% XP gained from combat` | +20 | tools/gen_ruleset.py `Nations` |
| Mortal Villages (friendBonusUniques) | `[+2 Food] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Mortal Villages (allyBonusUniques) | `[+2 Food] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Mortal Villages (allyBonusUniques) | `[+2 Production] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Merchant Clan (friendBonusUniques) | `[+2 Gold] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Merchant Clan (allyBonusUniques) | `[+3 Gold] [in capital]` | +3 | tools/gen_ruleset.py `Nations` |
| Merchant Clan (allyBonusUniques) | `[+10]% [Gold]` | +10 | tools/gen_ruleset.py `Nations` |
| Battle Tribe (friendBonusUniques) | `Provides military units every ≈[20] turns` | 20 | tools/gen_ruleset.py `Nations` |
| Battle Tribe (allyBonusUniques) | `Provides military units every ≈[17] turns` | 17 | tools/gen_ruleset.py `Nations` |
| Winged Folk (friendBonusUniques) | `[+1] Sight <for [Military] units>` | +1 | tools/gen_ruleset.py `Nations` |
| Winged Folk (allyBonusUniques) | `[+1] Sight <for [Military] units>` | +1 | tools/gen_ruleset.py `Nations` |
| Winged Folk (allyBonusUniques) | `[+1] Movement <for [Military] units> <in [Desert] tiles>` | +1 | tools/gen_ruleset.py `Nations` |
| Snow Folk (friendBonusUniques) | `[+5]% Strength <for [Military] units> <when defending>` | +5 | tools/gen_ruleset.py `Nations` |
| Snow Folk (allyBonusUniques) | `[+10]% Strength <for [Military] units> <when defending>` | +10 | tools/gen_ruleset.py `Nations` |
| Snow Folk (allyBonusUniques) | `Provides military units every ≈[25] turns` | 25 | tools/gen_ruleset.py `Nations` |
| Ink Folk (friendBonusUniques) | `[+2 Culture] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Ink Folk (allyBonusUniques) | `[+3 Culture] [in capital]` | +3 | tools/gen_ruleset.py `Nations` |
| Ink Folk (allyBonusUniques) | `[+1 Happiness]` | +1 | tools/gen_ruleset.py `Nations` |
| Stone Folk (friendBonusUniques) | `[+2 Production] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Stone Folk (allyBonusUniques) | `[+2 Production] [in capital]` | +2 | tools/gen_ruleset.py `Nations` |
| Stone Folk (allyBonusUniques) | `[+1 Production] from [Mine] tiles [in all cities]` | +1 | tools/gen_ruleset.py `Nations` |

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
| Heavenly Court Temperament | science | 9 | tools/gen_ruleset.py `Nations` |
| Heavenly Court Temperament | military | 8 | tools/gen_ruleset.py `Nations` |
| Heavenly Court Temperament | aggressive | 2 | tools/gen_ruleset.py `Nations` |
| Heavenly Court Temperament | declareWar | 0 | tools/gen_ruleset.py `Nations` |
| Heavenly Court Temperament | diplomacy | 8 | tools/gen_ruleset.py `Nations` |
| Heavenly Court Temperament | loyal | 9 | tools/gen_ruleset.py `Nations` |
| Heavenly Court Temperament | commerce | 6 | tools/gen_ruleset.py `Nations` |
| Heavenly Court Temperament | `[+500]% weight to [Fate Gu] for AI decisions` | +500 | tools/gen_ruleset.py `Nations` |
| Huang Jin Temperament | military | 10 | tools/gen_ruleset.py `Nations` |
| Huang Jin Temperament | aggressive | 10 | tools/gen_ruleset.py `Nations` |
| Huang Jin Temperament | declareWar | 10 | tools/gen_ruleset.py `Nations` |
| Huang Jin Temperament | expansion | 8 | tools/gen_ruleset.py `Nations` |
| Huang Jin Temperament | loyal | 5 | tools/gen_ruleset.py `Nations` |
| Huang Jin Temperament | diplomacy | 3 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance Temperament | gold | 8 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance Temperament | military | 7 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance Temperament | aggressive | 7 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance Temperament | declareWar | 6 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance Temperament | commerce | 8 | tools/gen_ruleset.py `Nations` |
| Zombie Alliance Temperament | loyal | 2 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | production | 8 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | science | 6 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | military | 6 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | aggressive | 3 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | declareWar | 2 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | diplomacy | 9 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | commerce | 9 | tools/gen_ruleset.py `Nations` |
| Fang Temperament | `[+200]% weight to [Gu House Formation] for AI decisions` | +200 | tools/gen_ruleset.py `Nations` |
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
| Rank Nine era | researchAgreementCost | 900 | tools/gen_ruleset.py `Eras` |
| Rank Nine era | baseUnitBuyCost | 900 | tools/gen_ruleset.py `Eras` |

### UnitTypes.json

No tunable numbers.

### Paths (tools/gen_paths.py)

Every path promotion and path Gu is built from these knobs; the hidden conflict lines follow data/path_conflicts.csv (an exact pair wins, then the milder of the two paths' `x,*` rows, then `*,*`).

| Object | Field or unique | Value | Edit in |
|---|---|---|---|
| every Master | `[+20]% Strength` | +20 | tools/gen_paths.py `TIER_STRENGTH` |
| every Grandmaster | `[+25]% Strength` | +25 | tools/gen_paths.py `TIER_STRENGTH` |
| every Great Grandmaster | `[+30]% Strength` | +30 | tools/gen_paths.py `TIER_STRENGTH` |
| every Supreme Grandmaster | `[+35]% Strength` | +35 | tools/gen_paths.py `TIER_STRENGTH` |
| every move | `<costs [+15 Gold] stats> <requires [1] movement>` | +15, 1 | tools/gen_paths.py `MOVE_COST` |
| every tier | `[+400]% weight to this choice for AI decisions` | +400 | tools/gen_paths.py `TIER_WEIGHT` |
| AI killer moves | an AI unit uses its path's move when it attacks, if it keeps this reserve after paying | 100 stones, 10 essence | tools/gen_paths.py `AI_STONES`, `AI_ESSENCE` |
| every Gu Master unit type | Gu spoils: one line per mortal catalog Gu, `<with [N]% chance>` | 25 | tools/gu_catalog.py `SPOILS_CHANCE` |
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
| Burning | `[This Unit] takes [8] damage <upon turn start>` | 8 | data/path_statuses.csv `uniques` |
| Frozen | `[-1] Movement` | -1 | data/path_statuses.csv `uniques` |
| Frozen | `[-15]% Strength <when attacking>` | -15 | data/path_statuses.csv `uniques` |
| Bleeding | `[This Unit] takes [6] damage <upon turn start>` | 6 | data/path_statuses.csv `uniques` |
| Blinded | `[-2] Sight` | -2 | data/path_statuses.csv `uniques` |
| Blinded | `[-10]% Strength` | -10 | data/path_statuses.csv `uniques` |
| Soul-Torn | `[-15]% Strength` | -15 | data/path_statuses.csv `uniques` |
| Soul-Torn | `[-50]% XP gained from combat` | -50 | data/path_statuses.csv `uniques` |
| Dazed | `[-1] Movement` | -1 | data/path_statuses.csv `uniques` |
| Dazed | `[-10]% Strength` | -10 | data/path_statuses.csv `uniques` |
| Guard Broken | `[-20]% Strength <when defending>` | -20 | data/path_statuses.csv `uniques` |
| Entangled | `[-2] Movement` | -2 | data/path_statuses.csv `uniques` |
| Shocked | `[-25]% Strength` | -25 | data/path_statuses.csv `uniques` |
| Doomed | `[-10]% Strength` | -10 | data/path_statuses.csv `uniques` |
| Doomed | `[This Unit] takes [5] damage <upon turn start>` | 5 | data/path_statuses.csv `uniques` |
| Aged | `[-10]% Strength <when defending>` | -10 | data/path_statuses.csv `uniques` |
| Aged | `[This Unit] takes [5] damage <upon turn start>` | 5 | data/path_statuses.csv `uniques` |
| Weighted | `[-1] Movement` | -1 | data/path_statuses.csv `uniques` |
| Weighted | `[-15]% Strength <when defending>` | -15 | data/path_statuses.csv `uniques` |

### Terrains.json, Speeds.json

Vanilla copies (tools/gen_ruleset.py `Terrains (Vanilla minus natural wonders and Fallout)` and the Speeds line in `Nations (Difficulties)`); the only change is that no terrain grants an extra Spirit Spring. Tune them there if a playtest asks for it; until then the Vanilla numbers stand.

3973 numbers listed.

<!-- inventory:end -->
