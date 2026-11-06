"""Reference_004 inspired rounded corridor portals and continuous wall-ceiling coves.
Author 송예찬. Plan coordinates unchanged; all manufactured edges bevelled.
"""
import bpy,bmesh,math,json,sys
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
SRC=Path(__file__).resolve().parent;REPO=SRC.parents[1]
ENV=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment'
plans=json.loads((REPO/'Docs/도면/잠입_탐색/layout.json').read_text(encoding='utf-8-sig'))['floors']
palette={'Floor':(.49,.51,.52,1),'Ceiling':(.77,.79,.79,1),'Shell':(.78,.80,.79,1),'Inset':(.30,.34,.35,1),'Champagne':(.47,.40,.28,1),'Diffuser':(.84,.91,.98,1)}
def world(u,h,v):return (24-u,16-v,h)
def mesh(name,vs,fs,mat,bevel=.009):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mats[mat]);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  p.use_smooth=True;axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:c=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(c[axes[0]],c[axes[1]])
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 m=o.modifiers.new('Manufactured_Soft_Edges','BEVEL');m.width=bevel;m.segments=3;m.limit_method='ANGLE';m.angle_limit=math.radians(28);m.harden_normals=True
 n=o.modifiers.new('Weighted_Normals','WEIGHTED_NORMAL');n.keep_sharp=True;o['bevel_width_m']=bevel
 return o
