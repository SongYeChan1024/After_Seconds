// Play 모드에서 실제 PlayerInput에 장치 상태를 전달한다. 씬/에셋을 저장하지 않는다.
if (!Application.isPlaying || !Application.dataPath.Contains("After_Seconds_Build")) throw new System.Exception("After Seconds Play mode required");
var t = UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();
var h = t.GetComponent<PlayerFirstPersonHands>(); var motor=t.GetComponent<PlayerMotor>();
var zoom=t.GetComponent<PlayerZoom>();var look=t.GetComponent<PlayerLook>();var cc=t.GetComponent<CharacterController>();
var keyboard=UnityEngine.InputSystem.Keyboard.current;var mouse=UnityEngine.InputSystem.Mouse.current;
var log=new System.Text.StringBuilder();int passed=0,failed=0;
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_FirstPersonThrow"));
Vector3 savedPosition=t.transform.position;Quaternion savedRotation=t.transform.rotation;
int oldFPS=Application.targetFrameRate,oldVSync=QualitySettings.vSyncCount;
var item=t.HeldItem;
var repeat=typeof(PlayerThrow).GetField("repeatTestItem",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance);
bool wasRepeat=(bool)repeat.GetValue(t);
int eventCount=0,initialReleaseCount=t.ReleaseCount;float maxSpawnError=0f;bool hiddenAtEveryRelease=true;
System.Action<ItemDefinition,ThrownObject> onRelease=(definition,thrown)=>
{ eventCount++;maxSpawnError=Mathf.Max(maxSpawnError,Vector3.Distance(h.ItemPosition,thrown.transform.position));hiddenAtEveryRelease&=!h.ItemVisible; };
t.Released+=onRelease;
void Check(string name,bool ok) {if(ok)passed++;else failed++;log.AppendLine((ok?"PASS ":"FAIL ")+name);}
void Keys(params UnityEngine.InputSystem.Key[] keys) => UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(keys));
void Mouse(ushort buttons) => UnityEngine.InputSystem.InputSystem.QueueStateEvent(mouse,new UnityEngine.InputSystem.LowLevel.MouseState{buttons=buttons});
System.Collections.IEnumerator Frames(int n){for(int i=0;i<n;i++)yield return null;}
void Home()
{
    cc.enabled=false;t.transform.SetPositionAndRotation(savedPosition,savedRotation);cc.enabled=true;
    typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,0f);
    t.Origin.localRotation=Quaternion.identity;
}
void Capture(string name)
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var target=c.targetTexture;var active=RenderTexture.active;
    var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try {c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());}
    finally{c.targetTexture=target;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
}
float LineLength(){var l=t.transform.Find("ThrowTrajectory").GetComponent<LineRenderer>();float n=0;for(int i=1;i<l.positionCount;i++)n+=Vector3.Distance(l.GetPosition(i-1),l.GetPosition(i));return n;}
System.Collections.IEnumerator Run()
{
    try
    {
        Keys();Mouse(0);t.ExitStance();zoom.SetZoomed(false);Home();yield return new WaitForSeconds(0.4f);
        Check("frame loop advancing",Time.frameCount>20);Capture("after_hold");
        Keys(UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys();yield return Frames(2);
        Check("E enters stance through PlayerInput",t.IsInThrowStance);
        Mouse(1);yield return new WaitForSeconds(0.3f);Check("left hold aims",t.IsAiming);
        float normal=LineLength();Check("normal preview length 2.5m",Mathf.Abs(normal-2.5f)<0.01f);Capture("after_aim");
        Keys(UnityEngine.InputSystem.Key.R);yield return Frames(2);Keys();yield return new WaitForSeconds(0.25f);
        Check("R selects underhand",t.IsUnderhand);Capture("after_underhand");
        int count=t.ReleaseCount;Mouse(3);yield return Frames(2);Check("right click cancels while holding left",!t.IsAiming);
        Mouse(0);yield return Frames(2);Check("canceled release does not spawn",t.ReleaseCount==count);
        Keys(UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys();yield return Frames(2);
        Mouse(2);yield return Frames(2);Mouse(0);yield return new WaitForSeconds(0.3f);Check("right click zooms outside aim",zoom.IsZoomed);
        Keys(UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys();Mouse(1);yield return new WaitForSeconds(0.3f);
        Capture("after_zoom");Check("zoom preview extends farther",LineLength()>normal+0.2f);
        Mouse(0);yield return Frames(2);Check("release spawns exactly once",t.ReleaseCount==count+1);
        Check("held duplicate hidden on release",!h.ItemVisible);Check("zoom exits on release",!zoom.IsZoomed);
        Check("duplicate release rejected",!t.ReleaseThrow()&&t.ReleaseCount==count+1);Capture("after_release");
        var thrown=t.LastThrown;Check("spawn shares actual hand center",maxSpawnError<0.00001f);
        Check("own collider ignored",Physics.GetIgnoreCollision(thrown.GetComponent<Collider>(),cc));
        yield return new WaitForSeconds(0.35f);Check("test item returns after recovery",h.ItemVisible);
        QualitySettings.vSyncCount=0;
        foreach(int fps in new[]{30,60,144})
        {
            Application.targetFrameRate=fps;yield return new WaitForSeconds(0.15f);
            int startFrame=Time.frameCount;float startTime=Time.realtimeSinceStartup;count=t.ReleaseCount;
            Keys(UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys();Mouse(1);yield return Frames(2);Mouse(0);yield return Frames(2);
            Check("single release at target FPS "+fps,t.ReleaseCount==count+1);
            log.AppendLine($"targetFPS={fps}, sampledFrames={Time.frameCount-startFrame}, wallSeconds={Time.realtimeSinceStartup-startTime:F3}");
            yield return new WaitForSeconds(0.3f);
        }
        Application.targetFrameRate=60;Home();
        Keys(UnityEngine.InputSystem.Key.W);yield return new WaitForSeconds(0.35f);float walkSpeed=cc.velocity.magnitude;
        Capture("after_walk");Check("W moves player",Vector3.Distance(t.transform.position,savedPosition)>0.3f);
        count=t.ReleaseCount;Keys(UnityEngine.InputSystem.Key.W,UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys(UnityEngine.InputSystem.Key.W);
        Mouse(1);yield return Frames(3);Mouse(0);yield return Frames(2);
        Check("walking aim and release preserves movement",t.ReleaseCount==count+1&&cc.velocity.magnitude>0.5f);
        Keys(UnityEngine.InputSystem.Key.W,UnityEngine.InputSystem.Key.LeftShift);yield return new WaitForSeconds(0.35f);
        Check("sprint accelerates",cc.velocity.magnitude>walkSpeed+0.3f);Capture("after_sprint");Keys();yield return new WaitForSeconds(0.3f);Home();
        float standing=t.Origin.localPosition.y;Keys(UnityEngine.InputSystem.Key.C);yield return Frames(2);Keys();yield return new WaitForSeconds(0.3f);
        Check("C crouches and lowers eyes",motor.IsCrouching&&t.Origin.localPosition.y<standing-0.4f);Capture("after_crouch");
        count=t.ReleaseCount;t.ToggleStance();t.BeginAim();yield return Frames(3);Check("crouched release",t.ReleaseThrow()&&t.ReleaseCount==count+1&&motor.IsCrouching);
        Keys(UnityEngine.InputSystem.Key.Space);yield return Frames(2);Keys();yield return Frames(2);
        Check("jump from crouch stands and jumps",!motor.IsCrouching&&motor.IsJumping);Capture("after_jump");yield return new WaitForSeconds(1f);Home();
        UnityEngine.InputSystem.InputSystem.QueueDeltaStateEvent(mouse.delta,new Vector2(600f,800f));yield return Frames(3);Capture("after_look_up");
        Check("rapid look keeps hands finite",!float.IsNaN(h.ItemPosition.x)&&h.Ready);
        UnityEngine.InputSystem.InputSystem.QueueDeltaStateEvent(mouse.delta,new Vector2(-1200f,-1600f));yield return Frames(3);Capture("after_look_down");Home();yield return new WaitForSeconds(0.2f);
        t.ToggleStance();t.BeginAim();t.enabled=false;Check("disable cancels aim",!t.IsAiming&&!t.IsInThrowStance);t.enabled=true;Check("enable does not emit stale throw",!t.ReleaseThrow());
        t.ToggleStance();t.BeginAim();h.enabled=false;Check("hand disable cancels aim",!t.IsAiming);h.enabled=true;t.ExitStance();yield return new WaitForSeconds(0.3f);
        var block=GameObject.CreatePrimitive(PrimitiveType.Cube);block.name="TemporaryThrowBlock";block.transform.position=h.ItemPosition;block.transform.localScale=Vector3.one*0.2f;Physics.SyncTransforms();
        t.ToggleStance();t.BeginAim();t.RefreshTrajectory(false);count=t.ReleaseCount;
        Check("overlapping start blocks release",t.IsBlocked&&!t.ReleaseThrow()&&t.ReleaseCount==count);
        yield return Frames(2);t.BeginAim();yield return Frames(2);Capture("after_blocked");
        UnityEngine.Object.Destroy(block);t.ExitStance();yield return new WaitForSeconds(0.3f);
        var trigger=new GameObject("TemporaryThrowTrigger");trigger.transform.position=h.ItemPosition;var sensor=trigger.AddComponent<SphereCollider>();sensor.radius=0.2f;sensor.isTrigger=true;Physics.SyncTransforms();
        Check("trigger excluded from launch clearance",t.TryGetLaunch(out _));UnityEngine.Object.Destroy(trigger);
        repeat.SetValue(t,false);t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(0.2f);
        Check("non-test item consumed once",t.ReleaseThrow()&&!t.HasHeldItem);
        yield return new WaitForSeconds(0.35f);Check("consumed item does not reappear",!h.ItemVisible);
        t.SetHeldItem(item);repeat.SetValue(t,wasRepeat);t.ExitStance();Home();
        Check("one release event per spawned object",eventCount==t.ReleaseCount-initialReleaseCount);
        Check("all release frames hide held duplicate",hiddenAtEveryRelease);
        Check("all spawn centers match held item",maxSpawnError<0.00001f);
        log.AppendLine($"release events={eventCount}, maximum same-frame hand/spawn mismatch={maxSpawnError:F7}m");
        log.AppendLine($"TOTAL passed={passed}, failed={failed}, final frame={Time.frameCount}");
    }
    finally
    {
        Keys();Mouse(0);Application.targetFrameRate=oldFPS;QualitySettings.vSyncCount=oldVSync;
        t.enabled=true;h.enabled=true;t.SetHeldItem(item);repeat.SetValue(t,wasRepeat);t.ExitStance();zoom.SetZoomed(false);Home();
        t.Released-=onRelease;
        System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"play_validation.txt"),log.ToString());
    }
}
t.StartCoroutine(Run());return "Play validation coroutine started";
