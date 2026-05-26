# Remaining Work For A Complete Port

## 1. Rebuild Gameplay Blueprints

The original UE5 gameplay Blueprints should not be trusted in VITE yet.

Problem actors/classes:

- `BP_AK47`
- `BP_M4A1`
- `BP_Pistol`
- `BP_CounterTerroristSpawnPoint`
- `BP_TerroristSpawnPoint`
- likely related player, game mode, HUD, and round-flow Blueprints

Recommended approach:

- Create new VITE-native Blueprints or C++ classes.
- Use current placeholder positions in `MAP_Main_VITE_Auto`.
- Keep the old Blueprints only as reference, not as runtime dependencies.

Minimum system to rebuild:

- GameMode
- PlayerController
- Character/Pawn
- Team assignment
- Spawn selection
- Weapon pickup
- Basic weapon fire
- Round reset

## 2. Recreate Widgets

These widgets remain incompatible:

- `WB_Crosshair`
- `WB_Main`
- `WB_TeamSelection`

Recommended approach:

- Recreate them in VITE/UE4.27 UMG.
- Avoid importing their downgraded packages directly.
- Reuse existing texture/font assets from `/Game/UI`, which validate OK.

Minimum widget rebuild:

- Crosshair
- Team selection
- Health/ammo/status HUD

## 3. Reconnect Map To Gameplay

Current map placeholders:

- 8 native `PlayerStart` actors tagged as `CT` or `T`.
- 84 native skeletal mesh weapon markers tagged as `AUTO_WEAPON_PLACEHOLDER`.

Next step:

- Replace marker-only weapons with functional pickup actors.
- Use marker transforms to spawn real pickup actors at BeginPlay.
- Use `PlayerStart` tags to choose CT/T spawn points.

## 4. Test Animations

Logs still show warnings around:

- `/Script/AnimationData`
- `/Script/ControlRig`
- custom version tags
- some animation assets saved by newer engine integrations

Recommended approach:

- Test player movement in PIE.
- If animation Blueprints crash or fail, create simplified UE4.27 animation assets or reimport source animations.

## 5. Final Validation

Before calling the port complete:

- Open `MAP_Main_VITE_Auto` in VITE.
- Set it as startup map.
- Launch PIE.
- Confirm player spawns.
- Confirm CT/T selection works.
- Confirm pickups work.
- Confirm HUD works.
- Run cook/package test.

## Known Bad Paths

Avoid re-enabling these in the stable target unless explicitly testing:

- `Downgrader` plugin
- `UE_MCP_Bridge`
- FSR plugins
- CMAA2 plugin
- old manually downgraded `MAP_Main.umap`
- `Content/Dependencies`
