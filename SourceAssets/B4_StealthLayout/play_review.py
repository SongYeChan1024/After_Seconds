from pathlib import Path
import json
import subprocess
import sys
import time
import shutil

sys.stdout.reconfigure(encoding='utf-8')
repository=Path(__file__).resolve().parents[2]
project=repository/'Unity/After_Seconds_Build_V0.01'
cli='C:/Users/Administrator/AppData/Local/Unity/bin/unity.exe'
report_directory=repository/'Docs/검수/2026-11-06_B5_B4/B4'
capture_directory=project/'Temp/B4Review'
capture_directory.mkdir(parents=True,exist_ok=True)

def invoke(*arguments,command=True):
    args=[cli]+(['command'] if command else [])+list(arguments)+(['--caller','plugin','--skill','unity-cli'] if command else [])+['--project-path',str(project),'--format','json']
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',timeout=100)
    response=json.loads(result.stdout)
    payload=response.get('data',{}).get('result',{}) if isinstance(response.get('data'),dict) else {}
    if not response.get('success') or (isinstance(payload,dict) and payload.get('success') is False):
        raise RuntimeError(response)
    return response

baseline=invoke('console','status')
cursor=baseline['data']['result']['cursor']
report={'consoleBefore':baseline['data']['result']}
try:
    invoke('editor','set_auto_tick','--enable','true','--persist','false')
    invoke('editor.playmode','set_run_in_background','--enable','true')
    report['playStart']=invoke('editor.playmode','start')['data']['result']
    invoke('status','--until-ready',command=False)
    report['frameBefore']=invoke('eval','return new { frame=UnityEngine.Time.frameCount, playing=UnityEditor.EditorApplication.isPlaying };')['data']['result']
    time.sleep(0.6)
    report['frameAfter']=invoke('eval','return new { frame=UnityEngine.Time.frameCount, playing=UnityEditor.EditorApplication.isPlaying };')['data']['result']
    capture=invoke('game_view','--source','screen','--width','1440','--height','900','--save_path',str(capture_directory/'11_PlayEntry.png'))
    shutil.copy2(project/capture['data']['result']['savedPath'],report_directory/'11_PlayEntry.png')
    input_report=report_directory/'play_input.json'
    previous_stamp=input_report.stat().st_mtime_ns if input_report.exists() else 0
    invoke('script','run',str(repository/'SourceAssets/B4_StealthLayout/PlayReview.cs'),'--entry','PlayReview.Begin')
    deadline=time.monotonic()+12
    while (not input_report.exists() or input_report.stat().st_mtime_ns==previous_stamp) and time.monotonic()<deadline:
        time.sleep(0.3)
    if not input_report.exists() or input_report.stat().st_mtime_ns==previous_stamp:
        raise RuntimeError('Play input verification did not complete')
    report['input']=json.loads(input_report.read_text(encoding='utf-8'))
    capture=invoke('game_view','--source','screen','--width','1440','--height','900','--save_path',str(capture_directory/'12_PlayAfterInput.png'))
    shutil.copy2(project/capture['data']['result']['savedPath'],report_directory/'12_PlayAfterInput.png')
    console=invoke('console','get','--since',str(cursor),'--level','warn','--tail','25')['data']['result']
    report['consoleAfter']={key:value for key,value in console.items() if key!='entries'}
    report['newWarningsAndErrors']=[{'seq':item['seq'],'level':item['level'],'message':item['message']} for item in console['entries']]
finally:
    invoke('status','--until-ready',command=False)
    invoke('editor.playmode','stop')
    invoke('status','--until-ready',command=False)
    invoke('editor.playmode','set_run_in_background','--enable','false')
    invoke('editor','set_auto_tick','--enable','false','--persist','false')
    report['restoredRunInBackground']=invoke('eval','return UnityEngine.Application.runInBackground;')['data']['result']
    (report_directory/'play_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
