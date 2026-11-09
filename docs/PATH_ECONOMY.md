# Path economy: one basic food per path, spread over the five regions (2026-11-09)

The user: every path should have its basic food, not only the moon path (Moon Orchid) and the strength path (Wild
Boar); spread the resources over all five regions, because the mod weighed heavily on the Southern Border and on the
moon and strength paths; make it even and balanced, with a systematic design and calculation. And: perfect the path
lore techs, fun but balanced.

## What was uneven (audit, 2026-11-09)

| Measure | Before |
|---|---|
| Resources on the Five Regions map | Southern Border 33, Northern Plains 19, Central Continent 13, Western Desert 11, Eastern Sea 7 |
| Per 100 land tiles | south 5.7, east 4.3, north 3.3, central 3.1, west 2.7 |
| Gu foods | Moon Orchid, Wild Boar, Jade, Wine: 40 of the 48 path Gu ate primeval stones; bone, blood and blade Gu borrowed Wild Boar and Jade |
| Every major's start | Moon Orchid and Wild Boar beside every capital, whatever its paths |
| Catalog Gu per path | strength 12; 16 paths had 1 |

## The design

**One food per path** (data/path_foods.csv): 47 foods, each the canon food of a Gu of that path where the novel names
one (23, CANON), or a canon plant, creature or material of the path's nature (24, ADAPTED); verdicts in
docs/LORE_MAPPING.md "Path foods". Moon Orchid, Wild Boar and Wine keep their Slice 1 roles.

**What eats it.** Each path's Gu (data/path_gu.csv) eats 1 of its path's food a turn, with the Slice 1 hunger meter
(weakened at once, then the meter and its death roll). A Master receives its path Gu only while the clan has more than
1 of the food spare, so a clan without the food never starves: its Masters simply go without that Gu. The stone upkeep
those Gu cost before (+10% each) is gone.

**Where it comes from.** Four sources, so a clan that commits to a path can feed it:

| Source | Food |
|---|---|
| A worked tile of the food | 1 |
| The path's branch (opener) | 2 |
| Each of the path's halls | 1 |
| The path's lore (tech) | 1 |

A signature clan at T300 holds about 10-13 Masters of one path; branch 2 + four halls 4 + lore 1 + two or three tiles
feed 9-10 of them. A clan of many paths (the arc majors) feeds its paths from their lores, the tiles of its region and
trade.

**What kind of resource.** A luxury whose happiness is switched off (every luxury gives 0; Furs, the one real luxury,
keeps its +4 through its own line). Not strategic: Unciv's random maps split one strategic budget evenly over every
strategic type and round down [src MapGenerator.spreadStrategicResources], so 46 more strategic types would leave a
Small map without spirit springs, jade or moon orchids. Luxuries share their budget by count [src
MapGenerator.spreadResources] and give one copy per worked tile [src CityResources], and the top bar shows only
strategic resources, so the phone's bar stays as it was.

**How it is worked.** Plants by a Plantation, beasts and sea creatures by a Camp, minerals by a Mine, waters by a
Spring Cave, old scrolls by an Inheritance Dig; plants and beasts give food, minerals production, waters and sea
creatures gold, scrolls science.

## Spread over the five regions

Each food has a home region (2 tiles) and a second region (1 tile), set from the canon and the region's nature: the
Southern Border's jungles and clans (moon, strength, blood, wood, wind, star, dark, shadow, enchantment, human), the
Northern Plains' herds, snows and golden tribes (bone, transformation, enslavement, ice, poison, luck, phantom,
restriction, qi, painting, weapon), the Western Desert (metal, blade, killing, fire, earth, cloud, light, wisdom,
theft), the Eastern Sea (water, lightning, space, sound, rule) and the Central Continent's sects (sword, illusion,
emotion, soul, dream, time, heaven, refinement, formation, pill, information).

| Resources on the Five Regions map (excluding the majors' start rings) | South | North | Central | West | East |
|---|---|---|---|---|---|
| Before (rings included) | 33 | 19 | 13 | 11 | 7 |
| After | 35 | 37 | 33 | 33 | 17 (on 164 land tiles: the richest per tile, the canon sea) |

Spirit springs (4 a region, 2 in the sea) and jade (2 a region, 1 in the sea) are spread the same way. Each major's
start ring now holds its own foods: the four Southern Border clans their signature paths', each arc major two of its
region's (docs/REGIONS.md).

## The path lores, redesigned

| | Before (Layer 8) | Now |
|---|---|---|
| Cost | 40 for every lore | by family: body, edge and five phases 40; sky and mind 60; law and craft 80; a sub-path 20 more |
| Gives | +15% XP for the path's Masters; Grandmaster needs it | the same, and 1 of the path's food |
| Opens | with a Master of rank three or higher | the same |

## Measured

See docs/AUTOPLAY.md "Path foods" for the autoplay A/B.
