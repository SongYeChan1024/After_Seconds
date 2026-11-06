"""Blender authoring: circular shells, traversable tunnel junctions, pocket doors, grating."""
import bpy,bmesh,math,json,sys
from mathutils import Vector
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
DATA=json.loads((REPO/'Docs/도면/원형공동/facility_layout.json').read_text(encoding='utf-8'))
ENV=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment'
manifest={}
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
 global mats;mats={}
 for n,col in [('Shell',(.66,.73,.79,1)),('Floor',(.28,.34,.4,1)),('Steel',(.27,.32,.37,1)),('Inset',(.09,.13,.17,1)),('Glass',(.2,.3,.36,1)),('Lamp',(.7,.8,.9,1)),('Guide',(.78,.85,.88,1))]:
  m=bpy.data.materials.new('CF_'+n);m.diffuse_color=col;m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=col;mats[n]=m
def world(x,h,v):return (-x,v,h)
def mesh(name,vs,fs,mat='Steel',bevel=.008,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mats[mat])
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 for p in me.polygons:p.use_smooth=smooth
 if bevel:
  mod=o.modifiers.new('Manufactured_Bevel','BEVEL');mod.width=bevel;mod.segments=3;mod.limit_method='ANGLE';mod.angle_limit=math.radians(28);mod.harden_normals=True
  mod=o.modifiers.new('Weighted_Normals','WEIGHTED_NORMAL');mod.keep_sharp=True
 o['bevel_width_m']=bevel;return o
def box(name,x,h,v,w,y,d,mat='Steel',bevel=.006):
 vs=[world(x+dx*w/2,h+dy*y/2,v+dv*d/2) for dx,dy,dv in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,min(bevel,min(w,y,d)*.22))
def boolean(o,cut,operation='DIFFERENCE'):
 bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Junction_'+operation,'BOOLEAN');m.operation=operation;m.solver='EXACT';m.object=cut
 bpy.ops.object.modifier_move_up(modifier=m.name)
 if len(o.modifiers)>2:bpy.ops.object.modifier_move_up(modifier=m.name)
 bpy.ops.object.modifier_apply(modifier=m.name)
def sphere(name,x,v,r):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=r,location=world(x,0,v));o=bpy.context.object;o.name=name;return o
def cylinder(name,x,v,r):
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=.3,location=world(x,-.15,v));o=bpy.context.object;o.name=name;o.data.materials.append(mats['Floor']);return o
def sweep(name,t,pad=0,extend=0,mat='Shell',bevel=0):
 p,q=t['p'],t['q'];dx=q[0]-p[0];dv=q[1]-p[1];L=math.hypot(dx,dv);ux,uv=dx/L,dv/L;w=t['w']/2+pad;spring=t['h']-t['w']/2
 prof=[(-w,-.5-pad),(w,-.5-pad),(w,spring)]
 prof += [(w*math.cos(a),spring+w*math.sin(a)) for a in [math.pi*i/32 for i in range(1,33)]]
 vs=[]
 for end in [-extend,L+extend]:
  for cross,h in prof:vs.append(world(p[0]+ux*end-uv*cross,h,p[1]+uv*end+ux*cross))
 n=len(prof);fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
 for i in range(n):fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
 return mesh(name,vs,fs,mat,bevel,True)
