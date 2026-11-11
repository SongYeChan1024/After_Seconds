from drive import *
H=ROOT/'SourceAssets/ZFightingReview'
for p in sorted((H/'plans').glob('*.json')):
 if (H/('applied_'+p.name)).exists():continue
 if not json.loads(p.read_text())['patches']:continue
 r=invoke('script','run',H/'Apply.cs','--entry','ZFApply.Run','--args',json.dumps([p.stem]))
 print(json.dumps(r,ensure_ascii=False),flush=True)
print(invoke('scene','open','Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity'),flush=True)
