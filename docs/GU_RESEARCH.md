# Gu and killer-move research (Phase D, 2026-11-02)

The research was done by a subagent on 2026-11-02, the user having allowed source research ("riset sumber semuanya").
It searched all 2,335 chapters of the raw Chinese text (hetushu mirror, book 7640) and the fan wiki's API. This file
keeps its verdicts, because research notes do not survive the container.

* **R** cites the raw text as volume and chapter (V#c#). To get the wiki's global chapter number, add V2 +199,
  V3 +404, V4 +648, V5 +1020 or V6 +1965 (accurate to about 2 chapters).
* **W** cites the wiki.

What came out of it:

* **The catalog itself.** The 113 Gu chosen are in `data/gu_catalog.csv`. Their names, sources and verdicts are in
  docs/PATHS.md "Gu catalog".
* **Not used yet.** About 40 more canon Gu were found and not used. The killer moves below are the input for the
  combination moves.

## Findings that change what we believed

* **Immortal Gu are unique.** In the novel every immortal Gu is one of a kind: 「仙蛊唯一，每一只仙蛊都是独一无二的」
  (V5c666, also V3c161, V5c108). The catalog's unit-held immortal Gu are a game compromise the user chose ("common
  immortal Gu 6-9 held by units"), marked in their civilopedia text. The canon one-of-a-kind immortal Gu stay wonders.
* **Wiki errors.** The raw text disagrees with the wiki on these:
  * the wiki's "Break Luck Gu 连运蛊" is Connect Luck, which the mod already has;
  * the wiki's "Mature Bamboo 熟竹仙蛊" is 成竹仙蛊 in the text;
  * the wiki's "Time Luck 时光运" is 时运仙蛊 in the text.
* **Possible duplicate.** Brown Bear Innate Strength 棕熊本力蛊 (rank 2, V2c76) may be the mod's Bear Strength Gu, so
  it is not used.
* **Weapon path.** Its only named Gu are Iron Rod Gu 铁棒蛊 and Whip Gu 皮鞭蛊 (V6c320), both without a rank. Both are
  in the catalog with an adapted rank.
* **Paths with no named Gu.** The text names no Gu for the illusion, painting and pill paths, and no mortal Gu for the
  formation path. Their catalog Gu are INVENTED.

## Killer moves built from two or more named Gu

These moves are the canon pool for the curated combination moves the user asked for: each would be a unit action
unlocked by holding the component Gu.

| Move | Chinese | Path | Component Gu | User | Source | Verdict |
|---|---|---|---|---|---|---|
| Four Arm Wind King | 四臂风王 | strength | Wind Overlord 风霸王 + Tyrant Strength 霸力 (for Borrow Strength) | Fang Yuan | R V3c155 | CANON |
| Four Arm Earth King | 四臂地王 | strength | Earth Overlord 土霸王 + Tyrant Strength 霸力 | Fang Yuan | R V3c134, V3c141 | CANON (components partly inferred) |
| Eight Beast Phantoms | 八大兽影 | strength | All-Out Effort 全力以赴, Bitter Strength 苦力, Self-Reliance 自力更生, Strength Qi 力气 | Fang Zheng | R V2c122 | CANON |
| Six Arm Heavenly Corpse King | 六臂天尸王 | strength / transformation | Borrow Strength 借力 core; six flying-zombie Gu (Asura and five more) | Mo Yao's legacy | R V3c174, V4c1 | CANON |
| Myriad Self | 万我 | strength / human | Self Strength 我力, Strength Qi 力气, Group Strength 群力, All-Out Effort, later many more | Fang Yuan | R V4c33, V4c120, V5c550 | CANON |
| Reverse Flow Protection Seal | 逆流护身印 | strength / human | Perseverance 坚持 + Pulling Water 挽澜 | Fang Yuan | R V5c271, V5c550 | CANON |
| Spring Star Rain | 春星雨 | star | Star Rain 星雨 (many) + Spring Wind 春风 + Star Shoot 星芽 (spent) | Star Lord, then Fang Yuan | R V4c18, V4c62 | CANON |
| Spiral Drill Star Spear | 螺旋钻星枪 | star | Spiral Bone Spear 螺旋骨枪 + Star River 星河 + Star Dart 星镖 + Shooting Star 流星 | Star Lord | R V4c18 | CANON |
| Splendid Star Armour | 灿烂星甲 | star | Starlight 星光 (many) + Nemesis Star 克星 + Star Shield 星盾 | Star Lord | R V4c18 | CANON |
| Myriad Star Fireflies | 万星飞萤 | wisdom / star | Starlight Firefly 星萤 swarms carrying star thoughts 星念 | Dong Fang Chang Fan | R V4c144 | CANON (partial list) |
| Blood Torrent | 血漂流 | blood | Blood Asset 血本 + mortal Gu | Fang Yuan | R V5c40 | CANON |
| Life-Staking Blood Print | 舍命血印 | blood | Blood Asset core | Fang Yuan | R V5c40 | CANON |
| Blood Healing Lake | 血愈湖 | blood | Blood Asset core (healing) | Fang Yuan | R V5c40 | CANON |
| Blood Turns Cold | 血渐冷 | blood | Cold Blood 冷血 (also Blood Feud 血仇) | Fang Zheng | R V5c664 | move CANON, core [VERIFY] |
| Sword Marks Targeting Death | 剑痕索命 | sword | Flying Sword 飞剑 core | Fang Yuan | R V5c33, V5c110 | CANON |
| One Sword Unrestrained | 一剑纵横 | sword | Sword Escape 剑遁 (one core) | Bo Qing | R V4c346 | CANON |
| Sword Flood-Dragon Transformation | 剑蛟变 | transformation | Change Form 变形 + Jiao Claw, Eye, Horn, Scale 蛟爪/睛/角/鳞 | Fang Yuan | R V5c176 | CANON |
| Divination Tortoise Transformation | 卜卦龟变化 | transformation | Change Form + Divination Tortoise Back 卜卦龟背 | Fang Yuan | R V5c279, V5c289 | CANON |
| Flying Bear Transformation | 飞熊变 | transformation | Change Form + Flying Bear Strength 飞熊之力 | Fang Yuan | R V5c78, V5c176 | CANON |
| Vaguely Familiar Face | 见面似相识 | transformation | three immortal cores, two transformation (Change Form) | Thieving Heaven's legacy | R V4c95, V4c221 | CANON |
| Ghost Official Garment | 鬼官衣 | soul | Change Soul 换魂 + Cleanse Soul 净魂 | Fang Yuan | R V5c427, V5c450 | CANON |
| Great Thief Ghost Hand | 大盗鬼手 | theft | Great Thief 大盗, on the move Ghostly Concealment 鬼不觉 | Fang Yuan | R V5c503, V5c508 | CANON |
| Time Assist Luck | 时济运 | time / luck | Time Luck 时运 + Inch of Time 寸光阴 (spent) | Li Shan, then Fang Yuan | R V4c168, V4c173 | CANON |
| Unravel Dream | 解梦 | dream | Unravel Mystery 解谜 core + many mortal dream Gu | Fang Yuan | R V4c124, V4c128 | CANON |
| Mature Bamboo Chest | 成竹在胸 | wood | Mature Bamboo 成竹 core | Fang Yuan | R V5c760 | CANON |
| Jade Flow Pearl | 翠流珠 | space | Fixed Immortal Travel 定仙游 core + space and refinement immortal Gu | Fang Yuan | R V5c756 | CANON |
| Five Restriction Profound Light Qi | 五禁玄光气 | rule | Region 界 + Limit 限 + many mortal Gu | Tao Zhu's legacy | R V5c766, V6c99 | CANON |
| Limitless Search Lock | 无极搜锁 | space / restriction | Search Lock 搜锁 + Fixed Star 定星 | Tie clan elders | R V2c154, V2c163, V2c199 | CANON |
| Righteous Army | 正义之师 | human | Justice 正义 + Soldier 兵卒 + Squad Leader 伍长 + Ten-Man Leader 什长 | a Tie clan immortal (planned) | R V6c296 | CANON |
| Triple Qi Retraction | 三气归来 | qi | Heaven Qi 天气 + Earth Qi 地气 + Human Qi 人气 | Duke Long | R V5c929, V6c59 | CANON |
| Nine Shines | 九曜 | light | nine "shine" Gu (Green 绿曜, Blue 蓝曜, Red 红曜...) | Zheng Shan Chuan | R V4c184 | CANON |
| Ice Blade Storm | 冰刃风暴 | ice / wind | Whirling Heel 旋踵 + Whirlwind 旋风 + Ice Knife 冰刀 | Bai Ning Bing | R V2c100 | CANON |
| Peerless Crescent Moon Slash | 无双偃月斩 | moon | Crescent Moon 偃月 + two rank-6 immortal Gu, two users | Ling Mei, Ao Xue | R V4c61, V4c274 | CANON |
| Seventy-Percent Expended Strength | 七分费力 | strength | Expend Strength 费力 core | a Gu Immortal | R V6c248 | CANON |
| Humble Reciprocation | 谦谦有礼 | wisdom | Humility 谦虚 core | Ming Hao | R V6c193 | CANON |
| Heaven Envies Heroic Geniuses | 天妒英才 | heaven | Heaven's Envy 天妒 (with Heavenly Secret, Heavenly Birth, Heavenly Web) | Fang Yuan | R V6c200, V6c261, V6c319 | CANON |
| Three Hearts Combine Soul | 三心合魂 | soul | merges three Gu Masters' souls; components on W only | Dong Fang clan | R V3c102; W | move CANON, components [VERIFY] |
| My Glorious Spear | 荣耀吾枪 | light / wisdom | Extreme Light 太光 + Self Will 我意 | Xiao Mang | R V2c194; W | CANON |
| One Song of Yang Pass | 一曲阳关 | sound | many mortal Gu; Pass Gu 关 would lengthen it | Feng Jiu Ge | R V5c402 | CANON |
| Dreamy Light Smoke | 梦里轻烟 | dream | Dream Token 如梦令 | Fang Yuan | R V6c131 | CANON (components from co-mention) |
| Nine Cloud Ring | 九云环 | cloud | nine cloud rings; W says Landscape as Before | Tai Bai Yun Sheng | R V4c21; W | move CANON, components [VERIFY] |
| Year Beast Summoning | 年兽召来 | time | Year Gu + Years Flow Like Water | Fang Yuan | W ch1137 only | [VERIFY] |
