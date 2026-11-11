from drive import *
import hashlib
H=ROOT/'SourceAssets/ZFightingReview'
hashes={p.relative_to(PROJECT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (PROJECT/'Assets/Afrer_Seconds/01.Scenes').rglob('*.unity')}
q=H/'protected_before_second.json'
if not q.exists():q.write_text(json.dumps(hashes,indent=2))
for p in sorted((H/'residual2').glob('*.json')):
 if (H/('applied_second_'+p.name)).exists():continue
 r=invoke('script','run',H/'Apply.cs','--entry','ZFApply.Residual','--args',json.dumps([p.stem]))
 print(json.dumps(r),flush=True)
print(invoke('scene','open','Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity'),flush=True)
