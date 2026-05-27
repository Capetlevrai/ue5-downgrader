# Lighting parity guide — UE 5.7 source vs VITE 4.27 downgraded map

Reference investigation done with `MAP_Main` → `MAP_Main_Downgraded` (2026-05-27).
Methodology: read every relevant render/lighting CVar and component property on both
sides via the live MCP bridges (`ue-mcp-counterstrike` on the 5.7 source, `unreal-vite`
on the VITE 4.27 target), diff them, fix what can be fixed, document what can't.

This is the canonical reference for "why does the same downgraded map look different in
the two editors, and what should I match."

## TL;DR

After the cross-engine investigation, **almost everything is already identical** between
the source and the downgraded VITE map. The single actionable delta we found and fixed
was `r.TonemapperFilm` (the engine-wide tonemap mode). Persist it in
`Config/DefaultEngine.ini`:

```ini
[SystemSettings]
r.TonemapperFilm=0
```

The remaining 5–10 % visual gap comes from **GoodSky dome material divergence** between
the UE5 and 4.27 product versions, plus **SkyLight captured-cubemap content** that we
cannot reproduce without a working Lightmass build (the VITE fork is shipped without
`UnrealLightmass.exe`).

## What we checked, and the result of each diff

### Scalability groups
Read on both: `sg.ResolutionQuality`, `sg.ViewDistanceQuality`, `sg.AntiAliasingQuality`,
`sg.ShadowQuality`, `sg.PostProcessQuality`, `sg.TextureQuality`, `sg.EffectsQuality`,
`sg.FoliageQuality`, `sg.ShadingQuality`. **All identical** (level 3 = High on both).

### Render-method CVars
| CVar | Source 5.7 | VITE 4.27 | Diff |
|---|---|---|---|
| `r.Lumen.GlobalIllumination` | 0 (off) | n/a | none — source isn't using Lumen either |
| `r.Lumen.Reflections` | 0 (off) | n/a | none |
| `r.DynamicGlobalIlluminationMethod` | 0 (None) | 0 (None) | identical |
| `r.ReflectionMethod` | 2 (SSR) | n/a (UE5-only CVar) | 4.27 uses SSR via PP volume defaults instead |
| `r.AntiAliasingMethod` | 2 (TAA) | n/a (UE5-only CVar) | 4.27 uses `r.DefaultFeature.AntiAliasing=2` (TAA), equivalent |
| `r.RayTracing.Enable` | 1 | 0 | expected — RT doesn't exist in 4.27 |
| `r.Tonemapper.Quality` | 5 | 5 | identical |
| **`r.TonemapperFilm`** | **0** (legacy) | **1** (Film/ACES) | **THE delta — VITE fork enables Film tonemap by default, source uses legacy** |
| `r.AutoExposure.Bias` | 0 | 0 | identical |
| `r.EyeAdaptationQuality` | 2 | 2 | identical |

**Action**: set `r.TonemapperFilm=0` in VITE's `Config/DefaultEngine.ini` under
`[SystemSettings]`. Done.

### PostProcessVolume settings (both maps)
Every single field we sampled is byte-identical:
- `white_temp=6500`, `white_tint=0.05`
- `color_saturation=(1,1,1,1)`, `color_contrast=(1,1,1,1)`, `color_gain=(1,1,1,1)`,
  `color_gamma=(1,1,1,1)`, `color_offset=(0,0,0,0)`
- `color_saturation_shadows/midtones/highlights = (1,1,1,1)` (no grading split)
- `auto_exposure_bias=1.0`, `auto_exposure_method=HISTOGRAM`,
  `auto_exposure_min_brightness=0.0`, `auto_exposure_max_brightness=1.0`
- `bloom_intensity=0.6`, `vignette_intensity=0.0`
- `film_slope=0.88`, `film_toe=0.55`, `film_shoulder=0.26`

The Asset Downgrader preserves the entire `FPostProcessSettings` struct correctly, and
the default values of that struct happen to match between UE 5.7 and UE 4.27.

### SkyLight component
| Property | Source 5.7 | VITE 4.27 |
|---|---|---|
| `mobility` | `STATIONARY` | `STATIONARY` |
| `source_type` | `SLS_CAPTURED_SCENE` | `SLS_CAPTURED_SCENE` |
| `intensity` | 5.0 | 5.0 |
| `real_time_capture` | False | False |
| `light_color` | white | white |
| `lower_hemisphere_color` | (0.0545, 0.0545, 0.0545) | (0.0545, 0.0545, 0.0545) |

**Identical.** What differs is the actual *content* of the captured cubemap stored in
the level's `_BuiltData`. The source has a cubemap captured (in-editor transient state,
or partially baked). VITE has none — we only copied the `.umap`, not the `_BuiltData`
sidecar (and even if we did, UE5 BuiltData wouldn't load in 4.27). Without a Lightmass
build on the VITE side, the captured cubemap stays empty / default → gray ambient
contribution.

Attempts that did NOT work for this in our session:
- `recapture_sky()` from Python + `BuildReflectionCaptures` console command — fired but
  result was indistinguishable; Stationary SkyLight capture data is tied to the lighting
  build pipeline, not refreshed live.
- Switching to `Movable` + `real_time_capture=True` — produced ORANGE-cramé scene because
  the GoodSky dome occludes the capture sphere; the SkyLight ends up capturing the dome's
  warm interior instead of the blue atmosphere. Reverted.

The proper fix requires `Build → Build Lighting Only`, which requires
`UnrealLightmass.exe` in `<engine>/Binaries/Win64/`. The VITE fork ships without it.
Copying the launcher 4.27 `UnrealLightmass.exe` into VITE's `Engine/Binaries/Win64/` is a
plausible workaround we tried but couldn't validate in this session (needs editor restart
to be re-detected by Swarm; we hit the `Swarm failed to kick off / Compile Unreal
Lightmass` message again after copy + retry without restart).

