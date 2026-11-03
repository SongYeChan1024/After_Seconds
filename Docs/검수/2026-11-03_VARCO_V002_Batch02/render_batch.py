import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).parent
assets=json.loads((R/'batch_manifest.json').read_text(encoding='utf-8'))['assets']
for asset in assets:
    if not all((R/(asset['id']+'_'+mode+'.glb')).exists() for mode in ['high','low']):continue
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images]:
        for item in list(collection):
            if item.users==0:collection.remove(item)
    for i,mode in enumerate(['high','low']):
        before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/(asset['id']+'_'+mode+'.glb')))
        objects=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
        points=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
        lo=Vector(tuple(min(p[j] for p in points) for j in range(3)));hi=Vector(tuple(max(p[j] for p in points) for j in range(3)));center=(lo+hi)/2;scale=1.8/max(hi-lo)
        rotation=Matrix.Rotation(math.radians(-30),4,'Z')
        for o in objects:o.matrix_world=Matrix.Translation((i*2.6-1.3,0,0))@rotation@Matrix.Scale(scale,4)@Matrix.Translation(-center)@o.matrix_world
        bpy.ops.object.text_add(location=(i*2.6-2.4,-.5,-1.25),rotation=(math.pi/2,0,0))
        text=bpy.context.object;text.data.body=asset['id']+' '+('HIGH 500K' if mode=='high' else 'REMESH '+str(asset['budget']));text.data.size=.17
    bpy.ops.object.camera_add(location=(0,-10,4));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,-.1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=5.5
    scene=bpy.context.scene;scene.camera=camera;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1000;scene.render.resolution_y=650;scene.render.resolution_percentage=100
    shading=scene.display.shading;shading.light='STUDIO';shading.color_type='SINGLE';shading.single_color=(.58,.62,.65);shading.show_shadows=True;shading.show_cavity=True;shading.cavity_type='BOTH';shading.background_type='WORLD';scene.world.color=(.16,.16,.16)
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(R/(asset['id']+'_mesh_review.png'));bpy.ops.render.render(write_still=True)
    print('RENDERED',asset['id'],flush=True)
