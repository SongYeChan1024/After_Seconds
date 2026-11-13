"""Close the unintended grid gaps in the three intact 1F core roofs.

Author: 송예찬. Run in Blender; output is staged outside Unity for inspection.
Sequence: validate the three core dimensions; build one continuous slab with
the existing two kerbs; retain the original world-space UV scale, material and
object names; export only these three models and a bounded geometry report.
The damaged production/annex roofs and the original generator are not run.
"""

import json
import sys
from pathlib import Path

import bpy
import bmesh


ROOT = Path(__file__).resolve().parents[2]
CORE_IDS = ("VA", "VB", "VL")


def build(core, output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    material = bpy.data.materials.new("AE_M_Concrete")
    material.diffuse_color = (1, 1, 1, 1)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.86
    x, z, width, depth, height = (core[key] for key in ("x", "z", "w", "d", "h"))
    assert (width, depth) == (10, 10)
    assert height == (4.6 if core["id"] == "VL" else 4.2)
    boxes = [((x, height + .09, z), (width - .02, .18, depth - .02))]
    boxes += [((side, height + .28, z), (.14, .25, depth)) for side in (x-width/2, x+width/2)]
    for position, size in boxes:
        # Match F1_AbandonedCamouflage/common.py's Unity-to-Blender axes.
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-position[0], -position[2], position[1]))
        obj = bpy.context.object
        obj.dimensions = (size[0], size[2], size[1])
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.data.materials.append(material)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = obj.data.name = "AE_" + core["id"] + "_Roof"
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    mesh = obj.data
    mesh.update()
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    for face in mesh.polygons:
        axes = [axis for axis in range(3) if axis != max(range(3), key=lambda axis: abs(face.normal[axis]))]
        for loop in face.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop].vertex_index].co
            mesh.uv_layers.active.data[loop].uv = (vertex[axes[0]]/2, vertex[axes[1]]/2)
    assert len(mesh.polygons) == 36 and all(face.area > 1e-7 for face in mesh.polygons)
    asset = output / (obj.name + ".fbx")
    bpy.ops.export_scene.fbx(filepath=str(asset), use_selection=True, object_types={"MESH"},
        axis_forward="-Z", axis_up="Y", apply_unit_scale=True, bake_space_transform=True,
        bake_anim=False, mesh_smooth_type="FACE")
    points = [(-v.co.x, v.co.z, -v.co.y) for v in mesh.vertices]
    return {"core":core["id"], "file":asset.name, "triangles":len(mesh.polygons),
        "min":[min(p[i] for p in points) for i in range(3)],
        "max":[max(p[i] for p in points) for i in range(3)],
        "material":material.name, "slabCount":1, "kerbCount":2, "gapMetresBefore":.02}


if __name__ == "__main__":
    output = Path(sys.argv[sys.argv.index("--")+1]).resolve()
    unity = (ROOT / "Unity").resolve()
    assert not output.is_relative_to(unity), "Stage outside Unity before applying."
    output.mkdir(parents=True, exist_ok=True)
    site = json.loads((ROOT / "SourceAssets/F1_AbandonedCamouflage/site.json").read_text(encoding="utf-8"))
    cores = {room["id"]:room for room in site["rooms"] if room["id"] in CORE_IDS}
    report = [build(cores[key], output) for key in CORE_IDS]
    (output / "geometry.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False), flush=True)
