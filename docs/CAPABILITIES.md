# CAPABILITIES — what Unciv can and cannot express for this mod

Ground truth: `ref/unciv` at tag **4.22.8** (commit `2eccbd0`, 2026-10-08), fetched by `tools/fetch_ref.sh`.

* Every unique quoted here matches a pattern in `docs/Modders/uniques.md` verbatim (placeholders shown with
  their documented type names) **and** is exercised by `tools/tests/fixtures/capability_proof`, which must
  pass `check_schema`, `lint_uniques` and `check_refs` with zero errors. `tools/tests` enforces both, so this
  file cannot quote an invented unique without the self-tests failing. The same fixture passes Unciv's own
  RulesetValidator (the 4.22.8 release jar's `mod-ci`, via `tools/unciv_ci.py`) with zero findings.
* **[src]** marks behaviour the docs do not state, read from the Unciv source (`ref/unciv/core`). Docs win where
  they speak; [src] fills gaps. Every [src] claim needs an in-game test before content depends on it.
* Status: ✅ supported · ⚠️ approximation (fallback described) · ❌ impossible (fallback described).
* AI: the Unciv AI never presses custom unit-action buttons (`TriggerUnique` actions), except golden-age actions
  of civilians [src `CivilianUnitAutomation`]. It **does** pick XP promotions, constructions and policies, and it
  resolves every event — Alert or not — by weighted random using
  `[relativeAmount]% weight to this choice for AI decisions` [src `Event.kt`].

---

## Engine facts that shape every design below

| # | Fact | Source |
|---|------|--------|
| E1 | An event with `"presentation": "None"` picks **one** viable choice by weighted random. Weight of a choice = product of its `[relativeAmount]% weight to this choice for AI decisions` uniques (`+X` → ×(1+X/100), default 1). AI civs resolve `"Alert"` events the same way. Odds are therefore exact and tunable. | [src] `Event.kt`, `UniqueTriggerActivation`, `IHasUniques.getWeightForAiDecision` |
| E2 | An event triggered from a unit (unit unique, promotion, ruins) keeps that unit as context: its choices may use the UnitTriggerable uniques (those starting with [unitTriggerTarget]) on **that** unit. From a building, tech, policy or global trigger there is no unit and unit effects silently do nothing. | [src] `EventChoice.triggerChoice`, `getTriggerFunction` |
| E3 | A triggerable unique on a unit **without** a trigger conditional or unit-action modifier fires **once, when the unit is created** (also after upgrade/transform; promotions are copied first). It becomes an action button only if it has a unit-action modifier such as `<costs [amount] [stockpiledResource]>`. The docs only describe the action case. | [src] `UnitManager.placeUnitNearTile`, `UnitActionsFromUniques` |
| E4 | Adding a promotion fires its triggerables (those without a trigger conditional) immediately on that unit. With `Doing so will consume this opportunity to choose a Promotion` the promotion is not kept: fine as a one-shot carrier that a unique **grants**, but the AI never **buys** such a promotion with XP (only heal promotions, at ≤ 60 HP). **Corrected in Phase 1**; Phase 0 claimed the opposite. The AI-compatible repeatable XP purchase is a **kept** promotion that removes itself: `[unitTriggerTarget] loses the [promotion] promotion` + `<upon turn start>` (skipped on purchase because it has a trigger conditional; fires next turn). It can be bought again once removed, at a rising XP price (10, 20, 30… per purchase). | [src] `UnitPromotions.addPromotion`, `doDirectPromotionEffects`, `isAvailable`; `NextTurnAutomation.applyPromotions` (line 463) |
| E5 | `<with [nonNegativeAmount]% chance>` rolls independently per unique. Two chance-uniques in one choice can both fire or both fail: use a `"None"` sub-event as a die when exactly one outcome must happen, and never let two chance-lines match the same unit state. The seed hashes object identities, so **reloading a save can reroll** (no protection against save-scumming). | docs + [src] `Conditionals.getStateBasedRandom`, `GameContext.stateBasedRandom` |
| E6 | `<every [positiveAmount] turns>` is `game turn % N == 0`: all civs are hit on the same turn. | [src] `Conditionals.kt` |
| E8 | City strength grows with the **share** of the tech tree a civ knows: + (share × `cityStrengthFromTechsMultiplier`)^`cityStrengthFromTechsExponent` × `cityStrengthFromTechsFullMultiplier` (ModOptions constants, defaults 5.5, 2.8, 1.0: +118 with every tech). A short tree reaches "every tech" early, so a slice must scale the full multiplier to its unit strengths (Slice 1: 0.1, autoplay round 5). Adding techs in a later slice changes every city's strength. | [src] `CityCombatant.getCityStrength`; docs Mod-file-structure 5 |
| E7 | Statuses (Phase 1, round 3): at turn start a unit's triggers fire **before** its statuses tick down, so an N-turn status given by an `<upon turn start>` trigger runs out at the (N−1)th turn start after that. A status that runs out fires `<upon losing the [promotion] status>`; giving a status the unit already has only ever raises its timer; `<for units without [promotion]>` sees statuses. The Gu hunger meter rests on this. | [src] `UnitTurnManager.startTurn`, `MapUnit.setStatus`, `removeStatus` |
| E9 | `<upon losing a [mapUnitFilter] unit>` fires whenever a unit leaves the civ's unit list: death (also by its own turn damage), **upgrade** (the old unit is destroyed and a new one placed), capture and gift. Filter it on a unit that never upgrades or changes owner. | [src] `UnitManager.removeUnit` (called by `MapUnit.destroy`, `capturedBy`, `gift`), `UnitUpgradeManager.performUpgrade`; probed (MOD_SPEC_3 A3, test 4) |
| E10 | An upgrade keeps every promotion, XP and promotion count, **also across a unit-type change** and also promotions whose `unitTypes` exclude the new type; their effects keep working. A unit is only *offered* promotions whose `unitTypes` list its own type. `Limited to [amount] per Civilization` counts the civ's living units of that name (plus queued ones) and blocks upgrades too; `Unbuildable` does not block upgrades. | [src] `MapUnit.copyStatisticsTo`, `UnitPromotions.isAvailable`, `CivConstructions.countConstructedObjects`, `UnitUpgradeManager.canUpgrade`; probed (MOD_SPEC_3 A3, tests 1-3) |

---

## S1 — Stone economy (pillar 1)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Gold displayed as primeval stones | `jsons/translations/English.properties` overriding base keys (Translation-mods.md: `gold = credits`). The mod file is loaded because the base game ships `English.properties` [src `Translations.kt`]. The stat name is one key, but dozens of base strings embed the word (e.g. "You found [goldAmount] gold in the ruins!") and each needs its own override. | ✅ done in Phase 2 (2026-10-18): `tools/gen_translations.py` overrides every base key that contains the word Gold (about 40, Golden excluded, placeholders kept) in English (Primeval Stones) and Indonesian (Batu Primordial, the user's choice). Fallback unchanged. | cosmetic |
| Feeding Gu = unit maintenance | Unit unique `[relativeAmount]% maintenance costs` (stacks multiplicatively; per rank). Engine formula [src `CivInfoStatsForNextTurn.getUnitMaintenance`]: cost = (0.5 × Σ unit weights × (1+p))^(1+p/3), p = turn / total turns. The 3 free units are the **most expensive** ones, which would erase rank multipliers for an elite core: put `[-3] units cost no maintenance` in GlobalUniques to make every Gu eat. | ✅ | same formula × `aiUnitMaintenanceModifier` |
| Starvation | Built in: at gold ≤ −200 with negative income, military units are disbanded, those inside own borders first, then the least promoted [src `TurnManager.endTurn`]. Message key `Cannot provide unit upkeep for [unitName] - unit has been disbanded! = ` exists in `template.properties` → override in English.properties. | ✅ text; ⚠️ the −200 threshold is hardcoded and civilians are never disbanded | AI disbands the same way: watch AI treasuries (§10) |
| Carrying capacity | Difficulties `unitSupplyBase`, `unitSupplyPerCity`; ModOptions `constants.unitSupplyPerPopulation`; `[amount] Unit Supply`. Over the limit: −10% production per extra unit, max −70% [src]. Supply costs **production, not stones**. | ✅ (as production pressure) | `aiUnitSupplyModifier` |
| Keep the AI solvent | Difficulties `aiUnitMaintenanceModifier`, `aiBuildingMaintenanceModifier` | ✅ | — |
| Stone sources | Veins: resource + improvement (`improvementStats` gold). Trade: engine city connections. Plunder: S6. | ✅ | native |

## S2 — Immortal essence (pillar 1)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Immortal Essence Stone | TileResources entry with `Stockpiled` (+ `Cannot be traded`). Stockpiles change at turn start by net supply [src `TurnManager.startTurn`]. | ✅ | — |
| Produced by Blessed Lands | Building unique `Provides [amount] [resource]` → +N per turn into the stockpile. | ✅ | builds it like any building |
| Gu Immortal units | `Costs [amount] [stockpiledResource]` (paid when work begins), `Limited to [amount] per Civilization` | ✅ | builds when it can pay; does not save up on purpose |
| Immortal upkeep in essence | `Consumes [amount] [resource]` on the unit drains the stockpile every turn. | ⚠️ the stockpile may go negative and nothing is disbanded [src]. Fallback: `[-50]% Strength <when below [0] [Immortal Essence Stone]>`. | penalty applies automatically |
| Immortal killer moves | Unit action: `[unitTriggerTarget] gains the [promotion] status for [positiveAmount] turn(s)` with `<costs [amount] [stockpiledResource]>` → a button that pays essence for a temporary combat status. | ✅ human only | AI never uses it (rule 7: optional power) |

## S3 — The gamble (pillar 2)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Event plumbing | `Triggers a [event] event`, `<with [nonNegativeAmount]% chance>`, Alert (player chooses) / None (weighted die, E1). Every choice carries `[relativeAmount]% weight to this choice for AI decisions` (check_refs enforces rule 7). | ✅ | weighted random |
| Refinement attempt | A kept promotion bought with XP: `Triggers a [event] event` + `[unitTriggerTarget] loses the [promotion] promotion` `<upon turn start>` (E4: repeatable once per turn, rising XP price). Its `Unavailable` lines must mirror every unit state in which no outcome can fire, or the AI pays for empty attempts. Alert event on that unit: **safe** = `Only available` with `<when above [amount] [stat/resource]>`, `Gain [amount] [civWideStat]` (negative) and `[unitTriggerTarget] gains the [promotion] promotion`; **gamble** = trigger a None die: Gu formed vs `[unitTriggerTarget] takes [positiveAmount] damage`. | ✅ ADAPTED (an XP purchase instead of a free-standing action) | AI buys it like any promotion and resolves the Alert by weights |
| Ascension (rank 5 → immortal), route A: national project (spec) | Building, gated by `Only available` + `<when number of [countable] is more than [countable]>` (a rank-5 unit exists), with `Triggers a [event] event` on completion → Alert strategy → None die. Success: `Free [unit] appears`, `Gain a free [buildingName] [cityFilter]`. Failure: `[amount] population [cityFilter]` (negative), `Gain [amount] [civWideStat]` (negative), `[mapUnitFilter] units gain the [promotion] promotion` (damage carrier, see S4), `Remove [buildingFilter] [cityFilter]` so it can be retried. | ⚠️ a building has no unit context (E2): "the unit" cannot be singled out, every matching unit is hit | AI builds it and rolls |
| Ascension, route B: per unit (recommended) | The rank-5 unit buys a kept, self-removing "Attempt Ascension" promotion (E4) → None die on **that** unit: success `Free [unit] appears` + `[unitTriggerTarget] is destroyed` (the mortal becomes the immortal); failure `[unitTriggerTarget] takes [positiveAmount] damage` or destruction. | ✅ (E3/E4 need in-game confirmation) | AI buys kept promotions → compatible |
| Aptitude A–D, exactly one | Unit unique `Triggers a [event] event` guarded by four `<for units without [promotion]>` (one per grade). Fires once at creation (E3) → None event with four choices, each `[unitTriggerTarget] gains the [promotion] promotion`, weights e.g. A 5 / B 20 / C 35 / D 40. One die roll can only pick one choice; the guards stop a second grade after upgrades. | ✅ by construction; ⚠️ relies on E3 (undocumented) | automatic for everyone |

## S4 — Merciless world (pillar 3)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Tribulation / calamity trigger | On the Blessed Land building: `Triggers a [event] event` + `<upon turn start>` + `<every [positiveAmount] turns>`; escalate with a second unique adding `<starting from the [era]>` (or one event per era). | ✅; E6: everyone is struck the same turn, use `<with [nonNegativeAmount]% chance>` to stagger | automatic |
| City / economy damage | `[amount] population [cityFilter]`, `Remove [buildingFilter] [cityFilter]`, `Instantly consumes [positiveAmount] [stockpiledResource]`, `Gain [amount] [civWideStat]` | ✅ | automatic |
| Unit damage | `[unitTriggerTarget] takes [positiveAmount] damage` straight in a tribulation event: ❌ no unit context (E2). Fallback: `[mapUnitFilter] units gain the [promotion] promotion` granting a carrier promotion whose uniques are `[unitTriggerTarget] takes [positiveAmount] damage` + `Doing so will consume this opportunity to choose a Promotion` (granted, not bought, so E4's AI filter does not matter). | ⚠️ hits **all** matching units; no random single victim | automatic |
| Preparation unlocks better choices | Choices with `Only available` + `<if [buildingFilter] is constructed>` or `<when above [amount] [stat/resource]>`; `Unavailable` | ✅ | AI picks weighted among the choices it qualifies for |
| Beast groups | Barbarians are the beasts. The barbarian pool is every military land unit the Barbarian civ can build (techs most civs know), weighted by strength [src `BarbarianManager`]. Beast units: `"uniqueTo": "Barbarians"` (matched as a civ filter [src]). Civ units: `Never appears as a Barbarian unit`. Lairs: improvements with `Marks a barbarian camp`. Needs a `Barbarians` nation, otherwise barbarians silently never exist [src `GameStarter`] (check_refs enforces). | ✅ | native barbarian handling |
| Desolate beasts are rare | Stronger units are **more** likely, so rarity cannot come from weights. Gate them by tech/era or `Only available` + `<after turn number [nonNegativeAmount]>`. | ⚠️ | — |
| Beast tide | Event `[positiveAmount] [unit]s rebel` → barbarian-owned units appear beside the civ's city [src]. Override "[1] [unit] has rebelled against us!" in English.properties. Needs barbarians enabled at game setup. | ✅ | automatic |
| Hostile terrain | GlobalUniques `unitUniques`: `[unitTriggerTarget] takes [positiveAmount] damage` + `<upon ending a turn in a [tileFilter] tile>` + `<for units without [promotion]>` (an adaptation promotion). Simpler: Terrain `Units ending their turn on this terrain take [amount] damage` (no conditionals). | ✅ | ⚠️ AI may not avoid the damage |

## S5 — Paths and dao marks (pillar 4)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Path commitment + conflicts | Policy branches. Exclusivity: `Unavailable` + `<after adopting [policy/belief]>` (spec), or the G&K idiom `Only available` + `<before adopting [policy/belief]>` (Autocracy/Freedom/Order). | ✅ ADAPTED | respects availability; Personalities `priorities` choose branches |
| Path-gated units and promotions | `Only available` + `<after adopting [policy/belief]>` | ✅ | AI only builds what is available |
| Same-path marks amplify | `<for every [countable]>` on a bonus, counting "Adopted [[Wind Path] branch] Policies" (the policy filter is "[branchName] branch" with literal brackets): `[+5]% Strength <for [Melee] units> <for every [Adopted [[Wind Path] branch] Policies]>` | ⚠️ ADAPTED: dao marks = policies adopted in a branch | automatic |
| Conflicting paths interfere | Hard exclusivity (above) or penalties with `<after adopting [policy/belief]>` | ⚠️ ADAPTED | automatic |

## S6 — Righteous vs demonic (pillar 5)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Mutually exclusive branches | `Only available` + `<before adopting [policy/belief]>` on both openers | ✅ | ✅ |
| Demonic: profit from violence | `Earn [amount]% of killed [mapUnitFilter] unit's [costOrStrength] as [stockpile]`, `Upon capturing a city, receive [amount] times its [stat] production as [stockpile] immediately`, `[relativeAmount]% Yield from pillaging tiles`, `Receive [relativeAmount]% Gold from Barbarian encampments and pillaging Cities` | ✅ | automatic on kills / captures |
| Demonic: diplomatic penalty | ❌ no unique lowers other civs' opinion of you. Fallback: `[relativeAmount]% City-State Influence degradation`, `[relativeAmount]% Unhappiness from [populationFilter] [cityFilter]`, betrayal events. | ⚠️ | automatic |
| Righteous: stability, city-state favour, defence, cheaper defensive upkeep | `Resting point for Influence with City-States is increased by [amount]`, `[relativeAmount]% Strength for cities`, `[relativeAmount]% maintenance costs <for [Melee] units>` (civ-wide maintenance uniques are evaluated per unit [src]) | ✅ | automatic |
| Rogue cultivator | `[amount] units cost no maintenance`, `[relativeAmount]% unhappiness from the number of cities` | ✅ | automatic |
| AI temperament | Personalities.json: stat focus 0–10, `priorities` per branch, `[relativeAmount]% weight to [baseUnitFilter/buildingFilter] for AI decisions`, `Will not build [baseUnitFilter/buildingFilter]`. The behaviour fields (military, war, …) are "not fully implemented" per docs. | ✅ / ⚠️ behaviours | — |

## S7 — Five regions (Slice 3)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Hand-made map | `maps/` + ModOptions `Mod preselects map [comment]` (docs: only meaningful with several maps) | ✅ | — |
| Region walls | Terrain `"impassable": true` + unit `Can pass through impassable tiles` (cached: conditionals on it are unreliable). Civ-wide alternative: `Land units may cross [terrainName] tiles after the first [baseUnitFilter] is earned` (lets **every** land unit cross). | ✅ / ⚠️ alternative | pathfinding handles both |
| Regional terrain, resources, factions | Terrains, `terrainsCanBeFoundOn`, Nations `startBias`; start positions placed in the map editor | ✅ | — |

## S8 — Foreknowledge (Fang Yuan)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Ruins become Inheritances | Ruins.json rewards (context = the entering unit) + an improvement with `Provides a random bonus when entered`. Double-edged: `Triggers a [event] event` → Alert on that unit, e.g. `[unitTriggerTarget] gains [amount] XP` + `[unitTriggerTarget] takes [positiveAmount] damage`. | ✅ | weighted |
| Foreknowledge bonuses | Nation uniques, e.g. `[relativeAmount]% [stat]` | ✅ | — |
| Paid with more "Heaven's Will" | Nation unique `Triggers a [event] event` + `<upon turn start>` + `<with [nonNegativeAmount]% chance>` | ✅ | automatic |

## §7 content map (spot checks)

* Eras = cultivation ranks; Rank 9 is a victory, not an era. ✅
* Final tech `Can be continually researched`. ✅
* Faith and religion off: ModOptions `Disable religion` + empty Beliefs.json / Religions.json. ✅
* City-states: CityStateTypes friend/ally bonuses such as `[stats] [cityFilter]`. ✅
* Immortal names: UnitNameGroups (`unitNames`) + unit unique `[unitTriggerTarget] gets a name from the [unitNameGroup] group` (fires at creation, E3). ✅
* *Eternal Life*: `requiredSpaceshipParts` + milestones "Build [building]" and "Add all [comment] in capital"; parts carry `Spaceship part` and `Can be added to [comment] in the Capital`; a building with `Enables construction of Spaceship parts`. AI spaceship logic keys on these uniques, not on the victory name [src `ConstructionAutomation`]. ✅
* *Five Regions Supremacy*: "Capture all capitals". ✅
* *Heavenly Court Mandate*: a building with `Triggers voting for the Diplomatic Victory` + "Anyone should build [building]" + "Win diplomatic vote". ✅ ADAPTED
* Score at max turns: "Have highest score after max turns". ✅

---

## MOD_SPEC_3 Phase A3 — rank chain and path promotions (2026-10-18)

Five capability tests, one test object each, on the throwaway branch `a3-capability-tests` (local):
`tools/a3/build_test_mod.py` builds the shipped `jsons/` plus the test objects as the mod `A3TEST` (Unciv's own
validator: 0 errors); `tools/a3/ProbeA3.java` runs them headless on the 4.22.8 release jar. Test objects: unit types
Gu Immortal and Venerable; units Test Rank Five (Gu Master) → Test Rank Six (Gu Immortal) → Test Venerable (Venerable:
`Limited to [amount] per Civilization`, `Unbuildable`, `Cannot be purchased`,
`[unitTriggerTarget] takes [positiveAmount] damage` `<upon turn start>`); five promotions; two test world wonders.

| # | Capability | Status | Evidence (probe output) | AI note |
|---|---|---|---|---|
| 1 | Promotions kept across a unit-type change on upgrade | ✅ | Test Rank Five (Gu Master) with a Gu-Master-only promotion (+2 sight) and an all-types promotion (+1 movement), 57 XP, upgraded to Test Rank Six (Gu Immortal): both promotions, both effects and the XP survive; the second upgrade to Test Venerable keeps both promotions too. The Gu Immortal is no longer *offered* the Gu-Master-only promotion (E10). | Automatic; the AI upgrades units itself. |
| 2 | `Only available` with a unit conditional on a promotion | ✅ | Tier promotion with prerequisite "Test Path All" and `Only available <for [mapUnitFilter] units>` (Gu Immortal): offered to the Gu Immortal that holds the prerequisite, not to a Gu Master that holds it, not to a Gu Immortal without it. | The AI picks only from available promotions [src `NextTurnAutomation.applyPromotions`]. |
| 3 | `Limited to [amount] per Civilization` blocks upgrades | ✅ | Two Test Rank Six: both may upgrade while no Venerable lives; after one upgrades, the other cannot (rejection `MaxNumberBuildable`; `Unbuildable` is ignored for upgrades); after the Venerable dies, it can again. | The AI's upgrade check uses the same `canUpgrade`. |
| 4 | `<upon losing a [mapUnitFilter] unit>` on death by turn damage | ✅ with ⚠️ | Venerable at 100 HP taking 30 per turn start dies at the 4th; at that moment `Gain [amount] [civWideStat]` (+1000 stones), `Remove [buildingFilter] [cityFilter]` (the ascension wonder is gone) and `Gain a free [buildingName] [cityFilter]` (the inheritance wonder appears in the capital) all fire. ⚠️ The same trigger also fired (+7 stones) when a Test Rank Six was **upgraded** (E9): never filter it on a unit that upgrades. | Global trigger: hits AI and human alike. |
| 5 | Per-civ AI promotion weights | ✅ | Two path promotions, each `[relativeAmount]% weight to this choice for AI decisions` −95 plus +19900 `<for [civFilter] Civilizations>` for its own clan. Weights: main path 10, the other path 0.05, two generic promotions 1 each → 83%. The AI's own routine on 161 units per clan: Wu took its path 133 times (83%), Bai's once; Bai mirrored it. | Weighted random per promotion purchase [src `applyPromotions`]. |

Design rules for Phase B3/C3 that follow:

* **Main-path share.** The AI draws one promotion at a time, weighted over everything the unit is offered. With
  about 35 path lines (off-path weight 0.05 each, 1.7 in total) and k generic promotions at weight 1, the main path
  needs a weight of at least 4 × (1.7 + k) to reach the ≥80% target: 47 for k = 10. So either give generic promotions
  negative weights too, or raise the main path's per-civ weight; B3 sets the numbers and autoplay checks them.
* **Death hooks** (Venerable, inheritance drop): filter on the Venerable only; it never upgrades, and its `Unbuildable`
  and `Cannot be purchased` do not stop the R8 → R9 upgrade.
* **One Venerable in the world** needs both locks: `Limited to [amount] per Civilization` (per civ) and the world wonder
  gate `Only available <if [buildingFilter] is constructed>` (one owner world-wide), which test 4 shows is removed again
  on death.
* Path lines must list all three unit types in `unitTypes`, or a unit that ranks up stops being offered its own line.

Check in game (needs the A3TEST mod from the throwaway branch; console as in `docs/TESTING.md`):

```
unit add <civ> "Test Rank Five"              # then, with it selected:
unit addpromotion "Test Path Old Type"       # test 1: +2 sight
unit addpromotion "Test Path All"            # test 1: +1 movement
civ addstat Gold 500                         # then the Upgrade button: promotions and XP stay
unit setxp 100                               # test 2: on the Gu Immortal the promotion screen offers Test Tier Immortal
unit add <civ> "Test Rank Six"               # test 3: upgrade one to Test Venerable; the second one's Upgrade is disabled
                                             # test 4: end 4 turns: +1000 stones, Test Ascension gone, Test True Inheritance in the capital
city addbuilding "Test Ascension"            # (before test 4, in the capital)
```

## MOD_SPEC_2 Phase A — immortal arc, rank 5 to 9 (2026-10-18)

Every pattern below matches `docs/Modders/uniques.md` 4.22.8 (`tools/unique_check.py`). The seven risky ones were
proven headless on the throwaway branch `test/capability-tests` (`tools/a3/build_test_mod.py` adds one test object
each to the shipped `jsons/`; `tools/a3/ProbePhaseA.java`; Unciv's validator: 0 errors). MOD_SPEC_3 overrides two
items: rank 9 becomes one unit (not only a victory), and paths are promotion lines (not a 6-path cap).

### The seven risky patterns

| # | Pattern | Status | Evidence (probe output) |
|---|---|---|---|
| A1 | for-every Strength: `[relativeAmount]% Strength` `<for every [positiveAmount] [countable]>` on [[Strength Path] Buildings] | ✅ | A unit with +5 per Strength mark and −5 per Wisdom mark: 0 → +5 → +10 with 1 and 2 Strength-marker buildings, +5 after one Wisdom marker. |
| A2 | `Remove [buildingFilter] [cityFilter]` on a world wonder reopens the race | ✅ | While Wu held the test immortal Gu, Gu Yue's city was rejected with `WonderAlreadyBuilt`; after Remove, no rejection. A **built** wonder with `Never destroyed when the city is captured` stays in the city when it changes hands. |
| A3 | `Unbuildable` + `Cannot be purchased` + free grant | ⚠️ | ✅ Nobody can build it (`Unbuildable`, `WonderAlreadyBuilt`). ✅ A nation unique `Gain a free [buildingName] [cityFilter]` `<upon founding a city>` `<if [buildingFilter] is not constructed by anybody>` granted it once, to that nation's first city. ❌ A free grant **ignores world-wonder uniqueness**: granted to two civs, both held it; [in all cities] put it in every city of the civ [src `GainFreeBuildings` → `completeConstruction`]. ❌ A **free** building is **removed** when its city changes hands, `Never destroyed when the city is captured` notwithstanding [src `CityConquestFunctions.removeBuildingsOnMoveToCiv`]: probe, the free wonder vanished on capture while the built one stayed. |
| A4 | Owned-tile trigger: `Triggers a [event] event` `<upon turn start>` `<when number of [countable] is more than [countable]>` on the countable Owned [tileFilter] Tiles, throttled by `<every [positiveAmount] turns>` | ✅ | Every 3rd turn, only clans owning more than 6 land tiles rolled the trial (Wu from turn 4, Bai from 7, the others from 13). The event's `Unavailable <if [buildingFilter] is constructed by anybody>` closed it for everybody once one clan held the inheritance: 0 trials in the next 6 turns. All clans roll on the same turn (E6). |
| A5 | Lifespan: `Instantly consumes [positiveAmount] [stockpiledResource]` `<upon turn start>` `<every [positiveAmount] turns>` `<for every [positiveAmount] [countable]>`; decay `[unitTriggerTarget] takes [positiveAmount] damage` `<upon turn start>` `<when below [amount] [stat/resource]>` | ✅ with ⚠️ | 5 lifespan Gu, 2 immortals, 1 per immortal every 2 turns: 5 → 3 → 1 → −1; the multiplier follows the living count (0 once both died). Decay started the turn the stock fell below 1; with healing, 30 damage per turn killed them in 4 turns. ⚠️ The stock goes **negative** (−5): consumption does not stop at zero, so new lifespan Gu first pay the debt. |
| A6 | `max()` countable: `Only available <when number of [countable] is more than [countable]>` with the countable max([[Strength Path] Buildings], [[Wisdom Path] Buildings]) | ✅ | Evaluates to 2 for 2 Strength + 1 Wisdom marks, 3 after a third Strength marker; the wonder was available to Wu, hidden (`ShouldNotBeDisplayed`) for a clan with none. |
| A7 | Camp gate for dream realms | ❌ as specified, ✅ fallback | `Only available <if [buildingFilter] is not constructed by anybody>` on the camp improvement does **not** gate spawning: 104 of 200 camps while the gate was shut. Camp spawning reads the conditional of the camp marker itself [src `BarbarianManager.createNewCamp`, `TileImprovement.isBarbarianCampEquivalent`]: `Marks a barbarian camp <if [buildingFilter] is not constructed by anybody>` gave 0 of 200 while the Fate Gu stood and 71 of 200 after it was removed. |

Note: Unciv's validator lists a path marker that is only referenced inside a countable ([[Wisdom Path] Buildings])
as "not used as a filtering unique" (INFO, not an error); `tools/unique_allowlist.txt` keeps lint quiet.

### Mechanics map 1–17

| # | Mechanic | Status | Implementation (verified patterns) | Fallback / caveat | AI |
|---|---|---|---|---|---|
| 1 | Ascension R5 → R6 | ⚠️ | Heaven, earth and human qi as `Stockpiled` resources; a national wonder with one `Costs [amount] [stockpiledResource]` per qi whose completion triggers `Triggers a [event] event`; `<with [nonNegativeAmount]% chance>` picks the grade; `Gain a free [buildingName] [cityFilter]` grants the Blessed Land. | A building has no unit context (E2): "failure costs a Rank 5 unit" cannot pick the unit. Per the CLAUDE.md decision and MOD_SPEC_3, run the ascension from the unit (a kept promotion, E4) so the event can use `[unitTriggerTarget] is destroyed` or upgrade it. A free Blessed Land vanishes if its city is captured (A3). | AI builds wonders and buys promotions; events by weight. |
| 2 | Immortal essence | ✅ | One `Stockpiled` resource per tier; it changes only through providers and triggers (Blessed Land buildings, trade, events, plunder). | — | automatic |
| 3 | Immortal Gu = world wonders | ✅ | `isWonder`, recipe tech, `Costs [amount] [stockpiledResource]`, `Never destroyed when the city is captured` (A2: a built one changes hands with the city), failed refinement `Remove [buildingFilter] [cityFilter]` reopens the race (A2); markers `Immortal Gu` and a path marker, allowlisted. | Never grant one free (A3). | AI builds wonders |
| 4 | Dao marks | ✅ | A1. | Conflicts: same pattern, negative amount (A1). | automatic |
| 5 | Immortal killer moves | ⚠️ | UnitTriggerable uniques with action modifiers, e.g. `[unitTriggerTarget] gains the [promotion] status for [positiveAmount] turn(s)` `<costs [amount] [stockpiledResource]>`, limited by `<once>`, `<[positiveAmount] times>`, `<requires [nonNegativeAmount] movement>`; the status carries `[relativeAmount]% Strength`, `[amount] additional attacks per turn` or `[unitTriggerTarget] heals [positiveAmount] HP`. | Never put `Can pass through impassable tiles` on a status (cached). | ❌ the AI never presses unit-action buttons: every unit must be viable without its moves. |
| 6 | Immortal Gu Houses | ✅ | `Limited to [amount] per Civilization` (MOD_SPEC_3 A3: also blocks upgrades), `Only available <if [buildingFilter] is constructed>`, `[relativeAmount]% maintenance costs`. | — | AI builds what is available |
| 7 | Lifespan | ✅ with ⚠️ | A5. | Debt: the stock goes negative. Tune damage vs healing for "dies within ~15 turns" (heal 10–20 per turn). | automatic |
| 8 | Immortal zombie | ⚠️ | `<upon being defeated>` only fires UnitTriggerable effects on the dying unit, so it cannot spawn a unit. Hook that works: civ-level `Free [unit] appears` `<upon losing a [mapUnitFilter] unit>`, plus `Can only heal by pillaging` on the zombie. | `upon losing` also fires on upgrade, capture and gift (E9): filter on the top immortal rank only, or accept a zombie when a rank-8 immortal ascends. Untested here. | automatic |
| 9 | Tribulations and calamities | ⚠️ | `Triggers a [event] event` `<upon turn start>` `<every [positiveAmount] turns>` `<if [buildingFilter] is constructed>`; interval by `<during the [era]>`; effects `[amount] population [cityFilter]`, `Remove [buildingFilter] [cityFilter]`, `[positiveAmount] [unit]s rebel`, timed debuffs `<for [nonNegativeAmount] turns>`. | `<every N turns>` is turn % N for everyone (E6): "first tribulation 10–15 turns after ascension" cannot be relative. Fallback: `<with [nonNegativeAmount]% chance>` per turn (expected gap 1/p), or a timed status on the ascended unit. | events by weight |
| 10 | Heaven's Will | ✅ | `<when number of [countable] is more than [countable]>` on `Cities` vs [[Immortal Gu] Buildings] (countables and expressions evaluate, A6). | — | automatic |
| 11 | Fate Gu | ❌ as specified | `Unbuildable` + `Cannot be purchased` blocks building; the guarded nation-unique grant works once (A3); world state via `<if [buildingFilter] is constructed by anybody>` / `<if [buildingFilter] is not constructed by anybody>` works (A4, A7). | ❌ A **free** Fate Gu is deleted when its city is captured (A3), so "capture → Fate War: Shatter or Seize" never happens. Fallback: Fate Gu `uniqueTo` the Heavenly Court and **built** by it (AI weight), or pre-built in a scenario save; a built wonder changes hands (A2). Detect the capture with `<upon conquering a city>` + `<if [buildingFilter] is constructed>`. | AI builds its unique wonder; events by weight |
| 12 | Inheritances | ⚠️ | Owned-tile trigger, throttle and `Unavailable <if [buildingFilter] is constructed by anybody>` (A4); trials mix chance and preparation. | Free grants duplicate (A3): guard each with `<if [buildingFilter] is not constructed by anybody>` and use [in capital]. A free inheritance cannot be seized by conquest (A3): if seizing matters, the trial should unlock **building** it (a cheap national seal + `Only available <if [buildingFilter] is constructed>`). | events by weight |
| 13 | Secret realms | ✅ | `NaturalWonder` terrains; counts by ModOptions constants `naturalWonderCountMultiplier` (0.124) and `naturalWonderCountAddedConstant` (0.1); hazard `[unitTriggerTarget] takes [positiveAmount] damage` `<upon entering a [tileFilter] tile>` `<for units without [promotion]>`. | All of them only on the five-region map (Slice 3). Untested here. | AI walks in blind (takes the damage) |
| 14 | Dream realms | ✅ via fallback | A7: the conditional goes on `Marks a barbarian camp`, not on the improvement. | — | barbarians |
| 15 | Desolate beasts | ✅ | Barbarian elite units; civ units carry `Never appears as a Barbarian unit`; `Earn [amount]% of killed [mapUnitFilter] unit's [costOrStrength] as [stockpile]`. | Barbarians only know techs every civ knows (LORE_MAPPING engine facts): gate elites by those techs. | automatic |
| 16 | Treasure Yellow Heaven | ✅ | A recurring event (`Triggers a [event] event` `<upon turn start>` `<every [positiveAmount] turns>`), every choice weighted. | — | events by weight |
| 17 | Venerable victory | ✅ | Milestones `Build [building]` and `Have at least [amount] [countable]` (Mod-file-structure 5); single-path mastery by `max()` (A6). | MOD_SPEC_3 makes the Venerable a unit raced against its lifespan (A3 tests 3–4). | AI builds wonders |

Check in game (download `https://github.com/yahyaayyasy79-collab/Reverend-Insanity-Gu-World/tree/test/capability-tests`,
start a new game on "Reverend Insanity Gu World test capability tests"; console as in `docs/TESTING.md`):

```
unit add <civ> "Test Dao Unit"            # A1: then city addbuilding "Test Strength Gu A" / "Test Strength Gu B" / "Test Wisdom Gu A";
                                          #     the attack preview shows +5 / +10 / +5
city addbuilding "Test Immortal Gu"       # A2: another clan's city no longer offers it; then
civ activatetrigger "Remove [Test Immortal Gu] [in all cities]"   # A2: it is offered again
                                          # A3: Bai's first city holds Test Fate Gu from turn 1; nobody can build it
civ activatetrigger "Gain a free [Test Fate Gu] [in capital]"     # A3: a second holder appears (the duplicate)
civ checkcountable "[Owned [Land] Tiles]" # A4: above 6, the trial adds 1 Test Trial Counter every 3rd turn
civ activatetrigger "Instantly provides [5] [Test Lifespan Gu]"   # A5: then unit add <civ> "Test Immortal" twice and end turns:
                                          #     -2 every 2 turns, then -30 HP per turn once below 1
civ checkcountable "[max([[Strength Path] Buildings], [[Wisdom Path] Buildings])]"   # A6: Test Venerable Ascension needs more than 1
                                          # A7: camps never show Test Dream Camp while Test Fate Gu stands
```

## Impossible or only approximable (checkpoint summary)

1. ❌ **Damage one specific unit from a civ-level tribulation.** Fallback: carrier promotion on a unit filter (all matching units).
2. ❌ **Diplomatic penalty for the demonic path** (other civs' opinion). Fallback: city-state influence, unhappiness, events.
3. ❌ **Moving the −200 starvation threshold**; civilians are never disbanded. Fallback: tune maintenance size.
4. ⚠️ **Immortal essence upkeep** can go negative without disbanding. Fallback: strength penalty below zero.
5. ⚠️ **Rare desolate beasts**: barbarian spawn prefers strong units. Fallback: tech/turn gating.
6. ⚠️ **"Primeval stones" rename** is partial (many embedded "gold" strings). Fallback: icon + civilopedia.
7. ⚠️ **Refinement as a free action** works only for humans; the AI-compatible form is an XP promotion.
8. ⚠️ **Ascension as a national project** cannot single out the ascending unit; the per-unit promotion route can.
9. ⚠️ **Dao marks** become "policies adopted in a branch"; **unit supply** is a production penalty, not food.
10. ⚠️ **Simultaneous tribulations** with `<every [positiveAmount] turns>` (E6); stagger with chance.
11. ⚠️ **Personality behaviours** (war, military, …) are unfinished in the engine.
12. ⚠️ Mechanics resting on undocumented engine behaviour (E2–E4) must be confirmed in game first.

## Conflicts between the docs, the schemas and the engine

| # | Where | Docs say | Schema / engine / bundled rulesets | We follow |
|---|---|---|---|---|
| D1 | TileResources | field `unique` | schema and G&K: `uniques` | schema |
| D2 | UnitNameGroups | field `names` (required) | schema, G&K, engine: `unitNames` | schema |
| D3 | Personalities | behaviour "DenounceWillingness" exists | G&K uses `denounceWillingness`, schema rejects it | avoid it (check_schema warns) |
| D4 | Eras | `uniques` attribute | schema does not declare it | docs (check_schema warns) |
| D5 | Quests | name "Contest Technology" | engine and G&K: "Contest Technologies" | engine |
| D6 | Techs | `row` default 0 | schema: minimum 1 | schema (rows start at 1) |
| D7 | uniques.md, Triggerable intro | triggerables on units become actions | only with a unit-action modifier; otherwise they fire at creation (E3) | engine |
| D8 | Events table | None: "the choice is made randomly" | weighted by the AI-weight unique (E1) | engine |

Spec items corrected by the docs/engine: S3 "None picks at random" (it is weighted, E1); S1 "supply = how many
Gu Masters a clan can sustain" (supply costs production, not stones); S4 "`[unitTriggerTarget] takes [positiveAmount] damage`"
as a tribulation effect (no unit context, E2).

## Scaffold recommendation

**Neither option as written. Start from a clean skeleton and copy only engine-coupled infrastructure from the
bundled Vanilla/G&K rulesets.**

* **Fork G&K — rejected.** Slice 1 needs ~15 techs, ~12 units, ~12 buildings; G&K ships 80, 127 and 125.
  Pruning removes >85% of the content, and every deletion breaks references (great people, religion, spaceship,
  city-state quests…). Days go into repairing references to content we delete anyway, and Civ V names and balance
  leak into the mod.
* **Unciv-minimal-base-ruleset — rejected as a base.** It is stale: it has keys the 4.22.8 schemas reject
  (`aisExchangeTechs`, Ruins `color`), no Water terrain although the docs require one, and two units. It adds
  nothing a clean skeleton lacks. For the Android atlas (§11; your call) the better workflow template is the newer
  RekMOD `autoupdate.yml` that Images-and-Audio.md links (Java 21, `mod-ci`): retarget its `branches:` from `master`,
  and take only the atlas files from its pull requests — `mod-ci` also rewrites `jsons/*.json`, which are generated.
* **Clean skeleton, chosen.** Write Slice-1 content from `docs/LORE_MAPPING.md`, and copy from Vanilla (converted to
  strict JSON) only what the engine treats specially: base terrains with their map-generation and region uniques
  (River must keep the vanilla uniques, per docs), the improvements with hardcoded names (Road, Remove \*, City
  center, City ruins, Barbarian encampment), the Difficulties and Speeds structure, and the `Barbarians` and
  `Spectator` nations. Everything else is new and passes `tools/check_all` from the first commit.
