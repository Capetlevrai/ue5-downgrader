# Asset Downgrader — Official documentation (vendor)

**Source**: Fab listing page of the **Asset Downgrader** plugin by **relativegames7@gmail.com**.
Pasted verbatim 2026-05-27 for archival, with minimal markdown formatting for readability.
See also our project-specific learnings in [`ASSET_DOWNGRADER_NOTES.md`](ASSET_DOWNGRADER_NOTES.md).

Author contact: relativegames7@gmail.com — vendor states: "I fix all errors sent to me (usually <24 hours)."

> If you need to migrate assets to a different project that uses an older Unreal Engine
> version — if you have migrated assets to an earlier version and they don't seem to
> "appear" in the content browser — or if you want to make your assets available to
> people using earlier versions — what you need is the Asset Downgrader.

## Supported target versions

Asset Downgrader downgrades to:

- 5.6.1
- 5.5.4
- 5.4.4
- 5.3.2
- 5.2.1
- 5.1.1
- 5.0.3
- 4.27
- 4.26

It works by first upgrading the assets to **Source Version (5.6)**, then applying various
patches to the `.uasset` files to make them compatible with the chosen TargetVersion —
just without the newer data (e.g. nanite data is removed for a 4.27 downgrade).

Features of newer Unreal versions (nanite on masked materials, new material nodes, new
Niagara module versions, new Blueprint nodes) **cannot** be ported to the older versions.

## How it works

1. **Back up all your assets first** — this plugin is highly experimental and may corrupt
   assets or crash the editor.
2. Either keep **two projects** (SourceVersion + TargetVersion) or **switch the same
   project** between versions. **Integrate the plugin in both** projects.
3. In the SourceVersion project, **select** the assets you wish to downgrade.
4. From the Downgrader menu choose **`DowngradeSelectedAssets`**.
5. **Migrate by copy-pasting the `.uasset` files manually.** Do NOT use Unreal's
   `Actions → Migrate...` — that would resave assets in the SourceVersion format.
   Alternatively, switch the project to the TargetVersion in place.
6. If the TargetVersion is a **5.0.3** project, add this to `Config/DefaultEngine.ini`:
   ```ini
   [Core.System]
   UsePackageTrailer=True
   ```
   You will get a crash on opening assets in 5.0.3 if this is not enabled.
7. On the TargetVersion project, install the **Google Drive version** of the plugin for
   that specific target version.
8. Open the TargetVersion project and then the downgraded assets. If there were no
   errors, the assets should open correctly.

