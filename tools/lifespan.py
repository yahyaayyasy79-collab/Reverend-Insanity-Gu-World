"""Immortal lifespan (MOD_SPEC_2 C2; the user, 2026-11-02: "kalo udah ascend ke abadi umurnya bertambah bukan malah
berkurang ... kasih tutor bagaimana cara menambah umur gu abadi rank 6, 7, 8 dan 9").

A clan's Lifespan Gu stock is its immortals' lifespan. Reaching each rank ADDS to it (ascension, each advancement,
the Venerable), and a higher rank burns it more slowly, so climbing lengthens an immortal's life. Without Lifespan
Gu an immortal wastes away (STARVE_DAMAGE a turn) and heals only by pillaging. tools/gen_ruleset.py builds the
uniques from these numbers and tools/gen_paths.py writes the Tutorial page from the same numbers.
Until 2026-11-02 the ascension gave 5 and every rank burned one each 10 turns: about 50 turns of life.
"""
from __future__ import annotations

LIFESPAN = "Lifespan Gu"
RANK_NAME = {6: ("Rank six", "Tingkat enam"), 7: ("Rank seven", "Tingkat tujuh"), 8: ("Rank eight", "Tingkat delapan"),
             9: ("The Venerable", "Yang Mulia")}
GRANT = {6: 20, 7: 25, 8: 35, 9: 60}  # Lifespan Gu gained on reaching the rank
BURN = {6: 10, 7: 15, 8: 20, 9: 30}   # one Lifespan Gu every N turns on Standard, per immortal of that rank
STARVE_DAMAGE = 7
# heaven and earth's own Lifespan Gu: owned forest, jungle and marsh (R V3/194), from Calamity Lore
WILD_TERRAIN = ("Forest", "Jungle", "Marsh")
WILD_TERRAIN_ID = ("hutan", "rimba", "rawa")
WILD_TILES, WILD_CHANCE = 8, 15       # 1 per WILD_TILES owned tiles of each kind, WILD_CHANCE% a turn on Standard
MARKET_PRICE, MARKET_GU = 120, 3      # Treasure Yellow Heaven: stones for Lifespan Gu
DREAD_TURNS = 10                      # while a Venerable lives, every clan loses one each DREAD_TURNS turns


def lasts(rank: int) -> int:
    """Turns the rank's own grant keeps one immortal of that rank alive (Standard)."""
    return GRANT[rank] * BURN[rank]
