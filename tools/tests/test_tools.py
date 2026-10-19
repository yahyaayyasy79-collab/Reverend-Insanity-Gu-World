"""Self-tests for the checkers. A checker that silently passes broken JSON is worse than no checker.

Run: python3 -m unittest discover -s tools/tests -t tools   (tools/check_all does this first)
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_package
import check_refs
import check_schema
import lint_uniques
import unciv_ci
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
            self.assertEqual([i for i in r.warnings if "no icon for" in i.message], [])
            self.assertFalse(make_placeholders.is_placeholder(real), "real art was overwritten")
            self.assertTrue(make_placeholders.is_placeholder(root / "Images" / "TechIcons" / "Awakening.png"))


@unittest.skipUnless(unciv_ci.jar_path().exists() and shutil.which("java"), "needs java + ref/Unciv-<tag>.jar")
class OfficialValidator(unittest.TestCase):
    """Unciv's own RulesetValidator (release jar, mod-ci) agrees with the capability proof and catches breakage."""

    def test_capability_proof_is_clean_for_unciv_itself(self):
        r = Reporter("unciv_ci")
        unciv_ci.run(PROOF, r)
        self.assertEqual([i for i in r.issues if i.severity != "INFO" or "Unciv" in i.where], [],
                         "the official validator reports findings on fixtures/capability_proof")

    def test_errors_are_reported_and_repo_is_not_rewritten(self):
        with TempMod({}, base=PROOF) as root:
            units = root / "jsons" / "Units.json"
            data = json.loads(units.read_text())
            data[1]["requiredTech"] = "Nope Tech"
            units.write_text(json.dumps(data))
            before = units.read_bytes()
            r = Reporter("unciv_ci")
            unciv_ci.run(root, r)
            self.assertIn("requires tech Nope Tech", messages(r))
            self.assertEqual(units.read_bytes(), before, "mod-ci must run on a copy")

    def test_pack_produces_an_atlas_check_refs_accepts(self):
        import make_placeholders
        with TempMod({}, base=PROOF) as root:
            with contextlib.redirect_stdout(io.StringIO()):
                make_placeholders.main(["--mod", str(root)])
            unciv_ci.run(root, Reporter("unciv_ci"), pack=True)
            self.assertTrue((root / "game.atlas").exists() and (root / "Atlases.json").exists())
            r = Reporter("refs")
            check_refs.run(root, r)
            self.assertEqual(r.errors + r.warnings, [])
            (root / "Images" / "UnitIcons" / "Late Addition.png").write_bytes(
                (root / "Images" / "TechIcons" / "Awakening.png").read_bytes())
            r = Reporter("refs")
            check_refs.run(root, r)
            self.assertIn("atlas is stale", messages(r, "WARNING"))


class LoreMapping(unittest.TestCase):
    """The mod's jsons/ is what tools/gen_ruleset.py generates from data/; docs/LORE_MAPPING.md quotes exactly its
    uniques (and check_all validates them); its refinement ladder passes tools/ladder_check.py."""

    # Files whose uniques the document must quote in full (terrains and engine-coupled improvements are Vanilla copies).
    QUOTED_FILES = ("Units.json", "UnitPromotions.json", "Buildings.json", "Policies.json", "Techs.json", "Events.json",
                    "Nations.json", "GlobalUniques.json", "Ruins.json", "TileResources.json", "CityStateTypes.json",
                    "Personalities.json", "ModOptions.json")

    @staticmethod
    def _strings(obj, out: set[str]) -> set[str]:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ("uniques", "friendBonusUniques", "allyBonusUniques", "milestones") and isinstance(v, list):
                    out.update(v)
                else:
                    LoreMapping._strings(v, out)
        elif isinstance(obj, list):
            for x in obj:
                LoreMapping._strings(x, out)
        return out

    def setUp(self):
        if not (REPO_ROOT / "jsons").is_dir():
            self.skipTest("jsons/ not generated yet")

    def test_jsons_match_the_data_tables(self):
        r = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "gen_ruleset.py"), "--check", "--quiet"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_refinement_ladder_has_no_empty_or_double_attempts(self):
        import ladder_check
        states, errors = ladder_check.check(REPO_ROOT)
        self.assertGreater(states, 1000)
        self.assertEqual(errors[:5], [], f"{len(errors)} ladder error(s)")

    def test_document_matches_ruleset(self):
        doc = REPO_ROOT / "docs" / "LORE_MAPPING.md"
        if not doc.exists():
            self.skipTest("docs/LORE_MAPPING.md not written yet")
        # C3: the path promotions are generated from data/paths*.csv and quoted by docs/PATHS.md (tools/gen_paths.py
        # writes its tables); their hidden conflict lines follow one documented rule and are exempt. PATHS.md's prose
        # also sketches patterns, so only LORE_MAPPING.md's quotes must all be real uniques.
        import gen_paths
        files = {f.name: json.loads(f.read_text(encoding="utf-8")) for f in (REPO_ROOT / "jsons").glob("*.json")}
        generated = self._strings(list(files.values()), set())

        def quotes(text: str) -> set[str]:
            found = set(re.findall(r"`([^`\n]+)`", text))
            found.update(line for block in re.findall(r"```\n(.*?)```", text, re.S) for line in block.splitlines())
            return found

        quoted = quotes(doc.read_text(encoding="utf-8"))

        db = load_db()
        pattern_texts = {p.text for p in db.all_patterns()}
        unvalidated = []
        for q in quoted:
            is_modifier = q.startswith("<") and q.endswith(">")
            bare = q[1:-1] if is_modifier else q
            if "[" not in q or placeholder_key(bare if is_modifier else remove_modifiers(q)) not in (
                    db.modifiers if is_modifier else db.base):
                continue  # not a unique (a parameter value, a field name...)
            if q not in generated and bare not in pattern_texts:
                unvalidated.append(q)
        self.assertEqual(unvalidated, [], "LORE_MAPPING.md quotes uniques jsons/ does not contain")

        quoted |= quotes((REPO_ROOT / "docs" / "PATHS.md").read_text(encoding="utf-8"))
        missing = []
        for name in self.QUOTED_FILES:
            for u in self._strings(files[name], set()):
                plain_weight = "% weight to this choice for AI decisions" in u and "<" not in u
                if u not in quoted and not (name == "Events.json" and plain_weight) and not gen_paths.CONFLICT.match(u):
                    missing.append(f"{name}: {u}")
        self.assertEqual(missing, [], "jsons/ contains uniques LORE_MAPPING.md does not show")


