"""Preserve current uncommitted C02 assets and create isolated review tools. 송예찬."""
from pathlib import Path
import json,hashlib,shutil,tempfile,datetime
H=Path(__file__).resolve().parent;R=H.parents[1];S=R/'SourceAssets/C02_Security';O=R/'Docs/검수/2026-11-08_C02_Refine';O.mkdir(parents=True,exist_ok=True)
A=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds'
if (H/'baseline.json').exists():raise SystemExit('Baseline already exists')
backup=Path(tempfile.gettempdir())/('AfterSeconds_C02_Refine_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
files={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in A.rglob('*') if p.is_file()}
(H/'baseline.json').write_text(json.dumps(files,indent=2),encoding='utf-8')
for p in list(A.rglob('SC_*'))+list(S.glob('*')):
 if not p.is_file():continue
 dest=backup/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
(H/'asset_backup.json').write_text(json.dumps({'backup':str(backup)},indent=2),encoding='utf-8')
for name in ['Prepare','Inspect','Capture','Audit','Walk','Play','PlayCapture','Restore']:
 p=S/(name+'.cs');s=p.read_text(encoding='utf-8').replace('2026-11-08_C02_Security','2026-11-08_C02_Refine').replace('AfterSeconds_C02_','AfterSeconds_C02_Refine_')
 s=s.replace('C02'+name,'C02Refine'+name).replace('PlayC02','PlayC02Refine')
 if name=='Audit':
  s=s.replace('if(path.Contains("/Door_B5-T02_2/")||path.Contains("/Door_B5-T05_9/")||path.EndsWith("/B5-12_P14")||path.EndsWith("/B5-15_P11"))continue;','')
 if name=='Capture':
  s=s.replace('var shots=new[]{','var shots=new[]{new{name="MonitorFront",p=new Vector3(-.15f,1.40f,3.0f),t=new Vector3(-1.25f,1.22f,4.20f),fov=53f},new{name="MonitorBack",p=new Vector3(-2.6f,1.65f,4.9f),t=new Vector3(-1.25f,1.16f,4.2f),fov=65f},')
 (H/(name+'.cs')).write_text(s,encoding='utf-8')
print(json.dumps({'backup':str(backup),'assetBaseline':len(files)},ensure_ascii=True))
