# Paths (流派) — MOD_SPEC_3 Phase B3

State on 2026-10-18, waiting at the B3 checkpoint (⛔ the user approves the list). No content JSON ships yet: after
approval, C3 turns this document into `data/paths.csv` + `tools/gen_paths.py` and proposes the Slice 1 migration
(Slice 1 already ships the Moon and Strength path policies and path × rank units; nothing changes before the user
approves the migration plan).

## How this was checked

* **Sources.** R = the raw Chinese text, cited by global chapter number (the numbering of the fan wiki's
  citations); the copy used is an unofficial upload, so it is never linked from the mod. F = the Reverend Insanity
  fan wiki (`reverend-insanity.fandom.com/wiki/<page>`), whose English names (a fan translation) are used here.
  Verdict rule: CANON = the name and its Chinese are attested in R **and** described on F. The research was done by
  subagents against R and F; only the verdicts are kept here (CLAUDE.md).
* **Attestation.** Every `X道` followed by a path marker (道痕, 蛊仙, 蛊师, 杀招, 仙蛊, 凡蛊, 境界, 流派, 宗师 /
  大宗师) was counted over the whole of R; the 46 paths below are everything that came out, plus the minor paths R
  names in prose. The best single passage is R ch1323 (the major paths by era and founder).
* **Every unique proposed here was run through the real checkers.** A throwaway prototype (the shipped `jsons/` plus
  all 46 lines: 184 tier promotions, 92 move statuses, 5 signature statuses, a stand-in essence stockpile; 300
  promotions, 979 conflict lines) passes `tools/check_all --mod <prototype> --no-self-test`: `lint_uniques` 2,660
  uniques, 0 errors, 0 warnings; Unciv 4.22.8's own validator 0 lines; the only warnings are missing icons.
  Autoplay on the prototype (6 games × 150 turns, Prince): 0 crashes, and the four AI clans held 264 path
  promotions, **264 on their main path** (see "AI"). Re-run: `tools/b3/gen_proto.py OUT && tools/check_all --mod OUT
  --no-self-test`; the tables below come from `tools/b3/paths_data.py` (`tools/b3/gen_tables.py`).
* What the prototype does **not** prove (C3 capability tests, one object each): the effects in battle of the
  signatures marked ⚠️ below, the move buttons, and how the promotion screen copes with 41 root lines.

## Decisions for the user (⛔)

1. **Killing path 杀道** [VERIFY]: R shows only "signs" of it in the last chapters (ch2233, ch2328); F calls it
   founded. Default: **left out** (46 lines). Including it adds a 47th line.
2. **Sub-paths** (phantom and restriction from rule, emotion and enchantment from wisdom, shadow from dark): default
   **own lines whose Master tier needs the parent's Master tier** (R ch1869: phantom attainment counts as rule path),
   compatible with the parent (no conflict penalty).
3. **Tier calibration.** MOD_SPEC_3 names four tiers; canon has nine (below). Default (a): the four named tiers,
   Master open at any rank, Grandmaster rank 3+, Great Grandmaster rank 6+, Supreme Grandmaster rank 8+ (inside the
   ≤4 budget; canon puts each tier one to two ranks higher, so this is ADAPTED). Option (b): a fifth promotion, so
   that tier 1 is "Initiate" (普通 / 准大师) and Supreme Grandmaster is the Venerable's alone (canon: all ten Venerables
   reached it, R ch1502) — over the ≤4 budget, needs approval.
4. **Transformation without `Can transform to [unit]`.** The palette's transformation unique needs a beast form per
   rank (9 more units, over the "9 + ≤1 unique per nation" Gu-unit budget) and a way back to the right rank. Default:
   `Double movement in [Forest]` (beast forms run where beasts run).
5. **Fire burns the land**: `Destroys tile improvements when attacking` hits Spirit Spring caves too (merciless, and
   the AI will do it). Alternative: a burning status like poison's.
6. **Bai's main path becomes Water** (F: the Bai clan specialises in water and ice; its emblem is the Stream Gu). In
   Slice 1 the Bai AI leans Moon as a balance choice (LORE_MAPPING question 11).

