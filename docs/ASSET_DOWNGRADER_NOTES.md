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

## Project-Specific Rules

- Keep the Downgrader plugin disabled in the VITE runtime validation target.
- Use the custom UE5.7 Downgrader source copy only as the downgrade/export staging project.
- Do not treat a commandlet-valid map as visually accepted until it has been compared against UE5.7 reference screenshots.
- Do not promote rebuilt maps unless actor counts, mesh counts, transforms, bounds, materials, lights, and screenshots have all been checked.
