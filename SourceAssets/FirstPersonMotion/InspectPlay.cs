if (!Application.isPlaying) throw new System.Exception("Play required");
var t = UnityEngine.Object.FindAnyObjectByType<PlayerThrow>();
var h = t.GetComponent<PlayerFirstPersonHands>(); var look = t.GetComponent<PlayerLook>();
var animator = t.transform.Find("VisualRoot").GetComponentsInChildren<Animator>().First(a => a.isHuman);
var dir = System.IO.Path.GetFullPath(System.IO.Path.Combine(Application.dataPath,"../../../Docs/Review/2026-11-17_FirstPersonMotion"));
System.IO.Directory.CreateDirectory(dir);
void Pitch(float degrees) { typeof(PlayerLook).GetField("pitchAngle",System.Reflection.BindingFlags.NonPublic|System.Reflection.BindingFlags.Instance).SetValue(look,degrees);t.Origin.localRotation=Quaternion.Euler(degrees,0,0); }
void Capture(string name)
{
    var c=Camera.main;var rt=new RenderTexture(1280,720,24);var target=c.targetTexture;var active=RenderTexture.active;var tex=new Texture2D(1280,720,TextureFormat.RGB24,false);
    try {c.targetTexture=rt;c.Render();RenderTexture.active=rt;tex.ReadPixels(new Rect(0,0,1280,720),0,0);tex.Apply();System.IO.File.WriteAllBytes(System.IO.Path.Combine(dir,name+".png"),tex.EncodeToPNG());}
    finally{c.targetTexture=target;RenderTexture.active=active;UnityEngine.Object.Destroy(tex);rt.Release();UnityEngine.Object.Destroy(rt);}
}
System.Collections.IEnumerator Run()
{
    int start=Time.frameCount;yield return new WaitForSeconds(.5f);Pitch(0);yield return new WaitForSeconds(.3f);Capture("idle");
    Pitch(80);yield return new WaitForSeconds(.4f);Capture("look_down");
    var log=new System.Text.StringBuilder();log.AppendLine("Frames="+start+"→"+Time.frameCount+" lower="+h.LowerBodyVisible);
    var cam=Camera.main;
    log.AppendLine("camera "+cam.transform.position+" fov="+cam.fieldOfView+" near="+cam.nearClipPlane);
    foreach(var bone in new[]{HumanBodyBones.Hips,HumanBodyBones.LeftFoot,HumanBodyBones.RightFoot})
    {var b=animator.GetBoneTransform(bone);log.AppendLine(bone+" local="+t.transform.InverseTransformPoint(b.position)+" viewport="+cam.WorldToViewportPoint(b.position));}
    log.AppendLine("left viewport="+cam.WorldToViewportPoint(h.LeftHandPosition));
    log.AppendLine("right item viewport="+cam.WorldToViewportPoint(h.ItemPosition));
    Pitch(12);t.ToggleStance();t.BeginAim();yield return new WaitForSeconds(.4f);Capture("aim");
    log.AppendLine("hit="+t.PreviewHit+" circle="+t.LandingMarkerVisible+" contact="+t.PreviewContact+" normal="+t.PreviewNormal);
    t.CancelAim();t.ExitStance();Pitch(0);System.IO.File.WriteAllText(System.IO.Path.Combine(dir,"initial_inspection.txt"),log.ToString());
}
t.StartCoroutine(Run());return "Inspection started";
