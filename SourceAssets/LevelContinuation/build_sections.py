"""B5/B4 stair sections V0.01. Bevelled derived models; source assets preserved."""
import bpy,bmesh,json,math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
SRC=Path(__file__).resolve().parent;REPO=SRC.parents[1]
MODELS=REPO/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Environment'
reports=[];colliders=[];lightdefs=[]
def material(key):
 name='LP_'+key;m=bpy.data.materials.get(name)
 if not m:m=bpy.data.materials.new(name);m.diffuse_color=(.35,.43,.42,1)
 return m
def box(name,u,h,v,w,r,d,mat='WallSteel',collision=False,bevel=.004):
 vs=[(-w/2,-d/2,-r/2),(w/2,-d/2,-r/2),(w/2,d/2,-r/2),(-w/2,d/2,-r/2),(-w/2,-d/2,r/2),(w/2,-d/2,r/2),(w/2,d/2,r/2),(-w/2,d/2,r/2)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(material(mat));me.update();uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis];p.use_smooth=True
  for li in p.loop_indices:co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.location=(24-u,16-v,h)
 m=ob.modifiers.new('Manufactured_Bevel','BEVEL');m.width=min(bevel,min(w,r,d)*.22);m.segments=2;m.harden_normals=True
 n=ob.modifiers.new('Weighted_Normals','WEIGHTED_NORMAL');n.keep_sharp=True;ob['bevel_width_m']=m.width
 if collision:colliders.append(dict(name=name,center=[u-24,h,v-16],size=[w,r,d]))
 return ob
def wall(u,start,end,low,high,doors):
 cuts=sorted(set([start,end]+[a for c,b,t in doors for a in (c-.75,c+.75)]))
 for a,b in zip(cuts,cuts[1:]):
  intervals=[(low,high)]
  for c,dl,dh in doors:
   if c-.75<(a+b)/2<c+.75:intervals=[(lo,min(hi,dl)) for lo,hi in intervals if lo<dl]+[(max(lo,dh),hi) for lo,hi in intervals if hi>dh]
  for lo,hi in intervals:
   if hi-lo<.001:continue
   box('LC_WallCore',u,(lo+hi)/2,(a+b)/2,.22,hi-lo,b-a,'Core',True)
   count=max(1,math.ceil((b-a)/1.5));rows=max(1,math.ceil((hi-lo)/2))
   for side in (-1,1):
    for j in range(count):
     for k in range(rows):box('LC_WallFacing',u+side*.123,lo+(k+.5)*(hi-lo)/rows,a+(j+.5)*(b-a)/count,.026,(hi-lo)/rows-.012,(b-a)/count-.012,'WallSteel')
def iswall(ob,u):
 x=24-ob.location.x;v=16-ob.location.y
 return abs(x-u)<.30 and 18.001<v<31.999 and ob.name.startswith(('Wall','Finish','Closed','ServicePanel','Vent_','Steel_','Structural_','Cast_','Continuous_','Tall_'))
def remove_where(predicate):
 names=[]
 for ob in list(bpy.context.scene.objects):
  if ob.type=='MESH' and predicate(ob):names.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
 return names
def copy_stairs(kind,offset):
 src=REPO/('SourceAssets/B45_LabPolish/LP_B5_Architecture.blend' if kind=='A' else 'SourceAssets/B45_LabPolish/LP_B4_Architecture.blend')
 prefixes=('StairA_','StairRail_','LandingRail_') if kind=='A' else ('StairB_',)
 with bpy.data.libraries.load(str(src),link=False) as (data,out):out.objects=[n for n in data.objects if n.startswith(prefixes) and not n.startswith(('StairA_Exit','StairA_TopLanding','StairB_TopLanding'))]
 for ob in out.objects:
  if ob:bpy.context.collection.objects.link(ob);ob.location.z+=offset;ob.name='Down'+kind+'_'+ob.name
 manifest=REPO/('SourceAssets/B5_StealthLayout/art_repair_manifest.json' if kind=='A' else 'SourceAssets/B4_StealthLayout/architecture_manifest.json')
 for c in json.loads(manifest.read_text(encoding='utf-8-sig'))['colliders']:
  if c['name'].startswith('Stair'+kind+'_') and 'TopLanding' not in c['name']:
   row=dict(c);row['name']='Down'+kind+'_'+c['name'];row['center']=list(c['center']);row['center'][1]+=offset;colliders.append(row)
def nosings(kind,offset=0):
 steps=20 if kind=='A' else 18;rise=7.8 if kind=='A' else 6.4
 for i in range(steps):
  h=(i+1)*rise/(steps*2)
  if kind=='A':
   box('LC_Nosing_A',42.3,h+offset+.004,26-i*.30-.018,1.23,.008,.045,'Legend',False,.001)
   box('LC_Nosing_A',40.3,h+rise/2+offset+.004,20+i*.30+.018,1.40,.008,.045,'Legend',False,.001)
  else:
   box('LC_Nosing_B',46.65,h+offset+.004,24.96+i*.28+.018,1.37,.008,.045,'Legend',False,.001)
   box('LC_Nosing_B',44.75,h+rise/2+offset+.004,30-i*.28-.018,1.37,.008,.045,'Legend',False,.001)
def rail(u1,u2,v,y):
 for h,thick in ((1.05,.04),(.52,.025)):box('LC_LandingRail', (u1+u2)/2,y+h,v,u2-u1,thick,thick,'Stainless')
 for u in (u1,(u1+u2)/2,u2):box('LC_RailPost',u,y+.52,v,.04,1.04,.04,'Stainless')
 colliders.append(dict(name='LC_LandingRailBarrier',center=[(u1+u2)/2-24,y+.55,v-16],size=[u2-u1,1.1,.08]))
