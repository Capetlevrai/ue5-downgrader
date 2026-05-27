# Pass 1 — Asset Inventory (VITE side)

Generated from `D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2_Summary.json`
checked against `D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\Content\` and `D:\CLONE VITE UE5\Engine\Content\`.

## Result: 100% available — no downgrade or placeholder needed

### Static meshes (14 unique, 364 components)

| Asset | Components | VITE |
|---|---:|:---:|
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_Box` | 276 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_CornerInner` | 40 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_CylinderFull` | 10 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_Arch2` | 8 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_CornerOuter` | 8 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_Slope` | 8 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_CylinderBend` | 6 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_Stairs` | 2 | OK |
| `/Engine/BasicShapes/Plane` | 1 | OK (engine) |
| `/Engine/BasicShapes/Sphere` | 1 | OK (engine) |
| `/Game/Marketplace/GoodSky/Resource/ArrowTool/SM_GoodSky_Moon` | 1 | OK |
| `/Game/Marketplace/GoodSky/Resource/ArrowTool/SM_GoodSky_StarMesh` | 1 | OK |
| `/Game/Marketplace/GoodSky/Resource/Mesh/SM_GoodSky_Sphere` | 1 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Source/Meshes/SuperGrid_RingFull` | 1 | OK |

### Materials (8 unique, 364 slot assignments)

| Asset | Slots | VITE |
|---|---:|:---:|
| `/Game/Marketplace/SuperGrid/TutorialLevel/MaterialInstances/M_TutOrient` | 161 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Materials/Palette/Basic/M_SuperGrid_Soil` | 110 | OK |
| `/Game/Marketplace/SuperGrid/TutorialLevel/MaterialInstances/M_Tut_Oriented` | 50 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Materials/Palette/Basic/M_SuperGrid_Stone` | 30 | OK |
| `/Game/Marketplace/SuperGrid/StarterPack/Materials/Palette/Advanced/M_SuperGrid_Auto` | 8 | OK |
| `/Game/Marketplace/GoodSky/Resource/ArrowTool/M_GoodSky_Sun_Emissive` | 3 | OK |
| `/Game/Marketplace/GoodSky/Resource/ArrowTool/M_GoodSky_SkyRing_` | 1 | OK |
| `/Game/Marketplace/GoodSky/Resource/Materials/M_GoodSky_Base` | 1 | OK |

## What this means for Pass 1

- No asset import / migration needed.
- The rebuild script can spawn 364 StaticMeshActors directly from `world_transform` of each `static_mesh_components[]` entry.
- BP_Pistol / BP_AK47 / BP_M4A1 / BP_*SpawnPoint actors are **excluded by handoff constraint** (gameplay rebuild is Pass 2+).
- BP_GoodSky_C: kept (no ban), its 4 sub-meshes (Moon, StarMesh, Sphere, RingFull) will be rebuilt as plain StaticMeshActors as well — visual-only.
- Lights / AmbientSound / PostProcessVolume / SkyAtmosphere / SkyLight / DirectionalLight / SphereReflectionCapture / LightmassImportanceVolume / CameraActor: **out of scope** for visual-only-v2 (no SMComps inside them). They will be re-introduced in Pass 1b once geometry is validated.
