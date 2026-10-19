#!/usr/bin/env python3
"""Headless AI-vs-AI games on the mod, for balance data (MOD_SPEC section 10, the user's tuning rule).

Compiles tools/autoplay/Autoplay.java against the Unciv release jar (ref/Unciv-<tag>.jar, tools/fetch_ref.sh), stages
the mod in a work folder as mods/<MOD_NAME>, and plays N games of T turns in which every major civ is AI and a
Spectator watches. Defaults follow the user's rule: Strategic Balance ON, no manual intervention.

  tools/autoplay.py [--mod PATH] [--games 4] [--turns 100] [--seed 1] [--jobs 2] [--difficulty Prince]
                    [--map-size Small] [--city-states N] [--out DIR] [--no-strategic-balance] [--quiet]
  tools/autoplay.py --summarize DIR     # re-print the summary of finished games

Writes DIR/game-<seed>.jsonl (one line per civ per turn: stones, upkeep, resources, units, Gu holders, hunger starts,
deaths and recoveries per Gu rank, trades, wars) and DIR/summary.json. Exit 1 if any game crashed.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import REF_DIR, REPO_ROOT, ref_tag  # noqa: E402

MOD_NAME = "Reverend Insanity Gu World"  # the installed folder name (CLAUDE.md decisions)
JAVA_SRC = Path(__file__).resolve().parent / "autoplay" / "Autoplay.java"
DEATH = re.compile(r"^\[This Unit\] loses the \[(.+?)\] promotion <upon losing the \[(.+?)\] status> <when below \[0\] \[(.+?)\]>")
TIMER = re.compile(r"^\[This Unit\] gains the \[(.+?)\] status for \[(\d+)\] turn\(s\)")


def load(mod: Path, name: str):
    import json5  # lenient: also reads Unciv's bundled rulesets (control games)
    path = mod / "jsons" / name
    return json5.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def gu_table(mod: Path) -> list[tuple[str, str, str, int]]:
    """(Gu, hunger status, food, rank) from the promotions; rank from the status length (shorter = rank 1)."""
    rows = []
    for p in load(mod, "UnitPromotions.json"):
        death = next((m for u in p.get("uniques", []) if (m := DEATH.match(u))), None)
        timer = next((int(m[2]) for u in p.get("uniques", []) if (m := TIMER.match(u))), None)
        if death and timer:
            rows.append((death[1], death[2], death[3], timer))
    lengths = sorted({t for *_, t in rows})
    return [(g, s, f, lengths.index(t) + 1) for g, s, f, t in rows]


def config(mod: Path, args, seed: int) -> str:
    nations = load(mod, "Nations.json")
    majors = args.majors.split(",") if args.majors else [
        n["name"] for n in nations if "cityStateType" not in n and n["name"] not in ("Barbarians", "Spectator")]
    city_states = sum(1 for n in nations if "cityStateType" in n)
    strategic = [r["name"] for r in load(mod, "TileResources.json") if r.get("resourceType") == "Strategic"]
    eras = load(mod, "Eras.json")
    gus = gu_table(mod)
    lines = [f"mod={args.mod_name}", f"turns={args.turns}", f"seed={seed}", f"difficulty={args.difficulty}",
             f"mapSize={args.map_size}", f"cityStates={args.city_states if args.city_states is not None else city_states}",
             f"speed={args.speed}", f"startingEra={eras[0]['name'] if eras else 'Ancient era'}",
             f"strategicBalance={'false' if args.no_strategic_balance else 'true'}"] + (
        [f"map={Path(args.map).resolve()}"] if args.map else [])
    lines += [f"major={m}" for m in majors] + [f"strategic={r}" for r in strategic]
    lines += [f"building={b['name']}" for b in load(mod, "Buildings.json")]
    lines += [f"gu={g}|{s}|{f}|{r}" for g, s, f, r in gus] + [f"fusion={g}" for g, _, _, r in gus if r >= 2]
    return "\n".join(lines) + "\n"


def compile_java(jar: Path, classes: Path) -> None:
    classes.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["javac", "-nowarn", "-encoding", "UTF-8", "-cp", str(jar), "-d", str(classes), str(JAVA_SRC)],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("javac failed:\n" + r.stderr)


def play(mod: Path, args, seed: int, jar: Path, classes: Path, out: Path) -> tuple[int, int, float, str]:
    with tempfile.TemporaryDirectory(prefix="autoplay-") as tmp:
        work = Path(tmp)
        shutil.copytree(mod / "jsons", work / "mods" / args.mod_name / "jsons")
        (work / "config.txt").write_text(config(mod, args, seed), encoding="utf-8")
        start = time.time()
        r = subprocess.run(["java", f"-Xmx{args.heap}", "-Dfile.encoding=UTF-8", "-cp", f"{jar}{os.pathsep}{classes}",
                            "Autoplay", str(work / "config.txt"), str(out / f"game-{seed}.jsonl")],
                           cwd=work, capture_output=True, text=True, timeout=args.timeout)
        tail = "\n".join((r.stderr or "").strip().splitlines()[-25:])
        return seed, r.returncode, time.time() - start, tail


def _mean(xs) -> float | None:
    xs = list(xs)
    return round(statistics.mean(xs), 2) if xs else None


def _share(n: int, d: int) -> float | None:
    return round(n / d, 3) if d else None


def summarize(out: Path) -> dict:
    games = {}
    for f in sorted(out.glob("game-*.jsonl")):
        rows = [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]
        end = next((r for r in rows if r["event"] in ("end", "crash")), None)
        turns = [r for r in rows if r["event"] == "turn" and r["major"]]
        civs = defaultdict(list)
        for r in turns:
            civs[r["civ"]].append(r)
        per_civ = {}
        for civ, rs in civs.items():
            last = rs[-1]
            hs = defaultdict(int)
            for r in rs:
                for key in ("hungerStart", "hungerDeath", "hungerRecover", "guHeld", "guHeldInDeficit"):
                    for rank, n in r[key].items():
                        hs[f"{key}.{rank}"] += n
            per_civ[civ] = {
                "alive": last["alive"], "cities": last["cities"], "pop": last["pop"], "techs": last["techs"],
                "policies": last["policies"], "era": last["era"], "gold": last["gold"], "gpt": last["gpt"],
                "upkeep": last["upkeep"], "minGold": min(r["gold"] for r in rs),
                "turnsGoldBelow0": sum(1 for r in rs if r["gold"] < 0),
                "maxUnits": max(sum(r["units"].values()) for r in rs), "units": sum(last["units"].values()),
                "res": last["res"], "resMean": {k: round(statistics.mean(r["res"][k] for r in rs), 2) for k in last["res"]},
                "resTurnsNegative": {k: sum(1 for r in rs if r["res"][k] < 0) for k in last["res"]},
                "guHolders": last["guHolders"], "promotionHolders": last.get("promotionHolders", {}), "hunger": dict(hs),
                "tradesMean": round(statistics.mean(r["trades"] for r in rs), 2),
                "resTradedOutMean": round(statistics.mean(r["resOut"] for r in rs), 2),
                "warTurns": sum(1 for r in rs if r["wars"]), "csAlliesLast": last["csAllies"],
                "capturedCitiesLast": last.get("capturedCities", 0),
                "pillagedTileTurns": sum(r.get("pillagedTiles", 0) for r in rs),
                "turnsPlayed": len(rs),
                "happinessMin": min(r["happiness"] for r in rs),
                "buildingsLast": last.get("buildings", {}),
                "firstTurnBuilt": {b: next(r["turn"] for r in rs if r.get("buildings", {}).get(b))
                                   for b in sorted({b for r in rs for b in r.get("buildings", {})})},
                "promotionsBoughtLast": last.get("promotionsBought"),
                "capitalPopLast": last.get("capitalPop"), "popOneCitiesLast": last.get("popOneCities"),
            }
        games[f.stem] = {"end": end, "civs": per_civ}
    # pooled hunger statistics per rank
    pooled = defaultdict(int)
    for g in games.values():
        for c in g["civs"].values():
            for k, v in c["hunger"].items():
                pooled[k] += v
    rates = {}
    for rank in sorted({k.split(".")[1] for k in pooled}):
        starts, deaths, rec = (pooled[f"hunger{x}.{rank}"] for x in ("Start", "Death", "Recover"))
        held, short = pooled[f"guHeld.{rank}"], pooled[f"guHeldInDeficit.{rank}"]
        rates[rank] = {"holderTurns": held, "holderTurnsInDeficit": short, "hungerEpisodes": starts, "deaths": deaths,
                       "recoveries": rec, "deathsPerEpisode": round(deaths / starts, 3) if starts else None,
                       "deathsPer100HolderTurns": round(100 * deaths / held, 2) if held else None}
    # the user's round-5 metrics (option B): share of rank-1 holder-turns in deficit, Gu deaths per clan per 100 turns
    civ_turns = sum(c["turnsPlayed"] for g in games.values() for c in g["civs"].values())
    deaths = sum(pooled[k] for k in pooled if k.startswith("hungerDeath."))
    r1 = rates.get("rank1", {})
    metrics = {
        "rank1ShareInDeficit": round(r1["holderTurnsInDeficit"] / r1["holderTurns"], 4) if r1.get("holderTurns") else None,
        "guHungerDeathsPerClanPer100Turns": round(100 * deaths / civ_turns, 3) if civ_turns else None,
        "clanTurns": civ_turns,
        "warShareOfClanTurns": round(sum(c["warTurns"] for g in games.values() for c in g["civs"].values()) / civ_turns, 3)
        if civ_turns else None,
        "gamesWithAWar": sum(1 for g in games.values() if any(c["warTurns"] for c in g["civs"].values())),
        "capturedCitiesAtEnd": sum(c["capturedCitiesLast"] for g in games.values() for c in g["civs"].values()),
        "pillagedTileTurns": sum(c["pillagedTileTurns"] for g in games.values() for c in g["civs"].values()),
        # the user's pop-1 report (2026-10-18): capital size and cities stuck at population 1, alive clans at the end
        "capitalPopMean": _mean(c["capitalPopLast"] for g in games.values() for c in g["civs"].values()
                                if c["alive"] and c.get("capitalPopLast") is not None),
        "popPerCityMean": _mean(c["pop"] / c["cities"] for g in games.values() for c in g["civs"].values()
                                if c["alive"] and c["cities"]),
        "popOneCityShare": _share(sum(c.get("popOneCitiesLast") or 0 for g in games.values() for c in g["civs"].values()),
                                  sum(c["cities"] for g in games.values() for c in g["civs"].values())),
        "games": len(games),
    }
    return {"games": games, "hungerByRank": rates, "metrics": metrics}


def print_summary(s: dict) -> None:
    for name, g in s["games"].items():
        end = g["end"] or {}
        print(f"\n== {name}: {end.get('result', end.get('event', '?'))} at turn {end.get('turn')} "
              f"({round(end.get('ms', 0) / 1000)} s)")
        print(f"   {'civ':<12}{'alive':>6}{'city':>5}{'pop':>5}{'tech':>5}{'pol':>4}{'gold':>6}{'gpt':>5}{'upk':>5}"
              f"{'minG':>6}{'<0':>4}{'unit':>5}{'trade':>6}{'war':>4}  resources (last / mean)")
        for civ, c in g["civs"].items():
            res = " ".join(f"{k.split()[0]}={c['res'][k]}/{c['resMean'][k]}" for k in c["res"])
            print(f"   {civ[:11]:<12}{str(c['alive'])[0]:>6}{c['cities']:>5}{c['pop']:>5}{c['techs']:>5}{c['policies']:>4}"
                  f"{c['gold']:>6}{c['gpt']:>5}{c['upkeep']:>5}{c['minGold']:>6}{c['turnsGoldBelow0']:>4}{c['units']:>5}"
                  f"{c['tradesMean']:>6}{c['warTurns']:>4}  {res}")
    print("\n== metrics:", s.get("metrics"))
    print("\n== hunger by Gu rank (all games, all civs)")
    for rank, r in s["hungerByRank"].items():
        print(f"   {rank}: {r}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mod", type=Path, default=REPO_ROOT)
    ap.add_argument("--games", type=int, default=4)
    ap.add_argument("--turns", type=int, default=100)
    ap.add_argument("--seed", type=int, default=1, help="first seed; game i uses seed+i")
    ap.add_argument("--jobs", type=int, default=max(1, min(4, (os.cpu_count() or 2) // 2)))
    ap.add_argument("--difficulty", default="Prince")
    ap.add_argument("--speed", default="Standard")
    ap.add_argument("--map", default=None, help="a map file (e.g. maps/Qing Mao Mountain) instead of a generated map")
    ap.add_argument("--map-size", default="Small", choices=["Tiny", "Small", "Medium", "Large", "Huge"])
    ap.add_argument("--city-states", type=int, default=None, help="default: every city-state nation of the mod")
    ap.add_argument("--no-strategic-balance", action="store_true")
    ap.add_argument("--majors", default=None, help="comma-separated major nations (default: all of the mod's)")
    ap.add_argument("--mod-name", default=MOD_NAME, help="folder name to stage the mod under")
    ap.add_argument("--heap", default="2g")
    ap.add_argument("--timeout", type=int, default=3600, help="seconds per game")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--summarize", type=Path, default=None, help="only summarize an existing output folder")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.summarize:
        s = summarize(args.summarize)
        print_summary(s)
        return 0
    jar = REF_DIR / f"Unciv-{ref_tag()}.jar"
    if not jar.exists() or not shutil.which("java") or not shutil.which("javac"):
        sys.exit(f"autoplay needs java, javac and {jar} (tools/fetch_ref.sh)")
    mod = args.mod.resolve()
    out = (args.out or Path(tempfile.mkdtemp(prefix="unciv-autoplay-"))).resolve()
    out.mkdir(parents=True, exist_ok=True)
    classes = out / ".classes"
    compile_java(jar, classes)
    seeds = [args.seed + i for i in range(args.games)]
    print(f"[autoplay] {args.games} game(s) x {args.turns} turns, {args.map_size}, {args.difficulty}, "
          f"strategic balance {'off' if args.no_strategic_balance else 'on'}, {args.jobs} in parallel -> {out}")
    crashed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(play, mod, args, s, jar, classes, out) for s in seeds]
        for fut in concurrent.futures.as_completed(futures):
            seed, code, secs, tail = fut.result()
            print(f"[autoplay] game {seed}: exit {code} after {secs:.0f} s")
            if code:
                crashed.append(seed)
                print(tail)
    s = summarize(out)
    (out / "summary.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    if not args.quiet:
        print_summary(s)
    print(f"[autoplay] {len(crashed)} crash(es); data in {out}")
    return 1 if crashed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
