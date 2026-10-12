#!/usr/bin/env python3
"""Lint every unique in the mod against the patterns documented in ref/.../docs/Modders/uniques.md.

For each unique:
  1. split off the `<...>` modifiers; the base must match a documented pattern verbatim
     (case-sensitive, only `[...]` contents may differ), or be an allowlisted filter marker;
  2. each modifier must match a documented Conditional / TriggerCondition / UnitTriggerCondition /
     UnitActionModifier / MetaModifier pattern, and be acceptable for the base unique;
  3. the base unique must be applicable to the object it sits on ("Applicable to" + UniqueTarget inheritance);
  4. parameters are type-checked: numbers and fixed vocabularies strictly, names of ruleset objects
     (units, buildings, techs, resources, promotions, policies, eras, events, ...) must exist in the mod,
     filters are checked atom by atom (unknown atoms are warnings: filters may also match uniques).

Usage: tools/lint_uniques.py [--mod PATH] [--quiet]
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

from common import (TOOLS_DIR, Reporter, Ruleset, UniqueSite, mod_root_from_args,
                    require_ref, DOCS_MODDERS)
from uniques_db import UniqueDb, UniquePattern, load_db, modifiers_of, placeholder_key, placeholder_params, \
    remove_modifiers

ALLOWLIST_FILE = TOOLS_DIR / "unique_allowlist.txt"

INT_RE = re.compile(r"^[+-]?\d+$")
FLOAT_RE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
STATS = ["Production", "Food", "Gold", "Science", "Culture", "Happiness", "Faith"]
CIV_WIDE_STATS = ["Gold", "Science", "Culture", "Faith"]
# Stats.kt: "([+-])(\\d+) (statName)" joined by ", " - sign required, whole numbers only
STATS_RE = re.compile(r"^[+-]\d+ (" + "|".join(STATS) + r")$")
BUILTIN_VICTORIES = {"Cultural", "Diplomatic", "Domination", "Scientific", "Time"}


def is_int(text: str, minimum: int | None = None) -> bool:
    if not INT_RE.match(text):
        return False
    value = int(text)
    return -2**31 <= value < 2**31 and (minimum is None or value >= minimum)


def load_allowlist() -> set[str]:
    if not ALLOWLIST_FILE.exists():
        return set()
    lines = (l.strip() for l in ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines())
    return {l for l in lines if l and not l.startswith("#")}


def multi_filter(value: str, single) -> bool:
    """Mirrors Unciv's MultiFilter: `{A} {B}` = all of; `non-[X]` = negation (validity: X must be valid)."""
    if value.startswith("{") and value.endswith("}"):
        return all(multi_filter(part, single) for part in value[1:-1].split("} {"))
    if value.startswith("non-[") and value.endswith("]"):
        return multi_filter(value[5:-1], single)
    return single(value)


class Knowledge:
    """Everything a parameter may legitimately name, collected from the mod."""

    def __init__(self, rs: Ruleset):
        named = rs.named
        self.units = rs.names("Units.json")
        self.unit_types = rs.names_with_fallback("UnitTypes.json")
        self.buildings = rs.names("Buildings.json")
        self.techs = rs.names("Techs.json")
        self.eras = rs.names("Eras.json")
        self.policies = {p["name"] for p in rs.policies()}
        self.branches = {b["name"] for b in rs.policy_branches()}
        self.beliefs = rs.names("Beliefs.json")
        self.religions = rs.names("Religions.json")
        self.nations = rs.names("Nations.json")
        self.promotions = rs.names("UnitPromotions.json")
        self.resources = rs.names("TileResources.json")
        self.stockpiled = {r["name"] for r in named("TileResources.json") if "Stockpiled" in (r.get("uniques") or [])}
        self.improvements = rs.names("TileImprovements.json")
        terrains = named("Terrains.json")
        self.terrains = {t["name"] for t in terrains}
        self.base_terrains = {t["name"] for t in terrains if t.get("type") in ("Land", "Water")}
        self.terrain_features = {t["name"] for t in terrains if t.get("type") == "TerrainFeature"}
        self.natural_wonders = {t["name"] for t in terrains if t.get("type") == "NaturalWonder"}
        self.region_terrains = {t["name"] for t in terrains
                                if any(str(u).startswith("A Region is formed with at least") for u in t.get("uniques") or [])}
        self.specialists = rs.names("Specialists.json")
        self.speeds = rs.names_with_fallback("Speeds.json")
        self.difficulties = rs.names_with_fallback("Difficulties.json")
        self.events = rs.names("Events.json")
        self.victories = rs.names_with_fallback("VictoryTypes.json") | BUILTIN_VICTORIES
        self.name_groups = rs.names("UnitNameGroups.json")

        def uniques(filename: str) -> set[str]:
            return {u for o in named(filename) for u in (o.get("uniques") or []) if isinstance(u, str)}

        self.unit_uniques = uniques("Units.json")
        self.unit_type_uniques = uniques("UnitTypes.json")
        self.promotion_uniques = uniques("UnitPromotions.json")
        self.building_uniques = uniques("Buildings.json")
        self.improvement_uniques = uniques("TileImprovements.json")
        self.terrain_uniques = uniques("Terrains.json")
        self.tech_uniques = {u for t in rs.techs() for u in (t.get("uniques") or [])}
        self.policy_uniques = {u for p in rs.policies() for u in (p.get("uniques") or [])}
        self.belief_uniques = uniques("Beliefs.json")
        self.nation_uniques = uniques("Nations.json")
        self.name_group_uniques = uniques("UnitNameGroups.json")
        self.countable_patterns = parse_countables()


