from pathlib import Path
import subprocess,json,time,sys,shutil
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/검수/2026-11-08_B5_CeilingLighting'
CLI=Path('C:/Users/Administrator/AppData/Local/Unity/bin/unity.exe')
def run(*args):
 p=subprocess.run([str(CLI),'command',*args,'--caller','plugin','--skill','unity-cli','--project-path',str(P),'--format','json'],capture_output=True,text=True,encoding='utf-8',timeout=45)
 d=json.loads(p.stdout)
 if p.returncode or not d.get('success'):raise RuntimeError(p.stdout)
 result=d['data']['result']
 if isinstance(result,dict) and result.get('success') is False:raise RuntimeError(result)
 return result
def ready():
 for attempt in range(6):
  p=subprocess.run([str(CLI),'status','--until-ready','--project-path',str(P),'--format','json'],capture_output=True,text=True,encoding='utf-8',timeout=45)
  if not p.returncode:return
  if not any(t in p.stdout for t in ['Hold on...','Reloading Domain','Importing assets','Reload Script Assemblies','EDITOR_NOT_RUNNING','EDITOR_NOT_READY']):raise RuntimeError(p.stdout)
  time.sleep(3)
 raise RuntimeError(p.stdout)
summary=[]
try:
 run('editor','set_auto_tick','--enable','true','--interval_ms','16','--persist','false')
 run('editor.playmode','set_run_in_background','--enable','true')
 if run('editor','status')['playMode']!='playing':run('editor.playmode','start')
 ready()
 run('editor','set_auto_tick','--enable','true','--interval_ms','16','--persist','false')
 cases=[('LabCeiling','lab_ceiling'),('CoolingCeiling','cooling_ceiling')] if '--ceilings' in sys.argv else [('Lab','lab'),('Cooling','cooling'),('Isolation','isolation'),('Control','control'),('Corridor','corridor')]
 if '--final-lab' in sys.argv:cases=[('Lab','lab'),('LabCeiling','lab_ceiling')]
 for method,label in cases:
  dest=O/f'play_{label}.json'
  if dest.exists():raise RuntimeError('Avoid overwriting existing play verification')
  result=run('script','run',str(R/'SourceAssets/B5_CeilingLighting/Play.cs'),'--entry','CeilingPlay.'+method)
  print(json.dumps(result,ensure_ascii=False),flush=True)
  time.sleep(3)
  temp=P/'Temp/B5_CeilingLighting'/f'play_{label}.png'
  temp.parent.mkdir(parents=True,exist_ok=True)
  shot=run('capture','game_view','--source','screen','--save_path',temp.relative_to(P).as_posix())
  print(json.dumps(shot,ensure_ascii=False),flush=True)
  shutil.copy2(P/shot['savedPath'],O/temp.name)
  limit=time.monotonic()+20
  while not dest.exists() and time.monotonic()<limit:time.sleep(.3)
  if not dest.exists():raise RuntimeError('Play measurement did not complete')
  d=json.loads(dest.read_text(encoding='utf-8'))
  assert d['complete'] and d['framesAdvanced']>20 and d['displacement']>.15 and not d['errors'],d
  summary.append(d)
  print(json.dumps({k:d[k] for k in ['label','framesAdvanced','displacement','medianMs','p95Ms','errors']}),flush=True)
finally:
 ready()
 run('editor.playmode','stop')
 ready()
 run('editor.playmode','set_run_in_background','--enable','false')
 run('editor','set_auto_tick','--enable','false','--persist','false')
if '--final-lab' in sys.argv:
 for filename,label in [('play_summary.json','lab'),('play_ceiling_summary.json','lab_ceiling')]:
  p=O/filename;old=json.loads(p.read_text(encoding='utf-8'));updated=next(x for x in summary if x['label']==label)
  p.write_text(json.dumps([updated if x['label']==label else x for x in old],ensure_ascii=False,indent=2),encoding='utf-8')
else:
 (O/('play_ceiling_summary.json' if '--ceilings' in sys.argv else 'play_summary.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