## The paths

Signature = the whole unique text, conditional included; no two paths share one (`tools/b3/gen_tables.py` asserts it). Every
pattern is documented in `uniques.md` 4.22.8; those from MOD_SPEC_3's palette are noted in "Signature notes".

| # | Path | Chinese | Family | Sub-path of | Source | Verdict | Signature (one unique) | Lore hook |
|---|---|---|---|---|---|---|---|---|
| 1 | Strength | 力道 | A |  | F Strength_Path; R ch597, 1064 | CANON | `No damage penalty for wounded units` | a tempered body keeps its force while hurt |
| 2 | Transformation | 变化道 | A |  | F Transformation_Path; R ch597, 1041 | CANON | `Double movement in [Forest]` | beast forms run where beasts run |
| 3 | Bone | 骨道 | A |  | F Bone_Path; R ch1736 | CANON | `[+20]% Strength <when defending>` | bone armour grown from one's own skeleton |
| 4 | Blood | 血道 | A |  | F Blood_Path; R ch1064, 2080 | CANON | `Heals [20] damage if it kills a unit` | blood taken from the slain feeds the killer |
| 5 | Sword | 剑道 | B |  | F Sword_Path; R ch1064 | CANON | `[+25]% Strength <when attacking>` | focused piercing, one of the five strongest attack paths (ch1064) |
| 6 | Blade | 刀道 | B |  | F Blade_Path; R ch1432 | CANON | `[+50]% to Flank Attack bonuses` | sweeping blade-qi cuts the flanks |
| 7 | Metal | 金道 | B |  | F Metal_Path; R ch1064 | CANON | `[+30]% Strength <vs cities>` | metal breaks walls (City-Crushing Hammer) |
| 8 | Weapon | 兵道 | B |  | F Weapon_Path; R ch2154 | CANON | `[+20]% Strength <when adjacent to a [Military] unit>` | a path for armies, built on human-path ideas |
| 9 | Fire | 炎道 | C |  | F Fire_Path; R ch1064, 1323 | CANON | `Destroys tile improvements when attacking` | fire burns the fields it fights over |
| 10 | Water | 水道 | C |  | F Water_Path; R ch1323 | CANON | `May travel on Water tiles without embarking` | water carries its own |
| 11 | Wood | 木道 | C |  | F Wood_Path; R ch1323 | CANON | `[15] HP when healing` | growth: wood mends what grows |
| 12 | Earth | 土道 | C |  | F Earth_Path; R ch1323, 1425 | CANON | `[+25]% Strength <when fighting in [Hill] tiles>` | rock and soil hold the high ground |
| 13 | Wind | 风道 | C |  | F Wind_Path; R ch1323 | CANON | `[1] Movement` | air currents and flight |
| 14 | Cloud | 云道 | C |  | F Cloud_Path; R ch752 | CANON | `Ignores terrain cost` | clouds carry the walker over any ground |
| 15 | Ice Snow | 冰雪道 | C |  | F Ice_Path, Snow_Path; R ch1323 | CANON | `[Target Unit] loses [1] movement <upon damaging a [Military] unit>` | cold that numbs and slows |
| 16 | Lightning | 雷道 | C |  | F Lightning_Path; R ch1064 | CANON | `[+30]% Strength <when above [1] movement>` | the first strike, before the thunder |
| 17 | Poison | 毒道 | C |  | F Poison_Path; R ch1293 | CANON | `[Target Unit] gains the [Poisoned] status for [3] turn(s) <upon damaging a [Military] unit>` | hidden venom that keeps working |
| 18 | Light | 光道 | D |  | F Light_Path; R ch1323 | CANON | `Can move after attacking` | light is speed |
| 19 | Dark | 暗道 | D |  | F Dark_Path; R ch1323 | CANON | `Invisible to others` | darkness hides auras and moves |
| 20 | Shadow | 影道 | D | Dark | F Shadow_Path; R ch2284 | CANON | `[+30]% Strength <vs [Wounded] units>` | a dark-path offshoot that strikes the weakened |
| 21 | Star | 星道 | D |  | F Star_Path; R ch1323, 2204 | CANON | `[2] Sight` | conjured stars light the field |
| 22 | Moon | 月道 | D |  | F Moon_Path; R ch795, 2169 | CANON | `Before engaging in combat performs an extra ranged attack with [40]% of melee combat strength` | the moon blade, as in Slice 1 |
| 23 | Sound | 音道 | D |  | F Sound_Path; R ch1425 | CANON | `[-10]% Strength for enemy [Military] units in adjacent [All] tiles` | sound spreads and rattles |
| 24 | Illusion | 幻道 | D |  | F Illusion_Path; R ch963 | CANON | `Withdraws before melee combat` | the blow lands on an illusion |
| 25 | Wisdom | 智道 | E |  | F Wisdom_Path; R ch1323, 2086 | CANON | `Can see invisible [All] units` | deduction sees through hiding |
| 26 | Emotion | 情道 | E | Wisdom | F Emotion_Path; R ch1156 | CANON | `[+25]% Strength <when below [50] HP>` | feeling surges when hurt |
| 27 | Enchantment | 魅道 | E | Emotion | F Enchantment_Path; R ch338, 1323 | CANON | `[Target Unit] gains the [Charmed] status for [1] turn(s) <upon damaging a [Military] unit>` | charm saps the will to strike |
| 28 | Soul | 魂道 | E |  | F Soul_Path; R ch1505 | CANON | `[This Unit] gains [10] XP <upon defeating a [Military] unit>` | the soul grows by taking souls |
| 29 | Dream | 梦道 | E |  | F Dream_Path; R ch1326, 1619 | CANON | `[+50]% XP gained from combat` | dream realms pour attainment into the explorer (ch1326) |
| 30 | Enslavement | 奴道 | E |  | F Enslavement_Path; R ch1323, 870 | CANON | `May capture killed [Barbarians] units` | beasts beaten become beasts commanded |
| 31 | Time | 宙道 | F |  | F Time_Path; R ch1323, 1754 | CANON | `[1] additional attacks per turn` | more time inside the same turn |
| 32 | Space | 宇道 | F |  | F Space_Path; R ch1323 | CANON | `All tiles cost 1 movement` | distance folds |
| 33 | Rule | 律道 | F |  | F Rule_Path; R ch1323, 1787 | CANON | `Ignores Zone of Control` | the laws bend around the walker |
| 34 | Phantom | 虚道 | F | Rule | F Phantom_Path; R ch1787, 1869 | CANON | `[This Unit] gains the [Phantom Veil] status for [1] turn(s) <upon losing at least [30] HP in a single attack>` | turns insubstantial after a heavy blow; defensive below rank 6 (F) |
| 35 | Restriction | 禁道 | F | Rule | F Restriction_Path; R ch1042, 1787 | CANON | `[Target Unit] gains the [Sealed] status for [2] turn(s) <upon damaging a [Military] unit>` | seals cut the target off from healing |
| 36 | Luck | 运道 | F |  | F Luck_Path; R ch1323, 1859 | CANON | `[+30]% Strength <with [50]% chance>` | fortune turns, for better or not at all |
| 37 | Heaven | 天道 | F |  | F Heaven_Path; R ch2196, 2285 | CANON | `[+25]% Strength <when fighting units from a Civilization with more Cities than you>` | heaven's balance strikes the strongest (Heaven's Will, MOD_SPEC_2 #10) |
| 38 | Qi | 气道 | F |  | F Qi_Path; R ch1323, 2001 | CANON | `[+3] Strength` | formless qi adds raw force, which counts for less at high rank |
| 39 | Refinement | 炼道 | G |  | F Refinement_Path; R ch1326, 1552 | CANON | `[-30]% Gold cost of upgrading` | refiners raise their own Gu more cheaply |
| 40 | Formation | 阵道 | G |  | F Formation_Path; R ch1323, 1326 | CANON | `[+15]% Strength bonus for [Military] units within [1] tiles` | a formation strengthens everyone inside it |
| 41 | Food | 食道 | G |  | F Food_Path; R ch1457 | CANON | `[-25]% maintenance costs` | the food path feeds Gu cheaply |
| 42 | Pill | 丹道 | G |  | F Pill_Path; R ch1712, 1865 | CANON | `Unit will heal every turn, even if it performs an action` | pills heal on the march |
| 43 | Information | 信道 | G |  | F Information_Path; R ch1323, 705 | CANON | `Can see over obstacles` | messages and records reach past the hills |
| 44 | Human | 人道 | G |  | F Human_Path; R ch1729 | CANON | `All adjacent units heal [10] HP when healing` | human-path marks clash with nothing, so it helps any ally (ch1729) |
| 45 | Painting | 画道 | G |  | F Painting_Path; R ch1721, 2204 | CANON | `[+20]% Strength <when fighting in [Friendly Land] tiles>` | paintings guard the home that hangs them |
| 46 | Theft | 偷道 | G |  | F Theft_Path; R ch1323, 1528 | CANON | `Earn [50]% of killed [Military] unit's [Cost] as [Gold]` | gain without paying the cost |