def box(name,u,h,v,w,r,d,mat='Shell',bevel=.008):
 vs=[world(u+x*w/2,h+y*r/2,v+z*d/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,min(bevel,min(w,r,d)*.22))
def band(name,path,mapper,depth,thickness,mat='Shell'):
 vs=[];fs=[]
 for i,p in enumerate(path):
  a=Vector(path[max(0,i-1)]);b=Vector(path[min(len(path)-1,i+1)]);t=(b-a).normalized();normal=Vector((-t.y,t.x))
  for sign,along in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   c=Vector(p)+normal*(thickness*.5*sign);vs.append(mapper(c.x,c.y,depth*.5*along))
 for i in range(len(path)-1):
  for j in range(4):fs.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
 fs.extend([(3,2,1,0),tuple((len(path)-1)*4+j for j in range(4))]);return mesh(name,vs,fs,mat,.022 if mat=='Shell' else .005)
def arch_profile(w,h):
 left=-w/2+.32;rx=-left;ry=rx;top=h-.18;cy=top-ry
 path=[(left+.14,.06),(left+.14,.25),(left+.09,.48),(left+.025,.80),(left,1.1),(left,cy)]
 for i in range(1,33):
  angle=math.pi-i*math.pi/32;path.append((rx*math.cos(angle),cy+ry*math.sin(angle)))
 path.extend([(-x,y) for x,y in reversed(path[:6][:-1])])
 return path
def cove(name,mapper,length,height,radius):
 count=max(1,math.ceil(length/2.6));step=length/count
 for k in range(count):
  vs=[];fs=[]
  for i in range(15):
   a=math.pi*i/28;xx=radius-radius*math.cos(a);yy=height-radius+radius*math.sin(a)
   lo=max(k*step+.004,xx);hi=min((k+1)*step-.004,length-xx)
   for sign,z in [(-1,lo),(1,lo),(1,hi),(-1,hi)]:
    x=xx-math.cos(a)*sign*.028;y=yy+math.sin(a)*sign*.028;vs.append(mapper(x,y,z))
  for i in range(14):
   for j in range(4):fs.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
  fs.extend([(3,2,1,0),tuple(56+j for j in range(4))]);mesh(name+'_'+str(k),vs,fs,'Shell',.004)
def tunnel_height(x,z,width,h,doors):
 r=width/2-.16;cy=h-.045-r
 y=cy+math.sqrt(max(0,r*r-x*x))
 for along,side in doors:
  # A groin/lunette over the door and its pocket; keep the 2.8m portal unobstructed.
  d=abs(z-along)
  if d>=2.55:continue
  hood=2.92
  if d<1.25:hood=max(hood,2.10+math.sqrt(1.25**2-d*d))
  fade=min(1,(2.55-d)/.45)
  hood=cy+(hood-cy)*fade-max(0,r-side*x)*.12
  y=max(y,hood)
 return y
def tunnel(room,h,plan):
 u,v,w,d=(room[k] for k in ('x','y','w','h'));rid=room['id'];horizontal=w>d
 length=w if horizontal else d;width=d if horizontal else w;start=u if horizontal else v;cross=v+d/2 if horizontal else u+w/2
 mapper=(lambda x,y,z:world(z,y,cross+x)) if horizontal else (lambda x,y,z:world(cross+x,y,z))
 doors=[]
 for door in plan['doors']:
  if door['a']!=rid and door['b']!=rid:continue
  along=door['x'] if horizontal else door['y'];sidecoord=door['y'] if horizontal else door['x']
  if abs(sidecoord-cross)>width*.35:doors.append((along,1 if sidecoord>cross else -1))
 radius=width/2-.16;panels=math.ceil(length/2.7);span=length/panels;na=40;nz=8
 for k in range(panels):
  lo=start+k*span+.002;hi=start+(k+1)*span-.002;vs=[];fs=[]
  for skin in (0,1):
   for iz in range(nz+1):
    z=lo+(hi-lo)*iz/nz
    for ia in range(na+1):
     angle=-math.pi/2+math.pi*ia/na;x=radius*math.sin(angle)
     y=tunnel_height(x,z,width,h,doors)+skin*.13
     vs.append(mapper(x,y,z))
  layer=(na+1)*(nz+1)
  for skin in (0,1):
   off=skin*layer
   for iz in range(nz):
    for ia in range(na):
     a=off+iz*(na+1)+ia;face=(a,a+1,a+na+2,a+na+1);fs.append(face if skin else tuple(reversed(face)))
  perimeter=list(range(na+1))+[i*(na+1)+na for i in range(1,nz+1)]+list(range(nz*(na+1)+na-1,nz*(na+1)-1,-1))+[i*(na+1) for i in range(nz-1,0,-1)]
  for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):fs.append((a,b,b+layer,a+layer))
  mesh(rid+'_TunnelVault_'+str(k),vs,fs,'Shell',.003)
 # Crown-mounted diffusers follow the vault curvature, rather than a flat roof.
 for i in range(max(1,int(length/8))):
  z=start+(i+.5)*length/max(1,int(length/8));center_mapper=lambda x,y,a,z=z:mapper(x,y,z+a)
  def crown(half,drop):return [(x,tunnel_height(x,z,width,h,[])-drop) for x in [-half+j*(2*half)/12 for j in range(13)]]
  band(rid+'_Tunnel_LightFrame_'+str(i),crown(.51,.030),center_mapper,1.70,.035,'Shell')
  band(rid+'_Tunnel_Diffuser_'+str(i),crown(.435,.058),center_mapper,1.55,.014,'Diffuser')


def dome_y(room,x,z):
 roof=room['roof'];rx=room['w']/2-.16;rz=room['h']/2-.16
 return roof['spring']+(roof['crown']-roof['spring'])*math.sqrt(max(0,1-(x/rx)**2)*max(0,1-(z/rz)**2))
