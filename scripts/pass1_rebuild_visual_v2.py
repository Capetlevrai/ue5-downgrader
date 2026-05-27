"""
Pass 1 — Rebuild visual-only map in VITE (UE 4.27) from Pass 0 v2 export.

Reads:   D:/PORTAGE_VITE/Pass0_SourceReference/MAP_Main_SourceVisual_v2.json
Writes:  /Game/Maps/MAP_Main_VisualOnly_V2  (inside the VITE project)
Report:  D:/PORTAGE_VITE/Pass1_Output/pass1_rebuild_report.json

Strategy (per handoff CONTINUE_WITH_CLAUDE.md):
  * Reconstruct per *component world_transform*, not per actor transform.
  * Skip BP_Pistol_C / BP_AK47_C / BP_M4A1_C / BP_*SpawnPoint_C actors (gameplay = Pass 2+).
  * Skip lights/audio/post-process for now (Pass 1b).
  * No Downgrader plugin involvement.
  * Idempotent: deletes the target map if it already exists before rebuilding.

Invoke (commandlet, no UI):
  "D:/CLONE VITE UE5/Engine/Binaries/Win64/UE4Editor-Cmd.exe" ^
    "D:/PORTAGE_VITE/CounterStrike_VITE_From57_CoreOnly_NoDowngrader/CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject" ^
    -run=pythonscript ^
    -script="D:/PORTAGE_VITE/ue5-downgrader/scripts/pass1_rebuild_visual_v2.py" ^
    -stdout -unattended -nopause
"""
import json
import os
import sys
import time

import unreal


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EXPORT_JSON     = r"D:/PORTAGE_VITE/Pass0_SourceReference/MAP_Main_SourceVisual_v2.json"
TARGET_MAP_PATH = "/Game/Maps/MAP_Main_VisualOnly_V2"
REPORT_DIR      = r"D:/PORTAGE_VITE/Pass1_Output"
REPORT_JSON     = os.path.join(REPORT_DIR, "pass1_rebuild_report.json")
SIDECAR_LOG     = os.path.join(REPORT_DIR, "pass1_sidecar.log")


def _ensure_log_dir():
    if not os.path.isdir(REPORT_DIR):
        os.makedirs(REPORT_DIR)


def _sidecar(line):
    try:
        _ensure_log_dir()
        with open(SIDECAR_LOG, "a") as fh:
            fh.write("[{0}] {1}\n".format(time.strftime("%H:%M:%S"), line))
            fh.flush()
    except Exception:
        pass

BANNED_ACTOR_CLASSES = {
    "BP_Pistol_C",
    "BP_AK47_C",
    "BP_M4A1_C",
    "BP_CounterTerroristSpawnPoint_C",
    "BP_TerroristSpawnPoint_C",
}

# Default mesh used for missing assets — None means skip entirely.
PLACEHOLDER_MESH = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def log(msg):
    unreal.log("[Pass1] " + str(msg))
    _sidecar(str(msg))


def warn(msg):
    unreal.log_warning("[Pass1] " + str(msg))
    _sidecar("WARN: " + str(msg))


def err(msg):
    unreal.log_error("[Pass1] " + str(msg))
    _sidecar("ERR:  " + str(msg))


def vec(xyz):
    return unreal.Vector(float(xyz[0]), float(xyz[1]), float(xyz[2]))


def rot(rpy):
    # CRITICAL: pass0_export_visual_v2_ue57.py serializes as [roll, pitch, yaw]
    # (see rot_to_list at line 25-26 of that script), NOT [pitch, yaw, roll].
    # unreal.Rotator() constructor takes (pitch, yaw, roll) so we re-order.
    return unreal.Rotator(float(rpy[1]), float(rpy[2]), float(rpy[0]))


