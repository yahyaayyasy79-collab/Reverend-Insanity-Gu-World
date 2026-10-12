"""Shared helpers for the mod checkers: paths, strict JSON loading, a ruleset model and a reporter.

The checkers approximate Unciv's Ruleset Validator. The in-game Options tab
"Locate mod errors" stays the final authority.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
REF_ROOT = Path(os.environ.get("UNCIV_REF", REPO_ROOT / "ref" / "unciv"))
REF_DIR = REF_ROOT.parent  # holds builtin_images.txt and UNCIV_TAG next to the clone

DOCS_MODDERS = REF_ROOT / "docs" / "Modders"
SCHEMA_DIR = DOCS_MODDERS / "schemas"
UNIQUES_MD = DOCS_MODDERS / "uniques.md"
UNIQUE_TARGET_KT = REF_ROOT / "core/src/com/unciv/models/ruleset/unique/UniqueTarget.kt"
BUILTIN_IMAGES = REF_DIR / "builtin_images.txt"
VANILLA_JSONS = REF_ROOT / "android/assets/jsons/Civ V - Vanilla"

# Canonical file names, from RulesetFile in core/.../models/ruleset/Ruleset.kt (4.22.8).
RULESET_FILES = [
    "Beliefs.json", "Buildings.json", "Eras.json", "Religions.json", "Nations.json", "Policies.json",
    "Techs.json", "Terrains.json", "Tutorials.json", "TileImprovements.json", "TileResources.json",
    "Specialists.json", "Units.json", "UnitPromotions.json", "UnitNameGroups.json", "UnitTypes.json",
    "VictoryTypes.json", "CityStateTypes.json", "Personalities.json", "Events.json", "GlobalUniques.json",
    "ModOptions.json", "Speeds.json", "Difficulties.json", "Quests.json", "Ruins.json",
]

# Base-ruleset fallbacks when a file is missing or empty (docs: Mod-file-structure/1-Overview.md).
VANILLA_FALLBACK_FILES = ["CityStateTypes.json", "Difficulties.json", "GlobalUniques.json", "Ruins.json",
                          "Speeds.json", "UnitTypes.json", "VictoryTypes.json"]


def ref_available() -> bool:
    return UNIQUES_MD.exists() and SCHEMA_DIR.exists()


def require_ref() -> None:
    if not ref_available():
        sys.exit(f"ERROR: Unciv reference not found at {REF_ROOT}. Run tools/fetch_ref.sh first.")


def ref_tag() -> str:
    tag_file = REF_DIR / "UNCIV_TAG"
    return tag_file.read_text().strip() if tag_file.exists() else "unknown"


# ---------------------------------------------------------------- reporting

@dataclass
class Issue:
    severity: str  # "ERROR" | "WARNING" | "INFO"
    where: str
    message: str

    def __str__(self) -> str:
        return f"{self.severity:7} {self.where}: {self.message}"


@dataclass
class Reporter:
    tool: str
    issues: list[Issue] = field(default_factory=list)

    def error(self, where: str, message: str) -> None:
        self.issues.append(Issue("ERROR", where, message))

    def warn(self, where: str, message: str) -> None:
        self.issues.append(Issue("WARNING", where, message))

    def info(self, where: str, message: str) -> None:
        self.issues.append(Issue("INFO", where, message))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "ERROR"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "WARNING"]

    def print(self, verbose: bool = True) -> None:
        for issue in self.issues:
            if verbose or issue.severity != "INFO":
                print(issue)
        print(f"[{self.tool}] {len(self.errors)} error(s), {len(self.warnings)} warning(s)")

    def exit_code(self) -> int:
        return 1 if self.errors else 0


# ---------------------------------------------------------------- JSON loading

class StrictJsonError(ValueError):
    pass


def _no_duplicate_keys(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise StrictJsonError(f"duplicate key {key!r}")
        seen[key] = value
    return seen


def load_strict_json(path: Path):
    """Standard JSON only: no trailing commas, no comments, no duplicate keys, no BOM."""
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise StrictJsonError("file starts with a UTF-8 byte order mark")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as ex:
        raise StrictJsonError(f"not valid UTF-8: {ex}") from ex
    try:
        return json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except json.JSONDecodeError as ex:
        raise StrictJsonError(f"invalid JSON at line {ex.lineno} col {ex.colno}: {ex.msg}") from ex


def load_lenient_json(path: Path):
    """Unciv's bundled files contain trailing commas; read them with json5."""
    import json5
    return json5.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- ruleset model

