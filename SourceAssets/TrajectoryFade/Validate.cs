if(!Application.isPlaying)throw new System.Exception("Play required");
var t=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();var h=t.GetComponent<PlayerFirstPersonHands>();var cc=t.GetComponent<CharacterController>();
var look=t.GetComponent<PlayerLook>();var zoom=t.GetComponent<PlayerZoom>();var motor=t.GetComponent<PlayerMotor>();
var sf=typeof(PlayerThrow).GetField("settings",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance);
var original=(PlayerThrowSettings)sf.GetValue(t);var copy=UnityEngine.Object.Instantiate(original);
var line=t.transform.Find("ThrowTrajectory").GetComponent<LineRenderer>();
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_TrajectoryFade"));System.IO.Directory.CreateDirectory(dir);
var log=new System.Text.StringBuilder();int passed=0,failed=0,firstFrame=Time.frameCount;
var savedPosition=t.transform.position;var savedRotation=t.transform.rotation;var savedItem=t.HeldItem;bool savedUnder=t.IsUnderhand;
var temporary=new List<GameObject>();int oldFPS=Application.targetFrameRate,oldVSync=QualitySettings.vSyncCount;
void Check(string name,bool ok){if(ok)passed++;else failed++;log.AppendLine((ok?"PASS ":"FAIL ")+name);}
void Float(string field,float value)=>typeof(PlayerThrowSettings).GetField(field,System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(copy,value);
void Pitch(float p){typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,p);t.Origin.localRotation=Quaternion.Euler(p,0,0);}
void Home(Vector3 p,Quaternion q){t.ExitStance();zoom.SetZoomed(false);motor.TryStandUp();cc.enabled=false;t.transform.SetPositionAndRotation(p,q);cc.enabled=true;Pitch(0);h.ResetPose();Physics.SyncTransforms();}
void Aim(bool under=false){t.ExitStance();t.ToggleStance();if(t.IsUnderhand!=under)t.ToggleThrowMode();t.BeginAim();}
float Length(){float length=0;for(int i=1;i<line.positionCount;i++)length+=Vector3.Distance(line.GetPosition(i-1),line.GetPosition(i));return length;}
GameObject Box(string name,Vector3 center,Vector3 size){var go=GameObject.CreatePrimitive(PrimitiveType.Cube);go.name=name;go.transform.position=center;go.transform.localScale=size;temporary.Add(go);Physics.SyncTransforms();return go;}
void Capture(string name)
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var previous=c.targetTexture;var active=RenderTexture.active;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());}
    finally{c.targetTexture=previous;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
}
System.Collections.IEnumerator Run()
{
    try
    {
        QualitySettings.vSyncCount=0;Application.targetFrameRate=60;sf.SetValue(t,copy);
        Home(savedPosition,savedRotation);yield return new WaitForSeconds(.3f);Aim();yield return new WaitForSeconds(.4f);Capture("b5_overhand");
        Check("default uses short fading guide",!copy.ShowFullTrajectory&&copy.TrajectoryOpacity<=.3f);
        Check("B5 guide respects 2.5m cap",Length()<=2.501f);
        Aim(true);yield return new WaitForSeconds(.4f);Capture("b5_underhand");
        Check("underhand guide respects same cap",Length()<=2.501f);Check("underhand rises from lowered hand",line.GetPosition(2).y>line.GetPosition(0).y);
        zoom.SetZoomed(true);yield return new WaitForSeconds(.4f);Capture("b5_zoom");Check("zoom guide respects 4m cap",Length()<=4.001f);
        var floor=Box("TemporaryFadeFloor",new Vector3(1000,199.5f,1000),new Vector3(100,1,100));
        var home=new Vector3(1000,200+cc.height*.5f-cc.center.y+.02f,1000);Home(home,Quaternion.identity);yield return new WaitForSeconds(.4f);Aim();yield return new WaitForSeconds(.35f);
        Check("far collision retains a short 2.5m line",Mathf.Abs(Length()-2.5f)<.003f);
        Check("far collision retains a separate circle",t.PreviewHit&&t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,line.GetPosition(line.positionCount-1))>3f);
        Check("line originates at actual held item",Vector3.Distance(line.GetPosition(0),h.ItemPosition)<.002f);
        Check("preview end equals visible line end",Vector3.Distance(t.PreviewEnd,line.GetPosition(line.positionCount-1))<.002f);
        Check("fade starts at configured opacity",Mathf.Abs(line.colorGradient.Evaluate(0).a-.3f)<.002f);
        Check("fade is softer in latter half",line.colorGradient.Evaluate(.75f).a<.15f&&line.colorGradient.Evaluate(.75f).a>0f);
        Check("line tip fades fully transparent",line.colorGradient.Evaluate(1).a<.001f);
        var predicted=t.PreviewContact;float normalLength=Length();zoom.SetZoomed(true);yield return new WaitForSeconds(.4f);
        Check("zoom extends guide only to 4m",Mathf.Abs(Length()-4f)<.003f&&Length()>normalLength);
        Check("zoom still stops before collision circle",t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,t.PreviewEnd)>2f);
        zoom.SetZoomed(false);yield return new WaitForSeconds(.4f);Aim(true);yield return new WaitForSeconds(.35f);
        Check("underhand far circle survives line cutoff",Mathf.Abs(Length()-2.5f)<.003f&&t.PreviewHit&&t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,t.PreviewEnd)>1f);
        Aim();yield return new WaitForSeconds(.3f);
        var wall=Box("TemporaryNearWall",home+Vector3.forward*1.8f,new Vector3(5,5,.2f));yield return new WaitForSeconds(.25f);Capture("near_wall");
        Check("near wall ends guide before distance cap",Length()<2f&&t.PreviewHit&&t.LandingMarkerVisible);
        Check("wall circle follows hit normal",Mathf.Abs(t.PreviewNormal.z)>.95f);
        Check("near-hit line is still faded",line.colorGradient.Evaluate(1).a<.001f);wall.SetActive(false);yield return new WaitForSeconds(.25f);
        Float("trajectoryMaxTime",.1f);yield return new WaitForSeconds(.1f);
        Check("time limit creates no fake circle",!t.PreviewHit&&!t.LandingMarkerVisible&&Length()>0);
        Float("trajectoryMaxTime",original.TrajectoryMaxTime);Float("maxPreviewDistance",1f);yield return new WaitForSeconds(.1f);
        Check("prediction distance limit creates no fake circle",!t.PreviewHit&&!t.LandingMarkerVisible&&Length()<=1.001f);
        Float("maxPreviewDistance",original.MaxPreviewDistance);
        t.TryGetLaunch(out var launch);var target=Box("TemporaryBeyondPredictionLimit",new Vector3(home.x,launch.Position.y,home.z+2.0f),new Vector3(5,5,.1f));
        Float("maxPreviewDistance",1f);yield return new WaitForSeconds(.1f);Check("collider beyond prediction cap is ignored",!t.PreviewHit&&!t.LandingMarkerVisible);target.SetActive(false);Float("maxPreviewDistance",original.MaxPreviewDistance);
        // 작은 발판 너머는 빈 공간이다. 위로 던지더라도 큰 바닥으로 돌아오는 경우와 구분한다.
        floor.transform.localScale=new Vector3(3,1,3);Physics.SyncTransforms();yield return new WaitForSeconds(.2f);Capture("no_hit");
        Check("flight into empty space has no circle",!t.PreviewHit&&!t.LandingMarkerVisible&&Length()>0);
        floor.transform.localScale=new Vector3(100,1,100);Physics.SyncTransforms();yield return new WaitForSeconds(.25f);
        var block=Box("TemporaryHandBlock",h.ItemPosition,Vector3.one*.2f);yield return new WaitForSeconds(.1f);
        Check("blocked hand clears line and old circle",t.IsBlocked&&!line.enabled&&!t.PreviewHit&&!t.LandingMarkerVisible);block.SetActive(false);yield return new WaitForSeconds(.2f);
        int releases=t.ReleaseCount;t.CancelAim();Check("cancel clears both without release",!line.enabled&&!t.LandingMarkerVisible&&t.ReleaseCount==releases);
        Aim();yield return new WaitForSeconds(.3f);predicted=t.PreviewContact;bool impact=false;Vector3 actual=Vector3.zero;
        System.Action<ItemDefinition,ThrownObject> release=(item,obj)=>obj.Hit+=(o,c)=>{if(!impact){impact=true;actual=c.GetContact(0).point;}};
        t.Released+=release;int releaseFrame=Time.frameCount;
        try
        {
            Check("release remains immediate",t.ReleaseThrow()&&Time.frameCount==releaseFrame&&t.ReleaseCount==releases+1);
            Check("release clears guide circle and duplicate",!line.enabled&&!t.LandingMarkerVisible&&!h.ItemVisible);
            yield return new WaitForSeconds(1.6f);
        }
        finally{t.Released-=release;}
        Check("hidden path still predicts real impact within 8cm",impact&&Vector3.Distance(actual,predicted)<.08f);log.AppendLine("impact error="+Vector3.Distance(actual,predicted).ToString("F4")+"m");
        Aim();yield return new WaitForSeconds(.1f);t.SetHeldItem(null);Check("item removal clears both",!line.enabled&&!t.LandingMarkerVisible);t.SetHeldItem(savedItem);
        Check("live frames advanced",Time.frameCount-firstFrame>100);log.AppendLine($"TOTAL passed={passed}, failed={failed}, frames={firstFrame}→{Time.frameCount}");
    }
    finally
    {
        sf.SetValue(t,original);UnityEngine.Object.Destroy(copy);
        foreach(var go in temporary)if(go)UnityEngine.Object.Destroy(go);
        foreach(var go in UnityEngine.Object.FindObjectsByType<ThrownObject>(FindObjectsSortMode.None))if(go.name.Contains("Clone"))UnityEngine.Object.Destroy(go.gameObject);
        t.SetHeldItem(savedItem);Home(savedPosition,savedRotation);if(t.IsUnderhand!=savedUnder){t.ToggleStance();t.ToggleThrowMode();t.ExitStance();}
        Application.targetFrameRate=oldFPS;QualitySettings.vSyncCount=oldVSync;System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"validation.txt"),log.ToString());
    }
}
t.StartCoroutine(Run());return "Fade validation running";
