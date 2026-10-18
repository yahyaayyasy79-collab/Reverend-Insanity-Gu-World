#!/usr/bin/env python3
"""Validate every jsons/*.json (and jsons/TileSets/*.json) against ref/.../docs/Modders/schemas.

Also enforces the project's strict-JSON rule (no trailing commas, comments, duplicate keys or BOM),
flags file names Unciv does not recognise, and keys the schema does not declare where the schema
itself is permissive (Eras, Religions).

Usage: tools/check_schema.py [--mod PATH] [--quiet]
"""
from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator
from referencing import Registry, Resource

from common import RULESET_FILES, SCHEMA_DIR, Reporter, StrictJsonError, load_strict_json, mod_root_from_args, \
    require_ref


# Keys the docs (Mod-file-structure/*.md) document and the bundled G&K ruleset uses, but the 4.22.8 schema
# does not declare. Reported as warnings, not errors; the docs win (MOD_SPEC.md rule 1).
SCHEMA_GAPS = {
    "Personalities": {"denounceWillingness"},  # docs: Personality Behaviours ("not fully implemented yet")
    "Eras": {"uniques", "civilopediaText"},    # docs: Eras.json attribute table; civilopediaText [src]: Era is a
                                               # RulesetObject, which carries it (used by Slice 1's era pages)
}


def build_registry() -> tuple[Registry, dict[str, dict]]:
    """Registers every schema under its $id, so relative $refs like "refs/Uniques.schema.json" resolve offline."""
    schemas: dict[str, dict] = {}
    resources = []
    for path in sorted(SCHEMA_DIR.rglob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
        if path.parent == SCHEMA_DIR:
            schemas[path.name.replace(".schema.json", "")] = schema
    return Registry().with_resources(resources), schemas


def schema_name_for(path: Path, jsons: Path) -> str | None:
    if path.parent.name == "TileSets" and path.parent.parent == jsons:
        return "TileSetConfig"
    return path.stem


def undeclared_keys(instance, schema: dict) -> list[str]:
    """Keys of array items not declared by a schema whose items allow additional properties."""
    items = schema.get("items") if schema.get("type") == "array" else None
    if not isinstance(items, dict) or items.get("additionalProperties") is False or "properties" not in items:
        return []
    declared = set(items["properties"])
    found = set()
    for item in instance if isinstance(instance, list) else []:
        if isinstance(item, dict):
            found |= set(item) - declared
    return sorted(found)


def format_path(error) -> str:
    parts = []
    for p in error.absolute_path:
        parts.append(f"[{p}]" if isinstance(p, int) else f".{p}")
    return "".join(parts) or "(root)"


def object_name(document, error) -> str:
    """Best-effort name of the top-level object an error points into, for readable messages."""
    path = list(error.absolute_path)
    node = document
    name = ""
    for p in path:
        try:
            node = node[p]
        except (KeyError, IndexError, TypeError):
            break
        if isinstance(node, dict) and isinstance(node.get("name"), str):
            name = node["name"]
    return f" ({name})" if name else ""


def run(mod_root: Path, reporter: Reporter) -> None:
    jsons = mod_root / "jsons"
    if not jsons.is_dir():
        reporter.info("jsons/", "no jsons/ folder yet - nothing to validate")
        return

    registry, schemas = build_registry()
    files = sorted(jsons.glob("*.json")) + sorted((jsons / "TileSets").glob("*.json"))
    for path in files:
        rel = path.relative_to(mod_root).as_posix()
        try:
            document = load_strict_json(path)
        except StrictJsonError as ex:
            reporter.error(rel, str(ex))
            continue

        name = schema_name_for(path, jsons)
        if path.parent == jsons and path.name not in RULESET_FILES:
            close = difflib.get_close_matches(path.name, RULESET_FILES, n=1)
            reporter.warn(rel, "not a ruleset file Unciv recognises - it will be ignored"
                               + (f" (did you mean {close[0]}?)" if close else ""))
            continue
        schema = schemas.get(name)
        if schema is None:
            reporter.info(rel, f"no schema {name}.schema.json in this Unciv version - skipped")
            continue

        validator = Draft7Validator(schema, registry=registry)
        count = 0
        gaps = SCHEMA_GAPS.get(name, set())
        sort_key = lambda e: [(0, p, "") if isinstance(p, int) else (1, 0, str(p)) for p in e.absolute_path]
        for error in sorted(validator.iter_errors(document), key=sort_key):
            where = f"{format_path(error)}{object_name(document, error)}"
            if error.validator == "additionalProperties" and isinstance(error.instance, dict):
                unexpected = set(error.instance) - set(error.schema.get("properties", {}))
                if unexpected and unexpected <= gaps:
                    reporter.warn(rel, f"{where}: {sorted(unexpected)} documented but missing from {name}.schema.json")
                    continue
            count += 1
            reporter.error(rel, f"{where}: {error.message}")
        for key in undeclared_keys(document, schema):
            if key in gaps:
                reporter.warn(rel, f"key \"{key}\" documented but missing from {name}.schema.json")
            else:
                reporter.warn(rel, f"key \"{key}\" is not declared in {name}.schema.json - check the docs for typos")
        if count == 0:
            reporter.info(rel, f"valid against {name}.schema.json")


def main(argv: list[str]) -> int:
    require_ref()
    reporter = Reporter("check_schema")
    run(mod_root_from_args(argv), reporter)
    reporter.print(verbose="--quiet" not in argv)
    return reporter.exit_code()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
