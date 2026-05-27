# Pass 0 Results

Date: 2026-05-27

## Source Export V2

Script:

```text
D:\PORTAGE_VITE\Scripts\pass0_export_visual_v2_ue57.py
```

Repo copy:

```text
scripts/pass0_export_visual_v2_ue57.py
```

Output:

```text
D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2.json
D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2_Summary.json
```

Command:

```powershell
& 'C:\Users\Capet9800X3D\Desktop\UNREAL ASSET DOWNGRADER (5.7)\UE_5.7.4_Downgrader\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' 'D:\PORTAGE_VITE\CounterStrike_5_7_DowngradeSource\CounterStrike.uproject' -run=pythonscript -script='D:\PORTAGE_VITE\Scripts\pass0_export_visual_v2_ue57.py' -unattended -nop4 -NullRHI
```

The commandlet exits with code `1` because the source map still logs Blueprint, Animation, and ControlRig load/compile errors. The export itself completed and reported `0` script export errors.

## Export Counts

```text
Actors: 462
Scene components: 766
Static mesh components: 364
Light components: 4
Audio components: 1
Script export errors: 0
```

## Actor Class Counts

```text
359 StaticMeshActor
42  BP_Pistol_C
22  BP_AK47_C
20  BP_M4A1_C
4   BP_TerroristSpawnPoint_C
4   BP_CounterTerroristSpawnPoint_C
2   PointLight
1   SkyAtmosphere
1   PostProcessVolume
1   SphereReflectionCapture
1   SkyLight
1   LightmassImportanceVolume
1   BP_GoodSky_C
1   AmbientSound
1   DirectionalLight
1   CameraActor
```

## Important Notes

- This export is the new baseline for the next rebuild attempt.
- It includes root component data, scene component transforms, static mesh component transforms, mesh paths, materials, actor bounds, light components, and audio components.
- The commandlet load errors are source asset problems and must be tracked separately from export success.
- Viewport screenshots are still needed. A visible UE5.7 editor launch was attempted but Windows cancelled the `Start-Process` call.

## Next Step

Produce source reference screenshots from the UE5.7 editor viewport:

- perspective overview
- top orthographic
- side/front orthographic if possible

Then build `MAP_Main_VisualOnly_V2` from component-level data and compare it against this export.
