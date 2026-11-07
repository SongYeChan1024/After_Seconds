from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'Play.cs';s=p.read_text(encoding='utf-8')
s=s.replace('Start(string id,Vector3 p,float yaw){','Start(string id,Vector3 p,float yaw,bool culling=true){')
old='var cc=player.GetComponent<CharacterController>();'
new='look=player.GetComponentsInChildren<MonoBehaviour>(true).Single(c=>c.GetType().Name=="PlayerLook");lookEnabled=look.enabled;look.enabled=false;pivot=(Transform)look.GetType().GetField("cameraRoot",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic).GetValue(look);previousPivot=pivot.localRotation;pivot.localRotation=Quaternion.identity;testCamera=player.GetComponentInChildren<Camera>();previousCulling=testCamera.useOcclusionCulling;testCamera.useOcclusionCulling=culling;'+old
assert old in s;s=s.replace(old,new)
s=s.replace('if(elapsed>5.0)End(true);','if(elapsed>8.0)End(true);')
s=s.replace('screen=new[]{Screen.width,Screen.height},','cameraRotation=new[]{testCamera.transform.eulerAngles.x,testCamera.transform.eulerAngles.y,testCamera.transform.eulerAngles.z},occlusion=testCamera.useOcclusionCulling,screen=new[]{Screen.width,Screen.height},')
s=s.replace('mouse disabled during sample then restored; focus override restored','mouse and PlayerLook disabled during forward-view sample/capture then restored; focus/culling restored')
old='JsonConvert.SerializeObject(result,Formatting.Indented));}'
new='JsonConvert.SerializeObject(result,Formatting.Indented));pivot.localRotation=previousPivot;look.enabled=lookEnabled;testCamera.useOcclusionCulling=previousCulling;}'
assert old in s;s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
p=H/'run_play.py';s=p.read_text(encoding='utf-8')
s=s.replace("[('Living','living'),","[('LivingUnculled','living_unculled'),('Living','living'),")
start=s.index('        time.sleep(6)');end=s.index('\nfinally:',start)
s=s[:start]+'''        time.sleep(5)
        output='Temp/Remaining_Play_'+label+'.png'
        capture=call(['capture','game_view','--source','screen','--save_path',output],'play_capture_'+label)
        shutil.copy2(P/capture['savedPath'],D/('Play_'+label+'.png'))
        time.sleep(4)
        data=json.loads((D/('play_'+label+'.json')).read_text(encoding='utf-8'))
        print(json.dumps(data,ensure_ascii=True),flush=True)
        assert data['complete'] and data['framesAdvanced']>10 and data['displacement']>.2 and not data['errors']
        assert abs(data['cameraRotation'][0])<.1 and abs(data['cameraRotation'][2])<.1
        if label=='stairs':assert data['rise']>.2
'''+s[end:]
p.write_text(s,encoding='utf-8')
p=H/'PostPlay.cs';s=p.read_text(encoding='utf-8').replace('new[]{"living",','new[]{"living_unculled","living",');p.write_text(s,encoding='utf-8')
