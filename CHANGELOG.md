# Changelog

## Phase 0 — ground truth and tooling (2026-10-12)

* Reference: Unciv **4.22.8** docs, schemas, G&K/Vanilla rulesets and engine source via `tools/fetch_ref.sh`
  (sparse, blob-less; `ref/` gitignored).
* Tools: `check_schema`, `lint_uniques`, `check_refs`, `check_package`, `make_placeholders`, `check_all`, with
  self-tests (broken-mod detection, capability proof, placeholder safety, packaging).
* Docs: `docs/CAPABILITIES.md` (systems S1–S8 → uniques, status, AI notes; engine facts E1–E6; docs conflicts
  D1–D8; scaffold recommendation), `CLAUDE.md`, copy of `MOD_SPEC.md`.
* No ruleset JSON yet (by design, MOD_SPEC §12).
* `fetch_ref.sh` also fetches all of `docs/`, `desktop/src` and `android/src` (installation questions).
* `docs/TESTING.md`: verified install routes (desktop, URL download, Android), naming rules, test loop, console.

## Phase 0 follow-up — official validator, decisions (2026-10-12)

* `tools/unciv_ci.py`: Unciv 4.22.8's own validator (`mod-ci` from the release jar) on a temp copy, in `check_all`;
  `--pack` produces the committed Android atlas. `fetch_ref.sh` downloads the jar.
* The official validator caught a docs-reading error the linter missed: the policy-branch filter is
  `[Wind Path] branch` with literal brackets. Fixed in `lint_uniques`, CAPABILITIES.md and the capability proof,
  which now passes the official validator with zero findings.
* `check_refs`: `Atlases.json` entries must have their atlas; stale atlas (images not packed) is flagged.
* Decisions recorded in CLAUDE.md: Unciv 4.22.8, mod name "Reverend Insanity Gu World", clean skeleton,
  promotion-based gambles, atlas packed here and committed.

## Phase 1 — lore → mechanics map (2026-10-12)

* `docs/LORE_MAPPING.md`: one row per planned Slice 1 object (116 rows) with English and Chinese names, lore basis,
  mechanical role, exact uniques, CANON/ADAPTED/INVENTED and [VERIFY]; budget check, path choice (Moon + Strength),
  pillar coverage for human and AI, 19 questions for the user, refinement ladder, every event choice with its AI
  weight, balance starting numbers and known limits. Made from three independent drafts, a synthesis and two
  skeptic reviews (lore, mechanics), whose findings are applied.
* `tools/slice1_prototype.py`: writes the whole plan as a throwaway ruleset; it passes `check_all`, including Unciv
  4.22.8's own validator with 0 errors and 0 warnings. A new self-test keeps it and LORE_MAPPING.md in sync.
* **Correction of Phase 0 (E4):** the AI never buys a promotion with `Doing so will consume this opportunity to
  choose a Promotion` (`NextTurnAutomation.applyPromotions`). Refinement and ascension now use a kept promotion that
  removes itself at the next turn start. Fixed in CAPABILITIES.md (E4, S3), CLAUDE.md and the capability proof.
* **Correction (E5):** chance rolls are seeded by object identity, so reloading a save can reroll them.
* No ruleset JSON yet: the user corrects the lore first (⛔).

## Phase 1, round 2 — the user's lore answers, checked and applied (2026-10-13)

* Fact check of the user's answers and the remaining [VERIFY] items against the raw novel text: 11 claims, each by a
  researcher and an independent skeptic, all high-confidence. Confirmed: White/Black Boar Gu eat pork and are kept and
  fed; Jade Skin Gu (玉皮蛊) eats jade; White Jade Gu is the rank-2 fusion. Not supported: the leader names Bai Mo and
  Xiong Jiang (the novel never names either leader), the ceremony "in the ancestral hall / 祖地" (it is held in the
  moon-orchid flower sea in a cave reached through the clan-head pavilion), and a rogue-cultivator faction.
