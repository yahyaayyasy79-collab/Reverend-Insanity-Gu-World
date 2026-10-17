// Headless AI-vs-AI game on a mod ruleset, for balance data (MOD_SPEC section 10). Run through tools/autoplay.py,
// which compiles this file against the Unciv release jar and stages the mod under <workdir>/mods/<name>.
//
// Engine entry points, as used by the engine's own simulation [src desktop/.../ConsoleLauncher.kt,
// core/.../logic/simulation/Simulation.kt]: UncivGame(consoleMode) + RulesetCache.loadRulesets(consoleMode, noMods)
// read <cwd>/mods; GameStarter.startNewGame; then GameInfo.nextTurn with simulateUntilWin/simulateMaxTurns, which
// plays every AI civ (TurnManager.startTurn + automateTurn) and stops once the turn counter reaches the target.
// One snapshot per round: between two snapshots every civ has started and played exactly one turn.
//
// Usage: java -cp <jar>:<classes> Autoplay CONFIG OUT_JSONL
//   CONFIG: key=value lines (mod, turns, seed, difficulty, mapSize, cityStates, speed, startingEra, major=<nation>
//   per major, strategic=<resource> per strategic resource, gu=<Gu>|<hungerStatus>|<food>|<rank> per Gu,
//   fusion=<promotion> per fusion product).
import com.unciv.UncivGame;
import com.unciv.logic.GameInfo;
import com.unciv.logic.GameStarter;
import com.unciv.logic.civilization.Civilization;
import com.unciv.logic.civilization.PlayerType;
import com.unciv.logic.civilization.diplomacy.DiplomacyManager;
import com.unciv.logic.city.City;
import com.unciv.logic.map.MapParameters;
import com.unciv.logic.map.MapSize;
import com.unciv.logic.map.mapunit.MapUnit;
import com.unciv.logic.trade.Trade;
import com.unciv.logic.trade.TradeOffer;
import com.unciv.models.metadata.GameParameters;
import com.unciv.models.metadata.GameSettings;
import com.unciv.models.metadata.GameSetupInfo;
import com.unciv.models.metadata.Player;
import com.unciv.models.ruleset.Ruleset;
import com.unciv.models.ruleset.RulesetCache;
import com.unciv.models.stats.Stats;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class Autoplay {
    static final class Gu {
        final String name, status, food; final int rank;
        Gu(String n, String s, String f, int r) { name = n; status = s; food = f; rank = r; }
    }
    static final class UnitState {
        final String civ; final Set<String> promos; final Set<String> statuses;
        UnitState(String c, Set<String> p, Set<String> s) { civ = c; promos = p; statuses = s; }
    }

    static String q(String s) {
        StringBuilder b = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            if (c == '"' || c == '\\') b.append('\\').append(c);
            else if (c < 0x20) b.append(String.format("\\u%04x", (int) c));
            else b.append(c);
        }
        return b.append('"').toString();
    }
    static String obj(Map<String, ?> m) {
        StringBuilder b = new StringBuilder("{");
        boolean first = true;
        for (Map.Entry<String, ?> e : m.entrySet()) {
            if (!first) b.append(',');
            first = false;
            b.append(q(e.getKey())).append(':');
            Object v = e.getValue();
            if (v instanceof String) b.append(q((String) v));
            else if (v instanceof Map) b.append(obj((Map<String, ?>) v));
            else if (v instanceof Collection) {
                b.append('[');
                boolean f2 = true;
                for (Object x : (Collection<?>) v) { if (!f2) b.append(','); f2 = false; b.append(q(String.valueOf(x))); }
                b.append(']');
            } else b.append(v);
        }
        return b.append('}').toString();
    }
    static void inc(Map<String, Integer> m, String k, int by) { m.merge(k, by, Integer::sum); }

    public static void main(String[] args) throws Exception {
        Map<String, String> cfg = new LinkedHashMap<>();
        List<String> majors = new ArrayList<>(), strategic = new ArrayList<>(), buildings = new ArrayList<>();
        Set<String> fusions = new HashSet<>();
        List<Gu> gus = new ArrayList<>();
        for (String line : Files.readAllLines(Paths.get(args[0]), StandardCharsets.UTF_8)) {
            int i = line.indexOf('=');
            if (line.isBlank() || i < 0) continue;
            String k = line.substring(0, i), v = line.substring(i + 1);
            switch (k) {
                case "major": majors.add(v); break;
                case "strategic": strategic.add(v); break;
                case "fusion": fusions.add(v); break;
                case "building": buildings.add(v); break;
                case "gu": { String[] p = v.split("\\|"); gus.add(new Gu(p[0], p[1], p[2], Integer.parseInt(p[3]))); break; }
                default: cfg.put(k, v);
            }
        }
        String modName = cfg.get("mod");
        int turns = Integer.parseInt(cfg.get("turns"));
        long seed = Long.parseLong(cfg.get("seed"));
        PrintWriter out = new PrintWriter(new OutputStreamWriter(new FileOutputStream(args[1]), StandardCharsets.UTF_8), true);

        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        GameSettings settings = new GameSettings();
        settings.setShowTutorials(false);
        settings.setTurnsBetweenAutosaves(100000);
        game.setSettings(settings);
        RulesetCache.INSTANCE.loadRulesets(true, false);
        Ruleset ruleset = RulesetCache.INSTANCE.get(modName);
        if (ruleset == null) throw new IllegalStateException("mod not loaded: " + modName + " (have " + RulesetCache.INSTANCE.keySet() + ")");

        GameParameters gp = new GameParameters();
        gp.setBaseRuleset(modName);
        gp.setDifficulty(cfg.get("difficulty"));
        gp.setSpeed(cfg.get("speed"));
        gp.setStartingEra(cfg.get("startingEra"));
        gp.setNumberOfCityStates(Integer.parseInt(cfg.get("cityStates")));
        gp.setNoBarbarians(false);
        gp.setMaxTurns(turns + 50);
        ArrayList<Player> players = new ArrayList<>();
        for (String m : majors) players.add(new Player(m, PlayerType.AI, ""));
        players.add(new Player("Spectator", PlayerType.Human, ""));
        gp.setPlayers(players);
        players.get(players.size() - 1).setNationTransient(ruleset);
        MapParameters mp = new MapParameters();
        mp.setMapSize(new MapSize(MapSize.Predefined.valueOf(cfg.get("mapSize"))));
        mp.setStrategicBalance(Boolean.parseBoolean(cfg.getOrDefault("strategicBalance", "true")));
        mp.setSeed(seed);

        long t0 = System.currentTimeMillis();
        GameInfo gi = GameStarter.Companion.startNewGame(new GameSetupInfo(gp, mp));
        gi.getGameParameters().setVictoryTypes(new ArrayList<>(gi.getRuleset().getVictories().keySet()));
        game.setGameInfo(gi);
        out.println(obj(new LinkedHashMap<String, Object>() {{
            put("event", "start"); put("seed", seed); put("civs", civNames(gi));
            put("setupMs", System.currentTimeMillis() - t0);
        }}));

        Map<Integer, UnitState> prev = new HashMap<>();
        String result = "max turns";
        int lastTurn = gi.getTurns();
        while (gi.getTurns() < turns) {
            int target = gi.getTurns() + 1;
            try {
                gi.setSimulateUntilWin(true);
                gi.setSimulateMaxTurns(target);
                gi.nextTurn(null, false);
            } catch (Throwable e) {
                StringWriter sw = new StringWriter();
                e.printStackTrace(new PrintWriter(sw));
                out.println(obj(new LinkedHashMap<String, Object>() {{
                    put("event", "crash"); put("turn", target); put("trace", sw.toString());
                }}));
                System.err.println("CRASH on turn " + target + ":\n" + sw);
                System.exit(2);
            }
            lastTurn = gi.getTurns();
            prev = snapshot(gi, out, prev, gus, strategic, fusions, buildings);
            Civilization winner = null;
            for (Civilization c : gi.getCivilizations()) if (c.getVictoryManager().hasWon()) winner = c;
            if (winner != null) { result = "won by " + winner.getCivName(); break; }
            if (gi.getAliveMajorCivs().isEmpty()) { result = "no major civ left"; break; }
        }
        final String res = result; final int lt = lastTurn;
        out.println(obj(new LinkedHashMap<String, Object>() {{
            put("event", "end"); put("result", res); put("turn", lt); put("ms", System.currentTimeMillis() - t0);
        }}));
        out.close();
        System.exit(0);
    }

    static List<String> civNames(GameInfo gi) {
        List<String> l = new ArrayList<>();
        for (Civilization c : gi.getCivilizations()) l.add(c.getCivName());
        return l;
    }

    static Map<Integer, UnitState> snapshot(GameInfo gi, PrintWriter out, Map<Integer, UnitState> prev, List<Gu> gus,
                                            List<String> strategic, Set<String> fusions, List<String> buildings) {
        Map<Integer, UnitState> now = new HashMap<>();
        int barbUnits = 0;
        // strategic deposits per owner: [owned tiles, improved and not pillaged], plus unowned ones on the map
        Map<String, Map<String, int[]>> deposits = new HashMap<>();
        Map<String, Integer> pillaged = new HashMap<>();
        for (com.unciv.logic.map.tile.Tile t : gi.getTileMap().getTileList()) {
            if (t.getOwner() != null && t.getImprovement() != null && t.getImprovementIsPillaged())
                inc(pillaged, t.getOwner().getCivName(), 1);
            String r = t.getResource();
            if (r == null || !strategic.contains(r)) continue;
            Civilization owner = t.getOwner();
            int[] a = deposits.computeIfAbsent(owner == null ? "" : owner.getCivName(), k -> new HashMap<>())
                    .computeIfAbsent(r, k -> new int[2]);
            a[0]++;
            if (t.getImprovement() != null && !t.isPillaged()) a[1]++;
        }
        Map<String, Object> unowned = new LinkedHashMap<>();
        for (Map.Entry<String, int[]> e : deposits.getOrDefault("", Map.of()).entrySet()) unowned.put(e.getKey(), e.getValue()[0]);
        for (Civilization c : gi.getCivilizations()) {
            if (c.isBarbarian()) { barbUnits = c.getUnits().getCivUnitsSize(); continue; }
            if (c.isSpectator()) continue;
            boolean major = c.isMajorCiv();
            Map<String, Object> rec = new LinkedHashMap<>();
            rec.put("event", "turn"); rec.put("turn", gi.getTurns()); rec.put("civ", c.getCivName());
            rec.put("major", major); rec.put("alive", c.isAlive());
            int pop = 0;
            int captured = 0;
            for (City city : c.getCities()) {
                pop += city.getPopulation().getPopulation();
                if (city.getFoundingCivObject() != null && city.getFoundingCivObject() != c) captured++;
            }
            rec.put("cities", c.getCities().size()); rec.put("pop", pop); rec.put("capturedCities", captured);
            rec.put("pillagedTiles", pillaged.getOrDefault(c.getCivName(), 0));
            if (!major) { out.println(obj(rec)); continue; }
            Stats next = c.getStats().getStatsForNextTurn();
            rec.put("gold", c.getGold()); rec.put("gpt", Math.round(next.getGold()));
            Stats upkeep = c.getStats().getStatMapForNextTurn().get("Unit upkeep");
            rec.put("upkeep", upkeep == null ? 0 : Math.round(-upkeep.getGold()));
            rec.put("science", Math.round(next.getScience()));
            rec.put("happiness", c.getHappiness());
            rec.put("techs", c.getTech().getTechsResearched().size());
            rec.put("policies", c.getPolicies().getAdoptedPolicies().size());
            rec.put("era", c.getEra().getName());
            Map<String, Integer> res = new LinkedHashMap<>();
            for (String r : strategic) res.put(r, c.getResourceAmount(r));
            rec.put("res", res);
            Map<String, Object> dep = new LinkedHashMap<>();
            for (Map.Entry<String, int[]> e : deposits.getOrDefault(c.getCivName(), Map.of()).entrySet())
                dep.put(e.getKey(), e.getValue()[0] + "/" + e.getValue()[1]);
            rec.put("deposits", dep);
            Map<String, Integer> built = new TreeMap<>();
            for (City city : c.getCities())
                for (String b : buildings) if (city.getCityConstructions().isBuilt(b)) inc(built, b, 1);
            rec.put("buildings", built);
            int bought = 0, xp = 0;

            Map<String, Integer> types = new TreeMap<>(), holders = new TreeMap<>(), hungry = new TreeMap<>();
            Map<String, Integer> start = new TreeMap<>(), death = new TreeMap<>(), recover = new TreeMap<>(),
                    held = new TreeMap<>(), heldShort = new TreeMap<>(), otherLoss = new TreeMap<>(),
                    allPromotions = new TreeMap<>();
            Iterator<MapUnit> it = c.getUnits().getCivUnits().iterator();
            while (it.hasNext()) {
                MapUnit u = it.next();
                inc(types, u.getName(), 1);
                bought += u.getPromotions().getNumberOfPromotions();
                xp += u.getPromotions().getXP();
                Set<String> promos = new HashSet<>(u.getPromotions().getPromotions());
                Set<String> statuses = new HashSet<>(u.getStatusMap().keySet());
                for (String pr : promos) inc(allPromotions, pr, 1);  // every promotion, not only Gu that eat
                now.put(u.getId(), new UnitState(c.getCivName(), promos, statuses));
                UnitState p = prev.get(u.getId());
                boolean gainedFusion = false;
                if (p != null) for (String f : fusions) if (promos.contains(f) && !p.promos.contains(f)) gainedFusion = true;
                Set<String> countedStatus = new HashSet<>();
                for (Gu g : gus) {
                    String r = "rank" + g.rank;
                    boolean hasP = promos.contains(g.name), hasS = statuses.contains(g.status);
                    if (hasP) {
                        inc(holders, g.name, 1);
                        inc(held, r, 1);
                        if (c.getResourceAmount(g.food) < 0) inc(heldShort, r, 1);
                    }
                    if (hasS && countedStatus.add(g.status)) inc(hungry, g.status, 1);
                    if (p == null) continue;
                    boolean hadP = p.promos.contains(g.name), hadS = p.statuses.contains(g.status);
                    if (hadP && !hadS && hasS && hasP) inc(start, r, 1);
                    if (hadP && hadS && !hasS && !hasP && !gainedFusion) inc(death, r, 1);
                    else if (hadP && hadS && !hasS && hasP) inc(recover, r, 1);
                    else if (hadP && !hasP && !gainedFusion) inc(otherLoss, g.name, 1);
                }
            }
            rec.put("promotionsBought", bought); rec.put("xp", xp);
            rec.put("units", types); rec.put("promotionHolders", allPromotions); rec.put("guHolders", holders); rec.put("hungry", hungry);
            rec.put("hungerStart", start); rec.put("hungerDeath", death); rec.put("hungerRecover", recover);
            rec.put("guHeld", held); rec.put("guHeldInDeficit", heldShort); rec.put("guLostOther", otherLoss);

            int trades = 0, resOut = 0, resIn = 0, gptOut = 0, gptIn = 0;
            List<String> wars = new ArrayList<>(), allies = new ArrayList<>();
            for (Map.Entry<String, DiplomacyManager> e : c.getDiplomacy().entrySet()) {
                DiplomacyManager dm = e.getValue();
                Civilization other = dm.getOtherCiv();
                if (other.isMajorCiv() && c.isAtWarWith(other)) wars.add(other.getCivName());
                if (other.isCityState() && other.getAllyCiv() == c)
                    allies.add(other.getCivName());
                for (Trade t : dm.getTrades()) {
                    trades++;
                    for (TradeOffer o : t.getOurOffers()) {
                        String ty = o.getType().name();
                        if (ty.endsWith("_Resource")) resOut += o.getAmount();
                        if (ty.equals("Gold_Per_Turn")) gptOut += o.getAmount();
                    }
                    for (TradeOffer o : t.getTheirOffers()) {
                        String ty = o.getType().name();
                        if (ty.endsWith("_Resource")) resIn += o.getAmount();
                        if (ty.equals("Gold_Per_Turn")) gptIn += o.getAmount();
                    }
                }
            }
            rec.put("trades", trades); rec.put("resOut", resOut); rec.put("resIn", resIn);
            rec.put("gptOut", gptOut); rec.put("gptIn", gptIn); rec.put("wars", wars); rec.put("csAllies", allies);
            out.println(obj(rec));
        }
        final int bu = barbUnits; final int turn = gi.getTurns();
        out.println(obj(new LinkedHashMap<String, Object>() {{ put("event", "barbarians"); put("turn", turn); put("units", bu);
            put("unownedDeposits", unowned); }}));
        return now;
    }
}
