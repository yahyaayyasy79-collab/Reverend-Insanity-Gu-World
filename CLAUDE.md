# CLAUDE.md — Reverend Insanity: Gu World (Unciv base-ruleset mod)

Read `MOD_SPEC.md` completely at the start of every session; it is the contract. Talk to the user in **Bahasa
Indonesia**; repository files stay in English.

## Status

Phase 0 approved 2026-10-12 (user: technical choices "bebas" = my call). Phase 1 delivered 2026-10-12:
`docs/LORE_MAPPING.md` waits at its ⛔ checkpoint for the user's lore corrections (19 questions near its top).
No ruleset JSON before that approval. Then: apply the corrections to the document and `tools/slice1_prototype.py`
together, and start Phase 2 (Slice 1) by turning the prototype into `data/*.csv` + `tools/gen_*.py`.

## Decisions

* Unciv **4.22.8** (the user's version) — ref, docs and the release jar are pinned to it.
* Mod name / installed folder: **"Reverend Insanity Gu World"**. The user agreed to rename the GitHub repo to
  `Reverend-Insanity-Gu-World` (downloads turn dashes into spaces); they must do it themselves (pending; then
  update the remote URL). Pushing to the session branch works.
* Scaffold: clean skeleton; copy only engine-coupled infrastructure from Vanilla (CAPABILITIES.md).
* Refinement and ascension: per-unit XP promotions (E4: kept and self-removing), not unit-action buttons or a
  national project.
* Android atlas: packed here with the official jar (`tools/unciv_ci.py --pack`) and committed
  (`game.atlas`, `game*.png`, `Atlases.json`); `check_refs` flags a stale atlas.
* User platform: unknown (ask when giving install steps; docs/TESTING.md covers both).

## Setup (every fresh container: `ref/` is gitignored)

```
tools/fetch_ref.sh [TAG]                 # ref/unciv (docs, schemas, rulesets, source) + ref/Unciv-<tag>.jar
pip install -r tools/requirements.txt    # java is needed for the official validator (unciv_ci)
tools/check_all                          # self-tests, schema, uniques, refs, OFFICIAL validator, packaging
```

Single tools: `tools/check_schema.py`, `tools/lint_uniques.py`, `tools/check_refs.py`, `tools/unciv_ci.py [--pack]`,
`tools/make_placeholders.py [--dry-run|--force|--report|--preview]`; all accept `--mod PATH` and `--quiet`.
While designing, `printf '%s\n' "<unique>" | tools/unique_check.py` checks loose strings against uniques.md, and
`tools/slice1_prototype.py OUT && tools/check_all --mod OUT --no-self-test` checks the whole Slice 1 plan in context
(a self-test keeps it and `docs/LORE_MAPPING.md` in sync).
`unciv_ci.py` runs Unciv's own validator (`mod-ci`) on a temp copy — it is the closest thing to "Locate mod
errors" available here; report its OptionsOnly lines too.
See `tools/README.md`.

## Rules (MOD_SPEC §2, non-negotiable)

1. Ground truth is `ref/unciv/docs/Modders/` (uniques.md, Unique-parameters.md, Mod-file-structure/*) and the
   bundled rulesets, never memory. Docs win over the spec; report conflicts. Engine source (`ref/unciv/core`)
   only fills gaps the docs leave — mark such claims [src] and test them in game.
2. No invented uniques: every unique and `<conditional>` matches a documented pattern verbatim (case-sensitive),
   only `[...]` contents change. `tools/lint_uniques.py` enforces it. No pattern → say so, propose a fallback.
3. Always shippable: thin layers; `tools/check_all` green after every step; commit after every green step.
4. Strict JSON (no trailing commas, comments, duplicate keys, BOM). Read Unciv's bundled JSON with json5.
5. ASCII object names (they become image paths). Chinese terms only in civilopedia text.
6. Nothing copied from the novel, its translations, manhua or fan art. Original, short civilopedia text.
7. AI compatibility: core tension hits everyone automatically; human-only mechanics (unit-action buttons) are
   optional power. Every event choice carries `[relativeAmount]% weight to this choice for AI decisions`
   (check_refs enforces).
8. ⛔ checkpoints: stop, summarise in Bahasa Indonesia, wait for approval.
9. Scope, lore and taste are the user's decisions: ask. Technical defaults: decide, then report what and why.

Per step (MOD_SPEC §9): plan → implement → `tools/check_all` → fix → `CHANGELOG.md` → commit → report (what
changed, what to test in game, developer-console commands) → wait for the user's "Locate mod errors" output.
Repetitive content is generated from `data/*.csv` by `tools/gen_*.py`; commit table and output.

## Know before designing (details: `docs/CAPABILITIES.md`)

* E1 `"None"` events roll a **weighted** die using the AI-weight unique; the AI resolves Alert events the same way.
* E2 Unit effects in an event work only when the event was triggered from a unit (unit, promotion, ruins).
* E3 A unit's triggerable unique without trigger/action modifiers fires once at unit creation (aptitude).
* E4 (corrected in Phase 1) The AI never BUYS a promotion with `Doing so will consume this opportunity to choose a
  Promotion`. AI-compatible repeatable gamble: a kept promotion whose triggerables fire on purchase, plus
  `[This Unit] loses the [X] promotion <upon turn start>`; its `Unavailable` lines must close every state in which
  nothing can happen, or the AI pays XP for nothing.
* E5 `<with [N]% chance>` rolls per unique (never two chance-lines for one outcome) and rerolls on reload.
* The AI never presses custom unit-action buttons. A `Barbarians` nation must exist or barbarians never spawn.
* Docs/schema conflicts D1–D8 are listed in CAPABILITIES.md; follow the "We follow" column.

## Files

* `MOD_SPEC.md` — the spec (phases, systems S1–S8, budget, Definition of Done).
* `docs/CAPABILITIES.md` — per-system uniques, status, AI notes, impossibilities, docs conflicts, scaffold choice.
* `docs/LORE_MAPPING.md` — Phase 1: one row per Slice 1 object (lore, role, exact uniques, CANON/ADAPTED/INVENTED,
  [VERIFY]), questions for the user, refinement ladder, events in detail, balance starting numbers.
* `docs/TESTING.md` — install paths per platform, naming rules, reload rules, console commands for step reports.
* `CHANGELOG.md` — one entry per green step.
* `tools/` — checkers; `tools/tests/fixtures/capability_proof` proves every unique CAPABILITIES.md cites;
  `tools/slice1_prototype.py` validates every unique LORE_MAPPING.md quotes.
