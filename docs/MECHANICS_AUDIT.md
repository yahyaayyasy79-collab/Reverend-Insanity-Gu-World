# Mechanics audit (2026-11-03)

The user asked: "rombak mekanik game atau diadaptasikan agar paling terbaik dengan situasi kanon novel, serta check
lah keseluruhan hasil efek atau dampak skill, jalur, dao, kebijakan, sumber daya, pemahaman, killer move dan gu".
The audit read every effect in `jsons/` and the generator tables. It measured effect sizes, looked for outliers,
for dead or unpayable effects and for what the AI cannot use, and compared each system with the canon.

The verdict: the systems are sound and largely canon-aligned. They do not need a rewrite. One cost was wrong and is
fixed. Six gaps are listed as proposals for the user's decision.

## What was measured

| System | Size | Finding |
|---|---|---|
| Path attainment (pemahaman) | 47 paths × 4 tiers | Tier strength is uniform: +20 / 25 / 30 / 35% (`TIER_STRENGTH`), gated by the unit's era: Grandmaster rank 3+, Great Grandmaster 6+, Supreme 8+. The paths differ only in each tier's ability (`data/path_powers.csv`). Healthy, except the spread of the Supreme abilities (P4). |
| Path hits | 47 | Hit kinds: duration of a status 24, damage 11, movement loss 4, heal 3, movement gain 2, XP 2, earnings 1; each scaled by dao marks (`path_powers.SCALE`). Every path attacks with its own effect. |
| Dao marks | I–V | +10 / 20 / 30 / 40 / 55% strength, V also +15 HP healing; gained by defeating immortal-era units, by the Dao Comprehension status running out, and by events; III+ need an immortal. Each tier replaces the last. Dao interference is implemented: every other path a unit holds costs 5–10% (hidden lines on each Master), immortal Gu of clashing paths cost more (`data/path_conflicts.csv`). |
| Gu | 113 catalog + 47 path Gu + 66 immortal | Effects grow linearly with rank in every role (strength 5+3r %, attack/defence 8+4r %, damage 2+2r, …): monotonic, no outliers. Every mortal Gu eats and has a hunger meter; immortal Gu sleep without their rank's essence or their wonder. Higher-rank Gu need a unit of that rank. |
| Killer moves | 94 path moves + 174 combinations | Path moves: the mortal one 15 stones; the immortal one, see the fix below. Combinations: 42 curated + 132 generated (Resonance and Fusion per immortal Gu); assault 71, bind 37, ward 23, aura 18, mobility 10, heal 8, insight 5, plunder 2; mortal ones cost stones, immortal ones 3 essence of their rank; each is gated by comprehension. All are buttons: the AI never uses one (P3). |
| Policies | 245 in 49 branches | Righteous and Demonic exclude each other, so do Moon and Strength; 45 more path branches. Every policy has an effect (strength 57, yields 71, movement 13, healing 12, wonder and unit production 13, sight, XP, upkeep, …). None is dead. |
| Resources | 16 | Every resource has a source and a use, except **Immortal Materials**: beast and realm kills give 30–50 at a time, while the only sink is one event choice (20) (P5). Furs is a plain luxury (happiness). |
| Aptitude | A–D | A +15% strength, −20% upkeep, +25% XP; B +5 / −10 / +10; C nothing (the average); D −10 / +20 / −25. Fits the canon's aperture grades. |
| Power curve | ranks 1–9 | Effective attack (base × (1 + tiers + dao + one attack Gu)): R1 7.9, R2 13.6, R3 23.1, R4 35.5, R5 56, R6 85, R7 128, R8 210, Venerable 519. That is about ×1.5–1.7 a rank, and the mortal → immortal step (×1.5) is no bigger than any other (P1). |

## Fixed now

* **Immortal path moves cost the right essence.** All 47 immortal moves (Great Grandmaster) cost 5 green grape
  essence at every rank, but only rank-six blessed lands make green grape. A clan whose immortals had risen to rank
  seven or eight drained its green grape while red date and white lychee piled up unused. Each rank now pays in its
  own essence:
  * rank six (and the immortal zombie): 5 green grape;
  * rank seven: 4 red date;
  * rank eight: 3 white lychee;
  * the Venerable: 2 yellow apricot (it makes 6 a turn).

  One action line per rank; Unciv shows only the line whose conditionals apply [src UnitActionsFromUniques].

## Proposals (the user's decision: scope and lore)

| # | Proposal | Canon | How (documented uniques) | Risk |
|---|---|---|---|---|
| P1 | **The immortal chasm.** Immortals fight mortals at +50% (the Venerable +100%). | Mortals and immortals are two worlds apart; a rank-six immortal sweeps a mortal army aside. | `[+50]% Strength <vs [pre-[Rank Six era]] units>` on the immortal units (eraFilter `pre-[era]`). | Immortal clans snowball over mortal ones; A/B with autoplay. |
| P2 | **Gu as spoils.** Defeating a Gu Master can take one of its mortal Gu (about 25%). | Victors loot the Gu of the fallen; Fang Yuan lives on this. | `[This Unit] gains the [<Gu>] promotion <upon defeating a [<Gu>] unit> <with [25]% chance>` (a promotion name is a mapUnitFilter) on a hidden promotion every Gu Master carries; a Gu above the victor's rank falls asleep as now. | The trigger on a removed unit needs an in-game test. |
| P3 | **The AI uses killer moves.** AI units get the path's mortal or immortal move at turn start when a hostile unit is adjacent and the clan can pay; the cost is taken at the same time. | Every Gu Master, not only the player, fights with killer moves. | `[This Unit] gains the [<move>] status for [2] turn(s) <upon turn start> <for [AI player] Civilizations> <when adjacent to a [Hostile] unit> <when above [N] [<cost>]>` plus `Gain [-15] [Gold]` or `Instantly consumes [N] [<essence>]` with the same conditionals. Two turns, because a one-turn status given at turn start runs out at once (E7). | The AI may pay and then not attack; numbers need an A/B. The user wants no weaker AI (2026-11-02). |
| P4 | **Even Supremes.** Four paths gain an extra attack a turn at Supreme (strength, light, moon, time). Nine get little combat value: sight (star, wisdom, information), movement (wind, cloud, space), cheaper upgrades (refinement), lower upkeep (food), double movement in two terrains (transformation). Give those nine a second, combat-worthy effect in their theme. | Every Supreme Grandmaster is a terror in their own path. | Extra lines in `data/path_powers.csv` `sup` (e.g. wind: `Can move after attacking`; star: `[1] additional attacks per turn`). | Balance; A/B. |
| P5 | **Immortal Materials as the refiners' stock.** The immortal Gu wonders and the Gu Houses also cost Immortal Materials. | Immortal Gu and Gu Houses are refined from immortal materials. | `Costs [N] [Immortal Materials]` on the wonders and Gu House units (removed when work begins). | A clan without beasts to kill cannot build them: the amounts must be modest. |
| P6 | **The vital Gu.** Losing the path Gu to hunger wounds its master (about 30 HP). | A Gu Master's vital Gu (本命蛊) is bound to them: its death injures them. | `[This Unit] takes [30] damage <upon losing the [<path Gu>] promotion>`. | Hunger becomes harsher; fine with the meter's warnings. |