* `docs/LORE_MAPPING.md` rewritten for round 2 (121 rows): Tie Clan replaces the Rogue Cultivators; clan emblem Gu
  (Moonlight, Bear Strength, Stream); canon fusion ladder (Moon Raiment, White Jade Gu) with the wild-boar tusk; Jade
  becomes a Strategic Gu food; Lightning Wolf / Bold Lightning Wolf / Thunder Crown Wolf; Clan Head Pavilion with the
  ancestral hall folded in; Foothill Villages replace the Stone Man Tribe; a double-edged Flower Wine Monk Inheritance.
  The user has 14 decisions to make.
* `tools/ladder_check.py` (new): exhaustive check of the refinement ladder (11,502 unit states: one roll per attempt,
  one rung per attempt, no attempt that cannot succeed, no Gu food overdrawn). A self-test runs it on the prototype.
* `tools/slice1_prototype.py` regenerated: passes `check_all`, including Unciv 4.22.8's own validator with 0 errors and
  0 warnings.

* Final lore and mechanics review of round 2, fixes applied:
  - Unfed Gu now starve (canon): while a food is in deficit, each holder loses the Gu at 10% a turn. Before this fix,
    a deficit was permanent, and the AI, which promotes on a stale resource count, ran into one as a matter of course.
  - The refinement ruin carries Refine Gu's guard; `ladder_check` now also checks it and the starved-Killer-Move
    state (14,742 states, 0 errors).
  - Moon Raiment follows canon: a defensive Gu that helps nearby allies, eats Moon Orchid.
  - The Xiong clan survives the wolf tide (ch175).
  - Primeval stones come from spirit springs, so the vein tiles are marked INVENTED.
  - Every difficulty gets +6 base happiness, because the slice has only one luxury.
  - The Gu Yue AI never builds the Flower Wine Monk Inheritance.
  - The Inheritance Trial cannot kill.

## Phase 1, round 3 — the user's decisions (2026-10-13)

* The Wu clan (武家, leader Wu Ji) is the fourth major instead of the Tie clan: righteous, strength path, starts on the
  Righteous Path; unique building Martial Arena (演武场) replaces the Gu Academy and gives new Gu Masters 20 XP. The Tie
  clan and its Demon Suppression Tower move to the roadmap.
* A hunger meter replaces the 10% starvation: an unfed Gu is weakened at once (its effects carry
  `<when above [-1] [food]>`), gets a timed hunger status (3 turns rank 1, 5 turns rank 2) at the first turn start in
  deficit, and dies when the status runs out while the food is still short; it recovers once the food is back. Built
  on the engine's status timing [src `UnitTurnManager.startTurn`, `MapUnit.setStatus`, `removeStatus`]; 4 hunger
  status promotions added.
