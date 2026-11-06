import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
H=Path(__file__).resolve().parent;R=H.parents[1];OUT=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment/Common'
manifest={}
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
 global mats;mats={}
 for n,c,m,s in [('Coat',(.58,.67,.71,1),.08,.44),('Steel',(.32,.36,.4,1),.9,.3),('Dark',(.05,.065,.075,1),.1,.65),('Lamp',(.7,.85,1,1),0,.4)]:
  a=bpy.data.materials.new('CFD_'+n);a.use_nodes=True;a.diffuse_color=c;a.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=c;a.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=m;a.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=s;mats[n]=a
def xyz(x,y,z):return (-x,-z,y)
def mesh(n,vs,fs,mat='Steel',bev=.003,smooth=False):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(*v) for v in vs],[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(mats[mat]);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=smooth
 if bev:
  b=o.modifiers.new('Manufactured_Bevel','BEVEL');b.width=bev;b.segments=3;b.limit_method='ANGLE';b.angle_limit=.48;b.harden_normals=True
  w=o.modifiers.new('Weighted_Normal','WEIGHTED_NORMAL');w.keep_sharp=True
 o['bevel_width_m']=bev;return o
def box(n,x,y,z,w,h,d,mat='Steel',bev=.003):
 vs=[(x+dx*w/2,y+dy*h/2,z+dz*d/2) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
 return mesh(n,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,min(bev,min(w,h,d)*.22))
def cyl(n,a,b,r,mat='Steel',verts=16):
 aa=Vector(xyz(*a));bb=Vector(xyz(*b));v=bb-aa;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=v.length,location=(aa+bb)/2);o=bpy.context.object;o.name=n;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);o.data.materials.append(mats[mat]);be=o.modifiers.new('Edge_Bevel','BEVEL');be.width=min(.002,r*.15);be.segments=2;o['bevel_width_m']=be.width;return o
def bolt(x,y,z):return cyl('Fastener',(x,y,z),(x,y,z+.009),.009,'Steel',6)
def arc(n,r,thick,depth,ang1,ang2,spring=1.3):
 vs=[];steps=16
 for z in [-depth/2,depth/2]:
  for rr in [r-thick,r]:
   for i in range(steps+1):
    a=ang1+(ang2-ang1)*i/steps;vs.append((rr*math.cos(a),spring+rr*math.sin(a),z))
 s=steps+1;fs=[]
 for i in range(steps):
  fs.extend([(i,i+1,s+i+1,s+i),(2*s+i,3*s+i,3*s+i+1,2*s+i+1),(i,2*s+i,2*s+i+1,i+1),(s+i,s+i+1,3*s+i+1,3*s+i)])
 fs.extend([(0,s,3*s,2*s),(s-1,3*s-1,4*s-1,2*s-1)])
 return mesh(n,vs,fs,'Coat',.004,True)
