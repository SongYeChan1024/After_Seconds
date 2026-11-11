"""Verify deliverable links and that every saved scene mesh asset still exists."""
from pathlib import Path
import json
from html.parser import HTMLParser
H=Path(__file__).parent;ROOT=H.parents[1];P=ROOT/'Unity/After_Seconds_Build_V0.01';O=ROOT/'Docs/Review/2026-11-11_ZFighting'
errors=[]
for path in (P/'Temp/ZFightingReview').glob('*.json'):
    d=json.loads(path.read_text())
    for row in d.get('rows',[]):
        if row['asset'].startswith('Assets/') and not (P/row['asset']).exists():errors.append(row['asset'])
class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for k,v in attrs:
            if k in ('href','src') and not (O/v).resolve().exists():errors.append(v)
Links().feed((O/'review.html').read_text(encoding='utf-8'))
res=json.loads((H/'residual_summary.json').read_text());assert res['nontrivialInteriorOverlaps']==0
assert len(res['scenes'])==15
assert not errors,errors
shots=json.loads((H/'shots.json').read_text());assert all((O/('after_'+s['name']+'.png')).exists() for s in shots)
print(json.dumps(dict(savedSceneMeshFilesPresent=True,reportLinksValid=True,sceneCount=15,interiorResidualsBeyondTolerance=0,afterImages=len(shots))))
