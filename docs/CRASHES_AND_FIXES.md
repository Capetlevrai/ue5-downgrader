# Crashes And Fixes

## ShaderCompileWorker Missing

Symptom:

```text
Unable to launch ... ShaderCompileWorker.exe
```

Fix:

- Build VITE engine tools, including `ShaderCompileWorker`.

## UE5.4 Asset Downgrader Refuses Standard Engine

Symptom:

```text
Assets can only be downgraded from the latest UE version
```

Finding:

- The Downgrader plugin requires vendor engine modifications for supported source versions.
- The available custom engine was UE5.7.4, not UE5.4.

Fix:

- Use the vendor-provided UE5.7.4 custom engine and UE5.7.4 custom Downgrader plugin.

## Downgrader Crashes With Copy Missing Assets

Symptom:

- Downgrader processes thousands of dependencies even for one selected asset.
- Crashes inside `CoreUObject` or `Downgrader`.

Fix:

- Set dependent assets behavior to do nothing:

```text
CopyAndDowngradeDependentAssets=DAO_DO_NOTHING
DependentAssets=
```

## VITE Cannot Load Manually Downgraded Map/Widgets

Symptom:

```text
Package is too old
Package Version: 0
Min Required Version: 214
```

Affected:

- `MAP_Main.umap`
- `WB_Crosshair`
- `WB_Main`
- `WB_TeamSelection`

Fix:

- Quarantine those assets.
- Rebuild the map and widgets natively or from exported metadata.

## VITE Commandlet Spawn Crash

Symptom:

```text
EXCEPTION_ACCESS_VIOLATION
FEditorViewportClient::GetCursorWorldLocationFromMousePos()
FActorPositioning::GetCurrentViewportPlacementTransform()
FLevelEditorViewportClient::TryPlacingActorFromObject()
UEditorLevelLibrary::SpawnActorFromClass()
```

Cause:

- `EditorLevelLibrary.spawn_actor_from_class()` uses editor viewport placement code.
- In commandlet mode the viewport is null.

Fix:

- Do actor spawning in full editor startup Python, not commandlet Python.

## UE 5.7 — World Memory Leaks On Duplicated Map Load

Symptom:

```text
Fatal error: [File:EditorServer.cpp] [Line: 2524]
World Memory Leaks: 2 leaks objects and packages.
```

Repro (2026-05-27):

1. UE 5.7 source editor open with `/Game/Maps/MAP_Main` loaded.
2. `asset.duplicate /Game/Maps/MAP_Main -> /Game/Maps/MAP_Main_Sanitized` (succeeds).
3. `level.load /Game/Maps/MAP_Main_Sanitized` → editor crashes.

Cause:

- Duplicating a map while the source map is still loaded leaves cross-references
  between the duplicate package and the source UWorld.
- The next world-switch triggers UE 5.7's strict world memory leak detector,
  which aborts because `MAP_Main` UWorld is still referenced by the duplicate's
  redirector tree.

Fix:

- Always work on the duplicated map from a fresh editor process where the
  source map was never loaded.
- Recipe:
  1. Duplicate first (with the source map loaded is fine).
  2. Close the editor.
  3. Reopen the editor (do NOT pre-open the source map).
  4. Load the duplicate — clean.

## Blueprint Class Loading Crash

Symptom:

- Loading some gameplay Blueprints crashes or emits many warnings about ControlRig/AnimationData.

Cause:

- UE5-only animation data, ControlRig dependencies, and missing plugin/script imports.

Fix:

- Do not spawn original gameplay Blueprints in the stable map.
- Replace with native placeholders.
- Recreate gameplay in VITE-native assets.
