# Audit against the user's lore reference (2026-11-08)

The user gave a lore reference for the mod (`reverend-insanity-lore-unciv.md`, Indonesian, summarised from an English
translation, chapters cited as `[chN]`). The request: "rombak dan sempurnakanlah apa yang kurang dari mod kita ini
menggunakan referensi file markdown ini kecuali bagian 10 nomor 1, buat sesuai dengan kanon seimbangkan sesuai
parameter game nya". In English: fill every gap the reference shows, canon-faithful and balanced to the game's numbers.
Section 10.1 ("start small") is excluded by the user.

Rules applied:

* The reference marks its "Saran Unciv" blocks as design proposals, not lore. Proposals that contradict a design the
  user already approved are listed under "Design proposals not adopted"; they stay the user's choice.
* Every lore claim was checked in the raw Chinese text (R) before it entered the plan (CLAUDE.md). Citations use
  `R V#c#` (volume and chapter of the raw text, `docs/CANON_REFERENCE.md`). The verdicts are in our own words; no
  text of the novel is kept anywhere.
* Balance: every layer is measured by autoplay against the previous build (`docs/AUTOPLAY.md`).

## Section by section

Status: **have** = already in the mod; **gap** = missing, built in the layer named; **kept** = a deliberate
simplification already documented; **not found** = the claim could not be confirmed in the raw text.

### 1. Cultivation

| Reference item | Raw-text verdict | Mod before | Action |
|---|---|---|---|
| Nine ranks; Gu Master 1-5, Gu Immortal 6-8, Venerable 9 | CANON | have (rank chain, eras) | - |
| Four small stages per rank: initial, middle, upper, peak | CANON: initial → middle → upper → peak are small steps; peak to the next rank's initial is a big breakthrough, much harder, and burns many primeval stones (R V1c63, V1c81, V1c90) | **gap** | Layer 1 |
| Essence colour per rank | CANON | have (era and unit texts) | - |
| Relic Gu: one small stage at once, one colour per rank | CANON: single use, raises one small stage instantly; green copper, red iron, white silver, yellow gold, purple crystal; a rank-two relic sells for thousands of stones (R V1c53, V1c111, V1c112) | partial: "Relic Gu" is the human path's Gu (+25% XP, D2) | Layer 1: five consumable relic Gu, one per rank |
| Aptitude A-D | CANON | have | - |
| Ten extreme physiques | CANON: the essence fills the whole aperture; cultivation speeds up as the rank rises; heaven does not tolerate them, the aperture finally bursts with a violent blast; only becoming an immortal saves them (R V1c135, V1c140, V1c144, V3c159, V3c181). Named: Northern Dark Ice Soul, Great Strength True Martial, Pure Dream Reality Seeker, Myriad Gold Wondrous Essence, Flame Brilliance Lightning Marsh, Carefree Wisdom Heart | **gap** | Layer 1 |
| Blessed land (3 grades), grotto-heaven, land spirit | CANON (the mod uses four grades, the user's correction of 2026-10-18) | have (blessed lands, grotto-heaven; the land spirit only in Lang Ya's text) | - |
| Calamities and tribulations by rank | CANON | have (countdowns; the first tribulation 10-15 turns after ascension is MOD_SPEC_2's target; aperture time runs faster than the world's) | kept |
| Primeval stones = Gold; Gu must be fed | CANON | have (Batu Primordial; hunger meter) | - |
| Immortal essence stones as the immortals' currency | CANON | kept: one stockpile per essence tier, bought at Treasure Yellow Heaven | - |
| Immortal materials per path | CANON | kept: one Immortal Materials stockpile (audit P5); 47 stockpiles would flood the resource bar | - |
| Dao marks clash between paths; killer moves; one immortal Gu of a kind; Gu Houses | CANON | have | - |

### 2. Paths and eras

| Reference item | Raw-text verdict | Mod before | Action |
|---|---|---|---|
| ~35 paths and when each was founded (R V5c302) | CANON | 47 path lines, policy branches and halls; origins not in the texts | Layer 5: each path's founding age and founder in its civilopedia |
| Venerables (Primordial Origin, Star Constellation, Limitless, Reckless Savage, Genesis Lotus, Thieving Heaven, Giant Sun, Spectral Soul, Red Lotus, Paradise Earth, Great Dream) | CANON | ten inheritances; Great Dream only through the dream realms | kept |

### 3-4. Geography and factions

| Reference item | Raw-text verdict | Mod before | Action |
|---|---|---|---|
| Five regions and walls that hinder the strong | CANON | have (Regions, 2026-11-08) | - |
| Southern Border super clans Wu, Shang, Tie; Gu Yue, Bai, Xiong | CANON (Tie R V1c171; Shang R V1c43) | Wu and the Gu Yue, Bai and Xiong majors; Shang Clan City as a wonder | Tie: see "Not built" |
| A Southern Border "Yi" clan | **not found** (no such clan name in the raw text) | - | not built |
| Northern Plains tribes Hei, Ma, Liu, Dong Fang, Ge | CANON (R V3c22, V3c36, V3c65, V3c96) | Huang Jin major stands for every Giant Sun line; Ge Tribe city-state | kept |
| Western Desert Tang clan, Dou Shen (Divine Bean) Palace | CANON (R V3c104, V5c486) | Fang clan, Lan, Xiao, Mo, Wan | see "Not built" |
| Eastern Sea Shen and Song clans, Dragon Palace | CANON (R V4c243, V5c215) | Song Clan, Xia Clan, Merman Court; Dragon Palace as a Gu House | - |
| Central Continent: ten great sects, Heavenly Court | CANON | have (Regions II) | - |
| Natural wonders: Dang Hun Mountain, Lang Ya | CANON | have | - |
| "Miniscule Mountain", "anti-sound desert" | not found under a name we could match | - | not built |

