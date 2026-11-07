import json,ast
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];p=json.loads((H/'guidance.json').read_text(encoding='utf-8'))
t=ast.parse((R/'SourceAssets/T02_StairA/verify_plan.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'distance','exec'))
def simplify(a):
 out=[a[0]]
 for i in range(1,len(a)-1):
  if abs(cross(a[i]-a[i-1],a[i+1]-a[i]))>1e-7:out.append(a[i])
 out.append(a[-1]);return np.array(out)
routes=[(r,simplify(np.array(r['points']))) for r in p['routes']];pairs=[];labels=[]
for i,(r,a) in enumerate(routes):
 for s,b in routes[i+1:]:
  if r['code']==s['code'] or np.any(a.max(axis=0)+.6<b.min(axis=0)) or np.any(b.max(axis=0)+.6<a.min(axis=0)):continue
  d=segment_distance(a,b);pairs.append(dict(a=r['id'],b=s['id'],lineClearance=d-.1,markerClearance=d-.20))
 for l in p['labels']:
  v=np.array(l['position']);f=np.array(l['forward']);right=np.array([f[1],-f[0]]);w=l['width']/2;h=l['length']/2;b=np.array([v+right*x+f*z for x,z in [(-w,-h),(w,-h),(w,h),(-w,h),(-w,-h)]])
  if np.any(a.max(axis=0)+.5<b.min(axis=0)) or np.any(b.max(axis=0)+.5<a.min(axis=0)):continue
  d=segment_distance(a,b);labels.append(dict(route=r['id'],label=l['id'],clearance=d-.1))
result=dict(pairs=pairs,labels=labels,minMarkerClearance=min(q['markerClearance'] for q in pairs),minLabelClearance=min(q['clearance'] for q in labels));(H/'guide_spacing.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('min',result['minMarkerClearance'],result['minLabelClearance']);print([x for x in pairs if x['markerClearance']<.035]);print([x for x in labels if x['clearance']<.04])
