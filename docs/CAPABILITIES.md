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
| E7 | Statuses (Phase 1, round 3): at turn start a unit's triggers fire **before** its statuses tick down, so an N-turn status given by an `<upon turn start>` trigger runs out at the (N−1)th turn start after that. A status that runs out fires `<upon losing the [promotion] status>`; giving a status the unit already has only ever raises its timer; `<for units without [mapUnitFilter]>` sees statuses. The Gu hunger meter rests on this. | [src] `UnitTurnManager.startTurn`, `MapUnit.setStatus`, `removeStatus` |

---

## S1 — Stone economy (pillar 1)

| Feature | Implementation | Status | AI |
|---|---|---|---|
| Gold displayed as primeval stones | `jsons/translations/English.properties` overriding base keys (Translation-mods.md: `gold = credits`). The mod file is loaded because the base game ships `English.properties` [src `Translations.kt`]. The stat name is one key, but dozens of base strings embed the word (e.g. "You found [goldAmount] gold in the ruins!") and each needs its own override. | ⚠️ partial rename; test on a throwaway branch (spec). Fallback: keep "Gold", override the icons `StatIcons/Gold` and `EmojiIcons/Gold`, explain in civilopedia. | cosmetic |
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