class MapFile(unittest.TestCase):
    """maps/Qing Mao Mountain is what tools/make_map.py builds from its design (Unciv's own serializer, the jar)."""

    def test_map_is_current(self):
        import shutil
        from common import REF_DIR, ref_tag
        if not (shutil.which("java") and shutil.which("javac") and (REF_DIR / f"Unciv-{ref_tag()}.jar").exists()):
            self.skipTest("needs java, javac and the release jar")
        r = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "make_map.py"), "--check", "--quiet"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class Autoplay(unittest.TestCase):
    """A short headless AI game on the mod must not crash (tools/autoplay.py, the release jar)."""

    def test_short_game_runs(self):
        import shutil
        from common import REF_DIR, ref_tag
        if not (shutil.which("java") and shutil.which("javac") and (REF_DIR / f"Unciv-{ref_tag()}.jar").exists()):
            self.skipTest("needs java, javac and the release jar")
        if not (REPO_ROOT / "jsons").is_dir():
            self.skipTest("jsons/ not generated yet")
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "autoplay.py"), "--games", "1", "--turns", "8",
                                "--jobs", "1", "--out", tmp, "--quiet"], capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
            rows = [json.loads(line) for f in Path(tmp).glob("game-*.jsonl") for line in f.read_text().splitlines()]
            self.assertEqual(sum(1 for x in rows if x["event"] == "turn" and x["major"]) // 4, 8)


class Translations(unittest.TestCase):
    """jsons/translations matches data/, covers every string the mod shows, keeps placeholders, and every new object
    has civilopedia text (MOD_SPEC section 11, Definition of Done)."""

    def setUp(self):
        from common import REF_DIR, ref_tag
        if not (REF_DIR / f"Unciv-{ref_tag()}.jar").exists() or not (REPO_ROOT / "jsons" / "translations").is_dir():
            self.skipTest("needs the release jar and generated translations")

    def test_up_to_date(self):
        r = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "gen_translations.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_every_displayed_string_is_translated(self):
        import gen_translations as gt
        ours = gt.read_properties(REPO_ROOT / "jsons" / "translations" / "Indonesian.properties")
        base = gt.base_translations("Indonesian")
        missing = [k for k in gt.displayed_strings() if k not in ours and k not in base]
        self.assertEqual(missing, [], "strings without an Indonesian translation (data/translations_id.csv)")

    def test_placeholders_survive_translation(self):
        import gen_translations as gt
        bad = []
        for f in ("Indonesian.properties", "English.properties"):
            for k, v in gt.read_properties(REPO_ROOT / "jsons" / "translations" / f).items():
                if sorted(re.findall(r"\[[^\]]*\]", k)) != sorted(re.findall(r"\[[^\]]*\]", v)):
                    bad.append(f"{f}: {k}")
        self.assertEqual(bad, [])

    def test_every_new_object_has_civilopedia_text(self):
        missing = []
        def objects(f):
            data = json.loads((REPO_ROOT / "jsons" / f).read_text(encoding="utf-8"))
            if f == "Techs.json":
                return [t for c in data for t in c["techs"]]
            if f == "Policies.json":
                return [p for b in data for p in [b] + b["policies"]]
            return data
        for f in ("Eras.json", "Techs.json", "Units.json", "UnitPromotions.json", "Buildings.json", "TileResources.json",
                  "Policies.json", "VictoryTypes.json", "UnitTypes.json"):  # city-state types have no page
            missing += [f"{f}: {o['name']}" for o in objects(f) if not o.get("civilopediaText")]
        nations = json.loads((REPO_ROOT / "jsons" / "Nations.json").read_text(encoding="utf-8"))
        missing += [f"Nations.json: {n['name']}" for n in nations
                    if n["name"] not in ("Barbarians", "Spectator") and not n.get("civilopediaText")]
        self.assertEqual(missing, [], "objects without civilopedia text (data/civilopedia.csv)")


class Balance(unittest.TestCase):
    """docs/BALANCE.md lists every tunable number of jsons/ (MOD_SPEC section 10): its inventory must be current."""

    def test_inventory_up_to_date(self):
        if not (REPO_ROOT / "docs" / "BALANCE.md").exists():
            self.skipTest("docs/BALANCE.md not written yet")
        r = subprocess.run([sys.executable, str(REPO_ROOT / "tools" / "gen_balance.py"), "--check"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_numbers_are_found(self):
        import gen_balance as gb
        self.assertEqual(gb.numbers("Gain [30]-[60] [Gold]"), ["30-60"])
        self.assertEqual(gb.numbers("[-6 Gold] <for [20] turns>"), ["-6", "20"])
        self.assertEqual(gb.numbers("[This Unit] gains the [Jade Skin Gu] promotion <when above [0] [Jade]> "
                                    "<with [85]% chance>"), ["85"])  # food gates are logic, not balance


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