def stairlights(kind,offset=0):
 specs=[(43.28,2.8,25.6,42.3,1.3,23.8),(39.22,6.65,20.6,40.3,5.7,23)] if kind=='A' else [(47.77,2.7,25.3,46.65,1.4,27),(43.73,5.9,29.5,44.75,5.0,27.6)]
 for u,y,v,tu,ty,tv in specs:
  box('LC_StepLightBody',u,y+offset,v,.10,.18,.64,'Graphite')
  box('LC_StepLightLens',u+(.054 if tu>u else -.054),y+offset-.035,v,.012,.10,.52,'Lamp',False,.002)
  lightdefs.append(dict(name='LC_StepFill_'+kind,position=[u-24,y+offset-.15,v-16],target=[tu-24,ty+offset,tv-16],intensity=6.0,range=6.5,angle=110))
def export(floor,removed):
 original=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.wm.save_as_mainfile(filepath=str(SRC/('LC_'+floor+'_Architecture.blend')))
 dep=bpy.context.evaluated_depsgraph_get();evaluated=[(o,bpy.data.meshes.new_from_object(o.evaluated_get(dep),depsgraph=dep)) for o in original];batches=defaultdict(list);col=bpy.data.collections.new('LC_Export');bpy.context.scene.collection.children.link(col)
 for o,mesh in evaluated:
  n=bpy.data.objects.new('Export',mesh);col.objects.link(n);n.matrix_world=o.matrix_world.copy();mat=mesh.materials[0].name;u=24-o.location.x;v=16-o.location.y;key=(mat,int(max(0,min(47.9,u))//8),int(max(0,min(31.9,v))//8));batches[key].append(n)
 output=[]
 for (mat,x,z),obs in batches.items():
  bpy.ops.object.select_all(action='DESELECT')
  for o in obs:o.select_set(True)
  bpy.context.view_layer.objects.active=obs[0]
  if len(obs)>1:bpy.ops.object.join()
  ob=bpy.context.object;ob.name=f'LC_{floor}_{mat}_{x}_{z}';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.dissolve_degenerate(bm,dist=1e-7,edges=list(bm.edges));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();output.append(ob)
 bpy.ops.object.select_all(action='DESELECT')
 for o in output:o.select_set(True)
 bpy.context.view_layer.objects.active=output[0];dest=MODELS/floor/('LC_'+floor+'_Architecture.fbx');bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,use_mesh_modifiers=True,bake_anim=False,mesh_smooth_type='FACE',use_custom_props=True)
 row=dict(floor=floor,removedSourceObjects=len(removed),sourceObjects=len(original),triangles=sum(len(o.data.polygons) for o in output),meshes=len(output),colliders=colliders.copy(),lights=lightdefs.copy());reports.append(row);(SRC/(floor+'_sections.json')).write_text(json.dumps(row,indent=2),encoding='utf-8')

for floor in ('B5','B4'):
 colliders.clear();lightdefs.clear();bpy.ops.wm.open_mainfile(filepath=str(REPO/f'SourceAssets/B45_LabPolish/LP_{floor}_Architecture.blend'))
 removed=remove_where(lambda o:iswall(o,39) or (floor=='B4' and iswall(o,43.5)) or o.name.startswith(('StairA_Exit','B3_ReviewBoundary','B5_ReviewBoundary')))
 if floor=='B5':
  wall(39,18,32,0,11.1,[(25,0,2.8),(28.25,7.8,10.6)])
  box('LC_UpperThreshold',39,7.77,28.25,.60,.06,1.5,'Floor',True)
  nosings('A');stairlights('A');rail(41.2,43.30,26.08,7.8)
 else:
  removed+=remove_where(lambda o:o.name.startswith('Floor_STA') or (o.name.startswith('FloorFinish_') and 39<24-o.location.x<43.5 and 18<16-o.location.y<32))
  wall(39,18,32,-7.8,4,[(25,-7.8,-5),(28.25,0,2.8)])
  wall(43.5,18,32,-7.8,9.6,[(23.5,6.4,9.2)])
  copy_stairs('A',-7.8)
  box('LC_ArrivalFloor_A',41.25,-.12,29,4.5,.24,6,'Floor',True)
  box('LC_LowerFloor_A',41.25,-7.92,25,4.5,.24,14,'Floor',True)
  for v in (18,32):box('LC_LowerShaft_A',41.25,-3.9,v,4.5,7.8,.22,'WallSteel',True)
  box('LC_UpperThreshold_B',43.5,6.37,23.5,.60,.06,1.5,'Floor',True)
  for ob in bpy.context.scene.objects:
   if ob.name.startswith('Ceiling_STB'):ob.location.z+=.7
  for v in (18,32):box('LC_UpperShaft_B',45.75,9.25,v,4.5,.7,.22,'WallSteel',True)
  box('LC_UpperShaft_B',48,9.25,25,.22,.7,14,'WallSteel',True)
  nosings('A',-7.8);nosings('B');stairlights('A',-7.8);stairlights('B');rail(41.2,43.30,26.08,0);rail(45.7,47.7,24.88,6.4)
 export(floor,removed)
print('SECTIONS_DONE',json.dumps([{k:v for k,v in r.items() if k not in ('colliders','lights')} for r in reports]))
