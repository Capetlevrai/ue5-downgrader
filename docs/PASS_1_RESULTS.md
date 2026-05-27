# Pass 1 — Visual-only rebuild results

Status: **PASSED (geometry counts + rotations correct after fix), visual screenshots deferred to manual capture.**

Date: 2026-05-27

## Critical bug fixed during this pass — rotation axis order

The Pass 0 export script (`pass0_export_visual_v2_ue57.py:25-26`) serializes rotations as
`[roll, pitch, yaw]`:

```python
def rot_to_list(value):
    return [as_float(value.roll), as_float(value.pitch), as_float(value.yaw)]
```

The first rebuild used `unreal.Rotator(rpy[0], rpy[1], rpy[2])` which the UE constructor
interprets as `Rotator(pitch, yaw, roll)`. So every component with a non-identity rotation
was reconstructed with its axes permuted: source roll became target pitch, source pitch
became target yaw, source yaw became target roll. Result: arches, slopes, stairs, inner
corners all visibly mis-oriented while axis-aligned boxes/walls still looked correct.

Fix in `pass1_rebuild_visual_v2.py`:

```python
def rot(rpy):
    # JSON is [roll, pitch, yaw]; Rotator constructor wants (pitch, yaw, roll)
    return unreal.Rotator(float(rpy[1]), float(rpy[2]), float(rpy[0]))
```

Either re-running the rebuild commandlet writes a fresh `MAP_Main_VisualOnly_V2` with
correct orientations, or this bug is reintroduced if the Pass 0 export schema ever
changes — keep `rot_to_list` and `rot` in sync.

## Outputs

| File | Path |
|---|---|
| Target map | `/Game/Maps/MAP_Main_VisualOnly_V2` (VITE Content) |
| Rebuild report | `D:\PORTAGE_VITE\Pass1_Output\pass1_rebuild_report.json` |
| Validation report | `D:\PORTAGE_VITE\Pass1_Output\pass1_validation_report.json` |
| Rebuild log | `D:\PORTAGE_VITE\Pass1_Output\pass1_run.log` (+ `pass1_sidecar.log`) |
| Validate log | `D:\PORTAGE_VITE\Pass1_Output\pass1_validate_run.log` (+ `pass1_validate_sidecar.log`) |

## Rebuild result (run #5, with working APIs)

```text
Source actor entries:   462
Banned BPs skipped:     92  (BP_Pistol_C×42, BP_AK47_C×22, BP_M4A1_C×20, BP_*SpawnPoint×8)
Static mesh components: 364 spawned (target == source)
Missing meshes:         0
Missing materials:      0
Spawn errors:           0
Save:                   True
Elapsed:                4.97 s
```

## Validation result

| Metric | Source | VITE | Delta | Verdict |
|---|---:|---:|---:|:---:|
| Total actor entries | 462 | 364 | -98 | EXPECTED (92 banned + 6 non-mesh decor classes skipped per scope) |
| `static_mesh_component_count` | 364 | 364 | **0** | OK |
| Unique mesh paths used | 14 | 14 | 0 | OK |
| Per-mesh count (all 14 paths) | match | match | **0** | OK |
| Bounds X | [-100, 8100] | [-100, 8100] | 0 | OK |
| Bounds Y | [-7983, 8000] | [-7983, 8000] | 0 | OK |
| Bounds Z low | -100 | -100 | 0 | OK |
| Bounds Z high | 3400 | 1100 | -2300 | INVESTIGATE — likely a GoodSky sub-mesh (Moon at z≈3400) whose `world_transform.location` differs from how Pass 0 measured it |

### Class diff (per source class)

All classes that were intentionally skipped show their full source count as a "missing" delta — that's correct by design:

| Class | Source | VITE | Delta | Why missing on VITE |
|---|---:|---:|---:|---|
| `StaticMeshActor`               | 359 | 364 | +5  | We split BP_GoodSky_C's 5 SMComps into plain SMAs |
| `BP_Pistol_C`                   | 42  | 0   | -42 | Banned by handoff (gameplay = Pass 2+) |
| `BP_AK47_C`                     | 22  | 0   | -22 | Banned by handoff |
| `BP_M4A1_C`                     | 20  | 0   | -20 | Banned by handoff |
| `BP_CounterTerroristSpawnPoint_C` | 4 | 0   | -4  | Banned by handoff |
| `BP_TerroristSpawnPoint_C`      | 4   | 0   | -4  | Banned by handoff |
| `BP_GoodSky_C`                  | 1   | 0   | -1  | Split into plain SMAs (above) |
| `DirectionalLight`              | 1   | 0   | -1  | Pass 1b scope |
| `SkyLight`                      | 1   | 0   | -1  | Pass 1b scope |
| `PointLight`                    | 2   | 0   | -2  | Pass 1b scope |
| `SkyAtmosphere`                 | 1   | 0   | -1  | Pass 1b scope |
| `SphereReflectionCapture`       | 1   | 0   | -1  | Pass 1b scope |
| `PostProcessVolume`             | 1   | 0   | -1  | Pass 1b scope |
| `LightmassImportanceVolume`     | 1   | 0   | -1  | Pass 1b scope |
| `AmbientSound`                  | 1   | 0   | -1  | Pass 1b scope |
| `CameraActor`                   | 1   | 0   | -1  | Pass 1b scope |

