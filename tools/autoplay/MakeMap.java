// Builds a map file with Unciv's own classes, so the saved JSON is exactly what the game loads
// [src MapSaver.mapToSavedString, TileMap(width, height, ruleset)]. Driven by tools/make_map.py.
//
//   java -cp <jar>:<classes> MakeMap <mods dir parent> <mod name> <spec file> <out file>
//
// Spec lines (tab-separated):
//   size <width> <height>
//   tile <column> <row> <base terrain> <features, '+'-joined or -> <resource or -> <amount> <improvement or ->
//        <rivers: 'b' bottom, 'r' bottom right, 'l' bottom left, any combination, or ->
//   start <column> <row> <nation>
import com.badlogic.gdx.Gdx;
import com.unciv.UncivGame;
import com.unciv.logic.files.MapSaver;
import com.unciv.logic.map.HexMath;
import com.unciv.logic.map.MapShape;
import com.unciv.logic.map.MapSize;
import com.unciv.logic.map.TileMap;
import com.unciv.logic.map.tile.Tile;
import com.unciv.models.metadata.GameSettings;
import com.unciv.models.ruleset.Ruleset;
import com.unciv.models.ruleset.RulesetCache;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class MakeMap {
    public static void main(String[] args) throws Exception {
        String modName = args[1];
        UncivGame game = new UncivGame(true);
        UncivGame.Companion.setCurrent(game);
        game.setSettings(new GameSettings());
        RulesetCache.INSTANCE.loadRulesets(true, false);
        Ruleset ruleset = RulesetCache.INSTANCE.get(modName);
        if (ruleset == null) throw new IllegalStateException("mod not loaded: " + modName);

        List<String[]> lines = new ArrayList<>();
        for (String l : Files.readAllLines(Paths.get(args[2]), StandardCharsets.UTF_8))
            if (!l.isBlank() && !l.startsWith("#")) lines.add(l.split("\t"));
        int w = Integer.parseInt(lines.get(0)[1]), h = Integer.parseInt(lines.get(0)[2]);
        TileMap map = new TileMap(w, h, ruleset, false);
        map.getMapParameters().setShape(MapShape.rectangular);
        map.getMapParameters().setMapSize(new MapSize(w, h));
        map.getMapParameters().setName("Qing Mao Mountain");
        map.getMapParameters().setBaseRuleset(modName);
        map.getMapParameters().setSeed(1L);  // a fixed seed keeps the file reproducible (tools/make_map.py --check)
        Map<String, Tile> byColRow = new HashMap<>();
        // the same column/row walk as the rectangular TileMap constructor
        for (int column = -w / 2; column <= (w - 1) / 2; column++)
            for (int row = -h / 2; row <= (h - 1) / 2; row++)
                byColRow.put(column + "," + row, map.get(HexMath.INSTANCE.getTileCoordsFromColumnRow(column, row)));
        int tiles = 0, starts = 0;
        for (String[] p : lines) {
            if (p[0].equals("tile")) {
                Tile t = byColRow.get(p[1] + "," + p[2]);
                if (t == null) throw new IllegalStateException("no tile at " + p[1] + "," + p[2]);
                t.setBaseTerrain(p[3]);
                t.setTerrainFeatures(p[4].equals("-") ? new ArrayList<>() : new ArrayList<>(Arrays.asList(p[4].split("\\+"))));
                if (!p[5].equals("-")) { t.setTileResource(p[5], false); t.setResourceAmount(Integer.parseInt(p[6])); }
                if (!p[7].equals("-")) t.setImprovementBasic(p[7]);
                t.setHasBottomRiver(p[8].contains("b"));
                t.setHasBottomRightRiver(p[8].contains("r"));
                t.setHasBottomLeftRiver(p[8].contains("l"));
                tiles++;
            } else if (p[0].equals("start")) {
                Tile t = byColRow.get(p[1] + "," + p[2]);
                if (!map.addStartingLocation(p[3], t, com.unciv.logic.map.TileMap.StartingLocation.Usage.Player))
                    throw new IllegalStateException("start rejected: " + p[3]);
                starts++;
            }
        }
        map.setTransients(ruleset, true);
        Files.write(Paths.get(args[3]), MapSaver.INSTANCE.mapToSavedString(map).getBytes(StandardCharsets.UTF_8));
        System.out.println("[make_map] " + tiles + " tiles, " + starts + " starting locations -> " + args[3]);
        System.exit(0);
    }
}
