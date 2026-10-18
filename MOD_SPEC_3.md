# MOD_SPEC_3 — Gu Masters Rank 1–9, All Paths (amendment)

Save this message verbatim as `MOD_SPEC_3.md` in the repo root and add a pointer to it in `CLAUDE.md`. Precedence on conflict: MOD_SPEC_3 > MOD_SPEC_2 > MOD_SPEC. Talk to me in Bahasa Indonesia.

## Objective
Make Gu Masters playable from Rank 1 to Rank 9 and implement every canonical cultivation path, as faithful to the novel as Unciv allows. All MOD_SPEC §2 rules stay binding: docs are law, no invented uniques, always shippable, AI compatibility, checkpoints.

## Overrides
- MOD_SPEC §6 S5, MOD_SPEC §7 ("Gu Masters as path × rank upgrade chains") and every 6-path limit (MOD_SPEC §8, MOD_SPEC_2 Budget) are replaced by the architecture below.
- MOD_SPEC_2 "Rank 9 never an era, never units": Rank 9 becomes one playable unit (below). It is still not an era. Historical Venerables stay lore and inheritances.
- MOD_SPEC_2 #17: the victory becomes Eternal Life as defined below.

## Architecture: four independent axes
1. Rank = one upgrade chain of 9 units on three unit types (promotion `unitTypes` targets): Gu Master (R1–R5), Gu Immortal (R6–R8), Venerable (R9). Upgrades keep promotions (verified in source: `MapUnit.copyStatisticsTo` clones them). R5 to R6 happens only through the ascension event (MOD_SPEC_2 #1). Gate R7 and R8 with `Only available <when above [amount] [stat/resource]>` on essence; per the docs, `Only available` also blocks upgrades.
2. Path = one promotion line per canonical path, open to all three unit types. A unit's first path promotion is its main path. Secondary paths are allowed but pay dao-mark conflicts (MOD_SPEC_2 #4). Steer each AI to its nation's main path with `[relativeAmount]% weight to this choice for AI decisions` (test a `<for [civFilter] Civilizations>` variant).
3. Attainment = tiers inside a path line, linked by `prerequisites`: Master, Grandmaster, Great Grandmaster, Supreme Grandmaster (canon also has quasi- steps [VERIFY]). XP buys tiers. High tiers need rank: `Only available <for [mapUnitFilter] units>` (ADAPTED).
4. Dao marks = path-marker building countables (MOD_SPEC_2 #4), unchanged.

Path academies grant tier 1 with `All newly-trained [baseUnitFilter] units [cityFilter] receive the [promotion] promotion`. XP sources: `New [baseUnitFilter] units start with [amount] XP [cityFilter]`, `[relativeAmount]% XP gained from combat`.

## Paths
- Phase B3 compiles the complete canonical path list from sources (fan-wiki path lists, glossaries): one source and the Chinese name per path. Seed list, all [VERIFY]: strength, wisdom, time, space, rule, luck, soul, blood, sword, blade, fire, water, wood, earth, metal, wind, cloud, ice-snow, lightning, light, dark, star, moon, sound, poison, transformation, enslavement, refinement, formation, food, information, human, heaven, qi, bone, painting, dream, theft.
- Group paths into families with shared templates. Generate all path content from `data/paths.csv` with `tools/gen_paths.py`.
- Each path gets 4 attainment tiers, 1 signature unique and ≤2 killer moves: a mortal move at Grandmaster, an immortal move at Great Grandmaster costing essence (MOD_SPEC_2 #5). Two paths MUST NOT share a signature.
- Signature palette (verified patterns): `[amount] additional attacks per turn`, `[amount] Movement`, `[amount] Sight`, `Ignores terrain cost`, `Invisible to others`, `Can see invisible [mapUnitFilter] units`, `Heals [amount] damage if it kills a unit`, `All adjacent units heal [amount] HP when healing`, `[relativeAmount]% Strength bonus for [mapUnitFilter] units within [amount] tiles`, `Ranged attacks may be performed over obstacles`, `Can transform to [unit]` (transformation), `Earn [amount]% of killed [mapUnitFilter] unit's [costOrStrength] as [stockpile]` (theft), `[relativeAmount]% Strength <when fighting in [tileFilter] tiles>`, `[relativeAmount]% Strength <vs cities>`.
- On-hit statuses: `[unitTriggerTarget] gains the [promotion] status for [positiveAmount] turn(s) <upon damaging a [mapUnitFilter] unit>` with `Target Unit`, e.g. poison as damage over time, ice via `[unitTriggerTarget] loses [positiveAmount] movement`.
- Permanent `Can pass through impassable tiles` only at space-path Supreme Grandmaster (the unique is cached).

## Rank 9: Venerable
- At most one Venerable alive in the world. The world wonder "Venerable Ascension" gates it: the R9 unit has `Only available <if [buildingFilter] is constructed>`, `Limited to [amount] per Civilization`, `Unbuildable` and `Cannot be purchased`. An R8 unit reaches R9 by upgrade, so it keeps its path and attainment.
- The ascension wonder demands single-path mastery (the `max(...)` expression from MOD_SPEC_2 #17).
- Even a Venerable has a finite lifespan: `[unitTriggerTarget] takes [positiveAmount] damage <upon turn start>` plus `Can only heal by pillaging`. Target: 30–40 turns of life.
- On death (`<upon losing a [mapUnitFilter] unit>`): `Remove [buildingFilter] [cityFilter]` on the ascension wonder, which reopens the race, and `Gain a free [buildingName] [cityFilter]` of an unbuildable True Inheritance world wonder that others can seize by conquest.
- Eternal Life victory: milestone `Build [building]` for the Eternal Life wonder. It is buildable only while you own a Venerable: `Only available <when number of [countable] is more than [countable]>` on `[[Venerable] Units]`. The Venerable races its own death.

## Budget
Paths: all canonical (expected ~35) | promotions: ≤4 per path + ≤10 general | killer moves: ≤2 per path | Gu units: 9 + ≤1 unique unit per nation | other MOD_SPEC_2 caps unchanged | placeholder icons colored by family.

## Phases (each ends ⛔: report in Bahasa Indonesia, then wait)
A3. Capability tests on a throwaway branch, one test object each: promotions kept across a unit-type change on upgrade; `Only available` with unit conditionals on promotions; `Limited to` blocking upgrades; `<upon losing a [mapUnitFilter] unit>` firing on death by turn damage; per-civ AI promotion weights. Record results in docs/CAPABILITIES.md. ⛔
B3. Path list and family matrix (signature, moves, conflicts) in docs/PATHS.md. ⛔ I approve the list.
C3. Migration: if Slice 1 already ships path policies or path × rank units, propose a migration plan and change nothing until I approve it. ⛔ Then build: rank chain and tiers 1–2 into Slice 1; tiers 3–4 and immortal moves into MOD_SPEC_2 layer C3; Venerable and Eternal Life into layer C5.

## Tension targets (add to docs/BALANCE.md)
- A single-path unit beats an equal-rank three-path unit in most duels.
- A rank 6 survives attacks from 4 fresh rank 5 units (the immortal–mortal gap). Among immortal ranks, one rank step is a strong edge, not an absolute one.
- A Venerable can take any city alone, but dies within its lifespan unless it keeps pillaging.
- In autoplay, AI units stay on their main path in ≥80% of path promotions.

## Boundaries
Same as MOD_SPEC_2 Boundaries. Never delete or rename Slice 1 objects without my approval. If the same check fails 3 times in a row, stop and report the exact error.

## First reply
Phase A3 only, and only after MOD_SPEC_2's Gate passes.
