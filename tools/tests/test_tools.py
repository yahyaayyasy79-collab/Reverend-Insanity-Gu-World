"""Self-tests for the checkers. A checker that silently passes broken JSON is worse than no checker.

Run: python3 -m unittest discover -s tools/tests -t tools   (tools/check_all does this first)
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import check_package
import check_refs
import check_schema
import lint_uniques
from common import REPO_ROOT, Reporter, Ruleset
from uniques_db import load_db, modifiers_of, placeholder_key, remove_modifiers

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PROOF = FIXTURES / "capability_proof"


def run_all(mod_root: Path) -> dict[str, Reporter]:
    out = {}
    for name, module in (("schema", check_schema), ("lint", lint_uniques), ("refs", check_refs)):
        r = Reporter(name)
        module.run(mod_root, r)
        out[name] = r
    return out


def messages(reporter: Reporter, severity: str = "ERROR") -> str:
    return "\n".join(str(i) for i in reporter.issues if i.severity == severity)


class TempMod:
    """A throwaway mod folder: files given as {name: python object | raw text}."""

    def __init__(self, files: dict[str, object], base: Path | None = None):
        self.dir = Path(tempfile.mkdtemp(prefix="unciv-mod-test-"))
        if base:
            shutil.copytree(base, self.dir, dirs_exist_ok=True)
        jsons = self.dir / "jsons"
        jsons.mkdir(exist_ok=True)
        for name, content in files.items():
            text = content if isinstance(content, str) else json.dumps(content, indent=1)
            (jsons / name).write_text(text, encoding="utf-8")

    def __enter__(self) -> Path:
        return self.dir

    def __exit__(self, *exc):
        shutil.rmtree(self.dir, ignore_errors=True)


class Normalisation(unittest.TestCase):
    def test_nested_brackets_become_one_placeholder(self):
        self.assertEqual(placeholder_key("[+10]% Strength <for [non-[Wounded]] units>"), "[]% Strength <for [] units>")
        self.assertEqual(placeholder_key("[[Melee] Units]"), "[]")

    def test_modifiers_are_split_like_unciv(self):
        text = "[+1 Gold]  <with a garrison> <for [Melee] units>"
        self.assertEqual(remove_modifiers(text), "[+1 Gold]")
        self.assertEqual(modifiers_of(text), ["with a garrison", "for [Melee] units"])

    def test_docs_parse(self):
        db = load_db()
        self.assertIn("Triggers a [] event", db.base)
        self.assertIn("every [] turns", db.modifiers)
        self.assertTrue(db.accepts("Building", "Global"))
        self.assertTrue(db.accepts("Promotion", "UnitTriggerable"))
        self.assertTrue(db.accepts("EventChoice", "Triggerable"))
        self.assertFalse(db.accepts("Terrain", "Global"))


class CapabilityProof(unittest.TestCase):
    """Every unique cited in docs/CAPABILITIES.md is exercised by fixtures/capability_proof."""

    def test_fixture_has_no_errors(self):
        reports = run_all(PROOF)
        for name, r in reports.items():
            self.assertEqual(r.errors, [], f"{name}:\n{messages(r)}")
        self.assertEqual(reports["lint"].warnings, [], messages(reports["lint"], "WARNING"))

    def test_capabilities_doc_cites_only_documented_uniques(self):
        doc = REPO_ROOT / "docs" / "CAPABILITIES.md"
        if not doc.exists():
            self.skipTest("docs/CAPABILITIES.md not written yet")
        db = load_db()
        proof_uniques = {s.text for s in Ruleset(PROOF).load().unique_sites()}
        bad, unproven = [], []
        for span in re.findall(r"`([^`\n]+)`", doc.read_text(encoding="utf-8")):
            if "[" not in span or span.lstrip().startswith(("[\"", "{", "jsons/", "Images")) or "=" in span:
                continue
            is_modifier = span.startswith("<") and span.endswith(">")
            key = placeholder_key(span[1:-1] if is_modifier else remove_modifiers(span))
            if key in check_refs.MILESTONES:  # victory milestones are not uniques
                continue
            if key not in (db.modifiers if is_modifier else db.base):
                bad.append(span)
            if not is_modifier and "[" in span and not any(key == placeholder_key(remove_modifiers(u))
                                                           for u in proof_uniques):
                unproven.append(span)
        self.assertEqual(bad, [], "CAPABILITIES.md cites uniques that uniques.md does not document")
        self.assertEqual(unproven, [], "CAPABILITIES.md cites uniques missing from fixtures/capability_proof")


BAD_UNITS = [
    {"name": "Settler", "unitType": "Civilian", "uniques": []},          # nobody can found a city
    {"name": "Bad Gu", "unitType": "Melee", "strength": 5, "requiredTech": "Nonexistent Tech", "upgradesTo": "Loop Gu",
     "uniques": ["triggers a [Some Event] event",                      # wrong case -> untyped
                 "[+10]% Strength <on a full moon>",                   # unknown modifier
                 "[abc]% maintenance costs",                           # bad number
                 "Triggers a [Missing Event] event",                   # unknown event
                 "Costs [5] [Iron]",                                   # Iron is not Stockpiled
                 "[+10]% Strength <once>"]},                           # action modifier on a non-action
    {"name": "Loop Gu", "unitType": "Melee", "strength": 5, "upgradesTo": "Bad Gu"},
    {"name": "Gu Maître", "unitType": "Melee", "strength": 5},  # non-ASCII
]
BAD_FILES = {
    "ModOptions.json": {"isBaseRuleset": True},
    "Units.json": BAD_UNITS,
    "UnitTypes.json": [{"name": "Civilian", "movementType": "Land"}, {"name": "Melee", "movementType": "Land"}],
    "Buildings.json": [{"name": "Wall", "cost": 10, "unexpectedField": 1,
                        "uniques": ["Can pass through impassable tiles", "[+1 gold]"]}],
    "TileResources.json": [{"name": "Iron", "resourceType": "Strategic"}],
    "Terrains.json": [{"name": "Plains", "type": "Land",
                       "uniques": ["Units ending their turn on this terrain take [5] damage <when at war>"]}],
    "Nations.json": [{"name": "Clan", "leaderName": "Elder", "outerColor": [1, 2, 3], "cities": ["A"]}],
    "Eras.json": [{"name": "First era", "startingSettlerUnit": "Settler", "startingMilitaryUnit": "Bad Gu"}],
    "Events.json": [{"name": "Some Event", "choices": [{"text": "Go", "uniques": ["Gain [5] [Gold]"]}]}],
    "Techs.json": "[{\"columnNumber\": 0, \"era\": \"First era\", \"buildingCost\": 1, \"wonderCost\": 1, \"techs\": [],}]",
    "Policies.json": "{\"a\": 1, \"a\": 2}",
    "Unit.json": [],
}


class BrokenMod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TempMod(BAD_FILES)
        cls.reports = run_all(cls.tmp.dir)
        cls.errors = {k: messages(v) for k, v in cls.reports.items()}
        cls.warnings = {k: messages(v, "WARNING") for k, v in cls.reports.items()}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.__exit__()

    def assertReported(self, tool, needle, severity="ERROR"):
        haystack = (self.errors if severity == "ERROR" else self.warnings)[tool]
        self.assertIn(needle, haystack, f"{tool} did not report {needle!r}:\n{haystack}")

    def test_strict_json(self):
        self.assertReported("schema", "jsons/Techs.json: invalid JSON")
        self.assertReported("schema", "duplicate key 'a'")
        self.assertReported("schema", "'unexpectedField' was unexpected")
        self.assertReported("schema", "Unit.json: not a ruleset file", "WARNING")

    def test_unique_patterns(self):
        self.assertReported("lint", "\"triggers a [Some Event] event\": untyped unique")
        self.assertReported("lint", "unknown modifier <on a full moon>")
        self.assertReported("lint", "must be a whole number like +25")
        self.assertReported("lint", "\"Missing Event\" is not a event defined in the mod")
        self.assertReported("lint", "resource with the \"Stockpiled\" unique")
        self.assertReported("lint", "\"Can pass through impassable tiles\": not applicable to Building")
        self.assertReported("lint", "must look like '+2 Production, +1 Gold'")
        self.assertReported("lint", "does not support conditionals")
        self.assertReported("lint", "<once> (UnitActionModifier) is not an acceptable modifier", "WARNING")

    def test_cross_references(self):
        self.assertReported("refs", "requiredTech \"Nonexistent Tech\" is not a tech")
        self.assertReported("refs", "upgrade cycle")
        self.assertReported("refs", "no city-founding unit")
        self.assertReported("refs", "no \"Barbarians\" nation")
        self.assertReported("refs", "MOD_SPEC rule 7")
        self.assertReported("refs", "object name is not ASCII")
        self.assertReported("refs", "no Water terrain")
        self.assertReported("refs", "never triggered", "WARNING")


class FilterMarkers(unittest.TestCase):
    FILES = {"Units.json": [{"name": "Gu", "unitType": "Melee", "strength": 1, "uniques": ["Heaven Fated"]},
                            {"name": "Hunter", "unitType": "Melee", "strength": 1,
                             "uniques": ["[+10]% Strength <vs [Heaven Fated] units>"]}],
             "UnitTypes.json": [{"name": "Melee", "movementType": "Land"}]}

    def lint(self, allowlist: set[str]) -> Reporter:
        with TempMod(self.FILES) as root:
            r = Reporter("lint")
            linter = lint_uniques.UniqueLinter(load_db(), Ruleset(root).load(), r)
            linter.allowlist = allowlist
            linter.run()
            return r

    def test_marker_needs_allowlist(self):
        self.assertIn("untyped unique", messages(self.lint(set())))
        self.assertEqual(self.lint({"Heaven Fated"}).errors, [])


class Placeholders(unittest.TestCase):
    def test_generated_icons_satisfy_check_refs_and_spare_real_art(self):
        import make_placeholders
        from PIL import Image
        with TempMod({}, base=PROOF) as root:
            real = root / "Images" / "UnitIcons" / "Gu Master.png"
            real.parent.mkdir(parents=True)
            Image.new("RGBA", (10, 10), (1, 2, 3, 255)).save(real)
            with contextlib.redirect_stdout(io.StringIO()):
                make_placeholders.main(["--mod", str(root)])
                make_placeholders.main(["--mod", str(root), "--force"])
            r = Reporter("refs")
            check_refs.run(root, r)
            self.assertEqual([i for i in r.warnings if "no icon" in i.message], [])
            self.assertFalse(make_placeholders.is_placeholder(real), "real art was overwritten")
            self.assertTrue(make_placeholders.is_placeholder(root / "Images" / "TechIcons" / "Awakening.png"))


class Packaging(unittest.TestCase):
    def test_too_much_tooling_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for d in ("jsons", "tools", "docs", "data"):
                (root / d).mkdir()
            self.assertTrue(check_package.check_packaging(root).errors)
            for f in ("README.md", "CHANGELOG.md", "CLAUDE.md"):
                (root / f).write_text("x")
            self.assertFalse(check_package.check_packaging(root).errors)


if __name__ == "__main__":
    unittest.main()
