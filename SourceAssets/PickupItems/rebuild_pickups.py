"""Rebuild pickup props with depth or surface defects in the VARCO reconstruction.

Run in Blender with --python rebuild_pickups.py -- OUTPUT_FOLDER ITEM.
The single-material GLB is input to prepare_models.py just like a VARCO source.
"""
import argparse
import math
import sys
from pathlib import Path

import bpy
import numpy as np


def make_atlas(out, key):
    # Clockwise from lower left: bookcloth, paper, graphite, brushed metal.
    colors = [(0.42, 0.50, 0.52), (0.86, 0.83, 0.74), (0.18, 0.19, 0.19), (0.66, 0.68, 0.67)]
    if key == 'DataShard':
        colors = [(0.31, 0.32, 0.32), (0.84, 0.69, 0.41), (0.16, 0.17, 0.17), (0.48, 0.50, 0.49)]
    if key == 'SampleCanister':
        colors = [(0.82, 0.81, 0.77), (0.96, 0.95, 0.90), (0.27, 0.44, 0.67), (0.55, 0.54, 0.52)]
    rng = np.random.default_rng(19)
    size = 512
    data = np.ones((size, size, 4), dtype=np.float32)
    half = size // 2
    for i, color in enumerate(colors):
        row, col = divmod(i, 2)
        grain = rng.normal(0, 0.012, (half, half, 1))
        if i in (0, 3):
            grain += rng.normal(0, 0.008, (half, 1, 1))
        tile = data[row*half:(row+1)*half, col*half:(col+1)*half]
        # Blender writes a linear generated image as sRGB when saving a color PNG.
        tile[:, :, :3] = np.clip(np.array(color) + grain, 0, 1) ** 2.2
    image = bpy.data.images.new('StationerySurface', width=size, height=size, alpha=False)
    image.pixels.foreach_set(data.ravel())
    image.filepath_raw = str(out / (key + '_Surface.png'))
    image.file_format = 'PNG'
    image.save()
    image = bpy.data.images.load(image.filepath_raw, check_existing=False)
    image.pack()
    mat = bpy.data.materials.new('Stationery')
    mat.use_nodes = True
    tree = mat.node_tree
    color = tree.nodes.new('ShaderNodeTexImage')
    color.image = image
    shader = tree.nodes.get('Principled BSDF')
    tree.links.new(color.outputs['Color'], shader.inputs['Base Color'])
    shader.inputs['Roughness'].default_value = 0.76
    return mat


