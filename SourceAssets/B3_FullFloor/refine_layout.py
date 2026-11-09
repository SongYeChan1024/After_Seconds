from pathlib import Path
import json,math
from shapely.geometry import Polygon,Point,LineString
H=Path(__file__).resolve().parent;plan=json.loads((H/'layout.json').read_text(encoding='utf-8'));cat={x['name']:x for x in json.loads((H/'catalog.json').read_text())};rooms={r['id']:r for r in plan['rooms']}
def turn(x,z,y):
 a=math.radians(y);return x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
def poly(w,d,x,z,yaw):return Polygon([(x+turn(a,b,yaw)[0],z+turn(a,b,yaw)[1]) for a,b in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]])
added=[]
for code,models in {'C01':['BS_SampleRack_1','BS_SampleRack_2','BS_SampleRack_3','BS_SampleRack_1'],'W01':['BS_SampleRack_2','BS_SampleRack_3'],'E03':['BS_SampleRack_3','BS_SampleRack_1'],'E02':['BS_ServerRack_1','BS_ServerRack_2','BS_ServerRack_1','BS_ServerRack_2'],'N01':['BS_AccessionBench','BS_PackingBench']}.items():
 r=rooms[code];blocks=[Polygon(z['polygon']).buffer(.45) for z in plan['zones'] if z['room']==code];routes=[LineString([(0,0),(d['x'],d['z'])]).buffer(1.0) for d in r['doors']]
 for i,n in enumerate(models):
  c=cat[n];w,h,d=c['size'];found=None
  for radius in [r['r']*.45,r['r']*.5,r['r']*.55,r['r']*.6]:
   for k in range(120):
    a=(k*3+i*83)%360;x,z=radius*math.cos(math.radians(a)),radius*math.sin(math.radians(a));yaw=270-a;shape=poly(w,d,x,z,yaw);dx,dz=turn(0,d/2+.55,yaw);apron=poly(w,1.1,x+dx,z+dz,yaw)
    if shape.intersects(Point(0,0).buffer(1.1)) or any(shape.intersects(q) for q in routes+blocks) or any(apron.intersects(q) for q in blocks):continue
    found=(x,z,yaw,shape,apron);break
   if found:break
  if not found:raise RuntimeError('No central storage bay '+code+str(i))
  x,z,yaw,shape,apron=found;blocks.extend([shape.buffer(.45),apron.buffer(.10)]);cx,cy,cz=c['center'];dx,dz=turn(cx,cz,yaw);name='B3_'+code+'_Central'+n.split('_',1)[1]+'_'+str(i+1)
  q=dict(room=code,name=name,model=n,asset=c['asset'],position=[x-dx,0,z-dz],yaw=yaw,size=c['size'],center=c['center'],meshCollider=False,role='StorageIsland');plan['placements'].append(q);added.append(q);plan['zones'].append(dict(room=code,name=name,center=[x,z],size=[w,d],yaw=yaw,polygon=list(shape.exterior.coords)[:-1]));dx,dz=turn(cx,cz+d/2+.57,yaw);plan['workspaces'].append(dict(room=code,name=name,point=[q['position'][0]+dx,0,q['position'][2]+dz]))
for code in ['C04','C05','N01']:
 r=rooms[code];rad=r['r'];c=cat['BP_WallSafety_R'+str(rad)];blocks=[Polygon(z['polygon']).buffer(.12) for z in plan['zones'] if z['room']==code];found=None
 for a in range(0,360,2):
  if any(abs((a-d['angle']+180)%360-180)<math.degrees(math.asin(3.1/rad)) for d in r['doors']):continue
  rr=math.sqrt(rad*rad-2.13**2)-.20;x,z=rr*math.cos(math.radians(a)),rr*math.sin(math.radians(a));yaw=270-a;dx,dz=turn(0,.21,yaw);shape=poly(1.34,.44,x+dx,z+dz,yaw);ax,az=turn(0,1.05,yaw);apron=poly(1.3,.80,x+ax,z+az,yaw)
  if any(shape.intersects(q) or apron.intersects(q) for q in blocks):continue
  found=(x,z,yaw,x+ax,z+az);break
 if not found:raise RuntimeError('Wall safety has no clear approach '+code)
 x,z,yaw,ax,az=found;q=dict(room=code,name='B3_'+code+'_WallSafety',model=c['name'],asset=c['asset'],position=[x,0,z],yaw=yaw,size=[1.34,1.82,.44],center=[0,1.19,.21],meshCollider=False,role='WallSafety');added.append(q);plan['placements'].append(q);plan['workspaces'].append(dict(room=code,name=q['name'],point=[ax,0,az]))
(H/'refine_additions.json').write_text(json.dumps(added,indent=2));(H/'layout.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8');print('Added storage and wall safety',len(added))