def load_asset(asset_path):
    if not asset_path:
        return None
    obj_path = asset_path
    if "." not in obj_path.rsplit("/", 1)[-1]:
        # convert /Game/Foo/Bar -> /Game/Foo/Bar.Bar
        obj_path = obj_path + "." + obj_path.rsplit("/", 1)[-1]
    return unreal.EditorAssetLibrary.load_asset(obj_path)


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


# ---------------------------------------------------------------------------
# Map prep
# ---------------------------------------------------------------------------
def reset_target_map():
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_MAP_PATH):
        log("Deleting existing target map: " + TARGET_MAP_PATH)
        unreal.EditorAssetLibrary.delete_asset(TARGET_MAP_PATH)

    log("Creating blank map in memory...")
    # 4.27 commandlet quirk: EditorLevelLibrary.new_level often returns False
    # without UI. EditorLoadingAndSavingUtils.new_blank_map gives a fresh
    # in-memory world we can populate, then save_map writes it to disk.
    world = unreal.EditorLoadingAndSavingUtils.new_blank_map(save_existing_map=False)
    if not world:
        raise RuntimeError("new_blank_map returned None")
    return world


def save_target_map(world):
    log("Saving map to: " + TARGET_MAP_PATH)
    ok = unreal.EditorLoadingAndSavingUtils.save_map(world, TARGET_MAP_PATH)
    if not ok:
        raise RuntimeError("save_map failed for " + TARGET_MAP_PATH)
    return ok


