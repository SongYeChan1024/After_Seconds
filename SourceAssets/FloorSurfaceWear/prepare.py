from pathlib import Path
import json,hashlib,re
H=Path(__file__).resolve().parent;R=H.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
out={}
for f,y in [('B5',-82),('B4',-66)]:
 rows=read(H/(f+'_renderers.json'));target=[]
 for r in rows:
  asset=r['asset'];stem=Path(asset).stem
  cargo=stem in ['BF_CargoLift','SF_VL_Interior','OD_VL_FreightHoist']
  floor='/Environment/' in asset and re.search('Floor|Vault|FullLayout|Dome|Shell',stem) and any(s['lo']<y+.15 and s['hi']>y-.10 and s['up']>1 and any(k in s['mat'] for k in ['Floor','Shell','Coat']) for s in r['submeshes'])
  if cargo or floor:target.append(dict(id=r['id'],name=r['name'],asset=asset,cargo=cargo))
 out[f]=target
(H/'targets.json').write_text(json.dumps(out,indent=2),encoding='utf8')
baseline=H/'protected_before.json'
if not baseline.exists():
 files=[]
 for root in [R/'Unity/After_Seconds_Build_V0.01/Assets',R/'Unity/After_Seconds_Build_V0.01/ProjectSettings']:
  files += [p for p in root.rglob('*') if p.is_file() and p.suffix in {'.unity','.mat','.cs','.prefab','.controller','.meta','.json','.txt'} and '/Temp/' not in p.as_posix() and not p.name.startswith('FW_')]
 baseline.write_text(json.dumps({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2),encoding='utf8')
print(json.dumps({f:dict(candidates=len(v),cargo=[r['name'] for r in v if r['cargo']]) for f,v in out.items()}))
