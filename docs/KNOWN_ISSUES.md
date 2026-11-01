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

10. **A human city does not re-check its worked tiles each turn; an AI city does** [src `CityTurnManager.startTurn`].
    A human city stuck at population 1 on a 0-food tile (a hill Spring Cave or mine) never grows, and never triggers
    the re-check that growth would. The user's capital sat at population 1 on turn 321 (Marathon) for exactly this
    reason: its focus was set to Production. A pop-1 city lands on a 0-food tile through Production or Gold focus, a
    locked tile, an idle citizen, or a re-check made while unhappy (growth food then counts for little) or while
    stones per turn were negative (the engine doubles the weight of gold) [src `Automation.rankStatsForCityWork`].
    Remedy in game: Default (Bawaan) or Food focus, then "Atur Ulang Warga Negara" (reset citizens). Not fixed in the
    ruleset: the only lever, a richer city centre, would speed up every clan's growth and needs its own autoplay A/B.
11. **Autoplay cannot stand in for a human's events:** the engine's simulation mode plays a human civ's turns but
    drops its Alert events, so a human-flagged civ in a simulation never loses population to them
    (`docs/AUTOPLAY.md`, round 7). `tools/autoplay.py` keeps every civ AI for that reason.
12. **Game speed.** Since round 7 every random event keeps the same rate per era on every speed (chance divided by the
    speed modifier, turn gates multiplied; chances are whole numbers, so Marathon's beast tides run about 20% above
    the Standard rate per era). What still counts per turn and so weighs differently on slower speeds: timed effects
    (`<for [N] turns>`), flat stone gains and costs of events (building and unit costs scale with speed, event stones
    do not), cultivation XP (2 per turn, so Gu Masters climb the ladder faster per era on Marathon), and the hunger
    meter's turn counts. Balance was measured on Standard.

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
5. **Balance verdicts not acted on yet** (light early upkeep, a calm late game, food abundant in peace, 11 of 48 AI
   clans at Prince still 20+ turns in the red by turn 320 on Standard after round 8, the tech tree ending near turn
   120): `docs/BALANCE.md`, "What the data says is off".
6. **Springs are improved late:** the AI keeps one Mortal Laborer per city [src `ConstructionAutomation`]; the user
   wants laborers produced, not given.
7. **Population costs need a population:** "Judge the traitor", "Strike first" and "Squeeze the mortals" are open
   only while the capital has more than 3 population, and "Abandon the outer fields" halves growth for 10 turns instead
   of taking a citizen from every city (round 7). At population 1 those choices used to be free rewards, and taken
   with the AI's weights they kept capitals at 1-4 population by turn 320.
8. **Over the Slice 1 budget at the user's request:** 9 events instead of 5 and 7 resources instead of about 6
   (round 6), and since C3 12 clan units (`docs/LORE_MAPPING.md` "Budget").
9. **The look follows the clan, not the path (C3).** Unciv picks a unit's map sprite and attack animation by unit
   name or unit type only [src `BattleTableHelpers.getAttackAnimationLocation`], never by promotion. The four
   signature clans train their own rank 2-4 units, drawn and animated in their signature path (Gu Yue moon, Bai
   water, Xiong strength, Wu wind); about 15% of their cultivators take another path and still look like the clan's.
   Every other cultivator uses the neutral rank units and the rank-one essence burst.
11. **The AI clans are slow to go to war at Prince.** Unciv's AI attacks only when its units can take a city without
   dying and its motivation clears trade, friendship and pact penalties [src `MotivationToAttackAutomation`]; with
   every clan righteous the villages were unassailable (0 wars in 12 games). Guardian Formations now gives +10% city
   strength, not +25% (3 of 12 games with a war); King plays more aggressively.
10. **A Rank One may hold a path (C3).** It climbs that path's first rung only; the fusions wait for rank two. An
   unpathed D-grade Rank One still loses the Gu Yue emblem at once (canon), a D-grade Moon Master keeps it.

12. **A blessed land is a promotion, not a building (C1).** The free-building unique cannot give a second immortal
    of the same grade its own land, so the land lives on the immortal: it shows among the unit's promotions and is
    lost with the unit. Its essence and stones arrive at turn start, not in the per-turn stat preview.

13. **No ascension in foreign land (C3).** Unciv's free special upgrade fails in foreign land without open borders and
    then crashes restoring the old unit [src UnitUpgradeManager.performUpgrade]; the Ascension promotion and its qi
    choices are closed there. Walk the master home first.
14. **The AI builds stat wonders first.** Star Eyes and Unravel Mystery go up in every autoplay game; Self Strength,
    Woman's Heart, Bone Spike and Divert Disaster rarely or never (they help units, which the AI weighs low), so a
    human can usually claim them.

15. **Secret realms are natural wonders (C4, done 2026-11-01).** On the Five Regions map the twelve stand in their
    canon regions; on generated maps Unciv scatters a few of them (naturalWonderCountMultiplier 0.3). Inheritances
    still surface anywhere, not in their canon regions.

