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

- Create new VITE-native Blueprints or C++ classes after the visual map is correct.
- Use the rejected placeholder positions only as rough reference data.
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

## 3. Rebuild The Map From Pass 0

The current map prototype is rejected for visual fidelity.

Do first:

- Follow `docs/PASS_0_RESTART_PLAN.md`.
- Capture UE5.7 source screenshots and full-fidelity actor/component data.
- Rebuild a new VITE visual-only map from component world transforms.
- Compare source vs target by screenshots and export diff.

Do not continue gameplay work against `MAP_Main_VITE_Auto` until the visual map is correct.

## 4. Reconnect Map To Gameplay

Rejected prototype placeholders:

- 8 native `PlayerStart` actors tagged as `CT` or `T`.
- 84 native skeletal mesh weapon markers tagged as `AUTO_WEAPON_PLACEHOLDER`.

Next step:

- Replace marker-only weapons with functional pickup actors.
- Use marker transforms to spawn real pickup actors at BeginPlay.
- Use `PlayerStart` tags to choose CT/T spawn points.

## 5. Test Animations

Logs still show warnings around:

- `/Script/AnimationData`
- `/Script/ControlRig`
- custom version tags
- some animation assets saved by newer engine integrations

Recommended approach:

- Test player movement in PIE.
- If animation Blueprints crash or fail, create simplified UE4.27 animation assets or reimport source animations.

## 6. Final Validation

Before calling the port complete:

- Open the accepted rebuilt map in VITE.
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

## Native Gameplay Update

Implemented:

- Added VITE-native plugin:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\Plugins\ViteGameplay
```

- Added `AViteCSGameMode`, `AViteCSPlayerController`, `AViteCSCharacter`, `AViteCSHUD`, `AViteCSWeaponPickup`.
- Added native UMG base classes:
  - `UViteCSCrosshairWidget`
  - `UViteCSTeamSelectionWidget`
  - `UViteCSHUDWidget`
- Set `/Game/Maps/MAP_Main_VITE_Auto` as startup/game default map at the time of the prototype.
- Set `/Script/ViteGameplay.ViteCSGameMode` as `GlobalDefaultGameMode`.
- Added input mappings for WASD, mouse look, jump, fire, reload, CT team, and T team.
- Validated `MAP_Main_VITE_Auto` with VITE `ResavePackages` after loading the plugin: exit code 0, but the map was later visually rejected.

Still to do:

- Repoint the native GameMode to the accepted rebuilt map, then PIE-test it.
- Confirm the player actually spawns on CT/T `PlayerStart` tags.
- Confirm BeginPlay converts all 84 weapon markers into functional pickups.
- Replace Canvas HUD with real UE4.27 WidgetBlueprint assets if UMG assets are required for final parity.
- Cook/package test after PIE is stable.
