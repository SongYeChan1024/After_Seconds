if(!Application.isPlaying)throw new System.Exception("Play required");
var t=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();var p=t.GetComponent<PlayerPresenter>();var h=t.GetComponent<PlayerFirstPersonHands>();
var cc=t.GetComponent<CharacterController>();var zoom=t.GetComponent<PlayerZoom>();var look=t.GetComponent<PlayerLook>();var motor=t.GetComponent<PlayerMotor>();
var pi=t.GetComponent<UnityEngine.InputSystem.PlayerInput>();var keyboard=UnityEngine.InputSystem.Keyboard.current;var mouse=UnityEngine.InputSystem.Mouse.current;
var originalInput=UnityEngine.InputSystem.InputSystem.settings;var input=UnityEngine.Object.Instantiate(originalInput);
var item=t.HeldItem;var otherItem=UnityEngine.Object.Instantiate(item);var position=t.transform.position;var rotation=t.transform.rotation;bool originalMode=t.IsUnderhand;
var repeatField=typeof(PlayerThrow).GetField("repeatTestItem",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance);bool originalRepeat=(bool)repeatField.GetValue(t);
int originalFPS=Application.targetFrameRate,originalVSync=QualitySettings.vSyncCount;int passed=0,failed=0,first=Time.frameCount;var log=new System.Text.StringBuilder();
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_DirectThrow"));System.IO.Directory.CreateDirectory(dir);
GameObject floor=null,block=null;
void Check(string name,bool value){if(value)passed++;else failed++;log.AppendLine((value?"PASS ":"FAIL ")+name);}
void Mouse(ushort buttons)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(mouse,new UnityEngine.InputSystem.LowLevel.MouseState{buttons=buttons});
void Keys(params UnityEngine.InputSystem.Key[] keys)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(keys));
System.Collections.IEnumerator Frames(int count){for(int i=0;i<count;i++)yield return null;}
void Reset(){Mouse(0);Keys();t.ExitStance();zoom.SetZoomed(false);if(t.IsUnderhand)t.ToggleThrowMode();}
void Move(Vector3 pos,Quaternion rot){cc.enabled=false;t.transform.SetPositionAndRotation(pos,rot);cc.enabled=true;Physics.SyncTransforms();}
void Capture()
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var prev=c.targetTexture;var active=RenderTexture.active;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,"direct_hold.png"),tex.EncodeToPNG());}
    finally{c.targetTexture=prev;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
}
System.Collections.IEnumerator Run()
{
    try
    {
        input.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;input.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
        UnityEngine.InputSystem.InputSystem.settings=input;UnityEngine.InputSystem.InputSystem.EnableDevice(keyboard);UnityEngine.InputSystem.InputSystem.EnableDevice(mouse);
        EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();QualitySettings.vSyncCount=0;Application.targetFrameRate=60;repeatField.SetValue(t,true);
        Reset();yield return new WaitForSeconds(.3f);int n=t.ReleaseCount;
        Check("idle does not require E or stance",!t.IsInThrowStance&&!t.IsAiming);
        Mouse(1);yield return new WaitForSeconds(.35f);Capture();
        Check("left press alone starts aiming",t.IsAiming&&t.IsInThrowStance);Check("holding left previews without throwing",t.ReleaseCount==n&&t.transform.Find("ThrowTrajectory").GetComponent<LineRenderer>().enabled);
        Mouse(2);yield return Frames(3);Mouse(0);yield return Frames(3);Reset();yield return Frames(3);
        floor=GameObject.CreatePrimitive(PrimitiveType.Cube);floor.name="TemporaryDirectThrowFloor";floor.transform.position=new Vector3(1000,199.5f,1000);floor.transform.localScale=new Vector3(100,1,100);
        Move(new Vector3(1000,200+cc.height*.5f-cc.center.y+.02f,1000),Quaternion.identity);
        typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,0f);t.Origin.localRotation=Quaternion.identity;yield return new WaitForSeconds(.4f);
        n=t.ReleaseCount;Mouse(1);Mouse(0);yield return Frames(3);
        Check("same-frame quick click throws exactly once without E",t.ReleaseCount==n+1);Check("quick throw exits aim and stance",!t.IsAiming&&!t.IsInThrowStance);
        yield return Frames(3);Check("quick click does not duplicate",t.ReleaseCount==n+1);
        n=t.ReleaseCount;Mouse(1);yield return new WaitForSeconds(.6f);Check("long hold never auto-fires",t.IsAiming&&t.ReleaseCount==n);
        Mouse(0);yield return Frames(2);Check("release fires in next input update",t.ReleaseCount==n+1);Check("release clears visual and guide",!h.ItemVisible&&!t.transform.Find("ThrowTrajectory").GetComponent<LineRenderer>().enabled);
        Check("overhand speed remains 12",Mathf.Abs(t.LastLaunch.Velocity.magnitude-12)<.01f);
        yield return new WaitForSeconds(.45f);n=t.ReleaseCount;
        for(int i=0;i<3;i++){Mouse(1);Mouse(0);yield return Frames(3);}
        Check("three consecutive clicks need no E",t.ReleaseCount==n+3);
        Reset();yield return Frames(3);Keys(UnityEngine.InputSystem.Key.R);yield return Frames(2);Keys();yield return Frames(2);
        Check("R preselects underhand before aiming",t.IsUnderhand&&!t.IsInThrowStance);
        n=t.ReleaseCount;Mouse(1);yield return Frames(3);Mouse(0);yield return Frames(3);Check("preselected underhand throws directly",t.ReleaseCount==n+1&&Mathf.Abs(t.LastLaunch.Velocity.magnitude-6)<.01f);
        Reset();yield return Frames(3);Mouse(1);yield return Frames(3);Keys(UnityEngine.InputSystem.Key.R);yield return Frames(2);Keys();yield return Frames(2);
        Check("R switches while holding left",t.IsUnderhand&&t.IsAiming);Mouse(3);yield return Frames(2);Mouse(0);yield return Frames(3);
        Reset();yield return Frames(3);n=t.ReleaseCount;Mouse(1);yield return Frames(3);Mouse(3);yield return Frames(3);
        Check("right click cancels held aim",!t.IsAiming&&!t.IsInThrowStance&&t.ReleaseCount==n);Mouse(1);yield return Frames(3);Check("continuing left hold cannot restart canceled aim",!t.IsAiming);Mouse(0);yield return Frames(3);Check("release after right cancel never throws",t.ReleaseCount==n);
        Mouse(1);yield return Frames(3);Mouse(0);yield return Frames(3);Check("fresh click after cancel works",t.ReleaseCount==n+1);
        Reset();yield return Frames(3);n=t.ReleaseCount;Mouse(1);yield return Frames(3);Keys(UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys();Mouse(0);yield return Frames(3);
        Check("E cancels without delayed throw",!t.IsAiming&&!t.IsInThrowStance&&t.ReleaseCount==n);
        Keys(UnityEngine.InputSystem.Key.E);yield return Frames(2);Keys();yield return Frames(2);Check("E at idle does not require a setup mode",!t.IsInThrowStance);
        Mouse(3);yield return Frames(3);Mouse(0);yield return Frames(3);Check("simultaneous left and right prioritizes cancel",t.ReleaseCount==n&&!t.IsAiming);
        Mouse(1);Mouse(0);Keys(UnityEngine.InputSystem.Key.E);yield return Frames(3);Keys();yield return Frames(2);Check("E cancels same-frame quick click",t.ReleaseCount==n);
        Reset();yield return Frames(3);Mouse(2);yield return Frames(2);Mouse(0);yield return Frames(3);Check("idle right click still toggles zoom",zoom.IsZoomed);
        Mouse(1);yield return Frames(3);Check("left press starts aim while zoomed",t.IsAiming&&zoom.IsZoomed);Mouse(0);yield return Frames(3);Check("direct zoom throw restores normal view",!zoom.IsZoomed&&t.ReleaseCount==n+1);
        Reset();yield return Frames(3);n=t.ReleaseCount;Mouse(1);yield return Frames(3);p.enabled=false;Mouse(0);yield return Frames(3);p.enabled=true;yield return Frames(3);
        Check("presenter disable cancels without ghost release",t.ReleaseCount==n&&!t.IsAiming);
        Mouse(1);yield return Frames(3);pi.DeactivateInput();yield return Frames(3);Check("action map disable is not a throw",t.ReleaseCount==n&&!t.IsAiming);
        Mouse(0);pi.ActivateInput();yield return Frames(3);Mouse(1);Mouse(0);yield return Frames(3);Check("fresh click works after input reactivation",t.ReleaseCount==n+1);
        Reset();yield return Frames(3);n=t.ReleaseCount;Mouse(1);yield return Frames(3);t.SetHeldItem(otherItem);Mouse(0);yield return Frames(3);Check("item switch cancels old click",t.ReleaseCount==n&&!t.IsAiming);t.SetHeldItem(item);
        t.SetHeldItem(null);Mouse(1);Mouse(0);Keys(UnityEngine.InputSystem.Key.R);yield return Frames(3);Keys();Check("empty hand cannot aim or throw",t.ReleaseCount==n&&!t.IsAiming&&!t.IsInThrowStance);t.SetHeldItem(item);
        Reset();yield return Frames(3);Mouse(1);yield return new WaitForSeconds(.25f);block=GameObject.CreatePrimitive(PrimitiveType.Cube);block.name="TemporaryDirectThrowBlock";block.transform.position=h.ItemPosition;block.transform.localScale=Vector3.one*.3f;Physics.SyncTransforms();yield return Frames(3);Mouse(0);yield return Frames(3);
        Check("blocked hand refuses direct throw without consuming",t.ReleaseCount==n&&t.HeldItem==item);block.SetActive(false);Reset();yield return Frames(3);
        repeatField.SetValue(t,false);Mouse(1);Mouse(0);yield return Frames(3);Check("single item is consumed once",t.ReleaseCount==n+1&&!t.HasHeldItem);Mouse(1);Mouse(0);yield return Frames(3);Check("consumed item cannot be thrown twice",t.ReleaseCount==n+1);
        Check("real game frames advanced",Time.frameCount-first>100);log.AppendLine($"TOTAL passed={passed}, failed={failed}, frames={first}→{Time.frameCount}");
    }
    finally
    {
        Mouse(0);Keys();p.enabled=true;pi.ActivateInput();repeatField.SetValue(t,originalRepeat);t.SetHeldItem(item);Reset();if(t.IsUnderhand!=originalMode)t.ToggleThrowMode();
        if(floor)UnityEngine.Object.Destroy(floor);if(block)UnityEngine.Object.Destroy(block);
        foreach(var obj in UnityEngine.Object.FindObjectsByType<ThrownObject>(FindObjectsSortMode.None))if(obj.name.Contains("Clone"))UnityEngine.Object.Destroy(obj.gameObject);
        Move(position,rotation);typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,0f);t.Origin.localRotation=Quaternion.identity;
        UnityEngine.InputSystem.InputSystem.settings=originalInput;UnityEngine.Object.Destroy(input);UnityEngine.Object.Destroy(otherItem);Application.targetFrameRate=originalFPS;QualitySettings.vSyncCount=originalVSync;
        System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"validation.txt"),log.ToString());
    }
}
t.StartCoroutine(Run());return "Direct click input validation running";
