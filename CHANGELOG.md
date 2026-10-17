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