* Spirit Springs (灵泉) replace the invented stone vein: a rare Strategic resource that cannot be traded, improved by a
  Spring Cave; every major has a start bias towards one; the Awakening Grounds (and Gu Yue's flower sea) need an
  improved spring in the city instead of the capital. Hill loses its extra start resource.
* `docs/LORE_MAPPING.md` (125 rows) and `tools/slice1_prototype.py` updated together; the prototype passes `check_all`
  including Unciv 4.22.8's own validator (0 errors, 0 warnings) and `ladder_check` (14,742 states, 0 errors).
* No ruleset JSON yet: Phase 1 waits for the user's approval (⛔).

## Phase 1, round 4 — hunger deaths by roll, Phase 1 approved (2026-10-13)

* The user's option B: when a hunger status runs out while the food is still short, each Gu dies with a 50% chance
  (`<with [50]% chance>`, seeded per unit and turn [src `Conditionals.getStateBasedRandom`]); a survivor gets the
  status again and rolls 3 (rank 1) or 5 (rank 2) turns later. Before, every holder of the food died at the same turn
  start, because the civ's resource count is not refreshed between units [src].
* The user approved Phase 1 and set the tuning rule: autoplay with Strategic Balance on decides; the rank-1 hunger
  death rate decides whether the rank-1 threshold rises.

## Phase 2, step 1 — the Slice 1 ruleset, generated (2026-10-17)

* `tools/gen_ruleset.py` writes the mod's `jsons/` (22 files, 403 distinct uniques) from `data/*.csv`
  (`tech_columns`, `techs`, `gu_masters`, `gu`, `gu_foods`, `hunger`) plus the one-of-a-kind content (events,
  policies, nations, buildings...). Its output is byte-identical to the validated Phase 1 prototype, which is removed.
  `--out DIR` writes a variant; `--check` detects a stale `jsons/`.
* `data/hunger.csv` holds the hunger meter per rank (status length, death chance): the user's tuning lever.
* 88 placeholder icons (`Images/`), `preview.png`, and the packed atlas for Android (`game.atlas`, `game.png`,
  `Atlases.json`).
* Self-tests now check the real mod: `jsons/` matches `data/`, `docs/LORE_MAPPING.md` quotes exactly its uniques, and
  the ladder check (14,742 states, 0 errors) runs on it. `ladder_check.py` defaults to the mod.
* README: installation, Strategic Balance recommendation, credits and disclaimer.
* Not yet: civilopedia text, the primeval-stones rename, the Indonesian translation, autoplay data.

## Phase 2, step 2 — headless autoplay and the first data (2026-10-17)

* `tools/autoplay.py` + `tools/autoplay/Autoplay.java`: headless AI-vs-AI games on the mod through the engine's own
  simulation path, compiled against the release jar (no Unciv build). Per-round metrics per civ, including Gu hunger
  starts, deaths and recoveries per rank; pooled summary; `--mod`/`--majors` for control rulesets. A self-test plays
  8 turns.
* `docs/AUTOPLAY.md`: 24 baseline games x 100 turns (Strategic Balance on): no crash, AI solvent (upkeep 30–38% of
  gross stone income), hunger meter works but almost never fires (0.5% of rank-1 holder-turns in deficit, 6 deaths),
  almost no trade, no wars (Vanilla control: none either), springs owned by every clan but improved late. Three A/B
  variants: a second starting laborer doubles the springs improved by T50; more yield does not help.
* Per the user's rule the rank-1 hunger threshold stays (the trigger condition is not met). No tuning applied.

## Phase 2, step 3 — round 5: King and Emperor, 200 turns (2026-10-17)

* The user chose option B. `tools/autoplay.py` reports the new metrics (share of rank-1 holder-turns in deficit, Gu
  hunger deaths per clan per 100 turns, games with a war, captured cities, pillaged tiles).
* `docs/AUTOPLAY.md`: 12 King + 12 Emperor games x 200 turns and a Vanilla control. No crash. Hunger stays
  irrelevant (0.17–0.40% of rank-1 holder-turns in deficit; every Gu food in surplus), so the rank-1 threshold stays.
  New findings: conquest almost never happens (1 captured city in 24 games vs 6 in 6 Vanilla games), the ladder stalls
  at rung 1 (no Killer Move in 30 games), the tech tree runs out around turn 120. No tuning applied.

## Phase 2, step 4 — war works: cities can fall, Moon fights in melee, first art (2026-10-17)

* Root cause of "no city ever falls": the engine adds city strength by the share of the tech tree known (+118 with
  every tech; Slice 1's 15 techs are done by turn ~120). `cityStrengthFromTechsFullMultiplier` 0.1 caps it at +12
  (variants 0.1/0.17/0.25 tested; 0.1 chosen under the user's "seru seperti di novel"). Engine fact E8.
* Moon Gu Masters are melee (13/20/29) and open every clash with a unit by throwing a moon blade (40% of their
  strength, a documented unique); ranged Moon armies could never take a city and were eliminated instead. Tested
  against a 50% variant. Result at King/200 turns: wars in 5–9 of 12 games, 13 cities captured, 2 clans eliminated,
  Moon clans capture too.
* Attack sounds per path (throw, whoosh, nonmetalhit, shot for wolves).
* Art: `tools/gen_art.py` + `tools/art/`: 19 original icons in Unciv's flat style and attack animations per attacker
  type (essence burst, moon blade, boar charge, lightning bite) for the default unit set; atlas repacked;
  `docs/ART.md` style guide. Remaining objects keep placeholders until the user approves the style.
* The repo is now `Reverend-Insanity-Gu-World`; `main` holds the mod (the user allowed it).

## Phase 2, step 5 — every icon designed (2026-10-17)

* The user approved the art style; `tools/art/glyphs2.py` draws the 70 remaining icons (units, Gu and status
  promotions, aptitudes, resources, improvements, buildings, city-state types, nations, policy branches, policies,
  techs) in the same flat style and motif language. No placeholder is left; atlas repacked.
* `tools/autoplay.py` now counts every promotion a unit holds (`promotionHolders`). It used to count only Gu with a
  hunger meter, so Killer Move (which eats nothing) was never counted: the earlier claim "Killer Move appears in no
  game" was not measured. Corrected in docs/AUTOPLAY.md once re-measured.

## Phase 2, step 6 — cultivation unsticks the refinement ladder (2026-10-17)

* Every Gu Master in a city with a Gu Academy (or Wu's Martial Arena) gains 2 XP per turn until it holds a Killer
  Move (`data/gu_masters.csv` column `cultivationXP`). Autoplay, King, 200 turns, per clan: rank-2 Gu 0.71 → 5.1,
  Killer Move 0.04 → 2.8, stones 315 → 187, hunger deaths 0.12 → 0.45 per 100 turns (3 XP tested too).
* Correction: the earlier "no Killer Move in any game" came from a counting gap in the tool (fixed in step 5); the
  true baseline was 0.04 per clan.

## Phase 2, step 7 — civilopedia, Indonesian translation, primeval stones (2026-10-18)

* `data/civilopedia.csv`: original civilopedia text (English and Indonesian, cold and pragmatic, the Chinese term once)
  for 109 objects: eras, techs, units, Gu and status promotions, buildings, resources, improvements, policies, clans
  and city-states, victories, unit types. `gen_ruleset.py` attaches it as `civilopediaText`. City-state types have no
  civilopedia page (the schema rejects the field); eras carry it although the docs omit it ([src] `Era` is a
  `RulesetObject`).
* `tools/gen_translations.py` writes `jsons/translations/Indonesian.properties` (162 names and texts from
  `data/translations_id.csv`, the civilopedia, the rename) and `English.properties`. Gold is shown as **Primeval
  Stones** / **Batu Primordial** (the user's choice) by overriding every base key with the word Gold.
* Self-tests: translations up to date, every displayed string translated (ours or the base game's), placeholders
  kept, every new object has civilopedia text.

## Phase 2, step 8 — wild Gu, contested inheritances, 3D characters (2026-10-18)

* Wild Gu (the user's request, 1.2%): every Gu Master rolls 6% per turn, 1 in 5 of those corners a wild Gu (popup;
  the AI rolls): a Liquor Worm, Jade Skin Gu or Black Boar Gu, food-gated and ladder-safe; never the Moonlight Gu.
* Buried inheritances: a Gu Master in foreign land, once the clan knows Inheritance Lore, rolls 1% per turn for a
  rumour, real 1 in 2. Claiming adds a **Gu Inheritance** to the tile (new resource: never generated, not tradeable;
  +3 insight, +2 culture, +2 stones; improved by the new **Inheritance Dig**, +20% combat XP for the holder) and takes
  the tiles within 1, from whoever owns them, at a diplomatic cost: clans fight over it. Autoplay: 1.25 per game.
* Four events (two silent dice), one resource, one improvement: over the Slice 1 budget at the user's request.
* 3D characters: `tools/art/render3d.py` (SDF ray-marcher) and `characters.py` pre-render the twelve units as map
  sprites with civ-colour layers, UI portraits and per-unit Gu attack effects; `docs/ART.md` documents them.

## Phase 2, step 9 — primeval-stone icon, BALANCE.md, KNOWN_ISSUES.md (2026-10-18)

* The Gold stat icon and its in-text glyph (`Images/StatIcons/Gold.png`, `Images/EmojiIcons/Gold.png`) are a pale
  jade primeval stone, drawn by `tools/gen_art.py`; atlas repacked.
* Fix: a buried inheritance could land on a tile with a resource, and placing it deletes that resource [src
  `OneTimeAddResource`], so a clan's Spirit Spring could vanish. The rumour now needs `<in tiles without [resource]>`.
* `docs/BALANCE.md`: the knobs that decide the game (value, source, autoplay evidence, when to turn them), what the
  data says is off, and an inventory of all 510 tunable numbers with file, object, field or unique and where to edit,
  generated by the new `tools/gen_balance.py` (self-test: stale inventory fails). Found on the way: the tech columns'
  `buildingCost`/`wonderCost` are inert (every building sets its own cost).
* `docs/KNOWN_ISSUES.md`: validator output (the one schema warning explained), engine limits, accepted trade-offs,
  and what still needs a real game, with console commands.
* Civilopedia: the 14 one-sentence entries got a second sentence (MOD_SPEC asks for 2–4); generic pronouns made
  neutral.
* Autoplay round 6b (`docs/AUTOPLAY.md`): two more 12-game batches. Identical batches differ twofold in hunger deaths,
  so the round-6 figure (0.52) was a low draw; pooled over 36 games: 0.90 hunger deaths per clan per 100 turns, 1.75
  inheritances per game, 4 of 144 clans 20+ turns in the red (all at war, no disband spiral). The guard changes
  nothing measurable.

## Phase 2, step 10 — the vanishing Clan Settler (2026-10-18)

* Bug (the user, Android): "Clan Settler cannot be produced although the city has more than 5 population". Cause,
  reproduced headless on the 4.22.8 engine: with happiness below −10 the Vanilla rule `Cannot build [Clan Settler]
  units <when below [-10] [Happiness]>` hides the unit from the build list without any reason [src
  `BaseUnit.shouldBeDisplayed`]; every citizen adds unhappiness, so big cities make it worse. In normal play the
  settler was buildable in every probed city-turn (404 of 404, all four clans, AI and human).
* Fix: the same rule moved onto the unit as `Can only be built <when above [-11] [Happiness]>` with `Shown while
  unbuilable`: the Clan Settler stays in the list, greyed, with the reason ("Hanya dapat dibangun saat di atas -11
  Kebahagiaan"). Verified headless: happiness −23 → shown, with that reason; normal play unchanged.

## Phase 2, step 11 — population-draining events, game speed (2026-10-18)

* The user's capital at population 1 (Marathon, turn 321): its focus was Production, so its one citizen worked a
  0-food tile, and a human city does not re-check its tiles each turn [src] (KNOWN_ISSUES engine limit 10). An
  investigation of five hypotheses with engine probes found three faults in the mod:
  * "Abandon the outer fields" now halves growth in every city for 10 turns, instead of taking a citizen from every
    city (free at population 1, and the largest drain on every clan).
  * "Judge the traitor", "Strike first" and "Squeeze the mortals" need a capital above 3 population: at population 1
    the loss was void and the reward free.
  * Event chances keep their rate per era on every speed (`<on [speed] game speed>`: chance ÷ modifier, turn gates ×
    modifier, the wild-Gu and inheritance dice re-weighted). Marathon used to roll three times the disasters per era.
* Autoplay round 7 (`docs/AUTOPLAY.md`): cities at population 1 fall from 17% to 2.4% (Standard, turn 320) and from 19%
  to 3.4% (Marathon, turn 480); on Marathon population per city rises from 3.0 to 4.3 and clans in the red from 12 to 3
  of 24. Found on the way, not caused here: at Prince, 40 of 48 clans are in the red by turn 320 on Standard.
* `tools/autoplay.py` records capital population and cities at population 1 (`capitalPopMean`, `popPerCityMean`,
  `popOneCityShare`).

## MOD_SPEC_2 Gate and MOD_SPEC_3 Phase A3 (2026-10-18)

* `MOD_SPEC_2.md` and `MOD_SPEC_3.md` saved verbatim; `CLAUDE.md` points to both (precedence MOD_SPEC_3 > MOD_SPEC_2 >
  MOD_SPEC).
* MOD_SPEC_2 Gate passed: check_all green; the user's Android "Locate mod errors" all green on the latest download; the
  user's game ran past turn 300 (Marathon) without a crash; autoplay keeps the AI solvent to turn 100 (2 of 48 clans
  briefly in the red, at most 7 turns).
* Phase A3 (capability tests, no content JSON): promotions survive an upgrade across unit types; `Only available`
  with a unit conditional works on promotions; `Limited to [amount] per Civilization` blocks upgrades and reopens on
  death; `<upon losing a [mapUnitFilter] unit>` fires on death by turn damage but also on upgrade (new engine fact E9);
  per-civ AI promotion weights steer 83% of the AI's picks. Results and design rules in `docs/CAPABILITIES.md`;
  probes on the local throwaway branch `a3-capability-tests`.

