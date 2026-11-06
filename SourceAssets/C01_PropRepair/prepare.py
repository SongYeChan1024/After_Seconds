"""사용자 피드백 후 수정 전 백업. 작성자: 송예찬."""
from pathlib import Path
import os,datetime,shutil,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/05.Model/Props/B5';O=R/'Docs/검수/2026-11-07_C01_PropRepair';O.mkdir(exist_ok=True)
if (H/'baseline.json').exists():raise RuntimeError('Baseline already exists')
B=Path(os.environ['TEMP'])/('AfterSeconds_PropRepair_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));B.mkdir()
files=[]
for d in ['C01_Perimeter','C01_InstrumentDetail','C01_PropFinish']:
 files.extend(p for p in (H.parent/d).rglob('*') if p.is_file())
files.extend(p for p in P.rglob('*') if p.is_file() and p.name.startswith(('CP_','ID_','PF_')))
scene=R/'Unity/After_Seconds_Build_V0.01/Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity';files.append(scene)
for p in files:
 dst=B/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
base=json.loads((H.parent/'C01_PropFinish/baseline.json').read_text('utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(H/'baseline.json').write_text(json.dumps({'backup':str(B),'files':len(files),'protected':base['protected'],'sceneHash':sha(scene),'modelHashes':{p.name:sha(p) for p in P.glob('*.fbx') if p.name.startswith(('CP_','ID_'))}},indent=2),encoding='utf-8')
for f in ['FinalAudit.cs','Audit.cs','FinishAudit.cs']:
 txt=(H.parent/'C01_PropFinish'/f).read_text('utf-8').replace('2026-11-07_C01_PropFinish','2026-11-07_C01_PropRepair').replace('SourceAssets/C01_PropFinish/','SourceAssets/C01_PropRepair/').replace('C01_PropFinish_20261107.json','C01_PropRepair_20261107.json');(H/f).write_text(txt,encoding='utf-8')
print(json.dumps({'backup':str(B),'files':len(files)}))