def dome_panel(name,room,u,v,x,z,w,d,drop,thick,mat):
 vs=[];fs=[];nx=6;nz=8
 for side in (0,1):
  for iz in range(nz+1):
   for ix in range(nx+1):
    a=x-w/2+w*ix/nx;b=z-d/2+d*iz/nz;vs.append(world(u+a,dome_y(room,a,b)-drop+side*thick,v+b))
 layer=(nx+1)*(nz+1)
 for side in (0,1):
  for iz in range(nz):
   for ix in range(nx):
    a=side*layer+iz*(nx+1)+ix;face=(a,a+1,a+nx+2,a+nx+1);fs.append(face if side else tuple(reversed(face)))
 per=list(range(nx+1))+[i*(nx+1)+nx for i in range(1,nz+1)]+list(range(nz*(nx+1)+nx-1,nz*(nx+1)-1,-1))+[i*(nx+1) for i in range(nz-1,0,-1)]
 for a,b in zip(per,per[1:]+per[:1]):fs.append((a,b,b+layer,a+layer))
 mesh(name,vs,fs,mat,.003)
def dome(room,rows):
 u=room['x']+room['w']/2;v=room['y']+room['h']/2;rx=room['w']/2-.16;rz=room['h']/2-.16;nx=32;nz=40;vs=[];fs=[];rid=room['id']
 for skin in (0,1):
  for iz in range(nz+1):
   z=rz*math.sin(-math.pi/2+math.pi*iz/nz)
   for ix in range(nx+1):
    x=rx*math.sin(-math.pi/2+math.pi*ix/nx);vs.append(world(u+x,dome_y(room,x,z)+skin*.13,v+z))
 layer=(nx+1)*(nz+1)
 for skin in (0,1):
  off=skin*layer
  for iz in range(nz):
   for ix in range(nx):
    a=off+iz*(nx+1)+ix;face=(a,a+1,a+nx+2,a+nx+1);fs.append(face if skin else tuple(reversed(face)))
 per=list(range(nx+1))+[i*(nx+1)+nx for i in range(1,nz+1)]+list(range(nz*(nx+1)+nx-1,nz*(nx+1)-1,-1))+[i*(nx+1) for i in range(nz-1,0,-1)]
 for a,b in zip(per,per[1:]+per[:1]):fs.append((a,b,b+layer,a+layer))
 mesh(rid+'_DomeShell',vs,fs,'Shell',.004)
 for axis,rad in ((0,rx),(1,rz)):
  path=[]
  for j in range(49):
   a=rad*math.sin(-math.pi/2+math.pi*j/48);yy=dome_y(room,a if axis==0 else 0,0 if axis==0 else a)-.08;path.append((a,yy))
  mapper=(lambda a,h,b:world(u+a,h,v+b)) if axis==0 else (lambda a,h,b:world(u+b,h,v+a))
  band(rid+'_Dome_Rib_'+str(axis),path,mapper,.22,.16)
 # New room lights sit against the dome itself; old flat-ceiling lights are removed.
 nxlight=2; nzlight=3 if room['h']>=12 else 2
 for ix in range(nxlight):
  for iz in range(nzlight):
   x=rx*(-.42+.84*ix);z=rz*(-.55+1.1*iz/max(1,nzlight-1));y=dome_y(room,x,z)
   dome_panel(rid+'_Dome_LampFrame_'+str(ix)+'_'+str(iz),room,u,v,x,z,.76,1.14,.05,.03,'Shell')
   dome_panel(rid+'_Dome_Lens_'+str(ix)+'_'+str(iz),room,u,v,x,z,.68,1.00,.072,.012,'Diffuser')
   rows['lights'].append({'name':rid+'_DomeLight_'+str(ix)+'_'+str(iz),'position':[u+x-24,y-.20,v+z-16],'range':max(6.5,y+2),'intensity':22.0,'angle':115})
 rows.setdefault('domes',[]).append({'room':rid,**room['roof']})
 # Cover sub-millimetre floor panel gaps without covering pit openings.
 pits=[b for b in plan['blocks'] if b.get('kind')=='pit' and b['x']<room['x']+room['w'] and b['x']+b['w']>room['x'] and b['y']<room['y']+room['h'] and b['y']+b['h']>room['y']]
 xs=sorted(set([room['x'],room['x']+room['w']]+[max(room['x'],min(room['x']+room['w'],x)) for b in pits for x in (b['x'],b['x']+b['w'])]))
 zs=sorted(set([room['y'],room['y']+room['h']]+[max(room['y'],min(room['y']+room['h'],z)) for b in pits for z in (b['y'],b['y']+b['h'])]))
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(zs,zs[1:]):
   x=(a+b)/2;z=(c+d)/2
   if any(p['x']<x<p['x']+p['w'] and p['y']<z<p['y']+p['h'] for p in pits):continue
   box(rid+'_Floor_SeamBacking',x,-.20,z,b-a,.05,d-c,'Floor',.003)


