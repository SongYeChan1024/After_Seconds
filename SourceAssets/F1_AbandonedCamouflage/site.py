"""Native Terrain input and reproducible landscape masks; preserve the three basement arrivals."""
from pathlib import Path
import sys,json,struct,math
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';sys.path.insert(0,str(U/'Temp/ZFightingReview/deps'))
import numpy as np,shapely
from shapely.geometry import box,LineString,Point
from shapely.ops import unary_union
p=json.loads((H/'before_layout.json').read_text(encoding='utf8'));roompolys=[box(*r['bounds']) for r in p['rooms']];hallpolys=[LineString(t['path']).buffer(t['w']/2,cap_style=2,join_style=2) for t in p['tunnels']];interior=unary_union(roompolys+hallpolys)
origin=(-192,-6,-160);size=(384,28,320);res=513
def height(x,z):
 x=np.asarray(x);z=np.asarray(z);d=np.maximum(abs(x)/80,abs(z)/62);outer=np.clip((d-.83)/1.2,0,1)
 waves=np.sin(x*.041+z*.016)*2+np.sin(z*.055-x*.02)*1.4+np.cos(x*.073+z*.032)*1.1
 hills=(4.8+waves)*outer**1.5
 ground=-.18+np.sin(x*.16)*np.cos(z*.11)*.10+np.sin(x*.31+z*.24)*.025
 ditch=-.48*np.exp(-((z+45)/4)**2)*np.exp(-((x+20)/60)**2)
 # Quiet, slightly sunken approach with wheel ruts; no perfectly flat infinite paving plane.
 roadz=-28-.035*(-51-x);roadweight=np.exp(-((z-roadz)/5.5)**4)*np.clip((-x-42)/12,0,1)
 road=-.12-np.clip((-x-60)/140,0,1)*.8+np.sin(x*.17)*.045
 y=(ground+hills+ditch)*(1-roadweight)+road*roadweight
 return y
xs=np.linspace(origin[0],origin[0]+size[0],res);zs=np.linspace(origin[2],origin[2]+size[2],res);xx,zz=np.meshgrid(xs,zs);ys=height(xx,zz)
inside=shapely.contains_xy(interior.buffer(.12),xx,zz);ys[inside]=-.24
hh=((ys-origin[1])/size[1]).astype('<f4');ar=128;ax,az=np.meshgrid(np.linspace(-192,192,ar),np.linspace(-160,160,ar));dist=np.maximum(abs(ax)/78,abs(az)/58);trackz=-28-.035*(-51-ax);road=np.exp(-((az-trackz)/5.5)**4)*np.clip((-ax-42)/12,0,1)
green=np.clip(.30+(dist-.65)*.4+.22*np.sin(ax*.09)*np.cos(az*.12)+.13*np.sin(ax*.21+az*.08),.08,.82)*(1-road*.94);gravel=np.clip(.43-road*.2-green*.3,0,.65);earth=1-green-gravel;alpha=np.stack([earth,gravel,green],2).astype('<f4');alpha=np.clip(alpha,0,1);alpha/=alpha.sum(2,keepdims=True)
hx,hz=np.meshgrid((xs[:-1]+xs[1:])/2,(zs[:-1]+zs[1:])/2);holes=(~shapely.contains_xy(interior.buffer(-.65),hx,hz)).astype(np.uint8)
with (H/'terrain.bin').open('wb') as f:f.write(struct.pack('<ii',res,ar));f.write(hh.tobytes());f.write(alpha.tobytes());f.write(holes.tobytes())
tri=[list(t.exterior.coords)[:3] for t in shapely.constrained_delaunay_triangles(interior).geoms]
# Scatter excludes indoor floors, the clear approach, core exits and a pedestrian corridor to the road.
rng=np.random.default_rng(1206);tufts=[];bushes=[];rubble=[];exclusion=interior.buffer(.55)
for i in range(3400):
 x=rng.uniform(-100,80);z=rng.uniform(-64,58)
 if exclusion.contains(Point(x,z)):continue
 if x<-48 and abs(z-(-28-.035*(-51-x)))<2.2:continue
 # Group growth along wall bases, fence edges and cracks, with bare patches.
 distance=interior.distance(Point(x,z));cluster=(math.sin(x*.32)+math.cos(z*.42)+math.sin((x+z)*.19))/3
 if distance>10 and cluster<.18:continue
 tufts.append([x,float(height(x,z)),z,float(rng.uniform(.30,.85)),int(rng.integers(0,3))])
for i in range(150):
 x=rng.uniform(-100,85);z=rng.uniform(-65,60)
 if exclusion.buffer(1.4).contains(Point(x,z)) or (x<-47 and abs(z+28)<6):continue
 bushes.append([x,float(height(x,z)),z,float(rng.uniform(.65,1.6)),int(rng.integers(0,3))])
plan=dict(version='V0.01',author='송예찬',source='Docs/Reference/1F',terrain=dict(origin=origin,size=size,resolution=res,alphaResolution=ar,holesResolution=res-1),floorTriangles=tri,grass=tufts,bushes=bushes,rooms=p['rooms'],tunnels=p['tunnels'],walls=p['walls'],arrivals=p['arrivals'],out=p['out'])
(H/'site.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8');print({'grassTufts':len(tufts),'bushes':len(bushes),'floorTriangles':len(tri),'terrainBytes':(H/'terrain.bin').stat().st_size},flush=True)
