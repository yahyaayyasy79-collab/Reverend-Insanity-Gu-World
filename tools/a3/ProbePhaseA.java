// MOD_SPEC_2 Phase A: seven risky patterns on the A3TEST mod (tools/a3/build_test_mod.py), headless, Unciv 4.22.8.
import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.GameStarter;
import com.unciv.logic.city.City;
import com.unciv.logic.civilization.Civilization;
import com.unciv.logic.civilization.PlayerType;
import com.unciv.logic.map.MapParameters;
import com.unciv.logic.map.MapSize;
import com.unciv.logic.map.mapunit.MapUnit;
import com.unciv.logic.map.tile.Tile;
import com.unciv.models.metadata.*;
import com.unciv.models.ruleset.*;
import com.unciv.models.ruleset.unique.*;
import com.unciv.models.ruleset.tile.TileResource;
import java.util.*;

public class ProbePhaseA {
    static GameInfo gi;
    static Civilization civ(String n) { for (Civilization c : gi.getCivilizations()) if (c.getCivName().equals(n)) return c; return null; }
    static void turn() { gi.setSimulateUntilWin(true); gi.setSimulateMaxTurns(gi.getTurns() + 1); gi.nextTurn(null, false); }
    static void trigger(String text, Civilization c) {
        UniqueTriggerActivation.INSTANCE.triggerUnique(new Unique(text, null, null), c, null, null, null, null, null);
    }
    static Integer count(String countable, Civilization c) { return Countables.Companion.getCountableAmount(countable, c.getState()); }
    static List<String> holders(String building) {
        List<String> out = new ArrayList<>();
        for (City city : kotlin.sequences.SequencesKt.toList(gi.getCities())) if (city.getCityConstructions().isBuilt(building)) out.add(city.getCiv().getCivName() + "/" + city.getName());
        return out;
    }
    static List<String> rejections(String building, City city) {
        List<String> out = new ArrayList<>();
        Building b = gi.getRuleset().getBuildings().get(building);
        for (RejectionReason r : kotlin.sequences.SequencesKt.toList(b.getRejectionReasons(city.getCityConstructions()))) out.add(r.getType().name());
        return out;
    }
    static int strengthPct(MapUnit u) {
        int sum = 0;
        for (Unique q : kotlin.sequences.SequencesKt.toList(u.getMatchingUniques(UniqueType.Strength, u.getCache().getState(), true)))
            sum += Integer.parseInt(q.getParams().get(0).replace("+", ""));
        return sum;
    }

