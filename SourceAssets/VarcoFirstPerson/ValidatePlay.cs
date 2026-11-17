// 실제 PlayerInput → Motor/Animator/손 표시/투척을 함께 검사한다. 임시 플랫폼과 입력은 마지막에 정리한다.
if (!Application.isPlaying || !Application.dataPath.Contains("After_Seconds_Build")) throw new System.Exception("After Seconds Play required");
var t=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();var h=t.GetComponent<PlayerFirstPersonHands>();
var cc=t.GetComponent<CharacterController>();var motor=t.GetComponent<PlayerMotor>();var look=t.GetComponent<PlayerLook>();var zoom=t.GetComponent<PlayerZoom>();
var animator=t.transform.Find("VisualRoot").GetComponentsInChildren<Animator>().First(a=>a.isHuman);
var lf=animator.GetBoneTransform(HumanBodyBones.LeftFoot);var rf=animator.GetBoneTransform(HumanBodyBones.RightFoot);
var keyboard=UnityEngine.InputSystem.Keyboard.current;var mouse=UnityEngine.InputSystem.Mouse.current;
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_VarcoFirstPerson"));System.IO.Directory.CreateDirectory(dir);
var originalInputSettings=UnityEngine.InputSystem.InputSystem.settings;
var captureInputSettings=UnityEngine.Object.Instantiate(originalInputSettings);
var motion=AssetDatabase.LoadAssetAtPath<PlayerHandAnimationSet>("Assets/Afrer_Seconds/06.Data/PlayerHandAnimations.asset");
var log=new System.Text.StringBuilder();int passed=0,failed=0;int firstFrame=Time.frameCount;
Vector3 savedPosition=t.transform.position;Quaternion savedRotation=t.transform.rotation;
int oldFPS=Application.targetFrameRate,oldVSync=QualitySettings.vSyncCount;
var temporary=new List<GameObject>();var projectItem=t.HeldItem;
var settings=(PlayerThrowSettings)typeof(PlayerThrow).GetField("settings",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).GetValue(t);
var runtimeSettings=UnityEngine.Object.Instantiate(settings);
var settingsField=typeof(PlayerThrow).GetField("settings",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance);
void Check(string name,bool ok){if(ok)passed++;else failed++;log.AppendLine((ok?"PASS ":"FAIL ")+name);}
void Keys(params UnityEngine.InputSystem.Key[] keys)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(keys));
void Mouse(ushort buttons)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(mouse,new UnityEngine.InputSystem.LowLevel.MouseState{buttons=buttons});
System.Collections.IEnumerator Frames(int n){for(int i=0;i<n;i++)yield return null;}
void Pitch(float p){typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,p);t.Origin.localRotation=Quaternion.Euler(p,0,0);}
void Teleport(Vector3 p,Quaternion q){cc.enabled=false;t.transform.SetPositionAndRotation(p,q);cc.enabled=true;Physics.SyncTransforms();}
Vector3 testHome=new Vector3(1000,200+cc.height*.5f-cc.center.y+.02f,1000);
void Home(){Keys();Mouse(0);t.ExitStance();if(t.IsUnderhand){t.ToggleStance();t.ToggleThrowMode();t.ExitStance();}zoom.SetZoomed(false);motor.TryStandUp();Teleport(testHome,Quaternion.identity);Pitch(0);h.ResetPose();}
GameObject Cube(string name,Vector3 position,Vector3 size){var g=GameObject.CreatePrimitive(PrimitiveType.Cube);g.name=name;g.transform.position=position;g.transform.localScale=size;temporary.Add(g);return g;}
void Capture(string name)
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var target=c.targetTexture;var active=RenderTexture.active;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());}
    finally{c.targetTexture=target;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
}
bool OnScreen(Vector3 p){var v=Camera.main.WorldToViewportPoint(p);return v.z>0&&v.x>0&&v.x<1&&v.y>0&&v.y<1;}
float LineLength(){var l=t.transform.Find("ThrowTrajectory").GetComponent<LineRenderer>();float length=0;for(int i=1;i<l.positionCount;i++)length+=Vector3.Distance(l.GetPosition(i-1),l.GetPosition(i));return length;}
float Range(List<float> v)=>v.Max()-v.Min();
float Correlation(List<float> x,List<float> y){float ax=x.Average(),ay=y.Average(),n=0,a=0,b=0;for(int i=0;i<x.Count;i++){float dx=x[i]-ax,dy=y[i]-ay;n+=dx*dy;a+=dx*dx;b+=dy*dy;}return n/Mathf.Sqrt(a*b);}
float walkRange=0,runRange=0,aimRange=0;
System.Collections.IEnumerator Sample(string label,bool running,bool aiming)
{
    Home();yield return new WaitForSeconds(.3f);
    if(aiming){t.ToggleStance();t.BeginAim();}
    Keys(running?new[]{UnityEngine.InputSystem.Key.W,UnityEngine.InputSystem.Key.LeftShift}:new[]{UnityEngine.InputSystem.Key.W});
    yield return new WaitForSeconds(.55f);
    var left=new List<float>();var right=new List<float>();var foot=new List<float>();
    float until=Time.time+1.6f;int sample=0;
    while(Time.time<until)
    {
        left.Add(t.Origin.InverseTransformPoint(h.LeftHandPosition).z);right.Add(t.Origin.InverseTransformPoint(h.ItemPosition).z);
        foot.Add(t.transform.InverseTransformPoint(lf.position).z-t.transform.InverseTransformPoint(rf.position).z);
        if(sample==4)Capture(label+"_a");if(sample==18)Capture(label+"_b");sample++;yield return null;
    }
    float range=Range(right),correlation=Correlation(left,right);
    log.AppendLine($"{label}: samples={sample}, speed={cc.velocity.magnitude:F3}, swing={range:F4}m, correlation={correlation:F3}, footStride={Range(foot):F3}m");
    Check(label+" actual movement",cc.velocity.magnitude>3f&&h.MovementWeight>.8f);
    Check(label+" opposing hand rhythm",correlation<-.75f);
    Check(label+" animated feet",Range(foot)>.1f);
    Check(label+" both hands in frame",OnScreen(h.LeftHandPosition)&&OnScreen(h.ItemPosition));
    if(aiming)aimRange=range;else if(running)runRange=range;else walkRange=range;
    Keys();t.ExitStance();yield return new WaitForSeconds(.4f);
}
System.Collections.IEnumerator Run()
{
    try
    {
        captureInputSettings.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;
        captureInputSettings.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
        UnityEngine.InputSystem.InputSystem.settings=captureInputSettings;
        UnityEngine.InputSystem.InputSystem.EnableDevice(keyboard);UnityEngine.InputSystem.InputSystem.EnableDevice(mouse);
        EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();
        Check("VARCO animation set connected",h.UsesAnimationClips);
        Check("three humanoid sources",motion.walkSource.isHumanMotion&&motion.runSource.isHumanMotion&&motion.overhandSource.isHumanMotion);
        Check("walk loop continuous",Vector3.Distance(motion.walkRight.Evaluate(0),motion.walkRight.Evaluate(1))<.001f&&Vector3.Distance(motion.walkLeft.Evaluate(0),motion.walkLeft.Evaluate(1))<.001f);
        Check("run loop continuous",Vector3.Distance(motion.runRight.Evaluate(0),motion.runRight.Evaluate(1))<.001f&&Vector3.Distance(motion.runLeft.Evaluate(0),motion.runLeft.Evaluate(1))<.001f);
        Check("follow-through returns smoothly",motion.releaseRight.Evaluate(0).magnitude<.001f&&motion.releaseRight.Evaluate(1).magnitude<.001f&&motion.releaseLeft.Evaluate(1).magnitude<.001f);
        Check("follow-through has motion",Enumerable.Range(0,21).Max(i=>motion.releaseRight.Evaluate(i/20f).magnitude)>.025f);
        QualitySettings.vSyncCount=0;Application.targetFrameRate=60;Keys();Mouse(0);t.ExitStance();zoom.SetZoomed(false);Pitch(0);
        yield return new WaitForSeconds(.5f);Capture("idle");Check("idle both hands in frame",OnScreen(h.LeftHandPosition)&&OnScreen(h.ItemPosition));
        Pitch(80);yield return new WaitForSeconds(.35f);Capture("look_down");
        Check("looking down shows both feet",h.LowerBodyVisible&&OnScreen(lf.position)&&OnScreen(rf.position));
        Keys(UnityEngine.InputSystem.Key.C);yield return Frames(2);Keys();yield return new WaitForSeconds(.4f);Capture("crouch_down");
        Check("crouch retains lower body and a visible foot",motor.IsCrouching&&h.LowerBodyVisible&&(OnScreen(lf.position)||OnScreen(rf.position)));
        Keys(UnityEngine.InputSystem.Key.C);yield return Frames(2);Keys();yield return new WaitForSeconds(.35f);
        Pitch(38);t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.3f);Capture("aim_floor");
        Check("B5 ground contact marker",t.PreviewHit&&t.LandingMarkerVisible&&t.PreviewNormal.y>.9f);
        t.ToggleThrowMode();yield return new WaitForSeconds(.3f);Capture("aim_underhand");t.ExitStance();Pitch(0);
        Cube("TemporaryMotionFloor",new Vector3(1000,199.5f,1000),new Vector3(100,1,100));Home();yield return new WaitForSeconds(.4f);
        yield return Sample("walk",false,false);yield return Sample("run",true,false);yield return Sample("aim_run",true,true);
        Check("running swing stronger than walking",runRange>walkRange*1.35f);
        Check("aim suppresses running swing",aimRange<runRange*.35f);
        Home();yield return new WaitForSeconds(.35f);Check("stop blends motion out",h.MovementWeight<.03f);
        Keys(UnityEngine.InputSystem.Key.W);Pitch(80);yield return new WaitForSeconds(.5f);Capture("walk_down");Check("moving down-view feet remain visible",OnScreen(lf.position)&&OnScreen(rf.position));
        Keys();yield return new WaitForSeconds(.4f);Pitch(0);
        Keys(UnityEngine.InputSystem.Key.Space);yield return Frames(2);Keys();yield return new WaitForSeconds(.14f);Capture("jump");
        Check("jump keeps body and hands",motor.IsJumping&&h.LowerBodyVisible&&OnScreen(h.LeftHandPosition)&&OnScreen(h.ItemPosition));
        yield return new WaitForSeconds(1.2f);Check("landing restores grounded pose",cc.isGrounded&&h.LowerBodyVisible);Home();yield return new WaitForSeconds(.3f);
        // PlayerInput의 실제 취소/방출 경로를 함께 확인한다.
        Keys(UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys();Mouse(1);yield return new WaitForSeconds(.3f);
        Check("input E + left hold shows landing marker",t.IsAiming&&t.LandingMarkerVisible);
        Check("full path extends past old 2.5m cap",LineLength()>2.6f);
        int releases=t.ReleaseCount;Mouse(3);yield return Frames(2);Check("right cancel clears line and circle",!t.IsAiming&&!t.PreviewHit&&!t.LandingMarkerVisible);
        Mouse(0);yield return Frames(2);Check("cancel then release does not spawn",t.ReleaseCount==releases);t.ExitStance();
        t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.3f);t.RefreshTrajectory(false);
        var predicted=t.PreviewContact;bool hiddenOnRelease=false;Vector3 impact=Vector3.zero;bool gotImpact=false;
        System.Action<ItemDefinition,ThrownObject> release=(item,thrown)=>{hiddenOnRelease=!h.ItemVisible;thrown.Hit+=(obj,collision)=>{if(!gotImpact){impact=collision.GetContact(0).point;gotImpact=true;}};};
        t.Released+=release;
        try{int releaseFrame=Time.frameCount;Check("release once",t.ReleaseThrow()&&t.ReleaseCount==releases+1);Check("release clears circle and held duplicate",!t.LandingMarkerVisible&&hiddenOnRelease);Check("VARCO follow-through starts without delay",Time.frameCount==releaseFrame&&h.Pose=="Recover");Check("duplicate release refused",!t.ReleaseThrow());yield return new WaitForSeconds(1.6f);}
        finally{t.Released-=release;}
        log.AppendLine($"actual first impact difference={Vector3.Distance(predicted,impact):F4}m predicted={predicted} actual={impact}");
        Check("marker matches real first impact within 8cm",gotImpact&&Vector3.Distance(predicted,impact)<.08f);
        Home();yield return new WaitForSeconds(.3f);
        var wall=Cube("TemporaryWall",testHome+Vector3.forward*2f,new Vector3(5,5,.2f));Physics.SyncTransforms();
        t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.3f);Capture("marker_wall");
        Check("wall marker follows wall normal",t.LandingMarkerVisible&&Mathf.Abs(t.PreviewNormal.z)>.95f&&Mathf.Abs(t.PreviewNormal.y)<.1f);
        wall.SetActive(false);t.ExitStance();
        var slope=Cube("TemporarySlope",new Vector3(1000,200.3f,1003),new Vector3(8,.3f,5));slope.transform.rotation=Quaternion.Euler(-20,0,0);Physics.SyncTransforms();Pitch(30);
        t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.3f);Capture("marker_slope");
        Check("slope marker follows surface",t.LandingMarkerVisible&&Vector3.Dot(t.PreviewNormal,slope.transform.up)>.98f);
        slope.SetActive(false);t.ExitStance();Pitch(0);
        // 시간/거리 한계는 접촉으로 취급하지 않는다. 설정 복제본만 바꾼다.
        settingsField.SetValue(t,runtimeSettings);
        typeof(PlayerThrowSettings).GetField("trajectoryMaxTime",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(runtimeSettings,.1f);
        t.ToggleStance();t.BeginAim();yield return Frames(3);Check("time cap has no false landing circle",!t.PreviewHit&&!t.LandingMarkerVisible);
        typeof(PlayerThrowSettings).GetField("trajectoryMaxTime",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(runtimeSettings,settings.TrajectoryMaxTime);
        typeof(PlayerThrowSettings).GetField("maxPreviewDistance",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(runtimeSettings,1f);
        yield return Frames(3);Check("distance cap has no false landing circle",!t.PreviewHit&&!t.LandingMarkerVisible);settingsField.SetValue(t,settings);t.ExitStance();
        t.ToggleStance();t.BeginAim();yield return Frames(3);Check("marker returns after valid surface",t.LandingMarkerVisible);
        var block=Cube("TemporaryStartBlock",h.ItemPosition,Vector3.one*.2f);Physics.SyncTransforms();yield return Frames(3);
        releases=t.ReleaseCount;Check("blocked start clears stale contact",t.IsBlocked&&!t.PreviewHit&&!t.LandingMarkerVisible&&!t.ReleaseThrow()&&t.ReleaseCount==releases);block.SetActive(false);t.ExitStance();
        yield return new WaitForSeconds(.25f);t.ToggleStance();t.BeginAim();yield return Frames(3);t.SetHeldItem(null);
        Check("item removal clears preview",!t.IsAiming&&!t.LandingMarkerVisible&&!t.PreviewHit);t.SetHeldItem(projectItem);
        t.ToggleStance();t.BeginAim();yield return Frames(3);h.enabled=false;
        Check("disable cancels aim and hides lower body",!t.IsAiming&&!h.LowerBodyVisible&&!t.LandingMarkerVisible);h.enabled=true;
        yield return Frames(3);Check("reenable restores body",h.LowerBodyVisible&&!t.ReleaseThrow());
        Check("live frames advanced",Time.frameCount-firstFrame>100);
        log.AppendLine($"TOTAL passed={passed}, failed={failed}, frames={firstFrame}→{Time.frameCount}");
    }
    finally
    {
        Keys();Mouse(0);settingsField.SetValue(t,settings);UnityEngine.Object.Destroy(runtimeSettings);
        foreach(var go in temporary)if(go)UnityEngine.Object.Destroy(go);
        foreach(var thrown in UnityEngine.Object.FindObjectsByType<ThrownObject>(FindObjectsSortMode.None))if(thrown.name.Contains("Clone"))UnityEngine.Object.Destroy(thrown.gameObject);
        t.enabled=true;h.enabled=true;t.SetHeldItem(projectItem);t.ExitStance();zoom.SetZoomed(false);motor.TryStandUp();Teleport(savedPosition,savedRotation);Pitch(0);
        Application.targetFrameRate=oldFPS;QualitySettings.vSyncCount=oldVSync;UnityEngine.InputSystem.InputSystem.settings=originalInputSettings;UnityEngine.Object.Destroy(captureInputSettings);
        System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"play_validation.txt"),log.ToString());
    }
}
t.StartCoroutine(Run());return "Motion validation running";
