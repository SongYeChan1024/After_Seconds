if(!Application.isPlaying)throw new System.Exception("Play required");
var t=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();var h=t.GetComponent<PlayerFirstPersonHands>();
var cc=t.GetComponent<CharacterController>();var look=t.GetComponent<PlayerLook>();var zoom=t.GetComponent<PlayerZoom>();var motor=t.GetComponent<PlayerMotor>();
var keyboard=UnityEngine.InputSystem.Keyboard.current;var mouse=UnityEngine.InputSystem.Mouse.current;
var settings=UnityEngine.InputSystem.InputSystem.settings;var input=UnityEngine.Object.Instantiate(settings);
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_VarcoFirstPerson"));
var log=new System.Text.StringBuilder();int pass=0,fail=0,start=Time.frameCount;var originalPosition=t.transform.position;var originalRotation=t.transform.rotation;
var objects=new List<GameObject>();var savedItem=t.HeldItem;int oldFPS=Application.targetFrameRate,oldVSync=QualitySettings.vSyncCount;
void Check(string name,bool ok){if(ok)pass++;else fail++;log.AppendLine((ok?"PASS ":"FAIL ")+name);}
void Keys(params UnityEngine.InputSystem.Key[] keys)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(keys));
void Pitch(float p){typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,p);t.Origin.localRotation=Quaternion.Euler(p,0,0);}
void Home(Vector3 p,Quaternion q){Keys();t.ExitStance();zoom.SetZoomed(false);motor.TryStandUp();cc.enabled=false;t.transform.SetPositionAndRotation(p,q);cc.enabled=true;Pitch(0);h.ResetPose();Physics.SyncTransforms();}
void Capture(string name)
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var prev=c.targetTexture;var active=RenderTexture.active;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());}
    finally{c.targetTexture=prev;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
}
bool Visible(Vector3 p){var v=Camera.main.WorldToViewportPoint(p);return v.z>0&&v.x>0&&v.x<1&&v.y>0&&v.y<1;}
System.Collections.IEnumerator Toggle(){Keys(UnityEngine.InputSystem.Key.R);yield return null;yield return null;Keys();yield return new WaitForSeconds(.4f);}
System.Collections.IEnumerator Run()
{
    try
    {
        input.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;
        input.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
        UnityEngine.InputSystem.InputSystem.settings=input;UnityEngine.InputSystem.InputSystem.EnableDevice(keyboard);UnityEngine.InputSystem.InputSystem.EnableDevice(mouse);
        EditorWindow.GetWindow(typeof(Editor).Assembly.GetType("UnityEditor.GameView")).Focus();QualitySettings.vSyncCount=0;Application.targetFrameRate=60;
        Home(originalPosition,originalRotation);yield return new WaitForSeconds(.3f);t.ToggleStance();t.BeginAim();if(t.IsUnderhand)yield return Toggle();yield return new WaitForSeconds(.3f);Capture("mode_overhand_b5");
        float highHand=t.Origin.InverseTransformPoint(h.ItemPosition).y;
        yield return Toggle();Check("R changes to underhand while aiming",t.IsUnderhand&&t.IsAiming);Capture("mode_underhand_b5");
        Check("underhand starts at least 15cm below overhand",highHand-t.Origin.InverseTransformPoint(h.ItemPosition).y>.15f);
        Check("low held item remains in frame",Visible(h.ItemPosition));Check("both hands remain visible",Visible(h.LeftHandPosition)&&Visible(h.ItemPosition));
        t.TryGetLaunch(out var underB5);Check("neutral aim launches upward",Vector3.Dot(underB5.Velocity,Vector3.up)>2.5f);
        zoom.SetZoomed(true);yield return new WaitForSeconds(.3f);Capture("mode_underhand_zoom");Check("zoom keeps low item visible",Visible(h.ItemPosition));zoom.SetZoomed(false);
        yield return new WaitForSeconds(.25f);t.ReleaseThrow();yield return new WaitForSeconds(.08f);Capture("underhand_release");yield return new WaitForSeconds(.4f);
        var floor=GameObject.CreatePrimitive(PrimitiveType.Cube);objects.Add(floor);floor.name="TemporaryModeFloor";floor.transform.position=new Vector3(1000,199.5f,1000);floor.transform.localScale=new Vector3(100,1,100);
        var home=new Vector3(1000,200+cc.height*.5f-cc.center.y+.02f,1000);Home(home,Quaternion.identity);yield return new WaitForSeconds(.4f);
        t.ToggleStance();t.BeginAim();if(t.IsUnderhand)yield return Toggle();yield return new WaitForSeconds(.3f);
        t.TryGetLaunch(out var over);float overDistance=Vector3.ProjectOnPlane(t.PreviewContact-over.Position,Vector3.up).magnitude;
        Check("overhand speed 12m/s",Mathf.Abs(over.Velocity.magnitude-12)<.01f);
        yield return Toggle();t.TryGetLaunch(out var under);var predicted=t.PreviewContact;float underDistance=Vector3.ProjectOnPlane(predicted-under.Position,Vector3.up).magnitude;
        Check("underhand speed 6m/s",Mathf.Abs(under.Velocity.magnitude-6)<.01f);Check("speed ratio 2 to 1",Mathf.Abs(over.Velocity.magnitude/under.Velocity.magnitude-2)<.01f);
        var line=t.transform.Find("ThrowTrajectory").GetComponent<LineRenderer>();float apex=Enumerable.Range(0,line.positionCount).Max(i=>line.GetPosition(i).y)-under.Position.y;
        Check("arc starts at low held item",Vector3.Distance(line.GetPosition(0),h.ItemPosition)<.015f);
        Check("arc rises visibly before falling",line.GetPosition(3).y>line.GetPosition(0).y&&apex>.4f&&t.PreviewContact.y<under.Position.y);
        Check("underhand travels materially less far",underDistance<overDistance*.8f&&underDistance>2f);Check("underhand has first contact circle",t.PreviewHit&&t.LandingMarkerVisible);
        log.AppendLine($"speed: over={over.Velocity.magnitude:F3}, under={under.Velocity.magnitude:F3}; range over={overDistance:F3}m, under={underDistance:F3}m; under rise={apex:F3}m");
        bool impact=false,hidden=false;Vector3 contact=Vector3.zero;float initialSpeed=0;
        System.Action<ItemDefinition,ThrownObject> release=(item,obj)=>{hidden=!h.ItemVisible;initialSpeed=obj.GetComponent<Rigidbody>().linearVelocity.magnitude;obj.Hit+=(o,c)=>{if(!impact){impact=true;contact=c.GetContact(0).point;}};};
        t.Released+=release;int frame=Time.frameCount,releases=t.ReleaseCount;
        try
        {
            Check("underhand releases immediately",t.ReleaseThrow()&&Time.frameCount==frame&&t.ReleaseCount==releases+1);
            Check("released physics uses underhand speed",Mathf.Abs(initialSpeed-6)<.01f);
            Check("underhand hides duplicate and circle",hidden&&!t.LandingMarkerVisible);
            yield return new WaitForSeconds(1.6f);
        }
        finally{t.Released-=release;}
        Check("underhand prediction matches impact within 8cm",impact&&Vector3.Distance(contact,predicted)<.08f);log.AppendLine("underhand impact error="+Vector3.Distance(contact,predicted).ToString("F4")+"m");
        t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.25f);Pitch(65);yield return new WaitForSeconds(.25f);t.TryGetLaunch(out var down);
        Check("deliberate downward aim is retained",down.Velocity.y<0);Pitch(0);yield return new WaitForSeconds(.3f);
        releases=t.ReleaseCount;t.CancelAim();Check("cancel clears line and marker without throw",!t.IsAiming&&!t.LandingMarkerVisible&&!t.ReleaseThrow()&&t.ReleaseCount==releases);
        Check("live frames advanced",Time.frameCount-start>100);log.AppendLine($"TOTAL passed={pass}, failed={fail}, frames={start}→{Time.frameCount}");
    }
    finally
    {
        Keys();UnityEngine.InputSystem.InputSystem.QueueStateEvent(mouse,new UnityEngine.InputSystem.LowLevel.MouseState());
        foreach(var o in objects)if(o)UnityEngine.Object.Destroy(o);
        foreach(var o in UnityEngine.Object.FindObjectsByType<ThrownObject>(FindObjectsSortMode.None))if(o.name.Contains("Clone"))UnityEngine.Object.Destroy(o.gameObject);
        t.SetHeldItem(savedItem);Home(originalPosition,originalRotation);if(t.IsUnderhand){t.ToggleStance();t.ToggleThrowMode();t.ExitStance();}
        UnityEngine.InputSystem.InputSystem.settings=settings;UnityEngine.Object.Destroy(input);Application.targetFrameRate=oldFPS;QualitySettings.vSyncCount=oldVSync;
        System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"mode_validation.txt"),log.ToString());
    }
}
t.StartCoroutine(Run());return "Throw mode validation running";
