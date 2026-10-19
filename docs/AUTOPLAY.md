# AUTOPLAY — headless AI-vs-AI data for tuning

The user's tuning rule (round 4): autoplay decides, with the Strategic Balance resource option on, and no manual
tuning before the data exists. The autoplay's rank-1 hunger death rate is the reference for raising the rank-1 hunger
threshold if the trade economy collapses too fast. This file records the runs; `tools/autoplay.py` reproduces them.

## Method

`tools/autoplay.py` compiles `tools/autoplay/Autoplay.java` against the Unciv 4.22.8 release jar and drives the
engine's own simulation path [src `ConsoleLauncher.kt`, `Simulation.kt`]: every major civ is AI, a Spectator watches,
`GameInfo.nextTurn` plays one round per step, and a snapshot is written after each round (one line per civ: stones,
upkeep, strategic resources and deposits, buildings, units, Gu holders, hunger starts, deaths and recoveries, trades,
wars). Setup: Small map, Prince, Standard speed, the four majors and three city-states, barbarians on, Strategic
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

## Re-run

```
tools/autoplay.py --games 12 --turns 100 --jobs 3 --out /tmp/ap      # about 1 minute on 4 cores
tools/autoplay.py --games 12 --turns 200 --jobs 3 --difficulty King --out /tmp/apk   # about 2 minutes
tools/autoplay.py --summarize /tmp/ap
```
