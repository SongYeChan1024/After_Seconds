from pathlib import Path
import sys,time,json
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'SourceAssets/ZFightingReview'))
from drive import invoke
for method in (sys.argv[1:] or ['W03','W02','E01','N01','C04','Corridor','Stairs']):
 print(json.dumps(invoke('script','run',H/'Play.cs','--entry','B1Play.'+method,'--args','[]')),flush=True)
 time.sleep(8.7)
 p=R/'Docs/Review/2026-11-11_B1_FullFloor'/('before_play_'+method+'.json');d=json.loads(p.read_text())
 print(json.dumps({k:d[k] for k in ['label','complete','framesAdvanced','displacement','rise','medianMs','errors']}),flush=True)
 if not d['complete'] or d['framesAdvanced']<10 or d['displacement']<.3 or d['errors']:raise RuntimeError('Play check failed '+method)
print('B1 PLAY CHECKS COMPLETE',flush=True)
