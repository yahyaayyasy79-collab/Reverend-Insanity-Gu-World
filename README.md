# Reverend Insanity: Gu World

An unofficial base-ruleset mod for [Unciv](https://github.com/yairm210/Unciv) (built and checked against **4.22.8**)
that adapts the dynamics of the novel *Reverend Insanity* (蛊真人) to a 4X game: Gu must be fed or they starve,
every breakthrough is a gamble, the world itself tries to kill you, paths conflict, and righteous and demonic are
strategies, not labels.

**Status: Slice 1 in development** — Qing Mao Mountain and the Southern Border: four clans (Gu Yue, Bai, Xiong, Wu),
three city-states, ranks one to four, the Moon and Strength paths. Icons are placeholders.

## Install

* **Download mod from URL** (desktop and Android): main menu → Mods → "Download mod from URL" → paste the repository
  URL (`https://github.com/<owner>/<repo>`). Unciv names the mod after the repository, turning dashes into spaces.
* **Desktop, manual:** put this folder into Unciv's `mods/` folder as `Reverend Insanity Gu World`, then restart
  Unciv.

Then: "Start new game" → "Base Ruleset" → **Reverend Insanity Gu World**. Recommended: turn on the **Strategic
Balance** resource option (every clan then starts near a Spirit Spring). Details, platform paths and the test loop:
[docs/TESTING.md](docs/TESTING.md).

GitHub topics for the in-game mod browser: `unciv-mod`, `unciv-mod-rulesets`.

## For developers

The ruleset in `jsons/` is generated: edit `data/*.csv` or `tools/gen_ruleset.py`, run `tools/gen_ruleset.py`, then
`tools/check_all` (includes Unciv's own validator). The design record is [docs/LORE_MAPPING.md](docs/LORE_MAPPING.md);
the rules for contributors are in [CLAUDE.md](CLAUDE.md) and [MOD_SPEC.md](MOD_SPEC.md).

## Credits and disclaimer

Unofficial, non-commercial fan work. *Reverend Insanity* (蛊真人) © Gu Zhen Ren. This mod contains no text, art or
translations from the novel, its translations, the manhua or fan art; all civilopedia text is original and all
icons are generated placeholders. Unciv is © its contributors (MPL-2.0); engine-coupled terrain, improvement,
difficulty and speed data are adapted from Unciv's bundled Vanilla ruleset.