16. **High immortals die young in autoplay (C5a).** Half the clans reach rank seven, but by turn 420 most of those
    immortals are gone (lifespan debt, unprepared tribulations, wars) and rank eight rarely lasts. Canon-like, but a
    lever if games feel thin at the top: tribulation odds, Lifespan Gu supply.

17. **No upgrade at sea (C5b).** Unciv places an upgraded unit before copying its promotions, so a Water Master
    standing on open water could not be placed and the game crashed restoring it. Ascension and rank advancement are
    closed on water, and every clan can embark land units from the start.
18. **The AI reaches a Venerable late and rarely** (Phase D): in 8-game batches of 500–550 turns, one or two AI clans
    become Venerables (T342–T494) and one won Eternal Life (T373). The AI never queues the two wonders, so both are
    promotions (Ascend to Venerable, Seek Eternal Life) and the wonders only markers. On the Five Regions map (6 × 500)
    no AI Venerable rose once the Zombie Alliance's immortals stopped making essence (before: 5 of 6 games won by it).
19. **Late-game AI debt on wide maps** (Phase D): Unciv's AI keeps training soldiers while its stones per turn are
    positive, up to five per city outside war [src ConstructionAutomation], and every rank they climb then raises
    their upkeep without any decision of the AI. So the AI clans drift into the red late; on the wide Five Regions
    map (eight majors, about four villages each) 32 of 48 clans spent 20+ turns in the red by T400, against 9 of 48 on
    Qing Mao Mountain with the same eight majors by T300. The red is shallow and self-correcting (weaker units, the
    Stone Shortage event); a human who keeps the army lean does not hit it. Fixed on the way: the map's riches and
    the stability of wide clans.

## Not yet seen in a real game

Autoplay runs the engine headless; these need eyes on a screen (Android first). Commands: `docs/TESTING.md`,
"Developer console".

