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
| `autoplay.py` | headless AI-vs-AI games on the mod (`tools/autoplay/Autoplay.java`, compiled with `javac` against the release jar; the engine's own simulation path): N games x T turns, Strategic Balance on by default, one JSON line per civ per round (stones, upkeep, resources and deposits, buildings, units, Gu holders, hunger starts/deaths/recoveries per Gu rank, trades, wars) and a pooled summary. `--mod` + `--majors` run other rulesets (the Vanilla control). Results and method: `docs/AUTOPLAY.md`. A self-test plays 8 turns. |
| `gen_art.py [--sheet FILE]` | the mod's original art from `tools/art/`: flat icons in Unciv's style (white or black silhouette, 100x100) and attack animations per attacker unit type for the default unit set; overwrites only its own files and placeholders (PNG tag `GeneratedArt`). Repack the atlas afterwards (`unciv_ci.py --pack`). |
| `gen_translations.py [--check]` | `jsons/translations/Indonesian.properties` (names, cities, leaders, event texts and choices, ruin notifications from `data/translations_id.csv`; civilopedia from `data/civilopedia.csv`) and `English.properties`; both carry the primeval-stones rename of every base key with the word Gold, read from the release jar. Self-tests check it is up to date, covers every displayed string and keeps placeholders. |
| `uniques_db.py` | parser shared by the linters; `python3 tools/uniques_db.py` prints pattern counts and detects `UniqueTarget` drift. |

Validation of the validators: run on the bundled rulesets (converted to strict JSON), `lint_uniques` reports zero
false positives on 1,698 G&K and 1,278 Vanilla uniques apart from the `Aircraft` filter marker, and `check_schema`
zero errors. `tests/` holds a broken mod every checker must catch, and the capability proof every unique cited in
`docs/CAPABILITIES.md` must pass — and it passes the official validator with zero findings.
`tests/` also checks that `jsons/` matches `data/`, that `docs/LORE_MAPPING.md` quotes exactly the uniques in `jsons/`,
and that the refinement ladder passes `ladder_check`.
