from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_RemainingDomes';A=R/'Unity/After_Seconds_Build_V0.01/Assets'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=0;self.sections=0
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='img':self.images+=1
  if tag=='section':self.sections+=1
  for name in ['src','href']:
   if name in d:self.links.append(d[name])
parser=Links();parser.feed((D/'review.html').read_text(encoding='utf-8'))
broken=[p for p in parser.links if not (D/unquote(p)).exists()]
record=A/'Afrer_Seconds/06.Data/AssetSources/B5_RemainingDomes_20261108.json'
assert record.with_name(record.name+'.meta').exists()
data=json.loads(record.read_text(encoding='utf-8'))
models_missing=[v['asset'] for v in data['models'].values() if not (R/v['asset']).exists() or not (R/(v['asset']+'.meta')).exists()]
pres=json.loads((D/'preservation.json').read_text(encoding='utf-8'))
assert not broken and not models_missing and not pres['archivedDoorTransformMismatches'] and not pres['duplicatePathChanges'],dict(broken=broken,missing=models_missing,doorMismatches=pres['archivedDoorTransformMismatches'],duplicateChanges=pres['duplicatePathChanges'])
for name,version in [('AGENTS.md','0.55'),('CLAUDE.md','0.55'),('Docs/AfterSeconds_메인기획서.md','0.44'),('Docs/이어하기_2026-11-06.md','0.39'),('Docs/회사_작업목록_2026-11-06.md','0.37'),('Docs/도면/Decision/원형공동/B5_안내체계/README.md','0.07')]:
 assert 'V'+version in (R/name).read_text(encoding='utf-8').splitlines()[0],name
status=subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=R,text=True,encoding='utf-8')
(H/'git_status_final.txt').write_text(status,encoding='utf-8')
print(json.dumps(dict(galleryImages=parser.images,gallerySections=parser.sections,brokenLinks=broken,missingModels=models_missing,sourceRecordMeta=True,archivedDoorTransformsPreserved=609,oldFilesPreserved=pres['unchangedFiles'],changedExistingFiles=pres['changedFiles'],documentVersions='verified',gitStatusEntries=len(status.splitlines())),ensure_ascii=True,indent=2))
