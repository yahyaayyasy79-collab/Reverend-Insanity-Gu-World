# MOD_SPEC.md — Reverend Insanity: Gu World (Unciv base-ruleset mod)

**Kick-off message to Claude Code:** "Read MOD_SPEC.md completely, then do Phase 0 only. Talk to me in Bahasa Indonesia."

---

## 0. Role and mission

Act as three specialists at once: a senior Unciv modder, a systems game designer, and a lore editor for *Reverend Insanity* (蛊真人, by Gu Zhen Ren). Build a **base-ruleset mod** for Unciv that adapts the novel.

**Fidelity target: the novel's dynamics, not its plot.** Unciv is a faction-level 4X; it cannot replay a single-protagonist story. It can make the player live by the Gu world's rules:

1. **Power is expensive to keep**, not just to obtain (Gu must be fed, essence must be replenished).
2. **Every breakthrough is a gamble** (refinement and ascension can fail).
3. **Heaven and earth are without benevolence**: the world periodically tries to kill you.
4. **Specialists beat dabblers**: paths conflict (dao marks).
5. **Righteous and demonic are strategies**, not moral labels.

Any feature that serves none of these five is cut.

## 1. Parameters

I may edit this table; otherwise use the defaults and tell me which ones you assumed.

| Key | Default |
|---|---|
| MOD_NAME | `Reverend-Insanity-Gu-World` (letters, digits, dashes only) |
| MOD_TYPE | Base ruleset (`"isBaseRuleset": true` in `jsons/ModOptions.json`) |
| TARGET_UNCIV | Latest stable release (4.22.x when this spec was written). Ask me which version I run |
| DEV_PLATFORM | Desktop. Texture atlases cannot be packed on Android |
| SHIP_ANDROID | Yes: ship a packed atlas, or the GitHub packing workflow linked in `Images-and-Audio.md` |
| LORE_SCOPE | Slice 1 = Qing Mao Mountain and the Southern Border. Five Regions later |
| SPOILERS | Civilopedia covers only the lore of the slices built so far |
| LANGUAGES | English base + `jsons/translations/Indonesian.properties` |
| ART | Generated placeholders; real art from me later |
| FEEL | Harsh but fair; the AI must stay functional |

## 2. Non-negotiable rules

1. **Ground truth is Unciv's own docs and rulesets, never memory.** Treat `docs/Modders/uniques.md`, `docs/Modders/Unique-parameters.md` and `docs/Modders/Mod-file-structure/*` as law. If this spec contradicts them, the docs win; report the conflict.
2. **No invented uniques.** Every unique and every `<conditional>` must match a documented pattern verbatim (case-sensitive), changing only what is inside `[...]`. A non-matching unique is "untyped": it does nothing and at best shows a warning. If you cannot find a pattern, say so and propose a fallback. Never guess.
3. **Always shippable.** Build in thin layers. After every step the mod loads and passes all checks; commit after every green step.
4. **Strict JSON.** Write standard JSON (no trailing commas, no comments) so tooling works. Unciv's bundled JSON files are lenient (they contain trailing commas): parse them with a JSON5-tolerant reader when you copy from them.
5. **ASCII object names.** Names become image paths, which must be ASCII. Chinese terms live in civilopedia text only.
6. **Nothing copied.** Civilopedia text is original and short; never paste passages from the novel or its translations. No manhua or fan art without the artist's permission; placeholders only.
7. **AI compatibility.** The Unciv AI plays by standard Civ V logic. Core tension must hit everyone automatically (maintenance, global uniques, triggered events). Mechanics that need clever choices (custom unit actions, stockpile planning) are optional power for the human, never the AI's only path to progress. Give every event choice an AI weight (`[relativeAmount]% weight to this choice for AI decisions`).
8. **Checkpoints (⛔):** stop, summarize in Bahasa Indonesia, and wait for my approval.
9. Decisions that are mine (scope, lore, taste): ask. Technical defaults: decide, then tell me what you chose and why.

## 3. Phase 0 — Ground truth and tooling ⛔

