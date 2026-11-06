from pathlib import Path
import json,hashlib,shutil,os,datetime
R=Path(__file__).resolve().parents[2];H=Path(__file__).resolve().parent;P=R/'Unity/After_Seconds_Build_V0.01';A=P/'Assets/Afrer_Seconds'
backup=Path(os.environ['TEMP'])/('AfterSeconds_PropFinish_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
files=[A/'01.Scenes/Stage/Level_B5_Circular.unity']
for folder in ['SourceAssets/C01_Perimeter','SourceAssets/C01_InstrumentDetail']:
 files.extend(p for p in (R/folder).rglob('*') if p.is_file())
files.extend(p for p in (A/'05.Model/Props/B5').rglob('*') if p.is_file() and (p.name.startswith('CP_') or p.name.startswith('ID_')))
for p in files:
 dst=backup/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
base=json.loads((R/'SourceAssets/C01_Perimeter/baseline.json').read_text('utf-8'))['protected']
guids={str(p.relative_to(R)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (A/'05.Model/Props/B5').glob('*.fbx.meta') if p.name.startswith(('CP_','ID_'))}
(H/'baseline.json').write_text(json.dumps({'backup':str(backup),'protected':base,'modelMetaBefore':guids,'backedUpFiles':len(files)},indent=2),encoding='utf-8')
O=R/'Docs/검수/2026-11-07_C01_PropFinish';O.mkdir(exist_ok=True)
for p in (R/'Docs/검수/2026-11-07_C01_InstrumentDetail').glob('After_*.png'):shutil.copy2(p,O/p.name.replace('After_','Before_'))
print(json.dumps({'backup':str(backup),'files':len(files),'modelGUIDs':len(guids)}))
