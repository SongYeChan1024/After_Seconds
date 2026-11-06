"""B3 specimen floor V0.01. Authored bevel geometry, plan-based multiple routes."""
import bpy,json,math
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent;REPOSITORY=HERE.parents[1]
helper=REPOSITORY/'SourceAssets/LevelContinuation/build_sections.py'
exec(compile(helper.read_text(encoding='utf-8').split("for floor in ('B5','B4'):")[0],str(helper),'exec'))
SRC=HERE;REPO=REPOSITORY
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC'
plan=next(f for f in json.loads((REPO/'Docs/도면/잠입_탐색/layout.json').read_text(encoding='utf-8-sig'))['floors'] if f['floor']=='B3')
heights={r['id']:4.8 if r['id'] in ('A','B') else 4.4 if r['id'] in ('D','HVAC','LIFT') else 4 for r in plan['rooms']}
def tile_area(name,x,y,w,d):
 box('Floor_'+name,x+w/2,-.12,y+d/2,w,.24,d,'Floor',True)
 for i in range(math.ceil(w/2)):
  for j in range(math.ceil(d/2)):
   pw=min(2,w-i*2);pd=min(2,d-j*2);box('FloorFinish_'+name,x+i*2+pw/2,.004,y+j*2+pd/2,pw-.012,.012,pd-.012,'Floor',False,.002)
for r in plan['rooms']:
 u,v,w,d=[r[k] for k in ('x','y','w','h')];rid=r['id'];h=heights[rid]
 if rid=='B':
  for area in [(u,v,w,3),(u,7,5,3),(30,7,6,3),(u,10,w,4)]:tile_area(rid,*area)
 elif rid=='STB':tile_area(rid,43.5,18,4.5,6.96)
 else:tile_area(rid,u,v,w,d)
 for i in range(math.ceil(w/2)):
  for j in range(math.ceil(d/2)):
   pw=min(2,w-i*2);pd=min(2,d-j*2);box('Ceiling_'+rid,u+i*2+pw/2,h+.08,v+j*2+pd/2,pw-.01,.16,pd-.01,'Ceiling')
 cols=max(1,math.ceil(w/6));rows=max(1,math.ceil(d/6))
 for i in range(cols):
  for j in range(rows):
   x=u+(i+.5)*w/cols;z=v+(j+.5)*d/rows
   if rid=='STB' and z>24.5:continue
   box('LightBody_'+rid,x,h-.15,z,1.2,.09,.26,'Graphite');box('LightLens_'+rid,x,h-.205,z,1.07,.018,.15,'Lamp',False,.002)
   lightdefs.append(dict(name='Ceiling_'+rid,position=[x-24,h-.30,z-16],target=[x-24,0,z-16],intensity=18.0 if h<4.5 else 24.0,range=h+3,angle=120))
edges=defaultdict(list)
for r in plan['rooms']:
 u,v,w,d=[r[k] for k in ('x','y','w','h')]
 for axis,c,a,b in [('H',v,u,u+w),('H',v+d,u,u+w),('V',u,v,v+d),('V',u+w,v,v+d)]:edges[(axis,c)].append((a,b,r['id']))
for (axis,c),owners in edges.items():
 doors=[d for d in plan['doors'] if d['axis']==axis and abs((d['y'] if axis=='H' else d['x'])-c)<.001];cuts=set(p for a,b,_ in owners for p in (a,b))
 for d in doors:
  q=d['x'] if axis=='H' else d['y'];cuts.update((q-.75,q+.75))
 for a,b in zip(sorted(cuts),sorted(cuts)[1:]):
  mid=(a+b)/2;rooms=[n for l,h,n in owners if l<mid<h]
  if not rooms:continue
  top=max(heights[n] for n in rooms);opening=any(abs(mid-(d['x'] if axis=='H' else d['y']))<.749 for d in doors);bottom=2.8 if opening else 0
  u,v=(mid,c) if axis=='H' else (c,mid);w,d=(b-a,.22) if axis=='H' else (.22,b-a)
  box('WallCore_'+axis,u,(bottom+top)/2,v,w,top-bottom,d,'Core',True)
  mat='WallClean' if any(n in ('D','SUP2','SUP4') for n in rooms) else 'WallSteel' if any(n in ('B','HVAC','STA','STB','LIFT') for n in rooms) else 'WallStaff'
  cols=max(1,math.ceil((b-a)/1.5));rows=max(1,math.ceil((top-bottom)/2))
  for side in (-1,1):
   for i in range(cols):
    along=a+(i+.5)*(b-a)/cols
    for j in range(rows):
     pu,pv=(along,c+side*.123) if axis=='H' else (c+side*.123,along);pw,pd=((b-a)/cols-.012,.026) if axis=='H' else (.026,(b-a)/cols-.012)
     box('WallFacing',pu,bottom+(j+.5)*(top-bottom)/rows,pv,pw,(top-bottom)/rows-.012,pd,mat)
   if not opening:
    pu,pv=(mid,c+side*.143) if axis=='H' else (c+side*.143,mid);pw,pd=(b-a-.012,.014) if axis=='H' else (.014,b-a-.012)
    box('WallPlinth',pu,.14,pv,pw,.18,pd,'Plinth');box('WallStripe',pu,1.2,pv,pw,.035,pd,'Teal' if mat=='WallClean' else 'SafetyPaint',False,.002)