### Not in the list

* **Killing 杀道** — decision 1.
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

| Family | Paths | Play feel | Mortal move template | Immortal move template | Icon colour |
|---|---|---|---|---|---|
| A. Body & Beast | Strength, Transformation, Bone, Blood | melee, self-buffs, sustain | +25% Strength | +50% Strength, heal 30 HP | [150, 40, 40] |
| B. Edge & War | Sword, Blade, Metal, Weapon | burst damage, sieges | +40% Strength when attacking | +80% Strength when attacking | [140, 150, 160] |
| C. Five Phases & Weather | Fire, Water, Wood, Earth, Wind, Cloud, Ice Snow, Lightning, Poison | terrain, mobility, damage over time | +20% Strength, 10 extra damage to the target | +40% Strength, 25 extra damage | [60, 130, 70] |
| D. Sky & Shade | Light, Dark, Shadow, Star, Moon, Sound, Illusion | stealth, sight, skirmish | +2 movement now, +20% Strength when attacking | +3 movement now, +40% Strength when attacking | [70, 60, 140] |
| E. Mind & Spirit | Wisdom, Emotion, Enchantment, Soul, Dream, Enslavement | control, growth, captives | the target is Shaken (-20% Strength) for 2 turns | Shaken target, +30% Strength | [130, 70, 150] |
| F. Law & Cosmos | Time, Space, Rule, Phantom, Restriction, Luck, Heaven, Qi | rare rule-bending effects | 1 additional attack this turn | 1 additional attack, +40% Strength | [190, 160, 60] |
| G. Craft & Society | Refinement, Formation, Food, Pill, Information, Human, Painting, Theft | economy, healing, support | heal 40 HP, +15% Strength | heal 80 HP, +30% Strength | [150, 100, 50] |

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
| Master | none; a sub-path also needs its parent's Master | the signature, the conflict lines, the AI lock | `[+10]% Strength` |
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

