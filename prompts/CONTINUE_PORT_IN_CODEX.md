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

Rejected prototype map:
/Game/Maps/MAP_Main_VITE_Auto

Prototype physical file:
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\Content\Maps\MAP_Main_VITE_Auto.umap

Do not use the original /Game/Maps/MAP_Main.umap. It is quarantined/too-old and VITE cannot load it.

Documentation repo:
D:\PORTAGE_VITE\ue5-downgrader

Read these first:
D:\PORTAGE_VITE\ue5-downgrader\README.md
D:\PORTAGE_VITE\ue5-downgrader\docs\PORTAGE_STATUS.md
D:\PORTAGE_VITE\ue5-downgrader\docs\MAP_RECONSTRUCTION.md
D:\PORTAGE_VITE\ue5-downgrader\docs\ASSET_DOWNGRADER_NOTES.md
D:\PORTAGE_VITE\ue5-downgrader\docs\PASS_0_RESTART_PLAN.md
D:\PORTAGE_VITE\ue5-downgrader\docs\PASS_0_RESULTS.md
D:\PORTAGE_VITE\ue5-downgrader\docs\REMAINING_WORK.md
D:\PORTAGE_VITE\ue5-downgrader\docs\CRASHES_AND_FIXES.md

Current state:
- VITE engine is built and launches.
- Stable VITE target validates in commandlets.
- Most non-map content validates with ResavePackages.
- The original MAP_Main package is unreadable in VITE.
- MAP_Main_VITE_Auto was rebuilt from UE5.7-exported actor data and validates with VITE ResavePackages exit code 0.
- MAP_Main_VITE_Auto is visually rejected and must not be treated as the current working map.
- MAP_Main_VisualOnly was generated for a visual-only test, then deleted after user verification showed the map was broken.
- Native gameplay plugin work exists, but it must be revalidated only after a visually correct map exists.

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

The next best task is no longer gameplay. The previous map rebuild was visually rejected.

Restart from Pass 0:

1. Open `/Game/Maps/MAP_Main` in the custom UE5.7 Downgrader source project.
2. Capture fixed-angle source reference screenshots.
3. Export full-fidelity visual scene data:
   - actor transforms
   - root component transforms
   - static mesh component world transforms
   - relative transforms
   - bounds
   - mesh paths
   - materials
   - light/sky/fog/post-process/volume properties
4. Build a new VITE candidate only after the source export is complete.
5. Compare source vs target by class counts, mesh counts, transforms, bounds, materials, and screenshots.

Before editing assets, inspect current project state and logs. Preserve existing working target and do not delete quarantines.
```
