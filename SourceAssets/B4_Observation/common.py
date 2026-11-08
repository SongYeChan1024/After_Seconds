"""Local art authoring helpers, metres, Unity front +Z. Author 송예찬."""
import ast,bpy,bmesh,math,json,os
from pathlib import Path
from mathutils import Vector,Matrix
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model'
manifest=json.loads((H/'models.json').read_text(encoding='utf-8')) if (H/'models.json').exists() else {}
for rel in ['CircularDressing/build_environment.py','C02_Security/build.py','B5_RemainingDomes/build.py']:
 tree=ast.parse((R/'SourceAssets'/rel).read_text(encoding='utf-8'))
 nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name not in ['reset','export','apply_subset']]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),rel,'exec'))
tree=ast.parse((R/'SourceAssets/CircularDressing/build_environment.py').read_text(encoding='utf-8'))
src=ast.unparse(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='export')).replace('obj.name = name','obj.name = name\n    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)').replace('for p in o.data.polygons:',"if o.get('display_uv'): continue\n        for p in o.data.polygons:")
exec(src);raw_export=export

def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;bpy.context.scene.unit_settings.system='METRIC'
 global mats;mats={}
 specs=[('Coat',(.26,.275,.29,1),.08,.57),('Steel',(.18,.20,.22,1),.75,.38),('Dark',(.024,.028,.033,1),.1,.55),('Rubber',(.015,.018,.022,1),0,.8),('Teal',(.22,.26,.28,1),.35,.45),('Fabric',(.11,.12,.13,1),0,.88),('Glass',(.38,.43,.46,.14),.02,.14),('Indicator',(.37,.64,.51,1),0,.3),('Paper',(.74,.75,.72,1),0,.85),('Lamp',(.85,.87,.89,1),0,.25),('Floor',(.16,.17,.19,1),.03,.7),('Warm',(.40,.34,.24,1),.1,.6),('Red',(.45,.12,.10,1),.05,.58),('Hazard',(.63,.51,.27,1),.05,.65),('Mark',(.52,.55,.57,1),.03,.73),('Lens',(.04,.10,.13,1),.55,.12)]
 specs += [(f'Display_{i:02}',(.12,.14,.17,1),0,.24) for i in range(1,7)]
 for n,c,metal,rough in specs:
  m=bpy.data.materials.new('B4O_'+n);m.diffuse_color=c;m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=c;p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;mats[n]=m

def save(name,category='Environment'):
 global OUT;OUT=A/category/'B4';raw_export('BO_'+name);manifest['BO_'+name]['category']=category
 (H/'models.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

def transform(objects,x,y,z,yaw):
 m=Matrix.Translation(Vector(xyz(x,y,z)))@Matrix.Rotation(-math.radians(yaw),4,'Z')
 for o in objects:o.matrix_world=m@o.matrix_world

def sector(name,ri,ro,y0,y1,a0,a1,mat='Steel',segments=16,bev=.005):
 vs=[]
 for y in [y0,y1]:
  for r in [ri,ro]:
   for i in range(segments+1):
    a=math.radians(a0+(a1-a0)*i/segments);vs.append((r*math.cos(a),y,r*math.sin(a)))
 n=segments+1;fs=[]
 for i in range(segments):fs.extend([(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),(i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
 fs.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
 return mesh(name,vs,fs,mat,bev)

def ringtube(name,r,y,a0,a1,th=.025,mat='Steel'):
 tube(name,[(r*math.cos(math.radians(a0+(a1-a0)*i/80)),y,r*math.sin(math.radians(a0+(a1-a0)*i/80))) for i in range(81)],th,mat)

def print_panel(n,x,y,z,w,h,kind=6):
 ob=mesh(n,[(x-w/2,y-h/2,z),(x+w/2,y-h/2,z),(x+w/2,y+h/2,z),(x-w/2,y+h/2,z)],[(0,3,2,1)],f'Display_{kind:02}',0)
 if ob.data.polygons[0].normal.y>0:ob.data.flip_normals()
 uv=ob.data.uv_layers.new(name='UVMap');coords=[(1,0),(0,0),(0,1),(1,1)]
 for p in ob.data.polygons:
  for li in p.loop_indices:uv.data[li].uv=coords[ob.data.loops[li].vertex_index]
 ob['display_uv']=True;return ob
