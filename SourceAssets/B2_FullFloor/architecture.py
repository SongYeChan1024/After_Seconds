import sys,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
plan=json.loads((H/'plan.json').read_text(encoding='utf8'));rooms={r['id']:r for r in plan['rooms']};ts=plan['tunnels']
for r in plan['rooms']:
 code=r['id'];rad=r['r'];core=r['kind']=='core';local=[]
 for t in ts:
  if code not in [t['a'],t['b']]:continue
  q=copy.deepcopy(t);q['path']=[[p[0]-r['x'],p[1]-r['v']] for p in t['path']];q['p']=q['path'][0];q['q']=q['path'][-1];local.append(q)
 reset();shell_mats()
 if core:
  o=cyl('ShaftOuter',(0,-.2,0),(0,21.2,0),rad+.22,'Coat',96);cut(o,cyl('ShaftVoid',(0,-.5,0),(0,21,0),rad,'Dark',96))
 else:
  o=env['sphere']('DomeOuter',0,0,rad+.22);o.data.materials.append(b.mats['Coat']);cut(o,env['sphere']('DomeVoid',0,0,rad));cut(o,env['box']('BaseCut',0,-rad,0,rad*3,rad*2,rad*3,'Shell',0))
 for t in local:cut(o,sweep('DoorVoid',t,extend=4))
 for p in o.data.polygons:p.use_smooth=True
 o.data.set_sharp_from_angle(angle=math.radians(20));be=o.modifiers.new('OpeningBevel','BEVEL');be.width=.008;be.segments=3;be.limit_method='ANGLE';o['bevel_width_m']=.008;save(code+'_Shell')
 if code!='C02':
  reset();cyl('Floor',(0,-.24,0),(0,0,0),rad-.005,'Floor',128);save(code+'_Floor')
 reset()
 def clear(a,y):return y>=4.03 or all(abs((a-d['angle']+180)%360-180)>math.degrees(math.asin(min(.95,3.05/rad))) for d in r['doors'])
 if not core:
  for i in range(48):
   a=i*7.5+3.75
   for lo,hi in [(.03,1.3),(1.32,2.64),(2.66,4.0),(4.03,rad*.73),(rad*.73+.02,rad*.87),(rad*.87+.02,rad-.07)]:
    if hi<=lo or hi>=rad or not clear(a,lo):continue
    sphere_patch('SteelLiner',math.radians(i*7.5+.08),math.radians((i+1)*7.5-.08),math.asin(lo/rad),math.asin(hi/rad),rad-.05,rad-.025,'Coat',2,3)
  for a in range(0,360,45):sphere_patch('DomeRib',math.radians(a-.48),math.radians(a+.48),.004 if clear(a,0) else math.asin(4.1/rad),1.5,rad-.16,rad-.06,'Steel',1,24)
  for y in [4.15,rad*.8]:
   p=math.asin(y/rad);sphere_patch('DomeRing',0,math.tau,p-.006,p+.006,rad-.15,rad-.06,'Steel',96,1)
 else:
  for y in [4.15,8.1,12.1,16.1,20.2]:ringtube('ShaftRing',4.90,y,0,360,.045)
  for a in range(0,360,15):
   t=math.radians(a);cyl('ShaftSeam',(4.96*math.cos(t),4.05,4.96*math.sin(t)),(4.96*math.cos(t),20.9,4.96*math.sin(t)),.007,'Dark',6)
 for i in range(72):
  if clear(i*5+2.5,0):sector('Skirting',rad-.15,rad+.10,-.01,.13,i*5,(i+1)*5,'Steel',2,.003)
 save(code+'_Lining')
 if code!='C02':
  reset();y=4.25;rr=4.85 if core else math.sqrt(rad*rad-y*y)-.18
  for yy in [y,y+.16]:ringtube('ServiceConduit',rr,yy,0,360,.025)
  for a in range(15,360,60):
   if not clear(a,2):continue
   t=math.radians(a);rad2=4.85 if core else math.sqrt(rad*rad-2.5**2)-.2;old=set(bpy.context.scene.objects);vent(0,2.5,0,.75,.27);box('VentBox',0,2.5,-.04,.82,.34,.09,'Dark',.008);transform(set(bpy.context.scene.objects)-old,rad2*math.cos(t),0,rad2*math.sin(t),270-a)
  save(code+'_Services')
 print('ROOM',code,flush=True)
