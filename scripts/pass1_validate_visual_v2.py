"""
Pass 1 — Validate the rebuilt VITE map.

Reads:   /Game/Maps/MAP_Main_VisualOnly_V2 (must exist on disk in VITE Content)
         D:/PORTAGE_VITE/Pass0_SourceReference/MAP_Main_SourceVisual_v2_Summary.json
Writes:  D:/PORTAGE_VITE/Pass1_Output/pass1_validation_report.json
         D:/PORTAGE_VITE/Pass1_Output/screenshots/MAP_VITE_perspective.png
         D:/PORTAGE_VITE/Pass1_Output/screenshots/MAP_VITE_top.png
         D:/PORTAGE_VITE/Pass1_Output/screenshots/MAP_VITE_side_Y.png

Invocation: same UE4Editor-Cmd commandlet pattern as the rebuild script
(no -nullrhi — required for spawn + scene capture).
"""
import json
import os
import time

import unreal


SOURCE_SUMMARY = r"D:/PORTAGE_VITE/Pass0_SourceReference/MAP_Main_SourceVisual_v2_Summary.json"
TARGET_MAP     = "/Game/Maps/MAP_Main_VisualOnly_V2"
OUT_DIR        = r"D:/PORTAGE_VITE/Pass1_Output"
SHOT_DIR       = os.path.join(OUT_DIR, "screenshots")
REPORT_JSON    = os.path.join(OUT_DIR, "pass1_validation_report.json")
SIDECAR_LOG    = os.path.join(OUT_DIR, "pass1_validate_sidecar.log")


def _ensure_dirs():
    for d in (OUT_DIR, SHOT_DIR):
        if not os.path.isdir(d):
            os.makedirs(d)


def _sidecar(line):
    _ensure_dirs()
    with open(SIDECAR_LOG, "a") as fh:
        fh.write("[{0}] {1}\n".format(time.strftime("%H:%M:%S"), line))
        fh.flush()


def log(msg):
    unreal.log("[Pass1Validate] " + str(msg))
    _sidecar(str(msg))


def capture(name, location, rotation, width, height, fov=75.0):
    """Capture via editor viewport + HighResShot (4.27 Python lacks
    TextureRenderTarget2DFactoryNew, so SceneCapture2D path is dead)."""
    cam_loc = unreal.Vector(*location)
    cam_rot = unreal.Rotator(*rotation)

    unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam_loc, cam_rot)

    # HighResShot writes to <Project>/Saved/Screenshots/Windows/<filename>.png
    cmd = 'HighResShot {0}x{1} filename="{2}"'.format(width, height, name)
    unreal.SystemLibrary.execute_console_command(
        unreal.EditorLevelLibrary.get_editor_world(), cmd
    )
    return name + ".png"


def collect_live_stats():
    actors = unreal.EditorLevelLibrary.get_all_level_actors()
    per_class = {}
    per_mesh = {}
    smc_count = 0
    xs = []; ys = []; zs = []
    for a in actors:
        cls = a.get_class().get_name()
        per_class[cls] = per_class.get(cls, 0) + 1
        try:
            loc = a.get_actor_location()
            xs.append(loc.x); ys.append(loc.y); zs.append(loc.z)
        except Exception:
            pass
        if cls == "StaticMeshActor":
            try:
                comp = a.static_mesh_component
                sm = comp.get_editor_property("static_mesh")
                if sm:
                    p = sm.get_path_name()
                    per_mesh[p] = per_mesh.get(p, 0) + 1
                    smc_count += 1
            except Exception:
                pass

    bounds = None
    if xs:
        bounds = {
            "min": [min(xs), min(ys), min(zs)],
            "max": [max(xs), max(ys), max(zs)],
        }
    return {
        "actor_count": len(actors),
        "static_mesh_component_count": smc_count,
        "per_class": per_class,
        "per_mesh_path": per_mesh,
        "bounds": bounds,
    }


def diff_counts(source_counts, live_counts):
    keys = set(source_counts.keys()) | set(live_counts.keys())
    rows = []
    for k in sorted(keys):
        s = source_counts.get(k, 0)
        l = live_counts.get(k, 0)
        rows.append({"key": k, "source": s, "vite": l, "delta": l - s})
    return rows


def main():
    started = time.time()
    _ensure_dirs()
    try:
        if os.path.exists(SIDECAR_LOG):
            os.remove(SIDECAR_LOG)
    except Exception:
        pass

    log("=== Pass 1 Validate START ===")
    log("Loading target map: " + TARGET_MAP)
    loaded = unreal.EditorLoadingAndSavingUtils.load_map(TARGET_MAP)
    # Workaround logged for posterity
    log("load result type: " + str(type(loaded).__name__))

    log("Reading source summary: " + SOURCE_SUMMARY)
    with open(SOURCE_SUMMARY, "r") as fh:
        source = json.load(fh)

    log("Collecting live stats...")
    live = collect_live_stats()
    log("live actors={0} smc={1}".format(live["actor_count"], live["static_mesh_component_count"]))

    log("Capturing screenshots...")
    # Need to leave the editor running long enough for HighResShot to render
    # and flush to disk before quit_editor is called.
    shots = []
    # Map bounds from source were X[-100,8100] Y[-7983,8000] Z[-100,3400]
    try:
        shots.append(capture("MAP_VITE_perspective",
                             location=(8500, 9500, 2200),
                             rotation=(-12, -130, 0),
                             width=2560, height=1440, fov=75))
    except Exception as exc:
        log("perspective shot failed: " + repr(exc))
    try:
        shots.append(capture("MAP_VITE_top",
                             location=(4000, 0, 6000),
                             rotation=(-89.5, 0, 0),
                             width=2560, height=2560, fov=90))
    except Exception as exc:
        log("top shot failed: " + repr(exc))
    try:
        shots.append(capture("MAP_VITE_side_Y",
                             location=(4000, -11500, 4000),
                             rotation=(-18, 90, 0),
                             width=2560, height=1440, fov=80))
    except Exception as exc:
        log("side_Y shot failed: " + repr(exc))

    report = {
        "schema": "pass1_validation_report.v1",
        "target_map": TARGET_MAP,
        "source_summary_path": SOURCE_SUMMARY,
        "source_actor_count": source.get("actor_count"),
        "source_static_mesh_component_count": source.get("static_mesh_component_count"),
        "live_actor_count": live["actor_count"],
        "live_static_mesh_component_count": live["static_mesh_component_count"],
        "live_bounds": live["bounds"],
        "class_diff": diff_counts(source.get("class_counts") or {}, live["per_class"]),
        "mesh_diff": diff_counts(source.get("mesh_counts") or {}, live["per_mesh_path"]),
        "screenshots": shots,
        "elapsed_seconds": round(time.time() - started, 2),
    }

    with open(REPORT_JSON, "w") as fh:
        json.dump(report, fh, indent=2)
    log("Report written: " + REPORT_JSON)

    # HighResShot is async — give the renderer a few seconds to flush PNGs
    # before we exit the editor.
    log("Waiting 8s for HighResShot renderer to flush PNGs...")
    time.sleep(8)
    log("Done.")

    try:
        unreal.SystemLibrary.quit_editor()
    except Exception:
        pass


try:
    main()
except Exception as exc:
    unreal.log_error("[Pass1Validate] FATAL " + repr(exc))
    _sidecar("FATAL " + repr(exc))
    raise
