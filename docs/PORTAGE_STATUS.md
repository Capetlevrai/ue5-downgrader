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
- Use `/Game/Maps/MAP_Main_VITE_Auto` as the current working map.

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
