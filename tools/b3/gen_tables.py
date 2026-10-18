#!/usr/bin/env python3
"""Markdown tables for docs/PATHS.md from paths_data.py (B3 draft): tools/b3/gen_tables.py > tables.md.
Asserts that no two paths share a signature."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paths_data import (P, FAMILIES, MOVE_TEMPLATE_TEXT, CLASH, CLASH_PAIR, LOW, LOW_PAIR, NEUTRAL, COMPATIBLE,
                        DEFAULT_PAIR, OWNERS)

key = {p[0]: p for p in P}
c = lambda s: "`" + s.replace("|", "\\|") + "`"
sigs = [p[7] for p in P]
assert len(set(sigs)) == len(sigs), "two paths share a signature"
assert len(P) == 46

out = []
out.append("| # | Path | Chinese | Family | Sub-path of | Source | Verdict | Signature (one unique) | Lore hook |")
out.append("|---|---|---|---|---|---|---|---|---|")
for i, (k, en, zh, fam, parent, src, verdict, sig, why, m, im) in enumerate(P, 1):
    out.append(f"| {i} | {en} | {zh} | {fam} | {key[parent][1] if parent else ''} | {src} | {verdict} | {c(sig)} | {why} |")
out.append("")
out.append("MOVES")
out.append("| Path | Family template | Mortal move (Grandmaster) | Tag | Immortal move (Great Grandmaster) | Tag |")
out.append("|---|---|---|---|---|---|")
for (k, en, zh, fam, parent, src, verdict, sig, why, m, im) in P:
    mn = m[0] + (f" {m[1]}" if m[1] else "")
    imn = im[0] + (f" {im[1]}" if im[1] else "")
    out.append(f"| {en} | {fam} | {mn} | {m[2]} | {imn} | {im[2]} |")
out.append("")
out.append("FAMILIES")
out.append("| Family | Paths | Play feel | Mortal move template | Immortal move template | Icon colour |")
out.append("|---|---|---|---|---|---|")
for f, (fname, feel, rgb) in FAMILIES.items():
    members = ", ".join(p[1] for p in P if p[3] == f)
    mt, it = MOVE_TEMPLATE_TEXT[f]
    out.append(f"| {f}. {fname} | {members} | {feel} | {mt} | {it} | {list(rgb)} |")
out.append("")
print("\n".join(out))
