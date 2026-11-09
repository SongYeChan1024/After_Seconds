from pathlib import Path
import json,math,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01'
(R/'Docs/Review/2026-11-09_B3_FullFloor').mkdir(parents=True,exist_ok=True)
if (H/'plan.json').exists():raise RuntimeError('Already prepared')
d=json.loads(next((R/'Docs').glob('**/Decision/**/facility_layout.json')).read_text(encoding='utf-8'));f=next(x for x in d['floors'] if x['id']=='B3')
for r in f['rooms']:
 r['doors']=[]
 for t in f['tunnels']:
  if r['id'] not in [t['a'],t['b']]:continue
  p=t['p'] if t['a']==r['id'] else t['q'];r['doors'].append(dict(id=t['id'],x=p[0]-r['x'],z=-p[1]+r['v'],angle=math.degrees(math.atan2(-p[1]+r['v'],p[0]-r['x']))))
f['circuits']=[x for x in d['light_circuits'] if x['id'].startswith('B3-')];f['sourceVersion']=d['version'];f['sourcePlacements']=[x for x in d['placements'] if x['floor']=='B3'];f['art']=d['floor_art_direction']['B3']
(H/'plan.json').write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding='utf-8')
for cat in ['Props','Environment']:
 for sub in ['','Materials','Textures']:(U/'Assets/Afrer_Seconds/05.Model'/cat/'B3'/sub).mkdir(parents=True,exist_ok=True)
s=(R/'SourceAssets/B4_FullFloor/architecture.py').read_text(encoding='utf-8').replace(" if r['id']=='C01':continue\n",'').replace(" if t['id']=='B4-T02':continue\n",'').replace("if code=='C02':","if False:").replace('B4-T02','B3-T02').replace('rise=17/8','rise=15/8').replace("x,8.5,z,.14,17,.14","x,7.5,z,.14,15,.14").replace('16.92','14.92').replace('17.002','15.002').replace('(x,17,z),(x,18.08,z)','(x,15,z),(x,16.08,z)').replace('[(18.08,.032),(17.54,.018)]','[(16.08,.032),(15.54,.018)]')
(H/'architecture.py').write_text(s,encoding='utf-8')
print('B3',len(f['rooms']),'rooms',len(f['tunnels']),'corridors')