| What | How to reach it |
|---|---|
| 3D sprites, clan colours, portraits | Start a game; `unit add gu-yue-clan "Rank Four Gu Yue Gu Master"` next to `"Rank Four Bai Gu Master"`, `"Rank Four Xiong Gu Master"` and `"Rank Four Gu Master"` |
| Attack effects per clan chain | Put those units next to a wolf (`unit add Barbarians "Lightning Wolf"`) and attack |
| 47 path lines on the promotion screen (C3) | Select a Gu Master: `unit setxp 200`; every Master shows; a Grandmaster only after its Master, on a rank-three or higher unit |
| Camp change (Collusion Exposed, Blood Lake) | As Gu Yue: `civ addtechnology gu-yue-clan "Inheritance Lore"` fires Blood Lake; choice 3 swaps Righteous for Demonic and marks every military unit with Demonic Infamy |
| Clan voices | Meet a clan (diplomacy screen) and declare war: the canon lines show in EN and ID |
| Path Gu (D2) | Select a rank-three Gu Master: `unit addpromotion "Fire Master"`, end the turn: it holds the Fiery Claw Gu; the Moon Master's Moonlight Gu needs a spare Moon Orchid |
| Path moves (Grandmaster) | With a Grandmaster: the move button costs 15 stones and 1 movement and gives its status for the turn |
| Legacy bridge (old saves) | `unit add gu-yue-clan "Rank Two Moon Gu Master"`, end the turn: it becomes Rank Two Gu Master (Gu Yue: its clan unit) holding Moon Master, promotions kept |
| Primeval-stone icon in the top bar and in texts | Any game; the stone replaces the gold coin in the stats bar, the city screen and notifications |
| Wild Gu popup | Select a Gu Master: `unit activatetrigger "Triggers a [Wild Gu Caught] event"` (have Jade or Wild Boar) |
| Buried inheritance, tile steal | Gu Master on a resource-free land tile beside a rival's border: `unit activatetrigger "Triggers a [Buried Inheritance] event"`; then `civ addtechnology gu-yue-clan "Inheritance Lore"` to build the Inheritance Dig |
| Hunger meter (E7) | Trade or pillage away all Moon Orchid as Gu Yue; Moonlight Gu holders weaken at once and about half lose the Gu two turns later |
| Moon blade before melee | Attack a unit with a Moon Master: two damage numbers (blade, then melee); against a city only one |
| Indonesian text | Options → Language → Bahasa Indonesia; every name, event and Civilopedia page should be translated |
| Ascension (MOD_SPEC_2 C1) | `civ addtechnology gu-yue-clan "Calamity Lore"`; `civ activatetrigger "Instantly provides [60] [Heaven Qi]"`, the same for `[Earth Qi]` and `[Human Qi]`; `unit add gu-yue-clan "Rank Five Gu Master"`, select it, `unit setxp 200`, buy Ascension: the popup offers balanced, hasty and not yet; success turns it into a Rank Six Gu Immortal with a blessed-land promotion, failure removes it |
| Blessed land income | With an immortal: the green grape essence and stones rise each turn by its grade (1/2, 2/4, 3/6, 5/10) |
| Qi income | After Three Qi the three qi appear in the resource overview and grow each turn (land, spring caves and hills, citizens and battle damage) |
| Earthly calamity (C2) | With an immortal: `unit activatetrigger "Triggers a [Earthly Calamity] event"`; build a Formation Ward (`civ addtechnology gu-yue-clan "Calamity Lore"`) to see the ward choice; the immortal's Calamity Countdown status shows when the next one comes |
| Heavenly tribulation | `unit activatetrigger "Triggers a [Heavenly Tribulation] event"`; "Face it bare" may kill the immortal |
| Lifespan Gu debt | `civ activatetrigger "Instantly consumes [20] [Lifespan Gu]"`: the immortal stops healing and loses 7 HP a turn |
| Heaven's Will | `civ activatetrigger "Triggers a [Heaven's Will] event"` |
| Immortal Gu wonders (C3) | `civ addtechnology gu-yue-clan "Immortal Gu Recipes"`; `civ activatetrigger "Instantly provides [60] [Green Grape Immortal Essence]"`; the ten Gu appear in the wonder list; on completion a city may lose 2 population to the birth's calamity; capture the city to seize the Gu |
| Great Grandmaster and immortal move | With a Rank Six Gu Immortal holding a Grandmaster: `unit setxp 300`, buy `<Path> Great Grandmaster`; the move button costs 5 essence |
| Dao marks | A Strength Master's strength rises 5% after Self Strength is built (unit's combat preview) |
| Inheritance trial (C4) | `civ addtechnology gu-yue-clan "Calamity Lore"`; `civ activatetrigger "Triggers a [Inheritance Trial] event"` a few times: a won trial puts a seal in the capital and the inheritance appears in the wonder list |
| Desolate beast | `civ activatetrigger "Triggers a [Desolate Beast Tide] event"`, choose "Hunt it"; kill it for 20 Immortal Materials |
| Treasure Yellow Heaven | `civ activatetrigger "Triggers a [Treasure Yellow Heaven] event"` |
| Rank seven and eight (C5a) | With a Rank Six Gu Immortal: `unit addpromotion "Tribulation Survivor"`, `civ addtechnology gu-yue-clan "Red Date Essence"`, `civ activatetrigger "Instantly provides [60] [Green Grape Immortal Essence]"`, `unit setxp 400`, buy Advance to Rank Seven (at home) |
| Venerable and Eternal Life (C5b, Phase D) | Select a Rank Eight Gu Immortal at home: `unit addpromotion "Fire Supreme Grandmaster"` (any path's), `civ addtechnology gu-yue-clan "Dao Lord"`, `civ activatetrigger "Instantly provides [60] [White Lychee Immortal Essence]"`, `unit setxp 500`, buy Ascend to Venerable: the immortal becomes the Venerable; then `civ activatetrigger "Instantly provides [150] [Yellow Apricot Immortal Essence]"` and buy Seek Eternal Life on the Venerable: you win |
| Gu Houses | `civ addtechnology gu-yue-clan "Gu House Formation"`; build Connect Luck, then the Calamity Luck Altar |
| Arc nations (C5c) | New game: pick the Heavenly Court, Huang Jin Family, Zombie Alliance or Fang Clan; leaders speak their own lines |
| Fate Gu and the Fate War | As the Heavenly Court: `civ addtechnology heavenly-court "Immortal Gu Recipes"`, `civ activatetrigger "Instantly provides [60] [Green Grape Immortal Essence]"`, build Fate Gu; as another clan capture that city: the Fate War popup; shatter it and the Qi Tides follow (`civ activatetrigger "Triggers a [Qi Tides] event"`) |
| Immortal zombie | As the Zombie Alliance with an immortal: `unit remove` on it (or lose it in battle): an Immortal Zombie appears |
| Path branches and halls | Policies screen: 47 path branches by era; adopt one, build its hall, train a Gu Master there: it starts as that path's Master |
| Rank nine dread | With a Venerable alive (see above), the other clans show -10% strength; `civ activatetrigger "Triggers a [Venerable's Shadow] event"` |
| Secret realms | Start a Medium or larger random map and explore; or the map editor: place a realm terrain, move a unit beside it |
| Dream realm, Shadow Sect | `civ activatetrigger "Triggers a [Dream Realm] event"`, `civ activatetrigger "Triggers a [Shadow Sect Envoy] event"` |
| Dao marks | Select a rank-three or higher Gu Master holding a path Master: its promotions show Dao Comprehension (a countdown) and later Dao Marks I with a star; `unit addpromotion "Dao Marks IV"` on an immortal shows tier IV and removes nothing below it unless gained by a step |
| 100 turns without a crash, AI solvent | The Definition of Done's last item: the user's own game (Debug tab → "Simulate until turn" also works) |
