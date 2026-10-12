# LORE_MAPPING — Slice 1: Qing Mao Mountain and the Southern Border

**Status: Phase 1 draft, waiting for the user's lore corrections (⛔ MOD_SPEC §4). No ruleset JSON exists yet.**

One row per planned object (116 rows): English name (common fan-translation term), Chinese original, one-line
lore basis, mechanical role, the exact uniques, and canon status.

* **CANON**: taken directly from the novel. **ADAPTED**: a novel element bent to fit a 4X game. **INVENTED**:
  mechanical glue with no novel source.
* **[VERIFY]**: canon is uncertain; the note says what. Anything beyond the MOD_SPEC §5 anchors carries it.
* The Chinese column appears once per term, on its primary object. It is left empty for invented objects so that
  civilopedia never presents a made-up term as canon. Chinese goes into civilopedia text only; object names are ASCII.
* Lore bases are my own one-line paraphrases. Mechanical effects are 4X mappings, never canon claims.
* "Stones" means the Gold stat (primeval stones, S1). "Upkeep" means unit maintenance. P1–P5 are the five pillars
  of MOD_SPEC §0.

**How the uniques were checked.** Every unique in this document is generated into a throwaway ruleset by
`tools/slice1_prototype.py`, together with every object, field and cross-reference the plan names. That ruleset
passes `tools/check_all`: schema 0/0, uniques 0/0, references 0 errors (only missing-icon warnings), packaging OK,
and **Unciv 4.22.8's own validator (`mod-ci`) with 0 errors and 0 warnings**. A self-test fails if this document
quotes a unique the prototype does not generate. To re-run:

```
tools/slice1_prototype.py /tmp/slice1 && tools/check_all --mod /tmp/slice1 --no-self-test
```

