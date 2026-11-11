from pathlib import Path
import json,numpy as np
H=Path(__file__).parent
shots=json.loads((H/'shots.json').read_text())
for p in sorted((H/'results').glob('*.json')):
 d=json.loads(p.read_text());rows=d['rows'];choices=[]
 if 'Circular' in p.stem:
  choices=[a for a in d['overlaps'] if a['a']==a['b'] and 'Stair' in rows[a['a']]['path']][:1]
 else:choices=d['overlaps'][:1]
 if choices:
  a=choices[0];at=np.array(a['point']);n=np.array(a['normal']);pos=at+n*2+np.array([.35,.6,.15])
 elif d['internal']:
  a=d['internal'][0];at=np.array(a['point']);n=np.array(a['normal']);pos=at+n*2+np.array([.3,.5,.2])
 else:
  ri=next((i for i,r in enumerate(rows) if r['asset'] in {v['asset'] for v in d['duplicateMeshes']} and not r['skinned']),None)
  if ri is None:continue
  r=rows[ri];at=(np.array(r['bmin'])+np.array(r['bmax']))/2;size=np.array(r['bmax'])-np.array(r['bmin']);pos=at+np.array([.3,max(.7,size[1]*.4),max(1.5,size[2]*.75)])
 name=p.stem+'_detail'
 if not any(s['name']==name for s in shots):shots.append(dict(scene=d['scene'],name=name,position=pos.tolist(),target=at.tolist()))
(H/'shots.json').write_text(json.dumps(shots,indent=2))
print('Shots',len(shots))
