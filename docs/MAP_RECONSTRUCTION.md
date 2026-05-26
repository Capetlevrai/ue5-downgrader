# MAP_Main Automated Reconstruction

The original downgraded `MAP_Main.umap` could not be loaded by VITE.

VITE error:

```text
Package Version: 0
Min Required Version: 214
Package is too old
```

## Working Strategy

The map was loaded in the custom UE5.7 Downgrader engine, then actor data was exported to JSON. A new VITE map was generated from that data.

Export file:

```text
D:\PORTAGE_VITE\MAP_Main_ActorExport.json
```

Export result:

```text
462 / 462 actors extracted
```

Rebuilt VITE map:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\Content\Maps\MAP_Main_VITE_Auto.umap
```

Initial reconstruction:

```text
370 actors spawned
```

Recovered actor types:

- Static mesh geometry
- Directional light
- Point lights
- Sky light
- Sky atmosphere
- Post-process volume
- Sphere reflection capture
- Lightmass importance volume
- Camera actor
- Ambient sound

## Extra Placeholder Pass

The original gameplay Blueprint classes were unstable in VITE:

- `BP_AK47`
- `BP_M4A1`
- `BP_Pistol`
- `BP_CounterTerroristSpawnPoint`
- `BP_TerroristSpawnPoint`

Loading/spawning those Blueprints can crash because of UE5-only animation, ControlRig, or missing plugin references.

Instead, a safe placeholder pass was run in the full VITE editor using startup Python:

```text
D:\PORTAGE_VITE\Scripts\add_safe_gameplay_placeholders_vite.py
```

Report:

```text
D:\PORTAGE_VITE\MAP_Main_VITE_Auto_PlaceholderReport.json
```

Result:

```json
{
  "spawn_points": 8,
  "weapon_markers": 84,
  "skipped": [],
  "errors": []
}
```

Placeholder replacements:

- Team spawn Blueprints -> native `PlayerStart`
- `BP_AK47` and `BP_M4A1` positions -> `/Game/Marketplace/MilitaryWeapDark/Weapons/Assault_Rifle_B`
- `BP_Pistol` positions -> `/Game/Marketplace/MilitaryWeapDark/Weapons/Pistols_B`

## Important Crash Pattern

In VITE commandlet mode, `EditorLevelLibrary.spawn_actor_from_class()` crashes in:

```text
FEditorViewportClient::GetCursorWorldLocationFromMousePos()
FActorPositioning::GetCurrentViewportPlacementTransform()
FLevelEditorViewportClient::TryPlacingActorFromObject()
```

Reason: the commandlet has no valid editor viewport. Use full editor startup Python when spawning actors through `EditorLevelLibrary`.

## Current Map Status

`/Game/Maps/MAP_Main_VITE_Auto` loads and resaves in VITE with exit code 0.

It is not yet a complete gameplay map. It is a stable reconstructed scene with safe placeholders.
