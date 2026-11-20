"""Convert VARCO pickup GLBs to metric FBXs and render front/back review views.

Run Blender in background with --python prepare_models.py -- STAGING ITEM [ITEM ...].
The staging folder holds export candidates until visual review is complete.
"""
import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector


SOURCE = Path(__file__).resolve().parent
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))
previous_bytecode_setting = sys.dont_write_bytecode
sys.dont_write_bytecode = True
import refine_pickups
sys.dont_write_bytecode = previous_bytecode_setting

SPECS = {r["id"]: r for r in json.loads((SOURCE / "varco_requests.json").read_text("utf-8"))["items"]}


def image_source(socket):
    if not socket.is_linked:
        return None
    node = socket.links[0].from_node
    if node.type == 'NORMAL_MAP':
        return image_source(node.inputs['Color'])
    return node.image if node.type == 'TEX_IMAGE' else None


def export_textures(obj, dest, prefix):
    if len(obj.data.materials) != 1:
        raise ValueError(f"Expected one VARCO material on {obj.name}, found {len(obj.data.materials)}")
    mat = obj.data.materials[0]
    mat.name = prefix
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    result = {}
    for slot, suffix in [('Base Color', 'Albedo'), ('Normal', 'Normal')]:
        image = image_source(bsdf.inputs[slot])
        if image is None:
            if suffix == 'Albedo':
                raise ValueError(f"Missing albedo on {prefix}")
            continue
        if not image.packed_file:
            raise ValueError(f"Missing embedded image on {prefix}")
        out = dest / f"{prefix}_{suffix}.png"
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-v', 'error', '-threads', '1', '-i', 'pipe:0',
                        '-vf', 'scale=1024:1024:flags=lanczos', '-frames:v', '1', '-threads', '1',
                        str(out)], input=image.packed_file.data, check=True)
        result[suffix] = out.name
    return result


def take_views(obj, dest, key, end_views=False):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 6 if end_views else 3
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 480 if end_views else 384
    scene.render.resolution_y = 400 if end_views else 320
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = 91
    world = bpy.data.worlds.new('Review world')
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (0.35, 0.38, 0.42, 1)
    bg.inputs['Strength'].default_value = 0.85
    center = Vector(tuple((max(v.co[i] for v in obj.data.vertices) + min(v.co[i] for v in obj.data.vertices)) / 2 for i in range(3)))
    span = max(obj.dimensions)
    for offset, energy in [((2,-3,4),150),((-3,2,2),110),((0,1,-3),55)]:
        light = bpy.data.lights.new('Softbox', 'AREA')
        light.energy = energy * span * span
        light.shape = 'DISK'
        light.size = 2.8 * span
        lamp = bpy.data.objects.new('Softbox', light)
        scene.collection.objects.link(lamp)
        lamp.location = center + Vector(offset) * span
        lamp.rotation_euler = (center-lamp.location).to_track_quat('-Z','Y').to_euler()
    cam = bpy.data.cameras.new('Review')
    camera = bpy.data.objects.new('Review', cam)
    scene.collection.objects.link(camera)
    scene.camera = camera
    cam.type = 'ORTHO'
    cam.clip_start = 0.001
    axes = sorted(range(3), key=lambda i: obj.dimensions[i])
    if end_views:
        coords = np.asarray([list(v.co) for v in obj.data.vertices])
        _, basis = np.linalg.eigh(np.cov(coords.T))
    for name, sign in ([('C', 1), ('D', -1)] if end_views else [('A', 1), ('B', -1)]):
        direction = Vector((0,0,0))
        for axis, weight in zip(axes, [1.35, 0.68, 0.33]):
            direction[axis] = weight * (-1 if axis == 1 else 1)
        direction[axes[0]] *= sign
        direction[axes[2]] *= sign
        if end_views:
            direction = Vector(basis[:, 2]*sign + basis[:, 1]*.34 + basis[:, 0]*.22*sign)
        camera.location = center + direction.normalized() * span * 3
        rotation = (center-camera.location).to_track_quat('-Z','Y')
        camera.rotation_euler = rotation.to_euler()
        inv = rotation.inverted()
        projected = [inv @ (v.co-center) for v in obj.data.vertices]
        low = [min(p[i] for p in projected) for i in (0,1)]
        high = [max(p[i] for p in projected) for i in (0,1)]
        camera.location += rotation @ Vector(((low[0]+high[0])/2, (low[1]+high[1])/2,0))
        cam.ortho_scale = 1.12 * max(high[0]-low[0], (high[1]-low[1]) * 384/320)
        scene.render.filepath = str(dest / f"{key}_{name}.jpg")
        bpy.ops.render.render(write_still=True)


