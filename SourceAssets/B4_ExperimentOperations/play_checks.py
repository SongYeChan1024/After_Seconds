from pathlib import Path
import json,subprocess,time,shutil,sys
R=Path(__file__).resolve().parents[2];O=R/'Docs/검수/2026-11-08_B4_ExperimentOperations';P=R/'Unity/After_Seconds_Build_V0.01'
def cli(*args):
 p=subprocess.run(['python','-X','utf8',str(R/'SourceAssets/B4_StealthLayout/unity_task.py'),*args],cwd=R,capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return json.loads(p.stdout)
for code in (sys.argv[1:] or ['C02','C04','W01','W02','W03','E01','E02','E03','N01','S01','VA','VL']):
 path=O/f'play_{code}.json';previous=path.stat().st_mtime_ns if path.exists() else 0
 if previous:shutil.copy2(path,O/f'previous_attempt_{code}.json')
 cli('script','run',str(R/'SourceAssets/B4_ExperimentOperations/Play.cs'),'--entry','BEOPlay.'+code)
 deadline=time.monotonic()+25
 while (not path.exists() or path.stat().st_mtime_ns==previous) and time.monotonic()<deadline:time.sleep(.5)
 if not path.exists() or path.stat().st_mtime_ns==previous:raise RuntimeError('Play sample timeout '+code)
 d=json.loads(path.read_text(encoding='utf8'))
 print(json.dumps({k:d[k] for k in ['label','complete','displacement','framesAdvanced','medianMs','p95Ms','errors']}),flush=True)
 cli('capture','game_view','--source','screen','--save_path',f'Temp/B4_ExperimentOperations/play_{code}.png')
 shutil.copy2(P/f'Assets/Temp/B4_ExperimentOperations/play_{code}.png',O/f'play_{code}.png')
 if not d['complete'] or d['displacement']<.1 or d['errors']:raise RuntimeError('Play failure '+code)
