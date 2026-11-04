"""저장된 씬과 보호 파일을 대조하고 중복 셔터 리브 근접 사진을 임시 보관한다."""
import json,hashlib,re,shutil
from pathlib import Path
from collections import Counter
REPO=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
TMP=REPO/'tmp/WallFrameRepair_20261104'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
protected=read(TMP/'protected_before.json');changes=[]
for item in protected:
 p=REPO/item['path']
 if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest().upper()!=item['hash'].upper():changes.append(item['path'])
assert not changes,changes

def normalize(text):
 # 허용된 차이는 MeshFilter의 직접 참조와 해당 프리팹 override뿐이다.
 text=re.sub(r'^  m_Mesh:.*\n','',text,flags=re.M)
 text=re.sub(r'^    - target:.*\n      propertyPath: m_Mesh\n      value:.*\n      objectReference:.*\n','',text,flags=re.M)
 return '\n'.join(line.rstrip() for line in text.splitlines())
scenes=[]
for item in read(TMP/'scenes_before.json'):
 p=REPO/item['path'];before=TMP/'scenes-before'/p.name
 same=hashlib.sha256(p.read_bytes()).hexdigest().upper()==item['hash'].upper()
 only_mesh=normalize(before.read_text(encoding='utf-8-sig'))==normalize(p.read_text(encoding='utf-8-sig'))
 scenes.append({'scene':item['path'],'byteIdentical':same,'onlyVisualMeshReferencesChanged':only_mesh})
 if not only_mesh:
  import difflib
  (TMP/(p.stem+'_unexpected.diff')).write_text('\n'.join(difflib.unified_diff(normalize(before.read_text(encoding='utf-8-sig')).splitlines(),normalize(p.read_text(encoding='utf-8-sig')).splitlines())),encoding='utf-8')
assert all(x['onlyVisualMeshReferencesChanged'] for x in scenes),scenes

photos=read(OUT/'photos.json');archive=TMP/'omitted-redundant-shutter-closeups';archive.mkdir(exist_ok=True)
retained=[]
for shot in photos:
 if shot['kind']=='opening' and shot['owner'].endswith('/Shutter_Rib'):
  for phase in ('before','after'):
   p=OUT/(shot['name']+'_'+phase+'.png')
   if p.exists():p.replace(archive/p.name)
 else:retained.append(shot)
if len(retained)!=len(photos):
 write(TMP/'photos_including_redundant_closeups.json',photos);write(OUT/'photos.json',retained)
 old=TMP/'superseded-contacts';old.mkdir(exist_ok=True)
 for p in OUT.glob('*_Review_*.jpg'):p.replace(old/p.name)

for name in ('overlaps_before.json','remaining_overlaps.json','trim_manifest.json'):
 shutil.copy2(TMP/name,OUT/name)
application=read(OUT/'application.json');before=read(OUT/'overlaps_before.json');after=read(OUT/'remaining_overlaps.json')
assert after['count']==0,after
assert all(x['uv2Preserved'] for x in application)
assert all(x['transformsCollidersAndBehavioursPreserved'] and x['missingMeshes']==0 for x in read(OUT/'preservation.json'))
validation=read(OUT/'mesh_validation.json');assert len(validation)==len(application) and all(x['valid'] for x in validation)
summary={'protectedFilesChecked':len(protected),'protectedFileChanges':changes,'sceneChanges':scenes,'repairedVisualInstances':len(application),'byFloor':dict(Counter(next(x['floor'] for x in read(TMP/'trim_manifest.json') if x['id']==a['instanceId']) for a in application)),'overlapPairsBefore':before['count'],'overlapPairsAfter':after['count'],'trianglesCheckedBefore':before['trianglesChecked'],'trianglesCheckedAfter':after['trianglesChecked'],'derivedTrianglesBefore':sum(x['trianglesBefore'] for x in application),'derivedTrianglesAfter':sum(x['trianglesAfter'] for x in application),'emptyVisualMeshes':sum(x['emptyVisual'] for x in validation),'retainedCameraViews':len(retained),'retainedScreenshots':len(retained)*2,'removedDuplicateSurfaceArea':sum(x['removedArea'] for x in application)}
write(OUT/'final_verification.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
