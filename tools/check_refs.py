#!/usr/bin/env python3
"""Cross-reference checks between ruleset objects, approximating Unciv's BaseRulesetValidator
(core/.../models/ruleset/validation/BaseRulesetValidator.kt), plus project rules from MOD_SPEC.md.

Covers: requiredTech, prerequisites, upgradesTo, obsoleteTech, replaces, uniqueTo, requiredResource,
era starting units and buildings, difficulty starting units, victory milestones and spaceship parts,
events named in `Triggers a [...] event` (missing, orphaned, circular), AI weights on event choices,
base-ruleset completeness, and an image for every object (warnings only).

Usage: tools/check_refs.py [--mod PATH] [--quiet]
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from common import BUILTIN_IMAGES, Reporter, Ruleset, mod_root_from_args, require_ref
from uniques_db import placeholder_key, placeholder_params, remove_modifiers

# From QuestName in core/.../models/ruleset/Quest.kt. The docs table says "Contest Technology"; the engine
# (and the bundled Quests.json) use "Contest Technologies" - a docs error.
QUEST_NAMES = {"Route", "Clear Barbarian Camp", "Construct Wonder", "Connect Resource", "Acquire Great Person",
               "Conquer City State", "Find Player", "Find Natural Wonder", "Give Gold", "Pledge to Protect",
               "Contest Culture", "Contest Faith", "Contest Technologies", "Invest", "Bully City State",
               "Denounce Civilization", "Spread Religion"}
MILESTONES = {"Build []", "Anyone should build []", "Add all [] in capital", "Destroy all players",
              "Capture all capitals", "Complete [] Policy branches", "Win diplomatic vote",
              "Become the world religion", "Have highest score after max turns", "Have at least [] []",
              "Have more [] than each player's []"}
CITY_STATE_PERSONALITIES = {"Friendly", "Neutral", "Hostile", "Irrational"}
MOD_CONSTANTS = {"maxXPfromBarbarians", "cityStrengthBase", "cityStrengthPerPop", "cityStrengthFromTechsMultiplier",
                 "cityStrengthFromTechsExponent", "cityStrengthFromTechsFullMultiplier", "cityStrengthFromGarrison",
                 "baseCityBombardRange", "cityWorkRange", "cityExpandRange", "cityAirUnitCapacity",
                 "unitSupplyPerPopulation", "minimalCityDistance", "minimalCityDistanceOnDifferentContinents",
                 "unitUpgradeCost", "naturalWonderCountMultiplier", "naturalWonderCountAddedConstant",
                 "ancientRuinCountMultiplier", "spawnIceBelowTemperature", "maxLakeSize", "riverCountMultiplier",
                 "minRiverLength", "maxRiverLength", "religionLimitBase", "religionLimitMultiplier", "pantheonBase",
                 "pantheonGrowth", "workboatAutomationSearchMaxTiles", "maxSpyRank", "spyRankSkillPercentBonus",
                 "minimumWarDuration", "baseTurnsUntilRevolt", "cityStateElectionTurns",
                 "maxImprovementTechErasForward", "goldGiftMultiplier", "goldGiftTradeMultiplier",
                 "goldGiftDegradationMultiplier"}
def as_list(value) -> list:
    """List-typed fields with a wrong type are check_schema's job; never iterate a string here."""
    return value if isinstance(value, list) else []


def as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


AI_WEIGHT_KEY = "[]% weight to this choice for AI decisions"
TRIGGER_EVENT_KEY = "Triggers a [] event"