Engine behaviour the docs do not state is marked **[src]** (read from the 4.22.8 source). It must be confirmed in
game before content depends on it (see [Engine facts this plan relies on](#engine-facts-this-plan-relies-on)).

---

## Budget (MOD_SPEC §8)

| Budget line | Slice 1 limit | Plan |
|---|---|---|
| Eras | ranks 1–4 as 3 eras | 3: Rank One-Two, Rank Three, Rank Four |
| Techs | ~15 | 15 (about 2,100 science in total); the last one, Dao Comprehension, is repeatable |
| Units | ~12 | 12: 2 civilians, 7 Gu Masters (unpathed Rank One, Moon ranks 2–4, Strength ranks 2–4), 3 beasts |
| Buildings (wonders count) | ~12 | 12: 9 buildings (Clan Hall counted) + 1 national wonder + 2 world wonders |
| Policy branches | Righteous, Demonic + 2 paths | 4: Righteous, Demonic, Moon Path, Strength Path (16 policies with finishers) |
| Resources | ~6 | 6: 1 bonus (Primeval Stone Vein), 3 strategic Gu foods (Moon Orchid, Wild Boar, Wine), 2 luxuries |
| Events | exactly 5 | 5: Aptitude Awakening, Refinement Attempt, Beast Tide, Betrayal, Stone Shortage |
| Nations | 4 majors + 3 city-states | Gu Yue, Bai, Xiong, Rogue Cultivators + Hairy Man Tribe, Stone Man Tribe, Jia Clan (plus the engine-required Barbarians and Spectator) |
| Victory | domination | Southern Border Supremacy (domination) + Endurance (score at max turns) |
| Not budgeted, kept minimal | — | 10 promotions, 8 improvements + 8 engine-coupled Vanilla copies, 18 Vanilla terrains, 6 ruin rewards, 3 city-state types, 4 personalities |

No helper events and no extra units were needed: traitors reuse path units and there is no scout.

## Path choice: why two paths, and which

**Spec tension.** §6 S5 suggests about six paths for Slice 1; §8 allows two path branches. §8 is the hard budget, so
Slice 1 ships two and the rest become the roadmap.

**Chosen: Moon Path (月道 [VERIFY]) and Strength Path (力道 [VERIFY]), mutually exclusive.**

1. They have the strongest Slice-1 anchors. Moonlight Gu fed on moon orchid petals is a §5 anchor and the Gu Yue
   signature. Boar-strength Gu feature in Fang Yuan's early Qing Mao cultivation [VERIFY]; the Xiong clan's strength
   tradition is inferred from its name (熊, bear) [VERIFY].
2. They cover Unciv's two combat roles: Moon is ranged, Strength is melee, so the choice changes tactics, not just
   numbers. Only melee kills recruit beasts (Beast Enslavement), which is a real Strength advantage.
3. They pull the stone loop in opposite directions (P1 + P4). Moon is cheaper in stones (+75/150/225% upkeep) and
   its Gu eat Moon Orchid; Strength costs more (+100/175/275%) and its Gu eat Wild Boar. Each opener and one member
   policy add +2 of the path's food.
4. Dao marks: +5% strength per adopted own-branch policy; a cross-path Gu on a unit gives −10%; only path units reach
   ranks 2–4, so an unpathed clan stalls at Rank One with a single refinement rung. Specialists beat dabblers.

**Rejected for Slice 1.** Soft cross-branch interference (Righteous and Demonic are exclusive too, so a culture-rich
AI would adopt the second path and penalise itself). Blood (overlaps the Demonic strategy; Blood Sea material may be
a spoiler). Enslavement as a branch (kept as the Beast Enslavement tech teaser).

**Later candidates**, one or two per slice as the budget allows: Enslavement (beast armies), Blood, Water/Ice
(Bai Ning Bing), Earth/Stone (stone men), Lightning (electric wolves), Wind, Wood, Light (if Moonlight Gu turns out to
be light path), Wisdom, Time (Spring Autumn Cicada, Fang Yuan, Slice 2 / S8), Theft, Poison, Fire.

## Pillar coverage (human and AI)

**P1 Power is expensive to keep.** Every unit of a major civ pays upkeep: `[-3] units cost no maintenance <for [Major] Civilizations>` cancels
the engine's three free units, which would otherwise be the three most expensive ones and erase the rank
multipliers. Rank multipliers: Rank One +25%; Moon +75/+150/+225%; Strength +100/+175/+275%. Every Gu eats its food
through `Consumes` on the promotion; a shortage gives every holder the engine's −25% "missing resource" malus [src].
White Jade Gu (+20%) and Killer Move (+25%) raise upkeep; Aptitude A lowers it (−20%), D raises it (+20%). Stone
sinks: upgrades, roads (1 per tile), buildings (1 each), careful refinement (40/70/100). Starvation has three tiers:
a missing Gu food (−25%), stones below 0 (−20% strength and a Stone Shortage at 25% per turn), and the engine's
disband at −200. *AI:* the same formula times `aiUnitMaintenanceModifier`; the refinement ladder and Gu Yue's free
Moonlight Gu hand out a Gu only while its food is in surplus; Ration (weight 2) is its way out of a shortage and
Borrow (weight 0.2) is closed below −100.

**P2 Every breakthrough is a gamble.** Aptitude Awakening rolls a None die on every new Gu Master (A/B/C/D
5/20/35/40%). Refine Gu is the only promotion bought with XP, so all XP becomes gambles: a careful, a reckless, a
Liquor Worm or a cooling choice, climbing the ladder path Gu → White Jade Gu → Killer Move. Inheritance Sites can
hold a refinement, a trial, a trap, a recruit or stones. *AI:* buys Refine Gu like any promotion and resolves the
Alert by weights; Refine Gu is closed below 50 HP and in every state where no rung can be gained, so the AI never
pays for an empty attempt.

**P3 Heaven and earth are without benevolence.** Beast Tides hit every major at random: 3% per turn after T30, +2%
after T90 (about 3.8 tides per civ by T130), plus 2% per turn after T20 for the Rogue Cultivators. Random timing
staggers civs (E6). Tides escalate by era (wolves; then a wolf king; then a Thunder Crown Wolf). Lairs spawn Electric
Wolves, and Electric Wolf Kings once every civ knows Rank Three Cultivation [src]. Inheritances can trap. Preparation
(Formation Platform, a stone reserve) opens better choices. *AI:* everything fires from GlobalUniques, nation uniques
and barbarian spawns; its tide choices are weighted.

**P4 Specialists beat dabblers.** Moon and Strength exclude each other; path units require their branch; unpathed
clans are capped at Rank One plus White Jade Gu. Dao marks: +5% per adopted own-branch policy, same-path Gu
amplifiers (Moonlight Mastery, Boar Strength), −10% for a cross-path Gu. Each path's food ties it to territory.
*AI:* personality priorities put one path first (Gu Yue Moon 10, Bai Moon 8, Xiong Strength 10 and starts with it
adopted, Rogue Strength 12); the AI upgrade logic picks the `Can upgrade to` target whose `Only available` holds [src].

**P5 Righteous and demonic are strategies.** The branches exclude each other. Righteous: −25% upkeep for units on
friendly land, city-state favour, defence, the clan-law Betrayal choice. Demonic: stones from every kill (beasts
too, so a tide is income), plunder, captures, cheaper upkeep at war, the strike-first and caravan-robbery choices;
paid for with faster city-state decay, more unhappiness and a 3% Betrayal chance per turn. The Rogue Cultivators
are the third strategy: a cheap elite core and few cities. *AI:* the effects are passive, personalities set the
alignment, event picks are weighted.

## Questions for you (⛔)

Answer what you can; anything left open keeps the default in brackets. Questions 1–6 change object names or whole
mechanics, so they matter most before any JSON is written.

**Lore facts the plan leans on**

1. Moonlight Gu: moon path (月道) or light path? If it is light, the branch and the Moon units are renamed. [moon]
2. Boar Gu: what is the right name (Black Boar Gu?), and what does it eat? Or is it used up into the body? That
   decides whether the Wild Boar resource exists at all. [Black Boar Gu eats Wild Boar]
3. White Jade Gu or Jade Skin Gu? What does it eat? [White Jade Gu; it eats stones (+20% upkeep)]
4. The wolf tide: electric wolves led by a Thunder Crown Wolf, with an "Electric Wolf King" (a hundred-beast king)
   as the middle tier. Are the tiers and names right? Is "Hundred-Beast Wolf King" better? [as planned]
5. The awakening ceremony: where was it held? Is 开窍大典 right? Is "Awakening Grounds" acceptable as the name of the
   national wonder that holds the Hope Gu? [Awakening Grounds]
6. Leaders: Gu Yue Bo (Gu Yue), Bai Ning Bing (Bai: a genius, not the clan head), Xiong Lin (Xiong). Who actually led
   the Bai and Xiong villages? [as planned]
7. Liquor Worm: is "refines essence = faster XP" an acceptable mapping, and did Fang Yuan lure his with wine?
8. Hairy men and stone men in the Southern Border? The Jia clan's caravan at Qing Mao? [as planned]
9. The Flower Wine Monk's inheritance on Qing Mao: name, contents, and is the wine link right?
10. Essence colour per rank (green copper, red steel, white silver, yellow gold). It only colours the era icons.

**Scope and taste**

11. Paths for Slice 1: Moon + Strength? [yes]
12. Path conflict: hard exclusivity (AI-safe) or soft interference that lets players dabble at a cost? [hard]
13. Fourth major: the Rogue Cultivators led by Fang Yuan, or the Shang clan (now only a wonder)? [Rogue Cultivators]
14. Aptitude odds A/B/C/D 5/20/35/40%, with A stronger and cheaper to feed and D weaker and costlier? [yes]
15. Beast Enslavement as a generic late tech (recruiting gated on stone income), or reserved for an Enslavement path?
    [generic tech]
16. Spring Autumn Cicada stays out of Slice 1 (rank 6; Slice 2 / S8)? [yes]
17. Naming: "Rank One Gu Master" in words; era names; victory names; Vanilla difficulty names or flavoured ones
    (Mortal / Gu Master / Gu Immortal / Venerable)? [words; as planned; Vanilla names]
18. Tone: Betrayal's "strike first and take the traitor's Gu", Stone Shortage's "squeeze the mortals" and "rob a
    passing caravan". OK? [yes]
19. Beast tides and traitor hunts need barbarians enabled at game setup. OK to say so in the README and to
    recommend small Pangaea or Continents maps (there are no water units)? [yes]

---

## Objects

### Eras

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Rank One-Two era | 一转、二转 | ADAPTED **[VERIFY]** | Newly awakened clan youths at ranks one and two.<br>*[VERIFY] Essence colour per rank (green copper, red steel, white silver, yellow gold) is from memory; it only sets the era icon colour.* | Opening era (tech columns 1-3): founding villages, aptitude rolls, first refinements, and the path choice. All four policy branches open here so every AI commits to a path early (P1, P2, P4, P5).<br>*Fields:* startingSettlerUnit Clan Settler x1; startingWorkerUnit Mortal Laborer x1; startingMilitaryUnit Rank One Gu Master; startingGold 50; baseUnitBuyCost 200; researchAgreementCost 150; iconRGB [72,140,100]; tech costs 20/40/65 | — |
| Rank Three era | 三转 | ADAPTED **[VERIFY]** | Rank-three Gu Masters, the elders a mountain clan leans on.<br>*[VERIFY] Essence colour per rank (green copper, red steel, white silver, yellow gold) is from memory; it only sets the era icon colour. Typical clan ranks in the Southern Border are from memory.* | Mid era (columns 4-5): rank-3 path units, formations, caravans, killer moves. Beast Tides add an Electric Wolf King and careful refinement costs 70 (P2, P3, P4).<br>*Fields:* iconRGB [205,205,215]; tech costs 120/170; researchAgreementCost 250; baseUnitBuyCost 300 (later-era starts are disabled by ModOptions, so the kit fields are placeholders) | — |
| Rank Four era | 四转 | ADAPTED **[VERIFY]** | Rank-four Gu Masters, rare and decisive in a mountain clan.<br>*[VERIFY] Essence colour per rank (green copper, red steel, white silver, yellow gold) is from memory; it only sets the era icon colour. Typical clan ranks in the Southern Border are from memory.* | Late Slice-1 era (columns 6-7): rank-4 elites with the heaviest upkeep, beast enslavement and super-clan trade. Tides add a Thunder Crown Wolf and careful refinement costs 100 (P1, P3).<br>*Fields:* iconRGB [230,190,60]; tech costs 250/350; researchAgreementCost 350; baseUnitBuyCost 400 | — |

### Techs

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Aperture Awakening | 开窍 | ADAPTED | At the awakening ceremony a Hope Gu opens each youth's aperture. | Starting tech. Unlocks Clan Settler, Mortal Laborer, Rank One Gu Master, Farm, Ancestral Hall and Awakening Grounds (P2 through aptitude).<br>*Fields:* Rank One-Two era, column 1, row 2, cost 20 | `Starting tech` |
| Primeval Stone Mining | 元石 | ADAPTED **[VERIFY]** | Clans dig primeval stones, which are both money and essence fuel, out of mountain veins.<br>*[VERIFY] Primeval stones coming from mined veins (rather than another source) is from memory.* | Stone income (P1): Stone Mine, Mine, Road, Remove Forest.<br>*Fields:* Rank One-Two era, column 2, row 1, cost 40, prerequisites [Aperture Awakening] | — |
| Gu Feeding | 养蛊 | ADAPTED | Every Gu eats one specific food and starves without it. | Reveals Moon Orchid and Wild Boar. Unlocks Plantation, Camp, Gu Academy and Gu Feeding House (Moon Orchid Terrace for Gu Yue). Also switches on Gu Yue's free Moonlight Gu (P1).<br>*Fields:* Rank One-Two era, column 2, row 3, cost 40, prerequisites [Aperture Awakening] | — |
| Wine Brewing | 酿酒 | ADAPTED | Villages brew wine for mortals and for wine-drinking Gu such as the Liquor Worm. | Wine Cellar, the main Wine source, which feeds Liquor Worms (P1, P2).<br>*Fields:* Rank One-Two era, column 3, row 1, cost 65, prerequisites [Gu Feeding] | — |
| Gu Refinement | 炼蛊 | ADAPTED | Gu are refined from recipes and materials, and a failed attempt wastes them. | Refinement Chamber; makes the Refine Gu XP promotion available (P2).<br>*Fields:* Rank One-Two era, column 3, row 2, cost 65, prerequisites [Primeval Stone Mining, Gu Feeding] | — |
| Rank Two Cultivation | — | ADAPTED | The breakthrough from rank one to rank two. | Rank Two Moon and Strength Gu Masters, each needing its path branch; unpathed clans stay at rank one (P4). Breakthroughs are stone-paid upgrades (P1).<br>*Fields:* Rank One-Two era, column 3, row 3, cost 65, prerequisites [Gu Feeding] | — |
| Gu Formations | 蛊阵 | ADAPTED **[VERIFY]** | Villages shelter behind formations powered by Gu and primeval stones.<br>*[VERIFY] Defensive village formations at this rank are recalled only loosely.* | Formation Platform, which unlocks 'Raise the formation' in Beast Tide; Remove Jungle; Remove Marsh. Opens the Rank Three era (P3).<br>*Fields:* Rank Three era, column 4, row 1, cost 120, prerequisites [Gu Refinement] | — |
| Rank Three Cultivation | — | ADAPTED | The breakthrough to rank three. | Rank Three path units. Once every civ knows it, Electric Wolf Kings join the lair spawn pool (P3, P4).<br>*Fields:* Rank Three era, column 4, row 3, cost 120, prerequisites [Rank Two Cultivation, Gu Refinement] | — |
| Merchant Caravans | 商队 | ADAPTED **[VERIFY]** | Merchant caravans cross the mountains trading Gu, materials and stones.<br>*[VERIFY] A merchant caravan (the Jia clan) calling at Qing Mao Mountain is from memory.* | Trading House and Open Borders (P1).<br>*Fields:* Rank Three era, column 5, row 1, cost 170, prerequisites [Gu Formations, Wine Brewing] | `Enables Open Borders agreements` |
| Inheritance Lore | — | ADAPTED **[VERIFY]** | Dead Gu Masters leave inheritances for whoever finds them.<br>*[VERIFY] Inheritances guarded by trials and traps are from memory (S8 is design, not a §5 anchor).* | Unlocks the Flower Wine Monk Inheritance wonder (P2, S8).<br>*Fields:* Rank Three era, column 5, row 2, cost 170, prerequisites [Gu Formations, Rank Three Cultivation] | — |
| Killer Moves | — | ADAPTED | Several Gu used together form a killer move stronger than any single Gu. | Opens the Killer Move rung of the refinement ladder (P2). That rung adds upkeep (P1).<br>*Fields:* Rank Three era, column 5, row 3, cost 170, prerequisites [Rank Three Cultivation] | — |
| Super Clan Commerce | 超级家族 | ADAPTED **[VERIFY]** | The great Southern Border clans run trade cities the whole region depends on.<br>*[VERIFY] Southern Border super clans are a §5 VERIFY candidate.* | Shang Clan City wonder (P1).<br>*Fields:* Rank Four era, column 6, row 1, cost 250, prerequisites [Merchant Caravans] | — |
| Beast Enslavement | 奴道 | ADAPTED **[VERIFY]** | Enslavement-path Gu Masters bind wild beasts to their will.<br>*[VERIFY] Enslavement path as a named path, and beast armies in the Southern Border arc, are from memory. Recruiting units that are uniqueTo Barbarians needs an in-game test.* | A defeated Beast joins you with +10 stones, but only while stone income is above +4 per turn, and only after a melee kill: ranged Moon Gu Masters never recruit [src BattleUnitCapture]. Recruits eat stones (wolf +50%, king +100%, Thunder Crown +200%), so a tide becomes an army you must feed (P3, P1). A teaser for a later Enslavement path.<br>*Fields:* Rank Four era, column 6, row 2, cost 250, prerequisites [Inheritance Lore, Killer Moves] | `When defeating a [Beast] unit, earn [10] Gold and recruit it <when number of [[Gold] Per Turn] is more than [4]>` |
| Rank Four Cultivation | — | ADAPTED | The breakthrough to rank four. | Rank Four path units, the heaviest upkeep in Slice 1 (P1, P4).<br>*Fields:* Rank Four era, column 6, row 3, cost 250, prerequisites [Killer Moves] | — |
| Dao Comprehension | 悟道 | ADAPTED | Insight into the Great Dao has no end. | Final repeatable tech (§7) and score sink; Slice 2 hooks rank five here.<br>*Fields:* Rank Four era, column 7, row 2, cost 350, prerequisites [Super Clan Commerce, Beast Enslavement, Rank Four Cultivation]; whole tree about 2,100 science | `Can be continually researched` |

### Units

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Clan Settler | — | INVENTED | A branch family leaves to raise a new mountain village under the clan's name. | City founder. Pays upkeep like every unit, since there are no free units (P1).<br>*Fields:* unitType Civilian, movement 2, cost 80, requiredTech Aperture Awakening | `Founds a new city <by consuming this unit>`<br>`Excess Food converted to Production when under construction`<br>`Requires at least [2] population`<br>`Never appears as a Barbarian unit` |
| Mortal Laborer | 凡人 | ADAPTED | Mortals whose apertures were never opened farm, mine and haul for the Gu Masters. | Worker. Every laborer still costs upkeep, so too many is a slow leak (P1).<br>*Fields:* unitType Civilian, movement 2, cost 45, requiredTech Aperture Awakening | `Can build [Land] improvements on tiles`<br>`Automation is a primary action`<br>`Never appears as a Barbarian unit` |
| Rank One Gu Master | 一转蛊师 | ADAPTED | A freshly awakened youth with one or two Gu. | Starting and unpathed Gu Master. Rolls aptitude at creation (E3, P2) and pays +25% upkeep (P1). It grows only by upgrading into the path its clan adopted, and refines only a White Jade Gu on its own, so dabblers stall (P4).<br>*Fields:* unitType Gu Master, strength 8, movement 2, cost 35, requiredTech Aperture Awakening; no upgradesTo; two 'Can upgrade to' targets, and the AI picks the one whose 'Only available' holds [src UnitAutomation.getUnitsToUpgradeTo] | `[+25]% maintenance costs`<br>`Never appears as a Barbarian unit`<br>`Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> <for units without [Aptitude C]> <for units without [Aptitude D]>`<br>`Can upgrade to [Rank Two Moon Gu Master]`<br>`Can upgrade to [Rank Two Strength Gu Master]` |
| Rank Two Strength Gu Master | 二转力道蛊师 | ADAPTED **[VERIFY]** | A rank-two Gu Master who grafts beast strength onto the body.<br>*[VERIFY] Strength path (力道) as a Southern Border tradition, and boar Gu as its archetype, are from memory.* | Strength-path melee. First refinement rung is Black Boar Gu, which eats Wild Boar. Upkeep +100% (P1, P4).<br>*Fields:* unitType Strength Gu Master, strength 14, movement 2, cost 60, requiredTech Rank Two Cultivation, upgradesTo Rank Three Strength Gu Master | `[+100]% maintenance costs`<br>`Never appears as a Barbarian unit`<br>`Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> <for units without [Aptitude C]> <for units without [Aptitude D]>`<br>`Only available <after adopting [Strength Path]>` |
| Rank Three Strength Gu Master | 三转力道蛊师 | ADAPTED **[VERIFY]** | A rank-three strength cultivator able to wrestle a beast pack.<br>*[VERIFY] Strength path (力道) as a Southern Border tradition, and boar Gu as its archetype, are from memory.* | Mid-game melee core (P4); upkeep +175% (P1).<br>*Fields:* unitType Strength Gu Master, strength 22, movement 2, cost 95, requiredTech Rank Three Cultivation, upgradesTo Rank Four Strength Gu Master | `[+175]% maintenance costs`<br>`Never appears as a Barbarian unit`<br>`Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> <for units without [Aptitude C]> <for units without [Aptitude D]>`<br>`Only available <after adopting [Strength Path]>` |
| Rank Four Strength Gu Master | 四转力道蛊师 | ADAPTED **[VERIFY]** | A rank-four strength master, a walking siege engine.<br>*[VERIFY] Strength path (力道) as a Southern Border tradition, and boar Gu as its archetype, are from memory.* | Elite melee with the highest stone upkeep in Slice 1: +275%, 3.75 times a plain unit before its Gu (P1, P4).<br>*Fields:* unitType Strength Gu Master, strength 32, movement 2, cost 140, requiredTech Rank Four Cultivation | `[+275]% maintenance costs`<br>`Never appears as a Barbarian unit`<br>`Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> <for units without [Aptitude C]> <for units without [Aptitude D]>`<br>`Only available <after adopting [Strength Path]>` |
| Rank Two Moon Gu Master | 二转月道蛊师 | ADAPTED **[VERIFY]** | A rank-two Gu Master who throws blades of moonlight, the Gu Yue tradition.<br>*[VERIFY] Whether Moonlight Gu belongs to the moon path (月道) or the light path in canon.* | Moon-path ranged unit. Cheaper in stones than Strength (+75%), but its first rung, Moonlight Gu, eats Moon Orchids. Ranged units never recruit beasts (P1, P4).<br>*Fields:* unitType Moon Gu Master, strength 8, rangedStrength 13, range 2, movement 2, cost 60, requiredTech Rank Two Cultivation, upgradesTo Rank Three Moon Gu Master | `[+75]% maintenance costs`<br>`Never appears as a Barbarian unit`<br>`Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> <for units without [Aptitude C]> <for units without [Aptitude D]>`<br>`Only available <after adopting [Moon Path]>` |
| Rank Three Moon Gu Master | 三转月道蛊师 | ADAPTED **[VERIFY]** | A rank-three moon cultivator whose blades cut from a distance.<br>*[VERIFY] Same moon/light path question.* | Mid-game ranged core (P4); upkeep +150% (P1).<br>*Fields:* unitType Moon Gu Master, strength 12, rangedStrength 20, range 2, cost 95, requiredTech Rank Three Cultivation, upgradesTo Rank Four Moon Gu Master | `[+150]% maintenance costs`<br>`Never appears as a Barbarian unit`<br>`Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> <for units without [Aptitude C]> <for units without [Aptitude D]>`<br>`Only available <after adopting [Moon Path]>` |
| Rank Four Moon Gu Master | 四转月道蛊师 | ADAPTED **[VERIFY]** | A rank-four moon master, the pride of a moonlit clan.<br>*[VERIFY] Same moon/light path question.* | Elite ranged unit (P4); upkeep +225% (P1).<br>*Fields:* unitType Moon Gu Master, strength 18, rangedStrength 29, range 2, cost 140, requiredTech Rank Four Cultivation | `[+225]% maintenance costs`<br>`Never appears as a Barbarian unit`<br>`Triggers a [Aptitude Awakening] event <for units without [Aptitude A]> <for units without [Aptitude B]> <for units without [Aptitude C]> <for units without [Aptitude D]>`<br>`Only available <after adopting [Moon Path]>` |
| Electric Wolf | 电狼 | CANON **[VERIFY]** | Lightning-charged wolves that hunt in packs on the Southern Border mountains.<br>*[VERIFY] The electric wolf tide is a §5 VERIFY candidate.* | The only beast in the lair spawn pool at first, and tide fodder. It gives XP for refinement (P2), a stone bounty to Demonic clans (P5), and eats stones if recruited (P1).<br>*Fields:* unitType Beast, strength 9, movement 3, cost 30, uniqueTo Barbarians, no requiredTech | `[+50]% maintenance costs` |
| Electric Wolf King | 电狼百兽王 | ADAPTED **[VERIFY]** | A hundred-beast king that leads an electric wolf pack and drives it harder.<br>*[VERIFY] Beast-king tiers are canon; an electric-wolf hundred-beast king in the Qing Mao tide is assumed. The English name is invented and 电狼百兽王 is a constructed term (fan translations say 'hundred-beast king').* | Mid beast. It enters the lair spawn pool only once EVERY civ knows Rank Three Cultivation [src BarbarianManager.updateBarbarianTech], and joins tides from the Rank Three era. Buffs nearby wolves (P3).<br>*Fields:* unitType Beast, strength 16, movement 3, cost 60, requiredTech Rank Three Cultivation, uniqueTo Barbarians | `[+15]% Strength bonus for [Electric Wolf] units within [2] tiles`<br>`[+100]% maintenance costs` |
| Thunder Crown Wolf | 雷冠头狼 | CANON **[VERIFY]** | A great wolf king crowned with thunder, said to lead the wolf tide against the Qing Mao villages.<br>*[VERIFY] §5 VERIFY candidate. Also: its tier (thousand- or ten-thousand-beast king) and Chinese name.* | Top Slice-1 beast with an aura for all beasts (P3). Unbuildable keeps it out of lair spawns, so it appears only through Rank Four era Beast Tides; rebel spawns ignore Unbuildable [src UniqueTriggerActivation OneTimeRebel].<br>*Fields:* unitType Beast, strength 28, movement 3, cost 120, uniqueTo Barbarians | `Unbuildable`<br>`[+20]% Strength bonus for [Beast] units within [2] tiles`<br>`[+200]% maintenance costs` |

### Promotions

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Aptitude A | 甲等资质 | CANON **[VERIFY]** | A primeval sea that fills most of the aperture and recovers fast; such youths need fewer stones to advance.<br>*[VERIFY] Grade names 甲乙丙丁; aptitude as the primeval sea's share of the aperture (not aperture size) and 'lower aptitude needs more stones' are from memory.* | Rolled at 5% (9.5% with the Awakening Grounds, about 9% for Bai): stronger, cheaper to feed, faster XP (P2, P1).<br>*Fields:* no unitTypes (never bought with XP); granted only by Aptitude Awakening | `[+15]% Strength`<br>`[-20]% maintenance costs`<br>`[+25]% XP gained from combat` |
| Aptitude B | 乙等资质 | CANON **[VERIFY]** | A good aptitude, the backbone of a clan's future.<br>*[VERIFY] Grade naming.* | Rolled at 20% (28.6% with the Awakening Grounds) (P2).<br>*Fields:* no unitTypes; Aptitude Awakening only | `[+5]% Strength`<br>`[-10]% maintenance costs`<br>`[+10]% XP gained from combat` |
| Aptitude C | 丙等资质 | CANON **[VERIFY]** | An ordinary aptitude.<br>*[VERIFY] Grade naming.* | Rolled at 35%; baseline grade with no effect, so every Gu Master shows a grade (P2).<br>*Fields:* no unitTypes; Aptitude Awakening only | — |
| Aptitude D | 丁等资质 | CANON **[VERIFY]** | A shallow primeval sea that recovers slowly and wastes stones.<br>*[VERIFY] Grade naming.* | Rolled at 40% (28.6% with the Awakening Grounds): weaker, eats more and learns slowly, so the player must decide whether to keep or disband the unit (P2, P1).<br>*Fields:* no unitTypes; Aptitude Awakening only | `[-10]% Strength`<br>`[+20]% maintenance costs`<br>`[-25]% XP gained from combat` |
| Refine Gu | — | ADAPTED | A Gu Master spends hard-won insight on a refinement attempt. | The only XP-purchasable promotion, so every XP spend is a gamble (P2). KEPT, because the AI never buys a promotion with 'Doing so will consume...' [src NextTurnAutomation.applyPromotions]; it removes itself at the next turn start, so it repeats at most once per unit per turn at XP cost 10/20/30/40... It opens the Refinement Attempt Alert on this unit (E2). Closed below 50 HP and in every dead state of the ladder (see 'Refinement ladder'), so neither the AI nor a player can pay XP for an attempt that cannot succeed.<br>*Fields:* unitTypes [Gu Master, Moon Gu Master, Strength Gu Master]; ModOptions constants.maxXPfromBarbarians 90 | `Only available <after discovering [Gu Refinement]>`<br>`Unavailable <when below [50] HP>`<br>`Unavailable <for units with [Killer Move]>`<br>`Unavailable <for [Gu Master] units> <for units with [White Jade Gu]>`<br>`Unavailable <for units with [White Jade Gu]> <for units with [Moonlight Gu]> <before discovering [Killer Moves]>`<br>`Unavailable <for units with [White Jade Gu]> <for units with [Black Boar Gu]> <before discovering [Killer Moves]>`<br>`Unavailable <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <when below [1] [Moon Orchid]>`<br>`Unavailable <for [Strength Gu Master] units> <for units without [Black Boar Gu]> <for units without [Moonlight Gu]> <when below [1] [Wild Boar]>`<br>`Triggers a [Refinement Attempt] event`<br>`[This Unit] loses the [Refine Gu] promotion <upon turn start>` |
| Moonlight Gu | 月光蛊 | CANON **[VERIFY]** | Gu Yue's signature attack Gu, which eats moon orchid petals.<br>*[VERIFY] Whether Moonlight Gu belongs to the moon path (月道) or the light path in canon. Gu and food are §5 anchors; the effects are 4X mappings, not canon.* | +20% attack. Eats 1 Moon Orchid, so a shortage gives every holder the engine's -25% 'Missing resource' malus [src BattleDamage] (P1). -10% on a Strength unit as mixed-path interference (P4).<br>*Fields:* no unitTypes; granted by the refinement ladder (Moon units) and by Gu Yue's nation unique | `[+20]% Strength <when attacking>`<br>`Consumes [1] [Moon Orchid]`<br>`[-10]% Strength <for [Strength Gu Master] units>` |
| Black Boar Gu | 黑豕蛊 | CANON **[VERIFY]** | A strength-path Gu that grants its owner the strength of one boar.<br>*[VERIFY] Name (Black Boar vs Black-White Boar) and its food. If canon says the boar Gu is used up into the body, drop the Consumes line and the Wild Boar resource. Effects are 4X mappings.* | First rung for Strength units: +15% strength, eats 1 Wild Boar (P1); -10% on a Moon unit (P4).<br>*Fields:* no unitTypes; refinement ladder only | `[+15]% Strength`<br>`Consumes [1] [Wild Boar]`<br>`[-10]% Strength <for [Moon Gu Master] units>` |
| White Jade Gu | 白玉蛊 | CANON **[VERIFY]** | A defensive Gu that hardens the skin like white jade.<br>*[VERIFY] White Jade Gu vs Jade Skin Gu as the canonical name; its rank and food. Effects are 4X mappings.* | Second rung for path units, and the only rung an unpathed Rank One can reach. +25% defending and +20% upkeep: its food is unknown, so it eats stones (P1, P2).<br>*Fields:* no unitTypes; refinement ladder only | `[+25]% Strength <when defending>`<br>`[+20]% maintenance costs` |
| Liquor Worm | 酒虫 | CANON **[VERIFY]** | A Gu that drinks wine and refines its master's primeval essence.<br>*[VERIFY] 'Refines essence = faster progress (XP)' is my mapping; how Fang Yuan obtained his (lured with wine?) is from memory.* | +50% XP (faster cultivation, so more refinements) but drinks 1 Wine. Only obtained through the Refinement Attempt choice that requires spare Wine, which competes with the next ladder rung (P1, P2).<br>*Fields:* no unitTypes; Refinement Attempt choice 3 only | `[+50]% XP gained from combat`<br>`Consumes [1] [Wine]` |
| Killer Move | 杀招 | ADAPTED | The unit's Gu now strike together as one move, at a steep essence cost. | Top rung, which needs White Jade Gu, a path Gu and the Killer Moves tech: +25% attack and +25% upkeep (P1, P2).<br>*Fields:* no unitTypes; refinement ladder only | `[+25]% Strength <when attacking>`<br>`[+25]% maintenance costs` |

### Buildings and wonders

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Clan Hall | — | INVENTED | Seat of the clan leader and the clan treasury in the main village. | Palace: base stones, science and culture every civ can count on (P1).<br>*Fields:* isNationalWonder (palace), cost 0, production 3, gold 5, science 2, culture 1, cityStrength 3; auto-placed in the capital | `Indicates the capital city` |
| Ancestral Hall | — | INVENTED | Where a clan honours its dead and binds its members. | Early culture so a path branch comes early (P4); +1 stability (P5); upkeep 1 (P1).<br>*Fields:* requiredTech Aperture Awakening, cost 45, maintenance 1, culture 2, happiness 1 | — |
| Gu Academy | 学堂 | ADAPTED **[VERIFY]** | The clan school where newly awakened youths learn to raise and use Gu.<br>*[VERIFY] The Gu Yue clan academy and its elder are from memory.* | Science. New Gu Masters start with 10 XP, enough for an immediate first refinement (P2).<br>*Fields:* requiredTech Gu Feeding, cost 65, maintenance 1, science 1 | `[+1 Science] per [2] population [in this city]`<br>`New [Military] units start with [10] XP [in this city]` |
| Gu Feeding House | — | INVENTED | Mortal servants grow and gather the foods the clan's Gu eat. | Turns stone upkeep into Gu food: +1 Moon Orchid and +1 Wild Boar per city (P1).<br>*Fields:* requiredTech Gu Feeding, cost 70, maintenance 1 | `Provides [1] [Moon Orchid]`<br>`Provides [1] [Wild Boar]` |
| Moon Orchid Terrace | — | ADAPTED **[VERIFY]** | Gu Yue's terraced orchid fields that feed the clan's Moonlight Gu.<br>*[VERIFY] Terraces are invented; only the Gu Yue clan's orchid supply is anchored.* | Gu Yue unique building, replacing Gu Feeding House: +2 Moon Orchid, +1 Wild Boar, +1 food. Gu Yue's free Moonlight Gu only flows while orchids are in surplus, so this building is what keeps it flowing (P1).<br>*Fields:* uniqueTo Gu Yue Clan, replaces Gu Feeding House, requiredTech Gu Feeding, cost 70, maintenance 1, food 1 | `Provides [2] [Moon Orchid]`<br>`Provides [1] [Wild Boar]` |
| Wine Cellar | 酒窖 | ADAPTED | Village wine stores, drunk by mortals and by wine-eating Gu. | +1 Wine (the Liquor Worm's food) and +1 stability for 1 stone per turn (P1).<br>*Fields:* requiredTech Wine Brewing, cost 60, maintenance 1, happiness 1 | `Provides [1] [Wine]` |
| Refinement Chamber | — | INVENTED | A sealed furnace room stocked with materials for safer refinements. | Required for the careful refinement choice (85% instead of 50% success), with upkeep 1: preparation that costs stones (P2, P1).<br>*Fields:* requiredTech Gu Refinement, cost 90, maintenance 1, production 1, science 1 | — |
| Formation Platform | — | ADAPTED **[VERIFY]** | A platform from which the village raises its defensive formation.<br>*[VERIFY] Formation use by low-rank village clans is an adaptation.* | City defence; unlocks 'Raise the formation' in Beast Tide, so preparation buys a better option (P3).<br>*Fields:* requiredTech Gu Formations, cost 110, maintenance 1, cityStrength 8, cityHealth 50 | — |
| Trading House | 商铺 | ADAPTED | A shop where caravans trade Gu, materials and stones. | Stone income with no upkeep (P1).<br>*Fields:* requiredTech Merchant Caravans, cost 130, gold 2, percentStatBonus gold +20 | — |
| Awakening Grounds (wonder) | 开窍大典 | ADAPTED **[VERIFY]** | The clan's stock of Hope Gu, used to open the youths' apertures at the awakening ceremony.<br>*[VERIFY] Ceremony venue (an altar or a flower field?) is unknown, so the name avoids one; 开窍大典 (awakening ceremony) needs confirming. In canon aptitude is innate and the ceremony only reveals it, so the odds shift is pure adaptation.* | National wonder that shifts the aptitude die through conditional AI weights in Aptitude Awakening: A from 5% to 9.5%, B from 20% to 28.6%, D from 40% to 28.6% (P2). An early race against building settlers; every personality weights it +100%.<br>*Fields:* isNationalWonder, requiredTech Aperture Awakening, cost 75, culture 1; the effect lives in Events.json | — |
| Flower Wine Monk Inheritance (wonder) | 花酒行者传承 | ADAPTED **[VERIFY]** | The hidden legacy of a demonic Gu Master who died on Qing Mao Mountain.<br>*[VERIFY] English and Chinese name, location and contents of this inheritance; the wine link is assumed from the name.* | World wonder: +2 Wine (feeds two Liquor Worms) and +25% combat XP civ-wide, so more refinement gambles (P2, P1).<br>*Fields:* isWonder, requiredTech Inheritance Lore, cost 240, culture 3 | `Provides [2] [Wine]`<br>`[+25]% XP gained from combat` |
| Shang Clan City (wonder) | 商家城 | ADAPTED **[VERIFY]** | The great market city ruled by a Southern Border merchant clan.<br>*[VERIFY] The Shang clan and its city are a §5 VERIFY candidate (super clans).* | World wonder and late stone engine: +5 stones, +2 per Trading House, and cheaper city-state influence (P1, P5).<br>*Fields:* isWonder, requiredTech Super Clan Commerce, cost 300, gold 5 | `[+2 Gold] from all [Trading House] buildings`<br>`Gifts of Gold to City-States generate [+50]% more Influence` |

### Resources

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Primeval Stone Vein | 元石矿脉 | ADAPTED **[VERIFY]** | A seam of primeval stones in the mountain rock.<br>*[VERIFY] Veins as the physical source of primeval stones.* | The stone tile: 3 stones when improved, against working a food tile instead. A pillage target for beasts and demonic raiders (P1, P5). Hill start regions get an extra one.<br>*Fields:* resourceType Bonus; terrains Hill, Plains, Tundra, Desert; gold 1; improvement Stone Mine (+2 gold) | — |
| Moon Orchid | 月兰 | CANON **[VERIFY]** | Pale orchids whose petals feed Moonlight Gu.<br>*[VERIFY] The Chinese name 月兰.* | Strategic Gu food: each Moonlight Gu eats 1, and a shortage gives every holder -25%. The decision: settle near orchids, feed your own Gu, or sell orchids to a Moon AI for stones (P1, P4).<br>*Fields:* Strategic; revealedBy Gu Feeding; terrains Grassland, Plains, Forest; food 1; Plantation +1 food; deposits minor 1 / major 2 (abundant 2/3); other sources: Gu Feeding House +1, Moon Orchid Terrace +2, Moon Path opener +2, Orchid Terraces +2 | `Guaranteed with Strategic Balance resource option` |
| Wild Boar | — | INVENTED **[VERIFY]** | Boars of the Southern Border forests, used as a placeholder food for boar-strength Gu.<br>*[VERIFY] What boar-strength Gu eat in canon; rename the resource or drop it.* | Strategic Gu food: each Black Boar Gu eats 1. Same decisions as Moon Orchid (P1, P4).<br>*Fields:* Strategic; revealedBy Gu Feeding; terrains Forest, Jungle, Grassland, Hill; food 1; Camp +1 production; deposits as Moon Orchid; other sources: Strength Path opener +2, Beast Hunters +2, Gu Feeding House +1 | `Guaranteed with Strategic Balance resource option` |
| Wine | 酒 | ADAPTED | Brewed wine, drunk by villagers and by the Liquor Worm. | Strategic, made only by Wine Cellars and the Flower Wine Monk wonder, with no map deposits; each Liquor Worm drinks 1 (P1). It is strategic on purpose: a consumed luxury still grants happiness once its net amount goes negative [src CivInfoTransientCache drops only zero entries; CivInfoStatsForNextTurn counts any entry], so a luxury food would be no decision.<br>*Fields:* resourceType Strategic; terrainsCanBeFoundOn [] (accepted by mod-ci) | — |
| Jade | — | INVENTED | Fine stone prized by mountain clans. | Luxury: +4 happiness, or trade it for stones (P1, P5).<br>*Fields:* Luxury; terrain Hill; gold 2; improvement Mine (+1 gold) | — |
| Furs | — | INVENTED | Pelts of Southern Border beasts sold by caravans. | Second luxury: happiness or trade. Keeps clan stability workable on small maps; uses the built-in icon.<br>*Fields:* Luxury; terrains Forest, Tundra, Jungle; gold 2; improvement Camp (+1 gold) | — |

### Improvements

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Farm | — | INVENTED | Mortal fields that feed the village. | Food and growth; Vanilla name kept for its built-in art.<br>*Fields:* techRequired Aperture Awakening; Plains, Grassland, Desert, Flood plains; food 1; turnsToBuild 7 | `Can also be built on tiles adjacent to fresh water` |
| Mine | — | INVENTED | Shafts dug into the hills. | Production on hills; improves Jade.<br>*Fields:* techRequired Primeval Stone Mining; Hill; production 1; turnsToBuild 7 | — |
| Stone Mine | 元石矿 | ADAPTED **[VERIFY]** | A mine dug into a primeval stone vein.<br>*[VERIFY] Veins as the physical source of primeval stones are from memory (as Primeval Stone Vein).* | Builds the stone tile. Pillaging it pays stones, doubled by the Demonic Plunder policy (P1, P5).<br>*Fields:* techRequired Primeval Stone Mining; turnsToBuild 6; improves Primeval Stone Vein | `Can only be built to improve a resource`<br>`Pillaging this improvement yields approximately [+20 Gold]` |
| Plantation | — | INVENTED | Tended beds of moon orchids. | Improves Moon Orchid; Vanilla name kept for art.<br>*Fields:* techRequired Gu Feeding; turnsToBuild 6 | `Can only be built to improve a resource`<br>`Does not need removal of [Forest]` |
| Camp | — | INVENTED | A hunters' lodge in the forest. | Improves Wild Boar and Furs; Vanilla name kept for art.<br>*Fields:* techRequired Gu Feeding; turnsToBuild 6 | `Does not need removal of [Forest]`<br>`Does not need removal of [Jungle]`<br>`Can only be built to improve a resource` |
| Road | — | INVENTED | Mountain paths between villages. | City connections bring stones, but each tile costs 1 stone per turn, so road spam is a trap for a careless player (P1). The name is hardcoded in the engine.<br>*Fields:* techRequired Primeval Stone Mining; terrainsCanBeBuiltOn Land; turnsToBuild 4 | `Can be built outside your borders`<br>`Costs [1] [Gold] per turn when in your territory` |
| Beast Lair | 兽巢 | ADAPTED | The den of a beast group; packs keep coming out of it until it is cleared. | Barbarian camp; the engine accepts any improvement that has 'Marks a barbarian camp'. It spawns beasts, and clearing it pays clearBarbarianCampReward in stones (P3, P1).<br>*Fields:* terrainsCanBeBuiltOn Land; the notification icon path 'ImprovementIcons/Barbarian encampment' is hardcoded but built in | `Unpillagable`<br>`Unbuildable`<br>`Excluded from map editor`<br>`Marks a barbarian camp` |
| Inheritance Site | 传承 | ADAPTED **[VERIFY]** | A dead Gu Master's sealed legacy, rewarding and sometimes trapped.<br>*[VERIFY] Inheritances guarded by trials and traps are from memory (S8 is design, not a §5 anchor).* | Ancient-ruins equivalent with double-edged rewards (S8; P2, P3).<br>*Fields:* terrainsCanBeBuiltOn Land; placed by map generation; the notification icon 'ImprovementIcons/Ancient ruins' is hardcoded and built in | `Unpillagable`<br>`Provides a random bonus when entered`<br>`Unbuildable`<br>`Does not need removal of [Forest]`<br>`Does not need removal of [Jungle]` |
| Engine-coupled Vanilla improvements | — | INVENTED | Not lore: infrastructure the engine refers to by name. | Copied from Vanilla as strict JSON, uniques verbatim: Remove Forest (tech Primeval Stone Mining), Remove Jungle and Remove Marsh (Gu Formations), Remove Road, Cancel improvement order, Repair, City center, City ruins.<br>*Fields:* techRequired retargeted to our techs or dropped; no yields changed | Vanilla, verbatim |

### Terrains

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Hill | — | INVENTED | Mountain slopes where villages and mines sit. | Vanilla Hill, except that the start-region bonus resource is a stone vein instead of Sheep (P1).<br>*Fields:* all other Vanilla uniques verbatim | `Starts in regions of this type receive an extra [Primeval Stone Vein]`<br>(other uniques: Vanilla, verbatim) |
| Mountain | — | INVENTED | Mountains divide the clans' villages. | Impassable, as in Vanilla; shapes the map. Its Vanilla damage unique never fires, because no unit can end a turn there.<br>*Fields:* Vanilla: impassable; other uniques verbatim | Vanilla, verbatim |
| Vanilla base terrains | — | INVENTED | Not lore: the Vanilla set already covers mountains, hills, forest and jungle. | Ocean, Coast, Lakes, Grassland, Plains, Tundra, Desert, Snow, Forest, Jungle, Marsh, Oasis, Flood plains, Ice, Atoll and River kept with their Vanilla map-generation and region uniques, so the generator covers every climate zone and the tileset art still works. Dropped: Fallout and every natural wonder. No hostile-terrain damage in Slice 1 (S4 hostile terrain belongs to Slice 3).<br>*Fields:* 18 terrains in total with Hill and Mountain; strict JSON copies | Vanilla, verbatim |

### Policies

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| **Righteous Path** (branch) | 正道 | ADAPTED | Righteous clans uphold clan law and alliances, and keep a respectable face. | Excludes Demonic. City-state favour, and cheaper upkeep for units standing on friendly land (the S6 'cheaper defensive upkeep'; civ-wide maintenance uniques are evaluated per unit [src]) (P5, P1).<br>*Fields:* era Rank One-Two era; members Clan Rules, Righteous Alliance, Guardian Formations, Righteous Path Complete | `Only available <before adopting [Demonic Path]>`<br>`Resting point for Influence with City-States is increased by [15]`<br>`[-25]% maintenance costs <in [Friendly Land] tiles>` |
| Clan Rules | 族规 | ADAPTED | Strict clan law keeps members in line. | Less unhappiness, so fewer unhappiness-driven betrayals (P5).<br>*Fields:* Righteous Path, row 1, column 1 | `[-15]% Unhappiness from [Population] [in all cities]` |
| Righteous Alliance | — | INVENTED | Righteous clans band together against demonic threats. | City-state favour (P5).<br>*Fields:* Righteous Path, row 1, column 3 | `City-State Influence recovers at twice the normal rate`<br>`Gifts of Gold to City-States generate [+25]% more Influence` |
| Guardian Formations | — | INVENTED | A righteous village is held, not abandoned. | Defence against tides and raiders (P3, P5).<br>*Fields:* Righteous Path, row 2, column 2, requires [Clan Rules] | `[+25]% Strength for cities`<br>`[+10]% Strength <when defending>` |
| Righteous Path Complete | — | INVENTED | A stable clan feeds its Gu efficiently. | Finisher: cheaper upkeep everywhere (P1).<br>*Fields:* finisher of Righteous Path | `[-10]% maintenance costs` |
| **Demonic Path** (branch) | 魔道 | ADAPTED | Demonic cultivators take what they need by force and trust no one. | Excludes Righteous. Every kill pays stones, beasts included (wolf 15, king 30). The price: faster city-state influence decay and a 3% Betrayal chance per turn (P5, P1).<br>*Fields:* era Rank One-Two era; members Plunder, Blood Harvest, Ruthless Cultivation, Demonic Path Complete | `Only available <before adopting [Righteous Path]>`<br>`Earn [50]% of killed [Military] unit's [Cost] as [Gold]`<br>`[+50]% City-State Influence degradation`<br>`Triggers a [Betrayal] event <upon turn start> <with [3]% chance>` |
| Plunder | — | INVENTED | Demonic Gu Masters strip whatever they overrun. | Pillage and lair income (P1, P5).<br>*Fields:* Demonic Path, row 1, column 1 | `[+100]% Yield from pillaging tiles`<br>`Receive [+100]% Gold from Barbarian encampments and pillaging Cities` |
| Blood Harvest | — | INVENTED | Every kill feeds the killer. | Heal on kill and faster XP, so more refinement gambles (P2, P5).<br>*Fields:* Demonic Path, row 1, column 3 | `Heals [15] damage if it kills a unit`<br>`[+25]% XP gained from combat` |
| Ruthless Cultivation | — | INVENTED | War feeds the Gu; peace starves them; mortals pay. | Stones on city capture and cheaper upkeep at war, paid for with unrest (P5, P1).<br>*Fields:* Demonic Path, row 2, column 2, requires [Plunder] | `Upon capturing a city, receive [3] times its [Gold] production as [Gold] immediately`<br>`[-20]% maintenance costs <when at war>`<br>`[+20]% Unhappiness from [Population] [in all cities]` |
| Demonic Path Complete | — | INVENTED | Strike first, strike hardest. | Finisher: offence (P5).<br>*Fields:* finisher of Demonic Path | `[+15]% Strength <when attacking>` |
| **Moon Path** (branch) | 月道 | ADAPTED **[VERIFY]** | Gu that shape moonlight into blades, the tradition of the Gu Yue clan.<br>*[VERIFY] Moon path vs light path as Moonlight Gu's canonical path; rename the branch if it is light.* | Path commitment, excluding Strength. Gives +2 Moon Orchid and dao marks: +5% strength for Moon units per adopted Moon policy. Unlocks Moon units (P4, P1).<br>*Fields:* era Rank One-Two era; members Moonlight Mastery, Orchid Terraces, Moon Blade Step, Moon Path Complete | `Only available <before adopting [Strength Path]>`<br>`Provides [2] [Moon Orchid]`<br>`[+5]% Strength <for [Moon Gu Master] units> <for every [Adopted [[Moon Path] branch] Policies]>` |
| Moonlight Mastery | — | ADAPTED | Path insight multiplies Gu of the same path. | Same-path amplification (P4).<br>*Fields:* Moon Path, row 1, column 1 | `[+15]% Strength <for units with [Moonlight Gu]>` |
| Orchid Terraces | — | INVENTED | Terraced orchid fields across the slopes. | More Gu food and cheaper Moon upkeep (P1, P4).<br>*Fields:* Moon Path, row 1, column 3 | `Provides [2] [Moon Orchid]`<br>`[-15]% maintenance costs <for [Moon Gu Master] units>` |
| Moon Blade Step | — | INVENTED | Moon cultivators strike and slip away. | Mobility (P4).<br>*Fields:* Moon Path, row 2, column 2, requires [Moonlight Mastery] | `[1] Movement <for [Moon Gu Master] units>` |
| Moon Path Complete | — | INVENTED | The clan's moon tradition is fully mastered. | Finisher: new Moon units start with 10 XP, an immediate refinement (P2).<br>*Fields:* finisher of Moon Path | `New [Moon Gu Master] units start with [10] XP [in all cities]` |
| **Strength Path** (branch) | 力道 | ADAPTED **[VERIFY]** | Strength-path Gu add raw might to the body itself.<br>*[VERIFY] Strength path (力道) as a Southern Border tradition, and boar Gu as its archetype, are from memory.* | Path commitment, excluding Moon. Gives +2 Wild Boar and dao marks: +5% for Strength units per adopted Strength policy. Unlocks Strength units (P4, P1).<br>*Fields:* era Rank One-Two era; members Boar Strength, Beast Hunters, Unyielding Body, Strength Path Complete | `Only available <before adopting [Moon Path]>`<br>`Provides [2] [Wild Boar]`<br>`[+5]% Strength <for [Strength Gu Master] units> <for every [Adopted [[Strength Path] branch] Policies]>` |
| Boar Strength | — | ADAPTED **[VERIFY]** | Path insight multiplies boar-strength Gu.<br>*[VERIFY] Boar-strength Gu as the archetypal early strength-path Gu.* | Same-path amplification (P4).<br>*Fields:* Strength Path, row 1, column 1 | `[+15]% Strength <for units with [Black Boar Gu]>` |
| Beast Hunters | — | INVENTED | Strength cultivators prove themselves against beast packs. | Gu food plus a bonus against beasts that turns tides into XP (P3, P2).<br>*Fields:* Strength Path, row 1, column 3 | `Provides [2] [Wild Boar]`<br>`[+25]% Strength <vs [Barbarians] units>` |
| Unyielding Body | — | INVENTED | A tempered body recovers in the middle of a fight. | Sustain (P4).<br>*Fields:* Strength Path, row 2, column 2, requires [Boar Strength] | `Heals [10] damage if it kills a unit` |
| Strength Path Complete | — | INVENTED | The body itself becomes the weapon. | Finisher: mobility (P4).<br>*Fields:* finisher of Strength Path | `[1] Movement <for [Strength Gu Master] units>` |

### Events

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Aptitude Awakening | 资质 | ADAPTED | At awakening each youth's aptitude is graded A to D, and the clan invests in them accordingly. | 'None' weighted die fired once when each Gu Master is created (E3); the four 'without' guards stop a second grade after an upgrade. Odds A/B/C/D 5/20/35/40%; with the Awakening Grounds 9.5/28.6/33.3/28.6%; Bai without it 9.1/22.7/31.8/36.4%. Hits AI and human alike (P2).<br>*Fields:* presentation None; see 'Events in detail' | see [Events in detail](#events-in-detail) |
| Refinement Attempt | — | ADAPTED | Refining a Gu always risks the materials and the refiner's time and stones. | Alert on the unit (E2), opened by Refine Gu or the Unfinished Refinement ruin. 1 CAREFUL: Refinement Chamber and a stone reserve, 40/70/100 stones by era, 85%. 2 RECKLESS: free, 50%, always 30 damage, closed below 31 HP. 3 LURE A LIQUOR WORM: spare Wine and 20 stones, 70%. 4 COOL: +5 XP. Choices 1-2 grant the next rung of the ladder and close in its dead states (P2, P1, P4).<br>*Fields:* presentation Alert; see 'Events in detail' and 'Refinement ladder' | see [Events in detail](#events-in-detail) |
| Beast Tide | 兽潮 | ADAPTED **[VERIFY]** | A wolf tide floods down the mountain and every village must fight, pay or give ground.<br>*[VERIFY] The wolf tide (electric wolves led by a Thunder Crown Wolf) is a §5 VERIFY candidate.* | Fires for every major at 3% per turn after T30 (+2% after T90), plus 2% per turn after T20 for the Rogue Cultivators; random timing staggers civs (E6). 1 MEET the beasts by your first city (they scale by era). 2 PAY rogue cultivators 60/100/150 stones: no beasts. 3 ABANDON the outer fields: -1 population in every city. 4 RAISE THE FORMATION: Formation Platform, 40/70 stones and -20% production for 5 turns (P3).<br>*Fields:* presentation Alert; see 'Events in detail'; rebels need barbarians enabled at game setup [src] | see [Events in detail](#events-in-detail) |
| Betrayal | 背叛 | ADAPTED | In the Gu world kin and allies sell each other out for stones and Gu. | Fires for unhappy clans (8% per turn below 0 happiness), rich clans (3% per turn above 300 stones) and the Demonic Path (3% per turn); the Demonic caravan robbery can chain it. 1 LET GO: -60 stones. 2 HUNT: the traitor appears by your first city as a hostile Gu Master of your path. 3 CLAN LAW (Righteous): -1 population in the capital, +2 happiness for 10 turns. 4 STRIKE FIRST (Demonic): +40 stones, -1 population in the capital, -3 happiness for 10 turns (P5, P1).<br>*Fields:* presentation Alert; see 'Events in detail'; rebels ignore 'Never appears as a Barbarian unit' [src] | see [Events in detail](#events-in-detail) |
| Stone Shortage | — | ADAPTED | The vaults run dry and the clan's Gu begin to starve. | Fires at 25% per turn while stones are below 0 AND income is negative, before the engine's -200 disband. 1 RATION: -40% upkeep and -15% strength for 8 turns (the AI's main exit). 2 BORROW: +80 now, -6 per turn for 20 turns (net -40), only above -100. 3 SQUEEZE THE MORTALS: +50 stones, -1 population in the capital. 4 ROB A CARAVAN (Demonic): +70 stones, 25% chance of a Betrayal (P1, P5).<br>*Fields:* presentation Alert; see 'Events in detail' | see [Events in detail](#events-in-detail) |

### Nations

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Gu Yue Clan | 古月一族 | CANON **[VERIFY]** | The Qing Mao Mountain clan whose Gu Masters wield Moonlight Gu fed from orchid fields.<br>*[VERIFY] Gu Yue Bo as clan leader in the Qing Mao arc; the extra city names are invented.* | Once Gu Feeding is known, every Rank One Gu Master trained while Moon Orchids are in surplus gets a Moonlight Gu: stronger, but each eats an orchid, so the clan farms them (Moon Orchid Terrace) (P1). AI leans Moon and Righteous.<br>*Fields:* leaderName Gu Yue Bo; personality 'Gu Yue Temperament' (science 7, culture 6, gold 5, military 4, aggressive 3; priorities Moon Path 10, Righteous Path 6; '[+50]% weight to [Moon Orchid Terrace] for AI decisions', '[+100]% weight to [Awakening Grounds] for AI decisions'); unique building Moon Orchid Terrace; cities Gu Yue Village + invented; colours [30,40,90]/[220,220,240] | `All newly-trained [Rank One Gu Master] units [in all cities] receive the [Moonlight Gu] promotion <after discovering [Gu Feeding]> <when above [0] [Moon Orchid]>`<br>`Start bias [Hill]`<br>Personality: `[+50]% weight to [Moon Orchid Terrace] for AI decisions`<br>Personality: `[+100]% weight to [Awakening Grounds] for AI decisions` |
| Bai Clan | 白家 | CANON **[VERIFY]** | Gu Yue's rival village on Qing Mao, home of a frighteningly gifted young genius.<br>*[VERIFY] Who actually led the Bai village; whether Bai Ning Bing is acceptable as its face. Bai Ning Bing's gift may be a special physique, not a clan trait, so civilopedia avoids 'lineage'. Bai's path tradition is unknown; leaning Moon is a balance choice.* | Gifted youths: A-grade aptitude about twice as likely (weights on Aptitude Awakening) and A-grade units +15%. A bet on luck (P2). AI leans Moon and Righteous.<br>*Fields:* leaderName Bai Ning Bing (ADAPTED: a genius, not the clan head); personality 'Bai Temperament' (gold 7, production 6, science 6; priorities Moon Path 8, Righteous Path 7; '[+50]% weight to [Gu Academy] for AI decisions', '[+100]% weight to [Awakening Grounds] for AI decisions'); cities Bai Village + invented; colours [230,230,230]/[40,70,120] | `[+15]% Strength <for units with [Aptitude A]>`<br>`Start bias [Plains]`<br>Personality: `[+50]% weight to [Gu Academy] for AI decisions`<br>Personality: `[+100]% weight to [Awakening Grounds] for AI decisions` |
| Xiong Clan | 熊家 | CANON **[VERIFY]** | The third Qing Mao village, whose Gu Masters favour raw bear-like strength.<br>*[VERIFY] Leader name Xiong Lin; the strength-path tradition is inferred from the clan name (熊, bear).* | Starts already on the Strength Path, so the AI is a committed specialist from turn 1 (P4). +15% against beasts turns tides into XP (P3, P2).<br>*Fields:* leaderName Xiong Lin; personality 'Xiong Temperament' (military 7, aggressive 6, production 6; priorities Strength Path 10, Righteous Path 5, Demonic Path 3; '[+50]% weight to [Formation Platform] for AI decisions', '[+100]% weight to [Awakening Grounds] for AI decisions'); cities Xiong Village + invented; colours [90,50,20]/[240,200,140] | `Starts with [Strength Path] adopted`<br>`[+15]% Strength <vs [Barbarians] units>`<br>`Start bias [Forest]`<br>Personality: `[+50]% weight to [Formation Platform] for AI decisions`<br>Personality: `[+100]% weight to [Awakening Grounds] for AI decisions` |
| Rogue Cultivators | 散修 | ADAPTED **[VERIFY]** | Fang Yuan, reborn into his youth by Spring Autumn Cicada, schemes alone for eternal life.<br>*[VERIFY] Fang Yuan heading a separate rogue faction is an adaptation (on Qing Mao he belongs to the Gu Yue clan). Heaven's Will as the source of his calamities is beyond §5 and a possible spoiler, so player-facing text says 'ill fortune'.* | S6 rogue-cultivator strategy plus S8 foreknowledge: +15% science; one unit eats free (an elite core); stays small (+50% unhappiness from the number of cities). Ill fortune follows him: extra Beast Tides (2% per turn after T20) (P1, P3, P5). AI leans Demonic and Strength.<br>*Fields:* leaderName Fang Yuan (方源); personality 'Rogue Temperament' (military 7, aggressive 7, expansion 3, loyal 0; priorities Strength Path 12, Demonic Path 10; '[+50]% weight to [Refinement Chamber] for AI decisions', '[+50]% weight to [Wine Cellar] for AI decisions'); cities invented hideouts; colours [20,20,20]/[200,30,30] | `[+15]% [Science]`<br>`[1] units cost no maintenance`<br>`[+50]% unhappiness from the number of cities`<br>`Triggers a [Beast Tide] event <upon turn start> <after turn number [20]> <with [2]% chance>`<br>Personality: `[+50]% weight to [Refinement Chamber] for AI decisions`<br>Personality: `[+50]% weight to [Wine Cellar] for AI decisions`<br>Personality: `[+100]% weight to [Awakening Grounds] for AI decisions` |
| Barbarians | 兽群 | ADAPTED | The beast groups of the wild, their kings and their lairs. | The name is required by the engine: without it barbarians never spawn. It owns every beast, tide rebel and traitor (P3). Display text 'Beast Groups' comes later through English.properties.<br>*Fields:* name must stay 'Barbarians'; colours [0,0,0]/[185,12,12] | `Can only heal by pillaging`<br>`Excluded from map editor` |
| Spectator | — | INVENTED | Not lore. | Engine infrastructure for the spectator slot and autoplay, copied from Vanilla.<br>*Fields:* outerColor [255,255,255] | Vanilla, verbatim |

### City-states

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Hairy Man Tribe | 毛民 | ADAPTED **[VERIFY]** | Shaggy variant humans famed as Gu refiners.<br>*[VERIFY] Hairy men are anchored; their presence in the Southern Border is not.* | CityStateType 'Refiner Tribe'. Friend: +2 Science in the capital. Ally: +2 Science and +20% combat XP, so more refinements (P2).<br>*Fields:* friendBonusUniques = unique 1; allyBonusUniques = uniques 2-3; type colour [180,120,60] | Friend: `[+2 Science] [in capital]`<br>Ally: `[+2 Science] [in capital]`<br>Ally: `[+20]% XP gained from combat` |
| Stone Man Tribe | 石人 | ADAPTED **[VERIFY]** | Variant humans whose bodies are as hard as rock.<br>*[VERIFY] Stone men are anchored; their Southern Border location is not.* | CityStateType 'Stone Tribe'. Friend: +2 Production in the capital. Ally: +2 Production and +20% city strength against tides (P3).<br>*Fields:* friendBonusUniques = unique 1; allyBonusUniques = uniques 2-3; type colour [130,130,130] | Friend: `[+2 Production] [in capital]`<br>Ally: `[+2 Production] [in capital]`<br>Ally: `[+20]% Strength for cities` |
| Jia Clan | 贾家 | ADAPTED **[VERIFY]** | A merchant clan whose caravans called at Qing Mao Mountain.<br>*[VERIFY] The Jia clan caravan (Jia Fu) at Qing Mao is from memory; a merchant clan as a city-state is an adaptation.* | CityStateType 'Merchant Clan'. Friend: +2 stones in the capital. Ally: +3 stones and +10% stones. The stone ally, and gifts to it are a stone sink (P1, P5).<br>*Fields:* friendBonusUniques = unique 1; allyBonusUniques = uniques 2-3; type colour [255,216,0] | Friend: `[+2 Gold] [in capital]`<br>Ally: `[+3 Gold] [in capital]`<br>Ally: `[+10]% [Gold]` |

### Victories

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Southern Border Supremacy | — | ADAPTED | Southern Border clans swallow one another; the last unconquered capital rules the mountains. | Domination victory; named to pair with Slice 3's Five Regions Supremacy (P5: violence pays).<br>*Fields:* milestones ['Capture all capitals'] | Milestone: `Capture all capitals` |
| Endurance | — | INVENTED | When time runs out, the strongest clan is remembered. | Score fallback at max turns; recommend max turns 150 for Slice 1 tests.<br>*Fields:* milestones ['Have highest score after max turns']. Cosmetic caveat: the victory screen shows 'Max Turns' only for a victory literally named 'Time' [src VictoryScreen.kt:144]; the new-game slider works with any name | Milestone: `Have highest score after max turns` |

### Ruin rewards (Inheritances)

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| Primeval Stone Cache | — | ADAPTED | A dead Gu Master's hidden stash of stones. | +30-60 stones (P1).<br>*Fields:* weight 4; notification 'We found [goldAmount] primeval stones in a dead Gu Master's cache!' | `Gain [30]-[60] [Gold]` |
| Cultivation Notes | — | ADAPTED | A dead master's notes on his own cultivation. | +15-30 science.<br>*Fields:* weight 3 | `Gain [15]-[30] [Science]` |
| Unfinished Refinement | — | ADAPTED | A refinement abandoned halfway, its materials still warm. | The entering Gu Master (not a beast) gets a free Refinement Attempt; reuses the event, so no extra event budget (E2, P2).<br>*Fields:* weight 3 | `Triggers a [Refinement Attempt] event`<br>`Only available <for [Military] units>`<br>`Unavailable <for [Beast] units>` |
| Inheritance Trial | — | ADAPTED **[VERIFY]** | Inheritances test their heirs and hurt the unworthy.<br>*[VERIFY] See Inheritance Lore.* | +30 XP (about two refinements) paid for with 40 damage; not for beasts (P2, P3).<br>*Fields:* weight 2; a multi-unique reward repeats its notification (docs) | `[This Unit] gains [30] XP`<br>`[This Unit] takes [40] damage`<br>`Only available <for [Military] units>`<br>`Unavailable <for [Beast] units>` |
| Inheritance Trap | — | ADAPTED **[VERIFY]** | Many inheritances guard themselves with lethal traps.<br>*[VERIFY] See Inheritance Lore.* | 40 damage to the entering unit (P3).<br>*Fields:* weight 1 | `[This Unit] takes [40] damage`<br>`Only available <for [Military] units> <after turn number [10]>` |
| Wandering Rogue Cultivator | — | ADAPTED | A rogue cultivator sheltering in the ruins joins the clan. | A free Rank One Gu Master: it rolls aptitude and is another mouth to feed (P1, P2).<br>*Fields:* weight 1 | `Free [Rank One Gu Master] found in the ruins` |

### Global files and difficulties

| Object | 中文 | Status | Lore basis | Mechanical role · key fields | Uniques |
|---|---|---|---|---|---|
| GlobalUniques | — | ADAPTED | Heaven and earth are without benevolence. | Lines 1-6: Vanilla's unhappiness effects, which a base ruleset only has if it declares them (settler target retargeted). Line 7: every Gu of a major civ eats; the engine otherwise exempts the 3 MOST expensive units, which would erase rank multipliers (city-states keep the 3 free units). Line 8: starvation tier 2 (tier 1 is a missing Gu food at -25%, tier 3 the engine's disband at -200). Lines 9-13: tide, betrayal and shortage triggers for majors only. All automatic for the AI (P1, P3, P5).<br>*Fields:* jsons/GlobalUniques.json 'uniques'; no unitUniques in Slice 1 | `[-75]% growth [in all cities] <when between [-10] and [-1] [Happiness]>`<br>`Nullifies Growth [in all cities] <when below [-10] [Happiness]>`<br>`[-50]% [Production] [in all cities] <when below [-10] [Happiness]>`<br>`[-33]% Strength <for [All] units> <when below [-10] [Happiness]>`<br>`Cannot build [Clan Settler] units <when below [-10] [Happiness]>`<br>`Rebel units may spawn <when below [-20] [Happiness]>`<br>`[-3] units cost no maintenance <for [Major] Civilizations>`<br>`[-20]% Strength <when below [0] [Gold]>`<br>`Triggers a [Beast Tide] event <upon turn start> <after turn number [30]> <with [3]% chance> <for [Major] Civilizations>`<br>`Triggers a [Beast Tide] event <upon turn start> <after turn number [90]> <with [2]% chance> <for [Major] Civilizations>`<br>`Triggers a [Betrayal] event <upon turn start> <when below [0] [Happiness]> <with [8]% chance> <for [Major] Civilizations>`<br>`Triggers a [Betrayal] event <upon turn start> <when above [300] [Gold]> <with [3]% chance> <for [Major] Civilizations>`<br>`Triggers a [Stone Shortage] event <upon turn start> <when below [0] [Gold]> <when number of [[Gold] Per Turn] is less than [0]> <with [25]% chance> <for [Major] Civilizations>` |
| ModOptions | — | INVENTED | Not lore. | Base ruleset; religion off (§7); starts only in the first era, so no later-era starting kits are needed. The beast XP cap is raised from 30 to 90 so beasts can fund several refinements (10+20+30 XP) (P2, P3).<br>*Fields:* isBaseRuleset true; constants.maxXPfromBarbarians 90 (a cap on totalXpProduced [src Battle.kt:607]); Beliefs.json and Religions.json empty | `Disable religion`<br>`Can only start games from the starting era` |
| UnitTypes, Personalities and Speeds | — | INVENTED | Not lore. | Unit types: Civilian, Gu Master (unpathed Rank One), Moon Gu Master, Strength Gu Master, Beast, all movementType Land. They drive promotion pools, path filters and dao marks. There are no water units, so naval barbarians never spawn: recommend Pangaea or Continents maps. Personalities are named '<Clan> Temperament' because mod-ci flags a nation and a personality sharing a name. Speeds: the four Vanilla speeds as strict JSON.<br>*Fields:* 4 personalities (listed on the nations); 3 CityStateTypes (Refiner Tribe, Stone Tribe, Merchant Clan) | personality uniques: see each nation |
| Difficulties (Vanilla 8 levels) | — | INVENTED | Not lore: carrying-capacity and AI-solvency knobs. | Keeps the Vanilla Settler..Deity values for now; the level names are a taste question. Remaps: bonus units Settler -> Clan Settler, Worker -> Mortal Laborer, Scout -> Rank One Gu Master (mod-ci rejects 'Settler'/'Worker' even though GameStarter maps them at runtime); aiFreeTechs Pottery -> Primeval Stone Mining, Animal Husbandry -> Gu Feeding, Mining -> Wine Brewing, The Wheel -> Gu Refinement. aiUnitMaintenanceModifier stays Vanilla: 1.0 up to Prince, falling to 0.5 at Deity (P1, AI).<br>*Fields:* tune unitSupplyBase/unitSupplyPerCity and aiUnitMaintenanceModifier/aiBuildingMaintenanceModifier in docs/BALANCE.md after the autoplay; clearBarbarianCampReward is the lair bounty | Vanilla, verbatim |


---

## Refinement ladder

Refine Gu opens the Refinement Attempt Alert on the unit. Choices 1 (careful) and 2 (reckless) carry the same ladder
with different odds (85% / 50%); each unit state matches **at most one** ladder line, so one attempt rolls once and
climbs at most one rung (E5; lines fire top to bottom and promotion conditionals are read live [src]).

| Unit | Rung 1 | Rung 2 | Rung 3 |
|---|---|---|---|
| Moon Gu Master | Moonlight Gu (only while Moon Orchid is in surplus) | White Jade Gu | Killer Move (after the Killer Moves tech) |
| Strength Gu Master | Black Boar Gu (only while Wild Boar is in surplus) | White Jade Gu | Killer Move (after Killer Moves) |
| Strength Gu Master that kept a Moonlight Gu from Gu Yue | — | White Jade Gu | Killer Move (after Killer Moves) |
| Rank One Gu Master (unpathed, any clan) | White Jade Gu: the cap | — | — |

**Dead states.** In these states no ladder line can fire, so the careful and reckless choices are closed and Refine
Gu cannot be bought (each is one `Unavailable` line, generated from one list):

1. the unit already has Killer Move;
2. an unpathed Gu Master that already has White Jade Gu;
3. White Jade Gu plus Moonlight Gu, or White Jade Gu plus Black Boar Gu, before the Killer Moves tech;
4. a Moon Gu Master without Moonlight Gu while Moon Orchid is not in surplus;
5. a Strength Gu Master without Black Boar Gu or Moonlight Gu while Wild Boar is not in surplus.

Refine Gu is also closed below 50 HP; the reckless choice closes below 31 HP (relevant only through the ruin). So
whenever the Alert opens through the promotion, at least one choice can grant a rung.

---

## Events in detail

AI weight = product of the choice's `[relativeAmount]% weight to this choice for AI decisions` uniques (E1). The
percentages assume every choice is open; closed choices drop out and the rest are renormalised.

### Aptitude Awakening

Presentation **None**. Fired by every Gu Master unit's own unique when the unit is created (E3). Pure die: the odds are the weights.

**1. Grade A aptitude** — AI weight 0.05, 5% when every choice is open and no conditional weight applies; conditional weights: `[+100]% weight to this choice for AI decisions <if [Awakening Grounds] is constructed>`; `[+100]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>`

```
[This Unit] gains the [Aptitude A] promotion
```

**2. Grade B aptitude** — AI weight 0.2, 20% when every choice is open and no conditional weight applies; conditional weights: `[+50]% weight to this choice for AI decisions <if [Awakening Grounds] is constructed>`; `[+25]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>`

```
[This Unit] gains the [Aptitude B] promotion
```

**3. Grade C aptitude** — AI weight 0.35, 35% when every choice is open and no conditional weight applies

```
[This Unit] gains the [Aptitude C] promotion
```

**4. Grade D aptitude** — AI weight 0.4, 40% when every choice is open and no conditional weight applies; conditional weights: `[-25]% weight to this choice for AI decisions <if [Awakening Grounds] is constructed>`

```
[This Unit] gains the [Aptitude D] promotion
```

### Refinement Attempt

Presentation **Alert**. Fired by the Refine Gu promotion on purchase, or by the Unfinished Refinement ruin, with the unit as context (E2). Popup text: *The furnace is lit. How far will you risk it?*

**1. Refine carefully** — AI weight 1.5, 42% when every choice is open and no conditional weight applies; conditional weights: `[-60]% weight to this choice for AI decisions <when below [150] [Gold]>`

```
Only available <if [Refinement Chamber] is constructed> <when above [80] [Gold]>
Unavailable <when below [140] [Gold]> <during the [Rank Three era]>
Unavailable <when below [200] [Gold]> <during the [Rank Four era]>
Gain [-40] [Gold] <during the [Rank One-Two era]>
Gain [-70] [Gold] <during the [Rank Three era]>
Gain [-100] [Gold] <during the [Rank Four era]>
Unavailable <for units with [Killer Move]>
Unavailable <for [Gu Master] units> <for units with [White Jade Gu]>
Unavailable <for units with [White Jade Gu]> <for units with [Moonlight Gu]> <before discovering [Killer Moves]>
Unavailable <for units with [White Jade Gu]> <for units with [Black Boar Gu]> <before discovering [Killer Moves]>
Unavailable <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <when below [1] [Moon Orchid]>
Unavailable <for [Strength Gu Master] units> <for units without [Black Boar Gu]> <for units without [Moonlight Gu]> <when below [1] [Wild Boar]>
[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units with [Moonlight Gu]> <after discovering [Killer Moves]> <with [85]% chance>
[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units with [Black Boar Gu]> <after discovering [Killer Moves]> <with [85]% chance>
[This Unit] gains the [White Jade Gu] promotion <for units with [Moonlight Gu]> <for units without [White Jade Gu]> <with [85]% chance>
[This Unit] gains the [White Jade Gu] promotion <for units with [Black Boar Gu]> <for units without [White Jade Gu]> <with [85]% chance>
[This Unit] gains the [Moonlight Gu] promotion <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <when above [0] [Moon Orchid]> <with [85]% chance>
[This Unit] gains the [Black Boar Gu] promotion <for [Strength Gu Master] units> <for units without [Black Boar Gu]> <for units without [Moonlight Gu]> <when above [0] [Wild Boar]> <with [85]% chance>
[This Unit] gains the [White Jade Gu] promotion <for [Gu Master] units> <for units without [White Jade Gu]> <for units without [Moonlight Gu]> <with [85]% chance>
```

**2. Refine recklessly** — AI weight 1, 28% when every choice is open and no conditional weight applies; conditional weights: `[-90]% weight to this choice for AI decisions <when below [50] HP>`

```
Unavailable <for units with [Killer Move]>
Unavailable <for [Gu Master] units> <for units with [White Jade Gu]>
Unavailable <for units with [White Jade Gu]> <for units with [Moonlight Gu]> <before discovering [Killer Moves]>
Unavailable <for units with [White Jade Gu]> <for units with [Black Boar Gu]> <before discovering [Killer Moves]>
Unavailable <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <when below [1] [Moon Orchid]>
Unavailable <for [Strength Gu Master] units> <for units without [Black Boar Gu]> <for units without [Moonlight Gu]> <when below [1] [Wild Boar]>
Unavailable <when below [31] HP>
[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units with [Moonlight Gu]> <after discovering [Killer Moves]> <with [50]% chance>
[This Unit] gains the [Killer Move] promotion <for units with [White Jade Gu]> <for units with [Black Boar Gu]> <after discovering [Killer Moves]> <with [50]% chance>
[This Unit] gains the [White Jade Gu] promotion <for units with [Moonlight Gu]> <for units without [White Jade Gu]> <with [50]% chance>
[This Unit] gains the [White Jade Gu] promotion <for units with [Black Boar Gu]> <for units without [White Jade Gu]> <with [50]% chance>
[This Unit] gains the [Moonlight Gu] promotion <for [Moon Gu Master] units> <for units without [Moonlight Gu]> <when above [0] [Moon Orchid]> <with [50]% chance>
[This Unit] gains the [Black Boar Gu] promotion <for [Strength Gu Master] units> <for units without [Black Boar Gu]> <for units without [Moonlight Gu]> <when above [0] [Wild Boar]> <with [50]% chance>
[This Unit] gains the [White Jade Gu] promotion <for [Gu Master] units> <for units without [White Jade Gu]> <for units without [Moonlight Gu]> <with [50]% chance>
[This Unit] takes [30] damage
```

**3. Lure a wild Liquor Worm with wine** — AI weight 1, 28% when every choice is open and no conditional weight applies

```
Only available <for units without [Liquor Worm]> <when above [0] [Wine]> <when above [20] [Gold]>
Unavailable <for [Beast] units>
Gain [-20] [Gold]
[This Unit] gains the [Liquor Worm] promotion <with [70]% chance>
```

**4. Let the furnace cool** — AI weight 0.05, 1% when every choice is open and no conditional weight applies

```
[This Unit] gains [5] XP
```

### Beast Tide

Presentation **Alert**. Fired by GlobalUniques (majors) and by the Rogue Cultivators' nation unique. Popup text: *A beast tide pours down the mountain toward your villages.*

**1. Meet the tide in the field** — AI weight 1, 24% when every choice is open and no conditional weight applies

```
[2] [Electric Wolf]s rebel <during the [Rank One-Two era]>
[3] [Electric Wolf]s rebel <starting from the [Rank Three era]>
A [Electric Wolf King] rebels <starting from the [Rank Three era]>
A [Thunder Crown Wolf] rebels <during the [Rank Four era]>
```

**2. Pay rogue cultivators to thin the pack** — AI weight 1, 24% when every choice is open and no conditional weight applies

```
Only available <when above [60] [Gold]>
Unavailable <when below [100] [Gold]> <during the [Rank Three era]>
Unavailable <when below [150] [Gold]> <during the [Rank Four era]>
Gain [-60] [Gold] <during the [Rank One-Two era]>
Gain [-100] [Gold] <during the [Rank Three era]>
Gain [-150] [Gold] <during the [Rank Four era]>
```

**3. Abandon the outer fields** — AI weight 0.7, 17% when every choice is open and no conditional weight applies

```
[-1] population [in all cities]
```

**4. Raise the formation** — AI weight 1.5, 36% when every choice is open and no conditional weight applies

```
Only available <if [Formation Platform] is constructed> <when above [70] [Gold]>
Gain [-40] [Gold] <during the [Rank Three era]>
Gain [-70] [Gold] <during the [Rank Four era]>
[-20]% [Production] <for [5] turns>
```

### Betrayal

Presentation **Alert**. Fired by GlobalUniques (unhappy or rich majors), by the Demonic Path opener and by Stone Shortage choice 4. Popup text: *A clan member has sold you out and fled with stones and Gu.*

**1. Let the traitor go** — AI weight 1, 17% when every choice is open and no conditional weight applies

```
Only available <when above [60] [Gold]>
Gain [-60] [Gold]
```

**2. Hunt the traitor down** — AI weight 1, 17% when every choice is open and no conditional weight applies

```
A [Rank Two Strength Gu Master] rebels <after adopting [Strength Path]>
A [Rank Two Moon Gu Master] rebels <after adopting [Moon Path]>
A [Rank One Gu Master] rebels <before adopting [Strength Path]> <before adopting [Moon Path]>
```

**3. Judge the traitor by clan law** — AI weight 2, 33% when every choice is open and no conditional weight applies

```
Only available <after adopting [Righteous Path]>
[-1] population [in capital]
[+2 Happiness] <for [10] turns>
```

**4. Strike first and take the traitor's Gu** — AI weight 2, 33% when every choice is open and no conditional weight applies

```
Only available <after adopting [Demonic Path]>
Gain [40] [Gold]
[-1] population [in capital]
[-3 Happiness] <for [10] turns>
```

### Stone Shortage

Presentation **Alert**. Fired by GlobalUniques while stones < 0 and income < 0 (majors). Popup text: *The stone vaults are empty and the Gu are going hungry.*

**1. Ration the Gu feed** — AI weight 2, 44% when every choice is open and no conditional weight applies

```
[-40]% maintenance costs <for [8] turns>
[-15]% Strength <for [8] turns>
```

**2. Borrow from the merchant caravans** — AI weight 0.2, 4% when every choice is open and no conditional weight applies

```
Only available <when above [-100] [Gold]>
Gain [80] [Gold]
[-6 Gold] <for [20] turns>
```

**3. Squeeze the mortals** — AI weight 0.8, 18% when every choice is open and no conditional weight applies

```
Gain [50] [Gold]
[-1] population [in capital]
```

**4. Rob a passing caravan** — AI weight 1.5, 33% when every choice is open and no conditional weight applies

```
Only available <after adopting [Demonic Path]>
Gain [70] [Gold]
Triggers a [Betrayal] event <with [25]% chance>
```


---

## Balance starting numbers

These are starting points for Phase 2; every tunable number goes into `docs/BALANCE.md` once JSON exists, and the
100-turn autoplay (MOD_SPEC §10, §11) decides.

**Unit upkeep in stones per turn**, from the engine formula [src `getUnitMaintenance`]: cost = (0.5 × Σ unit
weights × (1+p))^(1+p/3), p = turn / 500 on standard speed; weights multiply (+100% = ×2). Majors pay for every unit.

| Situation | Synthesized plan | After the review (this plan) |
|---|---|---|
| T40, careful Moon player: 2 laborers, 3 Rank One, 1 Rank Two Moon with White Jade | 5 | 4 |
| T40, careless: 2 laborers, 5 Rank Two Strength | 8 | 6 |
| T80, Xiong AI: 2 laborers, 2 Rank Three + 3 Rank Two Strength, 2 Rank One (all with White Jade), 2 recruited wolves | 17 | 14 |
| T120, 2 laborers + 6 elite Rank Four Strength (White Jade + Killer Move) | 38 | 28 |
| T120, 2 laborers + 6 elite Rank Four Moon (White Jade + Killer Move) | 30 | 24 |

The mechanics review found that the synthesized multipliers plus 1 stone per building and per road tile put a
careful player's upkeep at 70–95% of gross stones around T40, far above the ~40% starting target (§10). This plan
lowers the multipliers and raises Clan Hall gold from 4 to 5. Early on, unit upkeep is small (4–6 stones);
buildings and roads dominate, and the Gu foods carry most of the early P1 pressure. Expect the autoplay to move
these numbers.

**Event costs never push a non-negative treasury below zero:** every stone-costing choice is gated by a
`<when above [amount] [stat/resource]>` at or above its cost.

**Known limits, accepted for Slice 1 and watched in autoplay:**

1. Gaining a Gu does not refresh the civ's resource count [src], so several units refining in the same turn can
   each take "the last" orchid or boar and push the food into deficit (−25% for its holders until fixed).
2. Population loss stops at 1 [src]: "Abandon the outer fields" is free for size-1 colonies. Single-city costs use
   the capital (`[-1] population [in capital]`) because a civ-level "random city" always picks the same city [src].
3. With barbarians disabled, "Meet the tide" and "Hunt the traitor" summon nothing, so they cost nothing.
4. Ration can stack if Stone Shortage fires again during its 8 turns (upkeep ×0.6 per stack, −15% strength each).
5. The three Betrayal triggers are independent and can fire in the same turn.
6. Culture has no sink once both allowed branches are complete; later slices add branches.
7. Reloading a save rerolls every chance roll (E5).
8. The victory screen shows "Max Turns" only for a victory named "Time" (cosmetic) [src].

## Engine facts this plan relies on

Each needs an in-game check in the Phase 2 step report (console commands in `docs/TESTING.md`).

| Fact | Source | Check in game |
|---|---|---|
| E1: a None event picks one choice by weighted random; AI civs resolve Alerts the same way | [src] `Event.kt` | create ~20 Gu Masters, count grades |
| E2: an event triggered from a promotion or ruin keeps the unit as context | [src] `getTriggerFunction` | Refine Gu grants the rung to that unit |
| E3: a unit's triggerable without trigger conditional fires once at creation | [src] `UnitManager.placeUnitNearTile` | `unit add` a Rank One, see the grade |
| E4 (corrected): the AI never buys a "Doing so will consume…" promotion; a kept promotion with `<upon turn start>` self-removal is re-buyable at a rising XP price | [src] `NextTurnAutomation.applyPromotions`, `UnitPromotions` | `unit setxp`, buy Refine Gu, end turn, buy again; spectate an AI |
| Choice uniques fire in list order and promotion conditionals are read live (one rung per attempt) | [src] `Event.triggerChoice` | a unit with no Gu gains exactly one |
| Rebels ignore `Never appears as a Barbarian unit` and `Unbuildable`, spawn by the civ's first city, and are skipped without barbarians | [src] `UniqueTriggerActivation` | `civ activatetrigger "Triggers a [Beast Tide] event"` |
| Barbarians know only techs every civ knows (gates the Electric Wolf King) | [src] `BarbarianManager` | spectate past Rank Three Cultivation |
| A consumed luxury still gives happiness once its net is negative, so Gu foods must be Strategic | [src] `CivInfoTransientCache` | — (design rule) |
| Ranged attackers never capture or recruit | [src] `BattleUnitCapture` | kill a wolf with a Moon unit after Beast Enslavement |

## What the reviews changed

Two independent reviews (a lore skeptic and a mechanics skeptic) checked the synthesized plan.

* **Refinement (mechanics, must-fix ×3):** dead ladder states let the AI pay XP and stones for attempts that could
  not succeed; a Gu Yue Rank One rolled twice for White Jade Gu; the ladder ignored Gu food. Fixed with the
  dead-state `Unavailable` list, one ladder line per state, food gates, and a 50 HP gate on Refine Gu.
* **Balance:** lower rank multipliers, Clan Hall gold 5; the three free units removed for majors only
  (city-states keep their free units); paying rogue cultivators now clears the whole tide (it no longer loses to the
  formation choice); Beast Enslavement recruits only while stone income is above +4; the cooling choice is nearly
  never picked by the AI; reckless refinement cannot kill a unit below 31 HP; beasts cannot use refinement ruins.
* **Population costs** land on the capital instead of a fixed "random" city; clan law gives happiness instead of
  late-useless culture.
* **Lore (must-fix ×3):** Strength Path is ADAPTED + [VERIFY]; essence colours appear only on the era rows, flagged;
  the "Hope Gu Altar" became the neutral "Awakening Grounds" + [VERIFY].
* **Lore (should-fix):** CANON → ADAPTED for the aptitude event, both alignment branches and the two variant-human
  city-states; "famed" (not "finest") refiners; [VERIFY] on Fang Yuan's faction, inheritances and the stone mine;
  "Heaven's Will" kept out of player text; Chinese terms removed from invented objects and kept once per term.
* **Corrected claims:** E4 (see above; fixed in `docs/CAPABILITIES.md`), and "chance rolls cannot be rerolled by
  reloading" is false (E5). The mountain-damage claim was dropped: Mountain is impassable, so it never fires.

## Roadmap after Slice 1

* **Slice 2 (Ascension):** rank 5, ascension through a kept, self-removing "Attempt Ascension" promotion (E4 route B),
  Blessed Lands, Heavenly Tribulations, immortal essence stones, desolate beasts, Spring Autumn Cicada (S8).
* **Slice 3 (Five Regions):** the region-wall map, the other regions' factions, hostile terrain (S4), the Heavenly
  Court, the Eternal Life victory.
* **Paths:** the later candidates listed under [Path choice](#path-choice-why-two-paths-and-which).