for t in ts:
 code=t['id'].split('-')[1];ps=path_points(t);length=sum((bb-aa).length for aa,bb in zip(ps,ps[1:]))
 reset();o=sweep('CircularSteelShell',t,2.68,2.50);floor=ribbon('WalkFloor',t)
 for rid in [t['a'],t['b']]:
  r=rooms[rid];c=env['sphere']('RoomTrim',r['x'],r['v'],r['r']) if r['kind']!='core' else cyl('CoreTrim',(r['x'],-2,-r['v']),(r['x'],6,-r['v']),r['r'],'Dark',96);cut(o,c);cut(floor,cyl('FloorTrim',(r['x'],-1,-r['v']),(r['x'],1,-r['v']),r['r']-.005,'Dark',128))
 save(code+'_Shell')
 reset()
 for dist in [1.35+i*3.2 for i in range(max(1,int((length-2.7)/3.2)+1))]:
  if dist>length-1.2:continue
  p,dir=at(ps,dist);yaw=math.degrees(math.atan2(dir.x,dir.z));old=set(bpy.context.scene.objects)
  # Rings follow the inside of the pipe; lower arc is below the flat walking deck.
  for i in range(64):
   a0=math.tau*i/64;a1=math.tau*(i+1)/64;vs=[]
   for z in [-.065,.065]:
    for rr in [2.41,2.51]:
     for a in [a0,a1]:vs.append((rr*math.cos(a),1.35+rr*math.sin(a),z))
   mesh('FlangeSegment',vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],'Steel',.004)
  for j in range(24):
   a=math.tau*j/24;x,y=2.46*math.cos(a),1.35+2.46*math.sin(a)
   if y<.08:continue
   cyl('FlangeFastener',(x,y,-.083),(x,y,.083),.025,'Steel',6)
  transform(set(bpy.context.scene.objects)-old,p.x,0,p.z,yaw)
 # Physical longitudinal utility pipes and gutter grates, following curved paths.
 for side in [-1,1]:
  rights=frames(ps)
  for y,lateral,rad in [(1.38,2.34,.055),(1.62,2.30,.075),(2.65,1.94,.035)]:
   pp=[tuple(p+rr*side*lateral+Vector((0,y,0))) for p,rr in zip(ps,rights)];tube('ProcessLine',pp,rad,'PipeRed' if y==1.62 else 'Steel')
  pp=[tuple(p+rr*side*1.98+Vector((0,.025,0))) for p,rr in zip(ps,rights)];tube('EdgeDrain',pp,.045,'Dark')
 for dist in [2.1+i*4 for i in range(int((length-2)/4))]:
  p,di=at(ps,dist);old=set(bpy.context.scene.objects)
  for sign in [-1,1]:
   for y in [1.4,2.66]:box('PipeClamp',sign*(2.35 if y<2 else 1.95),y,0,.08,.18,.075,'Steel',.006)
  transform(set(bpy.context.scene.objects)-old,p.x,0,p.z,math.degrees(math.atan2(di.x,di.z)))
 save(code+'_Finish');print('PIPE TUNNEL',code,flush=True)
# Use the verified stair fabrication with the B2 -> B1 rise of 16m.
src=(R/'SourceAssets/B3_FullFloor/architecture.py').read_text(encoding='utf8');src=src[src.index('reset();rise=15/8'):]
src=src.replace('rise=15/8','rise=16/8').replace('x,7.5,z,.14,15,.14','x,8,z,.14,16,.14').replace('14.92','15.92').replace('15.002','16.002').replace('(x,15,z),(x,16.08,z)','(x,16,z),(x,17.08,z)').replace('[(16.08,.032),(15.54,.018)]','[(17.08,.032),(16.54,.018)]');exec(src)