class RefChecker:
    def __init__(self, rs: Ruleset, r: Reporter):
        self.rs, self.r = rs, r
        n = rs.names
        self.units = n("Units.json")
        self.unit_types = rs.names_with_fallback("UnitTypes.json")
        self.buildings = n("Buildings.json")
        self.techs = n("Techs.json")
        self.eras = n("Eras.json")
        self.policies = {p["name"] for p in rs.policies()}
        self.branches = {b["name"] for b in rs.policy_branches()}
        self.nations = n("Nations.json")
        self.nation_uniques = {u for o in rs.named("Nations.json") for u in (as_list(o.get("uniques")))}
        self.promotions = n("UnitPromotions.json")
        self.resources = n("TileResources.json")
        self.improvements = n("TileImprovements.json")
        self.terrains = n("Terrains.json")
        self.specialists = n("Specialists.json")
        self.religions = n("Religions.json")
        self.personalities = n("Personalities.json")
        self.city_state_types = rs.names_with_fallback("CityStateTypes.json")
        self.difficulties = rs.names_with_fallback("Difficulties.json")
        self.victories = rs.names_with_fallback("VictoryTypes.json")
        self.events = n("Events.json")

    # --- helpers ---------------------------------------------------------------------------
    def need(self, where: str, field: str, value, pool: set[str], kind: str, severity: str = "ERROR"):
        if value in (None, "") or not isinstance(value, str):  # wrong types are check_schema's job
            return
        if value not in pool:
            msg = f"{field} \"{value}\" is not a {kind} in the mod"
            (self.r.error if severity == "ERROR" else self.r.warn)(where, msg)

    def unique_to(self, where: str, value):
        if value and value not in self.nations and value not in self.nation_uniques and value != "Barbarians":
            self.r.warn(where, f"uniqueTo \"{value}\" matches no nation or nation unique (Unciv treats it as a civFilter)")

    def check_duplicates(self, filename: str, objects: list[dict]):
        seen = defaultdict(int)
        for o in objects:
            seen[o["name"]] += 1
        for name, count in seen.items():
            if count > 1:
                self.r.error(f"{filename} > {name}", f"defined {count} times")

    # --- per file ---------------------------------------------------------------------------
    def units_(self):
        units = self.rs.named("Units.json")
        self.check_duplicates("Units.json", units)
        for u in units:
            w = f"Units.json > {u['name']}"
            self.need(w, "unitType", u.get("unitType"), self.unit_types, "unit type")
            self.need(w, "requiredTech", u.get("requiredTech"), self.techs, "tech")
            self.need(w, "obsoleteTech", u.get("obsoleteTech"), self.techs, "tech")
            self.need(w, "upgradesTo", u.get("upgradesTo"), self.units, "unit")
            self.need(w, "replaces", u.get("replaces"), self.units, "unit")
            self.need(w, "requiredResource", u.get("requiredResource"), self.resources, "resource")
            self.unique_to(w, u.get("uniqueTo"))
            if u.get("replaces") and not u.get("uniqueTo"):
                self.r.warn(w, "has replaces but no uniqueTo - replacement only happens for a unique unit")
            for p in as_list(u.get("promotions")):
                self.need(w, "promotion", p, self.promotions, "promotion")
            if u.get("upgradesTo") == u["name"]:
                self.r.error(w, "upgrades to itself")
        # upgrade cycles
        nxt = {u["name"]: u.get("upgradesTo") for u in units}
        for start in nxt:
            seen, cur = [], start
            while cur in nxt and cur not in seen:
                seen.append(cur)
                cur = nxt[cur]
            if cur == start and len(seen) > 1:
                self.r.error(f"Units.json > {start}", "upgrade cycle: " + " -> ".join(seen + [start]))
        # unit auto-upgrading at obsoleteTech must be able to build its upgrade by then
        prereq = self.tech_prereq_closure()
        by_name = {u["name"]: u for u in units}
        for u in units:
            ob, up = u.get("obsoleteTech"), u.get("upgradesTo")
            if ob in self.techs and up in by_name:
                req = by_name[up].get("requiredTech")
                if req and req != ob and req not in prereq.get(ob, set()):
                    self.r.warn(f"Units.json > {u['name']}", f"obsolete at {ob}, but its upgrade {up} needs {req}, "
                                                             f"which {ob} does not require")
        if units and not any(any(str(x).startswith("Founds a new city") for x in (as_list(u.get("uniques")))) for u in units):
            self.r.error("Units.json", "no city-founding unit (no unit has \"Founds a new city\")")

    def buildings_(self):
        buildings = self.rs.named("Buildings.json")
        self.check_duplicates("Buildings.json", buildings)
        for b in buildings:
            w = f"Buildings.json > {b['name']}"
            self.need(w, "requiredTech", b.get("requiredTech"), self.techs, "tech")
            self.need(w, "requiredBuilding", b.get("requiredBuilding"), self.buildings, "building")
            self.need(w, "replaces", b.get("replaces"), self.buildings, "building")
            self.need(w, "requiredResource", b.get("requiredResource"), self.resources, "resource")
            self.unique_to(w, b.get("uniqueTo"))
            for res in as_list(b.get("requiredNearbyImprovedResources")):
                self.need(w, "requiredNearbyImprovedResources", res, self.resources, "resource")
            for gp in as_dict(b.get("greatPersonPoints")):
                self.need(w, "greatPersonPoints", gp, self.units, "unit", "WARNING")
            for sp in as_dict(b.get("specialistSlots")):
                self.need(w, "specialistSlots", sp, self.specialists, "specialist")
            if b.get("cost", -1) == -1 and not b.get("requiredTech"):
                self.r.warn(w, "no cost and no requiredTech: cost falls back to a tech column that does not exist")

    def tech_prereq_closure(self) -> dict[str, set[str]]:
        direct = {t["name"]: set(as_list(t.get("prerequisites"))) for t in self.rs.techs()}
        closure: dict[str, set[str]] = {}

        def visit(name, stack):
            if name in closure:
                return closure[name]
            if name in stack:
                return set()
            stack.add(name)
            result = set()
            for p in direct.get(name, ()):
                result |= {p} | visit(p, stack)
            stack.discard(name)
            closure[name] = result
            return result

        for name in direct:
            visit(name, set())
        return closure

    def techs_(self):
        techs = self.rs.techs()
        self.check_duplicates("Techs.json", techs)
        closure = self.tech_prereq_closure()
        positions = {}
        col_of = {x["name"]: x["_column"].get("columnNumber", 0) for x in techs}
        for t in techs:
            w = f"Techs.json > {t['name']}"
            column = t["_column"]
            self.need(w, "column era", column.get("era"), self.eras, "era")
            pos = (column.get("columnNumber"), t.get("row", 0))
            if pos in positions:
                self.r.error(w, f"same row and column as {positions[pos]}")
            positions[pos] = t["name"]
            for p in as_list(t.get("prerequisites")):
                self.need(w, "prerequisite", p, self.techs, "tech")
                if t["name"] in closure.get(p, set()):
                    self.r.error(w, f"{t['name']} and {p} require each other (cycle)")
            for p in as_list(t.get("prerequisites")):
                if p in col_of and col_of[p] >= column.get("columnNumber", 0):
                    self.r.warn(w, f"prerequisite {p} is not in an earlier column")
                if any(p in closure.get(o, set()) for o in (as_list(t.get("prerequisites"))) if o != p):
                    self.r.info(w, f"prerequisite {p} is already implied by another prerequisite")

    def policies_(self):
        branches = self.rs.policy_branches()
        self.check_duplicates("Policies.json", self.rs.policies())
        for b in branches:
            w = f"Policies.json > {b['name']}"
            self.need(w, "era", b.get("era"), self.eras, "era")
            for key in as_dict(b.get("priorities")):
                self.need(w, "priorities key", key, self.victories | {"Neutral"}, "victory type", "WARNING")
            members = [m for m in as_list(b.get("policies")) if isinstance(m, dict)]
            if not any(m.get("name") == f"{b['name']} Complete" for m in members):
                self.r.warn(w, f"no finisher named \"{b['name']} Complete\"")
            spots = {}
            for m in members:
                mw = f"Policies.json > {b['name']} > {m.get('name')}"
                for req in as_list(m.get("requires")):
                    self.need(mw, "requires", req, self.policies, "policy")
                if m.get("name", "").endswith(" Complete"):
                    continue
                spot = (m.get("row"), m.get("column"))
                if spot in spots:
                    self.r.warn(mw, f"same row/column as {spots[spot]}")
                spots[spot] = m.get("name")

    def promotions_(self):
        promos = self.rs.named("UnitPromotions.json")
        self.check_duplicates("UnitPromotions.json", promos)
        prereqs = {p["name"]: set(as_list(p.get("prerequisites"))) for p in promos}
        for p in promos:
            w = f"UnitPromotions.json > {p['name']}"
            for pre in as_list(p.get("prerequisites")):
                self.need(w, "prerequisite", pre, self.promotions, "promotion")
            for ut in as_list(p.get("unitTypes")):
                self.need(w, "unitType", ut, self.unit_types, "unit type")
        for start in prereqs:  # circular prerequisites
            stack, seen = [start], set()
            while stack:
                cur = stack.pop()
                for nxt in prereqs.get(cur, ()):
                    if nxt == start:
                        self.r.error(f"UnitPromotions.json > {start}", "circular prerequisites")
                        stack = []
                        break
                    if nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)

    def map_objects_(self):
        terrains = self.rs.named("Terrains.json")
        self.check_duplicates("Terrains.json", terrains)
        base = {t["name"] for t in terrains if t.get("type") in ("Land", "Water")}
        for t in terrains:
            w = f"Terrains.json > {t['name']}"
            for o in as_list(t.get("occursOn")):
                self.need(w, "occursOn", o, self.terrains, "terrain")
            if t.get("turnsInto"):
                self.need(w, "turnsInto", t["turnsInto"], base, "base terrain")
        if self.rs.is_base_ruleset or terrains:
            if not any(t.get("type") == "Land" and not t.get("impassable") for t in terrains):
                self.r.error("Terrains.json", "no passable Land terrain")
            if not any(t.get("type") == "Water" for t in terrains):
                self.r.error("Terrains.json", "no Water terrain (docs: base rulesets need at least one Land and one Water)")
        for i in self.rs.named("TileImprovements.json"):
            w = f"TileImprovements.json > {i['name']}"
            self.need(w, "techRequired", i.get("techRequired"), self.techs, "tech")
            self.need(w, "replaces", i.get("replaces"), self.improvements, "improvement")
            self.unique_to(w, i.get("uniqueTo"))
            for t in as_list(i.get("terrainsCanBeBuiltOn")):  # validator also accepts "Land" / "Water"
                self.need(w, "terrainsCanBeBuiltOn", t, self.terrains | {"Land", "Water"}, "terrain")
        for res in self.rs.named("TileResources.json"):
            w = f"TileResources.json > {res['name']}"
            self.need(w, "revealedBy", res.get("revealedBy"), self.techs, "tech")
            self.need(w, "improvement", res.get("improvement"), self.improvements, "improvement")
            for i in as_list(res.get("improvedBy")):
                self.need(w, "improvedBy", i, self.improvements, "improvement")
            for t in as_list(res.get("terrainsCanBeFoundOn")):
                self.need(w, "terrainsCanBeFoundOn", t, self.terrains, "terrain")

    def nations_(self):
        nations = self.rs.named("Nations.json")
        self.check_duplicates("Nations.json", nations)
        majors = 0
        for nat in nations:
            w = f"Nations.json > {nat['name']}"
            special = nat["name"] in ("Barbarians", "Spectator")
            cst = nat.get("cityStateType")
            self.need(w, "cityStateType", cst, self.city_state_types, "city-state type")
            if nat.get("personality"):
                pool = self.personalities | (CITY_STATE_PERSONALITIES if cst else set())
                self.need(w, "personality", nat["personality"], pool, "personality")
            self.need(w, "favoredReligion", nat.get("favoredReligion"), self.religions, "religion")
            pvt = nat.get("preferredVictoryType")
            if pvt and pvt != "Neutral":
                self.need(w, "preferredVictoryType", pvt, self.victories, "victory type")
            if not special and not cst:
                majors += 1
                if not nat.get("leaderName"):
                    self.r.error(w, "major civilization without leaderName")
            if not special and not nat.get("cities"):
                self.r.error(w, "no city names (required for majors and city-states)")
        if self.rs.is_base_ruleset or nations:
            if majors == 0:
                self.r.error("Nations.json", "no playable major civilization")
            if "Barbarians" not in self.nations:
                self.r.error("Nations.json", "no \"Barbarians\" nation: barbarians (beast tides, MOD_SPEC S4) silently never spawn")
            if "Spectator" not in self.nations:
                self.r.warn("Nations.json", "no \"Spectator\" nation: AI-only observation games (MOD_SPEC §10) are impossible")

    def eras_(self):
        eras = self.rs.named("Eras.json")
        if self.rs.is_base_ruleset and not eras:
            self.r.error("Eras.json", "no eras (docs: required for base rulesets)")
        for e in eras:
            w = f"Eras.json > {e['name']}"
            # Defaults from docs/Modders/Mod-file-structure/5-Miscellaneous-JSON-files.md
            if e.get("startingSettlerCount", 1) > 0:
                self.need(w, "startingSettlerUnit", e.get("startingSettlerUnit", "Settler"), self.units, "unit")
            if e.get("startingWorkerCount", 0) > 0:
                self.need(w, "startingWorkerUnit", e.get("startingWorkerUnit", "Worker"), self.units, "unit")
            if e.get("startingMilitaryUnitCount", 1) > 0:
                self.need(w, "startingMilitaryUnit", e.get("startingMilitaryUnit", "Warrior"), self.units, "unit")
            for b in as_list(e.get("settlerBuildings")):
                self.need(w, "settlerBuildings", b, self.buildings, "building")
            for b in as_list(e.get("startingObsoleteWonders")):
                self.need(w, "startingObsoleteWonders", b, self.buildings, "building")

    def difficulties_(self):
        for d in self.rs.named("Difficulties.json"):
            w = f"Difficulties.json > {d['name']}"
            for key in ("playerBonusStartingUnits", "aiMajorCivBonusStartingUnits", "aiCityStateBonusStartingUnits"):
                for u in as_list(d.get(key)):
                    if u != "Era Starting Unit":
                        self.need(w, key, u, self.units, "unit")
            for t in as_list(d.get("aiFreeTechs")):
                self.need(w, "aiFreeTechs", t, self.techs, "tech")
            if d.get("aiDifficultyLevel"):
                self.need(w, "aiDifficultyLevel", d["aiDifficultyLevel"], self.difficulties, "difficulty")

    def victories_(self):
        for v in self.rs.named("VictoryTypes.json"):
            w = f"VictoryTypes.json > {v['name']}"
            for part in as_list(v.get("requiredSpaceshipParts")):
                self.need(w, "requiredSpaceshipParts", part, self.units, "unit")
            for m in as_list(v.get("milestones")):
                key = placeholder_key(m)
                if key not in MILESTONES:
                    self.r.error(w, f"unknown milestone \"{m}\"")
                    continue
                params = placeholder_params(m)
                if key in ("Build []", "Anyone should build []"):
                    self.need(w, "milestone building", params[0], self.buildings, "building")
                if key in ("Complete [] Policy branches", "Have at least [] []") and not re.fullmatch(r"\d+", params[0]):
                    self.r.error(w, f"milestone \"{m}\" needs a whole number")

    def events_(self):
        events = self.rs.events()
        self.check_duplicates("Events.json", events)
        triggers: dict[str, set[str]] = defaultdict(set)  # event -> events its choices trigger
        referenced: set[str] = set()
        for site in self.rs.unique_sites():
            base = remove_modifiers(site.text)
            if placeholder_key(base) == TRIGGER_EVENT_KEY:
                target = placeholder_params(base)[0]
                referenced.add(target)
                self.need(site.where, "Triggers a [...] event", target, self.events, "event")
                if site.owner_kind == "Events":
                    triggers[site.owner_name].add(target)
        for e in events:
            w = f"Events.json > {e['name']}"
            if e["name"] not in referenced:
                self.r.warn(w, "never triggered by any \"Triggers a [...] event\" unique")
            choices = [c for c in as_list(e.get("choices")) if isinstance(c, dict)]
            if not choices:
                self.r.warn(w, "has no choices")
            first_only = "Only the first available choice is offered" in (as_list(e.get("uniques")))
            for i, c in enumerate(choices):
                has_weight = any(placeholder_key(remove_modifiers(u)) == AI_WEIGHT_KEY for u in as_list(c.get("uniques")))
                if not has_weight and not first_only:
                    self.r.error(f"{w} > {c.get('text') or i + 1}",
                                 "event choice has no \"[relativeAmount]% weight to this choice for AI decisions\" "
                                 "(MOD_SPEC rule 7)")
        # circular triggers loop forever for the AI (BaseRulesetValidator warns too)
        for start in triggers:
            stack = [(start, [start])]
            while stack:
                cur, path = stack.pop()
                for nxt in triggers.get(cur, ()):
                    if nxt == start:
                        self.r.warn(f"Events.json > {start}", "circular event trigger: " + " -> ".join(path + [nxt]))
                    elif nxt not in path and len(path) < 50:
                        stack.append((nxt, path + [nxt]))

    def misc_(self):
        ruins_improvements = [i["name"] for i in self.rs.named("TileImprovements.json")
                              if "Provides a random bonus when entered" in (as_list(i.get("uniques")))]
        ruins = self.rs.named("Ruins.json")
        if "Ruins.json" in self.rs.data and not ruins and ruins_improvements:
            self.r.error("Ruins.json", f"empty, but {ruins_improvements} give random bonuses when entered")
        for reward in ruins:
            for d in as_list(reward.get("excludedDifficulties")):
                self.need(f"Ruins.json > {reward['name']}", "excludedDifficulties", d, self.difficulties, "difficulty")
        for s in self.rs.named("Specialists.json"):
            for gp in as_dict(s.get("greatPersonPoints")):
                self.need(f"Specialists.json > {s['name']}", "greatPersonPoints", gp, self.units, "unit", "WARNING")
        for p in self.rs.named("Personalities.json"):
            w = f"Personalities.json > {p['name']}"
            for key in as_dict(p.get("priorities")):
                self.need(w, "priorities", key, self.branches, "policy branch", "WARNING")
            pvt = p.get("preferredVictoryType")
            if pvt and pvt != "Neutral":
                self.need(w, "preferredVictoryType", pvt, self.victories, "victory type")
        for q in self.rs.named("Quests.json"):
            if q["name"] not in QUEST_NAMES:
                self.r.warn(f"Quests.json > {q['name']}", "not a predefined quest name - it will have no behaviour")
        constants = as_dict(self.rs.mod_options.get("constants"))
        for key in constants:
            if key not in MOD_CONSTANTS:
                self.r.warn("ModOptions.json > constants", f"unknown constant \"{key}\"")
        if self.rs.exists and "ModOptions.json" in self.rs.data and not self.rs.is_base_ruleset:
            self.r.warn("ModOptions.json", "isBaseRuleset is not true (MOD_SPEC §1: MOD_TYPE = base ruleset)")
        if self.rs.is_base_ruleset:
            for filename in ("Buildings.json", "Nations.json", "Terrains.json", "Units.json"):
                if not self.rs.list_of(filename):
                    self.r.error(filename, "missing or empty (docs: not allowed to be empty in a base ruleset)")

    # --- images ----------------------------------------------------------------------------
    def images_(self):
        mod_images: set[str] = set()
        for folder in self.rs.mod_root.glob("Images*"):
            if folder.is_dir():
                for png in folder.rglob("*.png"):
                    mod_images.add(png.relative_to(folder).with_suffix("").as_posix())
        builtin = set(BUILTIN_IMAGES.read_text().split("\n")) if BUILTIN_IMAGES.exists() else set()
        missing = 0
        for kind, name, candidates in expected_images(self.rs):
            if not any(c in mod_images or c in builtin for c in candidates):
                missing += 1
                self.r.warn(f"Images/{candidates[0]}.png", f"no icon for {kind} \"{name}\" - run tools/make_placeholders.py")
        if not builtin:
            self.r.info("images", "ref/builtin_images.txt missing (run tools/fetch_ref.sh): base-game icons not counted")

    def ascii_(self):
        """MOD_SPEC rule 5: object names become image paths, which must be ASCII (Images-and-Audio.md)."""
        for filename in self.rs.data:
            for o in self.rs.named(filename):
                if not o["name"].isascii():
                    self.r.error(f"{filename} > {o['name']}", "object name is not ASCII (keep Chinese terms in civilopedia text)")
        for folder in self.rs.mod_root.glob("Images*"):
            for path in folder.rglob("*"):
                rel = path.relative_to(self.rs.mod_root).as_posix()
                if not rel.isascii():
                    self.r.error(rel, "image path is not ASCII - atlas loading breaks on some systems")

    def atlas_(self):
        """Android uses the committed atlas as-is (it cannot pack), while desktop silently repacks: a stale or
        missing atlas only shows up on phones. Every Images*/**.png must have a region in the packed atlases."""
        root = self.rs.mod_root
        image_dirs = [p for p in root.glob("Images*") if p.is_dir()]
        atlases = sorted(root.glob("*.atlas"))
        listed = []
        if (root / "Atlases.json").exists():
            # Unciv writes it with libGDX's lenient JSON: [game] - unquoted names are normal here.
            text = (root / "Atlases.json").read_text(encoding="utf-8").strip()
            if not (text.startswith("[") and text.endswith("]")):
                self.r.error("Atlases.json", "must be a JSON array of atlas names")
            listed = [n.strip().strip('"') for n in text[1:-1].split(",") if n.strip()]
            for name in listed:
                if not (root / f"{name}.atlas").exists():
                    self.r.error("Atlases.json", f"lists \"{name}\" but {name}.atlas is missing (blocks the base ruleset)")
        if not image_dirs:
            return
        if not atlases:
            self.r.warn("game.atlas", "Images exist but no packed atlas: Android cannot pack, so players get blank icons "
                                      "(run tools/unciv_ci.py --pack)")
            return
        regions = set()
        for atlas in atlases:
            for line in atlas.read_text(encoding="utf-8").splitlines():
                if line and not line[0].isspace() and ":" not in line and not line.endswith(".png"):
                    regions.add(line)
        stale = sorted(png.relative_to(folder).with_suffix("").as_posix()
                       for folder in image_dirs for png in folder.rglob("*.png")
                       if png.relative_to(folder).with_suffix("").as_posix() not in regions)
        if stale:
            self.r.warn("game.atlas", f"atlas is stale: {len(stale)} image(s) not packed, e.g. {stale[:3]} "
                                      f"(run tools/unciv_ci.py --pack)")

    def run(self):
        if not self.rs.exists:
            self.r.info("jsons/", "no jsons/ folder yet - nothing to cross-check")
            return
        for step in (self.units_, self.buildings_, self.techs_, self.policies_, self.promotions_, self.map_objects_,
                     self.nations_, self.eras_, self.difficulties_, self.victories_, self.events_, self.misc_,
                     self.ascii_, self.images_, self.atlas_):
            step()