Certain assets, in order to be migrated to **other TargetVersion projects that don't
have the Downgrader plugin**, need to be **resaved through the plugin** (select all the
assets and use the plugin's `SaveSelectedAssets` option) **inside the TargetVersion
editor**.

## Supported Assets Spreadsheet

Vendor maintains a spreadsheet of supported asset types:
https://docs.google.com/spreadsheets/d/1hMbFOg1IlH4AyOd2A7_eN1xw2H375rqiDYqOOLKvRaY/edit#gid=960867659

## Custom UE engine builds

To downgrade certain assets (or all assets in the case of 5.4) you need a **custom build
of Unreal Engine** with specific engine modifications. The plugin folder contains a URL
file:

```
UE_5.5\Engine\Plugins\Marketplace\AssetDowngrader\Download Custom Engine & Plugin.url
```

— follow it to download both the custom UE 5.5 build and the precompiled plugin for that
engine version. Integrate the precompiled plugin in the source project's Plugins folder,
then switch the source project engine version to this custom engine build. **The video
tutorial shows this entire process.**

If you need an older custom engine build (e.g. 5.3), remember that **upgrading assets to
the latest version is always possible**. The vendor recommends always using the latest
custom engine build because it's the only one in active development. If that's not
feasible, contact the vendor to discuss alternatives.

## FAQ

**Can it be downgraded lower than 4.26?** Not currently, but with enough research and
engine modifications definitely possible. Contact the vendor if you have specific needs.

**My asset is not in the support list, will it work?** Most likely yes; if not, email the
vendor with it and they'll work on a fix.

## Known issues & workarounds

- **Launcher version crashes** → use the **Downgrader Custom Engine** along with its own
  custom version of the plugin.
- **Assets don't appear in packaged builds** → you forgot to resave the assets; use
  `SaveSelectedAssets`.
- **Downgraded scenes look too bright in 5.0** → tune ReflectionProbes / Skylight /
  Directional light intensity, and/or rebuild lighting.
- **Whole-project downgrades may consume up to 128 GB RAM** because many assets stay in
  memory.
- **Crashes when downgrading many assets** → start a new run and answer **Yes** when
  asked to **resume the previous downgrade process**.
- **Textures in formats like RGBA32F** are not downgraded past versions like 5.0 because
  those formats don't exist in 5.0.
- **Opening certain maps will sometimes crash** — typically caused by masked materials
  with nanite (not allowed in 5.0). Try opening assets individually, or remove nanite
  entirely, and then open the map.
- **Landscapes pure black in 4.27** → use the Downgrader menu option **`FixLandscape`**.
- **Skeletal meshes can crash when saved in 4.27** if their binary format was not in the
  5.4+ format originally. Fix: save the skeletal mesh first so its binary format gets
  updated. For many of them, use `SaveSelectedAssets` prior to downgrading.
- **Packed level actors → crash on downgrade to 4.27** due to class reparenting (the
  classes don't exist in 4.27). Fix: open every map containing packed level actors and
  use the **`BreakPackedActors`** option. Then proceed with the downgrade as usual.
  *(BiKouZ confirmed this to us via Discord, 2026-05-27.)*
- **Niagara particles behaving differently after downgrade** → expected in some cases:
  the downgrade reverts a module to an older version of that module (to avoid crashes).
  Use the **`CopyAndDowngrade`** option so dependent modules from a higher version are
  copied, downgraded and referenced correctly.
- **Error extracting the Custom Build zip** → use **WinRAR**.
- If you use your own custom build of Unreal and require the engine modifications to
  integrate the downgrading process, the vendor can provide them for a fee (licensing
  contact).

## Vendor contact

Email: **relativegames7@gmail.com** — include the offending `.uasset` / project. Vendor
fixes issues usually within 24 hours.

---

## Video tutorial — walkthrough notes (plugin v1.10, 5.4 → 4.27)

- **Video**: https://www.youtube.com/watch?v=yXvJfDNfrSQ
- **Published**: 2024-06-13
- **Plugin version shown**: 1.10 (note: our local plugin is 1.34 — newer)

Transcribed from the auto-generated English subtitles
(`[English (auto-generated)] Asset Downgrader for UE5 Tutorial and Demo (v1.10).srt`).

**Concrete example demonstrated**: downgrading the *June 2024 free assets of the month*
marketplace pack — 340 assets — from UE 5.4 to UE 4.27 using plugin v1.10. Below are the
specific, actionable bits the video adds on top of the text documentation.

### 5.3 versus 5.4 — when you need the custom engine

- **5.3 → 4.27**: the launcher version of the plugin is enough.
  `Downgrader → DowngradeSelectedAssets → 4.27`, done.
- **5.4 → 4.27**: requires the **custom engine build**. Trying the launcher version in
  5.4 produces an error dialog asking *"download custom engine build? [Yes/No]"*. Click
  **Yes** and it opens the vendor's **Google Drive folder**.

### Custom engine setup — concrete steps from the demo

1. From the Google Drive, download:
   - The **custom UE 5.4.2 build** (~**15 GB zipped, ~50 GB unpacked**).
   - The **plugin precompiled for that custom 5.4.2 build** (in the demo: `Downgrader
     1.10 for 5.4.2`).
2. Extract the custom engine somewhere. The demo uses `C:\UE_5.4 downgrader`.
3. In your **project folder**, switch the engine version from launcher 5.4 to the
   downgrader build:
   - Right-click the `.uproject` → *Switch Unreal Engine Version*.
   - It won't be in the list — choose *"select folder"* and point it at the custom
     engine folder.
4. Extract the precompiled plugin zip, rename if needed, **create a `Plugins/` folder
   in the project**, and drop the plugin in there.
5. **Reopen the project on the custom engine.** The Downgrader menu is now backed by
   the engine-modification version that can handle 5.4 → older.
6. `Downgrader → DowngradeSelectedAssets → 4.27` → confirm the engine-modifications
   prompt → it loads all assets, patches them, saves them.

### Migration step shown in the video

After downgrade, **copy the `.uasset` files** from the source project's `Content/`
folder into a **fresh 4.27 project's `Content/`** folder, then open the 4.27 project.
No `Actions → Migrate`.

### Live fix demonstrated — landscape goes black in 4.27

When the user opens the downgraded map in 4.27, the ground is rendered black. Fix:

`Downgrader menu → FixLandscape` → recompiles the landscape material's shaders → ground
renders correctly. (This is the same `FixLandscape` option present in our menu screenshot
captured earlier.)

### Known live-discovered glitch — tree material swap

In the demo the trees in the downgraded scene had **swapped materials** (each tree mesh
ended up with the wrong material). The vendor explicitly says on camera that he had *just
discovered* this and would investigate. Treat it as an open class of post-downgrade
visual artifacts that may need per-asset cleanup.

### Closing line from the video

> "If you encounter crashes either while downgrading in 5.4 or when you open the maps in
> your target version, send them to me and I'll work on a fix." (relativegames7@gmail.com)

---

*Doc-version note*: this captures the vendor doc as it stood when we pasted it
(2026-05-27). Earlier local copies (`D:\PORTAGE_VITE\AssetDowngrader_Downloads\
Downgrader_1.34_for_4.27.2\Documentation.txt`) referenced a smaller version list
(source 5.3-5.4) and fewer known issues — this newer version supersedes them.
Cross-check the Fab listing for any further updates.
