# AUTOPLAY — headless AI-vs-AI data for tuning

The user's tuning rule (round 4): autoplay decides, with the Strategic Balance resource option on, and no manual
tuning before the data exists. The autoplay's rank-1 hunger death rate is the reference for raising the rank-1 hunger
threshold if the trade economy collapses too fast. This file records the runs; `tools/autoplay.py` reproduces them.

## Method

`tools/autoplay.py` compiles `tools/autoplay/Autoplay.java` against the Unciv 4.22.8 release jar and drives the
engine's own simulation path [src `ConsoleLauncher.kt`, `Simulation.kt`]: every major civ is AI, a Spectator watches,
`GameInfo.nextTurn` plays one round per step, and a snapshot is written after each round (one line per civ: stones,
upkeep, stones per turn and happiness by source (`goldBy`, `happyBy`, since Phase D), strategic resources and
deposits, buildings, units, Gu holders, hunger starts, deaths and recoveries, trades, wars). Setup: Small map, Prince, Standard speed, the four majors and three city-states, barbarians on, Strategic
Balance on, 100 turns.

Caveats: the engine's AI randomness is not tied to the map seed, so a seed does not reproduce a game; compare pooled
numbers, not single games. A hunger death is a Gu lost in the same round its hunger status ended, without a fusion;
snapshots are per round, so a death and a re-hunger inside one round would be missed (statuses last 3+ turns, so this
is rare). AI-only games say nothing about a human's experience.

## Baseline, 2026-10-17 (24 games x 100 turns, two batches of 12)

No crash in any game (also not in the 38 other games run while building the tool). Per clan, batch B (12 games, last
turn unless noted):

| Clan | Cities | Pop | Techs | Stones | Lowest stones | Turns below 0 | Units | Promotions bought | Upkeep / gross income |
|---|---|---|---|---|---|---|---|---|---|
| Gu Yue | 3.2 | 10.2 | 10.4 | 104 | 17 | 0.1 | 7.7 | 3.6 | 35% |
| Bai | 3.4 | 12.2 | 10.9 | 134 | 17 | 0 | 7.0 | 3.8 | 30% |
| Xiong | 3.3 | 10.9 | 10.3 | 176 | 25 | 2.0 | 8.2 | 3.4 | 38% |
| Wu | 3.2 | 12.4 | 10.8 | 135 | 18 | 0.4 | 8.2 | 4.6 | 36% |

* **Hunger meter (pooled, 24 games).** Rank-1 Gu: 6,573 holder-turns, 35 of them in deficit (0.5%), 16 hunger
  episodes, 6 deaths, 9 recoveries (deaths per episode 0.38, consistent with the 50% roll plus recoveries; 0.09 deaths
  per 100 holder-turns). Rank-2 Gu: 0 turns in deficit. The meter works in the engine (statuses, deaths and recoveries
  all occur), but the AI almost never runs a food deficit: every Gu grant is gated on a surplus, and nobody pillaged.
* **Trade.** 0.1–0.2 active deals per civ on average: there is no trade economy that could collapse.
* **Wars.** None in 2,400 civ-turns. The Vanilla control (below) has none either: Unciv's AI at Prince stays at peace
  in the first 100 turns; it is not this mod.
