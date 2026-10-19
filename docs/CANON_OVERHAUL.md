# Canon overhaul plan (2026-10-19) — waiting at a checkpoint

The user's request (2026-10-18): rework all lore, the world's conflicts (between clans, and between righteous, demonic
and lone cultivators), the texts and the tile regions to follow *Reverend Insanity*. Nothing below is implemented
yet. Four research passes back it (raw Chinese text from the hetushu mirror = **R**, volume/chapter like V2c81; the
fan wiki through its API = **W**); their verdicts are summarised here because research notes do not survive the
container. Every proposed unique was matched against the 4.22.8 `uniques.md` with `tools/unique_check.py`.

Decision ids (D1…) are what the user answers; items marked **default** are technical or text fixes with clear canon,
done unless the user objects.

## A. Texts that state something false or invented as canon (default)

| # | Object | Fix | Canon |
|---|---|---|---|
| A1 | Liquor Worm (pedia, HIGH) | Not "let go above rank one": it is useless above rank one unless refined into the Four Flavours Liquor Worm (四味酒虫) | R V1c121 |
| A2 | Refinement Attempt text and choice 4; Refinement Chamber; Gu Refinement tech | No furnace: refining pours the Gu Master's essence into the Gu and its materials; a failed combined refinement wastes materials and stones ("Stop and recover your essence") | R V1c10, V1c17, V1c121; 炉 never refines Gu in volumes 1–2 |
| A3 | Gu Formations tech; LORE_MAPPING verdicts | Formations (蛊阵) appear first in volume 4; Qing Mao villages are stockades. Tech text says so; verdict INVENTED for the Qing Mao arc | 蛊阵/阵法 in 0 chapters of V1–V2 |
| A4 | Lone Cultivators (pedia EN+ID) | 散修 means a lone, clanless cultivator; on the Southern Border every demonic Gu Master is one | R V2c81 |
| A5 | Wu Clan (pedia) | First righteous super clan; head Wu Ji walks strength, the clan's strongest tradition is wind; largest battle stage | R V2, V6c130 |
| A6 | Xiong, Gu Yue, Bai (pedia) | Xiong: weakest on paper, most numerous, lets others bleed first, once hired demonic Gu Masters. Gu Yue: the old overlord slipping behind Bai. Bai: the waterfall village, rising aggressor, water and ice Gu | R V1c125, V1c165, V1c173, V1c175, V1c179; W |
| A7 | Thunder Crown Wolf, Rank Four era, Super Clan Commerce, Killer Move, Stream Gu, Moon Path, Moon units | Canon look (hill-sized, crowned fur); rank four leads a mountain clan, not the Southern Border; only Shang runs a market city; a killer move rests on a core Gu (核心蛊); Stream Gu effect is the mod's, not canon; the moon path is the user's adaptation | audit rows 8–14 |
| A8 | Primeval-stone overrides of base-game strings | Drop the anachronisms (submarines, railroads, tourism); fix the garbled Indonesian line | — |
| A9 | Indonesian "menyuling" (distil) | 酿酒 is brewing: "Pembuatan Arak", "membuat arak" | — |
| A10 | Arc texts (LORE_MAPPING "Immortal arc") | Fang clan: a righteous super force, the world's best at Gu Houses, **not** the desert's first (R V5c499, V6c252); Zombie Alliance: only its Eastern Sea HQ outranks local powers, it shows a righteous face, is secretly a lower sect of the Shadow Sect, and is wiped out at Yi Tian in this timeline (R V4c242, V4c359, V5c143) | conflicts X1, X2 |
| A11 | LORE_MAPPING verdicts | Beast Tide 兽潮 is canon (15 chapters of V1); demonic inheritances test with lethal trials (R V1c47, V1c60); Righteous Path lore line CANON (R V5c361); Jia village ADAPTED (a large clan shrunk to a city-state); Xiong's demonic lean ADAPTED; Demonic Path members list (Lone Cultivators, not Blood Harvest) | conflicts X7, X11–X14 |

## B. Renames of Slice 1 objects (the user decides: CLAUDE.md asks before renaming)

| # | Now | Proposed | Canon |
|---|---|---|---|
| D1a | Formation Platform | Stockade Wall (寨墙) | 寨墙 in 6 chapters of V1 |
| D1b | Beast Tide "Raise the formation" | "Man the stockade walls" | as above |
| D1c | Orchid Terraces | Orchid Beds (orchids grow in the spring cave) | R V1 |
| D1d | Capital "Wu Clan City" | Wu Yi Mountain (武仪山) | R V5c300, V5c321 |
| D1e | Extra city names | Gu Yue: Alliance Slope, Spear Bamboo Grove, Stone Forest; Bai: Back-Slope Waterfall, Deep Pool; Xiong: Front Slope | geography research |
| D1f | Terrain display names (only the shown text, via translations; engine names stay) | Hill → Mountain Slope, Mountain → Ten-Thousand-Foot Peak, Forest → Spear Bamboo Forest, Jungle → Rainforest, Marsh → Rotting Swamp | R V1, V2c8–9 |

Saves keep working: buildings, policies and cities are matched by name, so a rename needs the same kind of bridge the
units got, or the user's word that no running game matters.

## C. World conflicts (mechanics)

What the engine allows (checked in the 4.22.8 docs and source): no unique declares war or peace or changes another
civ's opinion, and a civ's policies are not a civ filter. What it allows: defensive pacts gated by a unique, diplomacy
triggers, Personality fields (`declareWar`, `diplomacy`, `commerce`, `loyal`), marker promotions on units, and
counting adopted policies by other civs.

