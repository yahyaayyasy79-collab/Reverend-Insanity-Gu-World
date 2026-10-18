# Known issues — Slice 1

State on 2026-10-18, Unciv 4.22.8. MOD_SPEC §11 asks that every remaining validator warning is explained here; the
rest of the list is what a player or the next session should know before trusting the mod.

## Validator output

| Check | Result | Note |
|---|---|---|
| Unciv's own validator (`tools/unciv_ci.py`, the release jar's `mod-ci`, the same code as "Locate mod errors") | 0 errors, 0 warnings, no OptionsOnly lines | The user's "Locate mod errors" on Android was all green on 2026-10-17; re-run it after each download |
| `tools/check_schema.py` | 1 warning: `jsons/Eras.json: key "civilopediaText" documented but missing from Eras.schema.json` | Harmless. The bundled schema lags the engine: an Era is a `RulesetObject` and reads `civilopediaText` [src `Era.kt`], and Unciv's validator accepts it. Recorded in `SCHEMA_GAPS` (tools/check_schema.py). Check in game: Civilopedia → Eras shows the text |
| `tools/lint_uniques.py`, `tools/check_refs.py`, packaging | 0 errors, 0 warnings | — |

## Engine limits (no mod can change them)

1. **Unciv draws 2D sprites.** The "3D" characters are rendered here (`tools/art/render3d.py`) into flat sprites,
   portraits and attack frames; they do not rotate. Unciv has no idle or death animation; a unit that dies simply
   disappears.
2. **The attack effect belongs to the attacking unit, not to its Gu.** Unciv picks `<unit name or unit type>-attack-N`
   [src], so the effect follows the path and the rank (moon blade, boar charge, lightning, essence burst), not the
   specific Gu a unit carries. A Strength Gu Master with a Jade Skin Gu still charges like a boar.
3. **Sprites on the world map are hex-sized.** The detail of the 3D models shows in the portraits (unit panel, city
   screen, Civilopedia); on the map they read as silhouettes with clan colours.
4. **The AI never presses unit-action buttons and resolves popups by weight** (E1): it claims a buried inheritance 2
   times in 3 and never "chooses" among wild Gu, it rolls.
5. **Gaining a Gu does not refresh the civ's resource count** [src]: a wild Gu or a refinement can overdraw a food for
   a turn; the hunger meter then does its job. See `docs/LORE_MAPPING.md`, "Known limits" 1–8, which all still hold.
6. **Chance rolls reroll on reload** (E5): a player can reload to fish for a wild Gu or an inheritance.
7. **Three multi-line base-game tutorial texts still say "Gold"/"Emas"** (Civ V notes on natural wonders and city
   focus). `tools/gen_translations.py` skips keys with line breaks rather than risk breaking them.
8. **Tech-column building costs are inert.** `data/tech_columns.csv` `buildingCost` and `wonderCost` only apply to a
   building without its own cost [src `Ruleset.updateBuildingCosts`]; every Slice 1 building sets one.

9. **A construction blocked by a `Cannot build` unique vanishes from the build list without a reason** [src
   `BaseUnit.shouldBeDisplayed`: `CannotBeBuilt` is never shown]. The user hit it on 2026-10-18 with the Vanilla
   settler ban (happiness below −10): the Clan Settler disappeared and looked broken. The ban now sits on the unit as
   `Can only be built <when above [-11] [Happiness]>` plus `Shown while unbuilable`, so it stays in the list, greyed,
   with the reason. Use that pattern for every future conditional ban.

## Design trade-offs (accepted, watched)

1. **Claiming an inheritance steals land.** The tiles in a 1-tile radius change owner, city-states' included, and
   each stolen tile costs relations with the old owner [src `OneTimeTakeOverTilesInRadius`]. Far from home the claim
   becomes an exclave of the nearest city. That is the intended war trigger; a human game must show it is not a
   permanent grudge machine.
2. **An inheritance never appears on a resource tile.** Placing it would delete the tile's resource [src
   `OneTimeAddResource`], so a Spirit Spring could vanish; the rumour trigger carries `<in tiles without [resource]>`.
3. **Popups.** Each Gu Master rolls 1.2% per turn for a wild Gu; with ten Gu Masters the human sees one wild-Gu popup
   every eight turns or so, plus the rare inheritance.
4. **The wild Liquor Worm needs wine** (a Tavern): the AI almost never has spare wine (0.02 per clan by turn 200).
5. **Balance verdicts not acted on yet** (light early upkeep, a calm late game, food abundant in peace, 4 of 144 AI
   clans 20+ turns in the red during long wars, the tech tree ending near turn 120): `docs/BALANCE.md`, "What the
   data says is off".
6. **Springs are improved late:** the AI keeps one Mortal Laborer per city [src `ConstructionAutomation`]; the user
   wants laborers produced, not given.
7. **Over the Slice 1 budget at the user's request:** 9 events instead of 5 and 7 resources instead of about 6
   (round 6, `docs/LORE_MAPPING.md` "Budget").

## Not yet seen in a real game

Autoplay runs the engine headless; these need eyes on a screen (Android first). Commands: `docs/TESTING.md`,
"Developer console".

| What | How to reach it |
|---|---|
| 3D sprites, clan colours, portraits | Start a game; `unit add <civ> "Rank Four Moon Gu Master"` next to a Strength one |
| Attack effects per path | Put a Moon and a Strength Gu Master next to a wolf (`unit add Barbarians "Lightning Wolf"`) and attack |
| Primeval-stone icon in the top bar and in texts | Any game; the stone replaces the gold coin in the stats bar, the city screen and notifications |
| Wild Gu popup | Select a Gu Master: `unit activatetrigger "Triggers a [Wild Gu Caught] event"` (have Jade or Wild Boar) |
| Buried inheritance, tile steal | Gu Master on a resource-free land tile beside a rival's border: `unit activatetrigger "Triggers a [Buried Inheritance] event"`; then `civ addtech <civ> "Inheritance Lore"` to build the Inheritance Dig |
| Hunger meter (E7) | Trade or pillage away all Moon Orchid as Gu Yue; Moonlight Gu holders weaken at once and about half lose the Gu two turns later |
| Moon blade before melee | Attack a unit with a Moon Gu Master: two damage numbers (blade, then melee); against a city only one |
| Indonesian text | Options → Language → Bahasa Indonesia; every name, event and Civilopedia page should be translated |
| 100 turns without a crash, AI solvent | The Definition of Done's last item: the user's own game (Debug tab → "Simulate until turn" also works) |
