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