    public static void main(String[] a) throws Exception {
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        GameSettings s = new GameSettings(); s.setShowTutorials(false); s.setTurnsBetweenAutosaves(100000); game.setSettings(s);
        RulesetCache.INSTANCE.loadRulesets(true, false);
        Ruleset rs = RulesetCache.INSTANCE.get("A3TEST");
        GameParameters gp = new GameParameters();
        gp.setBaseRuleset("A3TEST"); gp.setDifficulty("Prince"); gp.setSpeed("Standard"); gp.setStartingEra("Rank One-Two era");
        gp.setNumberOfCityStates(0); gp.setMaxTurns(500);
        ArrayList<Player> ps = new ArrayList<>();
        for (String m : new String[]{"Gu Yue Clan", "Bai Clan", "Xiong Clan", "Wu Clan"}) ps.add(new Player(m, PlayerType.AI, ""));
        ps.add(new Player("Spectator", PlayerType.Human, "")); gp.setPlayers(ps); ps.get(4).setNationTransient(rs);
        MapParameters mp = new MapParameters(); mp.setMapSize(new MapSize(MapSize.Predefined.Small)); mp.setSeed(9);
        gi = GameStarter.Companion.startNewGame(new GameSetupInfo(gp, mp));
        game.setGameInfo(gi);
        turn(); turn();
        Civilization wu = civ("Wu Clan"), bai = civ("Bai Clan"), gy = civ("Gu Yue Clan");
        City wuCap = wu.getCapital(false), gyCap = gy.getCapital(false);

        // ---- A3 Unbuildable + free grant: Bai's nation unique at its first city, guarded ----
        System.out.println("A3 Test Fate Gu holders after turn 2: " + holders("Test Fate Gu"));
        System.out.println("A3 rejections for Wu building Test Fate Gu: " + rejections("Test Fate Gu", wuCap));

        // ---- A1 for-every Strength ----
        MapUnit dao = wu.getUnits().placeUnitNearTile(wuCap.getCenterTile().getPosition(), "Test Dao Unit");
        System.out.println("A1 strength % with 0 marks: " + strengthPct(dao));
        wuCap.getCityConstructions().addBuilding("Test Strength Gu A");
        System.out.println("A1 strength % with 1 Strength mark: " + strengthPct(dao) + "  count=" + count("[Strength Path] Buildings", wu));
        wuCap.getCityConstructions().addBuilding("Test Strength Gu B");
        System.out.println("A1 strength % with 2 Strength marks: " + strengthPct(dao));
        wuCap.getCityConstructions().addBuilding("Test Wisdom Gu A");
        System.out.println("A1 strength % with 2 Strength + 1 Wisdom: " + strengthPct(dao));

        // ---- A6 max() countable ----
        String expr = "max([[Strength Path] Buildings], [[Wisdom Path] Buildings])";
        System.out.println("A6 " + expr + " for Wu = " + count(expr, wu) + " (Strength 2, Wisdom 1); for Gu Yue = " + count(expr, gy));
        System.out.println("A6 Test Venerable Ascension rejections: Wu " + rejections("Test Venerable Ascension", wuCap) + " | Gu Yue " + rejections("Test Venerable Ascension", gyCap));

        // ---- A2 Remove on a wonder reopens the race; Never destroyed on capture (built wonder) ----
        wuCap.getCityConstructions().addBuilding("Test Immortal Gu");
        System.out.println("A2 Test Immortal Gu holders: " + holders("Test Immortal Gu") + "; Gu Yue rejections: " + rejections("Test Immortal Gu", gyCap));
        System.out.println("A6 after Test Immortal Gu (also Strength Path): max = " + count(expr, wu));
        trigger("Remove [Test Immortal Gu] [in all cities]", wu);
        System.out.println("A2 after Remove: holders " + holders("Test Immortal Gu") + "; Gu Yue rejections: " + rejections("Test Immortal Gu", gyCap));

        // ---- A4 owned-tile trigger + A5 lifespan consumption ----
        TileResource life = gi.getRuleset().getTileResources().get("Test Lifespan Gu");
        wu.gainStockpiledResource(life, 5);
        MapUnit im1 = wu.getUnits().placeUnitNearTile(wuCap.getCenterTile().getPosition(), "Test Immortal");
        MapUnit im2 = wu.getUnits().placeUnitNearTile(wuCap.getCenterTile().getPosition(), "Test Immortal");
        int id1 = im1.getId(), id2 = im2.getId();
        for (int i = 0; i < 12; i++) {
            turn();
            StringBuilder trials = new StringBuilder();
            for (Civilization c : new Civilization[]{gy, bai, civ("Xiong Clan"), wu})
                trials.append(c.getCivName().split(" ")[0]).append(" land=").append(count("Owned [Land] Tiles", c)).append(" trials=").append(c.getResourceAmount("Test Trial Counter")).append("; ");
            String hp = "";
            for (MapUnit u : kotlin.sequences.SequencesKt.toList(wu.getUnits().getCivUnits())) if (u.getId() == id1 || u.getId() == id2) hp += u.getHealth() + " ";
            System.out.println("A4/A5 T" + gi.getTurns() + ": Wu lifespan=" + wu.getResourceAmount("Test Lifespan Gu") + " immortal HP=[" + hp.trim() + "] | " + trials);
        }
        gyCap.getCityConstructions().addBuilding("Test Inheritance Wonder");
        int before = 0; for (Civilization c : new Civilization[]{gy, bai, civ("Xiong Clan"), wu}) before += c.getResourceAmount("Test Trial Counter");
        for (int i = 0; i < 6; i++) turn();
        int after = 0; for (Civilization c : new Civilization[]{gy, bai, civ("Xiong Clan"), wu}) after += c.getResourceAmount("Test Trial Counter");
        System.out.println("A4 trials in the 6 turns after someone built Test Inheritance Wonder: " + (after - before));

        // ---- A7 camp gate ----
        Tile spot = null;
        for (Tile t : gi.getTileMap().getTileList()) if (t.isLand() && !t.isImpassible() && t.getOwner() == null && t.getImprovement() == null && !t.getUnits().iterator().hasNext()) { spot = t; break; }
        for (int phase = 0; phase < 2; phase++) {
            Map<String, Integer> camps = new TreeMap<>();
            for (int i = 0; i < 200; i++) {
                gi.getBarbarians().createNewCamp(spot, kotlin.random.RandomKt.Random(i * 7919 + phase));
                camps.merge(String.valueOf(spot.getImprovement()), 1, Integer::sum);
                spot.removeImprovement();
            }
            System.out.println("A7 " + (phase == 0 ? "Fate Gu exists " + holders("Test Fate Gu") : "after Remove, Fate Gu holders " + holders("Test Fate Gu")) + ": camps " + camps);
            if (phase == 0) trigger("Remove [Test Fate Gu] [in all cities]", bai);
        }

        // ---- A3 continued: free grant ignores world-wonder uniqueness? capture of free vs built wonders ----
        trigger("Gain a free [Test Fate Gu] [in capital]", bai);
        trigger("Gain a free [Test Fate Gu] [in capital]", wu);
        System.out.println("A3 two civs granted the same free world wonder: holders " + holders("Test Fate Gu"));
        // need a civ with a non-capital city
        Civilization owner = null; City second = null;
        for (int t = 0; t < 80 && second == null; t++) {
            turn();
            for (Civilization c : gi.getCivilizations()) {
                if (!c.isMajorCiv() || !c.isAlive()) continue;
                for (City city : c.getCities()) if (!city.isCapital()) { owner = c; second = city; break; }
                if (second != null) break;
            }
        }
        if (second == null) { System.out.println("A3 capture: no non-capital city by turn " + gi.getTurns()); return; }
        Civilization taker = owner == wu ? gy : wu;
        second.getCityConstructions().addBuilding("Test Immortal Gu");
        trigger("Gain a free [Test Inheritance Wonder] [in all cities]", owner);
        System.out.println("A3 " + owner.getCivName() + " T" + gi.getTurns() + " before capture: " + second.getName() + " Test Immortal Gu(built)=" + second.getCityConstructions().isBuilt("Test Immortal Gu")
            + " Test Inheritance Wonder(free)=" + second.getCityConstructions().isBuilt("Test Inheritance Wonder") + "; free wonder holders " + holders("Test Inheritance Wonder"));
        second.moveToCiv(taker);
        System.out.println("A3 after " + taker.getCivName() + " takes " + second.getName() + ": Test Immortal Gu(built)=" + second.getCityConstructions().isBuilt("Test Immortal Gu")
            + " Test Inheritance Wonder(free)=" + second.getCityConstructions().isBuilt("Test Inheritance Wonder") + "; free wonder holders " + holders("Test Inheritance Wonder"));
    }
}
