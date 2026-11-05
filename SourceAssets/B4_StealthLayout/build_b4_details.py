import bpy
import json
import math
from pathlib import Path

SOURCE = Path(__file__).parent
REPOSITORY = SOURCE.parents[1]
MODEL = REPOSITORY / 'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/B4'
palette = json.loads((SOURCE/'architecture_manifest.json').read_text(encoding='utf-8'))['materials']
bpy.ops.wm.read_factory_settings(use_empty=True)
materials = {}
for name in ('Metal','Service','Clinical','Accent','Light'):
    material = bpy.data.materials.new('B4_'+name)
    material.diffuse_color = palette[name]
    materials[name] = material
objects = []

def box(name,u,height,v,width,rise,depth,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=(24-u,16-v,height))
    obj=bpy.context.object
    obj.name=name
    obj.scale=(width,depth,rise)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(materials[material])
    bevel=obj.modifiers.new('Manufactured_Bevel','BEVEL')
    bevel.width=min(0.008,min(width,rise,depth)*0.2)
    bevel.segments=2
    bevel.harden_normals=True
    normals=obj.modifiers.new('Weighted_Face_Normals','WEIGHTED_NORMAL')
    normals.keep_sharp=True
    for polygon in obj.data.polygons:
        polygon.use_smooth=True
    objects.append(obj)

for side in (-1,1):
    u=16+side*1.015
    for column in range(2):
        v=12.78+column*1.44
        box('RackDoor',u,1.2,v,0.035,2.02,1.34,'Metal')
        box('RackInset',u+side*0.024,1.35,v,0.018,1.55,1.13,'Service')
        for row in range(9):
            box('RackVent',u+side*0.038,0.52+row*0.13,v,0.012,0.025,0.92,'Metal')
        box('RackStatus',u+side*0.042,1.95,v-0.38,0.018,0.025,0.18,'Light')
        box('RackPull',u+side*0.06,1.16,v+0.47,0.055,0.25,0.035,'Clinical')
    for v in (12.03,14.97):
        box('RackEdge',u,1.15,v,0.06,2.28,0.06,'Metal')
for v in (12.0,15.0):
    box('RackEnd',16,1.15,v,1.94,2.24,0.04,'Metal')
    for row in range(11):
        box('RackEndVent',16,0.5+row*0.13,v+(-0.03 if v==12 else 0.03),1.55,0.035,0.018,'Service')

for u,width in ((30.3,2.28),(32.75,2.28)):
    for v in (14.98,20.02):
        box('DeckApronPanel',u,1.25,v,width,2.28,0.028,'Clinical')
        box('DeckApronStripe',u,2.12,v+(-0.018 if v<15 else 0.018),width,0.04,0.018,'Accent')
for index in range(4):
    v=15.625+index*1.25
    box('DeckEastPanel',34.02,1.25,v,0.028,2.28,1.1,'Clinical')
    box('DeckEastStripe',34.04,2.12,v,0.018,0.04,1.1,'Accent')
for u in (27.55,28.55):
    box('DeckLandingApron',u,1.25,20.02,0.88,2.28,0.028,'Clinical')

for u in (24.08,27.92):
    box('ConsoleEndCap',u,0.55,6,0.04,1.04,1.04,'Metal')
for side in (-1,1):
    v=6+side*0.52
    box('ConsoleSkirt',26,0.53,v,3.7,0.95,0.028,'Clinical')
    box('ConsoleStatusBand',26,0.96,v+side*0.02,3.62,0.025,0.018,'Accent')

for start,end in ((43.72,44.88),(46.62,47.78)):
    for height in (6.9,7.45):
        box('StairB_TopGuardrail',(start+end)/2,height,22.12,end-start,0.055,0.055,'Metal')
    for u in (start,end):
        box('StairB_TopGuardPost',u,6.92,22.12,0.055,1.04,0.055,'Metal')

bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'B4_ServiceDetails.blend'))
depsgraph=bpy.context.evaluated_depsgraph_get()
exports=[]
for material in materials:
    originals=[obj for obj in objects if obj.data.materials[0]==materials[material]]
    if not originals:
        continue
    baked=[]
    for original in originals:
        mesh=bpy.data.meshes.new_from_object(original.evaluated_get(depsgraph),depsgraph=depsgraph)
        obj=bpy.data.objects.new('Baked',mesh)
        obj.matrix_world=original.matrix_world.copy()
        bpy.context.scene.collection.objects.link(obj)
        baked.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in baked:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=baked[0]
    if len(baked)>1:
        bpy.ops.object.join()
    obj=bpy.context.object
    obj.name='B4_Detail_'+material+'_All'
    modifier=obj.modifiers.new('Explicit_Triangles','TRIANGULATE')
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    exports.append(obj)
bpy.ops.object.select_all(action='DESELECT')
for obj in exports:
    obj.select_set(True)
bpy.context.view_layer.objects.active=exports[0]
bpy.ops.export_scene.fbx(filepath=str(MODEL/'B4_ServiceDetails.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE')
report={'title':'B4 Service Details V0.01','author':'송예찬','sourceObjects':len(objects),'meshes':len(exports),'triangles':sum(len(obj.data.polygons) for obj in exports),'newColliders':0}
(SOURCE/'detail_manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
