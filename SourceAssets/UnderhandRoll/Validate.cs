if(!Application.isPlaying)throw new System.Exception("Play required");
var t=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();var h=t.GetComponent<PlayerFirstPersonHands>();var cc=t.GetComponent<CharacterController>();
var look=t.GetComponent<PlayerLook>();var zoom=t.GetComponent<PlayerZoom>();var mouse=UnityEngine.InputSystem.Mouse.current;var keyboard=UnityEngine.InputSystem.Keyboard.current;
var originalInput=UnityEngine.InputSystem.InputSystem.settings;var input=UnityEngine.Object.Instantiate(originalInput);
var position=t.transform.position;var rotation=t.transform.rotation;var eyeRotation=t.Origin.localRotation;
var flags=System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance;
var pitchField=typeof(PlayerLook).GetField("pitchAngle",flags);float originalPitch=(float)pitchField.GetValue(look);
var repeatField=typeof(PlayerThrow).GetField("repeatTestItem",flags);bool originalRepeat=(bool)repeatField.GetValue(t);bool originalMode=t.IsUnderhand;
int fps=Application.targetFrameRate,vsync=QualitySettings.vSyncCount,passed=0,failed=0,firstFrame=Time.frameCount;
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_UnderhandRoll"));System.IO.Directory.CreateDirectory(dir);
var log=new System.Text.StringBuilder();GameObject floor=null,block=null;var spawned=new System.Collections.Generic.List<GameObject>();
void Check(string name,bool ok){if(ok)passed++;else failed++;log.AppendLine((ok?"PASS ":"FAIL ")+name);}
void Mouse(ushort buttons)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(mouse,new UnityEngine.InputSystem.LowLevel.MouseState{buttons=buttons});
void Keys(params UnityEngine.InputSystem.Key[] keys)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(keys));
void Pitch(float angle){pitchField.SetValue(look,angle);t.Origin.localRotation=Quaternion.Euler(angle,0,0);}
void Move(Vector3 pos,Quaternion rot){cc.enabled=false;t.transform.SetPositionAndRotation(pos,rot);cc.enabled=true;Physics.SyncTransforms();}
System.Collections.IEnumerator Frames(int count){for(int i=0;i<count;i++)yield return null;}
void Capture(string name)
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var prev=c.targetTexture;var active=RenderTexture.active;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());}
    finally{c.targetTexture=prev;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
}
System.Collections.IEnumerator Run()
{
    try
    {
        input.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;input.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
        UnityEngine.InputSystem.InputSystem.settings=input;UnityEngine.InputSystem.InputSystem.EnableDevice(keyboard);UnityEngine.InputSystem.InputSystem.EnableDevice(mouse);
        EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();QualitySettings.vSyncCount=0;Application.targetFrameRate=60;repeatField.SetValue(t,true);
        t.ExitStance();zoom.SetZoomed(false);Mouse(0);Keys();if(t.IsUnderhand)t.ToggleThrowMode();yield return Frames(3);
        Keys(UnityEngine.InputSystem.Key.R);yield return Frames(2);Keys();yield return Frames(2);Check("R selects rolling mode without E",t.IsUnderhand&&!t.IsInThrowStance);
        Pitch(32);Mouse(1);yield return new WaitForSeconds(.5f);Capture("b5_01_ready");int count=t.ReleaseCount;
        Mouse(0);yield return Frames(2);Check("B5 direct click releases rolling object",t.ReleaseCount==count+1);
        if(t.LastThrown){spawned.Add(t.LastThrown.gameObject);}Capture("b5_02_push");yield return new WaitForSeconds(.35f);Capture("b5_03_contact");yield return new WaitForSeconds(.65f);Capture("b5_04_rolling");
        foreach(var obj in spawned)if(obj)UnityEngine.Object.Destroy(obj);spawned.Clear();
        floor=GameObject.CreatePrimitive(PrimitiveType.Cube);floor.name="TemporaryUnderhandRollFloor";floor.transform.position=new Vector3(1000,199.5f,1000);floor.transform.localScale=new Vector3(100,1,100);
        Move(new Vector3(1000,200+cc.height*.5f-cc.center.y+.02f,1000),Quaternion.identity);Pitch(0);yield return new WaitForSeconds(.5f);
        Mouse(1);yield return new WaitForSeconds(.5f);Check("holding left prepares rolling mode",t.IsAiming&&t.IsUnderhand);
        Check("neutral preview reaches first floor contact",t.PreviewHit&&t.LandingMarkerVisible);var predicted=t.PreviewContact;var hand=h.ItemPosition;
        var viewport=Camera.main.WorldToViewportPoint(hand);Check("low ready hand stays visible",viewport.x>0&&viewport.x<1&&viewport.y>0&&viewport.y<1&&viewport.z>0);
        count=t.ReleaseCount;Mouse(0);yield return null;yield return null;Check("release throws exactly once without windup delay",t.ReleaseCount==count+1);
        var ball=t.LastThrown;spawned.Add(ball.gameObject);var rb=ball.GetComponent<Rigidbody>();var launch=t.LastLaunch;
        Check("underhand speed is 4.5m/s",Mathf.Abs(launch.Velocity.magnitude-4.5f)<.01f);Check("neutral launch points down",launch.Velocity.y<-.5f);
        Check("spawn stays at actual hand",Vector3.Distance(launch.Position,hand)<.02f);Check("preview and physics use same damping",Mathf.Abs(rb.linearDamping-launch.Damping)<.001f&&Mathf.Abs(launch.Damping-.8f)<.001f);
        Check("forward spin clears default angular speed cap",rb.angularVelocity.magnitude>50&&rb.maxAngularVelocity>=70);
        bool hit=false;Vector3 contact=default,contactCenter=default;float contactTime=0,start=Time.time;float initialY=launch.Position.y,maxY=rb.position.y;
        var handLocal=t.Origin.InverseTransformPoint(hand);float handDown=0,handForward=0;bool followThroughVisible=!h.Obstructed;
        ball.Hit+=(obj,collision)=>{if(!hit&&collision.collider.gameObject==floor){hit=true;contact=collision.GetContact(0).point;contactCenter=rb.position;contactTime=Time.time-start;}};
        float maxBounce=0,rotationTravel=0,rollingSpeed=0;Quaternion previous=rb.rotation;int groundSamples=0;
        while(Time.time-start<6f)
        {
            yield return new WaitForFixedUpdate();maxY=Mathf.Max(maxY,rb.position.y);
            if(Time.time-start<.14f){var push=t.Origin.InverseTransformPoint(h.ItemPosition)-handLocal;handDown=Mathf.Min(handDown,push.y);handForward=Mathf.Max(handForward,push.z);followThroughVisible&=!h.Obstructed;}
            if(hit){maxBounce=Mathf.Max(maxBounce,rb.position.y-200-launch.Radius);rotationTravel+=Quaternion.Angle(previous,rb.rotation);groundSamples++;if(Time.time-start<contactTime+.25f)rollingSpeed=rb.linearVelocity.magnitude;}
            previous=rb.rotation;
        }
        float groundDistance=Vector3.ProjectOnPlane(rb.position-contactCenter,Vector3.up).magnitude;
        Check("floor contact happens within .7 seconds",hit&&contactTime<.7f);Check("flight never rises above release",maxY<=initialY+.005f);
        Check("hand follows through down and forward",handDown<-.01f&&handForward>.025f);
        Check("released ball does not hide follow-through hands",followThroughVisible);
        Check("predicted first contact matches actual within 8cm",hit&&Vector3.Distance(predicted,contact)<.08f);
        Check("roll travels at least 1m after contact",groundDistance>1f);Check("ball rotates multiple turns on floor",rotationTravel>720&&groundSamples>100);
        Check("floor does not create a high bounce",maxBounce<.06f);Check("roll slows to rest",rb.linearVelocity.magnitude<.15f&&rollingSpeed>1f);
        log.AppendLine($"MEASURE contactTime={contactTime:F3}s predictedError={Vector3.Distance(predicted,contact):F4}m groundTravel={groundDistance:F3}m turns={rotationTravel/360:F2} maxBounce={maxBounce:F4}m startRollSpeed={rollingSpeed:F3} finalSpeed={rb.linearVelocity.magnitude:F4} sleeping={rb.IsSleeping()} launch={launch.Velocity} handDown={handDown:F3} handForward={handForward:F3}");
        UnityEngine.Object.Destroy(ball.gameObject);yield return Frames(3);
        Pitch(-60);Mouse(1);yield return new WaitForSeconds(.35f);Check("looking up cannot turn roll into a lob",t.TryGetLaunch(out var upLaunch)&&upLaunch.Velocity.y<0&&Mathf.Abs(Mathf.Asin(upLaunch.Velocity.normalized.y)*Mathf.Rad2Deg+5)<.1f);t.CancelAim();Mouse(0);yield return Frames(3);
        Pitch(65);Mouse(1);yield return new WaitForSeconds(.35f);Check("looking down remains a forward low push",t.TryGetLaunch(out var downLaunch)&&downLaunch.Velocity.y<0&&Vector3.Dot(downLaunch.Velocity,t.transform.forward)>0);t.CancelAim();Mouse(0);yield return Frames(3);
        Pitch(0);zoom.SetZoomed(true);Mouse(1);yield return new WaitForSeconds(.4f);viewport=Camera.main.WorldToViewportPoint(h.ItemPosition);Check("zoom keeps low hand visible",viewport.y>0&&viewport.y<1&&viewport.x>0&&viewport.x<1);t.CancelAim();Mouse(0);zoom.SetZoomed(false);yield return Frames(3);
        count=t.ReleaseCount;Mouse(1);Mouse(0);yield return Frames(3);Check("quick click rolls without E or charging",t.ReleaseCount==count+1&&t.LastLaunch.Velocity.y<0);spawned.Add(t.LastThrown.gameObject);yield return new WaitForSeconds(.4f);
        t.ToggleThrowMode();Mouse(1);yield return new WaitForSeconds(.4f);Check("overhand still uses 12m/s with upward angle",t.TryGetLaunch(out var overLaunch)&&Mathf.Abs(overLaunch.Velocity.magnitude-12)<.01f&&overLaunch.Velocity.y>0&&overLaunch.Damping==0);
        Check("distant overhand contact still hides marker beyond visible line",t.PreviewHit&&!t.LandingMarkerVisible);Mouse(0);yield return Frames(3);spawned.Add(t.LastThrown.gameObject);rb=t.LastThrown.GetComponent<Rigidbody>();Check("overhand retains original angular damping and no added spin",Mathf.Abs(rb.angularDamping-.05f)<.001f&&rb.angularVelocity.magnitude<.001f);
        yield return new WaitForSeconds(.45f);t.ToggleThrowMode();Mouse(1);yield return new WaitForSeconds(.35f);block=GameObject.CreatePrimitive(PrimitiveType.Cube);block.transform.position=h.ItemPosition;block.transform.localScale=Vector3.one*.3f;Physics.SyncTransforms();yield return Frames(3);count=t.ReleaseCount;Mouse(0);yield return Frames(3);Check("blocked rolling hand still refuses launch",t.ReleaseCount==count);block.SetActive(false);
        Check("real play frames advanced",Time.frameCount-firstFrame>300);log.AppendLine($"TOTAL passed={passed}, failed={failed}, frames={firstFrame}→{Time.frameCount}");
    }
    finally
    {
        Mouse(0);Keys();t.ExitStance();zoom.SetZoomed(false);repeatField.SetValue(t,originalRepeat);if(t.IsUnderhand!=originalMode)t.ToggleThrowMode();
        foreach(var obj in spawned)if(obj)UnityEngine.Object.Destroy(obj);if(block)UnityEngine.Object.Destroy(block);if(floor)UnityEngine.Object.Destroy(floor);
        Move(position,rotation);pitchField.SetValue(look,originalPitch);t.Origin.localRotation=eyeRotation;
        UnityEngine.InputSystem.InputSystem.settings=originalInput;UnityEngine.Object.Destroy(input);Application.targetFrameRate=fps;QualitySettings.vSyncCount=vsync;
        System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"validation.txt"),log.ToString());
    }
}
t.StartCoroutine(Run());return "Underhand roll input/physics validation running";
