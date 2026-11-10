"""Reuse the beveled bench, clear its parts tray for a real motor workpiece."""
import sys,json,bpy
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent;b.H=H;b.manifest=json.loads((H/'models.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/'SourceAssets/B2_Cooling/BC_MaintenanceBench.blend'))
for ob in list(bpy.context.scene.objects):
 if ob.name.startswith(('PartsTray','TrayEdge','SealRing','SealCenter','LooseBolt')):bpy.data.objects.remove(ob,do_unlink=True)
b.OUT=b.A/'Props/B2';b.raw_export('BO_MotorServiceBench');b.manifest['BO_MotorServiceBench']['category']='Props'
ob=bpy.context.object;m=ob.modifiers.new('DistanceSimplification','DECIMATE');m.ratio=.4;m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name);ob.name='BO_MotorServiceBench_LOD1'
bpy.ops.export_scene.fbx(filepath=str(b.OUT/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
b.manifest[ob.name]={'triangles':len(ob.data.polygons),'category':'Props','distance_only':True}
(H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