def export(name):
 source=[o for o in bpy.context.scene.objects if o.type=='MESH']
 for o in source:
  if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(p.normal[j]))]
   for li in p.loop_indices:
    c=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;o.data.uv_layers.active.data[li].uv=(c[axes[0]],c[axes[1]])
 bpy.ops.wm.save_as_mainfile(filepath=str(H/(name+'.blend')))
 dep=bpy.context.evaluated_depsgraph_get();res=[]
 for o in source:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);n=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(n);n.matrix_world=o.matrix_world.copy();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();res.append(n)
 bpy.ops.object.select_all(action='DESELECT')
 for o in res:o.select_set(True)
 bpy.context.view_layer.objects.active=res[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=name
 OUT.mkdir(parents=True,exist_ok=True)
 bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
 manifest[name]={'triangles':len(obj.data.polygons),'parts':len(source),'beveled_parts':sum(bool(o.get('bevel_width_m',0)) for o in source),'asset':str(OUT/(name+'.fbx'))};print('DONE',name,manifest[name]['triangles'],flush=True)

reset()
for i in range(6):arc('ArchSegment',2.095,.085,.16,i*math.pi/6+.002,(i+1)*math.pi/6-.002)
for side in [-1,1]:
 box('Leg',side*2.052,.66,0,.085,1.32,.16,'Coat');box('Foot',side*2.018,.045,0,.16,.09,.24)
 for y in [.13,1.18]:
  box('LegJoint',side*2.05,y,.086,.095,.13,.012);bolt(side*2.05,y-.035,.094);bolt(side*2.05,y+.035,.094)
for a in [math.pi/6,math.pi/3,math.pi/2,2*math.pi/3,5*math.pi/6]:
 x=2.05*math.cos(a);y=1.3+2.05*math.sin(a);bolt(x,y,.083)
export('CFD_TunnelRib')
reset()
# Concave panel for a 10m radius hemisphere, pivot at base midpoint, front +Z.
vs=[];nx=12;ny=6
for layer in [0,.022]:
 for j in range(ny+1):
  y=.05+1.1*j/ny;rad=math.sqrt(100-y*y)-.025-layer
  for i in range(nx+1):
   a=(i/nx-.5)*.11;vs.append((rad*math.sin(a),y,9.91-rad*math.cos(a)))
N=(nx+1)*(ny+1);fs=[]
for j in range(ny):
 for i in range(nx):
  k=j*(nx+1)+i;fs.extend([(k,k+1,k+nx+2,k+nx+1),(N+k,N+k+nx+1,N+k+nx+2,N+k+1)])
per=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
for a,b in zip(per,per[1:]+per[:1]):fs.append((a,b,N+b,N+a))
mesh('CovedPanel',vs,fs,'Coat',.003,True)
for x in [-.48,.48]:
 for y in [.16,1.02]:bolt(x,y,9.91-math.sqrt(100-y*y-x*x)+.052)
export('CFD_CovePanel')
reset()
box('Panel',0,.96,.06,1.25,1.9,.06,'Coat',.008)
for x in [-.55,.55]:
 for y in [.15,1.7]:box('StandOff',x,y,-.11,.065,.065,.32);bolt(x,y,.092)
export('CFD_ServiceBackplate')
reset()
box('Housing',0,.05,0,1.2,.10,.18,'Steel',.008);box('Diffuser',0,-.007,0,1.1,.026,.135,'Lamp',.007)
for x in [-.48,.48]:box('Mount',x,.12,0,.07,.08,.14);bolt(x,.035,.095)
export('CFD_SealedLight')
reset()
box('VentBack',0,.225,0,.65,.45,.10,'Dark',.006)
for x in [-.315,.315]:box('VentFrame',x,.225,.05,.025,.45,.035,'Coat')
for y in [.012,.438]:box('VentFrame',0,y,.05,.63,.025,.035,'Coat')
for j in range(7):box('Louver',0,.065+j*.052,.068,.58,.018,.07,'Steel',.002)
for x in [-.29,.29]:
 for y in [.032,.418]:bolt(x,y,.074)
export('CFD_Vent')
reset()
for x in [-.146,.146]:box('SideRail',x,.055,0,.008,.11,2)
for z in [-.96,-.64,-.32,0,.32,.64,.96]:box('CrossRung',0,.004,z,.30,.018,.035)
for z in [-.85,.85]:
 box('CrossSupport',0,-.022,z,.38,.04,.04)
 for x in [-.18,.18]:cyl('HangerRod',(x,0,z),(x,.28,z),.009)
 box('CeilingPlate',0,.28,z,.46,.03,.08)
export('CFD_CableTray')
reset()
for i in range(20):
 a=2*math.pi*i/20;b=2*math.pi*(i+1)/20;cyl('ClampBand',(.13*math.cos(a),.13*math.sin(a),0),(.13*math.cos(b),.13*math.sin(b),0),.012)
box('Support',.22,0,0,.19,.045,.08);box('Anchor',.32,0,0,.025,.28,.14);bolt(.325,.09,.072);bolt(.325,-.09,.072)
export('CFD_PipeClamp')
reset();cyl('ServicePipe',(0,0,-1.5),(0,0,1.5),.10,verts=32)
for z in [-1.47,1.47]:cyl('Socket',(0,0,z-.026),(0,0,z+.026),.119,verts=32)
export('CFD_ServicePipe')
reset()
box('Box',0,.375,.05,.55,.75,.12,'Dark',.006);box('Door',0,.375,.122,.53,.73,.035,'Coat',.008)
for y in [.12,.63]:box('Hinge',-.25,y,.143,.045,.10,.025)
box('Latch',.20,.375,.15,.032,.15,.035);box('LabelRecess',0,.55,.144,.20,.08,.008,'Dark',.001)
export('CFD_InspectionBox')
(H/'environment_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