def block(name, center, size, radius, tile, mat, segments=5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = obj.modifiers.new('Rounded edges', 'BEVEL')
    bevel.width = radius
    bevel.segments = segments
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    mesh = obj.data
    mesh.materials.append(mat)
    uv = mesh.uv_layers.active or mesh.uv_layers.new()
    for face in mesh.polygons:
        axis = max(range(3), key=lambda i: abs(face.normal[i]))
        a, b = [i for i in range(3) if i != axis]
        for loop in face.loop_indices:
            v = mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv = ((tile % 2 + 0.04 + 0.92*(v[a]/size[a]+0.5))/2,
                                (tile // 2 + 0.04 + 0.92*(v[b]/size[b]+0.5))/2)
    return obj


def folder(mat):
    block('Back cover', (0,0,.002), (.235,.32,.004), .0018, 0, mat)
    block('Page block', (.001,0,.009), (.224,.308,.011), .002, 1, mat)
    for i in range(4):
        block('Page edge', (.0014, .0002*(i%2), .0051+i*.0024),
              (.2245+.00035*(i%2), .3085+.0003*(i%3), .0006), .00028, 1, mat, 3)
    block('Front cover', (0,0,.016), (.235,.32,.0032), .0015, 0, mat)
    block('Fabric spine', (-.1156,0,.0093), (.008,.319,.018), .0034, 0, mat)
    block('Spine crease', (-.106,0,.01768), (.00065,.313,.00022), .00010, 2, mat, 2)
    block('Spine clasp', (-.115, .032,.0108), (.009,.026,.0172), .0024, 2, mat)
    block('Clasp face', (-.1115,.032,.0191), (.012,.023,.0018), .0008, 3, mat)
    block('Paper label', (.046,.098,.01778), (.082,.032,.00038), .00017, 1, mat)


def clipboard(mat):
    block('Fibreboard', (0,0,.0035), (.226,.32,.007), .0032, 2, mat)
    block('Sheets', (.0008,-.005,.009), (.210,.294,.0035), .0014, 1, mat)
    block('Metal clip foot', (0,.135,.0115), (.090,.027,.0038), .0018, 3, mat)
    block('Clip jaw', (0,.122,.0153), (.078,.008,.0055), .0024, 3, mat)
    for x in (-.035,.035):
        block('Spring arm', (x,.134,.017), (.004,.023,.004), .0018, 3, mat)
    block('Spring crossbar', (0,.144,.018), (.074,.004,.004), .0019, 3, mat)
    for x in (-.041,.041):
        block('Rubber grip', (x,.122,.0163), (.006,.010,.0055), .002, 2, mat)


def cartridge(mat):
    block('Rear shell', (0,0,.004), (.052,.068,.008), .0033, 2, mat)
    block('Front shell', (0,.0009,.009), (.051,.065,.006), .0025, 0, mat)
    block('Face plate', (0,.005,.012), (.043,.045,.0012), .00055, 2, mat)
    block('Contact recess', (0,-.028,.012), (.038,.007,.0012), .00055, 2, mat)
    for i in range(10):
        block('Contact', ((i-4.5)*.00335,-.028,.01265), (.0023,.0055,.00065), .00028, 1, mat, 3)
    for x in (-.021,.021):
        block('Rear locating rail', (x,0,.001), (.003,.052,.003), .00125, 0, mat)
    block('Rear panel', (0,0,.0003), (.033,.041,.001), .00045, 0, mat)


def turned_surface(name, profile, count, tile, mat, arc=math.tau):
    closed = arc == math.tau
    width = count if closed else count+1
    verts = []
    for z, radius, grooves in profile:
        for i in range(width):
            a = arc*i/count - arc/2
            r = radius + grooves*math.cos(a*48)
            verts.append((math.sin(a)*r, -math.cos(a)*r, z))
    faces = [(j*width+i, j*width+(i+1)%width, (j+1)*width+(i+1)%width, (j+1)*width+i)
             for j in range(len(profile)-1) for i in range(count)]
    if closed:
        faces += [tuple(reversed(range(width))),tuple(range((len(profile)-1)*width,len(profile)*width))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat)
    uv = mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth = len(face.vertices) == 4
        for loop in face.loop_indices:
            v = mesh.vertices[mesh.loops[loop].vertex_index]
            if len(face.vertices) == 4:
                u = (v.index%width)/count
                if closed and face.index%count == count-1 and u == 0:
                    u = 1
                y = (v.co.z-profile[0][0])/(profile[-1][0]-profile[0][0])
            else:
                u, y = .5+v.co.x/.09, .5+v.co.y/.09
            uv.data[loop].uv = ((tile%2+.04+.92*u)/2,(tile//2+.04+.92*y)/2)


def canister(mat):
    turned_surface('Sealed body', [(0,.035,0),(.001,.0375,0),(.003,.0395,0),
                   (.006,.040,0),(.102,.040,0),(.105,.0395,0),(.108,.036,0),
                   (.110,.036,0)], 112, 0, mat)
    turned_surface('Closure seal', [(.108,.0365,0),(.109,.038,0),(.1115,.038,0)],
                   96, 3, mat)
    turned_surface('Ribbed cap', [(.110,.038,0),(.1115,.040,0),(.114,.0402,.00025),
                   (.1265,.0402,.00025),(.1285,.040,0),(.130,.0385,0)],
                   192, 2, mat)
    turned_surface('Paper label', [(.033,.04009,0),(.088,.04009,0)], 48, 1, mat, 2.0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    builds = {'DocumentFolder': folder, 'Clipboard': clipboard, 'DataShard': cartridge, 'SampleCanister': canister}
    parser.add_argument('item', choices=builds.keys())
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    args.output.mkdir(parents=True, exist_ok=True)
    surface = make_atlas(args.output, args.item)
    builds[args.item](surface)
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    bpy.context.object.name = args.item
    bpy.ops.export_scene.gltf(filepath=str(args.output / (args.item+'.glb')), export_format='GLB',
                              export_yup=True, export_animations=False, use_selection=True)
