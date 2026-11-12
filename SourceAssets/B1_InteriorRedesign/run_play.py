from pathlib import Path
import sys,time,json,subprocess
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'SourceAssets/ZFightingReview'))
from drive import invoke,CLI,PROJECT
def ready():
 for attempt in range(25):
  p=subprocess.run([str(CLI),'status','--until-ready','--project-path',str(PROJECT),'--format','json'],capture_output=True,text=True,encoding='utf8',timeout=30)
  d=json.loads(p.stdout)
  if p.returncode==0 and any(x.get('state')=='ready' for x in (d.get('data') or {}).get('instances',[])):
   print('Editor ready',flush=True);return
  time.sleep(1)
 raise RuntimeError('Editor did not become ready: '+p.stdout)
previous=invoke('script','eval','return UnityEngine.Application.runInBackground;')['result']
try:
 print(invoke('editor.playmode','set_run_in_background','--enable','true'),flush=True)
 print(invoke('editor.playmode','start'),flush=True);ready()
 for method in (sys.argv[1:] or ['C01','C02','C03','C04','C05','W01','W02','W03','E01','E02','E03','N01','S01']):
  print(json.dumps(invoke('script','run',H/'Play.cs','--entry','B1InteriorPlay.'+method,'--args','[]')),flush=True)
  time.sleep(8.7)
  p=R/'Docs/Review/2026-11-12_B1_Interior'/('play_'+method+'.json');d=json.loads(p.read_text())
  print(json.dumps({k:d[k] for k in ['label','complete','framesAdvanced','displacement','rise','errors']}),flush=True)
  assert d['complete'] and d['framesAdvanced']>10 and d['displacement']>.3 and not d['errors'],method
finally:
 ready();print(invoke('editor.playmode','stop'),flush=True);ready()
 print(invoke('editor.playmode','set_run_in_background','--enable',str(previous).lower()),flush=True)
