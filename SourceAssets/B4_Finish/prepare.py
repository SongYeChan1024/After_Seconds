from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/Review/2026-11-09_B4_Finish';O.mkdir(parents=True,exist_ok=True)
if not (H/'protected_before.json').exists():
 paths=[p for d in ['Assets','ProjectSettings'] for p in (U/d).rglob('*') if p.is_file() and '/Temp/' not in p.as_posix() and p.suffix.lower() in ['.unity','.mat','.asset','.cs','.prefab','.controller','.meta','.json','.txt','.fbx','.png']]
 hashes={}
 for p in paths:
  with p.open('rb') as f:hashes[p.relative_to(R).as_posix()]=hashlib.file_digest(f,'sha256').hexdigest()
 (H/'protected_before.json').write_text(json.dumps(hashes,indent=2),encoding='utf8')
for src,dest,old,new in [('B4_LabIdentity/Capture.cs','Capture.cs','LabIdentityCapture','FinishCapture'),('FloorSurfaceWear/Capture.cs','FloorCapture.cs','FloorWearCapture','FinishFloorCapture'),('B4_LabIdentity/Play.cs','Play.cs','LabPlay','FinishPlay')]:
 s=(R/'SourceAssets'/src).read_text(encoding='utf8').replace(old,new).replace('2026-11-09_B4_LabIdentity','2026-11-09_B4_Finish').replace('2026-11-09_FloorSurfaceWear','2026-11-09_B4_Finish')
 if dest=='Play.cs':s=s.replace('"play_"+label','(File.Exists(O+"after.marker")?"after_play_":"before_play_")+label')
 if dest=='Capture.cs':s=s.replace('renderPostProcessing=false','renderPostProcessing=true')
 (H/dest).write_text(s,encoding='utf8')
print('Prepared finish baseline')
