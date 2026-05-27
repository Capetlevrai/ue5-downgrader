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

## 2026-05-27 Result: Rejected For Visual Fidelity

`/Game/Maps/MAP_Main_VITE_Auto` remains useful as a record of what was attempted, but it is no longer accepted as the working map.

Follow-up test:

- Built `/Game/Maps/MAP_Main_VisualOnly` from the same actor export while excluding gameplay Blueprint actors.
- VITE `ResavePackages` succeeded with exit code 0.
- User visual verification showed the map was broken.
- The `MAP_Main_VisualOnly.umap`, its report, and its one-off rebuild script were deleted.

Conclusion:

- Commandlet load/save success is insufficient for this map.
- The previous export/rebuild path is too lossy for visual parity.
- Restart from Pass 0 using a full-fidelity source reference.

Next document:

```text
docs/PASS_0_RESTART_PLAN.md
```
