import json
import os
import traceback

import unreal


MAP_PATH = "/Game/Maps/MAP_Main"
OUT_DIR = r"D:\PORTAGE_VITE\Pass0_SourceReference"
OUT_JSON = os.path.join(OUT_DIR, "MAP_Main_SourceVisual_v2.json")
OUT_SUMMARY = os.path.join(OUT_DIR, "MAP_Main_SourceVisual_v2_Summary.json")


def as_float(value):
    try:
        return float(value)
    except Exception:
        return None


def vec_to_list(value):
    return [as_float(value.x), as_float(value.y), as_float(value.z)]


def rot_to_list(value):
    return [as_float(value.roll), as_float(value.pitch), as_float(value.yaw)]


def quat_to_list(value):
    return [as_float(value.x), as_float(value.y), as_float(value.z), as_float(value.w)]


def transform_to_dict(value):
    return {
        "location": vec_to_list(value.translation),
        "rotation": rot_to_list(value.rotation.rotator()),
        "quat": quat_to_list(value.rotation),
        "scale": vec_to_list(value.scale3d),
    }


def transform_parts(location, rotation, scale):
    return {
        "location": vec_to_list(location),
        "rotation": rot_to_list(rotation),
        "quat": None,
        "scale": vec_to_list(scale),
    }


def asset_path(obj):
    if not obj:
        return ""
    try:
        return obj.get_path_name()
    except Exception:
        return ""


def get_prop(obj, name, default=None):
    try:
        return obj.get_editor_property(name)
    except Exception:
        return default


def set_prop(obj, name, value):
    try:
        obj.set_editor_property(name, value)
        return True
    except Exception:
        return False


def actor_components(actor, cls):
    try:
        return list(actor.get_components_by_class(cls))
    except Exception:
        return []


def component_bounds(comp):
    try:
        bounds = comp.bounds
        return {
            "origin": vec_to_list(bounds.origin),
            "box_extent": vec_to_list(bounds.box_extent),
            "sphere_radius": as_float(bounds.sphere_radius),
        }
    except Exception:
        return None


def actor_bounds(actor):
    try:
        origin, extent = actor.get_actor_bounds(False)
        return {
            "origin": vec_to_list(origin),
            "box_extent": vec_to_list(extent),
        }
    except Exception:
        return None


def component_mobility(comp):
    mobility = get_prop(comp, "mobility", None)
    try:
        return str(mobility)
    except Exception:
        return ""


def call_noarg(obj, names):
    for name in names:
        fn = getattr(obj, name, None)
        if fn:
            try:
                return fn()
            except Exception:
                pass
    return None


def component_relative_transform(comp):
    value = call_noarg(comp, ["get_relative_transform"])
    if value:
        try:
            return transform_to_dict(value)
        except Exception:
            pass

    location = call_noarg(comp, ["get_relative_location"]) or get_prop(comp, "relative_location", None)
    rotation = call_noarg(comp, ["get_relative_rotation"]) or get_prop(comp, "relative_rotation", None)
    scale = call_noarg(comp, ["get_relative_scale3d"]) or get_prop(comp, "relative_scale3d", None)
    if location and rotation and scale:
        return transform_parts(location, rotation, scale)
    return None


def component_world_transform(comp):
    value = call_noarg(comp, ["get_component_transform", "get_world_transform"])
    if value:
        try:
            return transform_to_dict(value)
        except Exception:
            pass

    value = get_prop(comp, "component_to_world", None)
    if value:
        try:
            return transform_to_dict(value)
        except Exception:
            pass

    location = call_noarg(comp, ["get_component_location", "get_world_location", "k2_get_component_location"])
    rotation = call_noarg(comp, ["get_component_rotation", "get_world_rotation", "k2_get_component_rotation"])
    scale = call_noarg(comp, ["get_component_scale", "get_world_scale", "k2_get_component_scale"])
    if location and rotation and scale:
        return transform_parts(location, rotation, scale)

    return component_relative_transform(comp)


def material_slots(comp):
    result = []
    try:
        count = comp.get_num_materials()
    except Exception:
        count = 0
    for index in range(count):
        try:
            mat = comp.get_material(index)
        except Exception:
            mat = None
        result.append({
            "slot": index,
            "material": asset_path(mat),
        })
    return result


def export_scene_component(comp):
    return {
        "name": comp.get_name(),
        "class": comp.get_class().get_name(),
        "path": comp.get_path_name(),
        "relative_transform": component_relative_transform(comp),
        "world_transform": component_world_transform(comp),
        "bounds": component_bounds(comp),
        "mobility": component_mobility(comp),
    }


def export_static_mesh_component(comp):
    data = export_scene_component(comp)
    mesh = get_prop(comp, "static_mesh", None)
    data.update({
        "mesh": asset_path(mesh),
        "materials": material_slots(comp),
        "collision_profile_name": str(get_prop(comp, "collision_profile_name", "")),
        "cast_shadow": bool(get_prop(comp, "cast_shadow", False)),
    })
    return data


def export_light_component(comp):
    data = export_scene_component(comp)
    for prop in [
        "intensity",
        "light_color",
        "attenuation_radius",
        "source_radius",
        "source_length",
        "inner_cone_angle",
        "outer_cone_angle",
        "cast_shadows",
        "use_temperature",
        "temperature",
    ]:
        value = get_prop(comp, prop, None)
        try:
            if hasattr(value, "r") and hasattr(value, "g") and hasattr(value, "b"):
                value = [int(value.r), int(value.g), int(value.b), int(value.a)]
        except Exception:
            pass
        try:
            json.dumps(value)
        except Exception:
            value = str(value)
        data[prop] = value
    return data