### 5-6. Figures and variant humans

| Reference item | Raw-text verdict | Mod before | Action |
|---|---|---|---|
| Leaders: Gu Yue Bo, Duke Long, Feng Jiu Ge, Fairy Zi Wei ... | CANON | leaders and civilopedia | - |
| Hairy men refine Gu | CANON | Hairy Man Tribe, Lang Ya Sect | - |
| Mermen | CANON | Merman Imperial Court | - |
| Feathermen fly; Yu Sheng City | CANON: Western Desert (R V4c215, V4c217) | **gap** | Layer 4 |
| Snowmen | CANON: Northern Plains, they hardly laugh or cry (R V3c132) | **gap** | Layer 4 |
| Inkmen of Ink Man City, held down by the golden tribes | CANON: Northern Plains (R V4c13, V4c230) | **gap** | Layer 4 |
| Rockmen dig deep, live underground and eat earth | CANON (R V3c7) | **gap** | Layer 4 |
| Mushroommen: a mushroom cap for a head | CANON: Southern Border (R V5c316) | **gap** | Layer 4 |
| Dragonmen, minimen, eggmen, mudmen, treemen, beastmen | CANON but thin or scattered | - | not built |

### 7. Creatures

| Reference item | Raw-text verdict | Mod before | Action |
|---|---|---|---|
| Beast groups: hundred, thousand, myriad beast king, beast emperor | CANON (R V3c4) | Lightning Wolf, Bold Lightning Wolf, Thunder Crown Wolf | Layer 3 |
| Bold lightning wolf = hundred-beast king; frenzy lightning wolf = thousand-beast king; thunder crown wolf = myriad-beast king, each leading ten thousand wolves | CANON (R V1c114, V1c130, V1c131) | Frenzy Lightning Wolf missing | Layer 3 |
| Desolate, ancient desolate, immemorial desolate beasts; immortal zombies; wild Gu | CANON | have | - |
| Enslavement path tames beasts | CANON | have (Enslavement Master captures barbarians) | - |

### 8. Gu

| Reference item | Raw-text verdict | Mod before | Action |
|---|---|---|---|
| Hope, Moonlight, Little Light, Liquor Worm, Four Flavours, Jade Skin, White and Black Boar, Moonglow, White Jade, Stealth Scales, Chainsaw Golden Centipede, Heavenly Essence Treasure Lotus, Blood Skull | CANON | have (Hope as the awakening) | - |
| Thunderwings, Sky Canopy, Charred Thunder Potato, Bear Enslavement, Black Mane, Green Silk, Stealth Rock, Rock Skin | to verify one by one | **gap** | Layer 2 |
| Fusion recipes: Moonlight + Little Light → Moonglow; White Boar + Jade Skin → White Jade; Black Boar + Green Silk → Black Mane; Stealth Rock → Stealth Scales; White Jade → Sky Canopy | to verify | Moonglow and White Jade bought without their ingredients | Layer 2 |
| Immortal Gu: Spring Autumn Cicada, Fixed Immortal Travel, Perseverance, Regret, Wisdom, Fate, Love | CANON | have | - |

### 10. Design warnings

* 10.1 excluded by the user.
* 10.2 "a civ game, not a cultivation RPG: clan = civilisation, Gu Master = unit": the mod's architecture.
* 10.3 "limit immortals through essence and caps, not by nerfing them": the mod's essence, lifespan and immortal chasm.

## Built (2026-11-08)

| Layer | What | Commit |
|---|---|---|
| 1 | Small stages (middle, upper, peak; reset on a new rank; breakthrough price), five rank relic Gu, the ten extreme physiques; Tutorial "Gu World: Small Stages" | 98af8c4, fixed in 4cbadd2 |
| 2 | Ten canon Gu (Green Silk, Black Mane, Steel Mane, Stealth Rock, Rock Skin, Beast Skin, Bear Enslavement, Charred Thunder Potato, Thunder Wings, Sky Canopy) and the fusion recipes (`data/gu_fusions.csv`) | 4cbadd2 |
| 3 | Frenzy Lightning Wolf, the thousand-beast king; the wolf tide follows the beast-king ranks | 24b88ef |
| 4 | Feathermen, Snowmen, Inkmen, Rockmen as city-states with four new city-state types; the Court cannot ascend to Venerable | 6edf4a8 |
| 5 | Every path branch names its founding age and Venerable | 7b40304 |

Balance is measured per layer in `docs/AUTOPLAY.md` ("Reference audit layers").

## Design proposals not adopted (the user's choice)

| Proposal | Conflict | Option |
|---|---|---|
| Eras = the five antiquities | the rank eras were approved (MOD_SPEC_2, rank nine an era 2026-11-01) | the antiquities stay lore (Layer 5) |
| One tech per path | the paths are promotion lines and policy branches (MOD_SPEC_3, 2026-11-01) | - |
| No Venerable unit | MOD_SPEC_3 makes rank nine one playable unit | - |
| The Heavenly Court as a boss, not a nation | the Court is a playable major (C5c) | the open question on the Court's Venerable |
| Fang Yuan as a hero unit; figures as Great People | no Great Person system in the mod | a later layer if the user wants it |

## Not built (scale and map space)

The Five Regions map already holds 31 civs. Each further super force (Tie, Tang, Dou Shen Palace, Shen, the Huang Jin
lines as separate tribes) needs a city on the map, an icon and text, and every civ slows each turn on a phone. They
wait for the user's call, like the dragonmen and the minor variant races.
