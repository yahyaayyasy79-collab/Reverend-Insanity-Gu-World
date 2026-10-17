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
* **Refinement.** By T100 each clan holds 1–3 rank-1 Gu and 0–1 rank-2 Gu; Killer Move never appears.

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
  the 8–10 Gu holders a clan keeps. Rank-1 threshold: unchanged (the user's rule).
* **Conquest is broken.** Wars are half as frequent as in Vanilla and almost never take a city (1 in 24 games vs 6 in
  6). The only Slice 1 victory besides the score is domination, so in practice nobody can win. Not yet explained;
  candidates: city strength bonuses (Clan Head Pavilion, Formation Platform, Guardian Formations), ranged-only Moon
  armies (ranged units cannot capture), upkeep keeping armies small.
* **Wu vs Xiong: no dominance.** King: Xiong 4.5 cities, 28.5 units, White Jade Gu 7; Wu 4.2, 28.2, 5. Emperor: equal
  within noise. Pork is not scarce for either (mean 4.8–5.6), so there is nothing to clash over.
* **The refinement ladder stalls at rung 1.** At T200 the clans hold 8–11 rank-1 Gu each but 0.3–0.7 rank-2 Gu, and
  Killer Move appears in none of the 30 games: the AI buys each unit's first attempt with the academy's starting XP and
  rarely earns the 20 XP for a second one in peace.
* **The tech tree runs out** at turn 113 (Emperor) to 123 (King) on average; the rest is Dao Comprehension.
* **Stones.** Upkeep rises from 20% of gross income (T1–50) to 60% (T151–200), but treasuries still grow (mean 420
  stones in T151–200): the AI stays solvent, the late game is not tense.
* **Pillage is 7–10 times Vanilla's:** the wolf tides and barbarians (who heal only by pillaging) hit tiles hard. Pillar
  3 shows up as pillage, not as deaths.

## Re-run

```
tools/autoplay.py --games 12 --turns 100 --jobs 3 --out /tmp/ap      # about 1 minute on 4 cores
tools/autoplay.py --games 12 --turns 200 --jobs 3 --difficulty King --out /tmp/apk   # about 2 minutes
tools/autoplay.py --summarize /tmp/ap
```