def promotion_icon(name: str) -> list[str]:
    """Docs: ' I/II/III' suffixes are drawn as stars; '[Unit] ability' falls back to the unit icon."""
    base = re.sub(r" (I|II|III)$", "", name)
    out = [f"UnitPromotionIcons/{base}"]
    m = re.fullmatch(r"\[(.+)\] ability", base)
    if m:
        out.append(f"UnitIcons/{m.group(1)}")
    return out


def expected_images(rs: Ruleset):
    """(kind, name, [acceptable image keys]) for every object that is drawn with an icon."""
    for u in rs.named("Units.json"):
        yield "unit", u["name"], [f"UnitIcons/{u['name']}", f"UnitTypeIcons/{u.get('unitType')}"]
    for b in rs.named("Buildings.json"):
        yield "building", b["name"], [f"BuildingIcons/{b['name']}"]
    for t in rs.techs():
        yield "tech", t["name"], [f"TechIcons/{t['name']}"]
    for r in rs.named("TileResources.json"):
        yield "resource", r["name"], [f"ResourceIcons/{r['name']}"]
    for i in rs.named("TileImprovements.json"):
        yield "improvement", i["name"], [f"ImprovementIcons/{i['name']}"]
    for p in rs.named("UnitPromotions.json"):
        yield "promotion", p["name"], promotion_icon(p["name"])
    for n in rs.named("Nations.json"):  # Portrait.kt: city-states fall back to NationIcons/CityState
        if n["name"] != "Spectator":
            yield "nation", n["name"], [f"NationIcons/{n['name']}"] + (["NationIcons/CityState"] if n.get("cityStateType") else [])
    for p in rs.policies():
        if p["_is_branch"]:
            yield "policy branch", p["name"], [f"PolicyBranchIcons/{p['name']}"]
        elif not p["name"].endswith(" Complete"):
            yield "policy", p["name"], [f"PolicyIcons/{p['name']}"]
    for r in rs.names("Religions.json"):
        yield "religion", r, [f"ReligionIcons/{r}"]
    for c in rs.named("CityStateTypes.json"):
        yield "city-state type", c["name"], [f"CityStateIcons/{c['name']}"]


def run(mod_root: Path, reporter: Reporter) -> None:
    RefChecker(Ruleset(mod_root).load(), reporter).run()  # strict-JSON failures: see check_schema


def main(argv: list[str]) -> int:
    require_ref()
    reporter = Reporter("check_refs")
    run(mod_root_from_args(argv), reporter)
    reporter.print(verbose="--quiet" not in argv)
    return reporter.exit_code()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
