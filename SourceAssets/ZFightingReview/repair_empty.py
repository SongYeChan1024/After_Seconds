from drive import *
H=ROOT/'SourceAssets/ZFightingReview'
for p in sorted(H.glob('applied_Level*.json')):
 if not any(x['afterTriangles']==0 for x in json.loads(p.read_text())['records']):continue
 name=p.stem[len('applied_'):]
 print(json.dumps(invoke('script','run',H/'Apply.cs','--entry','ZFApply.RepairEmpty','--args',json.dumps([name]))),flush=True)
print(invoke('scene','open','Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity'),flush=True)
