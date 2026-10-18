# Test mod: capability tests (throwaway)

This branch is NOT the mod. It is the shipped ruleset plus test objects for MOD_SPEC_3 Phase A3 and MOD_SPEC_2 Phase A
(`tools/a3/build_test_mod.py`, results in `docs/CAPABILITIES.md` on the main branch). Download it as
`https://github.com/yahyaayyasy79-collab/Reverend-Insanity-Gu-World/tree/test/capability-tests`: the slash keeps it
a separate mod ("Reverend Insanity Gu World test capability tests"), so it never replaces the real one. Start a new
game with it as the base ruleset; never load a real save into it.

## MOD_SPEC_3 B3: all 47 path lines (promotion-screen check)

The jsons now also carry the B3 prototype (`tools/b3/gen_proto.py` on the main branch): every path's four tiers, its
two move statuses, the conflict lines and the AI main-path lock, on Slice 1's unit types. Icons are missing (blank).
What to look at on Android: start a game, select a Gu Master, open the console and run `unit setxp 200`, then open
its promotions. Every path's Master is offered at once (42 roots; the 5 sub-paths open after their parent). Is the
screen still usable: can you scroll it, find a path, read a promotion? A Rank Three or Four Gu Master is also
offered Grandmaster (`unit add <civ> "Rank Three Moon Gu Master"`).
