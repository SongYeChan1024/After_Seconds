if (!Application.isPlaying) throw new System.Exception("Play required");
var t=UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();var h=t.GetComponent<PlayerFirstPersonHands>();
var cc=t.GetComponent<CharacterController>();var look=t.GetComponent<PlayerLook>();var zoom=t.GetComponent<PlayerZoom>();var motor=t.GetComponent<PlayerMotor>();
var keyboard=UnityEngine.InputSystem.Keyboard.current;var mouse=UnityEngine.InputSystem.Mouse.current;
var dir=System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_FirstPersonMotion"));
Vector3 savedPosition=t.transform.position;Quaternion savedRotation=t.transform.rotation;int start=Time.frameCount;
var report=new System.Text.StringBuilder();
var originalInputSettings=UnityEngine.InputSystem.InputSystem.settings;
var captureInputSettings=UnityEngine.Object.Instantiate(originalInputSettings);
void Keys(params UnityEngine.InputSystem.Key[] keys)=>UnityEngine.InputSystem.InputSystem.QueueStateEvent(keyboard,new UnityEngine.InputSystem.LowLevel.KeyboardState(keys));
void Pitch(float p){typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,p);t.Origin.localRotation=Quaternion.Euler(p,0,0);}
void Home(){Keys();t.ExitStance();if(t.IsUnderhand){t.ToggleStance();t.ToggleThrowMode();t.ExitStance();}zoom.SetZoomed(false);motor.TryStandUp();cc.enabled=false;t.transform.SetPositionAndRotation(savedPosition,savedRotation);cc.enabled=true;Pitch(0);}
void Capture(string name)
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var target=c.targetTexture;var active=RenderTexture.active;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try{c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());}
    finally{c.targetTexture=target;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
    report.AppendLine(name+": frame="+Time.frameCount+", speed="+cc.velocity.magnitude.ToString("F3")+", lower="+h.LowerBodyVisible+", left="+c.WorldToViewportPoint(h.LeftHandPosition)+", right="+c.WorldToViewportPoint(h.ItemPosition));
}
System.Collections.IEnumerator Run()
{
    try
    {
        captureInputSettings.backgroundBehavior=UnityEngine.InputSystem.InputSettings.BackgroundBehavior.IgnoreFocus;
        captureInputSettings.editorInputBehaviorInPlayMode=UnityEngine.InputSystem.InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
        UnityEngine.InputSystem.InputSystem.settings=captureInputSettings;
        Home();yield return new WaitForSeconds(.4f);Capture("idle");Pitch(80);yield return new WaitForSeconds(.3f);Capture("look_down");
        Keys(UnityEngine.InputSystem.Key.C);yield return null;yield return null;Keys();yield return new WaitForSeconds(.4f);Capture("crouch_down");
        Home();yield return new WaitForSeconds(.4f);Keys(UnityEngine.InputSystem.Key.W);yield return new WaitForSeconds(.3f);Capture("b5_walk_a");yield return new WaitForSeconds(.16f);Capture("b5_walk_b");Keys();yield return new WaitForSeconds(.3f);
        Home();yield return new WaitForSeconds(.3f);Keys(UnityEngine.InputSystem.Key.W,UnityEngine.InputSystem.Key.LeftShift);yield return new WaitForSeconds(.3f);Capture("b5_run_a");yield return new WaitForSeconds(.13f);Capture("b5_run_b");Keys();yield return new WaitForSeconds(.3f);
        Home();Pitch(80);yield return new WaitForSeconds(.3f);Keys(UnityEngine.InputSystem.Key.W);yield return new WaitForSeconds(.3f);Capture("b5_walk_down_a");yield return new WaitForSeconds(.16f);Capture("b5_walk_down_b");Keys();yield return new WaitForSeconds(.3f);
        Home();Pitch(38);t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.35f);Capture("aim_floor");t.ToggleThrowMode();yield return new WaitForSeconds(.3f);Capture("aim_underhand");
        t.CancelAim();zoom.SetZoomed(true);t.BeginAim();yield return new WaitForSeconds(.4f);Capture("aim_zoom");
        var lv=Camera.main.WorldToViewportPoint(h.LeftHandPosition);var rv=Camera.main.WorldToViewportPoint(h.ItemPosition);
        report.AppendLine("ZOOM both wrists in frame="+(lv.x>0&&lv.x<1&&lv.y>0&&lv.y<1&&rv.x>0&&rv.x<1&&rv.y>0&&rv.y<1));
        Home();Pitch(-75);yield return new WaitForSeconds(.3f);Capture("look_up");report.AppendLine("frames="+start+"→"+Time.frameCount);
    }
    finally{Home();UnityEngine.InputSystem.InputSystem.settings=originalInputSettings;UnityEngine.Object.Destroy(captureInputSettings);System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"final_visual.txt"),report.ToString());}
}
t.StartCoroutine(Run());return "Final B5 capture running";
