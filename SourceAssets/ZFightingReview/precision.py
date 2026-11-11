from drive import *
import hashlib
H=ROOT/'SourceAssets/ZFightingReview'
plans=[json.loads(p.read_text()) for p in sorted((H/'precision_plans').glob('*.json'))]
hashfile=H/'protected_before_precision.json'
if not hashfile.exists():hashfile.write_text(json.dumps({p['scene']:hashlib.sha256((PROJECT/p['scene']).read_bytes()).hexdigest() for p in plans},indent=2))
for p in plans:
    name=Path(p['scene']).stem
    if not p['patches'] or (H/f'applied_precision_{name}.json').exists():continue
    print(json.dumps(invoke('script','run',H/'Apply.cs','--entry','ZFApply.Precision','--args',json.dumps([name])),ensure_ascii=False),flush=True)
    print(json.dumps(invoke('script','run',H/'Export.cs','--entry','ZFExport.Run','--args',json.dumps([p['scene']])),ensure_ascii=False),flush=True)
print(invoke('scene','open','Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity'))
