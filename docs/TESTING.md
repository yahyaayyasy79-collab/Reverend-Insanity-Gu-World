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
cannot pack atlases: without the committed atlases (`game.*`, `Units.*`, `Atlases.json`) icons are blank circles.
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

## The Five Regions map

The immortal arc's world: New game → Map type **Custom** → **Five Regions**, with "Select players from starting
locations" on. The Central Continent (Heavenly Court and three sects), the Northern Plains (Huang Jin), the Western
Desert (Fang Clan), the Eastern Sea (Zombie Alliance and the merfolk on islands) and the Southern Border (Gu Yue,
Bai, Xiong, Wu and three city-states) are sealed by region walls: mortals stay in their region until their clans raise
immortals, which cross the walls. Twelve secret realms stand in their canon regions.

## The Qing Mao Mountain map

New Game → choose the mod as base ruleset → **Map Type: Custom** (the premade maps of the selected mods are listed)
→ **Qing Mao Mountain**. Turn on "Select players from starting locations" to give each clan its canon village (Bai
north, Gu Yue centre, Xiong south, Wu east). Recommended: Prince or King; the AI clans rarely start wars at Settler to
Prince, so the tension comes from tides, hunger, betrayals and you.

## Before you launch: the official validator, here

`tools/unciv_ci.py` runs the 4.22.8 release jar's `mod-ci` mode — the same RulesetValidator as "Locate mod
errors" — on a temporary copy (part of `tools/check_all`). `tools/unciv_ci.py --pack` also writes the atlas Android
needs; commit every `*.atlas`, its `.png` and `Atlases.json` together. In-game checking remains the final word for
behaviour, not for syntax.

## Reload rules

| Changed | Takes effect after |
|---|---|
| `jsons/*.json` | Locate mod errors → "Reload mods", then a new game (running games keep their ruleset) |
| `Images/**`, `Images.Units/**` | full restart (packing happens at launch; delete the `.atlas` files after removing images) |
| `jsons/translations/*.properties` | restart or a language change |

## Developer console

Open with the backtick key on the world screen (desktop) or **long-press** the ☰ menu icon (top left) → "Developer
Console" (mobile; a normal tap opens the menu without that button, and the console is off when more than one human
plays) [src `WorldScreenMenuPopup`, `ActivationTypes.Longpress`]; Enter on empty input lists commands.

