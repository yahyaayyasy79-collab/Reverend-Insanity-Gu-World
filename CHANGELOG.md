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

