# Paths (流派) — MOD_SPEC_3 Phase B3

State on 2026-10-18: the list is **approved** with the user's decisions below. No content JSON ships yet: the C3
migration plan at the end waits for approval (⛔); then C3 turns this document into `data/paths.csv` +
`tools/gen_paths.py`.

## How this was checked

* **Sources.** R = the raw Chinese text, cited by global chapter number (R ch*N*, the numbering of the fan wiki's
  citations) or as R V*v*/*n* (volume *v*, chapter *n* of that volume); the copy used is an unofficial upload, so it is never linked from the mod. F = the Reverend Insanity
  fan wiki (`reverend-insanity.fandom.com/wiki/<page>`), whose English names (a fan translation) are used here.
  Verdict rule: CANON = the name and its Chinese are attested in R **and** described on F. The research was done by
  subagents against R and F; only the verdicts are kept here (CLAUDE.md).
* **Attestation.** Every `X道` followed by a path marker (道痕, 蛊仙, 蛊师, 杀招, 仙蛊, 凡蛊, 境界, 流派, 宗师 /
  大宗师) was counted over the whole of R; the 47 paths below are everything that came out, plus the minor paths R
  names in prose. The best single passage is R ch1323 (the major paths by era and founder).
* **Every unique proposed here was run through the real checkers.** A throwaway prototype (the shipped `jsons/` plus
  all 47 lines: 188 tier promotions, 94 move statuses, 5 signature statuses, a stand-in essence stockpile; 306
  promotions, 1,024 conflict lines) passes `tools/check_all --mod <prototype> --no-self-test`: `lint_uniques` 2,726
  uniques, 0 errors, 0 warnings; Unciv 4.22.8's own validator 0 lines; the only warnings are missing icons.
  Autoplay on the prototype (6 games × 150 turns, Prince): 0 crashes, and the four AI clans held 258 path
  promotions, **258 on their main path** under the draft's lock (the 46-line draft gave 264 of 264); the lock was
  then replaced by signature leanings (see "AI"). The draft (`tools/b3/`) became `data/paths*.csv` and
  `tools/gen_paths.py` in C3 (M2), which writes the tables below and the path promotions; the draft was then removed.
* What the prototype does **not** prove (C3 capability tests, one object each): the effects in battle of the
  signatures marked ⚠️ below, the move buttons, and how the promotion screen copes with 42 root lines.

## Decisions (user, 2026-10-18)

1. **Killing path 杀道 is in** (47 lines). R shows only "signs" of its founding in the last chapters (ch2233,
   ch2328) while F calls it founded; the user decided, so its verdict reads ADAPTED (user).
2. **Sub-paths are their own lines** (phantom and restriction from rule, emotion and enchantment from wisdom, shadow
   from dark): a sub-path's Master needs the parent's Master (R ch1869: phantom attainment counts as rule path), and
   it does not clash with its parent.
3. **Four tiers** (MOD_SPEC_3's names): Master at any rank, Grandmaster rank 3+, Great Grandmaster rank 6+, Supreme
   Grandmaster rank 8+. Canon puts each tier one to two ranks higher (ADAPTED).
4. **Transformation without `Can transform to [unit]`** (a beast form per rank would be 9 more units, over the
   Gu-unit budget): `Double movement in [Forest]`.
5. **Fire burns the land**: `Destroys tile improvements when attacking`, Spirit Spring caves included.
6. **Bai's signature path is Water** (F: the Bai clan specialises in water and ice; its emblem is the Stream Gu).
7. **Wu's signature path is Wind** (the user's decision D3, 2026-10-19; the Wu clan is best at the wind path, R V6c130).

## The paths

Signature = the whole unique text, conditional included; no two paths share one (`tools/gen_paths.py` asserts it). Every
pattern is documented in `uniques.md` 4.22.8; those from MOD_SPEC_3's palette are noted in "Signature notes".

<!-- paths:start (tools/gen_paths.py) -->
| # | Path | Chinese | Family | Sub-path of | Source | Verdict | Signature (one unique) | Lore hook |
|---|---|---|---|---|---|---|---|---|
| 1 | Strength | 力道 | A |  | F Strength_Path; R ch597, 1064 | CANON | `No damage penalty for wounded units` | a tempered body keeps its force while hurt |
| 2 | Transformation | 变化道 | A |  | F Transformation_Path; R ch597, 1041 | CANON | `Double movement in [Forest]` | beast forms run where beasts run |
| 3 | Bone | 骨道 | A |  | F Bone_Path; R ch1736 | CANON | `[+20]% Strength <when defending>` | bone armour grown from one's own skeleton |
| 4 | Blood | 血道 | A |  | F Blood_Path; R ch1064, 2080 | CANON | `Heals [20] damage if it kills a unit` | blood taken from the slain feeds the killer |
| 5 | Sword | 剑道 | B |  | F Sword_Path; R ch1064 | CANON | `[+25]% Strength <when attacking>` | focused piercing, one of the five strongest attack paths |
| 6 | Blade | 刀道 | B |  | F Blade_Path; R ch1432 | CANON | `[+50]% to Flank Attack bonuses` | sweeping blade-qi cuts the flanks |
| 7 | Metal | 金道 | B |  | F Metal_Path; R ch1064 | CANON | `[+30]% Strength <vs cities>` | metal breaks walls |
| 8 | Weapon | 兵道 | B |  | F Weapon_Path; R ch2154 | CANON | `[+20]% Strength <when adjacent to a [Military] unit>` | a path for armies, built on human-path ideas |
| 9 | Killing | 杀道 | B |  | F Killing_Path; R ch1014, 2233, 2328 | ADAPTED (user, 2026-10-18) | `[This Unit] gains [1] movement <upon defeating a [Military] unit>` | slaughter feeds the next kill |
| 10 | Fire | 炎道 | C |  | F Fire_Path; R ch1064, 1323 | CANON | `Destroys tile improvements when attacking` | fire burns the fields it fights over |
| 11 | Water | 水道 | C |  | F Water_Path; R ch1323 | CANON | `May travel on Water tiles without embarking` | water carries its own |
| 12 | Wood | 木道 | C |  | F Wood_Path; R ch1323 | CANON | `[15] HP when healing` | wood mends what grows |
| 13 | Earth | 土道 | C |  | F Earth_Path; R ch1323, 1425 | CANON | `[+25]% Strength <when fighting in [Hill] tiles>` | rock and soil hold the high ground |
| 14 | Wind | 风道 | C |  | F Wind_Path; R ch1323 | CANON | `[1] Movement` | air currents and flight |
| 15 | Cloud | 云道 | C |  | F Cloud_Path; R ch752 | CANON | `Ignores terrain cost` | clouds carry the walker over any ground |
| 16 | Ice Snow | 冰雪道 | C |  | F Ice_Path, Snow_Path; R ch1323 | CANON | `[Target Unit] loses [1] movement <upon damaging a [Military] unit>` | cold that numbs and slows |
| 17 | Lightning | 雷道 | C |  | F Lightning_Path; R ch1064 | CANON | `[+30]% Strength <when above [1] movement>` | the first strike, before the thunder |
| 18 | Poison | 毒道 | C |  | F Poison_Path; R ch1293 | CANON | `[Target Unit] gains the [Poisoned] status for [3] turn(s) <upon damaging a [Military] unit>` | hidden venom that keeps working |
| 19 | Light | 光道 | D |  | F Light_Path; R ch1323 | CANON | `Can move after attacking` | light is speed |
| 20 | Dark | 暗道 | D |  | F Dark_Path; R ch1323 | CANON | `Invisible to others` | darkness hides auras and moves |
| 21 | Shadow | 影道 | D | Dark | F Shadow_Path; R ch2284 | CANON | `[+30]% Strength <vs [Wounded] units>` | a dark-path offshoot that strikes the weakened |
| 22 | Star | 星道 | D |  | F Star_Path; R ch1323, 2204 | CANON | `[2] Sight` | conjured stars light the field |
| 23 | Moon | 月道 | D |  | F Moon_Path; R ch795, 2169 | CANON | `Before engaging in combat performs an extra ranged attack with [40]% of melee combat strength` | a crescent blade of moonlight strikes before the clash |
| 24 | Sound | 音道 | D |  | F Sound_Path; R ch1425 | CANON | `[-10]% Strength for enemy [Military] units in adjacent [All] tiles` | sound spreads and rattles |
| 25 | Illusion | 幻道 | D |  | F Illusion_Path; R ch963 | CANON | `Withdraws before melee combat` | the blow lands on an illusion |
| 26 | Wisdom | 智道 | E |  | F Wisdom_Path; R ch1323, 2086 | CANON | `Can see invisible [All] units` | deduction sees through hiding |
| 27 | Emotion | 情道 | E | Wisdom | F Emotion_Path; R ch1156 | CANON | `[+25]% Strength <when below [50] HP>` | feeling surges when hurt |
| 28 | Enchantment | 魅道 | E | Emotion | F Enchantment_Path; R ch338, 1323 | CANON | `[Target Unit] gains the [Charmed] status for [1] turn(s) <upon damaging a [Military] unit>` | charm saps the will to strike |
| 29 | Soul | 魂道 | E |  | F Soul_Path; R ch1505 | CANON | `[This Unit] gains [10] XP <upon defeating a [Military] unit>` | the soul grows by taking souls |
| 30 | Dream | 梦道 | E |  | F Dream_Path; R ch1326, 1619 | CANON | `[+50]% XP gained from combat` | dream realms pour attainment into the explorer |
| 31 | Enslavement | 奴道 | E |  | F Enslavement_Path; R ch1323, 870 | CANON | `May capture killed [Barbarians] units` | beasts beaten become beasts commanded |
| 32 | Time | 宙道 | F |  | F Time_Path; R ch1323, 1754 | CANON | `[1] additional attacks per turn` | stretched time gives one more strike |
| 33 | Space | 宇道 | F |  | F Space_Path; R ch1323 | CANON | `All tiles cost 1 movement` | distance folds |
| 34 | Rule | 律道 | F |  | F Rule_Path; R ch1323, 1787 | CANON | `Ignores Zone of Control` | the laws bend around the walker |
| 35 | Phantom | 虚道 | F | Rule | F Phantom_Path; R ch1787, 1869 | CANON | `[This Unit] gains the [Phantom Veil] status for [1] turn(s) <upon losing at least [30] HP in a single attack>` | turns insubstantial after a heavy blow |
| 36 | Restriction | 禁道 | F | Rule | F Restriction_Path; R ch1042, 1787 | CANON | `[Target Unit] gains the [Sealed] status for [2] turn(s) <upon damaging a [Military] unit>` | seals cut the target off from healing |
| 37 | Luck | 运道 | F |  | F Luck_Path; R ch1323, 1859 | CANON | `[+30]% Strength <with [50]% chance>` | fortune turns, for better or not at all |
| 38 | Heaven | 天道 | F |  | F Heaven_Path; R ch2196, 2285 | CANON | `[+25]% Strength <when fighting units from a Civilization with more Cities than you>` | heaven's balance strikes the strongest |
| 39 | Qi | 气道 | F |  | F Qi_Path; R ch1323, 2001 | CANON | `[+3] Strength` | formless qi adds raw force, which counts for less at high rank |
| 40 | Refinement | 炼道 | G |  | F Refinement_Path; R ch1326, 1552 | CANON | `[-30]% Gold cost of upgrading` | refiners raise their own Gu more cheaply |
| 41 | Formation | 阵道 | G |  | F Formation_Path; R ch1323, 1326 | CANON | `[+15]% Strength bonus for [Military] units within [1] tiles` | a formation strengthens everyone inside it |
| 42 | Food | 食道 | G |  | F Food_Path; R ch1457 | CANON | `[-25]% maintenance costs` | the food path feeds Gu cheaply |
| 43 | Pill | 丹道 | G |  | F Pill_Path; R ch1712, 1865 | CANON | `Unit will heal every turn, even if it performs an action` | pills heal on the march |
| 44 | Information | 信道 | G |  | F Information_Path; R ch1323, 705 | CANON | `Can see over obstacles` | messages and records reach past the hills |
| 45 | Human | 人道 | G |  | F Human_Path; R ch1729 | CANON | `All adjacent units heal [10] HP when healing` | human-path marks clash with nothing, so it helps any ally |
| 46 | Painting | 画道 | G |  | F Painting_Path; R ch1721, 2204 | CANON | `[+20]% Strength <when fighting in [Friendly Land] tiles>` | paintings guard the home that hangs them |
| 47 | Theft | 偷道 | G |  | F Theft_Path; R ch1323, 1528 | CANON | `Earn [50]% of killed [Military] unit's [Cost] as [Gold]` | gain without paying the cost |
<!-- paths:end -->

### Not in the list

* **Yin-yang 阴阳道** — one R mention (ch2300), a line Giant Sun built on human-path Gu; no F page. Treated as human
  path.
* **Not paths** (checked): bow or arrow (no 弓道 / 箭道; arrows fall under weapon path, ch1865); love (no 爱道; feelings
  are emotion path); 正道 / 魔道 righteous and demonic (factions, already Slice 1's two ideology branches); 仙道 / 凡道
  (immortal- vs mortal-grade moves); 影宗 Shadow Sect (an organisation).
* Seed-list corrections: fire is 炎道 (火道 is rare, ~15 marker hits vs ~150); ice-snow is one path 冰雪道 in R's era
  list (F keeps two pages); 天道 must be read by context (it also names the Heavenly Dao itself).

### Signature notes

* From MOD_SPEC_3's palette: time, wind, star, cloud, dark, wisdom, blood, human, formation, theft, earth and
  painting (tile Strength), metal; poison and ice-snow as on-hit statuses. Not used: `Ranged attacks may be performed
  over obstacles` and the ranged half of the palette (Gu Masters fight in melee since round 5c), `Can transform to
  [unit]` (decision 4).
* Kept from Slice 1: Moon's moon blade (AUTOPLAY round 5c).
* ⚠️ needs a C3 test in battle: luck (`<with [50]% chance>` in combat: does the preview match the result? E5), water
  (water travel on a land unit), restriction (`Can only heal by pillaging` on a status), phantom (the HP-loss trigger),
  lightning (`<when above [1] movement>` at attack time), fire (decision 5), sound (the enemy aura in both directions).
* Space adds `Can pass through impassable tiles` at Supreme Grandmaster only (MOD_SPEC_3: the unique is cached, never
  on a status).

## Families

Families group paths for templates (moves, icon colour) and for the reader; they carry no rules of their own. Canon
hooks: Reckless Savage founded strength and transformation; metal, fire, lightning, sword and blood are the five
strongest attack paths (R ch1064); metal, wood, water, fire and earth are the mainstream five (R ch752); wisdom, soul
and enslavement have been linked since antiquity (R ch870); time and space are the two oldest paths (R ch1323).

<!-- families:start (tools/gen_paths.py) -->
| Family | Paths | Play feel | Mortal move template | Immortal move template | Icon colour |
|---|---|---|---|---|---|
| A. Body & Beast | Strength, Transformation, Bone, Blood | melee, self-buffs, sustain | +25% Strength | +50% Strength, heal 30 HP | [150, 40, 40] |
| B. Edge & War | Sword, Blade, Metal, Weapon, Killing | burst damage, sieges | +40% Strength when attacking | +80% Strength when attacking | [140, 150, 160] |
| C. Five Phases & Weather | Fire, Water, Wood, Earth, Wind, Cloud, Ice Snow, Lightning, Poison | terrain, mobility, damage over time | +20% Strength, 10 extra damage to the target | +40% Strength, 25 extra damage | [60, 130, 70] |
| D. Sky & Shade | Light, Dark, Shadow, Star, Moon, Sound, Illusion | stealth, sight, skirmish | +2 movement now, +20% Strength when attacking | +3 movement now, +40% Strength when attacking | [70, 60, 140] |
| E. Mind & Spirit | Wisdom, Emotion, Enchantment, Soul, Dream, Enslavement | control, growth, captives | the target is Shaken (-20% Strength) for 2 turns | Shaken target, +30% Strength | [130, 70, 150] |
| F. Law & Cosmos | Time, Space, Rule, Phantom, Restriction, Luck, Heaven, Qi | rare rule-bending effects | 1 additional attack this turn | 1 additional attack, +40% Strength | [190, 160, 60] |
| G. Craft & Society | Refinement, Formation, Food, Pill, Information, Human, Painting, Theft | economy, healing, support | heal 40 HP, +15% Strength | heal 80 HP, +30% Strength | [150, 100, 50] |
<!-- families:end -->

## Attainment (流派境界)

Canon (R ch1326, ch2086; F "Dao"): nine grades.

| Canon grade | Chinese | Who has it in canon | Mod tier (default, decision 3) |
|---|---|---|---|
| Ordinary | 普通 | nearly every Gu Master, for life | — |
| Quasi-Master | 准大师 | gifted or long-seasoned Gu Masters | Master |
| Master | 大师 | one mortal in ten thousand; the usual main-path level of a rank-6 immortal | Master |
| Quasi-Grandmaster | 准宗师 | elite rank-6 immortals | Grandmaster |
| Grandmaster | 宗师 | usually rank 7; can imitate other paths with its own Gu | Grandmaster |
| Quasi-Great Grandmaster | 准大宗师 | rank-7 experts, a few rank 8 | Great Grandmaster |
| Great Grandmaster | 大宗师 | where most rank-8 immortals end | Great Grandmaster |
| Quasi-Supreme Grandmaster | 准无上大宗师 | once in thousands of years | Supreme Grandmaster |
| Supreme Grandmaster | 无上大宗师 | raises the path's ceiling; all ten Venerables; refinement has had three in all history | Supreme Grandmaster |

Correction to MOD_SPEC_3's wording: 大师 = Master, 宗师 = Grandmaster, 大宗师 = Great Grandmaster; the quasi steps are
canon (they were [VERIFY]).

Per path, four promotions (`<Path> Master`, `<Path> Grandmaster`, `<Path> Great Grandmaster`, `<Path> Supreme
Grandmaster`), linked by `prerequisites`, `unitTypes` = all three unit types (E10), bought with XP:

| Tier | Gate (`Only available <for [mapUnitFilter] units>`) | Carries | Starting numbers |
|---|---|---|---|
| Master | none; a sub-path also needs its parent's Master | the signature, the conflict lines, the `Path Master` marker and the AI one-path rule | `[+10]% Strength` |
| Grandmaster | rank 3+ (C3 writes the filter over the rank chain's units) | the mortal move button | `[+15]% Strength` |
| Great Grandmaster | rank 6+ (Gu Immortal or Venerable) | the immortal move button | `[+20]% Strength` |
| Supreme Grandmaster | rank 8+ | space only: `Can pass through impassable tiles`; MOD_SPEC_3's Venerable Ascension counts these | `[+25]% Strength` |

Canon ways to raise attainment that the mod already has or plans: practice (cultivation XP, Slice 1), dream realms
(dream path's XP; MOD_SPEC_2 #14), inherited true meaning (inheritances, MOD_SPEC_2 #12).

## Killer moves

Two per path: a mortal move at Grandmaster, an immortal move at Great Grandmaster (MOD_SPEC_2 #5). Each is a unit
action on the tier promotion that gives the unit a 1-turn status named after the move:
`[This Unit] gains the [<move>] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` (mortal;
primeval stones) and `… <costs [5] [<essence>]> <requires [1] movement>` (immortal; the essence names come from
MOD_SPEC_2 Phase B). The status's effect follows the family template. The AI never presses unit-action buttons
(CLAUDE.md): every unit stays viable without its moves; moves are the human's optional power (MOD_SPEC rule 7).

Tags: CANON = a killer move R/F name for this path; ADAPTED = a canon Gu, Immortal Gu or concept turned into a move,
or a canon move given a grade; INVENTED = my name (no Chinese). lit. = F has no English name, so the rendering is
literal. The names that are canon killer moves without a known grade are placed by their fame.

<!-- moves:start (tools/gen_paths.py) -->
| Path | Family template | Mortal move (Grandmaster) | Tag | Immortal move (Great Grandmaster) | Tag |
|---|---|---|---|---|---|
| Strength | A | Self-Reliance 自力更生 | ADAPTED: a Gu | Myriad Self 万我 | CANON; canon fuses enslavement and strength (R V4/134) |
| Transformation | A | Flying Bear Change 飞熊变 | CANON, lit. name | Ancient Sword Dragon 上古剑蛟 | CANON |
| Bone | A | Bone Spear 骨枪 | ADAPTED: a Gu | Bone Spike 骨刺 | ADAPTED: a rank-6 Immortal Gu |
| Blood | A | Blood Skull 血颅 | ADAPTED: a Gu | Blood Deity 血神子 | CANON |
| Sword | B | Sword Escape 剑遁 | ADAPTED: a Gu | Five Finger Fist Heart Sword 五指拳心剑 | CANON |
| Blade | B | Edge 刃 | ADAPTED: a Gu | Autumn Blade Sweep | INVENTED, after Autumn Blade Plain 秋刀原 |
| Metal | B | Iron Rain | INVENTED | City-Crushing Hammer 碎城锤 | CANON, lit. name |
| Weapon | B | Weapon Array | INVENTED | Hundred Weapons | INVENTED |
| Killing | B | Killing Intent | INVENTED | Kill 杀 | ADAPTED: the core Immortal Gu, still forming (R ch2233) |
| Fire | C | Five-Finger Flame Chain 五指炎链 | CANON, lit. name | Nirvana Fire 涅槃火 | CANON |
| Water | C | Stream Surge | ADAPTED: the Slice 1 Stream Gu | Worldly Wave Trace 浪迹天涯 | ADAPTED: an Immortal Gu |
| Wood | C | Rooted Vigor | INVENTED | Verdant Renewal | INVENTED |
| Earth | C | Nine-Ren Mountain 为山九仞 | ADAPTED: a Gu, lit. name | Earthen Bulwark | INVENTED |
| Wind | C | Gale Step | INVENTED | Wind-Rolled Dragon Whip 风卷龙鞭 | CANON, lit. name; grade ADAPTED |
| Cloud | C | Cloud Stride | INVENTED | Rising Azure Cloud 平步青云 | ADAPTED: a rank-6 Gu |
| Ice Snow | C | Frost Bind | INVENTED | Frozen Domain | INVENTED |
| Lightning | C | Lightning Wings 雷翼 | ADAPTED: a Gu | Thunder Judgement | INVENTED |
| Poison | C | Bee Net Sting 蜂罗刺 | CANON, lit. name | Woman's Heart 妇人心 | ADAPTED: an Immortal Gu |
| Light | D | Glare | INVENTED | Saw-Wheel Light 锯轮光 | CANON, lit. name |
| Dark | D | Shroud | INVENTED | Dark Limit 暗渡 | ADAPTED: an Immortal Gu |
| Shadow | D | Shadow Step | INVENTED | Shadow Severance | INVENTED |
| Star | D | Star Snake Rope 星蛇索 | CANON | Nebula Millstone 星云磨盘 | CANON, lit. name |
| Moon | D | Crescent Moon 偃月 | ADAPTED: a Gu; path per fan wiki only [VERIFY] | Peerless Crescent Moon Slash 无双偃月斩 | CANON move; path per fan wiki only [VERIFY] |
| Sound | D | Qin Strike 琴 | ADAPTED: the Qin Gu | Silence Beats Sound 此时无声胜有声 | CANON, lit. name |
| Illusion | D | Mirage | INVENTED | Illusory Garden | INVENTED, after Illusion Garden 幻景园 |
| Wisdom | E | Deduction | INVENTED | Unravel Mystery 解谜 | ADAPTED: an Immortal Gu |
| Emotion | E | Doting Mother 慈母 | ADAPTED: a Gu | Regret 悔 | ADAPTED: an Immortal Gu |
| Enchantment | E | Charming Glance | INVENTED | Captivation | INVENTED |
| Soul | E | Guts 胆识 | ADAPTED: a Gu | Soul Search 搜魂 | ADAPTED |
| Dream | E | Waking Dream | INVENTED | Dreamy Light Smoke 梦里轻烟 | CANON |
| Enslavement | E | Wolf Enslavement 驭狼 | ADAPTED: a Gu | Ambush on Eight Sides 八面埋伏 | CANON, lit. name |
| Time | F | Borrowed Moment | INVENTED | Call of the Ancient 前有古人 | CANON |
| Space | F | Folded Step | INVENTED | Sea and Sky Expands 海阔天空 | CANON |
| Rule | F | Bent Law | INVENTED | One Step Back 退一步 | CANON |
| Phantom | F | Hollow Form | INVENTED | Phantom Body | INVENTED |
| Restriction | F | Severing Essence 断元 | ADAPTED: a Gu, lit. name | Absolute Ban | INVENTED |
| Luck | F | Fortune Rivalling Heaven 鸿运齐天 | ADAPTED: a Gu | Turn of Fortune | INVENTED |
| Heaven | F | Heaven's Rebuke | INVENTED | Heavenly Web Protection Veil 天网恢恢 | CANON |
| Qi | F | Exploding Qi Roar 爆气吼 | CANON, lit. name | Qi Covers Mountains and Rivers 气盖山河 | CANON, lit. name |
| Refinement | G | Ink Transformation 墨化 | CANON, lit. name | Heavenly Light Rotation 天光轮转 | CANON, lit. name |
| Formation | G | Linked Formation | INVENTED | Grand Formation | INVENTED |
| Food | G | Eat Bitterness 吃苦 | CANON, lit. name | Banquet of Immortals | INVENTED |
| Pill | G | Recovery Pill | INVENTED | Life-Saving Pill | ADAPTED: fan wiki only [VERIFY] |
| Information | G | Mountain Pledge 山盟 | ADAPTED: a Gu | Sea Oath 海誓 | ADAPTED: a Gu |
| Human | G | Hopes of the Crowd 众望所归 | CANON, lit. name | Heroes Among People 人中豪杰 | CANON |
| Painting | G | Living Ink | INVENTED | Contented Lifestyle 安居乐业 | CANON |
| Theft | G | Light Fingers | INVENTED | Great Thief Ghost Hand 大盗鬼手 | CANON |
<!-- moves:end -->

## Generated uniques

<!-- uniques:start (tools/gen_paths.py) -->
Tiers 1-2 ship in Slice 1. Every Master also carries one hidden conflict line per later path whose pair costs Strength (`[relativeAmount]% Strength` `<for units with [promotion]>` `<hidden from users>`, values from data/path_conflicts.csv) and a visible comment line.

| Path | Master | Grandmaster | Mortal move status |
|---|---|---|---|
| Strength | `No damage penalty for wounded units` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [White Boar Gu] promotion <upon turn start> <for units without [White Boar Gu]> <for units without [White Jade Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` `[+23133]% weight to this choice for AI decisions <for [Xiong Clan] Civilizations>` | `[+15]% Strength` `[This Unit] gains the [Self-Reliance] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+25]% Strength` |
| Transformation | `Double movement in [Forest]` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Roaming Zombie Gu] promotion <upon turn start> <for units without [Roaming Zombie Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Flying Bear Change] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+25]% Strength` |
| Bone | `[+20]% Strength <when defending>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Bone Spear Gu] promotion <upon turn start> <for units without [Bone Spear Gu]> <when above [0] [Wild Boar]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Bone Spear] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+25]% Strength` |
| Blood | `Heals [20] damage if it kills a unit` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Blood Skull Gu] promotion <upon turn start> <for units without [Blood Skull Gu]> <for [Rank Four era] units> <when above [0] [Wild Boar]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Blood Skull] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+25]% Strength` |
| Sword | `[+25]% Strength <when attacking>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Sword Shadow Gu] promotion <upon turn start> <for units without [Sword Shadow Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Sword Escape] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+40]% Strength <when attacking>` |
| Blade | `[+50]% to Flank Attack bonuses` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Sole Blade Gu] promotion <upon turn start> <for units without [Sole Blade Gu]> <for [Rank Four era] units> <when above [0] [Jade]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Edge] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+40]% Strength <when attacking>` |
| Metal | `[+30]% Strength <vs cities>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Bronze Skin Gu] promotion <upon turn start> <for units without [Bronze Skin Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Iron Rain] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+40]% Strength <when attacking>` |
| Weapon | `[+20]% Strength <when adjacent to a [Military] unit>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Armoury Gu] promotion <upon turn start> <for units without [Armoury Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Weapon Array] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+40]% Strength <when attacking>` |
| Killing | `[This Unit] gains [1] movement <upon defeating a [Military] unit>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Killing Intent Gu] promotion <upon turn start> <for units without [Killing Intent Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Killing Intent] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+40]% Strength <when attacking>` |
| Fire | `Destroys tile improvements when attacking` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Fiery Claw Gu] promotion <upon turn start> <for units without [Fiery Claw Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Five-Finger Flame Chain] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Water | `May travel on Water tiles without embarking` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Water Shield Gu] promotion <upon turn start> <for units without [Water Shield Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` `[+23133]% weight to this choice for AI decisions <for [Bai Clan] Civilizations>` | `[+15]% Strength` `[This Unit] gains the [Stream Surge] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Wood | `[15] HP when healing` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Heavenly Essence Treasure Lotus] promotion <upon turn start> <for units without [Heavenly Essence Treasure Lotus]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Rooted Vigor] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Earth | `[+25]% Strength <when fighting in [Hill] tiles>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Gruel Mud Gu] promotion <upon turn start> <for units without [Gruel Mud Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Nine-Ren Mountain] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Wind | `[1] Movement` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Whirlwind Gu] promotion <upon turn start> <for units without [Whirlwind Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` `[+23133]% weight to this choice for AI decisions <for [Wu Clan] Civilizations>` | `[+15]% Strength` `[This Unit] gains the [Gale Step] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Cloud | `Ignores terrain cost` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Flying Cloud Gu] promotion <upon turn start> <for units without [Flying Cloud Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Cloud Stride] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Ice Snow | `[Target Unit] loses [1] movement <upon damaging a [Military] unit>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Frost Demon Gu] promotion <upon turn start> <for units without [Frost Demon Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Frost Bind] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Lightning | `[+30]% Strength <when above [1] movement>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Thunderclap Gu] promotion <upon turn start> <for units without [Thunderclap Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Lightning Wings] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Poison | `[Target Unit] gains the [Poisoned] status for [3] turn(s) <upon damaging a [Military] unit>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Poison Scorpion Gu] promotion <upon turn start> <for units without [Poison Scorpion Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Bee Net Sting] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength` `[Target Unit] takes [10] damage <upon damaging a [Military] unit>` |
| Light | `Can move after attacking` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Little Light Gu] promotion <upon turn start> <for units without [Little Light Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Glare] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength <when attacking>` `[This Unit] gains [2] movement <upon gaining the [Glare] status>` |
| Dark | `Invisible to others` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Shadow Follower Gu] promotion <upon turn start> <for units without [Shadow Follower Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Shroud] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength <when attacking>` `[This Unit] gains [2] movement <upon gaining the [Shroud] status>` |
| Shadow | `[+30]% Strength <vs [Wounded] units>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Overlapping Shadow Gu] promotion <upon turn start> <for units without [Overlapping Shadow Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] gains the [Shadow Step] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength <when attacking>` `[This Unit] gains [2] movement <upon gaining the [Shadow Step] status>` |
| Star | `[2] Sight` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Star Dart Gu] promotion <upon turn start> <for units without [Star Dart Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Star Snake Rope] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength <when attacking>` `[This Unit] gains [2] movement <upon gaining the [Star Snake Rope] status>` |
| Moon | `Before engaging in combat performs an extra ranged attack with [40]% of melee combat strength` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Moonlight Gu] promotion <upon turn start> <for units without [Moonlight Gu]> <for units without [Moon Raiment]> <when above [0] [Moon Orchid]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` `[+23133]% weight to this choice for AI decisions <for [Gu Yue Clan] Civilizations>` | `[+15]% Strength` `[This Unit] gains the [Crescent Moon] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength <when attacking>` `[This Unit] gains [2] movement <upon gaining the [Crescent Moon] status>` |
| Sound | `[-10]% Strength for enemy [Military] units in adjacent [All] tiles` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Heaven Earth Magnificent Sound Gu] promotion <upon turn start> <for units without [Heaven Earth Magnificent Sound Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Qin Strike] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength <when attacking>` `[This Unit] gains [2] movement <upon gaining the [Qin Strike] status>` |
| Illusion | `Withdraws before melee combat` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Illusory Moon Gu] promotion <upon turn start> <for units without [Illusory Moon Gu]> <for [non-[Rank One-Two era]] units> <when above [0] [Moon Orchid]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Mirage] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+20]% Strength <when attacking>` `[This Unit] gains [2] movement <upon gaining the [Mirage] status>` |
| Wisdom | `Can see invisible [All] units` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Clear Mind Gu] promotion <upon turn start> <for units without [Clear Mind Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Deduction] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` |
| Emotion | `[+25]% Strength <when below [50] HP>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Emotion Poetry Gu] promotion <upon turn start> <for units without [Emotion Poetry Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] gains the [Doting Mother] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` |
| Enchantment | `[Target Unit] gains the [Charmed] status for [1] turn(s) <upon damaging a [Military] unit>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Estrus Gu] promotion <upon turn start> <for units without [Estrus Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] gains the [Charming Glance] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` |
| Soul | `[This Unit] gains [10] XP <upon defeating a [Military] unit>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Soul Search Gu] promotion <upon turn start> <for units without [Soul Search Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Guts] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` |
| Dream | `[+50]% XP gained from combat` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Dream Pillow Gu] promotion <upon turn start> <for units without [Dream Pillow Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Waking Dream] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` |
| Enslavement | `May capture killed [Barbarians] units` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Wolf Enslavement Gu] promotion <upon turn start> <for units without [Wolf Enslavement Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Wolf Enslavement] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[Target Unit] gains the [Shaken] status for [2] turn(s) <upon damaging a [Military] unit>` |
| Time | `[1] additional attacks per turn` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Man as Before Gu] promotion <upon turn start> <for units without [Man as Before Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Borrowed Moment] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Space | `All tiles cost 1 movement` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Warp Gu] promotion <upon turn start> <for units without [Warp Gu]> <for [Rank Four era] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Folded Step] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Rule | `Ignores Zone of Control` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Amplify Effect Gu] promotion <upon turn start> <for units without [Amplify Effect Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Bent Law] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Phantom | `[This Unit] gains the [Phantom Veil] status for [1] turn(s) <upon losing at least [30] HP in a single attack>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Turn Phantom Gu] promotion <upon turn start> <for units without [Turn Phantom Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] gains the [Hollow Form] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Restriction | `[Target Unit] gains the [Sealed] status for [2] turn(s) <upon damaging a [Military] unit>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Primeval Break Gu] promotion <upon turn start> <for units without [Primeval Break Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] gains the [Severing Essence] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Luck | `[+30]% Strength <with [50]% chance>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Luck Inspection Gu] promotion <upon turn start> <for units without [Luck Inspection Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Fortune Rivalling Heaven] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Heaven | `[+25]% Strength <when fighting units from a Civilization with more Cities than you>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Lifespan Gu] promotion <upon turn start> <for units without [Lifespan Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Heaven's Rebuke] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Qi | `[+3] Strength` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Strength Qi Gu] promotion <upon turn start> <for units without [Strength Qi Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Exploding Qi Roar] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[1] additional attacks per turn` |
| Refinement | `[-30]% Gold cost of upgrading` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Revert Gu] promotion <upon turn start> <for units without [Revert Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Ink Transformation] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Ink Transformation] status>` |
| Formation | `[+15]% Strength bonus for [Military] units within [1] tiles` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Formation Heart Gu] promotion <upon turn start> <for units without [Formation Heart Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Linked Formation] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Linked Formation] status>` |
| Food | `[-25]% maintenance costs` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Liquor Worm] promotion <upon turn start> <for units without [Liquor Worm]> <for [Rank One Gu Master] units> <when above [0] [Wine]>` `[This Unit] gains the [Four Flavours Liquor Worm] promotion <upon turn start> <for units without [Four Flavours Liquor Worm]> <for [non-[Rank One Gu Master]] units> <when above [0] [Wine]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Eat Bitterness] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Eat Bitterness] status>` |
| Pill | `Unit will heal every turn, even if it performs an action` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Pill Refiner Gu] promotion <upon turn start> <for units without [Pill Refiner Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Recovery Pill] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Recovery Pill] status>` |
| Information | `Can see over obstacles` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Flying Sword Letter Gu] promotion <upon turn start> <for units without [Flying Sword Letter Gu]> <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Mountain Pledge] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Mountain Pledge] status>` |
| Human | `All adjacent units heal [10] HP when healing` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Relic Gu] promotion <upon turn start> <for units without [Relic Gu]>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Hopes of the Crowd] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Hopes of the Crowd] status>` |
| Painting | `[+20]% Strength <when fighting in [Friendly Land] tiles>` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Painting Idea Gu] promotion <upon turn start> <for units without [Painting Idea Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Living Ink] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Living Ink] status>` |
| Theft | `Earn [50]% of killed [Military] unit's [Cost] as [Gold]` `[+10]% Strength` `Comment [Every other path this unit holds costs Strength: dao marks interfere]` `Path Master` `[This Unit] gains the [Plunder Gu] promotion <upon turn start> <for units without [Plunder Gu]> <for [non-[Rank One Gu Master]] units>` `[+400]% weight to this choice for AI decisions` `Unavailable <for [AI player] Civilizations> <for [Path Master] units>` | `[+15]% Strength` `[This Unit] gains the [Light Fingers] status for [1] turn(s) <costs [+15 Gold] stats> <requires [1] movement>` `Only available <for [non-[Rank One-Two era]] units>` `[+400]% weight to this choice for AI decisions` | `[+15]% Strength` `[This Unit] heals [40] HP <upon gaining the [Light Fingers] status>` |

| Status | Uniques |
|---|---|
| Poisoned | `[This Unit] takes [10] damage <upon turn start>` |
| Charmed | `[-25]% Strength <when attacking>` |
| Sealed | `Can only heal by pillaging` |
| Phantom Veil | `[+50]% Strength <when defending>` |
| Shaken | `[-20]% Strength` |
<!-- uniques:end -->

## Conflicts (道痕 interference)

Canon rule (R ch1077, ch1804, ch1724): dao marks of different paths hinder each other, so immortals keep one main
path. The mod charges every **pair** of paths a unit holds at Master tier, so the cost grows with each extra path
(two paths 1 pair, three 3 pairs, four 6 pairs):

| Pair | Strength per pair | Basis |
|---|---|---|
| Default (any two paths) | −10% | the general rule above |
| Strong clash | −25% | earth–water (ch1425: an earth move in a water-rich place loses half or more); earth–fire (ch721); strength–water (ch734, ch758: 70–80% from a water Immortal Gu); metal–strength (ch716); light–dark (ch2271) |
| Sound with anything | −5% | ch1425: a sound move loses a fifth to a third where earth loses half |
| Human with anything | 0 | ch1729: human-path marks neither disturb nor are disturbed |
| Compatible | 0 | soul–enslavement, soul–wisdom, wisdom–enslavement (ch870, ch1062); rule–restriction (ch1062); rule–phantom (ch1869); wisdom–emotion (ch1062); emotion–enchantment and wisdom–enchantment (R 魅情道); dark–shadow and light–shadow (ch2284: shadow holds both); lightning–sound (ch1068) |

F only, not found in R, so left at the default: sword–blade "barely clash"; heaven marks convert into other paths'.
Painting "bridging" mismatched paths (ch1722) is only a hint: default.

Implementation (1,024 lines, generated): on the earlier path's Master,
`[-10]% Strength <for units with [<other> Master]> <hidden from users>` per pair, plus one visible
`Comment [...]` line. The same matrix gives the negative amounts of MOD_SPEC_2 #4's dao-mark countables
(`[relativeAmount]% Strength <for every [positiveAmount] [countable]>` on `[[<Path> Path] Buildings]`). Tension target
(MOD_SPEC_3): a single-path unit at Grandmaster (+25%, one signature, a move) against a three-path unit of the same
rank holding three Masters (+30% −30% for three pairs, three signatures); duels in C3 decide the numbers.

## Path Gu (the user's decision D2, 2026-10-19)

One canon mortal Gu per path, from the source research (35 canon, 4 adapted, 6 whose path or rank canon leaves open,
used as ADAPTED at the user's word, and two INVENTED for Weapon and Killing, which have no mortal Gu in canon; Food
has two, the Liquor Worm for rank one and the canon Four Flavours Liquor Worm above it). Effects follow each Gu's canon
use; a Gu whose canon food is known eats the nearest Gu food and starves like the Slice 1 Gu, the others cost +10%
upkeep in stones. Every unit holds the Gu of each Master it holds.

<!-- gu:start (tools/gen_paths.py) -->
Granted at a turn start to a unit holding the path's Master (the line is in the Master's column above), once the unit's rank reaches the Gu's (a rank-5 Gu at rank four until the immortal arc) and, for a food eater, while that food is in surplus. Moonlight Gu, White Boar Gu and the Liquor Worm are the Slice 1 Gu.

| Path | Gu | Chinese | Rank | Food | Uniques | Verdict | Source |
|---|---|---|---|---|---|---|---|
| Strength | White Boar Gu | 白豕蛊 | 1 | stones | Slice 1 Gu | CANON | existing (Slice 1 ladder rung 1; research picked the Black Boar, which stays the Jia caravan's Gu) |
| Transformation | Roaming Zombie Gu | 游僵蛊 | 2 | stones | `[+15]% Strength <when defending>` `[+10]% maintenance costs` | CANON | F Roaming_Zombie_Gu; R ch526 |
| Bone | Bone Spear Gu | 骨枪蛊 | 1 | Wild Boar | `[+15]% Strength <when attacking> <when above [-1] [Wild Boar]>` `Consumes [1] [Wild Boar]` `[This Unit] gains the [Pork Hunger] status for [3] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units without [Pork Hunger]>` `[This Unit] loses the [Bone Spear Gu] promotion <upon losing the [Pork Hunger] status> <when below [0] [Wild Boar]> <with [50]% chance>` | CANON | F Bone_Spear_Gu; R ch222, 228; food: milk in canon, pork here (ADAPTED) |
| Blood | Blood Skull Gu | 血颅蛊 | 4 | Wild Boar | `[+25]% XP gained from combat <when above [-1] [Wild Boar]>` `Consumes [1] [Wild Boar]` `[This Unit] gains the [Pork Hunger] status for [9] turn(s) <upon turn start> <when below [0] [Wild Boar]> <for units without [Pork Hunger]>` `[This Unit] loses the [Blood Skull Gu] promotion <upon losing the [Pork Hunger] status> <when below [0] [Wild Boar]> <with [50]% chance>` | CANON | F Blood_Skull_Gu; R ch205, 407; food: fresh blood in canon, pork here (ADAPTED) |
| Sword | Sword Shadow Gu | 剑影蛊 | 3 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Sword_Shadow_Gu; R ch265, 280 |
| Blade | Sole Blade Gu | 单刀蛊 | 4 | Jade | `[+25]% Strength <when attacking> <with [50]% chance> <when above [-1] [Jade]>` `Consumes [1] [Jade]` `[This Unit] gains the [Jade Hunger] status for [9] turn(s) <upon turn start> <when below [0] [Jade]> <for units without [Jade Hunger]>` `[This Unit] loses the [Sole Blade Gu] promotion <upon losing the [Jade Hunger] status> <when below [0] [Jade]> <with [50]% chance>` | CANON | F Sole_Blade_Gu; R ch519; food: it wears its blade away in canon, jade here (ADAPTED) |
| Metal | Bronze Skin Gu | 铜皮蛊 | 1 | stones | `[+15]% Strength <when defending>` `[+10]% maintenance costs` | CANON | F Bronze_Skin_Gu; R ch24, 62, 65 |
| Weapon | Armoury Gu | — | 2 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | INVENTED | the weapon path has no mortal Gu in canon (R ch1865, 2154; F Weapon_Path); the user's decision D2 |
| Killing | Killing Intent Gu | — | 3 | stones | `[+20]% Strength <vs [Wounded] units>` `[+10]% maintenance costs` | INVENTED | the killing path has only the rank-8 Kill Gu, still forming (R ch2233, 2328); the user's decision D2 |
| Fire | Fiery Claw Gu | 火爪蛊 | 3 | stones | `[Target Unit] takes [5] damage <upon damaging a [Military] unit>` `[+10]% maintenance costs` | CANON | F Fiery_Claw_Gu; R ch313-314 |
| Water | Water Shield Gu | 水罩蛊 | 2 | stones | `[+15]% Strength <when defending>` `[+10]% maintenance costs` | CANON | F Water_Shield_Gu; R ch136, 141, 150 |
| Wood | Heavenly Essence Treasure Lotus | 天元宝莲 | 3 | stones | `[-20]% maintenance costs` | CANON | F Heavenly_Essence_Treasure_Lotus; R ch162-163 (raw: 天元宝莲) |
| Earth | Gruel Mud Gu | 和稀泥蛊 | 1 | stones | `[+15]% Strength <when fighting in [Hill] tiles>` `[+10]% maintenance costs` | CANON | F Gruel_Mud_Gu; R ch425, 474 |
| Wind | Whirlwind Gu | 旋风蛊 | 1 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Whirlwind_Gu; R ch106, 109 |
| Cloud | Flying Cloud Gu | 腾云蛊 | 4 | stones | `[1] Movement` `[+10]% maintenance costs` | CANON | F Flying_Cloud_Gu; R ch429, 441 |
| Ice Snow | Frost Demon Gu | 霜妖蛊 | 3 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Frost_Demon_Gu; R ch275, 396 |
| Lightning | Thunderclap Gu | 炸雷蛊 | 3 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Thunderclap_Gu; R ch150, 353 |
| Poison | Poison Scorpion Gu | 毒蝎蛊 | 3 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Poison_Scorpion_Gu; R ch330 |
| Light | Little Light Gu | 小光蛊 | 1 | stones | `[1] Sight` `[+10]% maintenance costs` | CANON | F Little_Light_Gu; R ch62, 70, 563 |
| Dark | Shadow Follower Gu | 幽影随行蛊 | 2 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Shadow_Follower_Gu; R ch75-76 |
| Shadow | Overlapping Shadow Gu | 叠影蛊 | 4 | stones | `[+20]% Strength <when attacking>` `[+10]% maintenance costs` | ADAPTED | F Overlapping_Shadow_Gu; R ch505, 512 (filed under the dark path; no shadow-path mortal Gu in canon; the user's decision D2) |
| Star | Star Dart Gu | 星镖蛊 | 1 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Star_Dart_Gu; R ch276, 666 |
| Moon | Moonlight Gu | 月光蛊 | 1 | Moon Orchid | Slice 1 Gu | CANON | existing (Slice 1 ladder rung 1) |
| Sound | Heaven Earth Magnificent Sound Gu | 天地宏音蛊 | 5 | stones | `[+20]% Strength <when attacking>` `[+10]% maintenance costs` | CANON | F Heaven_Earth_Magnificent_Sound_Gu; R ch184, 186; rank 5 held at rank four until the immortal arc (ADAPTED) |
| Illusion | Illusory Moon Gu | 幻影月蛊 | 3 | Moon Orchid | `[+15]% Strength <when defending> <when above [-1] [Moon Orchid]>` `Consumes [1] [Moon Orchid]` `[This Unit] gains the [Orchid Hunger] status for [7] turn(s) <upon turn start> <when below [0] [Moon Orchid]> <for units without [Orchid Hunger]>` `[This Unit] loses the [Illusory Moon Gu] promotion <upon losing the [Orchid Hunger] status> <when below [0] [Moon Orchid]> <with [50]% chance>` | ADAPTED | F Illusory_Moon_Gu; R ch156 (the decoy is described, the path rests on F) |
| Wisdom | Clear Mind Gu | 神清蛊 | 4 | stones | `[+20]% XP gained from combat` `[+10]% maintenance costs` | CANON | F Clear_Mind_Gu; R ch486 |
| Emotion | Emotion Poetry Gu | 诗情蛊 | 4 | stones | `[+15]% Strength <when below [50] HP>` `[+10]% maintenance costs` | CANON | F Emotion_Poetry_Gu; R ch550, 570 |
| Enchantment | Estrus Gu | 发情蛊 | 2 | stones | `[+15]% Strength <vs [Barbarians] units>` `[+10]% maintenance costs` | ADAPTED | F Estrus_Gu (enchantment); R ch415, 570 (the emotion line from which enchantment split); rank not stated (the user's decision D2) |
| Soul | Soul Search Gu | 搜魂蛊 | 3 | stones | `[+25]% XP gained from combat` `[+10]% maintenance costs` | CANON | F Soul_Search_Gu; R ch488 |
| Dream | Dream Pillow Gu | 梦枕蛊 | 5 | stones | `[10] HP when healing` `[+10]% maintenance costs` | CANON | F Dream_Pillow_Gu; R ch1619; rank 5 held at rank four until the immortal arc (ADAPTED) |
| Enslavement | Wolf Enslavement Gu | 驭狼蛊 | 1 | stones | `[+15]% Strength <vs [Barbarians] units>` `[+10]% maintenance costs` | CANON | F Wolf_Enslavement_Gu; R ch437, 452-454 |
| Time | Man as Before Gu | 人如故蛊 | 5 | stones | `[20] HP when healing` `[+10]% maintenance costs` | CANON | F Man_as_Before_Gu; R ch533, 538; rank 5 held at rank four until the immortal arc (ADAPTED) |
| Space | Warp Gu | 挪移蛊 | 5 | stones | `[1] Movement` `[+10]% maintenance costs` | CANON | F Warp_Gu; R ch397-398; rank 5 held at rank four until the immortal arc (ADAPTED) |
| Rule | Amplify Effect Gu | 功倍蛊 | 1 | stones | `[+10]% Strength` `[+10]% maintenance costs` | CANON | F Amplify_Effect_Gu; R ch522, 527 |
| Phantom | Turn Phantom Gu | 弄虚蛊 | 3 | stones | `[+15]% Strength <when defending>` `[+10]% maintenance costs` | ADAPTED | F Turn_Phantom_Gu; R ch586; rank not stated (the user's decision D2) |
| Restriction | Primeval Break Gu | 断元蛊 | 3 | stones | `[+15]% Strength <when attacking>` `[+10]% maintenance costs` | ADAPTED | F Primeval_Break_Gu; R ch584; rank not stated (the user's decision D2) |
| Luck | Luck Inspection Gu | 察运蛊 | 1 | stones | `[1] Sight` `[+10]% maintenance costs` | CANON | F Luck_Inspection_Gu; R ch604, 611 (a series up to rank 5) |
| Heaven | Lifespan Gu | 寿蛊 | 1 | stones | `[10] HP when healing` `[+10]% maintenance costs` | CANON | F Lifespan_Gu; R ch38, 58, 2135, 2275 |
| Qi | Strength Qi Gu | 力气蛊 | 3 | stones | `[+15]% Strength` `[+10]% maintenance costs` | CANON | F Strength_Qi_Gu; R ch315, 320 |
| Refinement | Revert Gu | 幡然蛊 | 2 | stones | `[+10]% Strength` `[+10]% maintenance costs` | ADAPTED | F Revert_Gu; R ch113, 212; rank not stated (the user's decision D2) |
| Formation | Formation Heart Gu | 阵心蛊 | 1 | stones | `[+10]% Strength bonus for [Military] units within [1] tiles` `[+10]% maintenance costs` | CANON | F Formation_Heart_Gu; R ch1324 |
| Food | Liquor Worm | 酒虫 | 1 | Wine | Slice 1 Gu | CANON | existing (Slice 1; rank one only, canon) |
| Food | Four Flavours Liquor Worm | 四味酒虫 | 2 | Wine | `[+50]% XP gained from combat <when above [-1] [Wine]>` `Consumes [1] [Wine]` `[This Unit] gains the [Wine Hunger] status for [5] turn(s) <upon turn start> <when below [0] [Wine]> <for units without [Wine Hunger]>` `[This Unit] loses the [Four Flavours Liquor Worm] promotion <upon losing the [Wine Hunger] status> <when below [0] [Wine]> <with [50]% chance>` | CANON | R V1c121 (two Liquor Worms and four wines, sour, sweet, bitter, spicy, refine the rank-2 worm); W Liquor_Worm |
| Pill | Pill Refiner Gu | 炼丹师蛊 | 1 | stones | `[10] HP when healing` `[+10]% maintenance costs` | ADAPTED | F Pill_Refiner_Gu; R ch2284 (a human-path recipe born from the pill-path inheritance) |
| Information | Flying Sword Letter Gu | 飞剑传书蛊 | 3 | stones | `[1] Sight` `[+10]% maintenance costs` | CANON | F Flying_Sword_Letter_Gu; R ch418 |
| Human | Relic Gu | 舍利蛊 | 1 | stones | `[+25]% XP gained from combat` `[+10]% maintenance costs` | CANON | F Relic_Gu; R ch53, 111-113, 1796 |
| Painting | Painting Idea Gu | 画意蛊 | 2 | stones | `[+15]% Strength <when fighting in [Friendly Land] tiles>` `[+10]% maintenance costs` | ADAPTED | F Painting_Idea_Gu; R ch550 (filed under wisdom; only the name points to painting; the user's decision D2) |
| Theft | Plunder Gu | 强取蛊 | 2 | stones | `Earn [25]% of killed [Military] unit's [Cost] as [Gold]` `[+10]% maintenance costs` | CANON | F Plunder_Gu; R ch131-138 (carried by Xiong Zhan) |
<!-- gu:end -->

## AI

User decision (C3 checkpoint, 2026-10-18): **every cultivator takes its own path and Gu, unless its clan has a canon
signature path.** That replaces the main-path lock of the B3 draft.

* **One path per AI unit.** Every Master carries the filter marker `Path Master`; each root Master (not the sub-paths)
  also carries `Unavailable` `<for [AI player] Civilizations>` `<for [mapUnitFilter] units>` on that marker, so an AI
  unit that holds any Master is offered no other root Master. Its sub-paths stay open (they do not clash with the
  parent). Humans may mix paths and pay the conflict lines. Needed because the AI buys every promotion it can afford
  [src `NextTurnAutomation.applyPromotions`: weighted random while XP lasts]; without the rule cultivation XP would
  pile two or three paths onto every AI unit.
* **Signature clans lean, they are not locked.** Gu Yue — Moon, Bai — Water, Xiong — Strength, Wu — Wind (the
  user's decision D3, 2026-10-19: Wu Ji walks strength, the clan's tradition is wind, R V6c130) get
  `[relativeAmount]% weight to this choice for AI decisions` `<for [civFilter] Civilizations>` on their path's
  Master, sized so that about 85% of their cultivators take it (MOD_SPEC_3's ≥80% target, with margin); the rest
  take other paths, as canon's Gu Yue produced a strength-path Fang Yuan. All other clans, the arc's majors
  included (Heavenly Court, Huang Jin, Zombie Alliance, Fang clan), have no signature path: their cultivators
  spread over all paths.
* **Evidence (prototype, autoplay 6 games × 150 turns, Prince).** Signature weight for 80%: the four clans held
  25 / 26 / 29 / 33 root Masters on 25 / 26 / 29 / 33 Gu Masters (one path each), 69–85% on the signature path
  (pooled 80%, small samples). With Bai and Wu treated as having no signature path: 18 and 19 different paths among
  27 and 31 cultivators. At the shipped 85% setting (12 games): 84–89% per clan, pooled 214 of 249 (86%), still
  one path per unit (249 root Masters on 250 Gu Masters), 0 crashes.
* **Path tiers vs other promotions:** `[+400]% weight to this choice for AI decisions` on every tier keeps the AI
  spending XP on its path before generic promotions; Refine Gu keeps its own weights (E4).
* **Canon cost:** immortals often keep a secondary path (Venerables a hidden specialty, R ch2204); AI units do not.
* **Gu per path:** Slice 1's mortal Gu belong to the Moon and Strength ladders; cultivators of other paths have no
  path Gu yet (open question, C3).

## Budget (MOD_SPEC_3)

| Item | Cap | Here |
|---|---|---|
| Paths | all canonical (expected ~35) | 47 (42 + 5 sub-paths) |
| Promotions per path | ≤4 | 4 tiers |
| General promotions | ≤10 | 5 statuses (Poisoned, Charmed, Sealed, Phantom Veil, Shaken) |
| Killer moves | ≤2 per path | 2 per path (94 move statuses) |
| Gu units | 9 + ≤1 unique per nation | unchanged here (decision 4 keeps it) |
| Icons | placeholders coloured by family | family colours above |

## Risks for C3

* **The promotion screen** offers a human unit 42 Master tiers at once (sub-paths open later). Unciv lays promotions
  out as a tree; whether 42 roots stay usable on Android needs a look in game. Fallbacks: gate each family's Masters
  behind a family tech (`Only available <after discovering [techFilter]>`; 7 techs, which also lengthens the tech tree
  that ends near turn 120, BALANCE.md item 6), or open a path only where its academy stands.
* **Slice 1 overlap:** the Moon and Strength path policies, the Moon/Strength unit types, the generic Killer Move
  promotion and Refine Gu. C3's migration plan maps them onto the lines above; nothing is renamed or deleted without
  approval (MOD_SPEC_3 Boundaries).
* **XP budget:** path tiers now compete with Refine Gu for the AI's XP; C3 autoplay checks the refinement ladder
  still moves (AUTOPLAY round 5d).

## C3 migration plan (⛔ waiting for approval)

MOD_SPEC_3 C3: Slice 1 already ships path policies and path × rank units, so nothing changes until the user approves
this plan.

**What Slice 1 ships that the new architecture replaces**

* 6 units on 2 unit types: Rank Two / Three / Four Moon Gu Master (type Moon Gu Master) and Rank Two / Three / Four
  Strength Gu Master (type Strength Gu Master). Rank One upgrades to either: the upgrade is the path choice.
* Filters on those units and types across `jsons/` (lines naming them: Events 29, Units 18, UnitPromotions 10,
  Policies 6, Ruins 5, UnitTypes 2, CityStateTypes 1), plus `tools/gen_ruleset.py`
  (`GM_TYPES`, the refinement ladder), `tools/ladder_check.py`, the art, civilopedia, translations and autoplay counters.
* The Moon Path and Strength Path policy branches (mutually exclusive; +5% Strength per adopted policy for their unit
  type; Orchid Beds −15% upkeep for Moon units); Xiong starts with Strength Path; AI priorities Gu Yue Moon 10,
  Bai Moon 8, Xiong Strength 10, Wu Strength 10 (since D3: Righteous 10, Strength 4).

**Steps** (each one shippable: `tools/check_all`, autoplay, CHANGELOG, commit, then the user's "Locate mod errors")

| # | Step | Detail |
|---|---|---|
| M1 | Rank chain | New Rank Two / Three / Four Gu Master (type Gu Master); Rank One upgrades to the one Rank Two. Per rank the Strength line's numbers (strength 14 / 22 / 32, cost 60 / 95 / 140, upkeep +100 / +125 / +175%): Moon units lose 1–3 base Strength, their Master gives back the moon blade and +10%. Rank Five comes with MOD_SPEC_2 C1 |
| M2 | Path lines, tiers 1–2 | `data/paths.csv` + `tools/gen_paths.py` (from the B3 draft): 47 Masters, 47 Grandmasters with their mortal moves (47 move statuses), 5 signature statuses, the conflict lines, the AI one-path rule and the signature-clan weights. Tiers 3–4 and the immortal moves wait for MOD_SPEC_2 C3 (they need the Gu Immortal type and essence) |
| M3 | Retarget the filters | Every `[Moon Gu Master]` / `[Strength Gu Master]` becomes `[Moon Master]` / `[Strength Master]` (a promotion name is a valid mapUnitFilter); the Righteous/Demonic rebellions name Rank Two Gu Master; the refinement ladder keys on the Masters, and `tools/ladder_check.py` walks promotion states, including a human unit holding both Masters (it must match at most one ladder) |
| M4 | Legacy bridge for saves | Keep the 6 old units and 2 types, hidden (`Will not be displayed in Civilopedia`, `Unbuildable`, `Cannot be purchased`), each upgrading at its next turn start into the same-rank Gu Master after gaining its path's Master (`[unitTriggerTarget] gains the [promotion] promotion` and `[unitTriggerTarget] upgrades for free`, both `<upon turn start>`); promotions and XP survive the upgrade (A3 test 1). Reason: on load Unciv **deletes** every unit of a save that the ruleset no longer has [src `BackwardCompatibility.removeUnitsAndPromotions`], so removing them outright would wipe the Gu Masters of every running game. A capability test comes first (the order of the two triggers). Deleting the legacy objects later is a separate decision |
| M5 | Policies | Keep both branches (no deletion, no rename), retargeted to the Masters and still mutually exclusive; Bai's personality drops its Moon priority (Bai is Water now) |
| M6 | Art | Map sprites stay per clan through civ-name variants [src `TileSetStrings.tryGetUnitImageLocation`: `<unit>-<civ name>`]: Gu Yue and Bai keep the moon art (Bai until water art exists), Xiong and Wu the strength art; other civs get a neutral render. Attack animations follow the unit name or unit type only [src `BattleTableHelpers.getAttackAnimationLocation`], so after M1 they are per rank, no longer per path: the moon-blade and boar-charge effects become one effect per rank |
| M7 | Balance | Autoplay A/B (Prince, Standard, 320 turns; King, 200 turns): conquest per clan, E8 city strength re-tuned, solvency (round 8 must hold), refinement-ladder throughput (path tiers now compete with Refine Gu for XP), signature-clan share ≥80% and path spread in the other clans |
| M8 | Text | LORE_MAPPING rows (the self-test demands them), civilopedia EN + ID, translations, BALANCE inventory, KNOWN_ISSUES (attack effects, the 42-root promotion screen) |
| M9 | Android | The promotion screen on the test mod first (branch `test/capability-tests`, all 47 lines on Slice 1's units), then the shipped step |

Nothing is deleted or renamed in M1–M9: the six units and two types live on as hidden legacy objects.

**Decisions (user, 2026-10-18):** the plan with the legacy bridge is approved; the Moon and Strength policy branches
stay; cultivators take their own paths unless their clan has a signature path (see "AI"); the user's Marathon game is
over, so the legacy units can be deleted whenever the user says. Open: the attack animations (M6) and Gu for the
paths that have none.