1. `git init` this folder. `.gitignore`: `ref/`.
2. Shallow sparse clone of `https://github.com/yairm210/Unciv` into `ref/unciv`, at the tag that matches my version (fallback: master, noting that master docs may describe features my release lacks). Paths: `docs/Modders`, `docs/Translating`, `android/assets/jsons/Civ V - Gods & Kings`, `android/assets/jsons/Civ V - Vanilla`.
3. Read all of `docs/Modders` (Mods.md, Mod-file-structure 1–5, uniques.md, Unique-parameters.md, Images-and-Audio.md, Scenarios.md, Type-checking.md) and `docs/Translating/Translation-mods.md`.
4. Build `tools/` (Python; stdlib plus `jsonschema`, `json5`, `Pillow` as needed):
   - `check_schema.py`: validate every `jsons/*.json` against `ref/unciv/docs/Modders/schemas/*.schema.json`.
   - `lint_uniques.py`: parse every pattern in `uniques.md` (all sections, including Conditional, TriggerCondition, UnitTriggerCondition, UnitActionModifier and MetaModifier; the file escapes `<>` as `&lt;&gt;`). For each unique in the mod, split off the `<...>` parts, normalize `[anything]` to `[]`, and require a match for the base and for each conditional. Then check that bracket contents meant to name ruleset objects (units, buildings, techs, resources, promotions, policies, eras, events) exist in the mod. Keep an explicit allowlist for intentional filter-marker uniques (no brackets, no conditionals).
   - `check_refs.py`: cross-references for `requiredTech`, `prerequisites`, `upgradesTo`, `obsoleteTech`, `replaces`, `uniqueTo`, `requiredResource`, era starting units and buildings, events named in `Triggers a [...] event`, and an image for every object (warning only).
   - `make_placeholders.py`: placeholder PNGs at the exact paths Unciv expects (`Images/UnitIcons/<Name>.png`, `Images/BuildingIcons/...`, etc.), color-coded by path or category.
   - `check_all`: runs everything; non-zero exit on any error.

   These tools approximate Unciv's Ruleset Validator. The final authority is the in-game Options tab **"Locate mod errors"**, which I will run on desktop and paste back to you.
5. Create a short `CLAUDE.md` with the rules in §2 plus pointers to this spec and to the docs you create, so later sessions keep them.
6. Write `docs/CAPABILITIES.md`: for each system in §6, the exact uniques or fields that implement it, a status (✅ supported / ⚠️ approximation / ❌ impossible, with fallback) and an AI-compatibility note.
7. Recommend a scaffold, with reasons: fork the G&K JSONs (80 techs, 127 units, 125 buildings; prune hard) or start from the `Unciv-minimal-base-ruleset` template linked in `Mods.md`.

⛔ Report: CAPABILITIES summary, scaffold choice, and every part of this spec that is impossible or only approximable.

## 4. Phase 1 — Lore → mechanics map ⛔

Write `docs/LORE_MAPPING.md`, one row per planned object (era, tech, unit, building, wonder, resource, improvement, terrain, policy, event, nation, city-state, victory): English name (common fan-translation term), Chinese original, one-line lore basis, mechanical role, uniques used, canon status (CANON / ADAPTED / INVENTED), and `[VERIFY]` wherever canon is uncertain. Stay inside the budget in §8.

⛔ I correct the lore before any JSON is written.

## 5. Canon anchors

High confidence. Everything beyond this list gets `[VERIFY]` until I confirm it.