def export(floor,rows):
 source=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(SRC/f'WA_{floor}_Interior.blend'))
 dep=bpy.context.evaluated_depsgraph_get();col=bpy.data.collections.new('Export');bpy.context.scene.collection.children.link(col);batches=defaultdict(list)
 for o in source:
  me=bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep);n=bpy.data.objects.new('Export',me);col.objects.link(n);n.matrix_world=o.matrix_world.copy();coords=[o.matrix_world@v.co for v in o.data.vertices];c=sum(coords,Vector())/len(coords);key=(me.materials[0].name,int((24-c.x)//8),int((16-c.y)//8));batches[key].append(n)
 result=[]
 for (m,x,z),obs in batches.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  o=bpy.context.object;o.name=f'AR_{floor}_{m}_{x}_{z}';bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();result.append(o)
 bpy.ops.object.select_all(action='DESELECT')
 for o in result:o.select_set(True)
 bpy.context.view_layer.objects.active=result[0];bpy.ops.export_scene.fbx(filepath=str(ENV/floor/f'WA_{floor}_Interior.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,bake_anim=False,mesh_smooth_type='FACE')
 rows.update({'sourceObjects':len(source),'renderers':len(result),'triangles':sum(len(o.data.polygons) for o in result)})
 (SRC/f'{floor}_arches.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print('ARCH_DONE',floor,rows['arches'],rows['triangles'],flush=True)
for floor in (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ('B5','B4','B3')):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';mats={}
 for key,color in palette.items():
  m=bpy.data.materials.new('AR_'+key);m.diffuse_color=color;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=.50;mats[key]=m
 plan=next(p for p in plans if p['floor']==floor);rows={'floor':floor,'arches':0,'roomsWithCoves':[],'colliders':[],'lights':[],'skippedNearDoors':[]}
 for room in plan['rooms']:
  rid=room['id'];u,v,w,d=(room[k] for k in ('x','y','w','h'))
  if rid in ('STA','STB'):continue
  h=(7.2 if rid=='A' else 4.0) if floor=='B5' else (5.6 if rid=='D' else 4.0) if floor=='B4' else (4.8 if rid in ('A','B') else 4.4 if rid in ('D','HVAC','LIFT') else 4)
  # Start at the existing inner wall face. Mitered coves meet around room corners.
  if room['kind']=='corridor':
   tunnel(room,h,plan);rows['roomsWithCoves'].append(rid)
  elif room.get('roof',{}).get('kind')=='dome':
   dome(room,rows);rows['roomsWithCoves'].append(rid)
  else:
   inset=.16;cw=w-2*inset;cd=d-2*inset;rad=1.02 if room['kind']=='corridor' else .80
   cove(rid+'_Cove_N',lambda x,y,z:world(u+inset+z,y,v+inset+x),cw,h-.045,rad)
   cove(rid+'_Cove_S',lambda x,y,z:world(u+inset+z,y,v+d-inset-x),cw,h-.045,rad)
   cove(rid+'_Cove_W',lambda x,y,z:world(u+inset+x,y,v+inset+z),cd,h-.045,rad)
   cove(rid+'_Cove_E',lambda x,y,z:world(u+w-inset-x,y,v+inset+z),cd,h-.045,rad);rows['roomsWithCoves'].append(rid)
  if room['kind']!='corridor':continue
  box(rid+'_Floor_SeamBacking',u+w/2,-.18,v+d/2,w,.08,d,'Floor',.003)
  box(rid+'_Ceiling_SeamBacking',u+w/2,h+.12,v+d/2,w,.10,d,'Ceiling',.003)
  horizontal=w>d;length=w if horizontal else d;width=d if horizontal else w;start=u if horizontal else v;cross=v+d/2 if horizontal else u+w/2
  relevant=[door for door in plan['doors'] if door['a']==rid or door['b']==rid]
  candidates=[2.3+i*4.8 for i in range(int((length-4.4)/4.8)+1)]
  for index,dist in enumerate(candidates):
   chosen=None
   for delta in (0,.65,-.65,1.1,-1.1,1.6,-1.6):
    a=start+dist+delta
    if a<start+1.8 or a>start+length-1.8:continue
    if any(abs(a-(door['x'] if horizontal else door['y']))<2.65 for door in relevant):continue
    if any(abs(a-bay['x'])<1.25 for bay in plan.get('serviceBays',[]) if horizontal and v-.01<bay['y']<v+d+.01):continue
    chosen=a;break
   if chosen is None:rows['skippedNearDoors'].append(rid+'_'+str(index));continue
   mapper=(lambda x,y,z,a=chosen,c=cross:world(a+z,y,c+x)) if horizontal else (lambda x,y,z,a=chosen,c=cross:world(c+x,y,a+z))
   name=f'{rid}_Arch_{index:02}'
   blocked=json.loads((SRC/'excluded_arches.json').read_text()) if (SRC/'excluded_arches.json').exists() else {}
   if name in blocked.get(floor,[]):rows['skippedNearDoors'].append(name+'_existing_collision');continue
   band(name,arch_profile(width,h),mapper,.44,.24);rows['arches']+=1
   # The dark inset is recessed into the arch's front edge, giving a fine shadow line.
   band(name+'_InnerSeal',arch_profile(width-.22,h-.095),mapper,.12,.025,'Inset')
   for side in (-1,1):
    uu=chosen if horizontal else cross+side*(width/2-.46);vv=cross+side*(width/2-.46) if horizontal else chosen
    rows['colliders'].append({'name':name+('_Left' if side<0 else '_Right')+'_Foot','center':[uu-24,.45,vv-16],'size':[.44 if horizontal else .24,.90,.24 if horizontal else .44]})
    uu=chosen if horizontal else cross+side*(width/2-.32);vv=cross+side*(width/2-.32) if horizontal else chosen
    rows['colliders'].append({'name':name+('_Left' if side<0 else '_Right')+'_Stem','center':[uu-24,1.45,vv-16],'size':[.44 if horizontal else .24,1.10,.24 if horizontal else .44]})
    # Short warm-metal accents are real inset hardware, placed below the arch shoulder.
    bx=side*(width/2-.43);loc=mapper(bx,1.95,0);pu=24-loc[0];pv=16-loc[1]
    box(name+'_Accent',pu,1.95,pv,.45 if horizontal else .035,.055,.035 if horizontal else .45,'Champagne',.005)
  # Recessed diffuse ceiling panels emphasize the rounded sections without bloom glare.
  for i in range(max(1,int(length/8))):
   a=start+(i+.5)*length/max(1,int(length/8));pu=a if horizontal else cross;pv=cross if horizontal else a
   rows['lights'].append({'name':rid+'_Diffuse_'+str(i),'position':[pu-24,h-.18,pv-16],'range':h+2.5,'intensity':14.0,'angle':115})
 for v,d in ((.4,.8),(33.4,1.2)):
  box('Core_Junction_Closure',42.6,2,v,.24,4,d,'Shell',.01)
  rows['colliders'].append({'name':'Core_Junction_'+str(v),'center':[18.6,2,v-16],'size':[.24,4,d]})
 export(floor,rows)