* **Wu vs Xiong.** No clash (no war). Xiong holds more pork (mean Wild Boar 3.8 vs 3.3). Wu buys more promotions (4.6
  vs 3.4, the Martial Arena's 20 XP) and holds slightly more rank-2 Gu (White Jade Gu at T100: 6 vs 2 over 24 games),
  but has no lead in cities, population, techs or units. Not overpowered at 100 turns.
* **Spirit Springs.** Strategic Balance works for ownership: every clan owns 1–2 springs from turn 10 (Wu 11/12 at T10,
  all by T30). The AI improves them late: an improved spring at T30 for 10 of 48 clans, at T50 for 14, at T100 for
  37. The Awakening Grounds (or Gu Yue's flower sea) is built by 27 of 48 clans, first at turn 80 on average.
* **Refinement.** By T100 each clan holds 1–3 rank-1 Gu and 0–1 rank-2 Gu; Killer Move was not measured (see the correction in round 5d).

Control: Unciv's Vanilla ruleset on the same harness (2 games, four majors): 2–6 cities, 4–11 units, 13–17 techs,
no wars, and idle settlers as often as here (0.24–0.47 per turn vs 0.32–0.50), so the AI's slow expansion is the
engine's, not the mod's.

## Experiments (throwaway variants; the mod is unchanged), 12 games each

| Variant | Improved spring T30 | T50 | T100 | Awakening wonder built | First turn |
|---|---|---|---|---|---|
| Baseline | 10/48 | 14/48 | 37/48 | 27/48 | 80 |
| Two starting Mortal Laborers | 18/48 | **30/48** | 41/48 | **35/48** | 74 |
| Spring Cave +5 stones instead of +3 | 5/48 | 15/48 | 41/48 | 29/48 | 86 |
| Spring Cave builds in 3 turns instead of 6 | 12/48 | 21/48 | 41/48 | 34/48 | 80 |

The bottleneck is labour, not the improvement's value: the AI keeps one laborer for most of the game (0.94 at T30).
A second starting laborer doubles the springs improved by T50 without hurting the economy (lowest stones and turns
below 0 unchanged). Not applied: it is the user's call.

## Verdict on the user's rule

The trigger condition is not met: rank-1 Gu die of hunger about once per 1,100 holder-turns, and there is no trade
economy to collapse. Per the rule, the rank-1 threshold stays at 2 turns (status length 3). The metric itself is weak
while the AI never trades and never fights; see the report to the user for alternatives.

## Round 5 (user's option B), 2026-10-17: King and Emperor, 200 turns, 12 games each

New metrics (the user's choice): the share of rank-1 Gu holder-turns in food deficit, and Gu hunger deaths per clan
per 100 turns; plus wars, captured cities and pillaged tiles. No crash in 30 games (24 + 6 control).

| Metric | King | Emperor | Vanilla control, King (6 games) |
|---|---|---|---|
| Rank-1 holder-turns in deficit | 0.17% (35 of 21,184) | 0.40% (122 of 30,610) | — |
| Gu hunger deaths per clan per 100 turns | 0.05 | 0.18 | — |
| Rank-2: turns in deficit / deaths | 0 / 0 | 10 / 0 (3 episodes, all recovered) | — |
| Games with a war | 4/12 | 5/12 | 5/6 |
| Clan-turns at war | 3.4% | 1.8% | 7.6% |
| Cities captured (at T200) | 0 | 1 | 6 |
| Pillaged tile-turns | 4,967 | 3,428 | 501 |

* **Hunger is irrelevant at every level tested.** Every clan ends with a surplus of every Gu food (mean over the game:
  Moon Orchid 3.8–6.4, Wild Boar 3.7–5.6, Jade 3.4–5.1, Wine 2.1–2.8), the other path's food included. Supply outruns
  the 7–11 rank-1 Gu a clan keeps. Rank-1 threshold: unchanged (the user's rule).
* **Conquest is broken.** Wars are half as frequent as in Vanilla and almost never take a city (1 in 24 games vs 6 in
  6). The only Slice 1 victory besides the score is domination, so in practice nobody can win. Not yet explained;
  candidates: city strength bonuses (Clan Head Pavilion, Formation Platform, Guardian Formations), ranged-only Moon
  armies (ranged units cannot capture), upkeep keeping armies small.
* **Wu vs Xiong: no dominance.** King: Xiong 4.5 cities, 28.5 units, White Jade Gu 7; Wu 4.2, 28.2, 5. Emperor: equal
  within noise. Pork is not scarce for either (mean 4.8–5.6), so there is nothing to clash over.
* **The refinement ladder stalls at rung 1.** At T200 the clans hold 7–11 rank-1 Gu each but 0.3–0.7 rank-2 Gu, and
  Killer Move is rare (re-measured in round 5d: 0.04 per clan; this line first said "none", which the tool could not
  see, see round 5d): the AI buys each unit's first attempt with the academy's starting XP and rarely earns the 20 XP
  for a second one in peace.
* **The tech tree runs out** at turn 113 (Emperor) to 123 (King) on average; the rest is Dao Comprehension.
* **Stones.** Upkeep rises from 20% of gross income (T1–50) to 60% (T151–200), but treasuries still grow (mean 420
  stones in T151–200): the AI stays solvent, the late game is not tense.
* **Pillage is 7–10 times Vanilla's:** the wolf tides and barbarians (who heal only by pillaging) hit tiles hard. Pillar
  3 shows up as pillage, not as deaths.

## Round 5b: why cities never fell, and the fix (2026-10-17)

**Cause** [src `CityCombatant.getCityStrength`]: a city gets + (share of the tech tree known x 5.5)^2.8 x
`cityStrengthFromTechsFullMultiplier` (default 1.0). That is +118 with every tech, and Slice 1's 15-tech tree is
complete by turn ~120, so every city became a modern-era fortress against Gu Masters of strength 8–32. The user gave
the choice ("bebas, yang seru seperti di novelnya"). Variants, King, 200 turns, 12 games each:

| Full multiplier | City bonus with every tech | Games with a war | Clan-turns at war | Cities captured | Clans eliminated |
|---|---|---|---|---|---|
| 1.0 (old default) | +118 | 4/12 | 3.4% | 0 | 0 |
| **0.1 (applied)** | +12 | 9/12 | 13.3% | 16 | 8 |
| 0.17 | +20 | 5/12 | 4.1% | 9 | 2 |
| 0.25 | +30 | 6/12 | 5.2% | 6 | 1 |
| Vanilla control (6 games) | — | 5/6 | 7.6% | 6 | — |

Chosen: 0.1, the bloodiest that keeps the AI solvent (lowest stones 6–13 on average). Confirmed on the mod itself
(12 games): wars in 9/12, 14 cities captured, 5 clans eliminated, no crash, no winner by turn 200; rank-1 Gu now meet
hunger (0.7% of holder-turns in deficit, 26 deaths, from pillaged camps and plantations).

**New imbalance it exposed:** Wu captured 10 cities and Xiong 4; Gu Yue and Bai captured none and were eliminated 2
and 3 times. Moon armies are ranged, and ranged units cannot capture cities [src]. See round 5c.

## Round 5c: Moon fights in melee and throws a moon blade first (2026-10-17)

Ranged units cannot take cities, and the documented unit unique `Before engaging in combat performs an extra ranged
attack with [amount]% of melee combat strength` gives a melee unit a free ranged strike before every clash with a
unit (never against a city [src `Battle.tryExtraRangedAttack`]). Moon Gu Masters became melee skirmishers that open
with a moon blade; Strength stays the hardest melee hitter. King, 200 turns, 12 games each, city multiplier 0.1:

| Variant | Captured by Moon clans | Captured by Strength clans | Clans eliminated | Gu Yue / Bai alive |
|---|---|---|---|---|
| Moon ranged 13/20/29 (before) | 0 | 14 | 5 | 10 / 9 of 12 |
| Melee 12/19/27, blade 50% | 3 | 8 | 4 | 11 / 9 |
| **Melee 13/20/29, blade 40% (applied)** | **5** | **8** | **2** | 12 / 10 |

Wu still leads (5.2 cities on average vs 2.8–4.0; 7 cities captured), consistent with the Wu clan's canon rank as the
Southern Border's first clan. Bai builds the smallest army (18.8 units) and hoards stones (742): its personality, not
the ruleset.

## Round 5d: cultivation unsticks the ladder (2026-10-17)

**Correction first.** Until this round `autoplay.py` counted only Gu that have a hunger meter. Killer Move eats
nothing, so it was never counted, and "Killer Move appears in none of the games" (baseline and round 5) was not a
measurement. The tool now records every promotion (`promotionHolders`).

Every Gu Master standing in a city with a Gu Academy (or Wu's Martial Arena, which replaces it) gains N XP per turn
until it holds a Killer Move (`[This Unit] gains [N] XP <upon turn start> <in cities with a [Gu Academy]> <for units
without [Killer Move]>`). King, 200 turns, 12 games each, per clan at turn 200:

| Variant | Rank-1 Gu | Rank-2 Gu | Killer Move | Attempts bought | Stones | Hunger deaths per clan per 100 turns |
|---|---|---|---|---|---|---|
| No cultivation (before) | 7.1 | 0.71 | 0.04 | 16.1 | 315 | 0.12 |
| **2 XP (applied)** | 6.0 | **5.1** | **2.8** | 38.8 | 187 | 0.45 |
| 3 XP | 5.8 | 5.4 | 3.7 | 42.7 | 205 | 0.82 |

The ladder now plays out: climbing costs XP, stones (the attempts and the higher rungs' upkeep) and food, and the
hunger meter matters. 2 XP chosen: the slower climb. The aptitude die checks out in the same data: A 8%, B 27%,
C 31%, D 33% of Gu Masters.

## Round 6: wild Gu and buried inheritances (2026-10-18)

The user asked for wild Gu (about 1.2%) and for inheritances the clans fight over. Each Gu Master rolls 6% per
turn and 1 in 5 of those is a real wild Gu (1.2%); in foreign land after Inheritance Lore it rolls 1% per turn for a
rumour, and the rumour is real 1 in 2 (1 in 8 first gave only 0.42 inheritances per game). King, 200 turns, 12 games:

| Measure | Before round 6 (round 5d) | Round 6 |
|---|---|---|
| Inheritances held at T200 per game | — | 1.25 (8 of 12 games; Gu Yue 2, Bai 4, Xiong 4, Wu 5) |
| Wild Gu per clan at T200: Jade Skin / Black Boar / Liquor Worm | 0.08 / 0 / 0 | 1.50 / 2.40 / 0.02 |
| Rank-2 Gu / Killer Move per clan | 5.1 / 2.8 | 4.8 / 3.0 |
| Hunger deaths per clan per 100 turns | 0.45 | 0.52 |
| Games with a war / cities captured / clans eliminated | 2/12 / 6 / 3 | 5/12 / 3 / 3 |

Wild Gu add mouths; whether hunger bites more cannot be read from one batch (round 6b: identical batches differ
twofold). The ladder is unchanged; nothing crashed.

## Round 6b: replication, and how many games a metric needs (2026-10-18)

Two more 12-game batches (King, 200 turns): one on the round-6 commit, one with the step-9 inheritance guard
(`<in tiles without [resource]>`). The first batch and the round-6 batch ran the same ruleset with the same harness.

| Batch | Hunger deaths per clan per 100 turns | Rank-1 deaths (per 100 holder-turns) | Inheritances per game | Wild Jade Skin / Black Boar per clan | Rank-2 Gu / Killer Move per clan | Games with a war / captured / eliminated | Clans 20+ turns in the red |
|---|---|---|---|---|---|---|---|
| Round 6 (above) | 0.52 | 22 (0.06) | 1.25 | 1.50 / 2.40 | 4.8 / 3.0 | 5 / 3 / 3 | 0 of 48 |
| Same ruleset, again | 1.04 | 67 (0.18) | 2.00 | 1.48 / 2.15 | 4.8 / 2.8 | 4 / 6 / 1 | 2 of 48 |
| With the inheritance guard | 1.13 | 74 (0.20) | 2.00 | 1.67 / 2.02 | 4.9 / 2.7 | 4 / 7 / 1 | 2 of 48 |
| **Pooled, 36 games** | **0.90** | 163 (0.15) | **1.75** | 1.55 / 2.19 | 4.8 / 2.8 | 13 / 16 / 5 | 4 of 144 |

* **Hunger deaths vary twofold between identical 12-game batches** (AI randomness is not seeded). The round-6 figure
  0.52 was a low draw; use the pooled 0.90, and pool at least 36 games before tuning on this metric. Ladder, wild Gu
  and inheritance figures are stable within about 25%.
* The guard changes nothing measurable (inheritances 2.00 vs 2.00).
* The user's rule: rank-1 Gu still die about once per 670 holder-turns and there is still no trade economy, so the
  rank-1 threshold stays.
* **Solvency:** 4 of 144 AI clans spent 20 or more turns with a negative treasury, all of them clans at war. None
  fell into a disband spiral: the worst (Xiong, 41 turns, low of −144 stones) still fielded 24 units at turn 200.

## Round 7: the user's pop-1 capital, event population costs and game speed (2026-10-18)

The user's capital (human Wu, Marathon, turn 321) sat at population 1 with a food surplus of exactly 0. The direct cause
was in the game, not the ruleset: its focus was Production, so its one citizen worked a 0-food hill tile, and a human
city does not re-check its tiles each turn [src `CityTurnManager.startTurn`] (docs/KNOWN_ISSUES.md, engine limit 10).
A five-way investigation (citizen ranking, a human-flagged simulation, events, ruleset food, Wu's terrain; engine
probes, adversarially checked) found three faults in the mod that drain population on every speed:

* "Abandon the outer fields" took a citizen from every city on every beast tide, and the capital population costs
  ("Judge the traitor", "Strike first", "Squeeze the mortals") were free rewards at population 1. With all four clans
  answering events but never taking a population choice, capitals averaged 8.4 at turn 320 (Standard); with the AI's
  weights, 1.8-4.
* Every random event rolled per turn whatever the speed, so Marathon met three times the tides, betrayals and stone
  shortages per era.
* The simulation mode drops a human civ's Alert events, so autoplay keeps every civ AI.

Fix: Abandon halves growth in every city for 10 turns; the capital population costs need more than 3 population;
event chances divide by the speed modifier and turn gates multiply by it (`<on [speed] game speed>`, whole-number
chances); the wild-Gu and inheritance dice keep their rate per era. Verified in the engine: Abandon took a city's
surplus from 5.0 to 2.5 with population unchanged and expired after 10 turns. Prince, Small, 4 clans:

| Run | Cities at pop 1 | Pop per city | Capital pop | Hunger deaths per clan per 100 turns | Pillaged tile-turns | Clans 20+ turns in the red |
|---|---|---|---|---|---|---|
| Standard, 320 turns, 12 games, before | 17.1% | 5.12 | 2.92 | 0.42 | 7,259 | 40 of 48 |
| Standard, 320 turns, 12 games, round 7 | **2.4%** | 5.28 | 3.60 | 0.51 | 9,855 | 38 of 48 |
| Marathon, 480 turns, 6 games, before | 19.3% | 3.02 | 2.38 | 0.42 | 18,357 | 12 of 24 |
| Marathon, 480 turns, 6 games, round 7 | **3.4%** | **4.32** | **4.43** | 0.18 | 7,993 | **3 of 24** |

* Pop-1 cities nearly vanish on both speeds; Marathon now plays like Standard per era (pillage halves, treasuries
  recover).
* **New, and not caused by round 7:** at Prince on Standard, 40 of 48 clans spend 20+ turns in the red by turn 320
  (mean treasury about −65 at the end), before and after. Unit upkeep grows with the turn number [src
  `getUnitMaintenance`] and the tech tree ends near turn 120, so late armies outgrow income; King's AI upkeep discount
  (round 5-6: 4 of 144) hides it. Constant stone shortages also hold capitals near the new gate (3-4 population)
  through "Squeeze the mortals". Next step: the late-game stone economy.

## Round 8: the late-game stone economy (2026-10-18)

Where the stones went at Prince, Standard, turn 320 (round 7): upkeep took 111% of gross income in the last quarter
of the game, and about 10 of a clan's 23 units were Mortal Laborers, each paying the base upkeep of a unit. Unit upkeep grows with the turn number [src `getUnitMaintenance`: (0.5 × N × (1 + g))^(1 + g/3), g = turn /
total turns], so a fixed army costs about twice as much at turn 320 as at turn 100. Six throwaway variants (12 games
each, Prince, Small, 4 clans, Standard, 320 turns; the same seeds):

| Variant | Clans 20+ turns in the red | Treasury T320 | Stones per turn T320 | Upkeep / gross T1–50 | Upkeep / gross T241–320 | Units T320 |
|---|---|---|---|---|---|---|
| Round 7 (shipped) | 38 of 48 | −69 | −8.3 | 0.21 | 1.11 | 22.8 |
| v1: mortals pay no upkeep | 26 | −4 | −3.4 | 0.14 | — | 22.5 |
| v2: v1 + Rank One +25% → +50% | 23 | −6 | −4.6 | 0.17 | — | 22.6 |
| v3: v1 + ranks 3–4 cheaper (Strength +125 / +175, Moon +100 / +150) | 15 | 101 | 0.1 | 0.16 | — | 24.8 |
| v4: v1 + Trading House 4 stones, +35% | 10 | 411 | 6.0 | 0.16 | — | 24.9 |
| **v5: v2 + v3 (shipped)** | **11** | **101** | **2.8** | **0.17** | **0.90** | 24.6 |
| v6: v5 + the v4 Trading House | 3 | 719 | 11.5 | 0.16 | — | 25.5 |

* Free mortals alone cut the red clans by a third; the rest of the deficit is rank 3–4 Gu Masters, whose upkeep
  multipliers (up to +275%) compound with the turn-number growth. v3 halves the deficit again without making clans
  rich.
* Rank One +50% puts back early pressure that free mortals took out (0.14 → 0.17 of gross income in T1–50).
* A richer Trading House (v4, v6) ends the deficits but piles up 400–700 stones by turn 320: no late tension, and
  "What the data says is off" item 2 already says the late game is too calm. Rejected.
* v5 keeps the worst clans' armies (no disband spiral) and the AI still loses clans to war (1 city captured).

v5 on the other speeds and difficulty:

| Run | Clans 20+ turns in the red | Treasury at the end | Stones per turn at the end | Upkeep / gross, last quarter | Capital pop | Pop per city | Crashes |
|---|---|---|---|---|---|---|---|
| Marathon, Prince, 480 turns, 6 games, round 7 | 3 of 24 | 148 | 10.0 | 0.65 | 4.43 | 4.32 | 0 |
| Marathon, Prince, 480 turns, 6 games, v5 | 2 of 24 | 276 | 15.4 | 0.41 | 4.54 | 4.58 | 0 |
| King, 200 turns, 12 games, round 7 | 1 of 48 | 180 | 9.9 | 0.64 | 8.69 | 8.16 | 0 |
| King, 200 turns, 12 games, v5 | 0 of 48 | 607 | 32.6 | 0.38 | 8.43 | 7.94 | 0 |

* Marathon and King stay solvent and keep their population; at King the treasury in T151–200 rises from 244 to 431
  stones on average, so "the late game is not tense" (BALANCE.md item 2) gets worse in stones. The same King batch
  saw more war (7 of 12 games with a war, 16 cities captured, against 3 and 2), but war counts swing widely between
  12-game batches (round 6b), so that is a lead, not a result.
* Hunger is unchanged (King 1.07 → 0.96 Gu deaths per clan per 100 turns).

## C3 M7: rank chain and 47 paths against round 8 (2026-10-19)

The C3 mod (path promotions, clan chains, legacy bridge) against round 8's shipped v5, two 12-game batches each
(different seeds), Small, 4 clans, Standard speed, Strategic Balance on:

| Batch | Clans 20+ turns in the red | Treasury T320 | Stones per turn T320 | Upkeep / gross T151–320 | Rank-2 Gu per clan T200 | Gu deaths per clan per 100 turns | Crashes |
|---|---|---|---|---|---|---|---|
| Prince 320, v5, batch 1 | 11 of 48 | 101 | 2.8 | 0.77 | 3.79 | 0.63 | 0 |
| Prince 320, v5, batch 2 | 12 of 48 | 89 | −0.1 | 0.77 | 3.53 | 0.59 | 0 |
| Prince 320, C3, batch 1 | 18 of 48 | 111 | 2.6 | 0.80 | 1.58 | 0.79 | 0 |
| Prince 320, C3, batch 2 | 12 of 48 | 122 | 0.2 | 0.81 | 1.46 | 0.59 | 0 |

| Batch | Games with a war | Cities captured | Share of clan-turns at war | Gu deaths per clan per 100 turns | Crashes |
|---|---|---|---|---|---|
| King 200, v5, batch 1 | 7 of 12 | 16 | 0.112 | 0.96 | 0 |
| King 200, v5, batch 2 | 0 of 12 | 0 | 0.000 | 1.29 | 0 |
| King 200, C3, batch 1 | 4 of 12 | 6 | 0.037 | 0.53 | 0 |
| King 200, C3, batch 2 | 5 of 12 | 4 | 0.029 | 0.53 | 0 |

Paths (end of game, all batches): one root path per AI unit (the few extra Masters are sub-paths, which need their
parent); 84–86% of the signature clans' cultivators on the signature path (Prince 472 of 547 and 431 of 507, King 672
of 795); 41–45 different paths in a batch among the other 15%.

* **Solvency: no change beyond noise.** Pooled 30 of 96 red clans against 23 of 96 (the two C3 batches alone gave 18
  and 12), with a higher treasury at turn 320. The red turns sit in T240–319 as before. No re-tune.
* **Conquest: no change beyond noise.** Round 8's two King batches gave 16 and 0 captured cities; C3 gives 6 and 4.
  City strength (E8) stays at 0.1.
* **The ladder: half the rank-2 Gu.** Bai now walks Water (the user's decision), which has no fusion ladder: its units
  stop at Jade Skin Gu. Every path except Moon and Strength is in the same place until it has its own Gu (decision
  B.b, next step).
* **Hunger is lower** (King 0.53 against 0.96–1.29): fewer clans compete for moon orchids.

## Phase D: the Five Regions economy (2026-11-01)

Eight majors, Prince, seed 261, 6 games per batch (`--map "maps/Five Regions"`; Qing Mao Mountain with the same eight
majors as the reference). Clans 20+ turns in the red / in the red at the end / mean stones per turn at the end:

| Batch | Turns | Red 20+ | Red at end | Stones/turn |
| --- | --- | --- | --- | --- |
| Five Regions, start rings only | 400 | 42 / 48 | 14 | −12.6 |
| Five Regions + riches | 400 | 32 / 48 | 12 | −10.9 |
| Five Regions + riches | 280 | 18 / 48 | 14 | −5.9 |
| Five Regions + riches + stability | 280 | 14 / 48 | 8 | −9.0 |
| Qing Mao Mountain | 300 | 9 / 48 | 10 | −1.5 |
| Qing Mao Mountain + stability | 300 | 10 / 48 | 5 | +1.3 |

Stability (−33% unhappiness from villages, Tavern +2) raised the Five Regions population at T280 from 18 to 27; the
extra people became production and soldiers, so stones per turn fell while fewer clans ended in the red. Sources at
T280 (Five Regions): tiles +21, buildings +19, trade routes +16; unit upkeep −35, building upkeep −18, roads −11.
Details and levers: BALANCE.md "The Five Regions economy".

## Phase D: path power scaling (2026-11-02)

Five Regions, eight majors, Prince, seed 401, 6 × 350, per game (captured cities, clans destroyed):

| Batch | Per game | Total | Red 20+ |
| --- | --- | --- | --- |
| Before (flat tiers) | (3,1) (4,2) (0,0) (2,1) (2,1) (5,2) | 16, 7 | 25 / 48 |
| Hits on attack and defence | (5,1) (1,0) (2,0) (0,0) (1,0) (0,0) | 9, 1 | 32 / 48 |
| Hits on attack only (shipped) | (4,2) (2,1) (6,2) (6,2) (5,1) (4,1) | 27, 9 | 23 / 48 |

0 crashes in all three. Defenders hit back at melee besiegers while cities take no hits, so two-way hits stalled
conquest; attack-only hits make the attacker's path decide the fight.

## Phase D: immortal lifespan and the hunger meter (2026-11-02)

Five Regions, eight majors, Prince, seed 501:

| Batch | Immortals per clan T250 / T350 | Lifespan Gu stock T350 | Rank eight | Venerable (first) | Eternal Life |
| --- | --- | --- | --- | --- | --- |
| Before (grant 5, one each 10 turns), 6 × 400 | 1.24 / 2.15 | 6.4 | 2 clans | none | none |
| Lifespan by rank, Eternal Life 150, 6 × 400 | 1.49 / 3.14 | 107 | 10 clans | 6 of 6 (T314–378) | 4 of 6 (T345–382) |
| Lifespan by rank, Eternal Life 300, 6 × 450 | 1.51 / 3.55 | 106 | — | 6 of 6 (T332–394) | 5 of 6 (T391–443) |

Hunger meter (Qing Mao, eight majors, 6 × 300 before, 12 × 300 after): deaths per hunger start at rank one 0.46 → 0.50,
rank two 0.31 → 0.35 (the roll timing is unchanged; the harness now counts a death while the 100% step is still shown).
One crash in about 30 games on this code: a free upgrade in the ascension chain could neither place the immortal nor
restore the Gu Master (NullPointerException in UnitUpgradeManager.performUpgrade); the harness now records where every
Gu Master stood, so the next occurrence names the tile (KNOWN_ISSUES 20).

## Phase D: regional conflict (2026-11-02)

The user found no conflict outside the Southern Border. The Five Regions map was played 4 games × 200 turns (Prince,
Small, every city-state), before and after each change. The harness now records two more things: the city-states each
major is at war with (`csWars`), and the barbarian units within 4 tiles of a clan's city (`barbNear`).

| Run | Arc majors' turns at war with a major | Arc majors' turns at war with a city-state | City-states conquered |
|---|---|---|---|
| Wild factions only (seeds 21-24) | 0 | 70 | 2 |
| + warlike arc temperaments, raids on minor clans (21-24) | 0 | 194 | 3 |
| same (31-34) | 0 | 231 | 4 |
| + Eastern Sea raids (31-34, final) | 0 | 17 | 0 |

AI randomness is not tied to the seed, so the last two rows show how wide the noise is.

The share of turns (T40+) with raiders near a city, final run:

| Region | Clans and share of turns |
|---|---|
| North | Huang Jin 89%, Ge 55%, Man 39%, Lang Ya 38% |
| West | Fang 81%, Mo 55%, Xiao 37%, Lan 31% |
| Centre | Heavenly Court 64%, Spirit Affinity 39%, Immortal Crane 31%, Combat Immortal 30% |
| South | Gu Yue 69%, Wu 67%, Xiong 40%, Bai 34% |
| East | Song 41%, Zombie Alliance 12%, Xia 9%, Merman court 8% |

**Verdict.** Every region now has fighting.
* **North, west and centre:** raiders stand near a clan's cities half the turns or more.
* **Minor clans:** the warlike majors sometimes swallow one. Huang Jin took the Man Tribe in 4 of 12 games.
* **Arc majors:** they still never declare war on each other. The region walls keep them apart, and the AI declares
  war only when happiness is above 0, it has 4 soldiers and one per city, and its population is 12 or more [src].
* **Eastern Sea:** it stays the quietest. On its small islands a raider spawns beside a city and dies within a turn or
  two. Four times the raid rate only moved it from 7% to 12%.

## Phase D: power rebuild (2026-11-02)

The user wanted power to depend on Gu, with dao marks and comprehension carrying a Gu-less fighter. The changes:

* **The body alone is weaker.** A cultivator's base strength is 75% of its old value at ranks 1-2, 65% at ranks 3-5
  and 60% at ranks 6-9 (`tools/path_powers.py` `body_strength`).
* **Comprehension.** The path tiers go from +10/15/20/25% to +20/25/30/35%.
* **Dao marks.** They go from +5/10/15/20/30% to +10/20/30/40/55%.
* **Catalog Gu.** Attack and defence Gu get 8+4×rank %, strength Gu 5+3×rank %.

All runs were Five Regions, 6 games × 300 turns on Prince. "Base" is the commit before the change.

| Run | Majors alive | Cities captured | Immortals at T300 | Soldiers at T300 | Barbarians at T300 | Major-turns in the red |
|---|---|---|---|---|---|---|
| Base | 7.2 | 1.7 | 19.8 | 104 | 40 | 173 |
| Body cut only for clan cultivators | 7.0 | 2.7 | 15.5 | 87 | 77 | 138 |
| + rogues at 80%, ranks 3-5 at 65% (final) | 7.2 | 2.0 | 20.0 | 97 | 35 | 128 |

The first variant cut only the clans' cultivators. The barbarian Gu Masters kept their full strength, so they doubled
and the immortals fell by a fifth. The final variant also scales the rogues: they carry Gu but no clan's
comprehension, so they keep 80%. It matches the base within the noise. City strength (E8) needs no retune, because
conquest is unchanged.

## Phase D: one-of-a-kind immortal Gu (2026-11-02)

Five Regions, 4 games × 400 turns, Prince. The question: does the AI build the immortal Gu wonders and raise their
bearers, and does each Gu ever have two bearers at once?

| Run | Wonders built (canon / catalog) | Bearers at T400 per game | Most bearers of one Gu |
|---|---|---|---|
| Bearer needs the path's Master; catalog wonders at AI weight +100% | 10-16 / 0 | 0, 2, 1, 0 | 1 |
| No path prerequisite; catalog wonders at +300% (final) | 7-13 / 0-4 | 9, 9, 2, 16 | 1 |

The AI's units each walk one path, so they rarely matched their clan's wonders: only 3 bearers came up in four games.
Canon lets any immortal with the essence use an immortal Gu, so the bearer now needs only the rank. The path's
comprehension still gates the Gu's combination moves, which only a human presses anyway. Uniqueness held in every
game: never two bearers of one Gu.

## Phase D: every policy branch from the first era (2026-11-02)

The user asked for every policy branch to open without waiting for an era. The setup was Five Regions, 6 games × 300
turns, Prince, seeds 51-56, with "Base" as the commit before the change.

| Run | Majors alive | Cities captured | Immortals at T300 | Soldiers | Barbarians | Major-turns at war | Major-turns in the red | Policies adopted (all games) |
|---|---|---|---|---|---|---|---|---|
| Base (branches by era) | 7.3 | 2.3 | 17.8 | 99 | 47 | 202 | 150 | 537 |
| All branches in the first era | 6.7 | 2.7 | 17.3 | 92 | 51 | 398 | 124 | 514 |

The AI is no weaker: it keeps as many immortals and adopts as many policies. It went to war more often, but war turns
range from 22 to 721 per game, so that difference is within the noise. One game ended with 5 majors after 7 captures.

## Phase D: the mechanics audit's four changes (2026-11-03)

The user chose four audit proposals: the immortal chasm, Gu spoils, AI killer moves and even Supremes
(MECHANICS_AUDIT.md). The test setup was Five Regions, 18 games x 300 turns, Prince, seeds 51-68. "Base" is the
commit before P4 (15cc2ac). The harness now records statuses held at each snapshot and promotions gained without a
purchase.

| Run | Majors alive | Cities captured | Immortals at T300 | Soldiers | Barbarians | Major-turns at war | Major-turns in the red | Clans 20+ turns red | Treasury T300 |
|---|---|---|---|---|---|---|---|---|---|
| Base | 7.2 | 1.7 | 17.4 | 95 | 42 | 280 | 146 | 2.8 | 124 |
| P1-P4 | 7.2 | 2.3 | 17.9 | 93 | 45 | 228 | 159 | 2.9 | 134 |

* **The AI uses its killer moves.** Per game, 129 mortal-move statuses and 36 immortal-move statuses were seen at
  round ends; base had none. This is a lower bound: a snapshot sees only moves still active. The clans that fight
  most use the moves most, and they are not the ones in the red. Gu Yue used 256 in the first six games and had 27
  red turns. Red turns gather in the arc majors, which never go to war (KNOWN_ISSUES 21).
* **Spoils work but are rare between AIs.** 1.6 Gu changed hands per game, against about 118 catalog Gu held at
  T300. Most AI kills are made by cities or against beasts, and the harness counts only the eight majors' units.
* **No weaker AI, no poorer AI.** Every measure is within the noise. The first six games alone showed red turns at
  134 against 200; the next twelve did not repeat it.

## Phase D: immortal materials and the vital Gu (2026-11-03)

The setup was Five Regions, Prince, 300 turns. "Base" is P1-P4 (26 games: seeds 51-68 and 101-108). "P5+P6" is the
same seeds on 841cd4d (materials 15/20/25/40) and 375376b (doubled). SE is the standard error of the difference.

| Metric | Base | P5+P6 | Difference | SE |
|---|---|---|---|---|
| Majors alive at T300 | 7.2 | 6.9 | -0.3 | 0.2 |
| Cities captured | 2.3 | 2.7 | +0.4 | 0.6 |
| Immortals at T300 | 17.2 | 16.6 | -0.6 | 0.9 |
| Soldiers at T300 | 94 | 91 | -3 | 4 |
| Major-turns in the red | 153 | 155 | +3 | 16 |
| Clans 20+ turns red | 3.0 | 2.9 | -0.1 | 0.3 |
| Immortal Gu wonders per game | 2.7 | 2.5 | -0.2 | 0.4 |
| Immortal Materials at T300 (median clan) | 6 | 95 | +90 | 9 |

* **Materials no longer gate the race.** With costs of 15/20/25/40, the AI held 41-195 materials when it began a
  wonder (median 108), so the cost never bit. The costs were doubled, which would have delayed none of those 42
  builds. Most measures move by less than their noise. The largest is majors alive at 1.5 SE; watch it.
* **The vital Gu fires.** The harness records each unit's HP change between the snapshots around a starvation death.
  For the eight path Gu, it moved from +0.1 (918 deaths in 8 games) to -10.3 (668 deaths), lower in every one of
  the 8 games (-7 to -19). Other Gu stayed near zero (-0.1, then -1.6). It is not -30 because healing comes between snapshots,
  units at 30 HP or less take nothing, and a unit holding White Boar or Moonlight Gu without the path's Master is spared.
* **Hunger is the White Boar's.** White Boar Gu makes up about four starvation deaths in five (80-100 per game over
  8 clans). Wild Boar runs short wherever the Strength path spreads; the Master hands the Gu back once boar is in
  surplus, so the meter cycles. Not changed here: a balance question of its own.

## Phase D: tension targets (2026-11-03)

Five Regions, Prince, seeds 101-108. The runs are snapshots of a commit (git worktrees), because the harness copies
`jsons/` when each game starts.

**Long games, 8 × 450 turns** (aabaf80: P1-P6 and the White Boar fix). No crash. Rank seven was reached in 8 of 8
games (T247-291), rank eight in 8 (T320-377), a Venerable in 8 (T340-406). Five games ended with a victory at
T403-446. The AI built 1-3 immortal Gu wonders by T300 and 5-20 by the end, of 66. The arc majors were never at war
with each other (KNOWN_ISSUES 21). After T300 a third of AI clan-turns ran in debt, at -21 stones a turn on average,
and every game touched the -200 disband line (3-40 snapshots).

**White Boar loop.** Starvation deaths of White Boar Gu by T300: 79 per game before the fix (ab_v_new, 8 games), 0.2
after (the first 300 turns of the long games).

**Halls, 8 × 300** (4569c5a against aabaf80's first 300 turns). Share of root Masters on the signature path:

| Clan | Before | After |
|---|---|---|
| Gu Yue (Moon) | 89% | 85% |
| Bai (Water) | 69% | 86% |
| Xiong (Strength) | 87% | 86% |
| Wu (Wind) | 57% | 73% |

Wu still builds Strength Halls (28 in 8 games), with fewer units from them: at T300 its root Masters were Wind 50 and
Strength 10 (before: Wind 19, Strength 36).

**AI late-game upkeep relief, 8 × 450** (86d0f7d against aabaf80):

| Metric | Before | After |
|---|---|---|
| Clan-turns in debt after T300 | 32% | 10% |
| Snapshots at the -200 disband line per game | 19.6 | 2.8 |
| Stones per turn after T300 | -21 | -8 |
| Majors alive at the end | 6.6 | 6.8 |
| Soldiers at the end (all majors) | 89 | 112 |
| Immortals at the end | 35 | 41 |
| Games won before T450 | 5 | 4 |

## Regions as canon (2026-11-08)

Five Regions map, 8 × 450, seed 101, AI only. Baseline aabaf80 + the AI upkeep relief (`late450`); the regions build
8e02019 (`reg450`); the same with the Huang Jin contest and war economy toned down, 8f54dbc (`reg2_450`). Means per civ
of each region (majors and city-states together), at T300.

| Region | Techs (base / build / tuned) | Immortals (base / build / tuned) | Turns at war with a major |
|---|---|---|---|
| Central Continent | 20.9 / 23.9 / 23.8 | 1.9 / 4.6 / 4.2 | 0 / 26 / 8 |
| Northern Plains | 19.2 / 21.4 / 21.0 | 1.8 / 4.2 / 2.8 | 0 / 34 / 8 |
| Eastern Sea | 20.1 / 20.5 / 20.8 | 2.4 / 3.6 / 2.8 | 0 / 0 / 0 |
| Western Desert | 18.2 / 19.0 / 18.4 | 0.5 / 1.5 / 0.9 | 0 / 0 / 0 |
| Southern Border | 19.0 / 20.1 / 19.8 | 2.5 / 2.2 / 2.6 | 242 / 144 / 232 |

| Arc majors | Base | Build | Tuned |
|---|---|---|---|
| The Court fights a city-state (games) | 2 of 8 (took Spirit Affinity House twice) | 0 | 0 |
| The Huang Jin fight the northern tribes (games, turns) | 5 of 8, 1145 | 8 of 8, 1905 | 7 of 8, 1673 |
| The Fang clan conquers in the desert (games) | 1 of 8 (took Lan and Xiao) | 0 | 0 |
| Huang Jin cities at T150 | 4.5 | 7.4 | 6.8 |
| First rank eight: the Court | T371-425 (3 games) | T278-335 (5) | earliest in most games |
| Venerables (games) | Bai 3, Wu 3, Xiong 1, Huang Jin 1, Court 1 | Huang Jin 5, Court 2 | Court 5, Wu 1, Bai 1, Huang Jin 1 |
| Eternal Life wins | Wu 2, Bai 2 | Huang Jin 3 | Wu 1, Bai 1, Huang Jin 1 |
| Clan-turns in debt, Huang Jin | 15% | - | 23% |

* The regions now stand in canon order: the Central Continent ahead in techs and immortals, the plains second, the
  sea third, the desert last.
* The Court never declares war. In the build's game 108 the Huang Jin raised a Venerable at T337, declared war on
  the Court at T341 and razed it by T357; the Immortal Tomb did not wake, as the Court already had four rank sevens
  (the cap is three). The tuned run had no such game.
* The contest's XP had lasted as long as the gap between contests, so the plains trained every Gu Master with it; with
  +5 happiness the tribes settled and conquered to 7.4 cities by T150 and took every Venerable race the Court did not.
  The tuned numbers (XP for 5 turns, +3 happiness) keep the northern wars and spread the wins again.
* The Court, the strongest region, raises the Venerable in 5 of 8 tuned games. It cannot seek Eternal Life, so while
  it lives no one wins that way (docs/REGIONS.md, open question).
* Debt rose with the wars: Huang Jin in the red on 23% of turns (15% before), snapshots at the -200 line 10.4 per game
  (2.8).

## Regions II: the ten sects, the Refinement Conference (2026-11-08)

Five Regions map, 8 × 450, seed 101: the tuned regions build 8f54dbc (`reg2_450`, 3 sects); Regions II 60b633e (`r2b`,
all ten sects and the Wan clan, 31 civs); the same with the sects moved to the region's rim, 05c93a8 (`r2c`). No crash
in 24 games with 31 civs.

| The Heavenly Court | 3 sects | 10 sects around the Court | 10 sects on the rim |
|---|---|---|---|
| Cities at T300 | 5.1 | 3.4 | 5.6 |
| Techs at T300 | 23.8 | 22.4 | 23.5 |
| Immortals at T300 | 4.2 | 2.0 | 5.9 |
| Venerables (games) | 5 | 0 | 5 |

| All majors | 3 sects | 10 sects around | 10 sects on the rim |
|---|---|---|---|
| Venerables (games) | Court 5, Wu 1, Bai 1, Huang Jin 1 | Bai 5, Huang Jin 2, Gu Yue 1 | Court 5, Huang Jin 2, Wu 1 |
| Eternal Life wins | Wu, Bai, Huang Jin | Bai 4, Huang Jin 1 | Huang Jin, Wu |
| Clan-turns in debt after T300 | 10% | 14% | 8% |
| Sects destroyed | - | 0 | 0 |

* **The Refinement Conference fires** for every major at T130, T260 and T390. At T130 most clans buy 8 materials at
  the fair; the rich enter the contest (+20) more often later.
* **The Wan Coalition never fired:** the Fang clan never held more than three cities.
* **Ten sects around the Court boxed it in**: the Venerable race then went to the Bai clan. On the rim the Court is
  back to the strongest.
* **The Court strikes back.** In one rim game the Huang Jin declared war on the Court around T240; the Court, which
  never declares war itself, took two of their cities and the tribes fell (208 turns at war).
* **Fewer decided games.** With the Court raising the Venerable in 5 of 8 games and barred from Eternal Life, only 2
  of 8 games ended in an Eternal Life win (`docs/REGIONS.md`, open question).

## Reference audit layers (2026-11-08)

Five Regions, 8 × 450, seed 101. Baseline: Regions II with the sects on the rim (05c93a8, `r2c`). Layers 1-2 (4cbadd2,
`l2`); Layers 3-4 with the Court barred from rank nine (6edf4a8, `l4`).

| | Baseline | Layers 1-2 | Layers 3-4 |
|---|---|---|---|
| Eternal Life wins | Huang Jin, Wu | Wu | Huang Jin 2, Wu, Gu Yue, Bai |
| Venerables (games) | Court 5, Huang Jin 2, Wu 1 | Court 7, Wu 1 | Huang Jin 4, Wu 2, Gu Yue 1, Bai 1 |
| First rank seven / eight | T232-266 / T294-346 | T222-275 / T279-358 | T214-255 / T280-313 |
| The Court at T300 (cities, techs, immortals) | 5.6, 23.5, 5.9 | 4.9, 23.9, 5.9 | 5.6, 23.2, 5.8 |
| Gu Masters per major at T300 / at the peak stage | 9.7 / - | 10.8 / 5.8 | - |
| Extreme physiques per major at T300 | - | 0.02 | - |
| Rank relics bought (holder snapshots, 8 games) | - | 349 | - |
| Clan-turns in debt after T300 | 8% | 10% | 15% |
| Stones per turn after T300 | -10.5 | -13.4 | -9.3 |

* **Layer 1 bug found by autoplay:** the stage promotions and the extreme physique carried unitTypes, so they were for
  sale; the AI bought the physique as a plain +20% promotion (53 of 77 Gu Masters at T300). Fixed in 4cbadd2.
* **Stages work:** about half the Gu Masters stand at their rank's peak at T300. The AI buys rank relics and climbs the
  fusion chains (Black Mane 4, Steel Mane 2, Stealth Scales 3 holders at most).
* **The Court's Venerable:** with the stages the Court took the one Venerable slot in 7 of 8 games and, barred from
  Eternal Life, left one win in eight. Barred from rank nine (canon: its present leaders are rank eight), the race is
  open again: 5 games of 8 end in an Eternal Life win, spread over four clans.
* **The beast kings:** frenzy wolves replace part of the bold wolves and demonic elders in the camps; the barbarian
  total stays lower than before (T150 61 vs 67, T250 35 vs 42).
* **The variant humans:** the Huang Jin razed the snowmen in 5 of 8 games. An immortal's blessed land shields them in the
  canon, so their city now has +50% strength like the great sects'. The other three kinds survived every game.
* Region order holds in every run: Central > North > East > South > West in techs and immortals at T300.

## Re-run

```
tools/autoplay.py --games 12 --turns 100 --jobs 3 --out /tmp/ap      # about 1 minute on 4 cores
tools/autoplay.py --games 12 --turns 200 --jobs 3 --difficulty King --out /tmp/apk   # about 2 minutes
tools/autoplay.py --summarize /tmp/ap
```