## Visual validation — manual step

`HighResShot` from a headless `UE4Editor.exe -ExecutePythonScript -unattended` invocation
does not render a frame (no active viewport client tied to a real window), so the
automated screenshot stage produced zero PNGs (the call succeeds but nothing flushes
to `Saved/Screenshots/Windows/`).

**Manual repro on VITE side:**

1. Launch `D:\PORTAGE_VITE\Start_CounterStrike_VITE_CoreOnly.bat`
2. In the editor: `File → Open Level → /Game/Maps/MAP_Main_VisualOnly_V2`
3. ⚠️ The map will look very dark / unlit / black-sky — that is **expected**:
   no lights, no SkyAtmosphere, no PostProcessVolume, no SkyLight have been
   imported yet. They are Pass 1b scope. Use `unlit` view-mode (`Alt+3`) or
   `lit unbuilt` to inspect geometry.
4. Compare the 3 reference shots from `D:\PORTAGE_VITE\Pass0_SourceReference\screenshots\`
   against the VITE viewport at the same camera poses:
   - perspective: location (8500, 9500, 2200), rotation (pitch -12, yaw -130)
   - top:         location (4000, 0, 6000),    rotation (pitch -89.5, yaw 0)
   - side from -Y: location (4000, -11500, 4000), rotation (pitch -18, yaw 90)

## 4.27 Python API quirks discovered (saved in `docs/CRASHES_AND_FIXES.md`)

| Issue | Root cause | Workaround |
|---|---|---|
| `spawn_actor_from_class` crashes with `EXCEPTION_ACCESS_VIOLATION` in `FEditorViewportClient::GetCursorWorldLocationFromMousePos` | The 4.27 EditorLevelLibrary spawn path goes through `TryPlacingActorFromObject` which needs a LevelEditorViewportClient. `-run=pythonscript` commandlet has none. | Run with full `UE4Editor.exe -ExecutePythonScript=...` (not `UE4Editor-Cmd.exe -run=pythonscript`). |
| `World.spawn_actor`, `GameplayStatics.begin_deferred_actor_spawn_from_class` | Not exposed in 4.27 Python (added later). | n/a — must go through `EditorLevelLibrary` (see above). |
| `EditorLevelLibrary.new_level(path)` returns `False` in commandlet | Editor UI dependency. | `EditorLoadingAndSavingUtils.new_blank_map(save_existing_map=False)` + `save_map(world, path)`. |
| `EditorLoadingAndSavingUtils.new_blank_map(save_existing=False)` | 4.27 parameter is named `save_existing_map`, not `save_existing`. | Use the 4.27 spelling. |
| `unreal.TextureRenderTarget2DFactoryNew` | Not exposed in 4.27 Python. | Use `HighResShot` console command instead. |
| `HighResShot` from headless editor writes nothing | The async screenshot queue needs an active rendered frame. | Take screenshots manually from an interactive editor session. |
| Python prints lost on crash | `unreal.log` buffered to stdout. | Side-car log file that is flushed per line. |

## Next steps

- **Pass 1a verification (manual)**: launch the VITE editor, open the new map, eyeball geometry parity vs source screenshots. Report any visible discrepancies in this doc.
- **Investigate Z-max bounds discrepancy**: the GoodSky meshes (Moon / Sphere / RingFull / StarMesh) may need their root_component transform composed with their parent BP transform — currently we only read `static_mesh_components[].world_transform` which may not capture the full hierarchy for BP-actor children.
- **Pass 1b — re-introduce lighting/sky/postprocess**: 1 DirectionalLight, 1 SkyLight, 2 PointLight, 1 SkyAtmosphere, 1 PostProcessVolume, 1 SphereReflectionCapture, 1 LightmassImportanceVolume, 1 AmbientSound, 1 CameraActor, BP_GoodSky_C. The export v2 has the data in `light_components[]`, `audio_components[]`, `post_process` — Pass 1b will read those.
- **Pass 2 — gameplay** (still rejected from Pass 1 scope): rebuild weapons / spawn points / game mode flow. The original BPs are flagged unstable in VITE per handoff.
