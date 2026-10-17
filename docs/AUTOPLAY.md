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

## Re-run

```
tools/autoplay.py --games 12 --turns 100 --jobs 3 --out /tmp/ap      # about 1 minute on 4 cores
tools/autoplay.py --games 12 --turns 200 --jobs 3 --difficulty King --out /tmp/apk   # about 2 minutes
tools/autoplay.py --summarize /tmp/ap
```
