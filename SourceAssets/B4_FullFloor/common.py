import sys,importlib.util,json,math,ast,bpy,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1]
spec=importlib.util.spec_from_file_location('b4_art_helpers',R/'SourceAssets/B4_Observation/common.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
box=b.box;cyl=b.cyl;mesh=b.mesh;tube=b.tube;sector=b.sector;ringtube=b.ringtube;display=b.display;monitor_stand=b.monitor_stand;keyboard=b.keyboard;pull=b.pull;vent=b.vent;bolt=b.bolt;feet=b.feet;cabinet=b.cabinet;transform=b.transform;sphere_patch=b.sphere_patch;xyz=b.xyz;arc=b.arc
def reset():
 b.reset()
 for i in range(7,23):
  m=bpy.data.materials.new(f'BF_Display_{i:02}');m.diffuse_color=(.14,.18,.20,1);b.mats[f'Display_{i:02}']=m
def save(name,category='Environment'):
 import os
 if os.environ.get('BF_ONLY') and name!=os.environ['BF_ONLY']:return
 b.OUT=b.A/category/'B4';b.raw_export('BF_'+name);b.manifest['BF_'+name]['category']=category
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf-8')
tree=ast.parse((R/'SourceAssets/CircularFacility/build_geometry.py').read_text(encoding='utf-8'));env={'bpy':bpy,'bmesh':bmesh,'math':math,'Vector':Vector}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'shell_helpers','exec'),env)
def shell_mats():env['mats']={'Shell':b.mats['Coat'],'Floor':b.mats['Floor'],'Steel':b.mats['Steel']}
def cut(o,c):env['boolean'](o,c);bpy.data.objects.remove(c,do_unlink=True)