def export_audio_component(comp):
    data = export_scene_component(comp)
    data["sound"] = asset_path(get_prop(comp, "sound", None))
    data["volume_multiplier"] = as_float(get_prop(comp, "volume_multiplier", None))
    data["pitch_multiplier"] = as_float(get_prop(comp, "pitch_multiplier", None))
    return data


def export_post_process(actor):
    result = {}
    for prop in ["enabled", "unbound", "priority", "blend_radius", "blend_weight"]:
        value = get_prop(actor, prop, None)
        try:
            json.dumps(value)
        except Exception:
            value = str(value)
        result[prop] = value
    return result


def export_actor(actor):
    root = get_prop(actor, "root_component", None)
    entry = {
        "label": actor.get_actor_label(),
        "name": actor.get_name(),
        "class": actor.get_class().get_name(),
        "path": actor.get_path_name(),
        "folder_path": str(get_prop(actor, "folder_path", "")),
        "tags": [str(tag) for tag in list(get_prop(actor, "tags", []) or [])],
        "actor_transform": transform_to_dict(actor.get_actor_transform()),
        "actor_bounds": actor_bounds(actor),
        "root_component": export_scene_component(root) if root else None,
        "scene_components": [],
        "static_mesh_components": [],
        "light_components": [],
        "audio_components": [],
        "post_process": None,
    }

    for comp in actor_components(actor, unreal.SceneComponent):
        try:
            entry["scene_components"].append(export_scene_component(comp))
        except Exception:
            entry.setdefault("component_errors", []).append({
                "component": comp.get_path_name() if comp else "",
                "error": traceback.format_exc(),
            })

    for comp in actor_components(actor, unreal.StaticMeshComponent):
        entry["static_mesh_components"].append(export_static_mesh_component(comp))

    for cls_name in ["PointLightComponent", "DirectionalLightComponent", "SpotLightComponent", "SkyLightComponent"]:
        cls = getattr(unreal, cls_name, None)
        if cls:
            for comp in actor_components(actor, cls):
                entry["light_components"].append(export_light_component(comp))

    audio_cls = getattr(unreal, "AudioComponent", None)
    if audio_cls:
        for comp in actor_components(actor, audio_cls):
            entry["audio_components"].append(export_audio_component(comp))

    if entry["class"] == "PostProcessVolume":
        entry["post_process"] = export_post_process(actor)

    return entry


def summarize(data):
    class_counts = {}
    mesh_counts = {}
    material_counts = {}
    actor_bounds_min = [None, None, None]
    actor_bounds_max = [None, None, None]

    for actor in data["actors"]:
        class_counts[actor["class"]] = class_counts.get(actor["class"], 0) + 1
        bounds = actor.get("actor_bounds") or {}
        origin = bounds.get("origin")
        extent = bounds.get("box_extent")
        if origin and extent:
            for axis in range(3):
                low = origin[axis] - extent[axis]
                high = origin[axis] + extent[axis]
                actor_bounds_min[axis] = low if actor_bounds_min[axis] is None else min(actor_bounds_min[axis], low)
                actor_bounds_max[axis] = high if actor_bounds_max[axis] is None else max(actor_bounds_max[axis], high)
        for comp in actor.get("static_mesh_components", []):
            mesh = comp.get("mesh", "")
            mesh_counts[mesh] = mesh_counts.get(mesh, 0) + 1
            for slot in comp.get("materials", []):
                mat = slot.get("material", "")
                material_counts[mat] = material_counts.get(mat, 0) + 1

    return {
        "map": data["map"],
        "actor_count": len(data["actors"]),
        "component_count": sum(len(actor.get("scene_components", [])) for actor in data["actors"]),
        "static_mesh_component_count": sum(len(actor.get("static_mesh_components", [])) for actor in data["actors"]),
        "light_component_count": sum(len(actor.get("light_components", [])) for actor in data["actors"]),
        "audio_component_count": sum(len(actor.get("audio_components", [])) for actor in data["actors"]),
        "class_counts": dict(sorted(class_counts.items(), key=lambda item: (-item[1], item[0]))),
        "mesh_counts": dict(sorted(mesh_counts.items(), key=lambda item: (-item[1], item[0]))),
        "material_counts": dict(sorted(material_counts.items(), key=lambda item: (-item[1], item[0]))),
        "overall_actor_bounds": {
            "min": actor_bounds_min,
            "max": actor_bounds_max,
        },
        "errors": data["errors"],
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    unreal.log("Pass0 loading map: %s" % MAP_PATH)
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
    except Exception:
        unreal.log_warning("Map load reported errors; continuing with loaded world.")
        unreal.log_warning(traceback.format_exc())

    try:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
    except Exception:
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()

    data = {
        "schema": "pass0_source_visual_v2",
        "map": MAP_PATH,
        "actor_count_seen": len(actors),
        "actors": [],
        "errors": [],
    }

    for actor in actors:
        if not actor:
            continue
        try:
            data["actors"].append(export_actor(actor))
        except Exception:
            data["errors"].append({
                "actor": actor.get_path_name() if actor else "",
                "error": traceback.format_exc(),
            })

    summary = summarize(data)

    with open(OUT_JSON, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    with open(OUT_SUMMARY, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)

    unreal.log("Pass0 exported %d actors to %s" % (len(data["actors"]), OUT_JSON))
    unreal.log("Pass0 summary written to %s" % OUT_SUMMARY)


if __name__ == "__main__":
    main()