@dataclass
class UniqueSite:
    """One unique string, with where it lives and which UniqueTarget it is checked against."""
    target: str      # UniqueTarget name, e.g. "Building", "Unit", "EventChoice"
    where: str       # human-readable location
    text: str
    owner_kind: str  # ruleset category of the owning object, e.g. "Buildings"
    owner_name: str


class Ruleset:
    """A mod's jsons/ folder, loaded strictly. Load errors go to the reporter given to load()."""

    def __init__(self, mod_root: Path):
        self.mod_root = mod_root
        self.jsons = mod_root / "jsons"
        self.data: dict[str, object] = {}
        self.load_failures: dict[str, str] = {}

    def load(self, reporter: Reporter | None = None) -> "Ruleset":
        if not self.jsons.is_dir():
            return self
        for path in sorted(self.jsons.glob("*.json")):
            try:
                self.data[path.name] = load_strict_json(path)
            except StrictJsonError as ex:
                self.load_failures[path.name] = str(ex)
                if reporter:
                    reporter.error(f"jsons/{path.name}", str(ex))
        return self

    @property
    def exists(self) -> bool:
        return self.jsons.is_dir()

    def list_of(self, filename: str) -> list:
        value = self.data.get(filename)
        return value if isinstance(value, list) else []

    def obj(self, filename: str) -> dict:
        value = self.data.get(filename)
        return value if isinstance(value, dict) else {}

    @property
    def mod_options(self) -> dict:
        return self.obj("ModOptions.json")

    @property
    def is_base_ruleset(self) -> bool:
        return bool(self.mod_options.get("isBaseRuleset", False))

    # --- flattened object lists -------------------------------------------------

    @staticmethod
    def _named(items) -> list[dict]:
        return [i for i in items if isinstance(i, dict) and isinstance(i.get("name"), str)]

    def techs(self) -> list[dict]:
        out = []
        for column in self.list_of("Techs.json"):
            if isinstance(column, dict):
                for tech in self._named(column.get("techs", [])):
                    out.append({**tech, "_column": column})
        return out

    def policy_branches(self) -> list[dict]:
        return self._named(self.list_of("Policies.json"))

    def policies(self) -> list[dict]:
        """Branches (openers) and their member policies, including finishers."""
        out = []
        for branch in self.policy_branches():
            out.append({**branch, "_branch": branch["name"], "_is_branch": True})
            for member in self._named(branch.get("policies", [])):
                out.append({**member, "_branch": branch["name"], "_is_branch": False})
        return out

    def events(self) -> list[dict]:
        return self._named(self.list_of("Events.json"))

    def named(self, filename: str) -> list[dict]:
        if filename == "Techs.json":
            return self.techs()
        if filename == "Policies.json":
            return self.policies()
        return self._named(self.list_of(filename))

    def names(self, filename: str) -> set[str]:
        if filename == "Religions.json":
            return {r for r in self.list_of("Religions.json") if isinstance(r, str)}
        return {o["name"] for o in self.named(filename)}

    def names_with_fallback(self, filename: str) -> set[str]:
        """Object names after Unciv's vanilla fallback for missing/empty files (base rulesets only)."""
        own = self.names(filename)
        if own or not self.is_base_ruleset or filename not in VANILLA_FALLBACK_FILES:
            return own
        vanilla = VANILLA_JSONS / filename
        if vanilla.exists():
            return {o["name"] for o in load_lenient_json(vanilla) if isinstance(o, dict) and "name" in o}
        return own

    # --- every unique in the mod, with its target -------------------------------

    def unique_sites(self) -> Iterator[UniqueSite]:
        def strings(value):
            return [u for u in value if isinstance(u, str)] if isinstance(value, list) else []

        simple = {
            "Beliefs.json": None,  # target depends on belief type
            "Buildings.json": "Building",
            "Nations.json": "Nation",
            "Personalities.json": "Personality",
            "Eras.json": "Era",
            "Terrains.json": "Terrain",
            "TileImprovements.json": "Improvement",
            "TileResources.json": "Resource",
            "Units.json": "Unit",
            "UnitPromotions.json": "Promotion",
            "UnitTypes.json": "UnitType",
            "UnitNameGroups.json": "UnitTriggerable",
            "Ruins.json": "Ruins",
            "Speeds.json": "Speed",
            "Difficulties.json": "Difficulty",
            "VictoryTypes.json": "Victory",
            "Tutorials.json": "Tutorial",
            "Specialists.json": None,
            "Quests.json": None,
        }
        for filename, target in simple.items():
            kind = filename[:-5]
            for obj in self.named(filename):
                t = target
                if filename == "Beliefs.json":
                    t = "FollowerBelief" if obj.get("type") in ("Pantheon", "Follower") else "FounderBelief"
                if filename == "Buildings.json" and (obj.get("isWonder") or obj.get("isNationalWonder")):
                    t = "Wonder"
                if t is None:
                    continue
                for u in strings(obj.get("uniques")):
                    yield UniqueSite(t, f"{filename} > {obj['name']}", u, kind, obj["name"])

        for tech in self.techs():
            for u in strings(tech.get("uniques")):
                yield UniqueSite("Tech", f"Techs.json > {tech['name']}", u, "Techs", tech["name"])
        for policy in self.policies():
            for u in strings(policy.get("uniques")):
                yield UniqueSite("Policy", f"Policies.json > {policy['name']}", u, "Policies", policy["name"])
        for cst in self.named("CityStateTypes.json"):
            for key in ("friendBonusUniques", "allyBonusUniques"):
                for u in strings(cst.get(key)):
                    yield UniqueSite("CityState", f"CityStateTypes.json > {cst['name']} > {key}", u, "CityStateTypes", cst["name"])
            for u in strings(cst.get("uniques")):
                yield UniqueSite("CityState", f"CityStateTypes.json > {cst['name']}", u, "CityStateTypes", cst["name"])
        for event in self.events():
            for u in strings(event.get("uniques")):
                yield UniqueSite("Event", f"Events.json > {event['name']}", u, "Events", event["name"])
            for i, choice in enumerate(event.get("choices", []) or []):
                if isinstance(choice, dict):
                    label = choice.get("text") or f"choice {i + 1}"
                    for u in strings(choice.get("uniques")):
                        yield UniqueSite("EventChoice", f"Events.json > {event['name']} > {label}", u, "Events", event["name"])
        gu = self.obj("GlobalUniques.json")
        for u in strings(gu.get("uniques")):
            yield UniqueSite("GlobalUniques", "GlobalUniques.json > uniques", u, "GlobalUniques", "GlobalUniques")
        for u in strings(gu.get("unitUniques")):
            yield UniqueSite("Unit", "GlobalUniques.json > unitUniques", u, "GlobalUniques", "GlobalUniques")
        for u in strings(self.mod_options.get("uniques")):
            yield UniqueSite("ModOptions", "ModOptions.json > uniques", u, "ModOptions", "ModOptions")


def mod_root_from_args(argv: list[str]) -> Path:
    """`--mod <path>` selects another mod folder (used by the self-tests); default is the repo root."""
    if "--mod" in argv:
        return Path(argv[argv.index("--mod") + 1]).resolve()
    return REPO_ROOT