# ---------------------------------------------------------------------------
# Spawn loop
# ---------------------------------------------------------------------------
def spawn_components(world, actors):
    spawned = 0
    skipped_actor = 0
    skipped_missing_mesh = 0
    skipped_missing_mat = 0
    per_class = {}
    per_mesh = {}
    missing_meshes = {}
    missing_materials = {}
    errors = []

    sm_class = unreal.StaticMeshActor.static_class()

    for actor_entry in actors:
        actor_class = actor_entry.get("class", "")

        if actor_class in BANNED_ACTOR_CLASSES:
            skipped_actor += 1
            continue

        per_class[actor_class] = per_class.get(actor_class, 0) + 1

        smcs = actor_entry.get("static_mesh_components") or []
        if not smcs:
            continue

        actor_label = actor_entry.get("label") or actor_entry.get("name") or "Actor"

        for idx, smc in enumerate(smcs):
            mesh_path = smc.get("mesh")
            if not mesh_path:
                continue

            mesh_asset = load_asset(mesh_path)
            if not mesh_asset:
                skipped_missing_mesh += 1
                missing_meshes[mesh_path] = missing_meshes.get(mesh_path, 0) + 1
                if PLACEHOLDER_MESH is None:
                    continue
                mesh_asset = load_asset(PLACEHOLDER_MESH)
                if not mesh_asset:
                    continue

            wt = smc.get("world_transform") or {}
            loc = vec(wt.get("location", [0, 0, 0]))
            rotation = rot(wt.get("rotation", [0, 0, 0]))
            scale = vec(wt.get("scale", [1, 1, 1]))

            try:
                # 4.27 Python exposes only EditorLevelLibrary.spawn_actor_from_class
                # as a general spawn entry point (UWorld.spawn_actor and
                # GameplayStatics.begin_deferred_actor_spawn_from_class are NOT
                # exposed in 4.27). This call internally goes through
                # TryPlacingActorFromObject which null-derefs in -run=pythonscript
                # commandlet mode (no LevelEditorViewport client). The fix is to
                # run this script via the full UE4Editor.exe with
                # -ExecutePythonScript, NOT via UE4Editor-Cmd.exe -run=pythonscript.
                new_actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
                    sm_class, loc, rotation
                )
            except Exception as exc:
                errors.append({
                    "stage": "spawn",
                    "source_actor": actor_label,
                    "component": smc.get("name"),
                    "error": str(exc),
                })
                continue

            if not new_actor:
                errors.append({
                    "stage": "spawn",
                    "source_actor": actor_label,
                    "component": smc.get("name"),
                    "error": "begin/finish deferred spawn returned None",
                })
                continue

            label = "{0}__{1}".format(actor_label, smc.get("name", "SMC{0}".format(idx)))
            try:
                new_actor.set_actor_label(label)
            except Exception:
                pass

            try:
                new_actor.set_actor_scale3d(scale)
            except Exception as exc:
                errors.append({"stage": "scale", "actor": label, "error": str(exc)})

            smc_comp = new_actor.static_mesh_component
            try:
                smc_comp.set_static_mesh(mesh_asset)
            except Exception as exc:
                errors.append({
                    "stage": "set_mesh",
                    "actor": label,
                    "mesh": mesh_path,
                    "error": str(exc),
                })

            cast_shadow = smc.get("cast_shadow")
            if cast_shadow is not None:
                try:
                    smc_comp.set_editor_property("cast_shadow", bool(cast_shadow))
                except Exception:
                    pass

            coll = smc.get("collision_profile_name")
            if coll:
                try:
                    smc_comp.set_collision_profile_name(coll)
                except Exception:
                    pass

            for mat_entry in (smc.get("materials") or []):
                slot = int(mat_entry.get("slot", 0))
                mat_path = mat_entry.get("material")
                if not mat_path:
                    continue
                mat_asset = load_asset(mat_path)
                if not mat_asset:
                    skipped_missing_mat += 1
                    missing_materials[mat_path] = missing_materials.get(mat_path, 0) + 1
                    continue
                try:
                    smc_comp.set_material(slot, mat_asset)
                except Exception as exc:
                    errors.append({
                        "stage": "set_material",
                        "actor": label,
                        "slot": slot,
                        "material": mat_path,
                        "error": str(exc),
                    })

            spawned += 1
            per_mesh[mesh_path] = per_mesh.get(mesh_path, 0) + 1
            if spawned % 25 == 0:
                _sidecar("progress spawned={0}".format(spawned))

    return {
        "spawned_components": spawned,
        "skipped_actor_banned": skipped_actor,
        "skipped_missing_mesh": skipped_missing_mesh,
        "skipped_missing_material_slot": skipped_missing_mat,
        "per_source_class": per_class,
        "per_mesh_path": per_mesh,
        "missing_meshes": missing_meshes,
        "missing_materials": missing_materials,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    started = time.time()

    # Reset sidecar log for fresh run
    _ensure_log_dir()
    try:
        if os.path.exists(SIDECAR_LOG):
            os.remove(SIDECAR_LOG)
    except Exception:
        pass

    log("=== Pass 1 START ===")
    log("Reading export: " + EXPORT_JSON)
    with open(EXPORT_JSON, "r") as fh:
        data = json.load(fh)

    actors = data.get("actors") or []
    log("Source actor entries: {0}".format(len(actors)))

    world = reset_target_map()

    stats = spawn_components(world, actors)

    saved = save_target_map(world)
    log("Save result: " + str(saved))

    elapsed = round(time.time() - started, 2)

    report = {
        "schema": "pass1_rebuild_report.v1",
        "source_json": EXPORT_JSON,
        "target_map": TARGET_MAP_PATH,
        "source_actor_entries": len(actors),
        "save_ok": bool(saved),
        "elapsed_seconds": elapsed,
        "banned_actor_classes_skipped": sorted(BANNED_ACTOR_CLASSES),
    }
    report.update(stats)

    ensure_dir(REPORT_DIR)
    with open(REPORT_JSON, "w") as fh:
        json.dump(report, fh, indent=2)
    log("Report written: " + REPORT_JSON)
    log("Done in {0}s. Spawned={1} Missing meshes={2} Errors={3}".format(
        elapsed, stats["spawned_components"],
        len(stats["missing_meshes"]), len(stats["errors"])))

    # Auto-quit so the editor closes when invoked with -ExecutePythonScript
    try:
        unreal.SystemLibrary.quit_editor()
    except Exception:
        pass


try:
    main()
except Exception as exc:
    err("FATAL: " + repr(exc))
    raise
