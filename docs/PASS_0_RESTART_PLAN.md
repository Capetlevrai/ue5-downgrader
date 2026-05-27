# Pass 0 Restart Plan

## Reason For Restart

The earlier map reconstruction is rejected.

Observed result:

- `MAP_Main_VITE_Auto` loads and resaves in VITE but is visually unreliable.
- `MAP_Main_VisualOnly` was generated for visual-only testing and deleted after verification because the map layout was broken.

Likely causes:

- The first export did not preserve a full-fidelity representation of the UE5.7 scene.
- Component world transforms, root component state, pivots, bounds, lights, post-process, sky/fog, collisions, and unsupported actor types were not audited before rebuilding.
- The rebuild script spawned simplified actors from partial data and therefore could pass commandlet validation while still failing visually.

## Pass 0 Goal

Create a measurable source reference for `/Game/Maps/MAP_Main` in the custom UE5.7 Downgrader engine before rebuilding anything in VITE.

## Source Reference

Project:

```text
D:\PORTAGE_VITE\CounterStrike_5_7_DowngradeSource\CounterStrike.uproject
```

Engine:

```text
C:\Users\Capet9800X3D\Desktop\UNREAL ASSET DOWNGRADER (5.7)\UE_5.7.4_Downgrader\Engine\Binaries\Win64\UnrealEditor.exe
```

Map:

```text
/Game/Maps/MAP_Main
```

## Required Pass 0 Outputs

- Source screenshots from fixed camera angles:
  - perspective overview
  - top orthographic
  - front/side orthographic if possible
- Full actor inventory by class.
- Full static mesh inventory by mesh path.
- Per-actor and per-component world transforms.
- Per-component relative transforms.
- Root component class and transform.
- Actor/component bounds.
- Materials by slot.
- Light, sky, fog, reflection, post-process, and volume properties.
- Missing or unsupported actors listed separately.
- External actor / World Partition / packed actor evidence listed separately.

## Acceptance Criteria Before Pass 1

- The source export can prove the visual structure without relying on manual inspection only.
- The export records enough data to reconstruct each visible mesh using exact component world transforms.
- A diff tool can compare source export vs future VITE rebuild by class, mesh path, transform, bounds, and material.

## Pass 1 Preview

Only after Pass 0 is complete:

- Build `MAP_Main_VisualOnly_V2` in VITE from the full-fidelity export.
- Spawn meshes using component world transforms, not simplified actor transforms.
- Recreate lights and visual volumes from captured properties.
- Validate by commandlet and by visual screenshot comparison.
