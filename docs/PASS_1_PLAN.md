# Pass 1 — Visual-only rebuild plan (VITE)

## Goal

Reconstruct the geometry of `/Game/Maps/MAP_Main` (source UE 5.7 CounterStrike project)
into a new VITE (UE 4.27 fork) map `/Game/Maps/MAP_Main_VisualOnly_V2`, using the
**per-component world_transform** from the Pass 0 v2 export (not the per-actor transform,
which is unreliable for actors built from multiple meshes).

This pass is intentionally limited to **visual geometry only**. Lights, audio, post-process,
sky, gameplay BPs, and weapons spawns are out of scope.

## Why a fresh "V2" map (not reusing MAP_Main_VITE_Auto)

Per handoff `CONTINUE_WITH_CLAUDE.md`:
> Le portage precedent de la map est rejete. /Game/Maps/MAP_Main_VITE_Auto charge et resave
> dans VITE mais ne correspond pas visuellement a la map source.

So `MAP_Main_VITE_Auto` is left untouched and we build a brand-new map from the v2 export
to compare side-by-side.

## Inputs

| Input | Path | Notes |
|---|---|---|
| Pass 0 v2 full export | `D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2.json` | 2.7 MB, 462 actors, 364 SMComps |
| Pass 0 v2 summary | `D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2_Summary.json` | Class / mesh / material counts |
| Reference screenshots | `D:\PORTAGE_VITE\Pass0_SourceReference\screenshots\MAP_Main_*.png` | 3 angles, captured via ue-mcp on source 5.7 |
| VITE project | `D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject` | Downgrader plugin disabled |
| VITE engine | `D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor-Cmd.exe` | UE 4.27.2 base, VITE fork |

## Scope decisions

- **Include**: every `static_mesh_components[]` entry from every source actor, whatever
  the actor class — *except* the banned classes below.
- **Exclude (banned by handoff)**: `BP_Pistol_C`, `BP_AK47_C`, `BP_M4A1_C`,
  `BP_CounterTerroristSpawnPoint_C`, `BP_TerroristSpawnPoint_C`. Gameplay rebuild = Pass 2+.
- **Exclude for now (Pass 1b)**: lights (1 DirectionalLight, 1 SkyLight, 2 PointLight),
  `SkyAtmosphere`, `SphereReflectionCapture`, `PostProcessVolume`, `LightmassImportanceVolume`,
  `AmbientSound`, `CameraActor`, `BP_GoodSky_C` actor itself (we still spawn its 4 child meshes
  as plain StaticMeshActors — Moon / StarMesh / Sphere / RingFull).

## Asset availability

100 % of the 14 unique meshes and 8 unique materials referenced by the source map are already
present on the VITE side. See [pass1_asset_inventory.md](../reports/pass1_asset_inventory.md).
No downgrade, no migration, no placeholder needed.

## Rebuild approach

Script: [`scripts/pass1_rebuild_visual_v2.py`](../scripts/pass1_rebuild_visual_v2.py)

For each non-banned actor in the v2 export, iterate `static_mesh_components[]` and for each
component:

1. Load `mesh` asset → if missing, log and skip.
2. `spawn_actor_from_class(StaticMeshActor, world_transform.location, world_transform.rotation)`.
3. `set_actor_scale3d(world_transform.scale)`.
4. `static_mesh_component.set_static_mesh(mesh_asset)`.
5. Apply `cast_shadow` and `collision_profile_name` if present.
6. For each `materials[]` slot, `set_material(slot, material_asset)`.
7. Label the new actor `"<source_label>__<component_name>"` for traceability.

Then save the map via `EditorLoadingAndSavingUtils.save_map(world, TARGET_MAP_PATH)`.

## Known 4.27 gotchas discovered during this pass

| Symptom | Cause | Fix |
|---|---|---|
| `EXCEPTION_ACCESS_VIOLATION` in `FEditorViewportClient::GetCursorWorldLocationFromMousePos` when calling `spawn_actor_from_class` | `-nullrhi` mode → no viewport client; `EditorScriptingUtilities` spawn path dereferences a null viewport to compute a cursor placement transform. | Don't pass `-nullrhi`. RHI init costs ~30 s but the spawn path becomes safe. |
| `EditorLevelLibrary.new_level(path)` returns `False` in commandlet | Internal API depends on editor UI state. | Use `EditorLoadingAndSavingUtils.new_blank_map(save_existing=False)` to get an in-memory world, then `save_map(world, path)`. |
| `unreal.log` messages disappear when the script crashes | Python output buffered, flushed on clean exit only. | Side-car log: open a `.log` file in `Pass1_Output/` and write+flush each milestone manually. |

## Invocation

```powershell
& 'D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor-Cmd.exe' `
  'D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject' `
  -run=pythonscript `
  -script='D:\PORTAGE_VITE\ue5-downgrader\scripts\pass1_rebuild_visual_v2.py' `
  -stdout -unattended -nopause
```

(Run from `D:\PORTAGE_VITE\Pass1_Output\` to capture `pass1_run.log` next to the report.)

## Validation

Script: [`scripts/pass1_validate_visual_v2.py`](../scripts/pass1_validate_visual_v2.py)

- Loads `/Game/Maps/MAP_Main_VisualOnly_V2` in VITE.
- Collects live `actor_count`, `static_mesh_component_count`, `per_class`, `per_mesh_path`,
  and overall actor bounds.
- Diffs against the Pass 0 summary.
- Captures 3 screenshots via `SceneCapture2D + TextureRenderTarget2D` at the same camera
  poses as the source reference shots, then exports them to PNG via
  `RenderingLibrary.export_render_target`.
- Writes `Pass1_Output/pass1_validation_report.json` and PNGs under
  `Pass1_Output/screenshots/`.

## Acceptance criteria (Pass 1)

| Metric | Pass if |
|---|---|
| `live_static_mesh_component_count` | == 364 (or document the missing) |
| `class_diff[StaticMeshActor]` | live − source = +364 − 0 ≈ +364 (we replace 359 source SMA + 5 SMComps inside BP_GoodSky by 364 plain SMA) |
| `mesh_diff` per asset | live counts equal source counts within ±0 |
| Live bounds X / Y / Z | overlap source bounds X[-100,8100] Y[-7983,8000] Z[-100,3400] |
| Visual diff (screenshots) | recognizable identical geometry, layout, scale |

If any criterion fails → diagnose in `docs/PASS_1_RESULTS.md` and iterate the script.
