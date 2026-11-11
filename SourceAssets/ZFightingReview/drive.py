"""Run external review C# with the connected Unity Editor, without importing code."""
from pathlib import Path
import sys,subprocess,json
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/'Unity/After_Seconds_Build_V0.01'
CLI=Path.home()/'AppData/Local/Unity/bin/unity.exe'
def invoke(*args):
    p=subprocess.run([str(CLI),'command',*map(str,args),'--timeout','600','--caller','plugin','--skill','unity-cli','--project-path',str(PROJECT),'--format','json'],capture_output=True,text=True,encoding='utf-8',timeout=660)
    d=json.loads(p.stdout);r=d.get('data',{}).get('result',{})
    if not d.get('success') or isinstance(r,dict) and r.get('success') is False: raise RuntimeError(d)
    return r
if __name__=='__main__':
    if sys.argv[1]=='export':
        scenes=sorted((PROJECT/'Assets/Afrer_Seconds/01.Scenes').rglob('*.unity'))
        for p in scenes:
            r=invoke('script','run',ROOT/'SourceAssets/ZFightingReview/Export.cs','--entry','ZFExport.Run','--args',json.dumps([p.relative_to(PROJECT).as_posix()]))
            print(json.dumps(r,ensure_ascii=False),flush=True)
        print(invoke('scene','open','Assets/Afrer_Seconds/01.Scenes/Stage/Level_B4_Circular.unity'))
    elif sys.argv[1]=='run':
        print(json.dumps(invoke('script','run',ROOT/'SourceAssets/ZFightingReview'/sys.argv[2],'--entry',sys.argv[3],'--args',json.dumps(sys.argv[4:])),ensure_ascii=False))
    else: print(json.dumps(invoke(*sys.argv[1:]),ensure_ascii=False))