| # | Proposal | Canon | Slice |
|---|---|---|---|
| C1 | **Demonic Infamy**: units of a Demonic Path civ carry a marker promotion; righteous civs get bounties on them (`Earn [100]% of killed [Demonic Infamy] unit's [Cost] as [Gold]`) and a strength bonus against them | righteous clans hunt demonic cultivators, bounties and wanted lists (R V2c29, V2c35) | 1 |
| C2 | **Righteous pacts**: Righteous Alliance gains `Enables Defensive Pacts`; demonic civs can never pact | the written three-village alliance (R V1c127), the righteous army against Yi Tian | 1 |
| C3 | **Beast Tide choice 5 "Call the clans' alliance"**: wolves come, the clans fight together (+30% vs beasts for 10 turns) and split the spoils (−10% stones for 10 turns) | R V1c124, V1c127, V1c179 | 1 |
| C4 | **Canon temperaments** (Personalities): Bai `declareWar 7`, expansion 7 (wants all three springs); Gu Yue `declareWar 3`, diplomacy 7, commerce 7; Xiong `loyal 2` (free-rider); Wu diplomacy 7 (coalition leader) | R V1c173, V1c179; V2 | 1 |
| C5 | **Canon voices**: own-words leader lines (introduction, war, defeat) in EN and ID | — | 1 |
| C6 | Flower Wine Monk Inheritance: `[+15]% Strength <vs [Gu Yue Clan] units>` (his legacy's one condition is Gu Yue's end) | R V1c46 | 1 |
| C7 | Stone Shortage "Rob a passing caravan": merchants shun the clan (`[+100]% City-State Influence degradation <for [10] turns>`) | R V1c55–57 | 1 |
| C8 | **Collusion Exposed** / **Whitewashed Name** events: a camp can flip (righteous caught dealing with demons; a demonic clan buys a righteous name at the Shang battle stage) | Fang clan branded demonic; Wei Yang; whitening at Shang Clan City (R V2c66) | 1 (needs an in-game test of policy removal) |
| C9 | **Clan Contest**: a peacetime tournament splits the mountain's gains | R V1c179 | 1 |
| C10 | Righteous Coalition, Demon Extermination List, Zombie Alliance vs Heavenly Court, a third (lone) camp for ranks 6+ | R V4c51, V5c83, V5c864 | arc |

## D. Tile regions

| # | Proposal | Slice |
|---|---|---|
| T1 | Canon start biases now: Xiong `[Hill]`, Wu `[River]`; arc majors Huang Jin `[Grassland]`, Fang `[Desert]`, Zombie Alliance `[Coast]`, Heavenly Court `[Hill]` | 1 / arc |
| T2 | A hand-made Qing Mao map in `maps/` (three villages on the front slope, mountainside and back-slope waterfall; springs as the prize). The random generator is latitude-based and cannot place canon regions [src] | 1 |
| T3 | The five-region map for the arc, with the region walls as impassable terrains crossed only by immortals; miasma (瘴气) only on the Southern Border's wall, poison fog in the Northern Plains | arc |
| T4 | Landmarks as natural wonders (Spring Whirlpool, Howling Moon Mountain, Moon Bowl …), regional events (decade blizzard, earth tide) | arc, over the 12-realm cap |

## E. One Gu per path (decision B.b)

Research found a canon mortal Gu for 35 paths, ADAPTED for 4 (Moon: Moonlight Gu, Illusion: Illusory Moon Gu, Food:
Liquor Worm, Pill: Pill Refiner Gu), [VERIFY] for 6 (Shadow: Overlapping Shadow Gu, filed under dark; Enchantment:
Estrus Gu, filed under emotion; Phantom: Turn Phantom Gu, Restriction: Primeval Break Gu, Refinement: Revert Gu, rank
unknown; Painting: Painting Idea Gu, filed under wisdom) and none for 2 (Weapon, Killing). Strength keeps its boar Gu,
Food its Liquor Worm. Most canon foods are not stated, so most path Gu would cost stones (upkeep); the ones whose food
is known eat a Gu food and starve like the Slice 1 Gu.

| # | How a cultivator gets its path Gu | For | Against |
|---|---|---|---|
| E-a | **Refined**: the path's first rung of the Refinement Attempt, gated by the Gu's canon rank (rank-5 Gu at rank four until the arc) | canon (Gu are refined, attempts cost stones); the AI already buys Refine Gu; gives every path a ladder rung | the ladder check must model 47 paths; a low-rank cultivator of a path whose Gu is rank 3+ waits |
| E-b | **Granted with the Master** | simple, certain | no gamble, no stones: weaker tension |
| E-c | Granted with the Grandmaster tier | ties the Gu to mastery | Rank One–Two cultivators have none |

## F. Wu's signature path

Canon gives two answers: Wu Ji, the clan head in volume 2, walks strength; the clan's own strongest tradition is wind
(R V6c130). The clan chain's art shows strength.

## Order of work after the answers

1. Part A texts and verdicts (EN + ID), LORE_MAPPING rows; check_all; commit.
2. Path Gu (E): data table, generator, icons, ladder check; autoplay.
3. Slice 1 conflicts (C1–C9 as approved), temperaments, voices; autoplay A/B on war and solvency.
4. Tile regions: start biases, terrain display names, the Qing Mao map.
5. Renames (B) with a save bridge if needed.
6. Arc items go into LORE_MAPPING "Immortal arc" for MOD_SPEC_2 Phase C.