def prepare(spec, stage):
    key = spec['id']
    prefix = 'Pickup_' + key
    out = stage / key
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source_root = Path(os.environ.get('PICKUP_SOURCE_DIR', str(SOURCE)))
    bpy.ops.import_scene.gltf(filepath=str(source_root / 'Models' / (key + '.glb')))
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select_set(True)
    obj = objects[0]
    bpy.context.view_layer.objects.active = obj
    if len(objects)>1:
        bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.name = prefix
    obj.data.name = prefix
    # Merge coincident position seams. Blender stores texture UVs per face corner.
    mesh = obj.data
    source_triangles = len(mesh.polygons)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.000001)
    bm.to_mesh(mesh)
    bm.free()
    mod = obj.modifiers.new('Triangle budget', 'DECIMATE')
    mod.ratio = min(1, spec['triangleBudget'] / max(1, len(mesh.polygons)))
    mod.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=0.0000001)
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    bounds = [(min(v.co[i] for v in mesh.vertices), max(v.co[i] for v in mesh.vertices)) for i in range(3)]
    largest = max(b-a for a,b in bounds)
    factor = spec['longestMeters'] / largest
    origin = Vector(((bounds[0][0]+bounds[0][1])/2, (bounds[1][0]+bounds[1][1])/2, bounds[2][0]))
    for vertex in mesh.vertices:
        vertex.co = (vertex.co-origin)*factor
    mesh.update()
    atlas_strip = refine_pickups.refine(obj,key)
    if atlas_strip or key in refine_pickups.LOOSE:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=spec['longestMeters']*1e-7)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=spec['longestMeters']*1e-8)
        bm.normal_update()
        bm.to_mesh(obj.data)
        bm.free()
        if len(obj.data.polygons)>spec['triangleBudget']:
            mod=obj.modifiers.new('Final pickup budget','DECIMATE')
            mod.ratio=spec['triangleBudget']/len(obj.data.polygons)
            mod.use_collapse_triangulate=True
            bpy.ops.object.modifier_apply(modifier=mod.name)
        mesh=obj.data
        bounds=[(min(v.co[i] for v in mesh.vertices),max(v.co[i] for v in mesh.vertices)) for i in range(3)]
        factor=spec['longestMeters']/max(b-a for a,b in bounds)
        origin=Vector(((bounds[0][0]+bounds[0][1])/2,(bounds[1][0]+bounds[1][1])/2,bounds[2][0]))
        for v in mesh.vertices:
            v.co=(v.co-origin)*factor
        mesh.update()
    bpy.context.view_layer.update()
    mesh.calc_loop_triangles()
    triangles = len(mesh.loop_triangles)
    if not mesh.uv_layers.active or triangles < 500 or triangles > spec['triangleBudget']+30:
        raise ValueError(f"Unexpected geometry/UVs for {key}: {triangles}")
    textures = export_textures(obj,out,prefix)
    if atlas_strip:
        if key in refine_pickups.REBUILDS:
            refine_pickups.forged_atlas(out, prefix, key)
            textures['MetallicGloss']=prefix+'_MetallicGloss.png'
        else:
            for role, filename in textures.items():
                refine_pickups.pack_strip(out / filename, role=='Normal')
        shader=next(n for n in obj.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        for slot,suffix in [('Base Color','Albedo'),('Normal','Normal')]:
            if suffix in textures:
                socket=shader.inputs[slot]
                node=socket.links[0].from_node
                if node.type=='NORMAL_MAP':
                    node=node.inputs['Color'].links[0].from_node
                node.image=bpy.data.images.load(str(out/textures[suffix]),check_existing=False)
                if suffix=='Normal':
                    node.image.colorspace_settings.name='Non-Color'
    if spec.get('surface'):
        material=obj.data.materials[0]
        shader=next(n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        shader.inputs['Metallic'].default_value=spec['surface']['metallic']
        shader.inputs['Roughness'].default_value=spec['surface']['roughness']
        if 'MetallicGloss' in textures:
            bind_packed(material,out / textures['MetallicGloss'])
    object_types={'MESH'}
    if key=='Pistol':
        object_types.add('EMPTY')
        for name, coords in refine_pickups.PISTOL_MARKERS.items():
            marker=bpy.data.objects.new(name,None)
            bpy.context.collection.objects.link(marker)
            marker.parent=obj
            marker.location=(Vector(coords)-origin)*factor
            marker.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(out/(prefix+'.fbx')),use_selection=True,
                             object_types=object_types, axis_forward='-Z',axis_up='Y',
                             apply_unit_scale=True,bake_space_transform=True,
                             bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE',path_mode='STRIP')
    take_views(obj,out,key)
    report = dict(id=key,sourceTriangles=source_triangles,triangles=triangles,
                  vertices=len(mesh.vertices),dimensionsBlender=list(obj.dimensions),
                  textures=textures,model=prefix+'.fbx')
    (out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('PICKUP_READY', key, triangles, flush=True)


def bind_packed(material, path):
    tree=material.node_tree
    shader=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED')
    tex=tree.nodes.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(path),check_existing=False)
    tex.image.colorspace_settings.name='Non-Color'
    tex.image.alpha_mode='CHANNEL_PACKED'
    split=tree.nodes.new('ShaderNodeSeparateColor')
    tree.links.new(tex.outputs['Color'],split.inputs['Color'])
    tree.links.new(split.outputs['Red'],shader.inputs['Metallic'])
    invert=tree.nodes.new('ShaderNodeMath')
    invert.operation='SUBTRACT'
    invert.inputs[0].default_value=1
    tree.links.new(tex.outputs['Alpha'],invert.inputs[1])
    tree.links.new(invert.outputs[0],shader.inputs['Roughness'])


def review_export(spec, stage, unity_root, end_views=False):
    """Photograph the shipped FBX and its actual 1K textures."""
    key = spec['id']
    prefix = 'Pickup_' + key
    folder = unity_root / 'Assets/Afrer_Seconds/05.Model/Props' / spec['modelFolder']
    out = stage / key
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(folder / (prefix+'.fbx')), use_image_search=False)
    obj, = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    material = bpy.data.materials.new(prefix+' review')
    material.use_nodes = True
    obj.data.materials.clear()
    obj.data.materials.append(material)
    tree = material.node_tree
    shader = tree.nodes.get('Principled BSDF')
    settings = json.loads((stage / 'plan.json').read_text('utf-8'))
    item = next(entry for entry in settings if entry['id'] == key)
    shader.inputs['Roughness'].default_value = item['roughness']
    shader.inputs['Metallic'].default_value = item['metallic']
    if item.get('metallicGloss'):
        bind_packed(material,unity_root / item['metallicGloss'])
    color = tree.nodes.new('ShaderNodeTexImage')
    color.image = bpy.data.images.load(str(unity_root / item['albedo']))
    tree.links.new(color.outputs['Color'], shader.inputs['Base Color'])
    if item['normal']:
        tex = tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(unity_root / item['normal']))
        tex.image.colorspace_settings.name = 'Non-Color'
        normal = tree.nodes.new('ShaderNodeNormalMap')
        tree.links.new(tex.outputs['Color'], normal.inputs['Color'])
        tree.links.new(normal.outputs['Normal'], shader.inputs['Normal'])
    take_views(obj, out, key, end_views)
    if end_views:
        geometry = bmesh.new()
        geometry.from_mesh(obj.data)
        bmesh.ops.remove_doubles(geometry, verts=list(geometry.verts), dist=max(obj.dimensions)*1e-6)
        pending = set(geometry.faces)
        islands = []
        while pending:
            stack = [pending.pop()]
            faces = []
            while stack:
                face = stack.pop()
                faces.append(face)
                for edge in face.edges:
                    for adjacent in edge.link_faces:
                        if adjacent in pending:
                            pending.remove(adjacent)
                            stack.append(adjacent)
            points = np.array([list(v.co) for v in {v for f in faces for v in f.verts}])
            islands.append(dict(faces=len(faces), area=sum(f.calc_area() for f in faces),
                                low=points.min(axis=0).tolist(), high=points.max(axis=0).tolist()))
        stats = dict(islands=sorted(islands, key=lambda x: -x['area']),
                     boundaryEdges=sum(e.is_boundary for e in geometry.edges),
                     zeroArea=sum(f.calc_area() < 1e-12*max(obj.dimensions)**2 for f in geometry.faces))
        geometry.free()
        (out/'geometry.json').write_text(json.dumps(stats), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage',type=Path)
    parser.add_argument('items',nargs='+',choices=SPECS.keys())
    parser.add_argument('--review-unity-export', type=Path)
    parser.add_argument('--end-views', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    for item in args.items:
        if args.review_unity_export:
            review_export(SPECS[item], args.stage.resolve(), args.review_unity_export.resolve(), args.end_views)
        else:
            prepare(SPECS[item],args.stage.resolve())

