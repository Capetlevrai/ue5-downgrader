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

Important status as of 2026-05-27:

- The previous automatic map rebuild is no longer accepted as visually correct.
- `/Game/Maps/MAP_Main_VITE_Auto` can load/resave, but it must be treated as a failed prototype, not as the final map.
- `/Game/Maps/MAP_Main_VisualOnly` was deleted after visual verification showed the layout was broken.
- The map port must restart from Pass 0 with a measured UE5.7 reference scene before any new VITE rebuild.

## What Works

- VITE engine is built and launches.
- The stable VITE target opens headless and validates with commandlets.
- Most non-map content is downgraded enough to load in VITE.
- Native gameplay plugin work exists, but it was built against the rejected prototype map and must be revalidated after the map is rebuilt correctly.

## Rejected Work

- `MAP_Main_VITE_Auto`: commandlet-valid but visually unreliable.
- `MAP_Main_VisualOnly`: deleted after verification because the map was broken.
- Cause to investigate: the first exporter/rebuilder did not preserve enough UE scene data for exact visual parity.

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
- [Asset Downgrader notes](docs/ASSET_DOWNGRADER_NOTES.md)
- [Pass 0 restart plan](docs/PASS_0_RESTART_PLAN.md)
- [Pass 0 results](docs/PASS_0_RESULTS.md)
- [Remaining work](docs/REMAINING_WORK.md)
- [Fresh Codex prompt](prompts/CONTINUE_PORT_IN_CODEX.md)
