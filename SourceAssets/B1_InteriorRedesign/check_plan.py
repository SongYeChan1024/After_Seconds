from pathlib import Path
import sys,json,math
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'Unity/After_Seconds_Build_V0.01/Temp/ZFightingReview/deps'))
from shapely.geometry import box,LineString,Point
from shapely.affinity import rotate,translate
p=json.loads((H/'layout.json').read_text(encoding='utf8'));rooms={r['id']:r for r in p['rooms']};obs={}
for q in p['placements']:
 if q['model']=='BL_HandheldRecorder':continue
 w,_,d=q['size'];c=q['center'];g=box(c[0]-w/2,c[2]-d/2,c[0]+w/2,c[2]+d/2)
 g=translate(rotate(g,-q['yaw'],origin=(0,0)),q['position'][0],q['position'][2]);obs.setdefault(q['room'],[]).append((q['name'],g,'furniture'))
for w in p['interior']['walls']:
 obs.setdefault(w['room'],[]).append((w['name'],LineString([w['a'],w['b']]).buffer(w['th']/2,cap_style='flat'),'wall'))
errors=[]
for room,items in obs.items():
 for i,(n,g,t) in enumerate(items):
  for nn,gg,tt in items[i+1:]:
   area=g.intersection(gg).area
   if area>.012:errors.append(dict(room=room,a=n,b=nn,area=round(area,3)))
print(json.dumps(errors,indent=2));(H/'plan_overlap_candidates.json').write_text(json.dumps(errors,indent=2))
print('candidates',len(errors))
