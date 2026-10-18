// MOD_SPEC_3 Phase A3: five capability tests on the A3TEST mod (tools/a3/build_test_mod.py), headless, Unciv 4.22.8.
import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.GameStarter;
import com.unciv.logic.city.City;
import com.unciv.logic.civilization.Civilization;
import com.unciv.logic.civilization.PlayerType;
import com.unciv.logic.map.MapParameters;
import com.unciv.logic.map.MapSize;
import com.unciv.logic.map.mapunit.MapUnit;
import com.unciv.logic.map.mapunit.UnitTurnManager;
import com.unciv.models.metadata.*;
import com.unciv.models.ruleset.Ruleset;
import com.unciv.models.ruleset.RulesetCache;
import com.unciv.models.ruleset.unique.UniqueType;
import com.unciv.models.ruleset.unit.BaseUnit;
import com.unciv.models.ruleset.unit.Promotion;
import java.util.*;

public class ProbeA3 {
    static GameInfo gi;
    static BaseUnit bu(String n) { return gi.getRuleset().getUnits().get(n); }
    static MapUnit place(Civilization c, String name) {
        City cap = c.getCapital(false);
        return c.getUnits().placeUnitNearTile(cap.getCenterTile().getPosition(), name);
    }
    static MapUnit byId(Civilization c, int id) {
        for (MapUnit u : kotlin.sequences.SequencesKt.toList(c.getUnits().getCivUnits())) if (u.getId() == id) return u;
        return null;
    }
    static List<String> available(MapUnit u) {
        List<String> out = new ArrayList<>();
        for (Promotion p : kotlin.sequences.SequencesKt.toList(u.getPromotions().getAvailablePromotions())) out.add(p.getName());
        return out;
    }
    static Civilization civ(String n) {
        for (Civilization c : gi.getCivilizations()) if (c.getCivName().equals(n)) return c;
        return null;
    }