* **Civ names** are the nation names, written lowercase with dashes or in quotes: `gu-yue-clan`, `bai-clan`,
  `xiong-clan`, `wu-clan`, `heavenly-court`, `huang-jin-family`, `zombie-alliance`, `fang-clan` (or `"Gu Yue Clan"`).
  `<civ>` in a command is a placeholder, never typed as is (the user's report, 2026-11-01).
* **Tech command:** `civ addtechnology <civName> <techName>` on 4.22.15 [src ConsoleCivCommands] (4.22.8 called the
  key `addtech`). Use the name the console's own list shows.
* `unit ...` commands act on the **selected unit**; `unit add` places on the **selected tile**; `civ activatetrigger`
  acts on the civ you play unless its first word is a civ name. Uniques and names with spaces go in quotes.

Quick start for the immortal arc (as Gu Yue; select one of your own land tiles first):

```
civ addtechnology gu-yue-clan "Calamity Lore"
civ activatetrigger "Instantly provides [60] [Heaven Qi]"
civ activatetrigger "Instantly provides [60] [Earth Qi]"
civ activatetrigger "Instantly provides [60] [Human Qi]"
unit add gu-yue-clan "Rank Five Gu Master"
unit setxp 300                      # select the new unit first, then buy Ascension on its promotion screen
```

Path power scaling (Civilopedia > Tutorials > "Gu World: Power Scaling"; select a Gu Master first):

```
unit addpromotion "Fire Master"             # each attack: Burning 2 turns (3 with Dao Marks III); see the promotion
unit addpromotion "Fire Grandmaster"        # +6 damage per attack; the killer move button Five-Finger Flame Chain
unit addpromotion "Dao Marks V"             # Burning lasts 4 turns now: attack an enemy and read the notification
```

Immortal lifespan and Gu hunger (Civilopedia > Tutorials > "Gu World: Immortal Lifespan", "Gu World: Gu Hunger and Food"):

```
unit addpromotion "Moonlight Gu"     # on more Gu Masters than the clan has Moon Orchid (each eats 1): at the next turn
                                     # start each shows "Moonlight Gu Hunger 33%", then 67%, then 100% (the death roll)
unit addpromotion "Advance to Rank Seven"                      # on a Rank Six immortal at home: +25 Lifespan Gu
```

Attack sounds and animations (your own attacks only; the AI's play no path sounds): pick a Gu Master, then

```
unit addpromotion "Fire Master"              # attack an enemy: rank body + fire whoosh and crackle
unit addpromotion "Fire Grandmaster"         # the same attack now strikes twice (echo); the killer move swells first
unit addpromotion "Dao Marks V"              # a three-bell chord rings over every attack
unit add gu-yue-clan "Venerable"             # select a tile first: the Venerable's strike, choir and thunder
```

Dao marks (select one of your Gu Masters first; the tiers replace one another, the icon shows the stars):

```
unit addpromotion "Dao Marks III"           # +30% strength since the power rebuild; see it on the promotion list
unit setxp 300                              # Dao Comprehension is automatic: a rank-three+ path Master shows it
                                            # as a 20-turn status (Standard); when it runs out, the tier goes up
```

Phase D, 2026-11-02 (regional conflict, Gu catalog, power rebuild, combination moves):

```
# a Five Regions game: minor clans in every region (Man, Ge, Lang Ya north; Lan, Mo, Xiao west; Song, Xia, Merman
# east; Immortal Crane, Spirit Affinity, Combat Immortal centre); Demonic Dens on the map
unit add barbarians "Demonic Gu Master"     # select a tile beside your city: a raider (18 strength, +20% attacking)
civ activatetrigger "Triggers a [Wandering Gu Master] event"   # hire, send away or rob a lone Gu Master
# Gu catalog: a unit buys a catalog Gu with XP once it holds the path's Master and its rank reaches the Gu's
unit addpromotion "Ice Master"
unit setxp 200                              # open the promotions: Ice Knife Gu (rank 2) and Icicle Gu appear
# combination move on a Rank Three+ Gu Master: Ice Knife Gu + Whirlwind Gu, comprehension Ice and Wind Grandmaster
unit addpromotion "Ice Knife Gu"
unit addpromotion "Wind Master"             # end the turn: Whirlwind Gu arrives (granted with the Master)
unit addpromotion "Ice Snow Grandmaster"
unit addpromotion "Wind Grandmaster"        # now the Ice Blade Storm button shows (20 stones, 1 movement)
# one-of-a-kind immortal Gu: give your capital the wonder, then let one immortal carry it
city addbuilding "Star Mark Immortal Gu"    # (or build it: Immortal Gu Recipes)
unit setxp 300                              # on a Rank Six Gu Immortal: the Star Mark Immortal Gu Bearer promotion
                                            # appears; once taken, a second unit of yours can no longer take it
unit addpromotion "Star Grandmaster"        # with Star Master and Star Great Grandmaster too: the Star Mark
unit addpromotion "Star Great Grandmaster"  # Resonance button shows (3 green grape essence)
```


```
civ activatetrigger "Triggers a [Beast Tide] event"      # any Triggerable unique; validated against the ruleset
unit activatetrigger "Triggers a [Refinement Attempt] event"  # same, with the selected unit as context (E2)
civ activatetrigger "Instantly provides [100] [Green Grape Immortal Essence]"
civ addstat Gold 500          civ revealmap               civ addtechnology gu-yue-clan "<tech>"
civ addpolicy gu-yue-clan "<policy>"                      unit add gu-yue-clan "<unit>"  (select a tile first)
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
