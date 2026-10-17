# tools/

Python 3.10+ checkers that approximate Unciv's Ruleset Validator. The in-game Options tab
**"Locate mod errors"** stays the final authority.

```
tools/fetch_ref.sh [TAG]          # ref/unciv: docs, schemas, G&K + Vanilla rulesets, engine source (default 4.22.8)
pip install -r tools/requirements.txt
tools/check_all [--quiet]         # everything below; exit 1 on any error
```

| Tool | Checks |
|---|---|
| `check_schema.py` | strict JSON (no trailing commas/comments/duplicate keys/BOM), every `jsons/*.json` and `jsons/TileSets/*.json` against `docs/Modders/schemas`, unknown file names, undeclared keys where the schema is permissive. Known docs-vs-schema gaps (`SCHEMA_GAPS`) are warnings. |
| `lint_uniques.py` | every unique: base and each `<modifier>` must match a pattern parsed from `uniques.md` (all sections); applicability to the object ("Applicable to" + `UniqueTarget` inheritance); modifier acceptability; "does not support conditionals"; parameter types (numbers, stats, fixed vocabularies strictly; names of units, buildings, techs, resources, stockpiled resources, promotions, policies, eras, events… must exist; filters atom by atom, unknown atoms are warnings). Intentional filter markers go in `unique_allowlist.txt`. |
| `check_refs.py` | `requiredTech`, `prerequisites` (+ cycles), `upgradesTo` (+ cycles), `obsoleteTech`, `replaces`, `uniqueTo`, `requiredResource`, era/difficulty starting units and buildings, victory milestones and spaceship parts, `Triggers a [...] event` targets, orphan and circular events, AI weight on every event choice (MOD_SPEC rule 7), base-ruleset completeness (Land + Water terrain, city founder, `Barbarians`/`Spectator` nations), ASCII names, an icon for every object (warning). |
| `unciv_ci.py` | Unciv's **own** RulesetValidator: runs the release jar's `mod-ci` (from `ref/Unciv-<tag>.jar`) on a temporary copy, maps Error/Warning/OK lines to the reporter, flags JSON the autoupdater would rewrite (deprecated uniques), and with `--pack` copies the packed atlas (`game.atlas`, `game*.png`, `Atlases.json`) back for Android. Skipped with a warning without java or the jar. |
| `check_package.py` | Unciv's "Download mod from URL" heuristic: mod entries must outnumber other top-level entries. |
| `make_placeholders.py` | placeholder PNGs at the exact icon paths for objects without art (neither in the mod nor the base game), colour by category, tagged `Placeholder=true`; never overwrites real art. `--dry-run`, `--force`, `--report`, `--preview`. |
| `unique_check.py` | quick pattern check for loose unique strings (stdin or args) before they sit in a ruleset: base + every modifier must match uniques.md; prints the "Applicable to" targets. Used while designing (Phase 1 tables). |
| `gen_ruleset.py [--out DIR] [--check]` | **generates the mod's `jsons/`** from `data/*.csv` (tech tree, Gu Master units, Gu promotions and foods, the hunger meter per rank) plus the one-of-a-kind content in the script; removes JSON files it no longer writes. `--out DIR` writes a throwaway copy (variants for autoplay), `--check` exits 1 if the committed `jsons/` is stale (a self-test runs it). Edit `data/` or the script, never `jsons/` by hand. |
| `ladder_check.py [MOD]` | exhaustive check of the refinement ladder in a ruleset (default: the mod): in every reachable unit state at most one chance line matches, an attempt climbs at most one rung, the refining choices and Refine Gu close exactly where nothing can be gained, and no rung overdraws a Gu food. Run by the self-tests. |
| `uniques_db.py` | parser shared by the linters; `python3 tools/uniques_db.py` prints pattern counts and detects `UniqueTarget` drift. |

Validation of the validators: run on the bundled rulesets (converted to strict JSON), `lint_uniques` reports zero
false positives on 1,698 G&K and 1,278 Vanilla uniques apart from the `Aircraft` filter marker, and `check_schema`
zero errors. `tests/` holds a broken mod every checker must catch, and the capability proof every unique cited in
`docs/CAPABILITIES.md` must pass — and it passes the official validator with zero findings.
`tests/` also checks that `jsons/` matches `data/`, that `docs/LORE_MAPPING.md` quotes exactly the uniques in `jsons/`,
and that the refinement ladder passes `ladder_check`.
