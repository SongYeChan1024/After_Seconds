from pathlib import Path
import subprocess,shutil,json,time,sys
H=Path(__file__).resolve().parent;R=H.parents[1];P=R/'Unity/After_Seconds_Build_V0.01';O=R/'Docs/Review/2026-11-09_B4_LayoutPolish'
cli=shutil.which('unity')
def run(*args):
 p=subprocess.run([cli,'command',*args,'--caller','plugin','--skill','unity-cli','--project-path',str(P),'--format','json'],cwd=P,capture_output=True,text=True,encoding='utf8',timeout=120)
 j=json.loads(p.stdout)
 if not j.get('success') or isinstance(j.get('data',{}).get('result'),dict) and j['data']['result'].get('success') is False:raise RuntimeError(p.stdout)
 return j
for code in sys.argv[1:]:
 f=O/f'play_{code}.json';old=f.stat().st_mtime_ns if f.exists() else 0
 run('script','run','--file',str(H/'Play.cs'),'--entry','B4PolishPlay.'+code)
 deadline=time.monotonic()+25
 while (not f.exists() or f.stat().st_mtime_ns==old) and time.monotonic()<deadline:time.sleep(.3)
 d=json.loads(f.read_text(encoding='utf8'))
 print(json.dumps({k:d[k] for k in ['label','complete','displacement','framesAdvanced','medianMs','p95Ms','errors']}),flush=True)
 j=run('capture','game_view','--source','screen','--save_path','Temp/B4_LayoutPolish/play_'+code+'.png')
 candidates=[P/'Temp/B4_LayoutPolish'/f'play_{code}.png',P/'Assets/Temp/B4_LayoutPolish'/f'play_{code}.png']
 src=next((p for p in candidates if p.exists()),None)
 if src:shutil.copy2(src,O/f'play_{code}.png')
 else:raise RuntimeError('Capture path not found '+str(j))
 if not d['complete'] or d['displacement']<.1 or d['framesAdvanced']<10 or d['errors']:raise RuntimeError('Play sample failed '+code)
