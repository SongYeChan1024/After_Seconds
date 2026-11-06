"""실험동 문 상부 타일 보수 준비. 작성자: 송예찬."""
from pathlib import Path
import json,hashlib,shutil,tempfile,datetime
H=Path(__file__).resolve().parent;R=H.parents[1];U=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-07_C01_PortalTiles';O.mkdir(exist_ok=True)
if (H/'baseline.json').exists():raise SystemExit('Baseline exists; do not overwrite')
backup=Path(tempfile.gettempdir())/('AfterSeconds_PortalTiles_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
scene=U/'Assets/Afrer_Seconds/01.Scenes/Stage/Level_B5_Circular.unity';shutil.copy2(scene,backup/scene.name)
prior=json.loads((R/'SourceAssets/C01_Doors/baseline.json').read_text('utf-8'))
paths=[R/p for p in prior['protected']]
paths+=list((U/'Assets/Afrer_Seconds/05.Model/Environment/B5').glob('CDR*'))+list((U/'Assets/Afrer_Seconds/05.Model/Environment/B5/Materials').glob('CDR*'))
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
for p in (U/'Assets/Afrer_Seconds/05.Model').rglob('*.mat'):
 dst=backup/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
(H/'baseline.json').write_text(json.dumps(dict(backup=str(backup),protected=hashes,scene=str(scene.relative_to(R)),sceneHash=hashlib.sha256(scene.read_bytes()).hexdigest()),indent=2),encoding='utf-8')
text=(R/'SourceAssets/C01_Doors/Capture.cs').read_text('utf-8').replace('2026-11-07_C01_Doors','2026-11-07_C01_PortalTiles').replace('LabDoorCapture','PortalTileCapture').replace('if(prefix=="After")','if(prefix=="ClosedReview")')
(H/'Capture.cs').write_text(text,encoding='utf-8')
print(json.dumps(dict(backup=str(backup),protected=len(hashes))))