| Path | Family template | Mortal move (Grandmaster) | Tag | Immortal move (Great Grandmaster) | Tag |
|---|---|---|---|---|---|
| Strength | A | Self-Reliance 自力更生 | ADAPTED: a Gu | Myriad Self 万我 | CANON |
| Transformation | A | Flying Bear Change 飞熊变 | CANON, lit. name | Ancient Sword Dragon 上古剑蛟 | CANON |
| Bone | A | Bone Spear 骨枪 | ADAPTED: a Gu | Bone Spike 骨刺 | ADAPTED: a rank-6 Immortal Gu |
| Blood | A | Blood Skull 血颅 | ADAPTED: a Gu | Blood Deity 血神子 | CANON |
| Sword | B | Sword Escape 剑遁 | ADAPTED: a Gu | Five Finger Fist Heart Sword 五指拳心剑 | CANON |
| Blade | B | Edge 刃 | ADAPTED: a Gu | Autumn Blade Sweep | INVENTED, after Autumn Blade Plain 秋刀原 |
| Metal | B | Iron Rain | INVENTED | City-Crushing Hammer 碎城锤 | CANON, lit. name |
| Weapon | B | Weapon Array | INVENTED | Hundred Weapons | INVENTED |
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

Implementation (979 lines, generated): on the earlier path's Master,
`[-10]% Strength <for units with [<other> Master]> <hidden from users>` per pair, plus one visible
`Comment [...]` line. The same matrix gives the negative amounts of MOD_SPEC_2 #4's dao-mark countables
(`[relativeAmount]% Strength <for every [positiveAmount] [countable]>` on `[[<Path> Path] Buildings]`). Tension target
(MOD_SPEC_3): a single-path unit at Grandmaster (+25%, one signature, a move) against a three-path unit of the same
rank holding three Masters (+30% −30% for three pairs, three signatures); duels in C3 decide the numbers.

