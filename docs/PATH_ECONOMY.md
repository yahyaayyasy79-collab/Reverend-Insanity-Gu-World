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

**Where it comes from.** Five sources, so a clan that commits to a path can feed it (Layer 9b values):

| Source | Food |
|---|---|
| A worked tile of the food (each major starts beside two copies of its first food and one of its second) | 1 |
| The path's branch (opener) | 2 |
| The branch's Insight policy (the moon's Orchid Beds and the strength's Beast Hunters already gave 2) | 2 |
| Each of the path's halls (one per city) | 1 |
| The path's lore (tech) | 2 |

A grant needs 2 spare (the stock only refreshes at turn start, so two grants in one turn must not starve a third Gu), so
a supply of S feeds S - 1 Gu. A signature clan at T300 holds about 7-12 Masters of its path: branch 4 + lore 2 + four
halls 4 + the start tile 1 + a tile or two = 12-13, enough for 11-12 Gu. A path with 1-3 Masters in a clan is fed by its
lore (2: one Gu) and the tiles in reach.

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

| Riches on the Five Regions map (resources and sites) | South | North | Central | West | East |
|---|---|---|---|---|---|
| Before Layer 9 (start rings included) | 33 | 19 | 13 | 11 | 7 |
| Layer 9b, without the majors' start kits | 43 | 46 | 43 | 40 | 18 |
| Layer 9b, per 100 land tiles (kits included) | 13.0 | 10.0 | 14.5 | 13.6 | 23.0 (the canon sea, richest per tile) |

Spirit springs (4 a region, 2 in the sea) and jade (2 a region, 1 in the sea) are spread the same way. Each major's
start kit holds two copies of its first food and one of its second: the four Southern Border clans their signature paths' (Gu Yue moon
and strength, Bai water and wood, Xiong strength and blood, Wu wind and star), each arc major two of its region's (the
Court heaven and emotion, the Huang Jin qi and enslavement, the Fang wisdom and blade, the Zombie Alliance water and
lightning; docs/REGIONS.md).

## Layer 9b: what the first measurement showed (autoplay, 2026-11-09)

The first build (8 x 450 against Layer 8, then 4 x 300 with the foods' stock recorded) made the moon and strength paths
heavier, not lighter:

| Measure (T300) | Layer 8 (stones) | Layer 9 |
|---|---|---|
| Path Gu holders per Master | 0.89 | 0.53 |
| Moon + strength share of the holders | 15% | 35% |
| Bai's water / Wu's wind Masters holding their Gu | most | 1 in 6, on a stock of about 3 |
| Wu clan fell (of 8 games) | 2 | 6 (to the Bai) |

Four causes, each fixed:

1. **Uneven starts.** The scatter put 10-11 riches within 3.5 tiles of the Court, the Fang and the Zombie Alliance, 5
   and a beast lair beside the Wu, which also lost its inheritance site (Wu at T100: 3.4 cities, 11 pop; it had 5.2 and
   17). Now every major gets the same kit (a spirit spring, jade, two copies of its first food and one of its second, an
   inheritance site three tiles out; the Gu Yue's emblem Gu eats Moon Orchid, so one copy starved it), nothing else within 3.5 tiles of a capital, at most 4 scattered riches within 6 (8 for the sea's
   islands), no beast lair or demonic den within 6; a food without room in one of its regions spills into the other,
   and each region places its own foods before the ones it holds as a second region.
2. **The Slice 1 branches outranked the rest.** The AI ranks branches by priority; the Moon and Strength branches had
   5/5, every other path 3/3. Now all 3/3.
3. **Only two branches fed their Gu twice.** Orchid Beds and Beast Hunters gave 2 more Moon Orchid and Wild Boar; now
   every branch's Insight policy gives 2 of its food.
4. **Bai and Wu never chose their own branch.** Their AI personalities still leaned Righteous and Strength (from before
   the Water and Wind signatures); they now weigh Water and Wind like the Gu Yue weigh Moon and the Xiong Strength.

The lore now gives 2 (1 fed no Gu by itself).

## The path lores, redesigned

| | Before (Layer 8) | Now |
|---|---|---|
| Cost | 40 for every lore | by family: body, edge and five phases 40; sky and mind 60; law and craft 80; a sub-path 20 more |
| Gives | +15% XP for the path's Masters; Grandmaster needs it | the same, and 2 of the path's food |
| Opens | with a Master of rank three or higher | the same |

## Measured

docs/AUTOPLAY.md "Layers 9-11": with the fixes, 79-85% of Masters hold their path Gu (89% when stones fed them, 53% in
the first build); the moon and strength hold 22% of the Masters and 16% of the Gu (23% and 15% before Layer 9); the
supply per major at T300 is about 13 from lores, 7 from tiles, 7 from halls and 5-6 from branches; 2 majors fell in 8
games in the final build (14 before Layer 9), the Wu once (6 in the first build).