def floorbar(t):
 p,q=t['p'],t['q'];dx=q[0]-p[0];dv=q[1]-p[1];L=math.hypot(dx,dv);ux,uv=dx/L,dv/L
 vs=[]
 for h in [-.3,0]:
  for along,cross in [(0,-t['w']/2),(L,-t['w']/2),(L,t['w']/2),(0,t['w']/2)]:vs.append(world(p[0]+ux*along-uv*cross,h,p[1]+uv*along+ux*cross))
 return mesh(t['id']+'_Floor',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Floor',0)
def export(name,floor):
 source=[o for o in bpy.context.scene.objects if o.type=='MESH'];
 for o in source:
  me=o.data
  if not me.uv_layers:me.uv_layers.new(name='UVMap')
  for p in me.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
   for li in p.loop_indices:
    co=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;me.uv_layers.active.data[li].uv=(co[axes[0]]*.5,co[axes[1]]*.5)
 bpy.ops.wm.save_as_mainfile(filepath=str(HERE/(name+'.blend')))
 dep=bpy.context.evaluated_depsgraph_get();result=[]
 for o in source:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);n=bpy.data.objects.new(o.name,me);bpy.context.collection.objects.link(n);n.matrix_world=o.matrix_world.copy()
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();result.append(n)
 bpy.ops.object.select_all(action='DESELECT')
 for o in result:o.select_set(True)
 bpy.context.view_layer.objects.active=result[0];(ENV/floor).mkdir(exist_ok=True,parents=True)
 bpy.ops.export_scene.fbx(filepath=str(ENV/floor/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,bake_anim=False,mesh_smooth_type='FACE')
 manifest[name]={'floor':floor,'objects':len(source),'triangles':sum(len(o.data.polygons) for o in result),'source':str(HERE/(name+'.blend'))};print('EXPORTED',name,manifest[name],flush=True)
def build_shell(fid,only_room=None):
 reset();f=next(f for f in DATA['floors'] if f['id']==fid);rooms=[r for r in f['rooms'] if (r['id']==only_room if only_room else not r.get('wing'))];ids={r['id'] for r in rooms};ts=[t for t in f['tunnels'] if t['a'] in ids and t['b'] in ids]
 interior={r['id']:sphere('Cut_'+r['id'],r['x'],r['v'],r['r']) for r in rooms}
 cuts=[sweep('Cut_'+t['id'],t,extend=4) for t in ts]
 for r in rooms:
  out=sphere('CF_'+fid+'_'+r['id']+'_Dome',r['x'],r['v'],r['r']+.22);out.data.materials.append(mats['Shell']);boolean(out,interior[r['id']]);bottom=box('CutBottom',r['x'],-r['r'],r['v'],r['r']*3,r['r']*2,r['r']*3,bevel=0);boolean(out,bottom);bpy.data.objects.remove(bottom,do_unlink=True)
  for t,cut in zip(ts,cuts):
   if r['id'] in (t['a'],t['b']):boolean(out,cut)
  for p in out.data.polygons:p.use_smooth=True
  m=out.modifiers.new('Opening_Bevel','BEVEL');m.width=.012;m.segments=3;m.limit_method='ANGLE';m.angle_limit=.6;out['bevel_width_m']=.012
 for i,t in enumerate(ts):
  o=sweep('CF_'+t['id']+'_Vault',t,pad=.18,mat='Shell');boolean(o,cuts[i])
  for r in rooms:
   if r['id'] in (t['a'],t['b']):boolean(o,interior[r['id']])
  m=o.modifiers.new('Vault_Edge_Bevel','BEVEL');m.width=.008;m.segments=2;m.limit_method='ANGLE';o['bevel_width_m']=.008
 floor=cylinder('CF_'+fid+'_Floor',rooms[0]['x'],rooms[0]['v'],rooms[0]['r'])
 for r in rooms[1:]:
  ob=cylinder('JoinFloor',r['x'],r['v'],r['r']);boolean(floor,ob,'UNION');bpy.data.objects.remove(ob,do_unlink=True)
 for t in ts:
  ob=floorbar(t);boolean(floor,ob,'UNION');bpy.data.objects.remove(ob,do_unlink=True)
 for ob in list(interior.values())+cuts:bpy.data.objects.remove(ob,do_unlink=True)
 m=floor.modifiers.new('Slab_Edge_Bevel','BEVEL');m.width=.012;m.segments=2;m.limit_method='ANGLE';floor['bevel_width_m']=.012
 export('CF_'+fid+('_C02_Preview' if only_room else '_Core'),fid)
def door():
 reset()
 for side in [-1,1]:
  for z in [-.19,.19]:box('Pocket_'+str(side)+'_'+str(z),side*1.90,1.48,z,1.40,2.96,.065,'Steel',.008)
  box('Jamb_'+str(side),side*1.23,1.43,0,.08,2.86,.48,'Steel',.006)
  box('PocketEnd_'+str(side),side*2.59,1.48,0,.08,2.96,.44,'Steel',.006)
  box('Leaf_'+('Left' if side<0 else 'Right'),side*.602,1.39,0,1.198,2.78,.10,'Shell',.009)
  box('Seal_'+str(side),side*.013,1.39,.055,.018,2.76,.014,'Inset',.002)
 box('Header',0,2.97,0,5.24,.22,.48,'Steel',.009)
 box('Threshold',0,.012,0,2.4,.024,.40,'Steel',.003)
 export('CF_PocketDoor_240','Common')
def mezzanine():
 reset();m=DATA['mezzanines'][0];height=m['height'];panels=[]
 # Modular grated panels. Each contains real gaps; solid pads are deliberately opaque.
 for j,r in enumerate(m['deck_rects']):
  nx=math.ceil(r['w']/1.22);nv=math.ceil(r['d']/1.10);w=r['w']/nx;dep=r['d']/nv
  for ix in range(nx):
   for iv in range(nv):
    x=r['x']-r['w']/2+(ix+.5)*w;v=r['v']-r['d']/2+(iv+.5)*dep;objects=[]
    for side in [-1,1]:
     objects.append(box('Frame',x+side*(w/2-.02),height-.04,v,.04,.08,dep,'Steel',.002))
     objects.append(box('Frame',x,height-.04,v+side*(dep/2-.02),w,.08,.04,'Steel',.002))
    for k in range(1,int(w/.09)):
     objects.append(box('BearingBar',x-w/2+k*.09,height-.035,v,.009,.07,dep-.06,'Steel',.0015))
    for k in range(1,int(dep/.24)):
     objects.append(box('CrossBar',x,height-.02,v-dep/2+k*.24,w-.06,.025,.008,'Steel',.0015))
    # Retain bevel modifiers in source, batch the evaluated panel only for export later.
    panels.extend(objects)
 for r in m['solid_workpads']:box('Solid_WorkPad',r['x'],height+.01,r['v'],r['w'],.04,r['d'],'Steel',.004)
 for x in [12.8,25.2]:
  for v in [-4.1,.8]:
   box('Column',x,height/2-.14,v,.18,height-.28,.18,'Steel',.005);box('ColumnFoot',x,.03,v,.36,.06,.36,'Steel',.004)
   for dx in [-.12,.12]:
    for dv in [-.12,.12]:box('AnchorBolt',x+dx,.07,v+dv,.035,.025,.035,'Steel',.003)
  box('MainBeam',x,height-.22,-.3,.16,.28,7.4,'Steel',.005)
 for v in [-4.1,-2.3,.8]:box('CrossBeam',19,height-.22,v,14.6,.24,.12,'Steel',.004)
 for st in m['stairs']:
  for i in range(20):
   v=st['v_bottom']-(i+.5)*st['tread'];h=(i+1)*st['rise'];box('Stair_'+st['id']+'_'+str(i),st['x'],h-.04,v,st['w'],.08,.28,'Steel',.004)
  for side in [-1,1]:
   a=Vector(world(st['x']+side*.67,.03,st['v_bottom']+.08));b=Vector(world(st['x']+side*.67,height-.15,st['v_top']-.12));vec=b-a
   o=box('StairStringer',0,0,0,.13,.18,vec.length,'Steel',.004);o.location=(a+b)/2;o.rotation_euler=Vector((0,1,0)).rotation_difference(vec).to_euler()
   for i in range(0,21,4):
    v=st['v_bottom']-i*st['tread'];h=i*st['rise'];box('StairPost',st['x']+side*.73,h+.52,v,.035,1.04,.035,'Steel',.002)
   a=Vector(world(st['x']+side*.73,1.05,st['v_bottom']));b=Vector(world(st['x']+side*.73,height+1.05,st['v_top']));vec=b-a
   o=box('StairRail',0,0,0,.045,.045,vec.length,'Steel',.003);o.location=(a+b)/2;o.rotation_euler=Vector((0,1,0)).rotation_difference(vec).to_euler()
 # Deck rail segments, openings at stair mouths.
 segs=[(11.7,-4.6,26.3,-4.6),(11.7,-4.6,11.7,2.9),(26.3,-4.6,26.3,2.9),(13.9,-2.4,24.1,-2.4),(13.9,-2.4,13.9,2.9),(24.1,-2.4,24.1,2.9)]
 for x1,v1,x2,v2 in segs:
  L=math.hypot(x2-x1,v2-v1);n=max(1,math.ceil(L/1.5))
  for i in range(n+1):box('DeckPost',x1+(x2-x1)*i/n,height+.53,v1+(v2-v1)*i/n,.04,1.06,.04,'Steel',.002)
  for h,th in [(height+1.06,.045),(height+.53,.035),(height+.07,.12)]:box('DeckRail',(x1+x2)/2,h,(v1+v2)/2,abs(x2-x1)+.04,th,abs(v2-v1)+.04,'Steel',.003)
 # Join evaluated meshes by functional group to keep draw-call count reasonable.
 source=list(bpy.context.scene.objects);dep=bpy.context.evaluated_depsgraph_get();obs=[]
 for o in source:
  if o.type!='MESH':continue
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);n=bpy.data.objects.new('Evaluated',me);bpy.context.collection.objects.link(n);n.matrix_world=o.matrix_world.copy();obs.append(n)
 bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'CF_B2_Mezzanine_Editable.blend'))
 for o in source:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();bpy.context.object.name='CF_B2_GratingAndSupport';export('CF_B2_Mezzanine','B2')
