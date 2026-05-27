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

Important status as of 2026-05-27 (evening update):

- **WORKING MAP: `/Game/Maps/MAP_Main_Downgraded`** — produced via the official Asset
  Downgrader after stripping the gameplay GameMode override. Geometry visually confirmed
  correct in VITE, with native lights / sky atmosphere / post-process. Full recipe in
  [docs/DOWNGRADER_MAP_SUCCESS.md](docs/DOWNGRADER_MAP_SUCCESS.md). This is now the
  canonical visual map and the editor startup map.
- Rejected approaches (history only):
  - `/Game/Maps/MAP_Main_VITE_Auto` — commandlet-valid but visually wrong.
  - `/Game/Maps/MAP_Main_VisualOnly` (deleted) and `/Game/Maps/MAP_Main_VisualOnly_V2`
    (JSON rebuild) — visually wrong even after the rotation-order fix; the export/rebuild
    path is too lossy. Use the downgrader path instead.
- Sky: UE5 `BP_GoodSky_C` is un-downgradable; use the **native GoodSky 4.27** (Fab),
  copied to VITE at `/Game/GoodSky`.

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
- [Claude handoff prompt](prompts/CONTINUE_WITH_CLAUDE.md)
