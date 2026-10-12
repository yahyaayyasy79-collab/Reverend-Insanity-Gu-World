"""Unique patterns parsed from ref/unciv/docs/Modders/uniques.md, plus UniqueTarget inheritance.

Normalisation mirrors Unciv (core/.../models/translations/Translations.kt):
  * modifiers are every `<...>` match of the regex `<([^>]*)>`
  * the base text has them removed, then "  " -> " " (all occurrences) and trim()
  * top-level `[...]` parameters (nesting-aware) are replaced by `[]` to form the lookup key
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from common import UNIQUE_TARGET_KT, UNIQUES_MD

POINTY = re.compile(r"<([^>]*)>")
EXAMPLE_LINE = re.compile(r'^\?\?\? example\s+"(.*)"\s*$')
MODIFIER_TARGETS = {"Conditional", "TriggerCondition", "UnitTriggerCondition", "UnitActionModifier", "MetaModifier"}


def placeholder_params(text: str) -> list[str]:
    params, depth, start = [], 0, -1
    for i, ch in enumerate(text):
        if ch == "[":
            if depth == 0:
                start = i + 1
            depth += 1
        elif ch == "]" and depth > 0:
            depth -= 1
            if depth == 0:
                params.append(text[start:i])
    return params


def placeholder_key(text: str) -> str:
    key = text
    for param in placeholder_params(text):
        key = key.replace(f"[{param}]", "[]", 1)
    return key


def remove_modifiers(text: str) -> str:
    if "<" not in text:
        return text
    return POINTY.sub("", text).replace("  ", " ").strip()


def modifiers_of(text: str) -> list[str]:
    return [m.group(1) for m in POINTY.finditer(text)] if "<" in text else []


@dataclass
class UniquePattern:
    text: str
    params: list[str]
    targets: set[str]
    is_modifier: bool
    section: str
    no_conditionals: bool = False

    @property
    def key(self) -> str:
        return placeholder_key(self.text)


@dataclass
class UniqueDb:
    base: dict[str, list[UniquePattern]] = field(default_factory=dict)
    modifiers: dict[str, list[UniquePattern]] = field(default_factory=dict)
    inherits: dict[str, str | None] = field(default_factory=dict)

    def accepts(self, target: str, unique_target: str) -> bool:
        """UniqueTarget.canAcceptUniqueTarget: does an object of `target` accept a unique declared for `unique_target`?"""
        seen = set()
        current: str | None = target
        while current and current not in seen:
            if current == unique_target:
                return True
            seen.add(current)
            current = self.inherits.get(current)
        return False

    def all_patterns(self):
        for group in (self.base, self.modifiers):
            for patterns in group.values():
                yield from patterns


def parse_uniques_md(path: Path = UNIQUES_MD) -> tuple[dict, dict]:
    base: dict[str, list[UniquePattern]] = {}
    modifiers: dict[str, list[UniquePattern]] = {}
    section = ""
    current: UniquePattern | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if raw.startswith("## "):
            section = raw[3:].strip()
            current = None
            continue
        m = EXAMPLE_LINE.match(line)
        if m:
            text = html.unescape(m.group(1))
            is_modifier = text.startswith("<") and text.endswith(">")
            if is_modifier:
                text = text[1:-1]
            current = UniquePattern(text, placeholder_params(text), set(), is_modifier, section)
            (modifiers if is_modifier else base).setdefault(current.key, []).append(current)
            continue
        if current is None:
            continue
        if line.startswith("Applicable to:"):
            current.targets = {t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()}
        elif "does not support conditionals" in line:
            current.no_conditionals = True
    return base, modifiers


def _strip_balanced(text: str, open_ch: str, close_ch: str) -> str:
    out, depth = [], 0
    for ch in text:
        if ch == open_ch:
            depth += 1
        elif ch == close_ch and depth > 0:
            depth -= 1
            continue
        if depth == 0:
            out.append(ch)
    return "".join(out)


def parse_unique_target_inheritance(path: Path = UNIQUE_TARGET_KT) -> dict[str, str | None]:
    """Reads `inheritsFrom` for every UniqueTarget enum constant (named or second positional argument)."""
    text = path.read_text(encoding="utf-8")
    body = text[text.index("enum class UniqueTarget"):]
    body = body[body.index(") {") + 3:]
    body = body[:body.index(";\n")]                     # constants end at the first ';' line
    body = re.sub(r'"(?:\\.|[^"\\])*"', '""', body)     # drop string literals
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)   # drop block comments
    body = re.sub(r"//[^\n]*", "", body)                # drop line comments
    body = _strip_balanced(body, "{", "}")              # drop constant bodies (overrides)
    result: dict[str, str | None] = {}
    for m in re.finditer(r"\b([A-Z]\w*)\s*(\((?:[^()]|\([^()]*\))*\))?\s*,?", body):
        name, args = m.group(1), m.group(2)
        if name in ("ModifierType",):
            continue
        parent = None
        if args:
            named = re.search(r"inheritsFrom\s*=\s*(\w+)", args)
            if named:
                parent = named.group(1)
            else:
                parts = [p.strip() for p in args[1:-1].split(",")]
                if len(parts) >= 2 and re.fullmatch(r"[A-Z]\w*", parts[1]):
                    parent = parts[1]
        result.setdefault(name, parent)
    return result


# Fallback if UniqueTarget.kt is unavailable (copied from 4.22.8).
_FALLBACK_INHERITS = {
    "Triggerable": None, "UnitTriggerable": "Triggerable", "Global": "Triggerable", "Nation": "Global",
    "Personality": None, "Era": "Global", "Tech": "Global", "Policy": "Global", "FounderBelief": "Global",
    "FollowerBelief": "Triggerable", "Building": "Global", "Wonder": "Building", "UnitAction": "UnitTriggerable",
    "Unit": "UnitAction", "UnitType": "Unit", "Promotion": "Unit", "Terrain": None, "Improvement": "Triggerable",
    "Resource": "Global", "Ruins": "UnitTriggerable", "GlobalUniques": "Global", "Speed": "GlobalUniques",
    "Difficulty": "GlobalUniques", "Tutorial": None, "CityState": "Global", "ModOptions": None, "Event": None,
    "EventChoice": "UnitTriggerable", "Victory": None, "Conditional": None, "TriggerCondition": None,
    "UnitTriggerCondition": None, "UnitActionModifier": None, "MetaModifier": None,
}


@lru_cache(maxsize=1)
def load_db() -> UniqueDb:
    base, modifiers = parse_uniques_md()
    inherits = dict(_FALLBACK_INHERITS)
    if UNIQUE_TARGET_KT.exists():
        parsed = parse_unique_target_inheritance()
        if {"Building", "Unit", "Global", "EventChoice"} <= parsed.keys():
            inherits = parsed
    return UniqueDb(base, modifiers, inherits)


if __name__ == "__main__":
    db = load_db()
    print(f"{sum(len(v) for v in db.base.values())} base patterns, "
          f"{sum(len(v) for v in db.modifiers.values())} modifier patterns, "
          f"{len(db.inherits)} unique targets")
    drift = {k: (v, db.inherits.get(k)) for k, v in _FALLBACK_INHERITS.items() if db.inherits.get(k) != v}
    extra = sorted(set(db.inherits) - set(_FALLBACK_INHERITS))
    print("UniqueTarget.kt matches the 4.22.8 fallback" if not drift and not extra
          else f"UniqueTarget drift vs 4.22.8 fallback: changed={drift} new={extra}")