    public static void main(String[] a) throws Exception {
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        GameSettings s = new GameSettings(); s.setShowTutorials(false); s.setTurnsBetweenAutosaves(100000); game.setSettings(s);
        RulesetCache.INSTANCE.loadRulesets(true, false);
        Ruleset rs = RulesetCache.INSTANCE.get("A3TEST");
        GameParameters gp = new GameParameters();
        gp.setBaseRuleset("A3TEST"); gp.setDifficulty("Prince"); gp.setSpeed("Standard"); gp.setStartingEra("Rank One-Two era");
        gp.setNumberOfCityStates(0); gp.setMaxTurns(500); gp.setNoBarbarians(true);
        ArrayList<Player> ps = new ArrayList<>();
        for (String m : new String[]{"Gu Yue Clan", "Bai Clan", "Xiong Clan", "Wu Clan"}) ps.add(new Player(m, PlayerType.AI, ""));
        ps.add(new Player("Spectator", PlayerType.Human, "")); gp.setPlayers(ps); ps.get(4).setNationTransient(rs);
        MapParameters mp = new MapParameters(); mp.setMapSize(new MapSize(MapSize.Predefined.Small)); mp.setSeed(5);
        gi = GameStarter.Companion.startNewGame(new GameSetupInfo(gp, mp));
        game.setGameInfo(gi);
        while (gi.getTurns() < 3) { gi.setSimulateUntilWin(true); gi.setSimulateMaxTurns(gi.getTurns() + 1); gi.nextTurn(null, false); }
        Civilization wu = civ("Wu Clan"), bai = civ("Bai Clan");
        City cap = wu.getCapital(false);

        // ---------- TEST 1: promotions across a unit-type change on upgrade ----------
        MapUnit r5 = place(wu, "Test Rank Five");
        r5.getPromotions().addPromotion("Test Path Old Type", true);
        r5.getPromotions().addPromotion("Test Path All", true);
        r5.getPromotions().setXP(57);
        int id5 = r5.getId();
        System.out.println("T1 before: " + r5.getName() + " type=" + r5.getType().getName() + " promotions=" + r5.getPromotions().getPromotions()
            + " sightUnique=" + r5.hasUnique(UniqueType.Sight, r5.getCache().getState(), true) + " movement=" + r5.getMaxMovement(false) + " xp=" + r5.getPromotions().getXP());
        r5.getUpgrade().performUpgrade(bu("Test Rank Six"), true, 0);
        MapUnit r6 = byId(wu, id5);
        System.out.println("T1 after:  " + (r6 == null ? "null" : r6.getName() + " type=" + r6.getType().getName() + " promotions=" + r6.getPromotions().getPromotions()
            + " sightUnique=" + r6.hasUnique(UniqueType.Sight, r6.getCache().getState(), true) + " movement=" + r6.getMaxMovement(false) + " xp=" + r6.getPromotions().getXP()));

        // ---------- TEST 2: Only available <for [mapUnitFilter] units> on a promotion ----------
        MapUnit gm = place(wu, "Test Rank Five");
        gm.getPromotions().addPromotion("Test Path All", true);
        gm.getPromotions().setXP(500);
        System.out.println("T2 Gu Master (has Test Path All): offers Test Tier Immortal=" + available(gm).contains("Test Tier Immortal"));
        System.out.println("T2 Gu Immortal (has Test Path All): offers Test Tier Immortal=" + available(r6).contains("Test Tier Immortal"));
        MapUnit bare6 = place(wu, "Test Rank Six");
        System.out.println("T2 Gu Immortal without the prerequisite: offers Test Tier Immortal=" + available(bare6).contains("Test Tier Immortal"));
        // after upgrade the old-type promotion stays; can the new type still be OFFERED promotions limited to the old type?
        System.out.println("T2 Gu Immortal offered Test Path Old Type=" + available(bare6).contains("Test Path Old Type"));

        // ---------- TEST 3: Limited to [1] per Civilization blocks upgrades ----------
        BaseUnit ven = bu("Test Venerable");
        MapUnit sixA = r6, sixB = bare6;
        System.out.println("T3 before any Venerable: A canUpgrade=" + sixA.getUpgrade().canUpgrade(ven, false, false)
            + " B canUpgrade=" + sixB.getUpgrade().canUpgrade(ven, false, false));
        int goldBefore = wu.getGold();
        int idA = sixA.getId();
        sixA.getUpgrade().performUpgrade(ven, true, 0);
        MapUnit v = byId(wu, idA);
        System.out.println("T3 upgraded A: " + (v == null ? "null" : v.getName() + " promotions=" + v.getPromotions().getPromotions()));
        System.out.println("T4 side effect: gold delta at the upgrade (7 = 'upon losing a [Test Rank Six] unit' fired) = " + (wu.getGold() - goldBefore));
        System.out.println("T3 with one Venerable alive: B canUpgrade=" + sixB.getUpgrade().canUpgrade(ven, false, false));
        for (com.unciv.models.ruleset.RejectionReason r : kotlin.sequences.SequencesKt.toList(ven.getRejectionReasons(wu, null, com.unciv.models.Counter.Companion.getZERO()))) System.out.println("T3 rejection for B: " + r.getType() + " construction=" + r.isConstructionRejection());

        // ---------- TEST 4: <upon losing a [mapUnitFilter] unit> on death by its own turn damage ----------
        cap.getCityConstructions().addBuilding("Test Ascension");
        System.out.println("T4 setup: capital has Test Ascension=" + cap.getCityConstructions().containsBuildingOrEquivalent("Test Ascension"));
        int turns = 0;
        while (v != null && !v.isDestroyed() && turns < 10) {
            int g0 = wu.getGold();
            new UnitTurnManager(v).startTurn();
            turns++;
            System.out.println("T4 turn start " + turns + ": health=" + v.getHealth() + " destroyed=" + v.isDestroyed() + " gold delta=" + (wu.getGold() - g0));
        }
        System.out.println("T4 after death: Test Ascension=" + cap.getCityConstructions().containsBuildingOrEquivalent("Test Ascension")
            + " Test True Inheritance=" + cap.getCityConstructions().containsBuildingOrEquivalent("Test True Inheritance"));
        System.out.println("T3 after the Venerable died: B canUpgrade=" + sixB.getUpgrade().canUpgrade(ven, false, false));

        // ---------- TEST 5: per-civ AI promotion weights ----------
        for (Civilization c : new Civilization[]{wu, bai}) {
            MapUnit u = place(c, "Test Rank Five");
            u.getPromotions().setXP(10);
            Map<String, Float> w = new TreeMap<>();
            float total = 0;
            for (Promotion p : kotlin.sequences.SequencesKt.toList(u.getPromotions().getAvailablePromotions())) {
                float x = p.getWeightForAiDecision(u.getCache().getState());
                w.put(p.getName(), x); total += x;
            }
            StringBuilder sb = new StringBuilder();
            for (Map.Entry<String, Float> e : w.entrySet()) sb.append(e.getKey()).append("=").append(String.format("%.2f (%.0f%%) ", e.getValue(), 100 * e.getValue() / total));
            System.out.println("T5 " + c.getCivName() + " weights: " + sb);
        }
        // empirical: the AI's own promotion routine on units spread over distinct tiles (its RNG is seeded by state)
        List<com.unciv.logic.map.tile.Tile> land = new ArrayList<>();
        for (com.unciv.logic.map.tile.Tile t : gi.getTileMap().getTileList())
            if (t.isLand() && !t.isImpassible() && !t.getUnits().iterator().hasNext() && !t.isCityCenter()) land.add(t);
        for (Civilization c : new Civilization[]{wu, bai}) {
            Map<String, Integer> picks = new TreeMap<>();
            int n = 0;
            for (int i = 0; i < land.size() && n < 200; i += 2) {
                MapUnit u = c.getUnits().placeUnitNearTile(land.get(i).getPosition(), "Test Rank Five");
                if (u == null) continue;
                u.getPromotions().setXP(10);
                com.unciv.logic.automation.civilization.NextTurnAutomation.INSTANCE.applyPromotions$Unciv_core(u);
                for (String p : u.getPromotions().getPromotions()) picks.merge(p, 1, Integer::sum);
                u.destroy(true);
                n++;
            }
            System.out.println("T5 empirical " + c.getCivName() + " (" + n + " units, one promotion each): " + picks);
        }
    }
}
