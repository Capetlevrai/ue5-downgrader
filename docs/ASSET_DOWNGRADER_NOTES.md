# Asset Downgrader Notes

## Primary Links

- Fab listing: https://www.fab.com/listings/86a0ce48-ff38-493c-906d-8d2297067ee6
- Tutorial/demo video: https://www.youtube.com/watch?v=yXvJfDNfrSQ
- Custom engine/plugin downloads: https://drive.google.com/drive/folders/1jvPfzknzWHo_diP3k9OJhAmRQZQSjQ7v

## Local Copies

Downloaded plugin folders currently used during this port:

```text
D:\PORTAGE_VITE\AssetDowngrader_Downloads\Downgrader_1.34_for_5.4.4
D:\PORTAGE_VITE\AssetDowngrader_Downloads\Downgrader_1.34_for_4.27.2
D:\PORTAGE_VITE\BuiltPlugins\AssetDowngrader_VITE
```

Local plugin documentation:

```text
D:\PORTAGE_VITE\AssetDowngrader_Downloads\Downgrader_1.34_for_5.4.4\Documentation.txt
D:\PORTAGE_VITE\AssetDowngrader_Downloads\Downgrader_1.34_for_4.27.2\Documentation.txt
```

## Rules From Vendor Documentation

- Back up all assets before downgrading.
- Use the Downgrader menu action `DowngradeSelectedAssets` in the source-version editor.
- Copy `.uasset` files directly after downgrade; do not use Unreal's Migrate action for the downgrade transfer.
- Open the target-version project with the matching target-version Downgrader plugin.
- Use `SaveSelectedAssets` in the target-version editor for assets that need to work later without the Downgrader plugin.
- For some source versions, including the 5.4 family, a custom Unreal Engine build with Downgrader engine modifications is required.
- Large whole-project downgrades can need very high RAM.
- If a broad downgrade crashes, isolate assets and downgrade them one by one.
- Some maps can crash because unsupported newer features remain, including Nanite/masked-material cases and packed-level actors.
- Assets can load but still differ visually; lighting, reflection probes, skylight, and directional light may need manual retuning.

## GoodSky — use the native 4.27 version, do NOT downgrade

The UE5 `BP_GoodSky_C` dynamic-sky Blueprint cannot be downgraded into VITE: it drags
`Structure_GoodSky`, GoodSky material functions, and `*EditorOnlyData` classes that do
not exist in 4.27, and crashes the loader during `ResolveDeferredDependencies`
(confirmed 2026-05-27, see PASS_1_RESULTS / CRASHES_AND_FIXES).

A native UE 4.27 GoodSky exists on Fab and should be installed directly in the VITE
project instead of downgrading the UE5 one:

- GoodSky 4.27 (Fab): https://www.fab.com/listings/6eb8de95-710e-45cf-a029-e48e709aef03

Plan for the sky: install the 4.27-native GoodSky into VITE, then place / re-wire its
sky actor in the rebuilt map. Until then the rebuilt visual map uses no dynamic sky
(plain SkyAtmosphere + SkyLight + DirectionalLight from the export, which ARE native and
downgrade/spawn fine).

## Downgrader path verdict for MAP_Main (2026-05-27)

The official Downgrader successfully converts the `.umap` format (5.7 -> 4.27,
"Downgraded 1/1 assets"), but the resulting map still **fails to open in VITE** even after
removing all gameplay Blueprint actors AND `BP_GoodSky_C`, because the map's **Level
Blueprint** imports the UE5 gameplay/anim graph (`ST_PlayerInfo`, `ST_WeaponInfo`,
`AnimBP_Player` with `AnimNode_StateResult != FallbackStruct` struct mismatch) and trips an
`Assertion failed: Object [UObjectAnnotation.h:785]`.

Conclusion: the downgrader cannot produce an openable MAP_Main without also gutting the
Level Blueprint. The JSON-rebuild path (`MAP_Main_VisualOnly_V2`, native actors only,
zero Blueprint imports) remains the working approach. Lights/sky/postprocess are being
added to that rebuild from the Pass 0 export data (all native classes).

## Pre-downgrade fix — Packed Level Actors

From the Downgrader plugin author (**BiKouZ**, Discord, 2026-05-27, in reply to our
crash question):

> "Downgrading packed level actors to 4.27 can cause crashes due to class reparenting
> (They don't exist in 4.27). To fix that, open all maps where you have packed level
> actors and use the **BreakPackedActors** option. Afterwards proceed with the downgrade
> as usual."

How to apply, in the source UE 5.7 (Downgrader) editor:

1. Open the map containing packed level actors.
2. Select the packed-level-actor instances in the Content Browser or Outliner.
3. Downgrader menu → **`BreakPackedActors`** (visible in the Downgrader toolbar menu
   alongside `DowngradeSelectedAssets`, `RemoveWorldPartitionFromSelectedAssets`, etc.).
4. Save the map.
5. Then run `DowngradeSelectedAssets` as usual.

Our MAP_Main port did not need this (no packed level actors in it — only StaticMeshActor,
native lights/atmosphere/postprocess, and the BPs we stripped). But any future map that
uses packed-level instances or was built via level-instance-to-packed conversion will hit
this crash; `BreakPackedActors` is the prerequisite.

Related — also in the same Downgrader menu:

- **`RemoveWorldPartitionFromSelectedAssets`** — needed if the map uses World Partition
  (WP doesn't exist in 4.27). Run before `DowngradeSelectedAssets`.
- **`FixLandscape`** / **`FixSubstrateMaterials`** / **`RevertSubstrateMaterials`** —
  domain-specific repairs for landscape and Substrate materials.

## Project-Specific Rules

- Keep the Downgrader plugin disabled in the VITE runtime validation target.
- Use the custom UE5.7 Downgrader source copy only as the downgrade/export staging project.
- Do not treat a commandlet-valid map as visually accepted until it has been compared against UE5.7 reference screenshots.
- Do not promote rebuilt maps unless actor counts, mesh counts, transforms, bounds, materials, lights, and screenshots have all been checked.