def parse_countables() -> dict[str, list[str]]:
    """`[cityFilter] Cities` style countables from Unique-parameters.md -> {placeholder key: param types}."""
    path = DOCS_MODDERS / "Unique-parameters.md"
    text = path.read_text(encoding="utf-8")
    if "Countables automatically generated BEGIN" in text:
        text = text.split("Countables automatically generated BEGIN", 1)[1].split("Countables automatically generated END", 1)[0]
    out: dict[str, list[str]] = {}
    for m in re.finditer(r"^-\s+`([^`]+)`", text, re.M):
        pattern = m.group(1)
        out[placeholder_key(pattern)] = placeholder_params(pattern)
    return out


class ParamChecker:
    """Returns (severity, message) for a bad parameter, or None. Severity: ERROR for invariant/name params,
    WARNING for filter atoms we cannot resolve (they may legitimately match a unique)."""

    def __init__(self, k: Knowledge):
        self.k = k

    # --- filters -----------------------------------------------------------------------------
    def civ_atom(self, v):
        return v in {"Human player", "AI player", "Friendly", "Hostile", "Open Borders", "Known"} or self.nation_atom(v)

    def nation_atom(self, v):
        return v in {"All", "all", "City-States", "City-State", "Major"} or v in self.k.nations or v in self.k.nation_uniques

    def era_filter(self, v):
        if v in {"any era", "Starting Era"} or v in self.k.eras:
            return True
        m = re.fullmatch(r"(pre|post)-\[(.+)\]", v)
        return bool(m and m.group(2) in self.k.eras)

    def tech_atom(self, v):
        return v in {"All", "all"} or self.era_filter(v) or v in self.k.techs or v in self.k.tech_uniques

    def base_unit_atom(self, v):
        return (v in {"Land", "Water", "Air", "land units", "water units", "air units", "non-air", "Military",
                      "military units", "Civilian", "civilian units", "All", "all", "Melee", "Ranged",
                      "Nuclear Weapon", "Great Person", "Embarked",
                      "Religious", "relevant"}  # last two: UniqueParameterType.kt, undocumented
                or v in self.k.units or v in self.k.unit_types or v in self.k.unit_uniques
                or v in self.k.unit_type_uniques or self.tech_atom(v))

    def map_unit_atom(self, v):
        return (self.base_unit_atom(v) or self.civ_atom(v) or v in self.k.promotions or v in self.k.promotion_uniques
                or v in {"Wounded", "Embarked", "City-State", "Barbarians", "Barbarian", "Non-City",
                         "other"})  # "other": UniqueParameterType.kt, undocumented

    def building_atom(self, v):
        return (v in {"All", "all", "Buildings", "Building", "Wonder", "Wonders", "National Wonder", "National",
                      "World Wonder", "World"} or v in STATS
                or v in self.k.buildings or v in self.k.building_uniques or self.tech_atom(v))

    CITY_CONSTANTS = {"in this city", "in all cities", "All", "all", "in your cities", "Your", "in all coastal cities",
                      "Coastal", "in capital", "Capital", "in all non-occupied cities", "Non-occupied",
                      "in all cities with a world wonder", "in all cities connected to capital",
                      "in all cities with a garrison", "Garrisoned", "in non-enemy foreign cities", "in enemy cities",
                      "Enemy", "in foreign cities", "Foreign", "in annexed cities", "Annexed", "in puppeted cities",
                      "Puppeted", "in resisting cities", "Resisting", "in cities being razed", "Razing",
                      "in holy cities", "Holy", "in City-State cities", "in cities following this religion",
                      "in cities following our religion",
                      "in all cities in which the majority religion is a major religion",
                      "in all cities in which the majority religion is an enhanced religion"}

    def city_atom(self, v):
        return v in self.CITY_CONSTANTS or self.civ_atom(v)

    def improvement_atom(self, v):
        return (v in {"Improvement", "All", "all", "Great Improvement", "Great", "All Road"}
                or v in self.k.improvements or v in self.k.improvement_uniques)

    TERRAIN_CONSTANTS = {"All", "all", "Terrain", "Water", "Land", "Coastal", "River", "Open terrain", "Rough terrain",
                         "Water resource", "Strategic resource", "Luxury resource", "Bonus resource", "resource",
                         "Natural Wonder", "Terrain Feature", "Featureless", "Fresh Water", "non-fresh water",
                         "Impassable", "Friendly Land", "Friendly", "Foreign Land", "Enemy Land", "Enemy", "your",
                         "Unowned", "Foreign"}  # "Foreign": UniqueParameterType.kt, undocumented

    def terrain_atom(self, v):
        return (v in self.TERRAIN_CONSTANTS or v in self.k.terrains or v in self.k.terrain_uniques
                or v in self.k.resources or self.nation_atom(v))

    def tile_atom(self, v):
        return (self.terrain_atom(v) or self.improvement_atom(v) or self.civ_atom(v)
                or v in {"Improvement", "improved", "unimproved", "pillaged", "worked"})

    def resource_filter(self, v):  # no multi-filter for resourceFilter
        return v in {"any", "All", "all", "Strategic", "Luxury", "Bonus"} or v in STATS or v in self.k.resources

    def policy_atom(self, v):
        if v in {"All", "all"} or v in self.k.policies or v in self.k.policy_uniques:
            return True
        m = re.fullmatch(r"(.+) branch", v)
        if m and m.group(1) in self.k.branches:
            return True
        m = re.fullmatch(r"(.+) Completed", v)
        return bool(m and m.group(1) in self.k.branches)

    def population_filter(self, v):  # no multi-filter for populationFilter
        return v in {"Population", "Specialists", "Unemployed", "Followers of the Majority Religion",
                     "Followers of this Religion"} or v in self.k.specialists

    def religion_atom(self, v):
        return (v in {"any", "major", "enhanced", "your", "foriegn", "enemy"} or v in self.k.religions
                or v in self.k.beliefs or v in self.k.belief_uniques)

    def combatant_atom(self, v):
        return v in {"City", "All"} or self.map_unit_atom(v) or self.civ_atom(v)

    def countable(self, v) -> bool | None:
        """True/False when decidable; None for math expressions we do not evaluate."""
        if is_int(v) or v in {"turns", "year", "Cities", "Units", "Completed Policy branches", "Era number"}:
            return True
        if v in STATS or v in self.k.resources:
            return True
        m = re.fullmatch(r"\[(.+)\] Per Turn", v)
        if m:
            return m.group(1) in STATS or m.group(1) in self.k.resources
        key = placeholder_key(v)
        if key in self.k.countable_patterns:
            types = self.k.countable_patterns[key]
            return all(self.check(t, p) is None for t, p in zip(types, placeholder_params(v)))
        if re.search(r"[-+*/%^()√]|\b(abs|sqrt|floor|ceil|max|min)\b", v):
            return None
        return False

    # --- dispatcher ----------------------------------------------------------------------------
    def check(self, ptype: str, value: str):
        if "/" in ptype:
            # 'all' is UniqueParameterType.KeywordAll: Constants.all = {"All", "all"}
            results = [self.check(alt, value) if alt != "'all'" else (None if value in ("All", "all") else ("ERROR", ""))
                       for alt in ptype.split("/")]
            if any(r is None for r in results):
                return None
            worst = "ERROR" if all(r[0] == "ERROR" for r in results) else "WARNING"
            return worst, f"\"{value}\" does not fit any of [{ptype}]"
        k = self.k
        bad = lambda msg="": ("ERROR", msg or f"\"{value}\" is not a valid {ptype}")
        unknown = lambda what: ("ERROR", f"\"{value}\" is not a {what} defined in the mod")
        soft = ("WARNING", f"filter [{ptype}] has an atom that matches nothing known in \"{value}\" "
                           f"(fine only if it names a unique used as a filter marker)")
        match ptype:
            case "amount":
                return None if is_int(value) else bad("must be a whole number")
            case "positiveAmount":
                return None if is_int(value, 1) else bad("must be a whole number > 0")
            case "nonNegativeAmount":
                return None if is_int(value, 0) else bad("must be a whole number >= 0")
            case "relativeAmount":
                return None if is_int(value) else bad("must be a whole number like +25 or -10")
            case "fraction":
                return None if FLOAT_RE.match(value) else bad("must be a number")
            case "stat":
                return None if value in STATS else bad(f"must be one of {STATS}")
            case "civWideStat":
                return None if value in CIV_WIDE_STATS else bad(f"must be one of {CIV_WIDE_STATS}")
            case "stats":
                return None if all(STATS_RE.match(p) for p in value.split(", ")) else bad("must look like '+2 Production, +1 Gold'")
            case "costOrStrength":
                return None if value in ("Cost", "Strength") else bad()
            case "foundingOrEnhancing":
                return None if value in ("founding", "enhancing") else bad()
            case "beliefType":
                return None if value in ("Pantheon", "Follower", "Founder", "Enhancer") else bad()
            case "unitTriggerTarget":
                return None if value in ("This Unit", "Target Unit") else bad()
            case "terrainQuality":
                return None if value in ("Undesirable", "Food", "Desirable", "Production") else bad()
            case "unit" | "greatPerson":
                return None if value in k.units else unknown("unit")
            case "buildingName":
                return None if value in k.buildings else unknown("building")
            case "tech":
                return None if value in k.techs else unknown("tech")
            case "era":
                return None if value in k.eras else unknown("era")
            case "event":
                return None if value in k.events else unknown("event")
            case "policy":
                return None if value in k.policies else unknown("policy")
            case "belief":
                return None if value in k.beliefs else unknown("belief")
            case "promotion":
                return None if value in k.promotions else unknown("promotion")
            case "resource":
                return None if value in k.resources else unknown("resource")
            case "stockpiledResource":
                return None if value in k.stockpiled else unknown("resource with the \"Stockpiled\" unique")
            case "stockpile":
                ok = value in k.stockpiled or value in STATS or value in ("Stored Food", "Golden Age points")
                return None if ok else unknown("stockpiled resource / stat / 'Stored Food' / 'Golden Age points'")
            case "improvementName":
                return None if value in k.improvements and value != "Cancel improvement order" else unknown("improvement")
            case "terrainName":
                return None if value in k.terrains else unknown("terrain")
            case "baseTerrain":
                return None if value in k.base_terrains else unknown("base terrain (Land/Water)")
            case "terrainFeature":
                return None if value in k.terrain_features else unknown("terrain feature")
            case "specialist":
                return None if value in k.specialists else unknown("specialist")
            case "speed":
                return None if value in k.speeds else unknown("speed")
            case "difficulty":
                return None if value in k.difficulties else unknown("difficulty")
            case "victoryType":
                return None if value in k.victories else unknown("victory type")
            case "unitNameGroup":
                return None if value in k.name_groups or value in k.name_group_uniques else unknown("unit name group")
            case "regionType":
                return None if value == "Hybrid" or value in k.region_terrains else unknown("region type")
            case "simpleTerrain":
                return None if value in ("Land", "Water", "Elevated") or value in k.terrains else unknown("terrain")
            case "eraFilter":
                return None if self.era_filter(value) else unknown("era / eraFilter")
            case "resourceFilter":
                return None if self.resource_filter(value) else soft
            case "populationFilter":
                return None if self.population_filter(value) else soft
            case "civFilter":
                return None if multi_filter(value, self.civ_atom) else soft
            case "nationFilter":
                return None if multi_filter(value, self.nation_atom) else soft
            case "baseUnitFilter" | "unitType":
                return None if multi_filter(value, self.base_unit_atom) else soft
            case "mapUnitFilter":
                return None if multi_filter(value, self.map_unit_atom) else soft
            case "buildingFilter":
                return None if multi_filter(value, self.building_atom) else soft
            case "cityFilter":
                return None if multi_filter(value, self.city_atom) else soft
            case "improvementFilter":
                return None if multi_filter(value, self.improvement_atom) else soft
            case "terrainFilter":
                return None if multi_filter(value, self.terrain_atom) else soft
            case "tileFilter":
                return None if multi_filter(value, self.tile_atom) else soft
            case "techFilter" | "technologyFilter":
                return None if multi_filter(value, self.tech_atom) else soft
            case "policyFilter":
                return None if multi_filter(value, self.policy_atom) else soft
            case "religionFilter":
                return None if multi_filter(value, self.religion_atom) else soft
            case "combatantFilter":
                return None if multi_filter(value, self.combatant_atom) else soft
            case "countable":
                verdict = self.countable(value)
                if verdict is None:
                    return ("INFO", f"countable expression \"{value}\" not evaluated - test it in game with "
                                    f"`civ checkcountable`")
                return None if verdict else ("WARNING", f"\"{value}\" is not a recognised countable")
            case "comment" | "param" | "validationWarning" | "leaderTitle" | "modFilter" | "spyAction":
                return None
            case "pediaLink":
                return None if re.fullmatch(r"[^/]+/.+", value) else bad("must look like Category/Entry")
        return ("WARNING", f"parameter type [{ptype}] is not known to the linter - check \"{value}\" by hand")