def pipes():
 reset()
 def tube(name,coords,r=.10):
  curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=12;curve.bevel_depth=r;curve.bevel_resolution=3;curve.use_fill_caps=True
  # Straight rigid runs with local rounded elbows; global automatic tangents sag.
  raw=[Vector(world(*co)) for co in coords];points=[raw[0]]
  for i in range(1,len(raw)-1):
   p=raw[i];left=raw[i-1]-p;right=raw[i+1]-p;inset=min(.30,left.length*.32,right.length*.32)
   a=p+left.normalized()*inset;b=p+right.normalized()*inset;points.append(a)
   for k in range(1,9):
    t=k/8;points.append(a*(1-t)**2+p*2*(1-t)*t+b*t*t)
  points.append(raw[-1]);sp=curve.splines.new('POLY');sp.points.add(len(points)-1)
  for p,co in zip(sp.points,points):p.co=(*co,1)
  ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob);curve.materials.append(mats['Steel']);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob['bevel_width_m']=r
 def flange(x,h,v,axis='Z'):
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.19,depth=.055,location=world(x,h,v));o=bpy.context.object;o.name='Bolted_Flange';o.data.materials.append(mats['Steel'])
  if axis=='X':o.rotation_euler[1]=math.pi/2
  m=o.modifiers.new('Flange_Bevel','BEVEL');m.width=.004;m.segments=3;o['bevel_width_m']=.004
  for i in range(8):
   a=i*math.pi/4
   if axis=='Z':box('Flange_Bolt',x+math.cos(a)*.155,h+.035,v+math.sin(a)*.155,.028,.04,.028,'Steel',.003)
   else:box('Flange_Bolt',x+.035,h+math.cos(a)*.155,v+math.sin(a)*.155,.04,.028,.028,'Steel',.003)
 for tank,pump,side in [(16.5,16,-1),(21.5,22,1)]:
  tube('PumpToTank',[(pump+side*.65,.55,4.5),(pump+side*1.15,.55,4.5),(pump+side*1.25,.55,3.8),(pump+side*1.25,.55,1.6),(tank+side*.85,.9,1),(tank+side*.60,.9,1)])
  flange(tank+side*.72,.9,1,'X');flange(pump+side*.85,.55,4.5,'X');flange(tank,2.46,1)
 tube('Upper_Return_Header',[(16.5,2.42,1),(16.5,2.9,1),(16.5,3.05,.2),(17.1,3.05,-1.4),(20.9,3.05,-1.4),(21.5,3.05,.2),(21.5,2.9,1),(21.5,2.42,1)],.13)
 for i,h in enumerate([1.0,1.65,2.3]):
  tube('Service_Header_'+str(i),[(14,h,-3.2),(16,h,-3.2),(22,h,-3.2),(24,h,-3.2)],.13)
  for x in [16,22]:flange(x,h,-3.2,'X')
  for x in [14,24]:box('HeaderSupport',x,h-.18,-3.2,.22,.10,.5,'Steel',.005)
 bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'CF_B2_ProcessPipework_Editable.blend'))
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH');bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='CF_B2_ProcessPipework'
 export('CF_B2_ProcessPipework','B2')
if '--pipes-only' in sys.argv:
 if (HERE/'geometry_manifest.json').exists():manifest=json.loads((HERE/'geometry_manifest.json').read_text())
 pipes()
elif '--mezz-only' in sys.argv:
 if (HERE/'geometry_manifest.json').exists():manifest=json.loads((HERE/'geometry_manifest.json').read_text())
 mezzanine();pipes()
else:build_shell('B5');door();build_shell('B2','C02');mezzanine();pipes()
(HERE/'geometry_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
