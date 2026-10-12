# CLAUDE.md — Reverend Insanity: Gu World (Unciv base-ruleset mod)

Read `MOD_SPEC.md` completely at the start of every session; it is the contract. Talk to the user in **Bahasa
Indonesia**; repository files stay in English.

## Status

Phase 0 (ground truth + tooling) done, waiting at the ⛔ checkpoint. Next: Phase 1 (`docs/LORE_MAPPING.md`),
only after the user approves. No ruleset JSON before Phase 1 is approved.

## Setup (every fresh container: `ref/` is gitignored)

```
tools/fetch_ref.sh [TAG]                 # default 4.22.8 = the version the docs were read at
pip install -r tools/requirements.txt
tools/check_all                          # self-tests + schema + uniques + refs + packaging; non-zero on error
```

Single tools: `tools/check_schema.py`, `tools/lint_uniques.py`, `tools/check_refs.py`,
`tools/make_placeholders.py [--dry-run|--force|--report|--preview]`; all accept `--mod PATH` and `--quiet`.
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
* E4 A promotion with `Doing so will consume this opportunity to choose a Promotion` is a repeatable one-shot
  effect the AI buys with XP: the AI-compatible way to give it gambles (refinement, ascension).
* The AI never presses custom unit-action buttons. A `Barbarians` nation must exist or barbarians never spawn.
* Docs/schema conflicts D1–D8 are listed in CAPABILITIES.md; follow the "We follow" column.

## Files

* `MOD_SPEC.md` — the spec (phases, systems S1–S8, budget, Definition of Done).
* `docs/CAPABILITIES.md` — per-system uniques, status, AI notes, impossibilities, docs conflicts, scaffold choice.
* `CHANGELOG.md` — one entry per green step.
* `tools/` — checkers; `tools/tests/fixtures/capability_proof` proves every unique CAPABILITIES.md cites.
