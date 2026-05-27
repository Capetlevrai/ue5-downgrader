# CounterStrike VITE Port Status

## Key Paths

Original UE5.4 project:

```text
C:\Users\Capet9800X3D\Desktop\PORTAGE VITE\Projet Final\CounterStrike
```

UE5.7 custom source copy:

```text
D:\PORTAGE_VITE\CounterStrike_5_7_DowngradeSource
```

Stable VITE target:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader
```

Stable VITE `.uproject`:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject
```

VITE engine:

```text
D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor.exe
```

Official UE4.27:

```text
D:\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor.exe
```

Custom UE5.7 Downgrader engine:

```text
C:\Users\Capet9800X3D\Desktop\UNREAL ASSET DOWNGRADER (5.7)\UE_5.7.4_Downgrader\Engine\Binaries\Win64\UnrealEditor.exe
```

## Stable Target Rules

- Keep `Downgrader` disabled in the VITE runtime/validation target.
- Keep `UE_MCP_Bridge`, FSR, CMAA2 and other incompatible UE5 plugins disabled or outside active `Plugins`.
- Keep the original manually downgraded `MAP_Main.umap` quarantined. It remains unreadable by VITE.
- Do not use `/Game/Maps/MAP_Main_VITE_Auto` as final map evidence. It is commandlet-valid but visually rejected.
- Restart map work from Pass 0 before producing the next VITE map candidate.

## Validated Content

VITE `UE4Editor-Cmd.exe -run=ResavePackages` validated these folders:

- `/Game/Audio`
- `/Game/UI`, except the quarantined widgets
- `/Game/Blueprints`
- `/Game/Animations`
- `/Game/Assets`
- `/Game/References`
- `/Game/Marketplace/GoodSky`
- `/Game/Marketplace/SuperGrid`
- `/Game/Marketplace/ParagonMaleAnnouncer`
- `/Game/Marketplace/FPS_Weapon_Bundle`
- `/Game/Marketplace/MilitaryWeapDark`
- `/Game/Marketplace/MilitaryCharDark`
- `/Game/Marketplace/MilitaryCharSilver`

## Quarantined Or Excluded

Quarantined widgets:

- `/Game/UI/WB_Crosshair`
- `/Game/UI/WB_Main`
- `/Game/UI/WB_TeamSelection`

Quarantine folder:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\_Quarantine_TooOldAssets_AfterManual
```

Excluded folder:

```text
Content\Dependencies
```

Reason: too-old assets, World Partition/Substrate/Interchange dependencies, and Downgrader crashes.

## Validation Commands

Validate the rebuilt map:

```powershell
$Engine='D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor-Cmd.exe'
$Project='D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject'
& $Engine $Project -run=ResavePackages -PackageFilter=/Game/Maps/MAP_Main_VITE_Auto -SkipCompile -NullRHI -Unattended -NoSplash -NoSound
```

Latest result: exit code 0.

## Native Gameplay Pass

Added after the map reconstruction:

```text
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\Plugins\ViteGameplay
```

Current state:

- `ViteGameplay` is enabled in the stable `.uproject`.
- `ViteGameplay` compiles with the VITE `UE4Editor` target.
- `DefaultEngine.ini` sets both startup maps to `/Game/Maps/MAP_Main_VITE_Auto`.
- `GlobalDefaultGameMode` is `/Script/ViteGameplay.ViteCSGameMode`.
- `AViteCSGameMode` uses `PlayerStart` actor tags `CT` and `T`.
- `AViteCSGameMode` spawns `AViteCSWeaponPickup` actors from `AUTO_WEAPON_PLACEHOLDER` markers at BeginPlay.
- `AViteCSHUD` draws a minimal crosshair and health/ammo/team HUD through Canvas.
- Native UMG base classes exist for future VITE WidgetBlueprint assets.

Validation after adding this plugin:

```powershell
& 'D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor-Cmd.exe' 'D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject' -run=ResavePackages -PackageFilter=/Game/Maps/MAP_Main_VITE_Auto -SkipCompile -NullRHI -Unattended -NoSplash -NoSound
```

Latest result after native gameplay pass: exit code 0.

## Map Rebuild Reset 2026-05-27

Rejected:

- `/Game/Maps/MAP_Main_VITE_Auto`
- `/Game/Maps/MAP_Main_VisualOnly`

Reason:

- The generated maps could load/resave but did not visually match the source map.
- `MAP_Main_VisualOnly` was deleted after verification.
- The prior export/rebuild path did not capture enough scene fidelity.

New source of truth:

```text
docs/PASS_0_RESTART_PLAN.md
```

Next step:

- Reopen `/Game/Maps/MAP_Main` in the custom UE5.7 Downgrader engine.
- Capture fixed-angle source screenshots and a full-fidelity visual export.
- Build the next VITE map only after source-vs-target diff metrics are available.
