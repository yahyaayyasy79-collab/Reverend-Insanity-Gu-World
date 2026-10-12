#!/usr/bin/env python3
"""Run Unciv's own Ruleset Validator (the release jar's `mod-ci` mode) on the mod, headless.

`java -jar Unciv.jar mod-ci` (desktop/.../DesktopLauncher.kt) packs Images* into atlases, loads jsons/,
auto-updates deprecated uniques IN PLACE, runs RulesetValidator and exits 1 on Error severity. To keep the
repository untouched it runs in a temporary copy:

  * every validator line is reported (Error/ErrorOptionsOnly -> ERROR, Warning/WarningOptionsOnly -> WARNING,
    OK -> INFO); "OptionsOnly" lines are what "Locate mod errors" shows in its tab;
  * if Unciv would auto-update a JSON file (deprecated uniques), that is a WARNING - fix data/*.csv instead;
  * --pack copies the packed atlas (game.atlas, game*.png, other *.atlas, Atlases.json) back into the mod root,
    which is what Android players need (MOD_SPEC §11; Android cannot pack).

The jar is fetched by tools/fetch_ref.sh to ref/Unciv-<tag>.jar. Without java or the jar this step is skipped
with a warning. Usage: tools/unciv_ci.py [--mod PATH] [--pack] [--quiet]
"""
from __future__ import annotations

import filecmp
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from common import REF_DIR, Reporter, mod_root_from_args, ref_tag

SEVERITY_RE = re.compile(r"^(Error|ErrorOptionsOnly|Warning|WarningOptionsOnly|OK): ")
MAP = {"Error": "ERROR", "ErrorOptionsOnly": "ERROR", "Warning": "WARNING", "WarningOptionsOnly": "WARNING",
       "OK": "INFO"}
# RulesetErrorList.getErrorText escapes brackets as U+27E6/U+27E7 and U+2329/U+232A
UNKLUDGE = str.maketrans({"\u27e6": "[", "\u27e7": "]", "\u2329": "<", "\u232a": ">"})
PACKED = re.compile(r"^(.*\.atlas|game\d*\.png|.*\d*\.png|Atlases\.json)$")


def jar_path() -> Path:
    return REF_DIR / f"Unciv-{ref_tag()}.jar"


def parse(stdout: str) -> list[tuple[str, str]]:
    entries: list[list[str]] = []
    for line in stdout.splitlines():
        if SEVERITY_RE.match(line):
            entries.append([line])
        elif entries and line.strip() and not line.startswith(("Loaded ", "20")):  # skip loader / log lines
            entries[-1].append(line.strip())
    out = []
    for lines in entries:
        severity, text = lines[0].split(": ", 1)
        out.append((severity, " ".join([text] + lines[1:]).translate(UNKLUDGE)))
    return out


def run(mod_root: Path, reporter: Reporter, pack: bool = False) -> None:
    jsons = mod_root / "jsons"
    if not jsons.is_dir():
        reporter.info("unciv_ci", "no jsons/ folder yet - nothing for the official validator")
        return
    jar = jar_path()
    if not jar.exists() or shutil.which("java") is None:
        reporter.warn("unciv_ci", f"official validator skipped: needs java and {jar} (tools/fetch_ref.sh)")
        return

    with tempfile.TemporaryDirectory(prefix="unciv-ci-") as tmp:
        work = Path(tmp)
        shutil.copytree(jsons, work / "jsons")
        images = [p for p in mod_root.glob("Images*") if p.is_dir()]
        for folder in images:
            shutil.copytree(folder, work / folder.name)
        try:
            result = subprocess.run(
                ["java", "-Dstdout.encoding=UTF-8", "-Dfile.encoding=UTF-8", "-jar", str(jar), "mod-ci"],
                cwd=work, capture_output=True, text=True, encoding="utf-8", timeout=900)
        except subprocess.TimeoutExpired:
            reporter.error("unciv_ci", "official validator timed out after 15 minutes")
            return

        findings = parse(result.stdout)
        for severity, text in findings:
            {"ERROR": reporter.error, "WARNING": reporter.warn, "INFO": reporter.info}[MAP[severity]](
                f"Unciv {ref_tag()} {severity}", text)
        if result.returncode != 0 and not any(MAP[s] == "ERROR" for s, _ in findings):
            tail = (result.stderr or result.stdout).strip().splitlines()[-5:]
            reporter.error("unciv_ci", f"mod-ci exited {result.returncode}: " + " | ".join(tail))

        compare = filecmp.dircmp(jsons, work / "jsons")
        for name in compare.diff_files:
            reporter.warn(f"jsons/{name}", "Unciv's autoupdater would rewrite deprecated uniques here "
                                           "(fix the source table / generator, never accept the rewrite)")

        if pack:
            copied = []
            for path in sorted(work.iterdir()):
                if path.is_file() and PACKED.match(path.name):
                    shutil.copy2(path, mod_root / path.name)
                    copied.append(path.name)
            if images and not copied:
                reporter.error("unciv_ci", "--pack: Images folders exist but Unciv produced no atlas")
            reporter.info("unciv_ci", f"packed atlas files copied to the mod root: {copied or 'none (no Images)'}")
        reporter.info("unciv_ci", f"official validator: {len(findings)} line(s), exit {result.returncode}")


def main(argv: list[str]) -> int:
    reporter = Reporter("unciv_ci")
    run(mod_root_from_args(argv), reporter, pack="--pack" in argv)
    reporter.print(verbose="--quiet" not in argv)
    return reporter.exit_code()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
