"""Sequence: irregular apertures -> thick edges -> attached bent remnants -> export scoped roofs/floor."""
from pathlib import Path
import sys,os,json,math,random
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_20261113/deps'))
sys.path.insert(0,str(H))
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from meshlib import Model
OUT=Path(os.environ['LOCALAPPDATA'])/'Temp/AfterSeconds_20261113/candidate';OUT.mkdir(parents=True,exist_ok=True)
plan=json.loads((H.parent/'F1_AbandonedCamouflage/site.json').read_text(encoding='utf8'));original=json.loads((H.parent/'F1_FullFloor/plan.json').read_text(encoding='utf8'))
rng=random.Random(13112026);reports=[]
def jagged(x,z,rx,rz,n=25):
 return Polygon([(x+rx*(f:=rng.uniform(.77,1.18))*math.cos(i*math.tau/n),z+rz*f*math.sin(i*math.tau/n)) for i in range(n)]).buffer(0)
def remnants(m,hole,height,metal=True):
 pieces=[hole] if hole.geom_type=='Polygon' else list(hole.geoms)
 for p in pieces:
  q=list(p.exterior.coords);cx,cz=p.centroid.coords[0]
  for i in range(0,len(q)-1,3 if metal else 2):
   a,b=q[i],q[i+1];mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2;dx,dz=cx-mx,cz-mz;length=math.hypot(dx,dz);dx/=length;dz/=length
   if metal:
    reach=rng.uniform(.4,1.2);drop=rng.uniform(.25,1.05);y=height(mx,mz)
    pts=[(a[0],height(*a),a[1]),(b[0],height(*b),b[1]),(b[0]+dx*reach*.55,y-drop*.35,b[1]+dz*reach*.55),(mx+dx*reach,y-drop,mz+dz*reach),(a[0]+dx*reach*.45,y-drop*.55,a[1]+dz*reach*.45)]
    m.bent(pts,.035)
   else:
    y=height(mx,mz)-.10;reach=rng.uniform(.42,.9);m.tube([(mx-dx*.13,y,mz-dz*.13),(mx+dx*reach*.65,y-.02,mz+dz*reach*.65),(mx+dx*reach,y-rng.uniform(.06,.23),mz+dz*reach)],.014,'Corrosion',6)
for room in plan['rooms']:
 key=room['id']
 if not key.startswith('C'):continue
 x,z,w,d=[room[k] for k in ('x','z','w','d')];outer=box(x-w/2,z-d/2,x+w/2,z+d/2);m=Model('AE_'+key+'_Roof');metal=key in ('C01','C02')
 if metal:
  h,rise=(9,2.35) if key=='C01' else (7.3,1.8)
  height=lambda xx,zz:h+rise*(1-abs(xx-x)/(w/2))+.13
  specs=[(x+w*.28,z-d*.23,w*.25,d*.28),(x-.5,z+d*.22,w*.095,d*.18),(x-w*.27,z-d*.04,w*.10,d*.12),(x+w*.17,z+d*.40,w*.13,d*.14)]
 else:
  height=lambda xx,zz:room['h']+.18
  specs=[(x-w*.32,z+d*.11,w*.16,d*.17),(x+w*.12,z-d*.12,w*.155,d*.15)]
 holes=unary_union([jagged(*spec) for spec in specs]).intersection(outer);surface=outer.difference(holes)
 if metal:
  # Split at the ridge so no cap triangle bridges the two roof slopes.
  for side in [box(x-w/2,z-d/2,x,z+d/2),box(x,z-d/2,x+w/2,z+d/2)]:m.slab(surface.intersection(side),height,.045)
  for i in range(1,int(w/.42)):
   xx=x-w/2+i*.42;clip=LineString([(xx,z-d/2),(xx,z+d/2)]).intersection(surface)
   for line in ([clip] if clip.geom_type=='LineString' else getattr(clip,'geoms',[])):
    if line.geom_type!='LineString' or line.length<.08:continue
    a,b=line.coords[0],line.coords[-1];m.beam((a[0],height(*a)+.015,a[1]),(b[0],height(*b)+.015,b[1]),.023,'Corrosion',6)
  for zz in [z-d/2,z+d/2]:m.add([(x-w/2,h,zz),(x+w/2,h,zz),(x,h+rise,zz)],[(0,1,2)],'Plaster')
 else:
  m.slab(surface,height,.18,'Concrete')
  for xx in [x-w/2,x+w/2]:m.box((xx,room['h']+.28,z),(.14,.25,d),'Concrete')
 remnants(m,holes,height,metal);r=m.export(OUT);r['openingArea']=holes.area;r['roofArea']=outer.area;reports.append(r)
for tunnel in plan['tunnels']:
 key=tunnel['id'];m=Model('AE_'+key+'_Roof');area=0;holesArea=0
 for q in original['corridorRoofs']:
  if q['room']!=key:continue
  polygon=Polygon(q['points']);cx,cz=polygon.centroid.coords[0];inner=[]
  coords=list(polygon.exterior.coords)
  for a,b in zip(coords,coords[1:]):
   n=max(2,round(math.dist(a,b)/.6))
   for i in range(n):
    t=i/n;xx=a[0]+(b[0]-a[0])*t;zz=a[1]+(b[1]-a[1])*t;k=rng.uniform(.39,.63);inner.append((cx+(xx-cx)*k,cz+(zz-cz)*k))
  hole=Polygon(inner).buffer(0).intersection(polygon.buffer(-.2));surface=polygon.difference(hole);m.slab(surface,lambda x,z:3.56,.045);remnants(m,hole,lambda x,z:3.56,True);area+=polygon.area;holesArea+=hole.area
  for a,b in zip(coords,coords[1:]):m.beam((a[0],3.50,a[1]),(b[0],3.50,b[1]),.045)
 r=m.export(OUT);r.update(openingArea=holesArea,roofArea=area);reports.append(r)
# Cut only the two new vertical circulation openings from the present floor footprint.
floor=unary_union([Polygon(t) for t in plan['floorTriangles']]);floor=floor.difference(box(42.06,-31.05,45.94,-24.70)).difference(box(41.55,26.15,46.45,32.15))
m=Model('AE_InteriorFloor')
from shapely import constrained_delaunay_triangles
for t in constrained_delaunay_triangles(floor).geoms:m.add([(x,0,z) for x,z in list(t.exterior.coords)[:3]],[(0,2,1)],'Concrete')
reports.append(m.export(OUT))
# The lift head extends through the previously repaired VL roof; VA and VB stay intact.
m=Model('AE_VL_Roof');surface=box(39.01,23.01,48.99,32.99).difference(box(41.15,25.65,46.85,32.35));m.slab(surface,lambda x,z:4.78,.18,'Concrete')
for xx in [39,49]:m.box((xx,4.88,28),(.14,.25,10),'Concrete')
reports.append(m.export(OUT));(H/'roof_models.json').write_text(json.dumps(reports,indent=2),encoding='utf8');print('ROOFS',len(reports),sum(r['triangles'] for r in reports),flush=True)