### DirectionalLight component
| Property | Source 5.7 | VITE 4.27 |
|---|---|---|
| `mobility` | `STATIONARY` | `STATIONARY` |
| `intensity` | 7.0 | 7.0 |
| `light_color` | white | white |
| `temperature` | 6500 | 6500 |
| `use_temperature` | False | False |

**Identical.**

### SkyAtmosphere component
| Property | Source 5.7 | VITE 4.27 |
|---|---|---|
| `bottom_radius` | 6360 | 6360 |
| `atmosphere_height` | 60 | 60 |
| `ground_albedo` | (170,170,170) | (170,170,170) |
| `multi_scattering_factor` | 1.0 | 1.0 |
| `rayleigh_scattering_scale` | 0.0331 | 0.0331 |
| `rayleigh_exponential_distribution` | 8.0 | 8.0 |
| `mie_scattering_scale` | 0.003996 | 0.003996 |
| `mie_absorption_scale` | 0.000444 | 0.000444 |
| `mie_anisotropy` | 0.8 | 0.8 |
| `mie_exponential_distribution` | 1.2 | 1.2 |
| `other_absorption_scale` | 0.001881 | 0.001881 |
| `transform_mode` | `PLANET_TOP_AT_ABSOLUTE_WORLD_ORIGIN` | same |
| `trace_sample_count_scale` | 1.0 | 1.0 |

**Identical.** Both use the engine default values of the struct.

### GoodSky dome material — the asset-level divergence we can't byte-match
| | Path of the dome MID's parent material |
|---|---|
| Source 5.7 (`MAP_Main`) | `/Game/Marketplace/GoodSky/Resource/Materials/M_GoodSky_Sun_Stars` (UE5 GoodSky) |
| VITE 4.27 (`MAP_Main_Downgraded`) | `/Game/GoodSky/Source/Materials/M_GoodSky_Sun_Stars` (4.27 native GoodSky) |

Same **name** — `M_GoodSky_Sun_Stars` — but **two different assets**, because we had to
strip the UE5 `BP_GoodSky_C` (un-downgradable, see `ASSET_DOWNGRADER_NOTES.md`) and
install the native 4.27 GoodSky from Fab. The two versions of the product ship two
different shader graphs that read inputs and react to lighting/sun-angle differently. The
dome renders a slightly different color → the inside of the dome looks slightly
different → the SkyLight's captured cubemap (if rebuilt) would be slightly different →
ambient on the walls is slightly different.

No safe automated fix exists for this — you'd have to author a custom GoodSky 4.27
material that emulates the UE5 one exactly, which is significantly out of scope.

## What we can match (the actionable list)

In priority order for any future cross-version port:

1. **`r.TonemapperFilm=0`** in `[SystemSettings]` of the target project's
   `DefaultEngine.ini`. Equalizes the tonemap mode.
2. **PostProcessVolume** — read all overridden fields on the source and apply on the
   target. Asset Downgrader preserves them for free, so usually nothing to do.
3. **SkyLight / DirectionalLight / SkyAtmosphere** — read component properties on both
   sides via Python and diff. Same story: typically preserved.
4. **Engine Scalability** — set both to Epic via `Settings → Engine Scalability Settings
   → Epic` for the editor viewport so neither runs on a downgraded preset.
5. **Build Lighting** in the target — required to populate the SkyLight captured cubemap
   and lightmap GI. Needs `UnrealLightmass.exe` present (copy from the launcher 4.27
   engine if the fork doesn't ship one), and an editor restart so Swarm re-detects it.

## What we cannot match (the irreducible gap)

- **Lumen-style dynamic GI auto-tinting** the scene with the sky color in 5.7 default
  setups — but in this specific project the source isn't using Lumen, so this is a
  non-issue here.
- **GoodSky dome shader differences** between UE5 and 4.27 product versions. The dome
  itself renders slightly differently, which propagates to whatever the SkyLight captures
  and how reflections look against the dome.
- **Lightmass cache continuity** — the source map's SkyLight transient capture may
  reflect a previous bake or a previous GoodSky dome state we can't reconstruct.

## Methodology used (reusable for any future map)

1. Same map loaded in both editors (source via `ue-mcp-counterstrike`, target via
   `unreal-vite`).
2. Dump CVars on both sides:
   ```python
   import unreal
   for c in ["sg.ResolutionQuality","sg.ViewDistanceQuality","sg.AntiAliasingQuality",
             "sg.ShadowQuality","sg.PostProcessQuality","sg.TextureQuality",
             "sg.EffectsQuality","sg.FoliageQuality","sg.ShadingQuality",
             "r.TonemapperFilm","r.Tonemapper.Quality","r.AutoExposure.Bias",
             "r.EyeAdaptationQuality","r.DynamicGlobalIlluminationMethod",
             "r.ReflectionMethod","r.AntiAliasingMethod"]:
       print(c, unreal.SystemLibrary.get_console_variable_float_value(c))
   ```
3. Diff and apply matching CVars to the target's `DefaultEngine.ini` under
   `[SystemSettings]`.
4. Dump component properties on both sides for: `SkyLight`, `DirectionalLight`,
   `PostProcessVolume.settings`, `SkyAtmosphere`. Diff each field. Apply diffs on the
   target.
5. Identify any *asset-level* divergence (different material parents, mesh assets,
   re-imported textures). These are content fixes, not engine fixes.
6. Build lighting on the target once everything else matches.
