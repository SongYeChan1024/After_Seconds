import sys,math,json,bpy,bmesh,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1]
spec=importlib.util.spec_from_file_location('remaining_build',R/'SourceAssets/B5_RemainingDomes/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.H=H;b.manifest=json.loads((H/'models.json').read_text()) if (H/'models.json').exists() else {}
box=b.box;tube=b.tube;mesh=b.mesh;xyz=b.xyz;bolt=b.bolt
def smooth_round(o):
 if o.type=='MESH' and len([p for p in o.data.polygons if len(p.vertices)>4])==2:
  for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
def cyl(*args,**kw):
 o=b.cyl(*args,**kw);smooth_round(o);return o
def materials():
 for n,c in [('Coat',(.65,.71,.72,1)),('Steel',(.36,.43,.47,1)),('Dark',(.026,.04,.05,1)),('Rubber',(.016,.022,.025,1)),('Teal',(.08,.24,.26,1)),('Fabric',(.38,.46,.47,1)),('Glass',(.08,.18,.20,.18)),('Indicator',(.19,.67,.48,1)),('Paper',(.74,.76,.70,1)),('Lamp',(.75,.85,.88,1)),('Floor',(.23,.28,.3,1)),('Warm',(.55,.45,.29,1)),('Red',(.47,.13,.1,1)),('Hazard',(.77,.62,.21,1))]:
  if n in b.mats:continue
  m=bpy.data.materials.get('RD_'+n) or bpy.data.materials.new('RD_'+n);m.diffuse_color=c;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;b.mats[n]=m
 for n,c,metal,rough in [('Accent',(.13,.28,.33,1),.25,.48),('WarmAccent',(.43,.36,.24,1),.1,.54),('Blue',(.13,.20,.29,1),.25,.43),('Frost',(.31,.45,.47,.35),.02,.3),('Window',(.16,.30,.34,.13),.03,.18),('Gasket',(.016,.024,.03,1),0,.72),('Label',(.9,.95,1,1),0,.7),('FloorZone',(.14,.21,.24,1),.03,.62)]:
  m=bpy.data.materials.get('SF_'+n) or bpy.data.materials.new('SF_'+n);m.diffuse_color=c;m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=c;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;b.mats[n]=m
def reset():b.reset();materials()
def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.preferences.filepaths.save_version=0
 for o in bpy.context.scene.objects:smooth_round(o)
 b.mats={m.name.split('_',1)[1]:m for m in bpy.data.materials if m.name.startswith(('RD_','SC_','SR_'))};materials()
def save(name,category='Environment'):
 b.OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model'/category/'B5';b.raw_export(name);b.manifest[name]['category']=category;(H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf-8')
def transform(objects,x,z,yaw,y=0):
 m=Matrix.Translation(Vector(xyz(x,y,z)))@Matrix.Rotation(-math.radians(yaw),4,'Z')
 for o in objects:o.matrix_world=m@o.matrix_world
def label(x,y,z,w,h,index):
 o=mesh('Flush_Equipment_Print',[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)],[(0,3,2,1)],'Label',0)
 if o.data.polygons[0].normal.y>0:o.data.flip_normals()
 uv=o.data.uv_layers.new(name='UVMap');u=(index%8)/8;v=1-(index//8+1)/8
 coords=[(u+.124,v+.001),(u+.001,v+.001),(u+.001,v+.124),(u+.124,v+.124)]
 for p in o.data.polygons:
  for li in p.loop_indices:uv.data[li].uv=coords[o.data.loops[li].vertex_index]
 o['display_uv']=True;return o
def flange(x,y,z,r=.1):
 cyl('Flange',(x,y,z-.018),(x,y,z+.018),r,'Steel',24)
 for i in range(8):a=i*math.tau/8;cyl('Captive_Hex_Bolt',(x+r*.78*math.cos(a),y+r*.78*math.sin(a),z+.018),(x+r*.78*math.cos(a),y+r*.78*math.sin(a),z+.032),r*.075,'Steel',6)
def wheel(x,y,z,r=.1):
 tube('Valve_Handwheel',[(x+r*math.cos(i*math.tau/32),y+r*math.sin(i*math.tau/32),z) for i in range(33)],.009,'Red')
 for i in range(3):a=i*math.tau/3;cyl('Handwheel_Spoke',(x,y,z),(x+r*math.cos(a),y+r*math.sin(a),z),.007,'Steel',8)