- **Nine ranks.** Ranks 1–5: Gu Masters (mortal). Rank 6 is the immortal threshold; ranks 6–8: Gu Immortals. Rank 9: Venerables, who are legends, not units.
- **Gu** are living creatures with one ability each. Each must be **fed** its specific food or it starves (e.g., Liquor Worm drinks wine; Moonlight Gu, the Gu Yue clan's signature, eats moon orchid petals). Gu are refined from recipes (refinement can fail), kept in the aperture, and combined into **killer moves**.
- **Primeval stones** are both currency and fuel for primeval essence. Immortals run on immortal essence (immortal essence stones).
- The **aperture** is opened in youth (Hope Gu, at the awakening ceremony); **aptitude** is graded A to D.
- An immortal aperture is a **Blessed Land** (or Grotto-Heaven; `[VERIFY]` the distinction), struck periodically by **Heavenly Tribulations and Earthly Calamities** that grow stronger over time.
- **Dao marks** accumulate per path; same-path marks amplify, conflicting paths interfere.
- **Five regions** (Southern Border, Northern Plains, Eastern Sea, Western Desert, Central Continent) separated by region walls. The **Heavenly Court** in the Central Continent is the righteous path's apex and guards the Fate Gu.
- **Righteous path, demonic path, rogue cultivators.**
- **Beast groups** led by hundred-, thousand- and ten-thousand-beast kings; **desolate beasts**. **Variant humans**: hairy men (famed Gu refiners), stone men, feathered men, snowmen; others `[VERIFY]`.
- **Fang Yuan**: reborn 500 years into the past through Spring Autumn Cicada (rank 6, time path); pursues eternal life by any means; starts on Qing Mao Mountain (Gu Yue, Bai and Xiong villages).
- **`[VERIFY]` candidates:** the wolf tide of electric wolves led by a Thunder Crown Wolf; Southern Border super clans (Wu, Shang, Tie...); Northern Plains Huang Jin tribes descended from Giant Sun; the Central Continent's ten great ancient sects (e.g., Spirit Affinity House); Venerables and their paths (Red Lotus: time, Thieving Heaven: theft, Giant Sun: luck, Star Constellation: wisdom, Spectral Soul: soul, Reckless Savage: strength, Limitless: rule, Genesis Lotus: wood, ...).

## 6. Systems (pillar → mechanic)

The patterns below come from `uniques.md` at the time of writing. Re-verify each one in Phase 0.

### S1 — Stone economy (pillar 1)
- **Gold is primeval stones.** Rename it for display through `jsons/translations/English.properties` (Translation-mods.md documents overriding base strings, e.g. `gold = credits`). Test it on a throwaway branch first and keep it only if the UI text stays coherent. Fallback: keep the word, replace the icon, explain it in civilopedia.
- **Unit maintenance is Gu feeding plus essence.** Higher ranks carry steep per-unit multipliers through the unit unique `[relativeAmount]% maintenance costs`.
- **Starvation is already in the engine:** when gold is at or below −200 and income is negative, Unciv disbands military units ("Cannot provide unit upkeep for ... - unit has been disbanded!"). Override that notification in English.properties with Reverend Insanity flavor; find the exact key in the base translation template.
- **Carrying capacity:** tune `unitSupplyBase` and `unitSupplyPerCity` in Difficulties.json (how many Gu Masters a clan can sustain). Keep the AI solvent with `aiUnitMaintenanceModifier`.
- **Stone sources:** veins (resource + improvement), trade, demonic plunder (S6).

### S2 — Immortal essence (pillar 1)
- `Immortal Essence Stone`: a resource with `Stockpiled`, produced by Blessed Land buildings.
- Gu Immortal units: `Costs [amount] [stockpiledResource]` and `Limited to [amount] per Civilization`.
- Immortal killer moves: unit actions with the modifier `<costs [amount] [stockpiledResource]>`.

### S3 — The gamble (pillar 2)
- Tools: `Events.json`, `Triggers a [event] event`, `<with [nonNegativeAmount]% chance>`. An event with `"presentation": "None"` picks a viable choice at random (pure luck); `"Alert"` lets the player choose.
- **Refinement attempt:** the safe option costs more stones; the gamble can grant a promotion or waste everything.
- **Ascension (rank 5 → Gu Immortal):** a national project whose completion rolls success or failure. Failure must hurt (population, the unit, stones).
- **Aptitude:** each new Gu Master receives exactly one aptitude grade (A rare ... D common) by chance. Design it so that a unit can never receive two grades.

### S4 — Merciless world (pillar 3)
- **Heavenly Tribulation / Earthly Calamity:** for civs that own a Blessed Land, `<every [positiveAmount] turns>`, escalating by era. Effects come from triggerables such as `[amount] population [cityFilter]`, `Remove [buildingFilter] [cityFilter]` and `[unitTriggerTarget] takes [positiveAmount] damage`. Preparation (defensive formations, stored stones) unlocks better choices through `Only available` / `Unavailable`.
- **Beast tides:** barbarians become beast groups; camps become lairs (`Marks a barbarian camp`); civ units carry `Never appears as a Barbarian unit`; desolate beasts are rare elite barbarians.
- **Hostile terrain:** `<upon ending a turn in a [tileFilter] tile>` damages unprepared units (desert, frozen plains).

### S5 — Paths and dao marks (pillar 4)
- Pick about six paths for Slice 1 (e.g., Strength, Wind, Water, Wood, Earth, Blood); I approve the list.
- Path commitment as policies with a conflict matrix enforced by `Unavailable <after adopting [policy/belief]>` (mark it ADAPTED). Path units and promotions are gated by the adopted path.

### S6 — Righteous vs demonic (pillar 5)
- Mutually exclusive branches. **Righteous:** stability, city-state favor, defensive bonuses, cheaper defensive upkeep. **Demonic:** profit from violence, e.g. `Earn [amount]% of killed [mapUnitFilter] unit's [costOrStrength] as [stockpile]` and `Upon capturing a city, receive [amount] times its [stat] production as [stockpile] immediately`, paid for with diplomatic and stability penalties. **Rogue cultivator:** cheap upkeep, few cities.
- `Personalities.json` gives each faction an AI temperament.

### S7 — Five regions (Slice 3)
- A hand-made map in `maps/`, selected with the ModOptions unique `Mod preselects map [comment]`.
- Region walls: a terrain with `"impassable": true`; only immortal-tier units with `Can pass through impassable tiles` cross.
- Each region has its own terrain, resources and native factions.

### S8 — Foreknowledge (Fang Yuan)
- Ruins become **Inheritances** (传承): large, sometimes double-edged rewards.
- Fang Yuan's faction: foreknowledge bonuses, paid for with more frequent "Heaven's Will" calamities.

## 7. Default content map (propose changes in Phase 1)

- **Eras** = the faction's dominant cultivation tier: Rank 1–2 → Rank 3 → Rank 4 → Rank 5 (peak mortal) → Rank 6 (Blessed Land) → Rank 7–8. Rank 9 is the victory, not an era.
- **Techs** = Gu recipes, cultivation methods, path insights. The final tech is `Can be continually researched` (Dao Comprehension).
- **Units:** civilians (clan settlers, mortal laborers, scouts); Gu Masters as path × rank upgrade chains; a handful of Gu Immortals, named through `UnitNameGroups.json`.
- **Buildings:** clan hall, Gu academy, Gu feeding house, wine cellar (Liquor Worm), moon orchid garden, refinement chamber, formation platform, trading house. Wonders are tied to canon places and Gu.
- **Resources:** at most 6 strategic, 8 luxury, 8 bonus. Each one must force a decision.
- **Stats:** Science = cultivation insight; Culture = path doctrine (buys policies); Happiness = clan stability; Faith and religion disabled in Slice 1 (empty Beliefs/Religions) unless a strong use appears.
- **City-states:** variant-human tribes and minor clans.
- **Victories:** *Eternal Life*, the hardest, spaceship-style (`requiredSpaceshipParts` + `Add all [comment] in capital` + `Build [building]`); *Five Regions Supremacy* (`Capture all capitals`); *Heavenly Court Mandate* (`Win diplomatic vote`, ADAPTED); score at max turns.

## 8. Content budget

| Slice | Scope | Exit test |
|---|---|---|
| 1. Southern Border | Ranks 1–4 (3 eras), ~15 techs, ~12 units, ~12 buildings, Righteous/Demonic + 2 path branches, ~6 resources, 5 events (beast tide, refinement, aptitude, betrayal, stone shortage), 4 majors + 3 city-states, domination victory | The stone loop is tense and fun on a small map |
| 2. Ascension | Rank 5, ascension, Blessed Lands, tribulations, immortal essence | Tribulations are survivable with preparation and devastating without |
| 3. Five Regions | Map with region walls, the other regions' factions, Heavenly Court, Eternal Life victory | A full game reaches a victory without crashing |
| Polish | Indonesian translation, civilopedia, art, balance | Definition of Done (§11) |

Exceeding the budget requires my approval.

## 9. Workflow for every step

Plan (objects to add or change) → implement → `tools/check_all` → fix → update `CHANGELOG.md` → commit → report in Bahasa Indonesia: what changed, what to test in game, and the developer-console commands that reach that situation quickly (backtick key on desktop; see Scenarios.md) → wait for my "Locate mod errors" output and playtest notes.

Repetitive content (Gu Masters across path × rank) is generated from a table (`data/*.csv` → `tools/gen_*.py`); commit both the table and the output.

## 10. Balance and tension

- Early game: maintenance eats a large share of stone income (start near 40%, then tune). A careless player should starve at least once; a careful one never.
- No event choice strictly dominates another.
- The AI must not fall into a disband spiral. Watch AI treasuries in spectator or autoplay games. Optional, ask me first: build Unciv from source and adapt `desktop/src/com/unciv/app/desktop/ConsoleLauncher.kt` (it hardcodes G&K) to simulate AI-vs-AI games on this ruleset.
- List every tunable number with its file and field in `docs/BALANCE.md`.

## 11. Art, text, packaging, Definition of Done

- Placeholders at exact paths, ASCII names, `preview.png` in the mod root.
- Atlas: desktop packs it on launch; Android cannot. Commit the packed atlas or add the packing workflow (ask me).
- Civilopedia: 2–4 sentences, original wording, a cold and pragmatic tone, the Chinese term once, spoilers per §1.
- Translations: I run Options → Advanced → "Generate translation files"; you fill `Indonesian.properties`.
- README: installation (GitHub topics `unciv-mod` and `unciv-mod-rulesets`, or "Download mod from URL"), credits, and a disclaimer: unofficial, non-commercial fan work; *Reverend Insanity* © Gu Zhen Ren.
- **Done, per slice:** `check_all` passes; "Locate mod errors" shows zero errors (each remaining warning explained in `docs/KNOWN_ISSUES.md`); a 100-turn game against the AI finishes without a crash and the AI stays solvent; every new object has an icon (placeholder allowed), civilopedia text and an Indonesian translation; CHANGELOG updated and committed.

## 12. Your first reply

No JSON yet. Do Phase 0, then stop at its checkpoint.
