# MAP_Main — Working downgrade into VITE (2026-05-27)

**Status: SUCCESS.** The official Asset Downgrader path now produces a map that opens
correctly in VITE 4.27 with full geometry fidelity, native lights, sky atmosphere and
post-process. This supersedes the rejected JSON-rebuild (`MAP_Main_VisualOnly_V2`, which
was visually wrong even after the rotation fix).

Final map: `/Game/Maps/MAP_Main_Downgraded` in
`D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader`.

## Why the earlier downgrade attempts failed

Downgrading the *full* `MAP_Main` (or even a sanitized copy) crashed on load in VITE. Root
causes, peeled one layer at a time:

1. **Gameplay BP actors** (`BP_Pistol`, `BP_AK47`, `BP_M4A1`, spawn points) — UE5 anim /
   ControlRig deps. Removed them → still crashed.
2. **`BP_GoodSky_C`** — UE5 dynamic-sky Blueprint, drags `Structure_GoodSky` + GoodSky
   material `*EditorOnlyData` classes that don't exist in 4.27. Removed it → still crashed.
3. **The real blocker: the World Settings `GameMode Override` = `GM_CounterStrike`.**
   Loading the map instantiates the GameMode, which pulls the player pawn →
   `AnimBP_Player` (struct mismatch `AnimNode_StateResult != FallbackStruct`),
   `ST_PlayerInfo`, `ST_WeaponInfo`, weapon/character materials →
   `Assertion failed: Object [UObjectAnnotation.h:785]`.

The AssetRegistry dependency dump made it obvious: the sanitized map's only suspicious
hard dependency was `/Game/Blueprints/GM_CounterStrike`. Everything else (SuperGrid
meshes/materials, audio, Reflex input, engine scripts) was clean.

## The working recipe

All steps in the **custom UE 5.7 Downgrader editor** unless noted.

1. **Load `/Game/Maps/MAP_Main`** (fresh editor, see CRASHES_AND_FIXES for the
   duplicate-map world-leak crash — never load a freshly-duplicated map while the source
   map is still loaded).
2. **Strip what crashes VITE** (done via Python in the bridge, on the in-memory world):
   - Delete the 92 gameplay BP actors (`BP_Pistol_C`, `BP_AK47_C`, `BP_M4A1_C`,
     `BP_CounterTerroristSpawnPoint_C`, `BP_TerroristSpawnPoint_C`).
   - Delete `BP_GoodSky_C`.
   - **Set World Settings `default_game_mode` to `/Script/Engine.GameModeBase`**
     (NOT None — None falls back to the project default which is still gameplay).
     Done with the native `level.set_world_settings(defaultGameMode=...)`.
   - `EditorLoadingAndSavingUtils.save_map(world, "/Game/Maps/MAP_Main_Sanitized")`
     (save-as; leaves the original `MAP_Main.umap` untouched). Result: 369 native actors,
     0 Blueprint actors.
3. **Downgrade**: Content Browser → select `MAP_Main_Sanitized` → Downgrader menu →
   `DowngradeSelectedAssets`, Target `4.27.2`, dependent-assets = **DoNothing**
   (`CopyAndDowngradeDependentAssets=DAO_DO_NOTHING`, already set in
   `Saved/Config/.../EditorPerProjectUserSettings.ini`). All 14 meshes + 8 materials are
   already present in VITE, so DoNothing is sufficient — no Copy Missing Assets needed.
   - **Do NOT run `SaveSelectedAssets` in the 5.7 source editor** — it re-saves the map
     back to 5.7 format (file grows ~867 KB -> ~1.04 MB), undoing the downgrade.
     `SaveSelectedAssets` is a *target-version* (4.27 + plugin) operation only.
4. **Copy** `...CounterStrike_5_7_DowngradeSource\Content\Maps\MAP_Main_Sanitized.umap`
   to `...NoDowngrader\Content\Maps\MAP_Main_Downgraded.umap`.
5. **Open in VITE.** The downgraded package is **not AssetRegistry-scannable** until
   resaved, so it does NOT appear in the Content Browser / Open Level dialog. Load it by
   path from the editor Python console:
   ```python
   import unreal; unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/MAP_Main_Downgraded")
   ```
   It opens with only 4 non-fatal load errors (EnhancedInput / Reflex nodes left in the
   level blueprint — harmless for a visual map).
6. **`Ctrl+S` (Save Current) in VITE.** This rewrites the map as a clean native 4.27 asset
   (size 867 KB -> ~703 KB), after which it IS registry-visible and packageable. This is
   the practical substitute for the plugin's `SaveSelectedAssets` step, valid because the
   map already opened without the plugin.

## Result

`/Game/Maps/MAP_Main_Downgraded` — 369 actors:

| Class | Count |
|---|---:|
| StaticMeshActor | 359 |
| DirectionalLight | 1 |
| SkyLight | 1 |
| PointLight | 2 |
| SkyAtmosphere | 1 |
| SphereReflectionCapture | 1 |
| PostProcessVolume | 1 |
| LightmassImportanceVolume | 1 |
| AmbientSound | 1 |
| CameraActor | 1 |

Bounds X[-100,8100] Y[0,8000] Z[-100,3400] — matches source (the JSON rebuild had lost
Z-max). Geometry visually confirmed correct in the VITE editor (walls / arch / stairs
correctly oriented), lit.

## Editor startup map

`Config/DefaultEngine.ini` updated so VITE opens this map directly:

```ini
[/Script/EngineSettings.GameMapsSettings]
GameDefaultMap=/Game/Maps/MAP_Main_Downgraded.MAP_Main_Downgraded
EditorStartupMap=/Game/Maps/MAP_Main_Downgraded.MAP_Main_Downgraded
```

## Sky — GoodSky 4.27 native (replaces the removed UE5 BP_GoodSky_C)

- UE5 `BP_GoodSky_C` was removed (un-downgradable, see above).
- The native **GoodSky 4.27** (Fab: https://www.fab.com/listings/6eb8de95-710e-45cf-a029-e48e709aef03)
  was added to a stock 4.27 project (`CounterStrike_UE427_Official`) via the launcher, then
  its `Content/GoodSky` folder (48 files, path `/Game/GoodSky`, BP at
  `/Game/GoodSky/Blueprint/BP_GoodSky`) was copied into VITE. Clean native path — no clash
  with the old broken `/Game/Marketplace/GoodSky`.
- Place `BP_GoodSky` in the map, then reconcile the sun: GoodSky drives its own
  DirectionalLight, so delete the map's existing `DirectionalLight` to avoid two suns.

## Remaining

- Reconcile GoodSky sun vs existing DirectionalLight; tune time-of-day to match source by
  eye (original BP_GoodSky_C parameters were not captured).
- Empty / rebuild the level blueprint (still has EnhancedInput Reflex nodes -> 4 load
  warnings).
- Pass 2: gameplay (weapons, spawns, game mode) — native rebuild, not downgrade.
- Lighting build.
