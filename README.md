# UE5 to VITE/UE4.27 Downgrade Notes

This repository documents the ongoing port of a UE5 CounterStrike project to the VITE Unreal Engine 4.27 fork.

The goal is not only to record commands, but to preserve the decisions, crash patterns, working paths, and next steps so the port can continue in a fresh Codex session without repeating failed work.

## Current Result

The most stable target project is:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject
```

Launch script:

```text
D:\PORTAGE_VITE\Start_CounterStrike_VITE_CoreOnly.bat
```

Current VITE engine:

```text
D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor.exe
```

The main map was rebuilt into a VITE-loadable map:

```text
/Game/Maps/MAP_Main_VITE_Auto
```

Physical file:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\Content\Maps\MAP_Main_VITE_Auto.umap
```

## What Works

- VITE engine is built and launches.
- The stable VITE target opens headless and validates with commandlets.
- Most non-map content is downgraded enough to load in VITE.
- Main map geometry was reconstructed automatically from the UE5.7 source map.
- The rebuilt map loads and resaves in VITE with exit code 0.
- Original team spawn positions were recreated as native `PlayerStart` actors.
- Original weapon pickup positions were recreated as native `SkeletalMeshActor` markers.

## What Is Still Missing

- Real gameplay Blueprints need repair or replacement.
- Three UMG widgets need recreation in UE4.27/VITE.
- Spawn/team selection/game mode flow needs to be rebuilt.
- Weapon pickup functionality needs to be reimplemented.
- Player animation/ControlRig warnings need runtime testing and likely cleanup.
- Final PIE, cook, and package tests have not been completed.

See:

- [Portage status](docs/PORTAGE_STATUS.md)
- [Map reconstruction](docs/MAP_RECONSTRUCTION.md)
- [Remaining work](docs/REMAINING_WORK.md)
- [Fresh Codex prompt](prompts/CONTINUE_PORT_IN_CODEX.md)
