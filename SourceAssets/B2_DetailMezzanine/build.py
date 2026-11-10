"""B2 static art additions; Unity coordinates, metres. Author 송예찬."""
import sys,json,math,importlib.util,os
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent
b.H=H;b.manifest={}
plan=json.loads((R/'SourceAssets/B2_FullFloor/plan.json').read_text(encoding='utf8'))
layout=json.loads((R/'SourceAssets/B2_FullFloor/layout.json').read_text(encoding='utf8'))
manifest={'version':'0.01','deckY':2.42,'width':1.5,'stairStart':1.6,'deckStart':5.5,'tunnels':[],'addons':[]}
def save(n,category='Environment'):
 b.OUT=b.A/category/'B2';b.raw_export('BD_'+n);b.manifest['BD_'+n]['category']=category
 if n.endswith('_UpperWalk'):
  obj=bpy.context.object;mod=obj.modifiers.new('DistanceSimplification','DECIMATE');mod.ratio=.28;mod.use_collapse_triangulate=True
  bpy.ops.object.modifier_apply(modifier=mod.name)
  obj.name='BD_'+n+'_LOD1'
  bpy.ops.export_scene.fbx(filepath=str(b.OUT/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_space_transform=True,bake_anim=False,mesh_smooth_type='FACE')
  b.manifest[obj.name]={'triangles':len(obj.data.polygons),'category':category,'asset':str(b.OUT/(obj.name+'.fbx')),'distance_only':True}
 (H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
def bulkbox(vs,fs,x,y,z,w,h,d):
 k=len(vs);vs.extend([(x+dx*w/2,y+dy*h/2,z+dz*d/2) for dx,dy,dz in [(-1,-1,-1),(1,-1,-1),(1,-1,1),(-1,-1,1),(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]])
 fs.extend([tuple(k+j for j in f) for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
def height(s,L):return 2.42*max(0,min(1,(s-1.6)/3.9,(L-1.6-s)/3.9))
def local_to_path(vs,ps):
 out=[]
 for x,y,s in vs:
  p,di=at(ps,s);rr=Vector((di.z,0,-di.x));out.append(tuple(p+rr*x+Vector((0,y,0))))
 return out
def make_batch(n,vs,fs,mat,bevel,ps=None):
 if not vs:return
 o=mesh(n,local_to_path(vs,ps) if ps is not None else vs,fs,mat,bevel)
 if n=='BearingGrating':o.modifiers[0].segments=1
 return o
def path_tube(n,ps,a,c,x,y,r,mat='Steel'):
 pp=[];N=max(1,math.ceil((c-a)/.5))
 for i in range(N+1):
  d=a+(c-a)*i/N;p,di=at(ps,d);pp.append(tuple(p+Vector((di.z,0,-di.x))*x+Vector((0,y(d) if callable(y) else y,0))))
 tube(n,pp,r,mat)
only=os.environ.get('BD_ONLY','')
for t in plan['tunnels']:
 code=t['id'].split('-')[1];ps=path_points(t);L=sum((c-a).length for a,c in zip(ps,ps[1:]))
 if code in ['T04','T06']:continue
 spec={'id':code,'a':t['a'],'b':t['b'],'length':L,'path':t['path'],'deckY':2.42,'deckStart':5.5,'deckEnd':L-5.5}
 manifest['tunnels'].append(spec)
 if only and code!=only:continue
 reset();gv=[];gf=[];sv=[];sf=[];hv=[];hf=[]
 # Longitudinal bearing strips plus cross ties. Open cells remain visible.
 segments=math.ceil((L-11)/1.0)
 for k in range(segments):
  a=5.5+(L-11)*k/segments;c=5.5+(L-11)*(k+1)/segments;d=(a+c)/2
  for j in range(20):bulkbox(gv,gf,-.7125+j*.075,2.395,d,.008,.05,c-a-.006)
  for s in [a+.10+i*.18 for i in range(max(1,int((c-a)/.18)))]:bulkbox(gv,gf,0,2.389,s,1.47,.014,.008)
  bulkbox(sv,sf,0,2.375,a,1.51,.09,.035)
 # Physical stair treads, nosing and open risers.
 for side in [0,1]:
  for k in range(13):
   lo=1.6+k*.3;hi=lo+.3;d=(lo+hi)/2 if side==0 else L-(lo+hi)/2;y=2.42*(k+1)/13
   bulkbox(sv,sf,0,y-.035,d,1.5,.07,.295)
   bulkbox(hv,hf,0,y+.001,d+(-.129 if side==0 else .129),1.47,.008,.022)
   for j in range(7):bulkbox(gv,gf,0,y+.005,d-.11+j*.035,1.38,.006,.008)
 # Posts, folded toe boards, stringers and support anchors; clear lower centre.
 for x in [-.79,.79]:
  for a,c in [(1.6,5.5),(L-5.5,L-1.6)]:
   k=len(sv)
   for d in [a,c]:
    y=height(d,L)-.095
    sv.extend([(x-.035,y-.10,d),(x+.035,y-.10,d),(x-.035,y+.10,d),(x+.035,y+.10,d)])
   sf.extend([tuple(k+j for j in f) for f in [(0,4,6,2),(1,3,7,5),(2,6,7,3),(0,1,5,4),(0,2,3,1),(4,5,7,6)]])
   for d in [a,c]:bulkbox(sv,sf,x,max(.018,height(d,L)-.04),d,.16,.035,.25)
  path_tube('GuardHandrail',ps,1.6,L-1.6,x,lambda d:height(d,L)+.86,.023)
  path_tube('MidRail',ps,1.6,L-1.6,x,lambda d:height(d,L)+.44,.015)
  for d in [1.6+i*(L-3.2)/math.ceil((L-3.2)/1.25) for i in range(math.ceil((L-3.2)/1.25)+1)]:
   y=height(d,L);p,di=at(ps,d);rr=Vector((di.z,0,-di.x));v=p+rr*x
   cyl('GuardPost',(v.x,y,v.z),(v.x,y+.86,v.z),.021,'Steel',10)
   bulkbox(sv,sf,x,y+.025,d,.10,.05,.10)
  for i in range(math.ceil((L-11)/.65)):
   a=5.5+i*(L-11)/math.ceil((L-11)/.65);c=5.5+(i+1)*(L-11)/math.ceil((L-11)/.65)
   bulkbox(sv,sf,x,2.31,(a+c)/2,.055,.20,c-a+.004)
   bulkbox(sv,sf,x,2.48,(a+c)/2,.018,.12,c-a+.004)
 for d in [5.55+i*3 for i in range(max(1,int((L-11)/3)+1))]:
  if d>L-5.5:continue
  bulkbox(sv,sf,0,2.275,d,4.25,.15,.11)
  for x in [-2.13,2.13]:
   bulkbox(sv,sf,x,2.27,d,.08,.35,.26)
   # exposed hex fasteners on the support shoes
   p,di=at(ps,d);rr=Vector((di.z,0,-di.x))
   for dy in [-.11,.11]:
    for ds in [-.085,.085]:
     v=p+rr*x+di*ds+Vector((0,2.27+dy,0));cyl('AnchorBolt',tuple(v),tuple(v-rr*(.045 if x>0 else -.045)),.017,'Steel',6)
 make_batch('BearingGrating',gv,gf,'Steel',.0006,ps);make_batch('FabricatedStructure',sv,sf,'Steel',.003,ps);make_batch('SafetyNosing',hv,hf,'Hazard',.001,ps)
 save(code+'_UpperWalk')
 # Low poly dedicated collision: lower face-free stair ramp and closed guard edges.
 reset();vs=[];fs=[]
 samples=sorted(set([1.6,5.5,L-5.5,L-1.6]+[1.6+(L-3.2)*i/math.ceil((L-3.2)/.5) for i in range(math.ceil((L-3.2)/.5)+1)]))
 for d in samples:
  y=height(d,L)
  vs.extend([(-.77,y,d),(.77,y,d),(-.77,y-.06,d),(.77,y-.06,d)])
 for i in range(len(samples)-1):
  j=i*4;fs.extend([(j,j+4,j+5,j+1),(j+2,j+3,j+7,j+6),(j,j+2,j+6,j+4),(j+1,j+5,j+7,j+3)])
 fs.extend([(0,1,3,2),(len(vs)-4,len(vs)-2,len(vs)-1,len(vs)-3)])
 make_batch('ContinuousWalkingSurface',vs,fs,'Dark',0,ps)
 for x in [-.805,.805]:
  v=[];f=[]
  for d in samples:
   y=height(d,L);v.extend([(x-.018,y,d),(x+.018,y,d),(x-.018,y+.89,d),(x+.018,y+.89,d)])
  for i in range(len(samples)-1):
   k=i*4;f.extend([(k,k+4,k+6,k+2),(k+1,k+3,k+7,k+5),(k+2,k+6,k+7,k+3),(k,k+1,k+5,k+4)])
  f.extend([(0,2,3,1),(len(v)-4,len(v)-3,len(v)-1,len(v)-2)])
  make_batch('GuardCollision',v,f,'Dark',0,ps)
 save(code+'_Collision')
 print('UPPER_ROUTE',code,round(L,1),flush=True)

if not only:
 reset()
 box('WallMountPlate',0,0,-.045,.30,.54,.06,'Steel',.012)
 for y in [-.205,.205]:
  for x in [-.10,.10]:cyl('MountBolt',(x,y,-.012),(x,y,.01),.016,'Steel',6)
 box('LampHousing',0,0,.05,.24,.44,.14,'Dark',.028)
 box('LuminousRedGlass',0,0,.145,.175,.34,.10,'RedLamp',.035)
 for y in [-.19,.19]:box('LensCap',0,y,.14,.23,.055,.16,'Steel',.01)
 for x in [-.10,0,.10]:
  tube('CageWire',[(x,-.21,.10),(x,-.18,.22),(x,.18,.22),(x,.21,.10)],.009,'Steel')
 for y in [-.12,0,.12]:cyl('CageCrossbar',(-.115,y,.218),(.115,y,.218),.007,'Steel',8)
 cyl('CableGland',(0,-.26,.03),(0,-.32,.03),.025,'Dark',12)
 save('IndustrialRedLamp')
 # Filter headers join existing supply ends, include flanges/valves and support feet.
 reset()
 for z,mat in [(.70,'Steel'),(-.57,'PipeRed')]:
  tube('SupplyReturnHeader',[(-.50,.35 if z>0 else .40,z),(-.50,.22,z),(.50,.22,z),(.50,.35 if z>0 else .40,z)],.065,mat)
  flange(0,.22,z,.065,'x')
  for x in [-.62,.62]:box('SaddleFoot',x,.075,z,.18,.15,.22,'Steel',.008)
 tube('WallReturn',[(.5,.22,-.57),(.76,.22,-.57),(.76,2.55,-.57)],.065,'Steel');flange(.76,1.0,-.57,.065,'y')
 save('FilterHeaders','Props')
 reset()
 # Flanged riser grows out of the existing top outlet; insulated flexible joint.
 for y in [2.57,2.86]:box('DuctFlange',0,y,-.10,1.08,.06,.94,'Steel',.008)
 box('FlexibleConnector',0,2.72,-.10,.94,.28,.80,'Rubber',.014)
 for y in [2.61,2.66,2.71,2.76,2.81]:box('BellowsBand',0,y,-.10,.98,.018,.84,'Dark',.004)
 box('RiserDuct',0,3.32,-.10,.95,.86,.82,'Steel',.018)
 for y in [3.04,3.61]:
  box('DuctCollar',0,y,-.10,1.0,.04,.87,'Steel',.004)
  for x in [-.43,.43]:cyl('CollarBolt',(x,y,.34),(x,y,.375),.015,'Steel',6)
 box('TurningPlenum',0,3.77,-.30,.95,.44,1.22,'Steel',.025)
 box('RearGrille',0,3.77,-.923,.82,.32,.025,'Dark',.003)
 for x in [-.36,-.24,-.12,0,.12,.24,.36]:box('ExhaustSlat',x,3.77,-.94,.025,.30,.03,'Steel',.003)
 save('AirFilterRiser','Props')
 reset()
 for z in [-.49,-.77]:
  tube('DuctFlange',[(1.12*math.cos(math.tau*i/64),1.27+1.12*math.sin(math.tau*i/64),z) for i in range(65)],.04,'Steel')
  for i in range(16):
   a=math.tau*i/16;cyl('FlangeBolt',(1.12*math.cos(a),1.27+1.12*math.sin(a),z-.055),(1.12*math.cos(a),1.27+1.12*math.sin(a),z+.055),.025,'Steel',6)
 for z in [-.54,-.59,-.64,-.69,-.74]:tube('FlexDuctRing',[(1.07*math.cos(math.tau*i/48),1.27+1.07*math.sin(math.tau*i/48),z) for i in range(49)],.035,'Rubber')
 save('FanFlexibleJoint','Props')
 mapping={'BM_WaterFilterSkid':'FilterHeaders','BM_AirFilterSkid':'AirFilterRiser','BM_VentilationFan':'FanFlexibleJoint'}
 for p in layout['placements']:
  if p['model'] in mapping:manifest['addons'].append({'parent':p['name'],'model':mapping[p['model']]})
 # Power/service conduits follow existing cabinets, keeping equipment fronts free.
 for room in layout['rooms']:
  items=[p for p in layout['placements'] if p['room']==room['id'] and p['model'] in ['BM_ElectricalCabinet','BC_PumpDriveCabinet','BM_PowerTransformer']]
  if not items:continue
  reset()
  for p in items:
   old=set(bpy.context.scene.objects);w,h,d=p['size'];z=-d/2+.06
   for x in [-w*.26,w*.26]:
    tube('PowerCable',[(x,max(.20,h*.65),z),(x,h+.10,z),(x,h+.24,z-.06),(x,h+.24,z-.22)],.025,'Rubber')
    for y in [h*.65,h*.85]:box('CableClip',x,y,z,.085,.03,.08,'Steel',.004)
   transform(set(bpy.context.scene.objects)-old,*p['position'],p['yaw'])
  save(room['id']+'_PowerConnections','Props')
  manifest['addons'].append({'room':room['id'],'model':room['id']+'_PowerConnections'})
 (H/'layout.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('B2_DETAIL_READY',flush=True)
