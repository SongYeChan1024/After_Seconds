from pathlib import Path
import json,numpy as np
H=Path(__file__).resolve().parent;R=H.parents[1];p=json.loads((H/'plan.json').read_text(encoding='utf-8'));s=json.loads((H/'survey.json').read_text(encoding='utf-8'))
def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
def segment_distance(a,b):
 aa=a[:-1,None,:];bb=b[None,:-1,:];u=np.diff(a,axis=0)[:,None,:];v=np.diff(b,axis=0)[None,:,:];w=bb-aa;det=cross(u,v)
 valid=np.abs(det)>1e-10;div=np.where(valid,det,1);t=cross(w,v)/div;q=cross(w,u)/div
 if np.any(valid&(t>=0)&(t<=1)&(q>=0)&(q<=1)):return 0.
 def pointseg(pt,start,delta):
  f=np.clip(((pt-start)*delta).sum(axis=-1)/(delta*delta).sum(axis=-1),0,1);return np.linalg.norm(pt-start-delta*f[...,None],axis=-1).min()
 return float(min(pointseg(aa,bb,v),pointseg(aa+u,bb,v),pointseg(bb,aa,u),pointseg(bb+v,aa,u)))
routes=p['routes'];pairs=[]
for i,a in enumerate(routes):
 for b in routes[i+1:]:
  if a['code']==b['code']:continue
  dist=segment_distance(np.array(a['points']),np.array(b['points']));pairs.append(dict(a=a['id'],b=b['id'],lineClearance=dist-.10,markerClearance=dist-.20))
labels=[]
for g in s['guides']:
 name=g['path'].split('/')[-1]
 if not ('FloorCodes' in name or name.startswith('T01_C') or name.startswith('SC_Destination')):continue
 vs=np.array([[v[0],v[2]] for v in g['vertices']])
 for i in range(0,len(vs),4):labels.append((name,np.array([vs[i],vs[i+1],vs[i+3],vs[i+2],vs[i]])))
x,z=p['legend']['position'];w=p['legend']['width']/2;h=p['legend']['length']/2
labels.append(('DestinationLegend',np.array([[x-w,z-h],[x+w,z-h],[x+w,z+h],[x-w,z+h],[x-w,z-h]])))
x,z=p['labLegend']['position'];w=p['labLegend']['width']/2;h=p['labLegend']['length']/2
labels.append(('LabLegend',np.array([[x-w,z-h],[x+w,z-h],[x+w,z+h],[x-w,z+h],[x-w,z-h]])))
labelchecks=[]
for route in routes:
 a=np.array(route['points'])
 for name,poly in labels:
  # Convex quadrilateral interior is a collision even if no boundary crossing occurs.
  signs=np.array([cross(b-a0,a-a0) for a0,b in zip(poly,poly[1:])]);inside=np.any(np.all(signs>=-1e-9,axis=0)|np.all(signs<=1e-9,axis=0))
  dist=0 if inside else segment_distance(a,poly)
  labelchecks.append(dict(route=route['id'],label=name,clearance=dist-.10))
old=[]
for g in s['guides']:
 if not g['path'].endswith('CW_S1_FloorRoute'):continue
 vs=np.array([[v[0],v[2]] for v in g['vertices']]);mid=(vs[::2]+vs[1::2])*.5
 for route in routes:old.append(dict(route=route['id'],label='retained S1',clearance=segment_distance(np.array(route['points']),mid)-.145))
result=dict(pairs=pairs,labelChecks=labelchecks,retainedRouteChecks=old,minLineClearance=min(r['lineClearance'] for r in pairs),minMarkerClearance=min(r['markerClearance'] for r in pairs),minLabelClearance=min(r['clearance'] for r in labelchecks),minS1Clearance=min(r['clearance'] for r in old))
(R/'Docs/검수/2026-11-08_B5_DestinationColors/spacing.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if not isinstance(v,list)}));print(json.dumps([c for c in labelchecks if c['clearance']<.06]))
assert result['minMarkerClearance']>.10 and result['minLabelClearance']>.04 and result['minS1Clearance']>.08
