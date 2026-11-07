from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_SpatialRefinement';A=R/'Unity/After_Seconds_Build_V0.01/Assets'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=0;self.sections=0;self.anchors=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images+=1
  if tag=='section':self.sections+=1
  if 'id' in a:self.anchors.add(a['id'])
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
x=Links();x.feed((D/'review.html').read_text(encoding='utf8'));broken=[p for p in x.links if (p.startswith('#') and p[1:] not in x.anchors) or (not p.startswith('#') and not (D/unquote(p)).exists())]
record=A/'Afrer_Seconds/06.Data/AssetSources/B5_SpatialRefinement_20261108.json';data=json.loads(record.read_text(encoding='utf8'));missing=[k for k,v in data['models'].items() if not (R/v['asset']).exists() or not (R/(v['asset']+'.meta')).exists() or not (H/(k+'.blend')).exists()];assert not broken and not missing and record.with_name(record.name+'.meta').exists(),(broken,missing)
versions=[('AGENTS.md','0.56'),('CLAUDE.md','0.56'),('Docs/AfterSeconds_메인기획서.md','0.45'),('Docs/이어하기_2026-11-06.md','0.40'),('Docs/회사_작업목록_2026-11-06.md','0.38'),('Docs/도면/Decision/원형공동/B5_안내체계/README.md','0.08')]
for f,v in versions:assert ('V'+v) in (R/f).read_text(encoding='utf8').splitlines()[0],f
post=json.loads((D/'post_play.json').read_text(encoding='utf8'));assert not post['dirty'] and post['runInBackground'] is False
status=subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=R,encoding='utf8');(H/'git_status_final.txt').write_text(status,encoding='utf8')
result=dict(galleryImages=x.images,gallerySections=x.sections,brokenLinks=broken,models=len(data['models']),missingModels=missing,sourceRecordMeta=True,documentVersions='verified',editSceneSaved=True,player=post['player'],gitStatusEntries=len(status.splitlines()),committedOrPushed=False)
(D/'delivery.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
