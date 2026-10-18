# TESTING — installing the mod and the in-game test loop (Unciv 4.22.8)

Verified against `ref/unciv` source and docs; [src] = engine behaviour the docs do not state.

## Naming (decide before the first playtest)

* A mod's name **is its folder name** [src `RulesetCache`]. Saves store the base ruleset by that name, so desktop
  and Android installs must use the same folder name or saves will not load.
* "Download mod from URL" turns dashes into spaces and strips `-<branch>` [src `GithubAPI`, `Github.kt`]:
  repo `Unciv-mod` → mod **"Unciv mod"**; a branch with a slash (`claude/...`) is never stripped →
  "Unciv mod claude mod spec phase 0 8fxznp".
* A manually created folder keeps dashes. Name it `Reverend Insanity Gu World` (spaces) to match what a download of
  a repo named `Reverend-Insanity-Gu-World` produces.
* Recommendation (user's call): rename the GitHub repo to `Reverend-Insanity-Gu-World`; test from `main` or a
  branch without `/` (e.g. `dev`).

## Install

**Desktop (development).** Mods live in `<data dir>/mods`; the data dir is the working directory or `--data-dir=`
[src `DesktopLauncher`]. Find it by locating `GameSettings.json` after one launch. Typical: Windows MSI
`%APPDATA%\Unciv`; portable zip: next to `Unciv.exe`; Linux `Unciv.sh`/AUR `~/.local/share/Unciv`; Flatpak
`~/.var/app/io.github.yairm210.unciv/data/unciv`. Create `mods/` if missing, then either clone into
`mods/Reverend Insanity Gu World` or link a checkout there (`mklink /J` on Windows, `ln -s` elsewhere; Flatpak needs
`flatpak override --user --filesystem=<checkout>`). Restart Unciv: atlases are packed at launch only, and only if a
top-level `Images/` folder exists.

**Download mod from URL (desktop and Android).** Main menu → "Mods" → "Download mod from URL" → paste
`https://github.com/<owner>/<repo>` or `.../tree/<branch>` (https:// required, no `.git`, no trailing space) →
"Download". Public repos only. Re-paste the same URL to update; it replaces the folder cleanly.

**Android.** Use the URL download; the manual `Android/data/com.unciv.app/files/mods` route is usually unwritable
from the phone since Android 11, and its copy merges without deleting [src `AndroidLauncher.copyMods`]. Android
cannot pack atlases: without a committed `game.atlas` + `game.png` (+ `Atlases.json`) icons are blank circles.
Never commit `Atlases.json` without the atlas it lists (validation error that blocks the base ruleset).

## Play and check

* "Start new game" → "Base Ruleset" dropdown → the mod (listed only when `jsons/ModOptions.json` has
  `"isBaseRuleset": true`). A base with Error-severity problems is refused with "incorrectly defined".
* Options → "Locate mod errors" (also: Mods → select mod → "Check [mod]"). The tab exists only when a mod loaded at
  startup. Keep "Check extension mods based on:" on the default. "Copy to clipboard" appears when a mod has problems;
  the copied text has **no severity prefixes**, so also report the line colours (red Error, orange ErrorOptionsOnly,
  yellow Warning).
* A JSON parse error removes the mod from every list [src]; a broken `ModOptions.json` silently makes it a non-base
  extension. `tools/check_all` catches both before you launch.
* Never press "Autoupdate mod uniques", "Delete [mod]" or "Update [mod]" on the development checkout: the first
  rewrites generated JSON, the others may follow a symlink and wipe the checkout.

## Before you launch: the official validator, here

`tools/unciv_ci.py` runs the 4.22.8 release jar's `mod-ci` mode — the same RulesetValidator as "Locate mod
errors" — on a temporary copy (part of `tools/check_all`). `tools/unciv_ci.py --pack` also writes the atlas Android
needs; commit `game.atlas`, `game*.png` and `Atlases.json` together. In-game checking remains the final word for
behaviour, not for syntax.

## Reload rules

| Changed | Takes effect after |
|---|---|
| `jsons/*.json` | Locate mod errors → "Reload mods", then a new game (running games keep their ruleset) |
| `Images/**` | full restart (packing happens at launch; delete `game.atlas` after removing images) |
| `jsons/translations/*.properties` | restart or a language change |

## Developer console

Open with the backtick key on the world screen (desktop) or long-press the hamburger menu → "Developer Console"
(mobile); Enter on empty input lists commands. Names with spaces: `"Quoted Name"` or `dashed-name`.

```
civ activatetrigger "Triggers a [Beast Tide] event"      # any Triggerable unique; validated against the ruleset
unit activatetrigger "Triggers a [Refinement Attempt] event"  # same, with the selected unit as context (E2)
civ activatetrigger "Instantly provides [100] [Immortal Essence Stone]"
civ addstat Gold 500          civ revealmap               civ addtech <civ> "<tech>"   (not "addtechnology")
civ addpolicy <civ> "<policy>"                            unit add <civ> "<unit>"      (select a tile first)
unit addpromotion "<promotion>"    unit setxp 100         city addbuilding "<building>"  city setpop 8
civ checkcountable "[[Gu Master] Units]"                  unit checkfilter "<mapUnitFilter>"
```

Hidden Debug tab (long-press / right-click "Options"): "Simulate until turn:" automates every civ — use it for the
100-turn AI-solvency test (MOD_SPEC §10–11).

## Translations

The mod's translations are generated here: `tools/gen_translations.py` writes `jsons/translations/Indonesian.properties`
and `English.properties` from `data/translations_id.csv` and `data/civilopedia.csv` (the user plays on Android, where
the in-game generator does not exist). To test: Options → Language → Bahasa Indonesia, then reload the mod. For
reference, the desktop-only in-game tool: create `jsons/translations/Indonesian.properties` with at least one real
`key = value` line, then Options → Advanced → "Generate translation files" with the mod selected; without the seed
line it silently does nothing, and it also writes `completionPercentages.properties` into the mod.
