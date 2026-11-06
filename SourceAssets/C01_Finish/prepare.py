from pathlib import Path
import hashlib, json, os, shutil, datetime
R=Path(__file__).resolve().parents[2]
P=R/'Unity/After_Seconds_Build_V0.01'
H=Path(__file__).resolve().parent
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup=Path(os.environ['TEMP'])/('AfterSeconds_C01Finish_'+stamp)
files=[P/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity',R/'SourceAssets/B5_FullLayout/AF_C01_ThreePortalRibs.blend']
files+=list((P/'Assets/Afrer_Seconds/05.Model/Environment/B5').glob('AF_C01_ThreePortalRibs.fbx*'))
for p in files:
    target=backup/p.relative_to(R); target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
protected={str(p.relative_to(R)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'Assets').rglob('*') if p.is_file() and (p.suffix in ['.cs','.controller','.overrideController'] or (p.suffix=='.unity' and p!=files[0]))}
(H/'protected_before.json').write_text(json.dumps(protected,indent=2),encoding='utf-8')
(H/'backup_location.txt').write_text(str(backup),encoding='utf-8')
print(json.dumps({'backup':str(backup),'protected':len(protected)}))
