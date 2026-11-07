import json,hashlib,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];A=R/'Unity/After_Seconds_Build_V0.01/Assets';D=R/'Docs/검수/2026-11-08_B5_SpatialRefinement'
load=lambda p:json.loads(p.read_text(encoding='utf8'))
base=load(H/'assets_before.json');changed=[];missing=[];same=0
for name,digest in base.items():
 p=A/name
 if not p.exists():missing.append(name)
 elif hashlib.file_digest(p.open('rb'),'sha256').hexdigest()!=digest:changed.append(name)
 else:same+=1
before=load(D/'before.json');after=load(D/'verification.json');oldlights=before['lights'];newlights=after['lights'];oldcounter=collections.Counter(json.dumps(x,sort_keys=True) for x in oldlights);newcounter=collections.Counter(json.dumps(x,sort_keys=True) for x in newlights);lightchanges=[json.loads(x) for x in (oldcounter-newcounter).elements()]
protected=[x for x in before['hierarchy'] if 'C01' in x['path'] and 'DestinationGuidance' not in x['path'] and 'Destination_Colour' not in x['path']]
current=collections.defaultdict(list)
for x in after['hierarchy']:current[x['path']].append(x)
c01=[x['path'] for x in protected if x not in current[x['path']]]
plan=load(H/'plan.json');audit=load(D/'audit.json');byname={p['name']:p for p in audit['placements']};mismatch=[]
for p in plan['placements']:
 q=byname.get(p['id'])
 if q is None or max(abs(a-b) for a,b in zip(p['position'],q['position']))>.001 or abs((p['yaw']-q['yaw']+180)%360-180)>.01:mismatch.append(p['id'])
allowed=['Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity','Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular/OcclusionCullingData.asset']
result=dict(author='송예찬',baselineFiles=len(base),unchangedFiles=same,changedFiles=[p.replace('\\','/') for p in changed],missingFiles=missing,unexpectedChanges=[p for p in changed if p.replace('\\','/') not in allowed],existingLights=len(oldlights),existingLightChanges=lightchanges,addedLights=len(newlights)-len(oldlights),protectedC01Transforms=len(protected),protectedC01TransformChanges=c01,plannedPlacements=len(plan['placements']),placementMismatches=mismatch,activeDetailedPropPlacements=len([p for p in audit['placements'] if '/Props/' in p['asset']]))
(D/'preservation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=True,indent=2));assert not(missing or result['unexpectedChanges'] or lightchanges or c01 or mismatch)
