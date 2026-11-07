from pathlib import Path
import subprocess,json,time,sys,shutil
H=Path(__file__).resolve().parent;R=H.parents[1];D=R/'Docs/검수/2026-11-08_B5_RemainingDomes';P=R/'Unity/After_Seconds_Build_V0.01';CLI='C:/Users/Administrator/AppData/Local/Unity/bin/unity.exe'
def call(args,label):
    r=subprocess.run([CLI,'command','--caller','plugin','--skill','unity-cli','--project-path',str(P),'--format','json',*args],capture_output=True,text=True,encoding='utf-8',timeout=45)
    assert r.stdout.strip(),(label,r.stderr)
    (H/(label+'.json')).write_text(r.stdout,encoding='utf-8');d=json.loads(r.stdout)
    assert r.returncode==0 and d['success'],(label,r.stderr,d.get('errors'))
    result=d.get('data',{}).get('result',{})
    assert not (isinstance(result,dict) and result.get('success') is False),(label,result)
    return result
def ready():
    for attempt in range(8):
        r=subprocess.run([CLI,'status','--until-ready','--project-path',str(P),'--format','json'],capture_output=True,text=True,encoding='utf-8',timeout=40)
        if r.returncode==0:return
        data=json.loads(r.stdout)
        progress=any(t in r.stdout for t in ['Reloading Domain','Hold on...','Importing assets','Reload Script Assemblies'])
        if not progress and not any(e['code'] in ['EDITOR_NOT_RUNNING','EDITOR_NOT_READY'] for e in data.get('errors',[])):raise RuntimeError(r.stdout)
        time.sleep(2)
    raise RuntimeError('Unity did not finish domain reload')
resume='--resume' in sys.argv
if not resume:
    call(['editor','set_auto_tick','--enable','true','--persist','false'],'play_autotick')
    call(['editor.playmode','set_run_in_background','--enable','true'],'play_background')
try:
    if not resume:call(['editor.playmode','start'],'play_start')
    ready()
    call(['job','wait','--','--condition',json.dumps(dict(member='UnityEngine.Time.frameCount',op='changed')),'--timeout','10'],'play_frames')
    for method,label in [('LivingUnculled','living_unculled'),('Living','living'),('Control','control'),('Meal','meal'),('Cooling','cooling'),('Lift','lift'),('Stairs','stairs'),('Corridor','corridor')]:
        if '--stairs-only' in sys.argv and label!='stairs':continue
        if '--changed-only' in sys.argv and label not in ['living','control','lift']:continue
        call(['script','run',str(H/'Play.cs'),'--entry','RemainingPlay.'+method],'play_begin_'+label)
        time.sleep(5)
        output='Temp/Remaining_Play_'+label+'.png'
        capture=call(['capture','game_view','--source','screen','--save_path',output],'play_capture_'+label)
        shutil.copy2(P/capture['savedPath'],D/('Play_'+label+'.png'))
        time.sleep(4)
        data=json.loads((D/('play_'+label+'.json')).read_text(encoding='utf-8'))
        print(json.dumps(data,ensure_ascii=True),flush=True)
        assert data['complete'] and data['framesAdvanced']>10 and data['displacement']>.2 and not data['errors']
        assert abs(data['cameraRotation'][0])<.1 and abs(data['cameraRotation'][2])<.1
        if label=='stairs':assert data['rise']>.2

finally:
    ready()
    call(['editor.playmode','stop'],'play_stop')
    ready()
    call(['editor.playmode','set_run_in_background','--enable','false'],'play_background_restore')