## AI

* **Main path lock.** Each path's Master carries `Unavailable <for [{AI player} {Major} {non-[<owner>]}] Civilizations>`:
  an AI major can only enter its own main path; humans and city-states can enter any. The AI buys every promotion it
  can afford [src `NextTurnAutomation.applyPromotions`: weighted random while XP lasts], so weights alone would push
  AI units into off-path lines whenever the next main tier is rank-gated; the lock makes the main-path share 100%
  (prototype: 264 of 264), above MOD_SPEC_3's ≥80% target. The A3 weight math stays for the choice between path
  tiers (`[+400]% weight to this choice for AI decisions`), Refine Gu and generic promotions.
* **Canon cost of the lock:** immortals often keep a secondary path (Venerables a hidden specialty, R ch2204); the AI
  will not. A designated AI secondary would break the 80% target, because the AI buys whatever is left.
* **Main paths:** Gu Yue — Moon (Slice 1; Moonlight Gu's path is [VERIFY], LORE_MAPPING); Bai — Water (decision 6);
  Xiong — Strength (Bear Strength Gu, CANON); Wu — Strength (Wu Ji, CANON, LORE_MAPPING). Proposals for the arc majors
  (MOD_SPEC_2 Phase B decides the majors): Heavenly Court — Wisdom (Star Constellation's true inheritance stays in the
  Court); Huang Jin / Longevity Heaven — Luck (Giant Sun); Tang (Western Desert) — Dream; Shen or the Zombie Alliance
  (Eastern Sea) — [VERIFY].

## Budget (MOD_SPEC_3)

| Item | Cap | Here |
|---|---|---|
| Paths | all canonical (expected ~35) | 46 (41 + 5 sub-paths); 47 with killing |
| Promotions per path | ≤4 | 4 tiers |
| General promotions | ≤10 | 5 statuses (Poisoned, Charmed, Sealed, Phantom Veil, Shaken) |
| Killer moves | ≤2 per path | 2 per path (92 move statuses) |
| Gu units | 9 + ≤1 unique per nation | unchanged here (decision 4 keeps it) |
| Icons | placeholders coloured by family | family colours above |

## Risks for C3

* **The promotion screen** offers a human unit 41 Master tiers at once (sub-paths open later). Unciv lays promotions
  out as a tree; whether 41 roots stay usable on Android needs a look in game. Fallbacks: gate each family's Masters
  behind a family tech (`Only available <after discovering [techFilter]>`; 7 techs, which also lengthens the tech tree
  that ends near turn 120, BALANCE.md item 6), or open a path only where its academy stands.
* **Slice 1 overlap:** the Moon and Strength path policies, the Moon/Strength unit types, the generic Killer Move
  promotion and Refine Gu. C3's migration plan maps them onto the lines above; nothing is renamed or deleted without
  approval (MOD_SPEC_3 Boundaries).
* **XP budget:** path tiers now compete with Refine Gu for the AI's XP; C3 autoplay checks the refinement ladder
  still moves (AUTOPLAY round 5d).