# Shelving follows the six obstacle footprints exactly; no boxes spill into the aisles.
for index,r in enumerate([b for b in plan['blocks'] if b['name']=='시료 랙']):
 u=r['x'];v=r['y'];w=r['w'];d=r['h'];box('RackPlinth',u+w/2,.07,v+d/2,w,.14,d,'Graphite',True)
 for x in (u+.045,u+w-.045):
  for z in (v+.05,v+d/2,v+d-.05):box('RackUpright',x,1.45,z,.07,2.9,.07,'Stainless')
 for h in (.18,.95,1.72,2.49):
  box('ShelfDeck',u+w/2,h,v+d/2,w-.08,.055,d-.06,'Stainless')
  for x in (u+.03,u+w-.03):box('ShelfLip',x,h+.065,v+d/2,.035,.10,d-.06,'Graphite')
  for bay in range(6):
   z=v+.42+bay*.82
   for side in (0,1):
    x=u+.39+side*.72;box('SealedSpecimenCrate',x,h+.23,z,.62,.39,.68,'Coating' if (bay+side+index)%3 else 'Teal',False,.012)
    box('SpecimenCrateLid',x,h+.43,z,.64,.035,.70,'Graphite');box('SpecimenCrateLatch',x,h+.28,z+.347,.14,.06,.014,'Stainless')
 colliders.append(dict(name='Rack_Obstacle_'+str(index),center=[u+w/2-24,1.45,v+d/2-16],size=[w,2.9,d]))
# Wash pit has actual depth, retaining walls and guards.
box('WashPitBase',28.5,-1.32,8.5,3.0,.24,3.0,'Core',True)
for v in (7,10):box('WashPitWall',28.5,-.6,v,3,1.2,.16,'WallSteel',True);rail(27.05,29.95,v,.0)
for u in (27,30):
 box('WashPitWall',u,-.6,8.5,.16,1.2,3,'WallSteel',True)
 for h in (.52,1.05):box('WashPitRail',u,h,8.5,.04,.04,2.9,'Stainless')
 for v in (7.1,8.5,9.9):box('WashPitPost',u,.52,v,.04,1.04,.04,'Stainless')
 colliders.append(dict(name='WashPitBarrier',center=[u-24,.55,8.5-16],size=[.08,1.1,3]))
for i in range(5):box('PitDrain',28.5,-1.19,7.4+i*.55,2.55,.02,.045,'Graphite')
# Inspection island and corridor sight-line screens.
box('InspectionIsland',29.5,.46,19.5,5,.92,1,'Coating',True,.012);box('InspectionSurface',29.5,.945,19.5,5.02,.05,1.02,'Stainless')
for b in plan['blocks']:
 if b['kind']=='baffle':box('CorridorScreen',b['x']+b['w']/2,1.65,b['y']+b['h']/2,b['w'],3.3,b['h'],'WallStaff',True,.012)
# Descending B4 shaft, geometrically aligned with the previous floor.
copy_stairs('B',-6.4);nosings('B',-6.4);stairlights('B',-6.4)
box('LowerFloor_B',45.75,-6.52,21.48,4.5,.24,6.96,'Floor',True)
wall(43.5,18,32,-6.4,0,[]);wall(48,18,32,-6.4,0,[])
box('LowerShaft_B',45.75,-3.2,32,4.5,6.4,.22,'WallSteel',True)
# North wall has a closed return portal at B4 elevation.
for u,w in ((44.375,1.75),(47.375,1.25)):box('ReturnShaft_B',u,-3.2,18,w,6.4,.22,'WallSteel',True)
box('ReturnShaft_B',46,-1.8,18,1.5,3.6,.22,'WallSteel',True)
rail(45.7,47.7,24.88,0)
# Freight cabin is a stationary art destination; travel controls remain unimplemented.
box('LiftPlatform',43.5,-.025,11,3.4,.05,3.6,'Stainless',True)
for u in (41.78,45.22):box('LiftSide',u,1.5,11,.12,3,3.6,'WallSteel',True)
box('LiftBack',43.5,1.5,12.8,3.56,3,.12,'WallSteel',True);box('LiftCanopy',43.5,3.05,11,3.56,.10,3.6,'Graphite')
for u in (41.88,45.12):box('LiftProtectionRail',u,1,11,.08,.12,3.3,'Stainless')
box('LiftLamp',43.5,2.97,11,1.1,.025,.2,'Lamp')
lightdefs.append(dict(name='LiftInterior',position=[19.5,2.7,-5],target=[19.5,0,-5],intensity=14.0,range=4,angle=110))
export('B3',[])
(SRC/'plan_snapshot.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('B3_DONE',json.dumps({k:v for k,v in reports[-1].items() if k not in ('colliders','lights')}))
