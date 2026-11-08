"""Reference audit Layer 1 (docs/REFERENCE_AUDIT.md, 2026-11-08): the numbers of the small stages, the rank relics and
the extreme physiques, shared by tools/gen_ruleset.py (the uniques) and tools/gen_paths.py (the Tutorial page)."""
from __future__ import annotations

STAGES = ["Middle Stage", "Upper Stage", "Peak Stage"]    # initial is the bare rank
CULTIVATING = "Stage Cultivation"
STAGE_BONUS = 5                                            # % Strength per stage
PHYSIQUE, DOOMED = "Extreme Physique", "Doomed Aperture"
STAGE_TURNS = {PHYSIQUE: 5, "Aptitude A": 8, "Aptitude B": 10, "Aptitude C": 12, "Aptitude D": 16}  # Standard speed
IMMORTAL_STAGE_FACTOR = 2
PEAK_DISCOUNT, EARLY_PREMIUM = 30, 50                      # % gold cost of a rank upgrade, at / before the peak
PHYSIQUE_CHANCE = 1                                        # % of awakenings
PHYSIQUE_DOOM = 60                                         # turns, Standard speed
# (colour, unit filter of its rank, primeval stones)
RELICS = [("Green Copper", "<for [Rank One Gu Master] units>", 25),
          ("Red Iron", "<for [{Rank One-Two era} {non-[Rank One Gu Master]}] units>", 40),
          ("White Silver", "<for [Rank Three era] units>", 60),
          ("Yellow Gold", "<for [Rank Four era] units>", 90),
          ("Purple Crystal", "<for [Rank Five era] units>", 130)]
RELIC_ID = {"Green Copper": "Tembaga Hijau", "Red Iron": "Besi Merah", "White Silver": "Perak Putih",
            "Yellow Gold": "Emas Kuning", "Purple Crystal": "Kristal Ungu"}
