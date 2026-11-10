import json,math,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(R/'SourceAssets/B2_FullFloor'))
from common import *
H=Path(__file__).resolve().parent;b.H=H;b.manifest=json.loads((H/'models.json').read_text());C=json.loads((H/'layout.json').read_text(encoding='utf8'))
for id in ['E01','E02','W02','C02']:
 reset();room=next(r for r in C['rooms'] if r['id']==id);center=Vector((room['x'],0,-room['v']))
 for t in C['tunnels']:
  if id not in C['ends'][t['id']]:continue
  ps=[Vector((p[0],0,-p[1])) for p in t['path']];start=t['a']==id;di=(ps[1]-ps[0]).normalized() if start else (ps[-1]-ps[-2]).normalized();p=ps[0] if start else ps[-1];inside=di*(-1 if start else 1);right=Vector((di.z,0,-di.x))
  for side,y,rad,mat in [(-1.30,2.95,.15,'Steel'),(1.30,2.90,.12,'PipeRed')]:
   a=p+right*side+inside*2+Vector((0,y+2.5,0))-center
   if id=='C02':
    x=4.2 if side<0 else 3.9;target=(x,3.2 if side<0 else 2.95,6.15)
    pp=[tuple(a),(a.x,5.8,a.z),(x,5.8,6.15),target]
   else:
    target=(-3.4 if a.x<0 else 3.4,6.05,-.6 if side<0 else .6)
    pp=[tuple(a),(a.x*.85,5.85,a.z*.85),target]
   tube('ConnectedDomeProcessLine',pp,rad,mat)
 # Blanked inspection ends make unused branches explicit; no floating open tube ends.
 if id!='C02':
  for x in [-3.4,3.4]:
   for z in [-.6,.6]:flange(x,6.05,z,.13,'x')
 b.OUT=b.A/'Environment/B2';b.raw_export('BN_'+id+'_HeaderLinks');b.manifest['BN_'+id+'_HeaderLinks']['category']='Environment'
(H/'models.json').write_text(json.dumps(b.manifest,indent=2),encoding='utf8')
print('HEADER_LINKS_READY',flush=True)
