# MOD_SPEC_2 — Immortal Arc (Rank 5 to Rank 9)

Save this message verbatim as `MOD_SPEC_2.md` in the repo root and add a pointer to it in `CLAUDE.md`. Talk to me in Bahasa Indonesia.

## Objective
Extend the Reverend Insanity base-ruleset mod from Rank 5 to Rank 9: ascension, immortal economy, immortal Gu, immortal killer moves, inheritances, secret realms of heaven and earth, world events, Venerable victory. Fidelity target unchanged: the novel's dynamics, not its plot (MOD_SPEC.md §0, five pillars).

## Carry forward (binding)
- All rules in MOD_SPEC.md §2 and CLAUDE.md stay in force. Unciv docs in `ref/unciv` are law: every unique MUST match a documented pattern verbatim. If this spec conflicts with the docs, the docs win; report the conflict.
- This spec replaces Slices 2–3 of MOD_SPEC.md §8.
- Eras: Rank 5, Rank 6, Rank 7, Rank 8 (splits the old "Rank 7–8"). Rank 9 is the victory, never an era. Historical Venerables appear only as lore and inheritances, never as units.

## Gate (do first, read-only)
Read MOD_SPEC.md, CLAUDE.md, docs/*.md and CHANGELOG.md. Run `tools/check_all`. Report Slice 1 status against MOD_SPEC §11. If Slice 1 is not done or check_all fails: stop, report the gap, do nothing else.

## Mechanics map
Patterns below match the Unciv 4.22.8 docs; re-verify each on TARGET_UNCIV in Phase A. Global triggers need a trigger condition such as `<upon turn start>`; `<every [positiveAmount] turns>` is only a condition.

1. Ascension (rank 5 to 6): heaven, earth and human qi are `Stockpiled` resources. The ascension national wonder has one `Costs [amount] [stockpiledResource]` per qi and, on completion, `Triggers a [event] event`. Chance (`<with [nonNegativeAmount]% chance>`) sets the Blessed Land grade, granted with `Gain a free [buildingName] [cityFilter]`. Failure costs population and a Rank 5 unit. Preparation unlocks safer choices (`Only available <when above [amount] [stat/resource]>`).
2. Immortal essence: one stockpile per tier. It MUST NOT regenerate by itself: Blessed Land buildings, trade, events and plunder are the only sources.
3. Immortal Gu = world wonders (`isWonder`), because each immortal Gu is unique in the world. Add `Never destroyed when the city is captured`: conquest = killing the owner and seizing the Gu. Each needs a recipe tech and `Costs [amount] [stockpiledResource]`. Refinement can fail: the completion event may `Remove [buildingFilter] [cityFilter]`, reopening the race. Tag each with the filter marker `Immortal Gu` and a path marker such as `Strength Path`; allowlist markers in lint.
4. Dao marks = path-marker countables such as `[[Strength Path] Buildings]`, not per-path stockpiles. Same-path units get `[relativeAmount]% Strength <for every [positiveAmount] [countable]>`; conflicting paths get the same pattern with a negative amount.
5. Immortal killer moves = UnitTriggerable uniques on promotions or unit types (Unciv shows them as unit actions), e.g. `[unitTriggerTarget] gains the [promotion] status for [positiveAmount] turn(s) <costs [amount] [stockpiledResource]>`. The status carries `[relativeAmount]% Strength`, `[amount] additional attacks per turn` or `[unitTriggerTarget] heals [positiveAmount] HP`. Limit with `<once>`, `<[positiveAmount] times>`, `<requires [nonNegativeAmount] movement>`. `Can pass through impassable tiles` is cached: never put it on a temporary status. The AI rarely uses custom actions: every unit MUST be viable without its moves.
6. Immortal Gu Houses = super units: `Limited to [amount] per Civilization`, `Only available <if [buildingFilter] is constructed>` (specific immortal Gu), heavy `[relativeAmount]% maintenance costs`.
7. Lifespan, automatic and AI-safe: a global unique consumes `Lifespan Gu` per immortal unit (`Instantly consumes [positiveAmount] [stockpiledResource] <upon turn start> <every [positiveAmount] turns> <for every [positiveAmount] [countable]>`). At zero stock, immortals decay: `[unitTriggerTarget] takes [positiveAmount] damage <upon turn start> <when below [amount] [stat/resource]>`.
8. Immortal zombie: a defeated immortal may return as a zombie unit with `Can only heal by pillaging` and no lifespan decay. `<upon being defeated>` fires UnitTriggerable effects only: find a working hook or mark it ❌.
9. Tribulations and calamities: `Triggers a [event] event <upon turn start> <every [positiveAmount] turns> <if [buildingFilter] is constructed>` (Blessed Land owners). The interval shrinks per era (`<during the [era]>`); severity scales with grade. Effects: `[amount] population [cityFilter]`, `Remove [buildingFilter] [cityFilter]`, `[positiveAmount] [unit]s rebel` (beasts inside borders), temporary debuffs `<for [nonNegativeAmount] turns>`. Preparation unlocks safer choices.
10. Heaven's Will: extra calamities for the strongest, gated by `<when number of [countable] is more than [countable]>` on `Cities` and `[[Immortal Gu] Buildings]`. Fang Yuan's nation is the main target.
11. Fate Gu: world wonder with `Unbuildable` + `Cannot be purchased` (Unbuildable alone still allows purchase). Grant it once to the Heavenly Court's first city (nation unique `Gain a free [buildingName] [cityFilter] <upon founding a city>`, guarded against repeats; fallback: scenario save per Scenarios.md). World state hangs on `<if [buildingFilter] is constructed by anybody>` / `<if [buildingFilter] is not constructed by anybody>`. Capturing it fires the Fate War event: Shatter (`Remove`) or Seize. Shattered: chaos unlocks (dream realms, stronger chance events).
12. Inheritances = world wonders with `Unbuildable` + `Cannot be purchased`, granted only by trial events. Civ-level trigger: `<when number of [countable] is more than [countable]>` with `Owned [tileFilter] Tiles`, throttled with `<every [positiveAmount] turns>`. The event carries `Unavailable <if [buildingFilter] is constructed by anybody>`. Trials mix chance and preparation; failure can destroy units. Every inheritance is a test or a trap.
13. Secret realms of heaven and earth = natural wonders (`type: NaturalWonder`). Random maps place only 1–5 (ModConstants `naturalWonderCountMultiplier`, `naturalWonderCountAddedConstant`): place all of them on the five-region map. Hazard on unit types: `[unitTriggerTarget] takes [positiveAmount] damage <upon entering a [tileFilter] tile> <for units without [promotion]>`.
14. Dream realms, after Fate Gu shatters: test a camp improvement (`Marks a barbarian camp`) with `Only available <if [buildingFilter] is not constructed by anybody>`. Drop it if camp spawning ignores the gate.
15. Beasts: desolate, ancient desolate and remote-ancient desolate beasts are barbarian elites; civ units carry `Never appears as a Barbarian unit`. Kills yield materials: `Earn [amount]% of killed [mapUnitFilter] unit's [costOrStrength] as [stockpile]`.
16. Treasure Yellow Heaven: a recurring market event trading Gold for essence, lifespan Gu and materials. Every choice has `[relativeAmount]% weight to this choice for AI decisions`.
17. Venerable victory, final stage of Eternal Life: milestones `Build [building]` (Venerable Ascension) and `Have at least [amount] [countable]` on `[[Immortal Gu] Buildings]`. The ascension wonder demands single-path mastery: `Only available <when number of [countable] is more than [countable]>` with a `max(...)` expression over the path countables. Test with the console: `civ checkcountable`, `unit checkfilter`.

## Lore seeds
All [VERIFY] except CANON. Research with WebSearch/WebFetch (fan wikis, translation glossaries) and cite one source per LORE_MAPPING row. Never copy text. Unsourced rows stay [VERIFY].
- CANON: 9 ranks; rank 6 = immortal threshold; each immortal Gu (仙蛊) is unique in the world; the Heavenly Court (天庭) guards Fate Gu (宿命蛊); Spring Autumn Cicada (春秋蝉) is rank 6, time path.
- Ascension: heaven/earth/human qi; Blessed Land (福地) grades; Grotto-Heaven (洞天) tier.
- Essence tiers: Green Grape 青提 (6), Red Date 红枣 (7), White Lychee 白荔 (8), Purple Crystal 紫晶 (9).
- Venerables: Primordial Origin, Star Constellation (wisdom), Genesis Lotus (wood), Paradise Earth, Giant Sun (luck); Thieving Heaven (theft), Red Lotus (time), Spectral Soul (soul), Reckless Savage (strength), Limitless (rule).
- Immortal Gu: Fixed Immortal Travel (6, space), Wisdom Gu (8). Killer move: Myriad Self (Fang Yuan, strength).
- Places: Hu Immortal and Lang Ya Blessed Lands, Dang Hun Mountain, Luo Po Valley, Reverse Flow River, Yi Tian Mountain, Treasure Yellow Heaven (宝黄天), the Nine Heavens, the Imperial Court blessed land, dream realms (梦境).
- Factions: Heavenly Court, Shadow Sect (影宗), Southern Border super clans, Huang Jin tribes, the ten great ancient sects.
- Arcs: Imperial Court contest, Yi Tian Mountain battle, Fate War, Five Regions chaos war, immortal zombies (仙僵), lifespan Gu (寿蛊), desolate beasts (荒兽, 上古荒兽, 太古荒兽).

## Budget (caps; exceeding one needs my approval)
"All" is not a target: the novel has hundreds of Gu and moves, and Unciv's UI, AI and balance collapse under them. Pick by gameplay role; the rest goes to civilopedia.
Paths 6 | immortal Gu wonders ≤30 | killer moves ≤24 | Gu Houses ≤4 | inheritances ≤12 | secret realms ≤12 | new stockpiles ≤10 | events ≤25 | Heavenly Court + ≤4 majors + ≤4 city-states.

## Phases (each ends ⛔: report in Bahasa Indonesia, then wait)
A. Capabilities, no content JSON. In docs/CAPABILITIES.md give every mechanic a status (✅/⚠️/❌), fallback and AI note. Prove the risky patterns on a throwaway branch, one test object each: for-every Strength, Remove on a wonder, Unbuildable plus free grant, owned-tile trigger, lifespan consumption, max() countable, camp gate. Give me console commands to check each. ⛔
B. Lore. Extend docs/LORE_MAPPING.md with every rank 5–9 object within budget: EN name, Chinese, source, CANON/ADAPTED/INVENTED, mechanic, patterns. A subagent may do the source research only. ⛔
C. Build in layers, shippable after each: C1 ascension, essence, Rank 5–6 eras | C2 tribulations, Heaven's Will, lifespan | C3 immortal Gu, dao marks, killer moves | C4 inheritances, secret realms, beasts, market | C5 Rank 7–8, Gu Houses, Fate War, Venerable victory. Per layer: generate from data/*.csv with tools/gen_*.py, run check_all, update CHANGELOG, commit. ⛔ Playtest checklist with console shortcuts.
D. Balance and MOD_SPEC §11 Definition of Done, per layer.

## Tension targets (tune; record in docs/BALANCE.md)
- First tribulation 10–15 turns after ascension. Unprepared: lose ≥30% of Blessed Land output or a key building. Prepared: lose <10%.
- Rank 6 essence sustains about 1 killer move per immortal per 5 turns without trade or plunder.
- An immortal without lifespan Gu dies within about 15 turns.
- At least one AI contests each immortal Gu race in a standard game.
- The AI stays solvent and reaches Rank 7 in at least 1 of 3 autoplay games.
- No event choice strictly dominates another.

## Boundaries
- Work only inside the mod repo. `ref/` is read-only.
- Stop and ask before: deleting or renaming Slice 1 objects, adding dependencies, editing MOD_SPEC.md, exceeding a budget cap, deciding any [VERIFY] lore, pushing or publishing.
- Only make changes this spec requests.
- If the same check fails 3 times in a row, stop and report the exact error.
- Every progress claim cites a tool result (check_all output, commit hash).

## First reply
Run the Gate, then Phase A. No content JSON before I approve Phase A.
