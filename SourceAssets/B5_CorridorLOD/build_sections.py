"""Rebuild the segmented T11/T19 render meshes from their authored Blender parts.

Run with Blender 5.2 in background, passing the output directory after --.
The original colliders and the long floor, cable and drain surfaces span the corridor.
"""
import math
import sys
from collections import defaultdict
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

SOURCE = Path(__file__).resolve().parents[1] / "B5_RemainingDomes"
OUTPUT = Path(sys.argv[sys.argv.index("--") + 1])
SECTION_LENGTH = 12
CONTINUOUS = {"Resin_Floor", "Cable", "Drain_Back"}
FAR_DETAIL = {"Drain_Grate", "Tray_Hanger", "Tray_Rung", "Captive_Screw", "Vent_Louver"}


def build(corridor):
    name = f"RD_{corridor}_Finish"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE / (name + ".blend")))
    source = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    graph = bpy.context.evaluated_depsgraph_get()
    groups = defaultdict(list)
    collection = bpy.data.collections.new("LOD Export")
    bpy.context.scene.collection.children.link(collection)
    for obj in source:
        part = obj.name.split(".")[0]
        center = obj.matrix_world @ (sum((Vector(p) for p in obj.bound_box), Vector()) / 8)
        section = max(0, math.floor(abs(center.y) / SECTION_LENGTH))
        for tier in (("Fixed",) if part in CONTINUOUS else ("Near", "Mid", "Far")):
            if tier == "Far" and part in FAR_DETAIL:
                continue
            obj_eval = obj.evaluated_get(graph) if tier in {"Near", "Fixed"} else obj
            mesh = bpy.data.meshes.new_from_object(obj_eval, depsgraph=graph) if tier in {"Near", "Fixed"} else obj.data.copy()
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.dissolve_degenerate(bm, dist=1e-7, edges=list(bm.edges))
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bm.to_mesh(mesh)
            bm.free()
            mesh.transform(obj.matrix_world)
            out = bpy.data.objects.new("export part", mesh)
            collection.objects.link(out)
            key = "Spine" if tier == "Fixed" else f"S{section:02d}_{tier}"
            groups[key].append(out)

    result = []
    for key, parts in sorted(groups.items()):
        with bpy.context.temp_override(active_object=parts[0], selected_editable_objects=parts):
            if len(parts) > 1:
                bpy.ops.object.join()
        parts[0].name = corridor + "_" + key
        result.append(parts[0])
    bpy.ops.object.select_all(action="DESELECT")
    for obj in result:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = result[0]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.fbx(filepath=str(OUTPUT / (name + "_Sections.fbx")), use_selection=True,
                             object_types={"MESH"}, axis_forward="-Z", axis_up="Y", apply_unit_scale=True,
                             bake_space_transform=True, bake_anim=False, mesh_smooth_type="FACE")
    print(corridor, [(o.name, len(o.data.polygons)) for o in result], flush=True)


for corridor in ("T11", "T19"):
    build(corridor)