class UniqueLinter:
    def __init__(self, db: UniqueDb, rs: Ruleset, reporter: Reporter):
        self.db, self.rs, self.r = db, rs, reporter
        self.k = Knowledge(rs)
        self.params = ParamChecker(self.k)
        self.allowlist = load_allowlist()
        self.used_params: list[str] = []

    # --- helpers mirroring UniqueTarget / Unique in Unciv ---------------------------------------
    def is_triggerable(self, pattern: UniquePattern, modifiers: list[str]) -> bool:
        if any(placeholder_key(m) == "for [] turns" for m in modifiers):
            return True
        return any(self.db.accepts(t, "Triggerable") or self.db.accepts(t, "UnitTriggerable") for t in pattern.targets)

    def applicable(self, pattern: UniquePattern, target: str, modifiers: list[str]) -> bool:
        if any(self.db.accepts(target, t) for t in pattern.targets):
            return True
        timed = any(placeholder_key(m) == "for [] turns" for m in modifiers)
        return timed and self.db.accepts(target, "Triggerable")

    def modifier_acceptable(self, mod: UniquePattern, base: UniquePattern, site: UniqueSite, modifiers) -> bool:
        for t in mod.targets:
            if t in ("Conditional", "MetaModifier"):
                return True
            if t == "TriggerCondition" and self.is_triggerable(base, modifiers):
                return True
            if t == "UnitTriggerCondition":
                if self.is_triggerable(base, modifiers) and self.db.accepts(site.target, "Unit"):
                    return True
                if any(self.db.accepts("UnitTriggerable", bt) for bt in base.targets):
                    return True
            if t == "UnitActionModifier" and any(self.db.accepts("UnitAction", bt) for bt in base.targets):
                return True
        return False

    def check_params(self, pattern: UniquePattern, values: list[str]) -> list[tuple[str, str]]:
        problems = []
        for ptype, value in zip(pattern.params, values):
            self.used_params.append(value)
            result = self.params.check(ptype, value)
            if result:
                problems.append(result)
        return problems

    def best_pattern(self, candidates: list[UniquePattern], values: list[str], site: UniqueSite, modifiers):
        def score(p):
            probs = self.check_params(p, values)
            return (not self.applicable(p, site.target, modifiers),
                    sum(1 for s, _ in probs if s == "ERROR"), sum(1 for s, _ in probs if s == "WARNING")), probs
        scored = sorted((score(p) + (p,) for p in candidates), key=lambda x: x[0])
        _, problems, best = scored[0]
        return best, problems

    def suggest(self, key: str, pool) -> str:
        close = difflib.get_close_matches(key, list(pool), n=2, cutoff=0.75)
        return f" Did you mean: {' / '.join(repr(c) for c in close)}?" if close else ""

    def report(self, severity: str, where: str, message: str):
        {"ERROR": self.r.error, "WARNING": self.r.warn, "INFO": self.r.info}[severity](where, message)

    # --- main --------------------------------------------------------------------------------
    def lint_site(self, site: UniqueSite):
        text = site.text
        where = f"{site.where} \"{text}\""
        modifiers = modifiers_of(text)
        base_text = remove_modifiers(text)
        key = placeholder_key(base_text)
        values = placeholder_params(base_text)

        candidates = self.db.base.get(key)
        if not candidates:
            if base_text in self.allowlist and not modifiers:
                self.r.info(where, "allowlisted filter marker (untyped on purpose)")
                return
            hint = ""
            if key in self.db.modifiers:
                hint = " It is a modifier: wrap it in <...> after another unique."
            elif "[" not in base_text and not modifiers:
                hint = " If it is an intentional filter marker, add it to tools/unique_allowlist.txt."
            self.r.error(where, f"untyped unique: base \"{base_text}\" matches no pattern in uniques.md."
                                f"{hint}{self.suggest(key, self.db.base)}")
            return

        pattern, problems = self.best_pattern(candidates, values, site, modifiers)
        for severity, message in problems:
            self.report(severity, where, message)
        if not self.applicable(pattern, site.target, modifiers):
            self.r.error(where, f"not applicable to {site.target} (uniques.md says: Applicable to "
                                f"{', '.join(sorted(pattern.targets))})")

        for mod_text in modifiers:
            mod_key = placeholder_key(mod_text)
            mod_candidates = self.db.modifiers.get(mod_key)
            if not mod_candidates:
                extra = " It is a regular unique, not a modifier." if mod_key in self.db.base else ""
                self.r.error(where, f"unknown modifier <{mod_text}>.{extra}{self.suggest(mod_key, self.db.modifiers)}")
                continue
            mod_values = placeholder_params(mod_text)
            mod_pattern = min(mod_candidates, key=lambda p: len(self.check_params(p, mod_values)))
            for severity, message in self.check_params(mod_pattern, mod_values):
                self.report(severity, where, f"<{mod_text}>: {message}")
            if pattern.no_conditionals and "MetaModifier" not in mod_pattern.targets:
                self.r.error(where, f"uniques.md says this unique does not support conditionals, but it has <{mod_text}>")
            elif not self.modifier_acceptable(mod_pattern, pattern, site, modifiers):
                self.r.warn(where, f"<{mod_text}> ({', '.join(sorted(mod_pattern.targets))}) is not an acceptable "
                                   f"modifier for this unique on a {site.target}")

    def run(self):
        sites = list(self.rs.unique_sites())
        for site in sites:
            self.lint_site(site)
        for marker in sorted(self.allowlist):
            if "[" in marker or "<" in marker:
                self.r.error("tools/unique_allowlist.txt", f"\"{marker}\": filter markers must have no brackets or conditionals")
            elif not any(site.text == marker for site in sites):
                self.r.info("tools/unique_allowlist.txt", f"\"{marker}\" is allowlisted but not used by any object")
            elif not any(marker == p or marker in p for p in self.used_params):
                self.r.warn("tools/unique_allowlist.txt", f"\"{marker}\" is never referenced by a filter - Unciv will flag it as untyped")
        self.r.info("lint_uniques", f"checked {len(sites)} unique(s)")


def run(mod_root: Path, reporter: Reporter) -> None:
    rs = Ruleset(mod_root).load()  # strict-JSON failures are reported by check_schema
    if not rs.exists:
        reporter.info("jsons/", "no jsons/ folder yet - nothing to lint")
    else:
        UniqueLinter(load_db(), rs, reporter).run()


def main(argv: list[str]) -> int:
    require_ref()
    reporter = Reporter("lint_uniques")
    run(mod_root_from_args(argv), reporter)
    reporter.print(verbose="--quiet" not in argv)
    return reporter.exit_code()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
