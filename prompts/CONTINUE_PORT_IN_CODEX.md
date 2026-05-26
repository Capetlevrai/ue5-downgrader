# Fresh Codex Session Prompt

Use this prompt to continue the CounterStrike UE5 to VITE/UE4.27 port in a fresh Codex session.

```text
You are helping me continue a UE5 CounterStrike project port to the VITE Unreal Engine 4.27 fork.

Important: speak French with me, but use exact file paths and technical names.

Workspace/root:
C:\Users\Capet9800X3D\Desktop\CLONE VITE UE5

VITE engine:
D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor.exe
D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor-Cmd.exe

Stable VITE target project:
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject

Launch script:
D:\PORTAGE_VITE\Start_CounterStrike_VITE_CoreOnly.bat

Current working map:
/Game/Maps/MAP_Main_VITE_Auto

Physical map file:
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\Content\Maps\MAP_Main_VITE_Auto.umap

Do not use the original /Game/Maps/MAP_Main.umap. It is quarantined/too-old and VITE cannot load it.

Documentation repo:
D:\PORTAGE_VITE\ue5-downgrader

Read these first:
D:\PORTAGE_VITE\ue5-downgrader\README.md
D:\PORTAGE_VITE\ue5-downgrader\docs\PORTAGE_STATUS.md
D:\PORTAGE_VITE\ue5-downgrader\docs\MAP_RECONSTRUCTION.md
D:\PORTAGE_VITE\ue5-downgrader\docs\REMAINING_WORK.md
D:\PORTAGE_VITE\ue5-downgrader\docs\CRASHES_AND_FIXES.md

Current state:
- VITE engine is built and launches.
- Stable VITE target validates in commandlets.
- Most non-map content validates with ResavePackages.
- The original MAP_Main package is unreadable in VITE.
- A new VITE map MAP_Main_VITE_Auto was rebuilt from UE5.7-exported actor data.
- MAP_Main_VITE_Auto validates with VITE ResavePackages exit code 0.
- The map contains recovered geometry/lights/sky/camera/audio.
- It also contains 8 native PlayerStart placeholders at original team spawn positions.
- It also contains 84 native SkeletalMeshActor weapon markers at original weapon pickup positions.
- These placeholders were added through full editor startup Python because commandlet spawning crashes in VITE.

Critical constraints:
- Keep Downgrader disabled in the stable VITE target.
- Do not re-enable UE_MCP_Bridge, FSR, CMAA2, or other incompatible plugins unless explicitly testing.
- Do not put Content/Dependencies back into active Content without isolated validation.
- Do not try to directly use the three bad widgets:
  /Game/UI/WB_Crosshair
  /Game/UI/WB_Main
  /Game/UI/WB_TeamSelection
- Do not try to directly use the original MAP_Main.umap.
- Be careful with original gameplay Blueprints. BP_AK47, BP_M4A1, BP_Pistol and team spawn Blueprints have UE5/ControlRig/plugin dependency issues and may crash when loaded/spawned.

Known crash:
VITE commandlet Python + EditorLevelLibrary.spawn_actor_from_class crashes in:
FEditorViewportClient::GetCursorWorldLocationFromMousePos
FActorPositioning::GetCurrentViewportPlacementTransform
FLevelEditorViewportClient::TryPlacingActorFromObject

If you need to spawn actors with EditorLevelLibrary, do it via full VITE editor startup Python, wait some ticks for the viewport, save, then quit editor. Remove temporary Content/Python/init_unreal.py after use.

The next best task is to rebuild VITE-native gameplay:
1. Create or repair a GameMode for the VITE target.
2. Use PlayerStart tags CT/T from MAP_Main_VITE_Auto for team spawns.
3. Convert the 84 weapon marker actors into functional weapon pickup logic, ideally by spawning VITE-native pickup actors at BeginPlay.
4. Recreate minimal UMG widgets in UE4.27/VITE:
   - Crosshair
   - Team selection
   - HUD with health/ammo
5. Set MAP_Main_VITE_Auto as startup map.
6. Test PIE.
7. Validate with commandlets and eventually cook/package.

Before editing assets, inspect current project state and logs. Preserve existing working target and do not delete quarantines.
```
